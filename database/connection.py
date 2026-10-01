from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from contextlib import contextmanager
import logging
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
load_dotenv()


class Base(DeclarativeBase):
    pass


db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

if db_user and db_host and db_name:
    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=db_user,
        password=db_password,
        host=db_host,
        port=int(db_port) if db_port else 5432,
        database=db_name,
    )

    engine = create_engine(
        database_url,
        connect_args={
            "client_encoding": "utf8",
        },
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = sessionmaker(autocommit=False, autoflush=False)


@contextmanager
def get_db():
    """Fornece uma sessão segura e garante o fechamento ao final."""
    if SessionLocal is None or engine is None:
        raise RuntimeError("Banco de dados não configurado.")
    db = SessionLocal()
    try:
        yield db
        logger.info('Transação bem-sucedida.')
    except Exception as e:
        db.rollback()
        logger.error(f"Erro na transação com o banco de dados: {e}")
        raise e
    finally:
        db.close()
