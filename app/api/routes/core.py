from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import WelcomeResponse, UserInput
from app.utils.guardrails import validate_user_input
from openai import OpenAI
from dotenv import load_dotenv

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
def classify_prompt(data: UserInput):
    task_info = validate_user_input(data)

    if task_info.task == "general conversation":
        response = openai_client.responses.create(
            model="gpt-3.5-turbo",
            instructions="You are JCS Bot, an enterprise assistant. Be concise and informative.",
            input=data.prompt,
        )
        return {"response": response.output_text}

    # Other task handling can go here...

    return task_info

