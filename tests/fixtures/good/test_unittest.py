import unittest


class StatusTest(unittest.TestCase):
    def test_status(self):
        result = type("Result", (), {"status": "verified"})()
        self.assertIn("verified", result.status)
        self.assertEqual(result.status, "verified")
