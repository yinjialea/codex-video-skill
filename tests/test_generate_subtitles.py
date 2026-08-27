"""字幕模块测试：验证样式、换行和时间戳。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from generate_subtitles import Cue, build_ass, proportional_cues


class SubtitleTests(unittest.TestCase):
    def test_ass_uses_requested_style(self):
        ass = build_ass([Cue(0, 2, "测试字幕")], 52, 150)
        self.assertIn("SimHei,52", ass)
        self.assertIn(",150,1", ass)

    def test_cues_do_not_overlap(self):
        cues = proportional_cues("第一句。第二句。", 0, 4)
        self.assertTrue(all(a.end <= b.start for a, b in zip(cues, cues[1:])))

    def test_long_sentence_is_split_without_losing_text(self):
        text = "这是一个用于验证长字幕不会被截断的中文句子，它需要被拆成多条字幕并完整保留所有文字。"
        cues = proportional_cues(text, 0, 8)
        self.assertEqual("".join(cue.text for cue in cues), text)
        self.assertTrue(all(len(cue.text) <= 36 for cue in cues))


if __name__ == "__main__":
    unittest.main()
