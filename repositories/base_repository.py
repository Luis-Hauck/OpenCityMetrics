from abc import ABC, abstractmethod

class ItemNotFoundError(Exception):
    pass

class BaseRepository(ABC):
    @abstractmethod
    def create(self, item_data: dict) -> dict:
        pass

    @abstractmethod
    def get(self, item_id: int) -> dict:
        pass

    @abstractmethod
    def get_all(self) -> list:
        pass

    @abstractmethod
    def update(self, item_id: int, item_data: dict) -> dict:
        pass

    @abstractmethod
    def delete(self, item_id: int) -> bool:
        pass
