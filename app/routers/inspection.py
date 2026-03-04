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
from app.schemas import InspectionEntryCreate
from app.config import CURRENCY, APP_TITLE

router = APIRouter(prefix="/inspection")
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


def _ctx(request: Request, **kwargs):
    return {"request": request, "currency": CURRENCY, "app_title": APP_TITLE, **kwargs}


def _guard(request: Request):
    if not auth_module.is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    return None


@router.get("")
async def inspection_list(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    cars = crud.get_cars(db)
    if not cars:
        return RedirectResponse("/car/setup", status_code=302)
    car = cars[0]
    entries = crud.get_inspection_entries(db, car.id)
    today = date.today()
    return templates.TemplateResponse("inspection/list.html", _ctx(request, car=car, entries=entries, today=today))


@router.get("/add")
async def inspection_add_form(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    cars = crud.get_cars(db)
    if not cars:
        return RedirectResponse("/car/setup", status_code=302)
    return templates.TemplateResponse("inspection/add.html", _ctx(request, car=cars[0], today=date.today(), entry=None))


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
    cars = crud.get_cars(db)
    car = cars[0]
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
    cars = crud.get_cars(db)
    return templates.TemplateResponse("inspection/add.html", _ctx(request, car=cars[0], today=date.today(), entry=entry))


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
    return RedirectResponse("/inspection", status_code=302)


@router.post("/{entry_id}/delete")
async def inspection_delete(entry_id: int, request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    crud.delete_inspection_entry(db, entry_id)
    return RedirectResponse("/inspection", status_code=302)
