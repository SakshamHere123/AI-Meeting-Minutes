# 📝 AI Meeting Minutes Generator

An automated pipeline that converts raw meeting audio into structured, professional meeting minutes — including a summary, key decisions, and action items with owners and deadlines.

Built using **OpenAI Whisper** for transcription and **LangChain + GPT** for structured summarization, exposed via a **FastAPI** backend and a **Streamlit** demo UI.

---

## Demo

> *(Insert a GIF or screen recording of the Streamlit app here — drag-drop audio → generated minutes)*

---

## Features

- 🎙️ **High-fidelity transcription** using OpenAI's Whisper API, with automatic chunking for audio files over the 25MB API limit
- 🧠 **Structured extraction** via LangChain + GPT: summary, key decisions, attendees, and action items (task / owner / deadline) — enforced through a strict Pydantic schema, not free-text parsing
- 📄 **Auto-generated deliverables** in both Markdown and Word (`.docx`) formats
- ⚡ **REST API** (FastAPI) for programmatic use, plus interactive Swagger docs
- 🖥️ **Streamlit UI** for drag-and-drop demo usage with live timing breakdown

---

## Architecture

```
Audio File (.mp3/.wav/.m4a)
        │
        ▼
┌───────────────────┐
│  Whisper API       │  → chunks audio if >25MB, transcribes each chunk
│  (transcription.py)│
└─────────┬──────────┘
          │ raw transcript
          ▼
┌───────────────────┐
│  LangChain + GPT   │  → extracts summary, decisions, action items
│  (summarizer.py)   │     into a strict Pydantic schema
└─────────┬──────────┘
          │ structured JSON
          ▼
┌───────────────────┐
│  Formatter          │  → renders Markdown + Word (.docx)
│  (formatter.py)    │
└─────────┬──────────┘
          │
          ▼
   outputs/minutes/*.md, *.docx
```

All stages are orchestrated by `src/pipeline.py`, exposed through `app/main.py` (FastAPI) and `app/streamlit_app.py` (UI).

---

## Tech Stack

| Component | Technology |
|---|---|
| Transcription | OpenAI Whisper API |
| Summarization | LangChain + OpenAI GPT (gpt-4o-mini) |
| Structured output | Pydantic |
| Audio processing | pydub + ffmpeg |
| Backend API | FastAPI |
| UI | Streamlit |
| Document generation | python-docx |

---

## Project Structure

```
ai-meeting-minutes/
├── src/
│   ├── config.py          # env vars & constants
│   ├── transcription.py   # Whisper transcription + chunking
│   ├── summarizer.py      # LangChain summarization chain
│   ├── formatter.py       # Markdown/Word output generation
│   └── pipeline.py        # orchestrates the full pipeline
├── app/
│   ├── main.py             # FastAPI app
│   └── streamlit_app.py    # Streamlit demo UI
├── data/
│   ├── raw_audio/          # uploaded audio
│   └── transcripts/        # saved transcripts
├── outputs/
│   └── minutes/            # generated minutes (.md / .docx)
└── requirements.txt
```

---

## Setup

1. **Clone & create a virtual environment**
```bash
   git clone <your-repo-url>
   cd ai-meeting-minutes
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
   pip install -r requirements.txt
```
   Also requires `ffmpeg` installed system-wide (`brew install ffmpeg` / `apt install ffmpeg`).

3. **Add your OpenAI API key**
   Create a `.env` file in the project root:
```
   OPENAI_API_KEY=your_key_here
```

---

## Usage

### Option 1 — Streamlit UI (recommended for demo)
```bash
streamlit run app/streamlit_app.py
```
Upload an audio file, click **Generate Minutes**, view results, and download `.md`/`.docx`.

### Option 2 — FastAPI
```bash
uvicorn app.main:app --reload
```
Visit `http://127.0.0.1:8000/docs` for interactive API docs, or:
```bash
curl -X POST "http://127.0.0.1:8000/generate-minutes" \
  -F "file=@data/raw_audio/sample.mp3"
```

### Option 3 — Run the pipeline directly in Python
```python
from src.pipeline import run_pipeline

result = run_pipeline("data/raw_audio/sample.mp3")
print(result["minutes"].summary)
```

---

## Output Example

```json
{
  "title": "Q3 Roadmap Planning",
  "summary": "The team discussed Q3 priorities, agreeing to focus on the mobile app redesign...",
  "key_decisions": [
    "Legacy dashboard feature dropped from Q3 scope"
  ],
  "action_items": [
    {"task": "Prepare wireframes", "owner": "Priya", "deadline": "Next Friday"},
    {"task": "Backend API changes", "owner": "Raj", "deadline": "Two weeks"}
  ]
}
```

---

## Future Improvements
- Speaker diarization (who said what)
- PDF export option
- Persistent storage with a database instead of local files
- Slack/email auto-delivery of generated minutes

---

## License
MIT