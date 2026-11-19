"""Draw the 19 November 2026 front page, dense-broadsheet version (v3).

One 1024x1024 picture of the day on cream paper, in the classic
broadsheet shape the day's strongest pages share: a giant serif
masthead, a region-count bar, a figures strip, three hero cards with
drawn scenes, ten smaller cards, a world map with numbered pins, the
rest of the day in brief, and a DATE CHECK box naming the stories left
out because they broke earlier. 35 stories in all.

Facts: the nine features and eighteen briefs verified for v1 (Reuters,
AP, BBC, UN News, The Hindu, Pew, NASA, IMD), plus eight more stories
verified for this version across two or more sources each on 19 Nov
2026 — Anthropic's Nasdaq debut, the ICJ Rohingya judgment, the Van
Gogh record, the Florida floods, the Yellow Line incursion, the fresh
Kerch strike, the COP31 $120bn figure and Nvidia's $115.8bn quarter.
Nothing invented, no number changed. Drawn with PIL from the DejaVu
fonts; fixed seeds only, so the same run always writes the same bytes.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

# Palette: warm paper, near-black ink, red for badges and rules,
# navy for the map panel and region bar.
PAPER = (248, 243, 232)
INK = (20, 18, 16)
SOFT_INK = (74, 68, 60)
RED = (179, 38, 30)
NAVY = (29, 53, 87)
GOLD = (176, 132, 52)
MAP_TAN = (216, 196, 158)

PAGE = 1024
MARGIN = 24
CONTENT = PAGE - 2 * MARGIN


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def serif_b(size):
    return font("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return font("DejaVuSerif.ttf", size)


def serif_i(size):
    # No DejaVuSerif-Italic on this box; regular serif in red reads the same.
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
# 35 stories, numbered 1-35. Cards 1-3 are the heroes; cards 4-13 the
# smaller cards; 14-35 the briefs. Regions are counted for the bar.

HEROES = [
    dict(num=1, place="SHENZHEN", tag="SUMMIT", scene="flags",
         headline="Trump, Xi and Putin hold first three-way summit",
         summary="The three nuclear powers meet at APEC in Shenzhen; arms control "
                 "and the Iran war top the agenda."),
    dict(num=2, place="NEW YORK", tag="GAMES", scene="vicecity",
         headline="GTA VI arrives after a 13-year wait",
         summary="Rockstar's sequel unlocks at midnight in each country, New Zealand "
                 "first; 15.9m pre-orders banked. $79.99 on PS5 and Xbox, no PC yet."),
    dict(num=3, place="NASDAQ", tag="MARKETS", scene="chart",
         headline="Anthropic debuts in the biggest IPO on record",
         summary="Priced at $83, above its range, the Claude maker raised $81.3bn "
                 "and is valued near $1.5tn. Shares start trading as ANT today."),
]

CARDS = [
    dict(num=4, place="THE HAGUE", tag="LAW", scene="court",
         headline="ICJ rules on Myanmar genocide case",
         summary="Judges in The Hague deliver the verdict, seven years after "
                 "730,000 fled in 2017."),
    dict(num=5, place="THE GULF", tag="WAR", scene="gulf",
         headline="Iran hits US base in Kuwait",
         summary="Drones target Ali Al Salem air base; Bahrain intercepts a "
                 "fourth attack in six days."),
    dict(num=6, place="ODISHA", tag="STORM", scene="cyclone",
         headline="Cyclone Akvan bears down as 200,000 flee",
         summary="Red alerts in 11 districts as Odisha evacuates 200,000; "
                 "landfall near Puri due Friday."),
    dict(num=7, place="ANTALYA", tag="CLIMATE", scene="cop",
         headline="COP31 enters its final 48 hours",
         summary="Ministers take over the draft; the $120bn fund and "
                 "'phase out' stay open."),
    dict(num=8, place="WASHINGTON", tag="POLITICS", scene="capitol",
         headline="Jeffries picked to be first Black Speaker",
         summary="House Democrats nominate him 251–11; the full House votes "
                 "on 3 January."),
    dict(num=9, place="WASHINGTON", tag="ECONOMY", scene="fed",
         headline="Fed minutes point to more rate hikes",
         summary="October's 10–2 hold at 3.75–4% came with almost all "
                 "officials seeing further rises."),
    dict(num=10, place="KERCH", tag="WAR", scene="kerch",
         headline="Kerch span falls, Azov lane blocked",
         summary="Hit a third time in three days; a 270m road span lies in "
                 "the strait, shutting the channel."),
    dict(num=11, place="NEW YORK", tag="CULTURE", scene="vangogh",
         headline="Van Gogh sells for record $190.4m",
         summary="'Blossoming Chestnut Trees' sets a new auction record for "
                 "the artist at Sotheby's, New York."),
    dict(num=12, place="FLORIDA", tag="WEATHER", scene="florida",
         headline="Flooded Florida braces for more rain",
         summary="A foot of rain brought 300 rescue calls in Hollywood; "
                 "schools shut Thursday."),
    dict(num=13, place="US", tag="BUSINESS", scene="nvidia",
         headline="Nvidia chief promises December pay rises",
         summary="Interim CEO Kress tells staff after a record $115.8bn "
                 "quarter, up 103% on a year ago."),
]

BRIEFS = [
    (14, "PEW", "Islam to pass Christianity by 2035"),
    (15, "VOYAGER", "NASA confirms the probe is one light-day out"),
    (16, "YELLOW LINE", "Israeli tanks cross into central Gaza"),
    (17, "UNICREDIT", "Commerzbank deal; HQ stays in Frankfurt"),
    (18, "HEGSETH", "US–Venezuela military deal signed in Caracas"),
    (19, "APEC", "Leaders close the Shenzhen summit"),
    (20, "PELTOLA", "Alaska win gives Democrats a 56–44 Senate"),
    (21, "INDIA–JAPAN", "2+2 defence talks held in Tokyo"),
    (22, "CARNEY", "Canada recalibrates ties with China"),
    (23, "AI CYBER", "US senators warn threats outpace defences"),
    (24, "GROCERY", "Weight-loss drugs cut UK grocery spend £1bn"),
    (25, "LPG TANKER", "Sunk off Bulgaria, hit by projectiles"),
    (26, "LIBYA", "Cocaine and millions of pills seized in the east"),
    (27, "MICROSOFT", "AI services sale talks with ByteDance"),
    (28, "OIL", "Falls 3.2% to $83.26 a barrel"),
    (29, "MODI", "Meets the Prince and Princess of Wales"),
    (30, "GEOLOGY", "Earth's missing billion years may be solved"),
    (31, "MÉLENCHON", "Minister: he could win the presidency"),
    (32, "DUCKETT", "133 puts England on top in Australia ODI"),
    (33, "DEUTSCHE BANK", "Epstein-linked payments of $582m"),
    (34, "SAUDI", "Says danger has passed in three cities"),
    (35, "GREEN CARDS", "US proposes tougher rules"),
]

FIGURES = [
    ("$81.3bn", "raised by Anthropic — the largest IPO on record"),
    ("15.9m", "GTA VI pre-orders banked before release day"),
    ("200,000", "evacuated ahead of Cyclone Akvan"),
    ("$120bn", "adaptation finance proposed at COP31"),
    ("730,000", "Rohingya who fled in 2017 — the ICJ case"),
    ("16bn miles", "Voyager 1 from Earth — one light-day out"),
]

REGIONS = [
    ("EUROPE 7", (29, 53, 140)),
    ("THE AMERICAS 13", (34, 122, 72)),
    ("ASIA-PACIFIC 5", (179, 38, 30)),
    ("MIDEAST 3", (176, 112, 52)),
    ("AFRICA 1", (176, 132, 52)),
    ("OCEANIA 1", (42, 122, 122)),
    ("WORLD 5", (90, 90, 90)),
]

DATE_CHECK = ("DATE CHECK — FIRST REPORTED EARLIER, SO NOT ON THIS PAGE AS NEWS: "
              "the EU's proposed €45bn loan for Ukraine (18 Nov) · Australia's "
              "sanctions on West Bank settlers (17 Nov) · the NSA network outage "
              "(17 Nov) · KPMG's Australia job cuts (18 Nov) · Spain's general "
              "strike (11 Nov).")

FOOTER = ("Every story here happened, or was first reported, on Thursday 19 November 2026. "
          "Sources: Reuters, AP, AFP, BBC, The Hindu, IMD, NASA, ICJ, Pew Research, "
          "UN News, Sotheby's, Nvidia. Original drawings.")

# ---------------------------------------------------------------- card scenes
# Every scene draws on its own panel at whatever size it is asked for
# (heroes 314x108, small cards 188x50), so all coordinates are fractions
# of the panel. Fixed seeds only.

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


def scene_flags(w, h):
    """Three flags (US, China, Russia) over a dark skyline: Shenzhen."""
    img, d = new_panel(w, h, (36, 44, 66))
    scatter_stars(d, w, int(h * 0.6), 14, 5)
    # Skyline.
    rng = random.Random(9)
    x = 0
    while x < w:
        bw = rng.randint(int(w * 0.10), int(w * 0.16))
        bh = rng.randint(int(h * 0.35), int(h * 0.62))
        d.rectangle([x, h - bh, x + bw, h], fill=(12, 12, 20))
        for wy in range(h - bh + 4, h - 3, 6):
            for wx in range(x + 3, x + bw - 3, 6):
                if rng.random() < 0.4:
                    d.rectangle([wx, wy, wx + 2, wy + 3],
                                fill=rng.choice([(255, 214, 64), (64, 224, 255)]))
        x += bw + 2
    # Three flags on poles above the roofs.
    specs = [(0.10, "us"), (0.42, "cn"), (0.74, "ru")]
    fw, fh = int(w * 0.20), int(h * 0.42)
    for fx, kind in specs:
        x0 = int(w * fx)
        d.rectangle([x0 + fw // 2, int(h * 0.06), x0 + fw // 2 + 2, int(h * 0.62)],
                    fill=(220, 220, 220))
        if kind == "us":
            for i in range(7):
                d.rectangle([x0, int(h * 0.06) + i * fh // 7,
                             x0 + fw, int(h * 0.06) + (i + 1) * fh // 7],
                            fill=RED if i % 2 == 0 else (250, 250, 248))
            d.rectangle([x0, int(h * 0.06), x0 + fw // 2, int(h * 0.06) + fh // 2],
                        fill=NAVY)
        elif kind == "cn":
            d.rectangle([x0, int(h * 0.06), x0 + fw, int(h * 0.06) + fh],
                        fill=(222, 32, 24))
            d.ellipse([x0 + 3, int(h * 0.06) + 3, x0 + 11, int(h * 0.06) + 11],
                      fill=(255, 222, 64))
        else:
            d.rectangle([x0, int(h * 0.06), x0 + fw, int(h * 0.06) + fh // 3],
                        fill=(250, 250, 248))
            d.rectangle([x0, int(h * 0.06) + fh // 3, x0 + fw,
                         int(h * 0.06) + 2 * fh // 3], fill=(29, 53, 180))
            d.rectangle([x0, int(h * 0.06) + 2 * fh // 3, x0 + fw,
                         int(h * 0.06) + fh], fill=(200, 30, 30))
    return img


def scene_vicecity(w, h):
    """Vice City at night: indigo sky, synthwave sun, neon skyline, road."""
    img, d = new_panel(w, h, (22, 12, 48))
    horizon = int(h * 0.68)
    for row in range(horizon):
        t = row / max(1, horizon - 1)
        d.line([(0, row), (w, row)], fill=lerp((22, 12, 48), (96, 34, 76), t))
    scatter_stars(d, w, int(h * 0.45), 16, 7)
    # Sun, drawn over the skyline.
    cx, cy, r = int(w * 0.72), int(h * 0.48), int(h * 0.34)
    for k in range(8):
        rr = r - k * 3
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=lerp((255, 94, 120), (255, 170, 60), k / 7))
    for i, gap in enumerate([1, 2, 2, 3]):
        yy = cy + int(h * 0.06) + i * int(h * 0.07)
        d.rectangle([cx - r, yy, cx + r, yy + gap], fill=(10, 8, 26))
    rng = random.Random(11)
    x = 0
    while x < w:
        bw = rng.randint(int(w * 0.08), int(w * 0.14))
        bh = rng.randint(int(h * 0.30), int(h * 0.58))
        d.rectangle([x, horizon - bh, x + bw, horizon], fill=(8, 6, 22))
        for wy in range(horizon - bh + 4, horizon - 3, 6):
            for wx in range(x + 3, x + bw - 3, 6):
                if rng.random() < 0.45:
                    d.rectangle([wx, wy, wx + 2, wy + 3],
                                fill=rng.choice([(255, 214, 64), (64, 224, 255),
                                                 (255, 64, 160)]))
        x += bw + 2
    d.rectangle([0, horizon, w, h], fill=(12, 9, 24))
    for dx in range(6, w - 14, 26):
        d.rectangle([dx, horizon + 4, dx + 13, horizon + 6], fill=(255, 214, 64))
    return img


def scene_chart(w, h):
    """Rising green bars on dark green: the IPO debut."""
    img, d = new_panel(w, h, (16, 48, 32))
    d.line([(0, int(h * 0.78)), (w, int(h * 0.78))], fill=(120, 200, 140), width=2)
    rng = random.Random(13)
    bars = 8
    bw = w // (bars + 1)
    for i in range(bars):
        bh = int(h * (0.18 + 0.62 * (i / (bars - 1)) ** 1.4))
        x0 = bw // 2 + i * bw
        d.rectangle([x0, int(h * 0.78) - bh, x0 + bw - 6, int(h * 0.78)],
                    fill=(64, 190, 110))
    # Trend arrow over the bars.
    d.line([(int(w * 0.08), int(h * 0.62)), (int(w * 0.55), int(h * 0.30)),
            (int(w * 0.92), int(h * 0.14))], fill=(255, 222, 64), width=3)
    d.polygon([(int(w * 0.92), int(h * 0.14)), (int(w * 0.82), int(h * 0.10)),
               (int(w * 0.86), int(h * 0.24))], fill=(255, 222, 64))
    d.text((int(w * 0.05), int(h * 0.06)), "$83", font=sans_b(max(11, int(h * 0.28))),
           fill=(255, 255, 255))
    return img


def scene_court(w, h):
    """Peace Palace front: pale stone, columns, pediment, scales."""
    img, d = new_panel(w, h, (214, 208, 196))
    d.rectangle([0, int(h * 0.82), w, h], fill=(120, 118, 106))
    # Pediment.
    d.polygon([(int(w * 0.18), int(h * 0.34)), (int(w * 0.82), int(h * 0.34)),
               (int(w * 0.5), int(h * 0.10))], fill=(238, 234, 224))
    d.rectangle([int(w * 0.16), int(h * 0.34), int(w * 0.84), int(h * 0.40)],
                fill=(238, 234, 224))
    # Columns.
    for i in range(5):
        cx = int(w * (0.24 + i * 0.13))
        d.rectangle([cx, int(h * 0.40), cx + int(w * 0.03), int(h * 0.82)],
                    fill=(250, 248, 242))
    d.rectangle([int(w * 0.16), int(h * 0.82), int(w * 0.84), int(h * 0.88)],
                fill=(238, 234, 224))
    # Scales above the pediment.
    sx, sy = int(w * 0.5), int(h * 0.06)
    d.line([(sx, sy - 4), (sx, sy + 6)], fill=GOLD, width=2)
    d.line([(sx - 8, sy + 2), (sx + 8, sy + 2)], fill=GOLD, width=2)
    d.polygon([(sx - 10, sy + 8), (sx - 5, sy + 2), (sx - 5, sy + 8)], fill=GOLD)
    d.polygon([(sx + 10, sy + 8), (sx + 5, sy + 2), (sx + 5, sy + 8)], fill=GOLD)
    return img


def scene_gulf(w, h):
    """Night over the Gulf: dark sky, base silhouette, orange bursts."""
    img, d = new_panel(w, h, (16, 24, 48))
    scatter_stars(d, w, int(h * 0.6), 14, 15)
    d.rectangle([0, int(h * 0.66), w, h], fill=(196, 164, 120))
    d.rectangle([int(w * 0.08), int(h * 0.52), int(w * 0.30), int(h * 0.66)],
                fill=(70, 62, 52))
    d.pieslice([int(w * 0.08), int(h * 0.34), int(w * 0.30), int(h * 0.66)],
               180, 360, fill=(88, 78, 64))
    d.rectangle([int(w * 0.72), int(h * 0.44), int(w * 0.76), int(h * 0.66)],
                fill=(70, 62, 52))
    for bx, by in [(0.45, 0.42), (0.62, 0.30), (0.85, 0.46)]:
        px, py = int(w * bx), int(h * by)
        for k in range(8):
            a = k * math.pi / 4
            d.line([(px, py), (px + int(9 * math.cos(a)), py + int(9 * math.sin(a)))],
                   fill=(255, 150, 40), width=2)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 210, 90))
    return img


def scene_cyclone(w, h):
    """Spiral storm over blue sea, rain at the edges, coast at right."""
    img, d = new_panel(w, h, (58, 110, 158))
    cx, cy = int(w * 0.40), int(h * 0.52)
    for r in range(int(h * 0.46), 3, -4):
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 20, fill=(255, 255, 255), width=3)
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 200, fill=(190, 220, 240), width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255))
    rng = random.Random(21)
    for _ in range(18):
        x = rng.randint(0, w - 4)
        y = rng.randint(0, h - 8)
        d.line([(x, y), (x - 3, y + 7)], fill=(200, 225, 245), width=1)
    d.polygon([(int(w * 0.82), 0), (w, 0), (w, h), (int(w * 0.88), h),
               (int(w * 0.84), int(h * 0.45))], fill=(214, 196, 158))
    return img


def scene_cop(w, h):
    """Antalya climate talks: teal sky, big sun, globe, leaf."""
    img, d = new_panel(w, h, (32, 120, 110))
    d.ellipse([int(w * 0.74), int(h * 0.04), int(w * 0.94), int(h * 0.44)],
              fill=(255, 214, 64))
    d.ellipse([int(w * 0.06), int(h * 0.16), int(w * 0.46), int(h * 0.96)],
              fill=(64, 170, 150))
    d.ellipse([int(w * 0.06), int(h * 0.16), int(w * 0.46), int(h * 0.96)],
              outline=(220, 240, 235), width=2)
    d.arc([int(w * 0.12), int(h * 0.28), int(w * 0.40), int(h * 0.84)],
          200, 340, fill=(255, 255, 255), width=2)
    d.line([(int(w * 0.50), int(h * 0.66)), (int(w * 0.60), int(h * 0.44))],
           fill=(120, 220, 130), width=3)
    d.ellipse([int(w * 0.56), int(h * 0.32), int(w * 0.70), int(h * 0.52)],
              fill=(120, 220, 130))
    d.rectangle([0, int(h * 0.90), w, h], fill=(214, 196, 158))
    return img


def scene_capitol(w, h):
    """Capitol dome: grey stone building, white columns, solid dome."""
    img, d = new_panel(w, h, (210, 206, 196))
    d.rectangle([0, int(h * 0.80), w, h], fill=(88, 124, 78))
    # Main block, stone grey with a darker base.
    d.rectangle([int(w * 0.08), int(h * 0.58), int(w * 0.92), int(h * 0.80)],
                fill=(168, 162, 150))
    d.rectangle([int(w * 0.08), int(h * 0.74), int(w * 0.92), int(h * 0.80)],
                fill=(140, 134, 122))
    # Columns.
    for i in range(5):
        cx = int(w * (0.16 + i * 0.15))
        d.rectangle([cx, int(h * 0.58), cx + int(w * 0.035), int(h * 0.74)],
                    fill=(250, 248, 242))
    # Dome: solid light stone with a dark outline, on a drum.
    d.rectangle([int(w * 0.42), int(h * 0.44), int(w * 0.58), int(h * 0.58)],
                fill=(168, 162, 150))
    d.pieslice([int(w * 0.36), int(h * 0.10), int(w * 0.64), int(h * 0.52)],
               180, 360, fill=(232, 228, 218), outline=(110, 106, 96), width=2)
    d.rectangle([int(w * 0.49), int(h * 0.02), int(w * 0.51), int(h * 0.10)],
                fill=(110, 106, 96))
    # Bunting across the lawn.
    for i, col in enumerate([(179, 38, 30), NAVY] * 6):
        x0 = i * (w // 12)
        d.polygon([(x0, int(h * 0.80)), (x0 + w // 12, int(h * 0.80)),
                   (x0 + w // 24, int(h * 0.93))], fill=col)
    return img


def scene_fed(w, h):
    """Rate chart: rising bars with an upward arrow, navy on cream."""
    img, d = new_panel(w, h, (238, 234, 224))
    d.line([(0, int(h * 0.80)), (w, int(h * 0.80))], fill=(120, 116, 108), width=2)
    rng = random.Random(17)
    bars = 7
    bw = w // (bars + 1)
    for i in range(bars):
        bh = int(h * (0.15 + 0.55 * (i / (bars - 1))))
        x0 = bw // 2 + i * bw
        d.rectangle([x0, int(h * 0.80) - bh, x0 + bw - 5, int(h * 0.80)],
                    fill=NAVY if i < bars - 1 else RED)
    d.line([(int(w * 0.08), int(h * 0.66)), (int(w * 0.50), int(h * 0.34)),
            (int(w * 0.92), int(h * 0.12))], fill=RED, width=3)
    d.polygon([(int(w * 0.92), int(h * 0.12)), (int(w * 0.82), int(h * 0.08)),
               (int(w * 0.86), int(h * 0.22))], fill=RED)
    return img


def scene_kerch(w, h):
    """Kerch Strait: a bridge with its middle span dropped into the sea."""
    img, d = new_panel(w, h, (168, 196, 205))
    d.rectangle([0, int(h * 0.62), w, h], fill=(58, 110, 158))
    # Deck, left and right of the gap.
    d.rectangle([0, int(h * 0.42), int(w * 0.38), int(h * 0.50)], fill=(90, 88, 84))
    d.rectangle([int(w * 0.62), int(h * 0.42), w, int(h * 0.50)], fill=(90, 88, 84))
    # Pylons.
    d.rectangle([int(w * 0.10), int(h * 0.20), int(w * 0.13), int(h * 0.62)],
                fill=(70, 68, 64))
    d.rectangle([int(w * 0.86), int(h * 0.20), int(w * 0.89), int(h * 0.62)],
                fill=(70, 68, 64))
    # Fallen span in the water, tilted.
    d.polygon([(int(w * 0.40), int(h * 0.62)), (int(w * 0.58), int(h * 0.58)),
               (int(w * 0.60), int(h * 0.68)), (int(w * 0.42), int(h * 0.72))],
              fill=(70, 68, 64))
    for dx in range(0, w, 14):
        d.line([(dx, int(h * 0.70)), (dx + 7, int(h * 0.70))], fill=(220, 235, 245),
               width=1)
    return img


def scene_vangogh(w, h):
    """Sunflowers on deep blue: the record sale."""
    img, d = new_panel(w, h, (32, 64, 140))
    d.rectangle([0, int(h * 0.78), w, h], fill=(120, 96, 52))
    for fx, fy, fr in [(0.30, 0.38, 0.20), (0.62, 0.30, 0.16), (0.80, 0.52, 0.13)]:
        cx, cy, r = int(w * fx), int(h * fy), int(h * fr)
        for k in range(12):
            a = k * math.pi / 6
            d.ellipse([cx + int((r + 4) * math.cos(a)) - 4,
                       cy + int((r + 4) * math.sin(a)) - 4,
                       cx + int((r + 4) * math.cos(a)) + 4,
                       cy + int((r + 4) * math.sin(a)) + 4], fill=(255, 214, 64))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 70, 20))
        d.line([(cx, cy + r), (cx, int(h * 0.78))], fill=(60, 110, 50), width=3)
    return img


def scene_florida(w, h):
    """Rain over a flooded street: grey clouds, rain, rooftops."""
    img, d = new_panel(w, h, (120, 140, 160))
    for cx, cy, r in [(0.25, 0.22, 0.20), (0.55, 0.16, 0.24), (0.82, 0.24, 0.18)]:
        d.ellipse([int(w * (cx - r)), int(h * (cy - r * 0.7)),
                   int(w * (cx + r)), int(h * (cy + r * 0.7))], fill=(90, 100, 115))
    rng = random.Random(23)
    for _ in range(22):
        x = rng.randint(0, w - 4)
        y = rng.randint(int(h * 0.35), int(h * 0.75))
        d.line([(x, y), (x - 3, y + 8)], fill=(200, 225, 245), width=1)
    d.rectangle([0, int(h * 0.78), w, h], fill=(70, 120, 150))
    d.polygon([(int(w * 0.12), int(h * 0.78)), (int(w * 0.28), int(h * 0.60)),
               (int(w * 0.44), int(h * 0.78))], fill=(150, 80, 60))
    d.polygon([(int(w * 0.58), int(h * 0.78)), (int(w * 0.74), int(h * 0.62)),
               (int(w * 0.90), int(h * 0.78))], fill=(120, 70, 55))
    return img


def scene_nvidia(w, h):
    """A green chip on a dark board, pins out, glow behind."""
    img, d = new_panel(w, h, (14, 26, 18))
    d.ellipse([int(w * 0.28), int(h * 0.05), int(w * 0.72), int(h * 0.95)],
              fill=(24, 90, 48))
    cx, cy = int(w * 0.5), int(h * 0.5)
    s = int(h * 0.30)
    d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=(32, 160, 90))
    d.rectangle([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2],
                fill=(16, 60, 34))
    for i in range(-2, 3):
        off = i * s // 2
        d.line([(cx + off, cy - s), (cx + off, cy - s - 4)], fill=(200, 220, 200),
               width=2)
        d.line([(cx + off, cy + s), (cx + off, cy + s + 4)], fill=(200, 220, 200),
               width=2)
        d.line([(cx - s, cy + off), (cx - s - 4, cy + off)], fill=(200, 220, 200),
               width=2)
        d.line([(cx + s, cy + off), (cx + s + 4, cy + off)], fill=(200, 220, 200),
               width=2)
    return img


SCENES = {
    "flags": scene_flags,
    "vicecity": scene_vicecity,
    "chart": scene_chart,
    "court": scene_court,
    "gulf": scene_gulf,
    "cyclone": scene_cyclone,
    "cop": scene_cop,
    "capitol": scene_capitol,
    "fed": scene_fed,
    "kerch": scene_kerch,
    "vangogh": scene_vangogh,
    "florida": scene_florida,
    "nvidia": scene_nvidia,
}

# ---------------------------------------------------------------- the map
# Simplified continent outlines in lon/lat, drawn into the navy map
# panel. Pins mark the 13 card stories; grey dots mark the briefs.

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 62), (-60, 55), (-55, 47), (-70, 42), (-75, 35), (-80, 26),
     (-90, 21), (-97, 26), (-105, 20), (-110, 24), (-125, 40), (-125, 49),
     (-140, 60), (-158, 58)],
    # South America
    [(-80, 10), (-60, 5), (-50, 0), (-35, -8), (-40, -20), (-48, -28),
     (-58, -35), (-65, -45), (-70, -55), (-73, -40), (-72, -20), (-80, -5)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (28, 59), (30, 60), (24, 65), (18, 70), (12, 71),
     (5, 60), (-5, 58), (-10, 52), (-10, 43)],
    # Africa
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (28, -33), (20, -35),
     (15, -27), (12, -18), (13, -5), (9, 4), (-8, 5)],
    # Asia
    [(30, 60), (40, 68), (60, 70), (90, 75), (120, 73), (150, 70), (170, 66),
     (180, 65), (162, 60), (158, 52), (142, 50), (140, 40), (130, 35),
     (127, 40), (120, 30), (110, 20), (105, 10), (100, 8), (95, 15),
     (90, 22), (80, 15), (77, 8), (72, 20), (66, 25), (60, 25), (55, 27),
     (50, 29), (48, 30), (43, 35), (35, 36), (30, 36), (30, 42), (28, 45),
     (30, 50)],
    # Australia
    [(113, -22), (122, -14), (132, -12), (142, -11), (150, -22), (153, -32),
     (150, -37), (140, -38), (130, -32), (122, -34), (114, -30)],
    # New Zealand
    [(167, -45), (174, -41), (178, -38), (174, -42), (168, -46)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41),
     (143, 44), (145, 44), (141, 40), (139, 37), (136, 35), (133, 34)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -22), (45, -25), (43, -21)],
]

# (number, lon, lat, dx, dy) — dx/dy nudge pins apart where they cluster.
PINS = [
    (1, 114, 22, 0, 0), (2, -74, 41, 0, 0), (3, -74, 41, 10, -6),
    (4, 4, 52, 0, 0), (5, 48, 29, 5, 5), (6, 85, 20, 0, 0),
    (7, 31, 37, -8, 6), (8, -77, 39, -8, -8), (9, -77, 39, 8, 8),
    (10, 36, 45, 6, -6), (11, -74, 41, -10, 6), (12, -80, 26, 0, 0),
    (13, -122, 37, 0, 0),
]

# Grey dots for briefs with a clear place (lon, lat).
DOTS = [
    (8, 50), (-150, 64), (139, 36), (-76, 45), (25, 43), (20, 32),
    (77, 29), (147, -43), (47, 25), (2, 49), (-67, 10), (0, 51),
]


def lonlat_to_xy(mx, my, mw, mh, lon, lat):
    x = mx + (lon + 180.0) / 360.0 * mw
    y = my + (75.0 - lat) / 135.0 * mh
    return x, y


def draw_map(d, mx, my, mw, mh):
    d.rectangle([mx, my, mx + mw, my + mh], fill=NAVY)
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(mx, my, mw, mh, lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=MAP_TAN)
    for lon, lat in DOTS:
        x, y = lonlat_to_xy(mx, my, mw, mh, lon, lat)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(200, 200, 200))
    for num, lon, lat, dx, dy in PINS:
        x, y = lonlat_to_xy(mx, my, mw, mh, lon, lat)
        x += dx
        y += dy
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=RED,
                  outline=(255, 255, 255), width=1)
        label = str(num)
        lw = width(d, label, sans_b(8))
        d.text((x - lw / 2, y - 5), label, font=sans_b(8), fill=(255, 255, 255))


# ---------------------------------------------------------------- layout

def draw_header(d):
    tracked(d, (MARGIN, 12), "THE WORLD IN ONE DAY", sans_b(13), RED, tracking=2)
    badge = "35 STORIES · 6 CONTINENTS · ONE PAGE"
    bw = width(d, badge, sans_b(12))
    d.text((PAGE - MARGIN - bw, 13), badge, font=sans_b(12), fill=SOFT_INK)
    d.text((MARGIN, 28), "Thursday 19 November 2026", font=serif_b(54), fill=INK)
    d.text((MARGIN, 88),
           "Three leaders meet in Shenzhen · A court rules on Myanmar · "
           "The biggest IPO ever debuts",
           font=serif_i(15), fill=RED)
    d.line([(MARGIN, 110), (PAGE - MARGIN, 110)], fill=INK, width=2)
    d.line([(MARGIN, 113), (PAGE - MARGIN, 113)], fill=INK, width=1)


def draw_region_bar(d):
    y, h = 118, 24
    seg = CONTENT / len(REGIONS)
    for i, (label, colour) in enumerate(REGIONS):
        x0 = MARGIN + i * seg
        d.rectangle([x0, y, x0 + seg - 1, y + h], fill=colour)
        lw = width(d, label, sans_b(11))
        d.text((x0 + (seg - lw) / 2, y + 6), label, font=sans_b(11),
               fill=(255, 255, 255))


def draw_figures(d):
    y = 148
    col = CONTENT / len(FIGURES)
    for i, (number, caption) in enumerate(FIGURES):
        x0 = MARGIN + i * col
        d.text((x0, y), number, font=sans_b(22), fill=RED)
        lines = wrap(d, caption, sans(10), col - 8, max_lines=2)
        cy = y + 28
        for line in lines:
            d.text((x0, cy), line, font=sans(10), fill=SOFT_INK)
            cy += 12
    d.line([(MARGIN, 208), (PAGE - MARGIN, 208)], fill=INK, width=1)


def draw_hero(d, page, feat, x, y):
    w, h = 314, 216
    scene = SCENES[feat["scene"]](w, 108)
    page.paste(scene, (x, y))
    d.rectangle([x, y, x + 26, y + 22], fill=RED)
    num = str(feat["num"])
    nw = width(d, num, sans_b(13))
    d.text((x + (26 - nw) / 2, y + 3), num, font=sans_b(13), fill=(255, 255, 255))
    ty = y + 114
    tracked(d, (x, ty), feat["place"], sans_b(10), RED, tracking=1)
    kw = width(d, feat["place"], sans_b(10)) + len(feat["place"]) * 1
    d.text((x + kw + 8, ty), feat["tag"], font=sans_b(10), fill=INK)
    lines = wrap(d, feat["headline"], serif_b(19), w - 4, max_lines=2)
    hy = ty + 14
    for line in lines:
        d.text((x, hy), line, font=serif_b(19), fill=INK)
        hy += 22
    slines = wrap(d, feat["summary"], serif(12), w - 4, max_lines=3)
    sy = ty + 14 + 2 * 22 + 2
    for line in slines:
        d.text((x, sy), line, font=serif(12), fill=INK)
        sy += 15


def draw_card(d, page, feat, x, y):
    w, h = 188, 148
    scene = SCENES[feat["scene"]](w, 50)
    page.paste(scene, (x, y))
    d.rectangle([x, y, x + 22, y + 19], fill=RED)
    num = str(feat["num"])
    nw = width(d, num, sans_b(12))
    d.text((x + (22 - nw) / 2, y + 3), num, font=sans_b(12), fill=(255, 255, 255))
    ty = y + 54
    tracked(d, (x, ty), feat["place"], sans_b(9), RED, tracking=1)
    kw = width(d, feat["place"], sans_b(9)) + len(feat["place"]) * 1
    d.text((x + kw + 6, ty), feat["tag"], font=sans_b(9), fill=INK)
    lines = wrap(d, feat["headline"], serif_b(14), w - 2, max_lines=2)
    hy = ty + 13
    for line in lines:
        d.text((x, hy), line, font=serif_b(14), fill=INK)
        hy += 16
    slines = wrap(d, feat["summary"], sans(11), w - 2, max_lines=3)
    sy = ty + 13 + 2 * 16 + 2
    for line in slines:
        d.text((x, sy), line, font=sans(11), fill=SOFT_INK)
        sy += 13


def draw_bottom(d, y):
    d.text((MARGIN, y), "WHERE IT HAPPENED", font=sans_b(12), fill=INK)
    bx = MARGIN + 300 + 16
    d.text((bx, y), "ALSO ON THURSDAY 19 NOVEMBER — 22 MORE STORIES",
           font=sans_b(12), fill=INK)
    d.line([(MARGIN, y + 18), (PAGE - MARGIN, y + 18)], fill=INK, width=1)
    draw_map(d, MARGIN, y + 24, 300, 158)
    col_w = 326
    for col in range(2):
        cx = bx + col * (col_w + 8)
        for row in range(11):
            num, place, text = BRIEFS[col * 11 + row]
            line = "%d · %s — %s" % (num, place, text)
            lines = wrap(d, line, sans(10), col_w, max_lines=1)
            d.text((cx, y + 24 + row * 14), lines[0] if lines else "",
                   font=sans(10), fill=INK)


def draw_date_check(d, y):
    d.rectangle([MARGIN, y, PAGE - MARGIN, y + 38], outline=RED, width=2)
    lines = wrap(d, DATE_CHECK, sans(10), CONTENT - 20, max_lines=2)
    ty = y + 5
    for line in lines:
        d.text((MARGIN + 10, ty), line, font=sans(10), fill=INK)
        ty += 13


def build(path):
    page = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(page)
    draw_header(d)
    draw_region_bar(d)
    draw_figures(d)
    gx, gy = MARGIN, 216
    for idx, feat in enumerate(HEROES):
        draw_hero(d, page, feat, gx + idx * (314 + 17), gy)
    gx, gy = MARGIN, 442
    for idx, feat in enumerate(CARDS[:5]):
        draw_card(d, page, feat, gx + idx * (188 + 9), gy)
    gy = 600
    for idx, feat in enumerate(CARDS[5:]):
        draw_card(d, page, feat, gx + idx * (188 + 9), gy)
    draw_bottom(d, 758)
    draw_date_check(d, 948)
    d.text((MARGIN, 992),
           "Every story here happened, or was first reported, on Thursday "
           "19 November 2026.",
           font=sans(9), fill=SOFT_INK)
    d.text((MARGIN, 1004),
           "Sources: Reuters, AP, AFP, BBC, The Hindu, IMD, NASA, ICJ, Pew "
           "Research, UN News, Sotheby's, Nvidia. Original drawings.",
           font=sans(9), fill=SOFT_INK)
    page.save(path, format="PNG")
    return path


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    build(out)
    print("wrote", out)
