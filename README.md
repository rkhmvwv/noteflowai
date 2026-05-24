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
| 💾 Хранилище | Сохраняется в `data/notes.json`, не теряется при перезапуске |
| 🔍 Поиск | Поиск по заголовку, описанию и резюме |
| 📥 Экспорт | Выгрузка конспекта в TXT |
| 🗑️ Удаление | Удаление конспектов из интерфейса |

## Структура проекта

```
NoteFlowAI/
├── run.py               
├── .env                
├── requirements.txt
├── app/
│   ├── main.py          
│   ├── config.py        
│   ├── api/routes.py    
│   ├── db/storage.py    
│   └── services/
│       ├── transcription.py   
│       └── structuring.py     
├── frontend/index.html  
├── data/                
└── temp_audio/          
```
