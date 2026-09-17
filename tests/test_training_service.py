import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.models.user import User
from app.models.training import TrainingSession
from app.models.question import QuestionResult, QuestionStats
from app.services.training_service import TrainingService
from app.schemas.training import TrainingCreate, AnswerRequest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Create test user
    user = User(session_id="test-session")
    session.add(user)
    session.commit()
    
    yield session, user.id
    
    session.close()


def test_create_session(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)
    
    training_data = TrainingCreate(
        mode="practice",
        tables=[2, 3, 4],
        question_count=10
    )
    
    training_session = training_service.create_session(user_id, training_data)
    
    assert training_session.id is not None
    assert training_session.user_id == user_id
    assert training_session.mode == "practice"
    assert training_session.question_count == 10
    assert training_session.correct_count == 0
    assert training_session.wrong_count == 0


def test_get_session(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)
    
    training_data = TrainingCreate(mode="practice", tables=[2], question_count=5)
    created_session = training_service.create_session(user_id, training_data)
    
    retrieved_session = training_service.get_session(created_session.id)
    
    assert retrieved_session is not None
    assert retrieved_session.id == created_session.id


def test_submit_correct_answer(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)
    
    training_data = TrainingCreate(mode="practice", tables=[2], question_count=5)
    training_session = training_service.create_session(user_id, training_data)
    
    # Get the actual generated question and submit its real answer
    question = training_service.get_current_question(training_session)
    answer_data = AnswerRequest(answer=question["answer"], response_time=2.0)
    result = training_service.submit_answer(training_session, answer_data)
    
    assert result["is_correct"] == True
    assert result["score"] > 0
    assert result["streak"] >= 1
    assert "Правильно!" in result["feedback"]


def test_submit_wrong_answer(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)
    
    training_data = TrainingCreate(mode="practice", tables=[2], question_count=5)
    training_session = training_service.create_session(user_id, training_data)
    
    answer_data = AnswerRequest(answer=99, response_time=2.0)
    result = training_service.submit_answer(training_session, answer_data)
    
    assert result["is_correct"] == False
    assert result["score"] == 0
    assert result["streak"] == 0
    assert "Неверно" in result["feedback"]


def test_streak_calculation(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)
    
    training_data = TrainingCreate(mode="practice", tables=[2], question_count=10)
    training_session = training_service.create_session(user_id, training_data)
    
    # Submit 3 correct answers
    for i in range(3):
        # Get current question
        question = training_service.get_current_question(training_session)
        answer_data = AnswerRequest(answer=question["answer"], response_time=2.0)
        training_service.submit_answer(training_session, answer_data)
    
    session.refresh(training_session)
    assert training_session.max_streak >= 3


def test_finish_session(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)
    
    training_data = TrainingCreate(mode="practice", tables=[2], question_count=5)
    training_session = training_service.create_session(user_id, training_data)
    
    finished_session = training_service.finish_session(training_session)
    
    assert finished_session.finished_at is not None


def test_get_session_result(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)
    
    training_data = TrainingCreate(mode="practice", tables=[2], question_count=5)
    training_session = training_service.create_session(user_id, training_data)
    
    # Submit some answers
    for i in range(3):
        question = training_service.get_current_question(training_session)
        answer_data = AnswerRequest(answer=question["answer"], response_time=2.0)
        training_service.submit_answer(training_session, answer_data)
    
    training_service.finish_session(training_session)
    result = training_service.get_session_result(training_session)
    
    assert result["correct_count"] == 3
    assert result["wrong_count"] == 0
    assert result["accuracy"] == 100.0
    assert result["score"] > 0


def test_question_stats_update(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)
    
    training_data = TrainingCreate(mode="practice", tables=[2], question_count=5)
    training_session = training_service.create_session(user_id, training_data)
    
    # Submit an answer
    question = training_service.get_current_question(training_session)
    answer_data = AnswerRequest(answer=question["answer"], response_time=2.0)
    training_service.submit_answer(training_session, answer_data)
    
    # Check stats were updated
    stats = session.query(QuestionStats).filter(
        QuestionStats.user_id == user_id,
        QuestionStats.question_key == f"{question['left_operand']}x{question['right_operand']}"
    ).first()
    
    assert stats is not None
    assert stats.attempts == 1
    assert stats.correct_count == 1
    assert stats.wrong_count == 0


def test_current_question_persistence(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)
    
    training_data = TrainingCreate(mode="practice", tables=[2], question_count=5)
    training_session = training_service.create_session(user_id, training_data)
    
    # Get question twice - should return same question
    question1 = training_service.get_current_question(training_session)
    session.refresh(training_session)
    question2 = training_service.get_current_question(training_session)
    
    assert question1 == question2
    assert training_session.current_question is not None


def test_current_question_cleared_after_answer(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)
    
    training_data = TrainingCreate(mode="practice", tables=[2], question_count=5)
    training_session = training_service.create_session(user_id, training_data)
    
    # Get question and submit answer
    question = training_service.get_current_question(training_session)
    answer_data = AnswerRequest(answer=question["answer"], response_time=2.0)
    training_service.submit_answer(training_session, answer_data)
    
    session.refresh(training_session)
    assert training_session.current_question is None


def test_last_question_handling(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)
    
    training_data = TrainingCreate(mode="practice", tables=[2], question_count=2)
    training_session = training_service.create_session(user_id, training_data)
    
    # Answer first question
    question1 = training_service.get_current_question(training_session)
    answer_data1 = AnswerRequest(answer=question1["answer"], response_time=2.0)
    result1 = training_service.submit_answer(training_session, answer_data1)
    assert result1["question_number"] == 1
    
    # Answer second (last) question
    question2 = training_service.get_current_question(training_session)
    answer_data2 = AnswerRequest(answer=question2["answer"], response_time=2.0)
    result2 = training_service.submit_answer(training_session, answer_data2)
    assert result2["question_number"] == 2
    
    # Should not have more questions
    question3 = training_service.get_current_question(training_session)
    assert question3 is None


def test_operation_mode_persisted(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)

    training_data = TrainingCreate(mode="practice", tables=[9], question_count=5, operation_mode="divide")
    training_session = training_service.create_session(user_id, training_data)

    assert training_session.operation_mode == "divide"


def test_operation_mode_default_multiply(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)

    training_data = TrainingCreate(mode="practice", tables=[2], question_count=5)
    training_session = training_service.create_session(user_id, training_data)

    assert training_session.operation_mode == "multiply"


def test_division_session_questions(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)

    training_data = TrainingCreate(mode="practice", tables=[7], question_count=5, operation_mode="divide")
    training_session = training_service.create_session(user_id, training_data)

    question = training_service.get_current_question(training_session)

    assert question["operator"] == "÷"
    assert question["answer"] * question["right_operand"] == question["left_operand"]


def test_division_wrong_answer_feedback(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)

    training_data = TrainingCreate(mode="practice", tables=[9], question_count=5, operation_mode="divide")
    training_session = training_service.create_session(user_id, training_data)

    question = training_service.get_current_question(training_session)
    answer_data = AnswerRequest(answer=question["answer"] + 1, response_time=1.0)
    result = training_service.submit_answer(training_session, answer_data)

    assert result["is_correct"] == False
    assert "÷" in result["feedback"]
    assert str(question["answer"]) in result["feedback"]


def test_division_question_stats_key(db_session):
    session, user_id = db_session
    training_service = TrainingService(session)

    training_data = TrainingCreate(mode="practice", tables=[6], question_count=5, operation_mode="divide")
    training_session = training_service.create_session(user_id, training_data)

    question = training_service.get_current_question(training_session)
    answer_data = AnswerRequest(answer=question["answer"], response_time=2.0)
    training_service.submit_answer(training_session, answer_data)

    stats = session.query(QuestionStats).filter(
        QuestionStats.user_id == user_id,
        QuestionStats.question_key == question["key"]
    ).first()

    assert stats is not None
    assert "d" in stats.question_key
    assert stats.correct_count == 1
