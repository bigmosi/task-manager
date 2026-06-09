import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.dependencies import db_get

TEST_DATABASE_URL = "sqlite:///./test_taskmanager.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[db_get] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def authorized_client(client):
    client.post("/users/", json={
        "username": "taskuser",
        "email": "taskuser@example.com",
        "password": "password123"
    })
    response = client.post("/auth/login", data={
        "username": "taskuser",
        "password": "password123"
    })
    token = response.json()["access_token"]
    with TestClient(app, headers={"Authorization": f"Bearer {token}"}) as auth_client:
        yield auth_client