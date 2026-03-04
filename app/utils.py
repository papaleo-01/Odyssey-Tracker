from fastapi import Request
from sqlalchemy.orm import Session

import app.crud as crud


def get_selected_car(request: Request, db: Session):
    """Return (selected_car, all_cars). Falls back to first car if session has no valid car_id."""
    cars = crud.get_cars(db)
    if not cars:
        return None, []
    car_id = request.session.get("car_id")
    car = next((c for c in cars if c.id == car_id), cars[0])
    request.session["car_id"] = car.id
    return car, cars
