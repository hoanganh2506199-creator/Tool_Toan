import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Chưa tìm thấy GEMINI_API_KEY trong file .env!")

#MODEL = "gemini-3.8-flash"
MODEL = "gemini-3.5-flash-lite"