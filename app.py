from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import secrets
import asyncio

app = FastAPI()

class Model(BaseModel):
    password: str



# Текущее значение кода
code = {"value":None}

# Разрешаем все источники (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True
)

# Фоновая задача — обновляет код каждые 5 минут
async def update_code_every_5min():
    while True:
        new_code = secrets.token_hex(3).upper()  # 6 символов (пример: "A1B2C3")
        code["value"] = new_code
        print(f"[INFO] Новый код: {new_code}")
        await asyncio.sleep(10)  # 5 минут = 300 секунд

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_code_every_5min())

@app.post("/point")
async def point(password: Model):
    if password.password == "Quizizz_Admin":
        return {"status": "success", "code": code["value"]}
    return {"status": "error", "message": "Wrong password"}

@app.get("/get_code")
async def get_code():
    return {code["value"]}


if __name__ == "__main__":
    uvicorn.run("TST:app", host="0.0.0.0", port=8000)




