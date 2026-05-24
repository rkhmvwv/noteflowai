# NoteFlow AI

Приложение для транскрибации и структурирования лекций с помощью OpenAI Whisper + GPT-4o.

## Быстрый старт

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Вставить API ключ в .env
OPENAI_API_KEY=sk-...

# 3. Запустить
python run.py

# 4. Открыть http://localhost:8000
```

## Возможности

| Функция | Описание |
|---|---|
| 🎙️ Запись | Запись лекции с микрофона прямо в браузере |
| 📤 Загрузка | MP3, WAV, M4A, OGG, WEBM — перетащить или выбрать |
| 📝 Транскрипция | OpenAI Whisper, оптимизировано для русского языка |
| ✨ Структурирование | GPT-4o с retry при ошибках |
| 💾 Хранилище | Сохраняется в `data/notes.json`, не теряется при перезапуске |
| 🔍 Поиск | Поиск по заголовку, описанию и резюме |
| 📥 Экспорт | Выгрузка конспекта в TXT |
| 🗑️ Удаление | Удаление конспектов из интерфейса |

## Структура проекта

```
NoteFlowAI/
├── run.py               # Точка входа
├── .env                 # API ключ (не коммитить!)
├── requirements.txt
├── app/
│   ├── main.py          # FastAPI приложение, CORS, lifecycle
│   ├── config.py        # Конфиг с валидацией ключа
│   ├── api/routes.py    # Эндпоинты: upload, notes, delete
│   ├── db/storage.py    # JSON хранилище с блокировкой
│   └── services/
│       ├── transcription.py   # Whisper
│       └── structuring.py     # GPT-4o с retry
├── frontend/index.html  # SPA интерфейс
├── data/                # notes.json (создаётся автоматически)
└── temp_audio/          # Временные файлы (удаляются после обработки)
```
