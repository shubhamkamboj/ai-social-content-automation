from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1800
SAFE_L, SAFE_R = 60, 1020
BG = (8, 9, 18)
PANEL = (18, 17, 35)
PANEL2 = (23, 21, 43)
BORDER = (74, 56, 126)
WHITE = (244, 243, 250)
MUTED = (175, 175, 196)
BLUE = (60, 156, 255)
PURPLE = (159, 73, 255)
GREEN = (84, 218, 130)
ORANGE = (255, 173, 56)
CYAN = (68, 227, 220)


def font(size: int, bold: bool=False):
    candidates = (
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ] if bold else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit_font(text: str, max_width: int, start_size: int, min_size: int = 10, bold: bool = False):
    size = start_size
    while size > min_size:
        f = font(size, bold)
        if text_bbox_width(text, f) <= max_width:
            return f
        size -= 1
    return font(min_size, bold)


def text_bbox_width(text: str, fnt) -> int:
    dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    box = dummy.textbbox((0, 0), text, font=fnt)
    return max(0, box[2] - box[0])


def gradient_background():
    img = Image.new("RGB", (W, H), BG)
    px = img.load()
    for y in range(H):
        for x in range(W):
            glow = max(0, 1 - ((x-W*0.72)**2 + (y-H*0.10)**2) / (W*W*0.9))
            px[x, y] = (
                int(8 + 22*glow),
                int(9 + 10*glow),
                int(18 + 36*glow),
            )
    return img


def rounded(draw, box, radius=24, fill=PANEL, outline=BORDER, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap_by_pixels(text: str, fnt, max_width: int) -> list[str]:
    words = str(text).split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if text_bbox_width(trial, fnt) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def text_block(draw, xy, text, fnt, fill=WHITE, width=60, gap=5, max_lines=None):
    x, y = xy
    lines = wrap_by_pixels(text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        # Last-resort clamp: text is always drawn from the safe left edge.
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + gap
    return y


def draw_centered(draw, box, text, fnt, fill=WHITE, max_lines=2, line_gap=3):
    x1, y1, x2, y2 = box
    max_w = max(10, x2-x1-16)
    lines = wrap_by_pixels(text, fnt, max_w)[:max_lines]
    total_h = len(lines)*fnt.size + max(0, len(lines)-1)*line_gap
    y = y1 + max(0, (y2-y1-total_h)//2)
    for line in lines:
        w = text_bbox_width(line, fnt)
        draw.text((x1 + (x2-x1-w)//2, y), line, font=fnt, fill=fill)
        y += fnt.size + line_gap


def glow_circle(img, center, radius, color):
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    x, y = center
    d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=(*color, 80))
    layer = layer.filter(ImageFilter.GaussianBlur(radius//2))
    img.alpha_composite(layer)


def safe_node(draw, box, label, color=PURPLE, sub=None):
    x1, y1, x2, y2 = box
    rounded(draw, box, radius=13, fill=(20,19,40), outline=color, width=2)
    label_font = fit_font(label, x2-x1-12, 15, 10, bold=True)
    draw_centered(draw, (x1+5, y1+7, x2-5, y2-25 if sub else y2-6), label, label_font, color, max_lines=2)

    if sub:
        sub_font = fit_font(sub, x2-x1-10, 11, 8, bold=False)
        draw_centered(draw, (x1+4, y2-24, x2-4, y2-4), sub, sub_font, MUTED, max_lines=1)


def arrow(draw, p1, p2, color=BLUE, width=3):
    import math
    draw.line([p1, p2], fill=color, width=width)
    ang = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
    length = 10
    pts = [
        p2,
        (p2[0]-length*math.cos(ang-0.45), p2[1]-length*math.sin(ang-0.45)),
        (p2[0]-length*math.cos(ang+0.45), p2[1]-length*math.sin(ang+0.45)),
    ]
    draw.polygon(pts, fill=color)


def _flow_canvas(area):
    x1, y1, x2, y2 = area
    return Image.new("RGBA", (max(1, x2-x1), max(1, y2-y1)), (0,0,0,0))


def draw_flow(img, draw, kind, area):
    """
    Render every architecture diagram inside a dedicated fixed-size layer.
    The layer is cropped to the panel before compositing, so no diagram
    primitive can ever escape the parent frame.
    """
    x1, y1, x2, y2 = area
    layer = _flow_canvas(area)
    ld = ImageDraw.Draw(layer)
    w, h = layer.size

    if kind == "producer_topic_consumers":
        safe_node(ld, (8, 25, 105, 75), "PRODUCER", BLUE)
        safe_node(ld, (128, 25, 282, 75), "KAFKA TOPIC", PURPLE, "3 PARTITIONS")

        pw = 78
        for i, x in enumerate([28, 125, 222]):
            safe_node(ld, (x, 108, x+pw, 156), f"P{i}", PURPLE)

        cw = 102
        for i, x in enumerate([6, 126, 246]):
            safe_node(ld, (x, 225, x+cw, 276), f"CONSUMER {i+1}", [BLUE,GREEN,ORANGE][i], "GROUP G1")

        arrow(ld, (105,50), (128,50), BLUE)
        for sx, tx, c in [(205,67,PURPLE),(205,164,PURPLE),(205,261,PURPLE)]:
            arrow(ld, (sx,75),(tx,108), c)
        for sx, tx, c in [(67,156,BLUE),(164,156,GREEN),(261,156,ORANGE)]:
            arrow(ld, (sx,156),(tx,225), c)

    elif kind == "request_cache_db":
        safe_node(ld,(12,135,105,188),"CLIENT",BLUE)
        safe_node(ld,(150,45,285,98),"REDIS",PURPLE,"CACHE")
        safe_node(ld,(150,225,285,278),"DATABASE",GREEN)
        safe_node(ld,(330,135,420,188),"API",CYAN)
        arrow(ld,(105,161),(150,72),BLUE)
        arrow(ld,(105,161),(150,251),BLUE)
        arrow(ld,(285,72),(330,161),PURPLE)
        arrow(ld,(285,251),(330,161),GREEN)

    elif kind == "gateway_services":
        safe_node(ld,(12,140,112,195),"GATEWAY",BLUE)
        for y, label, color in [(35,"USER",PURPLE),(138,"ORDER",GREEN),(241,"PAYMENT",ORANGE)]:
            safe_node(ld,(205,y,370,y+62),label,color)
            arrow(ld,(112,167),(205,y+31),BLUE)

    elif kind == "client_controller_service_repo":
        boxes = [
            (5,145,92,200,"CLIENT",BLUE),
            (118,145,220,200,"SERVICE",PURPLE),
            (247,145,350,200,"DATABASE",GREEN),
        ]
        for b in boxes:
            safe_node(ld,b[:4],b[4],b[5])
        arrow(ld,(92,172),(118,172),BLUE)
        arrow(ld,(220,172),(247,172),PURPLE)

    elif kind == "user_cloud_service_db":
        boxes = [
            (5,140,95,195,"USER",BLUE),
            (125,140,225,195,"AWS",PURPLE),
            (255,70,410,125,"SERVICE",CYAN),
            (255,210,410,265,"DATABASE",GREEN),
        ]
        for b in boxes:
            safe_node(ld,b[:4],b[4],b[5])
        arrow(ld,(95,167),(125,167),BLUE)
        arrow(ld,(225,167),(255,98),PURPLE)
        arrow(ld,(225,167),(255,237),PURPLE)

    elif kind == "api_document_index":
        boxes = [
            (5,145,92,200,"API",BLUE),
            (125,95,250,150,"DOCUMENT",PURPLE),
            (125,210,250,265,"INDEX",CYAN),
            (285,145,410,200,"MONGO",GREEN),
        ]
        for b in boxes:
            safe_node(ld,b[:4],b[4],b[5])
        arrow(ld,(92,172),(125,123),BLUE)
        arrow(ld,(92,172),(125,237),BLUE)
        arrow(ld,(250,123),(285,172),PURPLE)
        arrow(ld,(250,237),(285,172),CYAN)

    elif kind == "code_image_container":
        boxes = [
            (5,145,92,200,"CODE",BLUE),
            (125,145,225,200,"IMAGE",PURPLE),
            (258,145,405,200,"CONTAINER",GREEN),
        ]
        for b in boxes:
            safe_node(ld,b[:4],b[4],b[5])
        arrow(ld,(92,172),(125,172),BLUE)
        arrow(ld,(225,172),(258,172),PURPLE)

    elif kind == "api_sql_query_db":
        boxes = [
            (5,145,92,200,"API",BLUE),
            (125,145,225,200,"QUERY",PURPLE),
            (258,145,405,200,"SQL DB",GREEN),
        ]
        for b in boxes:
            safe_node(ld,b[:4],b[4],b[5])
        arrow(ld,(92,172),(125,172),BLUE)
        arrow(ld,(225,172),(258,172),PURPLE)

    elif kind == "client_auth_api":
        boxes = [
            (5,145,95,200,"CLIENT",BLUE),
            (128,72,255,127,"AUTH",PURPLE),
            (128,218,255,273,"TOKEN",CYAN),
            (290,145,410,200,"API",GREEN),
        ]
        for b in boxes:
            safe_node(ld,b[:4],b[4],b[5])
        arrow(ld,(95,172),(128,99),BLUE)
        arrow(ld,(95,172),(128,245),BLUE)
        arrow(ld,(255,245),(290,172),CYAN)
        arrow(ld,(255,99),(290,172),PURPLE)

    else:
        boxes = [
            (5,145,92,200,"CLIENT",BLUE),
            (135,145,245,200,"SERVICE",PURPLE),
            (285,145,410,200,"STORE",GREEN),
        ]
        for b in boxes:
            safe_node(ld,b[:4],b[4],b[5])
        arrow(ld,(92,172),(135,172),BLUE)
        arrow(ld,(245,172),(285,172),PURPLE)

    img.alpha_composite(layer, (x1, y1))
