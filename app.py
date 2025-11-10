from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import secrets

app = FastAPI()

class Model(BaseModel):
    password: str

# Храним код в памяти (но на Vercel он не сохраняется между запросами)
code = {"value": None}

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True
)

def generate_new_code():
    """Создаёт новый 6-символьный код"""
    return secrets.token_hex(3).upper()

@app.post("/point")
async def point(password: Model):
    """Если пароль правильный — обновляем код и возвращаем его"""
    if password.password == "Quizizz_Admin":
        new_code = generate_new_code()
        code["value"] = new_code
        return {"status": "success", "code": new_code}
    return {"status": "error", "message": "Wrong password"}

@app.get("/get_code")
async def get_code():
    """Возвращает текущий код, если он уже был создан"""
    if code["value"] is None:
        return {"status": "empty", "message": "Code not generated yet"}
    return {"status": "success", "code": code["value"]}
