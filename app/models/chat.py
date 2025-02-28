from pydantic import BaseModel
from typing import List
from uuid import uuid4

class Message(BaseModel):
    role: str
    content: str

class ChatSession(BaseModel):
    session_id: str = str(uuid4())
    messages: List[Message] = []
    cv_data: dict = {}
