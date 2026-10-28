import json
import sqlite3
import threading
import time
import uuid
from pathlib import Path

from backend.config import ROOT_DIR

DB_PATH = ROOT_DIR / "results" / "jobs.db"
_lock = threading.Lock()


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                job_type TEXT NOT NULL,
                dataset_id TEXT,
                status TEXT NOT NULL,
                progress REAL NOT NULL DEFAULT 0,
                message TEXT,
                error TEXT,
                result TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        connection.commit()


def _row_to_job(row):
    if row is None:
        return None
    job = dict(row)
    if job.get("result"):
        try:
            job["result"] = json.loads(job["result"])
        except json.JSONDecodeError:
            pass
    return job


def create_job(job_type, dataset_id=None):
    job_id = str(uuid.uuid4())
    now = time.time()
    with _lock, _connect() as connection:
        connection.execute(
            "INSERT INTO jobs (job_id, job_type, dataset_id, status, progress, message, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (job_id, job_type, dataset_id, "queued", 0.0, "Queued", now, now),
        )
        connection.commit()
    return job_id


def update_job(job_id, **fields):
    if not fields:
        return
    if "result" in fields and not isinstance(fields["result"], str):
        fields["result"] = json.dumps(fields["result"])
    assignments = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [time.time(), job_id]
    with _lock, _connect() as connection:
        connection.execute(
            f"UPDATE jobs SET {assignments}, updated_at = ? WHERE job_id = ?",
            values,
        )
        connection.commit()


def get_job(job_id):
    with _lock, _connect() as connection:
        row = connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    return _row_to_job(row)


def list_jobs():
    with _lock, _connect() as connection:
        rows = connection.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
    return [_row_to_job(row) for row in rows]


def latest_job_id(job_type=None):
    query = "SELECT job_id FROM jobs"
    params = ()
    if job_type:
        query += " WHERE job_type = ?"
        params = (job_type,)
    query += " ORDER BY updated_at DESC LIMIT 1"
    with _lock, _connect() as connection:
        row = connection.execute(query, params).fetchone()
    return row["job_id"] if row else None


init_db()
