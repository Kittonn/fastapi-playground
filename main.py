from fastapi import FastAPI
from routers import chat_router
from config.environment import config
from utils.logger import Logger
from contextlib import asynccontextmanager
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
  Logger().setup_logging()
  yield


def create_app() -> FastAPI:
  app = FastAPI(lifespan=lifespan)

  app.include_router(chat_router.router)

  return app


app = create_app()


if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=config.port)
