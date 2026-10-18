"""'Perfect. So theoretically I can get one of my caps into the hands of anyone in the world.'

Timed to the voice recording (word starts from Whisper, checked against the waveform).
The voice itself is not included — drop this over the recording at 0:00 and it lines up.
"""
import math
import os

import numpy as np
import skia

import geo
import sfx
from engine import (W, H, FPS, ROOT, paint, prog, lerp, clamp, spring, ease_in_out, ease_in_cubic,
                    ease_out_cubic, stepped, font, draw_text, path_from)
from house import (BONE, RED, RED_DARK, INK, BLUE, OCHRE, DISPLAY, LABEL, MONO, offset_text, word_line,
                   line_size, decode, counter, label_build, sticker, to_image, draw_image_centered,
                   run_scenes, grain, glitch, halftone_disc, shake, pop_scale)

DURATION = 7.4

# word start times (s) in the recording
PERFECT, SO, THEO, THEO_END = 0.97, 1.72, 1.86, 2.42
I, CAN, GET, ONE, OF, MY, CAPS = 2.55, 2.82, 2.97, 3.12, 3.28, 3.38, 3.56
INTO, THE, HANDS, OF2 = 3.88, 4.40, 4.55, 4.78
ANYONE, IN, THE2, WORLD = 5.08, 5.80, 5.98, 6.12
LEAD = 0.03  # land hits a frame early so they read on the word

STILL_TIMES = [1.2, 1.9, 2.3, 2.9, 3.2, 3.75, 4.1, 4.6, 5.3, 5.7, 6.3, 7.3]

CAP = sticker(os.path.join(ROOT, "assets", "cap_stone.png"))
CAP_IMG = to_image(CAP)
CAP_MINI = to_image(CAP, 120)
CAP_W = 780


# ---------- 1. PERFECT ----------

def scene_perfect(c, t):
    c.drawPaint(paint(BONE))
    k = prog(t, PERFECT - LEAD, 0.4)
    if k > 0:
        r = 360 * lerp(0.4, 1.0, spring(k, 1.8, 6))
        halftone_disc(c, W / 2 + 120, 900, r, RED, 26)
        c.save()
        shake(c, t, PERFECT - LEAD, 22, 1)
        size = line_size("PERFECT.", W - 170, 330)
        sc = pop_scale(t, PERFECT - LEAD, 0.45, 1.9)
        c.translate(W / 2, 960)
        c.scale(sc, sc)
        offset_text(c, "PERFECT.", 0, 120, size, INK, RED, 12, 10)
        c.restore()


# ---------- 2. SO THEORETICALLY ----------

def scene_theo(c, t):
    c.drawPaint(paint(INK))
    if t >= SO - LEAD:
        sc = pop_scale(t, SO - LEAD, 0.25, 1.4)
        c.save()
        c.translate(W / 2, 760)
        c.scale(sc, sc)
        draw_text(c, "SO", 0, 0, font(LABEL, 76), paint(BONE), "center", 6)
        c.restore()
    size = line_size("THEORETICALLY", W - 100, 260)
    locked = clamp((t - THEO) / (THEO_END - THEO))
    c.save()
    if t >= THEO_END:
        sc = pop_scale(t, THEO_END, 0.3, 1.12)
        c.translate(W / 2, 960)
        c.scale(sc, sc)
        c.translate(-W / 2, -960)
        offset_text(c, "THEORETICALLY", W / 2, 1040, size, BONE, RED, 9, 8)
    else:
        decode(c, "THEORETICALLY", W / 2, 1040, size, t, SO, THEO, THEO_END, BONE, RED, salt=3)
    c.restore()
    if t >= SO:
        bw = (W - 200) * ease_out_cubic(locked)
        c.drawRect(skia.Rect.MakeXYWH(100, 1100, W - 200, 12), paint(BONE, 0.15))
        c.drawRect(skia.Rect.MakeXYWH(100, 1100, bw, 12), paint(RED))


# ---------- 3. I CAN GET ONE OF MY CAPS ----------

def scene_cap(c, t):
    c.drawPaint(paint(RED))
    c.save()
    shake(c, t, ONE - LEAD, 26, 2)
    if t >= ONE - LEAD:
        sc = pop_scale(t, ONE - LEAD, 0.45, 1.8)
        c.save()
        c.translate(W / 2, 1100)
        c.scale(sc, sc)
        draw_text(c, "1", 0, 520, font(DISPLAY, 1350), paint(RED_DARK), "center")
        c.restore()
    i_can_get = [("I", I - LEAD), ("CAN", CAN - LEAD), ("GET", GET - LEAD)]
    if t < ONE - LEAD:
        word_line(c, i_can_get, W / 2, 1040, 240, t, BONE, INK, 10, 9)
    else:
        label_build(c, i_can_get, W / 2, 420, t, INK, BONE, 46)
    words = [("ONE", ONE - LEAD), ("OF", OF - LEAD), ("MY", MY - LEAD), ("CAPS", CAPS - LEAD)]
    size = line_size("ONE OF MY CAPS", W - 110, 220)
    word_line(c, words, W / 2, 640, size, t, BONE, INK, 10, 9)
    c.restore()


def cap_pose(t):
    """Where the hero cap is: slams in on 'caps', then shrinks into the UK on 'into'."""
    k_in = prog(t, CAPS - LEAD, 0.45)
    if k_in <= 0:
        return None
    x, y = W / 2, 1120 + 8 * math.sin(t * 3.4)
    width = CAP_W * lerp(1.55, 1.0, spring(k_in, 2.0, 7))
    rot = lerp(-12, -4, spring(k_in, 2.0, 7)) + 1.2 * math.sin(t * 2.6)
    k_out = prog(t, INTO + 0.02, 0.5)
    if k_out > 0:
        e = ease_in_cubic(k_out)
        ux, uy = project(UK, *camera(t))
        x, y = lerp(x, ux, e), lerp(y, uy, e)
        width = lerp(width, 18, e)
        rot = lerp(rot, -35, e)
    if k_out >= 1:
        return None
    return x, y, width, rot


def draw_cap(c, t):
    pose = cap_pose(t)
    if pose:
        x, y, width, rot = pose
        c.save()
        shake(c, t, CAPS - LEAD, 30, 4)
        draw_image_centered(c, CAP_IMG if width > 200 else CAP_MINI, x, y, width, rot)
        c.restore()


# ---------- 4. INTO THE HANDS OF ANYONE IN THE WORLD ----------

UK = (-1.5, 53.0)
CITIES = [(-74.0, 40.7), (139.7, 35.7), (-46.6, -23.5), (3.4, 6.5), (151.2, -33.9), (55.3, 25.2),
          (-118.2, 34.0), (72.9, 19.1), (37.6, 55.8), (18.4, -33.9), (116.4, 39.9), (-99.1, 19.4),
          (103.8, 1.35), (-58.4, -34.6), (36.8, -1.3), (-79.4, 43.7), (31.2, 30.0), (126.9, 37.5)]
DOTS = np.array(geo.dot_grid(3.2, (-130, 160), (-50, 76)))
MAP_S = 1000 / 290  # px per degree at full view
MAP_Y = 1135
WORLD_CENTRE = (15.0, 13.0)
ZOOM_START, ZOOM_END = INTO - 0.04, OF2 + 0.15
FLIGHT = 0.5


def camera(t):
    k = ease_in_out(prog(t, ZOOM_START, ZOOM_END - ZOOM_START))
    z = lerp(2.7, 1.0, k)
    lon = lerp(UK[0], WORLD_CENTRE[0], k)
    lat = lerp(UK[1] - 4, WORLD_CENTRE[1], k)
    if t >= WORLD - LEAD:
        z *= lerp(1.05, 1.0, ease_out_cubic(prog(t, WORLD - LEAD, 0.35)))
    return z, lon, lat


def project(p, z, clon, clat):
    return W / 2 + (p[0] - clon) * MAP_S * z, MAP_Y + (clat - p[1]) * MAP_S * 1.15 * z


def arc_point(a, b, u, lift):
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - lift
    return ((1 - u) ** 2 * a[0] + 2 * (1 - u) * u * mx + u * u * b[0],
            (1 - u) ** 2 * a[1] + 2 * (1 - u) * u * my + u * u * b[1])


def launch_time(j):
    return ANYONE - LEAD + j * 0.045


def scene_world(c, t):
    c.drawPaint(paint(BLUE))
    z, clon, clat = camera(t)
    xs = W / 2 + (DOTS[:, 0] - clon) * MAP_S * z
    ys = MAP_Y + (clat - DOTS[:, 1]) * MAP_S * 1.15 * z
    r = min(3.9 * z, 11)
    for x, y in zip(xs, ys):
        if -20 < x < W + 20 and 700 < y < H:
            c.drawCircle(x, y, r, paint(BONE, 0.85 * clamp((y - 780) / 140)))
    uk = project(UK, z, clon, clat)
    # routes: a mini cap flies out to every corner of the map
    for j, city in enumerate(CITIES):
        t0 = launch_time(j)
        k = prog(t, t0, FLIGHT)
        if k <= 0:
            continue
        b = project(city, z, clon, clat)
        lift = 0.28 * math.hypot(b[0] - uk[0], b[1] - uk[1])
        u = ease_in_out(k)
        p = skia.Path()
        p.moveTo(*uk)
        for s in range(1, 41):
            p.lineTo(*arc_point(uk, b, u * s / 40, lift))
        c.drawPath(p, paint(OCHRE, 0.95, stroke=4))
        if k < 1:
            hx, hy = arc_point(uk, b, u, lift)
            draw_image_centered(c, CAP_MINI, hx, hy, 74, -6)
        else:
            age = t - t0 - FLIGHT
            ring = (age * 1.3) % 1
            c.drawCircle(b[0], b[1], 9, paint(OCHRE))
            c.drawCircle(b[0], b[1], 9 + 30 * ring, paint(OCHRE, 0.8 * (1 - ring), stroke=3))
    pin_k = prog(t, INTO + 0.5, 0.3)
    if pin_k > 0:
        ring = ((t - INTO) * 1.1) % 1
        c.drawCircle(*uk, 13 * spring(pin_k, 2, 6), paint(RED))
        c.drawCircle(*uk, 13 + 36 * ring, paint(RED, 0.9 * (1 - ring), stroke=4))
    # headline
    if t < ANYONE - LEAD:
        size = 200
        word_line(c, [("INTO", INTO - LEAD), ("THE", THE - LEAD)], W / 2, 560, size, t, BONE, INK)
        word_line(c, [("HANDS", HANDS - LEAD), ("OF", OF2 - LEAD)], W / 2, 770, size, t, BONE, INK)
    else:
        c.save()
        shake(c, t, ANYONE - LEAD, 24, 5)
        size = line_size("ANYONE", W - 120, 330)
        word_line(c, [("ANYONE", ANYONE - LEAD)], W / 2, 600, size, t, BONE, INK, 12, 10)
        c.restore()
        c.save()
        shake(c, t, WORLD - LEAD, 30, 6)
        size2 = line_size("IN THE WORLD.", W - 120, 170)
        word_line(c, [("IN", IN - LEAD), ("THE", THE2 - LEAD), ("WORLD.", WORLD - LEAD, OCHRE)],
                  W / 2, 790, size2, t, BONE, INK, 9, 8)
        c.restore()
    if t >= ANYONE - LEAD:
        k = clamp((t - ANYONE) / (WORLD - ANYONE))
        val = 8_000_000_000 * ease_out_cubic(k)
        locked = t >= WORLD - LEAD
        counter(c, val, 13, W / 2, 1478, 62, OCHRE if locked else BONE, t, WORLD - LEAD, "+" if locked else "")
        draw_text(c, "PEOPLE", W / 2, 1530, font(LABEL, 28), paint(BONE, 0.75), "center", 8)


SCENES = [(0.0, scene_perfect, BONE), (SO - 0.12, scene_theo, INK), (I - 0.12, scene_cap, RED),
          (INTO - 0.1, scene_world, BLUE)]


def render(c, t):
    t = stepped(t, 15)
    run_scenes(c, t, SCENES)
    draw_cap(c, t)
    grain(c)


def post(buf, t, fi):
    for at, length, strength in ((SO - 0.06, 0.12, 1.0), (THEO_END - 0.02, 0.07, 0.5), (ANYONE - 0.05, 0.08, 0.6)):
        if at <= t < at + length:
            return glitch(buf, fi, strength)
    return buf


# ---------- sound (no voice) ----------

def audio(path):
    m = sfx.Mix(DURATION)
    m.add(sfx.slam(1), PERFECT - LEAD - 0.18, 0.85, verb=0.2)
    m.add(sfx.thud(0.35, 70, 2), PERFECT - LEAD, 0.6)

    m.add(sfx.whoosh(0.22, 700, 6000, 3, 0.8), SO - 0.2, 0.5, pan=-0.3)
    m.add(sfx.glitch(0.14, 4), SO - 0.06, 0.55, verb=0.05)
    m.add(sfx.tick(5, 3500), SO, 0.6)
    m.add(sfx.data_chatter(THEO_END - THEO, 6, 32), THEO, 0.32, pan=0.2, verb=0.1)
    m.add(sfx.blip(1318, 0.1), THEO_END, 0.45)
    m.add(sfx.impact(0.6, 120, 45, 7, 2.2), THEO_END, 0.5, verb=0.25)

    m.add(sfx.whoosh(0.22, 600, 5000, 8, 0.8), I - 0.2, 0.5, pan=0.3)
    for j, at in enumerate((I, CAN, GET)):
        m.add(sfx.typing(2, 0.03, 9 + j), at - LEAD, 0.45, pan=-0.2 + 0.2 * j)
    m.add(sfx.impact(0.9, 150, 40, 12, 3.0), ONE - LEAD, 0.8, verb=0.3)
    m.add(sfx.pop(523, 0.12), OF - LEAD, 0.35, pan=-0.3)
    m.add(sfx.pop(659, 0.12), MY - LEAD, 0.35, pan=0.3)
    m.add(sfx.slam(13), CAPS - LEAD - 0.18, 0.95, verb=0.25)
    m.add(sfx.pop(880, 0.16), CAPS - LEAD, 0.4)

    m.add(sfx.whoosh(0.22, 600, 5000, 14, 0.8), INTO - 0.2, 0.45, pan=-0.3)
    m.add(sfx.whoosh(0.7, 4000, 300, 15, 0.3), INTO, 0.55)
    for j, at in enumerate((INTO, THE, HANDS, OF2)):
        m.add(sfx.tick(16 + j, 3000), at - LEAD, 0.4, pan=0.4 - 0.25 * j)
    m.add(sfx.pop(392, 0.14), INTO + 0.5, 0.45)

    m.add(sfx.slam(17), ANYONE - LEAD - 0.18, 0.9, verb=0.2)
    m.add(sfx.glitch(0.08, 18), ANYONE - 0.05, 0.35)
    m.add(sfx.data_chatter(WORLD - ANYONE, 19, 26), ANYONE + 0.05, 0.18, verb=0.1)
    pops = sfx.scale_pops(len(CITIES), 440)
    for j, p in enumerate(pops):
        x, _ = project(CITIES[j], 1.0, *WORLD_CENTRE)
        m.add(p, launch_time(j) + FLIGHT, 0.3, pan=clamp((x - W / 2) / (W / 2), -1, 1) * 0.8, verb=0.2)
    m.add(sfx.tick(20, 3000), IN - LEAD, 0.35)
    m.add(sfx.tick(21, 3000), THE2 - LEAD, 0.35)
    m.add(sfx.impact(1.2, 170, 34, 22, 3.5), WORLD - LEAD, 0.95, verb=0.35)
    m.add(sfx.sub_drop(1.2, 80, 26), WORLD - LEAD, 0.7, verb=0.05)
    m.add(sfx.shimmer(1318.5, 1.3), WORLD, 0.4, verb=0.5)
    return m.write(path, room=1.0, loudness=-18.0)
