from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

import app.crud as crud
import app.auth as auth_module
import app.analytics as analytics
from app.database import get_db
from app.config import CURRENCY, APP_TITLE

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/log")
async def log_page(request: Request, db: Session = Depends(get_db)):
    if not auth_module.is_authenticated(request):
        return RedirectResponse("/login", status_code=302)

    cars = crud.get_cars(db)
    if not cars:
        return RedirectResponse("/car/setup", status_code=302)

    car = cars[0]
    entries = analytics.get_all_entries(car)
    years = sorted({e["year"] for e in entries}, reverse=True)

    flash = request.session.pop("flash", None)

    return templates.TemplateResponse("log.html", {
        "request": request,
        "car": car,
        "entries": entries,
        "years": years,
        "currency": CURRENCY,
        "app_title": APP_TITLE,
        "flash": flash,
    })
