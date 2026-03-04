# Deployment Guide

Step-by-step guide to deploy Odyssey Tracker on your Ubuntu home server.

---

## Prerequisites

- Ubuntu 20.04 or newer
- Python 3.10+ (`python3 --version`)
- Git (optional, for cloning)

Install Python if needed:
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
```

---

## Step 1: Copy the project to your server

**Option A — SCP from your Mac:**
```bash
scp -r /path/to/odyssey-tracker user@your-server-ip:~/odyssey-tracker
```

**Option B — If using git:**
```bash
git clone <your-repo-url> ~/odyssey-tracker
```

**Option C — USB / network share:**
Copy the `odyssey-tracker` folder to `~/odyssey-tracker` on the server.

---

## Step 2: Run setup

```bash
cd ~/odyssey-tracker
chmod +x setup.sh run.sh
./setup.sh
```

This will:
- Create a Python virtual environment in `venv/`
- Install all dependencies (including `openpyxl` for Excel import)
- Generate a `.env` file with a random secret key
- Create the `data/` and `data/temp/` directories

---

## Step 3: Set your password

```bash
nano .env
```

Change `APP_PASSWORD=changeme` to something secure, e.g.:
```
APP_PASSWORD=MySecurePass2024!
```

Other settings you can adjust:
```
PORT=8000          # port to run on
HOST=0.0.0.0       # 0.0.0.0 = accessible on your LAN
CURRENCY=€         # currency symbol
APP_TITLE=My Car   # app name shown in the browser
```

Save and exit: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## Step 4: Test it manually

```bash
./run.sh
```

Open your browser and go to `http://<server-ip>:8000`

You should see the login page. Log in with your password.

Press `Ctrl+C` to stop.

---

## Step 5: Run as a systemd service (auto-start on boot)

### 5a. Edit the service file

```bash
nano odyssey-tracker.service
```

Replace `YOUR_USERNAME` with your actual Linux username (check with `whoami`).
Replace the paths if you put the project somewhere other than `~/odyssey-tracker`.

### 5b. Install the service

```bash
sudo cp odyssey-tracker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable odyssey-tracker
sudo systemctl start odyssey-tracker
```

### 5c. Check it's running

```bash
sudo systemctl status odyssey-tracker
```

You should see `active (running)`.

---

## Useful commands

```bash
# View live logs
sudo journalctl -u odyssey-tracker -f

# Restart after changes
sudo systemctl restart odyssey-tracker

# Stop the service
sudo systemctl stop odyssey-tracker

# Disable auto-start
sudo systemctl disable odyssey-tracker
```

---

## Accessing from other devices on your network

Find your server's IP address:
```bash
ip addr show | grep inet
# or
hostname -I
```

Then visit `http://<server-ip>:8000` from any device on your home network (phone, laptop, tablet).

---

## Backup your data

Your data is stored in a single SQLite file:
```
~/odyssey-tracker/data/car_tracker.db
```

To back it up:
```bash
cp ~/odyssey-tracker/data/car_tracker.db ~/car_tracker_backup_$(date +%Y%m%d).db
```

You can copy this file to restore data on a new machine.

---

## Updating the app

When you get a new version of the app (new Python files or templates):

```bash
cd ~/odyssey-tracker
# Copy in the new files, then:
./setup.sh --update          # updates Python dependencies
sudo systemctl restart odyssey-tracker
```

The `--update` flag re-installs/upgrades all packages from `requirements.txt` without touching your `.env` or data.

---

## Uninstalling

```bash
cd ~/odyssey-tracker
./setup.sh --uninstall
```

This will interactively prompt you to remove:
- `venv/` — the Python virtual environment
- `data/` — your SQLite database and temp files
- `.env` — your config and secret key

The app code itself (Python, templates) stays in place. To fully remove everything:
```bash
rm -rf ~/odyssey-tracker
sudo systemctl disable odyssey-tracker
sudo rm /etc/systemd/system/odyssey-tracker.service
sudo systemctl daemon-reload
```

---

## Optional: Access from outside your home network

> For home use, LAN access is usually sufficient. If you want remote access:

1. **Tailscale** (easiest): Install Tailscale on server and phone/laptop — zero-config VPN.
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   ```

2. **Reverse proxy** (Nginx + Let's Encrypt): More complex, requires a domain name.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `python3-venv` not found | `sudo apt install python3-venv` |
| Port 8000 already in use | Change `PORT=` in `.env` |
| Can't connect from other devices | Check `HOST=0.0.0.0` in `.env` and firewall: `sudo ufw allow 8000` |
| Forgot password | Edit `.env`, change `APP_PASSWORD=`, then `sudo systemctl restart odyssey-tracker` |
| Database corrupted | Restore from backup: `cp backup.db data/car_tracker.db` |
| Excel import fails | Ensure file is `.xlsx` format (not `.xls`); re-save from Excel/LibreOffice |
| Import preview shows wrong values | Check that Finnish date format (DD.MM.YYYY) and comma decimals are used |
