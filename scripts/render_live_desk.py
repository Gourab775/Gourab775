#!/usr/bin/env python3
"""Render assets/live-desk.svg from data/contributions.json.
Keeps the 02 mission-deck numbers + bars fresh via daily workflow.
Run by .github/workflows/update-profile-art.yml after fetch_contributions.py.
"""
import json
import os

HERE = os.path.dirname(__file__)
IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "assets", "live-desk.svg")

BAR_COLORS = {
    "low": "#0e4429",
    "mid": "#006d32",
    "high": "#26a641",
    "top": "url(#ld-bar)",
}


def color_for(total, mx):
    r = total / max(mx, 1)
    if r >= 0.7:
        return BAR_COLORS["top"]
    if r >= 0.4:
        return BAR_COLORS["high"]
    if r >= 0.2:
        return BAR_COLORS["mid"]
    return BAR_COLORS["low"]


def main():
    data = json.load(open(IN_PATH, encoding="utf-8"))
    monthly = data["monthly"][-13:]
    mx = max((m["total"] for m in monthly), default=1)
    total = data["total_contributions"]
    cs = data["current_streak"]["length"]
    ls = data["longest_streak"]["length"]
    best = data["best_day"]
    active = data["active_days"]
    avg = data["avg_per_active_day"]
    rng = data["range"]

    bars = []
    base_y = 462
    for i, m in enumerate(monthly):
        t = m["total"]
        h = 12 + (t / max(mx, 1)) * 78
        x = 96 + i * 76
        y = base_y - h
        label = m["month"]  # YYYY-MM
        stroke = "#34D399" if t == mx else "#1E293B"
        bars.append(
            f'<rect class="bar eq" style="animation-delay:{i*0.15:.2f}s" '
            f'x="{x}" y="{y:.1f}" width="56" height="{h:.1f}" rx="6" '
            f'fill="{color_for(t, mx)}" stroke="{stroke}">'
            f"<title>{label}: {t} contributions</title></rect>"
        )
    bars_svg = "\n".join(bars)

    tpl = open(os.path.join(HERE, "live-desk.template.svg"), encoding="utf-8").read() \
        if os.path.exists(os.path.join(HERE, "live-desk.template.svg")) else None
    # Fallback: patch the committed SVG in place (numbers only), keeping animations.
    svg = open(OUT_PATH, encoding="utf-8").read() if os.path.exists(OUT_PATH) else (tpl or "")
    if not svg:
        raise SystemExit("live-desk.svg template not found — commit assets/live-desk.svg first")
    import re
    svg = re.sub(r">[\d,]+</text>\s*\n<text[^>]*>contributions / last year", f">{total:,}</text>\n<text x=\"594\" y=\"172\" class=\"font-mono\" font-size=\"12.5\" fill=\"#94A3B8\">contributions / last year", svg, count=1)
    svg = re.sub(r"Current streak \d+ days", f"Current streak {cs} days", svg)
    svg = re.sub(r"Best day: \d+ contributions", f"Best day: {best['count']} contributions", svg)
    # Rebuild bars block between markers if present, else leave as-is.
    if "<!--BARS-->" in svg:
        svg = re.sub(r"<!--BARS-->.*?<!--/BARS-->", f"<!--BARS-->\n{bars_svg}\n<!--/BARS-->", svg, flags=re.S)
    print(f"deck refresh: total={total} streak={cs} best={best['count']} range={rng['start']}..{rng['end']} active={active} avg={avg}")
    open(OUT_PATH, "w", encoding="utf-8").write(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
