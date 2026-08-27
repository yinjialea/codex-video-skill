# 输入配置字段

- `topic`：视频主题或核心问题，必填。
- `raw_text`：待审核口播稿，必填；空行优先作为场景边界。
- `target_duration`：规划目标秒数；最终时长以 TTS 为准。
- `voice`：Edge TTS 音色，默认 `zh-CN-XiaoxiaoNeural`。
- `speech_rate`：统一语速，例如 `+50%`。
- `visual_style`：当前支持 `dark-tech`。
- `subtitle_enabled`：是否生成字幕，默认 `true`。
- `subtitle_font_size`：ASS 字号，默认 52。
- `subtitle_margin_bottom`：字幕距底边像素，默认 150。
- `cover_enabled`：是否生成抖音封面，默认 `true`。
- `cover_episode_label`：封面期数标签，例如 `第 1 集`。
- `cover_title`：封面主标题；可用 `\n` 手动换行，推荐避免英文词被自动拆开。
- `cover_subtitle`：封面副标题。
- `cover_hook`：封面底部钩子文案。
- `cover_vertical_background`：可选，竖封面 3:4 底图路径；适合放 image2/imagegen 生成的无字底图。
- `cover_horizontal_background`：可选，横封面 4:3 底图路径；适合放 image2/imagegen 生成的无字底图。
- `ffmpeg_bin` / `ffprobe_bin`：完整路径或 PATH 中的命令名。

JSON 使用 UTF-8。Windows 路径建议使用正斜线。
