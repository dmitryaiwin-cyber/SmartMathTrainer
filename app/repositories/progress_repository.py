from sqlalchemy.orm import Session
from app.models.question import QuestionStats
from typing import List


class ProgressRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_stats(self, user_id: int):
        return self.db.query(QuestionStats).filter(QuestionStats.user_id == user_id).all()
