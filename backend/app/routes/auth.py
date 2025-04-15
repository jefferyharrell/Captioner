from fastapi import APIRouter
from app.schemas import LoginRequest
import os

router = APIRouter()

@router.post("/login")
def login(data: LoginRequest):
    password = os.environ.get("PASSWORD", "letmein")
    if data.password == password:
        return {"success": True}
    return {"success": False}
