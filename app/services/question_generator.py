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
    
    def generate_question(self, tables: Optional[List[int]] = None, operation_mode: str = "multiply") -> dict:
        if tables is None or not tables:
            tables = list(range(self.min_operand, self.max_operand + 1))
        
        left = random.choice(tables)
        right = random.randint(1, 10)
        
        if operation_mode == "mixed":
            operation_mode = random.choice(["multiply", "divide"])
        
        if operation_mode == "divide":
            return self._make_division_question(left, right)
        return self._make_multiplication_question(left, right)
    
    def _make_multiplication_question(self, left: int, right: int) -> dict:
        return {
            "left_operand": left,
            "right_operand": right,
            "operator": "×",
            "answer": left * right,
            "key": f"{left}x{right}"
        }
    
    def _make_division_question(self, table: int, right: int) -> dict:
        dividend = table * right
        divisor = random.choice([table, right])
        return {
            "left_operand": dividend,
            "right_operand": divisor,
            "operator": "÷",
            "answer": dividend // divisor,
            "key": f"{table}d{right}"
        }
    
    def generate_questions(self, tables: List[int], count: int = 10, operation_mode: str = "multiply") -> List[dict]:
        questions = []
        used_combinations = set()
        
        while len(questions) < count:
            question = self.generate_question(tables, operation_mode)
            key = question["key"]
            
            if key not in used_combinations or len(used_combinations) >= count:
                questions.append(question)
                used_combinations.add(key)
            
            if len(used_combinations) >= len(tables) * 10:
                used_combinations.clear()
        
        random.shuffle(questions)
        return questions
    
    def generate_mistake_questions(self, count: int = 10, tables: Optional[List[int]] = None, operation_mode: str = "multiply") -> List[dict]:
        stats = self.db.query(QuestionStats).filter(
            QuestionStats.user_id == self.user_id,
            QuestionStats.wrong_count > 0
        ).all()
        
        # Filter by selected tables if provided (key starts with the table number)
        if tables:
            stats = [s for s in stats if any(
                s.question_key.startswith(f"{table}x") or s.question_key.startswith(f"{table}d")
                for table in tables
            )]
        
        # Filter by operation mode
        if operation_mode == "multiply":
            stats = [s for s in stats if "x" in s.question_key]
        elif operation_mode == "divide":
            stats = [s for s in stats if "d" in s.question_key]
        
        if not stats:
            return []
        
        # Weight by mistake rate — the more mistakes, the more often the question appears
        weights = [stat.wrong_count / stat.attempts for stat in stats]
        selected = random.choices(stats, weights=weights, k=count)
        
        questions = []
        for stat in selected:
            if "d" in stat.question_key:
                table, right = map(int, stat.question_key.split("d"))
                questions.append(self._make_division_question(table, right))
            else:
                left, right = map(int, stat.question_key.split("x"))
                questions.append(self._make_multiplication_question(left, right))
        
        return questions
