from sqlalchemy.orm import Session
from app.models.training import TrainingSession
from typing import Optional


class TrainingRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, session: TrainingSession) -> TrainingSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_by_id(self, session_id: int) -> Optional[TrainingSession]:
        return self.db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    
    def get_user_sessions(self, user_id: int, limit: int = 10):
        return self.db.query(TrainingSession).filter(
            TrainingSession.user_id == user_id
        ).order_by(TrainingSession.started_at.desc()).limit(limit).all()
