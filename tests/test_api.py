import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.database import Base, get_db
from app.main import app
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Test database — shared in-memory SQLite usable across threads
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Таблица умножения" in response.text


def test_train_page(client):
    response = client.get("/train")
    assert response.status_code == 200
    assert "Выбери режим тренировки" in response.text


def test_create_training(client):
    # First visit home to set session cookie
    client.get("/")
    
    response = client.post(
        "/api/training",
        json={
            "mode": "practice",
            "tables": [2, 3],
            "question_count": 10
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert isinstance(data["session_id"], int)


def test_get_question(client):
    # First visit home to set session cookie
    client.get("/")
    
    # Create training
    create_response = client.post(
        "/api/training",
        json={
            "mode": "practice",
            "tables": [2],
            "question_count": 5
        }
    )
    session_id = create_response.json()["session_id"]
    
    # Get question
    response = client.get(f"/api/training/{session_id}/question")
    
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "left_operand" in data["question"]
    assert "right_operand" in data["question"]
    assert "answer" in data["question"]


def test_submit_answer(client):
    # First visit home to set session cookie
    client.get("/")
    
    # Create training
    create_response = client.post(
        "/api/training",
        json={
            "mode": "practice",
            "tables": [2],
            "question_count": 5
        }
    )
    session_id = create_response.json()["session_id"]
    
    # Get question
    question_response = client.get(f"/api/training/{session_id}/question")
    question = question_response.json()["question"]
    correct_answer = question["answer"]
    
    # Submit correct answer
    response = client.post(
        f"/api/training/{session_id}/answer",
        json={
            "answer": correct_answer,
            "response_time": 2.0
        }
    )
    
    assert response.status_code == 200


def test_progress_page(client):
    # First visit home to set session cookie
    client.get("/")
    
    response = client.get("/progress")
    assert response.status_code == 200
    assert "Твой прогресс" in response.text


def test_table_page(client):
    response = client.get("/table")
    assert response.status_code == 200
    assert "Таблица умножения" in response.text


def test_table_detail(client):
    response = client.get("/table/7")
    assert response.status_code == 200
    assert "Таблица ×7" in response.text


def test_settings_page(client):
    response = client.get("/settings")
    assert response.status_code == 200
    assert "Настройки" in response.text


def test_reset_progress(client):
    # First visit home to set session cookie
    client.get("/")
    
    response = client.post("/api/progress/reset")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_404_page(client):
    response = client.get("/nonexistent-page")
    assert response.status_code == 404
    assert "Страница не найдена" in response.text
