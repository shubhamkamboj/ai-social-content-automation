from __future__ import annotations

from math import atan2, cos, sin, pi

from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1800

BG = (255, 255, 255)
PANEL = (248, 249, 252)
PANEL_ALT = (242, 245, 250)
TEXT = (28, 31, 42)
WHITE = TEXT
MUTED = (92, 99, 118)
BORDER = (184, 190, 204)
BLUE = (58, 141, 255)
PURPLE = (132, 84, 240)
GREEN = (52, 194, 141)
ORANGE = (245, 145, 49)
CYAN = (48, 185, 210)


def font(size: int, bold: bool = False):
    from PIL import ImageFont
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def fit_font(text: str, max_width: int, start_size: int, min_size: int = 12, bold: bool = False):
    from PIL import ImageFont
    # No draw dependency; size based on approximate text width and exact PIL measurement.
    size = start_size
    while size > min_size:
        f = font(size, bold)
        bbox = f.getbbox(str(text))
        if bbox[2] - bbox[0] <= max_width:
            return f
        size -= 1
    return font(min_size, bold)


def text_width(draw, text, fnt):
    b = draw.textbbox((0, 0), str(text), font=fnt)
    return b[2] - b[0]


def rounded(draw, box, radius=24, fill=PANEL, outline=BORDER, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_block(draw, xy, text, fnt, fill=TEXT, width=400, gap=4, max_lines=4):
    x, y = xy
    words = str(text).split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if not cur or text_width(draw, trial, fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + gap
    return y


def draw_arrow(draw, start, end, color, width=4):
    draw.line([start, end], fill=color, width=width)
    angle = atan2(end[1] - start[1], end[0] - start[0])
    size = 11
    pts = [
        end,
        (end[0] - size*cos(angle-pi/6), end[1] - size*sin(angle-pi/6)),
        (end[0] - size*cos(angle+pi/6), end[1] - size*sin(angle+pi/6)),
    ]
    draw.polygon(pts, fill=color)


def draw_chip(draw, box, label, color, small=False):
    rounded(draw, box, radius=11 if small else 14, fill=(255,255,255), outline=color, width=2)
    f = fit_font(label, box[2]-box[0]-16, 14 if small else 16, 10, True)
    bbox = draw.textbbox((0,0), label, font=f)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text(((box[0]+box[2]-tw)/2, (box[1]+box[3]-th)/2-bbox[1]), label, font=f, fill=color)


def draw_background():
    img = Image.new("RGB", (W, H), BG)
    # Subtle soft gradient-like glow, still predominantly white.
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-120, -120, 420, 420), fill=(148, 110, 255, 28))
    gd.ellipse((760, 80, 1180, 520), fill=(64, 156, 255, 22))
    gd.ellipse((380, 1350, 900, 1920), fill=(90, 220, 177, 18))
    glow = glow.filter(ImageFilter.GaussianBlur(100))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")


def draw_topic_flow(draw, box, architecture: dict):
    x1, y1, x2, y2 = box
    nodes = architecture.get("nodes") or []
    if not nodes:
        nodes = [
            {"label": "Input", "sub": ""},
            {"label": "Process", "sub": ""},
            {"label": "Output", "sub": ""},
        ]

    # Keep labels short enough for visual layout.
    colors = [BLUE, PURPLE, GREEN, ORANGE, CYAN]
    n = min(len(nodes), 6)
    nodes = nodes[:n]

    arch_type = str(architecture.get("type", "linear_flow")).lower()
    if arch_type in {"comparison", "branching_flow"} and n >= 3:
        # Center hub with two/three branches.
        hub_w, hub_h = 170, 72
        cx = (x1+x2)//2
        hub = (cx-hub_w//2, y1+95, cx+hub_w//2, y1+95+hub_h)
        draw_chip(draw, hub, str(nodes[0]["label"]), colors[0])
        branch = nodes[1:5]
        start_y = y1 + 20
        step = max(86, (y2-y1-80)//max(1,len(branch)))
        for i, node in enumerate(branch):
            yy = start_y + i*step
            bx = (x1+30, yy, x1+255, yy+64) if i % 2 == 0 else (x2-255, yy, x2-30, yy+64)
            color = colors[(i+1)%len(colors)]
            draw_chip(draw, bx, str(node["label"]), color)
            draw_arrow(
                draw,
                (hub[0] if bx[2] < hub[0] else hub[2], (hub[1]+hub[3])//2),
                (bx[2] if bx[2] < hub[0] else bx[0], (bx[1]+bx[3])//2),
                color,
                3
            )
        return

    if arch_type in {"layered_architecture"}:
        layer_h = min(62, (y2-y1-60)//n)
        for i, node in enumerate(nodes):
            yy = y1+30+i*(layer_h+8)
            color = colors[i%len(colors)]
            rounded(draw, (x1+60, yy, x2-60, yy+layer_h), radius=15, fill=(255,255,255), outline=color, width=2)
            label = str(node["label"])
            sub = str(node.get("sub",""))
            draw_chip(draw, (x1+75, yy+9, x1+250, yy+layer_h-9), label, color, small=True)
            if sub:
                text_block(draw, (x1+270, yy+15), sub, fit_font(sub, x2-x1-340, 14, 10, False),
                           fill=MUTED, width=x2-x1-340, max_lines=2)
        return

    # Default linear visual; the actual Gemini nodes are the content.
    total_w = x2-x1-70
    gap = 28
    node_w = max(125, min(190, int((total_w-gap*(n-1))/n)))
    y = (y1+y2)//2 - 38
    start_x = x1 + (x2-x1-(node_w*n+gap*(n-1)))//2
    node_boxes = []

    for i, node in enumerate(nodes):
        xx = start_x+i*(node_w+gap)
        color = colors[i%len(colors)]
        box2 = (xx, y, xx+node_w, y+76)
        draw_chip(draw, box2, str(node["label"]), color)
        sub = str(node.get("sub","")).strip()
        if sub:
            text_block(draw, (xx+8, y+84), sub, fit_font(sub, node_w-16, 11, 9, False),
                       fill=MUTED, width=node_w-16, max_lines=2)
        node_boxes.append(box2)
        if i:
            draw_arrow(draw, (node_boxes[i-1][2], y+38), (box2[0], y+38), color, 3)

    # If Gemini supplied explicit connection semantics, show a small legend.
    connections = architecture.get("connections") or []
    if connections:
        summary = "  •  ".join(str(c) for c in connections[:3])
        f = fit_font(summary, x2-x1-40, 12, 9, False)
        text_block(draw, (x1+20, y2-34), summary, f, fill=MUTED, width=x2-x1-40, max_lines=1)


def draw_key_card(draw, box, idea, color):
    x1,y1,x2,y2 = box
    rounded(draw, box, radius=18, fill=(255,255,255), outline=BORDER, width=2)
    draw.ellipse((x1+15,y1+16,x1+35,y1+36), outline=color, width=2)
    title = str(idea.get("title","")).strip().title()
    desc = str(idea.get("description","")).strip()
    draw.text((x1+48,y1+13), title, font=fit_font(title, x2-x1-62, 15, 11, True), fill=color)
    text_block(draw, (x1+15,y1+45), desc, fit_font(desc, x2-x1-30, 12, 9, False),
               fill=MUTED, width=x2-x1-30, max_lines=3, gap=2)


def draw_simple_list(draw, box, title, items, accent):
    x1,y1,x2,y2 = box
    rounded(draw, box, radius=20, fill=(255,255,255), outline=BORDER, width=2)
    draw.text((x1+18,y1+16), str(title).title(), font=font(22,True), fill=accent)
    y = y1+56
    for i, item in enumerate(items[:4]):
        color = [accent, BLUE, GREEN, ORANGE][i%4]
        draw.ellipse((x1+18,y+6,x1+31,y+19), outline=color, width=2)
        text_block(draw, (x1+42,y), str(item), fit_font(str(item), x2-x1-58, 13, 10, False),
                   fill=TEXT, width=x2-x1-58, max_lines=2, gap=2)
        y += 42
