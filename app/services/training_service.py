from datetime import datetime
from typing import Optional, List
import json
from sqlalchemy.orm import Session
from app.models.training import TrainingSession, TrainingMode
from app.models.question import Question, QuestionResult, QuestionStats
from app.schemas.training import TrainingCreate, AnswerRequest
from app.services.question_generator import QuestionGenerator
from app.services.scoring_service import ScoringService


class TrainingService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, user_id: int, training_data: TrainingCreate) -> TrainingSession:
        session = TrainingSession(
            user_id=user_id,
            mode=training_data.mode,
            operation_mode=training_data.operation_mode,
            tables=",".join(map(str, training_data.tables)) if training_data.tables else None,
            question_count=training_data.question_count,
            time_limit=training_data.time_limit
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_session(self, session_id: int) -> Optional[TrainingSession]:
        return self.db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    
    def get_current_question(self, session: TrainingSession) -> Optional[dict]:
        # Check time limit for timed mode
        if session.time_limit and session.started_at:
            elapsed = (datetime.utcnow() - session.started_at).total_seconds()
            if elapsed >= session.time_limit:
                return None
        
        answered_count = self.db.query(QuestionResult).filter(
            QuestionResult.session_id == session.id
        ).count()
        
        # Check if we've answered all questions (except timed mode which is unlimited)
        if session.mode != TrainingMode.TIMED and answered_count >= session.question_count:
            return None
        
        # If we have a current question stored, return it
        if session.current_question:
            try:
                return json.loads(session.current_question)
            except json.JSONDecodeError:
                # If JSON is corrupted, clear it and generate new question
                session.current_question = None
                self.db.commit()
        
        # Generate new question and store it
        generator = QuestionGenerator(self.db, session.user_id)
        
        tables = list(map(int, session.tables.split(","))) if session.tables else None
        operation_mode = session.operation_mode or "multiply"
        
        if session.mode == TrainingMode.MISTAKES:
            questions = generator.generate_mistake_questions(count=1, tables=tables, operation_mode=operation_mode)
            if not questions:
                return None
            question = questions[0]
        else:
            questions = generator.generate_questions(tables, count=1, operation_mode=operation_mode)
            question = questions[0] if questions else None
        
        if question:
            session.current_question = json.dumps(question)
            self.db.commit()
        
        return question
    
    def submit_answer(self, session: TrainingSession, answer_data: AnswerRequest) -> dict:
        # Get current question BEFORE submitting answer
        current_question = self.get_current_question(session)
        if not current_question:
            return {"error": "Вопросы закончились"}
        
        is_correct = answer_data.answer == current_question["answer"]
        
        streak = self._calculate_streak(session, is_correct)
        score = ScoringService.calculate_score(is_correct, streak)
        
        result = QuestionResult(
            session_id=session.id,
            question_id=0,  # Will be updated if we implement question persistence
            user_answer=answer_data.answer,
            is_correct=1 if is_correct else 0,
            response_time=answer_data.response_time
        )
        self.db.add(result)
        
        session.correct_count += 1 if is_correct else 0
        session.wrong_count += 0 if is_correct else 1
        session.score += score
        session.max_streak = max(session.max_streak, streak)
        
        # Store feedback before clearing current_question
        op_symbol = current_question.get("operator", "×")
        feedback_text = "Правильно!" if is_correct else f"Неверно. {current_question['left_operand']} {op_symbol} {current_question['right_operand']} = {current_question['answer']}"
        
        # Clear current question so next one gets generated
        session.current_question = None
        
        self._update_question_stats(
            session.user_id,
            current_question.get("key") or f"{current_question['left_operand']}x{current_question['right_operand']}",
            is_correct,
            answer_data.response_time
        )
        
        self.db.commit()
        
        answered_count = self.db.query(QuestionResult).filter(
            QuestionResult.session_id == session.id
        ).count()
        
        return {
            "is_correct": is_correct,
            "correct_answer": current_question["answer"],
            "score": score,
            "streak": streak,
            "question_number": answered_count,
            "total_questions": session.question_count,
            "feedback": feedback_text
        }
    
    def _calculate_streak(self, session: TrainingSession, is_correct: bool) -> int:
        if not is_correct:
            return 0
        
        last_results = self.db.query(QuestionResult).filter(
            QuestionResult.session_id == session.id
        ).order_by(QuestionResult.id.desc()).limit(10).all()
        
        streak = 1
        for result in reversed(last_results):
            if result.is_correct:
                streak += 1
            else:
                break
        
        return streak
    
    def _update_question_stats(self, user_id: int, key: str, is_correct: bool, response_time: Optional[float]):
        stats = self.db.query(QuestionStats).filter(
            QuestionStats.user_id == user_id,
            QuestionStats.question_key == key
        ).first()
        
        if not stats:
            stats = QuestionStats(
                user_id=user_id,
                question_key=key,
                attempts=0,
                correct_count=0,
                wrong_count=0
            )
            self.db.add(stats)
        
        stats.attempts += 1
        if is_correct:
            stats.correct_count += 1
        else:
            stats.wrong_count += 1
        
        if response_time:
            if stats.average_response_time is None:
                stats.average_response_time = response_time
            else:
                stats.average_response_time = (stats.average_response_time * (stats.attempts - 1) + response_time) / stats.attempts
    
    def finish_session(self, session: TrainingSession) -> TrainingSession:
        session.finished_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_session_result(self, session: TrainingSession) -> dict:
        total = session.correct_count + session.wrong_count
        accuracy = (session.correct_count / total * 100) if total > 0 else 0
        
        return {
            "id": session.id,
            "mode": session.mode,
            "correct_count": session.correct_count,
            "wrong_count": session.wrong_count,
            "score": session.score,
            "max_streak": session.max_streak,
            "accuracy": accuracy,
            "finished_at": session.finished_at
        }
