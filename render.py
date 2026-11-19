"""Draw the 19 November 2026 front page: one 1024x1024 picture of the day.

The picture is a broadsheet front page on cream paper. Nine feature cards
carry the day's biggest stories, each with a small scene drawn from shapes;
below them a figures strip, a dotted world map with numbered pins, and a
two-column list of the rest of the day's news. Everything is drawn with PIL
from the DejaVu fonts, so the same run always writes the same bytes.
"""

import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

# Palette: warm paper, near-black ink, one red for badges and rules.
PAPER = (248, 243, 232)
INK = (20, 18, 16)
SOFT_INK = (74, 68, 60)
RED = (179, 38, 30)
NAVY = (29, 53, 87)
GOLD = (176, 132, 52)
RULE = (20, 18, 16)

PAGE = 1024
MARGIN = 24
CONTENT = PAGE - 2 * MARGIN


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def text_width(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap_lines(draw, text, fnt, max_width, max_lines=None):
    """Greedy word wrap; returns at most max_lines lines (last one ellipsised)."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(draw, trial, fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and text_width(draw, lines[-1] + "…", fnt) > max_width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + "…"
    return lines


def tracked(draw, xy, text, fnt, fill, tracking=2):
    """Draw text with extra space between letters (for eyebrows and labels)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


# ---------------------------------------------------------------- the news
# Nine feature stories, each verified across at least two sources this
# morning (Reuters, AP, BBC, UN News, The Hindu, Pew, NASA, IMD).

FEATURES = [
    dict(num=1, region="CULTURE", tag="REPORTED", scene="gta",
         headline="GTA VI goes on sale after 13 years",
         summary="Rockstar's sequel unlocks at midnight worldwide; preorders top $1.5bn, reviews hit 99."),
    dict(num=2, region="WASHINGTON", tag="REPORTED", scene="capitol",
         headline="Jeffries picked to be first Black Speaker",
         summary="House Democrats nominate him 251–11; the full House votes on 3 January."),
    dict(num=3, region="SHENZHEN", tag="TODAY", scene="flags",
         headline="Trump, Xi and Putin meet in Shenzhen",
         summary="The three leaders meet at APEC in Shenzhen, with Ukraine, Iran, trade and nuclear arms on the table."),
    dict(num=4, region="THE GULF", tag="REPORTED", scene="gulf",
         headline="Iran hits US base in Kuwait",
         summary="Tehran's drones target Ali Al Salem air base; Kuwait and Bahrain say the attacks were intercepted."),
    dict(num=5, region="INDIA", tag="REPORTED", scene="cyclone",
         headline="Cyclone Akvan bears down on India",
         summary="IMD scales back the landfall forecast as Odisha evacuates 200,000."),
    dict(num=6, region="ECONOMY", tag="REPORTED", scene="fed",
         headline="Fed signals more rate rises ahead",
         summary="Minutes show almost all officials see further hikes; the October hold was a 10–2 vote at 3.75–4%."),
    dict(num=7, region="EUROPE", tag="REPORTED", scene="bank",
         headline="UniCredit and Berlin strike bank deal",
         summary="The Italian bank and Germany agree the Commerzbank takeover terms."),
    dict(num=8, region="SOCIETY", tag="REPORTED", scene="pewbars",
         headline="Islam to pass Christianity by 2035",
         summary="Pew projects 2.57bn Muslims and 2.52bn Christians by 2035, driven by higher Muslim fertility."),
    dict(num=9, region="SPACE", tag="TODAY", scene="voyager",
         headline="NASA confirms Voyager's light-day",
         summary="The probe crossed one light-day from Earth on Wednesday; NASA confirms it at noon today."),
]

FIGURES = [
    ("$1.5bn", "GTA VI preorders"),
    ("251–11", "Jeffries nomination"),
    ("99", "GTA VI Metacritic score"),
    ("200,000", "evacuations in Odisha"),
]

# Map pins: (grid column, grid row) on the 40x22 land grid, and the key text.
PINS = [
    (11, 8, "Miami — GTA VI goes on sale"),
    (10, 6, "Washington — Jeffries picked for Speaker"),
    (33, 9, "Shenzhen — three leaders meet"),
    (25, 8, "Kuwait — Iran hits US base"),
    (29, 10, "Andhra coast — Cyclone Akvan"),
    (12, 6, "New York — Fed signals more rises"),
    (21, 4, "Frankfurt — UniCredit bank deal"),
    (32, 14, "Jakarta — Islam to pass Christianity"),
    (7, 7, "California — Voyager's light-day"),
]

BRIEFS_LEFT = [
    "COP31: 21 issues still open as new draft texts are due",
    "Peltola win gives Democrats a 56–44 Senate",
    "India and Japan hold 2+2 defence talks in Tokyo",
    "Canada's Carney recalibrates ties with China",
    "US senators warn AI cyber threats outpace defences",
    "Weight-loss drugs cut UK grocery spend by £1bn",
    "LPG tanker sunk off Bulgaria was hit by projectiles",
    "US proposes tougher rules for green cards",
    "Saudi Arabia says danger has passed in three cities",
]

BRIEFS_RIGHT = [
    "Cocaine and millions of pills seized in eastern Libya",
    "Nvidia chief promises earlier pay rises; SEC opens inquiry",
    "Microsoft in talks to sell AI services to ByteDance",
    "Oil falls 3.2% to $83.26 a barrel",
    "Modi meets the Prince and Princess of Wales",
    "Scientists may have solved Earth's missing billion years",
    "French minister: Mélenchon could win the presidency",
    "Duckett's 133 puts England on top in Australia ODI",
    "Deutsche Bank handled $582m of Epstein-linked payments",
]

DAY_SUMMARY = ("GTA VI goes on sale, Jeffries is picked for Speaker, three leaders "
               "meet in Shenzhen, Iran hits a US base in Kuwait.")

# ---------------------------------------------------------------- the map
# A hand-built land bitmap: 22 rows of 40 columns, each land area given as
# explicit column spans so no row can drift out of width. Coarse but
# recognisable: the Americas on the left, Europe and Africa in the middle,
# Asia on the right, Australia at lower right.

LAND_SPANS = {
    0: [(2, 9), (20, 36)],
    1: [(2, 10), (19, 37)],
    2: [(3, 10), (19, 37)],
    3: [(3, 10), (19, 37)],
    4: [(4, 9), (19, 22), (24, 36)],
    5: [(4, 9), (20, 22), (25, 36)],
    6: [(5, 12), (20, 21), (25, 35)],
    7: [(5, 8), (20, 24), (26, 34)],
    8: [(6, 12), (20, 33)],
    9: [(7, 9), (20, 24), (28, 34)],
    10: [(8, 11), (21, 24), (29, 31)],
    11: [(8, 11), (21, 23)],
    12: [(9, 11), (21, 23)],
    13: [(9, 11), (22, 23)],
    14: [(9, 10), (31, 34)],
    15: [(9, 10), (31, 34)],
    16: [(10, 10), (32, 33)],
}
MAP_COLS = 40
MAP_ROWS = 22


def land_cells():
    cells = set()
    for row, spans in LAND_SPANS.items():
        for start, end in spans:
            for col in range(start, end + 1):
                cells.add((col, row))
    return cells


# ---------------------------------------------------------------- scenes
# Every scene is drawn with plain PIL shapes on a 314x72 panel. A fixed
# seed keeps the star fields identical on every run.

def panel(w=314, h=72):
    img = Image.new("RGB", (w, h), PAPER)
    return img, ImageDraw.Draw(img)


def starfield(d, w, h, count, seed, colour=(255, 255, 255)):
    rng = random.Random(seed)
    for _ in range(count):
        x = rng.randint(2, w - 3)
        y = rng.randint(2, h - 3)
        r = rng.choice([1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=colour)


def scene_gta():
    img, d = panel()
    # Night sky over Vice City: deep indigo bands, then a neon skyline.
    for y in range(72):
        shade = 26 + y // 3
        d.line([(0, y), (314, y)], fill=(shade, 16, 51))
    d.rectangle([0, 52, 314, 72], fill=(12, 8, 28))
    d.rectangle([0, 50, 314, 52], fill=(255, 64, 160))
    rng = random.Random(7)
    x = 0
    while x < 314:
        bw = rng.randint(18, 34)
        bh = rng.randint(18, 40)
        d.rectangle([x, 52 - bh, x + bw, 52], fill=(8, 6, 22))
        for wy in range(52 - bh + 4, 48, 7):
            for wx in range(x + 3, x + bw - 2, 6):
                if rng.random() < 0.55:
                    d.rectangle([wx, wy, wx + 2, wy + 3],
                                fill=rng.choice([(255, 214, 64), (64, 224, 255), (255, 64, 160)]))
        x += bw + 2
    # Two palm silhouettes against the sky.
    for px, ph in [(28, 26), (282, 22)]:
        d.line([(px, 52), (px, 52 - ph)], fill=(6, 40, 20), width=3)
        for ang in range(-70, 71, 35):
            import math
            ex = px + int(16 * math.cos(math.radians(ang - 90)))
            ey = 52 - ph + int(10 * math.sin(math.radians(ang - 90)))
            d.line([(px, 52 - ph), (ex, ey)], fill=(10, 70, 34), width=2)
    return img


def scene_capitol():
    img, d = panel()
    d.rectangle([0, 0, 314, 72], fill=(233, 230, 222))
    # The Capitol dome in white with a grey outline, on a low green lawn.
    d.rectangle([0, 56, 314, 72], fill=(88, 124, 78))
    d.rectangle([104, 44, 210, 56], fill=(250, 250, 248))
    d.pieslice([118, 2, 196, 52], 180, 360, fill=(250, 250, 248),
               outline=(150, 146, 138), width=2)
    d.rectangle([156, 0, 159, 8], fill=(120, 116, 108))
    d.polygon([(159, 0), (159, 7), (170, 4)], fill=(179, 38, 30))
    for cx in range(110, 210, 10):
        d.rectangle([cx, 48, cx + 4, 56], fill=(210, 208, 200))
    # Red and blue bunting across the bottom.
    for i, col in enumerate([(179, 38, 30), (29, 53, 87)] * 6):
        x0 = i * 27
        d.polygon([(x0, 56), (x0 + 27, 56), (x0 + 13, 68)], fill=col)
    return img


def scene_flags():
    img, d = panel()
    d.rectangle([0, 0, 314, 72], fill=(238, 234, 224))
    d.rectangle([0, 56, 314, 72], fill=(120, 110, 96))
    # Three flags on poles: United States, China, Russia.
    specs = [
        (28, "us"), (122, "cn"), (216, "ru"),
    ]
    for x0, kind in specs:
        d.rectangle([x0 + 44, 6, x0 + 47, 56], fill=(90, 80, 66))
        if kind == "us":
            for i in range(7):
                d.rectangle([x0, 8 + i * 6, x0 + 44, 8 + i * 6 + 3],
                            fill=(179, 38, 30) if i % 2 == 0 else (250, 250, 248))
            d.rectangle([x0, 8, x0 + 18, 26], fill=(29, 53, 87))
            for sy in (12, 18, 24):
                for sx in (4, 11):
                    d.ellipse([x0 + sx, sy, x0 + sx + 2, sy + 2], fill=(255, 255, 255))
        elif kind == "cn":
            d.rectangle([x0, 8, x0 + 44, 50], fill=(222, 32, 24))
            d.ellipse([x0 + 6, 12, x0 + 16, 22], fill=(255, 222, 64))
            for sx, sy in [(24, 12), (30, 16), (30, 24), (24, 28)]:
                d.ellipse([x0 + sx, sy, x0 + sx + 3, sy + 3], fill=(255, 222, 64))
        else:
            d.rectangle([x0, 8, x0 + 44, 22], fill=(250, 250, 248))
            d.rectangle([x0, 22, x0 + 44, 36], fill=(29, 53, 180))
            d.rectangle([x0, 36, x0 + 44, 50], fill=(200, 30, 30))
    return img


def scene_gulf():
    img, d = panel()
    d.rectangle([0, 0, 314, 48], fill=(16, 24, 48))
    d.rectangle([0, 48, 314, 72], fill=(196, 164, 120))
    starfield(d, 314, 48, 26, 11)
    # Air base: hangars and a control tower on the sand.
    d.rectangle([30, 40, 86, 52], fill=(70, 62, 52))
    d.pieslice([30, 28, 86, 52], 180, 360, fill=(88, 78, 64))
    d.rectangle([120, 34, 150, 52], fill=(70, 62, 52))
    d.rectangle([238, 26, 246, 52], fill=(70, 62, 52))
    d.rectangle([230, 20, 254, 28], fill=(88, 78, 64))
    # Drones overhead and orange interception bursts.
    for dx, dy in [(120, 14), (180, 22), (250, 12)]:
        d.line([(dx - 8, dy), (dx + 8, dy)], fill=(220, 220, 220), width=2)
        d.line([(dx, dy - 3), (dx, dy + 3)], fill=(220, 220, 220), width=2)
    for bx, by in [(100, 30), (205, 34), (268, 28)]:
        for k in range(8):
            import math
            a = k * 3.14159 / 4
            d.line([(bx, by), (bx + int(11 * math.cos(a)), by + int(11 * math.sin(a)))],
                   fill=(255, 150, 40), width=2)
        d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(255, 210, 90))
    return img


def scene_cyclone():
    img, d = panel()
    d.rectangle([0, 0, 314, 72], fill=(58, 110, 158))
    # Spiral bands of the storm over the sea.
    cx, cy = 120, 38
    for r in range(34, 4, -6):
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 20, fill=(255, 255, 255), width=4)
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 200, fill=(190, 220, 240), width=4)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255))
    # Rain streaks and the coastline at the right.
    rng = random.Random(21)
    for _ in range(26):
        x = rng.randint(0, 300)
        y = rng.randint(0, 60)
        d.line([(x, y), (x - 4, y + 9)], fill=(200, 225, 245), width=1)
    d.polygon([(252, 0), (314, 0), (314, 72), (268, 72), (258, 40)],
              fill=(214, 196, 158))
    d.polygon([(252, 0), (268, 72), (258, 40)], fill=(176, 150, 110))
    return img


def scene_fed():
    img, d = panel()
    d.rectangle([0, 0, 314, 72], fill=(238, 234, 224))
    # A rising line chart with markers, above a columned bank front.
    pts = [(16, 56), (70, 50), (124, 52), (178, 40), (232, 30), (292, 16)]
    d.line(pts, fill=(29, 110, 60), width=3)
    for px, py in pts:
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(29, 110, 60))
    d.polygon([(292, 16), (282, 16), (292, 6)], fill=(29, 110, 60))
    d.line([(16, 60), (300, 60)], fill=(150, 142, 128), width=1)
    for cx in range(24, 300, 34):
        d.rectangle([cx, 62, cx + 12, 72], fill=(120, 110, 96))
    return img


def scene_bank():
    img, d = panel()
    d.rectangle([0, 0, 314, 72], fill=(238, 234, 224))
    # Two bank fronts facing each other, a gold euro between them.
    for bx in (18, 208):
        d.polygon([(bx, 26), (bx + 44, 26), (bx + 22, 12)], fill=(90, 80, 66))
        d.rectangle([bx, 26, bx + 44, 34], fill=(120, 110, 96))
        for cx in range(bx + 4, bx + 44, 11):
            d.rectangle([cx, 34, cx + 5, 58], fill=(150, 142, 128))
        d.rectangle([bx - 2, 58, bx + 46, 62], fill=(90, 80, 66))
    d.ellipse([122, 8, 192, 66], fill=(176, 132, 52))
    d.ellipse([128, 14, 186, 60], fill=(248, 243, 232))
    d.text((141, 16), "€", font=SANS_B(34), fill=(176, 132, 52))
    d.line([(66, 40), (118, 40)], fill=(29, 110, 60), width=3)
    d.polygon([(118, 40), (108, 35), (108, 45)], fill=(29, 110, 60))
    d.line([(248, 40), (196, 40)], fill=(29, 110, 60), width=3)
    d.polygon([(196, 40), (206, 35), (206, 45)], fill=(29, 110, 60))
    return img


def scene_pewbars():
    img, d = panel()
    d.rectangle([0, 0, 314, 72], fill=(238, 234, 224))
    # Two bars: Muslims 2.57bn against Christians 2.52bn in 2035.
    d.text((34, 8), "2035", font=SANS_B(13), fill=INK)
    d.text((14, 26), "Muslims", font=SANS(12), fill=SOFT_INK)
    d.rectangle([86, 24, 252, 38], fill=(29, 110, 96))
    d.text((258, 25), "2.57bn", font=SANS_B(12), fill=INK)
    d.text((14, 48), "Christians", font=SANS(12), fill=SOFT_INK)
    d.rectangle([86, 46, 247, 60], fill=(96, 110, 140))
    d.text((253, 47), "2.52bn", font=SANS_B(12), fill=INK)
    return img


def scene_voyager():
    img, d = panel()
    d.rectangle([0, 0, 314, 72], fill=(6, 8, 20))
    starfield(d, 314, 72, 40, 33)
    # The probe: a gold dish, a bus body and a long boom.
    d.line([(150, 36), (196, 30)], fill=(220, 220, 220), width=2)
    d.polygon([(196, 30), (214, 18), (222, 34)], fill=(200, 170, 80))
    d.rectangle([138, 32, 152, 44], fill=(200, 170, 80))
    d.line([(138, 38), (96, 46)], fill=(200, 200, 200), width=2)
    d.ellipse([92, 42, 100, 50], fill=(255, 220, 120))
    # Earth's blue arc in the corner and a dotted path behind the probe.
    d.ellipse([-30, 52, 60, 130], fill=(58, 110, 180))
    d.ellipse([-22, 58, 52, 122], fill=(120, 180, 230))
    for i in range(9):
        x = 220 + i * 10
        y = 34 - i * 2
        d.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 255))
    return img


SCENES = {
    "gta": scene_gta,
    "capitol": scene_capitol,
    "flags": scene_flags,
    "gulf": scene_gulf,
    "cyclone": scene_cyclone,
    "fed": scene_fed,
    "bank": scene_bank,
    "pewbars": scene_pewbars,
    "voyager": scene_voyager,
}

# ---------------------------------------------------------------- layout

def draw_header(d, page):
    # Eyebrow on the left, story-count badge on the right, same line.
    tracked(d, (MARGIN, 16), "THE DAY IN ONE PICTURE", SANS_B(13), RED, tracking=2)
    badge = "30 STORIES · 6 CONTINENTS · ONE PAGE"
    bw = text_width(d, badge, SANS_B(12))
    d.text((PAGE - MARGIN - bw, 17), badge, font=SANS_B(12), fill=SOFT_INK)
    # Giant serif masthead naming the day.
    d.text((MARGIN, 34), "THURSDAY, 19 NOVEMBER 2026",
           font=SERIF_B(52), fill=INK)
    # One-line summary of the day.
    d.text((MARGIN, 96), DAY_SUMMARY, font=SERIF(16), fill=SOFT_INK)
    d.line([(MARGIN, 120), (PAGE - MARGIN, 120)], fill=RULE, width=2)
    d.line([(MARGIN, 123), (PAGE - MARGIN, 123)], fill=RULE, width=1)


def draw_card(d, page, feat, x, y):
    w, h = 314, 168
    # Scene across the top of the card.
    scene = SCENES[feat["scene"]]()
    page.paste(scene, (x, y))
    # Numbered red badge over the scene's top-left corner.
    d.rectangle([x, y, x + 26, y + 22], fill=RED)
    num = str(feat["num"])
    nw = text_width(d, num, SANS_B(13))
    d.text((x + (26 - nw) / 2, y + 3), num, font=SANS_B(13), fill=(255, 255, 255))
    ty = y + 78
    # Region kicker in red, tag in black after it.
    tracked(d, (x, ty), feat["region"], SANS_B(10), RED, tracking=1)
    kw = text_width(d, feat["region"], SANS_B(10)) + len(feat["region"]) * 1
    d.text((x + kw + 8, ty), feat["tag"], font=SANS_B(10), fill=INK)
    # Headline, up to two lines of large serif.
    lines = wrap_lines(d, feat["headline"], SERIF_B(18), w - 4, max_lines=2)
    hy = ty + 14
    for line in lines:
        d.text((x, hy), line, font=SERIF_B(18), fill=INK)
        hy += 20
    # Summary, up to two lines of small sans.
    slines = wrap_lines(d, feat["summary"], SANS(12), w - 4, max_lines=2)
    sy = ty + 14 + 2 * 20 + 2
    for line in slines:
        d.text((x, sy), line, font=SANS(12), fill=SOFT_INK)
        sy += 14


def draw_figures(d, page, y):
    tracked(d, (MARGIN, y), "BY THE NUMBERS", SANS_B(11), RED, tracking=2)
    col_w = CONTENT / len(FIGURES)
    for i, (value, label) in enumerate(FIGURES):
        cx = MARGIN + i * col_w
        d.text((cx, y + 16), value, font=SERIF_B(24), fill=INK)
        d.text((cx, y + 46), label, font=SANS(11), fill=SOFT_INK)
    d.line([(MARGIN, y + 62), (PAGE - MARGIN, y + 62)], fill=(200, 192, 176), width=1)


def draw_map(d, page, y):
    tracked(d, (MARGIN, y), "WHERE IT HAPPENED", SANS_B(12), RED, tracking=2)
    map_x, map_y = MARGIN, y + 18
    map_w, map_h = 644, 112
    cell_w = map_w / MAP_COLS
    cell_h = map_h / MAP_ROWS
    # Dotted land: one small dot per land cell.
    for col, row in land_cells():
        cx = map_x + (col + 0.5) * cell_w
        cy = map_y + (row + 0.5) * cell_h
        d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill=(150, 140, 124))
    # Numbered pins on top of the dots.
    for i, (col, row, _label) in enumerate(PINS, start=1):
        cx = map_x + (col + 0.5) * cell_w
        cy = map_y + (row + 0.5) * cell_h
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED,
                  outline=(255, 255, 255), width=1)
        num = str(i)
        nw = text_width(d, num, SANS_B(8))
        d.text((cx - nw / 2, cy - 5), num, font=SANS_B(8), fill=(255, 255, 255))
    # Key at the right of the map.
    kx = 700
    ky = map_y + 2
    for i, (_c, _r, label) in enumerate(PINS, start=1):
        d.text((kx, ky), f"{i}  {label}", font=SANS(11.5), fill=INK)
        ky += 13


def draw_also(d, page, y):
    d.text((MARGIN, y), "ALSO ON THE DAY", font=SANS_B(13), fill=INK)
    d.line([(MARGIN, y + 18), (PAGE - MARGIN, y + 18)], fill=RULE, width=1)
    left_x, right_x = MARGIN, 512
    row_y = y + 28
    for briefs, x in ((BRIEFS_LEFT, left_x), (BRIEFS_RIGHT, right_x)):
        yy = row_y
        for text in briefs:
            d.text((x, yy), "•", font=SANS_B(11), fill=RED)
            d.text((x + 12, yy), text, font=SANS(11), fill=INK)
            yy += 12
    return row_y + 9 * 12


def build(path):
    page = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(page)
    draw_header(d, page)
    # Nine feature cards in a 3x3 grid.
    gx, gy = MARGIN, 132
    for idx, feat in enumerate(FEATURES):
        col = idx % 3
        row = idx // 3
        draw_card(d, page, feat, gx + col * (314 + 17), gy + row * (168 + 12))
    draw_figures(d, page, 672)
    draw_map(d, page, 740)
    draw_also(d, page, 880)
    page.save(path, format="PNG")
    return path


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    build(out)
    print("wrote", out)
