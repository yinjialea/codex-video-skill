"""文案规划测试：验证估时和场景顺序。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from plan_content import build_plan, estimate_duration


class PlanContentTests(unittest.TestCase):
    def test_preserves_paragraph_order(self):
        plan = build_plan("测试", "第一段。\n\n第二段。", 30)
        self.assertEqual([s["id"] for s in plan["scenes"]], ["scene-01", "scene-02"])
        self.assertIn("第一段", plan["scenes"][0]["narration"])

    def test_longer_text_has_longer_estimate(self):
        self.assertGreater(estimate_duration("这是一段更长的中文内容"), estimate_duration("短句"))


if __name__ == "__main__":
    unittest.main()
