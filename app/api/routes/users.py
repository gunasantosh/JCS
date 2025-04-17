from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/")
def get_users():
    return [{"id": 1, "name": "Alice"}]

@router.get("/{user_id}")
def get_user(user_id: int):
    return {"id": user_id, "name": "Bob"}
