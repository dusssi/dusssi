#!/usr/bin/env python3
"""Convert a prepared grayscale photo into a row-by-row animated SVG."""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source-prepped.png"
OUT = ROOT / "dusssi-ascii.svg"
RAMP = " .`:-=+*cs#%@"
COLS, ROWS = 52, 42
CHAR_H = 10.5


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit("Prepared portrait not found. Run prep_photo.py with your photo first.")
    image = Image.open(SOURCE).convert("L")
    # Crop to the character-cell aspect ratio instead of distorting a portrait.
    image = ImageOps.fit(
        image,
        (COLS, ROWS),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.42),
    )
    pixels = np.asarray(image)
    lines = [
        "".join(RAMP[min(len(RAMP) - 1, int((255 - int(value)) / 256 * len(RAMP)))] for value in row)
        for row in pixels
    ]

    clips, text_lines = [], []
    for index, line in enumerate(lines):
        y = 25 + index * CHAR_H
        delay = index * 0.10
        clips.append(
            f'<clipPath id="row{index}"><rect x="0" y="{y - 10:.1f}" width="0" height="12">'
            f'<animate attributeName="width" from="0" to="340" dur="0.8s" '
            f'begin="{delay:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        text_lines.append(
            f'<text x="12" y="{y:.1f}" clip-path="url(#row{index})">{escape(line)}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="370" height="485" viewBox="0 0 370 485" role="img" aria-label="Animated ASCII portrait for dusssi">
<rect width="100%" height="100%" rx="10" fill="#0d1117" stroke="#30363d"/>
<text x="12" y="16" fill="#8b949e" font-family="monospace" font-size="10">dusssi@github:~/portrait</text>
<defs>{''.join(clips)}</defs>
<g fill="#c9d1d9" font-family="monospace" font-size="10.5" xml:space="preserve">
{''.join(text_lines)}
</g>
<text x="12" y="468" fill="#8b949e" font-family="monospace" font-size="10">[ portrait render complete ]</text>
</svg>"""
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
