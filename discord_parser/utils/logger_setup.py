# Authored by AI: Google's Gemini Model
import logging
import sys

def setup_logger():
    """Configures and returns a root logger."""
    # Configure logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - (%(threadName)-10s) - %(message)s",
        stream=sys.stdout,
    )
    logger = logging.getLogger(__name__)
    logger.info("Logger initialized.")
    return logger

# Create a single logger instance to be used across the application
logger = setup_logger()