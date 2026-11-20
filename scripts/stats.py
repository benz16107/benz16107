"""Draws stats.svg and stats-dark.svg: commits to public repositories over the last 12 months, by month.

The daily Action runs this with its own GITHUB_TOKEN, which cannot see private repositories, so
every number here is one anyone can check. Standard library only.

    GITHUB_TOKEN=... python3 scripts/stats.py [login]
"""
import base64
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Same palettes as scripts/hero.py.
LIGHT = dict(bg="#F2F0EA", ink="#1A1916", ink2="#45423C", ink3="#66625A", line="#CFCABF")
DARK = dict(bg="#1A1916", ink="#F2F0EA", ink2="#CFCABF", ink3="#A29D92", line="#3A3833")
W, H = 960, 260


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
