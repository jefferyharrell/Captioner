from fastapi import APIRouter
from app.schemas import LoginRequest
import os

router = APIRouter()

@router.post("/login", operation_id="login_post")
def login(data: LoginRequest) -> dict[str, bool]:
    password = os.environ.get("PASSWORD", "letmein")
    if data.password == password:
        return {"success": True}
    return {"success": False}
