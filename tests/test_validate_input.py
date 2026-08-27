"""配置校验模块测试：确保错误在耗时操作开始前被发现。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from validate_input import validate_config


class ValidateInputTests(unittest.TestCase):
    def test_reports_all_missing_fields(self):
        errors = validate_config({})
        joined = " ".join(errors)
        self.assertIn("topic", joined)
        self.assertIn("raw_text", joined)

    def test_rejects_invalid_rate(self):
        config = {"topic": "主题", "raw_text": "文案", "target_duration": 60, "speech_rate": "fast"}
        self.assertTrue(any("speech_rate" in error for error in validate_config(config)))


if __name__ == "__main__":
    unittest.main()
