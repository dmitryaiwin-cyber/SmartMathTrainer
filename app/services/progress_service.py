from sqlalchemy.orm import Session
from app.models.training import TrainingSession
from app.models.question import QuestionResult, QuestionStats
from app.models.achievement import UserAchievement


class ProgressService:
    def __init__(self, db: Session):
        self.db = db
    
    def reset_user_progress(self, user_id: int):
        self.db.query(QuestionResult).filter(
            QuestionResult.session_id.in_(
                self.db.query(TrainingSession.id).filter(TrainingSession.user_id == user_id)
            )
        ).delete(synchronize_session=False)
        
        self.db.query(TrainingSession).filter(TrainingSession.user_id == user_id).delete()
        
        self.db.query(QuestionStats).filter(QuestionStats.user_id == user_id).delete()
        
        self.db.query(UserAchievement).filter(UserAchievement.user_id == user_id).delete()
        
        self.db.commit()
