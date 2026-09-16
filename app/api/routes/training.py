from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.schemas.training import TrainingCreate, AnswerRequest, TrainingResult
from app.services.training_service import TrainingService
from app.services.achievement_service import AchievementService
from app.models.user import User
from app.models.question import QuestionResult
import secrets
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def get_user_from_request(request: Request, db: Session) -> User:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="No session found")
    
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/api/training")
async def create_training(
    training_data: TrainingCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_user_from_request(request, db)
    training_service = TrainingService(db)
    session = training_service.create_session(user.id, training_data)
    return {"session_id": session.id}


@router.get("/api/training/{session_id}/question")
async def get_question(session_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_user_from_request(request, db)
    training_service = TrainingService(db)
    session = training_service.get_session(session_id)
    
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    question = training_service.get_current_question(session)
    if not question:
        return {"finished": True}
    
    answered_count = db.query(func.count(QuestionResult.id)).filter(
        QuestionResult.session_id == session_id
    ).scalar() or 0
    
    return {
        "question": question,
        "question_number": answered_count + 1,
        "total_questions": session.question_count,
        "streak": session.max_streak,
        "time_limit": session.time_limit
    }


@router.post("/api/training/{session_id}/answer", response_class=HTMLResponse)
async def submit_answer(
    session_id: int,
    answer_data: AnswerRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user = get_user_from_request(request, db)
        training_service = TrainingService(db)
        session = training_service.get_session(session_id)
        
        if not session or session.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        result = training_service.submit_answer(session, answer_data)
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        return f"<div class='bg-red-100 border-2 border-red-500 rounded-xl p-4 text-red-700'>Ошибка при обработке ответа</div>"
    
    if "error" in result:
        return f"<div class='error'>{result['error']}</div>"
    
    answered_count = result["question_number"]
    total_questions = result["total_questions"]
    
    is_finished = answered_count >= total_questions
    
    if is_finished:
        training_service.finish_session(session)
        achievement_service = AchievementService(db)
        achievements = achievement_service.check_achievements(user.id, session)
        
        from fastapi.templating import Jinja2Templates
        templates = Jinja2Templates(directory="app/templates")
        
        return templates.TemplateResponse(request, "training/feedback_finished.html", {
            "request": request,
            "result": result,
            "session_id": session_id,
            "achievements": achievements
        })
    
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    
    return templates.TemplateResponse(request, "training/feedback.html", {
        "request": request,
        "result": result,
        "session_id": session_id
    })


@router.post("/api/training/{session_id}/finish")
async def finish_training(session_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        user = get_user_from_request(request, db)
        training_service = TrainingService(db)
        session = training_service.get_session(session_id)
        
        if not session or session.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        training_service.finish_session(session)
        achievement_service = AchievementService(db)
        achievements = achievement_service.check_achievements(user.id, session)
        
        result = training_service.get_session_result(session)
        
        return {
            "result": result,
            "achievements": [{"code": a.code, "name": a.name} for a in achievements]
        }
    except Exception as e:
        logger.error(f"Error finishing training: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/training/{session_id}/result")
async def get_training_result(session_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_user_from_request(request, db)
    training_service = TrainingService(db)
    session = training_service.get_session(session_id)
    
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = training_service.get_session_result(session)
    return result
