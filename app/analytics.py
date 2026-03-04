"""
All cost and efficiency calculations.
Every function takes a Car ORM object (with loaded relationships) and returns
plain dicts/lists suitable for passing directly to Jinja2 templates or JSON.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Car


def _safe_div(numerator: float, denominator: float, default=None):
    if denominator and denominator != 0:
        return numerator / denominator
    return default


# ── Per-tank stats ────────────────────────────────────────────────────────────

def compute_fuel_stats(fuel_entries) -> list[dict]:
    """
    Enrich fuel entries with per-tank km driven and consumption (L/100 km).
    Entries must be sorted oldest-first for correct calculation.
    """
    sorted_entries = sorted(fuel_entries, key=lambda e: (e.date, e.id))
    stats = []
    for i, entry in enumerate(sorted_entries):
        km_driven = None
        consumption = None
        if i > 0:
            prev = sorted_entries[i - 1]
            km_driven = entry.odometer - prev.odometer
            if km_driven > 0 and entry.full_tank and entry.liters:
                consumption = round((entry.liters / km_driven) * 100, 2)
            if km_driven <= 0:
                km_driven = None
        stats.append({
            "entry": entry,
            "km_driven": round(km_driven, 1) if km_driven is not None else None,
            "consumption_l100": consumption,
            "price_per_liter": entry.price_per_liter,
        })
    # Return newest-first for display
    return list(reversed(stats))


# ── Summary totals ────────────────────────────────────────────────────────────

def compute_summary(car: "Car") -> dict:
    fuel = car.fuel_entries
    maintenance = car.maintenance_entries
    inspections = car.inspection_entries

    total_fuel_cost = sum(e.total_cost for e in fuel)
    total_fuel_liters = sum(e.liters or 0 for e in fuel)
    total_maintenance_cost = sum(e.cost for e in maintenance)
    total_inspection_cost = sum(e.cost for e in inspections)
    total_cost = total_fuel_cost + total_maintenance_cost + total_inspection_cost

    # Mileage
    odometer_readings = [e.odometer for e in fuel if e.odometer]
    latest_odometer = max(odometer_readings) if odometer_readings else None
    earliest_odometer = min(odometer_readings) if odometer_readings else None
    start_km = car.purchase_mileage or earliest_odometer or 0
    total_km = (latest_odometer - start_km) if latest_odometer is not None else 0

    # Fuel efficiency (only from full-tank entries between consecutive fills)
    full_tank_stats = compute_fuel_stats(fuel)
    valid_consumptions = [s["consumption_l100"] for s in full_tank_stats if s["consumption_l100"] is not None]
    avg_consumption = round(sum(valid_consumptions) / len(valid_consumptions), 2) if valid_consumptions else None

    avg_price_per_liter = round(total_fuel_cost / total_fuel_liters, 4) if total_fuel_liters > 0 else None
    cost_per_km = round(total_cost / total_km, 4) if total_km > 0 else None
    fuel_cost_per_km = round(total_fuel_cost / total_km, 4) if total_km > 0 else None

    # Next inspection
    upcoming_inspection = None
    for insp in sorted(inspections, key=lambda i: i.valid_until or date.min, reverse=True):
        if insp.valid_until:
            upcoming_inspection = insp.valid_until
            break

    return {
        "total_cost": round(total_cost, 2),
        "total_fuel_cost": round(total_fuel_cost, 2),
        "total_fuel_liters": round(total_fuel_liters, 2),
        "total_maintenance_cost": round(total_maintenance_cost, 2),
        "total_inspection_cost": round(total_inspection_cost, 2),
        "total_km": round(total_km, 1),
        "latest_odometer": round(latest_odometer, 1) if latest_odometer else None,
        "avg_consumption_l100": avg_consumption,
        "avg_price_per_liter": avg_price_per_liter,
        "cost_per_km": cost_per_km,
        "fuel_cost_per_km": fuel_cost_per_km,
        "fuel_entry_count": len(fuel),
        "maintenance_entry_count": len(maintenance),
        "inspection_entry_count": len(inspections),
        "upcoming_inspection": upcoming_inspection,
        "days_until_inspection": (upcoming_inspection - date.today()).days if upcoming_inspection else None,
    }


# ── Monthly breakdown ─────────────────────────────────────────────────────────

_CAT_KEY = {"Service": "service", "Tyres": "tyres", "Insurance": "insurance", "Road Tax": "road_tax"}


def compute_monthly_costs(car: "Car") -> list[dict]:
    def _blank():
        return {"fuel": 0.0, "service": 0.0, "tyres": 0.0,
                "insurance": 0.0, "road_tax": 0.0, "inspection": 0.0, "other": 0.0}

    monthly: dict[str, dict] = defaultdict(_blank)

    for e in car.fuel_entries:
        monthly[e.date.strftime("%Y-%m")]["fuel"] += e.total_cost

    for e in car.maintenance_entries:
        key = _CAT_KEY.get(e.category or "", "other")
        monthly[e.date.strftime("%Y-%m")][key] += e.cost

    for e in car.inspection_entries:
        monthly[e.date.strftime("%Y-%m")]["inspection"] += e.cost

    result = []
    for month_key in sorted(monthly.keys()):
        row = monthly[month_key]
        total = sum(row.values())
        result.append({
            "month": month_key,
            "label": datetime.strptime(month_key, "%Y-%m").strftime("%b %Y"),
            "fuel": round(row["fuel"], 2),
            "service": round(row["service"], 2),
            "tyres": round(row["tyres"], 2),
            "insurance": round(row["insurance"], 2),
            "road_tax": round(row["road_tax"], 2),
            "inspection": round(row["inspection"], 2),
            "other": round(row["other"], 2),
            # keep aggregate for yearly table
            "maintenance": round(row["service"] + row["tyres"] + row["insurance"] + row["road_tax"] + row["other"], 2),
            "total": round(total, 2),
        })
    return result


# ── Yearly breakdown ──────────────────────────────────────────────────────────

def compute_yearly_costs(car: "Car") -> list[dict]:
    yearly: dict[str, dict] = defaultdict(lambda: {"fuel": 0.0, "maintenance": 0.0, "inspection": 0.0, "liters": 0.0})

    for e in car.fuel_entries:
        key = str(e.date.year)
        yearly[key]["fuel"] += e.total_cost
        yearly[key]["liters"] += e.liters or 0

    for e in car.maintenance_entries:
        key = str(e.date.year)
        yearly[key]["maintenance"] += e.cost

    for e in car.inspection_entries:
        key = str(e.date.year)
        yearly[key]["inspection"] += e.cost

    result = []
    for year in sorted(yearly.keys()):
        row = yearly[year]
        total = row["fuel"] + row["maintenance"] + row["inspection"]
        result.append({
            "year": year,
            "fuel": round(row["fuel"], 2),
            "maintenance": round(row["maintenance"], 2),
            "inspection": round(row["inspection"], 2),
            "liters": round(row["liters"], 2),
            "total": round(total, 2),
        })
    return result


# ── Fuel price history ────────────────────────────────────────────────────────

def compute_fuel_price_history(car: "Car") -> list[dict]:
    result = []
    for e in sorted(car.fuel_entries, key=lambda x: (x.date, x.id)):
        if e.price_per_liter:
            result.append({
                "date": e.date.isoformat(),
                "price_per_liter": e.price_per_liter,
                "fuel_type": e.fuel_type,
            })
    return result


# ── Depreciation estimate ─────────────────────────────────────────────────────

def compute_depreciation(car: "Car") -> dict | None:
    if not car.purchase_price or not car.purchase_date:
        return None

    today = date.today()
    years_owned = (today - car.purchase_date).days / 365.25

    valuations = sorted(car.valuations, key=lambda v: v.date) if car.valuations else []

    if valuations:
        # Use real recorded market values
        latest = valuations[-1]
        estimated_value = latest.value
        total_depreciation = car.purchase_price - estimated_value
        depreciation_per_year = total_depreciation / years_owned if years_owned > 0 else 0

        curve = [{"year": car.purchase_date.year, "value": car.purchase_price, "label": str(car.purchase_date.year)}]
        for v in valuations:
            curve.append({"year": v.date.year, "value": round(v.value, 2), "label": v.date.strftime("%b %Y")})
        using_real_data = True
    else:
        # Fallback: 15% annual declining-balance estimate
        ANNUAL_DEPRECIATION_RATE = 0.15
        estimated_value = car.purchase_price * ((1 - ANNUAL_DEPRECIATION_RATE) ** years_owned)
        total_depreciation = car.purchase_price - estimated_value
        depreciation_per_year = total_depreciation / years_owned if years_owned > 0 else 0

        curve = []
        for y in range(int(years_owned) + 2):
            val = car.purchase_price * ((1 - ANNUAL_DEPRECIATION_RATE) ** y)
            year_label = car.purchase_date.year + y
            curve.append({"year": year_label, "value": round(val, 2), "label": str(year_label)})
        using_real_data = False

    depreciation_per_km = _safe_div(total_depreciation, compute_summary(car)["total_km"])

    return {
        "purchase_price": car.purchase_price,
        "purchase_date": car.purchase_date.isoformat(),
        "years_owned": round(years_owned, 1),
        "estimated_value": round(estimated_value, 2),
        "total_depreciation": round(total_depreciation, 2),
        "depreciation_per_year": round(depreciation_per_year, 2),
        "depreciation_per_km": round(depreciation_per_km, 4) if depreciation_per_km else None,
        "current_market_value": car.current_market_value,
        "using_real_data": using_real_data,
        "curve": curve,
    }


# ── Maintenance breakdown by category ─────────────────────────────────────────

def compute_maintenance_by_category(car: "Car") -> list[dict]:
    """Returns maintenance cost grouped by category, sorted by total cost descending."""
    totals: dict[str, float] = defaultdict(float)
    for e in car.maintenance_entries:
        totals[e.category or "Other"] += e.cost
    return [
        {"category": cat, "total": round(total, 2)}
        for cat, total in sorted(totals.items(), key=lambda x: x[1], reverse=True)
    ]


# ── Unified log entries ───────────────────────────────────────────────────────

def get_all_entries(car: "Car") -> list[dict]:
    """
    Merge all entry types into a single list for the unified log view.
    Fuel entries are enriched with per-tank consumption data.
    Returns newest-first, with data-attributes dict for client-side filtering.
    """
    entries: list[dict] = []

    # Fuel — enrich with per-tank stats via compute_fuel_stats
    fuel_stats = compute_fuel_stats(car.fuel_entries)
    for s in fuel_stats:
        e = s["entry"]
        desc_parts = [e.fuel_type]
        if e.station:
            desc_parts.append(e.station)
        entries.append({
            "id": e.id,
            "type": "fuel",
            "date": e.date,
            "date_iso": e.date.isoformat(),
            "year": str(e.date.year),
            "description": " · ".join(desc_parts),
            "category": e.fuel_type,
            "cost": e.total_cost,
            "liters": e.liters,
            "price_per_liter": s["price_per_liter"],
            "consumption_l100": s["consumption_l100"],
            "km_driven": s["km_driven"],
            "odometer": e.odometer,
            "notes": e.notes or "",
            "edit_url": f"/fuel/{e.id}/edit",
            "delete_url": f"/fuel/{e.id}/delete",
        })

    # Maintenance
    for e in car.maintenance_entries:
        note_parts = []
        if e.shop:
            note_parts.append(e.shop)
        if e.notes:
            note_parts.append(e.notes)
        entries.append({
            "id": e.id,
            "type": "maintenance",
            "date": e.date,
            "date_iso": e.date.isoformat(),
            "year": str(e.date.year),
            "description": e.description,
            "category": e.category,
            "cost": e.cost,
            "liters": None,
            "price_per_liter": None,
            "consumption_l100": None,
            "km_driven": None,
            "odometer": e.odometer,
            "notes": " · ".join(note_parts),
            "edit_url": f"/maintenance/{e.id}/edit",
            "delete_url": f"/maintenance/{e.id}/delete",
        })

    # Inspection
    for e in car.inspection_entries:
        desc = "Annual Inspection"
        if not e.passed:
            desc += " (Failed)"
        if e.valid_until:
            desc += f" · valid until {e.valid_until.strftime('%d %b %Y')}"
        entries.append({
            "id": e.id,
            "type": "inspection",
            "date": e.date,
            "date_iso": e.date.isoformat(),
            "year": str(e.date.year),
            "description": desc,
            "category": "Inspection",
            "cost": e.cost,
            "liters": None,
            "price_per_liter": None,
            "consumption_l100": None,
            "km_driven": None,
            "odometer": None,
            "notes": e.notes or "",
            "edit_url": f"/inspection/{e.id}/edit",
            "delete_url": f"/inspection/{e.id}/delete",
        })

    entries.sort(key=lambda x: (x["date"], x["id"] if isinstance(x.get("id"), int) else 0), reverse=True)
    return entries
