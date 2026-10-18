"""'Let's take Harry Kane as an example. All I need to do is find four people between me
and him, with each one getting closer and closer to him. Easy.'

Kane is locked on as the target, then a ladder of four unknown people climbs from me to
him and the cap hops up it hand to hand while a handshake counter falls to zero.
Faces come from assets/private/ (kept out of git). The voice is not included.
"""
import math
import os

import skia

import sfx
from engine import (W, H, ROOT, paint, prog, lerp, clamp, spring, ease_in_out, ease_out_cubic, stepped,
                    font, draw_text, path_from, trimmed)
from house import (BONE, RED, INK, OCHRE, DISPLAY, LABEL, MONO, offset_text, word_line, line_size,
                   label_build, sticker, to_image, draw_image_centered, run_scenes, grain, glitch, shake,
                   pop_scale, silhouette, tag_label)

DURATION = 11.7  # recording is 10.73s; the extra second lets the punchline land

# word start times (s) in the recording
LETS, TAKE, HARRY, KANE, EXAMPLE = 1.02, 1.26, 1.46, 1.70, 2.42
ALL, I, NEED, TO, DO, IS, FIND = 3.40, 3.52, 3.68, 3.80, 3.94, 4.16, 4.38
FOUR, PEOPLE, BETWEEN, ME, AND, HIM = 4.80, 5.08, 5.48, 6.10, 6.42, 6.60
WITH, CLOSER, AND2, CLOSER2, HIM2, EASY = 7.47, 8.40, 8.84, 9.20, 9.98, 10.30
LEAD = 0.03

STILL_TIMES = [1.6, 1.9, 2.7, 3.6, 4.5, 5.2, 6.8, 8.1, 8.6, 9.4, 10.1, 11.2]

PRIVATE = os.path.join(ROOT, "assets", "private")
BORDER, SHADOW = 18, (16, 14)
PAD = BORDER + max(SHADOW) + 4
KANE_RGBA = sticker(os.path.join(PRIVATE, "kane_bust.png"), BORDER, SHADOW)
ME_RGBA = sticker(os.path.join(PRIVATE, "me_bust.png"), BORDER, SHADOW)
KANE_IMG, KANE_SMALL = to_image(KANE_RGBA), to_image(KANE_RGBA, 420)
ME_SMALL = to_image(ME_RGBA, 420)
CAP_MINI = to_image(sticker(os.path.join(ROOT, "assets", "cap_stone.png")), 200)

# Kane's face inside his sticker, as fractions of the sticker image
_kw, _kh = KANE_IMG.width(), KANE_IMG.height()
FACE = ((PAD + 0.5 * (_kw - 2 * PAD)) / _kw, (PAD + 0.37 * (_kh - 2 * PAD)) / _kh)
FACE_HALF = (0.2, 0.3)


# ---------- the chain ----------

NODES = [(235, 1400), (630, 1290), (300, 1180), (705, 1065), (345, 950), (790, 840)]  # me, 1-4, Kane
CAP_DY = [-150, -95, -95, -95, -95, -155]  # how high the cap sits on each head
NODE_W = 240
SIL_W = 170
HOP_ARRIVE = [None, 7.95, CLOSER + 0.02, 8.88, CLOSER2 + 0.05, HIM2]
HOP_LEAVE = [WITH + 0.15, 8.10, 8.55, 9.00, 9.60]
KANE_FLY = (ALL - 0.12, ALL + 0.35)


def chain_path():
    p = skia.Path()
    p.moveTo(*NODES[0])
    for a, b in zip(NODES, NODES[1:]):
        p.lineTo(*b)
    return p


CHAIN = chain_path()
CHAIN_LEN = skia.PathMeasure(CHAIN, False).getLength()
SEG_LENS = [math.dist(a, b) for a, b in zip(NODES, NODES[1:])]


def chain_pos(d):
    pos, _ = skia.PathMeasure(CHAIN, False).getPosTan(d)
    return pos.x(), pos.y()


def cap_distance(t):
    """How far along the chain the cap is (in px), hopping node to node."""
    done = 0.0
    for j in range(5):
        leave, arrive = HOP_LEAVE[j], HOP_ARRIVE[j + 1]
        if t < leave:
            return done, j
        if t < arrive:
            return done + SEG_LENS[j] * ease_in_out((t - leave) / (arrive - leave)), j
        done += SEG_LENS[j]
    return done, 5


def camera(t):
    """Push in toward Kane as the cap climbs."""
    return lerp(1.0, 1.15, ease_in_out(prog(t, WITH, HIM2 - WITH)))


def apply_camera(c, t):
    z = camera(t)
    kx, ky = NODES[5]
    c.translate(kx, ky)
    c.scale(z, z)
    c.translate(-kx, -ky)


def node_tag(c, x, y, txt, t, appear, bg=OCHRE, fg=INK):
    sc = spring(prog(t, appear, 0.3), 2.2, 6)
    if sc <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    c.drawCircle(0, 0, 26, paint(bg))
    draw_text(c, txt, 0, 11, font(LABEL, 30), paint(fg), "center")
    c.restore()


# ---------- scene 1: the target ----------

KANE_A = (W / 2, 1140, 680)  # x, y, width


def brackets(c, t):
    k = prog(t, HARRY - LEAD + 0.05, KANE - HARRY)
    if k <= 0:
        return
    x, y, w = KANE_A
    h = w * _kh / _kw
    fx, fy = x - w / 2 + FACE[0] * w, y - h / 2 + FACE[1] * h
    e = ease_out_cubic(k)
    hw, hh = lerp(480, FACE_HALF[0] * w, e), lerp(560, FACE_HALF[1] * h, e)
    locked = k >= 1
    col = RED if locked else BONE
    p = paint(col, stroke=10, cap="square")
    ln = 54
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        cx, cy = fx + sx * hw, fy + sy * hh
        c.drawPath(path_from([(cx, cy - sy * ln), (cx, cy), (cx - sx * ln, cy)]), p)
    if locked and t < KANE + 0.25 and int(t * 15) % 2 == 0:
        c.drawRect(skia.Rect.MakeLTRB(fx - hw, fy - hh, fx + hw, fy + hh), paint(RED, 0.25))


def stamp(c, t):
    k = prog(t, EXAMPLE - LEAD, 0.3)
    if k <= 0:
        return
    sc = lerp(2.3, 1.0, spring(k, 1.6, 9))
    c.save()
    c.translate(W / 2 + 20, 1330)
    c.rotate(-12)
    c.scale(sc, sc)
    f = font(LABEL, 96)
    w = f.measureText("EXAMPLE") + 6 * 6
    c.drawRect(skia.Rect.MakeLTRB(-w / 2 - 40, -94, w / 2 + 40, 40), paint(RED, stroke=14, cap="butt"))
    draw_text(c, "EXAMPLE", 0, 0, f, paint(RED), "center", 6)
    c.restore()


def scene_target(c, t):
    c.drawPaint(paint(INK))
    label_build(c, [("LET'S", LETS - LEAD), ("TAKE", TAKE - LEAD)], W / 2, 330, t, BONE, INK, 44)
    c.save()
    shake(c, t, KANE - LEAD, 18, 1)
    size = line_size("HARRY KANE", W - 120, 220)
    word_line(c, [("HARRY", HARRY - LEAD), ("KANE", KANE - LEAD)], W / 2, 590, size, t, BONE, RED, 10, 9)
    c.restore()
    if t >= HARRY - LEAD and t < KANE_FLY[0]:
        x, y, w = KANE_A
        c.save()
        shake(c, t, HARRY - LEAD, 22, 2)
        draw_image_centered(c, KANE_IMG, x, y, w * pop_scale(t, HARRY - LEAD, 0.4, 1.5))
        c.restore()
    brackets(c, t)
    stamp(c, t)


def kane_flying(c, t):
    """Kane leaves the target scene and settles at the top of the ladder."""
    if not (KANE_FLY[0] <= t < KANE_FLY[1]):
        return
    e = ease_in_out(prog(t, KANE_FLY[0], KANE_FLY[1] - KANE_FLY[0]))
    x0, y0, w0 = KANE_A
    x1, y1 = NODES[5]
    draw_image_centered(c, KANE_IMG, lerp(x0, x1, e), lerp(y0, y1, e), lerp(w0, NODE_W, e), lerp(0, 4, e))


# ---------- scene 2: the ladder ----------

def scene_chain(c, t):
    c.drawPaint(paint(BONE))
    c.save()
    apply_camera(c, t)
    # dotted route, then the travelled part in solid red
    kd = prog(t, BETWEEN - LEAD, HIM + 0.15 - BETWEEN)
    if kd > 0:
        dots = paint(INK, stroke=9, cap="round")
        dash = skia.DashPathEffect.Make([0.1, 26], 0)
        dots.setPathEffect(skia.PathEffect.MakeCompose(dash, skia.TrimPathEffect.Make(0, kd)) if kd < 1 else dash)
        c.drawPath(CHAIN, dots)
    d, seg = cap_distance(t)
    if t >= WITH and d > 0:
        c.drawPath(CHAIN, trimmed(paint(RED, stroke=9), 0, d / CHAIN_LEN))
    # four unknowns pop in on "four"
    for j in range(1, 5):
        x, y = NODES[j]
        visited = HOP_ARRIVE[j] is not None and t >= HOP_ARRIVE[j]
        silhouette(c, x, y, SIL_W, OCHRE if visited else INK, INK if visited else RED, t, FOUR - LEAD + (j - 1) * 0.08)
        node_tag(c, x + (SIL_W * 0.55 if x < W / 2 else -SIL_W * 0.55), y - 70, str(j), t,
                 FOUR - LEAD + (j - 1) * 0.08 + 0.1, RED if visited else OCHRE, BONE if visited else INK)
    # me at the bottom, Kane at the top
    mx, my = NODES[0]
    if t >= I - LEAD:
        draw_image_centered(c, ME_SMALL, mx, my, NODE_W * pop_scale(t, I - LEAD, 0.4, 1.6), -3)
    tag_label(c, "ME", mx, my + 105, t, ME - LEAD, RED, BONE)
    kx, ky = NODES[5]
    if t >= KANE_FLY[1]:
        pulse = 1 + 0.12 * math.exp(-max(t - HIM2, 0) * 6) * (t >= HIM2)
        draw_image_centered(c, KANE_SMALL, kx, ky, NODE_W * pulse, 4)
        if t >= HIM2:
            ring = prog(t, HIM2, 0.6)
            c.drawCircle(kx, ky, 130 + 220 * ease_out_cubic(ring), paint(OCHRE, 0.9 * (1 - ring), stroke=12))
    tag_label(c, "HIM", kx, ky + 105, t, HIM - LEAD, INK, BONE)
    # the cap hops up the chain
    if t >= WITH - LEAD:
        cx, cy = chain_pos(d)
        hop, dy = 0, CAP_DY[seg]
        if seg < 5 and t >= HOP_LEAVE[seg]:
            u = clamp((t - HOP_LEAVE[seg]) / (HOP_ARRIVE[seg + 1] - HOP_LEAVE[seg]))
            hop = 70 * math.sin(math.pi * u)
            dy = lerp(CAP_DY[seg], CAP_DY[seg + 1], ease_in_out(u))
        sc = pop_scale(t, WITH - LEAD, 0.35, 1.8)
        draw_image_centered(c, CAP_MINI, cx, cy + dy - hop, 130 * sc, -8 + 6 * math.sin(t * 7))
    c.restore()
    # headline (screen space)
    if t < WITH - 0.05:
        label_build(c, [(w, at - LEAD) for w, at in
                        (("ALL", ALL), ("I", I), ("NEED", NEED), ("TO", TO), ("DO", DO), ("IS", IS))],
                    W / 2, 300, t, INK, BONE, 40)
        size = line_size("FIND 4 PEOPLE", W - 120, 210)
        word_line(c, [("FIND", FIND - LEAD), ("4", FOUR - LEAD, RED), ("PEOPLE", PEOPLE - LEAD)],
                  W / 2, 520, size, t, INK, RED, 10, 9)
        word_line(c, [("BETWEEN", BETWEEN - LEAD), ("ME", ME - LEAD), ("&", AND - LEAD), ("HIM", HIM - LEAD)],
                  W / 2, 650, 110, t, INK, OCHRE, 7, 6)
    else:
        c.save()
        shake(c, t, CLOSER - LEAD, 16, 3)
        word_line(c, [("CLOSER", CLOSER - LEAD)], W / 2, 420, 150, t, INK, RED, 9, 8)
        c.restore()
        c.save()
        shake(c, t, CLOSER2 - LEAD, 26, 4)
        word_line(c, [("AND", AND2 - LEAD), ("CLOSER", CLOSER2 - LEAD, RED)], W / 2, 610, 190, t, INK, INK, 10, 9)
        c.restore()
        handshakes(c, t, seg)


def handshakes(c, t, seg):
    n = 5 - seg if t >= WITH else 5
    txt = str(n)
    x, y = 250, 760  # under the headline, left of Kane and clear of the TikTok side buttons
    k = pop_scale(t, HOP_ARRIVE[seg], 0.3, 1.5) if seg >= 1 else 1.0
    c.save()
    c.translate(x - 35, y - 40)
    c.scale(k, k)
    draw_text(c, txt, 35, 40, font(MONO, 120), paint(RED if n else OCHRE), "right")
    c.restore()
    fl = font(LABEL, 32)
    draw_text(c, "HANDSHAKES", x + 20, y - 46, fl, paint(INK), "left", 3)
    draw_text(c, "AWAY", x + 20, y - 6, fl, paint(INK), "left", 3)


# ---------- scene 3: easy ----------

def scene_easy(c, t):
    c.drawPaint(paint(OCHRE))
    c.save()
    shake(c, t, EASY - LEAD, 28, 5)
    size = line_size("EASY.", W - 140, 520)
    sc = pop_scale(t, EASY - LEAD, 0.45, 2.0)
    c.translate(W / 2, 900)
    c.scale(sc, sc)
    offset_text(c, "EASY.", 0, size * 0.36, size, INK, RED, 14, 12)
    c.restore()
    k = prog(t, EASY + 0.55, 0.25)
    if k > 0:
        draw_text(c, "*theoretically", W / 2 + 180, 1210, font(LABEL, 46), paint(INK, k), "center", 2)


SCENES = [(0.0, scene_target, INK), (ALL - 0.12, scene_chain, BONE), (EASY - 0.1, scene_easy, OCHRE)]


def render(c, t):
    t = stepped(t, 15)
    run_scenes(c, t, SCENES)
    kane_flying(c, t)
    grain(c)


def post(buf, t, fi):
    for at, length, strength in ((KANE - 0.02, 0.08, 0.6), (EASY - 0.05, 0.1, 0.9)):
        if at <= t < at + length:
            return glitch(buf, fi, strength)
    return buf


# ---------- sound (no voice) ----------

def audio(path):
    m = sfx.Mix(DURATION)
    for j, at in enumerate((LETS, TAKE)):
        m.add(sfx.typing(2, 0.03, 1 + j), at - LEAD, 0.4, pan=-0.2)
    m.add(sfx.slam(3), HARRY - LEAD - 0.18, 0.85, verb=0.2)
    m.add(sfx.data_chatter(KANE - HARRY, 4, 30), HARRY, 0.25, pan=0.3)
    m.add(sfx.alarm(1568, 2), KANE - LEAD, 0.35)
    m.add(sfx.glitch(0.08, 5), KANE - 0.02, 0.3)
    m.add(sfx.impact(0.7, 120, 45, 6, 2.2), KANE - LEAD, 0.55, verb=0.25)
    m.add(sfx.stamp(7), EXAMPLE - LEAD, 0.95, verb=0.2)

    m.add(sfx.whoosh(0.22, 600, 5000, 8, 0.8), ALL - 0.3, 0.5, pan=0.3)
    m.add(sfx.whoosh(0.5, 3000, 600, 9, 0.4), KANE_FLY[0], 0.4, pan=0.4)
    for j, at in enumerate((ALL, I, NEED, TO, DO, IS)):
        m.add(sfx.tick(10 + j, 3500), at - LEAD, 0.35, pan=-0.3 + 0.1 * j)
    m.add(sfx.pop(523, 0.14), I - LEAD, 0.45, pan=-0.5)
    m.add(sfx.impact(0.6, 140, 50, 16, 2.5), FIND - LEAD, 0.6, verb=0.25)
    for j in range(4):
        m.add(sfx.pop(440 * 1.26 ** j, 0.12), FOUR - LEAD + j * 0.08, 0.45, pan=0.4 if j % 2 == 0 else -0.4)
    m.add(sfx.tick(17, 3000), PEOPLE - LEAD, 0.35)
    m.add(sfx.riser(HIM + 0.15 - BETWEEN, 18), BETWEEN, 0.18)
    m.add(sfx.pop(392, 0.14), ME - LEAD, 0.45, pan=-0.5)
    m.add(sfx.pop(784, 0.14), HIM - LEAD, 0.45, pan=0.5)
    m.add(sfx.thud(0.3, 85, 19), HIM - LEAD, 0.4)

    m.add(sfx.pop(880, 0.16), WITH - LEAD, 0.5, pan=-0.5)
    for j in range(5):
        m.add(sfx.whoosh(0.2, 800, 4000, 20 + j, 0.7), HOP_LEAVE[j], 0.25, pan=-0.4 + 0.2 * j)
        m.add(sfx.pop(523 * 1.19 ** j, 0.14), HOP_ARRIVE[j + 1], 0.5, pan=0.4 if j % 2 == 0 else -0.4, verb=0.2)
        m.add(sfx.blip(1760, 0.05), HOP_ARRIVE[j + 1] + 0.04, 0.25)
    m.add(sfx.impact(0.6, 140, 50, 26, 2.5), CLOSER - LEAD, 0.55, verb=0.2)
    m.add(sfx.slam(27), CLOSER2 - LEAD - 0.18, 0.8, verb=0.2)
    m.add(sfx.impact(1.0, 160, 36, 28, 3.0), HIM2 - LEAD, 0.8, verb=0.3)
    m.add(sfx.shimmer(1318.5, 1.0), HIM2, 0.35, verb=0.5)

    m.add(sfx.slam(29), EASY - LEAD - 0.18, 0.95, verb=0.2)
    m.add(sfx.glitch(0.1, 30), EASY - 0.05, 0.4)
    m.add(sfx.sub_drop(0.9, 80, 30), EASY - LEAD, 0.6)
    m.add(sfx.typing(4, 0.04, 31), EASY + 0.55, 0.3)
    return m.write(path, room=1.0, loudness=-18.0)
