"""
Logging module for GitHub Repository Analyzer
"""

import logging
import os
import sys
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)


# Configure logging
def setup_logger(name="github_analyzer"):
    """
    Set up and configure logger

    Args:
        name (str): Logger name

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create console handler for info level logs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Create rotating file handler for debug level logs
    from logging.handlers import RotatingFileHandler

    log_filename = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=5 * 1024 * 1024,  # 5MB per file
        backupCount=3,  # Keep 3 backup files
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Create a default logger instance
logger = setup_logger()
