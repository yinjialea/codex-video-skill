"""文案规划：估算口播时长，并把确认后的文案变成有序场景。"""
from __future__ import annotations

import re
from typing import Any


def estimate_duration(text: str, chars_per_second: float = 4.2) -> float:
    """按中文字符、英文词和数字组估算口播时长。"""
    cjk = len(re.findall(r"[\u3400-\u9fff]", text))
    words = len(re.findall(r"[A-Za-z]+", text))
    numbers = len(re.findall(r"\d+(?:\.\d+)?", text))
    return round(max(0.5, (cjk + words * 2.2 + numbers * 1.2) / chars_per_second), 2)


def split_sections(text: str) -> list[str]:
    """优先用空行作为场景边界；没有空行时按句号等标点分段。"""
    normalized = text.replace("\r\n", "\n").strip()
    paragraphs = [item.strip() for item in re.split(r"\n\s*\n", normalized) if item.strip()]
    if len(paragraphs) > 1:
        return paragraphs
    return [item.strip() for item in re.split(r"(?<=[。！？；])", normalized) if item.strip()]


def build_plan(topic: str, raw_text: str, target_duration: float) -> dict[str, Any]:
    """生成可供人工审核、TTS 和画面模板共同使用的内容计划。"""
    sections = split_sections(raw_text)
    scenes = []
    for index, narration in enumerate(sections, 1):
        scenes.append({
            "id": f"scene-{index:02d}",
            "title": narration.split("。", 1)[0][:24],
            "narration": narration,
            "estimated_duration": estimate_duration(narration),
            "visual_keywords": [topic, f"场景 {index}", "信息卡片"],
        })
    return {
        "topic": topic.strip(),
        "target_duration": float(target_duration),
        "estimated_duration": round(sum(scene["estimated_duration"] for scene in scenes), 2),
        "confirmed": False,
        "scenes": scenes,
    }
