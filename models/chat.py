from pydantic import BaseModel
from enum import Enum


class ChatMode(str, Enum):
  SINGLE_SHOT = "single_shot",
  STREAM = "stream"


class ChatRequest(BaseModel):
  prompt: str
  mode: ChatMode = ChatMode.STREAM
