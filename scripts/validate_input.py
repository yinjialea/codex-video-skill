"""输入校验：在联网、TTS 或视频渲染前集中报告配置问题。"""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = ("topic", "raw_text", "target_duration")


def validate_config(config: dict[str, Any], check_tools: bool = False) -> list[str]:
    """返回全部错误，而不是发现第一项错误就停止。"""
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if config.get(field) in (None, ""):
            errors.append(f"缺少必填字段：{field}")
    try:
        if float(config.get("target_duration", 0)) <= 0:
            errors.append("target_duration 必须大于 0")
    except (TypeError, ValueError):
        errors.append("target_duration 必须是数字")
    rate = str(config.get("speech_rate", "+50%"))
    if not re.fullmatch(r"[+-]\d{1,3}%", rate):
        errors.append("speech_rate 必须使用 +50% 或 -10% 格式")
    if check_tools:
        for field, default in (("ffmpeg_bin", "ffmpeg"), ("ffprobe_bin", "ffprobe")):
            value = str(config.get(field, default))
            if not Path(value).exists() and shutil.which(value) is None:
                errors.append(f"找不到 {field}：{value}")
    return errors
