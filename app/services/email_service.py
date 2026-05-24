

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import GMAIL_USER, GMAIL_PASSWORD, APP_NAME, BASE_URL


def _send(to_email: str, subject: str, html_body: str):
    """Низкоуровневая отправка через Gmail SMTP SSL."""
    if not GMAIL_USER or not GMAIL_PASSWORD:
        
        logging.warning(f"[EMAIL] Почта не настроена. Письмо НЕ отправлено.")
        logging.info(f"[EMAIL] Кому: {to_email}")
        logging.info(f"[EMAIL] Тема: {subject}")
        return

    msg = MIMEMultipart("alternative")
    msg["From"]    = f"{APP_NAME} <{GMAIL_USER}>"
    msg["To"]      = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        logging.info(f"[EMAIL] ✅ Отправлено → {to_email}")
    except smtplib.SMTPAuthenticationError:
        logging.error("[EMAIL] ❌ Ошибка авторизации Gmail. Проверь GMAIL_USER и GMAIL_PASSWORD в .env")
    except Exception as e:
        logging.error(f"[EMAIL] ❌ Ошибка отправки: {e}")


def _base_template(title: str, content: str) -> str:
    
    return f"""
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#010528;font-family:'Helvetica Neue',Arial,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#010528;padding:40px 20px">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0"
             style="background:rgba(0,32,96,0.4);border:1px solid rgba(0,153,255,0.2);border-radius:20px;overflow:hidden">

        <!-- Header -->
        <tr>
          <td style="padding:32px 40px 24px;border-bottom:1px solid rgba(0,153,255,0.15)">
            <div style="font-size:22px;font-weight:700;color:#ffffff;letter-spacing:-0.5px">
              📚 {APP_NAME}
            </div>
          </td>
        </tr>

        <!-- Content -->
        <tr>
          <td style="padding:32px 40px">
            <h2 style="font-size:20px;font-weight:600;color:#E8F4FF;margin:0 0 16px">{title}</h2>
            {content}
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding:20px 40px;border-top:1px solid rgba(0,153,255,0.1)">
            <p style="font-size:12px;color:#7EB3D8;margin:0">
              Это письмо отправлено автоматически. Не отвечайте на него.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""


def send_verification_email(to_email: str, name: str, token: str):
    """Письмо с ссылкой подтверждения email при регистрации."""
    verify_url = f"{BASE_URL}/api/auth/verify?token={token}"

    content = f"""
    <p style="color:#a0c4e0;font-size:15px;margin:0 0 20px;line-height:1.6">
        Привет, <strong style="color:#E8F4FF">{name}</strong>!<br>
        Для завершения регистрации подтверди свой email.
    </p>

    <div style="text-align:center;margin:28px 0">
      <a href="{verify_url}"
         style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#0057A8,#003580);
                color:#ffffff;text-decoration:none;border-radius:12px;font-weight:600;font-size:15px;
                letter-spacing:0.3px">
        ✅ Подтвердить email
      </a>
    </div>

    <p style="color:#7EB3D8;font-size:13px;margin:20px 0 0;line-height:1.5">
      Ссылка действует <strong>24 часа</strong>.<br>
      Если ты не регистрировался — просто проигнорируй это письмо.
    </p>

    <div style="margin-top:20px;padding:12px 16px;background:rgba(0,75,142,0.2);
                border-radius:10px;border:1px solid rgba(0,153,255,0.15)">
      <p style="color:#7EB3D8;font-size:11px;margin:0;word-break:break-all">
        Или скопируй ссылку: {verify_url}
      </p>
    </div>
    """

    _send(to_email, f"Подтвердите email — {APP_NAME}", _base_template("Подтверждение email", content))


def send_reset_email(to_email: str, name: str, token: str):
    """Письмо со ссылкой сброса пароля."""
    reset_url = f"{BASE_URL}/reset-password?token={token}"

    content = f"""
    <p style="color:#a0c4e0;font-size:15px;margin:0 0 20px;line-height:1.6">
        Привет, <strong style="color:#E8F4FF">{name}</strong>!<br>
        Мы получили запрос на сброс пароля для твоего аккаунта.
    </p>

    <div style="text-align:center;margin:28px 0">
      <a href="{reset_url}"
         style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#B91C1C,#7F1D1D);
                color:#ffffff;text-decoration:none;border-radius:12px;font-weight:600;font-size:15px">
        🔑 Сбросить пароль
      </a>
    </div>

    <p style="color:#7EB3D8;font-size:13px;margin:20px 0 0;line-height:1.5">
      Ссылка действует <strong>30 минут</strong>.<br>
      Если ты не запрашивал сброс — просто проигнорируй это письмо.
    </p>
    """

    _send(to_email, f"Сброс пароля — {APP_NAME}", _base_template("Сброс пароля", content))


def send_welcome_email(to_email: str, name: str):
    """Приветственное письмо после подтверждения email."""
    content = f"""
    <p style="color:#a0c4e0;font-size:15px;margin:0 0 20px;line-height:1.6">
        🎉 Добро пожаловать, <strong style="color:#E8F4FF">{name}</strong>!<br>
        Твой аккаунт успешно подтверждён.
    </p>

    <p style="color:#a0c4e0;font-size:14px;margin:0 0 16px;line-height:1.6">
        Теперь ты можешь:
    </p>

    <ul style="color:#a0c4e0;font-size:14px;line-height:1.8;padding-left:20px;margin:0 0 24px">
      <li>🎙️ Записывать лекции прямо в браузере</li>
      <li>📤 Загружать аудиофайлы (MP3, WAV, M4A)</li>
      <li>✨ Получать AI-структурированные конспекты</li>
    </ul>

    <div style="text-align:center;margin:24px 0">
      <a href="{BASE_URL}"
         style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#0057A8,#003580);
                color:#ffffff;text-decoration:none;border-radius:12px;font-weight:600;font-size:15px">
        Открыть NoteFlow →
      </a>
    </div>
    """

    _send(to_email, f"Добро пожаловать в {APP_NAME}! 🎉", _base_template(f"Добро пожаловать!", content))
