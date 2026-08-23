from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw

from src.content.content_builder import build_content
from src.infographic.drawing import (
    W, H, OUTPUT_W, OUTPUT_H, TEXT, MUTED, PANEL, PANEL_ALT, BORDER, BLUE, PURPLE, GREEN, ORANGE, CYAN,
    font, fit_font, text_width, text_block, rounded, draw_background, draw_topic_flow,
    draw_key_card, draw_simple_list
)


def create_infographic(item: dict, output_path: str) -> str:
    content = build_content(item)
    img = draw_background()
    draw = ImageDraw.Draw(img)

    # Outer frame
    rounded(draw, (28, 28, W-28, H-28), radius=34, fill=(255,255,255), outline=BORDER, width=2)

    # Header chip
    category = str(content.get("category", "tech")).replace("_", " ").title()
    rounded(draw, (55, 50, 250, 94), radius=15, fill=(247, 241, 255), outline=PURPLE, width=2)
    draw.text((72, 61), category, font=font(16, True), fill=PURPLE)
    brand = "CodeWithKambojShubham"
    bf = fit_font(brand, 260, 13, 9, True)
    draw.text((W-60-text_width(draw, brand, bf), 62), brand, font=bf, fill=MUTED)

    # Title — normal title case, never forced to ALL CAPS.
    title = str(content.get("title", "")).strip()
    tf = fit_font(title, 930, 56, 34, True)
    draw.text((55, 112), title, font=tf, fill=TEXT)

    tagline = str(content.get("tagline", "")).strip()
    sub_y = 112 + tf.size + 8
    sf = fit_font(tagline, 900, 18, 12, False)
    draw.text((55, sub_y), tagline, font=sf, fill=BLUE)
    draw.line((55, sub_y+sf.size+10, W-55, sub_y+sf.size+10), fill=PURPLE, width=2)

    # Overview
    y = sub_y + sf.size + 28
    rounded(draw, (55, y, W-55, y+145), radius=20, fill=PANEL, outline=BORDER, width=2)
    draw.text((78, y+17), "At a glance", font=font(21, True), fill=PURPLE)
    overview = str(content.get("overview", "")).strip()
    text_block(draw, (78, y+55), overview, fit_font(overview, 850, 17, 12, False),
               fill=TEXT, width=850, max_lines=4, gap=4)

    # Main architecture panel
    y += 163
    arch_h = 330
    rounded(draw, (55, y, W-55, y+arch_h), radius=22, fill=PANEL_ALT, outline=BORDER, width=2)
    arch = content.get("architecture") or {}
    arch_title = str(arch.get("label") or arch.get("title") or "How it works").strip()
    draw.text((78, y+17), arch_title.title(), font=font(23, True), fill=PURPLE)
    draw_topic_flow(draw, (75, y+60, W-75, y+arch_h-20), arch)

    # Key ideas
    y += arch_h + 18
    draw.text((55, y), "Key ideas", font=font(23, True), fill=PURPLE)
    y += 38

    ideas = content.get("key_ideas") or []
    idea_h = 104
    gap = 12
    card_w = (W-110-gap)//2
    for i, idea in enumerate(ideas[:4]):
        x = 55+(i%2)*(card_w+gap)
        yy = y+(i//2)*(idea_h+gap)
        if isinstance(idea, dict):
            draw_key_card(draw, (x,yy,x+card_w,yy+idea_h), idea,
                          [BLUE, GREEN, ORANGE, PURPLE][i%4])

    y += 2*(idea_h+gap)-gap+16

    # Examples / failure impact side-by-side
    panel_h = 190
    left = (55, y, 520, y+panel_h)
    right = (540, y, W-55, y+panel_h)
    rounded(draw, left, radius=20, fill=(255,255,255), outline=BORDER, width=2)
    rounded(draw, right, radius=20, fill=(255,255,255), outline=BORDER, width=2)

    example_title = str(content.get("example_title","Example")).title()
    draw.text((74,y+15), example_title, font=font(19,True), fill=ORANGE)
    rows = content.get("example_rows") or []
    yy = y+52
    for row in rows[:3]:
        if isinstance(row,(list,tuple)):
            vals = [str(v) for v in row[:2]]
        else:
            vals = [str(row), ""]
        rounded(draw,(74,yy,174,yy+34),radius=9,fill=(255,255,255),outline=ORANGE,width=1)
        draw.text((86,yy+9),vals[0],font=fit_font(vals[0],80,11,8,True),fill=ORANGE)
        text_block(draw,(188,yy+8),vals[1],fit_font(vals[1],280,11,8,False),fill=TEXT,width=280,max_lines=1)
        yy += 42

    failure_title = str(content.get("failure_title","Failure / Impact")).title()
    draw.text((560,y+15), failure_title, font=font(19,True), fill=GREEN)
    before = content.get("failure_before") or []
    after = content.get("failure_after") or []
    yy = y+53
    for i in range(min(3,max(len(before),len(after)))):
        b = before[i] if i<len(before) else ["",""]
        a = after[i] if i<len(after) else ["",""]
        left_text = " → ".join(map(str,b[:2]))
        right_text = " → ".join(map(str,a[:2]))
        draw.text((560,yy), left_text, font=fit_font(left_text,170,10,8,False), fill=MUTED)
        draw.text((738,yy), "→", font=font(15,True), fill=GREEN)
        draw.text((765,yy), right_text, font=fit_font(right_text,185,10,8,False), fill=TEXT)
        yy += 38

    y += panel_h + 18

    # Best practices and use cases
    bottom_h = H-80-y
    col_gap=16
    col_w=(W-110-col_gap)//2
    best = content.get("best_practices") or []
    cases = content.get("use_cases") or []
    draw_simple_list(draw,(55,y,55+col_w,y+bottom_h),"Best practices",best,BLUE)
    draw_simple_list(draw,(55+col_w+col_gap,y,W-55,y+bottom_h),"Use cases",cases,PURPLE)

    # Footer
    draw.text((55,H-50),"CodeWithKambojShubham",font=font(17,True),fill=TEXT)
    draw.text((W-300,H-50),"Learn • Build • Grow",font=font(13,False),fill=MUTED)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Export high-resolution 9:15 artwork (2160x3600).
    # Lanczos gives the cleanest available raster upscale for the existing
    # composition and keeps text/shapes significantly sharper when zoomed.
    hd = img.resize((OUTPUT_W, OUTPUT_H), Image.Resampling.LANCZOS)
    hd.save(
        out,
        "PNG",
        optimize=True,
        compress_level=6,
        dpi=(300, 300),
    )

    return str(out)
