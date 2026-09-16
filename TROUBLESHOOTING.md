# Troubleshooting Guide

## Database Issues

### Problem: "duplicate column name" or "table already exists"

**Quick fix — delete the database and restart:**

```powershell
Remove-Item *.db -Force
python -m app.main
```

Migrations run automatically on startup and will recreate a clean schema.

**Or use the reset script (asks for confirmation):**

```powershell
python reset_db.py
python migrate.py
```

### Problem: "No module named 'alembic'" (or other missing modules)

The virtual environment is not activated or dependencies are not installed.

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If `venv` doesn't exist, create it first:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Problem: "No module named 'app'"

You are running Python from the wrong directory. Run the app from the project root:

```powershell
cd C:\Users\IM\Desktop\math_project_divin
.\venv\Scripts\Activate.ps1
python -m app.main
```

### Problem: `uvicorn.run() got an unexpected keyword argument 'debug'`

Already fixed — `app/main.py` uses `reload=settings.debug` now. Make sure you have the latest code.

## Common Commands

**Start the app:**

```powershell
start.bat            # cmd — full setup + run
.\start.ps1          # PowerShell — full setup + run
python -m app.main   # direct (venv must be activated)
```

**Apply migrations manually:**

```powershell
python migrate.py
```

**Run tests:**

```powershell
pip install pytest pytest-asyncio httpx
pytest
```

## If nothing works

1. Delete the `venv` folder
2. Delete all `*.db` files
3. Run `start.bat` — it recreates everything from scratch
