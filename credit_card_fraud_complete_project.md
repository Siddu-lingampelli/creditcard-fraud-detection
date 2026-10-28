# Credit Card Fraud Detection Using Apache Spark and Spark MLlib
## Complete Project Specification, Implementation Guide, Website Workflow, Testing Plan, and AWS Deployment

> **Purpose:** This is the single source of truth for implementing the complete college project. Give this Markdown file to OpenCode and instruct it to inspect the repository, implement the system, run tests, fix issues, and report exactly what was verified.
>
> **Truthfulness requirement:** Do not present illustrative numbers as model results. Do not claim code, tests, dataset runs, or AWS deployment succeeded unless they were actually run and verified.

---

## 1. Project Identity

- **Project title:** Credit Card Fraud Detection Using Apache Spark
- **Project type:** Big Data Analytics + Machine Learning + Web Dashboard
- **Core technologies:** Apache Spark, Spark MLlib, Python, FastAPI, React, TypeScript, Vite, Tailwind CSS, Recharts
- **Cloud technologies:** AWS S3 for private object storage and AWS EC2 for application hosting (optional deployment stage)
- **Development target:** Windows laptop, local execution first
- **Primary dataset:** Public, anonymized Credit Card Fraud Detection dataset from Kaggle
- **Main deliverable:** A functioning web application that trains/evaluates a fraud classifier on labelled transaction data and applies a saved model to new transactions.

### 1.1 Aim

To develop a credit card fraud detection system that processes transaction data using Apache Spark and applies a Spark MLlib machine-learning model to classify transactions as likely genuine or potentially fraudulent, with an interactive website for data upload, training, evaluation, prediction, and report export.

### 1.2 Problem Statement

Credit card fraud is difficult to identify because fraudulent transactions are rare compared with genuine transactions. The project uses historical labelled transaction records to train and evaluate a classifier. The system must report precision, recall, F1 score, ROC-AUC when available, and a confusion matrix rather than relying on accuracy alone.

### 1.3 Objectives

1. Accept and validate transaction CSV files.
2. Use Apache Spark for data processing.
3. Train a model using Spark MLlib.
4. Separate training data from test data to evaluate generalization.
5. Prevent target leakage by excluding the `Class` label from model features.
6. Persist trained models and job metadata.
7. Predict labels for new, unlabelled transactions.
8. Present actual results in a responsive web dashboard.
9. Let users search/filter results and export prediction CSV files.
10. Support local development without cloud credentials.
11. Document optional AWS S3/EC2 deployment safely.
12. Test the complete workflow using synthetic fixtures and, when available, the real dataset.

### 1.4 Scope and Limitations

- This is an educational demonstration, not a production banking fraud prevention service.
- The dataset contains anonymized features; the model cannot explain real-world cardholder identity.
- A predicted fraud label is a model estimate, not proof of fraud.
- The system does not connect to a live payment network or block transactions.
- The initial target is a local Windows workflow. AWS is a later optional stage.
- No AWS resources may be created automatically by the application or coding agent.
- Do not claim regulatory compliance, production-grade security, or guaranteed fraud detection.

---

## 2. High-Level Architecture

```text
User's browser
    |
    v
React + TypeScript + Vite dashboard
    |
    | HTTP/JSON and CSV upload/download
    v
FastAPI backend
    |
    +--> Upload validation and data-quality checks
    |
    +--> Persistent job manager / job status
    |
    +--> Apache Spark / Spark MLlib pipeline
    |        |
    |        +--> Train on labelled data
    |        +--> Evaluate on held-out test data
    |        +--> Save model and preprocessing pipeline
    |        +--> Predict new unlabelled transactions
    |
    +--> Persistent metadata store (SQLite is suitable locally)
    |
    +--> Local filesystem for data, models, and reports
    |
    +--> Optional AWS S3 storage adapter
             |
             v
       Private S3 bucket

Optional cloud deployment:
Browser --> HTTPS / Nginx on EC2 --> FastAPI and frontend
                                  --> EC2 IAM role --> private S3 bucket
```

### 2.1 Component Responsibilities

| Component | Responsibility |
|---|---|
| React | User interface, forms, tables, charts, loading and error states |
| TypeScript | Frontend type safety |
| Vite | Frontend development server and build |
| Tailwind CSS | Consistent responsive styling |
| Recharts | Charts based on actual API data |
| FastAPI | API routes, request validation, job orchestration, exports |
| Pydantic | API request/response validation |
| Apache Spark | Data processing and transformations |
| Spark MLlib | Model pipeline, training, scoring and prediction |
| SQLite | Persistent local job/model metadata if suitable |
| Local filesystem | Uploaded files, saved models and result artifacts |
| boto3 | Optional S3 integration |
| AWS S3 | Private object storage for cloud mode |
| AWS EC2 | Optional cloud compute and hosting |
| Nginx | Optional reverse proxy in cloud deployment |
| Pytest | Backend and ML tests |

---

## 3. Dataset and Exact Input Contract

### 3.1 Dataset Source

Public dataset: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

The standard dataset commonly has approximately 284,807 rows and 492 fraud examples, but the application must inspect the actual uploaded file and must not hardcode these counts as current results.

Expected standard columns:
- `Time`
- `V1` through `V28`
- `Amount`
- `Class`

`Class` is the target label in labelled training/evaluation data:
- `0`: labelled genuine transaction
- `1`: labelled fraudulent transaction

`Time`, `V1`–`V28`, and `Amount` are the standard input features. `Class` must never be included in the model feature vector.

### 3.2 Two Different CSV Workflows

The website must make the distinction very clear.

#### Workflow A — Labelled training/evaluation CSV

Required:
- Expected feature columns.
- `Class` label column.
- Valid numeric feature values.
- `Class` values restricted to 0 and 1.

Purpose:
- Validate and inspect the dataset.
- Split into training and held-out test subsets.
- Train the model using only the training subset.
- Evaluate predictions on the held-out test subset using its labels.
- Save the model, metrics and job metadata.

#### Workflow B — New prediction CSV

Required:
- Expected feature columns.
- `Class` is not required.
- If `Class` is optionally present, it must not be used as an input feature. It may be used for a separately labelled retrospective evaluation, clearly distinguished from ordinary prediction.

Purpose:
- Load an existing saved model.
- Apply the same feature schema and preprocessing.
- Generate predictions for every valid row.
- Export predictions.

If a prediction file is uploaded before a model exists, show a clear message instructing the user to train a model first. Do not automatically train a new model from an unlabelled prediction file.

### 3.3 Upload Validation

Validate:
- File size against a documented configurable limit.
- CSV content can be parsed.
- Required columns exist.
- Feature values are numeric.
- Values are finite (not NaN or positive/negative infinity), or handled by an explicitly documented safe policy.
- `Class` exists for labelled training data.
- `Class` contains only valid labels 0 and 1.
- Enough rows exist for a meaningful train/test split.
- Class distribution is reported.
- Missing values and duplicate rows are measured and reported where practical.
- Column names are not duplicated.
- Unexpected columns are reported; do not silently treat them as model features.
- Files cannot escape the intended storage directory through path traversal or malicious names.

Use safe server-generated filenames and unique IDs. Do not trust the extension alone. Do not display raw stack traces to the user.

### 3.4 Dataset Quality Report

After upload, show:
- Filename (safe display value).
- File size.
- Row count.
- Column count and names.
- Schema validation result.
- Missing-value counts.
- Duplicate count, if checked.
- Label counts and percentages for `Class = 0` and `Class = 1`, when labelled.
- Warnings for severe class imbalance.
- Validation errors with practical next steps.

Do not show fabricated data-quality metrics.

---

## 4. End-to-End User Workflow

### Step 1 — Open the website

The overview page must show:
- Project name and short explanation.
- Model status: `Not trained`, `Training`, `Trained`, or `Failed`.
- Dataset status.
- Recent jobs if any exist.
- Actions to upload a labelled dataset, train a model, or upload prediction data.

When no data or model exists, show a helpful empty state. All counts should be zero or absent as appropriate; do not invent sample metrics.

### Step 2 — Upload a labelled CSV

The user selects a labelled training CSV. The frontend uploads it to FastAPI. The backend validates the contents and returns a data-quality report. The UI shows the report and explains any errors before training can begin.

### Step 3 — Configure training

Allow the user to:
- Choose a supported classifier that is actually implemented.
- Choose a train/test ratio (default 80/20).
- Set a random seed for reproducibility.
- Start training.
- View job status.
- Cancel a job only if cancellation is genuinely implemented and reliable.

A logistic regression classifier is a sensible baseline. Random Forest or other classifiers can be optional additions only if compatible with the installed Spark version and tested.

### Step 4 — Train and evaluate

The backend must:
1. Read labelled data using Spark.
2. Validate the schema and target labels.
3. Split into training and test data with a reproducible seed.
4. Fit learned preprocessing only on training data.
5. Train a Spark MLlib pipeline.
6. Predict on the held-out test subset.
7. Calculate metrics from held-out predictions and labels.
8. Persist the fitted pipeline/model.
9. Persist metrics and job metadata.
10. Mark the job as completed or failed with a meaningful message.

Show truthful job states: `Queued`, `Running`, `Completed`, `Failed`. Report percentage progress only if it can be measured honestly. Do not invent a progress percentage.

### Step 5 — Review model metrics

Show:
- ROC-AUC, if valid scores/probabilities are available.
- Fraud-class precision.
- Fraud-class recall.
- Fraud-class F1 score.
- Confusion matrix.
- True positives, false positives, true negatives and false negatives.
- Training row count and test row count.
- Algorithm, configuration, timestamp and model version.

Metric explanations:
- **Precision:** Among transactions predicted as fraud, the fraction actually labelled fraud.
- **Recall:** Among transactions labelled fraud in the test set, the fraction detected.
- **F1 score:** Harmonic mean of precision and recall.
- **ROC-AUC:** Ability to rank positive fraud examples above genuine examples across thresholds.
- **Confusion matrix:** Counts of correct and incorrect positive/negative predictions.

Fraud data is highly imbalanced. Accuracy alone is insufficient. Handle cases where a test split contains only one class or has no fraud examples; report the metric as unavailable or explain the limitation rather than crashing or inventing a value.

### Step 6 — Upload a new prediction CSV

The user uploads a separate CSV that has the required feature columns but does not need `Class`. The backend checks compatibility and uses the saved model and preprocessing pipeline. It must not retrain the model automatically.

For each input row, produce:
- Stable row number or transaction reference.
- Original features needed for review.
- Predicted class.
- Human-readable label: `Potential Fraud` or `Likely Genuine`.
- Fraud probability/score only if the selected model actually supports a valid score.
- Applied threshold, if threshold-based classification is used.

The UI must say predictions are estimates and not confirmed fraud events.

### Step 7 — Inspect prediction results

Display:
- Number of input transactions processed.
- Number predicted as potential fraud.
- Number predicted as likely genuine.
- Predicted fraud percentage.
- Searchable, sortable, paginated table.
- Filters for prediction class and amount range.
- Transaction detail panel.
- Download CSV button.
- Download summary report button.

Every number must derive from the selected, completed prediction job.

### Step 8 — Export results

Prediction CSV should contain the input row/features and prediction outputs, including class and score/probability only when available. A summary report should include:
- Job ID.
- Safe dataset filename/reference.
- Model version.
- Timestamp.
- Rows processed.
- Prediction counts.
- Metrics when applicable.

Never export credentials, secrets, raw stack traces, or internal filesystem paths.

### Step 9 — Review prior jobs

Persist job metadata and results across application restarts as documented. The Jobs page should show:
- Job ID.
- Job type.
- Safe filename/reference.
- Status.
- Start/end timestamps.
- Rows processed.
- Model version.
- Error summary if failed.
- Link/action to reopen completed results.

Do not delete a working model before a replacement has trained and been saved successfully.

---

## 5. Website Pages and Detailed Requirements

### 5.1 Overview
Display total transactions processed from persisted real jobs, predicted potential fraud count, predicted likely genuine count, current model status, latest training metrics when available, recent jobs, an actual prediction-distribution chart, and actions for upload/train/predict. Before data exists, show an empty state and no fabricated metrics.

### 5.2 Transactions
Display results from a selected prediction job with pagination, search, sort, prediction-class filter, amount filter when available, a detail panel, model prediction and score if supported, and CSV export. Use backend pagination and filtering for large datasets.

### 5.3 Fraud Detection
Provide prediction CSV upload, schema validation, active model selection if multiple models are supported, start-prediction action, job status/errors, result summary, results table, and CSV export. Disable unavailable actions and explain why.

### 5.4 Model Performance
Provide model name/version, ROC-AUC, precision, recall, F1 for the fraud class, confusion matrix, training/test counts, algorithm/configuration, timestamp, and comparison charts only if multiple actual model runs exist.

If threshold adjustment is supported, recompute metrics from saved held-out scores and labels. Do not pretend changing a threshold retrains the model.

### 5.5 Dataset
Provide labelled training CSV upload, unlabelled prediction CSV upload, schema/data-quality report, row/column counts, missing values and duplicates, class distribution when labelled, clear errors/warnings, and a start-training action only for valid labelled data.

### 5.6 Jobs
List training and prediction jobs with status, timestamps, row counts, model version and safe error details. Completed jobs should reopen saved results.

### 5.7 About / How It Works
Explain the objective, classification problem, input data and `Class` label, Spark and Spark MLlib, backend/frontend roles, training versus prediction, evaluation metrics, architecture, local/AWS deployment and limitations. Show a simple flow:
`CSV input -> validation -> Spark processing -> MLlib model -> predictions/metrics -> dashboard/export`.

### 5.8 Shared UI Requirements
- Professional, responsive design.
- Consistent navigation and typography.
- Accessible labels and keyboard navigation.
- Loading, empty, error and success states.
- API error handling.
- Confirmation dialogs for destructive actions.
- Charts with readable labels and tooltips.
- No decorative controls that do nothing.
- No mock fallback that disguises a real API failure.

---

## 6. Backend API Specification

Use versioned endpoints under `/api/v1`.

### Health and overview
- `GET /api/v1/health`: report backend health and relevant dependency status.
- `GET /api/v1/dashboard/summary`: return persisted real counts, current model status and latest available metrics.

### Datasets
- `POST /api/v1/datasets/validate`: accept CSV and declared purpose (`training` or `prediction`); return validation status, safe dataset ID/reference, schema report, row count, missing values, duplicate count if checked, and label distribution if applicable.

### Training
- `POST /api/v1/training-jobs`: accept validated dataset reference and training configuration, create a persisted job and start background execution, and return a job ID.

### Prediction
- `POST /api/v1/prediction-jobs`: accept validated prediction dataset reference and selected saved model, create a job and run prediction using the existing model, and return a job ID.

### Jobs
- `GET /api/v1/jobs`: list jobs with optional filters and pagination.
- `GET /api/v1/jobs/{job_id}`: return job metadata and status.
- `GET /api/v1/jobs/{job_id}/metrics`: return actual metrics for a completed training job.
- `GET /api/v1/jobs/{job_id}/predictions`: return paginated results with search/filter support.
- `GET /api/v1/jobs/{job_id}/export`: download generated CSV or supported summary report.

### Models
- `GET /api/v1/models`: list available saved models and metadata.

Use typed Pydantic schemas, proper HTTP status codes, request validation, safe errors, and clear API documentation. Long-running Spark jobs must not block API request handling. Implement a simple reliable background job mechanism suitable for the project, and document its recovery limitations.

---

## 7. Machine-Learning Design

### 7.1 Pipeline
1. Load labelled CSV with Spark.
2. Validate required columns and target values.
3. Exclude `Class` from features.
4. Split data into training/test sets.
5. Fit transformations using training data only.
6. Train a Spark MLlib classifier.
7. Score the held-out test data.
8. Compute metrics.
9. Persist the fitted pipeline and metadata.
10. Load that saved pipeline for new prediction jobs.

### 7.2 Baseline Model
Start with a Spark MLlib logistic regression pipeline if compatible with the environment. Optionally add a Spark MLlib Random Forest or other supported classifier after the baseline is working and tested.

Any feature scaling, imputation, encoding or feature assembly must be implemented consistently. Fit learned transformations on training data only and reuse them during prediction.

### 7.3 Class Imbalance
The standard fraud dataset is highly imbalanced. Consider class weights where supported, a documented threshold selection strategy, precision and recall, confusion matrix, and PR-oriented evaluation if practical. Do not oversample the test set. Do not choose a threshold based on test labels and then report the same test performance as unbiased final evaluation without explaining the selection process.

### 7.4 Metric Definitions

For the fraud class:
- `TP`: fraud correctly predicted as fraud.
- `FP`: genuine incorrectly predicted as fraud.
- `TN`: genuine correctly predicted as genuine.
- `FN`: fraud incorrectly predicted as genuine.

\[
\text{Precision} = \frac{TP}{TP + FP}
\]

\[
\text{Recall} = \frac{TP}{TP + FN}
\]

\[
\text{F1} = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
\]

Guard against zero denominators. Report a clear unavailable/zero convention consistently and document it.

ROC-AUC must be calculated from valid continuous model scores or probabilities, not from predicted class labels alone.

### 7.5 Persistence
Save:
- Fitted Spark ML pipeline/model.
- Model version/ID.
- Algorithm and configuration.
- Feature schema and order.
- Threshold when applicable.
- Training dataset reference/hash when appropriate.
- Training timestamp.
- Evaluation metrics.
- Job metadata.

Ensure the prediction pipeline loads the same preprocessing and feature order. Use safe replacement so a failed training run does not destroy the last working model.

### 7.6 Scalability
Use Spark DataFrames and MLlib for core processing. Avoid collecting the full dataset to the driver or converting the full dataset to Pandas unnecessarily. Use pagination for large result tables and bounded summaries for charts.

---

## 8. Suggested Repository Structure

Adapt to the existing repository rather than duplicating good existing structure.

```text
creditcard/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── ml/
│   │   ├── storage/
│   │   └── database/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
├── data/
├── models/
├── results/
├── docs/
├── .env.example
├── .gitignore
└── README.md
```

Recommended storage separation:
- `data/`: source or staged input datasets.
- `models/`: saved model pipelines and metadata.
- `results/`: prediction files and reports.
- Backend persistent metadata database: jobs and model references.
- Temporary files: isolated and cleaned up safely.

Do not commit datasets, model binaries, secrets, virtual environments, node modules, or generated results.

---

## 9. Local Windows Environment

Known environment notes:
- Project directory: `A:\pro\bda\pro\creditcard`
- Python virtual environment: `.venv`
- Java 17 is installed.
- PySpark 4.2.0 is installed in `.venv`.
- A local Spark smoke test previously succeeded.
- Windows may emit warnings about `python3`, `winutils.exe`, or the native Hadoop library. Investigate only if these cause an actual failure.

### 9.1 Initial PowerShell Setup

```powershell
cd A:\pro\bda\pro\creditcard

New-Item -ItemType Directory -Force data, models, results, docs | Out-Null

Test-Path .venv\Scripts\python.exe

$pythonPath = (Resolve-Path ".venv\Scripts\python.exe").Path
$env:PYSPARK_PYTHON = $pythonPath
$env:PYSPARK_DRIVER_PYTHON = $pythonPath

& $pythonPath --version
java -version
& $pythonPath -c "import pyspark; print('PySpark:', pyspark.__version__)"
```

If running these commands in a new terminal, repeat the directory change and environment setup. Do not run `Resolve-Path` from an unrelated directory.

### 9.2 Dependency Setup
Inspect existing dependency files first. Install documented backend dependencies into `.venv`. Do not indiscriminately upgrade every package or change the working Spark/Java setup.

Frontend prerequisites:
- Node.js version compatible with the chosen Vite version.
- npm or the package manager specified by the repository.

Provide verified commands in README for installing dependencies and starting both services.

### 9.3 Dataset Setup
Download the dataset manually from:
https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

Place the extracted `creditcard.csv` in the documented data directory, for example:

`A:\pro\bda\pro\creditcard\data\creditcard.csv`

Verify that the file exists and is readable before running a real-data test. Never claim the dataset was tested if it was not present.

---

## 10. Security, Privacy and Reliability

Implement:
- Upload size limits.
- CSV parsing and schema validation.
- Server-generated filenames and IDs.
- Path traversal protection.
- Explicit CORS configuration.
- API request validation.
- Pagination limits.
- Safe error responses.
- No secrets in frontend code, logs, responses or exports.
- `.env.example` with placeholders only.
- `.gitignore` for secrets and generated files.
- Access control before deployment on a public/untrusted network.
- Protection against unrestricted expensive job creation.
- Private S3 bucket access.
- IAM role-based AWS access where possible.
- Configurable data retention and cleanup.
- No public access to uploaded transaction data.
- No false claims that predicted fraud is confirmed fraud.

Do not use real customer payment information in this educational project. The supplied dataset is anonymized.

---

## 11. Testing Plan

Use deterministic synthetic fixtures for fast tests and real Kaggle data for a representative smoke test when available.

### 11.1 Backend Tests
Test:
1. Health endpoint.
2. Valid labelled CSV validation.
3. Valid unlabelled prediction CSV validation.
4. Missing-column rejection.
5. Invalid CSV rejection.
6. Invalid/non-numeric/non-finite values.
7. Invalid `Class` labels.
8. Class-column exclusion from features.
9. Dataset split and reproducibility.
10. Training job creation and status changes.
11. Metric calculation against known expected values.
12. Single-class or no-fraud test-split handling.
13. Model persistence and reload.
14. Prediction using a CSV without `Class`.
15. Prediction output schema and labels.
16. CSV export contents.
17. Pagination and filters.
18. Safe failure handling.
19. Job metadata/results persistence across restart where supported.
20. AWS integration errors if AWS mode is configured.

### 11.2 Frontend Tests
Test:
- Empty dashboard state.
- Loading states.
- Successful dataset validation.
- Upload and validation errors.
- Training job status.
- Display of real model metrics.
- Prediction job flow.
- Search/filter/pagination.
- Export action.
- API failure handling.
- No fabricated fallback data.

### 11.3 Integration and End-to-End Tests
1. Start backend.
2. Start frontend.
3. Validate a small labelled CSV.
4. Train a model.
5. Confirm the job completes and real metrics are returned.
6. Confirm the model is saved.
7. Upload a separate unlabelled CSV.
8. Run predictions with the saved model.
9. Confirm predictions are displayed.
10. Download and inspect the CSV output.
11. Restart the application and verify persisted artifacts/results.
12. Run the full workflow against the real Kaggle dataset if it is available and resources permit.

Use small fixtures for routine automated tests. Do not run expensive full-data training repeatedly without reason. If a test fails, fix it or document the exact unresolved issue. Report actual test counts and pass/fail results.

---

## 12. AWS S3 and EC2 Deployment

AWS is optional until the local application is working.

### 12.1 S3
Use S3 for uploaded datasets if cloud storage is enabled, saved model artifacts if appropriate, prediction exports and reports, and other documented artifacts.

Requirements:
- Private bucket.
- Least-privilege IAM policy.
- EC2 instance role rather than hardcoded access keys.
- Configurable region and bucket name.
- Clear errors for access denied, missing bucket and network failure.
- No public object ACLs.
- Avoid logging signed URLs or secrets.

### 12.2 EC2
Use EC2 to host the backend and frontend/reverse proxy when deployed.

Document:
1. Choosing an appropriate instance based on actual available budget and memory.
2. Installing compatible Python, Java and Node.js/runtime dependencies.
3. Copying or cloning the application.
4. Configuring environment variables.
5. Configuring S3 access through an IAM role.
6. Building the frontend.
7. Starting the backend.
8. Configuring Nginx as a reverse proxy.
9. Enabling HTTPS with an appropriate certificate setup.
10. Restricting inbound network access.
11. Adding authentication/access control before public exposure.
12. Logs, restart behavior and health checks.
13. Data/model backup and cleanup.
14. Stopping or terminating resources when no longer needed.
15. Reviewing current AWS costs and free-tier eligibility.

Do not automatically provision resources or claim AWS deployment is complete without an actual deployment and verification. The local application must work with AWS configuration disabled.

---

## 13. UI Data Rules

Every metric, chart and table must come from a real API response or persisted job result.

Forbidden:
- Hardcoded fake transaction totals.
- Randomly generated dashboard metrics.
- Static sample confusion matrices in production pages.
- Showing fake 100% progress.
- Claiming a training run succeeded without a completed job.
- Claiming AWS is connected if it is not configured.
- Replacing API errors with mock data without clearly labelling a deliberate demo mode.

If demo mode is provided for design development, label it prominently as **DEMO DATA — NOT REAL MODEL OUTPUT** and never mix it with actual jobs.

---

## 14. Error Handling and Edge Cases

Handle:
- Missing dataset.
- Empty CSV.
- Wrong delimiter or malformed CSV.
- Missing required columns.
- Extra unexpected columns.
- Wrong feature order.
- Invalid `Class` values.
- Missing or non-finite feature values.
- Very small datasets.
- Insufficient class examples for stratification or evaluation.
- Training failure.
- Model save/load failure.
- Prediction without a trained model.
- Invalid model version.
- Large uploads.
- Long-running jobs.
- Server restart during a job.
- Missing or inaccessible S3 bucket.
- Invalid AWS configuration.
- Export failure.
- Browser/API network error.
- Zero-denominator metrics.
- Test set containing one class.
- A classifier without probability support.

Give users concise, actionable messages. Keep detailed diagnostic information in protected server logs without exposing secrets.

---

## 15. Documentation Deliverables

### README.md
Include:
- Aim and problem statement.
- Features.
- Architecture.
- Technology stack.
- Project tree.
- Prerequisites.
- Exact local setup commands.
- How to obtain and place the dataset.
- How to start backend and frontend.
- How to train.
- How to predict.
- How to download results.
- How to run tests.
- Common errors and fixes.
- Known limitations.
- AWS deployment summary.

### docs/PROJECT_SPECIFICATION.md
This complete specification or a linked copy of it.

### docs/API.md
Document endpoint methods, paths, parameters, response shapes, errors and upload requirements.

### docs/MODEL_METHODOLOGY.md
Document features, label, preprocessing, train/test split, model choice, imbalance handling, threshold, metrics, leakage prevention and limitations.

### docs/AWS_DEPLOYMENT.md
Document S3, IAM, EC2, environment configuration, Nginx/HTTPS, security, verification and cleanup.

### docs/TESTING.md
Document automated test commands, manual end-to-end checklist, synthetic fixtures and real-data verification status.

### .env.example
Only placeholder settings, such as:
- `APP_ENV`
- `API_HOST`
- `API_PORT`
- `CORS_ORIGINS`
- `DATA_DIR`
- `MODEL_DIR`
- `RESULTS_DIR`
- `DATABASE_URL`
- `AWS_REGION`
- `S3_BUCKET`
- `STORAGE_BACKEND`

Use actual names consistent with the implemented code. Do not include real credentials.

---

## 16. Required Commands and Verification

Document exact, tested commands for:
1. Preparing the local environment.
2. Installing backend dependencies.
3. Installing frontend dependencies.
4. Starting FastAPI.
5. Starting React/Vite.
6. Running backend tests.
7. Running frontend tests.
8. Running integration tests.
9. Validating a dataset.
10. Training a model.
11. Running predictions.
12. Checking job status.
13. Downloading results.
14. Building the production frontend.
15. Running in local mode without AWS.
16. Configuring AWS mode without committing credentials.

Use the actual repository structure and CLI interface. Do not document commands that have not been implemented or tested as if they were verified.

---

## 17. Definition of Done

The project is complete only when:
- The backend starts.
- The frontend starts.
- The frontend calls actual backend APIs.
- A valid labelled CSV is validated.
- A Spark MLlib model trains successfully.
- Evaluation metrics come from held-out test predictions.
- `Class` is excluded from input features.
- The saved model can be loaded after a restart.
- A new unlabelled CSV can be predicted using the saved model.
- Prediction results appear in the website.
- Search, filters and pagination work.
- CSV export works and contains the expected results.
- Jobs and results persist as documented.
- Empty states and errors work.
- Automated tests have been run.
- README and setup instructions match the actual code.
- AWS setup is documented without automatically creating resources.
- No fake metrics appear in the real dashboard.
- Unverified behavior is clearly disclosed.

---

## 18. Instructions to OpenCode: Execute the Work

Treat this document as the authoritative specification.

### Phase 1 — Inspect
- Inspect all repository files and existing project documentation.
- Inspect Python, Java, PySpark, Node.js and npm versions.
- Inspect whether `data/creditcard.csv` exists.
- Preserve useful existing work.
- Report any blocking compatibility issues, then proceed with reasonable solutions.

### Phase 2 — Implement ML
- Implement data validation, Spark MLlib training, evaluation, model persistence and prediction.
- Add deterministic synthetic fixtures.
- Run tests and fix failures.

### Phase 3 — Implement backend
- Implement FastAPI routes, persistent job handling, safe file storage, model management, results and exports.
- Run API tests and fix failures.

### Phase 4 — Implement frontend
- Build every required page.
- Connect all actions to real endpoints.
- Implement loading, empty, error and success states.
- Ensure the website is responsive.
- Run frontend tests and build.

### Phase 5 — Integration
- Run the full local workflow.
- Train on synthetic test data.
- Predict on a separate unlabelled test file.
- Test CSV export.
- Test persistence across restart.
- Run one real-data smoke test if the Kaggle dataset is available and resources permit.

### Phase 6 — Documentation
- Update all documentation to match actual code.
- Include exact PowerShell commands.
- Document known limitations and AWS deployment steps.

### Phase 7 — Final report
Return:
1. What was implemented.
2. Files created/modified.
3. Exact commands to run locally.
4. Exact training workflow.
5. Exact prediction workflow.
6. Test commands and actual results.
7. Whether the real Kaggle dataset was tested.
8. Known failures or unfinished features.
9. AWS deployment status and manual steps remaining.

**Do not stop after creating a plan or a frontend mockup. Implement and verify the actual end-to-end application. Do not invent successful tests, metrics, dataset runs, or deployment status.**
