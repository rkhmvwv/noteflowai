import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.services.transcription import transcribe
from app.services.structuring import structure
from app.db.storage import db_save, db_list, db_delete
from app.auth import get_current_user


router = APIRouter(prefix="/api")

MAX_SIZE = 25 * 1024 * 1024

SUPPORTED_EXTS = {
    '.flac', '.m4a', '.mp3', '.mp4', '.mpeg',
    '.mpga', '.oga', '.ogg', '.wav', '.webm'
}

TEMP_DIR = Path("temp_audio")


async def _cleanup(path: Path):
    try:
        if path.exists():
            path.unlink()
            logging.info(f"Temp удалён: {path.name}")
    except Exception as e:
        logging.warning(f"Не удалось удалить {path}: {e}")


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    job_id = str(uuid.uuid4())
    original_filename = file.filename or "audio.webm"
    file_ext = Path(original_filename).suffix.lower()
    mime = (file.content_type or "").lower()

   
    if not file_ext or file_ext == ".":
        if "webm" in mime:   file_ext = ".webm"
        elif "ogg" in mime:  file_ext = ".ogg"
        elif "mp4" in mime:  file_ext = ".mp4"
        elif "wav" in mime:  file_ext = ".wav"
        elif "mpeg" in mime: file_ext = ".mp3"
        else:                file_ext = ".webm"

    logging.info(f"[{job_id}] {user['email']} | {original_filename} | {file_ext}")

    if file_ext not in SUPPORTED_EXTS:
        raise HTTPException(400, f"Неподдерживаемый формат: {file_ext}")

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(400, "Файл пустой.")
    if len(content) > MAX_SIZE:
        mb = len(content) / 1024 / 1024
        raise HTTPException(400, f"Файл слишком большой ({mb:.1f} МБ). Максимум 25 МБ.")

    TEMP_DIR.mkdir(exist_ok=True)
    temp_path = TEMP_DIR / f"{job_id}{file_ext}"
    temp_path.write_bytes(content)

    try:
        transcript = await transcribe(str(temp_path))

        if not transcript or not transcript.strip():
            raise HTTPException(422, "Не удалось распознать речь.")

        note = await structure(transcript)
        note["transcript_length"] = len(transcript)

        
        await db_save(user["user_id"], job_id, note)

        logging.info(f"[{job_id}] ✅ «{note.get('title', '—')}» → {user['email']}")

        return {"job_id": job_id, "status": "success", "note": note}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"[{job_id}] ❌ {type(e).__name__}: {e}")
        raise HTTPException(500, f"Ошибка обработки: {str(e)}")
    finally:
        await _cleanup(temp_path)


@router.get("/notes")
async def get_notes(user: dict = Depends(get_current_user)):
    return {"notes": await db_list(user["user_id"])}


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: str,
    user: dict = Depends(get_current_user)
):
    deleted = await db_delete(user["user_id"], note_id)
    if not deleted:
        raise HTTPException(404, "Конспект не найден.")
    return {"status": "deleted"}