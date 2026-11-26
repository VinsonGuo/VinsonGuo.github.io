#!/usr/bin/env python3
"""
Batch-generate 1200x630 Open Graph preview images for all Jekyll product pages
in _projects/*.md.

Automatically detects framed phone screenshots (both solid-background and
App Store promotional cards), cuts out the phone mockup cleanly to remove the
surrounding background, and composites a clean 1200x630 social preview card.

Usage:
    python3 scripts/generate_og.py
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = ROOT / "_projects"

# Render at 2x for crisp anti-aliased text, borders, and rounded corners
SCALE = 2
W, H = 1200 * SCALE, 630 * SCALE


def parse_front_matter(md_path: Path) -> dict:
    """Minimal YAML front-matter parser (no PyYAML required)."""
    text = md_path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}
    lines = m.group(1).splitlines()
    data = {}
    current_list_key = None

    for line in lines:
        if not line.strip() or line.strip().startswith("#"):
            continue
        list_m = re.match(r"^\s+-\s+(.*)$", line)
        if list_m and current_list_key:
            val = list_m.group(1).strip().strip('"').strip("'")
            data[current_list_key].append(val)
            continue
        kv_m = re.match(r"^([a-zA-Z0-9_]+):\s*(.*)$", line)
        if kv_m:
            key, val = kv_m.group(1), kv_m.group(2).strip()
            if val == "":
                data[key] = []
                current_list_key = key
            else:
                current_list_key = None
                data[key] = val.strip('"').strip("'")
        else:
            current_list_key = None
    return data


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def load_font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    """Load macOS Helvetica Neue / Arial with sensible fallbacks."""
    if weight == "bold":
        candidates = [
            ("/System/Library/Fonts/HelveticaNeue.ttc", 1),
            ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0),
            ("/System/Library/Fonts/Helvetica.ttc", 1),
        ]
    elif weight == "semibold":
        candidates = [
            ("/System/Library/Fonts/HelveticaNeue.ttc", 10),
            ("/System/Library/Fonts/HelveticaNeue.ttc", 1),
            ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0),
        ]
    else:
        candidates = [
            ("/System/Library/Fonts/HelveticaNeue.ttc", 0),
            ("/System/Library/Fonts/Supplemental/Arial.ttf", 0),
            ("/System/Library/Fonts/Helvetica.ttc", 0),
        ]

    for path, idx in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size, index=idx)
            except Exception:
                continue
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def round_corners(im: Image.Image, radius: int) -> Image.Image:
    im = im.convert("RGBA")
    mask = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, im.size[0], im.size[1]], radius=radius, fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def paste_alpha_with_shadow(
    canvas: Image.Image,
    fg: Image.Image,
    pos: tuple[int, int],
    shadow_offset: tuple[int, int] = (0, 24),
    shadow_blur: int = 40,
    shadow_alpha: int = 44,
):
    """Composite an RGBA image using its own alpha channel to cast a soft shadow."""
    x, y = pos
    w, h = fg.size
    pad = shadow_blur * 2 + max(abs(shadow_offset[0]), abs(shadow_offset[1])) + 20

    alpha = fg.getchannel("A")
    # Scale alpha down to shadow_alpha
    shadow_mask = alpha.point(lambda a: int(a * shadow_alpha / 255))

    shadow_layer = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    shadow_fill = Image.new("RGBA", (w, h), (15, 23, 42, 255))
    shadow_fill.putalpha(shadow_mask)
    shadow_layer.paste(shadow_fill, (pad + shadow_offset[0], pad + shadow_offset[1]))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=shadow_blur))

    canvas.alpha_composite(shadow_layer, (x - pad, y - pad))
    canvas.alpha_composite(fg, (x, y))


def paste_rect_with_shadow(
    canvas: Image.Image,
    fg: Image.Image,
    pos: tuple[int, int],
    radius: int,
    shadow_offset: tuple[int, int] = (0, 12),
    shadow_blur: int = 20,
    shadow_alpha: int = 34,
    border_color: tuple[int, int, int, int] | None = (0, 0, 0, 20),
    border_width: int = 2,
):
    rounded = round_corners(fg, radius)
    paste_alpha_with_shadow(
        canvas,
        rounded,
        pos=pos,
        shadow_offset=shadow_offset,
        shadow_blur=shadow_blur,
        shadow_alpha=shadow_alpha,
    )
    if border_color and border_width > 0:
        w, h = fg.size
        border_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(border_layer)
        bdraw.rounded_rectangle(
            [border_width // 2, border_width // 2, w - 1 - border_width // 2, h - 1 - border_width // 2],
            radius=radius,
            outline=border_color,
            width=border_width,
        )
        canvas.alpha_composite(border_layer, pos)


def create_background(accent_rgb: tuple[int, int, int]) -> Image.Image:
    # Subtle light vertical gradient (#FFFFFF -> #F4F5F8)
    bg = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        r = int(255 - 10 * t)
        g = int(255 - 9 * t)
        b = int(255 - 6 * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # Soft radial accent glow behind the right-side showcase
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    cx, cy = int(W * 0.78), int(H * 0.56)
    rx, ry = int(W * 0.34), int(H * 0.68)
    gdraw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(*accent_rgb, 34))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=140 * SCALE))
    bg.alpha_composite(glow)

    # Secondary subtle accent glow top-left
    glow2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw2 = ImageDraw.Draw(glow2)
    gdraw2.ellipse([-200 * SCALE, -220 * SCALE, 420 * SCALE, 320 * SCALE], fill=(*accent_rgb, 14))
    glow2 = glow2.filter(ImageFilter.GaussianBlur(radius=110 * SCALE))
    bg.alpha_composite(glow2)

    return bg


def _cutout_phone_bbox(im: Image.Image) -> tuple[int, int, int, int] | None:
    """
    Detect a framed phone mockup inside a screenshot and return its (x0, y0, x1, y1)
    bounding box, or None if the image is already a raw frameless screenshot.
    """
    arr = np.array(im.convert("RGB"))
    h, w, _ = arr.shape

    # Strategy 1: Solid-color surrounding background (e.g. pure white or pure black)
    corners = np.array([arr[5, 5], arr[5, w - 6], arr[h - 6, 5], arr[h - 6, w - 6]], dtype=int)
    if np.abs(corners - corners[0]).max() <= 12:
        bg = corners[0]
        diff = np.abs(arr.astype(int) - bg).max(axis=2) > 18
        ys, xs = np.where(diff)
        if len(xs) > 0:
            x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())
            bw, bh = x1 - x0 + 1, y1 - y0 + 1
            # Surrounded by clear margin and phone-like aspect ratio
            if bw / w < 0.96 and bh / h < 0.96 and 1.6 <= bh / bw <= 2.4:
                return (x0, y0, x1, y1)

    # Strategy 2: App Store promotional card (gradient/colored background + dark phone bezel)
    dark = (arr[:, :, 0] < 52) & (arr[:, :, 1] < 52) & (arr[:, :, 2] < 52)
    mid_y = int(h * 0.55)
    dark_xs = np.where(dark[mid_y])[0]
    if len(dark_xs) >= 2:
        x0_init, x1_init = int(dark_xs[0]), int(dark_xs[-1])
        mid_x = (x0_init + x1_init) // 2
        y_start = int(h * 0.14)
        dark_ys = np.where(dark[y_start:, mid_x])[0] + y_start
        if len(dark_ys) >= 2:
            y0_init, y1_init = int(dark_ys[0]), int(dark_ys[-1])
            if y1_init - y0_init > h * 0.5 and x1_init - x0_init > w * 0.5:
                margin_y = min(150, (y1_init - y0_init) // 6)
                margin_x = min(150, (x1_init - x0_init) // 6)
                sub_x = dark[y0_init + margin_y : y1_init - margin_y, :]
                cols = np.where(sub_x.sum(axis=0) > sub_x.shape[0] * 0.45)[0]
                sub_y = dark[y_start:, x0_init + margin_x : x1_init - margin_x]
                rows = np.where(sub_y.sum(axis=1) > sub_y.shape[1] * 0.45)[0] + y_start
                if len(cols) >= 2 and len(rows) >= 2:
                    rx0, rx1 = int(cols[0]), int(cols[-1])
                    ry0, ry1 = int(rows[0]), int(rows[-1])
                    bw, bh = rx1 - rx0 + 1, ry1 - ry0 + 1
                    if 0.55 <= bw / w <= 0.96 and 1.7 <= bh / bw <= 2.35:
                        return (rx0, ry0, rx1, ry1)

    return None


def make_phone_cutout(screenshot_path: Path, target_w: int) -> Image.Image:
    """
    Extract the framed phone from the screenshot (removing its outer background),
    apply a clean anti-aliased rounded-corner mask matching the iPhone shell,
    and resize to target_w.
    """
    im = Image.open(screenshot_path).convert("RGBA")
    bbox = _cutout_phone_bbox(im)

    if bbox is not None:
        x0, y0, x1, y1 = bbox
        # Inset by 2px to eliminate any anti-aliased halo from the original background
        inset = 2
        crop = im.crop((x0 + inset, y0 + inset, x1 + 1 - inset, y1 + 1 - inset))
        ratio = target_w / crop.width
        target_h = int(crop.height * ratio)
        resized = crop.resize((target_w, target_h), Image.Resampling.LANCZOS)
        # iPhone hardware shell corner radius is ~15.5% of phone width
        corner_r = int(target_w * 0.155)
        return round_corners(resized, corner_r)

    # Fallback for raw frameless screenshots
    ratio = target_w / im.width
    target_h = int(im.height * ratio)
    resized = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
    return round_corners(resized, 28 * SCALE)


def generate_og_for_project(md_path: Path) -> Path:
    meta = parse_front_matter(md_path)
    slug = md_path.stem
    title = meta.get("title", slug)
    tagline = meta.get("tagline", meta.get("description", ""))
    logo_rel = meta.get("logo", "").lstrip("/")
    accent = meta.get("accent", "#0071e3")
    accent_text = meta.get("accent_text", accent)
    platforms = meta.get("platforms", [])
    screenshots = [s.lstrip("/") for s in meta.get("showcase_screenshots", [])]

    accent_rgb = hex_to_rgb(accent)
    accent_text_rgb = hex_to_rgb(accent_text)

    canvas = create_background(accent_rgb)

    # --- Right side: Cutout phone mockups ---
    if len(screenshots) >= 2:
        back_shot = ROOT / screenshots[1]
        front_shot = ROOT / screenshots[0]
        if back_shot.exists():
            back_phone = make_phone_cutout(back_shot, target_w=244 * SCALE)
            paste_alpha_with_shadow(
                canvas,
                back_phone,
                pos=(902 * SCALE, 114 * SCALE),
                shadow_offset=(0, 24 * SCALE),
                shadow_blur=36 * SCALE,
                shadow_alpha=42,
            )
        if front_shot.exists():
            front_phone = make_phone_cutout(front_shot, target_w=266 * SCALE)
            paste_alpha_with_shadow(
                canvas,
                front_phone,
                pos=(664 * SCALE, 44 * SCALE),
                shadow_offset=(0, 30 * SCALE),
                shadow_blur=46 * SCALE,
                shadow_alpha=54,
            )
    elif len(screenshots) == 1:
        front_shot = ROOT / screenshots[0]
        if front_shot.exists():
            front_phone = make_phone_cutout(front_shot, target_w=282 * SCALE)
            paste_alpha_with_shadow(
                canvas,
                front_phone,
                pos=(760 * SCALE, 44 * SCALE),
                shadow_offset=(0, 30 * SCALE),
                shadow_blur=46 * SCALE,
                shadow_alpha=54,
            )

    # --- Left side: Logo, badge, title, tagline, footer ---
    draw = ImageDraw.Draw(canvas)
    left_x = 76 * SCALE
    max_text_w = 545 * SCALE
    cursor_y = 74 * SCALE

    # Logo
    logo_path = ROOT / logo_rel if logo_rel else None
    if logo_path and logo_path.exists():
        logo_size = 88 * SCALE
        logo_im = Image.open(logo_path).convert("RGBA").resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        paste_rect_with_shadow(
            canvas,
            logo_im,
            pos=(left_x, cursor_y),
            radius=22 * SCALE,
            shadow_offset=(0, 12 * SCALE),
            shadow_blur=20 * SCALE,
            shadow_alpha=34,
            border_color=(0, 0, 0, 20),
            border_width=2,
        )
        cursor_y += logo_size + 34 * SCALE

    # Platforms badge
    if platforms:
        badge_text = "  ·  ".join(platforms)
        badge_font = load_font(18 * SCALE, weight="semibold")
        draw.text((left_x, cursor_y), badge_text, font=badge_font, fill=(*accent_text_rgb, 255))
        bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        cursor_y += (bbox[3] - bbox[1]) + 18 * SCALE

    # Title (auto-size down slightly for long titles)
    title_size = 56 * SCALE if len(title) <= 14 else 46 * SCALE
    title_font = load_font(title_size, weight="bold")
    title_lines = wrap_text(draw, title, title_font, max_text_w)
    line_gap = int(title_size * 1.14)
    for line in title_lines:
        draw.text((left_x, cursor_y), line, font=title_font, fill=(29, 29, 31, 255))
        cursor_y += line_gap
    cursor_y += 18 * SCALE

    # Tagline
    tagline_font = load_font(24 * SCALE, weight="regular")
    tagline_lines = wrap_text(draw, tagline, tagline_font, max_text_w)
    for line in tagline_lines[:3]:
        draw.text((left_x, cursor_y), line, font=tagline_font, fill=(81, 81, 84, 255))
        cursor_y += int(24 * SCALE * 1.42)

    # Bottom domain watermark
    footer_y = H - 64 * SCALE
    dot_r = 5 * SCALE
    draw.ellipse(
        [left_x, footer_y + 7 * SCALE, left_x + dot_r * 2, footer_y + 7 * SCALE + dot_r * 2],
        fill=(*accent_rgb, 255),
    )
    footer_font = load_font(18 * SCALE, weight="semibold")
    draw.text(
        (left_x + dot_r * 2 + 12 * SCALE, footer_y),
        "vinsonguo.github.io",
        font=footer_font,
        fill=(110, 110, 115, 255),
    )

    # Downsample 2x -> 1x (1200x630)
    final_im = canvas.convert("RGB").resize((1200, 630), Image.Resampling.LANCZOS)

    out_dir = ROOT / "assets" / "img" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "og.png"
    final_im.save(out_path, format="PNG", optimize=True)
    return out_path


def main():
    md_files = sorted(PROJECTS_DIR.glob("*.md"))
    for md_path in md_files:
        out_path = generate_og_for_project(md_path)
        size_kb = out_path.stat().st_size / 1024
        print(f"Generated {out_path.relative_to(ROOT)} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
