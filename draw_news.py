#!/usr/bin/env python3
"""Draw a newspaper front page (1024x1024 PNG) for make.fun news-image-20261120.
PIL only, no network. Classic broadsheet: masthead, lead story with three
flags, two-column grid for stories 2-3, full-width story 4, bottom strip.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)      # off-white
INK = (26, 26, 26)           # dark ink
RED = (139, 26, 26)          # deep red accent
GREY = (90, 86, 78)
LIGHT = (232, 226, 214)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_I = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

M = 36                      # side margin
CW = W - 2 * M              # content width = 952


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, text, f):
    return draw.textlength(text, font=f)


def fit_font(draw, text, path, max_w, start, min_size=10):
    """Largest size <= start at which text fits max_w."""
    size = start
    while size > min_size:
        f = font(path, size)
        if text_w(draw, text, f) <= max_w:
            return f
        size -= 1
    return font(path, min_size)


def wrap(draw, text, f, max_w):
    """Word-wrap text to lines fitting max_w."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def star_points(cx, cy, r_out, r_in, rot=-90):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_us_flag(d, x, y, w, h):
    """Simple US flag: 13 stripes + blue canton with dot stars."""
    stripe = h / 13
    for i in range(13):
        if i % 2 == 0:
            d.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe], fill=(178, 34, 52))
    canton_w, canton_h = w * 0.4, stripe * 7
    d.rectangle([x, y, x + canton_w, y + canton_h], fill=(28, 48, 94))
    for r in range(5):
        for c in range(6):
            sx = x + canton_w * (c + 0.5) / 6
            sy = y + canton_h * (r + 0.5) / 5
            d.ellipse([sx - 1.6, sy - 1.6, sx + 1.6, sy + 1.6], fill=(255, 255, 255))
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def draw_china_flag(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    d.polygon(star_points(x + w * 0.16, y + h * 0.28, h * 0.22, h * 0.09), fill=(255, 222, 0))
    for (fx, fy, fr) in [(0.34, 0.12, 0.07), (0.42, 0.24, 0.07),
                         (0.42, 0.40, 0.07), (0.34, 0.50, 0.07)]:
        d.polygon(star_points(x + w * fx, y + h * fy, h * fr, h * fr * 0.4),
                  fill=(255, 222, 0))
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def draw_russia_flag(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def draw_bridge(d, x, y, w, h):
    """Suspension bridge icon: towers, sagging main cable, deck, water."""
    deck = y + h - 12
    t1, t2 = x + w * 0.22, x + w * 0.78
    # sagging main cable: tower top -> dip -> tower top
    def cable(x0, y0, x1, y1, sag):
        pts = []
        for i in range(21):
            t = i / 20
            bx = x0 + (x1 - x0) * t
            by = y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)
            pts.append((bx, by))
        d.line(pts, fill=INK, width=2)
    cable(x, deck - 2, t1, y + 6, 26)
    cable(t1, y + 6, t2, y + 6, 22)
    cable(t2, y + 6, x + w, deck - 2, 26)
    # towers
    for tx in (t1, t2):
        d.line([tx, y + 6, tx, deck], fill=INK, width=4)
    # suspenders from midspan cable down to deck
    for sx in (x + w * 0.36, x + w * 0.5, x + w * 0.64):
        d.line([sx, y + 6 + 22 * 4 * ((sx - t1) / (t2 - t1)) *
                (1 - (sx - t1) / (t2 - t1)), sx, deck], fill=GREY, width=1)
    # deck
    d.line([x, deck, x + w, deck], fill=INK, width=4)
    # water lines
    for wy in (deck + 5, deck + 9):
        d.line([x, wy, x + w, wy], fill=(120, 140, 160), width=1)


def draw_scales(d, x, y, w, h):
    """Scales of justice icon: pole, crossbar, two hanging pans."""
    cx = x + w / 2
    base = y + h - 6
    d.line([cx, y + 4, cx, base], fill=INK, width=4)
    d.line([x + 8, base, x + w - 8, base], fill=INK, width=4)
    d.line([x + 6, y + 12, x + w - 6, y + 12], fill=INK, width=3)
    d.polygon([(cx - 5, y), (cx + 5, y), (cx, y + 8)], fill=RED)
    for top_x, px in ((x + 6, x + w * 0.18), (x + w - 6, x + w * 0.82)):
        # strings from crossbar end to pan rim
        d.line([top_x, y + 12, px - 20, y + 32], fill=INK, width=2)
        d.line([top_x, y + 12, px + 20, y + 32], fill=INK, width=2)
        # bowl pan
        d.chord([px - 20, y + 28, px + 20, y + 50], 0, 180,
                fill=(210, 202, 186), outline=INK, width=2)


def draw_chart(d, x, y, w, h):
    """Rising stock chart icon."""
    d.line([x, y + h - 8, x + w, y + h - 8], fill=INK, width=2)
    d.line([x, y + h - 8, x, y + 4], fill=INK, width=2)
    pts = [(x + 6, y + h - 22), (x + w * 0.32, y + h - 34),
           (x + w * 0.52, y + h - 26), (x + w * 0.74, y + h - 48),
           (x + w - 8, y + h - 62)]
    d.line(pts, fill=RED, width=4, joint="curve")
    # arrowhead
    ax, ay = pts[-1]
    d.polygon([(ax, ay), (ax - 14, ay + 2), (ax - 4, ay + 12)], fill=RED)
    # bars
    for i, bh in enumerate((14, 24, 18, 34)):
        bx = x + 10 + i * (w - 20) / 4
        d.rectangle([bx, y + h - 8 - bh, bx + (w - 20) / 4 - 8, y + h - 8],
                    fill=(170, 180, 195))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- Masthead ----------
    f_mast = fit_font(d, "THE WORLD", SERIF_B, CW, 112)
    tw = text_w(d, "THE WORLD", f_mast)
    d.text(((W - tw) / 2, 14), "THE WORLD", font=f_mast, fill=INK)

    f_date = font(SERIF_I, 27)
    date = "Friday, 20 November 2026"
    dw = text_w(d, date, f_date)
    d.text(((W - dw) / 2, 128), date, font=f_date, fill=INK)

    d.rectangle([M, 166, W - M, 169], fill=RED)          # red rule
    d.rectangle([M, 173, W - M, 174], fill=INK)          # thin black rule

    # ---------- Lead story ----------
    y = 188
    f_label = font(SANS_B, 17)
    d.text((M, y), "WORLD  •  SUMMIT", font=f_label, fill=RED)
    y += 26

    lead = "TRUMP, XI AND PUTIN MEET IN SHENZHEN"
    f_lead = fit_font(d, lead, SERIF_B, CW, 46)
    d.text((M, y), lead, font=f_lead, fill=INK)
    y += 54

    f_stand = font(SERIF_I, 24)
    stand = ("First-ever three-way talks end with a \u2018peace declaration\u2019 \u2014 "
             "but no breakthrough on Ukraine.")
    for line in wrap(d, stand, f_stand, CW):
        d.text((M, y), line, font=f_stand, fill=INK)
        y += 30
    y += 8

    # Three flags illustration
    fw, fh = 300, 92
    gap = (CW - 3 * fw) / 2
    fx = M
    draw_us_flag(d, fx, y, fw, fh)
    fx += fw + gap
    draw_china_flag(d, fx, y, fw, fh)
    fx += fw + gap
    draw_russia_flag(d, fx, y, fw, fh)
    # flag captions
    f_cap = font(SANS, 15)
    for i, name in enumerate(("UNITED STATES", "CHINA", "RUSSIA")):
        cx = M + i * (fw + gap) + fw / 2
        nw = text_w(d, name, f_cap)
        d.text((cx - nw / 2, y + fh + 6), name, font=f_cap, fill=GREY)
    y += fh + 28

    d.rectangle([M, y, W - M, y + 1], fill=INK)
    y += 12

    # ---------- Stories 2 & 3: two columns ----------
    col_w = (CW - 24) / 2
    col2_x = M + col_w + 24
    row_top = y

    def story_column(x, label, headline, caption, icon_fn):
        yy = row_top
        d.text((x, yy), label, font=f_label, fill=RED)
        yy += 24
        f_h = fit_font(d, headline, SERIF_B, col_w, 30)
        lines = wrap(d, headline, f_h, col_w)
        for line in lines:
            d.text((x, yy), line, font=f_h, fill=INK)
            yy += 36
        yy += 4
        # icon band
        icon_fn(d, x, yy, col_w, 58)
        yy += 66
        f_c = font(SANS, 19)
        for line in wrap(d, caption, f_c, col_w):
            d.text((x, yy), line, font=f_c, fill=INK)
            yy += 24
        return yy

    end2 = story_column(M, "WAR IN UKRAINE", "KYIV UNDER FIRE",
                        "100+ missiles and 400 drones hit Kyiv overnight; "
                        "three bridges struck, power cut. Poland scrambled jets.",
                        draw_bridge)
    end3 = story_column(col2_x, "THE HAGUE", "COURT: MYANMAR COMMITTED GENOCIDE",
                        "The UN\u2019s top court finds Myanmar guilty of genocide "
                        "against the Rohingya, in a 9\u20136 vote.",
                        draw_scales)
    # vertical divider between columns
    d.rectangle([M + col_w + 11, row_top, M + col_w + 12, max(end2, end3) - 8],
                fill=(200, 192, 176))

    y = max(end2, end3) + 10
    d.rectangle([M, y, W - M, y + 1], fill=INK)
    y += 12

    # ---------- Story 4: full width ----------
    d.text((M, y), "MARKETS", font=f_label, fill=RED)
    y += 24
    head4 = "ANTHROPIC\u2019S $2 TRILLION DEBUT"
    f_h4 = fit_font(d, head4, SERIF_B, CW - 170, 36)
    d.text((M, y), head4, font=f_h4, fill=INK)
    # chart icon on the right
    draw_chart(d, W - M - 140, y - 18, 140, 78)
    y += 46
    f_c4 = font(SANS, 20)
    cap4 = ("The first purely AI company to list publicly; shares soared 34% "
            "on its Wall Street debut \u2014 the biggest IPO ever.")
    for line in wrap(d, cap4, f_c4, CW - 170):
        d.text((M, y), line, font=f_c4, fill=INK)
        y += 26
    y += 10
    d.rectangle([M, y, W - M, y + 1], fill=INK)
    y += 12

    # ---------- Bottom strip: small items ----------
    d.text((M, y), "ALSO TODAY", font=f_label, fill=RED)
    y += 26
    items = [
        "US and Venezuela restore military ties",
        "UK\u2013EU summit agrees youth mobility scheme",
        "Mexico\u2019s president flies economy to APEC \u2014 goes viral in China",
        "Trump pardons baseball legend Pete Rose",
    ]
    f_item = font(SANS, 19)
    for it in items:
        d.rectangle([M, y + 6, M + 8, y + 14], fill=RED)
        d.text((M + 16, y), it, font=f_item, fill=INK)
        y += 27

    # ---------- Footer ----------
    d.rectangle([M, 982, W - M, 983], fill=INK)
    f_foot = font(SANS_B, 14)
    foot = "THE WORLD  \u2022  FRIDAY, 20 NOVEMBER 2026"
    fw = text_w(d, foot, f_foot)
    d.text(((W - fw) / 2, 992), foot, font=f_foot, fill=GREY)

    img.save("/home/hatch/workspace/makefun/news-image-20261120/news-image/entry.png",
             "PNG", optimize=True)
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
