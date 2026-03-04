from datetime import date
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)       # e.g. "My BMW"
    make = Column(String(50))                         # e.g. "BMW"
    model = Column(String(50))                        # e.g. "320d"
    year = Column(Integer)
    purchase_date = Column(Date)
    purchase_price = Column(Float)                    # EUR
    purchase_mileage = Column(Float, default=0)       # km at purchase
    current_market_value = Column(Float)              # optional, for depreciation
    notes = Column(Text)

    fuel_entries = relationship("FuelEntry", back_populates="car", cascade="all, delete-orphan", order_by="FuelEntry.date.desc()")
    maintenance_entries = relationship("MaintenanceEntry", back_populates="car", cascade="all, delete-orphan", order_by="MaintenanceEntry.date.desc()")
    inspection_entries = relationship("InspectionEntry", back_populates="car", cascade="all, delete-orphan", order_by="InspectionEntry.date.desc()")


class FuelEntry(Base):
    __tablename__ = "fuel_entries"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    liters = Column(Float)                            # liters filled (nullable: sometimes not recorded)
    total_cost = Column(Float, nullable=False)        # EUR total paid
    odometer = Column(Float, nullable=False)          # km reading at fill-up
    full_tank = Column(Boolean, default=True)         # was tank filled completely?
    fuel_type = Column(String(20), default="Diesel")  # Diesel / Petrol / LPG / E10 etc.
    station = Column(String(100))                     # gas station name
    notes = Column(Text)

    car = relationship("Car", back_populates="fuel_entries")

    @property
    def price_per_liter(self) -> float | None:
        if self.liters and self.liters > 0:
            return round(self.total_cost / self.liters, 4)
        return None


class MaintenanceEntry(Base):
    __tablename__ = "maintenance_entries"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    description = Column(String(200), nullable=False)  # e.g. "Oil change"
    category = Column(String(50), default="General")   # Oil / Tires / Brakes / Battery / etc.
    cost = Column(Float, nullable=False)               # EUR
    odometer = Column(Float)                           # km at service (optional)
    shop = Column(String(100))                         # service shop name
    notes = Column(Text)

    car = relationship("Car", back_populates="maintenance_entries")


class InspectionEntry(Base):
    __tablename__ = "inspection_entries"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    cost = Column(Float, nullable=False)               # EUR
    valid_until = Column(Date)                         # next inspection due date
    passed = Column(Boolean, default=True)
    notes = Column(Text)

    car = relationship("Car", back_populates="inspection_entries")
