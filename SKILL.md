---
name: knowledge-video-workflow-skill
description: Use when a user wants to turn a Chinese topic, outline, question, or narration script into a vertical knowledge-sharing video with script review, Edge TTS voiceover, timed subtitles, HyperFrames visuals, FFmpeg composition, Douyin cover images, and explicit confirmation gates.
---

# 中文知识视频工作流

把本 Skill 作为唯一入口。文案、旁白、字幕、画面和封面必须来自同一份已确认内容；画面切换必须使用逐场景旁白的真实时长。

**REQUIRED SUB-SKILL:** 设计或修改视频组合时使用 `hyperframes:hyperframes`。

**REQUIRED SUB-SKILL:** 检查、预览或渲染组合时使用 `hyperframes:hyperframes-cli`。

若子 Skill 未安装但 HyperFrames CLI 可用，读取 `assets/dark-tech-template/DESIGN.md` 并进入兼容模式。若 CLI 也不可用，停在渲染前并提示安装。

## 输入和确认

至少收集主题、原始文案或要点、期望时长。默认采用 1080×1920、暗色科技风、晓晓音色、统一 `+50%`、SRT/ASS、内嵌字幕、竖封面 3:4 和横封面 4:3。字段见 `references/input-schema.md`。

封面默认由本地 Pillow 脚本生成，确保中文标题准确。若当前 Codex 会话可用 `imagegen`/image2，可先生成无字暗色科技底图，再把路径写入 `cover_vertical_background` 和 `cover_horizontal_background`，由脚本叠加准确中文标题。

依次执行四个确认点：

1. 需求确认：主题、时长、语速、音色、风格、字幕和输出。
2. 文案确认：完整口播稿、预计时长、修改摘要和场景提纲。确认前禁止 TTS。
3. 画面确认：场景对应关系、关键帧或预览、字幕样式和真实时间轴。确认前禁止正式长视频渲染。
4. 成品验收：两个 MP4、旁白、SRT、ASS、竖封面、横封面、媒体信息和文件路径。

只有用户明确说文案和画面均已确认时，才允许 `all --yes`。

## 执行命令

准备文案：

```powershell
python scripts/workflow.py prepare --config workflow-input.json --output output
```

审核 `review-script.md`，确认后将 `content-plan.json` 的 `confirmed` 改为 `true`。

生成旁白、字幕和组合并停在画面确认点：

```powershell
python scripts/workflow.py build --config workflow-input.json --output output
```

此步骤也会生成 `output/covers/cover-vertical-3x4.png` 和 `output/covers/cover-horizontal-4x3.png`。

画面确认后正式渲染：

```powershell
python scripts/workflow.py build --config workflow-input.json --output output --render
```

完整步骤见 `references/workflow-steps.md`，失败时见 `references/troubleshooting.md`。

## 重跑规则

- 仅字幕样式变化：重新生成 ASS 和 FFmpeg 合成。
- 仅画面变化：从 HyperFrames 检查和渲染开始。
- 文案、音色或语速变化：重新执行 TTS、时间轴、字幕、画面和合成。

## 完成标准

验证最终 MP4 含 H.264 和 AAC、分辨率 1080×1920、音视频时长一致、字幕存在，并确认场景边界等于逐场景旁白累计时长。验证失败时报告真实状态，不得标记完成。
