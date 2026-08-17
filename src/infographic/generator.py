from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw

from src.content.content_builder import build_content
from src.infographic.drawing import (
    W, H, BG, PANEL, PANEL2, BORDER, WHITE, MUTED, BLUE, PURPLE, GREEN, ORANGE, CYAN,
    font, gradient_background, rounded, text_block, draw_flow
)


def create_infographic(item: dict, output_path: str) -> str:
    content = build_content(item)
    img = gradient_background().convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Outer frame
    rounded(draw, (32, 32, W-32, H-32), radius=38, fill=(9,10,20), outline=(52,44,82), width=2)

    # Header
    tag = content["category"].upper()
    rounded(draw, (60, 56, 230, 104), radius=18, fill=(46,22,86), outline=PURPLE, width=1)
    draw.text((86, 67), tag, font=font(20, True), fill=WHITE)
    draw.text((770, 68), "TECH CHEAT SHEET", font=font(18, False), fill=MUTED)

    title_y = 125
    # Fit title into available width.
    title_font = font(64, True)
    title_lines = []
    words = content["title"].upper().split()
    line = ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textbbox((0,0), trial, font=title_font)[2] <= 920:
            line = trial
        else:
            if line:
                title_lines.append(line)
            line = word
    if line:
        title_lines.append(line)
    title_lines = title_lines[:2]
    for i, line in enumerate(title_lines):
        draw.text((70, title_y + i*70), line, font=title_font, fill=WHITE)
    title_bottom = title_y + len(title_lines)*70

    # Gradient-like accent line
    draw.line((70, title_bottom+8, 1010, title_bottom+8), fill=PURPLE, width=4)
    draw.text((70, title_bottom+20), content["tagline"], font=font(21, False), fill=MUTED)

    # Overview card
    overview_y = title_bottom + 62
    rounded(draw, (60, overview_y, 1020, overview_y+208), radius=26, fill=PANEL, outline=BORDER, width=2)
    draw.text((92, overview_y+24), "AT A GLANCE", font=font(27, True), fill=PURPLE)
    text_block(draw, (92, overview_y+72), content["overview"], font(23), fill=WHITE, width=82, gap=7, max_lines=5)

    # Main two-column block
    main_y = overview_y + 230
    main_h = 440
    left = (60, main_y, 505, main_y+main_h)
    right = (530, main_y, 1020, main_y+main_h)
    rounded(draw, left, radius=26, fill=PANEL, outline=BORDER, width=2)
    rounded(draw, right, radius=26, fill=PANEL2, outline=BORDER, width=2)

    draw.text((90, main_y+24), "KEY CONCEPTS", font=font(27, True), fill=PURPLE)
    y = main_y + 82
    concept_font = font(20, True)
    small = font(16, False)
    for idx, concept in enumerate(content["key_concepts"][:5]):
        color = [BLUE, GREEN, CYAN, ORANGE, PURPLE][idx % 5]
        draw.ellipse((90, y+5, 116, y+31), outline=color, width=2)
        draw.text((138, y), concept, font=concept_font, fill=WHITE)
        y += 55

    draw.text((560, main_y+24), content["diagram_title"], font=font(27, True), fill=PURPLE)
    draw_flow(img, draw, content["diagram"], (560, main_y+60, 990, main_y+410))

    # Scenario table
    table_y = main_y + main_h + 24
    table_h = 300
    rounded(draw, (60, table_y, 1020, table_y+table_h), radius=26, fill=PANEL, outline=BORDER, width=2)
    draw.text((90, table_y+20), "SCENARIOS & IMPACT", font=font(25, True), fill=PURPLE)

    cols = [90, 280, 620, 810, 970]
    headers = ["SCENARIO", "WHAT HAPPENS", "IMPACT", "EXAMPLE"]
    for i, htxt in enumerate(headers):
        draw.text((cols[i], table_y+65), htxt, font=font(15, True), fill=WHITE)
    y = table_y + 100
    row_font = font(14, False)
    for row in content["scenarios"][:5]:
        if len(row) >= 4:
            vals = row[:4]
            for i, val in enumerate(vals):
                draw.text((cols[i], y), val[:24], font=row_font, fill=MUTED if i else WHITE)
            draw.line((85, y+28, 995, y+28), fill=(38,34,62), width=1)
            y += 38

    # Best practices
    bp_y = table_y + table_h + 24
    draw.text((60, bp_y), "BEST PRACTICES", font=font(25, True), fill=PURPLE)
    card_gap = 14
    card_w = (960 - card_gap*3) / 4
    x = 60
    practice_colors = [GREEN, ORANGE, BLUE, PURPLE]
    practice_font = font(15, False)
    for i, practice in enumerate(content["best_practices"][:4]):
        rounded(draw, (x, bp_y+45, x+card_w, bp_y+185), radius=20, fill=PANEL2, outline=practice_colors[i], width=2)
        draw.ellipse((x+18, bp_y+65, x+48, bp_y+95), outline=practice_colors[i], width=2)
        text_block(draw, (x+60, bp_y+63), practice, practice_font, fill=WHITE, width=22, gap=4, max_lines=4)
        x += card_w + card_gap

    # Use cases strip
    uc_y = bp_y + 212
    draw.text((60, uc_y), "USE CASES", font=font(25, True), fill=PURPLE)
    rounded(draw, (60, uc_y+42, 1020, uc_y+125), radius=22, fill=PANEL, outline=BORDER, width=2)
    n = max(1, len(content["use_cases"][:5]))
    gap = 900 // n
    for i, use in enumerate(content["use_cases"][:5]):
        cx = 110 + i*gap
        color = [BLUE, PURPLE, GREEN, CYAN, ORANGE][i % 5]
        draw.ellipse((cx-11, uc_y+57, cx+11, uc_y+79), outline=color, width=2)
        f = font(11, False)
        import textwrap
        label_lines = textwrap.wrap(use, width=19)[:2]
        yy = uc_y + 84
        for line in label_lines:
            bbox = draw.textbbox((0,0), line, font=f)
            draw.text((cx-(bbox[2]-bbox[0])/2, yy), line, font=f, fill=MUTED)
            yy += 14

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, "PNG", optimize=True)
    return str(out)
