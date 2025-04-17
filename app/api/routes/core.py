import logging
from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter()

openai_client = OpenAI()

class WelcomeResponse(BaseModel):
    message: str
    time: str

class TaskCategoryResponseFormat(BaseModel):
    """Extract the category if task from user prompt."""
    task: str = Field(description="type of task to be performed. [general conversation, summarization, comparison, data analysis and forecast, file Q&A]")
    confidence_score: float = Field(description="Confidence score between 0 and 1")

class UserInput(BaseModel):
    prompt: str
    task: Optional[str] = None
    files: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Summarize the following document: quarterly_report.pdf",
                "task": None,
                "files": ["quarterly_report.pdf"]
            }
        }


@router.get("/")
def read_root():
    return WelcomeResponse(
        message="Welcome to the JCS Bot!",
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@router.post("/chat")
def classify_prompt(data: UserInput):
    if not data.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    logger.info("Starting Task extraction analysis")
    logger.debug(f"Input text: {data}")
    completion = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"\nYou are a helpful assistant that classifies user prompts into task categories.\n\n"
                "The task categories are: general conversation, summarization, comparison, data analysis and forecast, file Q&A.\n\n"
                "Use the additional optional context information such as task and files to help classify the task.\n\n"
                "If the task is not clear, respond with 'unknown'.\n\n"},
            {"role": "user", "content": f"{data.prompt}, files: {data.files}, task: {data.task}"},
        ],
        response_format=TaskCategoryResponseFormat,
    )
    result = completion.choices[0].message.parsed
    logger.info(
        f"Extraction complete - task Category: {result.task}, Confidence: {result.confidence_score:.2f}"
    )
    if result.task == "unknown":
        raise HTTPException(status_code=400, detail="Please provide a valid prompt. Insufficient context.")
    elif result.task == "general conversation":
        response = openai_client.responses.create(
            model="gpt-3.5-turbo",
            instructions="You are an enterprise assistant that helps users with their queries. Maintain a balance between being informative and concise.",
            input=data.prompt,
        )
        return {"response": response.output_text}
    elif result.task == "summarization":
        pass
    
    return result