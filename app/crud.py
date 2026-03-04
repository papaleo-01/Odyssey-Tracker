from sqlalchemy.orm import Session
from sqlalchemy import desc
from app import models
from app.schemas import CarCreate, FuelEntryCreate, MaintenanceEntryCreate, InspectionEntryCreate


# ── Car ──────────────────────────────────────────────────────────────────────

def get_cars(db: Session) -> list[models.Car]:
    return db.query(models.Car).order_by(models.Car.id).all()


def get_car(db: Session, car_id: int) -> models.Car | None:
    return db.query(models.Car).filter(models.Car.id == car_id).first()


def create_car(db: Session, data: CarCreate) -> models.Car:
    car = models.Car(**data.model_dump())
    db.add(car)
    db.commit()
    db.refresh(car)
    return car


def update_car(db: Session, car_id: int, data: dict) -> models.Car | None:
    car = get_car(db, car_id)
    if not car:
        return None
    for key, value in data.items():
        setattr(car, key, value)
    db.commit()
    db.refresh(car)
    return car


# ── Fuel ─────────────────────────────────────────────────────────────────────

def get_fuel_entries(db: Session, car_id: int) -> list[models.FuelEntry]:
    return (
        db.query(models.FuelEntry)
        .filter(models.FuelEntry.car_id == car_id)
        .order_by(desc(models.FuelEntry.date), desc(models.FuelEntry.id))
        .all()
    )


def get_fuel_entry(db: Session, entry_id: int) -> models.FuelEntry | None:
    return db.query(models.FuelEntry).filter(models.FuelEntry.id == entry_id).first()


def create_fuel_entry(db: Session, data: FuelEntryCreate) -> models.FuelEntry:
    entry = models.FuelEntry(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_fuel_entry(db: Session, entry_id: int, data: dict) -> models.FuelEntry | None:
    entry = get_fuel_entry(db, entry_id)
    if not entry:
        return None
    for key, value in data.items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


def delete_fuel_entry(db: Session, entry_id: int) -> bool:
    entry = get_fuel_entry(db, entry_id)
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True


# ── Maintenance ───────────────────────────────────────────────────────────────

def get_maintenance_entries(db: Session, car_id: int) -> list[models.MaintenanceEntry]:
    return (
        db.query(models.MaintenanceEntry)
        .filter(models.MaintenanceEntry.car_id == car_id)
        .order_by(desc(models.MaintenanceEntry.date), desc(models.MaintenanceEntry.id))
        .all()
    )


def get_maintenance_entry(db: Session, entry_id: int) -> models.MaintenanceEntry | None:
    return db.query(models.MaintenanceEntry).filter(models.MaintenanceEntry.id == entry_id).first()


def create_maintenance_entry(db: Session, data: MaintenanceEntryCreate) -> models.MaintenanceEntry:
    entry = models.MaintenanceEntry(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_maintenance_entry(db: Session, entry_id: int, data: dict) -> models.MaintenanceEntry | None:
    entry = get_maintenance_entry(db, entry_id)
    if not entry:
        return None
    for key, value in data.items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


def delete_maintenance_entry(db: Session, entry_id: int) -> bool:
    entry = get_maintenance_entry(db, entry_id)
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True


# ── Inspection ────────────────────────────────────────────────────────────────

def get_inspection_entries(db: Session, car_id: int) -> list[models.InspectionEntry]:
    return (
        db.query(models.InspectionEntry)
        .filter(models.InspectionEntry.car_id == car_id)
        .order_by(desc(models.InspectionEntry.date), desc(models.InspectionEntry.id))
        .all()
    )


def get_inspection_entry(db: Session, entry_id: int) -> models.InspectionEntry | None:
    return db.query(models.InspectionEntry).filter(models.InspectionEntry.id == entry_id).first()


def create_inspection_entry(db: Session, data: InspectionEntryCreate) -> models.InspectionEntry:
    entry = models.InspectionEntry(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_inspection_entry(db: Session, entry_id: int, data: dict) -> models.InspectionEntry | None:
    entry = get_inspection_entry(db, entry_id)
    if not entry:
        return None
    for key, value in data.items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


def delete_inspection_entry(db: Session, entry_id: int) -> bool:
    entry = get_inspection_entry(db, entry_id)
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True
