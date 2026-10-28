Setup Guide
Windows Local Development and AWS Deployment
This guide is for the existing Windows project directory:

A:\pro\bda\pro\creditcard

Java 17 and PySpark 4.2.0 have already been installed and a Spark smoke
test has started successfully. Do not reinstall them unless
troubleshooting proves it necessary.
1. Local prerequisites
- Windows PowerShell
- Python 3.13.5 (currently installed)
- Java JDK 17 (currently installed under
  C:\Program Files\Eclipse Adoptium\)
- PySpark 4.2.0 installed in .venv (currently installed)
- VS Code (recommended)
- Public Kaggle dataset downloaded manually
The installed combination has passed a basic Spark session test. If
OpenCode finds an actual compatibility error, it should diagnose it
before changing versions.
2. Open the project folder
In PowerShell:
Set-Location "A:\pro\bda\pro\creditcard"
Check the environment:
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -c "import pyspark; print(pyspark.__version__)"
java -version
Configure Python for Spark in the current PowerShell session:
$pythonPath = (Resolve-Path ".venv\Scripts\python.exe").Path
$env:PYSPARK_PYTHON = $pythonPath
$env:PYSPARK_DRIVER_PYTHON = $pythonPath
These two environment variables are session-specific. Set them again in
a new terminal before running Spark if needed.

Create directories if they do not exist:
New-Item -ItemType Directory -Force data, results, tests | Out-Null
3. Dataset setup
Download and extract the dataset from:

https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

Place the CSV here:

A:\pro\bda\pro\creditcard\data\creditcard.csv

Verify:
Test-Path .\data\creditcard.csv
Expected output: True.

Do not upload real payment-card information. Do not commit the dataset
to a public repository.
4. Python dependencies
Use the project interpreter explicitly:
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
If the project is still being initialized and requirements.txt does
not exist yet, OpenCode should create it with only necessary
dependencies. The initial core dependency is pyspark; avoid adding
packages without a project need.
5. Run locally
From the project root:
$pythonPath = (Resolve-Path ".venv\Scripts\python.exe").Path
$env:PYSPARK_PYTHON = $pythonPath
$env:PYSPARK_DRIVER_PYTHON = $pythonPath
& $pythonPath .\fraud_detection.py --input data/creditcard.csv --output results
The exact CLI options should match the implementation. OpenCode must
keep README and this guide synchronized with the actual command-line
interface.

Expected local outputs include prediction CSV part files and a saved
Spark ML pipeline model under results/.
6. Windows troubleshooting
java is not recognized
Close and reopen PowerShell/VS Code. Verify JAVA_HOME and that
%JAVA_HOME%\bin is on PATH. Java was installed at:

C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot
Spark says Python executable python3 is missing
Set the PYSPARK_PYTHON and PYSPARK_DRIVER_PYTHON variables as shown
above, using the absolute path to .venv\Scripts\python.exe.
winutils.exe or native Hadoop warning
A warning alone is not proof of failure. If Spark successfully starts
and processes the dataset, do not add random binaries. Diagnose the
actual exception if an operation fails.
Out of memory
Close other applications, avoid running multiple Spark sessions, and
test on a smaller sample for debugging. Do not silently change the final
evaluation dataset.
7. AWS S3 setup
1. Sign in to AWS Console and open S3:
   https://console.aws.amazon.com/s3/
2. Create a globally unique bucket name, for example
   team9-credit-fraud-<unique-suffix>.
3. Choose a region and use the same region for EC2 when possible.
4. Keep Block Public Access enabled.
5. Create a data/ prefix and upload creditcard.csv.
6. Note the bucket name and region. Do not put credentials in project
   files.
Input URI:

s3://YOUR-BUCKET-NAME/data/creditcard.csv
8. AWS EC2 setup
1. Open EC2: https://console.aws.amazon.com/ec2/
2. Launch a supported Ubuntu Server LTS 64-bit instance.
3. Choose instance memory based on budget and workload. Spark is
   memory-intensive; 4 GiB or more is more comfortable than 1 GiB, but
   check current pricing and account eligibility.
4. Restrict inbound SSH (port 22) to your own IP. Do not open all
   ports.
5. Create and securely retain a key pair if using SSH.
6. Create an IAM role for EC2 with only the S3 permissions needed for
   the project bucket.
7. Attach the role to the instance.
8. Review AWS pricing before launching. EC2, EBS storage, public IPv4
   addresses, and data transfer can incur charges depending on account
   and usage. Stopping an instance may not stop every charge.
Do not automate resource creation without explicit approval.
9. Install runtime on Ubuntu EC2
Connect to EC2 and run:
sudo apt update
sudo apt install -y openjdk-17-jdk python3-pip python3-venv awscli
java -version
python3 --version
aws --version
Create an environment and install the project's pinned/declared
dependencies:
mkdir -p ~/credit-fraud/data ~/credit-fraud/results
cd ~/credit-fraud
python3 -m venv .venv
source .venv/bin/activate
Copy requirements.txt to EC2, then run:
pip install -r requirements.txt
Verify the instance role and S3 access:
aws sts get-caller-identity
aws s3 ls s3://YOUR-BUCKET-NAME/data/
If access is denied, verify role attachment, region, bucket name, and
the policy. Do not add long-lived credentials to the source code.
10. Transfer code and data
From Windows PowerShell, upload the project code (adjust key path and
public IP):
scp -i "$HOME\Downloads\team9-key.pem" .\fraud_detection.py ubuntu@YOUR-EC2-PUBLIC-IP:~/credit-fraud/
scp -i "$HOME\Downloads\team9-key.pem" .\requirements.txt ubuntu@YOUR-EC2-PUBLIC-IP:~/credit-fraud/
From the EC2 terminal:
aws s3 cp s3://YOUR-BUCKET-NAME/data/creditcard.csv ~/credit-fraud/data/creditcard.csv
Run the app using the documented EC2 command, then upload outputs:
aws s3 cp ~/credit-fraud/results/ s3://YOUR-BUCKET-NAME/results/ --recursive
aws s3 ls s3://YOUR-BUCKET-NAME/results/ --recursive
11. Clean up AWS
After the demonstration: - Stop or terminate EC2 when no longer
needed. - Understand the difference: stopping generally retains EBS
storage; terminating may delete instance storage depending on
settings. - Remove unused EBS volumes, snapshots, Elastic IPs, or other
billable resources only after checking whether they contain needed
data. - Keep the S3 bucket only if needed; empty it before deleting if
deletion is intended. - Review AWS Billing and Cost Management.