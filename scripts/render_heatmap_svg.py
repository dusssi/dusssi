#!/usr/bin/env python3
"""Render real fetched contribution cells as a self-contained animated SVG."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    days = payload.get("days", [])
    if not days:
        raise RuntimeError("No contribution days in data/contributions.json")

    first = date.fromisoformat(days[0]["date"])
    # Align the first column to Sunday.
    start = first.fromordinal(first.toordinal() - (first.weekday() + 1) % 7)
    by_date = {item["date"]: item for item in days}
    username = escape(payload.get("username", "GitHub"))
    stats = payload.get("stats", {})
    total = stats.get("contributions_visible_calendar")
    total_label = (
        f"{total:,} contributions visible on GitHub"
        if isinstance(total, int)
        else "Contribution counts not exposed by GitHub HTML"
    )
    current = stats.get("current_streak_days_estimate", 0)
    longest = stats.get("longest_streak_days_estimate", 0)

    left, top, cell, gap = 18, 32, 10, 4
    rects, month_labels = [], []
    for col in range(53):
        col_date = start.fromordinal(start.toordinal() + col * 7)
        if col_date.day <= 7:
            month_labels.append(
                f'<text x="{left + col * (cell + gap)}" y="18" class="month">{col_date.strftime("%b")}</text>'
            )
        for row in range(7):
            day = start.fromordinal(start.toordinal() + col * 7 + row)
            if day > date.today():
                continue
            item = by_date.get(day.isoformat(), {})
            level = max(0, min(4, int(item.get("level", 0))))
            x, y = left + col * (cell + gap), top + row * (cell + gap)
            delay = col * 0.010 + row * 0.025
            count = item.get("count")
            detail = f"{count} contributions" if count is not None else f"activity level {level}"
            title = escape(f"{day.isoformat()}: {detail}")
            rects.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
                f'fill="{PALETTE[level]}" class="day" style="--delay:{delay:.3f}s">'
                f'<title>{title}</title></rect>'
            )

    legend = '<text x="665" y="146" class="small">Less</text>'
    for index, color in enumerate(PALETTE):
        legend += f'<rect x="{700 + index * 15}" y="136" width="10" height="10" rx="2" fill="{color}"/>'
    legend += '<text x="780" y="146" class="small">More</text>'
    footer = escape(
        f"{total_label} · Current streak estimate: {current} days · Longest estimate: {longest} days"
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="860" height="190" viewBox="0 0 860 190" role="img" aria-label="GitHub contribution calendar for {username}">
<style>
 text {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
 .month {{ font-size: 10px; fill: #8b949e; }}
 .small {{ font-size: 10px; fill: #8b949e; }}
 .footer {{ font-size: 11px; fill: #c9d1d9; }}
 .day {{ opacity: 0; animation: reveal .35s ease-out var(--delay) forwards; }}
 @keyframes reveal {{ from {{ opacity: 0; transform: translateY(-5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
 @media (prefers-reduced-motion: reduce) {{ .day {{ animation: none; opacity: 1; }} }}
</style>
<rect width="100%" height="100%" rx="10" fill="#0d1117" stroke="#30363d"/>
<text x="18" y="18" font-size="11" fill="#8b949e">github.com/{username} · contributions</text>
{''.join(month_labels)}
{''.join(rects)}
{legend}
<text x="18" y="164" class="footer">{footer}</text>
<text x="18" y="179" class="small">Source: public GitHub contributions page · refreshed by GitHub Actions</text>
</svg>"""
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
