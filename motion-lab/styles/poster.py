"""POSTER — a printed propaganda / Isotype poster that won't sit still.

Every beat is a new flat colour block that wipes in on a diagonal. Huge condensed type
with a misregistered print offset, Isotype pictograms (one figure = one man), halftone
dots, paper grain, and everything animated 'on twos' (15fps) like cut paper.
Sounds: slams, short whooshes, pitched pops, a rubber stamp.
"""
import math

import numpy as np
import skia
from scipy import ndimage

import sfx
from engine import (W, H, rgb, paint, prog, lerp, clamp, ease_out_cubic, ease_in_out, spring,
                    stepped, font, draw_text, text_width, fit_size, path_from, hash01)
from script import timeline, HANDLE, END

BONE = "#F2EBDC"
RED = "#E3301F"
INK = "#151413"
BLUE = "#1F3CB5"
OCHRE = "#F2AD1B"

DISPLAY, LABEL = "Anton-Regular", "ArchivoBlack-Regular"
BG = dict(year=RED, ships=BONE, count=INK, route=BLUE, gold=OCHRE)
FG = dict(year=BONE, ships=INK, count=BONE, route=BONE, gold=INK)
OFFSET = dict(year=INK, ships=RED, count=RED, route=INK, gold=RED)
WIPE = 0.3


def _grain():
    rng = np.random.default_rng(3)
    n = ndimage.gaussian_filter(rng.standard_normal((H, W)), 0.7)
    fib = ndimage.gaussian_filter(rng.standard_normal((H, W)), (0.5, 6))
    a = np.clip(0.5 + 0.18 * n / n.std() + 0.1 * fib / fib.std(), 0, 1)
    img = np.dstack([np.full((H, W), v, np.uint8) for v in (40, 34, 30)] + [(a * 60).astype(np.uint8)])
    return skia.Image.fromarray(np.ascontiguousarray(img))


GRAIN = _grain()


# ---------- print devices ----------

def offset_text(c, s, x, y, size, fg, off, dx=9, dy=7, name=DISPLAY, tracking=0):
    f = font(name, size)
    draw_text(c, s, x + dx, y + dy, f, paint(off), "center", tracking)
    draw_text(c, s, x, y, f, paint(fg), "center", tracking)


def label(c, s, x, y, bg, fg, rot=-2.5, size=34):
    f = font(LABEL, size)
    w = text_width(s, f, 2)
    c.save()
    c.rotate(rot, x, y)
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2 - 22, y - size - 10, x + w / 2 + 22, y + 16), paint(bg))
    draw_text(c, s, x, y, f, paint(fg), "center", 2)
    c.restore()


def halftone_disc(c, cx, cy, r, color, cell=22, light=(-0.6, -0.7)):
    c.save()
    clip = skia.Path()
    clip.addCircle(cx, cy, r)
    c.clipPath(clip, skia.ClipOp.kIntersect, True)
    p = paint(color)
    for y in np.arange(cy - r, cy + r + cell, cell):
        row = int((y - cy) / cell)
        for x in np.arange(cx - r + (cell / 2 if row % 2 else 0), cx + r + cell, cell):
            u, v = (x - cx) / r, (y - cy) / r
            shade = clamp(0.62 - 0.45 * (u * light[0] + v * light[1]))
            c.drawCircle(x, y, cell * 0.62 * shade, p)
    c.restore()


def shake(c, lt, at, amt=18, salt=0):
    k = lt - at
    if 0 <= k < 0.3:
        d = amt * (1 - k / 0.3) ** 2
        c.translate((hash01(int(k * 15), salt, 1) - 0.5) * 2 * d, (hash01(int(k * 15), salt, 2) - 0.5) * 2 * d)


def slam_scale(lt, at, from_scale=1.9):
    k = prog(lt, at, 0.45)
    return lerp(from_scale, 1.0, spring(k, 2.2, 7)), k > 0


def hero_slam(c, b, s, y, size, lt, at=0.05, salt=0):
    kind = b["kind"]
    size = fit_size(s, DISPLAY, W - 150, size)
    sc, on = slam_scale(lt, at)
    if not on:
        return
    c.save()
    c.translate(W / 2, y - size * 0.35)
    c.scale(sc, sc)
    c.translate(-W / 2, -(y - size * 0.35))
    offset_text(c, s, W / 2, y, size, FG[kind], OFFSET[kind])
    c.restore()


def figure_path(cx, cy, s):
    """Isotype person: round head, tapered body, legs."""
    p = skia.Path()
    p.addCircle(cx, cy - s * 0.62, s * 0.17)
    body = skia.Path()
    body.moveTo(cx - s * 0.26, cy - s * 0.38)
    body.lineTo(cx + s * 0.26, cy - s * 0.38)
    body.lineTo(cx + s * 0.2, cy + s * 0.12)
    body.lineTo(cx + s * 0.13, cy + s * 0.12)
    body.lineTo(cx + s * 0.13, cy + s * 0.5)
    body.lineTo(cx + s * 0.02, cy + s * 0.5)
    body.lineTo(cx + s * 0.02, cy + s * 0.14)
    body.lineTo(cx - s * 0.02, cy + s * 0.14)
    body.lineTo(cx - s * 0.02, cy + s * 0.5)
    body.lineTo(cx - s * 0.13, cy + s * 0.5)
    body.lineTo(cx - s * 0.13, cy + s * 0.12)
    body.lineTo(cx - s * 0.2, cy + s * 0.12)
    body.close()
    p.addPath(body)
    return p


def ship_shapes(w):
    hull = skia.Path()
    hull.moveTo(-0.55 * w, -0.08 * w)
    hull.lineTo(0.52 * w, -0.16 * w)
    hull.lineTo(0.38 * w, 0.14 * w)
    hull.lineTo(-0.36 * w, 0.14 * w)
    hull.close()
    sails, masts = skia.Path(), skia.Path()
    for x, h, sw in [(-0.25, 0.6, 0.15), (0.04, 0.8, 0.2), (0.3, 0.52, 0.13)]:
        base = -0.1 * w - x * 0.08 * w
        masts.addRect(skia.Rect.MakeLTRB(x * w - 5, base - h * w - 10, x * w + 5, base))
        for top, hgt in [(0.92, 0.36), (0.5, 0.34)]:
            t0 = base - h * w * top
            sails.addRect(skia.Rect.MakeLTRB((x - sw) * w, t0, (x + sw) * w, t0 + h * w * hgt))
    flag = path_from([(0.04 * w + 5, -0.1 * w - 0.003 * w - 0.8 * w - 10), (0.04 * w + 70, -0.1 * w - 0.8 * w + 8),
                      (0.04 * w + 5, -0.1 * w - 0.8 * w + 26)], True)
    return hull, masts, sails, flag


def draw_ship(c, x, y, w, sc, t, salt):
    hull, masts, sails, flag = ship_shapes(w)
    c.save()
    c.translate(x, y + 8 * math.sin(t * 3 + salt))
    c.rotate(2.5 * math.sin(t * 2.4 + salt))
    c.scale(sc, sc)
    c.drawPath(masts, paint(INK))
    c.drawPath(sails, paint(BONE))
    c.drawPath(sails, paint(INK, stroke=6, cap="butt"))
    c.drawPath(flag, paint(RED))
    c.drawPath(hull, paint(INK))
    c.restore()


def sea(c, y, t, color, amp=16, wl=180):
    p = skia.Path()
    p.moveTo(0, H)
    for x in range(0, W + 21, 20):
        p.lineTo(x, y + amp * math.sin(x / wl * 2 * math.pi + t * 3))
    p.lineTo(W, H)
    p.close()
    c.drawPath(p, paint(color))


# ---------- beats ----------

def beat_year(c, b, lt, t):
    f = font(DISPLAY, 560)
    scroll = (t * 140) % 600
    outline = paint(BONE, 0.35, stroke=4)
    for k in range(-2, 4):
        draw_text(c, "1607", W / 2, 760 - 600 * k + scroll - 300, f, outline)
    c.drawRect(skia.Rect.MakeLTRB(0, 180, W, 1540), paint(RED, 0.0))
    hero_slam(c, b, "1607", 1010, 560, lt, 0.05)
    label(c, b["kicker"], W / 2, 470, INK, BONE, -3)
    halftone_disc(c, 860, 1330, 160, INK, 20)


SHIP_SLOTS = [(250, 1225, 260), (560, 1185, 330), (860, 1245, 230)]


def beat_ships(c, b, lt, t):
    halftone_disc(c, 760, 900, 260, RED, 24)
    c.drawCircle(760, 900, 150, paint(RED))
    hero_slam(c, b, "3 SHIPS", 760, 330, lt, 0.05)
    label(c, b["kicker"], W / 2, 400, INK, BONE, -2)
    sea(c, 1250, t, BLUE)
    for j, (x, y, w) in enumerate(SHIP_SLOTS):
        k = prog(lt, 0.25 + j * 0.16, 0.5)
        if k > 0:
            sc = spring(k, 2.4, 6)
            draw_ship(c, x, y + (1 - min(1, k * 3)) * 300, w, sc, t, j)
            f = font(LABEL, 30)
            c.drawCircle(x, y + 175, 30, paint(BONE))
            draw_text(c, f"0{j + 1}", x, y + 186, f, paint(INK), "center")
    sea(c, 1300, t + 0.7, "#18309A", 12, 140)


FIG_ROWS, FIG_COLS = 8, 13
FIG_POP = 0.95


def beat_count(c, b, lt, t):
    k_all = prog(lt, 0.2, FIG_POP)
    shown = int(k_all * 104)
    c.save()
    shake(c, lt, 0.2 + FIG_POP, 14, 3)
    num = str(max(shown, 0)) if shown < 104 else "104"
    hero_slam(c, b, f"{num} MEN", 720, 300, lt, 0.05)
    c.restore()
    label(c, b["kicker"], W / 2, 380, RED, BONE, 2)
    cell_w, cell_h = 76, 82
    x0 = (W - FIG_COLS * cell_w) / 2 + cell_w / 2
    for m in range(104):
        r, col = divmod(m, FIG_COLS)
        appear = 0.2 + (m / 104) * FIG_POP
        k = prog(lt, appear, 0.25)
        if k <= 0:
            continue
        sc = spring(k, 2.0, 6)
        x, y = x0 + col * cell_w, 880 + r * cell_h
        c.save()
        c.translate(x, y)
        c.scale(sc, sc)
        c.drawPath(figure_path(0, 0, 72), paint(RED if m == 0 else BONE))
        c.restore()
    if lt > 0.2 + FIG_POP + 0.1:
        draw_text(c, "EACH FIGURE = 1 MAN", W / 2, 1530, font(LABEL, 30), paint(BONE, 0.7), "center", 3)


def arrow_path(x0, y0, x1, y1, w, head):
    ang = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0)
    p = path_from([(0, -w / 2), (L - head, -w / 2), (L - head, -w * 1.25), (L, 0),
                   (L - head, w * 1.25), (L - head, w / 2), (0, w / 2)], True)
    m = skia.Matrix()
    m.setRotate(math.degrees(ang))
    m.postTranslate(x0, y0)
    p.transform(m)
    return p


def beat_route(c, b, lt, t):
    fw = paint(BONE, 0.22, stroke=5)
    for row in range(10):
        y = 900 + row * 70
        for col in range(9):
            x = 60 + col * 120 + (60 if row % 2 else 0) + (t * 30) % 120
            p = skia.Path()
            p.moveTo(x, y)
            p.quadTo(x + 18, y - 14, x + 36, y)
            p.quadTo(x + 54, y + 14, x + 72, y)
            c.drawPath(p, fw)
    hero_slam(c, b, "4 MONTHS", 700, 290, lt, 0.05)
    label(c, b["kicker"], W / 2, 380, INK, BONE, -2)
    sx, sy, ex, ey = 900, 980, 170, 1420
    k = ease_out_cubic(prog(lt, 0.3, 0.55))
    if k > 0:
        x1, y1 = lerp(sx, ex, k), lerp(sy, ey, k)
        c.drawPath(arrow_path(sx + 10, sy + 12, x1 + 10, y1 + 12, 60, 110), paint(INK))
        c.drawPath(arrow_path(sx, sy, x1, y1, 60, 110), paint(OCHRE))
    for j in range(4):
        kk = prog(lt, 0.55 + j * 0.16, 0.3)
        if kk > 0:
            u = (j + 1) / 4.6
            x, y = lerp(sx, ex, u), lerp(sy, ey, u)
            r = 38 * spring(kk, 2.2, 6)
            c.drawCircle(x, y, r, paint(INK))
            draw_text(c, ["I", "II", "III", "IV"][j], x, y + 13, font(LABEL, 34) if r > 30 else font(LABEL, 20), paint(BONE), "center")
    label(c, "LONDON", sx - 20, sy - 70, BONE, INK, 3, 30)
    if lt > 0.85:
        label(c, "VIRGINIA", ex + 120, ey + 95, BONE, INK, -3, 30)


def beat_gold(c, b, lt, t):
    rays = 18
    rot = t * 12
    p = paint("#E39A0E")
    cx, cy = W / 2, 860
    for r in range(rays):
        a0 = math.radians(rot + r * 360 / rays)
        a1 = a0 + math.radians(360 / rays / 2)
        c.drawPath(path_from([(cx, cy), (cx + 2400 * math.cos(a0), cy + 2400 * math.sin(a0)),
                              (cx + 2400 * math.cos(a1), cy + 2400 * math.sin(a1))], True), p)
    label(c, b["kicker"], W / 2, 400, INK, OCHRE, 2)
    hero_slam(c, b, "FIND", 640, 220, lt, 0.0)
    c.save()
    shake(c, lt, 0.45, 26, 7)
    sc, on = slam_scale(lt, 0.25, 2.4)
    if on:
        c.translate(W / 2, 830)
        c.scale(sc, sc)
        c.translate(-W / 2, -830)
        offset_text(c, "GOLD.", W / 2, 1010, 440, RED, INK, 12, 10)
    c.restore()
    ks = prog(lt, 1.1, 0.3)
    if ks > 0:
        sc = lerp(2.2, 1.0, spring(ks, 1.6, 9))
        c.save()
        c.translate(W / 2, 1300)
        c.rotate(-11)
        c.scale(sc, sc)
        f = font(LABEL, 72)
        w = text_width("NOT FOUND", f, 6)
        box = skia.Rect.MakeLTRB(-w / 2 - 34, -64, w / 2 + 34, 34)
        c.drawRect(box, paint(INK, stroke=12, cap="butt"))
        draw_text(c, "NOT FOUND", 0, 0, f, paint(INK), "center", 6)
        c.restore()


BEAT_FN = dict(year=beat_year, ships=beat_ships, count=beat_count, route=beat_route, gold=beat_gold)


def draw_scene(c, i, lt, t):
    b = timeline.beats[i]
    c.drawPaint(paint(BG[b["kind"]]))
    BEAT_FN[b["kind"]](c, b, lt, t)
    f = font(LABEL, 26)
    draw_text(c, HANDLE, W - 80, 230, f, paint(FG[b["kind"]], 0.7), "right", 3)
    draw_text(c, f"{i + 1:02d}/{len(timeline.beats):02d}", 80, 230, f, paint(FG[b["kind"]], 0.7), "left", 3)


def half_plane(e, d=(0.53, -0.85), L=6000):
    nx, ny = -d[1], d[0]
    px, py = d[0] * e, d[1] * e + H
    return path_from([(px + nx * L, py + ny * L), (px - nx * L, py - ny * L),
                      (px - nx * L - d[0] * L, py - ny * L - d[1] * L),
                      (px + nx * L - d[0] * L, py + ny * L - d[1] * L)], True)


def render(c, t):
    t = stepped(t, 15)
    i, b, lt, dur = timeline.at(t)
    if i > 0 and lt < WIPE:
        prev = timeline.beats[i - 1]
        draw_scene(c, i - 1, b["start"] - prev["start"] - 0.01, t)
        span = W * 0.53 + H * 0.85 + 200
        e = lerp(-100, span, ease_in_out(lt / WIPE))
        c.save()
        c.clipPath(half_plane(e + 60), skia.ClipOp.kIntersect, True)
        c.drawPaint(paint(INK if BG[b["kind"]] != INK else RED))
        c.restore()
        c.save()
        c.clipPath(half_plane(e), skia.ClipOp.kIntersect, True)
        draw_scene(c, i, lt, t)
        c.restore()
    else:
        draw_scene(c, i, lt, t)
    gp = skia.Paint()
    gp.setBlendMode(skia.BlendMode.kMultiply)
    c.drawImage(GRAIN, 0, 0, skia.SamplingOptions(), gp)


def audio(path):
    m = sfx.Mix(END)
    for i, b in enumerate(timeline.beats):
        s = b["start"]
        if i > 0:
            m.add(sfx.whoosh(0.3, 600, 6000, i, 0.8), s - 0.12, 0.55, pan=-0.3 + 0.15 * i)
        m.add(sfx.slam(seed=i), s, 0.75, verb=0.2)
    s = timeline.beats[1]["start"]
    for j in range(3):
        m.add(sfx.thud(0.3, 90 + j * 12, 30 + j), s + 0.33 + j * 0.16, 0.6, pan=(j - 1) * 0.5)
        m.add(sfx.whoosh(0.25, 300, 1800, 33 + j, 0.5), s + 0.2 + j * 0.16, 0.25)
    s = timeline.beats[2]["start"]
    pops = sfx.scale_pops(16, 392)
    for k, p in enumerate(pops):
        m.add(p, s + 0.2 + k / 16 * FIG_POP, 0.35, pan=((k % 13) - 6) / 8, verb=0.15)
    m.add(sfx.impact(0.7, 160, 50, 40, 3.0), s + 0.2 + FIG_POP, 0.7, verb=0.25)
    s = timeline.beats[3]["start"]
    m.add(sfx.whoosh(0.6, 250, 2500, 41, 0.4), s + 0.28, 0.6, pan=0.5)
    for j in range(4):
        m.add(sfx.pop(523 * 1.12 ** j, 0.14), s + 0.55 + j * 0.16, 0.5, pan=0.3 - j * 0.2)
    s = timeline.beats[4]["start"]
    m.add(sfx.impact(1.0, 170, 38, 50, 3.5), s + 0.3, 0.9, verb=0.3)
    m.add(sfx.shimmer(1318.5, 1.6), s + 0.32, 0.45, verb=0.5)
    m.add(sfx.stamp(51), s + 1.15, 0.85, verb=0.2)
    return m.write(path, room=1.0)
