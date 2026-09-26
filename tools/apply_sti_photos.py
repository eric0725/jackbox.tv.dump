"""Point Survive the Internet's controller photos at the custom images in
images/survivetheinternet/photos/.

How it works: the game host only sends a photo *name* (e.g.
"images/survivetheinternet/photos/Beach.jpg"); the controller turns that into a
CSS class ("finalRoundImage Beach" / "Beach-thumb") whose background-image comes
from the bundle's stylesheet. This script appends override rules for every custom
photo to that stylesheet, between marker comments, so re-running it is safe.

Files must be named exactly like the game's photo (case-sensitive), e.g. Beach.jpg.
An optional <Name>-thumb.jpg is used for the voting thumbnail; otherwise the full
image is reused (thumbnails are drawn with background-size: contain).

Usage: python tools/apply_sti_photos.py
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "images" / "survivetheinternet" / "photos"
CSS = ROOT / "main" / "pp4" / "survivetheinternet" / "assets" / "style-0.css"
# Relative to the stylesheet's directory (main/pp4/survivetheinternet/assets/).
URL_PREFIX = "../../../../images/survivetheinternet/photos/"
START = "/* [mod] custom STI photos: start */"
END = "/* [mod] custom STI photos: end */"
EXTS = (".jpg", ".jpeg", ".png", ".webp", ".gif")


def main():
    css = CSS.read_text(encoding="utf-8")
    css = re.sub(r"\n*" + re.escape(START) + r".*?" + re.escape(END) + r"\n*", "\n", css, flags=re.S)
    known = set(re.findall(r"\.finalRoundImage\.([A-Za-z]+)\s*\{", css))

    files = {p.stem: p.name for p in sorted(PHOTOS.iterdir()) if p.suffix.lower() in EXTS}
    rules, applied, unknown = [], [], []
    for stem, name in files.items():
        if stem.endswith("-thumb"):
            continue
        if stem not in known:
            unknown.append(name)
            continue
        thumb = files.get(stem + "-thumb", name)
        rules.append(
            f".survivetheinternet .finalRoundImage.{stem} {{ background-image: url({URL_PREFIX}{name}) }}\n"
            f".survivetheinternet .{stem}-thumb {{ background-image: url({URL_PREFIX}{thumb}) }}"
        )
        applied.append(stem)

    block = "\n".join([START, *rules, END])
    CSS.write_text(css.rstrip("\n") + "\n\n" + block + "\n", encoding="utf-8", newline="")

    print(f"Overrode {len(applied)} of {len(known)} game photos: {', '.join(applied)}")
    for name in unknown:
        print(f"WARNING: {name} does not match any game photo name; ignored")


if __name__ == "__main__":
    main()
