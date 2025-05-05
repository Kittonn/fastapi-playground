from structlog.types import EventDict, Processor
from structlog.processors import CallsiteParameter
from structlog.stdlib import BoundLogger
from enum import Enum
from config.environment import config
import structlog
import logging
import sys

# https://github.com/VendiTech/vendi/blob/022f4e366966072a34b265b04e471831402492ce/mspy_vendi/core/logger.py


class LogFormat(str, Enum):
  JSON = "json",
  CONSOLE = "console"


class Logger:
  def __init__(self, log_level: str = "INFO", log_format: LogFormat = LogFormat.CONSOLE):
    self.log_level = log_level
    self.log_format = log_format

  @staticmethod
  def rename_event_key(_, __, event_dict: EventDict) -> EventDict:
    event_dict["message"] = event_dict.pop("event")

    return event_dict

  @staticmethod
  def drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
    event_dict.pop("color_message", None)

    return event_dict

  def get_processors(self) -> list[Processor]:
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    processors = [
      structlog.contextvars.merge_contextvars,
      structlog.stdlib.add_log_level,
      structlog.stdlib.add_logger_name,
      structlog.stdlib.PositionalArgumentsFormatter(),
      self.drop_color_message_key,
      timestamper,
      structlog.processors.UnicodeDecoder(),
      structlog.processors.StackInfoRenderer(),
      structlog.processors.CallsiteParameterAdder([
        CallsiteParameter.FILENAME,
        CallsiteParameter.FUNC_NAME,
        CallsiteParameter.LINENO
      ])
    ]

    if self.log_format == LogFormat.JSON:
      processors.append(self.rename_event_key)
      processors.append(structlog.processors.format_exc_info)

    return processors

  @staticmethod
  def clear_uvicorn_logger() -> None:
    for log in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
      logging.getLogger(log).handlers.clear()
      logging.getLogger(log).propagate = True

  @staticmethod
  def configure_structlog(processors: list[Processor]) -> None:
    structlog.configure(
      processors=processors + [
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter
      ],
      logger_factory=structlog.stdlib.LoggerFactory(),
      cache_logger_on_first_use=True
    )

  def configure_logging(self, processors: list[Processor]) -> logging.Logger:
    if self.log_format == LogFormat.JSON:
      renderer = structlog.processors.JSONRenderer()
    else:
      renderer = structlog.dev.ConsoleRenderer(colors=True)

    formatter = structlog.stdlib.ProcessorFormatter(
      foreign_pre_chain=processors,
      processors=[
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        renderer
      ],
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()

    if hasattr(root_logger, "addHandler"):
      root_logger.addHandler(handler)

    root_logger.setLevel(self.log_level.upper())

    return root_logger

  def configure(self) -> None:
    shared_processors = self.get_processors()
    self.configure_structlog(shared_processors)
    root_logger = self.configure_logging(shared_processors)
    self.clear_uvicorn_logger()

    def handle_exception(exc_type, exc_value, exc_traceback):
      if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

      root_logger.error("Uncaught exception", exc_info=(
        exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

  def setup_logging(self) -> BoundLogger:
    self.configure()

    return structlog.get_logger()


# log = Logger().setup_logging()