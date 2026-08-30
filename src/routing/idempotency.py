from typing import Protocol


class IdempotencyStore(Protocol):
    def claim(self, key: str) -> bool: ...


class InMemoryIdempotencyStore:
    def __init__(self):
        self._keys: set[str] = set()

    def claim(self, key: str) -> bool:
        if key in self._keys:
            return False
        self._keys.add(key)
        return True


class MongoIdempotencyStore:
    def __init__(self, database: str = "pharaoh", collection: str = "processed_financial_requests"):
        self.database = database
        self.collection = collection

    def claim(self, key: str) -> bool:
        from pymongo.errors import DuplicateKeyError

        from utils.mongo_helper import get_mongo_client

        client = get_mongo_client()
        try:
            client[self.database][self.collection].insert_one({"_id": key})
            return True
        except DuplicateKeyError:
            return False
        finally:
            client.close()
