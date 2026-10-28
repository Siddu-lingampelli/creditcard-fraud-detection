import csv
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.config import ROOT_DIR, UPLOADS_DIR, RUNS_DIR, ALLOWED_ORIGINS, MAX_UPLOAD_BYTES
from backend.job_manager import create_job, get_job, latest_job_id, list_jobs, update_job
from backend.services.data_service import (
    save_upload,
    summarize_csv,
    validate_csv_path,
    validate_creditcard_columns,
    default_dataset_available,
    default_dataset_summary,
    resolve_dataset_path,
)
from backend.services.ml_service import start_prediction_job, start_training_job

app = FastAPI(title="Credit Card Fraud Detection API", version="1.0.0")
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _run_dir(job_id: str) -> Path:
    return RUNS_DIR / job_id


def _latest_completed_job(job_type: Optional[str] = None):
    candidates = [job for job in list_jobs() if job["status"] == "completed"]
    if job_type:
        candidates = [job for job in candidates if job["job_type"] == job_type]
    if not candidates:
        return None
    return max(candidates, key=lambda item: item["updated_at"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "fraud-detection-api"}


@router.get("/datasets")
def datasets():
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    try:
        items.append(default_dataset_summary())
    except Exception:
        pass
    for path in sorted(UPLOADS_DIR.glob("*.csv")):
        try:
            items.append(summarize_csv(path))
        except Exception:
            continue
    return {"datasets": items}


@router.post("/dataset/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Uploaded file is too large.")
    try:
        import csv, io
        reader = csv.reader(io.StringIO(content.decode('utf-8', errors='replace')))
        header = next(reader, None) or []
        validate_creditcard_columns(header)
        summary = save_upload(file.filename, content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return summary


@router.get("/dataset/default")
def default_dataset():
    try:
        return default_dataset_summary()
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/dataset/{dataset_id}")
def dataset(dataset_id: str):
    if dataset_id == "default":
        try:
            return default_dataset_summary()
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc))
    path = UPLOADS_DIR / dataset_id
    try:
        return summarize_csv(path)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/jobs/train")
def create_training_job(dataset_id: str, target: str = "Class", seed: int = 42, test_size: float = 0.2, threshold: float = 0.5):
    dataset_path = resolve_dataset_path(dataset_id)
    try:
        validate_csv_path(dataset_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    job_id = create_job("training", dataset_id)
    output_dir = _run_dir(job_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    update_job(job_id, status="queued", progress=0.0, message="Queued")
    start_training_job(job_id, str(dataset_path), str(output_dir), target, seed, test_size, threshold)
    return {"job_id": job_id}


@router.post("/jobs/predict")
def create_prediction_job(dataset_id: str, model_job_id: Optional[str] = None, target: str = "Class"):
    dataset_path = resolve_dataset_path(dataset_id)
    try:
        validate_csv_path(dataset_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if model_job_id:
        model_job = get_job(model_job_id)
        if not model_job or not model_job.get("result"):
            raise HTTPException(status_code=400, detail="Selected model job is not completed.")
        model_path = model_job["result"].get("model_path")
    else:
        completed = _latest_completed_job("training")
        if not completed or not completed.get("result"):
            raise HTTPException(status_code=400, detail="No trained model is available.")
        model_path = completed["result"].get("model_path")
    if not model_path or not Path(model_path).exists():
        raise HTTPException(status_code=400, detail="Saved model could not be found.")
    job_id = create_job("prediction", dataset_id)
    output_dir = _run_dir(job_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    update_job(job_id, status="queued", progress=0.0, message="Queued")
    start_prediction_job(job_id, str(dataset_path), model_path, str(output_dir), target)
    return {"job_id": job_id}


@router.get("/jobs")
def jobs_list():
    return {"jobs": list_jobs()}


@router.get("/jobs/{job_id}")
def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@router.get("/metrics")
def metrics(job_id: Optional[str] = None):
    if job_id:
        job = get_job(job_id)
    else:
        job = _latest_completed_job("training")
    if not job or not job.get("result"):
        raise HTTPException(status_code=404, detail="No completed training metrics are available.")
    result = job["result"]
    return {
        "job_id": job["job_id"],
        "metrics": result.get("metrics", {}),
        "train_rows": result.get("train_rows"),
        "test_rows": result.get("test_rows"),
        "train_class_counts": result.get("train_class_counts"),
        "test_class_counts": result.get("test_class_counts"),
        "feature_count": result.get("feature_count"),
        "dropped_rows": result.get("dropped_rows"),
    }


@router.get("/summary")
def summary():
    job = _latest_completed_job()
    if not job:
        return {"has_results": False, "latest_job": None}
    result = job.get("result") or {}
    metrics = result.get("metrics", {}) if isinstance(result, dict) else {}
    return {
        "has_results": True,
        "latest_job": job,
        "metrics": metrics,
        "predictions_path": result.get("predictions_path") if isinstance(result, dict) else None,
        "model_path": result.get("model_path") if isinstance(result, dict) else None,
    }


def _prediction_files(predictions_path: Path):
    if predictions_path.is_file():
        return [predictions_path]
    if predictions_path.is_dir():
        return sorted(predictions_path.glob("*.csv"))
    return []


def _read_predictions(job_id: str):
    job = get_job(job_id)
    if not job or not job.get("result"):
        raise HTTPException(status_code=404, detail="Job results are not available.")
    result = job["result"]
    predictions_path = Path(result.get("predictions_path", ""))
    files = _prediction_files(predictions_path)
    if not files:
        raise HTTPException(status_code=404, detail="Prediction file is missing.")
    rows = []
    index = 1
    for file_path in files:
        with file_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                row["_id"] = index
                index += 1
                rows.append(row)
    return rows, result


@router.get("/transactions")
def transactions(
    job_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    predicted: Optional[str] = None,
    actual: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    min_probability: Optional[float] = None,
    search: Optional[str] = None,
):
    if job_id:
        selected_job_id = job_id
    else:
        completed = _latest_completed_job()
        selected_job_id = completed["job_id"] if completed else None
    if not selected_job_id:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}
    rows, _ = _read_predictions(selected_job_id)
    filtered = []
    for row in rows:
        if predicted is not None and str(row.get("prediction")) != predicted:
            continue
        if actual is not None and row.get("actual_class") is not None and str(row.get("actual_class")) != actual:
            continue
        amount = row.get("amount")
        if amount is not None:
            try:
                amount_value = float(amount)
                if min_amount is not None and amount_value < min_amount:
                    continue
                if max_amount is not None and amount_value > max_amount:
                    continue
            except ValueError:
                pass
        prob = row.get("fraud_probability")
        if prob is not None and min_probability is not None:
            try:
                if float(prob) < min_probability:
                    continue
            except ValueError:
                pass
        if search and search.lower() not in str(row.get("_id")).lower():
            continue
        filtered.append(row)
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    return {"items": filtered[start:end], "total": total, "page": page, "page_size": page_size}


@router.get("/transactions/{transaction_id}")
def transaction_detail(transaction_id: int, job_id: Optional[str] = None):
    if job_id:
        selected_job_id = job_id
    else:
        completed = _latest_completed_job()
        selected_job_id = completed["job_id"] if completed else None
    if not selected_job_id:
        raise HTTPException(status_code=404, detail="No prediction results are available.")
    rows, _ = _read_predictions(selected_job_id)
    for row in rows:
        if int(row["_id"]) == transaction_id:
            return row
    raise HTTPException(status_code=404, detail="Transaction not found.")


@router.get("/exports/predictions")
def export_predictions(job_id: Optional[str] = None):
    if job_id:
        selected_job_id = job_id
    else:
        completed = _latest_completed_job()
        selected_job_id = completed["job_id"] if completed else None
    if not selected_job_id:
        raise HTTPException(status_code=404, detail="No prediction results are available.")
    job = get_job(selected_job_id)
    result = job.get("result") or {}
    path = Path(result.get("predictions_path", ""))
    files = _prediction_files(path)
    if not files:
        raise HTTPException(status_code=404, detail="Prediction file is missing.")
    combined = path.parent / f"predictions_{selected_job_id}.csv"
    if not combined.exists():
        with combined.open("w", encoding="utf-8", newline="") as output:
            writer = None
            for file_path in files:
                with file_path.open("r", encoding="utf-8", newline="") as handle:
                    reader = csv.DictReader(handle)
                    if writer is None:
                        writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
                        writer.writeheader()
                    for row in reader:
                        writer.writerow(row)
    return FileResponse(combined, filename=f"predictions_{selected_job_id}.csv", media_type="text/csv")


app.include_router(router, prefix='/api')
app.include_router(router, prefix='/api/v1')


