from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
RESULTS_DIR = ROOT_DIR / "results"
RUNS_DIR = RESULTS_DIR / "runs"
MAX_UPLOAD_BYTES = 200 * 1024 * 1024
ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
