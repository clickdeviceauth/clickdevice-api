from fastapi import FastAPI, Request
import os
import json
import random
import shutil

app = FastAPI()
BASE_DIR = os.environ.get("RENDER_DISK_PATH", "data_storage")
if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR, exist_ok=True)

@app.post("/register")
async def register(request: Request):
    # PIL импортируется только в момент вызова функции
    from PIL import Image
    data = await request.json()
    email = data['email']
    user_dir = os.path.join(BASE_DIR, email)
    if os.path.exists(user_dir): return {"status": "error", "message": "Exists"}
    
    os.makedirs(user_dir)
    with open(f"{user_dir}/info.json", "w") as f:
        json.dump({"email": email, "2fa": True}, f)
    
    img = Image.new('RGB', (64, 64), color=(100, 100, 100))
    img.save(f"{user_dir}/avatar.ico", format='ICO')
    return {"status": "success"}

@app.post("/login")
async def login(request: Request):
    # smtplib импортируется только здесь
    import smtplib
    from email.mime.text import MIMEText
    
    data = await request.json()
    email = data['email']
    user_dir = os.path.join(BASE_DIR, email)
    if not os.path.exists(user_dir): return {"status": "error"}
    
    code = str(random.randint(100000, 999999))
    with open(f"{user_dir}/code.json", "w") as f:
        json.dump({"code": code}, f)
    
    # Отправка почты (упрощено)
    return {"status": "code_sent"}

@app.get("/list_users")
async def list_users():
    return {"users": os.listdir(BASE_DIR)}
