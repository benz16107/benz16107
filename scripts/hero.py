"""Draws hero.svg: an ASCII portrait that types itself in, next to the name and headline numbers.

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
PAPER, SURFACE, INK, INK2, INK3, LINE = "#F2F0EA", "#FBFAF7", "#1A1916", "#45423C", "#66625A", "#CFCABF"

W, H = 960, 420
CROP = (330, 130, 1170, 970)  # head and shoulders in the 1500x2000 Cal Hacks headshot
COLS = 100
PX, PY, PW = 20, 20, 380  # portrait box
RAMP = " .:-=+*#%@"  # light to dark; a white background becomes spaces

LABEL = "CS · UNIVERSITY OF TORONTO"
NAME = "Ben Zhou"
TAGLINE = ["I build things fast, ship them,", "and keep the ones that work."]
FACTS = [("22", "projects in 2026"), ("14", "hackathon wins"), ("9", "live right now")]
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


def ascii_rows(photo, cols, cell_ratio):
    """Photo to rows of ramp characters. cell_ratio is character cell height over width."""
    cut = remove(Image.open(photo).convert("RGB")).crop(CROP)
    a = np.asarray(cut.getchannel("A")) > 128
    g = np.asarray(ImageOps.grayscale(cut.convert("RGB")), dtype=np.float32)
    # stretch tones over the subject only, so skin lands light and hair stays dark
    lo, hi = np.percentile(g[a], [3, 97])
    g = np.clip((g - lo) / (hi - lo), 0, 1) ** 0.8
    g[~a] = 1.0
    rows = round(cols * g.shape[0] / g.shape[1] / cell_ratio)
    bh, bw = g.shape[0] / rows, g.shape[1] / cols
    small = np.ones((rows, cols))
    for i in range(rows):
        for j in range(cols):
            blk = g[int(i * bh):int((i + 1) * bh), int(j * bw):int((j + 1) * bw)]
            # mostly the block's darker pixels, so thin features (eyes, brows, mouth) survive the shrink
            small[i, j] = 0.15 * blk.mean() + 0.85 * np.percentile(blk, 10)
    idx = ((1 - small) * (len(RAMP) - 1) + 0.5).astype(int)
    idx[small > 0.93] = 0
    return ["".join(RAMP[i] for i in row) for row in idx]


def main(photo, sw400, sw600):
    mono = ROOT / "fonts" / "martian-mono.woff2"
    cell_w = PW / COLS
    fs = cell_w / 0.65  # Martian Mono at 87.5% width advances 0.65em
    cell_h = cell_w * 1.875
    rows = ascii_rows(photo, COLS, cell_h / cell_w)
    ph = len(rows) * cell_h
    py = PY + (H - 2 * PY - ph) / 2

    text_x = PX + PW + 36
    facts_y = 300
    col_w = (W - 24 - text_x) / len(FACTS)
    sans_text = NAME + "".join(TAGLINE) + "".join(n for n, _ in FACTS)
    mono_b64 = base64.b64encode(mono.read_bytes()).decode()

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" xml:space="preserve" role="img">',
        f"<title>{NAME}. {html.escape(' '.join(TAGLINE))}</title>",
        "<style>",
        f"@font-face{{font-family:'Martian Mono';src:url(data:font/woff2;base64,{mono_b64}) format('woff2')}}",
        font_face("Switzer", sw400, sans_text, 400),
        font_face("Switzer", sw600, sans_text, 600),
        "text{text-rendering:geometricPrecision}",
        ".m{font-family:'Martian Mono',ui-monospace,Menlo,monospace}",
        ".s{font-family:Switzer,ui-sans-serif,system-ui,sans-serif}",
        f".a{{white-space:pre;font-size:{fs:.3f}px;fill:{INK}}}",
        f".c{{animation:k .18s steps({COLS // 4}) var(--d) both}}",
        ".u{animation:u .18s var(--d) both}",
        f"@keyframes k{{to{{transform:translateX({PW + cell_w * 3:.2f}px)}}}}",
        "@keyframes u{0%,100%{opacity:0}1%,99%{opacity:1}}",
        "@media (prefers-reduced-motion:reduce){.c{display:none}}",
        "</style>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="{PAPER}" stroke="{LINE}"/>',
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
            f'<rect x="{PX}" y="{top:.2f}" width="{PW}" height="{cell_h + 0.6:.2f}" fill="{PAPER}"/>'
            f'<rect class="u" x="{PX - cell_w * 1.5:.2f}" y="{top + 0.6:.2f}" width="{cell_w * 1.5:.2f}" height="{cell_h - 0.6:.2f}" fill="{INK}"/></g>'
        )
    out.append("</g>")

    out += [
        f'<text class="m" x="{text_x}" y="74" font-size="15" letter-spacing="1" fill="{INK3}">{html.escape(LABEL)}</text>',
        f'<text class="s" x="{text_x - 3}" y="140" font-size="64" font-weight="600" letter-spacing="-1.5" fill="{INK}">{NAME}</text>',
    ]
    for i, line in enumerate(TAGLINE):
        out.append(f'<text class="s" x="{text_x}" y="{186 + i * 30}" font-size="23" fill="{INK2}">{html.escape(line)}</text>')
    out.append(f'<line x1="{text_x}" y1="{facts_y - 52}" x2="{W - 24}" y2="{facts_y - 52}" stroke="{LINE}"/>')
    for i, (num, label) in enumerate(FACTS):
        x = text_x + i * col_w
        out.append(f'<text class="s" x="{x - 2}" y="{facts_y}" font-size="44" font-weight="600" letter-spacing="-1" fill="{INK}">{num}</text>')
        out.append(f'<text class="m" x="{x}" y="{facts_y + 28}" font-size="14" fill="{INK3}">{html.escape(label)}</text>')
    out.append(f'<text class="m" x="{W - 24}" y="{H - 30}" font-size="15" text-anchor="end" fill="{INK3}">{SITE}</text>')
    out.append("</svg>")
    (ROOT / "hero.svg").write_text("\n".join(out) + "\n")
    print(f"hero.svg: {len(rows)} rows x {COLS} cols, {(ROOT / 'hero.svg').stat().st_size // 1024} KB")


if __name__ == "__main__":
    main(*sys.argv[1:4])
