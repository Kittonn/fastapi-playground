from fastapi import APIRouter
from models.chat import ChatRequest, ChatMode
from fastapi.responses import StreamingResponse
from services.chat_service import fake_event_stream
# from utils.logger import log

router = APIRouter(
  prefix="/chat",
  tags=["Chat"]
)


@router.post("/")
async def chat(chat_request: ChatRequest):
  # log.info(f"request body is {chat_request}")
  if chat_request.mode == ChatMode.STREAM:
    return StreamingResponse(fake_event_stream(), media_type="text/event-stream")

  return {
    "message": "Hello, World!"
  }
