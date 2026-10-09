"""旁白生成：逐场景调用 Edge TTS，并用 FFmpeg 统一为 WAV 后拼接。"""
from __future__ import annotations

import asyncio
import os
import tempfile
import time
from pathlib import Path
from typing import Any

from common import WorkflowError, probe_duration, run_command


async def _save_edge_tts(text: str, output: Path, voice: str, rate: str) -> None:
    """延迟导入 edge_tts，让不需要 TTS 的 prepare 模式无需安装依赖。"""
    try:
        import edge_tts
    except ImportError as exc:
        raise WorkflowError("缺少 edge-tts，请执行：python -m pip install edge-tts") from exc
    # edge-tts 使用 aiohttp，默认不会自动继承所有系统代理设置。
    # 显式传入进程级代理，方便受限网络环境通过 HTTP(S)_PROXY 生成语音。
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    await edge_tts.Communicate(text, voice=voice, rate=rate, proxy=proxy).save(str(output))


def _save_edge_tts_with_retry(text: str, output: Path, voice: str, rate: str, retries: int = 3) -> None:
    """Edge TTS 偶尔会返回空音频；这里做短重试，避免整条视频被瞬时网络抖动打断。"""
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            asyncio.run(_save_edge_tts(text, output, voice, rate))
            if output.exists() and output.stat().st_size > 0:
                return
        except Exception as exc:  # noqa: BLE001 - 这里需要保留 edge-tts 的原始异常用于最终报错
            last_error = exc
        if attempt < retries:
            time.sleep(1.5 * attempt)
    raise WorkflowError(f"Edge TTS 生成失败，已重试 {retries} 次：{last_error}") from last_error


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
            _save_edge_tts_with_retry(scene["narration"], mp3, voice, rate)
            run_command([ffmpeg, "-y", "-loglevel", "error", "-i", str(mp3), "-ar", "24000", "-ac", "1", str(wav)])
            durations.append(round(probe_duration(ffprobe, wav), 3))
            wavs.append(wav)
        concat = temp / "concat.txt"
        concat.write_text("\n".join(f"file '{path.as_posix()}'" for path in wavs), encoding="utf-8")
        run_command([ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-c:a", "pcm_s16le", str(narration)])
    return narration, durations
