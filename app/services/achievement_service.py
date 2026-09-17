from typing import List
from sqlalchemy.orm import Session
from app.models.achievement import Achievement, UserAchievement
from app.models.training import TrainingSession
from app.models.question import QuestionResult


class AchievementService:
    def __init__(self, db: Session):
        self.db = db
    
    def initialize_achievements(self):
        achievements = [
            {
                "code": "first_answer",
                "name": "⭐ Первый ответ",
                "description": "Реши первый пример"
            },
            {
                "code": "streak_5",
                "name": "🔥 5 правильных подряд",
                "description": "Ответь правильно 5 раз подряд"
            },
            {
                "code": "streak_10",
                "name": "🔥 10 правильных подряд",
                "description": "Ответь правильно 10 раз подряд"
            },
            {
                "code": "hundred_solved",
                "name": "🏆 100 решённых примеров",
                "description": "Реши 100 примеров"
            },
            {
                "code": "accuracy_90",
                "name": "🚀 90% правильных ответов",
                "description": "Достигни 90% точности"
            }
        ]
        
        for ach in achievements:
            existing = self.db.query(Achievement).filter(Achievement.code == ach["code"]).first()
            if not existing:
                achievement = Achievement(**ach)
                self.db.add(achievement)
        
        self.db.commit()
    
    def check_achievements(self, user_id: int, session: TrainingSession) -> List[Achievement]:
        user_achievements = self.db.query(UserAchievement.achievement_id).filter(
            UserAchievement.user_id == user_id
        ).all()
        earned_ids = {ua[0] for ua in user_achievements}
        
        new_achievements = []
        
        total_solved = self.db.query(QuestionResult).join(
            TrainingSession, QuestionResult.session_id == TrainingSession.id
        ).filter(
            TrainingSession.user_id == user_id
        ).count()
        
        if total_solved >= 1:
            ach = self._get_achievement("first_answer")
            if ach and ach.id not in earned_ids:
                self._award_achievement(user_id, ach.id)
                new_achievements.append(ach)
        
        if session.max_streak >= 5:
            ach = self._get_achievement("streak_5")
            if ach and ach.id not in earned_ids:
                self._award_achievement(user_id, ach.id)
                new_achievements.append(ach)
        
        if session.max_streak >= 10:
            ach = self._get_achievement("streak_10")
            if ach and ach.id not in earned_ids:
                self._award_achievement(user_id, ach.id)
                new_achievements.append(ach)
        
        if total_solved >= 100:
            ach = self._get_achievement("hundred_solved")
            if ach and ach.id not in earned_ids:
                self._award_achievement(user_id, ach.id)
                new_achievements.append(ach)
        
        total_correct = self.db.query(QuestionResult).join(
            TrainingSession, QuestionResult.session_id == TrainingSession.id
        ).filter(
            TrainingSession.user_id == user_id,
            QuestionResult.is_correct == 1
        ).count()
        
        if total_solved > 0 and (total_correct / total_solved) >= 0.9:
            ach = self._get_achievement("accuracy_90")
            if ach and ach.id not in earned_ids:
                self._award_achievement(user_id, ach.id)
                new_achievements.append(ach)
        
        return new_achievements
    
    def _get_achievement(self, code: str) -> Achievement:
        return self.db.query(Achievement).filter(Achievement.code == code).first()
    
    def _award_achievement(self, user_id: int, achievement_id: int):
        user_ach = UserAchievement(user_id=user_id, achievement_id=achievement_id)
        self.db.add(user_ach)
        self.db.commit()
    
    def get_user_achievements(self, user_id: int) -> List[Achievement]:
        return self.db.query(Achievement).join(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()
