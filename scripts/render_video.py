"""HyperFrames 渲染适配器：构造检查、预览和渲染命令。"""
from __future__ import annotations


def build_render_command(project_dir: str, output: str, workers: int = 2) -> dict[str, object]:
    """返回命令与工作目录；HyperFrames 通过 cwd 识别项目，不使用不存在的 --project 参数。"""
    return {
        "cwd": project_dir,
        "command": ["npx.cmd", "--yes", "hyperframes@0.7.5", "render", "--workers", str(workers), "--output", output],
    }


def build_check_commands() -> list[list[str]]:
    """正式渲染前依次执行三项质量检查。"""
    base = ["npx.cmd", "--yes", "hyperframes@0.7.5"]
    return [base + [name] for name in ("lint", "validate", "inspect")]
