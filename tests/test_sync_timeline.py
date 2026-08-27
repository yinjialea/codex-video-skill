"""时间轴同步测试：场景边界必须来自真实音频时长。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from sync_timeline import apply_durations


class TimelineTests(unittest.TestCase):
    def test_applies_measured_durations(self):
        result = apply_durations([{"id": "a"}, {"id": "b"}], [2.5, 3.25])
        self.assertEqual((result[0]["start"], result[0]["end"]), (0.0, 2.5))
        self.assertEqual((result[1]["start"], result[1]["end"]), (2.5, 5.75))


if __name__ == "__main__":
    unittest.main()
