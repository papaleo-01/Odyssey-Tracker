from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

import app.crud as crud
import app.auth as auth_module
import app.analytics as analytics
from app.database import get_db
from app.schemas import FuelEntryCreate
from app.config import CURRENCY, APP_TITLE
from app.utils import get_selected_car
from app.templates_config import templates

router = APIRouter(prefix="/fuel")

FUEL_TYPES = ["Diesel", "Petrol", "E10", "E5", "LPG", "CNG", "Electric"]


def _ctx(request: Request, cars=None, **kwargs):
    return {"request": request, "currency": CURRENCY, "app_title": APP_TITLE, "fuel_types": FUEL_TYPES, "cars": cars or [], **kwargs}


def _guard(request: Request):
    if not auth_module.is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    return None


@router.get("")
async def fuel_list(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    car, cars = get_selected_car(request, db)
    if not car:
        return RedirectResponse("/car/add", status_code=302)
    entries = crud.get_fuel_entries(db, car.id)
    stats = analytics.compute_fuel_stats(entries)
    return templates.TemplateResponse("fuel/list.html", _ctx(request, cars=cars, car=car, stats=stats))


@router.get("/add")
async def fuel_add_form(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    car, cars = get_selected_car(request, db)
    if not car:
        return RedirectResponse("/car/add", status_code=302)
    entries = crud.get_fuel_entries(db, car.id)
    last_odometer = entries[0].odometer if entries else (car.purchase_mileage or 0)
    return templates.TemplateResponse("fuel/add.html", _ctx(request, cars=cars, car=car, today=date.today(), last_odometer=last_odometer, entry=None))


@router.post("/add")
async def fuel_add_submit(
    request: Request,
    date_field: date = Form(..., alias="date"),
    liters: float = Form(...),
    total_cost: float = Form(...),
    odometer: Optional[str] = Form(None),
    full_tank: bool = Form(True),
    fuel_type: str = Form("Diesel"),
    station: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if r := _guard(request):
        return r
    car, _ = get_selected_car(request, db)
    crud.create_fuel_entry(db, FuelEntryCreate(
        car_id=car.id,
        date=date_field,
        liters=liters,
        total_cost=total_cost,
        odometer=float(odometer) if odometer else None,
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
    car, cars = get_selected_car(request, db)
    return templates.TemplateResponse("fuel/add.html", _ctx(request, cars=cars, car=car, today=date.today(), entry=entry, last_odometer=entry.odometer))


@router.post("/{entry_id}/edit")
async def fuel_edit_submit(
    entry_id: int,
    request: Request,
    date_field: date = Form(..., alias="date"),
    liters: float = Form(...),
    total_cost: float = Form(...),
    odometer: Optional[str] = Form(None),
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
        "odometer": float(odometer) if odometer else None, "full_tank": full_tank,
        "fuel_type": fuel_type, "station": station or None, "notes": notes or None,
    })
    return RedirectResponse("/log", status_code=302)


@router.post("/{entry_id}/delete")
async def fuel_delete(entry_id: int, request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    crud.delete_fuel_entry(db, entry_id)
    return RedirectResponse("/fuel", status_code=302)
