#!/usr/bin/env python3
"""Render an animated contribution grid SVG for a GitHub user.

Why this exists instead of an off-the-shelf action: Platane/snk queried the
GraphQL API with the workflow's GITHUB_TOKEN, so it read the *bot's*
contributions calendar (empty) and produced a blank grid while reporting
success. This script scrapes the public contributions endpoint that the
profile page itself uses, and fails loudly if the parse looks wrong.

Usage: contribution-grid.py <out_dir> [login]
"""
import datetime as dt
import os
import re
import sys
import urllib.request

CELL = 12
GAP = 3
PAD = 16
DAY_LABEL_W = 30
MONTH_ROW_H = 20
LEGEND_H = 34
DAYS = 7

LIGHT = {
    "bg": "#FFFFFF",
    "empty": "#EBEDF0",
    "levels": ["#FFD7C2", "#FFB28A", "#FF8A52", "#FF5C1F"],
    "text": "#57606A",
    "accent": "#FF5C1F",
    "stroke": "#00000014",
}
DARK = {
    "bg": "#0D0C0A",
    "empty": "#241F1A",
    "levels": ["#5A2A12", "#96421A", "#CC5520", "#FF5C1F"],
    "text": "#A79F90",
    "accent": "#FF5C1F",
    "stroke": "#FFFFFF14",
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fetch(login):
    url = "https://github.com/users/%s/contributions" % login
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (compatible; contribution-grid/1.0)")
    with urllib.request.urlopen(req, timeout=60) as r:
        html = r.read().decode("utf-8", errors="replace")
    # Pair the attributes per <td> element: the page reuses data-level in the
    # legend swatches, so two flat lists do not line up.
    days = {}
    for tag in re.findall(r"<td[^>]*>", html):
        d = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        lv = re.search(r'data-level="(\d)"', tag)
        if d and lv:
            days[dt.date.fromisoformat(d.group(1))] = int(lv.group(1))
    if len(days) < 300:
        raise SystemExit("only %d cells parsed - refusing to publish an empty grid" % len(days))
    return days


def build(days, theme):
    order = sorted(days)
    first = order[0]
    # back up to the Sunday that starts the first column
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    last = order[-1]
    weeks = ((last - start).days // 7) + 1

    grid_w = weeks * (CELL + GAP) - GAP
    width = PAD * 2 + DAY_LABEL_W + grid_w
    height = PAD * 2 + MONTH_ROW_H + DAYS * (CELL + GAP) - GAP + LEGEND_H

    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
               'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" '
               'role="img" aria-label="Contribution activity for the last year">' % (width, height, width, height))
    out.append("<style>"
               ".w{animation:wave 7s ease-in-out infinite}"
               "@keyframes wave{0%%,100%%{opacity:.72}18%%,38%%{opacity:1}}"
               ".lvl{transition:opacity .3s}"
               "@media (prefers-reduced-motion: reduce){.w{animation:none}}"
               "</style>")
    out.append('<rect width="%d" height="%d" fill="%s"/>' % (width, height, theme["bg"]))

    # month labels
    x0 = PAD + DAY_LABEL_W
    y_grid = PAD + MONTH_ROW_H
    seen = set()
    for i in range(weeks):
        d = start + dt.timedelta(days=i * 7)
        if d.month not in seen:
            seen.add(d.month)
            out.append('<text x="%d" y="%d" font-size="11" fill="%s">%s</text>'
                       % (x0 + i * (CELL + GAP), PAD + 13, theme["text"], MONTHS[d.month - 1]))
    # day labels
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append('<text x="%d" y="%d" font-size="10" fill="%s">%s</text>'
                   % (PAD, y_grid + row * (CELL + GAP) + CELL - 2, theme["text"], label))

    # cells, grouped per column so the wave animates across the year
    for i in range(weeks):
        out.append('<g class="w" style="animation-delay:%.2fs">' % (i * 0.055))
        for row in range(DAYS):
            d = start + dt.timedelta(days=i * 7 + row)
            lv = days.get(d)
            if lv is None:
                fill = "none"
            elif lv == 0:
                fill = theme["empty"]
            else:
                fill = theme["levels"][min(lv, 4) - 1]
            if fill == "none":
                continue
            out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2.5" fill="%s" stroke="%s"/>'
                       % (x0 + i * (CELL + GAP), y_grid + row * (CELL + GAP), CELL, CELL, fill, theme["stroke"]))
        out.append("</g>")

    # legend
    ly = height - PAD - CELL
    total = sum(1 for v in days.values() if v > 0)
    out.append('<text x="%d" y="%d" font-size="11" fill="%s">%d active days in the last year</text>'
               % (PAD, ly + CELL - 1, theme["text"], total))
    lx = PAD + DAY_LABEL_W + grid_w - (len(theme["levels"]) + 3) * (CELL + 4)
    out.append('<text x="%d" y="%d" font-size="10" fill="%s">less</text>' % (lx, ly + CELL - 1, theme["text"]))
    lx += 30
    out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2.5" fill="%s"/>' % (lx, ly, CELL, CELL, theme["empty"]))
    for lv, color in enumerate(theme["levels"]):
        lx += CELL + 4
        out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2.5" fill="%s" stroke="%s"/>'
                   % (lx, ly, CELL, CELL, color, theme["stroke"]))
    lx += CELL + 8
    out.append('<text x="%d" y="%d" font-size="10" fill="%s">more</text>' % (lx, ly + CELL - 1, theme["text"]))
    out.append("</svg>")
    return "\n".join(out)


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "dist"
    login = sys.argv[2] if len(sys.argv) > 2 else "Enc48"
    os.makedirs(out_dir, exist_ok=True)
    days = fetch(login)
    active = sum(1 for v in days.values() if v > 0)
    print("parsed %d days (%s .. %s), %d active" % (len(days), min(days), max(days), active))
    for name, theme in (("contributions.svg", LIGHT), ("contributions-dark.svg", DARK)):
        svg = build(days, theme)
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print("wrote %s (%d bytes)" % (path, len(svg.encode())))
    if active == 0:
        raise SystemExit("no active days - nothing worth publishing")


if __name__ == "__main__":
    main()