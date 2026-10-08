"""Turn a book-reduction .md (or .txt) file into an MP3 with free Microsoft neural voices.

Usage:
    python3 md_to_audio.py FILE [--voice en-GB-RyanNeural] [--rate -5%] [--out OUT.mp3] [--preview]

The MP3 is saved next to FILE with the same name, unless --out gives another path. --preview prints the
cleaned text instead of making audio, so you can check what will be read.
Needs: python3 -m pip install edge-tts
"""
import argparse
import asyncio
import re
import sys
from pathlib import Path

ABBREVIATIONS = {
    r"\bCh\.\s*": "Chapter ",
    r"\be\.g\.": "for example",
    r"\bi\.e\.": "that is",
    r"\betc\.": "and so on",
    r"\bvs\.": "versus",
    r"\bc\.\s*": "about ",
    r"&": " and ",
    r"→|->": ", which leads to, ",
    r"%": " percent",
}


def clean(text: str) -> str:
    # Lines that only explain the page-numbering system
    text = re.sub(r"^.*\b(References are|Page references are)\b.*$", "", text, flags=re.M)
    # Page references: (p. 4), (pp. 4–5), (pp. 31–32, 52), pp. vii–xii
    page = r"[\dvxlic]+(?:\s*[–\-]\s*[\dvxlic]+)?"
    text = re.sub(rf"\s*\((?:pp?\.|pages?)\s*{page}(?:,\s*{page})*\)", "", text)
    text = re.sub(rf",?\s*\bpp?\.\s*{page}(?:,\s*{page})*", "", text)
    # Classical references like (XII, 26) or (VI, 42, quoted on p. 54)
    text = re.sub(r"\((?:[IVXL]+,\s*\d+[^)]*)\)", "", text)
    text = re.sub(r"\b[IVXL]+,\s*\d+(?:,\s*\d+)?\b", "", text)
    # Markdown structure
    text = re.sub(r"^\s*---+\s*$", "", text, flags=re.M)
    text = re.sub(r"^\s*#+\s*(.+?)\s*$", r"\n\1.\n", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"\*\*|__|\*|_|`", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Abbreviations and symbols
    for pattern, spoken in ABBREVIATIONS.items():
        text = re.sub(pattern, spoken, text)
    text = text.replace("…", ".").replace(". . .", ".").replace("—", ", ").replace("–", " to ")
    text = re.sub(r"\s*\(\s*\)", "", text)
    # Make sure every line ends in a pause
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if line and line[-1] not in ".!?:;,":
            line += "."
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"\.\.+", ".", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


async def speak(text: str, voice: str, rate: str, out: Path) -> None:
    import edge_tts
    await edge_tts.Communicate(text, voice, rate=rate).save(str(out))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", type=Path)
    parser.add_argument("--voice", default="en-GB-RyanNeural")
    parser.add_argument("--rate", default="+0%", help="e.g. -10%% slower, +10%% faster")
    parser.add_argument("--out", type=Path, help="where to save the MP3 (default: next to FILE)")
    parser.add_argument("--preview", action="store_true", help="print cleaned text, make no audio")
    args = parser.parse_args()

    if not args.file.exists():
        sys.exit(f"Can't find {args.file}. Tip: type the command, then drag the file into Terminal.")
    text = clean(args.file.read_text(encoding="utf-8"))
    if args.preview:
        print(text)
        return

    out = args.out.expanduser() if args.out else args.file.with_suffix(".mp3")
    print(f"Making {out.name} ({len(text.split()):,} words, about {len(text.split()) // 150} min of audio)...")
    print("This can take a few minutes with no further output.")
    asyncio.run(speak(text, args.voice, args.rate, out))
    print(f"Done: {out}")


if __name__ == "__main__":
    main()
