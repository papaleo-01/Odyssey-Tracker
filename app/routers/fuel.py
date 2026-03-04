from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import date
from typing import Optional

import app.crud as crud
import app.auth as auth_module
import app.analytics as analytics
from app.database import get_db
from app.schemas import FuelEntryCreate
from app.config import CURRENCY, APP_TITLE

router = APIRouter(prefix="/fuel")
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

FUEL_TYPES = ["Diesel", "Petrol", "E10", "E5", "LPG", "CNG", "Electric"]


def _ctx(request: Request, **kwargs):
    return {"request": request, "currency": CURRENCY, "app_title": APP_TITLE, "fuel_types": FUEL_TYPES, **kwargs}


def _guard(request: Request):
    if not auth_module.is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    return None


@router.get("")
async def fuel_list(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    cars = crud.get_cars(db)
    if not cars:
        return RedirectResponse("/car/setup", status_code=302)
    car = cars[0]
    entries = crud.get_fuel_entries(db, car.id)
    stats = analytics.compute_fuel_stats(entries)
    return templates.TemplateResponse("fuel/list.html", _ctx(request, car=car, stats=stats))


@router.get("/add")
async def fuel_add_form(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    cars = crud.get_cars(db)
    if not cars:
        return RedirectResponse("/car/setup", status_code=302)
    car = cars[0]
    # Pre-fill odometer with latest reading
    entries = crud.get_fuel_entries(db, car.id)
    last_odometer = entries[0].odometer if entries else (car.purchase_mileage or 0)
    return templates.TemplateResponse("fuel/add.html", _ctx(request, car=car, today=date.today(), last_odometer=last_odometer, entry=None))


@router.post("/add")
async def fuel_add_submit(
    request: Request,
    date_field: date = Form(..., alias="date"),
    liters: float = Form(...),
    total_cost: float = Form(...),
    odometer: float = Form(...),
    full_tank: bool = Form(True),
    fuel_type: str = Form("Diesel"),
    station: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if r := _guard(request):
        return r
    cars = crud.get_cars(db)
    car = cars[0]
    crud.create_fuel_entry(db, FuelEntryCreate(
        car_id=car.id,
        date=date_field,
        liters=liters,
        total_cost=total_cost,
        odometer=odometer,
        full_tank=full_tank,
        fuel_type=fuel_type,
        station=station or None,
        notes=notes or None,
    ))
    return RedirectResponse("/fuel", status_code=302)


@router.get("/{entry_id}/edit")
async def fuel_edit_form(entry_id: int, request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    entry = crud.get_fuel_entry(db, entry_id)
    if not entry:
        return RedirectResponse("/fuel", status_code=302)
    cars = crud.get_cars(db)
    return templates.TemplateResponse("fuel/add.html", _ctx(request, car=cars[0], today=date.today(), entry=entry, last_odometer=entry.odometer))


@router.post("/{entry_id}/edit")
async def fuel_edit_submit(
    entry_id: int,
    request: Request,
    date_field: date = Form(..., alias="date"),
    liters: float = Form(...),
    total_cost: float = Form(...),
    odometer: float = Form(...),
    full_tank: bool = Form(True),
    fuel_type: str = Form("Diesel"),
    station: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if r := _guard(request):
        return r
    crud.update_fuel_entry(db, entry_id, {
        "date": date_field, "liters": liters, "total_cost": total_cost,
        "odometer": odometer, "full_tank": full_tank, "fuel_type": fuel_type,
        "station": station or None, "notes": notes or None,
    })
    return RedirectResponse("/fuel", status_code=302)


@router.post("/{entry_id}/delete")
async def fuel_delete(entry_id: int, request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    crud.delete_fuel_entry(db, entry_id)
    return RedirectResponse("/fuel", status_code=302)
