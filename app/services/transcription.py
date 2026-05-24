from pathlib import Path

from openai import AsyncOpenAI

from app.config import OPENAI_API_KEY


client = AsyncOpenAI(
    api_key=OPENAI_API_KEY
)


async def transcribe(file_path: str) -> str:
    path = Path(file_path)

    webm_path = path.with_suffix(".webm")

    if path != webm_path:
        path.rename(webm_path)
        path = webm_path

    with open(path, "rb") as f:
        resp = await client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.webm", f, "audio/webm"),
            language="ru",
            response_format="text"
        )

    return resp