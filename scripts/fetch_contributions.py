#!/usr/bin/env python3
"""Fetch contribution cells from GitHub's public contributions HTML page."""
from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "contributions.json"
USERNAME = os.getenv("GITHUB_USERNAME", "dusssi")
URL = f"https://github.com/users/{USERNAME}/contributions"


def main() -> None:
    response = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; profile-art-generator/1.0)"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    days = []

    for cell in soup.select("[data-date][data-level]"):
        try:
            day = date.fromisoformat(cell.get("data-date", ""))
        except ValueError:
            continue
        try:
            level = max(0, min(4, int(cell.get("data-level", "0"))))
        except ValueError:
            level = 0

        label = " ".join([
            cell.get("aria-label", ""),
            cell.get("data-tip", ""),
            cell.get("title", ""),
        ])
        match = re.search(r"([\d,]+)\s+contributions?", label, re.I)
        if match:
            count = int(match.group(1).replace(",", ""))
        elif re.search(r"no contributions?", label, re.I):
            count = 0
        else:
            count = None
        days.append({"date": day.isoformat(), "level": level, "count": count})

    if not days:
        raise RuntimeError(
            "No contribution cells found. GitHub may have changed its HTML or "
            "the profile may be unavailable. No output was overwritten."
        )

    days.sort(key=lambda item: item["date"])
    known = [item for item in days if item["count"] is not None]
    total = sum(item["count"] or 0 for item in known) if known else None
    best = max(known, key=lambda item: item["count"] or 0) if known else None

    active_dates = {
        date.fromisoformat(item["date"])
        for item in days
        if (item["count"] is not None and item["count"] > 0)
        or (item["count"] is None and item["level"] > 0)
    }

    current = 0
    cursor = date.today()
    # GitHub's newest cell may be today or yesterday depending on refresh timing.
    if cursor not in active_dates and cursor - timedelta(days=1) in active_dates:
        cursor -= timedelta(days=1)
    while cursor in active_dates:
        current += 1
        cursor -= timedelta(days=1)

    longest, streak, previous = 0, 0, None
    for item in days:
        day = date.fromisoformat(item["date"])
        if day in active_dates:
            streak = streak + 1 if previous and day == previous + timedelta(days=1) else 1
            longest = max(longest, streak)
        else:
            streak = 0
        previous = day

    monthly = defaultdict(int)
    for item in known:
        monthly[item["date"][:7]] += item["count"] or 0

    payload = {
        "username": USERNAME,
        "source": URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": {
            "contributions_visible_calendar": total,
            "current_streak_days_estimate": current,
            "longest_streak_days_estimate": longest,
            "best_day": best,
            "monthly_totals": dict(sorted(monthly.items())),
            "counts_available": bool(known),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved {len(days)} contribution days for @{USERNAME} to {OUT}")


if __name__ == "__main__":
    main()
