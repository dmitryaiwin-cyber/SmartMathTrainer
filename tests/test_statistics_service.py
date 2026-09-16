import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.models.user import User
from app.models.training import TrainingSession
from app.models.question import QuestionResult, QuestionStats
from app.services.statistics_service import StatisticsService
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


def test_get_user_progress_no_data(db_session):
    session, user_id = db_session
    stats_service = StatisticsService(session)
    
    progress = stats_service.get_user_progress(user_id)
    
    assert progress.total_solved == 0
    assert progress.total_correct == 0
    assert progress.total_wrong == 0
    assert progress.accuracy == 0
    assert progress.best_streak == 0


def test_get_user_progress_with_data(db_session):
    session, user_id = db_session
    stats_service = StatisticsService(session)
    
    # Create training session
    training = TrainingSession(
        user_id=user_id,
        mode="practice",
        question_count=10,
        correct_count=7,
        wrong_count=3,
        max_streak=5
    )
    session.add(training)
    session.commit()
    
    # Create question results
    for i in range(7):
        result = QuestionResult(
            session_id=training.id,
            question_id=1,
            user_answer=10,
            is_correct=1,
            response_time=2.0
        )
        session.add(result)
    
    for i in range(3):
        result = QuestionResult(
            session_id=training.id,
            question_id=2,
            user_answer=5,
            is_correct=0,
            response_time=3.0
        )
        session.add(result)
    
    session.commit()
    
    progress = stats_service.get_user_progress(user_id)
    
    assert progress.total_solved == 10
    assert progress.total_correct == 7
    assert progress.total_wrong == 3
    assert progress.accuracy == 70.0
    assert progress.best_streak == 5


def test_get_table_progress_no_data(db_session):
    session, user_id = db_session
    stats_service = StatisticsService(session)
    
    table_progress = stats_service.get_table_progress(user_id)
    
    assert len(table_progress) == 8  # Tables 2-9
    for table in table_progress:
        assert table.table in range(2, 10)
        assert table.accuracy == 0
        assert table.attempts == 0


def test_get_table_progress_with_data(db_session):
    session, user_id = db_session
    stats_service = StatisticsService(session)
    
    # Add question stats
    stats1 = QuestionStats(user_id=user_id, question_key="2x3", attempts=10, correct_count=9, wrong_count=1)
    stats2 = QuestionStats(user_id=user_id, question_key="2x4", attempts=10, correct_count=8, wrong_count=2)
    stats3 = QuestionStats(user_id=user_id, question_key="3x5", attempts=5, correct_count=5, wrong_count=0)
    session.add(stats1)
    session.add(stats2)
    session.add(stats3)
    session.commit()
    
    table_progress = stats_service.get_table_progress(user_id)
    
    # Check table 2
    table_2 = next(t for t in table_progress if t.table == 2)
    assert table_2.attempts == 20
    assert table_2.accuracy == 85.0  # (9+8)/20 * 100
    
    # Check table 3
    table_3 = next(t for t in table_progress if t.table == 3)
    assert table_3.attempts == 5
    assert table_3.accuracy == 100.0
    
    # Check table 4 (no data)
    table_4 = next(t for t in table_progress if t.table == 4)
    assert table_4.attempts == 0
    assert table_4.accuracy == 0
