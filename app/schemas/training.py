from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class TrainingCreate(BaseModel):
    mode: str = Field(..., description="Training mode: practice, timed, mistakes, challenge")
    tables: List[int] = Field(default_factory=list, description="Selected multiplication tables")
    question_count: int = Field(default=10, ge=1, le=100)
    time_limit: Optional[int] = Field(default=None, ge=10, le=600, description="Time limit in seconds for timed mode")
    operation_mode: Literal["multiply", "mixed", "divide"] = Field(default="multiply", description="Operations: multiply, mixed, divide")


class TrainingResponse(BaseModel):
    id: int
    mode: str
    tables: List[int]
    question_count: int
    time_limit: Optional[int]
    started_at: datetime
    
    class Config:
        from_attributes = True


class AnswerRequest(BaseModel):
    answer: int = Field(..., description="User's answer")
    response_time: Optional[float] = Field(default=None, description="Response time in seconds")


class AnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: int
    score: int
    streak: int
    question_number: int
    total_questions: int
    feedback: str


class TrainingResult(BaseModel):
    id: int
    mode: str
    correct_count: int
    wrong_count: int
    score: int
    max_streak: int
    accuracy: float
    finished_at: Optional[datetime]
    
    class Config:
        from_attributes = True
