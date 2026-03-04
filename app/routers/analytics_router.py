import json
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

router = APIRouter(prefix="/analytics")
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("")
async def analytics_page(request: Request, db: Session = Depends(get_db)):
    if not auth_module.is_authenticated(request):
        return RedirectResponse("/login", status_code=302)

    car, cars = get_selected_car(request, db)
    if not car:
        return RedirectResponse("/car/add", status_code=302)

    summary = analytics.compute_summary(car)
    monthly = analytics.compute_monthly_costs(car)
    yearly = analytics.compute_yearly_costs(car)
    fuel_price_history = analytics.compute_fuel_price_history(car)
    depreciation = analytics.compute_depreciation(car)
    fuel_stats = analytics.compute_fuel_stats(car.fuel_entries)

    consumption_history = [
        {"date": s["entry"].date.isoformat(), "consumption": s["consumption_l100"]}
        for s in reversed(fuel_stats)
        if s["consumption_l100"] is not None
    ]

    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "car": car,
        "cars": cars,
        "summary": summary,
        "monthly": monthly,
        "yearly": yearly,
        "fuel_price_history_json": json.dumps(fuel_price_history),
        "consumption_history_json": json.dumps(consumption_history),
        "monthly_json": json.dumps(monthly),
        "depreciation": depreciation,
        "depreciation_json": json.dumps(depreciation["curve"] if depreciation else []),
        "currency": CURRENCY,
        "app_title": APP_TITLE,
    })
