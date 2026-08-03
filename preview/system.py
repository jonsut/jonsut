"""The football callout with a frame around it, not a poster shouting.

The Wimbledon, Premier League and Going references share a discipline the Mainz
posters do not: air. Type is large but it is given room, the panel is bounded by a
hairline, small marks sit in the corners as punctuation, the metadata is pushed
right out to the edges, and the data appears as a diagram drawn in the same two
colours as everything else. Nothing is cropped for effect.

So the parts are fixed and every panel is built from them: a rule, a point mark, an
edge label, a caption, and one thing in the middle that carries the season.

Two colours and a paper: claret ground, gold, bone. One red for accents.
"""
import os
import sys
from datetime import date, timedelta

from parade import Shaper, N7, FORWARD   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_football as bf   # noqa: E402
import cover                  # noqa: E402

W = 900
CLARET = "#3d060c"     # the ground: red taken down until gold can sit on it
RED = "#db0007"
GOLD = "#d8a53a"
BONE = "#f2ece0"
M = 46                 # the margin everything is measured from
INSET = M + 30         # where edge labels start, clear of the corner mark

L = cover.TABLES["lede"]
N, F = Shaper(N7), Shaper(FORWARD)


# ------------------------------------------------------------------- the parts

def rule(y, fill=GOLD, x=M, width=None, opacity=0.5):
    width = W - M * 2 if width is None else width
    return (f'<rect x="{x}" y="{y}" width="{width}" height="1" fill="{fill}" '
            f'opacity="{opacity}"/>')


def point(cx, cy, fill=GOLD, size=4, gap=3):
    """The corner mark. Four squares in a diamond, the way the references use a
    small repeated device as punctuation rather than as a logo."""
    s, g = size, gap + size
    return "".join(
        f'<rect x="{cx + dx - s / 2:.1f}" y="{cy + dy - s / 2:.1f}" '
        f'width="{s}" height="{s}" fill="{fill}"/>'
        for dx, dy in ((0, -g), (0, g), (-g, 0), (g, 0)))


def corners(height, fill=GOLD):
    return "".join(point(x, y, fill) for x in (M, W - M)
                   for y in (M, height - M))


def label(text, x, y, fill=GOLD, size=10, anchor="start"):
    run, _ = N.run(text, size, x, y, fill, tracking=0.26, anchor=anchor)
    return run


def caption(text, y, fill=BONE, size=13):
    width = cover.measure(text, L, size)
    return cover.run(text, L, size, (W - width) / 2, y, fill)


def svg(height, body, alt):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" '
            f'width="{W}" height="{height}" role="img" aria-label="{alt}">'
            f"<title>{alt}</title>"
            f'<rect width="{W}" height="{height}" fill="{CLARET}"/>'
            f"{body}</svg>\n")


# -------------------------------------------------------------------- the data

def season():
    end = date.today() - timedelta(days=1)
    labels = bf.seasons(end)
    league = {label: bf.premier_league(label) for label in labels}
    current = next(label for label in reversed(labels) if league[label])
    matches = league[current]
    ranks, table = bf.table_after(matches, max(m[0] for m in matches))
    ours = sorted(m for m in matches if bf.CLUB in (m[1], m[2]))
    run = []
    for when, home, away, ft in ours:
        us, them = (ft[0], ft[1]) if home == bf.CLUB else (ft[1], ft[0])
        run.append({"date": when, "score": f"{us}-{them}",
                    "against": (away if home == bf.CLUB else home).replace(" FC", ""),
                    "home": home == bf.CLUB,
                    "got": 3 if us > them else 1 if us == them else 0})
    secured = bf.title_secured(matches)
    top = [(ranks[c], c.replace(" FC", ""), table[c][0])
           for c in sorted(ranks, key=ranks.get)[:6]]
    return {"label": current, "short": current[2:4] + "/" + current[-2:],
            "points": table[bf.CLUB][0], "run": run, "top": top,
            "won": sum(1 for m in run if m["got"] == 3),
            "drew": sum(1 for m in run if m["got"] == 1),
            "lost": sum(1 for m in run if m["got"] == 0),
            "secured": secured[0] if secured else None}


# ------------------------------------------------------------------ the panels

def headline(s):
    """1. Two lines, given room. The Wimbledon page, in claret and gold."""
    H = 420
    body = [corners(H), rule(M + 22, width=300), rule(M + 22, x=W - M - 300, width=300),
            point(W / 2, M + 22, BONE, size=5)]
    for i, (text, size) in enumerate((("CHAMPIONS", 118), ("85 POINTS", 118))):
        run, width = N.run(text, size, 0, 202 + i * 108, GOLD, tracking=-0.01)
        body.append(run.replace("translate(0.0", f"translate({(W - width) / 2:.1f}"))
    body += [label("EST", M, H / 2, BONE), label("1886", W - M, H / 2, BONE,
                                                 anchor="end")]
    body.append(caption(f"Arsenal won the {s['label']} Premier League with "
                        f"{s['points']} points, {s['won']} wins and {s['lost']} "
                        "defeats.", H - 78))
    body.append(rule(H - M - 22))
    return H, "".join(body)


def scores(s):
    """2. The run-in as a score list, the way a scoreboard sets a game."""
    H = 560
    last = s["run"][-5:]
    body = [corners(H), label("THE RUN IN", INSET, M + 5),
            label(f"{last[0]['date']:%-d %B} — {last[-1]['date']:%-d %B %Y}".upper(),
                  W - INSET, M + 5, anchor="end")]
    y = 146
    for match in last:
        run, width = N.run(match["score"], 78, M + 10, y, GOLD)
        body.append(run)
        body.append(label(match["against"].upper(), M + 34 + width, y - 6, BONE,
                          size=13))
        body.append(label("HOME" if match["home"] else "AWAY", W - M, y - 6,
                          GOLD, size=11, anchor="end"))
        body.append(rule(y + 20, opacity=0.22))
        y += 82
    body.append(caption(f"Five wins to finish. The title was settled on "
                        f"{s['secured']:%-d %B}.", H - 40))
    return H, "".join(body)


def table(s):
    """3. The diagram: the top of the table as bars, the way the court is drawn."""
    H = 480
    body = [corners(H), label("FINAL TABLE", INSET, M + 5),
            label(s["short"], W - INSET, M + 5, anchor="end")]
    top = s["top"]
    high = max(points for _, _, points in top)
    x, width = M + 4, W - M * 2 - 8
    row, gap = 38, 12
    y = 116
    for rank, club, points in top:
        mine = rank == 1
        length = width * points / high
        body.append(f'<rect x="{x}" y="{y}" width="{length:.1f}" height="{row}" '
                    f'fill="{GOLD if mine else "none"}" '
                    f'stroke="{GOLD}" stroke-opacity="{1 if mine else 0.4}"/>')
        body.append(label(f"{rank}  {club}".upper(), x + 14, y + 25,
                          CLARET if mine else BONE, size=13))
        body.append(label(str(points), W - M - 14, y + 25,
                          CLARET if mine else GOLD, size=13, anchor="end"))
        y += row + gap
    body.append(caption("Seven clear of Manchester City, with the title settled "
                        f"on {s['secured']:%-d %B}.", H - 52))
    return H, "".join(body)


def cropped(s):
    """4. Crop, brought inside the frame: the 85 held by rules rather than bleeding."""
    H = 400
    body = [corners(H), label("ARSENAL", INSET, M + 5),
            label(f"PREMIER LEAGUE {s['short']}", W - INSET, M + 5, anchor="end")]
    number, width = N.run("85", 300, W - M - 4, 306, GOLD, anchor="end")
    body.append(number)
    body.append(rule(H - M - 62, opacity=0.3))
    word, _ = F.run("CHAMPIONS", 76, M, 176, BONE, tracking=-0.015)
    body.append(word)
    body.append(label("POINTS", W - INSET, 344, GOLD, size=11, anchor="end"))
    body.append(cover.run(f"{s['won']} won, {s['drew']} drawn, {s['lost']} lost. "
                          f"Settled on {s['secured']:%-d %B %Y}.", L, 14, M, 218,
                          BONE))
    body.append(label("SEASON IN FULL", M, H - M - 44, GOLD, size=9.5))
    unit = (300 - 2 * 37) / 38
    for i, match in enumerate(s["run"]):
        fill = GOLD if match["got"] == 3 else BONE if match["got"] == 1 else RED
        tall = 22 if match["got"] == 3 else 12 if match["got"] == 1 else 6
        body.append(f'<rect x="{M + i * (unit + 2):.1f}" '
                    f'y="{H - M - 36 + (22 - tall)}" width="{unit:.1f}" '
                    f'height="{tall}" fill="{fill}"/>')
    return H, "".join(body)


def split(s):
    """5. Split, with the seam as a drawn line rather than a collision."""
    H = 400
    CUT = 392
    body = [f'<rect width="{CUT}" height="{H}" fill="{GOLD}"/>',
            f'<rect x="{CUT}" y="0" width="1" height="{H}" fill="{BONE}" '
            'opacity="0.5"/>']
    number, width = N.run("85", 268, 0, 262, CLARET)
    body.append(number.replace("translate(0.0", f"translate({(CUT - width) / 2:.1f}"))
    body.append(label("POINTS", CUT / 2, 306, CLARET, size=11,
                      anchor="middle" if False else "start"))
    pts, pw = N.run("POINTS", 11, 0, 306, CLARET, tracking=0.26)
    body[-1] = pts.replace("translate(0.0", f"translate({(CUT - pw) / 2:.1f}")
    body += [point(M, M, CLARET), point(CUT - M, M, CLARET),
             point(M, H - M, CLARET), point(CUT - M, H - M, CLARET),
             point(W - M, M), point(W - M, H - M)]
    body.append(label("ARSENAL", CUT + M, M + 5))
    body.append(label(s["short"], W - INSET, M + 5, anchor="end"))
    word, _ = F.run("CHAMPIONS", 62, CUT + M, 168, BONE, tracking=-0.015)
    body.append(word)
    body.append(cover.run(f"{s['won']} won, {s['drew']} drawn, {s['lost']} lost.",
                          L, 14, CUT + M, 206, BONE))
    body.append(cover.run(f"Settled on {s['secured']:%-d %B %Y}.", L, 14,
                          CUT + M, 226, BONE))
    body.append(label("SEASON IN FULL", CUT + M, H - M - 44, GOLD, size=9.5))
    unit = (W - CUT - M * 2 - 37 * 2) / 38
    for i, match in enumerate(s["run"]):
        fill = GOLD if match["got"] == 3 else BONE if match["got"] == 1 else RED
        tall = 22 if match["got"] == 3 else 12 if match["got"] == 1 else 6
        body.append(f'<rect x="{CUT + M + i * (unit + 2):.1f}" '
                    f'y="{H - M - 36 + (22 - tall)}" width="{unit:.1f}" '
                    f'height="{tall}" fill="{fill}"/>')
    return H, "".join(body)


def build():
    s = season()
    alt = (f"Arsenal, champions of the {s['label']} Premier League with "
           f"{s['points']} points")
    cards = []
    for name, fn in (("headline", headline), ("scores", scores), ("table", table),
                     ("crop", cropped), ("split", split)):
        height, body = fn(s)
        open(os.path.join(HERE, f"sys-{name}.svg"), "w").write(svg(height, body, alt))
        cards.append(f'<div class="c"><span>{name}</span>'
                     f'<img src="sys-{name}.svg"></div>')
        print(f"sys-{name}.svg  {W}x{height}")
    open(os.path.join(HERE, "system.html"), "w").write(
        '<!doctype html><meta charset="utf-8"><style>'
        'body{margin:0;background:#e9e9e9;font:11px/1 -apple-system,sans-serif}'
        '.p{padding:24px 40px;width:900px}.c{margin-bottom:26px}'
        '.c span{display:block;color:#999;text-transform:uppercase;'
        'letter-spacing:.12em;margin-bottom:6px}'
        'img{display:block;width:100%;height:auto}</style>'
        f'<div class="p">{"".join(cards)}</div>')
    print("wrote system.html")


if __name__ == "__main__":
    build()
