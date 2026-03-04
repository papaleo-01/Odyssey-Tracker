from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

import app.crud as crud
import app.auth as auth_module
from app.database import get_db
from app.schemas import MaintenanceEntryCreate
from app.config import CURRENCY, APP_TITLE
from app.utils import get_selected_car
from app.templates_config import templates

router = APIRouter(prefix="/maintenance")

CATEGORIES = [
    # Engine & Fluids
    "Oil Change", "Filters", "Coolant", "Brake Fluid", "Transmission Fluid",
    # Drivetrain & Brakes
    "Brakes", "Tires", "Wheels & Alignment", "Suspension", "Steering",
    "Transmission", "Clutch",
    # Electrical & Lighting
    "Battery", "Electrical", "Lights", "Starter / Alternator",
    # Body & Comfort
    "Body/Paint", "Windscreen", "Wipers", "Interior", "AC / Heating",
    # Wear Parts
    "Belts & Chains", "Exhaust",
    # Admin & Running Costs
    "Insurance", "Road Tax", "MOT / Pre-inspection", "Parking", "Tolls",
    # General
    "Car Wash", "Accessories", "General", "Other",
]


def _ctx(request: Request, cars=None, **kwargs):
    return {"request": request, "currency": CURRENCY, "app_title": APP_TITLE, "categories": CATEGORIES, "cars": cars or [], **kwargs}


def _guard(request: Request):
    if not auth_module.is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    return None


@router.get("")
async def maintenance_list(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    car, cars = get_selected_car(request, db)
    if not car:
        return RedirectResponse("/car/add", status_code=302)
    entries = crud.get_maintenance_entries(db, car.id)
    return templates.TemplateResponse("maintenance/list.html", _ctx(request, cars=cars, car=car, entries=entries))


@router.get("/add")
async def maintenance_add_form(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    car, cars = get_selected_car(request, db)
    if not car:
        return RedirectResponse("/car/add", status_code=302)
    fuel_entries = crud.get_fuel_entries(db, car.id)
    last_odometer = fuel_entries[0].odometer if fuel_entries else (car.purchase_mileage or 0)
    return templates.TemplateResponse("maintenance/add.html", _ctx(request, cars=cars, car=car, today=date.today(), last_odometer=last_odometer, entry=None))


@router.post("/add")
async def maintenance_add_submit(
    request: Request,
    date_field: date = Form(..., alias="date"),
    description: str = Form(...),
    category: str = Form("General"),
    cost: float = Form(...),
    odometer: Optional[float] = Form(None),
    shop: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if r := _guard(request):
        return r
    car, _ = get_selected_car(request, db)
    crud.create_maintenance_entry(db, MaintenanceEntryCreate(
        car_id=car.id,
        date=date_field,
        description=description,
        category=category,
        cost=cost,
        odometer=odometer,
        shop=shop or None,
        notes=notes or None,
    ))
    return RedirectResponse("/maintenance", status_code=302)


@router.get("/{entry_id}/edit")
async def maintenance_edit_form(entry_id: int, request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    entry = crud.get_maintenance_entry(db, entry_id)
    if not entry:
        return RedirectResponse("/maintenance", status_code=302)
    car, cars = get_selected_car(request, db)
    return templates.TemplateResponse("maintenance/add.html", _ctx(request, cars=cars, car=car, today=date.today(), entry=entry, last_odometer=entry.odometer or 0))


@router.post("/{entry_id}/edit")
async def maintenance_edit_submit(
    entry_id: int,
    request: Request,
    date_field: date = Form(..., alias="date"),
    description: str = Form(...),
    category: str = Form("General"),
    cost: float = Form(...),
    odometer: Optional[float] = Form(None),
    shop: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if r := _guard(request):
        return r
    crud.update_maintenance_entry(db, entry_id, {
        "date": date_field, "description": description, "category": category,
        "cost": cost, "odometer": odometer, "shop": shop or None, "notes": notes or None,
    })
    return RedirectResponse("/maintenance", status_code=302)


@router.post("/{entry_id}/delete")
async def maintenance_delete(entry_id: int, request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    crud.delete_maintenance_entry(db, entry_id)
    return RedirectResponse("/maintenance", status_code=302)
