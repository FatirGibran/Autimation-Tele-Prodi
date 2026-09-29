import unittest
from scripts.env_doctor import check_environment

class TestEnvDoctor(unittest.TestCase):
    def test_check_environment_structure(self):
        report = check_environment()
        self.assertIn("healthy", report)
        self.assertIn("checks", report)
        self.assertIn("issues", report)
        self.assertIn("python_version", report["checks"])
        self.assertIn("database", report["checks"])
        self.assertIn("env_vars", report["checks"])
        self.assertTrue(report["checks"]["python_version"]["passed"])

if __name__ == "__main__":
    unittest.main()
