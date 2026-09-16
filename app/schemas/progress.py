from pydantic import BaseModel
from typing import Optional


class ProgressStats(BaseModel):
    total_solved: int
    total_correct: int
    total_wrong: int
    accuracy: float
    best_streak: int


class TableProgress(BaseModel):
    table: int
    accuracy: float
    attempts: int
