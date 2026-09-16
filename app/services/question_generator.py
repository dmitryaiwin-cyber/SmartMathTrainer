import random
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.question import QuestionStats


class QuestionGenerator:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.min_operand = 2
        self.max_operand = 9
    
    def generate_question(self, tables: Optional[List[int]] = None) -> dict:
        if tables is None or not tables:
            tables = list(range(self.min_operand, self.max_operand + 1))
        
        left = random.choice(tables)
        right = random.randint(1, 10)
        answer = left * right
        
        return {
            "left_operand": left,
            "right_operand": right,
            "answer": answer
        }
    
    def generate_questions(self, tables: List[int], count: int = 10) -> List[dict]:
        questions = []
        used_combinations = set()
        
        while len(questions) < count:
            question = self.generate_question(tables)
            key = f"{question['left_operand']}x{question['right_operand']}"
            
            if key not in used_combinations or len(used_combinations) >= count:
                questions.append(question)
                used_combinations.add(key)
            
            if len(used_combinations) >= len(tables) * 10:
                used_combinations.clear()
        
        random.shuffle(questions)
        return questions
    
    def generate_mistake_questions(self, count: int = 10, tables: Optional[List[int]] = None) -> List[dict]:
        stats = self.db.query(QuestionStats).filter(
            QuestionStats.user_id == self.user_id,
            QuestionStats.wrong_count > 0
        ).all()
        
        # Filter by selected tables if provided
        if tables:
            stats = [s for s in stats if any(
                s.question_key.startswith(f"{table}x") for table in tables
            )]
        
        if not stats:
            return []
        
        # Weight by mistake rate — the more mistakes, the more often the question appears
        weights = [stat.wrong_count / stat.attempts for stat in stats]
        selected = random.choices(stats, weights=weights, k=count)
        
        questions = []
        for stat in selected:
            left, right = map(int, stat.question_key.split('x'))
            questions.append({
                "left_operand": left,
                "right_operand": right,
                "answer": left * right
            })
        
        return questions
