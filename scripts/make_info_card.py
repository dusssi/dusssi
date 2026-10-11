"""Generate an animated neofetch-style developer information SVG."""
import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "info-card.svg"
STATIC = os.getenv("STATIC", "0") == "1"
ROWS = [
    ("role", "MCA · AI/ML student"),
    ("focus", "Python · NLP · Computer Vision"),
    ("stack", "React · FastAPI · PostgreSQL"),
    ("building", "Practical AI applications"),
    ("projects", "Resume matching · Route planning"),
    ("learning", "ML systems · full-stack engineering"),
]


def main() -> None:
    rows = []
    for index, (key, value) in enumerate(ROWS):
        y = 95 + index * 43
        animation = "" if STATIC else f' class="row" style="--delay:{index * 0.14:.2f}s"'
        rows.append(
            f'<g{animation}><text x="28" y="{y}" class="key">{escape(key)}</text>'
            f'<text x="142" y="{y}" class="value">{escape(value)}</text></g>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="490" height="485" viewBox="0 0 490 485" role="img" aria-label="Developer info card for dusssi">
<style>
 text {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
 .title {{ font-size: 13px; fill: #c9d1d9; }}
 .key {{ font-size: 12px; fill: #7ee787; }}
 .value {{ font-size: 12px; fill: #c9d1d9; }}
 .muted {{ font-size: 10px; fill: #8b949e; }}
 .row {{ opacity: 0; animation: enter .4s ease-out var(--delay) forwards; }}
 @keyframes enter {{ from {{ opacity: 0; transform: translateX(8px); }} to {{ opacity: 1; transform: translateX(0); }} }}
 @media (prefers-reduced-motion: reduce) {{ .row {{ animation: none; opacity: 1; }} }}
</style>
<rect width="100%" height="100%" rx="10" fill="#0d1117" stroke="#30363d"/>
<path d="M10 0 H480 Q490 0 490 10 V42 H0 V10 Q0 0 10 0Z" fill="#161b22"/>
<circle cx="18" cy="21" r="4" fill="#ff7b72"/><circle cx="32" cy="21" r="4" fill="#d29922"/><circle cx="46" cy="21" r="4" fill="#7ee787"/>
<text x="65" y="25" class="title">dusssi@github — profile</text>
<text x="28" y="67" class="muted">PROFILE :: AI / ML</text>
{''.join(rows)}
<line x1="28" y1="370" x2="462" y2="370" stroke="#30363d"/>
<text x="28" y="399" class="muted">STATUS</text><text x="142" y="399" class="value">learning · building · iterating</text>
<text x="28" y="431" class="muted">GITHUB</text><text x="142" y="431" class="value">github.com/dusssi</text>
<text x="28" y="455" class="muted">Keep it real. Build useful things.</text>
</svg>"""
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
