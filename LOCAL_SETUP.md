# 本地环境准备指南

这份文档说明如何在本地准备中文知识视频生成环境。整体依赖包括：

如果你完全不熟悉本地环境配置，建议优先把 [CODEX_SETUP_GUIDE.md](CODEX_SETUP_GUIDE.md) 发给 Codex，让 Codex 先帮你检查缺什么、该安装什么，再回到本文查看细节。

- Python
- Edge TTS
- Pillow
- FFmpeg / FFprobe
- HyperFrames by HeyGen / HyperFrames CLI
- 可选：image2/imagegen，用于生成更好看的无字封面底图

## 一、安装 Python 依赖

建议使用 Python 3.10 或更高版本。

在 Skill 根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

`requirements.txt` 里包含：

```text
edge-tts
Pillow
```

说明：

- `edge-tts` 用于本地生成中文旁白。
- `Pillow` 用于生成抖音竖封面和横封面，并绘制准确中文标题。

## 二、Edge TTS 是否需要花钱

当前工作流使用的是 `edge-tts` Python 包。它调用 Microsoft Edge 的在线语音能力，通常不需要你单独注册云服务或填写 API Key。

注意：

- 需要联网。
- 不是 Azure Speech 的正式企业 API。
- 如果微软侧服务策略变化，可能会不可用。
- 商用前建议自行确认对应服务条款。

常用中文音色：

```text
zh-CN-XiaoxiaoNeural
zh-CN-YunxiNeural
zh-CN-YunjianNeural
zh-CN-XiaoyiNeural
```

## 三、安装 FFmpeg 和 FFprobe

FFmpeg 用于：

- 检查音视频时长
- 合成旁白和视频
- 烧录 ASS 字幕
- 导出最终 MP4

Windows 推荐下载已编译版本，而不是源码包。

推荐来源：

```text
https://www.gyan.dev/ffmpeg/builds/
```

下载类似：

```text
ffmpeg-git-essentials.7z
```

解压后找到：

```text
ffmpeg-xxxx-essentials_build/bin/ffmpeg.exe
ffmpeg-xxxx-essentials_build/bin/ffprobe.exe
```

你可以把 `bin` 目录加入系统或用户 `Path`，也可以在 `workflow-input.json` 里写完整路径：

```json
"ffmpeg_bin": "E:/tools/ffmpeg/ffmpeg-xxxx-essentials_build/bin/ffmpeg.exe",
"ffprobe_bin": "E:/tools/ffmpeg/ffmpeg-xxxx-essentials_build/bin/ffprobe.exe"
```

验证：

```powershell
ffmpeg -version
ffprobe -version
```

能看到版本信息即可。

## 四、安装或准备 HyperFrames

HyperFrames 用于生成和渲染 HTML 动画视频。

如果你在 Codex 里安装了 `HyperFrames by HeyGen` 插件，Codex 可以调用相关 Skill 和 CLI 辅助生成、检查、渲染视频。

普通本地命令一般是：

```powershell
npx hyperframes lint
npx hyperframes validate
npx hyperframes inspect
npx hyperframes preview
npx hyperframes render --output output/explainer-silent.mp4 --fps 30 --quality high
```

如果网络或 npm 缓存有问题，可以先确认：

```powershell
node -v
npm -v
npx hyperframes --help
```

HyperFrames 渲染时会启动浏览器/Chrome，因此在某些沙箱或权限环境下可能需要额外授权。

## 五、字幕是怎么生成的

本工作流会生成两类字幕：

```text
output/subtitles.srt
output/subtitles.ass
```

区别：

- `SRT`：通用字幕文件，可以导入剪映、PR、达芬奇等工具。
- `ASS`：带样式的字幕文件，支持字号、描边、边距等，适合直接用 FFmpeg 烧录到视频里。

最终发布视频：

```text
output/final-with-subtitles.mp4
```

里面已经内嵌字幕，不需要再去剪映做 AI 字幕。

如果想只拿字幕文件去剪映用，使用：

```text
output/subtitles.srt
```

## 六、封面是怎么生成的

默认会生成：

```text
output/covers/cover-vertical-3x4.png
output/covers/cover-horizontal-4x3.png
```

竖封面适合抖音的竖切面，横封面适合横切面。

封面生成分两层：

1. 背景层：可以用 image2/imagegen 生成，也可以使用本地脚本自动生成兜底背景。
2. 文字层：始终由 Pillow 本地绘制，保证中文标题准确。

如果你用 image2 生成了无字底图，把路径写进配置：

```json
"cover_vertical_background": "E:/covers/vertical-bg.png",
"cover_horizontal_background": "E:/covers/horizontal-bg.png"
```

如果不填，脚本也会自动生成暗色科技风兜底封面。

## 七、推荐目录结构

```text
knowledge-video-workflow-skill/
  SKILL.md
  README.md
  LOCAL_SETUP.md
  requirements.txt
  scripts/
  assets/
  references/

my-video-project/
  workflow-input.json
  output/
    review-script.md
    content-plan.json
    narration.wav
    subtitles.srt
    subtitles.ass
    composition/
    covers/
    final-with-voice.mp4
    final-with-subtitles.mp4
```

## 八、常见问题

### 1. FFmpeg 找不到

现象：

```text
FFmpeg binary not found
```

解决：

- 把 FFmpeg 的 `bin` 目录加入 Path；或
- 在 `workflow-input.json` 里写 `ffmpeg.exe` 和 `ffprobe.exe` 的完整路径。

### 2. TTS 失败

可能原因：

- 没联网。
- `edge-tts` 没安装。
- 音色名称写错。

验证：

```powershell
python -m pip show edge-tts
```

### 3. 字幕位置不合适

修改：

```json
"subtitle_font_size": 52,
"subtitle_margin_bottom": 150
```

数值越大，字幕越大；`subtitle_margin_bottom` 越大，字幕越往上。

### 4. 封面标题换行不好看

在 `cover_title` 里手动写换行：

```json
"cover_title": "Prompt / Skill\n版本管理\n动态插拔"
```

这样可以避免英文词被拆成奇怪的两半。

### 5. HyperFrames 预览可以，导出失败

优先检查：

```powershell
npx hyperframes doctor
ffmpeg -version
ffprobe -version
```

如果路径里有中文或空格，建议优先在配置里写 FFmpeg 完整路径，避免环境变量被错误解析。
