import os
import shutil
import sys

# allow imports from src/ when running uvicorn from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from src.pipeline import run_pipeline
from src.config import RAW_AUDIO_DIR

app = FastAPI(
    title="AI Meeting Minutes Generator",
    description="Upload a meeting audio file and get structured minutes with action items.",
    version="1.0.0"
)

ALLOWED_EXTENSIONS = {".mp3", ".mp4", ".wav", ".m4a", ".webm", ".mpeg", ".mpga"}


@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Meeting Minutes Generator is running."}


@app.post("/generate-minutes")
async def generate_minutes(file: UploadFile = File(...)):
    """
    Upload an audio file. Returns structured meeting minutes (JSON)
    and saves .md/.docx versions to outputs/minutes/.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}"
        )

    os.makedirs(RAW_AUDIO_DIR, exist_ok=True)
    save_path = os.path.join(RAW_AUDIO_DIR, file.filename)

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")

    try:
        result = run_pipeline(save_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

    return JSONResponse(content={
        "title": result["minutes"].title,
        "summary": result["minutes"].summary,
        "key_decisions": result["minutes"].key_decisions,
        "action_items": [item.model_dump() for item in result["minutes"].action_items],
        "attendees": result["minutes"].attendees,
        "timing": result["timing"],
        "files": result["saved_files"]
    })


@app.get("/download/{filename}")
def download_file(filename: str):
    """Download a generated minutes file (.md or .docx) by filename."""
    filepath = os.path.join("outputs/minutes", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath, filename=filename)