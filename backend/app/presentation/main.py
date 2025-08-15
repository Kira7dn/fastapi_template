from fastapi import FastAPI
import uvicorn
import os
import subprocess
from datetime import datetime
from pathlib import Path
import sys

from app.presentation.api.v1.routers import user

app = FastAPI(title="FastAPI Onion App")

app.include_router(user.router, prefix="/users", tags=["users"])


def main():
    dev_mode = os.getenv("DEV_MODE", "true").lower() == "true"
    # Compute reload directory to avoid hardcoded absolute paths
    current_file = Path(__file__).resolve()
    backend_app_dir = current_file.parent.parent  # backend/app
    if dev_mode:
        print(
            "🔄 Checking for schema changes and running Alembic migrations in DEV mode..."
        )
        run_alembic_autogen_and_upgrade()
    uvicorn.run(
        "app.presentation.main:app",
        host="0.0.0.0",
        port=8006,
        reload=dev_mode,
        reload_dirs=[str(backend_app_dir)],
        # reload_excludes=["/home/kira7/workspace/template/fastapi_onion/postgres_data"],
    )


def run_alembic_autogen_and_upgrade():
    """Tự động generate migration + upgrade DB"""
    try:
        # Resolve important paths
        current_file = Path(__file__).resolve()
        backend_dir = current_file.parent.parent.parent  # backend/
        project_root = backend_dir.parent  # repo root
        # Prefer alembic.ini under backend/, fallback to repo root if not found
        backend_ini = backend_dir / "alembic.ini"
        if backend_ini.exists():
            alembic_ini = backend_ini
            working_dir = backend_dir
            ini_arg = "alembic.ini"
        else:
            alembic_ini = project_root / "alembic.ini"
            working_dir = project_root
            ini_arg = str(alembic_ini)

        # 1. Autogenerate migration file
        msg = f"auto migration {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        # Use venv's Alembic executable and clear PYTHONPATH so project 'backend/alembic' doesn't shadow package
        venv_bin = Path(sys.executable).parent
        alembic_exe = venv_bin / "alembic"
        clean_env = os.environ.copy()
        clean_env.pop("PYTHONPATH", None)
        subprocess.run(
            [
                str(alembic_exe),
                "-c",
                ini_arg,
                "revision",
                "--autogenerate",
                "-m",
                msg,
            ],
            check=True,
            cwd=str(working_dir),
            env=clean_env,
        )
        print(f"✅ Alembic autogenerate done: {msg}")

        # 2. Upgrade DB
        subprocess.run(
            [str(alembic_exe), "-c", ini_arg, "upgrade", "head"],
            check=True,
            cwd=str(working_dir),
            env=clean_env,
        )
        print("✅ Alembic migration applied.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Alembic migration failed: {e}")
        exit(1)
