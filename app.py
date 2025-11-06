from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import secrets
import asyncio
import httpx

app = FastAPI()

class Model(BaseModel):
    password: str

class GroqRequest(BaseModel):
    message: str = "Hello"

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

@app.post("/groq_chat")
async def groq_chat(request: GroqRequest):
    """
    Новый эндпоинт для отправки запроса к Groq API
    """
    url = "https://api.groq.com/openai/v1/chat/completions?project_id=project_01k92gvcg6f8pveava7f06fw4g"
    
    headers = {
        'accept': 'application/json',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6Imp3ay1saXZlLTMyNDg5ODNiLWEzYWYtNGVlZi1iZDAyLTQ4YTEyOWU3NmIyYSIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsicHJvamVjdC1saXZlLTVjYjM4ODBlLTc3NGUtNDNlYS1hYjkwLWY0ZDMyMzRlMzZkZCJdLCJleHAiOjE3NjI0MjE5OTUsImh0dHBzOi8vZ3JvcS5jb20vb3JnYW5pemF0aW9uIjp7ImlkIjoib3JnXzAxazkyZ3ZjMGpmOG50ejgydHNjdHh5ZDEyIn0sImh0dHBzOi8vc3R5dGNoLmNvbS9vcmdhbml6YXRpb24iOnsib3JnYW5pemF0aW9uX2lkIjoib3JnYW5pemF0aW9uLWxpdmUtODBiZDczNWQtMjlkYS00NmQzLWFmYjAtNGEzMDA2MWE0NjVmIiwic2x1ZyI6Im9yZ18wMWs5Mmd2YzBqZjhudHo4MnRzY3R4eWQxMiJ9LCJodHRwczovL3N0eXRjaC5jb20vc2Vzc2lvbiI6eyJpZCI6Im1lbWJlci1zZXNzaW9uLWxpdmUtNjMwYzQ1NjYtNTE2MC00ODIzLTgxNzEtNTNjZWYyNjE5Yjc5Iiwic3RhcnRlZF9hdCI6IjIwMjUtMTEtMDZUMDk6MzQ6NTVaIiwibGFzdF9hY2Nlc3NlZF9hdCI6IjIwMjUtMTEtMDZUMDk6MzQ6NTVaIiwiZXhwaXJlc19hdCI6IjIwMjUtMTItMDZUMDk6MzQ6NTVaIiwiYXR0cmlidXRlcyI6eyJ1c2VyX2FnZW50IjoiIiwiaXBfYWRkcmVzcyI6IiJ9LCJhdXRoZW50aWNhdGlvbl9mYWN0b3JzIjpbeyJ0eXBlIjoib2F1dGgiLCJkZWxpdmVyeV9tZXRob2QiOiJvYXV0aF9nb29nbGUiLCJsYXN0X2F1dGhlbnRpY2F0ZWRfYXQiOiIyMDI1LTExLTA2VDA5OjM0OjU0WiIsImdvb2dsZV9vYXV0aF9mYWN0b3IiOnsiaWQiOiJvYXV0aC1yZWdpc3RyYXRpb24tbGl2ZS0xMDZlNjIwMC0zOWJhLTQ2NmItOTUyZi1iYjM4YTc3NDg2NGIiLCJlbWFpbF9pZCI6Im1lbWJlci1lbWFpbC1saXZlLWMxODcyZTIzLWRmMmItNDg0YS1hOWFhLTQ3MzNhMmM5MTNjYSIsInByb3ZpZGVyX3N1YmplY3QiOiIxMDAwMzkzNjgyMzI3MjQyMTEwNTQifX1dLCJyb2xlcyI6WyJzdHl0Y2hfbWVtYmVyIiwic3R5dGNoX2FkbWluIl19LCJpYXQiOjE3NjI0MjE2OTUsImlzcyI6Imh0dHBzOi8vYXBpLnN0eXRjaGIyYi5ncm9xLmNvbSIsIm5iZiI6MTc2MjQyMTY5NSwic3ViIjoibWVtYmVyLWxpdmUtMWNiMmM2ZTctMzAzYi00NjI5LWFhNmUtZmI2Zjg5MTFlMzcwIn0.INffalbKXlWHUAIT2g9tv1v0Nc2Tfugxe6-iP9fODGMoni5nCxd0dAbQfjYoFX3eIwwJiBnjc6u2TlkHe0OtbwCPjb3Y23OxERKaHY23yuPMCvY3cwuaegThRVmuvAbw1BqtRDAHmGzQVje07zNCdLQJzjJMa_y9gv6jRSQ7dHdU_M92HMTzuoosn6XVPCgTz02GWBWuZJZ645slUqkcRUp1-DHVapFMJ3lnWOXIQ7p-n1rGm8OdbnemxXKe81vA_IsOA9r7BhSy_oKLlYbsV8ru0F2IoQjpxYCbvpWIlv1bbx3OiKnlWRuMiN19ZkW90gT-MLVDY5ZZDUxU1lPyrA',
        'content-type': 'application/json',
        'groq-organization': 'org_01k92gvc0jf8ntz82tsctxyd12',
        'origin': 'https://console.groq.com',
        'priority': 'u=1, i',
        'referer': 'https://console.groq.com/',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'x-stainless-arch': 'unknown',
        'x-stainless-lang': 'js',
        'x-stainless-os': 'Unknown',
        'x-stainless-package-version': '0.31.0',
        'x-stainless-retry-count': '0',
        'x-stainless-runtime': 'browser:chrome',
        'x-stainless-runtime-version': '141.0.0',
        'x-stainless-timeout': '60'
    }
    
    data = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {
                "role": "user",
                "content": request.message
            }
        ],
        "temperature": 0.1,
        "max_completion_tokens": 8000,
        "stop": None,
        "stream": False,
        "reasoning_effort": "high"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=60.0)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("TST:app", host="0.0.0.0", port=8000)
