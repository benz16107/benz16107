"""Draws hero.svg and hero-dark.svg: an ASCII portrait that types itself in, next to the name and
headline numbers. The README picks one with <picture> to match the viewer's GitHub theme.

Run by hand when the photo or the numbers change. The daily Action does not touch this file.

    uv run -p 3.12 --with pillow --with numpy --with "rembg[cpu]" --with fonttools --with brotli \
        scripts/hero.py PHOTO SWITZER_400.ttf SWITZER_600.ttf

Switzer comes from fontshare.com. Its license does not allow committing the font files, so they stay
out of the repo and the SVG carries only the glyphs it uses.
"""
import base64
import html
import io
import sys
from pathlib import Path

import numpy as np
from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image, ImageOps
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
# thebenzhou.com's paper and ink. The site has no dark theme, so dark swaps paper and ink.
LIGHT = dict(bg="#F2F0EA", ink="#1A1916", ink2="#45423C", ink3="#66625A", line="#CFCABF")
DARK = dict(bg="#1A1916", ink="#F2F0EA", ink2="#CFCABF", ink3="#A29D92", line="#3A3833")

W, H = 960, 420
CROP = (70, 95, 830, 855)  # head and shoulders in the 900x1200 RCVC team portrait
GAMMA = 1.3  # above 1 darkens midtones, so sunlit skin keeps its shading instead of going blank
COLS = 100
PX, PY, PW = 20, 20, 380  # portrait box
RAMP = " .:-=+*#%@"  # sparse to dense

LABEL = "CS · UNIVERSITY OF TORONTO"
NAME = "Ben Zhou"
TAGLINE = ["I build things fast, ship them,", "and keep the ones that work."]
FACTS = [("24", "projects in 2026"), ("15", "hackathon wins"), ("9", "live right now")]
SITE = "thebenzhou.com"


def font_face(family, ttf_path, text, weight=400):
    font = TTFont(ttf_path)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    opts.hinting = False  # hinted glyphs space unevenly when GitHub shrinks the card on a phone
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:'{family}';font-weight:{weight};src:url(data:font/woff2;base64,{b64}) format('woff2')}}"


def tone_grid(photo, cols, cell_ratio):
    """Photo to a cols-wide grid of (tone, subject coverage), both 0..1. cell_ratio is cell height over width."""
    cut = remove(Image.open(photo).convert("RGB")).crop(CROP)
    a = np.asarray(cut.getchannel("A")) > 128
    g = np.asarray(ImageOps.grayscale(cut.convert("RGB")), dtype=np.float32)
    # stretch tones over the subject only, so skin lands light and hair stays dark
    lo, hi = np.percentile(g[a], [3, 97])
    g = np.clip((g - lo) / (hi - lo), 0, 1) ** GAMMA
    g[~a] = 1.0
    rows = round(cols * g.shape[0] / g.shape[1] / cell_ratio)
    bh, bw = g.shape[0] / rows, g.shape[1] / cols
    tone, cover = np.ones((rows, cols)), np.zeros((rows, cols))
    for i in range(rows):
        for j in range(cols):
            ys, xs = slice(int(i * bh), int((i + 1) * bh)), slice(int(j * bw), int((j + 1) * bw))
            blk = g[ys, xs]
            # mostly the block's darker pixels, so thin features (eyes, brows, mouth) survive the shrink
            tone[i, j] = 0.15 * blk.mean() + 0.85 * np.percentile(blk, 10)
            cover[i, j] = a[ys, xs].mean()
    return tone, cover


def ascii_rows(tone, cover, dark):
    """Ink on paper draws dark areas densely. Light on dark draws light areas densely, so the portrait is
    not a negative, and keeps at least a dot on the subject so black hair still has an outline."""
    top = len(RAMP) - 1
    if dark:
        idx = (tone * top + 0.5).astype(int).clip(1, top)
    else:
        idx = ((1 - tone) * top + 0.5).astype(int)
        idx[tone > 0.93] = 0
    idx[cover < 0.5] = 0
    return ["".join(RAMP[i] for i in row) for row in idx]


CELL_W = PW / COLS
CELL_H = CELL_W * 1.875
FS = CELL_W / 0.65  # Martian Mono at 87.5% width advances 0.65em


def render(rows, c, fonts):
    cell_w, cell_h, fs = CELL_W, CELL_H, FS
    ph = len(rows) * cell_h
    py = PY + (H - 2 * PY - ph) / 2

    text_x = PX + PW + 36
    facts_y = 300
    col_w = (W - 24 - text_x) / len(FACTS)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" xml:space="preserve" role="img">',
        f"<title>{NAME}. {html.escape(' '.join(TAGLINE))}</title>",
        "<style>",
        fonts,
        "text{text-rendering:geometricPrecision}",
        ".m{font-family:'Martian Mono',ui-monospace,Menlo,monospace}",
        ".s{font-family:Switzer,ui-sans-serif,system-ui,sans-serif}",
        f".a{{white-space:pre;font-size:{fs:.3f}px;fill:{c['ink']}}}",
        f".c{{animation:k .18s steps({COLS // 4}) var(--d) both}}",
        ".u{animation:u .18s var(--d) both}",
        f"@keyframes k{{to{{transform:translateX({PW + cell_w * 3:.2f}px)}}}}",
        "@keyframes u{0%,100%{opacity:0}1%,99%{opacity:1}}",
        "@media (prefers-reduced-motion:reduce){.c{display:none}}",
        "</style>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="{c['bg']}" stroke="{c['line']}"/>',
        '<g class="m">',
    ]
    for i, row in enumerate(rows):
        y = py + (i + 0.8) * cell_h
        out.append(f'<text class="a" x="{PX}" y="{y:.2f}" textLength="{PW}" lengthAdjust="spacing">{html.escape(row)}</text>')
    # one cover per row slides right to reveal it, with a block cursor riding its left edge.
    # No clipPath: Safari ignores it on animated children, so the cursor hides itself instead.
    for i in range(len(rows)):
        top = py + i * cell_h
        out.append(
            f'<g class="c" style="--d:{0.25 + i * 0.05:.3f}s">'
            f'<rect x="{PX}" y="{top:.2f}" width="{PW}" height="{cell_h + 0.6:.2f}" fill="{c['bg']}"/>'
            f'<rect class="u" x="{PX - cell_w * 1.5:.2f}" y="{top + 0.6:.2f}" width="{cell_w * 1.5:.2f}" height="{cell_h - 0.6:.2f}" fill="{c['ink']}"/></g>'
        )
    out.append("</g>")

    out += [
        f'<text class="m" x="{text_x}" y="74" font-size="15" letter-spacing="1" fill="{c['ink3']}">{html.escape(LABEL)}</text>',
        f'<text class="s" x="{text_x - 3}" y="140" font-size="64" font-weight="600" letter-spacing="-1.5" fill="{c['ink']}">{NAME}</text>',
    ]
    for i, line in enumerate(TAGLINE):
        out.append(f'<text class="s" x="{text_x}" y="{186 + i * 30}" font-size="23" fill="{c['ink2']}">{html.escape(line)}</text>')
    out.append(f'<line x1="{text_x}" y1="{facts_y - 52}" x2="{W - 24}" y2="{facts_y - 52}" stroke="{c['line']}"/>')
    for i, (num, label) in enumerate(FACTS):
        x = text_x + i * col_w
        out.append(f'<text class="s" x="{x - 2}" y="{facts_y}" font-size="44" font-weight="600" letter-spacing="-1" fill="{c['ink']}">{num}</text>')
        out.append(f'<text class="m" x="{x}" y="{facts_y + 28}" font-size="14" fill="{c['ink3']}">{html.escape(label)}</text>')
    out.append(f'<text class="m" x="{W - 24}" y="{H - 30}" font-size="15" text-anchor="end" fill="{c['ink3']}">{SITE}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main(photo, sw400, sw600):
    mono = base64.b64encode((ROOT / "fonts" / "martian-mono.woff2").read_bytes()).decode()
    sans_text = NAME + "".join(TAGLINE) + "".join(n for n, _ in FACTS)
    fonts = "".join([
        f"@font-face{{font-family:'Martian Mono';src:url(data:font/woff2;base64,{mono}) format('woff2')}}",
        font_face("Switzer", sw400, sans_text, 400),
        font_face("Switzer", sw600, sans_text, 600),
    ])
    tone, cover = tone_grid(photo, COLS, CELL_H / CELL_W)
    for name, palette, dark in [("hero.svg", LIGHT, False), ("hero-dark.svg", DARK, True)]:
        rows = ascii_rows(tone, cover, dark)
        (ROOT / name).write_text(render(rows, palette, fonts))
        print(f"{name}: {len(rows)} rows x {COLS} cols, {(ROOT / name).stat().st_size // 1024} KB")


if __name__ == "__main__":
    main(*sys.argv[1:4])
