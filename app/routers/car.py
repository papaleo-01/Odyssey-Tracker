from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import date
from typing import Optional

import app.crud as crud
import app.auth as auth_module
from app.database import get_db
from app.schemas import CarCreate
from app.config import CURRENCY, APP_TITLE

router = APIRouter(prefix="/car")
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


def _ctx(request: Request, **kwargs):
    return {"request": request, "currency": CURRENCY, "app_title": APP_TITLE, **kwargs}


def _guard(request: Request):
    if not auth_module.is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    return None


@router.get("/setup")
async def car_setup(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    cars = crud.get_cars(db)
    car = cars[0] if cars else None
    return templates.TemplateResponse("car/setup.html", _ctx(request, car=car, today=date.today()))


@router.post("/setup")
async def car_setup_submit(
    request: Request,
    name: str = Form(...),
    make: str = Form(""),
    model: str = Form(""),
    year: Optional[int] = Form(None),
    purchase_date: Optional[date] = Form(None),
    purchase_price: Optional[float] = Form(None),
    purchase_mileage: float = Form(0),
    current_market_value: Optional[float] = Form(None),
    notes: str = Form(""),
    car_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
):
    if r := _guard(request):
        return r

    data = {
        "name": name,
        "make": make or None,
        "model": model or None,
        "year": year,
        "purchase_date": purchase_date,
        "purchase_price": purchase_price,
        "purchase_mileage": purchase_mileage,
        "current_market_value": current_market_value or None,
        "notes": notes or None,
    }

    if car_id:
        crud.update_car(db, car_id, data)
    else:
        crud.create_car(db, CarCreate(**data))

    return RedirectResponse("/", status_code=302)
