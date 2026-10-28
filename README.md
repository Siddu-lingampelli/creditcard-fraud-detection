# Credit Card Fraud Detection Using Apache Spark MLlib

Academic demonstration project. Not a production fraud system.

## Local setup (Windows)

```powershell
Set-Location "A:\pro\bda\pro\creditcard"
$pythonPath = (Resolve-Path ".venv\Scripts\python.exe").Path
$env:PYSPARK_PYTHON = $pythonPath
$env:PYSPARK_DRIVER_PYTHON = $pythonPath
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Dataset

Download the public Kaggle dataset and place it at `data/creditcard.csv`. Do not commit the dataset.

## Run locally

```powershell
$pythonPath = (Resolve-Path ".venv\Scripts\python.exe").Path
$env:PYSPARK_PYTHON = $pythonPath
$env:PYSPARK_DRIVER_PYTHON = $pythonPath
& $pythonPath .\fraud_detection.py --input .\data\creditcard.csv --output .\results
```

## Tests

```powershell
& $pythonPath -m unittest discover -s tests -v
```

## Outputs

- `results/predictions/` CSV files with `actual_class`, `prediction`, `fraud_probability`.
- `results/model/` saved Spark ML pipeline model.
- `results/manifest.json` configuration and metrics.

## AWS deployment (documentation only)

Create private S3 bucket, upload dataset, launch EC2 with IAM role, install runtime, run same app, upload results, verify. No AWS resources created by this project.


## Windows Hadoop note

Spark writes require Hadoop Windows binaries. If missing, install them under C:\hadoop\bin (winutils.exe and hadoop.dll) or set HADOOP_HOME. The app attempts to detect C:\hadoop automatically.


## Web application (FastAPI + React)

Backend:
```powershell
$pythonPath = (Resolve-Path ".venv\Scripts\python.exe").Path
$env:PYSPARK_PYTHON = $pythonPath
$env:PYSPARK_DRIVER_PYTHON = $pythonPath
& $pythonPath -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Frontend:
```powershell
Set-Location frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. API docs: http://127.0.0.1:8000/docs.

Tests:
```powershell
& $pythonPath -m unittest discover -s tests -v
```

Frontend build:
```powershell
Set-Location frontend
npm run build
```
