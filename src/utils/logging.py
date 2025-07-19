import logging
import sys
from typing import Any
from functools import wraps
import traceback

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def setup_logging(self, level: str = "INFO"):
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.setLevel(getattr(logging, level.upper()))

    def log_api_call(self, service: str, method: str, **kwargs):
        self.logger.info(f"API Call: {service}.{method}", extra=kwargs)

    def log_error(self, error: Exception, context: dict = None):
        self.logger.error(
            f"Error: {str(error)}",
            extra={
                "error_type": type(error).__name__,
                "traceback": traceback.format_exc(),
                "context": context or {}
            }
        )

def handle_exceptions(logger: StructuredLogger):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.log_error(e, {"function": func.__name__})
                raise
        return wrapper
    return decorator
