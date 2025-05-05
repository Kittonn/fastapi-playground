import asyncio


class ChatService:
  async def fake_event_stream(self):
    for i in range(10):
      yield f"data: message {i}\n\n"
      await asyncio.sleep(1)
