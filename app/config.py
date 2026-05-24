import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SECRET_KEY     = os.getenv("SECRET_KEY", "change-me-please-32-chars-minimum!")
APP_NAME       = os.getenv("APP_NAME", "NoteFlow AI")
BASE_URL       = os.getenv("BASE_URL", "http://localhost:8000")


GMAIL_USER     = os.getenv("GMAIL_USER", "")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "")  

if not OPENAI_API_KEY:
    logging.critical("❌ OPENAI_API_KEY не задан в .env!")
    sys.exit(1)

if SECRET_KEY == "change-me-please-32-chars-minimum!":
    logging.warning("⚠️  SECRET_KEY не изменён — смените перед деплоем!")
