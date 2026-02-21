"""
logging_config.py — Centralized logging setup.

Writes DEBUG-level logs to `trading_bot.log` and INFO-level to the console.
Every request, response, and error is captured for audit.
"""

import logging
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trading_bot.log")
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> logging.Logger:
    """Configure and return the root application logger."""
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    # ── File handler (DEBUG) ──────────────────────────────────────────────
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    # ── Console handler (INFO) ────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
