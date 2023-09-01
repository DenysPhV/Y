from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser
from pathlib import Path

from PhotoShare.app.core.config import settings

path_config = Path(__file__).joinpath('config.py')
config = ConfigParser()
config.read(path_config)

POSTGRES_URL = settings.postgres_path
engine = create_engine(POSTGRES_URL, echo=False, max_overflow=5)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
