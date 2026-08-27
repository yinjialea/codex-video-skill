"""外部命令测试：确保中文和空格路径作为独立参数传递。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from render_video import build_render_command
from compose_video import build_subtitle_command


class CommandTests(unittest.TestCase):
    def test_render_command_preserves_project_path(self):
        invocation = build_render_command("项目 路径", "silent.mp4")
        self.assertEqual(invocation["cwd"], "项目 路径")
        self.assertEqual(invocation["command"][-1], "silent.mp4")
        self.assertNotIn("--project", invocation["command"])

    def test_subtitle_command_maps_audio(self):
        command = build_subtitle_command({"ffmpeg_bin": "ffmpeg", "video": "v.mp4", "audio": "a.wav", "ass": "s.ass", "output": "o.mp4", "fonts_dir": "assets"})
        self.assertTrue(any(arg.startswith("ass=") for arg in command))
        self.assertIn("1:a:0", command)


if __name__ == "__main__":
    unittest.main()
