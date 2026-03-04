"""
Shared Jinja2Templates instance with custom filters.
All routers import `templates` from here instead of creating their own.
"""
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _fmt_num(value, decimals=0):
    """Format a number with space as thousands separator.
    {{ 10000 | fmt_num }}      → "10 000"
    {{ 10000.5 | fmt_num(2) }} → "10 000.50"
    """
    if value is None:
        return "—"
    try:
        s = f"{float(value):,.{decimals}f}"
        return s.replace(",", "\u202f")  # narrow no-break space (ISO thousands sep)
    except (TypeError, ValueError):
        return str(value)


templates.env.filters["fmt_num"] = _fmt_num
