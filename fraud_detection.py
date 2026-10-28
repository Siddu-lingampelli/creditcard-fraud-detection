"""Credit Card Fraud Detection using Apache Spark MLlib."""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.functions import vector_to_array

DEFAULT_TARGET = "Class"
DEFAULT_SEED = 42
DEFAULT_TEST_SIZE = 0.2
DEFAULT_THRESHOLD = 0.5
REQUIRED_BASE_COLUMNS = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]
ID_COLUMNS = {"id", "ID", "transaction_id", "TransactionID"}


def validate_input_path(input_path):
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Input CSV not found: {path}. "
            "Download creditcard.csv from Kaggle and place it at data/creditcard.csv."
        )
    return path


def validate_binary_labels(values):
    if not values:
        raise ValueError("Target column has no values.")
    normalized = set()
    for value in values:
        if value is None:
            raise ValueError("Target column contains null values.")
        try:
            integer_value = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Target column contains a non-integer label: {value!r}.") from exc
        if integer_value not in (0, 1):
            raise ValueError(f"Target column contains an invalid binary label: {value!r}.")
        normalized.add(integer_value)
    return normalized


def validate_creditcard_schema(columns, require_target=False, target=DEFAULT_TARGET):
    missing = [column for column in REQUIRED_BASE_COLUMNS if column not in columns]
    if require_target and target not in columns:
        missing.append(target)
    if missing:
        raise ValueError(
            "This CSV does not look like the credit card fraud dataset. Missing columns: "
            + ", ".join(missing)
        )


def get_feature_columns(columns, dtypes, target, id_columns=ID_COLUMNS):
    dtype_map = {name: dtype for name, dtype in dtypes}
    numeric_types = {
        "byte", "short", "integer", "long", "float", "double", "decimal",
    }
    features = []
    for column in columns:
        if column == target or column in id_columns:
            continue
        dtype = str(dtype_map.get(column, "")).lower()
        base_type = dtype.split("(")[0].strip()
        if base_type in numeric_types:
            features.append(column)
    return features


def compute_metrics(tp, tn, fp, fn):
    total = tp + tn + fp + fn
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    accuracy = (tp + tn) / total if total else 0.0
    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
    }


def configure_windows_hadoop():
    if os.name != "nt":
        return
    existing = os.environ.get("HADOOP_HOME")
    if existing and Path(existing, "bin", "winutils.exe").exists() and Path(existing, "bin", "hadoop.dll").exists():
        os.environ["PATH"] = str(Path(existing, "bin")) + os.pathsep + os.environ.get("PATH", "")
        return
    candidate_dirs = [Path("C:/hadoop")]
    for candidate in candidate_dirs:
        if (candidate / "bin" / "winutils.exe").exists() and (candidate / "bin" / "hadoop.dll").exists():
            os.environ["HADOOP_HOME"] = str(candidate)
            os.environ["PATH"] = str(candidate / "bin") + os.pathsep + os.environ.get("PATH", "")
            return
    source_dir = Path("C:/hadoop")
    if (source_dir / "bin" / "winutils.exe").exists() and (source_dir / "bin" / "hadoop.dll").exists():
        hadoop_home = Path.cwd() / ".hadoop"
        binary_dir = hadoop_home / "bin"
        binary_dir.mkdir(parents=True, exist_ok=True)
        for filename in ("winutils.exe", "hadoop.dll"):
            source = source_dir / "bin" / filename
            destination = binary_dir / filename
            if not destination.exists():
                shutil.copy2(source, destination)
        os.environ["HADOOP_HOME"] = str(hadoop_home)
        os.environ["PATH"] = str(binary_dir) + os.pathsep + os.environ.get("PATH", "")
        return
    print(
        "WARNING: Hadoop Windows binaries (winutils.exe and hadoop.dll) were not found. "
        "Spark file writes may fail. Install them under C:/hadoop/bin or set HADOOP_HOME.",
        file=sys.stderr,
    )


def create_spark_session():
    return (
        SparkSession.builder
        .appName("CreditCardFraudDetection")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.hadoop.hadoop.io.nativeio.enabled", "false")
        .config("spark.hadoop.io.nativeio.enabled", "false")
        .getOrCreate()
    )


def validate_dataset(df, target):
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' is missing from the input CSV.")
    feature_columns = get_feature_columns(df.columns, df.dtypes, target)
    if not feature_columns:
        raise ValueError("No numeric feature columns were found.")
    distinct_labels = [row[0] for row in df.select(target).distinct().collect()]
    validate_binary_labels(distinct_labels)
    class_counts = {int(row[0]): int(row[1]) for row in df.groupBy(target).count().collect()}
    if len(class_counts) < 2:
        raise ValueError("Both classes 0 and 1 must be present in the target column.")
    return feature_columns, class_counts


def print_class_distribution(name, counts):
    print(f"{name} class distribution:")
    for label in sorted(counts):
        print(f"  class {label}: {counts[label]}")


def train_and_evaluate(input_path, output_dir, target=DEFAULT_TARGET, seed=DEFAULT_SEED,
                      test_size=DEFAULT_TEST_SIZE, threshold=DEFAULT_THRESHOLD):
    input_path = validate_input_path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    configure_windows_hadoop()
    spark = create_spark_session()
    try:
        spark.sparkContext.setLogLevel("WARN")
        print(f"Input path: {input_path}")
        print(f"Output directory: {output_dir}")

        df = spark.read.csv(str(input_path), header=True, inferSchema=True)
        print("Schema:")
        df.printSchema()
        original_count = df.count()
        print(f"Row count: {original_count}")
        validate_creditcard_schema(df.columns, require_target=True, target=target)
        feature_columns, class_counts = validate_dataset(df, target)
        print(f"Feature count: {len(feature_columns)}")
        print(f"Feature columns: {feature_columns}")
        print_class_distribution("Input", class_counts)

        clean_columns = feature_columns + [target]
        clean_df = df.dropna(subset=clean_columns)
        dropped_rows = original_count - clean_df.count()
        if dropped_rows:
            print(f"Dropped rows with missing values: {dropped_rows}")
        if clean_df.count() == 0:
            raise ValueError("No valid rows remain after removing missing values.")

        clean_df = clean_df.withColumn("label", col(target).cast("double"))
        train_df, test_df = clean_df.randomSplit(
            [1.0 - test_size, test_size], seed=seed
        )
        train_counts = {
            int(row[0]): int(row[1])
            for row in train_df.groupBy(target).count().collect()
        }
        test_counts = {
            int(row[0]): int(row[1])
            for row in test_df.groupBy(target).count().collect()
        }
        print(f"Train rows: {train_df.count()}")
        print_class_distribution("Train", train_counts)
        print(f"Test rows: {test_df.count()}")
        print_class_distribution("Test", test_counts)

        assembler = VectorAssembler(
            inputCols=feature_columns, outputCol="features_raw", handleInvalid="skip"
        )
        scaler = StandardScaler(
            inputCol="features_raw", outputCol="features", withMean=True, withStd=True
        )
        logistic_regression = LogisticRegression(
            featuresCol="features",
            labelCol="label",
            predictionCol="prediction",
            probabilityCol="probability",
            rawPredictionCol="rawPrediction",
            maxIter=100,
            regParam=0.01,
            elasticNetParam=0.0,
            threshold=threshold,
        )
        pipeline = Pipeline(stages=[assembler, scaler, logistic_regression])
        print("Training Logistic Regression baseline...")
        model = pipeline.fit(train_df)

        predictions = model.transform(test_df)
        tp = predictions.filter((col("label") == 1.0) & (col("prediction") == 1.0)).count()
        tn = predictions.filter((col("label") == 0.0) & (col("prediction") == 0.0)).count()
        fp = predictions.filter((col("label") == 0.0) & (col("prediction") == 1.0)).count()
        fn = predictions.filter((col("label") == 1.0) & (col("prediction") == 0.0)).count()
        metrics = compute_metrics(tp, tn, fp, fn)

        evaluator = BinaryClassificationEvaluator(
            labelCol="label", rawPredictionCol="rawPrediction", metricName="areaUnderROC"
        )
        roc_auc = evaluator.evaluate(predictions)
        metrics["roc_auc"] = roc_auc

        print("Evaluation metrics (held-out test set):")
        print(f"  ROC-AUC: {roc_auc:.6f}")
        print(f"  Precision (fraud class): {metrics['precision']:.6f}")
        print(f"  Recall (fraud class): {metrics['recall']:.6f}")
        print(f"  F1-score (fraud class): {metrics['f1']:.6f}")
        print(f"  Accuracy: {metrics['accuracy']:.6f}")
        print("  Confusion matrix:")
        print(f"    TP: {tp}  TN: {tn}")
        print(f"    FP: {fp}  FN: {fn}")

        predictions_output = output_dir / "predictions"
        prediction_select = []
        if target in [f.name for f in predictions.schema.fields]:
            prediction_select.append(col(target).alias("actual_class"))
        if "Amount" in predictions.columns:
            prediction_select.append(col("Amount").alias("amount"))
        prediction_select.append(col("prediction"))
        prediction_select.append(vector_to_array(col("probability"))[1].alias("fraud_probability"))
        output_predictions = predictions.select(*prediction_select)
        output_predictions.write.mode("overwrite").option("header", "true").csv(
            str(predictions_output)
        )
        print(f"Predictions written to: {predictions_output}")

        model_output = output_dir / "model"
        model.write().overwrite().save(str(model_output))
        print(f"Model written to: {model_output}")

        manifest = {
            "input": str(input_path),
            "output": str(output_dir),
            "target": target,
            "seed": seed,
            "test_size": test_size,
            "threshold": threshold,
            "feature_count": len(feature_columns),
            "feature_columns": feature_columns,
            "train_rows": train_df.count(),
            "test_rows": test_df.count(),
            "train_class_counts": train_counts,
            "test_class_counts": test_counts,
            "dropped_rows": dropped_rows,
            "metrics": metrics,
            "predictions_path": str(predictions_output),
            "model_path": str(model_output),
        }
        manifest_path = output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"Manifest written to: {manifest_path}")

        readme_path = output_dir / "README.md"
        readme_path.write_text(
            "# Credit Card Fraud Detection Outputs\n\n"
            "Generated by fraud_detection.py.\n\n"
            "- predictions/: CSV files with actual_class, prediction, fraud_probability.\n"
            "- model/: Saved Spark ML pipeline model.\n"
            "- manifest.json: Run configuration and evaluation metrics.\n",
            encoding="utf-8",
        )
        print(f"Output README written to: {readme_path}")
        print("Run completed successfully.")
        return manifest
    except Exception:
        raise
    finally:
        spark.stop()


def predict_with_model(input_path, model_path, output_dir, target=DEFAULT_TARGET):
    input_path = validate_input_path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    configure_windows_hadoop()
    spark = create_spark_session()
    try:
        spark.sparkContext.setLogLevel("WARN")
        df = spark.read.csv(str(input_path), header=True, inferSchema=True)
        validate_creditcard_schema(df.columns, require_target=False)
        model = PipelineModel.load(str(model_path))
        assembler = model.stages[0]
        feature_columns = list(assembler.getInputCols())
        missing = [c for c in feature_columns if c not in df.columns]
        if missing:
            raise ValueError(f"Input is missing required feature columns: {missing}")
        clean_df = df.dropna(subset=feature_columns)
        if clean_df.count() == 0:
            raise ValueError("No valid rows remain after removing missing values.")
        predictions = model.transform(clean_df)
        fraud_probability = vector_to_array(col("probability"))[1].alias("fraud_probability")
        select_cols = []
        if target in df.columns:
            select_cols.append(col(target).alias("actual_class"))
        if "Amount" in predictions.columns:
            select_cols.append(col("Amount").alias("amount"))
        select_cols.append(col("prediction"))
        select_cols.append(fraud_probability)
        output_predictions = predictions.select(*select_cols)
        predictions_output = output_dir / "predictions"
        output_predictions.write.mode("overwrite").option("header", "true").csv(
            str(predictions_output)
        )
        total = predictions.count()
        fraud_count = predictions.filter(col("prediction") == 1.0).count()
        summary = {
            "input": str(input_path),
            "output": str(output_dir),
            "model": str(model_path),
            "rows": total,
            "predicted_fraud": fraud_count,
            "predicted_legitimate": total - fraud_count,
            "fraud_percentage": (fraud_count / total * 100.0) if total else 0.0,
            "feature_columns": feature_columns,
            "predictions_path": str(predictions_output),
            "has_labels": target in df.columns,
        }
        manifest_path = output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary
    finally:
        spark.stop()


def run_cli(args):
    try:
        manifest = train_and_evaluate(
            args.input, args.output, args.target, args.seed, args.test_size, args.threshold
        )
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Credit Card Fraud Detection using Apache Spark MLlib"
    )
    parser.add_argument("--input", default="data/creditcard.csv", help="Input CSV path.")
    parser.add_argument("--output", default="results", help="Output directory.")
    parser.add_argument("--target", default=DEFAULT_TARGET, help="Target column name.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed.")
    parser.add_argument(
        "--test-size", type=float, default=DEFAULT_TEST_SIZE, help="Test split ratio."
    )
    parser.add_argument(
        "--threshold", type=float, default=DEFAULT_THRESHOLD, help="Classification threshold."
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if not 0.0 < args.test_size < 1.0:
        print("ERROR: --test-size must be between 0 and 1.", file=sys.stderr)
        return 2
    if not 0.0 <= args.threshold <= 1.0:
        print("ERROR: --threshold must be between 0 and 1.", file=sys.stderr)
        return 2
    return run_cli(args)


if __name__ == "__main__":
    sys.exit(main())
