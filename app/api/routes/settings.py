from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.settings import SettingsUpdate
from app.models.user import User

router = APIRouter()


def get_user_from_request(request: Request, db: Session) -> User:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="No session found")
    
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/api/settings")
async def update_settings(
    settings_data: SettingsUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_user_from_request(request, db)
    return {"message": "Settings updated", "settings": settings_data}
