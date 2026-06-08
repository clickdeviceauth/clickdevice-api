import os
import json
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, Request
from PIL import Image, ImageDraw

app = FastAPI()
BASE_DIR = "/var/data" if os.path.exists("/var/data") else "users_data"
if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)

def send_email(to_email, code):
    password = os.environ.get("EMAIL_PASS")
    msg = MIMEMultipart()
    msg['Subject'] = "Код подтверждения"
    msg['From'] = "clickdevice.auth@gmail.com"
    msg['To'] = to_email
    msg.attach(MIMEText(f"Ваш код подтверждения: {code}", 'plain'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("clickdevice.auth@gmail.com", password)
        server.sendmail("clickdevice.auth@gmail.com", to_email, msg.as_string())

@app.post("/register")
async def register(request: Request):
    data = await request.json()
    email = data['email']
    user_dir = os.path.join(BASE_DIR, email)
    if os.path.exists(user_dir): return {"status": "error", "message": "Пользователь существует"}
    
    os.makedirs(user_dir)
    with open(f"{user_dir}/account_info_login.json", "w") as f:
        json.dump({"login": email, "password": data['password']}, f)
    
    # Генерация первой аватарки
    update_avatar_logic(email, (100, 100, 100), user_dir)
    return {"status": "success"}

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    email = data['email']
    code = str(random.randint(100000, 999999))
    with open(f"{BASE_DIR}/{email}/auth_codes.json", "w") as f:
        json.dump({"code": code}, f)
    send_email(email, code)
    return {"status": "code_sent"}

@app.post("/verify_2fa")
async def verify_2fa(request: Request):
    data = await request.json()
    with open(f"{BASE_DIR}/{data['email']}/auth_codes.json", "r") as f:
        stored = json.load(f)
    if stored['code'] == data['code']:
        return {"status": "success"}
    return {"status": "error", "message": "Неверный код"}

@app.post("/update_avatar")
async def update_avatar(request: Request):
    data = await request.json()
    update_avatar_logic(data['email'], tuple(data['color']), os.path.join(BASE_DIR, data['email']))
    return {"status": "success"}

def update_avatar_logic(email, color, path):
    img = Image.new('RGB', (64, 64), color=color)
    d = ImageDraw.Draw(img)
    d.text((20, 20), email[0].upper(), fill=(255, 255, 255))
    img.save(f"{path}/avatar_64.ico", format='ICO')
