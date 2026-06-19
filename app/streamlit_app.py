import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.pipeline import run_pipeline
from src.config import RAW_AUDIO_DIR

st.set_page_config(
    page_title="AI Meeting Minutes Generator",
    page_icon="📝",
    layout="centered"
)

st.title("AI Meeting Minutes Generator")
st.caption("Upload meeting audio → get transcript, summary, decisions, and action items automatically.")

uploaded_file = st.file_uploader(
    "Upload audio file",
    type=["mp3", "wav", "m4a", "mp4", "webm", "mpeg", "mpga"]
)

if uploaded_file is not None:
    os.makedirs(RAW_AUDIO_DIR, exist_ok=True)
    save_path = os.path.join(RAW_AUDIO_DIR, uploaded_file.name)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.audio(uploaded_file)

    if st.button("Generate Minutes", type="primary"):
        with st.spinner("Transcribing and summarizing... this may take a minute."):
            try:
                result = run_pipeline(save_path)
            except Exception as e:
                st.error(f"Pipeline failed: {e}")
                st.stop()

        minutes = result["minutes"]
        timing = result["timing"]

        st.success(f"Done in {timing['total_sec']}s")

        st.divider()
        st.subheader(minutes.title)

        if minutes.attendees:
            st.markdown("**Attendees:** " + ", ".join(minutes.attendees))

        st.markdown("### Summary")
        st.write(minutes.summary)

        st.markdown("### Key Decisions")
        if minutes.key_decisions:
            for d in minutes.key_decisions:
                st.markdown(f"- {d}")
        else:
            st.write("No formal decisions recorded.")

        st.markdown("### Action Items")
        if minutes.action_items:
            table_data = [
                {"Task": item.task, "Owner": item.owner, "Deadline": item.deadline}
                for item in minutes.action_items
            ]
            st.table(table_data)
        else:
            st.write("No action items identified.")

        st.divider()
        st.markdown("### Timing Breakdown")
        col1, col2, col3 = st.columns(3)
        col1.metric("Transcription", f"{timing['transcription_sec']}s")
        col2.metric("Summarization", f"{timing['summarization_sec']}s")
        col3.metric("Formatting", f"{timing['formatting_sec']}s")

        st.divider()
        st.markdown("### Download")
        saved_files = result["saved_files"]

        col_a, col_b = st.columns(2)
        if "md" in saved_files:
            with open(saved_files["md"], "rb") as f:
                col_a.download_button("Download Markdown", f, file_name=os.path.basename(saved_files["md"]))
        if "docx" in saved_files:
            with open(saved_files["docx"], "rb") as f:
                col_b.download_button("Download Word Doc", f, file_name=os.path.basename(saved_files["docx"]))