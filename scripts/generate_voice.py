"""旁白生成：逐场景调用 Edge TTS，并用 FFmpeg 统一为 WAV 后拼接。"""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any

from common import WorkflowError, probe_duration, run_command


async def _save_edge_tts(text: str, output: Path, voice: str, rate: str) -> None:
    """延迟导入 edge_tts，让不需要 TTS 的 prepare 模式无需安装依赖。"""
    try:
        import edge_tts
    except ImportError as exc:
        raise WorkflowError("缺少 edge-tts，请执行：python -m pip install edge-tts") from exc
    await edge_tts.Communicate(text, voice=voice, rate=rate).save(str(output))


def generate_narration(plan: dict[str, Any], config: dict[str, Any], output_dir: Path) -> tuple[Path, list[float]]:
    """生成完整旁白并返回文件路径和逐场景真实时长。"""
    ffmpeg = str(config.get("ffmpeg_bin", "ffmpeg"))
    ffprobe = str(config.get("ffprobe_bin", "ffprobe"))
    voice = str(config.get("voice", "zh-CN-XiaoxiaoNeural"))
    rate = str(config.get("speech_rate", "+50%"))
    output_dir.mkdir(parents=True, exist_ok=True)
    narration = output_dir / "narration.wav"

    with tempfile.TemporaryDirectory() as temp_name:
        temp = Path(temp_name)
        wavs, durations = [], []
        # 每个场景独立生成，便于用真实时长同步画面切换。
        for index, scene in enumerate(plan["scenes"]):
            mp3, wav = temp / f"scene-{index:02d}.mp3", temp / f"scene-{index:02d}.wav"
            asyncio.run(_save_edge_tts(scene["narration"], mp3, voice, rate))
            run_command([ffmpeg, "-y", "-loglevel", "error", "-i", str(mp3), "-ar", "24000", "-ac", "1", str(wav)])
            durations.append(round(probe_duration(ffprobe, wav), 3))
            wavs.append(wav)
        concat = temp / "concat.txt"
        concat.write_text("\n".join(f"file '{path.as_posix()}'" for path in wavs), encoding="utf-8")
        run_command([ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-c:a", "pcm_s16le", str(narration)])
    return narration, durations
