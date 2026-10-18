# motion-lab

Code-driven vertical video (1080x1920, 30fps) for short-form edits, with every sound effect synthesised from scratch.

- `engine.py`: canvas, easing, text, timeline, MP4 export (Skia, piped to ffmpeg)
- `sfx.py`: sound-effect synths (whoosh, impact, pencil, glitch, pops and more) plus a mixer and a -16 LUFS master
- `script.py`: the beats (kicker + hero word per beat) and their start times
- `house.py`: the chosen house style: Poster base with Signal accents, nothing on the frame edges
- `pieces/`: finished videos timed to a voice line (the voice itself is never baked in)
  - `caps_world.py`: "Perfect. So theoretically I can get one of my caps into the hands of anyone in the world."
  - `kane_chain.py`: "Let's take Harry Kane as an example... four people between me and him... Easy."
    Needs `assets/private/me_bust.png` and `kane_bust.png` (cut-out photos, kept out of git).
- `geo.py`: dot-matrix world map from `assets/land-110m.json` (Natural Earth via world-atlas)
- `assets/`: cap cut-out, map data
- `styles/`: the three original directions, each with `render(canvas, t)` and `audio(path)`
  - `field_notes.py`: ink on paper, a red marker, sheets sliding in
  - `signal.py`: terminal HUD, decoding type, glitch cuts
  - `poster.py`: colour-block print poster, Isotype pictograms, diagonal wipes

```
pip install skia-python scipy numpy      # skia needs libegl1 on Linux
python render.py signal                  # -> out/signal.mp4 (with sound)
python render.py signal --stills         # -> out/signal_sheet.png (key frames)
python render.py pieces.caps_world       # -> out/caps_world.mp4 + out/caps_world_sfx.wav
```

Word timings for a piece come from the voice recording (faster-whisper word timestamps,
checked against the waveform) and live as constants at the top of the piece.

Fonts in `fonts/` are from Google Fonts under the SIL Open Font License.
