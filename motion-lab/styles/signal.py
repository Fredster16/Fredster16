"""SIGNAL — a classified-file terminal.

Pure black, one acid lime, monospace type that decodes from noise, HUD brackets that
never leave the frame, scanlines and a glitch on every cut. Sounds: digital blips,
data chatter, glitch zaps, sub-bass locks.
"""
import math
import random

import numpy as np
import skia

import sfx
from engine import (W, H, FPS, rgb, paint, prog, lerp, clamp, ease_out_cubic, ease_out_expo,
                    ease_out_back, font, draw_text, text_width, trimmed, path_from, hash01)
from script import timeline, HANDLE, END

BG = "#040605"
LIME = "#C6FF3D"
WHITE = "#ECEFE8"
DIM = "#1C241E"
AMBER = "#FFB21A"
RED = "#FF3B30"

BOLD, MED = "JetBrainsMono-ExtraBold", "JetBrainsMono-Medium"
GLYPHS = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#%&@$/<>"
GLITCH_FRAMES = 4


def accent(i):
    return AMBER if timeline.beats[i]["kind"] == "gold" else LIME


# ---------- HUD ----------

def corners(c, x0, y0, x1, y1, ln, p):
    for (x, y, dx, dy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        c.drawPath(path_from([(x, y + dy * ln), (x, y), (x + dx * ln, y)]), p)


def hud(c, t, i):
    col = accent(i)
    corners(c, 60, 170, W - 60, 1545, 60, paint(col, 0.9, stroke=4, cap="square"))
    f = font(MED, 28)
    if int(t * 2) % 2 == 0:
        c.drawCircle(92, 220, 9, paint(RED))
    draw_text(c, "REC", 112, 230, f, paint(WHITE, 0.85), "left", 2)
    draw_text(c, f"FILE_{1607:04d}.{i + 1:02d}", 200, 230, f, paint(col, 0.75), "left", 2)
    draw_text(c, HANDLE, W - 90, 230, f, paint(WHITE, 0.6), "right", 2)
    fr = int(t * FPS)
    tc = f"{fr // (FPS * 3600):02d}:{fr // (FPS * 60) % 60:02d}:{fr // FPS % 60:02d}:{fr % FPS:02d}"
    draw_text(c, tc, 90, 1510, f, paint(WHITE, 0.55), "left", 2)
    bars = 4 + int(hash01(int(t * 6)) * 3)
    for k in range(6):
        c.drawRect(skia.Rect.MakeXYWH(W - 230 + k * 22, 1510 - 8 - k * 5, 14, 8 + k * 5),
                   paint(col if k < bars else DIM))


def dot_grid(c, t, i):
    p = paint(accent(i), 0.10)
    for y in range(190, 1545, 40):
        for x in range(80, W - 60, 40):
            c.drawRect(skia.Rect.MakeXYWH(x, y, 3, 3), p)
    # slow scan band
    y = (t / 2.6 % 1) * 1500 + 150
    sh = skia.GradientShader.MakeLinear([skia.Point(0, y - 120), skia.Point(0, y)],
                                        [rgb(accent(i), 0.0), rgb(accent(i), 0.07)])
    c.drawRect(skia.Rect.MakeLTRB(0, y - 120, W, y), skia.Paint(Shader=sh))


# ---------- type ----------

def decode(c, s, cx, baseline, size, lt, start=0.08, per=0.045, color=WHITE, col_dim=LIME, salt=0):
    """Characters scramble through random glyphs, then lock left to right."""
    f = font(BOLD, size)
    cw = f.measureText("M")
    x0 = cx - cw * len(s) / 2
    locked_all = True
    for j, ch in enumerate(s):
        lock_t = start + 0.12 + j * per
        x = x0 + j * cw
        if ch == " ":
            continue
        if lt < start:
            locked_all = False
            continue
        if lt < lock_t:
            locked_all = False
            g = GLYPHS[int(hash01(j, int(lt * 40), salt) * len(GLYPHS))]
            draw_text(c, g, x + cw / 2, baseline, f, paint(col_dim, 0.6))
        else:
            k = prog(lt, lock_t, 0.12)
            draw_text(c, ch, x + cw / 2, baseline, f, paint(color))
            if k < 1:
                c.drawRect(skia.Rect.MakeXYWH(x, baseline - size * 0.78, cw, size * 0.86),
                           paint(col_dim, 0.85 * (1 - k)))
    if locked_all and int(lt * 3.5) % 2 == 0:
        c.drawRect(skia.Rect.MakeXYWH(x0 + cw * len(s) + 10, baseline - size * 0.72, cw * 0.55, size * 0.76),
                   paint(col_dim))
    return x0, x0 + cw * len(s)


def kicker(c, s, lt, i, y=420):
    f = font(MED, 36)
    n = int(len(s) * prog(lt, 0.0, 0.25))
    txt = f"[{i + 1:02d}] > " + s[:n]
    draw_text(c, txt, 100, y, f, paint(accent(i)), "left", 3)
    if n < len(s) or int(lt * 4) % 2:
        w = text_width(txt, f, 3)
        c.drawRect(skia.Rect.MakeXYWH(104 + w, y - 30, 20, 36), paint(accent(i)))


def punch(c, lt, at=0.4, amt=0.06):
    """Hard zoom-punch when something locks in."""
    k = prog(lt, at, 0.22)
    if 0 < k < 1:
        s = 1 + amt * (1 - ease_out_cubic(k))
        c.translate(W / 2, 800)
        c.scale(s, s)
        c.translate(-W / 2, -800)


# ---------- beats ----------

def beat_year(c, b, lt, t, i):
    c.save()
    punch(c, lt, 0.33)
    decode(c, b["hero"], W / 2, 720, 280, lt, salt=1)
    c.restore()
    # time ruler rewinding from today to 1607
    k = ease_out_expo(prog(lt, 0.05, 1.0))
    year = lerp(2026, 1607, k)
    y = 1080
    spacing = 16
    f = font(MED, 30)
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(90, y - 140, W - 90, y + 120))
    first = int(year - W / 2 / spacing) - 1
    for yr in range(first, first + W // spacing + 3):
        x = W / 2 + (yr - year) * spacing
        big = yr % 10 == 0
        c.drawLine(x, y, x, y + (60 if big else 26 if yr % 5 == 0 else 14),
                   paint(WHITE if big else LIME, 0.9 if big else 0.45, stroke=3 if big else 2))
        if big:
            draw_text(c, str(yr), x, y + 100, f, paint(WHITE, 0.7))
    c.restore()
    c.drawLine(90, y, W - 90, y, paint(LIME, 0.5, stroke=2))
    c.drawPath(path_from([(W / 2 - 18, y - 40), (W / 2 + 18, y - 40), (W / 2, y - 12)], True), paint(LIME))
    c.drawLine(W / 2, y - 12, W / 2, y + 80, paint(LIME, stroke=4))
    readout = f"T-{2026 - int(round(year)):03d} YRS"
    draw_text(c, readout, W / 2, y - 70, font(MED, 34), paint(LIME), "center", 4)


def wire_ship(w):
    hull = path_from([(-0.5 * w, -0.05 * w), (0.5 * w, -0.12 * w), (0.36 * w, 0.12 * w), (-0.34 * w, 0.12 * w)], True)
    rig = skia.Path()
    for x, h in [(-0.22, 0.55), (0.04, 0.78), (0.28, 0.5)]:
        base = -0.08 * w - x * 0.07 * w
        rig.moveTo(x * w, base)
        rig.lineTo(x * w, base - h * w)
        rig.moveTo(x * w - 0.13 * w, base - h * w * 0.85)
        rig.lineTo(x * w + 0.13 * w, base - h * w * 0.85)
        rig.lineTo(x * w + 0.1 * w, base - h * w * 0.25)
        rig.lineTo(x * w - 0.1 * w, base - h * w * 0.25)
        rig.close()
    rig.moveTo(0.5 * w, -0.12 * w)
    rig.lineTo(0.28 * w, -0.08 * w - 0.5 * w)
    return hull, rig


def beat_ships(c, b, lt, t, i):
    c.save()
    punch(c, lt, 0.45)
    decode(c, b["hero"], W / 2, 690, 190, lt, salt=2)
    c.restore()
    slots = [(230, 1250, 200), (545, 1080, 260), (850, 1280, 200)]
    fs = font(MED, 24)
    for j, (x, y, w) in enumerate(slots):
        k = prog(lt, 0.15 + j * 0.22, 0.35)
        if k <= 0:
            continue
        hull, rig = wire_ship(w)
        c.save()
        c.translate(x, y)
        line = paint(LIME, 0.95, stroke=3)
        c.drawPath(hull, trimmed(line, 0, k * 1.6))
        c.drawPath(rig, trimmed(paint(LIME, 0.7, stroke=2), 0, k * 1.4 - 0.3))
        c.restore()
        # target box closing in, then locked
        lk = ease_out_cubic(k)
        pad = lerp(120, 26, lk)
        bx0, by0, bx1, by1 = x - w * 0.55 - pad, y - w * 0.85 - pad, x + w * 0.55 + pad, y + w * 0.18 + pad
        locked = k >= 1
        corners(c, bx0, by0, bx1, by1, 22, paint(WHITE if locked else LIME, stroke=3, cap="square"))
        if locked:
            draw_text(c, f"VSL-{j + 1:02d}", bx0, by1 + 34, fs, paint(LIME), "left", 2)
            draw_text(c, b["names"][j].upper(), bx0, by1 + 64, fs, paint(WHITE, 0.8), "left", 1)
            if int(lt * 6) % 2 == 0 or lt > 0.15 + j * 0.22 + 0.7:
                draw_text(c, "LOCKED", bx1, by0 - 12, fs, paint(BG), "right", 2)
                w_l = text_width("LOCKED", fs, 2)
                c.drawRect(skia.Rect.MakeLTRB(bx1 - w_l - 8, by0 - 38, bx1 + 4, by0 - 4), paint(LIME))
                draw_text(c, "LOCKED", bx1 - 2, by0 - 12, fs, paint(BG), "right", 2)


GRID_ORDER = sorted(range(104), key=lambda m: hash01(m, 77))
GRID_FILL = 0.95


def beat_count(c, b, lt, t, i):
    kf = prog(lt, 0.1, GRID_FILL)
    lit = int(kf * 104)
    c.save()
    punch(c, lt, 0.1 + GRID_FILL, 0.05)
    f = font(BOLD, 230)
    cw = f.measureText("M")
    num = f"{lit:03d}" if lit < 104 else "104"
    x0 = W / 2 - cw * 3.8 / 2
    for j, ch in enumerate(num):
        draw_text(c, ch, x0 + cw * (j + 0.5), 690, f, paint(WHITE if lit >= 104 or j < 2 else LIME))
    draw_text(c, "MEN", x0 + cw * 3.15, 690, font(BOLD, 110), paint(LIME, prog(lt, 0.05, 0.2)), "left")
    c.restore()
    size, gap, cols = 56, 14, 13
    gx = (W - cols * (size + gap) + gap) / 2
    order_rank = {m: r for r, m in enumerate(GRID_ORDER)}
    for m in range(104):
        r, col = divmod(m, cols)
        x, y = gx + col * (size + gap), 870 + r * (size + gap)
        rank = order_rank[m]
        rect = skia.Rect.MakeXYWH(x, y, size, size)
        if rank < lit:
            age = kf * 104 - rank
            c.drawRect(rect, paint(WHITE if age < 3 else LIME, 1.0 if age < 3 else 0.85))
        else:
            c.drawRect(rect, paint(LIME, 0.35, stroke=2))
    if lit >= 104:
        draw_text(c, "MANIFEST COMPLETE · 104/104", W / 2, 1474, font(MED, 30), paint(LIME), "center", 3)


# route via the Canaries and the West Indies, as the 1606-07 fleet actually sailed
ROUTE_PTS = [("LONDON", 51.5, -0.1), ("CANARY IS.", 28.3, -16.5), ("W. INDIES", 15.4, -61.4), ("VIRGINIA", 37.2, -76.8)]


def geo(lat, lon):
    return lerp(150, 940, (lon + 82) / 88), lerp(1450, 930, (lat - 10) / 46)


def route_path():
    pts = [geo(la, lo) for _, la, lo in ROUTE_PTS]
    p = skia.Path()
    p.moveTo(*pts[0])
    for a, bpt in zip(pts, pts[1:]):
        mx, my = (a[0] + bpt[0]) / 2, (a[1] + bpt[1]) / 2 + 40
        p.quadTo(mx, my, *bpt)
    return p, pts


ROUTE, ROUTE_NODES = route_path()
ROUTE_LEN = skia.PathMeasure(ROUTE, False).getLength()


def beat_route(c, b, lt, t, i):
    c.save()
    punch(c, lt, 0.35)
    decode(c, b["hero"], W / 2, 690, 175, lt, salt=4)
    c.restore()
    fl = font(MED, 22)
    for lat in range(10, 60, 10):
        x0, y = geo(lat, -82)
        c.drawLine(140, y, 950, y, paint(LIME, 0.12, stroke=1))
        draw_text(c, f"{lat}°N", 142, y - 8, fl, paint(LIME, 0.4), "left")
    for lon in range(-80, 10, 20):
        x, _ = geo(10, lon)
        c.drawLine(x, 920, x, 1460, paint(LIME, 0.12, stroke=1))
    k = prog(lt, 0.25, 1.0)
    dash = paint(LIME, 0.9, stroke=4, cap="butt")
    dash.setPathEffect(skia.DashPathEffect.Make([16, 10], -lt * 60))
    c.drawPath(ROUTE, trimmed(dash, 0, k))
    meas = skia.PathMeasure(ROUTE, False)
    if 0 < k < 1:
        for tr in range(8):
            d = max(0, ROUTE_LEN * k - tr * 9)
            pos, _ = meas.getPosTan(d)
            c.drawCircle(pos.x(), pos.y(), 12 - tr * 1.2, paint(WHITE, 1 - tr / 8))
    fs = font(MED, 26)
    for j, ((name, la, lo), (x, y)) in enumerate(zip(ROUTE_PTS, ROUTE_NODES)):
        reach = [0, 0.33, 0.66, 1.0][j]
        if k >= reach:
            age = lt - (0.25 + reach * 1.0)
            ring = (age * 1.4) % 1
            c.drawCircle(x, y, 10, paint(WHITE if j in (0, 3) else LIME))
            c.drawCircle(x, y, 10 + 40 * ring, paint(LIME, 0.8 * (1 - ring), stroke=2))
            right = x < W / 2
            draw_text(c, name, x + (24 if right else -24), y - 18, fs, paint(WHITE, 0.9), "left" if right else "right", 2)
            draw_text(c, f"{la:.1f}N {abs(lo):.1f}W", x + (24 if right else -24), y + 14, font(MED, 20),
                      paint(LIME, 0.6), "left" if right else "right", 1)
    months = min(4, int(k * 4 + 0.001))
    draw_text(c, f"T+ {months} MO", W - 100, 920, font(MED, 30), paint(LIME), "right", 3)


def beat_gold(c, b, lt, t, i):
    # sonar ping rings
    for r in range(3):
        k = ((lt - 0.4 - r * 0.35) / 1.4)
        if 0 < k < 1:
            c.drawCircle(W / 2, 1180, 40 + 520 * k, paint(AMBER, 0.6 * (1 - k), stroke=3))
    c.save()
    punch(c, lt, 0.5, 0.09)
    decode(c, "FIND", W / 2, 640, 200, lt, color=WHITE, col_dim=AMBER, salt=5)
    glow = paint(AMBER, 0.55)
    glow.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
    if lt > 0.5:
        f = font(BOLD, 250)
        draw_text(c, "GOLD", W / 2, 880, f, glow)
    decode(c, "GOLD", W / 2, 880, 250, lt, 0.2, color=AMBER, col_dim=AMBER, salt=6)
    c.restore()
    if lt > 0.75:
        blink = int(lt * 5) % 2 == 0 or lt > 1.4
        fs = font(BOLD, 40)
        box = skia.Rect.MakeLTRB(150, 1010, W - 150, 1090)
        c.drawRect(box, paint(AMBER, stroke=4))
        if blink:
            c.drawRect(box.makeInset(10, 10), paint(AMBER))
            draw_text(c, "PRIMARY OBJECTIVE", W / 2, 1066, fs, paint(BG), "center", 4)
        else:
            draw_text(c, "PRIMARY OBJECTIVE", W / 2, 1066, fs, paint(AMBER), "center", 4)
    if lt > 1.2:
        s = "STATUS: UNCONFIRMED"
        n = int(len(s) * prog(lt, 1.2, 0.35))
        draw_text(c, s[:n], W / 2, 1400, font(MED, 34), paint(RED), "center", 4)


BEAT_FN = dict(year=beat_year, ships=beat_ships, count=beat_count, route=beat_route, gold=beat_gold)


def render(c, t):
    i, b, lt, dur = timeline.at(t)
    c.clear(rgb(BG))
    dot_grid(c, t, i)
    kicker(c, b["kicker"], lt, i)
    BEAT_FN[b["kind"]](c, b, lt, t, i)
    hud(c, t, i)


# ---------- post: scanlines, grain, chromatic split, glitch on cuts ----------

_yy, _xx = np.mgrid[0:H, 0:W]
_VIGNETTE = (1 - 0.45 * np.clip(np.sqrt(((_xx - W / 2) / (W * 0.62)) ** 2 + ((_yy - H / 2) / (H * 0.62)) ** 2) - 0.45, 0, 1)) \
    .astype(np.float32)
_SCAN = np.where(_yy % 4 < 2, 1.0, 0.82).astype(np.float32)
_SHADE = (_VIGNETTE * _SCAN)[..., None]
_GRAIN = [np.random.default_rng(s).normal(0, 7, (H // 2, W // 2)).astype(np.float32) for s in range(6)]


def post(buf, t, fi):
    img = buf[..., :3].astype(np.float32)
    # constant chromatic split, stronger right after a cut
    i, b, lt, dur = timeline.at(t)
    cut = i > 0 and lt < GLITCH_FRAMES / FPS
    shift = 9 if cut else 3
    img[..., 0] = np.roll(img[..., 0], shift, axis=1)
    img[..., 2] = np.roll(img[..., 2], -shift, axis=1)
    if cut:
        rng = random.Random(fi * 31)
        for _ in range(9):
            y0 = rng.randrange(0, H - 200)
            hgt = rng.randrange(20, 160)
            img[y0:y0 + hgt] = np.roll(img[y0:y0 + hgt], rng.randrange(-140, 140), axis=1)
        if lt < 1 / FPS:
            img = img * 0.4 + 255 * 0.6 * np.array([0.78, 1.0, 0.24], np.float32)
    g = np.repeat(np.repeat(_GRAIN[fi % len(_GRAIN)], 2, 0), 2, 1)
    img = img * _SHADE + g[..., None]
    out = np.empty((H, W, 4), np.uint8)
    out[..., :3] = np.clip(img, 0, 255)
    out[..., 3] = 255
    return out


# ---------- sound ----------

def audio(path):
    m = sfx.Mix(END)
    hum_t = np.arange(int(END * sfx.SR)) / sfx.SR
    hum = (np.sin(2 * np.pi * 55 * hum_t) + 0.3 * np.sin(2 * np.pi * 110 * hum_t)) * 0.05
    m.add(hum.astype(np.float32), 0, 0.5, verb=0)
    for i, b in enumerate(timeline.beats):
        s = b["start"]
        if i > 0:
            m.add(sfx.glitch(0.16, seed=i), s, 0.55, verb=0.05)
        m.add(sfx.typing(len(b["kicker"]) // 2, 0.018, seed=10 + i), s + 0.02, 0.3, pan=-0.3, verb=0.05)
        m.add(sfx.data_chatter(0.35, seed=20 + i, rate=34), s + 0.1, 0.35, pan=0.2, verb=0.1)
    s = timeline.beats[0]["start"]
    m.add(sfx.whoosh(0.9, 3000, 300, 70, 0.2), s + 0.05, 0.5)
    m.add(sfx.impact(0.8, 120, 38, 71, 2.0), s + 0.33, 0.8, verb=0.3)
    s = timeline.beats[1]["start"]
    m.add(sfx.impact(0.6, 110, 40, 72, 2.0), s + 0.45, 0.6, verb=0.3)
    for j, pan in enumerate((-0.5, 0, 0.5)):
        m.add(sfx.blip(1760, 0.05), s + 0.15 + j * 0.22, 0.4, pan=pan)
        m.add(sfx.blip(2637, 0.09), s + 0.5 + j * 0.22, 0.4, pan=pan)
    s = timeline.beats[2]["start"]
    m.add(sfx.data_chatter(GRID_FILL, 73, 60), s + 0.1, 0.5, verb=0.1)
    m.add(sfx.impact(0.8, 120, 38, 74, 2.2), s + 0.1 + GRID_FILL, 0.75, verb=0.3)
    m.add(sfx.blip(1318, 0.12), s + 0.1 + GRID_FILL, 0.4)
    s = timeline.beats[3]["start"]
    m.add(sfx.impact(0.6, 110, 40, 75, 2.0), s + 0.35, 0.55, verb=0.3)
    for j in range(4):
        m.add(sfx.blip(880 * (1.26 ** j), 0.08), s + 0.25 + j * 0.33, 0.4, pan=0.5 - j / 3)
    s = timeline.beats[4]["start"]
    m.add(sfx.sub_drop(1.2, 80, 26), s + 0.5, 0.9, verb=0.1)
    m.add(sfx.impact(1.0, 150, 36, 76, 3.0), s + 0.5, 0.7, verb=0.35)
    for r in range(3):
        m.add(sfx.blip(988, 0.25, 1), s + 0.4 + r * 0.35, 0.3, verb=0.6)
    m.add(sfx.alarm(1046, 2), s + 0.78, 0.35, verb=0.2)
    m.add(sfx.typing(10, 0.03, 77), s + 1.2, 0.3)
    return m.write(path, room=1.4)
