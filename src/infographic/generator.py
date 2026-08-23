from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from src.content.content_builder import build_content
from src.infographic.drawing import (
    W, H, BG, TEXT, MUTED, LINE, PANEL,
    font, fit_font, rounded, draw_text, draw_section_header,
    draw_architecture, draw_key_idea_card, draw_example, draw_failure,
    draw_practice_card, draw_use_cases, draw_branding
)
from src.infographic.visual_templates import template_for, palette_for


def _background() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Soft radial-ish glow using layered circles.
    for center, color, radius in [
        ((160, 180), (30, 22, 70), 220),
        ((930, 350), (22, 30, 80), 260),
        ((720, 1450), (33, 20, 70), 260),
    ]:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        x, y = center
        ld.ellipse((x-radius, y-radius, x+radius, y+radius), fill=(*color, 120))
        layer = layer.filter(__import__("PIL").ImageFilter.GaussianBlur(90))
        img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

    return img


def create_infographic(item: dict, output_path: str) -> str:
    content = build_content(item)
    template = template_for(content["category"])
    palette = palette_for(template)

    img = _background().convert("RGB")
    draw = ImageDraw.Draw(img)

    # Outer frame
    rounded(draw, (30, 30, W-30, H-30), radius=36, fill=BG, outline=LINE, width=2)

    # Header brand/category chip
    rounded(draw, (60, 55, 260, 104), radius=18, fill=(31, 18, 56), outline=palette["primary"], width=2)
    category_label = content["category"].replace("_", " ").title()
    draw.text((82, 68), category_label, font=font(18, True), fill=TEXT)
    draw.text((765, 68), "CodeWithKambojShubham", font=font(14, True), fill=TEXT)

    # Hero title
    # Keep content headings in normal title/camel-style casing instead of ALL CAPS.
    # Example: "API Gateway" rather than "API GATEWAY".
    title = content["title"].strip()
    title_font = fit_font(draw, title, 930, 60, 34, True)
    draw.text((60, 130), title, font=title_font, fill=TEXT)

    y = 130 + title_font.size + 14
    tagline_font = fit_font(draw, content["tagline"], 930, 24, 16, True)
    draw.text((60, y), content["tagline"].title(), font=tagline_font, fill=palette["secondary"])

    y += tagline_font.size + 12

    # Intro divider
    draw.line((60, y, 1020, y), fill=palette["primary"], width=3)
    y += 16

    # Overview
    overview_h = 150
    rounded(draw, (60, y, 1020, y+overview_h), radius=22, fill=PANEL, outline=LINE, width=2)
    draw_section_header(draw, 86, y+20, "AT A GLANCE", palette["primary"])
    draw_text(draw, (86, y+58), content["overview"], font(18, False), fill=WHITE, max_width=880, max_lines=3, line_gap=5)
    y += overview_h + 18

    # Architecture (largest visual)
    arch_h = 380
    draw_architecture(draw, (60, y, 1020, y+arch_h), content, palette)
    y += arch_h + 18

    # Key idea cards
    draw_section_header(draw, 60, y, "KEY IDEAS", palette["primary"])
    y += 45
    cols = 2
    gap = 14
    card_w = (960-gap)//cols
    card_h = 115
    for i, (head, desc) in enumerate(content["key_ideas"][:4]):
        col = i % cols
        row = i // cols
        x = 60 + col*(card_w+gap)
        yy = y + row*(card_h+gap)
        draw_key_idea_card(draw, (x, yy, x+card_w, yy+card_h), head, desc, [palette["secondary"], palette["accent"], palette["primary"], palette["secondary"]][i])
    y += 2*card_h + gap + 18

    # Example + failure row
    row_h = 240
    left_w = 470
    draw_example(draw, (60, y, 60+left_w, y+row_h), content["example_title"], content["example_rows"], palette["primary"], palette["secondary"], palette["accent"])
    draw_failure(draw, (60+left_w+20, y, 1020, y+row_h), content["failure_title"], content["failure_before"], content["failure_after"], palette["primary"], palette["secondary"], palette["accent"])
    y += row_h + 18

    # Best practices
    draw_section_header(draw, 60, y, "BEST PRACTICES", palette["primary"])
    y += 42
    bp_w = (960-3*12)//4
    bp_h = 122
    for i, practice in enumerate(content["best_practices"][:4]):
        x = 60 + i*(bp_w+12)
        color = [palette["accent"], palette["primary"], palette["secondary"], palette["accent"]][i]
        draw_practice_card(draw, (x, y, x+bp_w, y+bp_h), practice, color)
    y += bp_h + 18

    # Use cases
    draw_section_header(draw, 60, y, "USE CASES", palette["primary"])
    y += 38
    draw_use_cases(draw, (60, y, 1020, y+92), content["use_cases"], [palette["secondary"], palette["primary"], palette["accent"], palette["secondary"]])

    # Branding footer (no AUTO-GENERATED / TECH CHEAT SHEET)
    draw_branding(draw)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return str(out)
