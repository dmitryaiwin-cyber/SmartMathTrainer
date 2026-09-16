from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.statistics_service import StatisticsService
from app.services.achievement_service import AchievementService
from app.models.user import User
import secrets

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_or_create_user(request: Request, db: Session) -> User:
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = secrets.token_hex(16)
    
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        user = User(session_id=session_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user, session_id


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user, session_id = get_or_create_user(request, db)
    response = templates.TemplateResponse(request, "index.html", {"request": request})
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response


@router.get("/train", response_class=HTMLResponse)
async def train_page(request: Request, db: Session = Depends(get_db)):
    user, session_id = get_or_create_user(request, db)
    return templates.TemplateResponse(request, "training/index.html", {"request": request})


@router.get("/train/{session_id}", response_class=HTMLResponse)
async def training_session(request: Request, session_id: int, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "training/session.html", {
        "request": request,
        "session_id": session_id
    })


@router.get("/result/{session_id}", response_class=HTMLResponse)
async def result_page(request: Request, session_id: int, db: Session = Depends(get_db)):
    # Get session to check if it exists and get basic info
    from app.models.training import TrainingSession
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    
    if not session:
        return templates.TemplateResponse(request, "errors/404.html", {"request": request}, status_code=404)
    
    return templates.TemplateResponse(request, "training/result.html", {
        "request": request,
        "session_id": session_id,
        "session": session
    })


@router.get("/progress", response_class=HTMLResponse)
async def progress_page(request: Request, db: Session = Depends(get_db)):
    user, session_id = get_or_create_user(request, db)
    stats_service = StatisticsService(db)
    progress = stats_service.get_user_progress(user.id)
    table_progress = stats_service.get_table_progress(user.id)
    
    return templates.TemplateResponse(request, "progress/index.html", {
        "request": request,
        "progress": progress,
        "table_progress": table_progress
    })


@router.get("/table", response_class=HTMLResponse)
async def table_page(request: Request, db: Session = Depends(get_db)):
    user, session_id = get_or_create_user(request, db)
    return templates.TemplateResponse(request, "table/index.html", {"request": request})


@router.get("/table/{table_num}", response_class=HTMLResponse)
async def table_detail(request: Request, table_num: int, db: Session = Depends(get_db)):
    user, session_id = get_or_create_user(request, db)
    table_data = [(table_num, i, table_num * i) for i in range(1, 11)]
    return templates.TemplateResponse(request, "table/detail.html", {
        "request": request,
        "table_num": table_num,
        "table_data": table_data
    })


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    user, session_id = get_or_create_user(request, db)
    return templates.TemplateResponse(request, "settings/index.html", {"request": request})
