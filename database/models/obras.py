from sqlalchemy import String, DateTime, ForeignKey, Text, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


from database.connection import Base


class DadosObras(Base):
    __tablename__ = "dados_obras"

    __table_args__ = (
        UniqueConstraint('id_cidade', 'entidade', 'numero_obra', name='uix_cidade_obra', unique=True)
    )

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False, incubator="autoincrement")
    id_cidade: Mapped[int] = mapped_column(ForeignKey("cidades.id_ibge"), nullable=False)
    entidade: Mapped[str] = mapped_column(String(150), nullable=False)

    numero_obra: Mapped[str] = mapped_column(String, nullable=False)
    ano_obra: Mapped[str] = mapped_column(String, nullable=False)
    cnpj_cpf_empresa: Mapped[str] = mapped_column(String(20), nullable=False)
    nome_empresa: Mapped[str] = mapped_column(String(), nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)
    descricao_da_obra: Mapped[str] = mapped_column(Text, nullable=False)

    data_cadastramento: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    data_inicio_execucao: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    data_previsao_conclusao: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    situacao_obra: Mapped[str] = mapped_column(String(50), nullable=False)

    qtd_contratada: Mapped[float] = mapped_column(Float, nullable=False)
    valor_unit_contratado: Mapped[float] = mapped_column(Float, nullable=False)
    valor_tot_contratado: Mapped[float] = mapped_column(Float, nullable=False)
    percentual_contratado: Mapped[float] = mapped_column(Float, nullable=False)
    qtd_executada: Mapped[float] = mapped_column(Float, nullable=False)
    valor_unit_executado: Mapped[float] = mapped_column(Float, nullable=False)
    valor_tot_executado: Mapped[float] = mapped_column(Float, nullable=False)
    percentual_executado: Mapped[float] = mapped_column(Float, nullable=False)
    percentual_pago: Mapped[float] = mapped_column(Float, nullable=False)




