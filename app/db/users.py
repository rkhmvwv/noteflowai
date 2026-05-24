
import json
import uuid
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

USERS_FILE = Path("data/users.json")
_lock = asyncio.Lock()


def _ensure():
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        USERS_FILE.write_text("[]", encoding="utf-8")


def _read() -> list:
    _ensure()
    try:
        return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        logging.error(f"Ошибка чтения users.json: {e}")
        return []


def _write(users: list):
    _ensure()
    USERS_FILE.write_text(
        json.dumps(users, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )




async def find_by_email(email: str) -> Optional[dict]:
    """Ищем пользователя по email (регистронезависимо)."""
    async with _lock:
        email = email.lower().strip()
        for u in _read():
            if u["email"] == email:
                return u
        return None


async def create_user(email: str, password_hash: str, name: str) -> dict:
    """Создаём нового пользователя. Возвращаем запись."""
    async with _lock:
        users = _read()
        email = email.lower().strip()

        
        if any(u["email"] == email for u in users):
            from fastapi import HTTPException
            raise HTTPException(400, "Этот email уже зарегистрирован")

        user = {
            "id":            str(uuid.uuid4()),
            "email":         email,
            "name":          name.strip(),
            "password_hash": password_hash,
            "is_verified":   False,
            "created_at":    datetime.now().strftime("%d.%m.%Y %H:%M"),
            "last_login":    None,
        }
        users.append(user)
        _write(users)
        logging.info(f"Новый пользователь: {email}")
        return user


async def verify_user_email(email: str) -> bool:
    """Помечаем email как подтверждённый."""
    async with _lock:
        users = _read()
        email = email.lower().strip()
        for u in users:
            if u["email"] == email:
                u["is_verified"] = True
                _write(users)
                logging.info(f"Email подтверждён: {email}")
                return True
        return False


async def update_last_login(email: str):
    """Обновляем дату последнего входа."""
    async with _lock:
        users = _read()
        for u in users:
            if u["email"] == email.lower().strip():
                u["last_login"] = datetime.now().strftime("%d.%m.%Y %H:%M")
                _write(users)
                return


async def update_password(email: str, new_hash: str):
    """Меняем пароль пользователя."""
    async with _lock:
        users = _read()
        for u in users:
            if u["email"] == email.lower().strip():
                u["password_hash"] = new_hash
                _write(users)
                logging.info(f"Пароль изменён: {email}")
                return
