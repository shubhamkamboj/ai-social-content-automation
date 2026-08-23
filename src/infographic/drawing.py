from __future__ import annotations

from math import atan2, cos, sin, pi

from PIL import Image, ImageDraw, ImageFilter


W, H = 1080, 1800

BG = (255, 255, 255)
PANEL = (248, 249, 252)
PANEL_ALT = (244, 246, 250)
TEXT = (25, 28, 38)
WHITE = TEXT
MUTED = (93, 99, 116)
LINE = (178, 184, 198)
DARK_LINE = (214, 218, 226)


def font(size: int, bold: bool = False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
        if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in paths:
        try:
            from PIL import ImageFont
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue

    from PIL import ImageFont
    return ImageFont.load_default()


def fit_font(draw, text: str, max_width: int, start_size: int, min_size: int = 22, bold: bool = False):
    size = start_size
    while size > min_size:
        fnt = font(size, bold)
        bbox = draw.textbbox((0, 0), text, font=fnt)
        if bbox[2] - bbox[0] <= max_width:
            return fnt
        size -= 2
    return font(min_size, bold)


def rounded(draw, box, radius=24, fill=PANEL, outline=LINE, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_text(
    draw,
    xy,
    text,
    fnt,
    fill=TEXT,
    max_width=400,
    line_gap=5,
    max_lines=None,
):
    x, y = xy
    words = text.split()
    lines = []
    line = ""

    for word in words:
        candidate = f"{line} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=fnt)
        if bbox[2] - bbox[0] <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word

    if line:
        lines.append(line)

    if max_lines:
        lines = lines[:max_lines]

    for current in lines:
        draw.text((x, y), current, font=fnt, fill=fill)
        y += fnt.size + line_gap

    return y


def draw_centered(draw, box, text, fnt, fill=TEXT):
    x1, y1, x2, y2 = box
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(
        ((x1 + x2 - tw) / 2, (y1 + y2 - th) / 2 - bbox[1]),
        text,
        font=fnt,
        fill=fill,
    )


def draw_arrow(draw, start, end, color, width=4):
    draw.line([start, end], fill=color, width=width)
    angle = atan2(end[1] - start[1], end[0] - start[0])
    size = 12
    points = [
        end,
        (
            end[0] - size * cos(angle - pi / 6),
            end[1] - size * sin(angle - pi / 6),
        ),
        (
            end[0] - size * cos(angle + pi / 6),
            end[1] - size * sin(angle + pi / 6),
        ),
    ]
    draw.polygon(points, fill=color)


def draw_node(draw, box, label, color, sub=None):
    rounded(
        draw,
        box,
        radius=14,
        fill=(255, 255, 255),
        outline=color,
        width=2,
    )
    x1, y1, x2, y2 = box
    fnt = fit_font(draw, label, x2 - x1 - 18, 20, 12, True)
    draw_centered(draw, (x1 + 8, y1 + 8, x2 - 8, y1 + 42), label, fnt, color)

    if sub:
        sf = fit_font(draw, sub, x2 - x1 - 16, 13, 10, False)
        draw_centered(
            draw,
            (x1 + 8, y2 - 29, x2 - 8, y2 - 6),
            sub,
            sf,
            MUTED,
        )


def draw_icon(draw, center, color, kind="dot", size=22):
    x, y = center

    if kind == "people":
        draw.ellipse(
            (x - size, y - size, x - 2, y + 2),
            outline=color,
            width=3,
        )
        draw.ellipse(
            (x + 2, y - size, x + size, y + 2),
            outline=color,
            width=3,
        )
        draw.line(
            (x - size - 4, y + 10, x + size + 4, y + 10),
            fill=color,
            width=3,
        )
    elif kind == "flow":
        draw.line(
            (x - size, y, x + size, y),
            fill=color,
            width=4,
        )
        draw.polygon(
            [
                (x + size, y),
                (x + size - 10, y - 8),
                (x + size - 10, y + 8),
            ],
            fill=color,
        )
    elif kind == "warning":
        draw.polygon(
            [
                (x, y - size),
                (x - size, y + size),
                (x + size, y + size),
            ],
            outline=color,
        )
        draw.line((x, y - 7, x, y + 8), fill=color, width=3)
        draw.ellipse((x - 2, y + 13, x + 2, y + 17), fill=color)
    else:
        draw.ellipse(
            (x - size, y - size, x + size, y + size),
            outline=color,
            width=3,
        )


def draw_section_header(draw, x, y, title, color):
    draw.text((x, y), title, font=font(26, True), fill=color)


def draw_kafka_architecture(draw, box, primary, secondary, accent):
    x1, y1, x2, y2 = box

    draw_icon(draw, (x1 + 68, y1 + 165), secondary, "flow", 22)
    draw.text(
        (x1 + 25, y1 + 205),
        "Producer",
        font=font(18, True),
        fill=TEXT,
    )
    draw_arrow(
        draw,
        (x1 + 100, y1 + 165),
        (x1 + 165, y1 + 165),
        secondary,
    )

    rounded(
        draw,
        (x1 + 165, y1 + 75, x1 + 430, y1 + 295),
        radius=22,
        fill=(255, 255, 255),
        outline=primary,
        width=2,
    )
    draw.text(
        (x1 + 190, y1 + 94),
        "Kafka Topic",
        font=font(22, True),
        fill=primary,
    )

    part_y = [y1 + 138, y1 + 195, y1 + 252]
    colors = [primary, secondary, accent]

    for idx, yy in enumerate(part_y):
        rounded(
            draw,
            (x1 + 195, yy, x1 + 400, yy + 42),
            radius=10,
            fill=(251, 252, 254),
            outline=colors[idx],
            width=2,
        )
        draw.text(
            (x1 + 215, yy + 11),
            f"Partition {idx}",
            font=font(14, True),
            fill=TEXT,
        )

    rounded(
        draw,
        (x1 + 495, y1 + 50, x1 + 755, y1 + 320),
        radius=22,
        fill=(255, 255, 255),
        outline=accent,
        width=2,
    )
    draw.text(
        (x1 + 525, y1 + 72),
        "Consumer Group",
        font=font(22, True),
        fill=accent,
    )

    consumer_boxes = [
        (x1 + 525, y1 + 120, x1 + 730, y1 + 168, "Consumer 1", primary),
        (x1 + 525, y1 + 184, x1 + 730, y1 + 232, "Consumer 2", accent),
        (x1 + 525, y1 + 248, x1 + 730, y1 + 296, "Consumer 3", secondary),
    ]

    for bx1, by1, bx2, by2, label, color in consumer_boxes:
        rounded(
            draw,
            (bx1, by1, bx2, by2),
            radius=10,
            fill=(255, 255, 255),
            outline=color,
            width=2,
        )
        draw_centered(
            draw,
            (bx1 + 5, by1 + 4, bx2 - 5, by2 - 4),
            label,
            font(15, True),
            TEXT,
        )

    for yy, color, target_y in zip(part_y, colors, [144, 208, 272]):
        draw_arrow(
            draw,
            (x1 + 430, yy + 20),
            (x1 + 495, y1 + target_y),
            color,
            3,
        )

    rounded(
        draw,
        (x1 + 790, y1 + 85, x2 - 20, y1 + 285),
        radius=20,
        fill=(255, 255, 255),
        outline=secondary,
        width=2,
    )
    draw.text(
        (x1 + 815, y1 + 108),
        "Group",
        font=font(19, True),
        fill=secondary,
    )
    draw.text(
        (x1 + 815, y1 + 134),
        "Coordinator",
        font=font(19, True),
        fill=secondary,
    )
    draw_text(
        draw,
        (x1 + 815, y1 + 178),
        "Membership • assignments • rebalance",
        font(14),
        fill=MUTED,
        max_width=205,
        max_lines=3,
        line_gap=2,
    )
    draw_arrow(
        draw,
        (x1 + 755, y1 + 185),
        (x1 + 790, y1 + 185),
        accent,
        3,
    )


def draw_generic_flow(draw, box, primary, secondary, accent, kind):
    x1, y1, x2, y2 = box

    labels = {
        "java_runtime": [
            ("Source", secondary),
            ("Bytecode", primary),
            ("JVM", accent),
            ("JIT", primary),
        ],
        "spring_request": [
            ("Client", secondary),
            ("Filters", primary),
            ("Service", accent),
            ("Database", secondary),
        ],
        "aws_flow": [
            ("Client", secondary),
            ("API", primary),
            ("Compute", accent),
            ("Data", secondary),
        ],
        "redis_cache": [
            ("Client", secondary),
            ("Redis", primary),
            ("Database", accent),
            ("API", secondary),
        ],
        "sql_query": [
            ("Query", secondary),
            ("Index", primary),
            ("Table", accent),
            ("Result", secondary),
        ],
        "docker_container": [
            ("Code", secondary),
            ("Image", primary),
            ("Container", accent),
            ("App", secondary),
        ],
        "observability": [
            ("Alert", secondary),
            ("Trace", primary),
            ("Root Cause", accent),
            ("Fix", secondary),
        ],
        "generic": [
            ("Input", secondary),
            ("Process", primary),
            ("Output", accent),
            ("Impact", secondary),
        ],
    }

    items = labels.get(kind, labels["generic"])
    step = (x2 - x1 - 40) / len(items)
    boxes = []

    for i, (label, color) in enumerate(items):
        bx1 = int(x1 + 20 + i * step)
        bx2 = int(bx1 + step - 18)
        by1 = int(y1 + 120)
        by2 = int(y1 + 200)

        draw_node(
            draw,
            (bx1, by1, bx2, by2),
            label,
            color,
        )
        boxes.append((bx1, by1, bx2, by2))

        if i > 0:
            previous = boxes[i - 1]
            draw_arrow(
                draw,
                (previous[2], (previous[1] + previous[3]) // 2),
                (bx1, (by1 + by2) // 2),
                color,
                3,
            )


def draw_architecture(draw, box, content, palette):
    x1, y1, x2, y2 = box
    primary = palette["primary"]
    secondary = palette["secondary"]
    accent = palette["accent"]

    rounded(
        draw,
        box,
        radius=26,
        fill=PANEL_ALT,
        outline=LINE,
        width=2,
    )

    draw_section_header(
        draw,
        x1 + 28,
        y1 + 22,
        content["architecture"]["label"].title(),
        primary,
    )

    kind = content["architecture"]["type"]

    if kind == "kafka_consumer_group":
        draw_kafka_architecture(
            draw,
            (x1 + 25, y1 + 58, x2 - 25, y2 - 25),
            primary,
            secondary,
            accent,
        )
    else:
        draw_generic_flow(
            draw,
            (x1 + 25, y1 + 65, x2 - 25, y2 - 25),
            primary,
            secondary,
            accent,
            kind,
        )


def draw_key_idea_card(draw, box, title, desc, color):
    x1, y1, x2, y2 = box

    rounded(
        draw,
        box,
        radius=20,
        fill=PANEL,
        outline=LINE,
        width=2,
    )

    draw_icon(
        draw,
        (x1 + 38, y1 + 38),
        color,
        "dot",
        15,
    )

    draw.text(
        (x1 + 66, y1 + 18),
        title.title(),
        font=font(17, True),
        fill=color,
    )

    draw_text(
        draw,
        (x1 + 18, y1 + 62),
        desc,
        font(14),
        fill=TEXT,
        max_width=x2 - x1 - 36,
        max_lines=3,
        line_gap=3,
    )


def draw_example(draw, box, title, rows, primary, secondary, accent):
    x1, y1, x2, y2 = box

    rounded(
        draw,
        box,
        radius=22,
        fill=PANEL,
        outline=LINE,
        width=2,
    )

    draw_section_header(
        draw,
        x1 + 22,
        y1 + 20,
        title.title(),
        primary,
    )

    y = y1 + 72
    cols = [primary, secondary, accent]

    for idx, row in enumerate(rows[:4]):
        label, value = row
        color = cols[idx % len(cols)]

        rounded(
            draw,
            (x1 + 22, y, x1 + 112, y + 42),
            radius=10,
            fill=(251, 252, 254),
            outline=color,
            width=2,
        )

        draw_centered(
            draw,
            (x1 + 26, y + 3, x1 + 108, y + 39),
            label,
            font(14, True),
            TEXT,
        )

        draw_arrow(
            draw,
            (x1 + 115, y + 21),
            (x1 + 155, y + 21),
            color,
            2,
        )

        rounded(
            draw,
            (x1 + 165, y, x2 - 22, y + 42),
            radius=10,
            fill=(255, 255, 255),
            outline=color,
            width=2,
        )

        draw.text(
            (x1 + 182, y + 11),
            value,
            font=font(13, True),
            fill=TEXT,
        )

        y += 50


def draw_failure(
    draw,
    box,
    title,
    before,
    after,
    primary,
    secondary,
    accent,
):
    x1, y1, x2, y2 = box

    rounded(
        draw,
        box,
        radius=22,
        fill=PANEL_ALT,
        outline=LINE,
        width=2,
    )

    draw_section_header(
        draw,
        x1 + 22,
        y1 + 18,
        title.title(),
        accent,
    )

    draw.text(
        (x1 + 22, y1 + 58),
        "Before",
        font=font(15, True),
        fill=secondary,
    )

    y = y1 + 92

    for left, right in before[:3]:
        rounded(
            draw,
            (x1 + 22, y, x1 + 128, y + 38),
            radius=9,
            fill=(255, 255, 255),
            outline=secondary,
            width=2,
        )
        draw_centered(
            draw,
            (x1 + 25, y + 2, x1 + 125, y + 36),
            left,
            font(12, True),
            secondary,
        )
        draw.text(
            (x1 + 142, y + 9),
            right,
            font=font(12, False),
            fill=TEXT,
        )
        y += 43

    mid = (x1 + x2) // 2

    draw.text(
        (mid + 10, y1 + 58),
        "After",
        font=font(15, True),
        fill=accent,
    )

    y = y1 + 92

    for left, right in after[:3]:
        rounded(
            draw,
            (mid + 10, y, mid + 116, y + 38),
            radius=9,
            fill=(255, 255, 255),
            outline=accent,
            width=2,
        )
        draw_centered(
            draw,
            (mid + 13, y + 2, mid + 113, y + 36),
            left,
            font(12, True),
            accent,
        )
        draw.text(
            (mid + 130, y + 9),
            right,
            font=font(12, False),
            fill=TEXT,
        )
        y += 43


def draw_practice_card(draw, box, text, color):
    rounded(
        draw,
        box,
        radius=18,
        fill=PANEL,
        outline=color,
        width=2,
    )

    draw_icon(
        draw,
        (box[0] + 24, box[1] + 24),
        color,
        "dot",
        11,
    )

    draw_text(
        draw,
        (box[0] + 46, box[1] + 12),
        text,
        font(13, False),
        fill=TEXT,
        max_width=box[2] - box[0] - 60,
        max_lines=5,
        line_gap=2,
    )


def draw_use_cases(draw, box, use_cases, colors):
    x1, y1, x2, y2 = box
    rounded(
        draw,
        box,
        radius=22,
        fill=PANEL,
        outline=LINE,
        width=2,
    )

    cols = max(1, min(4, len(use_cases)))
    width = (x2 - x1 - 32 - (cols - 1) * 12) // cols

    for i, use in enumerate(use_cases[:cols]):
        bx1 = x1 + 16 + i * (width + 12)
        bx2 = bx1 + width
        color = colors[i % len(colors)]

        draw_icon(
            draw,
            ((bx1 + bx2) // 2, y1 + 25),
            color,
            "dot",
            10,
        )

        fnt = fit_font(
            draw,
            use,
            width - 20,
            13,
            10,
            False,
        )

        draw_centered(
            draw,
            (bx1 + 8, y1 + 44, bx2 - 8, y2 - 12),
            use,
            fnt,
            TEXT,
        )


def draw_branding(draw):
    draw.text(
        (60, H - 50),
        "CodeWithKambojShubham",
        font=font(20, True),
        fill=TEXT,
    )
    draw.text(
        (750, H - 50),
        "Learn • Build • Grow",
        font=font(15, False),
        fill=MUTED,
    )
