from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base

class Cidade(Base):
    __tablename__ = "cidades"

    id_ibge : Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False)
    nome : Mapped[str] = mapped_column(String(100), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    populacao: Mapped[int] = mapped_column(Integer, nullable=False)
