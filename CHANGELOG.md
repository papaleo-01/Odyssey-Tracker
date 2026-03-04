# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
