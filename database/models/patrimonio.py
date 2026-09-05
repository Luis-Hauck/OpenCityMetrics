from sqlalchemy import String, Date, ForeignKey, Text, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from typing import Optional

from database.connection import Base


class DadosPatrimonio(Base):
    __tablename__ = "dados_patrimonio"

    __table_args__ = (
        UniqueConstraint('id_cidade', 'entidade', 'codigo', name='uix_cidade_patrimonio', unique=True)
    )


    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False, incubator="autoincrement")
    id_cidade: Mapped[int] = mapped_column(ForeignKey("cidades.id_ibge"), nullable=False)
    
    entidade: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo_patrimonio: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    num_tombamento: Mapped[str] = mapped_column(String(50), nullable=False)

    data_aquisicao: Mapped[Optional[date]] = mapped_column(Date)
    data_incorporacao: Mapped[Optional[date]] = mapped_column(Date)

    status_patrimonio: Mapped[str] = mapped_column(String(50), nullable=False)
    centro_custo: Mapped[str] = mapped_column(String(100), nullable=False)
    fornecedor: Mapped[str] = mapped_column(String(150), nullable=False)
    valor_contabil: Mapped[float] = mapped_column(Float, nullable=False)
    sit_aquisicao: Mapped[str] = mapped_column(String(100), nullable=False)
