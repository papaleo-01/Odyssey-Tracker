from datetime import date
from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

import app.auth as auth_module
from app.database import get_db
from app.config import CURRENCY, APP_TITLE, DB_PATH
from app.utils import get_selected_car

router = APIRouter(prefix="/settings")
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


def _guard(request: Request):
    if not auth_module.is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    return None


@router.get("")
async def settings_page(request: Request, db: Session = Depends(get_db)):
    if r := _guard(request):
        return r
    car, cars = get_selected_car(request, db)
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "car": car,
        "cars": cars,
        "currency": CURRENCY,
        "app_title": APP_TITLE,
    })


@router.get("/backup")
async def backup_db(request: Request):
    if r := _guard(request):
        return r
    filename = f"odyssey-backup-{date.today().isoformat()}.db"
    return FileResponse(
        path=str(DB_PATH),
        filename=filename,
        media_type="application/octet-stream",
    )


@router.post("/restore")
async def restore_db(request: Request, file: UploadFile = File(...)):
    if r := _guard(request):
        return r
    content = await file.read()
    if not content.startswith(b"SQLite format 3\x00"):
        request.session["flash"] = "error:Invalid file — not a valid SQLite database."
        return RedirectResponse("/settings", status_code=302)
    tmp = DB_PATH.with_suffix(".restore_tmp")
    tmp.write_bytes(content)
    tmp.replace(DB_PATH)
    request.session["flash"] = "success:Database restored. Refresh to see your data."
    return RedirectResponse("/settings", status_code=302)
