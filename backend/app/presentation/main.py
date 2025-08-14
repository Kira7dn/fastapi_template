from fastapi import FastAPI
import uvicorn
import os
import subprocess
from datetime import datetime
from pathlib import Path
import sys

# Ensure 'backend' is on sys.path when running this file directly
# Path layout: backend/app/presentation/main.py -> parents[2] == backend/
CURRENT_FILE = Path(__file__).resolve()
BACKEND_DIR = CURRENT_FILE.parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.presentation.api.v1.routers import user

app = FastAPI(title="FastAPI Onion App")

app.include_router(user.router, prefix="/users", tags=["users"])


def run_alembic_autogen_and_upgrade():
    """Tự động generate migration + upgrade DB"""
    print("🔄 Checking for schema changes and running Alembic migrations...")

    try:
        # Resolve important paths
        current_file = Path(__file__).resolve()
        backend_dir = current_file.parent.parent.parent  # backend/
        project_root = backend_dir.parent  # repo root
        alembic_ini = project_root / "alembic.ini"

        # 1. Autogenerate migration file
        msg = f"auto migration {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        subprocess.run(
            [
                "alembic",
                "-c",
                str(alembic_ini),
                "revision",
                "--autogenerate",
                "-m",
                msg,
            ],
            check=True,
            cwd=str(project_root),
        )
        print(f"✅ Alembic autogenerate done: {msg}")

        # 2. Upgrade DB
        subprocess.run(
            ["alembic", "-c", str(alembic_ini), "upgrade", "head"],
            check=True,
            cwd=str(project_root),
        )
        print("✅ Alembic migration applied.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Alembic migration failed: {e}")
        exit(1)


if __name__ == "__main__":
    dev_mode = os.getenv("DEV_MODE", "true").lower() == "true"

    if dev_mode:
        print(
            "🔄 Checking for schema changes and running Alembic migrations in DEV mode..."
        )
        run_alembic_autogen_and_upgrade()

    # Compute reload directory to avoid hardcoded absolute paths
    current_file = Path(__file__).resolve()
    backend_app_dir = current_file.parent.parent  # backend/app

    uvicorn.run(
        "app.presentation.main:app",
        host="0.0.0.0",
        port=8006,
        reload=dev_mode,
        reload_dirs=[str(backend_app_dir)],
        # reload_excludes=["/home/kira7/workspace/template/fastapi_onion/postgres_data"],
    )
