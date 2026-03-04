from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

import app.crud as crud
import app.auth as auth_module
from app.database import get_db
from app.schemas import CarCreate, CarValuationCreate
from app.config import CURRENCY, APP_TITLE
from app.utils import get_selected_car
from app.templates_config import templates

router = APIRouter(prefix="/car")


def _ctx(request: Request, cars=None, **kwargs):
    return {"request": request, "currency": CURRENCY, "app_title": APP_TITLE, "cars": cars or [], **kwargs}


def _guard(request: Request):
    if not auth_module.is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    return None


# ── Car switcher ──────────────────────────────────────────────────────────────

@router.get("/switch/{car_id}")
async def car_switch(car_id: int, request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    car = crud.get_car(db, car_id)
    if car:
        request.session["car_id"] = car_id
    return RedirectResponse("/", status_code=302)


# ── Edit current car ──────────────────────────────────────────────────────────

@router.get("/setup")
async def car_setup(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    car, cars = get_selected_car(request, db)
    if not car:
        return RedirectResponse("/car/add", status_code=302)
    valuations = sorted(car.valuations, key=lambda v: v.date, reverse=True)
    return templates.TemplateResponse("car/setup.html", _ctx(request, car=car, cars=cars, valuations=valuations, today=date.today()))


@router.post("/setup")
async def car_setup_submit(
    request: Request,
    car_id: int = Form(...),
    name: str = Form(...),
    make: str = Form(""),
    model: str = Form(""),
    year: Optional[int] = Form(None),
    purchase_date: Optional[date] = Form(None),
    purchase_price: Optional[float] = Form(None),
    purchase_mileage: Optional[float] = Form(None),
    current_market_value: Optional[float] = Form(None),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if r := _guard(request):
        return r
    crud.update_car(db, car_id, {
        "name": name,
        "make": make or None,
        "model": model or None,
        "year": year,
        "purchase_date": purchase_date,
        "purchase_price": purchase_price,
        "purchase_mileage": purchase_mileage if purchase_mileage is not None else 0,
        "current_market_value": current_market_value or None,
        "notes": notes or None,
    })
    request.session["flash"] = "success:Car updated."
    return RedirectResponse("/car/setup", status_code=302)


@router.post("/delete")
async def car_delete(request: Request, car_id: int = Form(...), db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    cars = crud.get_cars(db)
    if len(cars) <= 1:
        request.session["flash"] = "error:Cannot delete the only car."
        return RedirectResponse("/car/setup", status_code=302)
    crud.delete_car(db, car_id)
    remaining = crud.get_cars(db)
    if remaining:
        request.session["car_id"] = remaining[0].id
    request.session["flash"] = "success:Car deleted."
    return RedirectResponse("/", status_code=302)


# ── Add new car ───────────────────────────────────────────────────────────────

@router.get("/add")
async def car_add_form(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    _, cars = get_selected_car(request, db)
    return templates.TemplateResponse("car/setup.html", _ctx(request, car=None, cars=cars, valuations=[], today=date.today()))


@router.post("/add")
async def car_add_submit(
    request: Request,
    name: str = Form(...),
    make: str = Form(""),
    model: str = Form(""),
    year: Optional[int] = Form(None),
    purchase_date: Optional[date] = Form(None),
    purchase_price: Optional[float] = Form(None),
    purchase_mileage: Optional[float] = Form(None),
    current_market_value: Optional[float] = Form(None),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if r := _guard(request):
        return r
    car = crud.create_car(db, CarCreate(
        name=name,
        make=make or None,
        model=model or None,
        year=year,
        purchase_date=purchase_date,
        purchase_price=purchase_price,
        purchase_mileage=purchase_mileage if purchase_mileage is not None else 0,
        current_market_value=current_market_value or None,
        notes=notes or None,
    ))
    request.session["car_id"] = car.id
    request.session["flash"] = f"success:{car.name} added."
    return RedirectResponse("/", status_code=302)


# ── Car valuations ────────────────────────────────────────────────────────────

@router.post("/valuation/add")
async def valuation_add(
    request: Request,
    date_field: date = Form(..., alias="date"),
    value: float = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if r := _guard(request):
        return r
    car, _ = get_selected_car(request, db)
    if car:
        crud.create_valuation(db, CarValuationCreate(
            car_id=car.id,
            date=date_field,
            value=value,
            notes=notes or None,
        ))
    return RedirectResponse("/car/setup", status_code=302)


@router.post("/valuation/{val_id}/delete")
async def valuation_delete(val_id: int, request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    crud.delete_valuation(db, val_id)
    return RedirectResponse("/car/setup", status_code=302)
