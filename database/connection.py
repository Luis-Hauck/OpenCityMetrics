from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
import logging
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
load_dotenv()

database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(
    database_url,
    connect_args={
        "client_encoding": "utf8",
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def get_db():
    """Fornece uma sessão segura e garante o fechamento ao final."""
    db = SessionLocal()
    try:
        yield db
        logger.info('Suce')
    except Exception as e:
        db.rollback()
        logger.error(f"Erro na transação com o banco de dados: {e}")
        raise e
    finally:
        db.close()

