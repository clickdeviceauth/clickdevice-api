import os
import json
import random
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, Request
from PIL import Image, ImageDraw

app = FastAPI()
BASE_DIR = "/var/data"
if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)

def send_email(to_email, code):
    password = os.environ.get("EMAIL_PASS")
    msg = MIMEMultipart()
    msg['Subject'] = "Код подтверждения"
    msg['From'] = "clickdevice.auth@gmail.com"
    msg['To'] = to_email
    msg.attach(MIMEText(f"Ваш код: {code}", 'plain'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("clickdevice.auth@gmail.com", password)
        server.sendmail("clickdevice.auth@gmail.com", to_email, msg.as_string())

@app.post("/register")
async def register(request: Request):
    data = await request.json()
    email = data['email']
    user_dir = os.path.join(BASE_DIR, email)
    if os.path.exists(user_dir): return {"status": "error", "message": "Пользователь есть"}
    
    os.makedirs(user_dir)
    # Сохраняем настройки профиля, включая 2FA
    with open(f"{user_dir}/account_info.json", "w") as f:
        json.dump({"email": email, "password": data['password'], "2fa_enabled": True}, f)
    
    img = Image.new('RGB', (64, 64), color=(100, 100, 100))
    img.save(f"{user_dir}/avatar.ico", format='ICO')
    return {"status": "success"}

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    email = data['email']
    user_dir = os.path.join(BASE_DIR, email)
    if not os.path.exists(user_dir): return {"status": "error", "message": "Нет такого"}
    
    code = str(random.randint(100000, 999999))
    with open(f"{user_dir}/auth_codes.json", "w") as f:
        json.dump({"code": code}, f)
    send_email(email, code)
    return {"status": "code_sent"}

@app.post("/toggle_2fa")
async def toggle_2fa(request: Request):
    data = await request.json()
    path = f"{BASE_DIR}/{data['email']}/account_info.json"
    with open(path, "r") as f: acc = json.load(f)
    acc['2fa_enabled'] = data['enable']
    with open(path, "w") as f: json.dump(acc, f)
    return {"status": "success"}

@app.get("/list_users")
async def list_users():
    # Просмотр всех папок (аналог ls /var/data)
    return {"users": [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]}

@app.post("/delete_user")
async def delete_user(request: Request):
    data = await request.json()
    user_dir = os.path.join(BASE_DIR, data['email'])
    if os.path.exists(user_dir):
        shutil.rmtree(user_dir)
        return {"status": "deleted"}
    return {"status": "error"}
