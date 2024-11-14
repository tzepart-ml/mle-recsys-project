import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.recommendation_handler import Recommendations
import requests

logger = logging.getLogger("uvicorn.error")

features_store_url = "http://features_service:8010"
events_store_url = "http://events_service:8020"

rec_store = Recommendations()
rec_store.load(
    "personal",
    "/app/data/recommendations.parquet",
    columns=["user_id", "item_id", "score"],
)
rec_store.load(
    "default",
    "/app/data/top_popular.parquet",
    columns=["item_id", "popularity_weighted"],
)


def dedup_ids(ids):
    """
    Дедублицирует список идентификаторов, оставляя только первое вхождение
    """
    seen = set()
    ids = [id for id in ids if not (id in seen or seen.add(id))]

    return ids


@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    logger.info("Starting")
    yield
    # этот код выполнится только один раз при остановке сервиса
    logger.info("Stopping")


# создаём приложение FastAPI
app = FastAPI(title="recommendations", lifespan=lifespan)


@app.post("/recommendations_offline")
async def recommendations_offline(user_id: int, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """

    recs = rec_store.get(user_id, k)

    return {"recs": recs}


@app.post("/recommendations_online")
async def recommendations_online(user_id: int, k: int = 100):
    """
    Возвращает список онлайн-рекомендаций длиной k для пользователя user_id
    """

    headers = {"Content-type": "application/json", "Accept": "text/plain"}

    # получаем список последних событий пользователя, возьмём три последних
    params = {"user_id": user_id, "k": 3}
    resp = requests.post(events_store_url + "/get", headers=headers, params=params)
    events = resp.json().get("events", [])

    # получаем список айтемов, похожих на последние три, с которыми взаимодействовал пользователь
    items = []
    for item_id in events:
        # для каждого item_id получаем список похожих в item_similar_items
        params = {"item_id": item_id, "k": k}
        resp = requests.post(features_store_url + "/similar_items", headers=headers, params=params)
        item_similar_items = resp.json()
        items += item_similar_items["item_id_2"]

    # ограничиваем рекомендации до k
    recs = items[:k]

    return {"recs": recs}


@app.post("/recommendations")
async def recommendations(user_id: int, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """

    recs_offline = await recommendations_offline(user_id, k)
    recs_online = await recommendations_online(user_id, k)

    recs_offline = recs_offline["recs"]
    recs_online = recs_online["recs"]

    recs_blended = []

    min_length = min(len(recs_offline), len(recs_online))

    # Чередуем элементы из списков, пока позволяет минимальная длина
    for i in range(min_length):
        recs_blended.append(recs_offline[i])
        recs_blended.append(recs_online[i])

    # Добавляем оставшиеся элементы из оффлайн или онлайн списка в конец
    if len(recs_offline) > min_length:
        recs_blended.extend(recs_offline[min_length:])
    elif len(recs_online) > min_length:
        recs_blended.extend(recs_online[min_length:])

    # Удаляем дубликаты
    recs_blended = dedup_ids(recs_blended)

    # Оставляем только первые k рекомендаций
    recs_blended = recs_blended[:k]

    return {"recs": recs_blended}
