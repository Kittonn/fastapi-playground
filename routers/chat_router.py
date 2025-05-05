from fastapi import APIRouter, Depends
from models.chat import ChatRequest, ChatMode
from fastapi.responses import StreamingResponse
from services.chat_service import ChatService
from typing import Annotated
from utils.logger import log

router = APIRouter(
  prefix="/chat",
  tags=["Chat"]
)


@router.post("/")
async def chat(
  chat_request: ChatRequest,
  chat_service: Annotated[ChatService, Depends()]
):
  log.info(f"chat router")
  if chat_request.mode == ChatMode.STREAM:
    return StreamingResponse(chat_service.fake_event_stream(), media_type="text/event-stream")

  return {
    "message": "Hello, World!"
  }
