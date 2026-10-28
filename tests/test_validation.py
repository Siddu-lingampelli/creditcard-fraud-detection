import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fraud_detection import (
    compute_metrics,
    get_feature_columns,
    validate_binary_labels,
    validate_input_path,
)


class ValidationTests(unittest.TestCase):
    def test_validate_input_path_missing_raises(self):
        with self.assertRaises(FileNotFoundError):
            validate_input_path("data/does-not-exist.csv")

    def test_validate_binary_labels_invalid_raises(self):
        with self.assertRaises(ValueError):
            validate_binary_labels([0, 1, 2])

    def test_validate_binary_labels_empty_raises(self):
        with self.assertRaises(ValueError):
            validate_binary_labels([])

    def test_get_feature_columns_excludes_target_and_ids(self):
        columns = ["Time", "Amount", "V1", "Class", "id"]
        dtypes = [
            ("Time", "double"),
            ("Amount", "double"),
            ("V1", "double"),
            ("Class", "integer"),
            ("id", "long"),
        ]
        features = get_feature_columns(columns, dtypes, "Class")
        self.assertEqual(features, ["Time", "Amount", "V1"])

    def test_compute_metrics_basic(self):
        metrics = compute_metrics(tp=10, tn=90, fp=5, fn=2)
        self.assertEqual(metrics["tp"], 10)
        self.assertEqual(metrics["tn"], 90)
        self.assertEqual(metrics["fp"], 5)
        self.assertEqual(metrics["fn"], 2)
        self.assertAlmostEqual(metrics["precision"], 10 / 15)
        self.assertAlmostEqual(metrics["recall"], 10 / 12)
        self.assertGreater(metrics["f1"], 0)

    def test_compute_metrics_zero_division(self):
        metrics = compute_metrics(tp=0, tn=5, fp=0, fn=0)
        self.assertEqual(metrics["precision"], 0.0)
        self.assertEqual(metrics["recall"], 0.0)
        self.assertEqual(metrics["f1"], 0.0)


if __name__ == "__main__":
    unittest.main()
