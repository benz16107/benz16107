"""Draws map.svg and map-dark.svg: an ASCII map of North America with a mark on every city where I competed
at a hackathon this year. Run by hand after each hackathon, once it is added to HACKATHONS.

    uv run -p 3.12 --with pillow scripts/map.py [GEOJSON_DIR]

Land and lakes are Natural Earth 1:50m (public domain), downloaded on each run unless GEOJSON_DIR
already holds both files.
"""
import base64
import html
import json
import math
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
# Same palettes as scripts/hero.py, plus `dim` for the land.
LIGHT = dict(bg="#F2F0EA", ink="#1A1916", ink2="#45423C", ink3="#66625A", line="#CFCABF", dim="#ADA89C")
DARK = dict(bg="#1A1916", ink="#F2F0EA", ink2="#CFCABF", ink3="#A29D92", line="#3A3833", dim="#5C5951")

W, H = 960, 420
YEAR = 2026
# (event, city, lon, lat, won a prize). Prizes as thebenzhou.com lists them.
HACKATHONS = [
    ("Mac-a-thon", "Hamilton", -79.92, 43.26, True),
    ("DeerHacks V", "Mississauga", -79.66, 43.55, False),
    ("Hack Days in the 6ix", "Toronto", -79.38, 43.65, True),
    ("GenAI Genesis", "Toronto", -79.38, 43.65, True),
    ("McGill AeroHacks", "Montreal", -73.58, 45.50, True),
    ("SOON", "Goodwood", -79.18, 44.03, False),
    ("Sandcastle", "Toronto", -79.38, 43.65, False),
    ("cuHacking7", "Ottawa", -75.70, 45.39, True),
    ("Hack the North", "Waterloo", -80.54, 43.47, True),
    ("Cal Hacks 13.0", "San Francisco", -122.40, 37.78, True),
    ("HackUTD", "Dallas", -96.75, 32.99, True),
    ("HackPrinceton", "Princeton", -74.66, 40.35, False),
]
# Cities around Toronto sit within a few cells of each other, so they share one label block.
CLUSTER = {"Toronto", "Mississauga", "Hamilton", "Waterloo", "Goodwood"}

FS = 11  # map glyph size; Martian Mono at 87.5% width advances 0.65em
CELL_W = FS * 0.65
CELL_H = CELL_W * 1.875
MARGIN = 14
COLS = int((W - 2 * MARGIN) / CELL_W)
ROWS = int((H - 2 * MARGIN) / CELL_H)
WINDOW = (-124, -58, 24, 52)  # lon and lat range the card frames


def albers(lon, lat, lon0=-96, lat0=23, lat1=29.5, lat2=45.5):
    """Albers equal-area conic, the projection of most US maps. Returns unscaled x, y with y up."""
    f = math.radians
    n = (math.sin(f(lat1)) + math.sin(f(lat2))) / 2
    c = math.cos(f(lat1)) ** 2 + 2 * n * math.sin(f(lat1))
    rho0 = math.sqrt(c - 2 * n * math.sin(f(lat0))) / n
    rho = math.sqrt(c - 2 * n * math.sin(f(lat))) / n
    t = n * f(lon - lon0)
    return rho * math.sin(t), rho0 - rho * math.cos(t)


def frame():
    """Scale and offset that fit WINDOW across the card. Returns a lon, lat -> card px function."""
    lo0, lo1, la0, la1 = WINDOW
    edge = [albers(lo, la) for lo in range(lo0, lo1 + 1) for la in (la0, la1)]
    edge += [albers(lo, la) for la in range(la0, la1 + 1) for lo in (lo0, lo1)]
    xs, ys = [p[0] for p in edge], [p[1] for p in edge]
    k = (W - 2 * MARGIN) / (max(xs) - min(xs))
    cy = (max(ys) + min(ys)) / 2
    return lambda lon, lat: (MARGIN + (albers(lon, lat)[0] - min(xs)) * k, H / 2 - (albers(lon, lat)[1] - cy) * k)


def geojson(name, src):
    path = Path(src or "/nonexistent") / f"ne_50m_{name}.geojson"
    if path.exists():
        return json.loads(path.read_text())["features"]
    url = f"https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_{name}.geojson"
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)["features"]


def rings(feature):
    """A feature's polygons, each a list of rings, whether it is a Polygon or a MultiPolygon."""
    g = feature["geometry"]
    return [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]


def cell_grid(src, to_px):
    """Land coverage per glyph cell, 0 to 1, from a mask drawn at 4x the card size."""
    s = 4
    px = lambda ring: [(x * s, y * s) for x, y in (to_px(lo, la) for lo, la in ring)]
    land = Image.new("L", (W * s, H * s))
    d = ImageDraw.Draw(land)
    for f in geojson("land", src):
        for poly in rings(f):
            d.polygon(px(poly[0]), fill=255)
            for hole in poly[1:]:
                d.polygon(px(hole), fill=0)
    for f in geojson("lakes", src):
        for poly in rings(f):
            d.polygon(px(poly[0]), fill=0)
    box = (MARGIN * s, MARGIN * s, int((MARGIN + COLS * CELL_W) * s), int((MARGIN + ROWS * CELL_H) * s))
    cover = land.crop(box).resize((COLS, ROWS), Image.BOX)
    return [[cover.getpixel((j, i)) / 255 for j in range(COLS)] for i in range(ROWS)]


def map_rows(cover):
    """Two layers of glyph rows: the coast, any land cell touching water, and the land inside it."""
    land = [[c > 0.35 for c in row] for row in cover]
    wet = lambda i, j: 0 <= i < ROWS and 0 <= j < COLS and not land[i][j]  # the card edge is not a coast
    coast = [[land[i][j] and any(wet(i + a, j + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
              for j in range(COLS)] for i in range(ROWS)]
    inner = ["".join(":" if land[i][j] and not coast[i][j] else " " for j in range(COLS)) for i in range(ROWS)]
    edge = ["".join(":" if coast[i][j] else " " for j in range(COLS)) for i in range(ROWS)]
    return inner, edge


def label(x, y, text, c, fs=13, anchor="start", fill=None, pad=3):
    """Text on a background plate so it stays readable over the land."""
    w = len(text) * fs * 0.65
    x0 = x if anchor == "start" else x - w
    return (f'<rect x="{x0 - pad:.1f}" y="{y - fs * 0.85:.1f}" width="{w + 2 * pad:.1f}" height="{fs * 1.2:.1f}" fill="{c['bg']}"/>'
            f'<text x="{x0:.1f}" y="{y:.1f}" font-size="{fs}" fill="{fill or c['ink']}">{html.escape(text)}</text>')


def marker(x, y, won, c, r=4.5):
    fill = c["ink"] if won else c["bg"]
    return f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}" fill="{fill}" stroke="{c['ink']}" stroke-width="1.5"/>'


# Where each city's label sits relative to its marker: (dx, dy, anchor).
PLACE = {
    "San Francisco": (12, 4, "start"),
    "Dallas": (12, 4, "start"),
    "Princeton": (12, 10, "start"),
    "Montreal": (12, 4, "start"),
    "Ottawa": (-4, -14, "end"),
}


def render(rows, to_px, c):
    mono = base64.b64encode((ROOT / "fonts" / "martian-mono.woff2").read_bytes()).decode()
    cities = {}
    for event, city, lon, lat, won in HACKATHONS:
        e = cities.setdefault(city, dict(pos=to_px(lon, lat), won=False, events=[]))
        e["won"] |= won
        e["events"].append(event)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" xml:space="preserve" role="img">',
        f"<title>Hackathons I competed at in {YEAR}: {html.escape(', '.join(f'{e} in {ci}' for e, ci, *_ in HACKATHONS))}</title>",
        f"<style>@font-face{{font-family:'Martian Mono';src:url(data:font/woff2;base64,{mono}) format('woff2')}}"
        "text{font-family:'Martian Mono',ui-monospace,Menlo,monospace;text-rendering:geometricPrecision;white-space:pre}</style>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="{c['bg']}" stroke="{c['line']}"/>',
    ]
    for layer, fill in zip(rows, (c["dim"], c["ink3"])):
        out.append(f'<g font-size="{FS}" fill="{fill}">')
        for i, row in enumerate(layer):
            if row.strip():
                y = MARGIN + (i + 0.8) * CELL_H
                out.append(f'<text x="{MARGIN}" y="{y:.2f}" textLength="{COLS * CELL_W:.2f}" lengthAdjust="spacing">{html.escape(row)}</text>')
        out.append("</g>")

    cluster = [ci for ci in cities if ci in CLUSTER]
    for ci, e in cities.items():
        if ci in CLUSTER:
            continue
        out.append(marker(*e["pos"], e["won"], c))
        if ci in PLACE:
            dx, dy, anchor = PLACE[ci]
            x, y = e["pos"]
            out.append(label(x + dx, y + dy, " · ".join(e["events"]), c, anchor=anchor))
    if cluster:
        # one ring on the map, and the events listed in the open Atlantic with their own markers
        cx = sum(cities[ci]["pos"][0] for ci in cluster) / len(cluster)
        cy = sum(cities[ci]["pos"][1] for ci in cluster) / len(cluster)
        rows_ = [(ev, ci, won) for ev, ci, *_, won in HACKATHONS if ci in CLUSTER]
        bx, by = W - 262, H - 26 - len(rows_) * 18
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="13" fill="none" stroke="{c['ink']}" stroke-width="1.5"/>')
        out.append(f'<path d="M{cx + 9:.1f} {cy + 10:.1f} L{bx - 10:.1f} {by - 24:.1f}" stroke="{c['ink3']}" fill="none"/>')
        out.append(label(bx - 2, by - 20, "TORONTO AREA", c, fs=12, fill=c["ink3"]))
        for k, (ev, ci, won) in enumerate(rows_):
            y = by + k * 18
            out.append(marker(bx + 2, y - 4, won, c, r=3.5) + label(bx + 12, y, f"{ev} · {ci}", c, fs=12))

    out.append(label(40, 50, f"HACKATHONS · {YEAR}", c, fs=15, fill=c["ink3"]))
    out.append(marker(46, H - 44, True, c) + label(60, H - 39, "won a prize", c, fs=13, fill=c["ink3"]))
    out.append(marker(186, H - 44, False, c) + label(200, H - 39, "competed", c, fs=13, fill=c["ink3"]))
    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else None
    to_px = frame()
    rows = map_rows(cell_grid(src, to_px))
    assert sum(r.count(":") for r in rows[0]) > COLS * ROWS * 0.2, "the land mask came out nearly empty"
    for name, palette in [("map.svg", LIGHT), ("map-dark.svg", DARK)]:
        (ROOT / name).write_text(render(rows, to_px, palette))
        print(f"{name}: {ROWS} rows x {COLS} cols, {(ROOT / name).stat().st_size // 1024} KB")
