from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    left_operand = Column(Integer, nullable=False)
    right_operand = Column(Integer, nullable=False)
    answer = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class QuestionResult(Base):
    __tablename__ = "question_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False, index=True)
    question_id = Column(Integer, nullable=False)
    user_answer = Column(Integer, nullable=False)
    is_correct = Column(Integer, nullable=False)  # 0 or 1
    response_time = Column(Float, nullable=True)  # seconds
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class QuestionStats(Base):
    __tablename__ = "question_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    question_key = Column(String, nullable=False, index=True)  # "7x8"
    attempts = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    wrong_count = Column(Integer, default=0)
    average_response_time = Column(Float, nullable=True)
    last_answered_at = Column(DateTime, server_default=func.now())
