# Odyssey Tracker

A self-hosted web app to track and analyse all costs for your car — fuel, maintenance, inspections, insurance, and more.

Runs on your Ubuntu home server. No cloud. No subscription. Your data stays with you.

---

## Features

- **Multiple cars** — track as many vehicles as you want; switch between them from the sidebar dropdown
- **Fuel log** — fill-ups: liters, total cost, odometer, fuel type, gas station
- **Maintenance log** — services, repairs, oil changes, tires, insurance, road tax, parking, and more
- **Inspection log** — annual inspection dates, costs, validity, and expiry alerts
- **Unified log** — all entry types in one filterable, sortable view (filter by year and type)
- **Analytics** — cost per km, average consumption, fuel price history, monthly/yearly breakdown, depreciation curve
- **Depreciation tracking** — record market valuations over time for a real depreciation curve; falls back to a 15% annual estimate if no valuations are recorded
- **Database backup/restore** — download the SQLite file from Settings; restore from a backup with one click
- **Dashboard** — quick overview with key stats and recent entries
- **Password protection** — simple session-based login
- **Inspection alerts** — warned on dashboard when inspection is due or overdue
- **Dark theme** — modern dark UI

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + SQLAlchemy |
| Database | SQLite (single file) |
| Templates | Jinja2 |
| Styling | Tailwind CSS (CDN Play) |
| Charts | Chart.js (CDN) |
| Runtime | Python 3.10+ in venv |

No Node.js. No npm. No Docker required. Just Python.

## Quick Start

```bash
# 1. Setup (run once)
chmod +x setup.sh run.sh
./setup.sh

# 2. Set your password
nano .env   # change APP_PASSWORD=changeme

# 3. Start
./run.sh
```

Open `http://localhost:8000` in your browser.

For full Ubuntu server deployment, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Project Structure

```
odyssey-tracker/
├── app/
│   ├── main.py            # FastAPI app, startup, router registration
│   ├── config.py          # Settings from .env
│   ├── database.py        # SQLAlchemy engine & session
│   ├── models.py          # ORM models: Car, FuelEntry, MaintenanceEntry, InspectionEntry, CarValuation
│   ├── schemas.py         # Pydantic input validation
│   ├── auth.py            # Session-based password auth
│   ├── crud.py            # Database CRUD operations
│   ├── utils.py           # Shared helpers (car selection)
│   ├── analytics.py       # Cost and efficiency calculations
│   ├── routers/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── car.py         # Car CRUD + switch + valuations
│   │   ├── fuel.py
│   │   ├── maintenance.py
│   │   ├── inspection.py
│   │   ├── analytics_router.py
│   │   ├── log_router.py       # Unified log (/log)
│   │   └── settings_router.py  # Backup / restore (/settings)
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── log.html
│       ├── analytics.html
│       ├── settings.html
│       ├── car/setup.html
│       ├── fuel/add.html
│       ├── maintenance/add.html
│       └── inspection/add.html
├── data/                  # SQLite database (auto-created, gitignored)
├── .env                   # Your local config (not in git)
├── .env.example           # Config template
├── requirements.txt
├── setup.sh               # Setup / update / uninstall
├── run.sh                 # Start the app
├── odyssey-tracker.service    # Systemd service template
├── README.md
├── CHANGELOG.md
└── DEPLOYMENT.md
```

## Configuration (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_PASSWORD` | `changeme` | Login password — **change this!** |
| `SECRET_KEY` | auto-generated | Session signing key |
| `PORT` | `8000` | Port to run on |
| `HOST` | `0.0.0.0` | Bind address (`0.0.0.0` = LAN accessible) |
| `CURRENCY` | `€` | Currency symbol shown in the UI |
| `APP_TITLE` | `Odyssey Tracker` | Title shown in browser/sidebar |

## Data Model

```
Car
 ├── FuelEntry        (date, liters, total_cost, odometer, fuel_type, station)
 ├── MaintenanceEntry (date, description, category, cost, odometer, shop)
 ├── InspectionEntry  (date, cost, valid_until, passed)
 └── CarValuation     (date, value) — optional market value history for real depreciation
```

All data is stored in `data/car_tracker.db` — a single SQLite file. Back it up from **Settings → Download Backup**.

## setup.sh modes

```bash
./setup.sh              # First-time setup
./setup.sh --update     # Update Python dependencies (keeps .env and data)
./setup.sh --uninstall  # Remove venv/data/.env (interactive prompts)
```

## Roadmap

- Receipt photo scanning (OCR to auto-fill fuel entries)
- CSV export
- Mobile-optimized PWA

## License

MIT — personal use, modify freely.
