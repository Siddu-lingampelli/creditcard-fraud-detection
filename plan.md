Implementation Plan
Credit Card Fraud Detection Using Spark MLlib
1. Delivery Strategy
Build and verify locally first, then deploy the same code to AWS EC2 and
use S3 for input/output storage. Do not create AWS resources until local
training works.
2. Phases and Tasks
Phase 0 --- Inspect the existing environment
- [ ] Confirm working directory is A:\pro\bda\pro\creditcard.
- [ ] Confirm Java 17 works.
- [ ] Confirm .venv exists and PySpark imports.
- [ ] Run a small Spark session test.
- [ ] Record Python, Java, and PySpark versions.
- [ ] Do not reinstall software unnecessarily.
Exit condition: A Spark session starts and stops successfully.
Phase 1 --- Project skeleton
- [ ] Create data/, results/, and tests/.
- [ ] Create fraud_detection.py.
- [ ] Create requirements.txt.
- [ ] Create .gitignore.
- [ ] Create README.md.
- [ ] Keep prd.md, plan.md, setup.md, and do.md in the
  repository root.
Exit condition: Project structure is clear and generated data is
ignored by Git.
Phase 2 --- Dataset and validation
- [ ] Obtain the public Kaggle dataset manually.
- [ ] Place creditcard.csv in data/.
- [ ] Validate that the file exists and is readable.
- [ ] Validate Class column and binary labels.
- [ ] Print schema, row count, and class distribution.
- [ ] Produce actionable errors for missing or malformed input.
Exit condition: Data validation succeeds on the real dataset and
fails clearly on invalid input.
Phase 3 --- Machine learning pipeline
- [ ] Build a Spark ML pipeline with feature assembly, optional
  scaling, and Logistic Regression.
- [ ] Use a reproducible split/seed.
- [ ] Fit preprocessing only on training data.
- [ ] Train the model.
- [ ] Calculate ROC-AUC, precision, recall, F1-score, and TP/TN/FP/FN.
- [ ] Print metrics and class counts.
- [ ] Save predictions and the fitted pipeline model.
- [ ] Add an optional threshold setting if it can be implemented and
  tested cleanly.
Exit condition: Local execution completes and writes real outputs.
Phase 4 --- Automated checks
- [ ] Add lightweight unit tests for data validation and metric
  calculations where practical.
- [ ] Test missing file, missing target column, and invalid labels.
- [ ] Run tests.
- [ ] Test one successful local end-to-end run.
- [ ] Confirm no metric is hard-coded.
- [ ] Confirm no secrets are logged.
Exit condition: Tests pass and output files exist.
Phase 5 --- AWS S3
- [ ] User creates a private S3 bucket.
- [ ] User uploads data/creditcard.csv to data/.
- [ ] Confirm bucket and EC2 are in the same region.
- [ ] Document the S3 URI.
- [ ] Keep public access blocked.
Exit condition: Dataset can be listed in S3 and is not public.
Phase 6 --- AWS EC2
- [ ] User launches an Ubuntu EC2 instance appropriate for the dataset
  and budget.
- [ ] User restricts SSH ingress to their IP.
- [ ] User attaches an EC2 IAM role with bucket-scoped S3 permissions.
- [ ] Install Java, Python, PySpark, and AWS CLI on EC2.
- [ ] Verify identity and S3 access.
- [ ] Copy project code to EC2.
- [ ] Download the dataset from S3 to EC2.
- [ ] Run the same Python application on EC2.
- [ ] Upload outputs to S3 and verify them.
Exit condition: Cloud run produces outputs and those outputs appear
in S3.
Phase 7 --- Submission and demonstration
- [ ] Capture S3 bucket/object screenshot.
- [ ] Capture EC2 instance screenshot (hide sensitive details).
- [ ] Capture Spark execution and metric output.
- [ ] Capture S3 result objects.
- [ ] Prepare architecture diagram and a short explanation.
- [ ] Explain class imbalance and metric interpretation.
- [ ] Confirm all AWS resources and costs after demonstration.
3. Priority Order
P0: Local Spark startup, dataset validation, baseline model,
metrics, local outputs.
P1: Tests, reproducible commands, clean documentation.
P2: S3 storage and EC2 deployment.
P3: Optional model comparison, improved thresholding, charts, or a
dashboard only if requested.
4. Implementation Rules for OpenCode
1. Inspect the repository and current environment before editing files.
2. Preserve the existing .venv; do not recreate it unless it is
   broken.
3. Do not replace working installed versions without a demonstrated
   compatibility reason.
4. Do not download the dataset automatically; provide the official link
   and validate the user-provided file.
5. Do not create AWS resources or incur charges automatically.
6. Never request or store AWS secret access keys in code.
7. Use an IAM role for EC2 S3 access.
8. Implement the smallest working end-to-end version first.
9. Run tests and the real local command. Fix errors before claiming
   success.
10. Never fabricate metrics, screenshots, or AWS deployment status.
11. Keep output and dataset out of Git.
12. Explain any command that could delete data, modify system
    configuration, or incur cloud charges before running it.
5. Definition of Done
- Local end-to-end run succeeds.
- Metrics are computed from held-out data.
- Prediction and model outputs are written.
- Validation tests pass.
- Local and AWS commands are documented.
- S3 and EC2 steps are repeatable and use secure permissions.
- Remaining limitations are documented honestly.