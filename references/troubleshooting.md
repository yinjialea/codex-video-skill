# 常见问题

## 找不到 FFmpeg

将 FFmpeg 的 `bin` 目录加入 PATH，或在 JSON 中填写 `ffmpeg.exe` 和 `ffprobe.exe` 完整路径。

## Edge TTS 失败

确认网络可用并执行 `python -m pip install edge-tts`。

## HyperFrames 不可用

确认 Node.js 与 npm 可用，运行 `npx --yes hyperframes@0.7.5 info`。子 Skill 缺失可进入模板兼容模式；CLI 缺失则不能渲染。

## 画面提前切换

检查 `content-plan.json` 的 `start/end/duration`。切换点必须等于当前场景的真实 `end`。

## 字幕不同步

TTS 没有返回时间事件时，字幕按字符权重估算。可导入 SRT 微调，或后续接入 ASR 获取词级时间戳。

## 封面标题换行不好看

在 JSON 的 `cover_title` 中手动加入 `\n` 控制换行，例如 `Prompt / Skill\n版本管理\n动态插拔`。封面文字由本地 Pillow 绘制，优先保证标题准确。

## 封面底图不够好看

本地脚本会生成兜底暗色科技背景。若需要更强视觉效果，可用 image2/imagegen、Midjourney 或 Stable Diffusion 生成无字底图，再把路径写入 `cover_vertical_background` 和 `cover_horizontal_background`。
