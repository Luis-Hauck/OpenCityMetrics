from sqlalchemy.orm import Session
from models.cidade import Cidade
from repositories.base_repository import BaseRepository, ItemNotFoundError

class CidadeRepository(BaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, item_data: dict) -> Cidade:
        db_item = Cidade(**item_data)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def get(self, item_id: int) -> Cidade:
        item = self.db.query(Cidade).filter(Cidade.id_ibge == item_id).first()
        if not item:
            raise ItemNotFoundError(f"Cidade with id_ibge {item_id} not found")
        return item

    def get_all(self) -> list[Cidade]:
        return self.db.query(Cidade).all()

    def update(self, item_id: int, item_data: dict) -> Cidade:
        item = self.get(item_id)
        for key, value in item_data.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item_id: int) -> bool:
        item = self.get(item_id)
        self.db.delete(item)
        self.db.commit()
        return True
