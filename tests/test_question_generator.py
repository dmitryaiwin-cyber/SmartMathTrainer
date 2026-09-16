import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.models.question import QuestionStats
from app.models.user import User
from app.services.question_generator import QuestionGenerator
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


def test_generate_question_basic(db_session):
    session, user_id = db_session
    generator = QuestionGenerator(session, user_id)
    
    question = generator.generate_question([2, 3, 4])
    
    assert "left_operand" in question
    assert "right_operand" in question
    assert "answer" in question
    assert question["left_operand"] in [2, 3, 4]
    assert 1 <= question["right_operand"] <= 10
    assert question["answer"] == question["left_operand"] * question["right_operand"]


def test_generate_question_all_tables(db_session):
    session, user_id = db_session
    generator = QuestionGenerator(session, user_id)
    
    question = generator.generate_question()
    
    assert 2 <= question["left_operand"] <= 9
    assert 1 <= question["right_operand"] <= 10
    assert question["answer"] == question["left_operand"] * question["right_operand"]


def test_generate_questions_count(db_session):
    session, user_id = db_session
    generator = QuestionGenerator(session, user_id)
    
    questions = generator.generate_questions([2, 3], count=5)
    
    assert len(questions) == 5
    for q in questions:
        assert q["left_operand"] in [2, 3]
        assert q["answer"] == q["left_operand"] * q["right_operand"]


def test_generate_questions_variety(db_session):
    session, user_id = db_session
    generator = QuestionGenerator(session, user_id)
    
    questions = generator.generate_questions([2, 3], count=20)
    
    # Check that we get variety, not all the same question
    combinations = set((q["left_operand"], q["right_operand"]) for q in questions)
    assert len(combinations) > 1


def test_generate_mistake_questions_no_mistakes(db_session):
    session, user_id = db_session
    generator = QuestionGenerator(session, user_id)
    
    questions = generator.generate_mistake_questions(count=5)
    
    assert questions == []


def test_generate_mistake_questions_with_mistakes(db_session):
    session, user_id = db_session
    generator = QuestionGenerator(session, user_id)
    
    # Add some mistake stats
    stats = QuestionStats(
        user_id=user_id,
        question_key="7x8",
        attempts=5,
        correct_count=2,
        wrong_count=3
    )
    session.add(stats)
    session.commit()
    
    questions = generator.generate_mistake_questions(count=3)
    
    assert len(questions) > 0
    for q in questions:
        assert q["left_operand"] == 7
        assert q["right_operand"] == 8
        assert q["answer"] == 56


def test_generate_mistake_questions_weighted(db_session):
    session, user_id = db_session
    generator = QuestionGenerator(session, user_id)
    
    # Add stats with different mistake rates
    stats1 = QuestionStats(user_id=user_id, question_key="7x8", attempts=10, correct_count=5, wrong_count=5)
    stats2 = QuestionStats(user_id=user_id, question_key="6x7", attempts=10, correct_count=9, wrong_count=1)
    session.add(stats1)
    session.add(stats2)
    session.commit()
    
    # Generate multiple times and check distribution
    questions_7x8 = 0
    questions_6x7 = 0
    
    for _ in range(20):
        questions = generator.generate_mistake_questions(count=1)
        if questions:
            if questions[0]["left_operand"] == 7 and questions[0]["right_operand"] == 8:
                questions_7x8 += 1
            elif questions[0]["left_operand"] == 6 and questions[0]["right_operand"] == 7:
                questions_6x7 += 1
    
    # 7x8 should appear more often due to higher mistake rate
    assert questions_7x8 > questions_6x7
