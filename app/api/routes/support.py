import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.suggestion import Suggestion
from app.models.user import User
from app.schemas.idea import IdeaCreate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/ideas")
async def submit_idea(
    idea_data: IdeaCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    session_id = request.cookies.get("session_id")
    user = None
    if session_id:
        user = db.query(User).filter(User.session_id == session_id).first()
    
    suggestion = Suggestion(
        user_id=user.id if user else None,
        text=idea_data.text.strip()
    )
    db.add(suggestion)
    db.commit()
    
    logger.info(f"New suggestion #{suggestion.id} from user {suggestion.user_id}")
    return {"message": "Спасибо за идею!"}
