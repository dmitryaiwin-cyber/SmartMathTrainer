from sqlalchemy import Column, Integer, DateTime, String, Text
from sqlalchemy.sql import func
from app.db.database import Base


class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
