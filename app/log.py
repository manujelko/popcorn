import logging
import os
from pathlib import Path

import structlog

from .env import LOG_LEVEL


def set_process_id(_, __, event_dict):
    event_dict["process_id"] = os.getpid()
    return event_dict


level = getattr(logging, LOG_LEVEL)
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(level),
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        set_process_id,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.WriteLoggerFactory(
        file=Path("app").with_suffix(".log").open("wt")
    ),
)
logger: structlog.stdlib.BoundLogger = structlog.get_logger()
