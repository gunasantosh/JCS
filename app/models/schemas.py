from pydantic import BaseModel, Field
from typing import Optional, List


class WelcomeResponse(BaseModel):
    message: str
    time: str

class SecurityCheck(BaseModel):
    """Check for prompt injection or system manipulation attempts"""

    is_safe: bool = Field(description="Whether the input appears safe")
    risk_flags: Optional[list[str]] = Field(description="List of potential security concerns")

class TaskCategoryResponseFormat(BaseModel):
    """Extract the category if task from user prompt."""
    task: str = Field(description="Type of task [general conversation, summarization, comparison, data analysis and forecast, file Q&A]")
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
