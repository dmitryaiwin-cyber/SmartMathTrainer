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
    ops = request.query_params.get("ops", "")
    
    mistakes_count = db.query(func.count(QuestionStats.id)).filter(
        QuestionStats.user_id == user.id,
        QuestionStats.wrong_count > 0
    ).scalar() or 0
    
    # If tables or operation mode are specified, filter by them
    table_list = [int(t) for t in tables.split(",") if t.isdigit()] if tables else []
    if table_list or ops in ("multiply", "divide"):
        filtered_stats = db.query(QuestionStats).filter(
            QuestionStats.user_id == user.id,
            QuestionStats.wrong_count > 0
        ).all()
        
        def matches(stat) -> bool:
            if ops == "multiply" and "x" not in stat.question_key:
                return False
            if ops == "divide" and "d" not in stat.question_key:
                return False
            if table_list:
                return any(
                    stat.question_key.startswith(f"{table}x") or stat.question_key.startswith(f"{table}d")
                    for table in table_list
                )
            return True
        
        mistakes_count = sum(1 for stat in filtered_stats if matches(stat))
    
    return {"has_mistakes": mistakes_count > 0}
