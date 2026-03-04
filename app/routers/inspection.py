from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

import app.crud as crud
import app.auth as auth_module
from app.database import get_db
from app.schemas import InspectionEntryCreate
from app.config import CURRENCY, APP_TITLE
from app.utils import get_selected_car
from app.templates_config import templates

router = APIRouter(prefix="/inspection")


def _ctx(request: Request, cars=None, **kwargs):
    return {"request": request, "currency": CURRENCY, "app_title": APP_TITLE, "cars": cars or [], **kwargs}


def _guard(request: Request):
    if not auth_module.is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    return None


@router.get("")
async def inspection_list(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    car, cars = get_selected_car(request, db)
    if not car:
        return RedirectResponse("/car/add", status_code=302)
    entries = crud.get_inspection_entries(db, car.id)
    today = date.today()
    return templates.TemplateResponse("inspection/list.html", _ctx(request, cars=cars, car=car, entries=entries, today=today))


@router.get("/add")
async def inspection_add_form(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    car, cars = get_selected_car(request, db)
    if not car:
        return RedirectResponse("/car/add", status_code=302)
    return templates.TemplateResponse("inspection/add.html", _ctx(request, cars=cars, car=car, today=date.today(), entry=None))


@router.post("/add")
async def inspection_add_submit(
    request: Request,
    date_field: date = Form(..., alias="date"),
    cost: float = Form(...),
    valid_until: Optional[date] = Form(None),
    passed: bool = Form(True),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if r := _guard(request):
        return r
    car, _ = get_selected_car(request, db)
    crud.create_inspection_entry(db, InspectionEntryCreate(
        car_id=car.id,
        date=date_field,
        cost=cost,
        valid_until=valid_until,
        passed=passed,
        notes=notes or None,
    ))
    return RedirectResponse("/inspection", status_code=302)


@router.get("/{entry_id}/edit")
async def inspection_edit_form(entry_id: int, request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    entry = crud.get_inspection_entry(db, entry_id)
    if not entry:
        return RedirectResponse("/inspection", status_code=302)
    car, cars = get_selected_car(request, db)
    return templates.TemplateResponse("inspection/add.html", _ctx(request, cars=cars, car=car, today=date.today(), entry=entry))


@router.post("/{entry_id}/edit")
async def inspection_edit_submit(
    entry_id: int,
    request: Request,
    date_field: date = Form(..., alias="date"),
    cost: float = Form(...),
    valid_until: Optional[date] = Form(None),
    passed: bool = Form(True),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if r := _guard(request):
        return r
    crud.update_inspection_entry(db, entry_id, {
        "date": date_field, "cost": cost, "valid_until": valid_until,
        "passed": passed, "notes": notes or None,
    })
    return RedirectResponse("/log", status_code=302)


@router.post("/{entry_id}/delete")
async def inspection_delete(entry_id: int, request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    crud.delete_inspection_entry(db, entry_id)
    return RedirectResponse("/inspection", status_code=302)
