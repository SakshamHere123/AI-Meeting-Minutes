import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Add it to your .env file.")

WHISPER_MODEL = "whisper-1"
LLM_MODEL = "gpt-4o-mini"   # cheap + good enough for summarization

RAW_AUDIO_DIR = "data/raw_audio"
TRANSCRIPTS_DIR = "data/transcripts"
MINUTES_DIR = "outputs/minutes"

MAX_AUDIO_SIZE_MB = 25   # Whisper API hard limit