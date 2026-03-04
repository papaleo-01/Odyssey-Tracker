from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import app.auth as auth_module
import app.analytics as analytics
from app.database import get_db
from app.config import CURRENCY, APP_TITLE
from app.utils import get_selected_car
from app.templates_config import templates

router = APIRouter()


@router.get("/")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    if not auth_module.is_authenticated(request):
        return RedirectResponse("/login", status_code=302)

    car, cars = get_selected_car(request, db)
    if not car:
        return RedirectResponse("/car/add", status_code=302)

    summary = analytics.compute_summary(car)
    recent_fuel = car.fuel_entries[:5]
    recent_maintenance = car.maintenance_entries[:3]
    recent_inspections = car.inspection_entries[:2]
    monthly = analytics.compute_monthly_costs(car)[-12:]

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "car": car,
        "cars": cars,
        "summary": summary,
        "recent_fuel": recent_fuel,
        "recent_maintenance": recent_maintenance,
        "recent_inspections": recent_inspections,
        "monthly": monthly,
        "currency": CURRENCY,
        "app_title": APP_TITLE,
    })
