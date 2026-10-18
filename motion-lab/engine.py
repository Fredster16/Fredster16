"""Core of the motion lab: canvas, easing, text, timeline and video export.

Every style is a pure function of time: render(canvas, t) draws one frame.
Frames are rendered with Skia into a numpy buffer and piped straight to ffmpeg.
"""
import math
import os
import subprocess

import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(ROOT, "fonts")

# TikTok / Reels / Shorts UI covers the bottom ~380px and the right ~140px.
SAFE_TOP, SAFE_BOTTOM, SAFE_RIGHT = 160, H - 380, W - 140


# ---------- colour ----------

def rgb(hexstr, a=1.0):
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return skia.Color(r, g, b, int(max(0, min(1, a)) * 255))


def paint(color="#000000", a=1.0, stroke=None, cap="round", **kw):
    p = skia.Paint(AntiAlias=True, Color=rgb(color, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap({"round": skia.Paint.kRound_Cap, "butt": skia.Paint.kButt_Cap,
                        "square": skia.Paint.kSquare_Cap}[cap])
        p.setStrokeJoin(skia.Paint.kRound_Join)
    for k, v in kw.items():
        getattr(p, "set" + k)(v)
    return p


# ---------- easing ----------

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, start, dur):
    """0..1 progress of t through [start, start+dur]."""
    return clamp((t - start) / dur) if dur > 0 else float(t >= start)


def lerp(a, b, k):
    return a + (b - a) * k


def ease_out_cubic(k):
    return 1 - (1 - k) ** 3


def ease_in_cubic(k):
    return k ** 3


def ease_in_out(k):
    return 4 * k ** 3 if k < 0.5 else 1 - (-2 * k + 2) ** 3 / 2


def ease_out_expo(k):
    return 1 if k >= 1 else 1 - 2 ** (-10 * k)


def ease_out_back(k, s=1.70158):
    k -= 1
    return k * k * ((s + 1) * k + s) + 1


def spring(k, freq=3.2, damp=6.0):
    """Overshooting settle from 0 to 1 — the 'slam' feel."""
    if k <= 0:
        return 0.0
    if k >= 1:
        return 1.0
    return 1 - math.exp(-damp * k) * math.cos(freq * 2 * math.pi * k)


def stepped(t, fps):
    """Quantise time to a lower frame rate (stop-motion / hand-drawn feel)."""
    return math.floor(t * fps) / fps


# ---------- text ----------

_fonts = {}


def font(name, size):
    key = (name, size)
    if key not in _fonts:
        tf = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, name + ".ttf"))
        f = skia.Font(tf, size)
        f.setEdging(skia.Font.Edging.kAntiAlias)
        f.setSubpixel(True)
        _fonts[key] = f
    return _fonts[key]


def text_width(s, f, tracking=0.0):
    if not tracking:
        return f.measureText(s)
    return sum(f.measureText(ch) for ch in s) + tracking * (len(s) - 1)


def draw_text(c, s, x, y, f, p, align="center", tracking=0.0):
    """Draw s with its baseline at y. align: left|center|right."""
    w = text_width(s, f, tracking)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    if not tracking:
        c.drawString(s, x, y, f, p)
        return w
    for ch in s:
        c.drawString(ch, x, y, f, p)
        x += f.measureText(ch) + tracking
    return w


def fit_size(s, name, max_w, max_size, tracking_em=0.0):
    """Largest font size (<= max_size) at which s fits in max_w."""
    size = max_size
    while size > 20:
        f = font(name, size)
        if text_width(s, f, tracking_em * size) <= max_w:
            return size
        size -= 4
    return size


def cap_height(f):
    m = f.getMetrics()
    return m.fCapHeight or -m.fAscent * 0.7


# ---------- geometry helpers ----------

def path_from(points, closed=False):
    p = skia.Path()
    p.moveTo(*points[0])
    for pt in points[1:]:
        p.lineTo(*pt)
    if closed:
        p.close()
    return p


def trimmed(p_or_paint, start, stop):
    """Return a copy of a paint that only draws [start, stop] of each path (draw-on)."""
    p = skia.Paint(p_or_paint)
    start, stop = clamp(start), clamp(stop)
    if stop <= start:
        p.setAlphaf(0)
        return p
    eff = skia.TrimPathEffect.Make(start, stop)
    if eff is None:  # Skia returns None for the no-op range 0..1
        return p
    old = p.getPathEffect()
    p.setPathEffect(skia.PathEffect.MakeCompose(eff, old) if old else eff)
    return p


def jitter(p_or_paint, seg=14, dev=2.2, seed=0):
    """Hand-drawn wobble on strokes. Change seed every few frames for a 'boil'."""
    p = skia.Paint(p_or_paint)
    eff = skia.DiscretePathEffect.Make(seg, dev, seed)
    old = p.getPathEffect()
    p.setPathEffect(skia.PathEffect.MakeCompose(old, eff) if old else eff)
    return p


def hash01(*args):
    """Deterministic pseudo-random 0..1 from integers."""
    h = 2166136261
    for a in args:
        h = ((h ^ (int(a) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0x5bd1e995) & 0xFFFFFFFF
    h ^= h >> 15
    return (h & 0xFFFFFF) / float(0xFFFFFF)


# ---------- timeline ----------

class Timeline:
    """A list of beats (one idea per beat), each lasting until the next starts."""

    def __init__(self, beats, end):
        self.beats = beats
        self.end = end

    def at(self, t):
        i = 0
        for j, b in enumerate(self.beats):
            if t >= b["start"]:
                i = j
        b = self.beats[i]
        nxt = self.beats[i + 1]["start"] if i + 1 < len(self.beats) else self.end
        return i, b, t - b["start"], nxt - b["start"]


# ---------- export ----------

def render_video(render, duration, out_path, audio_path=None, post=None, fps=FPS):
    """Render frames 0..duration and encode to H.264 MP4 (with audio if given)."""
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
    if audio_path:
        cmd += ["-i", audio_path]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart"]
    if audio_path:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += [out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    buf = np.zeros((H, W, 4), np.uint8)
    surface = skia.Surface(buf)
    n = int(round(duration * fps))
    for i in range(n):
        t = i / fps
        canvas = surface.getCanvas()
        canvas.save()
        render(canvas, t)
        canvas.restore()
        frame = post(buf, t, i) if post else buf
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed")
    return out_path


def render_still(render, t, out_path, post=None):
    buf = np.zeros((H, W, 4), np.uint8)
    surface = skia.Surface(buf)
    render(surface.getCanvas(), t)
    frame = post(buf, t, int(t * FPS)) if post else buf
    img = skia.Image.fromarray(np.ascontiguousarray(frame))
    img.save(out_path, skia.kPNG)
    return out_path
