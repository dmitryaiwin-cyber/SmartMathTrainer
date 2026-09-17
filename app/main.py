from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from app.db.database import engine, Base, get_db
from app.core.config import settings
from app.api.routes import pages, training, progress, settings as settings_routes, admin, support
from app.services.achievement_service import AchievementService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Run Alembic migrations
    try:
        from alembic.config import Config
        from alembic import command
        from sqlalchemy import inspect
        
        # Check if tables exist but no migration history
        inspector = inspect(engine)
        tables_exist = "users" in inspector.get_table_names()
        migration_table_exists = "alembic_version" in inspector.get_table_names()
        
        if tables_exist and not migration_table_exists:
            # Tables were created by create_all, stamp initial migration
            logger.info("Tables exist but no migration history. Stamping initial migration...")
            alembic_cfg = Config("alembic.ini")
            command.stamp(alembic_cfg, "001")
        
        # Run migrations
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations applied")
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        # Fallback to create_all for development
        Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    try:
        achievement_service = AchievementService(db)
        achievement_service.initialize_achievements()
        logger.info("Achievements initialized")
    finally:
        db.close()
    
    yield
    
    # Shutdown
    logger.info("Application shutdown")


app = FastAPI(title="Таблица умножения", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.middleware("http")
async def session_cookie_middleware(request: Request, call_next):
    response = await call_next(request)
    session_id = getattr(request.state, "session_id", None)
    if session_id and request.cookies.get("session_id") != session_id:
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=60 * 60 * 24 * 365,
            httponly=True,
            samesite="lax",
        )
    return response

app.include_router(pages.router)
app.include_router(training.router)
app.include_router(progress.router)
app.include_router(settings_routes.router, prefix="/api")
app.include_router(admin.router)
app.include_router(support.router)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(request, "errors/404.html", {"request": request}, status_code=404)


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    logger.error(f"Server error: {exc}")
    return templates.TemplateResponse(request, "errors/500.html", {"request": request}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug)
