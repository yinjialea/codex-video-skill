"""共享命令执行测试：Windows 中文环境也必须安全读取 UTF-8 日志。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from common import run_command


class CommonCommandTests(unittest.TestCase):
    def test_reads_utf8_output_without_using_system_gbk(self):
        command = [sys.executable, "-c", "import sys;sys.stdout.buffer.write('✓中文'.encode('utf-8'))"]
        result = run_command(command)
        self.assertEqual(result.stdout, "✓中文")


if __name__ == "__main__":
    unittest.main()
