"""时间轴同步：以每段旁白的实测时长计算场景起止点。"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def apply_durations(scenes: list[dict[str, Any]], durations: list[float]) -> list[dict[str, Any]]:
    """返回带 start/end/duration 的场景副本，避免修改调用方原数据。"""
    if len(scenes) != len(durations):
        raise ValueError("场景数量和音频时长数量必须一致")
    if any(float(value) <= 0 for value in durations):
        raise ValueError("每个音频时长都必须大于 0")
    result, cursor = deepcopy(scenes), 0.0
    for scene, value in zip(result, durations):
        seconds = round(float(value), 3)
        scene["start"] = round(cursor, 3)
        cursor = round(cursor + seconds, 3)
        scene["end"] = cursor
        scene["duration"] = seconds
    return result
