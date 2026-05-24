
import os
import time
import secrets
import hashlib
import logging
from typing import Optional

import bcrypt
import jwt
from fastapi import Cookie, HTTPException

from app.config import SECRET_KEY

ALGORITHM = "HS256"
SESSION_TTL   = 60 * 60 * 24 * 30   
VERIFY_TTL    = 60 * 60 * 24         



def hash_password(password: str) -> str:
    """Хэшируем пароль через bcrypt. Возвращаем строку для хранения в БД."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Проверяем введённый пароль против хэша из БД."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def validate_password(password: str):
    """Проверяем сложность пароля. Выбрасываем 400 если слабый."""
    if len(password) < 8:
        raise HTTPException(400, "Пароль должен быть не менее 8 символов")
    if not any(c.isdigit() for c in password):
        raise HTTPException(400, "Пароль должен содержать хотя бы одну цифру")




def create_session_token(user_id: str, email: str, name: str) -> str:
    """Создаём подписанный JWT для хранения в cookie."""
    payload = {
        "user_id": user_id,
        "email":   email,
        "name":    name,
        "exp":     int(time.time()) + SESSION_TTL,
        "iat":     int(time.time()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_session_token(token: str) -> dict:
    """Декодируем JWT. Выбрасываем 401 если истёк или невалидный."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Сессия истекла — войдите снова")
    except Exception:
        raise HTTPException(401, "Невалидная сессия")


def get_current_user(session: Optional[str] = Cookie(default=None)) -> dict:
    """
    FastAPI dependency — используй везде где нужна авторизация:
        user = Depends(get_current_user)
    """
    if not session:
        raise HTTPException(401, "Необходима авторизация")
    return decode_session_token(session)




def create_verify_token(email: str) -> str:
    """
    Создаём короткий JWT для ссылки подтверждения.
    Ссылка будет: http://localhost:8000/api/auth/verify?token=XXX
    """
    payload = {
        "email": email,
        "purpose": "email_verify",
        "exp": int(time.time()) + VERIFY_TTL,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_verify_token(token: str) -> str:
    """Проверяем токен из письма. Возвращаем email или выбрасываем 400."""
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if data.get("purpose") != "email_verify":
            raise ValueError
        return data["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(400, "Ссылка подтверждения устарела. Запросите новую.")
    except Exception:
        raise HTTPException(400, "Неверная ссылка подтверждения")



def create_reset_token(email: str) -> str:
    payload = {
        "email": email,
        "purpose": "password_reset",
        "exp": int(time.time()) + 60 * 30,  # 30 минут
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_reset_token(token: str) -> str:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if data.get("purpose") != "password_reset":
            raise ValueError
        return data["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(400, "Ссылка сброса устарела. Запросите новую.")
    except Exception:
        raise HTTPException(400, "Неверная ссылка сброса пароля")
