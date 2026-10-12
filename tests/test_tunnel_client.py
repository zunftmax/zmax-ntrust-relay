"""Test the tunnel client argument handling; no network is opened."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "client" / "ntrust-tunnel"


class TunnelClient(unittest.TestCase):
    def run_client(self, *args):
        return subprocess.run(["sh", str(CLIENT), *args],
                              capture_output=True, text=True)

    def test_help_explains_direction_and_defaults(self):
        result = self.run_client("-h")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("127.0.0.1:8081", result.stdout)
        self.assertIn("usage:", result.stdout)

    def test_missing_destination_is_rejected(self):
        result = self.run_client()
        self.assertNotEqual(result.returncode, 0)

    def test_non_numeric_ports_are_rejected_before_ssh(self):
        result = self.run_client("-l", "eighty", "operator@example.com")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decimal", result.stderr)


if __name__ == "__main__":
    unittest.main()
