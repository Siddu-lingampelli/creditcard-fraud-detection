Product Requirements Document (PRD)
Credit Card Fraud Detection Using Apache Spark MLlib
Project team: Team 9
Project title: Credit Card Fraud Detection using Spark
Required cloud services: AWS S3 and AWS EC2
Primary implementation language: Python
Document status: Initial implementation specification
1. Project Overview
Build a reproducible machine-learning project that identifies
potentially fraudulent credit-card transactions using Apache Spark and
Spark MLlib. The project must run locally on a Windows laptop for
development and testing, then run on an AWS EC2 virtual machine. Amazon
S3 stores the dataset and generated outputs.

This is an academic demonstration using a public, anonymized dataset. It
is not a production banking fraud system and must not be represented as
one.
2. Problem Statement
Fraudulent transactions are rare compared with legitimate transactions.
A classifier should learn from labeled transaction records and estimate
whether a transaction is fraudulent. Because the classes are imbalanced,
overall accuracy alone is not a sufficient evaluation measure.
3. Goals
1. Load and validate a public labeled credit-card transaction CSV.
2. Use PySpark DataFrames and Spark MLlib to train a baseline
   classifier.
3. Evaluate the model with ROC-AUC, precision, recall, F1-score, and a
   confusion matrix.
4. Save predictions and a trained model to local output directories.
5. Support the same application running locally and on AWS EC2.
6. Use Amazon S3 to store the input dataset and copy output artifacts
   to the cloud.
7. Provide clear setup, run, test, and AWS deployment documentation.
8. Avoid embedding AWS credentials or secrets in source code.
4. Non-Goals
- Real-time payment authorization.
- Connection to a real bank or payment processor.
- Use of real cardholder data.
- A production web application or customer-facing dashboard.
- Automatic creation of AWS resources unless explicitly requested and
  configured by the user.
- Guaranteeing that every fraudulent transaction will be detected.
- Training a distributed multi-node Spark cluster. A single EC2
  instance running Spark in local mode is acceptable unless the
  instructor specifies otherwise.
5. Target Users
- Student developers building and demonstrating the project.
- Faculty evaluating the implementation and cloud-service usage.
- Project teammates who need repeatable setup and execution
  instructions.
6. Required Technology Stack
  Area                    Technology              Purpose
  Language                Python                  Application and ML
                                                  pipeline

  Data processing         Apache Spark / PySpark  DataFrames and scalable
                                                  processing

  ML                      Spark MLlib             Classification pipeline
                                                  and evaluation

  Baseline model          Logistic Regression     Interpretable baseline
                                                  classifier

  Optional comparison     Random Forest or        Model comparison, if
                          another Spark MLlib     resources allow
                          classifier              

  Local development       Windows, VS Code,       Build and test locally
                          Python virtual
                          environment             

  Runtime                 Java JDK 17, compatible JVM runtime for Spark
                          with installed Spark
                          distribution            

  Cloud compute           AWS EC2, Ubuntu Server  Run the application in
                                                  the cloud

  Cloud storage           Amazon S3               Store dataset,
                                                  predictions, and model
                                                  artifacts

  AWS permissions         EC2 IAM role with       Secure access to the
                          least-privilege S3      bucket
                          policy                  

  CLI                     AWS CLI                 Verify and transfer S3
                                                  objects

  Version control         Git (recommended)       Track project code

  Documentation           Markdown                PRD, plan, setup, and
                                              execution instructions
Use the installed project environment as the initial baseline. Before
changing Spark/Python versions, confirm compatibility and explain the
reason.
7. Dataset
Use the public Kaggle Credit Card Fraud Detection dataset:
https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

Expected filename: creditcard.csv

Expected target column: Class, where 0 is non-fraud and 1 is
fraud. Typical columns include Time, Amount, anonymized PCA
features, and Class.

The application must: - Check that the CSV exists. - Check that the
Class column exists and has only valid binary labels after
conversion. - Check that at least one feature column exists. - Handle or
clearly report invalid/missing values. - Never silently continue if the
target column is absent. - Never commit the full dataset to a public Git
repository. - Never use real customer or cardholder data.

The dataset is imbalanced. A basic random split is acceptable for a
first academic baseline, but the report must state its limitations. If
feasible, use a reproducible stratified split or explain the selected
split strategy.
8. Functional Requirements
FR-1: Configuration
The application must accept configuration through command-line arguments
or environment variables, including: - Input CSV path. - Output
directory. - Target column (default Class). - Random seed. -
Train/test split ratio. - Optional S3 bucket and S3 input/output paths.

Local execution must work without AWS configuration.
FR-2: Data validation
Print the input path, schema, row count, feature count, and class
distribution. Errors must be actionable.
FR-3: Preprocessing
- Exclude the target column from features.
- Exclude any non-feature identifier if one is added in the future.
- Assemble numeric feature columns using VectorAssembler.
- Scale features if required by the chosen model.
- Fit preprocessing stages on training data as part of a Spark ML
  Pipeline, avoiding leakage from test data.
- Use a stable, reproducible random seed.
FR-4: Training
Train a Logistic Regression baseline with Spark MLlib. Handle invalid
rows deliberately and document the chosen behavior.
FR-5: Evaluation
Report: - ROC-AUC. - Precision. - Recall. - F1-score. - Confusion matrix
values: TP, TN, FP, FN. - Class counts for train and test sets where
practical.

Metrics must be computed from the held-out test set. Do not report
invented or hard-coded scores.
FR-6: Predictions
Save at least these columns to a Spark CSV output directory: - Actual
target (Class). - Predicted label (prediction). - Probability
(probability) or a derived fraud probability if safely extracted.

Include a short README or manifest describing the output files.
FR-7: Model persistence
Save the fitted Spark ML pipeline model to an output directory. Make it
possible to load the model later for prediction, or clearly document any
limitation.
FR-8: S3 integration
Support: - Reading a dataset from S3 or downloading it to EC2 with AWS
CLI. - Uploading local prediction/model artifacts to S3 using AWS CLI or
a documented helper. - A dry-run or preview option for transfers where
practical. - Clear errors if AWS credentials, IAM permissions, bucket
name, or objects are missing.

Prefer an EC2 instance profile/IAM role. Do not require long-lived
access keys in source files.
FR-9: Logging and exit codes
Use clear console logging. Return a non-zero exit code on a failed run.
Never print secret values.
FR-10: Documentation
Provide commands for local setup, local run, tests, AWS preparation, EC2
run, and S3 verification.
9. Non-Functional Requirements
- Reproducible random seed.
- Maintainable modular Python code.
- Reasonable resource use on a student laptop and a small EC2
  instance.
- No secrets committed to Git.
- Dataset and generated artifacts excluded from Git by .gitignore.
- Clear separation between application code, data, and output.
- Graceful error messages.
- No public access to the S3 bucket.
- Restrict EC2 SSH access to the user's IP address.
10. Suggested Project Structure
creditcard/
├── fraud_detection.py
├── requirements.txt
├── README.md
├── .gitignore
├── prd.md
├── plan.md
├── setup.md
├── do.md
├── data/
│   └── creditcard.csv          # downloaded by user; do not commit
├── results/                    # generated; do not commit
└── tests/
    └── test_validation.py
The implementation may introduce a src/ directory if it improves
organization, but keep the run commands simple for a student project.
11. Acceptance Criteria
The project is accepted when: 1. Setup instructions work on the user's
Windows machine with Python, Java 17, and PySpark installed. 2. Missing
dataset or missing Class column produces a useful error. 3. A valid
dataset runs through training and evaluation. 4. The program prints real
metrics from the test split. 5. Predictions and model artifacts are
saved locally. 6. Automated validation tests pass. 7. The same code can
be copied to Ubuntu EC2 and run there. 8. S3 input/output paths are
documented and verified. 9. An EC2 IAM role is used instead of
hard-coded credentials. 10. Documentation explains how to stop/terminate
EC2 and check AWS charges.
12. Risks and Mitigations
- Class imbalance: Report precision/recall/F1 and confusion
  matrix; do not rely on accuracy alone.
- Small instance memory: Start with a small test run; avoid
  training multiple models simultaneously; stop if memory is
  exhausted.
- Windows Spark warnings: Distinguish non-fatal Hadoop
  native-library warnings from actual exceptions.
- Version incompatibility: Record Python, Java, and PySpark
  versions and test the Spark session.
- AWS costs: Use one region for EC2 and S3, least-cost eligible
  resources, and remove resources when finished.
- S3 permission failures: Verify bucket name, role attachment, and
  least-privilege policy.
- Data leakage: Fit preprocessing stages only on training data
  through the Spark ML pipeline.
13. Academic Integrity and Responsible Use
This project is for education and demonstration. Predictions are
probabilistic and can produce false positives and false negatives. Do
not use the system to make real financial decisions. Credit card dataset
features are anonymized; do not claim that the model understands actual
cardholder identity or behavior.