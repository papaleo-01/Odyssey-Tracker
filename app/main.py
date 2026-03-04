from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path

from app.config import SECRET_KEY, APP_TITLE
from app.database import init_db
from app.routers import auth, dashboard, car, fuel, maintenance, inspection
from app.routers.analytics_router import router as analytics_router
from app.routers.log_router import router as log_router
from app.routers.settings_router import router as settings_router

app = FastAPI(title=APP_TITLE, docs_url=None, redoc_url=None)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=86400 * 30)

# Static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(car.router)
app.include_router(fuel.router)
app.include_router(maintenance.router)
app.include_router(inspection.router)
app.include_router(analytics_router)
app.include_router(log_router)
app.include_router(settings_router)


@app.on_event("startup")
async def startup():
    init_db()
