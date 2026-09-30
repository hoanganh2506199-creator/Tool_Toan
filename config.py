

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Tải biến môi trường từ .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Chưa cấu hình GEMINI_API_KEY trong file .env")

# Khởi tạo model
genai.configure(api_key=API_KEY)

# DÒNG NÀY RẤT QUAN TRỌNG, HÃY CHẮC CHẮN NÓ TỒN TẠI:
model = genai.GenerativeModel('gemini-3.5-flash-lite')