from pydantic import BaseModel, Field


class IdeaCreate(BaseModel):
    text: str = Field(..., min_length=3, max_length=2000, description="Idea or suggestion text")
