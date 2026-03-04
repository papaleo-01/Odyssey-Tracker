from fastapi import Request
from fastapi.responses import RedirectResponse
from app.config import APP_PASSWORD


def is_authenticated(request: Request) -> bool:
    return request.session.get("authenticated") is True


def require_auth(request: Request):
    """Use as a dependency or call directly; raises redirect if not authenticated."""
    if not is_authenticated(request):
        return False
    return True


def login(request: Request, password: str) -> bool:
    if password == APP_PASSWORD:
        request.session["authenticated"] = True
        return True
    return False


def logout(request: Request):
    request.session.clear()
