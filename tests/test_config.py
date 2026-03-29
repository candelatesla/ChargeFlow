import unittest

from src.utils.config import load_base_config


class ConfigTests(unittest.TestCase):
    def test_base_config_contains_expected_sections(self) -> None:
        config = load_base_config()

        self.assertIn("project", config)
        self.assertIn("sources", config)
        self.assertIn("regions", config)


if __name__ == "__main__":
    unittest.main()
