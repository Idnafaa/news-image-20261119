"""Draw the 19 November 2026 front page, hero-led version.

One 1024x1024 picture of the day on cream paper. The day's biggest story
— GTA VI going on sale after 13 years — gets a full-width Vice City night
scene with a giant headline, so the page reads at a glance even small.
Below it six bigger feature cards, then the rest of the day in brief.
21 stories in all, every fact the same verified 19 November 2026 news as
the first version: nothing new added, no number changed. Drawn with PIL
from the DejaVu fonts; fixed seeds only, so the same run always writes
the same bytes.
"""

import math
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

PAGE = 1024
MARGIN = 24
CONTENT = PAGE - 2 * MARGIN


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def serif_b(size):
    return font("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return font("DejaVuSerif.ttf", size)


def sans_b(size):
    return font("DejaVuSans-Bold.ttf", size)


def sans(size):
    return font("DejaVuSans.ttf", size)


def width(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_width, max_lines=None):
    """Greedy word wrap; at most max_lines lines, last one ellipsised."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if width(draw, trial, fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and width(draw, lines[-1] + "…", fnt) > max_width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + "…"
    return lines


def tracked(draw, xy, text, fnt, fill, tracking=2):
    """Draw text with extra space between letters (eyebrows, labels)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- the news
# The same verified 19 November 2026 stories as v1 (Reuters, AP, BBC, UN
# News, The Hindu, Pew, NASA, IMD). Six features get cards; the Fed and
# UniCredit stories join the briefs so all nine features stay on the page.

HERO_HEADLINE = "GTA VI goes on sale after 13 years"
HERO_SUMMARY = ("Rockstar's sequel unlocks at midnight worldwide, starting in New "
                "Zealand. Preorders top $1.5bn on 15.88M units; reviews hit 99 "
                "and Take-Two shares jump 6.5%.")

DAY_SUMMARY = ("GTA VI goes on sale, Jeffries is picked for Speaker, three leaders "
               "meet in Shenzhen, Iran hits a US base in Kuwait.")

FEATURES = [
    dict(num=2, region="WASHINGTON", tag="REPORTED", scene="capitol",
         headline="Jeffries picked to be first Black Speaker",
         summary="House Democrats nominate him 251–11; the full House votes on 3 January."),
    dict(num=3, region="SHENZHEN", tag="TODAY", scene="flags",
         headline="Trump, Xi and Putin meet in Shenzhen",
         summary="Three leaders meet at APEC, with Ukraine, Iran, trade and nuclear arms on the table."),
    dict(num=4, region="THE GULF", tag="REPORTED", scene="gulf",
         headline="Iran hits US base in Kuwait",
         summary="Drones target Ali Al Salem air base; Bahrain intercepts a fourth attack in six days."),
    dict(num=5, region="INDIA", tag="REPORTED", scene="cyclone",
         headline="Cyclone Akvan bears down on India",
         summary="IMD scales back the landfall forecast as Odisha evacuates 200,000."),
    dict(num=8, region="SOCIETY", tag="REPORTED", scene="pewbars",
         headline="Islam to pass Christianity by 2035",
         summary="Pew projects 2.57bn Muslims vs 2.52bn Christians by 2035."),
    dict(num=9, region="SPACE", tag="TODAY", scene="voyager",
         headline="NASA confirms Voyager's light-day",
         summary="The probe crossed one light-day from Earth; NASA confirms it at noon today."),
]

BRIEFS_LEFT = [
    "Fed minutes signal more rate rises; October hold was 10–2 at 3.75–4%",
    "UniCredit and Berlin strike Commerzbank deal; HQ stays in Frankfurt",
    "COP31: 21 issues still open as new draft texts are due",
    "Peltola win gives Democrats a 56–44 Senate",
    "India and Japan hold 2+2 defence talks in Tokyo",
    "Canada's Carney recalibrates ties with China",
    "US senators warn AI cyber threats outpace defences",
]

BRIEFS_RIGHT = [
    "Weight-loss drugs cut UK grocery spend by £1bn",
    "LPG tanker sunk off Bulgaria was hit by projectiles",
    "Cocaine and millions of pills seized in eastern Libya",
    "Nvidia chief promises earlier pay rises; SEC opens inquiry",
    "Microsoft in talks to sell AI services to ByteDance",
    "Oil falls 3.2% to $83.26 a barrel",
    "Modi meets the Prince and Princess of Wales",
]


# ---------------------------------------------------------------- hero scene
# A full-width Vice City night: indigo sky, seeded stars, a big striped
# synthwave sun over the horizon, a neon skyline, palms, and a dark road
# with a car at the bottom. Drawn straight onto the page.

def draw_hero(draw, x0, y0, w, h):
    horizon = y0 + 168
    road_top = y0 + 196
    # Sky: indigo at the top warming to violet-pink at the horizon.
    for row in range(horizon - y0):
        t = row / max(1, horizon - y0 - 1)
        draw.line([(x0, y0 + row), (x0 + w, y0 + row)],
                  fill=lerp((22, 12, 48), (96, 34, 76), t))
    # Stars in the upper sky.
    rng = random.Random(1911)
    for _ in range(90):
        sx = x0 + rng.randint(4, w - 4)
        sy = y0 + rng.randint(4, 140)
        r = rng.choice([1, 1, 1, 2])
        shade = rng.choice([(255, 255, 255), (220, 228, 255), (255, 240, 200)])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=shade)
    # Pink glow band just above the horizon.
    draw.rectangle([x0, horizon - 6, x0 + w, horizon], fill=(255, 64, 160))
    draw.rectangle([x0, horizon - 2, x0 + w, horizon], fill=(255, 120, 180))
    # Neon skyline: seeded towers with lit windows.
    rng = random.Random(7)
    x = x0
    while x < x0 + w:
        bw = rng.randint(42, 78)
        bh = rng.randint(52, 116)
        base = horizon - 4
        draw.rectangle([x, base - bh, x + bw, base], fill=(8, 6, 22))
        for wy in range(base - bh + 8, base - 6, 12):
            for wx in range(x + 6, x + bw - 6, 11):
                if rng.random() < 0.5:
                    draw.rectangle([wx, wy, wx + 4, wy + 6],
                                   fill=rng.choice([(255, 214, 64), (64, 224, 255),
                                                    (255, 64, 160)]))
        x += bw + 4
    # Dark ground strip between the skyline base and the road, so no
    # paper shows through.
    draw.rectangle([x0, horizon, x0 + w, road_top], fill=(12, 9, 24))
    # Synthwave sun, drawn over the skyline so it stays visible: a
    # pink-orange disc with dark slats across its lower half.
    cx, cy, r = x0 + 690, y0 + 118, 56
    for k in range(12):
        rr = r - k * 4
        shade = lerp((255, 94, 120), (255, 170, 60), k / 11)
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=shade)
    for i, gap in enumerate([2, 3, 4, 5]):
        yy = cy + 10 + i * 11
        draw.rectangle([cx - r, yy, cx + r, yy + gap], fill=(10, 8, 26))
    # Palm silhouettes at both edges.
    for px, ph in [(x0 + 46, 64), (x0 + w - 46, 56)]:
        draw.line([(px, horizon - 4), (px, horizon - 4 - ph)],
                  fill=(6, 40, 20), width=5)
        for ang in range(-70, 71, 35):
            ex = px + int(34 * math.cos(math.radians(ang - 90)))
            ey = horizon - 4 - ph + int(20 * math.sin(math.radians(ang - 90)))
            draw.line([(px, horizon - 4 - ph), (ex, ey)], fill=(10, 70, 34), width=3)
    # Dark road with a dashed centre line and one low car.
    draw.rectangle([x0, road_top, x0 + w, y0 + h], fill=(14, 10, 24))
    for dx in range(x0 + 10, x0 + w - 30, 56):
        draw.rectangle([dx, road_top + 16, dx + 28, road_top + 20], fill=(255, 214, 64))
    car_x, car_y = x0 + 170, road_top + 4
    draw.polygon([(car_x, car_y + 14), (car_x + 12, car_y + 2),
                  (car_x + 52, car_y + 2), (car_x + 64, car_y + 14)],
                 fill=(196, 32, 96))
    draw.rectangle([car_x - 6, car_y + 10, car_x + 70, car_y + 20], fill=(196, 32, 96))
    draw.ellipse([car_x + 6, car_y + 18, car_x + 18, car_y + 30], fill=(8, 8, 10))
    draw.ellipse([car_x + 46, car_y + 18, car_x + 58, car_y + 30], fill=(8, 8, 10))
    draw.ellipse([car_x + 62, car_y + 12, car_x + 68, car_y + 18], fill=(255, 230, 140))


# ---------------------------------------------------------------- card scenes
# Small 314x84 panels, one per feature card. Each is drawn on its own
# image and pasted into the card.

def new_panel(w, h, bg):
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)


def scatter_stars(d, w, h, count, seed, colour=(255, 255, 255)):
    rng = random.Random(seed)
    for _ in range(count):
        x = rng.randint(2, w - 3)
        y = rng.randint(2, h - 3)
        r = rng.choice([1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=colour)


def scene_capitol(w, h):
    img, d = new_panel(w, h, (233, 230, 222))
    d.rectangle([0, h - 16, w, h], fill=(88, 124, 78))
    d.rectangle([104, h - 28, 210, h - 16], fill=(250, 250, 248))
    d.pieslice([118, 2, 196, h - 20], 180, 360, fill=(250, 250, 248),
               outline=(150, 146, 138), width=2)
    d.rectangle([156, 0, 159, 8], fill=(120, 116, 108))
    d.polygon([(159, 0), (159, 7), (170, 4)], fill=RED)
    for cx in range(110, 210, 10):
        d.rectangle([cx, h - 24, cx + 4, h - 16], fill=(210, 208, 200))
    for i, col in enumerate([(179, 38, 30), NAVY] * 6):
        x0 = i * 27
        d.polygon([(x0, h - 16), (x0 + 27, h - 16), (x0 + 13, h - 4)], fill=col)
    return img


def scene_flags(w, h):
    img, d = new_panel(w, h, (238, 234, 224))
    d.rectangle([0, h - 16, w, h], fill=(120, 110, 96))
    specs = [(28, "us"), (122, "cn"), (216, "ru")]
    for x0, kind in specs:
        d.rectangle([x0 + 44, 6, x0 + 47, h - 16], fill=(90, 80, 66))
        if kind == "us":
            for i in range(7):
                d.rectangle([x0, 8 + i * 6, x0 + 44, 8 + i * 6 + 3],
                            fill=RED if i % 2 == 0 else (250, 250, 248))
            d.rectangle([x0, 8, x0 + 18, 26], fill=NAVY)
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


def scene_gulf(w, h):
    img, d = new_panel(w, h, (16, 24, 48))
    d.rectangle([0, 56, w, h], fill=(196, 164, 120))
    scatter_stars(d, w, 56, 26, 11)
    d.rectangle([30, 48, 86, 60], fill=(70, 62, 52))
    d.pieslice([30, 36, 86, 60], 180, 360, fill=(88, 78, 64))
    d.rectangle([120, 42, 150, 60], fill=(70, 62, 52))
    d.rectangle([238, 34, 246, 60], fill=(70, 62, 52))
    d.rectangle([230, 28, 254, 36], fill=(88, 78, 64))
    for dx, dy in [(120, 14), (180, 22), (250, 12)]:
        d.line([(dx - 8, dy), (dx + 8, dy)], fill=(220, 220, 220), width=2)
        d.line([(dx, dy - 3), (dx, dy + 3)], fill=(220, 220, 220), width=2)
    for bx, by in [(100, 38), (205, 42), (268, 36)]:
        for k in range(8):
            a = k * math.pi / 4
            d.line([(bx, by), (bx + int(11 * math.cos(a)), by + int(11 * math.sin(a)))],
                   fill=(255, 150, 40), width=2)
        d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(255, 210, 90))
    return img


def scene_cyclone(w, h):
    img, d = new_panel(w, h, (58, 110, 158))
    cx, cy = 120, 44
    for r in range(38, 4, -6):
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 20, fill=(255, 255, 255), width=4)
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 200, fill=(190, 220, 240), width=4)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255))
    rng = random.Random(21)
    for _ in range(26):
        x = rng.randint(0, 300)
        y = rng.randint(0, 66)
        d.line([(x, y), (x - 4, y + 9)], fill=(200, 225, 245), width=1)
    d.polygon([(252, 0), (314, 0), (314, 84), (268, 84), (258, 40)],
              fill=(214, 196, 158))
    return img


def scene_pewbars(w, h):
    img, d = new_panel(w, h, (238, 234, 224))
    d.text((34, 8), "2035", font=sans_b(13), fill=INK)
    d.text((14, 28), "Muslims", font=sans(12), fill=SOFT_INK)
    d.rectangle([86, 26, 252, 40], fill=(29, 110, 96))
    d.text((258, 27), "2.57bn", font=sans_b(12), fill=INK)
    d.text((14, 52), "Christians", font=sans(12), fill=SOFT_INK)
    d.rectangle([86, 50, 247, 64], fill=(96, 110, 140))
    d.text((253, 51), "2.52bn", font=sans_b(12), fill=INK)
    return img


def scene_voyager(w, h):
    img, d = new_panel(w, h, (6, 8, 20))
    scatter_stars(d, w, h, 40, 33)
    d.line([(150, 40), (196, 34)], fill=(220, 220, 220), width=2)
    d.polygon([(196, 34), (214, 22), (222, 38)], fill=(200, 170, 80))
    d.rectangle([138, 36, 152, 48], fill=(200, 170, 80))
    d.line([(138, 42), (96, 50)], fill=(200, 200, 200), width=2)
    d.ellipse([92, 46, 100, 54], fill=(255, 220, 120))
    d.ellipse([-30, 58, 60, 136], fill=(58, 110, 180))
    d.ellipse([-22, 64, 52, 128], fill=(120, 180, 230))
    for i in range(9):
        x = 220 + i * 10
        y = 38 - i * 2
        d.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 255))
    return img


SCENES = {
    "capitol": scene_capitol,
    "flags": scene_flags,
    "gulf": scene_gulf,
    "cyclone": scene_cyclone,
    "pewbars": scene_pewbars,
    "voyager": scene_voyager,
}

# ---------------------------------------------------------------- layout

def draw_header(d):
    tracked(d, (MARGIN, 14), "THE DAY IN ONE PICTURE", sans_b(13), RED, tracking=2)
    badge = "21 STORIES · 6 CONTINENTS · ONE PAGE"
    bw = width(d, badge, sans_b(12))
    d.text((PAGE - MARGIN - bw, 15), badge, font=sans_b(12), fill=SOFT_INK)
    d.text((MARGIN, 34), "THURSDAY, 19 NOVEMBER 2026", font=serif_b(46), fill=INK)
    d.text((MARGIN, 88), DAY_SUMMARY, font=serif(15), fill=SOFT_INK)
    d.line([(MARGIN, 110), (PAGE - MARGIN, 110)], fill=INK, width=2)
    d.line([(MARGIN, 113), (PAGE - MARGIN, 113)], fill=INK, width=1)


def draw_hero_block(d):
    draw_hero(d, MARGIN, 122, CONTENT, 232)
    tracked(d, (MARGIN, 362), "CULTURE · THE BIG STORY", sans_b(11), RED, tracking=1)
    kw = width(d, "CULTURE · THE BIG STORY", sans_b(11)) + len("CULTURE · THE BIG STORY") * 1
    d.text((MARGIN + kw + 8, 362), "REPORTED", font=sans_b(11), fill=INK)
    d.text((MARGIN, 376), HERO_HEADLINE, font=serif_b(40), fill=INK)
    lines = wrap(d, HERO_SUMMARY, serif(16), CONTENT, max_lines=2)
    hy = 424
    for line in lines:
        d.text((MARGIN, hy), line, font=serif(16), fill=INK)
        hy += 20
    d.line([(MARGIN, 474), (PAGE - MARGIN, 474)], fill=INK, width=1)


def draw_card(d, page, feat, x, y):
    w, h = 314, 196
    scene = SCENES[feat["scene"]](w, 84)
    page.paste(scene, (x, y))
    d.rectangle([x, y, x + 26, y + 22], fill=RED)
    num = str(feat["num"])
    nw = width(d, num, sans_b(13))
    d.text((x + (26 - nw) / 2, y + 3), num, font=sans_b(13), fill=(255, 255, 255))
    ty = y + 90
    tracked(d, (x, ty), feat["region"], sans_b(10), RED, tracking=1)
    kw = width(d, feat["region"], sans_b(10)) + len(feat["region"]) * 1
    d.text((x + kw + 8, ty), feat["tag"], font=sans_b(10), fill=INK)
    lines = wrap(d, feat["headline"], serif_b(18), w - 4, max_lines=2)
    hy = ty + 14
    for line in lines:
        d.text((x, hy), line, font=serif_b(18), fill=INK)
        hy += 20
    slines = wrap(d, feat["summary"], sans(12), w - 4, max_lines=2)
    sy = ty + 14 + 2 * 20 + 4
    for line in slines:
        d.text((x, sy), line, font=sans(12), fill=SOFT_INK)
        sy += 14


def draw_also(d, y):
    d.text((MARGIN, y), "ALSO ON THE DAY", font=sans_b(13), fill=INK)
    d.line([(MARGIN, y + 18), (PAGE - MARGIN, y + 18)], fill=INK, width=1)
    row_y = y + 28
    for briefs, x in ((BRIEFS_LEFT, MARGIN), (BRIEFS_RIGHT, 512)):
        yy = row_y
        for text in briefs:
            d.text((x, yy), "•", font=sans_b(11), fill=RED)
            d.text((x + 12, yy), text, font=sans(11), fill=INK)
            yy += 12
    return row_y + 7 * 12


def build(path):
    page = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(page)
    draw_header(d)
    draw_hero_block(d)
    gx, gy = MARGIN, 486
    for idx, feat in enumerate(FEATURES):
        col = idx % 3
        row = idx // 3
        draw_card(d, page, feat, gx + col * (314 + 17), gy + row * (196 + 12))
    draw_also(d, 900)
    page.save(path, format="PNG")
    return path


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    build(out)
    print("wrote", out)
