from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from typing import Callable, Awaitable
from utils.logger import log
import uuid
import structlog


class LoggingMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
    structlog.contextvars.bind_contextvars(
      request_id=self.generate_request_id()
    )

    body = await request.json()

    log.info(
      f"Request: {request.method} {request.url}",
      headers=dict(request.headers),
      body=body,
      type="request"
    )

    response = await call_next(request)

    content_type = response.headers.get("content-type", "")
    is_streaming = content_type.startswith("text/event-stream")
    print(is_streaming)

    if is_streaming:
      async def logging_wrapper():
        full_body = []
        async for chunk in response.body_iterator:
          log.debug(f"Streaming chunk: {chunk.decode()}")
          yield chunk

          full_body.append(chunk)

        log.info(
          f"Response status: {response.status_code}",
          headers=response.headers,
          body=b"".join(full_body),
          type="response"
        )

      return StreamingResponse(
        content=logging_wrapper(),
        status_code=response.status_code,
        media_type=response.media_type,
        headers=dict(response.headers)
      )
    else:
      response_body = []
      async for chunk in response.body_iterator:
        response_body.append(chunk)

      response_body_bytes = b"".join(response_body)

      log.info(
        f"Response status: {response.status_code}",
        headers=response.headers,
        body=response_body_bytes.decode(),
        type="response"
      )

      new_response = Response(
        content=response_body_bytes,
        status_code=response.status_code,
        headers=dict(response.headers),
      )

      return new_response

  def generate_request_id(self) -> str:
    request_id = str(uuid.uuid4())

    return request_id
