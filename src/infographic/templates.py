from __future__ import annotations

from textwrap import wrap

INK = (38, 43, 55)
MUTED = (92, 99, 115)
BORDER = (207, 212, 224)
CARD = (248, 249, 253)
ACCENT = (92, 74, 195)
WHITE = (255, 255, 255)


def add_title(draw, title, font, x, y, max_width_chars=24):
    lines = wrap(title.upper(), width=max_width_chars)
    current_y = y
    for line in lines[:3]:
        draw.text((x, current_y), line, font=font, fill=INK)
        current_y += font.size + 8
    return current_y


def render_topic_card(draw, title, category, summary, key_points, fonts):
    title_font, category_font, section_font, body_font = fonts
    draw.rounded_rectangle((60, 60, 1020, 1740), radius=36, fill=WHITE, outline=BORDER, width=4)
    draw.rounded_rectangle((92, 98, 988, 155), radius=20, fill=(241, 239, 255))
    draw.text((118, 112), category.upper(), font=category_font, fill=ACCENT)

    y = add_title(draw, title, title_font, 110, 200)
    y += 30
    draw.rounded_rectangle((110, y, 970, y + 250), radius=28, fill=CARD, outline=BORDER, width=2)
    draw.text((140, y + 30), "AT A GLANCE", font=section_font, fill=ACCENT)

    body_y = y + 90
    for line in wrap(summary, width=58):
        draw.text((140, body_y), line, font=body_font, fill=INK)
        body_y += body_font.size + 10

    y += 300
    draw.text((110, y), "KEY CONCEPTS", font=section_font, fill=ACCENT)
    y += 72
    for point in key_points[:5]:
        draw.ellipse((114, y + 9, 132, y + 27), fill=ACCENT)
        lines = wrap(point, width=58)
        for line in lines:
            draw.text((152, y), line, font=body_font, fill=INK)
            y += body_font.size + 6
        y += 16

    draw.line((110, 1605, 970, 1605), fill=BORDER, width=2)
    draw.text((110, 1640), "TECH CHEAT SHEET • AUTO-GENERATED", font=category_font, fill=MUTED)
