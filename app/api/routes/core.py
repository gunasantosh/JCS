from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

class WelcomeResponse(BaseModel):
    message: str
    time: str

@router.get("/")
def read_root():
    return WelcomeResponse(
        message="Welcome to the JCS Bot!",
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@router.post("/chat")
def chat():
    return {"message": "Chat endpoint"}