from typing import Dict


class ScoringService:
    BASE_POINTS = 10
    STREAK_BONUSES = {
        3: 5,
        5: 10,
        10: 25
    }
    
    @classmethod
    def calculate_score(cls, is_correct: bool, streak: int) -> int:
        if not is_correct:
            return 0
        
        score = cls.BASE_POINTS
        
        for threshold, bonus in cls.STREAK_BONUSES.items():
            if streak >= threshold:
                score += bonus
        
        return score
    
    @classmethod
    def get_streak_bonus(cls, streak: int) -> int:
        bonus = 0
        for threshold, bonus_amount in cls.STREAK_BONUSES.items():
            if streak >= threshold:
                bonus += bonus_amount
        return bonus
