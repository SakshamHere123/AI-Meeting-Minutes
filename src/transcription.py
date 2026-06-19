import os
import math
from pydub import AudioSegment
from openai import OpenAI

from src.config import OPENAI_API_KEY, WHISPER_MODEL, MAX_AUDIO_SIZE_MB, TRANSCRIPTS_DIR

client = OpenAI(api_key=OPENAI_API_KEY)


def get_file_size_mb(filepath: str) -> float:
    return os.path.getsize(filepath) / (1024 * 1024)


def chunk_audio(filepath: str, chunk_length_ms: int = 10 * 60 * 1000) -> list[str]:
    """
    Splits audio into chunks (default 10 min each) if the file is too large.
    Returns list of chunk file paths. If file is small enough, returns [filepath].
    """
    if get_file_size_mb(filepath) <= MAX_AUDIO_SIZE_MB:
        return [filepath]

    print(f"File exceeds {MAX_AUDIO_SIZE_MB}MB, chunking...")
    audio = AudioSegment.from_file(filepath)
    total_chunks = math.ceil(len(audio) / chunk_length_ms)

    chunk_paths = []
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    chunk_dir = os.path.join(os.path.dirname(filepath), f"{base_name}_chunks")
    os.makedirs(chunk_dir, exist_ok=True)

    for i in range(total_chunks):
        start = i * chunk_length_ms
        end = min((i + 1) * chunk_length_ms, len(audio))
        chunk = audio[start:end]

        chunk_path = os.path.join(chunk_dir, f"{base_name}_part{i+1}.mp3")
        chunk.export(chunk_path, format="mp3")
        chunk_paths.append(chunk_path)

    print(f"Created {len(chunk_paths)} chunks.")
    return chunk_paths


def transcribe_chunk(filepath: str) -> str:
    """Sends a single audio chunk to Whisper API and returns transcribed text."""
    with open(filepath, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=audio_file,
            response_format="text"
        )
    return response


def transcribe_audio(filepath: str, save: bool = True) -> str:
    """
    Full pipeline: chunk audio if needed, transcribe each chunk,
    stitch together into one transcript.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Audio file not found: {filepath}")

    chunks = chunk_audio(filepath)
    full_transcript = []

    for idx, chunk_path in enumerate(chunks, start=1):
        print(f"Transcribing chunk {idx}/{len(chunks)}...")
        text = transcribe_chunk(chunk_path)
        full_transcript.append(text.strip())

    transcript = "\n".join(full_transcript)

    if save:
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        out_path = os.path.join(TRANSCRIPTS_DIR, f"{base_name}.txt")
        os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"Transcript saved to {out_path}")

    return transcript


if __name__ == "__main__":
    # quick manual test
    test_file = "data/raw_audio/sample.mp3"
    result = transcribe_audio(test_file)
    print("\n--- TRANSCRIPT ---\n")
    print(result)