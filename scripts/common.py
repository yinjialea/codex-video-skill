"""共享基础能力：负责 JSON 读写、外部命令执行和媒体时长探测。"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


class WorkflowError(RuntimeError):
    """工作流可预期错误，消息应直接告诉用户如何修复。"""


def read_json(path: Path) -> dict[str, Any]:
    """读取 UTF-8 JSON；配置文件格式错误时抛出清晰异常。"""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkflowError(f"无法读取 JSON：{path}；{exc}") from exc


def write_json(path: Path, data: Any) -> None:
    """以 UTF-8 和便于人工检查的缩进格式保存 JSON。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_command(command: list[str], cwd: Path | None = None, log_path: Path | None = None) -> subprocess.CompletedProcess[str]:
    """使用参数列表执行命令，避免中文、空格路径被错误拆分。"""
    # HyperFrames 输出 UTF-8；Windows 默认 GBK 会让 subprocess 读取线程崩溃。
    result = subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True)
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text((result.stdout or "") + (result.stderr or ""), encoding="utf-8")
    if result.returncode:
        raise WorkflowError(f"命令执行失败（{result.returncode}）：{' '.join(command)}\n{result.stderr[-1200:]}")
    return result


def probe_duration(ffprobe_bin: str, media_path: Path) -> float:
    """通过 FFprobe 获取真实媒体时长，单位为秒。"""
    result = run_command([ffprobe_bin, "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(media_path)])
    return float(result.stdout.strip())
