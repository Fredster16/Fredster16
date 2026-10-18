# motion-lab

Code-driven vertical video (1080x1920, 30fps) for short-form edits, with every sound effect synthesised from scratch.

- `engine.py`: canvas, easing, text, timeline, MP4 export (Skia, piped to ffmpeg)
- `sfx.py`: sound-effect synths (whoosh, impact, pencil, glitch, pops and more) plus a mixer and a -16 LUFS master
- `script.py`: the beats (kicker + hero word per beat) and their start times
- `styles/`: one module per visual direction, each with `render(canvas, t)` and `audio(path)`
  - `field_notes.py`: ink on paper, a red marker, sheets sliding in
  - `signal.py`: terminal HUD, decoding type, glitch cuts
  - `poster.py`: colour-block print poster, Isotype pictograms, diagonal wipes

```
pip install skia-python scipy numpy      # skia needs libegl1 on Linux
python render.py signal                  # -> out/signal.mp4 (with sound)
python render.py signal --stills         # -> out/signal_sheet.png (key frames)
```

Fonts in `fonts/` are from Google Fonts under the SIL Open Font License.
