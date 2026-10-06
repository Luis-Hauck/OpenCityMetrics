from datetime import datetime
from sqlalchemy import String, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base


class Funcionario(Base):
    __tablename__ = "funcionarios"

    __table_args__ = (
        UniqueConstraint('id_cidade', 'id_funcionario', 'data_referencia', name='uix_cidade_funcionario', unique=True)
    )

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False)
    id_cidade: Mapped[int] = mapped_column(ForeignKey("cidades.id_ibge"), nullable=False)
    id_funcionario: Mapped[str] = mapped_column(String, nullable=False)
    entidade: Mapped[str] = mapped_column(String(100), nullable=False)
    contrato: Mapped[str] = mapped_column(String(100), nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cargo: Mapped[str] = mapped_column(String(100), nullable=False)
    regime_trabalho: Mapped[str] = mapped_column(String(100), nullable=False)
    proventos: Mapped[float] = mapped_column(Float, nullable=False)
    data_referencia: Mapped[datetime] = mapped_column(nullable=False)
