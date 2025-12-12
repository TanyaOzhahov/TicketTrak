import os
from datetime import datetime
import requests
from dotenv import load_dotenv
from fastapi import HTTPException
from loguru import logger
from pydantic import BaseModel
from pymongo import MongoClient
from pathlib import Path

load_dotenv()
print("Loaded .env from:", Path(".").resolve())
print("MONGO_HOST:", os.getenv("MONGO_HOST"))

# Конфигурация MongoDB
MONGO_CONFIG = {
    "username": os.getenv("MONGO_INITDB_ROOT_USERNAME"),
    "password": os.getenv("MONGO_INITDB_ROOT_PASSWORD"),
    "host": os.getenv("MONGO_HOST"),
    #"host": "0.0.0.0",
    "port": int(os.getenv("MONGO_PORT")),
    "authSource": "admin",
}

logger.info(f"Connecting to MongoDB: {MONGO_CONFIG}")

client = MongoClient(**MONGO_CONFIG)
db = client["aviasales_db"]
collection = db["prices_logs"]


# ===============================
#    Логирование в MongoDB
# ===============================
def save_request_to_mongo(url, request, response, status_code, created_at, updated_at):
    """Сохранение лога запроса в БД"""

    try:
        collection.insert_one({
            "url": url,
            "request": request,
            "response": response,
            "status_code": status_code,
            "created_at": created_at,
            "updated_at": updated_at
        })
    except Exception as e:
        logger.error(f"Ошибка записи в Mongo: {e}")


# ===============================
#    Pydantic модель
# ===============================
class PricesRequest(BaseModel):
    origin: str
    destination: str
    departure_at: str
    return_at: str | None = None
    limit: int | None = 10


# ===============================
#    Основная логика Aviasales API
# ===============================
def get_prices_data(req: PricesRequest) -> dict:
    API_URL = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    

    # Читаем токен из .env
    API_TOKEN = os.getenv("AVIASALES_TOKEN")

    if not API_TOKEN:
        logger.error("AVIASALES_TOKEN отсутствует")
        raise HTTPException(500, "AVIASALES_TOKEN не найден в окружении")

    headers = {
        "X-Access-Token": API_TOKEN
    }

    params = {
        "origin": req.origin,
        "destination": req.destination,
        "departure_at": req.departure_at,
        "return_at": req.return_at,
        "limit": req.limit,
    }

    logger.info(f"Отправка запроса в Aviasales: {params}")

    created_at = datetime.now()

    try:
        response = requests.get(
            API_URL,
            params=params,
            headers=headers,
            timeout=60
        )
    except Exception as e:
        logger.error(f"Ошибка сети: {e}")
        raise HTTPException(500, f"Ошибка сети или API: {e}")

    updated_at = datetime.now()

    # Пытаемся получить JSON
    try:
        raw_response = response.json()
    except Exception:
        raw_response = response.text

    # Логируем запрос в Mongo
    save_request_to_mongo(
        API_URL,
        params,
        raw_response,
        response.status_code,
        created_at,
        updated_at
    )

    # Проверка на ошибку Aviasales
    if response.status_code != 200:
        logger.error(f"Ошибка Aviasales: {response.text}")
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Ошибка Aviasales API: {response.text}"
        )

    return raw_response
