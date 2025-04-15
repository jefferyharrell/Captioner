from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    password: str

class PhotoResponse(BaseModel):
    hash: str
    filename: str
    caption: Optional[str] = None
