import json
import logging
import asyncio
from openai import AsyncOpenAI, APIError, RateLimitError
from app.config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """Ты — AI-ассистент для структурирования конспектов лекций.
На основе транскрипции лекции составь структурированный конспект и верни ТОЛЬКО валидный JSON без каких-либо пояснений.

Формат ответа:
{
  "title": "Название темы лекции (кратко и точно)",
  "description": "Краткое описание (1-2 предложения)",
  "concepts": ["концепция 1", "концепция 2"],
  "key_points": ["ключевой момент 1", "ключевой момент 2"],
  "important": ["важное замечание 1"],
  "summary": "Резюме лекции в 2-3 предложениях"
}

Правила:
- Если транскрипция короткая или нечёткая — делай всё равно, по тому что есть
- Все поля обязательны, списки должны содержать минимум 1 элемент
- Отвечай на том же языке, на котором лекция"""

MAX_RETRIES = 3
RETRY_DELAY = 2  

async def structure(transcript: str) -> dict:
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"Структурирование, попытка {attempt}/{MAX_RETRIES}")
            resp = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Транскрипция лекции:\n\n{transcript}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,  
                timeout=60,
            )

            raw = resp.choices[0].message.content
            result = json.loads(raw)

            
            return {
                "title": result.get("title") or "Без названия",
                "description": result.get("description") or "",
                "concepts": result.get("concepts") or [],
                "key_points": result.get("key_points") or [],
                "important": result.get("important") or [],
                "summary": result.get("summary") or "",
            }

        except json.JSONDecodeError as e:
            logging.error(f"GPT вернул невалидный JSON (попытка {attempt}): {e}")
            last_error = f"Ошибка разбора ответа AI: {e}"

        except RateLimitError:
            logging.warning(f"Rate limit OpenAI, ждём {RETRY_DELAY * attempt}с...")
            last_error = "Превышен лимит запросов OpenAI"
            await asyncio.sleep(RETRY_DELAY * attempt)

        except APIError as e:
            logging.error(f"OpenAI API ошибка (попытка {attempt}): {e}")
            last_error = f"Ошибка OpenAI API: {e}"
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY)

        except Exception as e:
            logging.error(f"Неожиданная ошибка структурирования: {e}")
            last_error = str(e)
            break

    raise RuntimeError(f"Не удалось структурировать после {MAX_RETRIES} попыток: {last_error}")
