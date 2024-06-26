import logging
import os
import sys
import time
from os import environ

from logtail import LogtailHandler
from fastapi import Request

# Environment variable for Logtail token
TOKEN_REQUESTS = environ.get("TOKEN_REQUESTS", None)
uvicorn_logger = logging.getLogger("uvicorn")

# Define a formatter for logging
formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Configure the requests logger
requests_logger = logging.getLogger("requests")
requests_logger.setLevel(logging.INFO)

# Stream handler to log to stdout
stream_handler_2 = logging.StreamHandler(sys.stdout)
stream_handler_2.setFormatter(formatter)

# File handler to log to a file
file_handler_2 = logging.FileHandler(filename='requests.log', encoding='utf-8')
file_handler_2.setFormatter(formatter)

# Logtail handler to send logs to Logtail
logtail_handler_2 = LogtailHandler(source_token=TOKEN_REQUESTS)
logtail_handler_2.setFormatter(formatter)

# Add handlers to the requests logger
requests_logger.addHandler(stream_handler_2)
requests_logger.addHandler(file_handler_2)
requests_logger.addHandler(logtail_handler_2)


async def log_middleware(request: Request, call_next):
    """
    Middleware to log request details and processing time.

    Args:
        request (Request): The incoming request.
        call_next (function): The next middleware or endpoint.

    Returns:
        Response: The response from the next middleware or endpoint.
    """
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    log_dict = {
        "url": str(request.url),
        "method": request.method,
        "status": response.status_code,
        "process_time": process_time,
    }
    requests_logger.info(log_dict)
    return response


def get_uvicorn_logger_config():
    """
    Get the logger configuration for Uvicorn.

    Returns:
        dict: A dictionary containing the logger configuration.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s - %(message)s",
                "use_colors": None,
            },
            "custom": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
            },
            "file": {
                "formatter": "custom",
                "class": "logging.FileHandler",
                "filename": "uvicorn.log",
            },
            "logtail": {
                "formatter": "custom",
                "class": "logtail.LogtailHandler",
                "source_token": os.getenv("TOKEN_UVICORN"),
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default", "file", "logtail"],
                "level": "INFO",
            },
            "storage.error": {
                "handlers": ["default", "file", "logtail"],
                "level": "INFO",
            },
        },
    }
