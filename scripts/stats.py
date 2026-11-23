"""Draws stats.svg and stats-dark.svg: commits to public repositories over the last 12 months, by month.
Also draws live.svg and live-dark.svg: whether each live project answered a request just now, with a ring
pulsing out of each one that did.

The daily Action runs this with its own GITHUB_TOKEN, which cannot see private repositories, so
every number here is one anyone can check. Standard library only.

    GITHUB_TOKEN=... python3 scripts/stats.py [login]
"""
import base64
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Same palettes as scripts/hero.py.
LIGHT = dict(bg="#F2F0EA", ink="#1A1916", ink2="#45423C", ink3="#66625A", line="#CFCABF")
DARK = dict(bg="#1A1916", ink="#F2F0EA", ink2="#CFCABF", ink3="#A29D92", line="#3A3833")
W, H = 960, 260
# The README's "Live" section, in the same order.
SITES = [
    ("GurtOS", "https://gurtos.com"),
    ("Pixie", "https://pixie-underwriting.vercel.app"),
    ("UofTime", "https://uoftime.com"),
    ("Keypace", "https://apps.apple.com/app/keypace/id6777376987?mt=12"),
    ("DataFrame", "https://dataframe.space"),
    ("tradex", "https://tradex-six-dun.vercel.app"),
    ("Cracked City", "https://huggingface.co/spaces/crackedcity/app"),
    ("RouteWatch", "https://routewatch-jn559.ondigitalocean.app"),
    ("rcventure.ca", "https://rcventure.ca"),
]


def graphql(query, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        raise SystemExit(f"GitHub API error: {body['errors']}")
    return body["data"]


def month_starts(now):
    """The first instant of each of the last 12 months, oldest first, plus `now` as the end."""
    y, m = now.year, now.month
    starts = []
    for _ in range(12):
        starts.append(datetime(y, m, 1, tzinfo=timezone.utc))
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    return starts[::-1] + [now]


def fetch(login, token, now):
    edges = month_starts(now)
    parts = [
        f'm{i}: contributionsCollection(from: "{a.isoformat()}", to: "{b.isoformat()}") {{ totalCommitContributions }}'
        for i, (a, b) in enumerate(zip(edges, edges[1:]))
    ]
    parts.append(
        f'year: contributionsCollection(from: "{edges[0].isoformat()}", to: "{now.isoformat()}") '
        "{ commitContributionsByRepository(maxRepositories: 100) { repository { isPrivate } } }"
    )
    user = graphql(f'{{ user(login: "{login}") {{ {" ".join(parts)} }} }}', token)["user"]
    months = [(edges[i].strftime("%b"), user[f"m{i}"]["totalCommitContributions"]) for i in range(12)]
    repos = sum(not r["repository"]["isPrivate"] for r in user["year"]["commitContributionsByRepository"])
    return months, repos


def check(url):
    """Seconds until the page answered with a status below 400, or None if it did not."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (profile live check)"})
    t = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            r.read(1)
            return time.perf_counter() - t
    except Exception:
        return None


def render_live(results, now, c):
    mono = base64.b64encode((ROOT / "fonts" / "martian-mono.woff2").read_bytes()).decode()
    up = sum(t is not None for _, t in results)
    h, x0, x1, top, row = 200, 280, W - 40, 96, 36
    col_w = (x1 - x0) / 3
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img">',
        f"<title>{up} of {len(results)} live projects answered on {now:%b} {now.day}, {now.year}</title>",
        f"<style>@font-face{{font-family:'Martian Mono';src:url(data:font/woff2;base64,{mono}) format('woff2')}}"
        "text{font-family:'Martian Mono',ui-monospace,Menlo,monospace;text-rendering:geometricPrecision}"
        # a ring leaves each site that answered, one after another in reading order, every 4 s
        f".p{{fill:none;stroke:{c['ink']};stroke-width:1.5;vector-effect:non-scaling-stroke;opacity:0;"
        "animation:p 4s cubic-bezier(0.23,1,0.32,1) var(--d) infinite}"
        "@keyframes p{0%{transform:scale(1);opacity:.6}30%,100%{transform:scale(2.6);opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.p{display:none}}</style>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="6" fill="{c['bg']}" stroke="{c['line']}"/>',
        f'<text x="40" y="50" font-size="15" letter-spacing="1" fill="{c['ink3']}">LIVE RIGHT NOW</text>',
        f'<text x="{x1}" y="50" font-size="15" text-anchor="end" fill="{c['ink3']}">checked {now:%b} {now.day}, {now:%H:%M} UTC</text>',
        f'<text x="38" y="124" font-size="46" letter-spacing="-2" fill="{c['ink']}">{up}/{len(results)}</text>',
        f'<text x="40" y="150" font-size="16" fill="{c['ink2']}">answered today</text>',
    ]
    for i, (name, t) in enumerate(results):
        x, y = x0 + (i % 3) * col_w, top + (i // 3) * row
        dot = c["ink"] if t is not None else c["bg"]
        out.append(f'<circle cx="{x + 5}" cy="{y - 5}" r="5" fill="{dot}" stroke="{c['ink']}" stroke-width="1.5"/>')
        if t is not None:  # centred on the group's origin, so scale() grows the ring from the dot in every browser
            out.append(f'<g transform="translate({x + 5} {y - 5})"><circle class="p" r="5" style="--d:{0.6 + i * 0.12:.2f}s"/></g>')
        out.append(f'<text x="{x + 20}" y="{y}" font-size="15" fill="{c['ink'] if t is not None else c['ink3']}">{name}</text>')
        note = f"{t:.1f}s" if t is not None else "down"
        out.append(f'<text x="{x + col_w - 28}" y="{y}" font-size="13" text-anchor="end" fill="{c['ink3']}">{note}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def render(months, repos, now, c):
    mono = base64.b64encode((ROOT / "fonts" / "martian-mono.woff2").read_bytes()).decode()
    total = sum(n for _, n in months)
    peak = max(n for _, n in months) or 1
    x0, x1, base, top = 330, W - 40, 196, 96
    slot = (x1 - x0) / len(months)
    bar_w = slot * 0.6

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">',
        f"<title>{total:,} commits to {repos} public repositories in the last 12 months</title>",
        f"<style>@font-face{{font-family:'Martian Mono';src:url(data:font/woff2;base64,{mono}) format('woff2')}}"
        "text{font-family:'Martian Mono',ui-monospace,Menlo,monospace;text-rendering:geometricPrecision}</style>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="{c['bg']}" stroke="{c['line']}"/>',
        f'<text x="40" y="50" font-size="15" letter-spacing="1" fill="{c['ink3']}">PUBLIC GITHUB · LAST 12 MONTHS</text>',
        f'<text x="38" y="114" font-size="46" letter-spacing="-2" fill="{c['ink']}">{total:,}</text>',
        f'<text x="40" y="140" font-size="16" fill="{c['ink2']}">commits</text>',
        f'<text x="38" y="196" font-size="30" letter-spacing="-1" fill="{c['ink']}">{repos}</text>',
        f'<text x="40" y="220" font-size="16" fill="{c['ink2']}">public repositories</text>',
        f'<text x="{x1}" y="50" font-size="15" text-anchor="end" fill="{c['ink3']}">updated {now:%b} {now.day}, {now.year}</text>',
        f'<line x1="{x0}" y1="{base + 0.5}" x2="{x1}" y2="{base + 0.5}" stroke="{c['line']}"/>',
    ]
    for i, (label, n) in enumerate(months):
        cx = x0 + slot * (i + 0.5)
        h = (base - top) * n / peak
        if n:
            out.append(f'<rect x="{cx - bar_w / 2:.1f}" y="{base - h:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="{c['ink']}"/>')
        if n == peak:
            out.append(f'<text x="{cx:.1f}" y="{base - h - 8:.1f}" font-size="15" text-anchor="middle" fill="{c['ink']}">{n:,}</text>')
        out.append(f'<text x="{cx:.1f}" y="{base + 24}" font-size="14" text-anchor="middle" fill="{c['ink3']}">{label}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    login = sys.argv[1] if len(sys.argv) > 1 else "benz16107"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    months, repos = fetch(login, os.environ["GITHUB_TOKEN"], now)
    assert len(months) == 12 and all(n >= 0 for _, n in months), months
    (ROOT / "stats.svg").write_text(render(months, repos, now, LIGHT))
    (ROOT / "stats-dark.svg").write_text(render(months, repos, now, DARK))
    print(f"stats.svg: {sum(n for _, n in months):,} commits, {repos} repos", months)
    results = [(name, check(url)) for name, url in SITES]
    # every site down at once means the runner lost its network, not that the sites fell over
    assert any(t is not None for _, t in results), results
    (ROOT / "live.svg").write_text(render_live(results, now, LIGHT))
    (ROOT / "live-dark.svg").write_text(render_live(results, now, DARK))
    print("live.svg:", results)
