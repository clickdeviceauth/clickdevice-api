import os
import json
import random
from fastapi import FastAPI, Request
from PIL import Image, ImageDraw

app = FastAPI()
# Используем папку для диска, которую подключим в Render
BASE_DIR = "/var/data" 

@app.post("/register")
async def register(request: Request):
    data = await request.json()
    email = data.get('email')
    user_dir = os.path.join(BASE_DIR, email)
    
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
        
        # Сохраняем логин/пароль
        with open(f"{user_dir}/account_info_login.json", "w") as f:
            json.dump({"login": email, "password": data.get('password')}, f)
            
        # Генерация аватарки
        color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        img = Image.new('RGB', (64, 64), color=color)
        d = ImageDraw.Draw(img)
        d.text((22, 18), email[0].upper(), fill=(255, 255, 255))
        
        # Сохраняем иконки
        img.save(f"{user_dir}/avatar_64.ico", format='ICO')
        img.resize((32, 32)).save(f"{user_dir}/avatar_32.ico", format='ICO')
        img.resize((16, 16)).save(f"{user_dir}/avatar_16.ico", format='ICO')
            
        # Статус
        with open(f"{user_dir}/auth_codes.json", "w") as f:
            json.dump({"status": "1x1"}, f)
            
        return {"status": "success", "message": "Профиль создан"}
    return {"status": "error", "message": "Пользователь уже существует"}