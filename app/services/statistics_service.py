from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.question import QuestionResult, QuestionStats
from app.models.training import TrainingSession
from app.schemas.progress import ProgressStats, TableProgress


class StatisticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_progress(self, user_id: int) -> ProgressStats:
        total_solved = self.db.query(func.count(QuestionResult.id)).filter(
            QuestionResult.session_id.in_(
                self.db.query(TrainingSession.id).filter(TrainingSession.user_id == user_id)
            )
        ).scalar() or 0
        
        total_correct = self.db.query(func.count(QuestionResult.id)).filter(
            QuestionResult.session_id.in_(
                self.db.query(TrainingSession.id).filter(TrainingSession.user_id == user_id)
            ),
            QuestionResult.is_correct == 1
        ).scalar() or 0
        
        total_wrong = total_solved - total_correct
        accuracy = (total_correct / total_solved * 100) if total_solved > 0 else 0
        
        best_streak = self.db.query(func.max(TrainingSession.max_streak)).filter(
            TrainingSession.user_id == user_id
        ).scalar() or 0
        
        return ProgressStats(
            total_solved=total_solved,
            total_correct=total_correct,
            total_wrong=total_wrong,
            accuracy=accuracy,
            best_streak=best_streak
        )
    
    def get_table_progress(self, user_id: int) -> List[TableProgress]:
        table_stats = self.db.query(
            QuestionStats.question_key,
            QuestionStats.attempts,
            QuestionStats.correct_count
        ).filter(QuestionStats.user_id == user_id).all()
        
        progress_by_table = {}
        
        for stat in table_stats:
            # Keys: "9x6" for multiplication, "9d6" for division — table number is the prefix
            if 'x' in stat.question_key:
                table_num = int(stat.question_key.split('x')[0])
            elif 'd' in stat.question_key:
                table_num = int(stat.question_key.split('d')[0])
            else:
                continue
            if table_num not in progress_by_table:
                progress_by_table[table_num] = {"attempts": 0, "correct": 0}
            progress_by_table[table_num]["attempts"] += stat.attempts
            progress_by_table[table_num]["correct"] += stat.correct_count
        
        result = []
        for table_num in range(2, 10):
            if table_num in progress_by_table:
                attempts = progress_by_table[table_num]["attempts"]
                correct = progress_by_table[table_num]["correct"]
                accuracy = (correct / attempts * 100) if attempts > 0 else 0
            else:
                attempts = 0
                accuracy = 0
            
            result.append(TableProgress(
                table=table_num,
                accuracy=accuracy,
                attempts=attempts
            ))
        
        return result
