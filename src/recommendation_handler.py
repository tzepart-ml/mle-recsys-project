import logging as logger
import pandas as pd


class Recommendations:

    def __init__(self):

        self._recs = {"personal": None, "default": None}
        self._stats = {
            "request_personal_count": 0,
            "request_default_count": 0,
        }

    def load(self, type, path, **kwargs):
        """
        Загружает рекомендации из файла
        """

        logger.info(f"Loading recommendations, type: {type}")
        self._recs[type] = pd.read_parquet(path, **kwargs)
        if type == "personal":
            self._recs[type] = self._recs[type].set_index("user_id")
        logger.info(f"Loaded")

    def get(self, user_id: int, k: int = 100):
        """
        Возвращает список рекомендаций для пользователя
        """
        try:
            recs = self._recs["personal"].loc[user_id]
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_personal_count"] += 1
        except KeyError:
            recs = self._recs["default"]
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_default_count"] += 1
        except:
            logger.error("No recommendations found")
            recs = []

        return recs

    def get_default(self, k: int = 100):
        """
        Возвращает список рекомендаций для пользователя
        """
        recs = self._recs["default"]
        recs = recs["item_id"].to_list()[:k]
        self._stats["request_default_count"] += 1

        return recs

    def log_stats(self) -> None:

        logger.info("Log Stats for recommendations")
        for name, value in self._stats.items():
            logger.info(f"{name:<30} {value} ")

    def get_stats(self) -> dict:

        logger.info("Get Stats for recommendations")
        return self._stats



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
