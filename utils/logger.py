# utils/logger.py

from datetime import datetime

def log(message):
    """Logs a message with timestamp."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
