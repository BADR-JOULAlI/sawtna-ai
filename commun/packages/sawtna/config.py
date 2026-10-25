from pathlib import Path
import os

ROOT = Path(os.getenv("SAWTNA_PROJECT_ROOT", str(Path(__file__).resolve().parents[3])))


def data_root() -> Path:
    path = Path(os.getenv("SAWTNA_DATA_DIR", str(ROOT / "commun/data")))
    path.mkdir(parents=True, exist_ok=True)
    return path


def service_key() -> str:
    return os.getenv("SAWTNA_SERVICE_KEY", "local-sawtna-development-only")


def admin_key() -> str:
    return os.getenv("SAWTNA_ADMIN_KEY", "local-sawtna-admin-only")
