"""FIELD NOTES — an investigator's notebook.

Cream paper, black ink line drawings that draw themselves on and 'boil' at 12fps,
one red marker for annotations, serif headlines. Each beat is a new sheet sliding
over the last. Sounds: paper, pencil, felt-tip, soft desk thuds.
"""
import math

import numpy as np
import skia
from scipy import ndimage

import sfx
from engine import (W, H, rgb, paint, prog, lerp, clamp, ease_out_cubic, ease_out_back,
                    ease_in_out, font, draw_text, text_width, fit_size, trimmed, jitter,
                    path_from, hash01)
from script import timeline, HANDLE, END

PAPER = "#EDE4CC"
INK = "#1B1915"
RED = "#CF3A22"
GRID = "#6F8DB8"
HILITE = "#F4C430"

SERIF, SERIF_I, MONO, HAND = "InstrumentSerif-Regular", "InstrumentSerif-Italic", "JetBrainsMono-Medium", "PermanentMarker-Regular"
SLIDE = 0.32  # sheet transition length


def _paper_texture():
    rng = np.random.default_rng(7)
    fine = ndimage.gaussian_filter(rng.standard_normal((H, W)), 0.8)
    blotch = ndimage.gaussian_filter(rng.standard_normal((H // 8, W // 8)), 6)
    blotch = ndimage.zoom(blotch, 8, order=1)[:H, :W]
    fibres = ndimage.gaussian_filter(rng.standard_normal((H, W)), (0.6, 9))
    shade = 1 - 0.03 * fine / fine.std() - 0.018 * blotch / blotch.std() - 0.015 * fibres / fibres.std()
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
    shade *= 1 - 0.22 * np.clip(d - 0.35, 0, 1) ** 1.5
    base = np.array([int(PAPER[i:i + 2], 16) for i in (1, 3, 5)], float)
    img = np.clip(base[None, None, :] * shade[..., None], 0, 255).astype(np.uint8)
    rgba = np.dstack([img, np.full((H, W), 255, np.uint8)])
    return skia.Image.fromarray(np.ascontiguousarray(rgba))


PAPER_IMG = _paper_texture()


def boil_seed(t):
    return int(t * 12)


def ink(width=6, color=INK, a=1.0):
    return paint(color, a, stroke=width)


def wobbly(p, t, dev=1.6, seg=16, salt=0):
    return jitter(p, seg, dev, boil_seed(t) * 7 + salt)


# ---------- drawing primitives ----------

def loop_path(cx, cy, rx, ry, start=-1.9, sweep=2 * math.pi + 0.5, salt=0):
    """Loose marker loop around something — overshoots like a real hand."""
    pts = []
    n = 90
    for k in range(n + 1):
        u = k / n
        a = start + sweep * u
        wob = 1 + 0.035 * math.sin(3 * a + salt) + 0.06 * u
        pts.append((cx + rx * wob * math.cos(a), cy + ry * wob * math.sin(a)))
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    return p


def underline_path(x0, x1, y, salt=0):
    p = skia.Path()
    p.moveTo(x0, y + 4)
    p.quadTo((x0 + x1) / 2, y - 10 + 6 * math.sin(salt), x1, y + 2)
    return p


def ship_paths(w):
    """Line drawing of a 17th-century ship, centred on its waterline, width w."""
    hull = skia.Path()
    hull.moveTo(-0.52 * w, -0.06 * w)
    hull.lineTo(0.5 * w, -0.13 * w)
    hull.quadTo(0.42 * w, 0.14 * w, -0.3 * w, 0.13 * w)
    hull.quadTo(-0.5 * w, 0.1 * w, -0.52 * w, -0.06 * w)
    masts, sails = [], []
    for x, hgt, sw in [(-0.24, 0.62, 0.17), (0.04, 0.82, 0.22), (0.3, 0.55, 0.15)]:
        base_y = -0.08 * w - x * 0.06 * w
        masts.append(path_from([(x * w, base_y), (x * w, base_y - hgt * w)]))
        for tier in (0.18, 0.5):
            top = base_y - hgt * w * (1 - tier * 0.9) + 0.05 * w
            bot = top + hgt * w * 0.3
            s = skia.Path()
            s.moveTo((x - sw) * w, top)
            s.lineTo((x + sw) * w, top)
            s.quadTo((x + sw * 1.25) * w, (top + bot) / 2, (x + sw * 0.9) * w, bot)
            s.lineTo((x - sw * 0.9) * w, bot)
            s.quadTo((x - sw * 0.7) * w, (top + bot) / 2, (x - sw) * w, top)
            sails.append(s)
    flag_x, flag_y = 0.04 * w, -0.08 * w - 0.0024 * w - 0.82 * w
    flag = path_from([(flag_x, flag_y), (flag_x + 0.12 * w, flag_y + 0.03 * w), (flag_x, flag_y + 0.06 * w)], True)
    return hull, masts, sails, flag


def draw_ship(c, cx, cy, w, k, t, salt=0):
    """Draw a ship with draw-on progress k in 0..1."""
    hull, masts, sails, flag = ship_paths(w)
    c.save()
    c.translate(cx, cy + 3 * math.sin(t * 2.4 + salt))
    c.rotate(1.5 * math.sin(t * 1.9 + salt))
    line = wobbly(ink(5), t, 1.2, 12, salt)
    c.drawPath(hull, trimmed(line, 0, k * 2.2))
    for j, m in enumerate(masts):
        c.drawPath(m, trimmed(line, 0, k * 3 - 0.6 - 0.2 * j))
    for j, s in enumerate(sails):
        c.drawPath(s, trimmed(wobbly(ink(4), t, 1.0, 12, salt + j), 0, k * 3 - 1.1 - 0.15 * j))
    if k > 0.85:
        c.drawPath(flag, paint(RED, prog(k, 0.85, 0.15)))
    c.restore()


def waves(c, x0, x1, y, t, k=1.0, salt=0, a=0.55):
    p = skia.Path()
    x = x0
    p.moveTo(x, y)
    while x < x1:
        p.quadTo(x + 18, y - 10, x + 36, y)
        p.quadTo(x + 54, y + 10, x + 72, y)
        x += 72
    c.drawPath(p, trimmed(wobbly(ink(3, INK, a), t, 1.0, 14, salt), 0, k))


def hand_text(c, s, x, y, size, k, color=RED, align="left", rot=0):
    """Handwritten note revealed left-to-right as if being written."""
    f = font(HAND, size)
    w = text_width(s, f)
    x0 = x - w / 2 if align == "center" else x
    c.save()
    c.rotate(rot, x0, y)
    c.clipRect(skia.Rect.MakeLTRB(x0 - 20, y - size * 1.4, x0 + w * k + 4, y + size * 0.6))
    draw_text(c, s, x0, y, f, paint(color), "left")
    c.restore()


def hero(c, s, cx, baseline, size, lt, start=0.05, name=SERIF, color=INK, stagger=0.04):
    """Serif headline: letters drop in with a slight settle."""
    f = font(name, size)
    widths = [f.measureText(ch) for ch in s]
    x = cx - sum(widths) / 2
    for j, ch in enumerate(s):
        k = prog(lt, start + j * stagger, 0.28)
        if k > 0:
            e = ease_out_back(k, 2.2)
            c.save()
            c.translate(x + widths[j] / 2, baseline + (1 - e) * 40)
            c.rotate((1 - e) * (6 if j % 2 else -6))
            draw_text(c, ch, 0, 0, f, paint(color, min(1, k * 2.5)))
            c.restore()
        x += widths[j]
    return cx - sum(widths) / 2, cx + sum(widths) / 2


def header(c, i, lt):
    f = font(MONO, 30)
    p = paint(INK, 0.6)
    draw_text(c, f"FIELD NOTES · No.{i + 1:02d}", 90, 215, f, p, "left", 3)
    draw_text(c, HANDLE, W - 90, 215, f, p, "right", 3)
    c.drawLine(90, 240, W - 90, 240, paint(INK, 0.35, stroke=2))


def kicker(c, s, lt, y=455):
    f = font(MONO, 38)
    k = prog(lt, 0.0, 0.3)
    n = int(len(s) * k)
    draw_text(c, s[:n], W / 2, y, f, paint(INK, 0.75), "center", 6)


def grid(c):
    p = paint(GRID, 0.22, stroke=1.5)
    for x in range(0, W + 1, 60):
        c.drawLine(x, 0, x, H, p)
    for y in range(30, H + 1, 60):
        c.drawLine(0, y, W, y, p)


# ---------- beats ----------

def beat_year(c, b, lt, t):
    x0, x1 = hero(c, "1607", W / 2, 760, 330, lt)
    c.drawPath(loop_path(W / 2, 650, 330, 185, salt=1),
               trimmed(wobbly(paint(RED, 0.9, stroke=10), t, 2.0, 18), 0, prog(lt, 0.5, 0.4)))
    # pencil timeline 1600-1610 with the year marked
    y = 1080
    k = prog(lt, 0.25, 0.45)
    c.drawPath(path_from([(140, y), (940, y)]), trimmed(wobbly(ink(4), t), 0, k))
    f = font(MONO, 30)
    for j, yr in enumerate(range(1600, 1611)):
        x = 140 + j * 80
        if k * 800 >= x - 140:
            big = yr in (1600, 1605, 1610)
            c.drawLine(x, y - (24 if big else 12), x, y + (24 if big else 12), paint(INK, 0.9, stroke=3))
            if big:
                draw_text(c, str(yr), x, y + 70, f, paint(INK, 0.6))
    km = prog(lt, 0.75, 0.25)
    if km > 0:
        x = 140 + 7 * 80
        c.drawPath(path_from([(x, y - 150), (x, y - 38)]), trimmed(paint(RED, stroke=6), 0, km))
        c.drawPath(path_from([(x - 18, y - 60), (x, y - 36), (x + 18, y - 60)]),
                   trimmed(paint(RED, stroke=6), 0, prog(lt, 0.9, 0.12)))
        hand_text(c, "here.", x + 30, y - 120, 50, prog(lt, 0.95, 0.3), rot=-4)


def beat_ships(c, b, lt, t):
    hero(c, b["hero"], W / 2, 720, 230, lt)
    specs = [(205, 1235, 250), (545, 1195, 330), (870, 1255, 215)]
    for j, (x, y, w) in enumerate(specs):
        k = prog(lt, 0.15 + j * 0.2, 0.5)
        draw_ship(c, x, y, w, k, t, salt=j * 3)
        hand_text(c, b["names"][j], x, y + 175, 36, prog(lt, 0.45 + j * 0.2, 0.3), INK, "center", rot=-2)
    waves(c, 60, 1020, 1300, t, prog(lt, 0.1, 0.7), 4)
    waves(c, 120, 980, 1345, t, prog(lt, 0.2, 0.7), 5, 0.35)


TALLY_DRAW = 1.15


def tally_paths():
    paths = []
    gx0, gy0, gw, gh, gap_x, gap_y = 100, 950, 140, 125, 42, 50
    for m in range(104):
        g, s = divmod(m, 5)
        row, col = divmod(g, 5)
        x = gx0 + col * (gw + gap_x)
        y = gy0 + row * (gh + gap_y)
        if s < 4:
            xs = x + 14 + s * 28 + (hash01(m, 1) - 0.5) * 6
            paths.append(path_from([(xs + 4, y), (xs - 4, y + gh)]))
        else:
            paths.append(path_from([(x - 6, y + gh * 0.82), (x + gw - 6, y + gh * 0.18)]))
    return paths


TALLIES = tally_paths()


def beat_count(c, b, lt, t):
    k_all = prog(lt, 0.15, TALLY_DRAW)
    drawn = k_all * len(TALLIES)
    count = min(104, int(drawn))
    f = font(SERIF, 250)
    fi = font(SERIF_I, 150)
    num = str(count)
    nw = text_width("104", f)
    ww = text_width(" men", fi)
    x = W / 2 - (nw + ww) / 2
    draw_text(c, num, x + nw, 720, f, paint(INK), "right")
    if lt > 0.05:
        draw_text(c, " men", x + nw, 720, fi, paint(INK, prog(lt, 0.05, 0.3)), "left")
    line = wobbly(ink(5), t, 1.0, 10)
    for m, p in enumerate(TALLIES):
        k = clamp(drawn - m)
        if k > 0:
            c.drawPath(p, trimmed(line, 0, k))
    ku = prog(lt, 0.15 + TALLY_DRAW + 0.05, 0.25)
    if ku > 0:
        c.drawPath(underline_path(x - 10, x + nw + 10, 760, 1), trimmed(wobbly(paint(RED, stroke=9), t), 0, ku))


def route_path():
    p = skia.Path()
    p.moveTo(880, 1000)
    p.cubicTo(660, 820, 330, 1000, 200, 1400)
    return p


ROUTE = route_path()
ROUTE_MEASURE = skia.PathMeasure(ROUTE, False)


def beat_route(c, b, lt, t):
    hero(c, "4", 250, 760, 330, lt)
    hero(c, "months", 640, 740, 170, lt, 0.12, SERIF_I)
    k = prog(lt, 0.3, 0.9)
    dash = skia.Paint(paint(INK, 0.9, stroke=5))
    dash.setPathEffect(skia.DashPathEffect.Make([22, 18], 0))
    c.drawPath(ROUTE, trimmed(dash, 0, k))
    for (x, y, label, side, delay) in [(880, 1000, "London", 1, 0.1), (200, 1400, "Virginia", -1, 1.05)]:
        kx = prog(lt, delay, 0.2)
        if kx > 0:
            r = 22
            c.drawPath(path_from([(x - r, y - r), (x + r, y + r)]), trimmed(paint(RED, stroke=8), 0, kx * 2))
            c.drawPath(path_from([(x + r, y - r), (x - r, y + r)]), trimmed(paint(RED, stroke=8), 0, kx * 2 - 1))
            hand_text(c, label, x - 40 if side > 0 else x + 50, y + 80 if side > 0 else y + 25, 50,
                      prog(lt, delay + 0.1, 0.3), INK, "left", rot=-3)
    if 0 < k:
        pos, tan = ROUTE_MEASURE.getPosTan(ROUTE_MEASURE.getLength() * k)
        draw_ship(c, pos.x(), pos.y() - 24, 140, 1.0, t, 9)
    for j, (x, y) in enumerate([(400, 1200), (660, 1320), (480, 1470), (820, 1220), (760, 1450)]):
        waves(c, x, x + 140, y, t, prog(lt, 0.2 + j * 0.1, 0.4), 10 + j, 0.35)


def beat_gold(c, b, lt, t):
    hero(c, "find", W / 2, 640, 190, lt, 0.0, SERIF_I)
    # highlighter swipe behind GOLD (multiply, so ink stays black)
    kh = ease_out_cubic(prog(lt, 0.4, 0.3))
    if kh > 0:
        x0, x1 = 140, 140 + (W - 280) * kh
        hp = paint(HILITE, 0.85)
        hp.setBlendMode(skia.BlendMode.kMultiply)
        r = skia.Path()
        r.moveTo(x0, 790)
        r.lineTo(x1, 780)
        r.lineTo(x1 + 10, 935)
        r.lineTo(x0 + 6, 945)
        r.close()
        c.drawPath(r, hp)
    hero(c, "GOLD.", W / 2, 925, 300, lt, 0.12)
    for j, y in enumerate((965, 990)):
        c.drawPath(underline_path(190, 890, y, j + 2),
                   trimmed(wobbly(paint(RED, stroke=8), t, 1.5, 16, j), 0, prog(lt, 0.75 + j * 0.12, 0.2)))
    ka = prog(lt, 1.0, 0.25)
    if ka > 0:
        a = skia.Path()
        a.moveTo(330, 1250)
        a.quadTo(300, 1120, 420, 1035)
        c.drawPath(a, trimmed(paint(RED, stroke=6), 0, ka))
        c.drawPath(path_from([(395, 1030), (425, 1033), (420, 1062)]), trimmed(paint(RED, stroke=6), 0, prog(lt, 1.2, 0.08)))
    hand_text(c, "spoiler: they didn't.", 200, 1330, 58, prog(lt, 1.25, 0.5), rot=-4)


BEAT_FN = dict(year=beat_year, ships=beat_ships, count=beat_count, route=beat_route, gold=beat_gold)


def draw_sheet(c, i, lt, t):
    b = timeline.beats[i]
    c.save()
    c.rotate((hash01(i, 3) - 0.5) * 1.2, W / 2, H / 2)
    c.drawImageRect(PAPER_IMG, skia.Rect.MakeLTRB(-80, -80, W + 80, H + 80))
    grid(c)
    header(c, i, lt)
    kicker(c, b["kicker"], lt)
    s = 1 + 0.02 * ease_in_out(clamp(lt / 1.8))
    c.save()
    c.scale(s, s)
    c.translate(-(s - 1) * W / 2 / s, -(s - 1) * H / 2 / s)
    BEAT_FN[b["kind"]](c, b, lt, t)
    c.restore()
    c.restore()


def render(c, t):
    i, b, lt, dur = timeline.at(t)
    if i > 0 and lt < SLIDE:
        prev = timeline.beats[i - 1]
        draw_sheet(c, i - 1, b["start"] - prev["start"], t)
        k = ease_out_cubic(lt / SLIDE)
        c.save()
        c.translate(lerp(160, 0, k), lerp(H * 1.02, 0, k))
        c.rotate(lerp(-7, 0, k), W / 2, 0)
        shadow = skia.Paint(Color=rgb("#000000", 0.35), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
        c.drawRect(skia.Rect.MakeLTRB(-60, -20, W + 60, H + 200), shadow)
        draw_sheet(c, i, lt, t)
        c.restore()
    else:
        draw_sheet(c, i, lt, t)


def audio(path):
    m = sfx.Mix(END)
    for i, b in enumerate(timeline.beats):
        s = b["start"]
        if i > 0:
            m.add(sfx.paper_slide(0.38, seed=i), s - 0.04, 0.9, verb=0.1)
        m.add(sfx.thud(0.35, 70 + i * 4, seed=i), s + 0.12, 0.65, verb=0.25)
        m.add(sfx.typing(len(b["kicker"]) // 3, 0.03, seed=i), s + 0.02, 0.18, pan=-0.2)
    m.add(sfx.marker(0.4), 0.5, 0.55)
    m.add(sfx.pencil(0.45, 21), 0.25, 0.4, pan=0.2)
    m.add(sfx.marker(0.3, 22), 0.78, 0.4)
    m.add(sfx.marker(0.3, 23), 1.0, 0.35, pan=0.3)
    s = timeline.beats[1]["start"]
    for j, pan in enumerate((-0.5, 0.0, 0.5)):
        m.add(sfx.pencil(0.5, 30 + j, 18 + j * 4), s + 0.15 + j * 0.2, 0.42, pan=pan)
    s = timeline.beats[2]["start"]
    m.add(sfx.pencil(TALLY_DRAW, 40, 44), s + 0.15, 0.55)
    for g in range(21):
        m.add(sfx.tick(41 + g, 2500, 0.02), s + 0.15 + (g * 5 + 4) / 104 * TALLY_DRAW, 0.25, pan=(g % 5 - 2) / 3)
    m.add(sfx.marker(0.3, 42), s + 0.15 + TALLY_DRAW + 0.05, 0.5)
    s = timeline.beats[3]["start"]
    m.add(sfx.pencil(0.9, 50, 12), s + 0.3, 0.45, pan=0.3)
    m.add(sfx.marker(0.2, 51), s + 0.1, 0.4, pan=0.4)
    m.add(sfx.marker(0.2, 52), s + 1.05, 0.4, pan=-0.4)
    s = timeline.beats[4]["start"]
    m.add(sfx.marker(0.32, 60), s + 0.4, 0.6)
    m.add(sfx.marker(0.22, 61), s + 0.75, 0.45)
    m.add(sfx.marker(0.22, 62), s + 0.87, 0.45)
    m.add(sfx.pencil(0.5, 63, 26), s + 1.25, 0.4, pan=-0.2)
    return m.write(path, room=0.9)
