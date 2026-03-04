from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator


class CarCreate(BaseModel):
    name: str
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    purchase_mileage: Optional[float] = 0
    current_market_value: Optional[float] = None
    notes: Optional[str] = None


class FuelEntryCreate(BaseModel):
    car_id: int
    date: date
    liters: float
    total_cost: float
    odometer: float
    full_tank: bool = True
    fuel_type: str = "Diesel"
    station: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("liters", "total_cost", "odometer")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Must be a positive number")
        return v


class MaintenanceEntryCreate(BaseModel):
    car_id: int
    date: date
    description: str
    category: str = "General"
    cost: float
    odometer: Optional[float] = None
    shop: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("cost")
    @classmethod
    def cost_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Cost cannot be negative")
        return v


class InspectionEntryCreate(BaseModel):
    car_id: int
    date: date
    cost: float
    valid_until: Optional[date] = None
    passed: bool = True
    notes: Optional[str] = None


class CarValuationCreate(BaseModel):
    car_id: int
    date: date
    value: float
    notes: Optional[str] = None
