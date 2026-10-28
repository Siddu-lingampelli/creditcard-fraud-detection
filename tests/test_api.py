import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class ApiTests(unittest.TestCase):
    def test_health(self):
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_summary(self):
        response = client.get("/api/summary")
        self.assertEqual(response.status_code, 200)
        self.assertIn("has_results", response.json())

    def test_datasets(self):
        response = client.get("/api/datasets")
        self.assertEqual(response.status_code, 200)
        self.assertIn("datasets", response.json())


if __name__ == "__main__":
    unittest.main()
