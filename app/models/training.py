from sqlalchemy import Column, Integer, DateTime, String, Enum
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class TrainingMode(str, enum.Enum):
    PRACTICE = "practice"
    TIMED = "timed"
    MISTAKES = "mistakes"
    CHALLENGE = "challenge"


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    mode = Column(String, nullable=False)
    operation_mode = Column(String, default="multiply", nullable=False)  # multiply, mixed, divide
    tables = Column(String)  # JSON string of selected tables
    question_count = Column(Integer, default=10)
    time_limit = Column(Integer, nullable=True)  # seconds for timed mode
    started_at = Column(DateTime, server_default=func.now(), nullable=False)
    finished_at = Column(DateTime, nullable=True)
    correct_count = Column(Integer, default=0)
    wrong_count = Column(Integer, default=0)
    score = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)
    current_question = Column(String, nullable=True)  # JSON string of current question
