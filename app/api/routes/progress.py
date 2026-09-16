from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.services.progress_service import ProgressService
from app.models.user import User
from app.models.question import QuestionStats

router = APIRouter()


def get_user_from_request(request: Request, db: Session) -> User:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="No session found")
    
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/api/progress/reset")
async def reset_progress(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_request(request, db)
    progress_service = ProgressService(db)
    progress_service.reset_user_progress(user.id)
    return {"message": "Progress reset successfully"}


@router.get("/api/progress/check-mistakes")
async def check_mistakes(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_request(request, db)
    tables = request.query_params.get("tables", "")
    
    mistakes_count = db.query(func.count(QuestionStats.id)).filter(
        QuestionStats.user_id == user.id,
        QuestionStats.wrong_count > 0
    ).scalar() or 0
    
    # If tables are specified, filter by them
    if tables:
        table_list = [int(t) for t in tables.split(",") if t.isdigit()]
        if table_list:
            filtered_stats = db.query(QuestionStats).filter(
                QuestionStats.user_id == user.id,
                QuestionStats.wrong_count > 0
            ).all()
            
            filtered_mistakes = sum(
                1 for stat in filtered_stats 
                if any(stat.question_key.startswith(f"{table}x") for table in table_list)
            )
            mistakes_count = filtered_mistakes
    
    return {"has_mistakes": mistakes_count > 0}
