"""Render a style direction or a finished piece.

    python render.py field_notes                # style demo: full MP4 with sound
    python render.py field_notes --stills       # contact sheet of key frames only
    python render.py pieces.caps_world          # a piece timed to a voice line
"""
import argparse
import importlib
import os
import subprocess

import engine
from script import timeline, END

OUT = os.path.join(engine.ROOT, "out")


def stills(mod, name):
    times = getattr(mod, "STILL_TIMES", None)
    if not times:
        times = []
        for i, b in enumerate(timeline.beats):
            nxt = timeline.beats[i + 1]["start"] if i + 1 < len(timeline.beats) else END
            times += [b["start"] + 0.15, b["start"] + 0.5, nxt - 0.05]
    paths = []
    for j, t in enumerate(times):
        p = os.path.join(OUT, f"{name}_still_{j:02d}.png")
        engine.render_still(mod.render, t, p, getattr(mod, "post", None))
        paths.append(p)
    sheet = os.path.join(OUT, f"{name}_sheet.png")
    subprocess.run(["montage", *paths, "-tile", f"{-(-len(times) // 3)}x3", "-geometry", "360x640+4+4",
                    "-background", "#111", sheet], check=True)
    for p in paths:
        os.remove(p)
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("style")
    ap.add_argument("--stills", action="store_true")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    mod = importlib.import_module(args.style if "." in args.style else f"styles.{args.style}")
    name = args.style.split(".")[-1]
    if args.stills:
        print(stills(mod, name))
        return
    wav = mod.audio(os.path.join(OUT, f"{name}_sfx.wav"))
    mp4 = engine.render_video(mod.render, getattr(mod, "DURATION", END), os.path.join(OUT, f"{name}.mp4"), wav,
                              getattr(mod, "post", None))
    print(mp4)


if __name__ == "__main__":
    main()
