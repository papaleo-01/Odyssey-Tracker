from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

import app.auth as auth_module
import app.analytics as analytics
from app.database import get_db
from app.config import CURRENCY, APP_TITLE
from app.utils import get_selected_car

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/log")
async def log_page(request: Request, db: Session = Depends(get_db)):
    if not auth_module.is_authenticated(request):
        return RedirectResponse("/login", status_code=302)

    car, cars = get_selected_car(request, db)
    if not car:
        return RedirectResponse("/car/add", status_code=302)

    entries = analytics.get_all_entries(car)
    years = sorted({e["year"] for e in entries}, reverse=True)

    flash = request.session.pop("flash", None)

    return templates.TemplateResponse("log.html", {
        "request": request,
        "car": car,
        "cars": cars,
        "entries": entries,
        "years": years,
        "currency": CURRENCY,
        "app_title": APP_TITLE,
        "flash": flash,
    })
