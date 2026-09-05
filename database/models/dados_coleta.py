from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column


from database.connection import Base


class DadosColeta(Base):
    __tablename__ = "dados_coleta"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False)
    id_cidade: Mapped[int] = mapped_column(ForeignKey("cidades.id_ibge"), nullable=False)
    software_portal: Mapped[str] = mapped_column(String(50), nullable=False)
    base_de_dados: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    formato_origem: Mapped[str] = mapped_column(String(50), nullable=True)
    frequencia_coleta: Mapped[str] = mapped_column(String(50), nullable=False)
    dados_ausentes: Mapped[int] = mapped_column(Integer, nullable=True)
    data_coleta: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

