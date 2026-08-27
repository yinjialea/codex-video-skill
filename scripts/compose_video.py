"""FFmpeg 合成适配器：生成有声版和内嵌字幕版命令。"""
from __future__ import annotations

from typing import Any


def build_voice_command(config: dict[str, Any]) -> list[str]:
    """视频流直接复制，只编码 AAC 音轨，速度快且不损失画质。"""
    return [str(config["ffmpeg_bin"]), "-y", "-i", str(config["video"]), "-i", str(config["audio"]), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", str(config["output"])]


def build_subtitle_command(config: dict[str, Any]) -> list[str]:
    """烧录 ASS 必须重新编码视频，同时映射独立旁白音轨。"""
    subtitle_filter = f"ass={config['ass']}:fontsdir={config.get('fonts_dir', 'assets')}"
    return [str(config["ffmpeg_bin"]), "-y", "-i", str(config["video"]), "-i", str(config["audio"]), "-vf", subtitle_filter, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", str(config["output"])]
