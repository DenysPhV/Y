import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from main import app
from PhotoShare.app.models.base import Base
from PhotoShare.app.core.database import get_db
from PhotoShare.app.core.config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.postgres_user}:" \
                          f"{settings.postgres_password}@snuffleupagus.db.elephantsql.com/{settings.postgres_db_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {"username": "deadpool", "email": "philichkindenis1@gmail.com", "password": "qwerty123456"}


@pytest.fixture(scope="module")
def user_moder():
    return {"username": "dead2pool", "email": "dead2pool@example.com", "password": "123456789"}


@pytest.fixture(scope="module")
def user_user():
    return {"username": "dead1pool", "email": "dead1pool@example.com", "password": "123456789"}
