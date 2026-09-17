from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.question import QuestionResult
from app.models.suggestion import Suggestion
from app.models.training import TrainingSession
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

MODE_NAMES = {
    "practice": "Тренировка",
    "timed": "На время",
    "mistakes": "Ошибки",
    "challenge": "Испытание",
}


@router.get("/admin/stats", response_class=HTMLResponse)
async def admin_stats(request: Request, db: Session = Depends(get_db)):
    if settings.admin_key:
        if request.query_params.get("key") != settings.admin_key:
            raise HTTPException(status_code=404)

    week_ago = datetime.utcnow() - timedelta(days=7)

    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(func.distinct(TrainingSession.user_id))).scalar() or 0
    active_week = db.query(func.count(func.distinct(TrainingSession.user_id))).filter(
        TrainingSession.started_at >= week_ago
    ).scalar() or 0
    total_sessions = db.query(func.count(TrainingSession.id)).scalar() or 0
    finished_sessions = db.query(func.count(TrainingSession.id)).filter(
        TrainingSession.finished_at.isnot(None)
    ).scalar() or 0
    total_answers = db.query(func.count(QuestionResult.id)).scalar() or 0
    correct_answers = db.query(func.count(QuestionResult.id)).filter(
        QuestionResult.is_correct == 1
    ).scalar() or 0
    accuracy = (correct_answers / total_answers * 100) if total_answers else 0
    best_streak = db.query(func.max(TrainingSession.max_streak)).scalar() or 0

    mode_stats = dict(
        db.query(TrainingSession.mode, func.count(TrainingSession.id))
        .group_by(TrainingSession.mode)
        .all()
    )

    recent_sessions = (
        db.query(TrainingSession)
        .order_by(TrainingSession.started_at.desc())
        .limit(10)
        .all()
    )

    suggestions = (
        db.query(Suggestion)
        .order_by(Suggestion.created_at.desc())
        .limit(50)
        .all()
    )

    return templates.TemplateResponse(request, "admin/stats.html", {
        "request": request,
        "total_users": total_users,
        "active_users": active_users,
        "active_week": active_week,
        "total_sessions": total_sessions,
        "finished_sessions": finished_sessions,
        "total_answers": total_answers,
        "accuracy": accuracy,
        "best_streak": best_streak,
        "mode_stats": mode_stats,
        "mode_names": MODE_NAMES,
        "recent_sessions": recent_sessions,
        "suggestions": suggestions,
    })
