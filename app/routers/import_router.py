"""
CSV / XLSX import router.

Flow:
  GET  /import            → upload form
  POST /import            → parse file → save temp JSON → preview page
  POST /import/confirm    → load temp → insert DB → redirect /log
"""
import csv
import io
import json
import re
import uuid
from datetime import datetime, date
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Request, File, UploadFile, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import app.crud as crud
import app.auth as auth_module
from app.database import get_db
from app.config import BASE_DIR, CURRENCY, APP_TITLE
from app.schemas import FuelEntryCreate, MaintenanceEntryCreate, InspectionEntryCreate

router = APIRouter(prefix="/import")
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
TEMP_DIR = BASE_DIR / "data" / "temp"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_fi_number(s: str) -> Optional[float]:
    """Parse Finnish/European number: '1.234,56 €' → 1234.56"""
    if not s:
        return None
    s = re.sub(r"[€$\s\xa0]", "", s.strip())  # strip currency/whitespace
    if not s or s in ("-", "—"):
        return None
    # European: 1.234,56  →  remove thousands dot, swap decimal comma
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        v = float(s)
        return v if v != 0 else None
    except ValueError:
        return None


def _parse_date(s: str) -> Optional[date]:
    for fmt in ["%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]:
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    return None


# Column aliases: Finnish → internal key
_COL_MAP = {
    "pvm": "date", "päivämäärä": "date", "date": "date",
    "bensa": "fuel_cost", "polttoaine": "fuel_cost", "fuel": "fuel_cost", "fuel cost": "fuel_cost",
    "litrat": "liters", "liter": "liters", "liters": "liters",
    "mittarilukema": "odometer", "mileage": "odometer", "odometer": "odometer", "km": "odometer",
    "ajettu km": "km_driven", "km driven": "km_driven",
    "huolto": "maintenance", "maintenance": "maintenance",
    "katsastus": "inspection", "inspection": "inspection",
    "muu": "other", "other": "other", "muut": "other",
    "renkaat": "tires", "tires": "tires", "tyres": "tires",
    "vakuutukset": "insurance", "insurance": "insurance", "vakuutus": "insurance",
    "huom": "notes", "huom!": "notes", "notes": "notes", "remarks": "notes",
    "vuosi": None,  # skip year column
}


def _normalize_header(h) -> Optional[str]:
    if h is None:
        return None
    key = str(h).strip().lower()
    if not key:
        return None
    return _COL_MAP.get(key, key)


def _parse_csv_bytes(content: bytes) -> list[dict]:
    # Detect BOM
    if content.startswith(b"\xef\xbb\xbf"):
        content = content[3:]
    text = content.decode("utf-8", errors="replace")

    # Detect separator by counting in first line
    first_line = text.split("\n")[0]
    sep = ";" if first_line.count(";") >= first_line.count(",") else ","

    reader = csv.DictReader(io.StringIO(text), delimiter=sep)
    rows = []
    for row in reader:
        norm = {_normalize_header(k): v for k, v in row.items() if _normalize_header(k) is not None}
        rows.append(norm)
    return rows


def _parse_xlsx_bytes(content: bytes) -> list[dict]:
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
    ws = wb.active

    rows_iter = ws.iter_rows(values_only=True)
    headers = None
    rows = []
    for raw_row in rows_iter:
        if headers is None:
            # Find the header row (first non-empty row with date-like column)
            str_cells = [str(c).strip() if c is not None else "" for c in raw_row]
            if any(s.lower() in _COL_MAP for s in str_cells):
                headers = [_normalize_header(s) for s in str_cells]
            continue
        if headers:
            norm = {}
            for key, val in zip(headers, raw_row):
                if key is None:
                    continue
                norm[key] = str(val) if val is not None else ""
            rows.append(norm)
    return rows


def _rows_to_entries(rows: list[dict]) -> list[dict]:
    """
    Convert parsed rows to a list of entry dicts ready for preview / DB insert.
    One row can produce multiple entries (e.g., fuel + insurance on same day).
    """
    entries = []
    for row in rows:
        raw_date = row.get("date", "")
        d = _parse_date(str(raw_date)) if raw_date else None
        if not d:
            continue  # skip rows without a valid date

        notes = str(row.get("notes", "") or "").strip()

        fuel_cost = _parse_fi_number(str(row.get("fuel_cost", "") or ""))
        liters = _parse_fi_number(str(row.get("liters", "") or ""))
        odometer = _parse_fi_number(str(row.get("odometer", "") or ""))

        # Fuel entry: need liters + odometer (cost can be 0 if missing)
        if liters and liters > 0 and odometer and odometer > 0:
            entries.append({
                "entry_type": "fuel",
                "date": d.isoformat(),
                "fuel_cost": round(fuel_cost, 2) if fuel_cost else 0.0,
                "liters": round(liters, 3),
                "odometer": round(odometer, 1),
                "notes": notes,
            })

        # Maintenance / service
        maint_cost = _parse_fi_number(str(row.get("maintenance", "") or ""))
        if maint_cost and maint_cost > 0:
            entries.append({
                "entry_type": "maintenance",
                "date": d.isoformat(),
                "description": notes or "Maintenance",
                "category": "General",
                "cost": round(maint_cost, 2),
                "notes": notes,
            })

        # Tires
        tires_cost = _parse_fi_number(str(row.get("tires", "") or ""))
        if tires_cost and tires_cost > 0:
            entries.append({
                "entry_type": "maintenance",
                "date": d.isoformat(),
                "description": notes or "Tires",
                "category": "Tires",
                "cost": round(tires_cost, 2),
                "notes": notes,
            })

        # Insurance
        ins_cost = _parse_fi_number(str(row.get("insurance", "") or ""))
        if ins_cost and ins_cost > 0:
            entries.append({
                "entry_type": "maintenance",
                "date": d.isoformat(),
                "description": notes or "Insurance",
                "category": "Insurance",
                "cost": round(ins_cost, 2),
                "notes": notes,
            })

        # Other
        other_cost = _parse_fi_number(str(row.get("other", "") or ""))
        if other_cost and other_cost > 0:
            entries.append({
                "entry_type": "maintenance",
                "date": d.isoformat(),
                "description": notes or "Other",
                "category": "Other",
                "cost": round(other_cost, 2),
                "notes": notes,
            })

        # Inspection
        insp_cost = _parse_fi_number(str(row.get("inspection", "") or ""))
        if insp_cost and insp_cost > 0:
            entries.append({
                "entry_type": "inspection",
                "date": d.isoformat(),
                "cost": round(insp_cost, 2),
                "notes": notes,
            })

    return entries


def _count_types(entries: list[dict]) -> dict:
    counts = {"fuel": 0, "maintenance": 0, "inspection": 0}
    for e in entries:
        counts[e["entry_type"]] = counts.get(e["entry_type"], 0) + 1
    return counts


# ── Routes ────────────────────────────────────────────────────────────────────

def _guard(request: Request):
    if not auth_module.is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    return None


def _ctx(request: Request, **kwargs):
    return {"request": request, "currency": CURRENCY, "app_title": APP_TITLE, **kwargs}


@router.get("")
async def import_form(request: Request):
    if r := _guard(request):
        return r
    return templates.TemplateResponse("import.html", _ctx(request, step="upload"))


@router.post("")
async def import_upload(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if r := _guard(request):
        return r

    content = await file.read()
    filename = file.filename or ""

    try:
        if filename.lower().endswith(".xlsx"):
            rows = _parse_xlsx_bytes(content)
        else:
            rows = _parse_csv_bytes(content)

        entries = _rows_to_entries(rows)
    except Exception as exc:
        return templates.TemplateResponse("import.html", _ctx(
            request, step="upload",
            error=f"Could not parse file: {exc}. Make sure it's a valid CSV or Excel file."
        ))

    if not entries:
        return templates.TemplateResponse("import.html", _ctx(
            request, step="upload",
            error="No valid entries found. Check that your file has the expected columns (PVM, Bensa, Litrat, Mittarilukema…)."
        ))

    # Duplicate check (skip fuel entries with same odometer already in DB)
    cars = crud.get_cars(db)
    car = cars[0] if cars else None
    if car:
        existing_odometers = {e.odometer for e in crud.get_fuel_entries(db, car.id)}
        entries = [
            e for e in entries
            if not (e["entry_type"] == "fuel" and e.get("odometer") in existing_odometers)
        ]

    if not entries:
        return templates.TemplateResponse("import.html", _ctx(
            request, step="upload",
            error="All entries already exist in the database (duplicate odometer readings detected)."
        ))

    # Save to temp file
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    temp_id = str(uuid.uuid4())
    (TEMP_DIR / f"{temp_id}.json").write_text(json.dumps(entries))

    return templates.TemplateResponse("import.html", _ctx(
        request,
        step="preview",
        entries=entries,
        counts=_count_types(entries),
        temp_id=temp_id,
        filename=filename,
    ))


@router.post("/confirm")
async def import_confirm(
    request: Request,
    temp_id: str = Form(...),
    db: Session = Depends(get_db),
):
    if r := _guard(request):
        return r

    temp_file = TEMP_DIR / f"{temp_id}.json"
    if not temp_file.exists():
        request.session["flash"] = "error:Import session expired. Please upload again."
        return RedirectResponse("/import", status_code=302)

    entries = json.loads(temp_file.read_text())
    temp_file.unlink(missing_ok=True)

    cars = crud.get_cars(db)
    if not cars:
        return RedirectResponse("/car/setup", status_code=302)
    car = cars[0]

    inserted = {"fuel": 0, "maintenance": 0, "inspection": 0}
    for e in entries:
        d = date.fromisoformat(e["date"])
        if e["entry_type"] == "fuel":
            crud.create_fuel_entry(db, FuelEntryCreate(
                car_id=car.id,
                date=d,
                liters=e["liters"],
                total_cost=max(e["fuel_cost"], 0.01),  # schema requires >0
                odometer=e["odometer"],
                fuel_type="Diesel",
                notes=e.get("notes") or None,
            ))
            inserted["fuel"] += 1
        elif e["entry_type"] == "maintenance":
            crud.create_maintenance_entry(db, MaintenanceEntryCreate(
                car_id=car.id,
                date=d,
                description=e["description"],
                category=e["category"],
                cost=e["cost"],
                notes=e.get("notes") or None,
            ))
            inserted["maintenance"] += 1
        elif e["entry_type"] == "inspection":
            crud.create_inspection_entry(db, InspectionEntryCreate(
                car_id=car.id,
                date=d,
                cost=e["cost"],
                notes=e.get("notes") or None,
            ))
            inserted["inspection"] += 1

    total = sum(inserted.values())
    request.session["flash"] = (
        f"success:Imported {total} entries "
        f"({inserted['fuel']} fuel, {inserted['maintenance']} maintenance, {inserted['inspection']} inspection)."
    )
    return RedirectResponse("/log", status_code=302)
