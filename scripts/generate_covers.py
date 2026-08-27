"""生成抖音发布封面：竖封面 3:4 与横封面 4:3。

设计目标：
1. 标题文字由 Pillow 本地绘制，保证中文、Prompt、Skill 等词不被图片模型写错。
2. 如果配置提供 image2/imagegen 生成的底图，就使用底图并叠字。
3. 如果没有底图，就生成一个本地暗色科技风兜底背景，保证开源后也能跑通。
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont


VERTICAL_SIZE = (900, 1200)
HORIZONTAL_SIZE = (1200, 900)


def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """加载 Windows 常见中文字体；跨平台找不到时回退到 Pillow 默认字体。"""
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _crop_to_size(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """按目标比例居中裁切，避免封面背景被拉伸。"""
    target_w, target_h = size
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    else:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))
    return img.resize(size, Image.Resampling.LANCZOS).convert("RGBA")


def _local_tech_background(size: tuple[int, int]) -> Image.Image:
    """生成无需外部模型的暗色科技底图，作为 image2 不可用时的兜底。"""
    w, h = size
    img = Image.new("RGBA", size, (3, 7, 20, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # 径向光晕
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    for i in range(90, 0, -1):
        alpha = int(70 * (i / 90) ** 2)
        gd.ellipse((w - i * 10, -i * 4, w + i * 2, i * 8), fill=(169, 133, 255, alpha))
        gd.ellipse((-i * 5, h - i * 7, i * 8, h + i * 4), fill=(69, 224, 170, alpha))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(18)))
    draw = ImageDraw.Draw(img, "RGBA")

    # 网格线和粒子
    for x in range(0, w, 72):
        draw.line((x, 0, x, h), fill=(76, 232, 255, 18), width=1)
    for y in range(0, h, 72):
        draw.line((0, y, w, y), fill=(169, 133, 255, 14), width=1)
    for i in range(85):
        # 确定性伪随机，避免每次生成结果乱跳。
        x = int((math.sin(i * 12.9898) * 43758.5453 % 1) * w)
        y = int((math.sin(i * 78.233) * 24634.6345 % 1) * h)
        color = (76, 232, 255, 130) if i % 3 else (169, 133, 255, 120)
        draw.ellipse((x, y, x + 4, y + 4), fill=color)

    # 右下角模块/插拔感装饰
    base_x, base_y = int(w * 0.58), int(h * 0.66)
    for i in range(5):
        x = base_x + i * 54
        y = base_y + int(math.sin(i) * 32)
        draw.rounded_rectangle((x, y, x + 86, y + 86), radius=14, outline=(76, 232, 255, 160), fill=(8, 24, 52, 150), width=3)
        draw.line((x - 80, y + 43, x, y + 43), fill=(69, 224, 170, 140), width=3)
    return img


def _readability_panel(img: Image.Image, vertical: bool) -> Image.Image:
    """给标题区域增加半透明深色面板，增强抖音列表里的可读性。"""
    w, h = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, w, h), fill=(0, 0, 0, 48))
    if vertical:
        box = (48, 155, w - 48, 760)
    else:
        box = (54, 90, int(w * 0.62), h - 88)
    draw.rounded_rectangle(box, radius=42, fill=(2, 7, 20, 172), outline=(76, 232, 255, 90), width=2)
    return Image.alpha_composite(img, overlay)


def _draw_stroked(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font_obj: ImageFont.FreeTypeFont, stroke: int = 6) -> None:
    """绘制带黑色描边的大标题，保证在亮色科技元素上仍可读。"""
    draw.text(xy, text, font=font_obj, fill=(245, 248, 255, 255), stroke_width=stroke, stroke_fill=(0, 0, 0, 220))


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """按像素宽度自动换行；如果用户用换行符指定行，则尊重手动换行。"""
    if "\n" in text:
        return [line for line in text.splitlines() if line.strip()]
    lines: list[str] = []
    current = ""
    for ch in text:
        test = current + ch
        if draw.textbbox((0, 0), test, font=font_obj)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def _make_one_cover(
    *,
    background_path: Path | None,
    output_path: Path,
    size: tuple[int, int],
    episode_label: str,
    title: str,
    subtitle: str,
    hook: str,
) -> None:
    """生成单张封面。"""
    vertical = size[1] > size[0]
    if background_path and background_path.exists():
        img = _crop_to_size(Image.open(background_path), size)
    else:
        img = _local_tech_background(size)
    img = _readability_panel(img, vertical)
    draw = ImageDraw.Draw(img)
    w, h = size

    margin = 82 if vertical else 92
    tag_y = 198 if vertical else 128
    title_y = 300 if vertical else 230
    max_width = w - margin * 2 if vertical else int(w * 0.50)
    title_font = _font(78 if vertical else 62)
    subtitle_font = _font(36 if vertical else 31, bold=False)
    badge_font = _font(30 if vertical else 26)
    hook_font = _font(32 if vertical else 28)

    badge_text = f"{episode_label}｜AI Agent 面试题"
    badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    badge_w = badge_bbox[2] + 34
    badge_h = 50 if vertical else 44
    draw.rounded_rectangle((margin, tag_y, margin + badge_w, tag_y + badge_h), radius=badge_h // 2, fill=(69, 224, 170, 238))
    draw.text((margin + 18, tag_y + 8), badge_text, font=badge_font, fill=(3, 7, 20, 255))

    y = title_y
    for line in _wrap_text(draw, title, title_font, max_width):
        _draw_stroked(draw, (margin, y), line, title_font)
        y += title_font.size + (14 if vertical else 10)

    y += 22
    for line in _wrap_text(draw, subtitle, subtitle_font, max_width)[:3]:
        draw.text((margin, y), line, font=subtitle_font, fill=(190, 221, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 180))
        y += subtitle_font.size + 10

    hook_bbox = draw.textbbox((0, 0), hook, font=hook_font)
    hook_w = hook_bbox[2] + 44
    hook_h = 58 if vertical else 52
    hook_y = h - (135 if vertical else 100)
    draw.rounded_rectangle((margin, hook_y, margin + hook_w, hook_y + hook_h), radius=18, fill=(169, 133, 255, 220))
    draw.text((margin + 22, hook_y + 12), hook, font=hook_font, fill=(255, 255, 255, 255))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output_path, quality=96)


def generate_covers(config: dict[str, Any], output_dir: Path) -> dict[str, str]:
    """根据 workflow 配置生成竖封面和横封面，返回产物路径。"""
    if config.get("cover_enabled", True) is False:
        return {}

    covers_dir = output_dir / "covers"
    topic = str(config.get("topic", "知识科普视频"))
    cover_title = str(config.get("cover_title") or topic)
    cover_subtitle = str(config.get("cover_subtitle") or "中文知识科普｜AI Agent 工程化")
    cover_hook = str(config.get("cover_hook") or "收藏这一条，面试能讲清楚")
    episode_label = str(config.get("cover_episode_label") or "第 1 集")
    vertical_bg = config.get("cover_vertical_background")
    horizontal_bg = config.get("cover_horizontal_background")

    vertical_output = covers_dir / "cover-vertical-3x4.png"
    horizontal_output = covers_dir / "cover-horizontal-4x3.png"

    _make_one_cover(
        background_path=Path(vertical_bg) if vertical_bg else None,
        output_path=vertical_output,
        size=VERTICAL_SIZE,
        episode_label=episode_label,
        title=cover_title,
        subtitle=cover_subtitle,
        hook=cover_hook,
    )
    _make_one_cover(
        background_path=Path(horizontal_bg) if horizontal_bg else None,
        output_path=horizontal_output,
        size=HORIZONTAL_SIZE,
        episode_label=episode_label,
        title=cover_title,
        subtitle=cover_subtitle,
        hook=cover_hook,
    )
    return {
        "cover_vertical": str(vertical_output),
        "cover_horizontal": str(horizontal_output),
    }
