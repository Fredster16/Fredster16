"""House style: POSTER base with SIGNAL accents.

Poster: flat colour blocks per beat, diagonal wipes, huge Anton type with a
misregistered print offset, halftone, paper grain, slams with screen shake, animated
on twos. Signal: type that scrambles before it locks, counters, dot-matrix maps,
a short glitch on key cuts. Nothing sits on the frame edges — no handle, no HUD.
"""
import random

import numpy as np
import skia
from PIL import Image
from scipy import ndimage

from engine import W, H, FPS, rgb, paint, prog, lerp, clamp, spring, font, draw_text, text_width
from styles.poster import GRAIN, halftone_disc, shake, half_plane, offset_text

BONE = "#F2EBDC"
RED = "#E3301F"
RED_DARK = "#B9230F"
INK = "#151413"
BLUE = "#1F3CB5"
OCHRE = "#F2AD1B"

DISPLAY, LABEL, MONO = "Anton-Regular", "ArchivoBlack-Regular", "JetBrainsMono-ExtraBold"
SCRAMBLE = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#%&@$"
WIPE = 0.18


# ---------- type ----------

def pop_scale(t, at, dur=0.32, start=1.6):
    """Spring from `start` down to 1 — the per-word slam."""
    return lerp(start, 1.0, spring(prog(t, at, dur), 2.2, 7))


def word_line(c, words, cx, baseline, size, t, fg, off, dx=8, dy=7):
    """A line that builds word by word as each is spoken.
    words = [(text, time), ...] or [(text, time, colour), ...] to colour single words."""
    f = font(DISPLAY, size)
    space = f.measureText(" ")
    widths = [f.measureText(w[0]) for w in words]
    x = cx - (sum(widths) + space * (len(words) - 1)) / 2
    for word, wd in zip(words, widths):
        w, at = word[:2]
        if t >= at:
            sc = pop_scale(t, at)
            c.save()
            c.translate(x + wd / 2, baseline - size * 0.35)
            c.scale(sc, sc)
            offset_text(c, w, 0, size * 0.35, size, word[2] if len(word) > 2 else fg, off, dx, dy)
            c.restore()
        x += wd + space


def line_size(text, max_w, max_size):
    size = max_size
    while size > 40 and text_width(text, font(DISPLAY, size)) > max_w:
        size -= 4
    return size


def decode(c, s, cx, baseline, size, t, start, lock0, lock1, fg, scramble_color, salt=0):
    """Signal-style decode on proportional type: each cell flickers through random
    glyphs, then locks left to right between lock0 and lock1."""
    f = font(DISPLAY, size)
    widths = [f.measureText(ch) for ch in s]
    x = cx - sum(widths) / 2
    n = max(len(s) - 1, 1)
    for j, ch in enumerate(s):
        lock_t = lock0 + (lock1 - lock0) * j / n
        if t >= start and ch != " ":
            if t < lock_t:
                g = SCRAMBLE[int(abs(hash((j, int(t * 30), salt))) % len(SCRAMBLE))]
                squeeze = min(1.0, widths[j] / f.measureText(g))
                c.save()
                c.translate(x + widths[j] / 2, baseline)
                c.scale(squeeze, 1)
                draw_text(c, g, 0, 0, f, paint(scramble_color, 0.9))
                c.restore()
            else:
                draw_text(c, ch, x + widths[j] / 2, baseline, f, paint(fg))
        x += widths[j]
    return clamp((t - lock0) / max(lock1 - lock0, 1e-6))


def counter(c, value, digits, cx, baseline, size, color, t, lock_t, suffix=""):
    """Comma-grouped counter whose unlocked digits scramble."""
    s = f"{int(value):0{digits},}"
    f = font(MONO, size)
    if t < lock_t:
        s = "".join(ch if ch in ", " or hash((i, int(t * 30))) % 3 else str(abs(hash((i, int(t * 60)))) % 10)
                    for i, ch in enumerate(s))
    draw_text(c, s + suffix, cx, baseline, f, paint(color), "center")


def label_build(c, words, x, y, t, bg, fg, size=40, rot=-2.5):
    """Kicker label whose text types on word by word."""
    shown = " ".join(w for w, at in words if t >= at)
    if not shown:
        return
    f = font(LABEL, size)
    w = text_width(shown, f, 2)
    c.save()
    c.rotate(rot, x, y)
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2 - 24, y - size - 12, x + w / 2 + 24, y + 18), paint(bg))
    draw_text(c, shown, x, y, f, paint(fg), "center", 2)
    c.restore()


def silhouette(c, x, y, s, fill, mark, t, appear, off=RED):
    """Unknown person: head-and-shoulders bust with a "?" face and a print offset."""
    sc = spring(prog(t, appear, 0.35), 2.2, 6)
    if sc <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    p = skia.Path()
    p.addCircle(0, -0.2 * s, 0.25 * s)
    body = skia.Path()
    body.moveTo(-0.5 * s, 0.56 * s)
    body.lineTo(-0.5 * s, 0.4 * s)
    body.cubicTo(-0.5 * s, 0.14 * s, -0.3 * s, 0.08 * s, 0, 0.08 * s)
    body.cubicTo(0.3 * s, 0.08 * s, 0.5 * s, 0.14 * s, 0.5 * s, 0.4 * s)
    body.lineTo(0.5 * s, 0.56 * s)
    body.close()
    p.addPath(body)
    c.save()
    c.translate(9, 8)
    c.drawPath(p, paint(off))
    c.restore()
    c.drawPath(p, paint(fill))
    draw_text(c, "?", 0, -0.2 * s + 0.15 * s, font(DISPLAY, 0.42 * s), paint(mark), "center")
    c.restore()


def tag_label(c, txt, x, y, t, at, bg, fg):
    """Small tilted name tag that pops in on a word."""
    if t >= at:
        sc = pop_scale(t, at, 0.3, 1.6)
        c.save()
        c.translate(x, y)
        c.scale(sc, sc)
        f = font(LABEL, 38)
        w = f.measureText(txt) + 2 * (len(txt) - 1)
        c.rotate(-3)
        c.drawRect(skia.Rect.MakeLTRB(-w / 2 - 18, -40, w / 2 + 18, 12), paint(bg))
        draw_text(c, txt, 0, 0, f, paint(fg), "center", 2)
        c.restore()


# ---------- images ----------

def sticker(path, border=18, shadow=(16, 14)):
    """Cut-out photo with a bone sticker border and a hard ink print shadow."""
    im = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32) / 255
    pad = border + max(shadow) + 4
    im = np.pad(im, ((pad, pad), (pad, pad), (0, 0)))
    solid = im[..., 3] > 0.5
    dist = ndimage.distance_transform_edt(~solid)
    edge = np.clip(border - dist + 0.5, 0, 1)
    h, w = solid.shape
    out = np.zeros((h, w, 4), np.float32)
    ink = np.array([int(INK[i:i + 2], 16) for i in (1, 3, 5)]) / 255
    bone = np.array([int(BONE[i:i + 2], 16) for i in (1, 3, 5)]) / 255
    sh = np.roll(np.roll(edge, shadow[1], 0), shadow[0], 1)
    for layer_rgb, layer_a in ((ink, sh), (bone, edge), (im[..., :3], im[..., 3])):
        a = layer_a[..., None]
        out[..., :3] = layer_rgb * a + out[..., :3] * (1 - a)
        out[..., 3:] = a + out[..., 3:] * (1 - a)
    rgba = (np.clip(out, 0, 1) * 255).astype(np.uint8)
    rgba[..., :3] = (rgba[..., :3].astype(np.float32) * (rgba[..., 3:] / 255)).astype(np.uint8)  # premultiply
    return rgba


def to_image(rgba, width=None):
    if width:
        pil = Image.fromarray(rgba, "RGBA")
        pil = pil.resize((width, round(rgba.shape[0] * width / rgba.shape[1])), Image.LANCZOS)
        rgba = np.asarray(pil)
    return skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType,
                                alphaType=skia.kPremul_AlphaType)


def draw_image_centered(c, img, x, y, width, rot=0.0):
    h = width * img.height() / img.width()
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.drawImageRect(img, skia.Rect.MakeXYWH(-width / 2, -h / 2, width, h),
                    skia.SamplingOptions(skia.FilterMode.kLinear), skia.Paint(AntiAlias=True))
    c.restore()


# ---------- scenes ----------

def run_scenes(c, t, scenes):
    """scenes = [(start, draw_fn, bg)]; each new scene wipes in on the poster diagonal."""
    i = max(j for j, s in enumerate(scenes) if t >= s[0])
    start, fn, bg = scenes[i]
    lt = t - start
    if i > 0 and lt < WIPE:
        scenes[i - 1][1](c, t)
        span = W * 0.53 + H * 0.85 + 200
        e = lerp(-100, span, lt / WIPE)
        c.save()
        c.clipPath(half_plane(e + 60), skia.ClipOp.kIntersect, True)
        c.drawPaint(paint(INK if bg != INK else RED))
        c.restore()
        c.save()
        c.clipPath(half_plane(e), skia.ClipOp.kIntersect, True)
        fn(c, t)
        c.restore()
    else:
        fn(c, t)


def grain(c):
    gp = skia.Paint()
    gp.setBlendMode(skia.BlendMode.kMultiply)
    c.drawImage(GRAIN, 0, 0, skia.SamplingOptions(), gp)


def glitch(buf, fi, strength=1.0):
    """Signal's cut glitch: RGB split, sliced rows, one bright flash frame."""
    img = buf[..., :3].astype(np.int16)
    shift = int(10 * strength)
    img[..., 0] = np.roll(img[..., 0], shift, axis=1)
    img[..., 2] = np.roll(img[..., 2], -shift, axis=1)
    rng = random.Random(fi * 31)
    for _ in range(int(8 * strength)):
        y0 = rng.randrange(0, H - 200)
        hgt = rng.randrange(16, 150)
        img[y0:y0 + hgt] = np.roll(img[y0:y0 + hgt], rng.randrange(-150, 150), axis=1)
    out = np.empty((H, W, 4), np.uint8)
    out[..., :3] = np.clip(img, 0, 255)
    out[..., 3] = 255
    return out
