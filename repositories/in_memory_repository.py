from repositories.base_repository import BaseRepository, ItemNotFoundError

class InMemoryRepository(BaseRepository):
    def __init__(self):
        self.data = {}
        self.current_id = 1

    def create(self, item_data: dict) -> dict:
        item_id = self.current_id
        self.current_id += 1
        item = {"id": item_id, **item_data}
        self.data[item_id] = item
        return item

    def get(self, item_id: int) -> dict:
        if item_id not in self.data:
            raise ItemNotFoundError(f"Item {item_id} not found")
        return self.data[item_id]

    def get_all(self) -> list:
        return list(self.data.values())

    def update(self, item_id: int, item_data: dict) -> dict:
        if item_id not in self.data:
            raise ItemNotFoundError(f"Item {item_id} not found")
        self.data[item_id].update(item_data)
        return self.data[item_id]

    def delete(self, item_id: int) -> bool:
        if item_id not in self.data:
            raise ItemNotFoundError(f"Item {item_id} not found")
        del self.data[item_id]
        return True
