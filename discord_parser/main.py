# Authored by AI: Google's Gemini Model
import sys
import os
from utils.logger_setup import logger

# Add parent directory to path to allow for package-like imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from discord_parser.ui.main_window import App

def main():
    """Main function to launch the application."""
    logger.info("Application starting.")
    try:
        app = App()
        logger.info("Main application loop started.")
        app.mainloop()
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}", exc_info=True)
    finally:
        logger.info("Application shutdown.")

if __name__ == "__main__":
    main()