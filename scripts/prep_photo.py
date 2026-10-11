#!/usr/bin/env python3
"""Prepare a local photo for ASCII conversion; the original photo stays local."""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "source-prepped.png"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/prep_photo.py path/to/photo.jpg")
    source = Path(sys.argv[1])
    if not source.is_file():
        raise SystemExit(f"Photo not found: {source}")

    try:
        from rembg import remove
        cutout = remove(Image.open(source).convert("RGBA"))
        white = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
        white.alpha_composite(cutout)
        rgb = white.convert("RGB")
    except Exception as exc:
        print(f"Background removal unavailable ({exc}); using photo on white: {exc}")
        rgb = Image.open(source).convert("RGB")

    gray = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8)).apply(gray)
    gray = cv2.convertScaleAbs(gray, alpha=1.12, beta=8)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(gray).save(OUTPUT)
    print(f"Prepared image saved to {OUTPUT}")


if __name__ == "__main__":
    main()
