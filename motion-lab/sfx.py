"""Synthesised sound-effect library — every sound is generated from scratch,
so it is original and royalty-free.

Each function returns a mono float32 numpy array at SR. `Mix` places sounds on a
timeline and writes a stereo WAV.
"""
import json
import math
import os
import subprocess
import wave

import numpy as np
from scipy import signal

SR = 48000


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def _rng(seed):
    return np.random.default_rng(seed)


def _env(n, attack=0.005, decay=0.2, curve=4.0):
    """Fast attack, exponential decay envelope."""
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    d = np.exp(-curve * np.maximum(t - attack, 0) / max(decay, 1e-4))
    return a * d


def _swell(n, peak=0.6, power=2.0):
    """Rise to a peak (as a fraction of length) then fall — for whooshes."""
    x = np.linspace(0, 1, n)
    up = (x / peak) ** power
    down = ((1 - x) / (1 - peak)) ** power
    return np.where(x < peak, up, down)


def _band(x, lo, hi, order=4):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def _lp(x, f, order=4):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)


def _hp(x, f, order=4):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)


def _sweep_sine(f0, f1, dur, curve="exp"):
    t = _t(dur)
    k = t / dur
    f = f0 * (f1 / f0) ** k if curve == "exp" else f0 + (f1 - f0) * k
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def _shaped_noise(dur, centre, width, seed=0):
    """Noise whose spectrum follows a moving band: centre(k)/width(k) for k in 0..1."""
    n = int(dur * SR)
    x = _rng(seed).standard_normal(n)
    f, tt, Z = signal.stft(x, fs=SR, nperseg=1024)
    k = tt / max(tt[-1], 1e-6)
    c = np.array([centre(v) for v in k])[None, :]
    w = np.array([width(v) for v in k])[None, :]
    mask = np.exp(-0.5 * ((np.log2(f[:, None] + 1) - np.log2(c)) / w) ** 2)
    _, y = signal.istft(Z * mask, fs=SR, nperseg=1024)
    return y[:n]


def norm(x, peak=1.0):
    m = np.max(np.abs(x)) or 1.0
    return (x / m * peak).astype(np.float32)


# ---------- transitions ----------

def whoosh(dur=0.45, lo=400, hi=3500, seed=1, peak=0.65):
    """Air whoosh: band of noise sweeping up then down."""
    y = _shaped_noise(dur, lambda k: lo + (hi - lo) * math.sin(math.pi * min(k / peak, 1) / 2) ** 2
                      if k < peak else hi - (hi - lo) * ((k - peak) / (1 - peak)) ** 0.7,
                      lambda k: 0.9, seed)
    return norm(y * _swell(len(y), peak, 1.6))


def paper_slide(dur=0.35, seed=2):
    """Soft papery swish — a sheet sliding over another."""
    y = _shaped_noise(dur, lambda k: 900 + 1400 * k, lambda k: 1.4, seed)
    grain = 0.6 + 0.4 * np.abs(_lp(_rng(seed + 9).standard_normal(len(y)), 60))
    return norm(_hp(y * grain, 250) * _swell(len(y), 0.35, 1.3), 0.8)


def riser(dur=1.0, seed=3):
    y = _shaped_noise(dur, lambda k: 300 + 6000 * k ** 2, lambda k: 0.7, seed)
    tone = _sweep_sine(110, 880, dur) * 0.25
    e = np.linspace(0, 1, len(y)) ** 2.5
    return norm((y + tone[:len(y)]) * e)


# ---------- hits ----------

def impact(dur=0.9, f0=140, f1=42, seed=4, drive=2.5):
    """Cinematic boom: pitch-dropping sine body + click + noise tail, saturated."""
    n = int(dur * SR)
    body = _sweep_sine(f0, f1, dur)[:n] * _env(n, 0.002, dur * 0.55, 3.0)
    click = _hp(_rng(seed).standard_normal(n), 1500) * _env(n, 0.0005, 0.012, 5)
    tail = _lp(_rng(seed + 1).standard_normal(n), 900) * _env(n, 0.002, 0.25, 4) * 0.5
    return norm(np.tanh(drive * (body + 0.6 * click + tail)))


def sub_drop(dur=1.1, f0=90, f1=28):
    n = int(dur * SR)
    return norm(_sweep_sine(f0, f1, dur)[:n] * _env(n, 0.01, dur * 0.7, 2.5))


def thud(dur=0.35, f=78, seed=5):
    """Soft low knock — a book landing on a desk."""
    n = int(dur * SR)
    body = _sweep_sine(f * 1.6, f, 0.06 + dur)[:n] * _env(n, 0.001, 0.12, 4)
    knock = _band(_rng(seed).standard_normal(n), 180, 900) * _env(n, 0.0008, 0.03, 5)
    return norm(np.tanh(1.8 * (body + 0.7 * knock)))


def slam(seed=6):
    """Poster slam: short whoosh into a punchy, bright impact."""
    w = whoosh(0.18, 800, 5000, seed, 0.9) * 0.5
    hit = impact(0.6, 180, 55, seed, 3.5)
    slap = _band(_rng(seed).standard_normal(int(0.08 * SR)), 900, 4000) * _env(int(0.08 * SR), 0.0005, 0.03, 5)
    out = np.zeros(len(w) + len(hit))
    out[:len(w)] += w
    out[len(w) - 400:len(w) - 400 + len(hit)] += hit
    out[len(w) - 400:len(w) - 400 + len(slap)] += slap * 0.8
    return norm(out)


def stamp(seed=7):
    n = int(0.3 * SR)
    knock = thud(0.3, 95, seed)
    rubber = _band(_rng(seed).standard_normal(n), 500, 2500) * _env(n, 0.001, 0.05, 5)
    return norm(knock[:n] + 0.6 * rubber)


# ---------- small accents ----------

def pop(freq=660, dur=0.12):
    """Bubbly UI pop — pitch falls into the note."""
    n = int(dur * SR)
    t = _t(dur)
    f = freq * (1 + 0.9 * np.exp(-t * 60))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.001, dur * 0.6, 4)
    return norm(y, 0.9)


def tick(seed=8, bright=4000, dur=0.025):
    n = int(dur * SR)
    y = _band(_rng(seed).standard_normal(n), bright * 0.6, min(bright * 1.6, 20000)) * _env(n, 0.0003, 0.006, 5)
    return norm(y)


def blip(freq=1200, dur=0.07, harmonics=5):
    """Digital square-ish blip."""
    n = int(dur * SR)
    t = _t(dur)
    y = sum(np.sin(2 * np.pi * freq * (2 * h + 1) * t) / (2 * h + 1) for h in range(harmonics))
    gate = np.ones(n)
    gate[int(n * 0.85):] = np.linspace(1, 0, n - int(n * 0.85))
    gate[:48] = np.linspace(0, 1, 48)
    return norm(y * gate, 0.7)


def glitch(dur=0.22, seed=9):
    """Bit-crushed digital burst made of random square stutters."""
    rng = _rng(seed)
    n = int(dur * SR)
    out = np.zeros(n)
    i = 0
    while i < n:
        seg = int(rng.uniform(0.008, 0.035) * SR)
        kind = rng.integers(0, 3)
        tt = np.arange(min(seg, n - i)) / SR
        if kind == 0:
            out[i:i + len(tt)] = np.sign(np.sin(2 * np.pi * rng.uniform(80, 2400) * tt))
        elif kind == 1:
            noise = rng.standard_normal(len(tt))
            out[i:i + len(tt)] = np.repeat(noise[::12], 12)[:len(tt)]
        i += seg
    crushed = np.round(out * 6) / 6
    return norm(_hp(crushed, 120) * _env(n, 0.001, dur, 1.2), 0.75)


def data_chatter(dur=1.0, seed=10, rate=28):
    """Rapid random computer beeps — counters and scanning."""
    rng = _rng(seed)
    out = np.zeros(int(dur * SR) + SR // 10)
    for k in range(int(dur * rate)):
        b = blip(rng.choice([880, 1320, 1760, 2640, 3520]), 0.022, 3)
        i = int(k / rate * SR)
        out[i:i + len(b)] += b * rng.uniform(0.35, 0.8)
    return norm(out[:int(dur * SR)], 0.8)


def typing(n_keys=8, interval=0.045, seed=11):
    rng = _rng(seed)
    out = np.zeros(int((n_keys * interval + 0.1) * SR))
    for k in range(n_keys):
        tk = tick(seed + k, rng.uniform(2500, 5000), 0.02)
        i = int((k * interval + rng.uniform(-0.006, 0.006)) * SR)
        i = max(i, 0)
        out[i:i + len(tk)] += tk * rng.uniform(0.5, 1)
    return norm(out, 0.9)


def alarm(freq=1046, beeps=2):
    out = np.zeros(int(0.32 * beeps * SR))
    for k in range(beeps):
        b = blip(freq, 0.12, 4)
        i = int(k * 0.16 * SR)
        out[i:i + len(b)] += b
    return norm(out, 0.8)


def pencil(dur=0.5, seed=12, speed=22):
    """Graphite scratch — bandpassed noise with stroke-rate amplitude flutter."""
    n = int(dur * SR)
    x = _band(_rng(seed).standard_normal(n), 2200, 9000)
    t = _t(dur)
    flutter = 0.55 + 0.45 * np.abs(np.sin(np.pi * speed * t + _lp(_rng(seed + 1).standard_normal(n), 8) * 30))
    e = np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.05)
    return norm(x * flutter * e, 0.7)


def marker(dur=0.45, seed=13):
    """Felt-tip squeak/scrape — lower, smoother than pencil."""
    n = int(dur * SR)
    x = _band(_rng(seed).standard_normal(n), 900, 3800)
    t = _t(dur)
    squeak = np.sin(2 * np.pi * np.cumsum(1400 + 220 * np.sin(2 * np.pi * 7 * t)) / SR) * 0.08
    e = np.minimum(1, t / 0.015) * np.minimum(1, (dur - t) / 0.06)
    return norm((x + squeak) * e * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * t)), 0.7)


def shimmer(freq=1318.5, dur=1.6):
    """Bell/sparkle for a reveal — inharmonic partials, slightly detuned."""
    n = int(dur * SR)
    t = _t(dur)
    y = np.zeros(n)
    for ratio, amp, dec in [(1, 1, 1.0), (2.76, 0.5, 0.6), (5.4, 0.28, 0.35), (8.93, 0.15, 0.2)]:
        for det in (-1.5, 1.5):
            y += amp * np.sin(2 * np.pi * (freq * ratio + det) * t) * np.exp(-t / (dec * dur * 0.5))
    sparkle = _hp(_rng(14).standard_normal(n), 7000) * np.exp(-t * 6) * 0.15
    return norm((y + sparkle) * np.minimum(1, t / 0.003))


def scale_pops(count, start_freq=440, step=1.0595 ** 2):
    """A rising run of pops (one per item that appears)."""
    return [pop(start_freq * step ** (k % 12), 0.1) for k in range(count)]


# ---------- mixing ----------

def _reverb_ir(seconds=1.2, seed=99):
    n = int(seconds * SR)
    rng = _rng(seed)
    ir = rng.standard_normal((2, n)) * np.exp(-np.arange(n) / SR * 5.5)
    ir = np.stack([_lp(ch, 6000) for ch in ir])
    ir[:, :int(0.012 * SR)] = 0
    return ir / np.max(np.abs(ir))


class Mix:
    def __init__(self, duration):
        self.n = int(duration * SR)
        self.dry = np.zeros((2, self.n))
        self.send = np.zeros(self.n)

    def add(self, sound, at, gain=0.8, pan=0.0, verb=0.15):
        i = int(at * SR)
        if i >= self.n:
            return
        s = sound[:self.n - i]
        l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        self.dry[0, i:i + len(s)] += s * gain * l * 1.414
        self.dry[1, i:i + len(s)] += s * gain * r * 1.414
        self.send[i:i + len(s)] += s * gain * verb

    def add_stereo(self, stereo, at, gain=1.0):
        i = int(at * SR)
        s = stereo[:, :self.n - i]
        self.dry[:, i:i + s.shape[1]] += s * gain

    def render(self, room=1.2):
        ir = _reverb_ir(room)
        wet = np.stack([signal.fftconvolve(self.send, ir[c])[:self.n] for c in range(2)]) * 0.35
        out = self.dry + wet
        out = np.tanh(out * 1.1) / np.tanh(1.1)
        return norm(out, 0.89)

    def write(self, path, room=1.2, loudness=-16.0):
        write_wav(path, self.render(room))
        return master(path, loudness)


def master(path, loudness=-16.0, true_peak=-1.5):
    """Two-pass EBU R128 loudness normalisation in place (TikTok plays around -14 to -16 LUFS)."""
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
                            f"loudnorm=I={loudness}:TP={true_peak}:LRA=20:print_format=json",
                            "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    tmp = path + ".tmp.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-af",
                    f"loudnorm=I={loudness}:TP={true_peak}:LRA=20:linear=true:"
                    f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
                    f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}",
                    "-ar", str(SR), tmp], check=True)
    os.replace(tmp, path)
    return path


def write_wav(path, data):
    data = np.atleast_2d(data)
    if data.shape[0] > data.shape[1]:
        data = data.T
    pcm = (np.clip(data, -1, 1) * 32767).astype("<i2").T.copy()
    with wave.open(path, "wb") as w:
        w.setnchannels(pcm.shape[1])
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
