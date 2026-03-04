from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
import app.auth as auth_module
from app.templates_config import templates

router = APIRouter()


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
