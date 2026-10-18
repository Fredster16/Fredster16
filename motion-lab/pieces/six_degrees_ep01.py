"""SIX DEGREES, episode 01: the series launch.

'Delusional self-belief, and apparently that's all you need. So this video officially
marks the start of the series. I'm going to try and prove six degrees of separation is
real by getting this cap from me all the way to [BLEEP] and come back on October the
19th when I reveal who the first target is.'

The bleep (13.78-14.62s in the recording) is covered by a CLASSIFIED redaction bar.
No tone is added over it; the voice and its bleep are not included in the render.
"""
import math
import os

import skia

import sfx
from engine import (W, H, ROOT, paint, prog, lerp, clamp, spring, ease_in_out, ease_out_cubic, stepped,
                    font, draw_text, text_width, path_from, trimmed)
from house import (BONE, RED, INK, BLUE, OCHRE, DISPLAY, LABEL, offset_text, word_line, line_size,
                   label_build, sticker, to_image, draw_image_centered, run_scenes, grain, glitch, shake,
                   pop_scale, silhouette, tag_label)

DURATION = 19.4  # speech ends at 18.2s; the recording's trailing silence is dropped

# word start times (s) in the recording
DELUSIONAL, SELF = 0.77, 1.22
AND, APPARENTLY, THATS, ALL, YOU, NEED = 2.72, 2.91, 3.08, 3.48, 3.66, 3.82
SO, THIS, VIDEO, OFFICIALLY, MARKS, THE, START, SERIES = 4.71, 4.76, 4.94, 5.24, 5.54, 5.94, 6.16, 6.62
IM, GOING, TO, TRY, AND2, PROVE = 7.92, 8.04, 8.16, 8.32, 8.50, 8.56
SIX, DEGREES, OF, SEPARATION, IS, REAL = 8.80, 9.10, 9.38, 9.60, 10.00, 10.32
BY, GETTING, THIS2, CAP, ME, ALL2, THE2, WAY, TO2 = 11.10, 11.18, 11.42, 11.68, 12.26, 12.54, 12.96, 13.14, 13.36
BLEEP, BLEEP_END = 13.78, 14.62
COME, BACK, ON, OCTOBER, NINETEENTH = 14.74, 14.90, 15.14, 15.34, 15.92
WHEN, I, REVEAL, WHO, FIRST, TARGET, IS2 = 16.46, 16.58, 16.74, 16.96, 17.38, 17.60, 17.94
LEAD = 0.03

STILL_TIMES = [1.0, 1.9, 3.3, 3.95, 5.6, 7.2, 9.0, 10.6, 11.9, 13.5, 14.2, 15.6, 16.3, 18.0, 19.2]

ME_IMG = to_image(sticker(os.path.join(ROOT, "assets", "private", "me_bust.png")), 420)
CAP_RGBA = sticker(os.path.join(ROOT, "assets", "cap_stone.png"))
CAP_IMG, CAP_MINI = to_image(CAP_RGBA), to_image(CAP_RGBA, 200)


# ---------- 1. delusional self-belief ----------

def wobbly_word(c, s, cx, baseline, size, t, at, fg, off):
    """A word that can't hold itself together: every letter drifts and tilts."""
    if t < at:
        return
    f = font(DISPLAY, size)
    widths = [f.measureText(ch) for ch in s]
    x = cx - sum(widths) / 2
    sc = pop_scale(t, at, 0.4, 1.7)
    c.save()
    c.translate(cx, baseline - size * 0.35)
    c.scale(sc, sc)
    c.translate(-cx, -(baseline - size * 0.35))
    for j, ch in enumerate(s):
        dy = 16 * math.sin(t * 8 + j * 1.3)
        rot = 5 * math.sin(t * 6.5 + j * 2.1)
        c.save()
        c.translate(x + widths[j] / 2, baseline + dy)
        c.rotate(rot)
        offset_text(c, ch, 0, 0, size, fg, off, 9, 8)
        c.restore()
        x += widths[j]
    c.restore()


def scene_delusional(c, t):
    c.drawPaint(paint(INK))
    wobbly_word(c, "DELUSIONAL", W / 2, 860, line_size("DELUSIONAL", W - 140, 280), t, DELUSIONAL - LEAD, BONE, RED)
    c.save()
    shake(c, t, SELF - LEAD, 22, 1)
    word_line(c, [("SELF-BELIEF", SELF - LEAD)], W / 2, 1110, line_size("SELF-BELIEF", W - 120, 260), t, RED, BONE)
    c.restore()


# ---------- 2. what you need ----------

CHECK_ITEMS = [("CONNECTIONS", 2.78, APPARENTLY + 0.08), ("MONEY", 2.86, THATS + 0.12), ("A PLAN", 2.94, ALL)]
ROWS = [640, 790, 940]
BOX = 84


def checkbox(c, x, y, fill=None):
    r = skia.Rect.MakeXYWH(x, y - BOX + 8, BOX, BOX)
    if fill:
        c.drawRect(r, paint(fill))
    c.drawRect(r, paint(INK, stroke=8, cap="square"))


def scene_checklist(c, t):
    c.drawPaint(paint(BONE))
    label_build(c, [("WHAT YOU NEED:", AND - LEAD)], W / 2, 430, t, INK, BONE, 48)
    f = font(DISPLAY, 110)
    for (item, appear, strike), y in zip(CHECK_ITEMS, ROWS):
        if t < appear:
            continue
        sc = pop_scale(t, appear, 0.3, 1.4)
        c.save()
        c.translate(140, y)
        c.scale(sc, sc)
        c.translate(-140, -y)
        checkbox(c, 130, y)
        draw_text(c, item, 260, y, f, paint(INK, 0.35 if t >= strike + 0.15 else 1.0), "left")
        k = prog(t, strike, 0.15)
        if k > 0:
            xe = 260 + f.measureText(item) + 14
            c.drawPath(path_from([(248, y - 40), (xe, y - 46)]), trimmed(paint(RED, stroke=14), 0, k))
            cross = paint(RED, stroke=12)
            c.drawPath(path_from([(146, y - BOX + 24), (130 + BOX - 16, y - 8)]), trimmed(cross, 0, k * 2))
            c.drawPath(path_from([(130 + BOX - 16, y - BOX + 24), (146, y - 8)]), trimmed(cross, 0, k * 2 - 1))
        c.restore()
    if t >= YOU - LEAD:
        c.save()
        shake(c, t, NEED - LEAD, 20, 2)
        ticked = t >= NEED - LEAD
        checkbox(c, 130, 1150, OCHRE if ticked else None)
        if ticked:
            tick = path_from([(146, 1110), (172, 1140), (130 + BOX + 22, 1050)])
            c.drawPath(tick, trimmed(paint(INK, stroke=16), 0, prog(t, NEED - LEAD, 0.12)))
        word_line(c, [("DELUSIONAL", YOU - LEAD)], 260 + 330, 1150, 130, t, RED, INK, 9, 8)
        word_line(c, [("SELF-BELIEF", YOU - LEAD + 0.06)], 260 + 330, 1290, 130, t, RED, INK, 9, 8)
        c.restore()


# ---------- 3. officially the start of the series ----------

def rubber_stamp(c, text, x, y, size, t, at, color, rot=-10):
    k = prog(t, at, 0.3)
    if k <= 0:
        return
    sc = lerp(2.3, 1.0, spring(k, 1.6, 9))
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(sc, sc)
    f = font(LABEL, size)
    w = text_width(text, f, size * 0.06)
    c.drawRect(skia.Rect.MakeLTRB(-w / 2 - 0.4 * size, -1.0 * size, w / 2 + 0.4 * size, 0.42 * size),
               paint(color, stroke=size * 0.14, cap="butt"))
    draw_text(c, text, 0, 0, f, paint(color), "center", size * 0.06)
    c.restore()


def scene_official(c, t):
    c.drawPaint(paint(RED))
    if t < SERIES - LEAD:
        label_build(c, [("SO", SO - LEAD), ("THIS", THIS - LEAD), ("VIDEO", VIDEO - LEAD)], W / 2, 400, t, INK, BONE, 46)
        c.save()
        shake(c, t, OFFICIALLY - LEAD, 20, 3)
        rubber_stamp(c, "OFFICIAL", W / 2, 800, 120, t, OFFICIALLY - LEAD, BONE)
        c.restore()
        word_line(c, [("MARKS", MARKS - LEAD), ("THE", THE - LEAD), ("START", START - LEAD)],
                  W / 2, 1150, 170, t, BONE, INK, 10, 9)
    else:
        c.save()
        shake(c, t, SERIES - LEAD, 30, 4)
        word_line(c, [("EPISODE", SERIES - LEAD)], W / 2, 560, 160, t, INK, BONE, 8, 7)
        sc = pop_scale(t, SERIES - LEAD, 0.45, 1.9)
        c.translate(W / 2, 1000)
        c.scale(sc, sc)
        offset_text(c, "01", 0, 360, 820, BONE, INK, 18, 16)
        c.restore()


# ---------- 4. the series logo ----------

LOGO = (W / 2, 800)
RING_R = 300


def series_logo(c, t, at_six, at_degrees, at_sep):
    cx, cy = LOGO
    nodes = []
    for k in range(6):
        a = math.radians(-90 + k * 60 + t * 8)
        nodes.append((cx + RING_R * math.cos(a), cy + RING_R * math.sin(a)))
    dots = paint(BONE, 0.7, stroke=7, cap="round")
    dots.setPathEffect(skia.DashPathEffect.Make([0.1, 20], 0))
    for k in range(5):
        kk = prog(t, at_six + 0.1 + k * 0.12, 0.15)
        if kk > 0:
            a, b = nodes[k], nodes[k + 1]
            c.drawPath(path_from([a, (lerp(a[0], b[0], kk), lerp(a[1], b[1], kk))]), dots)
    for k, (x, y) in enumerate(nodes):
        s = spring(prog(t, at_six + k * 0.12, 0.3), 2.2, 6)
        if s > 0:
            c.drawCircle(x, y, 30 * s, paint({0: RED, 5: OCHRE}.get(k, BONE)))
            c.drawCircle(x, y, 30 * s, paint(INK, stroke=6))
    if t >= at_six - LEAD:
        sc = pop_scale(t, at_six - LEAD, 0.45, 1.9)
        c.save()
        c.translate(cx, cy)
        c.scale(sc, sc)
        c.drawCircle(10, 10, 215, paint(BONE))
        c.drawCircle(0, 0, 215, paint(RED))
        offset_text(c, "6", 0, 120, 340, BONE, INK, 12, 10)
        c.restore()
    word_line(c, [("DEGREES", at_degrees - LEAD)], W / 2, 1290, 210, t, BONE, RED, 10, 9)
    word_line(c, [("OF", at_sep[0] - LEAD), ("SEPARATION", at_sep[1] - LEAD)], W / 2, 1400, 104, t, RED, INK)


def scene_logo(c, t):
    c.drawPaint(paint(INK))
    label_build(c, [(w, at - LEAD) for w, at in
                    (("I'M", IM), ("GOING", GOING), ("TO", TO), ("TRY", TRY), ("AND", AND2), ("PROVE", PROVE))],
                W / 2, 360, t, BONE, INK, 44)
    c.save()
    shake(c, t, SIX - LEAD, 24, 5)
    series_logo(c, t, SIX, DEGREES, (OF, SEPARATION))
    c.restore()
    c.save()
    shake(c, t, REAL - LEAD, 18, 6)
    word_line(c, [("IS", IS - LEAD), ("REAL", REAL - LEAD, OCHRE)], W / 2, 1515, 96, t, BONE, INK)
    c.restore()


# ---------- 5. from me all the way to [classified] ----------

NODES = [(235, 1400), (630, 1292), (300, 1184), (705, 1076), (345, 968), (790, 870)]  # me, 1-4, target
CAP_DY = [-150, -95, -95, -95, -95, -130]
CAP_IN = (CAP - LEAD, ME - LEAD)  # cap slams centre-stage, then drops onto my head
FLIGHT = (THE2 - 0.05, BLEEP - 0.06)  # cap climbs the whole chain
CAP_CENTRE = (W / 2, 1040, 560)


def chain():
    p = skia.Path()
    p.moveTo(*NODES[0])
    for n in NODES[1:]:
        p.lineTo(*n)
    return p


CHAIN = chain()
CHAIN_MEASURE = skia.PathMeasure(CHAIN, False)
CHAIN_LEN = CHAIN_MEASURE.getLength()
NODE_D = [0.0]
for a, b in zip(NODES, NODES[1:]):
    NODE_D.append(NODE_D[-1] + math.dist(a, b))


def cap_on_chain(t):
    """Distance along the chain, hop height and head offset while the cap climbs."""
    k = prog(t, FLIGHT[0], FLIGHT[1] - FLIGHT[0])
    seg_f = ease_in_out(k) * 5
    seg = min(int(seg_f), 4)
    u = seg_f - seg
    d = lerp(NODE_D[seg], NODE_D[seg + 1], u)
    return d, 60 * math.sin(math.pi * u) * (k < 1), lerp(CAP_DY[seg], CAP_DY[seg + 1], u)


def redaction(c, t):
    k = prog(t, BLEEP - LEAD, 0.25)
    if k <= 0:
        return
    sc = lerp(1.8, 1.0, spring(k, 1.8, 8))
    c.save()
    c.translate(W / 2, 600)
    c.rotate(-3)
    c.scale(sc, sc)
    c.drawRect(skia.Rect.MakeLTRB(-372, -62, 388, 86), paint(RED))
    c.drawRect(skia.Rect.MakeLTRB(-380, -70, 380, 78), paint(INK))
    on = t < BLEEP_END or int(t * 4) % 2 == 0
    draw_text(c, "CLASSIFIED", 0, 34, font(LABEL, 84), paint(RED if on else BONE), "center", 10)
    c.restore()


def scene_chain(c, t):
    c.drawPaint(paint(BONE))
    label_build(c, [(w, at - LEAD) for w, at in (("BY", BY), ("GETTING", GETTING), ("THIS", THIS2), ("CAP", CAP))],
                W / 2, 300, t, INK, BONE, 44)
    kd = prog(t, ALL2 - LEAD, 0.4)
    if kd > 0:
        dots = paint(INK, stroke=9, cap="round")
        dash = skia.DashPathEffect.Make([0.1, 26], 0)
        dots.setPathEffect(skia.PathEffect.MakeCompose(dash, skia.TrimPathEffect.Make(0, kd)) if kd < 1 else dash)
        c.drawPath(CHAIN, dots)
    d, hop, dy = cap_on_chain(t)
    if t >= FLIGHT[0]:
        c.drawPath(CHAIN, trimmed(paint(RED, stroke=9), 0, d / CHAIN_LEN))
    for j in range(1, 5):
        x, y = NODES[j]
        reached = t >= FLIGHT[0] and d >= NODE_D[j]
        silhouette(c, x, y, 170, OCHRE if reached else INK, INK if reached else RED, t, ALL2 - LEAD + 0.05 * j)
    tx, ty = NODES[5]
    silhouette(c, tx, ty, 230, RED, BONE, t, ALL2 - LEAD + 0.3, INK)
    tag_label(c, "TARGET 01", tx, ty + 112, t, ALL2 + 0.35, INK, BONE)
    mx, my = NODES[0]
    if t >= ME - LEAD:
        draw_image_centered(c, ME_IMG, mx, my, 240 * pop_scale(t, ME - LEAD, 0.4, 1.6), -3)
    tag_label(c, "ME", mx, my + 105, t, ME + 0.1, RED, BONE)
    # the cap: centre stage, onto my head, then up the chain
    if t >= CAP_IN[0]:
        x0, y0, w0 = CAP_CENTRE
        if t < CAP_IN[1]:
            draw_image_centered(c, CAP_IMG, x0, y0, w0 * pop_scale(t, CAP_IN[0], 0.4, 1.6), -6)
        else:
            k = ease_in_out(prog(t, CAP_IN[1], 0.25))
            if t < FLIGHT[0]:
                x, y, w = lerp(x0, mx, k), lerp(y0, my + CAP_DY[0], k), lerp(w0, 130, k)
            else:
                pos, _ = CHAIN_MEASURE.getPosTan(d)
                x, y, w = pos.x(), pos.y() + dy - hop, 130
            draw_image_centered(c, CAP_IMG if w > 200 else CAP_MINI, x, y, w, -8 + 5 * math.sin(t * 7))
    c.save()
    shake(c, t, BLEEP - LEAD, 26, 7)
    word_line(c, [("ALL", ALL2 - LEAD), ("THE", THE2 - LEAD), ("WAY", WAY - LEAD), ("TO", TO2 - LEAD)],
              W / 2, 480, 150, t, INK, RED, 9, 8)
    redaction(c, t)
    c.restore()


# ---------- 6. come back on October the 19th ----------

CAL = (W / 2, 1010, 640, 720)  # centre x, centre y, width, height


def calendar_page(c, num, w, h, color):
    c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2 + 170, w / 2, h / 2), paint(BONE))
    offset_text(c, num, 0, h / 2 - 110, 400, color, RED if color == INK else INK, 12, 10)


def scene_calendar(c, t):
    c.drawPaint(paint(BLUE))
    label_build(c, [("COME", COME - LEAD), ("BACK", BACK - LEAD), ("ON", ON - LEAD)], W / 2, 400, t, BONE, INK, 46)
    if t < OCTOBER - LEAD:
        return
    x, y, w, h = CAL
    c.save()
    shake(c, t, NINETEENTH - LEAD, 24, 8)
    c.translate(x, y)
    c.rotate(-3)
    s = pop_scale(t, OCTOBER - LEAD, 0.4, 1.6)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-w / 2 + 18, -h / 2 + 16, w / 2 + 18, h / 2 + 16), paint(INK))
    c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, -h / 2 + 170), paint(RED))
    draw_text(c, "OCT", 0, -h / 2 + 135, font(DISPLAY, 130), paint(BONE), "center", 8)
    for rx in (-w / 4, w / 4):
        c.drawRoundRect(skia.Rect.MakeLTRB(rx - 14, -h / 2 - 46, rx + 14, -h / 2 + 34), 14, 14, paint(INK))
    calendar_page(c, "19", w, h, INK)
    k = prog(t, NINETEENTH - LEAD, 0.55)
    if k < 1:
        c.save()
        e = ease_out_cubic(k)
        c.translate(lerp(0, 520, e), lerp(0, 900, e * e))
        c.rotate(lerp(0, 38, e))
        calendar_page(c, "18", w, h, INK)
        c.restore()
    c.restore()


# ---------- 7. who is the first target ----------

def scene_target(c, t):
    c.drawPaint(paint(RED))
    label_build(c, [("WHEN", WHEN - LEAD), ("I", I - LEAD), ("REVEAL", REVEAL - LEAD)], W / 2, 330, t, INK, BONE, 46)
    breathe = 1 + 0.015 * math.sin(t * 3)
    c.save()
    shake(c, t, WHO - LEAD, 18, 9)
    c.translate(W / 2, 930)
    c.scale(breathe, breathe)
    silhouette(c, 0, 0, 560, INK, INK if t >= WHO - LEAD else BONE, t, WHEN - 0.05, BONE)
    if t >= WHO - LEAD:
        q = pop_scale(t, WHO - LEAD, 0.35, 1.5)
        c.save()
        c.translate(0, -0.2 * 560)
        c.scale(q, q)
        draw_text(c, "?", 0, 0.15 * 560, font(DISPLAY, 0.42 * 560), paint(OCHRE), "center")
        c.restore()
    c.restore()
    c.save()
    shake(c, t, TARGET - LEAD, 24, 10)
    word_line(c, [("FIRST", FIRST - LEAD), ("TARGET", TARGET - LEAD)], W / 2, 1400, 170, t, BONE, INK, 10, 9)
    c.restore()
    tag_label(c, "REVEALED 19.10", W / 2, 1505, t, IS2 + 0.25, INK, BONE)


SCENES = [(0.0, scene_delusional, INK), (AND - 0.12, scene_checklist, BONE), (SO - 0.12, scene_official, RED),
          (IM - 0.12, scene_logo, INK), (BY - 0.12, scene_chain, BONE), (COME - 0.12, scene_calendar, BLUE),
          (WHEN - 0.12, scene_target, RED)]


def render(c, t):
    t = stepped(t, 15)
    run_scenes(c, t, SCENES)
    grain(c)


GLITCHES = [(DELUSIONAL - 0.02, 0.2, 0.8), (1.10, 0.06, 0.4), (1.55, 0.05, 0.3), (BLEEP - 0.02, 0.12, 1.0),
            (WHO - 0.02, 0.08, 0.6), (18.7, 0.06, 0.4)]


def post(buf, t, fi):
    for at, length, strength in GLITCHES:
        if at <= t < at + length:
            return glitch(buf, fi, strength)
    return buf


# ---------- sound (no voice, and nothing tonal over the bleep) ----------

def audio(path):
    m = sfx.Mix(DURATION)
    m.add(sfx.glitch(0.25, 1), DELUSIONAL - 0.02, 0.45)
    m.add(sfx.whoosh(0.5, 300, 2500, 2, 0.4), DELUSIONAL, 0.35)
    m.add(sfx.slam(3), SELF - LEAD - 0.18, 0.85, verb=0.2)

    m.add(sfx.whoosh(0.22, 600, 5000, 4, 0.8), AND - 0.3, 0.45, pan=0.3)
    for j, (_, appear, strike) in enumerate(CHECK_ITEMS):
        m.add(sfx.pop(392 + 60 * j, 0.12), appear, 0.35, pan=-0.3)
        m.add(sfx.marker(0.18, 5 + j), strike, 0.55, pan=0.2)
        m.add(sfx.blip(196, 0.09, 3), strike + 0.02, 0.3)
    m.add(sfx.pop(659, 0.14), YOU - LEAD, 0.45)
    m.add(sfx.impact(0.6, 140, 50, 8, 2.5), NEED - LEAD, 0.6, verb=0.25)
    m.add(sfx.shimmer(1568, 0.8), NEED, 0.3, verb=0.4)

    m.add(sfx.whoosh(0.22, 600, 5000, 9, 0.8), SO - 0.3, 0.45, pan=-0.3)
    for j, at in enumerate((SO, THIS, VIDEO)):
        m.add(sfx.tick(10 + j, 3500), at - LEAD, 0.35)
    m.add(sfx.stamp(13), OFFICIALLY - LEAD, 0.9, verb=0.2)
    for j, at in enumerate((MARKS, THE, START)):
        m.add(sfx.tick(14 + j, 3000), at - LEAD, 0.35, pan=-0.3 + 0.3 * j)
    m.add(sfx.slam(17), SERIES - LEAD - 0.18, 0.95, verb=0.25)
    m.add(sfx.sub_drop(1.0, 80, 28), SERIES - LEAD, 0.6)

    m.add(sfx.whoosh(0.22, 600, 5000, 18, 0.8), IM - 0.3, 0.45, pan=0.3)
    for j, at in enumerate((IM, GOING, TO, TRY, AND2, PROVE)):
        m.add(sfx.tick(19 + j, 3500), at - LEAD, 0.3, pan=-0.3 + 0.12 * j)
    m.add(sfx.impact(1.0, 160, 36, 25, 3.0), SIX - LEAD, 0.85, verb=0.3)
    for k, p in enumerate(sfx.scale_pops(6, 440)):
        m.add(p, SIX + k * 0.12, 0.35, pan=math.cos(math.radians(-90 + k * 60)) * 0.7, verb=0.2)
    m.add(sfx.slam(26), DEGREES - LEAD - 0.18, 0.6, verb=0.2)
    m.add(sfx.tick(27, 3000), SEPARATION - LEAD, 0.35)
    m.add(sfx.stamp(28), REAL - LEAD, 0.6, verb=0.2)

    m.add(sfx.whoosh(0.22, 600, 5000, 29, 0.8), BY - 0.3, 0.45, pan=-0.3)
    for j, at in enumerate((BY, GETTING, THIS2)):
        m.add(sfx.tick(30 + j, 3500), at - LEAD, 0.3)
    m.add(sfx.slam(33), CAP - LEAD - 0.18, 0.85, verb=0.2)
    m.add(sfx.pop(392, 0.14), ME - LEAD, 0.45, pan=-0.5)
    m.add(sfx.whoosh(0.25, 2500, 500, 34, 0.5), CAP_IN[1], 0.3, pan=-0.4)
    for j in range(5):
        m.add(sfx.pop(523 * 1.12 ** j, 0.1), ALL2 - LEAD + 0.05 * (j + 1), 0.3, pan=0.5 if j % 2 else -0.5)
    m.add(sfx.riser(FLIGHT[1] - FLIGHT[0], 35), FLIGHT[0], 0.3)
    for j in range(1, 6):
        u = j / 5
        land = FLIGHT[0] + (FLIGHT[1] - FLIGHT[0]) * u
        m.add(sfx.tick(36 + j, 3000), land, 0.35, pan=0.4 if j % 2 else -0.4)
    for j, at in enumerate((ALL2, THE2, WAY, TO2)):
        m.add(sfx.tick(42 + j, 2500), at - LEAD, 0.25)
    m.add(sfx.impact(0.7, 90, 32, 46, 2.0), BLEEP - LEAD, 0.7, verb=0.2)  # low, so it sits under the bleep

    m.add(sfx.whoosh(0.22, 600, 5000, 47, 0.8), COME - 0.3, 0.45, pan=0.3)
    for j, at in enumerate((COME, BACK, ON)):
        m.add(sfx.tick(48 + j, 3500), at - LEAD, 0.3)
    m.add(sfx.slam(51), OCTOBER - LEAD - 0.18, 0.85, verb=0.2)
    m.add(sfx.paper_slide(0.4, 52), NINETEENTH - LEAD, 0.9, pan=0.4)
    m.add(sfx.impact(0.8, 150, 40, 53, 3.0), NINETEENTH - LEAD, 0.7, verb=0.25)

    m.add(sfx.whoosh(0.22, 600, 5000, 54, 0.8), WHEN - 0.3, 0.45, pan=-0.3)
    for j, at in enumerate((WHEN, I, REVEAL)):
        m.add(sfx.tick(55 + j, 3500), at - LEAD, 0.3)
    m.add(sfx.glitch(0.08, 58), WHO - 0.02, 0.35)
    m.add(sfx.sub_drop(1.0, 70, 26), WHO - LEAD, 0.7)
    m.add(sfx.slam(59), FIRST - LEAD - 0.18, 0.6, verb=0.2)
    m.add(sfx.slam(60), TARGET - LEAD - 0.18, 0.85, verb=0.25)
    m.add(sfx.typing(6, 0.035, 61), IS2 + 0.25, 0.3)
    m.add(sfx.shimmer(1046.5, 1.4), IS2 + 0.3, 0.3, verb=0.5)
    m.add(sfx.glitch(0.06, 62), 18.7, 0.3)
    return m.write(path, room=1.0, loudness=-18.0)
