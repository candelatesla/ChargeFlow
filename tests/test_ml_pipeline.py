import json
import unittest

from src.ml.pipeline import run_ml_pipeline


class MLPipelineTests(unittest.TestCase):
    def test_run_ml_pipeline_writes_core_outputs(self) -> None:
        outputs = run_ml_pipeline()

        for path in outputs.values():
            self.assertTrue(path.exists())

        demand_metrics = json.loads(outputs["demand_metrics"].read_text(encoding="utf-8"))
        failure_metrics = json.loads(outputs["failure_metrics"].read_text(encoding="utf-8"))

        self.assertIn("mae", demand_metrics)
        self.assertIn("rmse", demand_metrics)
        self.assertIn("precision", failure_metrics)
        self.assertIn("recall", failure_metrics)


if __name__ == "__main__":
    unittest.main()
