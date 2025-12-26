"""Logging configuration for docs-translator."""

import logging
import sys
from pathlib import Path
from typing import Optional

# Custom log levels
VERBOSE = 15  # Between DEBUG(10) and INFO(20)
logging.addLevelName(VERBOSE, "VERBOSE")


class ColorFormatter(logging.Formatter):
    """Formatter that adds colors for terminal output."""

    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "VERBOSE": "\033[34m",    # Blue
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


class TranslatorLogger:
    """Centralized logger for docs-translator."""

    _instance: Optional["TranslatorLogger"] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_logger(cls, name: str = "docs-translator") -> logging.Logger:
        """Get or create the logger instance."""
        if cls._logger is None:
            cls._logger = logging.getLogger(name)
            cls._logger.setLevel(logging.INFO)

            # Console handler with colors
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setFormatter(
                ColorFormatter("%(levelname)s: %(message)s")
            )
            cls._logger.addHandler(console_handler)

        return cls._logger

    @classmethod
    def configure(
        cls,
        level: str = "INFO",
        log_file: Optional[Path] = None,
        verbose: bool = False,
    ):
        """Configure the logger.

        Args:
            level: Log level (DEBUG, VERBOSE, INFO, WARNING, ERROR)
            log_file: Optional file to write logs to
            verbose: If True, set level to VERBOSE
        """
        logger = cls.get_logger()

        # Set level
        if verbose:
            logger.setLevel(VERBOSE)
        else:
            logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Add file handler if requested
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            logger.addHandler(file_handler)


# Convenience functions
def get_logger() -> logging.Logger:
    """Get the translator logger."""
    return TranslatorLogger.get_logger()


def configure_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    verbose: bool = False,
):
    """Configure logging for the translator."""
    TranslatorLogger.configure(level=level, log_file=log_file, verbose=verbose)


# Quick access to log functions
logger = get_logger()


def debug(msg: str, *args, **kwargs):
    """Log debug message."""
    logger.debug(msg, *args, **kwargs)


def verbose(msg: str, *args, **kwargs):
    """Log verbose message (between debug and info)."""
    logger.log(VERBOSE, msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """Log info message."""
    logger.info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """Log warning message."""
    logger.warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """Log error message."""
    logger.error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """Log critical message."""
    logger.critical(msg, *args, **kwargs)
