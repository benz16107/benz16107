"""Draws photos.svg and photos-dark.svg: a strip of my photos that scrolls forever, captioned with where each
was taken. The photos are built into the SVG, because GitHub does not load images an SVG links to.

Run by hand from the repo root when the photos change. They come from the portfolio's assets:

    uv run --with pillow python3 scripts/photos.py [~/Code/projects/portfolio-site/assets/photos-sm]
"""
import base64
import html
import io
import sys
from pathlib import Path

from PIL import Image

from stats import DARK, LIGHT, W, font_css

ROOT = Path(__file__).resolve().parent.parent
# (file, caption), all shot on the A7S III; places from the portfolio's photo-meta.js
PHOTOS = [
    ("japan-05.jpg", "Kyoto, Japan"),
    ("select-40.jpg", "Tainan, Taiwan"),
    ("japan-12.jpg", "Lake Yamanaka, Japan"),
    ("select-28.jpg", "Hong Kong"),
    ("photo-study-07.jpg", "Vancouver"),
    ("select-49.jpg", "Kaohsiung, Taiwan"),
    ("japan-19.jpg", "Suwa, Japan"),
    ("select-31.jpg", "Taipei, Taiwan"),
    ("select-37.jpg", "Taichung, Taiwan"),
    ("japan-16.jpg", "Lake Yamanaka, Japan"),
    ("select-44.jpg", "Kaohsiung, Taiwan"),
    ("select-33.jpg", "Taichung, Taiwan"),
]
LABEL, RIGHT = "AWAY FROM THE KEYBOARD", "shot on a Sony A7S III"
H, TOP, PH, GAP, SPEED, EDGE = 250, 68, 140, 12, 28, 24  # PH photo height, SPEED px per second


def data_uri(path):
    """The photo at twice its drawn height, so it stays sharp on a high-density screen."""
    im = Image.open(path).convert("RGB")
    im = im.resize((round(im.width * PH * 2 / im.height), PH * 2), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=70, optimize=True)
    return im.width / 2, "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def render(items, c):
    strip, x = [], 0
    for w, uri, cap in items:
        strip.append(f'<image x="{x:.1f}" y="{TOP}" width="{w:.1f}" height="{PH}" href="{uri}"/>')
        strip.append(f'<text x="{x:.1f}" y="{TOP + PH + 20}" font-size="12" fill="{c["ink3"]}">{html.escape(cap)}</text>')
        x += max(w, len(cap) * 12 * 0.65 + 8) + GAP  # a caption wider than its photo pushes the next one along
    total = x
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">',
        f"<title>My photos, scrolling: {html.escape(', '.join(dict.fromkeys(cap for *_, cap in items)))}</title>",
        f"<style>{font_css()}"
        # two copies side by side slide left by one copy's width, so the loop has no seam
        f".s{{animation:s {total / SPEED:.1f}s linear infinite}}@keyframes s{{to{{transform:translateX({-total:.1f}px)}}}}"
        "@media (prefers-reduced-motion:reduce){.s{animation:none}}</style>",
        "<defs>",
        f'<linearGradient id="l"><stop offset="0" stop-color="{c["bg"]}"/><stop offset="1" stop-color="{c["bg"]}" stop-opacity="0"/></linearGradient>',
        f'<linearGradient id="r"><stop offset="0" stop-color="{c["bg"]}" stop-opacity="0"/><stop offset="1" stop-color="{c["bg"]}"/></linearGradient>',
        f'<g id="strip">{"".join(strip)}</g>',
        "</defs>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="{c["bg"]}"/>',
        f'<g class="s"><use href="#strip" x="{EDGE}"/><use href="#strip" x="{EDGE + total:.1f}"/></g>',
        # no clipPath (Safari drops it on animated children): paper edges and fades cover the strip instead
        f'<rect x="0" y="{TOP - 4}" width="{EDGE}" height="{PH + 36}" fill="{c["bg"]}"/>',
        f'<rect x="{W - EDGE}" y="{TOP - 4}" width="{EDGE}" height="{PH + 36}" fill="{c["bg"]}"/>',
        f'<rect x="{EDGE}" y="{TOP - 4}" width="48" height="{PH + 36}" fill="url(#l)"/>',
        f'<rect x="{W - EDGE - 48}" y="{TOP - 4}" width="48" height="{PH + 36}" fill="url(#r)"/>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="none" stroke="{c["line"]}"/>',
        f'<text x="40" y="44" font-size="15" letter-spacing="1" fill="{c["ink3"]}">{LABEL}</text>',
        f'<text x="{W - 40}" y="44" font-size="15" text-anchor="end" fill="{c["ink3"]}">{RIGHT}</text>',
        "</svg>",
    ]) + "\n"


if __name__ == "__main__":
    src = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "Code/projects/portfolio-site/assets/photos-sm").expanduser()
    items = [(*data_uri(src / name), cap) for name, cap in PHOTOS]
    for suffix, palette in [("", LIGHT), ("-dark", DARK)]:
        (ROOT / f"photos{suffix}.svg").write_text(render(items, palette))
    print(f"photos.svg: {len(items)} photos, {(ROOT / 'photos.svg').stat().st_size // 1024} KB")
