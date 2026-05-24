from app.services.transcription import transcribe
from app.services.structuring import structure

async def process_audio(job_id, file_path):
    transcript = await transcribe(file_path)
    note = await structure(transcript)
    print(note)
