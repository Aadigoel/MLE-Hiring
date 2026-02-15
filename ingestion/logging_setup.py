"""Logging setup for the ingestion pipeline."""

import logging
import sys
from pathlib import Path
from config import settings

# Create logs directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOG_DIR / "ingestion.log"

# File handler
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(settings.log_level)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(settings.log_level)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Root logger configuration
root_logger = logging.getLogger()
root_logger.setLevel(settings.log_level)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(name)
