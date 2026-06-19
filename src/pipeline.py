import os
import time

from src.transcription import transcribe_audio
from src.summarizer import summarize_transcript
from src.formatter import save_minutes


def run_pipeline(audio_path: str, formats=("md", "docx")) -> dict:
    """
    Full end-to-end pipeline:
    audio file -> transcript -> structured summary -> formatted minutes

    Returns a dict with:
      - transcript (str)
      - minutes (MeetingMinutes object)
      - saved_files (dict of format -> filepath)
      - timing (dict of stage -> seconds taken)
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    timing = {}
    base_filename = os.path.splitext(os.path.basename(audio_path))[0]

    # Stage 1: Transcription
    print("=" * 50)
    print("STAGE 1: Transcribing audio...")
    print("=" * 50)
    t0 = time.time()
    transcript = transcribe_audio(audio_path, save=True)
    timing["transcription_sec"] = round(time.time() - t0, 2)
    print(f"Done in {timing['transcription_sec']}s\n")

    # Stage 2: Summarization
    print("=" * 50)
    print("STAGE 2: Extracting summary & action items...")
    print("=" * 50)
    t0 = time.time()
    minutes = summarize_transcript(transcript)
    timing["summarization_sec"] = round(time.time() - t0, 2)
    print(f"Done in {timing['summarization_sec']}s\n")

    # Stage 3: Formatting & saving
    print("=" * 50)
    print("STAGE 3: Formatting & saving minutes...")
    print("=" * 50)
    t0 = time.time()
    saved_files = save_minutes(minutes, base_filename=base_filename, formats=formats)
    timing["formatting_sec"] = round(time.time() - t0, 2)
    print(f"Done in {timing['formatting_sec']}s\n")

    timing["total_sec"] = round(sum(timing.values()), 2)

    print("=" * 50)
    print(f"PIPELINE COMPLETE in {timing['total_sec']}s")
    print("=" * 50)

    return {
        "transcript": transcript,
        "minutes": minutes,
        "saved_files": saved_files,
        "timing": timing
    }


if __name__ == "__main__":
    # quick manual test — point this to a real audio file
    test_audio = "data/raw_audio/sample.mp3"

    result = run_pipeline(test_audio)

    print("\n--- FINAL SUMMARY ---")
    print(result["minutes"].summary)

    print("\n--- ACTION ITEMS ---")
    for item in result["minutes"].action_items:
        print(f"- {item.task} | Owner: {item.owner} | Deadline: {item.deadline}")

    print("\n--- TIMING ---")
    print(result["timing"])

    print("\n--- SAVED FILES ---")
    print(result["saved_files"])