"""Three number panels in the bone colourway, and the lockup they make together.

85 is the season. It is not the only number worth setting, but the other two do not
come from openfootball: the club's title count and the gap since the last one are
history, not this season's fixture list. They are declared here as constants with
the rule that maintains them, because a number nobody can recompute is exactly the
kind of thing that goes stale and wrong on a page that claims to rebuild itself.

TITLES increments the year the position plate turns gold. SINCE is the year of the
previous title, and the panel does the subtraction.
"""
import os
import sys

from parade import Shaper, N7, FORWARD    # noqa: E402
from system import season, M, INSET, W    # noqa: E402
from colourways import ermine, seme       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import cover  # noqa: E402

RED = "#ef0107"
BONE = "#f2efe6"
L = cover.TABLES["lede"]
N, F = Shaper(N7), Shaper(FORWARD)

TITLES = 14        # league championships won, 1931 to 2026
PREVIOUS = 2004    # the one before this
THIS = 2026


def cell(x, width, height, number, label):
    """One number and its name. Nothing else: a sentence under each was explaining
    a figure that does not need explaining, and three of them in a row read as
    footnotes to something the panel above has already said."""
    body = [seme(x, 0, width, height, RED, 0.10)]
    run, w = N.run(number, 132, 0, height * 0.62, RED)
    body.append(run.replace("translate(0.0", f"translate({x + (width - w) / 2:.1f}"))
    cap, cw = N.run(label, 11, 0, height * 0.62 + 34, RED, tracking=0.26)
    body.append(cap.replace("translate(0.0", f"translate({x + (width - cw) / 2:.1f}"))
    return "".join(body)


def trio(cells, name):
    H, GAP = 232, 2
    width = (W - GAP * 2) / 3
    body = [f'<rect width="{W}" height="{H}" fill="{BONE}"/>']
    for i, (number, label) in enumerate(cells):
        x = i * (width + GAP)
        body.append(cell(x, width, H, number, label))
        if i:
            body.append(f'<rect x="{x - GAP}" y="24" width="1" height="{H - 48}" '
                        f'fill="{RED}" opacity="0.28"/>')
    body += [ermine(M, M, 26, RED), ermine(W - M, M, 26, RED)]
    alt = "  ".join(f"{n} {l.lower()}" for n, l in cells)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" role="img" aria-label="{alt}">'
           f"<title>{alt}</title>{''.join(body)}</svg>\n")
    open(os.path.join(HERE, f"{name}.svg"), "w").write(svg)
    print(f"{name}.svg  {W}x{H}  |  {alt}")


def build():
    s = season()
    clear = s["top"][0][2] - s["top"][1][2]
    # The set: the history, the season, the margin. No opponent is named, because
    # the number is about Arsenal's distance and naming who was behind them makes
    # it about somebody else.
    trio([(str(TITLES), "LEAGUE TITLES"), (str(s["points"]), "POINTS"),
          (str(clear), "CLEAR")], "trio-history")

    open(os.path.join(HERE, "trio.html"), "w").write(
        '<!doctype html><meta charset="utf-8"><style>'
        'body{margin:0;background:#e9e9e9;font:11px/1 -apple-system,sans-serif}'
        '.p{padding:24px 40px;width:900px}.c{margin-bottom:22px}'
        '.c span{display:block;color:#999;text-transform:uppercase;'
        'letter-spacing:.12em;margin-bottom:6px}'
        'img{display:block;width:100%;height:auto}</style>'
        '<div class="p">'
        '<div class="c"><span>the lockup</span><img src="way-bone.svg">'
        '<img src="trio-history.svg" style="margin-top:2px"></div>'
        '<div class="c"><span>the strip alone</span>'
        '<img src="trio-history.svg"></div></div>')
    print("wrote trio.html")


if __name__ == "__main__":
    build()
