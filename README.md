# Odyssey Tracker

A self-hosted web app to track and analyse all costs for your car — fuel, maintenance, inspections, insurance, and more.

Runs on your Ubuntu home server. No cloud. No subscription. Your data stays with you.

---

## Features

- **Fuel log** — fill-ups: liters, total cost, odometer, fuel type, gas station
- **Maintenance log** — services, repairs, oil changes, tires, insurance, road tax, parking, and more
- **Inspection log** — annual inspection dates, costs, validity, and expiry alerts
- **Unified log** — all entry types in one filterable, sortable view (filter by year and type)
- **Data import** — import existing data from CSV or Excel (Finnish format supported: DD.MM.YYYY dates, comma decimals)
- **Analytics** — cost per km, average consumption, fuel price history, monthly/yearly breakdown, depreciation estimate
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
│   ├── models.py          # ORM models: Car, FuelEntry, MaintenanceEntry, InspectionEntry
│   ├── schemas.py         # Pydantic input validation
│   ├── auth.py            # Session-based password auth
│   ├── crud.py            # Database CRUD operations
│   ├── analytics.py       # Cost and efficiency calculations + get_all_entries()
│   ├── routers/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── car.py
│   │   ├── fuel.py
│   │   ├── maintenance.py
│   │   ├── inspection.py
│   │   ├── analytics_router.py
│   │   ├── log_router.py       # Unified log (/log)
│   │   └── import_router.py    # CSV/Excel import (/import)
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── log.html            # Unified filterable log
│       ├── import.html         # Two-step import flow
│       ├── analytics.html
│       ├── car/setup.html
│       ├── fuel/add.html
│       ├── maintenance/add.html
│       └── inspection/add.html
├── data/                  # SQLite database + temp import files (auto-created)
├── .env                   # Your local config (not in git)
├── .env.example           # Config template
├── requirements.txt
├── setup.sh               # Setup / update / uninstall
├── run.sh                 # Start the app
├── odyssey-tracker.service    # Systemd service template
├── README.md
├── DEPLOYMENT.md
└── CLAUDE.md              # AI assistant context
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

## Maintenance Categories

The maintenance log supports these cost categories:

`Oil Change` · `Tires` · `Brakes` · `Battery` · `Filters` · `Wipers` · `Belts` · `Suspension` · `Exhaust` · `Electrical` · `Body/Paint` · `Insurance` · `Road Tax` · `Parking` · `Car Wash` · `General` · `Other`

## Data Import (CSV / Excel)

Go to **Import Data** in the sidebar. Supported column names (Finnish or English):

| Finnish | English | Maps to |
|---------|---------|---------|
| PVM | Date | Fill-up or entry date (DD.MM.YYYY) |
| Bensa | Fuel cost (€) | Fuel entry |
| Litrat | Liters | Fuel liters |
| Mittarilukema | Odometer (km) | Fuel odometer |
| Huolto | Maintenance cost (€) | Maintenance (General) |
| Katsastus | Inspection cost (€) | Inspection entry |
| Renkaat | Tires cost (€) | Maintenance (Tires) |
| Vakuutukset | Insurance cost (€) | Maintenance (Insurance) |
| Muu | Other cost (€) | Maintenance (Other) |
| Huom! | Notes | Notes on all entries from that row |

One row can produce multiple entries (e.g. fuel + insurance on the same date).
Finnish number format (comma as decimal) and dates (DD.MM.YYYY) are auto-detected.
Duplicate fuel entries (same odometer) are skipped automatically.

## Data Model

```
Car
 ├── FuelEntry     (date, liters, total_cost, odometer, fuel_type, station)
 ├── MaintenanceEntry  (date, description, category, cost, odometer, shop)
 └── InspectionEntry   (date, cost, valid_until, passed)
```

All data is stored in `data/car_tracker.db` — a single SQLite file you can back up by copying it.

## setup.sh modes

```bash
./setup.sh              # First-time setup
./setup.sh --update     # Update Python dependencies (keeps .env and data)
./setup.sh --uninstall  # Remove venv/data/.env (interactive prompts)
```

## Version 2.0 Ideas

- Receipt photo scanning (OCR to auto-fill fuel entries)
- Multiple car support
- CSV export
- Mobile-optimized PWA

## License

MIT — personal use, modify freely.
