import os
import json
import random
import shutil
import logging
from fastapi import FastAPI, Request, HTTPException

# Настройка логов — мы увидим любые ошибки прямо в консоли Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClickDevice")

app = FastAPI()

# Используем путь из переменной окружения или дефолт
BASE_DIR = os.environ.get("RENDER_DISK_PATH", "data_storage")
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR, exist_ok=True)

def safe_json_write(path, data):
    """Безопасная запись JSON: сначала во временный файл, потом подмена."""
    temp_path = f"{path}.tmp"
    with open(temp_path, "w") as f:
        json.dump(data, f)
    os.replace(temp_path, path)

@app.post("/register")
async def register(request: Request):
    try:
        data = await request.json()
        email = str(data.get('email', '')).strip()
        if not email: raise ValueError("Empty email")
        
        user_dir = os.path.join(BASE_DIR, email)
        if os.path.exists(user_dir):
            return {"status": "error", "message": "User exists"}
        
        os.makedirs(user_dir)
        safe_json_write(f"{user_dir}/info.json", {"email": email, "2fa": True})
        logger.info(f"New user registered: {email}")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Register failed: {e}")
        return {"status": "error", "message": "Internal error"}

@app.post("/login")
async def login(request: Request):
    try:
        data = await request.json()
        email = data.get('email')
        user_dir = os.path.join(BASE_DIR, email)
        
        if not os.path.exists(user_dir):
            return {"status": "error", "message": "User not found"}
        
        code = "123456" # Тестовый код, пока не настроишь SMTP
        safe_json_write(f"{user_dir}/code.json", {"code": code})
        return {"status": "code_sent", "debug_code": code}
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return {"status": "error", "message": "Login failed"}

@app.post("/verify_2fa")
async def verify_2fa(request: Request):
    try:
        data = await request.json()
        email, code = data.get('email'), data.get('code')
        path = os.path.join(BASE_DIR, email, "code.json")
        
        if not os.path.exists(path): return {"status": "error", "message": "No code"}
        
        with open(path, "r") as f:
            if json.load(f).get("code") == code:
                return {"status": "success"}
        return {"status": "error", "message": "Invalid code"}
    except Exception as e:
        logger.error(f"Verify failed: {e}")
        return {"status": "error"}

@app.get("/list_users")
async def list_users():
    try:
        # Только папки, никаких системных файлов
        return {"users": [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]}
    except Exception:
        return {"users": []}
