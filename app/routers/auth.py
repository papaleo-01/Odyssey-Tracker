from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import app.auth as auth_module

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/login")
async def login_page(request: Request, error: str = ""):
    if auth_module.is_authenticated(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": error})


@router.post("/login")
async def login_submit(request: Request, password: str = Form(...)):
    if auth_module.login(request, password):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Wrong password. Try again."})


@router.get("/logout")
async def logout(request: Request):
    auth_module.logout(request)
    return RedirectResponse("/login", status_code=302)
