import unittest

from scripts.export_powerbi import export_powerbi_bundle


class Day6ExportTests(unittest.TestCase):
    def test_export_powerbi_bundle_writes_outputs(self) -> None:
        outputs = export_powerbi_bundle()
        self.assertTrue(outputs)
        self.assertTrue(all(path.exists() for path in outputs))


if __name__ == "__main__":
    unittest.main()
