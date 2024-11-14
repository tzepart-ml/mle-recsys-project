import logging
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI

logger = logging.getLogger("uvicorn.error")


class SimilarItems:

    def __init__(self):
        self._similar_items = None

    def load(self, path, **kwargs):
        """
        Загружаем данные из файла
        """
        logger.info(f"Loading data from {path}")
        # Load the similar items data from the provided file path
        self._similar_items = pd.read_parquet(path, **kwargs)
        # Set item_id_1 as the index for easy lookup
        self._similar_items.set_index("item_id_1", inplace=True)
        logger.info("Data loaded successfully")

    def get(self, item_id: int, k: int = 10):
        """
        Возвращает список похожих объектов
        """
        try:
            # Retrieve the top k similar items for the given item_id
            i2i = self._similar_items.loc[item_id].head(k)
            i2i = i2i[["item_id_2"]].to_dict(orient="list")
        except KeyError:
            logger.error(f"No recommendations found for item_id: {item_id}")
            i2i = {"item_id_2": []}

        return i2i


# Initialize the SimilarItems store
sim_items_store = SimilarItems()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the data when the service starts
    sim_items_store.load(
        path="/app/data/similar.parquet",  # Specify the correct path to your parquet file
        columns=["item_id_1", "item_id_2"]
    )
    logger.info("Ready!")
    # Wait until the application is shut down
    yield


# Create the FastAPI application
app = FastAPI(title="features", lifespan=lifespan)


@app.post("/similar_items")
async def recommendations(item_id: int, k: int = 10):
    """
    Возвращает список похожих объектов длиной k для item_id
    """
    i2i = sim_items_store.get(item_id, k)
    return i2i
