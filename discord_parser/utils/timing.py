# Authored by AI: Google's Gemini Model
import time
from utils.logger_setup import logger

class Timer:
    """A context manager to time and log code blocks."""
    def __init__(self, description="Process"):
        self.description = description
        self.start_time = None

    def __enter__(self):
        logger.info(f"[TIMER] {self.description}...")
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = time.perf_counter() - self.start_time
        logger.info(f"[TIMER] {self.description}... Done ({elapsed_time:.2f}s)")