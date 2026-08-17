from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1800
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
    candidates = []
    if bold:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def gradient_background():
    img = Image.new("RGB", (W, H), BG)
    px = img.load()
    for y in range(H):
        for x in range(W):
            glow = max(0, 1 - ((x-W*0.72)**2 + (y-H*0.10)**2) / (W*W*0.9))
            r = int(8 + 22*glow)
            g = int(9 + 10*glow)
            b = int(18 + 36*glow)
            px[x, y] = (r, g, b)
    return img


def rounded(draw, box, radius=24, fill=PANEL, outline=BORDER, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap_lines(text, width_chars):
    import textwrap
    return textwrap.wrap(text, width=width_chars) or [""]


def text_block(draw, xy, text, fnt, fill=WHITE, width=60, gap=5, max_lines=None):
    x, y = xy
    lines = wrap_lines(text, width)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + gap
    return y


def glow_circle(img, center, radius, color):
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    x, y = center
    d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=(*color, 80))
    layer = layer.filter(ImageFilter.GaussianBlur(radius//2))
    img.alpha_composite(layer)


def node(draw, box, label, color=PURPLE, sub=None):
    rounded(draw, box, radius=14, fill=(20,19,40), outline=color, width=2)
    x1, y1, x2, y2 = box
    f = font(18, True)
    tw = draw.textbbox((0,0), label, font=f)
    draw.text(((x1+x2-(tw[2]-tw[0]))/2, y1+24), label, font=f, fill=color)
    if sub:
        fs = font(13, False)
        tw2 = draw.textbbox((0,0), sub, font=fs)
        draw.text(((x1+x2-(tw2[2]-tw2[0]))/2, y2-32), sub, font=fs, fill=MUTED)


def arrow(draw, p1, p2, color=BLUE, width=4):
    import math
    draw.line([p1,p2], fill=color, width=width)
    ang = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
    length = 16
    pts = [
        p2,
        (p2[0]-length*math.cos(ang-0.45), p2[1]-length*math.sin(ang-0.45)),
        (p2[0]-length*math.cos(ang+0.45), p2[1]-length*math.sin(ang+0.45)),
    ]
    draw.polygon(pts, fill=color)


def draw_flow(img, draw, kind, area):
    x1,y1,x2,y2 = area
    if kind == "producer_topic_consumers":
        node(draw, (x1+8,y1+32,x1+125,y1+96), "PRODUCER", BLUE)
        node(draw, (x1+158,y1+32,x1+360,y1+96), "KAFKA TOPIC", PURPLE, "3 PARTITIONS")
        node(draw, (x1+40,y1+142,x1+140,y1+198), "P0", PURPLE)
        node(draw, (x1+170,y1+142,x1+270,y1+198), "P1", PURPLE)
        node(draw, (x1+300,y1+142,x1+400,y1+198), "P2", PURPLE)
        node(draw, (x1+20,y1+265,x1+138,y1+328), "CONSUMER 1", BLUE, "G1")
        node(draw, (x1+156,y1+265,x1+274,y1+328), "CONSUMER 2", GREEN, "G1")
        node(draw, (x1+292,y1+265,x1+410,y1+328), "CONSUMER 3", ORANGE, "G1")
        arrow(draw, (x1+125,y1+64),(x1+158,y1+64))
        arrow(draw, (x1+235,y1+96),(x1+90,y1+142), PURPLE)
        arrow(draw, (x1+255,y1+96),(x1+220,y1+142), PURPLE)
        arrow(draw, (x1+275,y1+96),(x1+350,y1+142), PURPLE)
        arrow(draw, (x1+90,y1+198),(x1+80,y1+265), BLUE)
        arrow(draw, (x1+220,y1+198),(x1+215,y1+265), GREEN)
        arrow(draw, (x1+350,y1+198),(x1+350,y1+265), ORANGE)
    elif kind == "request_cache_db":
        node(draw,(x1+20,y1+120,x1+150,y1+200),"CLIENT",BLUE)
        node(draw,(x1+250,y1+45,x1+410,y1+125),"REDIS",PURPLE,"CACHE")
        node(draw,(x1+250,y1+225,x1+410,y1+305),"DATABASE",GREEN)
        node(draw,(x1+520,y1+120,x1+650,y1+200),"API",CYAN)
        arrow(draw,(x1+150,y1+160),(x1+250,y1+85),BLUE)
        arrow(draw,(x1+150,y1+160),(x1+250,y1+265),BLUE)
        arrow(draw,(x1+410,y1+85),(x1+520,y1+160),PURPLE)
        arrow(draw,(x1+410,y1+265),(x1+520,y1+160),GREEN)
    elif kind == "gateway_services":
        node(draw,(x1+30,y1+125,x1+180,y1+205),"GATEWAY",BLUE)
        node(draw,(x1+260,y1+30,x1+425,y1+100),"USER",PURPLE)
        node(draw,(x1+260,y1+150,x1+425,y1+220),"ORDER",GREEN)
        node(draw,(x1+260,y1+270,x1+425,y1+340),"PAYMENT",ORANGE)
        arrow(draw,(x1+180,y1+165),(x1+260,y1+65),BLUE)
        arrow(draw,(x1+180,y1+165),(x1+260,y1+185),BLUE)
        arrow(draw,(x1+180,y1+165),(x1+260,y1+305),BLUE)
    else:
        node(draw,(x1+20,y1+145,x1+160,y1+215),"CLIENT",BLUE)
        node(draw,(x1+240,y1+145,x1+400,y1+215),"SERVICE",PURPLE)
        node(draw,(x1+480,y1+145,x1+640,y1+215),"DATABASE",GREEN)
        arrow(draw,(x1+160,y1+180),(x1+240,y1+180),BLUE)
        arrow(draw,(x1+400,y1+180),(x1+480,y1+180),PURPLE)
