from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw

from src.content.content_builder import build_content
from src.infographic.drawing import (
    W, H, PANEL, PANEL2, BORDER, WHITE, MUTED, BLUE, PURPLE, GREEN, ORANGE, CYAN,
    font, fit_font, gradient_background, rounded, text_block, draw_flow
)


def draw_title(draw, title: str):
    max_width = 930
    title_font = fit_font(title.upper(), max_width, 58, 38, bold=True)
    words = title.upper().split()
    lines = []
    line = ""
    for word in words:
        trial = (line + " " + word).strip()
        if not line or draw.textbbox((0,0), trial, font=title_font)[2] <= max_width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    lines = lines[:2]

    y = 122
    for line in lines:
        draw.text((70, y), line, font=title_font, fill=WHITE)
        y += title_font.size + 6
    return y


def create_infographic(item: dict, output_path: str) -> str:
    content = build_content(item)
    img = gradient_background().convert("RGBA")
    draw = ImageDraw.Draw(img)

    rounded(draw, (32, 32, W-32, H-32), radius=38, fill=(9,10,20), outline=(52,44,82), width=2)

    # Header
    tag = str(content["category"]).upper()[:16]
    tag_font = fit_font(tag, 130, 20, 12, bold=True)
    rounded(draw, (60, 56, 230, 104), radius=18, fill=(46,22,86), outline=PURPLE, width=1)
    draw.text((145 - draw.textbbox((0,0), tag, font=tag_font)[2]/2, 67), tag, font=tag_font, fill=WHITE)

    cheat_font = fit_font("CodeWithKambojShubham", 220, 18, 12, bold=False)
    draw.text((1010-text_width(draw,"CodeWithKambojShubham",cheat_font), 68), "CodeWithKambojShubham", font=cheat_font, fill=MUTED)

    # Title / subtitle
    title_bottom = draw_title(draw, content["title"])
    draw.line((70, title_bottom+8, 1010, title_bottom+8), fill=PURPLE, width=4)

    tagline_font = fit_font(content["tagline"], 900, 20, 12, bold=False)
    draw.text((70, title_bottom+20), content["tagline"], font=tagline_font, fill=MUTED)

    # Overview
    overview_y = title_bottom + 62
    rounded(draw, (60, overview_y, 1020, overview_y+208), radius=26, fill=PANEL, outline=BORDER, width=2)
    draw.text((92, overview_y+24), "AT A GLANCE", font=font(27, True), fill=PURPLE)
    overview_font = fit_font(content["overview"], 820, 22, 15, bold=False)
    text_block(draw, (92, overview_y+72), content["overview"], overview_font, fill=WHITE, width=820, gap=6, max_lines=5)

    # Main two-column block
    main_y = overview_y + 230
    main_h = 440
    left = (60, main_y, 505, main_y+main_h)
    right = (530, main_y, 1020, main_y+main_h)
    rounded(draw, left, radius=26, fill=PANEL, outline=BORDER, width=2)
    rounded(draw, right, radius=26, fill=PANEL2, outline=BORDER, width=2)

    draw.text((90, main_y+24), "KEY CONCEPTS", font=font(27, True), fill=PURPLE)
    y = main_y + 82
    concept_font = font(18, True)
    for idx, concept in enumerate(content["key_concepts"][:5]):
        color = [BLUE, GREEN, CYAN, ORANGE, PURPLE][idx % 5]
        draw.ellipse((90, y+5, 116, y+31), outline=color, width=2)
        available = 505 - 138 - 28
        f = fit_font(str(concept), available, 18, 12, bold=True)
        text_block(draw, (138, y), str(concept), f, fill=WHITE, width=available, gap=3, max_lines=2)
        y += 55

    draw.text((560, main_y+24), str(content["diagram_title"])[:24], font=font(27, True), fill=PURPLE)
    # Fixed drawing viewport. draw_flow is clipped to this layer by construction.
    draw_flow(img, draw, content["diagram"], (560, main_y+60, 990, main_y+410))

    # Scenario table
    table_y = main_y + main_h + 24
    table_h = 300
    rounded(draw, (60, table_y, 1020, table_y+table_h), radius=26, fill=PANEL, outline=BORDER, width=2)
    draw.text((90, table_y+20), "SCENARIOS & IMPACT", font=font(25, True), fill=PURPLE)

    col_x = [90, 280, 570, 750]
    col_w = [175, 275, 165, 210]
    headers = ["SCENARIO", "WHAT HAPPENS", "IMPACT", "EXAMPLE"]
    header_font = font(13, True)
    for x, header, width in zip(col_x, headers, col_w):
        hf = fit_font(header, width, 13, 9, True)
        draw.text((x, table_y+65), header, font=hf, fill=WHITE)

    y = table_y + 98
    row_font = font(12, False)
    for row in content["scenarios"][:5]:
        if len(row) >= 4:
            vals = row[:4]
            row_max_h = 30
            for i, (x, width, value) in enumerate(zip(col_x, col_w, vals)):
                f = fit_font(str(value), width-8, 12, 9, False)
                lines = []
                words = str(value).split()
                cur = ""
                for word in words:
                    trial = (cur + " " + word).strip()
                    if not cur or text_width(draw, trial, f) <= width-8:
                        cur = trial
                    else:
                        lines.append(cur)
                        cur = word
                if cur:
                    lines.append(cur)
                lines = lines[:2]
                yy = y
                for line in lines:
                    draw.text((x, yy), line, font=f, fill=WHITE if i == 0 else MUTED)
                    yy += f.size + 2
                row_max_h = max(row_max_h, len(lines)*(f.size+2))
            draw.line((85, y+row_max_h+5, 995, y+row_max_h+5), fill=(38,34,62), width=1)
            y += row_max_h + 10
            if y > table_y + table_h - 24:
                break

    # Best practices
    bp_y = table_y + table_h + 24
    draw.text((60, bp_y), "BEST PRACTICES", font=font(25, True), fill=PURPLE)
    card_gap = 14
    card_w = int((960 - card_gap*3) / 4)
    x = 60
    practice_colors = [GREEN, ORANGE, BLUE, PURPLE]
    for i, practice in enumerate(content["best_practices"][:4]):
        x2 = x + card_w
        rounded(draw, (x, bp_y+45, x2, bp_y+185), radius=20, fill=PANEL2, outline=practice_colors[i], width=2)
        draw.ellipse((x+18, bp_y+65, x+48, bp_y+95), outline=practice_colors[i], width=2)
        available = x2 - (x+60) - 12
        f = fit_font(str(practice), available, 14, 10, False)
        text_block(draw, (x+60, bp_y+63), str(practice), f, fill=WHITE, width=available, gap=4, max_lines=4)
        x += card_w + card_gap

    # Use cases
    uc_y = bp_y + 212
    draw.text((60, uc_y), "USE CASES", font=font(25, True), fill=PURPLE)
    rounded(draw, (60, uc_y+42, 1020, uc_y+125), radius=22, fill=PANEL, outline=BORDER, width=2)
    cases = content["use_cases"][:5]
    n = max(1, len(cases))
    usable = 900
    gap = usable / max(1, n)
    for i, use in enumerate(cases):
        cx = int(100 + (i + 0.5)*gap)
        color = [BLUE, PURPLE, GREEN, CYAN, ORANGE][i%5]
        draw.ellipse((cx-11, uc_y+57, cx+11, uc_y+79), outline=color, width=2)
        f = fit_font(str(use), int(gap-12), 11, 8, False)
        text_block(draw, (cx-int(gap/2)+6, uc_y+84), str(use), f, fill=MUTED, width=int(gap-12), gap=2, max_lines=2)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, "PNG", optimize=True)
    return str(out)


def text_width(draw, text, fnt):
    b = draw.textbbox((0,0), text, font=fnt)
    return b[2]-b[0]
