"""总入口测试：确认 prepare 会停在人工确认点。"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from workflow import prepare_workflow, require_confirmed_plan
from common import WorkflowError


class WorkflowTests(unittest.TestCase):
    def test_prepare_creates_review_files_and_stops(self):
        output = Path("virtual-output")
        with patch("workflow._ensure_writable"), patch("workflow.write_json"), patch("pathlib.Path.write_text"):
            result = prepare_workflow({"topic": "测试", "raw_text": "第一段。\n\n第二段。", "target_duration": 30, "speech_rate": "+50%"}, output, overwrite=True)
        self.assertEqual(result["status"], "awaiting_script_confirmation")

    def test_build_requires_confirmed_plan(self):
        with patch("workflow.read_json", return_value={"confirmed": False}):
            with self.assertRaises(WorkflowError):
                require_confirmed_plan(Path("virtual-plan.json"))


if __name__ == "__main__":
    unittest.main()
