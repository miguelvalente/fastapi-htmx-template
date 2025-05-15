import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import structlog
from rich.console import Console
from structlog.processors import format_exc_info

LOG_FILE = Path(os.environ["LOG_FILE"])
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


# Map log levels to Rich color
LEVEL_COLOR_MAP = {
    "DEBUG": "blue",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold red",
}

# Shared processors for Structlog
shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
    structlog.processors.dict_tracebacks,
    format_exc_info,
]

console = Console()


def rich_renderer(_, __, event_dict):
    from pydantic import BaseModel

    # Separate Pydantic models from other fields
    models = []
    for key, val in list(event_dict.items()):
        if isinstance(val, BaseModel):
            models.append(val)
            del event_dict[key]
    timestamp = event_dict.get("timestamp", "")
    level = event_dict.get("level", "").upper()

    # message = event_dict.get("event", "")
    message = (
        event_dict.get("event", "")
        or event_dict.get("exception", "")
        or event_dict.get("traceback", "")
    )
    # Colorize the level
    color = LEVEL_COLOR_MAP.get(level, "white")
    level_styled = f"[{color}]{level}[/]"
    # Print main log line
    console.print(f"{timestamp} [{level_styled:<7}] {message}")
    # Print any Pydantic models with indentation and spacing
    for i, model in enumerate(models):
        if i > 0:
            console.print()  # Blank line before subsequent models
        console.print(model)
    return ""


# Console (stdout) handler with a custom Rich renderer
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    structlog.stdlib.ProcessorFormatter(
        processor=rich_renderer,
        foreign_pre_chain=shared_processors,
    )
)

# Replace FileHandler with TimedRotatingFileHandler
file_handler = TimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",  # Rotate at midnight
    interval=1,  # Once per day
    backupCount=30,  # Keep 30 days of logs
)
file_handler.setFormatter(
    structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )
)

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    # handlers=[console_handler, file_handler],
    handlers=[console_handler],
)

structlog.configure(
    processors=shared_processors
    + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def main():
    from pydantic import BaseModel

    class ExampleModel(BaseModel):
        step: str
        query: str
        iteration: int

    example = ExampleModel(
        step="ReasonNextSteps", query="What vulnerabilities exist?", iteration=1
    )
    logger.info(
        "Testing structured log with Pydantic model", model=example, model2=example
    )
    logger.error(
        "Testing structured log with Pydantic model", model=example, model2=example
    )
    logger.warning(
        "Testing structured log with Pydantic model", model=example, model2=example
    )
