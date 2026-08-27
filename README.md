# 中文知识视频工作流 Skill

这个 Skill 用来把一个中文主题、问题或口播稿，制作成一条竖屏知识科普视频。它适合做 AI Agent、RAG、Prompt、Workflow、Skill 等技术科普，也适合面试题讲解类短视频。

默认产物包括：

- 竖屏视频工程：1080×1920
- Edge TTS 中文旁白
- SRT 字幕文件
- ASS 样式字幕文件
- 有声无字幕 MP4
- 内嵌字幕 MP4
- 抖音竖封面 3:4
- 抖音横封面 4:3

## 一、工作流是什么

这个 Skill 不是单个 Prompt，而是一套完整工作流：

1. 根据主题和原始文案生成待确认口播稿和场景计划。
2. 用户确认文案后，生成中文 TTS 旁白。
3. 根据每个场景的真实语音时长同步画面时间轴。
4. 生成 SRT / ASS 字幕。
5. 生成 HyperFrames 暗色科技风视频工程。
6. 用户确认画面后，渲染无声视频。
7. 使用 FFmpeg 合成有声视频和内嵌字幕视频。
8. 顺路生成抖音竖封面和横封面。

## 二、最小输入配置

在你自己的视频项目目录里新建 `workflow-input.json`，例如：

```json
{
  "topic": "单 Agent 和多 Agent 的区别与联系",
  "target_duration": 180,
  "raw_text": "单 Agent 和多 Agent 有什么区别？先说结论：单 Agent 适合目标明确、职责集中的任务。多 Agent 更像分工明确的小团队。",
  "voice": "zh-CN-XiaoxiaoNeural",
  "speech_rate": "+50%",
  "visual_style": "dark-tech",
  "subtitle_enabled": true,
  "subtitle_font_size": 52,
  "subtitle_margin_bottom": 150,
  "cover_enabled": true,
  "cover_episode_label": "第 1 集",
  "cover_title": "单 Agent\n和多 Agent\n怎么选？",
  "cover_subtitle": "别为了炫技上多 Agent",
  "cover_hook": "先跑通，再拆分，再协作",
  "ffmpeg_bin": "ffmpeg",
  "ffprobe_bin": "ffprobe"
}
```

建议把每期视频单独放一个项目目录，例如：

```text
my-video-project/
  workflow-input.json
  output/
```

## 三、怎么运行

如果你是第一次使用，先把 [CODEX_SETUP_GUIDE.md](CODEX_SETUP_GUIDE.md) 发给 Codex，让它检查本机是否缺 Python、Edge TTS、Pillow、Node.js、HyperFrames、FFmpeg 和 FFprobe。环境确认后再继续。

### 1. 准备文案和场景计划

```powershell
python scripts/workflow.py prepare --config workflow-input.json --output output --overwrite
```

这一步只生成审核文件，不会生成音频或视频。

输出：

```text
output/content-plan.json
output/review-script.md
```

你需要打开 `output/review-script.md` 检查口播稿。如果确认没问题，把 `output/content-plan.json` 里的：

```json
"confirmed": false
```

改成：

```json
"confirmed": true
```

### 2. 生成旁白、字幕、画面工程和封面

```powershell
python scripts/workflow.py build --config workflow-input.json --output output
```

输出：

```text
output/narration.wav
output/subtitles.srt
output/subtitles.ass
output/composition/index.html
output/composition/scene-data.js
output/covers/cover-vertical-3x4.png
output/covers/cover-horizontal-4x3.png
```

这一步会停在画面确认点。你可以用 HyperFrames 预览或检查 `output/composition`。

### 3. 确认画面后渲染最终视频

```powershell
python scripts/workflow.py build --config workflow-input.json --output output --render
```

输出：

```text
output/explainer-silent.mp4
output/final-with-voice.mp4
output/final-with-subtitles.mp4
output/result-manifest.json
```

## 四、产物保存在哪

默认全部保存在你传入的 `--output` 目录里。

常用文件：

| 文件 | 说明 |
|---|---|
| `review-script.md` | 待人工审核的口播稿和场景稿 |
| `content-plan.json` | 结构化场景计划、真实时间轴和确认状态 |
| `narration.wav` | Edge TTS 生成的旁白 |
| `subtitles.srt` | 可导入剪映等工具的字幕 |
| `subtitles.ass` | 带字号、描边、位置的样式字幕 |
| `composition/` | HyperFrames 视频工程 |
| `explainer-silent.mp4` | 无声画面视频 |
| `final-with-voice.mp4` | 有旁白但无内嵌字幕的视频 |
| `final-with-subtitles.mp4` | 最终可发布视频，含旁白和内嵌字幕 |
| `covers/cover-vertical-3x4.png` | 抖音竖封面 |
| `covers/cover-horizontal-4x3.png` | 抖音横封面 |

## 五、怎么调整风格

### 1. 调整视频画面风格

默认模板在：

```text
assets/dark-tech-template/
```

主要文件：

```text
assets/dark-tech-template/DESIGN.md
assets/dark-tech-template/index.html
```

你可以改：

- 背景颜色
- 标题字号
- 信息卡样式
- 科技线条和光效
- 动画节奏
- 场景切换方式

注意：如果修改 HyperFrames 组合，需要重新检查布局，避免文字溢出或被截断。

### 2. 调整字幕样式

在 `workflow-input.json` 里改：

```json
"subtitle_font_size": 52,
"subtitle_margin_bottom": 150
```

如果想改字幕描边、字体、颜色，需要改：

```text
scripts/generate_subtitles.py
```

### 3. 调整封面风格

封面脚本在：

```text
scripts/generate_covers.py
```

可配置字段：

```json
"cover_enabled": true,
"cover_episode_label": "第 1 集",
"cover_title": "单 Agent\n和多 Agent\n怎么选？",
"cover_subtitle": "别为了炫技上多 Agent",
"cover_hook": "先跑通，再拆分，再协作"
```

`cover_title` 推荐手动加 `\n` 换行，避免英文单词被自动拆开。

如果你有 image2、Midjourney、Stable Diffusion 或其他工具生成的无字底图，可以写入：

```json
"cover_vertical_background": "path/to/vertical-bg.png",
"cover_horizontal_background": "path/to/horizontal-bg.png"
```

脚本会使用这些底图，并叠加准确中文标题。

## 六、怎么和 Codex 配合使用

推荐流程：

1. 给 Codex：主题、原始文案、期望时长。
2. Codex 先输出优化后的口播稿和场景计划。
3. 你确认文案。
4. Codex 生成 TTS、字幕、HyperFrames 工程、封面。
5. 你确认画面。
6. Codex 渲染并合成最终 MP4。

如果 Codex 环境支持 image2/imagegen，可以让 Codex 先生成两张无字封面底图，再写入 `workflow-input.json` 的封面背景字段。

## 七、开源注意事项

建议不要提交：

- `.venv/`
- `output/`
- `*.mp4`
- `*.wav`
- `.env`
- 包含私有文案、客户信息或本地路径的配置文件

当前 `.gitignore` 已默认排除这些内容。

## 八、给新用户的环境准备

- 面向普通用户的本地依赖说明见 [LOCAL_SETUP.md](LOCAL_SETUP.md)。
- 面向 Codex 的自动排查和安装指导见 [CODEX_SETUP_GUIDE.md](CODEX_SETUP_GUIDE.md)。
