from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from typing import Optional

from database.connection import Base

class DadosOrcamento(Base):
    __tablename__ = "dados_orcamento"


    __table_args__ = (
        UniqueConstraint('id_cidade', 'funcao', 'subfuncao', 'programa', 'acao', 'vinculo', 'categoria_economica',
                         'grupo_despesa', 'modalidade', 'mes_referencia', 'ano_exercicio', name='uix_cidade_patrimonio', unique=True)
    )

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False, incubator="autoincrement")
    id_cidade: Mapped[int] = mapped_column(ForeignKey("cidades.id_ibge"), nullable=False)

    ano_exercicio: Mapped[str] = mapped_column(String(4), nullable=False)
    mes_referencia: Mapped[str] = mapped_column(String(2), nullable=False)

    entidade: Mapped[str] = mapped_column(String(150), nullable=False)
    funcao: Mapped[str] = mapped_column(Text, nullable=False)
    subfuncao: Mapped[str] = mapped_column(Text, nullable=False)
    programa: Mapped[str] = mapped_column(Text, nullable=False)
    acao: Mapped[str] = mapped_column(Text, nullable=False)
    vinculo: Mapped[str] = mapped_column(Text, nullable=False)
    categoria_economica: Mapped[str] = mapped_column(Text, nullable=False)
    grupo_despesa: Mapped[str] = mapped_column(Text, nullable=False)
    modalidade: Mapped[str] = mapped_column(Text, nullable=False)

    orcamento_inicial: Mapped[float] = mapped_column(Float, nullable=False)
    orcamento_atualizado: Mapped[float] = mapped_column(Float, nullable=False)
    empenhado_no_periodo: Mapped[float] = mapped_column(Float, nullable=False)
    liquidado_no_periodo: Mapped[float] = mapped_column(Float, nullable=False)
    pago_no_periodo: Mapped[float] = mapped_column(Float, nullable=False)

