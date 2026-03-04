# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.1.1] — 2026-03-04

### Fixed
- **422 error on Car Setup / Add Car** — `purchase_mileage` was a required `float` field; an empty browser input caused a parse failure. It is now optional and defaults to `0`.
- **Import Data button in Log** — the empty-state card still linked to the removed `/import` route. Replaced with + Service and + Inspection buttons.

### Changed
- **Car switcher** — the sidebar vehicle selector is now a visibly styled dropdown with a chevron arrow and "Switch vehicle" label, making it discoverable for users with multiple cars.
- **Number formatting** — all large prices, costs, and odometer readings now use a narrow-no-break-space thousands separator (`10 000` instead of `10000`). Applies to Dashboard, Analytics, Log live stats, and Car Setup valuation table.
- **Maintenance categories** expanded from 17 to 31 entries, grouped into Engine & Fluids, Drivetrain, Electrical, Body & Comfort, Wear Parts, and Admin & Running Costs. New additions include Coolant, Brake Fluid, Transmission Fluid, Wheels & Alignment, Steering, Transmission, Clutch, Lights, Starter/Alternator, Windscreen, Interior, AC/Heating, Belts & Chains, MOT/Pre-inspection, Tolls, Accessories.
- All routers now share a single `Jinja2Templates` instance (via `app/templates_config.py`) so custom filters are available everywhere.

---

## [1.1.0] — 2026-03-04

### Added
- **Multiple car support** — track as many vehicles as you want. A dropdown in the sidebar lets you switch between cars instantly. Each car has fully isolated fuel, maintenance, inspection, and valuation data.
- **Add Car / Delete Car** — new sidebar link to add a car; delete button on Car Setup when more than one car exists.
- **Car value history** — record the car's market value at specific dates from the Car Setup page. The Analytics depreciation chart uses real data points when available.
- **Database backup** — download the SQLite database file from the new Settings page (`/settings`).
- **Database restore** — upload a previously downloaded `.db` backup to restore all data.
- **Settings page** — new sidebar entry consolidating backup, restore, and future app-level settings.

### Changed
- All routers now use the session-selected car instead of always defaulting to the first car.
- `compute_depreciation()` in `analytics.py` uses recorded valuations if present; falls back to the 15% annual declining-balance estimate when no valuations exist.
- Car Setup (`/car/setup`) now always edits the currently selected car; creating a new car goes to `/car/add`.
- Sidebar bottom section reorganised: Add Car, Car Setup, Settings, Logout.

### Removed
- **Import feature** (`/import`) removed — CSV/Excel import router and template deleted.

---

## [1.0.0] — 2026-03-03

### Added
- Initial release.
- Fuel, maintenance, and inspection logs with full CRUD.
- Unified log view with year and type filtering.
- Analytics: cost per km, fuel price history, monthly/yearly breakdown, depreciation estimate.
- Dashboard with summary stats and recent entries.
- Session-based password authentication.
- Inspection expiry alerts on dashboard.
- Database backup/restore via Settings.
- CSV/Excel import (removed in 1.1.0).
- Systemd service template for Ubuntu deployment.
- Dark theme UI (Tailwind CSS + Chart.js).
