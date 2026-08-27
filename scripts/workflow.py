"""知识视频工作流总入口：组织 prepare、build 和 all 三种模式。"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from common import WorkflowError, read_json, run_command, write_json
from compose_video import build_subtitle_command, build_voice_command
from generate_covers import generate_covers
from generate_subtitles import build_ass, build_srt, proportional_cues
from generate_voice import generate_narration
from plan_content import build_plan
from render_video import build_check_commands, build_render_command
from sync_timeline import apply_durations
from validate_input import validate_config


SKILL_DIR = Path(__file__).resolve().parents[1]


def _ensure_writable(output_dir: Path, overwrite: bool) -> None:
    """默认保护已有产物；只有 --overwrite 才允许重建。"""
    if output_dir.exists() and any(output_dir.iterdir()) and not overwrite:
        raise WorkflowError(f"输出目录非空：{output_dir}；如需覆盖请添加 --overwrite")
    output_dir.mkdir(parents=True, exist_ok=True)


def prepare_workflow(config: dict[str, Any], output_dir: Path, overwrite: bool = False) -> dict[str, Any]:
    """生成待确认文案和场景计划，不联网、不生成语音、不渲染。"""
    errors = validate_config(config)
    if errors:
        raise WorkflowError("配置存在问题：\n- " + "\n- ".join(errors))
    _ensure_writable(output_dir, overwrite)
    plan = build_plan(str(config["topic"]), str(config["raw_text"]), float(config["target_duration"]))
    write_json(output_dir / "content-plan.json", plan)
    review = [f"# {plan['topic']}\n", f"预计口播时长：{plan['estimated_duration']} 秒\n", "## 待确认口播稿\n"]
    review.extend(f"### 场景 {index}\n\n{scene['narration']}\n" for index, scene in enumerate(plan["scenes"], 1))
    review.append("\n确认后，请把 content-plan.json 中的 confirmed 改为 true，再执行 build。\n")
    (output_dir / "review-script.md").write_text("\n".join(review), encoding="utf-8")
    return {"status": "awaiting_script_confirmation", "plan": str(output_dir / "content-plan.json")}


def require_confirmed_plan(path: Path) -> dict[str, Any]:
    """Build 的硬确认关口：未确认文案不能生成正式旁白。"""
    plan = read_json(path)
    if plan.get("confirmed") is not True:
        raise WorkflowError("文案尚未确认：请检查 review-script.md，并把 content-plan.json 的 confirmed 改为 true")
    return plan


def _create_cues(scenes: list[dict[str, Any]]) -> list:
    """按真实场景时长生成连续字幕提示块。"""
    cues = []
    for scene in scenes:
        cues.extend(proportional_cues(scene["narration"], scene["start"], scene["duration"]))
    return cues


def _write_composition(plan: dict[str, Any], output_dir: Path) -> Path:
    """把主题和真实时间轴写入可复用的 HyperFrames 暗色科技模板。"""
    template = SKILL_DIR / "assets" / "dark-tech-template" / "index.html"
    composition = output_dir / "composition"
    composition.mkdir(parents=True, exist_ok=True)
    duration = plan["scenes"][-1]["end"]
    html = template.read_text(encoding="utf-8").replace("__DURATION__", str(duration)).replace("__TOPIC__", plan["topic"])
    (composition / "index.html").write_text(html, encoding="utf-8")
    data = "window.__SCENE_DATA__ = " + json.dumps(plan["scenes"], ensure_ascii=False, indent=2) + ";\n"
    (composition / "scene-data.js").write_text(data, encoding="utf-8")
    return composition


def build_workflow(config: dict[str, Any], output_dir: Path, render: bool = False) -> dict[str, Any]:
    """从确认计划生成旁白、字幕、组合；render=True 时继续输出 MP4。"""
    plan = require_confirmed_plan(output_dir / "content-plan.json")
    narration, durations = generate_narration(plan, config, output_dir)
    plan["scenes"] = apply_durations(plan["scenes"], durations)
    plan["actual_duration"] = plan["scenes"][-1]["end"]
    write_json(output_dir / "content-plan.json", plan)
    cues = _create_cues(plan["scenes"])
    (output_dir / "subtitles.srt").write_text(build_srt(cues), encoding="utf-8-sig")
    (output_dir / "subtitles.ass").write_text(build_ass(cues, int(config.get("subtitle_font_size", 52)), int(config.get("subtitle_margin_bottom", 150))), encoding="utf-8-sig")
    composition = _write_composition(plan, output_dir)
    covers = generate_covers(config, output_dir)
    result = {"status": "awaiting_visual_confirmation", "duration": plan["actual_duration"], "composition": str(composition), **covers}
    if not render:
        write_json(output_dir / "result-manifest.json", result)
        return result

    # 画面确认后才执行正式检查和长视频渲染。
    logs = output_dir / "logs"
    for command in build_check_commands():
        run_command(command, cwd=composition, log_path=logs / f"{command[-1]}.log")
    silent = output_dir / "explainer-silent.mp4"
    invocation = build_render_command(str(composition), str(silent))
    run_command(invocation["command"], cwd=Path(invocation["cwd"]), log_path=logs / "render.log")
    voice_output = output_dir / "final-with-voice.mp4"
    subtitle_output = output_dir / "final-with-subtitles.mp4"
    run_command(build_voice_command({"ffmpeg_bin": config.get("ffmpeg_bin", "ffmpeg"), "video": silent, "audio": narration, "output": voice_output}))
    run_command(build_subtitle_command({"ffmpeg_bin": config.get("ffmpeg_bin", "ffmpeg"), "video": silent, "audio": narration, "ass": output_dir / "subtitles.ass", "fonts_dir": composition, "output": subtitle_output}))
    result.update({"status": "completed", "voice_video": str(voice_output), "subtitle_video": str(subtitle_output)})
    write_json(output_dir / "result-manifest.json", result)
    return result


def main() -> None:
    """解析命令行，并清晰区分准备、构建预览和正式渲染。"""
    parser = argparse.ArgumentParser(description="把中文文案制作成知识科普视频。")
    parser.add_argument("mode", choices=("prepare", "build", "all"))
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--render", action="store_true", help="画面已确认，执行正式渲染和合成")
    parser.add_argument("--yes", action="store_true", help="文案和画面均已确认，允许自动执行")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    config, output = read_json(Path(args.config)), Path(args.output).resolve()
    if args.mode == "prepare":
        result = prepare_workflow(config, output, args.overwrite)
    elif args.mode == "build":
        result = build_workflow(config, output, args.render)
    else:
        prepare_workflow(config, output, args.overwrite)
        plan_path = output / "content-plan.json"
        plan = read_json(plan_path)
        if not args.yes:
            raise WorkflowError("all 模式需要 --yes，表示文案和画面已经确认")
        plan["confirmed"] = True
        write_json(plan_path, plan)
        result = build_workflow(config, output, render=True)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except WorkflowError as exc:
        raise SystemExit(f"工作流停止：{exc}")
