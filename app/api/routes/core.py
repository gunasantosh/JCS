from fastapi import APIRouter, Form, UploadFile, File, Request
from typing import List, Optional
from datetime import datetime
from app.models.schemas import WelcomeResponse
from app.utils.guardrails import validate_user_input
from openai import OpenAI
from dotenv import load_dotenv
from app.services.summarization import summarize_document

load_dotenv()

router = APIRouter()
openai_client = OpenAI()


@router.get("/")
def read_root():
    return WelcomeResponse(
        message="Welcome to the JCS Bot!",
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@router.post("/chat")
async def chat(
    request: Request,
    prompt: str = Form(...),
    task: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    # Get task info
    print(f"Files: {[file.filename for file in files] if files else 'No files'}")
    task_info = validate_user_input(prompt, task, files)

    if task_info.task == "general conversation" and not files:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are JCS Bot, an enterprise assistant. Be concise and informative."},
                {"role": "user", "content": prompt}
            ],
        )
        return {"response": response.choices[0].message.content}

    elif task_info.task == "summarization" and files:
        return {"message": "Summarization task detected."}

    return {"message": "Task not recognized or unsupported."}
