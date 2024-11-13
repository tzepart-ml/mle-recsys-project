from fastapi import FastAPI


class EventStore:

    def __init__(self, max_events_per_user=10):
        self.events = {}
        self.max_events_per_user = max_events_per_user

    def put(self, user_id, item_id):
        """
        Сохраняет событие
        """
        # Get the existing events for the user or initialize an empty list if none exist
        user_events = self.events.get(user_id, [])
        # Add the new item_id to the beginning of the list and limit the list size
        self.events[user_id] = [item_id] + user_events[:self.max_events_per_user - 1]

    def get(self, user_id, k):
        """
        Возвращает события для пользователя
        """
        # Get the events for the user, if no events exist for the user return an empty list
        user_events = self.events.get(user_id, [])
        # Return the last k events (or fewer if there are not enough)
        return user_events[:k]


# Initialize the event store
events_store = EventStore()

# создаём приложение FastAPI
app = FastAPI(title="events")


@app.post("/put")
async def put(user_id: int, item_id: int):
    """
    Сохраняет событие для user_id, item_id
    """
    events_store.put(user_id, item_id)
    return {"result": "ok"}


@app.post("/get")
async def get(user_id: int, k: int = 10):
    """
    Возвращает список последних k событий для пользователя user_id
    """
    events = events_store.get(user_id, k)
    return {"events": events}
