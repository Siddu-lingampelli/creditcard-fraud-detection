Instructions for OpenCode
Build, Test, and Run the Credit Card Fraud Detection Project
You are the coding agent responsible for implementing this repository.
Follow the instructions in prd.md, plan.md, and setup.md. Do not
merely describe the project: inspect the repository, create the files,
run the tests, run the application, and report actual outcomes.
1. Current environment and constraints
- OS: Windows
- Project root: A:\pro\bda\pro\creditcard
- Python: 3.13.5
- Java: Eclipse Temurin JDK 17
- PySpark: 4.2.0 installed in .venv
- A Spark session smoke test has succeeded.
- Dataset may not yet exist. Expected path: data\creditcard.csv.
- AWS resources have not necessarily been created.
- AWS credentials are not provided and must not be requested for
  inclusion in source code.
Before doing anything, confirm the current working directory. If it
differs, navigate to the project root. Inspect the existing files and
preserve useful user work.
2. Required workflow
Task A --- Inspect
1. List the project files.
2. Check the .venv interpreter and installed PySpark version.
3. Check whether data/creditcard.csv exists.
4. Do not assume the dataset exists.
5. Do not recreate .venv or reinstall Java/PySpark unless needed.
Task B --- Implement
Create or update the following: - fraud_detection.py -
requirements.txt - .gitignore - README.md -
tests/test_validation.py (or an equivalent small test suite) - Keep
the provided prd.md, plan.md, setup.md, and do.md.

Use a simple, maintainable structure. The main program should support
command-line arguments for input path and output directory, with
sensible defaults. Local runs must not require AWS credentials.
Task C --- Application behavior
The application must: 1. Validate the input file and schema. 2. Verify
that the target column Class exists and contains binary labels 0 and
1. 3. Print row count, feature count, and class distribution. 4. Build
a Spark ML pipeline with VectorAssembler, optional scaling, and
Logistic Regression. 5. Use a reproducible train/test split. 6. Fit
preprocessing only on training data through the pipeline. 7. Calculate
and print ROC-AUC, precision, recall, F1-score, and TP/TN/FP/FN. 8. Save
predictions with actual label, predicted label, and fraud probability if
available. 9. Save the fitted Spark ML pipeline model. 10. Return a
non-zero exit code with a useful message for missing/invalid data or a
failed run. 11. Never hard-code or fabricate model metrics. 12. Keep
logs useful and do not print secrets.

If metric implementation needs a threshold, document it and use it
consistently. Handle the imbalanced dataset honestly. Do not claim the
baseline is production-ready.
Task D --- Compatibility and dependency discipline
1. Use the existing .venv\Scripts\python.exe on Windows.
2. Set PYSPARK_PYTHON and PYSPARK_DRIVER_PYTHON to that interpreter
   in the current terminal before running Spark.
3. Preserve installed Python 3.13.5 / PySpark 4.2.0 / Java 17 unless an
   actual failure demonstrates incompatibility.
4. Keep dependencies minimal. Pin versions only after confirming the
   chosen versions work.
5. Do not add Hadoop binaries or random downloads just to silence a
   warning. Diagnose real exceptions.
Task E --- Tests
Run tests for: - Missing dataset. - Missing Class column. - Invalid
target labels. - Metric calculations if extracted into testable
functions.

Then run the real app if the dataset is present. If it is missing, run
validation tests and tell the user exactly where to place the CSV. Do
not fabricate a successful end-to-end run.
Task F --- Local run
From the project root in PowerShell, use the project interpreter.
Configure:
$pythonPath = (Resolve-Path ".venv\Scripts\python.exe").Path
$env:PYSPARK_PYTHON = $pythonPath
$env:PYSPARK_DRIVER_PYTHON = $pythonPath
Then run the actual CLI command implemented by the program, for example:
& $pythonPath .\fraud_detection.py --input .\data\creditcard.csv --output .\results
Make the README and setup guide match the implemented arguments exactly.
Task G --- AWS readiness
Document, but do not automatically execute, the following: - Create
private S3 bucket with public access blocked. - Upload dataset to
s3://BUCKET/data/creditcard.csv. - Create EC2 Ubuntu instance and
restrict SSH to the user's IP. - Attach least-privilege IAM role for
bucket-specific S3 read/write. - Install Java, Python, PySpark, and AWS
CLI. - Copy code to EC2. - Download the dataset from S3. - Run the same
Python application. - Upload results to S3 and verify objects.

Do not create, modify, or delete AWS resources and do not run commands
that can incur cloud charges without explicit user approval. Do not
request AWS secret access keys. Prefer an EC2 instance profile/IAM role.
3. Project quality requirements
- Include comments only where they clarify non-obvious logic.
- Use clear names and modular functions.
- Add .gitignore entries for .venv/, data/, results/,
  __pycache__/, .pytest_cache/, and local secrets.
- Never commit the dataset or generated artifacts.
- Do not create a web dashboard unless the user requests it.
- Do not add unrelated frameworks or cloud services.
- Make local execution the first successful milestone.
4. Final report required from OpenCode
At the end, provide: 1. Files created or modified. 2. Dependencies used.
3. Exact local run command. 4. Test commands and actual pass/fail
results. 5. Whether the real dataset was available and whether the
end-to-end run succeeded. 6. Actual model metrics only if the program
ran successfully. 7. Exact next actions for AWS, clearly distinguishing
documentation from actions already performed. 8. Any warnings or
limitations.

Never say the project is fully working unless the relevant tests and
actual execution prove it.