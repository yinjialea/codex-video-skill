"""字幕生成：从时间事件或场景文本生成 SRT 和 ASS。"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Cue:
    """单条字幕的开始时间、结束时间和文本。"""
    start: float
    end: float
    text: str


def proportional_cues(text: str, start: float, duration: float) -> list[Cue]:
    """TTS 没有时间事件时，按句子字符权重分配真实场景时长。"""
    sentences = [part.strip() for part in re.split(r"(?<=[。！？；])", text) if part.strip()]
    parts: list[str] = []
    # 一条字幕最多 36 个字符，优先在逗号、顿号或冒号处切开，且不丢弃尾部文字。
    for sentence in sentences:
        remaining = sentence
        while len(remaining) > 36:
            cut = 36
            candidates = [remaining.rfind(mark, 16, 37) for mark in ("，", "、", "：", ",", ":")]
            punctuation_cut = max(candidates)
            if punctuation_cut >= 16:
                cut = punctuation_cut + 1
            parts.append(remaining[:cut])
            remaining = remaining[cut:]
        if remaining:
            parts.append(remaining)
    weights = [max(1, len(re.sub(r"\s", "", part))) for part in parts]
    total, cursor, cues = sum(weights) or 1, float(start), []
    for part, weight in zip(parts, weights):
        length = duration * weight / total
        cues.append(Cue(round(cursor, 3), round(cursor + length, 3), part))
        cursor += length
    return cues


def _ass_time(seconds: float) -> str:
    centis = round(max(0, seconds) * 100)
    hours, rem = divmod(centis, 360000)
    minutes, rem = divmod(rem, 6000)
    secs, part = divmod(rem, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{part:02d}"


def _srt_time(seconds: float) -> str:
    millis = round(max(0, seconds) * 1000)
    hours, rem = divmod(millis, 3600000)
    minutes, rem = divmod(rem, 60000)
    secs, part = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{part:03d}"


def wrap_text(text: str, line_limit: int = 18) -> str:
    """把字幕限制为最多两行，防止竖屏画面横向溢出。"""
    compact = re.sub(r"\s+", " ", text.strip())
    return "\\N".join([compact[:line_limit], compact[line_limit:line_limit * 2]]).rstrip("\\N")


def build_ass(cues: list[Cue], font_size: int = 52, margin_bottom: int = 150) -> str:
    """生成适合暗色竖屏视频的大号白字黑描边 ASS。"""
    header = f"""[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\nStyle: Default,SimHei,{font_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,4,2,2,70,70,{margin_bottom},1\n\n[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"""
    return header + "\n".join(f"Dialogue: 0,{_ass_time(c.start)},{_ass_time(c.end)},Default,,0,0,0,,{wrap_text(c.text)}" for c in cues) + "\n"


def build_srt(cues: list[Cue]) -> str:
    """生成剪映等软件可直接导入的 SRT。"""
    blocks = []
    for index, cue in enumerate(cues, 1):
        text = wrap_text(cue.text).replace("\\N", "\n")
        blocks.append(f"{index}\n{_srt_time(cue.start)} --> {_srt_time(cue.end)}\n{text}")
    return "\n\n".join(blocks) + "\n"
