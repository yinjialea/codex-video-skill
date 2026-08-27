# 给 Codex 的安装与运行检查指南

这份文档是给“第一次使用这个 Skill 的人”和“他的 Codex”看的。

使用方式很简单：把整个 `knowledge-video-workflow-skill/` 放进一个项目目录或 Codex Skills 目录，然后把这份文档发给 Codex，让 Codex 按下面的检查清单判断本机缺什么、怎么安装、怎么运行、怎么按你的需求改脚本。

## 0. 先告诉 Codex 你要做什么

可以直接把下面这段话发给 Codex：

```text
请阅读当前项目里的 knowledge-video-workflow-skill/CODEX_SETUP_GUIDE.md。
你需要先检查我的本机环境是否满足要求，包括 Python、pip、edge-tts、Pillow、Node.js、npm/npx、HyperFrames、FFmpeg、FFprobe，以及 Codex 是否有 HyperFrames by HeyGen 插件或可用的 HyperFrames CLI。

如果缺依赖，请告诉我缺什么、为什么需要、给我对应安装命令。
不要直接假设环境可用。

环境确认后，请使用 knowledge-video-workflow-skill 帮我把一个中文主题和文案制作成竖屏知识科普视频。
默认使用暗色科技风、Edge TTS 中文旁白、SRT/ASS 字幕、内嵌字幕 MP4、抖音竖封面 3:4、抖音横封面 4:3。

如果我没有要求改风格，就使用项目默认风格。
如果我要改风格，请先告诉我要改哪些文件和字段，再帮我修改。
```

## 1. Codex 需要先检查什么

请 Codex 在项目根目录或 Skill 根目录执行这些检查。

### 1.1 检查 Python

```powershell
python --version
python -m pip --version
```

要求：

- 推荐 Python 3.10 或更高。
- `pip` 必须可用。

如果失败，让用户先安装 Python，并勾选 `Add Python to PATH`。

### 1.2 检查 Python 依赖

```powershell
python -m pip show edge-tts
python -m pip show Pillow
```

如果缺少，执行：

```powershell
python -m pip install -r requirements.txt
```

如果用户不想使用虚拟环境，可以直接装到当前 Python；如果希望项目隔离，使用：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

依赖说明：

- `edge-tts`：生成中文旁白。
- `Pillow`：生成抖音竖封面和横封面，并绘制准确中文标题。

### 1.3 检查 FFmpeg / FFprobe

```powershell
ffmpeg -version
ffprobe -version
```

如果不可用，说明用户还没装 FFmpeg，或者没把 FFmpeg 的 `bin` 目录加入 `Path`。

Windows 推荐：

1. 打开 `https://www.gyan.dev/ffmpeg/builds/`
2. 下载 `ffmpeg-git-essentials.7z`
3. 解压
4. 找到：

```text
ffmpeg-xxxx-essentials_build/bin/ffmpeg.exe
ffmpeg-xxxx-essentials_build/bin/ffprobe.exe
```

可以二选一：

方案 A：把 `bin` 目录加入系统或用户 `Path`。

方案 B：在 `workflow-input.json` 里写完整路径：

```json
"ffmpeg_bin": "D:/tools/ffmpeg/bin/ffmpeg.exe",
"ffprobe_bin": "D:/tools/ffmpeg/bin/ffprobe.exe"
```

注意：路径可以有中文，但如果工具报错，优先建议用户把 FFmpeg 放到英文路径，例如：

```text
D:/tools/ffmpeg/
E:/tools/ffmpeg/
```

### 1.4 检查 Node.js / npm / npx

HyperFrames 依赖 Node.js 环境。

```powershell
node -v
npm -v
npx --version
```

要求：

- 推荐 Node.js 22 或更高。
- `npx` 必须可用。

如果不可用，让用户安装 Node.js LTS，或用 nvm 管理 Node.js。

### 1.5 检查 HyperFrames

这个工作流的视频画面由 HyperFrames 渲染。

优先方式：Codex 安装并启用 `HyperFrames by HeyGen` 插件。

如果用户在 Codex 里使用插件市场：

1. 打开 Codex / ChatGPT 的插件或连接器管理入口。
2. 搜索 `HyperFrames by HeyGen`。
3. 安装或启用该插件。
4. 回到任务里，明确告诉 Codex：使用 `HyperFrames by HeyGen` 或 `$hyperframes`。

如果用户不知道怎么装，让他直接对 Codex 说：

```text
请检查我当前 Codex 是否安装了 HyperFrames by HeyGen 插件。
如果没有，请帮我查找并指导我安装。
如果插件不可用，请检查是否可以通过 npx hyperframes 使用 HyperFrames CLI。
```

备用方式：本地可直接使用 HyperFrames CLI。

```powershell
npx hyperframes --help
npx hyperframes doctor
```

如果本机 npm 网络不稳定，也可以指定版本：

```powershell
npx --yes hyperframes@0.7.5 --help
```

说明：

- `HyperFrames by HeyGen` 插件给 Codex 提供视频组合、预览、检查、渲染相关能力。
- `npx hyperframes` 是本地命令行方式。
- 这个 Skill 的 Python 脚本会生成 `output/composition/`，最终仍需要 HyperFrames 把 HTML 画面渲染成 MP4。

### 1.6 检查浏览器/权限

HyperFrames 渲染时会启动浏览器或 Headless Chrome。

如果出现：

```text
spawn EPERM
```

通常是沙箱或权限限制。Codex 应该向用户申请允许启动浏览器/渲染命令，而不是直接放弃。

### 1.7 检查 image2/imagegen

image2/imagegen 不是必需项。

它只用于生成更好看的“无字封面底图”。封面标题文字仍然由本地 Pillow 绘制，避免中文错字。

如果 Codex 当前支持 image2/imagegen，可以这样做：

1. 先生成竖版 3:4 无字封面底图。
2. 再生成横版 4:3 无字封面底图。
3. 把底图路径写入：

```json
"cover_vertical_background": "path/to/vertical-bg.png",
"cover_horizontal_background": "path/to/horizontal-bg.png"
```

如果没有 image2/imagegen，也没关系。`scripts/generate_covers.py` 会用 Pillow 生成本地暗色科技兜底封面。

## 2. 环境通过后怎么运行

假设你已经在 Skill 根目录。

### 2.1 准备一个项目目录

建议每条视频一个目录：

```text
my-video-project/
  workflow-input.json
  output/
```

在 `my-video-project/` 里新建 `workflow-input.json`，字段可以参考本文第 7 节的 30 秒测试 JSON。

### 2.2 第一步：生成待确认文案

```powershell
python scripts/workflow.py prepare --config my-video-project/workflow-input.json --output my-video-project/output --overwrite
```

输出：

```text
my-video-project/output/review-script.md
my-video-project/output/content-plan.json
```

让用户审核 `review-script.md`。

确认后，把 `content-plan.json` 里的：

```json
"confirmed": false
```

改成：

```json
"confirmed": true
```

### 2.3 第二步：生成旁白、字幕、画面工程和封面

```powershell
python scripts/workflow.py build --config my-video-project/workflow-input.json --output my-video-project/output
```

输出：

```text
my-video-project/output/narration.wav
my-video-project/output/subtitles.srt
my-video-project/output/subtitles.ass
my-video-project/output/composition/
my-video-project/output/covers/cover-vertical-3x4.png
my-video-project/output/covers/cover-horizontal-4x3.png
```

这时还没有最终视频，应该先检查画面和封面。

### 2.4 第三步：预览和检查 HyperFrames 画面

进入 composition 目录：

```powershell
cd my-video-project/output/composition
```

检查：

```powershell
npx hyperframes lint
npx hyperframes validate
npx hyperframes inspect
```

预览：

```powershell
npx hyperframes preview
```

如果画面文字截断、溢出、提前切场景，让 Codex 修改：

```text
my-video-project/output/composition/index.html
my-video-project/output/composition/scene-data.js
```

### 2.5 第四步：确认画面后正式渲染

回到 Skill 根目录，然后执行：

```powershell
python scripts/workflow.py build --config my-video-project/workflow-input.json --output my-video-project/output --render
```

最终输出：

```text
my-video-project/output/explainer-silent.mp4
my-video-project/output/final-with-voice.mp4
my-video-project/output/final-with-subtitles.mp4
my-video-project/output/result-manifest.json
```

发布抖音优先使用：

```text
my-video-project/output/final-with-subtitles.mp4
my-video-project/output/covers/cover-vertical-3x4.png
my-video-project/output/covers/cover-horizontal-4x3.png
```

## 3. 用户想自定义时，Codex 应该改哪里

### 3.1 只改文案和时长

改：

```text
workflow-input.json
```

重点字段：

```json
"topic": "视频主题",
"target_duration": 180,
"raw_text": "用户提供的原始文案或要点"
```

如果文案变了，必须重新执行：

```powershell
python scripts/workflow.py prepare ...
python scripts/workflow.py build ...
```

### 3.2 改声音

改：

```json
"voice": "zh-CN-XiaoxiaoNeural",
"speech_rate": "+50%"
```

常见中文音色：

```text
zh-CN-XiaoxiaoNeural
zh-CN-YunxiNeural
zh-CN-YunjianNeural
zh-CN-XiaoyiNeural
```

如果声音或语速变了，需要重新生成 TTS、字幕、画面时间轴和最终视频。

### 3.3 改字幕大小和位置

改：

```json
"subtitle_font_size": 52,
"subtitle_margin_bottom": 150
```

规则：

- `subtitle_font_size` 越大，字幕越大。
- `subtitle_margin_bottom` 越大，字幕越往上。

如果只改字幕样式，通常只需要重新生成 ASS 和重新 FFmpeg 合成。

### 3.4 改封面

改：

```json
"cover_enabled": true,
"cover_episode_label": "第 1 集",
"cover_title": "Prompt / Skill\n版本管理\n动态插拔",
"cover_subtitle": "Registry、灰度、回滚、Runtime 装配",
"cover_hook": "不要写死，要运行时装配"
```

封面标题建议手动换行，尤其包含英文词时。

如果要更好看的封面底图，让 Codex 使用 image2/imagegen 生成无字背景，再写：

```json
"cover_vertical_background": "path/to/vertical-bg.png",
"cover_horizontal_background": "path/to/horizontal-bg.png"
```

### 3.5 改视频画面风格

默认风格文件：

```text
assets/dark-tech-template/DESIGN.md
assets/dark-tech-template/index.html
```

常见可改项：

- 背景色和光效
- 标题字号
- 信息卡片布局
- 场景转场
- 进度条样式
- 关键词卡片

如果只想使用默认风格，不用改这些文件。

如果用户要求“换成极简白底风、赛博朋克风、课堂白板风”，Codex 应先改 `DESIGN.md`，再改 `index.html`，然后用 HyperFrames inspect 检查布局。

## 4. Codex 应该如何判断缺什么

Codex 可以按这个表排查：

| 能力 | 检查命令 | 缺失时怎么做 |
|---|---|---|
| Python | `python --version` | 安装 Python 3.10+ |
| pip | `python -m pip --version` | 修复 Python 安装或 PATH |
| Edge TTS | `python -m pip show edge-tts` | `python -m pip install edge-tts` |
| Pillow | `python -m pip show Pillow` | `python -m pip install Pillow` |
| FFmpeg | `ffmpeg -version` | 下载 FFmpeg essentials build 并配置 Path |
| FFprobe | `ffprobe -version` | 与 FFmpeg 一起安装 |
| Node.js | `node -v` | 安装 Node.js LTS / 22+ |
| npm | `npm -v` | 安装 Node.js 或修复 PATH |
| HyperFrames CLI | `npx hyperframes --help` | 安装/允许 npx 下载 HyperFrames |
| HyperFrames 插件 | Codex 插件市场检查 | 安装或启用 `HyperFrames by HeyGen` |
| 浏览器渲染权限 | `npx hyperframes inspect` | 需要时向用户申请权限 |
| image2/imagegen | Codex 当前工具能力 | 可选；没有也能生成本地封面 |

## 5. 常见用户请求和 Codex 应答方式

### 请求 1：我只给主题，让你生成视频

Codex 应回答：

```text
请给我主题、原始要点或目标受众、期望时长。
如果你没有特别要求，我会使用默认暗色科技风、晓晓音色、+50% 语速、内嵌字幕和双封面。
```

### 请求 2：我给了一大段文案，让你判断时间是否合适

Codex 应：

1. 估算字数和 TTS 时长。
2. 判断是否太短或太长。
3. 给出优化版文案。
4. 先让用户确认文案，再生成 TTS。

### 请求 3：画面和语音对不上

Codex 应：

1. 检查 `content-plan.json` 里的每个场景 `start/end/duration`。
2. 确认画面切换点是否等于真实 TTS 场景时长。
3. 如果文案变了，重新 TTS 和同步时间轴。

### 请求 4：画面信息显示不全

Codex 应：

1. 检查 `composition/index.html` 是否截断了 `scene.narration`。
2. 调整卡片字体、行高、padding、max-height。
3. 跑 `npx hyperframes inspect`。
4. 抽关键帧截图给用户确认。

### 请求 5：我想换一种风格

Codex 应：

1. 先确认目标风格，例如暗色科技、极简白底、赛博朋克、课堂白板。
2. 修改 `assets/dark-tech-template/DESIGN.md` 和 `index.html`。
3. 保持字幕、TTS、输出路径不变。
4. 重新检查画面，再渲染。

## 6. 不要让 Codex 做什么

不要让 Codex：

- 未经确认就生成 TTS。
- 未经画面确认就渲染长视频。
- 把 API Key、私有文案、本地绝对路径提交到 GitHub。
- 直接把 `.venv/`、`output/`、`.env` 上传。
- 完全依赖视频截图当封面。
- 让图片模型直接生成中文标题封面，因为容易错字。

## 7. 开源用户最推荐的第一次测试

先不要上来就做 5 分钟视频。先用 15～30 秒测试链路：

```json
{
  "topic": "什么是 AI Agent？",
  "target_duration": 30,
  "raw_text": "什么是 AI Agent？简单说，它不是只会回答问题的大模型，而是能围绕目标规划步骤、调用工具、读取信息并持续执行任务的智能体。",
  "voice": "zh-CN-XiaoxiaoNeural",
  "speech_rate": "+50%",
  "visual_style": "dark-tech",
  "subtitle_enabled": true,
  "subtitle_font_size": 52,
  "subtitle_margin_bottom": 150,
  "cover_enabled": true,
  "cover_episode_label": "测试",
  "cover_title": "什么是\nAI Agent？",
  "cover_subtitle": "从聊天到任务执行",
  "cover_hook": "30 秒跑通视频工作流",
  "ffmpeg_bin": "ffmpeg",
  "ffprobe_bin": "ffprobe"
}
```

跑通后，再做正式视频。
