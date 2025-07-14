
import os
from dotenv import load_dotenv

class Settings:
    ZERODHA_API_KEY = None
    ZERODHA_API_SECRET = None
    ZERODHA_ACCESS_TOKEN = None

    @classmethod
    def load(cls):
        load_dotenv()

        cls.ZERODHA_API_KEY = os.getenv("ZERODHA_API_KEY")
        cls.ZERODHA_API_SECRET = os.getenv("ZERODHA_API_SECRET")
        cls.ZERODHA_ACCESS_TOKEN = os.getenv("ZERODHA_ACCESS_TOKEN")

        if not all([cls.ZERODHA_API_KEY, cls.ZERODHA_API_SECRET, cls.ZERODHA_ACCESS_TOKEN]):
            raise ValueError("Missing one or more required environment variables in .env")

        return cls
