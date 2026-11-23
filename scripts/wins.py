"""Draws wins.svg and wins-dark.svg: hackathon prizes with a public write-up, stacked by month, and prints the
README table that sits under the card. Run by hand after a hackathon; prizes as thebenzhou.com lists them.

    python3 scripts/wins.py
"""
from pathlib import Path

from stats import DARK, LIGHT, W, font_css

ROOT = Path(__file__).resolve().parent.parent
TOTAL = 15  # every win, including the ones with no public write-up
# (month, hackathon, project, prizes, Devpost), oldest first
WINS = [
    (2, "Mac-a-thon", "BlindSpot", ["MLH Best Use of ElevenLabs", "Best Use of Backboard.io (GitCloud)"], "https://devpost.com/software/blindspot-zs7dwq"),
    (3, "Hack Days in the 6ix", "Packwise", ["Runner up"], "https://devpost.com/software/packwise-jmgtqi"),
    (3, "GenAI Genesis", "Eco-Pulse", ["Top 2 teams, online"], "https://devpost.com/software/eco-pulse-fpbo15"),
    (3, "McGill AeroHacks", "OOPS", ["Best Use of MongoDB Atlas"], "https://devpost.com/software/skygrid"),
    (7, "cuHacking7", "tradex", ["MLH Best Use of Solana"], "https://devpost.com/software/tradex-0efat7"),
    (9, "Hack the North 2026", "Pixie", ["Intact track", "Federato track"], "https://devpost.com/software/pixie-8vlj7g"),
    (10, "Cal Hacks 13.0", "GurtOS", ["Atlassian prize", "Fetch.ai special recognition prize", "MLH Best Use of Solana"], "https://devpost.com/software/gurtos"),
    (11, "HackUTD 2026", "Tessera", ["Spacetime track, 2nd place"], "https://devpost.com/software/bean-4970h3"),
]
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def render(c):
    h, x0, x1, base, block, gap = 260, 330, W - 40, 196, 26, 5
    slot = (x1 - x0) / 12
    prizes = sum(len(p) for *_, p, _ in WINS)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img">',
        f"<title>{prizes} hackathon prizes with a public write-up from {len(WINS)} hackathons in 2026, by month</title>",
        f"<style>{font_css()}"
        # each prize drops onto its month's stack once, oldest first; the newest one then blinks
        ".k{animation:k .5s cubic-bezier(0.23,1,0.32,1) var(--d) both}@keyframes k{from{transform:translateY(-14px);opacity:0}}"
        ".z{animation:z 1.1s steps(1) var(--d) infinite}@keyframes z{50%{opacity:.25}}"
        "@media (prefers-reduced-motion:reduce){.k,.z{animation:none}}</style>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="6" fill="{c['bg']}" stroke="{c['line']}"/>',
        f'<text x="40" y="50" font-size="15" letter-spacing="1" fill="{c['ink3']}">HACKATHON PRIZES · 2026</text>',
        f'<text x="{x1}" y="50" font-size="15" text-anchor="end" fill="{c['ink3']}">{TOTAL} wins, {prizes} written up</text>',
        f'<text x="38" y="114" font-size="46" letter-spacing="-2" fill="{c['ink']}">{prizes}</text>',
        f'<text x="40" y="140" font-size="16" fill="{c['ink2']}">prizes</text>',
        f'<text x="38" y="196" font-size="30" letter-spacing="-1" fill="{c['ink']}">{len(WINS)}</text>',
        f'<text x="40" y="220" font-size="16" fill="{c['ink2']}">hackathons</text>',
        f'<line x1="{x0}" y1="{base + 0.5}" x2="{x1}" y2="{base + 0.5}" stroke="{c['line']}"/>',
    ]
    height = [0] * 12
    n = 0
    for month, *_, names, _ in WINS:
        for _ in names:
            cx = x0 + slot * (month - 0.5)
            y = base - gap - height[month - 1] * (block + gap) - block
            height[month - 1] += 1
            last = n == prizes - 1
            d = 0.3 + n * 0.09
            cls = f'class="k" style="--d:{d:.2f}s"'
            rect = f'<rect x="{cx - block / 2:.1f}" y="{y}" width="{block}" height="{block}" fill="{c['ink']}"/>'
            if last:  # the blink sits on a wrapper, so it never fights the drop for opacity
                rect = f'<g class="z" style="--d:{d + 0.8:.2f}s">{rect}</g>'
            out.append(f"<g {cls}>{rect}</g>")
            n += 1
    for i, label in enumerate(MONTHS):
        cx = x0 + slot * (i + 0.5)
        out.append(f'<text x="{cx:.1f}" y="{base + 24}" font-size="14" text-anchor="middle" fill="{c['ink'] if height[i] else c['ink3']}">{label}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def table():
    rows = ["| When | Hackathon | Project | Prize |", "|---|---|---|---|"]
    for month, event, project, names, devpost in reversed(WINS):
        rows.append(f"| {MONTHS[month - 1]} 2026 | {event} | [{project}]({devpost}) | {'<br>'.join(names)} |")
    return "\n".join(rows)


if __name__ == "__main__":
    assert sum(len(p) for *_, p, _ in WINS) <= TOTAL
    (ROOT / "wins.svg").write_text(render(LIGHT))
    (ROOT / "wins-dark.svg").write_text(render(DARK))
    print(table())
