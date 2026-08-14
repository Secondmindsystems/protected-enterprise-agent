import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("render_execution_proof", ROOT / "scripts" / "render_execution_proof.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ExecutionProofRendererTests(unittest.TestCase):
    def test_missing_required_evidence_is_not_proven(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = MODULE.evaluate(ROOT, Path(temporary))
        self.assertEqual(result["status"], "NOT PROVEN")
        self.assertIn("VENDOR_QUALIFICATION.json", result["missing"])


if __name__ == "__main__":
    unittest.main()
