import csv
import uuid
from pathlib import Path

from backend.config import ROOT_DIR, DATA_DIR, UPLOADS_DIR, MAX_UPLOAD_BYTES

DEFAULT_DATASET_PATH = ROOT_DIR / "data" / "creditcard.csv"


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def default_dataset_available():
    return DEFAULT_DATASET_PATH.is_file()


def resolve_dataset_path(dataset_id_or_path):
    if dataset_id_or_path == "default":
        return DEFAULT_DATASET_PATH
    if any(part in str(dataset_id_or_path) for part in ("..", "/", "\\")):
        raise ValueError("Invalid dataset id.")
    return UPLOADS_DIR / dataset_id_or_path


def validate_csv_path(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError("Only CSV files are supported.")
    if path.stat().st_size > MAX_UPLOAD_BYTES:
        raise ValueError("Uploaded file is too large.")
    return path


def summarize_csv(path):
    path = validate_csv_path(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if not header:
            raise ValueError("CSV file is empty or has no header.")
        rows = list(reader)
    missing_counts = {column: 0 for column in header}
    class_counts = {}
    for row in rows:
        for index, column in enumerate(header):
            value = row[index] if index < len(row) else ""
            if value == "" or value is None:
                missing_counts[column] += 1
        if "Class" in header:
            class_index = header.index("Class")
            if class_index < len(row):
                label = row[class_index]
                class_counts[label] = class_counts.get(label, 0) + 1
    return {
        "path": str(path),
        "name": path.name,
        "row_count": len(rows),
        "column_count": len(header),
        "columns": header,
        "missing_counts": missing_counts,
        "class_counts": class_counts,
    }


def default_dataset_summary():
    if not default_dataset_available():
        raise FileNotFoundError("Default dataset data/creditcard.csv was not found.")
    summary = summarize_csv(DEFAULT_DATASET_PATH)
    summary["dataset_id"] = "default"
    summary["original_filename"] = "creditcard.csv"
    return summary


def save_upload(filename, content):
    ensure_dirs()
    safe_name = f"{uuid.uuid4().hex}.csv"
    destination = UPLOADS_DIR / safe_name
    destination.write_bytes(content)
    summary = summarize_csv(destination)
    summary["dataset_id"] = safe_name
    summary["original_filename"] = filename
    return summary
