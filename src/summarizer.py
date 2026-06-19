import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

from src.config import OPENAI_API_KEY, LLM_MODEL


# ---------- Schema ----------

class ActionItem(BaseModel):
    task: str = Field(description="The specific action/task to be done")
    owner: str = Field(description="Person responsible, or 'Unassigned' if unclear")
    deadline: str = Field(description="Deadline if mentioned, else 'Not specified'")


class MeetingMinutes(BaseModel):
    title: str = Field(description="A short, descriptive meeting title")
    summary: str = Field(description="A concise 3-5 sentence summary of the meeting")
    key_decisions: List[str] = Field(description="List of decisions made during the meeting")
    action_items: List[ActionItem] = Field(description="List of action items with owner and deadline")
    attendees: List[str] = Field(description="Names mentioned as participants, empty list if none identifiable")


# ---------- Chain setup ----------

parser = PydanticOutputParser(pydantic_object=MeetingMinutes)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert executive assistant who writes precise, professional meeting minutes. "
     "Extract only what is explicitly said or strongly implied in the transcript. "
     "Do not invent names, deadlines, or decisions that are not present."),
    ("human",
     "Here is a raw meeting transcript:\n\n{transcript}\n\n"
     "Extract structured meeting minutes from it.\n\n{format_instructions}")
])

llm = ChatOpenAI(
    model=LLM_MODEL,
    temperature=0,
    api_key=OPENAI_API_KEY
)

chain = prompt | llm | parser


# ---------- Public function ----------

def summarize_transcript(transcript: str) -> MeetingMinutes:
    """
    Runs the LangChain summarization chain on a transcript.
    Returns a MeetingMinutes pydantic object.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Transcript is empty, cannot summarize.")

    result = chain.invoke({
        "transcript": transcript,
        "format_instructions": parser.get_format_instructions()
    })
    return result


def summarize_to_dict(transcript: str) -> dict:
    """Convenience wrapper that returns plain dict/JSON instead of pydantic object."""
    minutes = summarize_transcript(transcript)
    return minutes.model_dump()


if __name__ == "__main__":
    # quick manual test
    sample_transcript = """
    John: Alright team, let's kick off. We need to finalize the Q3 roadmap.
    Priya: I think we should prioritize the mobile app redesign first.
    John: Agreed. Priya, can you have the wireframes ready by next Friday?
    Priya: Yes, I'll get that done.
    Raj: I'll handle backend API changes, should take about two weeks.
    John: Great, let's also decide — we're dropping the legacy dashboard feature.
    Priya: Confirmed, removing it from this quarter's scope.
    John: Perfect. Let's reconvene next week.
    """

    minutes = summarize_transcript(sample_transcript)
    print(json.dumps(minutes.model_dump(), indent=2))