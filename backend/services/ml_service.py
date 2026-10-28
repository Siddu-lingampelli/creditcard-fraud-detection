import sys
import threading
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fraud_detection import train_and_evaluate, predict_with_model
from backend.job_manager import update_job


def run_training_job(job_id, dataset_path, output_dir, target, seed, test_size, threshold):
    update_job(job_id, status="running", progress=0.1, message="Starting Spark training job")
    try:
        manifest = train_and_evaluate(
            dataset_path,
            output_dir,
            target=target,
            seed=seed,
            test_size=test_size,
            threshold=threshold,
        )
        update_job(job_id, status="completed", progress=1.0, message="Training completed", result=manifest)
    except Exception as exc:
        update_job(job_id, status="failed", progress=1.0, message="Training failed", error=str(exc))


def start_training_job(job_id, dataset_path, output_dir, target, seed, test_size, threshold):
    thread = threading.Thread(
        target=run_training_job,
        args=(job_id, dataset_path, output_dir, target, seed, test_size, threshold),
        daemon=True,
    )
    thread.start()


def run_prediction_job(job_id, dataset_path, model_path, output_dir, target):
    update_job(job_id, status="running", progress=0.1, message="Starting Spark prediction job")
    try:
        summary = predict_with_model(dataset_path, model_path, output_dir, target=target)
        update_job(job_id, status="completed", progress=1.0, message="Prediction completed", result=summary)
    except Exception as exc:
        update_job(job_id, status="failed", progress=1.0, message="Prediction failed", error=str(exc))


def start_prediction_job(job_id, dataset_path, model_path, output_dir, target):
    thread = threading.Thread(
        target=run_prediction_job,
        args=(job_id, dataset_path, model_path, output_dir, target),
        daemon=True,
    )
    thread.start()
