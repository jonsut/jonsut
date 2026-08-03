"""Five graphical marks for the football callout. Flat colour, no gradients.

The references share one idea: type at a size the frame cannot hold, in two flat
colours, with a hard-edged graphic doing the structural work. Nothing is shaded,
nothing glows, and the only shapes are ones a screen printer could cut.

So: one red, one gold, one bone, and 85 set in Northbank as a piece of
architecture rather than a number sitting on a background.

The season is in every panel. Thirty-eight matches, in order, as bars, stripes or
a band: gold won, bone drew, deep red lost.
"""
import os
import sys
from datetime import date, timedelta

from parade import Shaper, season, N7, FORWARD   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import cover  # noqa: E402

W = 900
RED = "#db0007"      # the shirt, one shade off the official red so it holds ink
GOLD = "#d8a53a"     # flat leaf, no gradient
BONE = "#f2ece0"
DEEP = "#7a0510"     # the losses, and the shadow side of a split field

L = cover.TABLES["lede"]
N, F = Shaper(N7), Shaper(FORWARD)


def svg(height, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" '
            f'width="{W}" height="{height}" role="img" aria-label="{label}">'
            f"<title>{label}</title>"
            f'<defs><clipPath id="f"><rect width="{W}" height="{height}"/>'
            f"</clipPath></defs>"
            f'<g clip-path="url(#f)">{body}</g></svg>\n')


def strip(results, x, y, width, height, gap=3, colours=None):
    """The season as bars, in the order they were played."""
    gold, bone, deep = colours or (GOLD, BONE, DEEP)
    unit = (width - gap * (len(results) - 1)) / len(results)
    out = []
    for i, got in enumerate(results):
        fill = gold if got > 0 else bone if got == 0 else deep
        tall = height if got > 0 else height * 0.5 if got == 0 else height * 0.22
        out.append(f'<rect x="{x + i * (unit + gap):.1f}" y="{y + height - tall:.1f}" '
                   f'width="{unit:.1f}" height="{tall:.1f}" fill="{fill}"/>')
    return "".join(out)


def slashes(results, x, y, width, height, lean=26):
    """The same record as a hatch, the way a poster rules off a block of colour."""
    unit = width / len(results)
    out = []
    for i, got in enumerate(results):
        fill = GOLD if got > 0 else BONE if got == 0 else DEEP
        left = x + i * unit
        out.append(f'<path d="M{left + lean:.1f} {y} L{left + lean + unit * 0.62:.1f} '
                   f'{y} L{left + unit * 0.62:.1f} {y + height} L{left:.1f} '
                   f'{y + height}Z" fill="{fill}"/>')
    return "".join(out)


def micro(text, x, y, fill=BONE, size=11, tracking=0.24, anchor="start"):
    run, _ = N.run(text, size, x, y, fill, tracking=tracking, anchor=anchor)
    return run


# --------------------------------------------------------------------- the five

def crop(s):
    """1. The number as architecture: 85 too big for the frame, cropped by it."""
    H = 360
    body = [f'<rect width="{W}" height="{H}" fill="{RED}"/>']
    # Set from the right and allowed to run off. Losing the outer stroke of the 5
    # is the point: the number reads as a thing in the room rather than a figure.
    number, width = N.run("85", 470, 0, 356, GOLD)
    body.append(number.replace("translate(0.0", f"translate({W - width + 150:.1f}"))
    body.append(micro(f"ARSENAL   PREMIER LEAGUE {s['short']}", 46, 74))
    word, _ = F.run("CHAMPIONS", 96, 44, 172, BONE, tracking=-0.01)
    body.append(word)
    body.append(micro(f"{s['won']} WON   {s['drew']} DRAWN   {s['lost']} LOST",
                      46, 212, fill=GOLD))
    body.append(micro("EVERY MATCH, IN ORDER", 46, H - 96, fill=BONE, size=9.5))
    body.append(strip(s["results"], 46, H - 84, 420, 46))
    return H, "".join(body)


def stack(s):
    """2. Four lines, edge to edge, the way a terrace chant is set."""
    H = 400
    body = [f'<rect width="{W}" height="{H}" fill="{GOLD}"/>']
    # Three lines and then the season itself as the fourth, so the block is
    # type, type, type, evidence.
    lines = [("ARSENAL", RED, 0), ("CHAMPIONS", RED, 0), ("85 POINTS", BONE, 0)]
    y, size = 104, 96
    for text, fill, _ in lines:
        run, width = F.run(text, size, 0, y, fill, tracking=-0.02)
        # Every line is set to the same width, so the block is justified by scale
        # rather than by spacing: the type fills the panel because it was drawn to.
        scale = (W + 60) / width
        body.append(run.replace(f"scale({size / N.upem:.6f}",
                                f"scale({size * scale / N.upem:.6f}")
                    .replace("translate(0.0", "translate(-30.0"))
        y += 82
    body.append(strip(s["results"], -30, y - 46, W + 60, 96, gap=4,
                      colours=(RED, BONE, DEEP)))
    body.append(micro(f"{s['short']}   SECURED {s['secured']:%-d %B %Y}".upper(),
                      W - 30, H - 16, fill=RED, size=12, anchor="end"))
    return H, "".join(body)


def chevron(s):
    """3. The mark first: a gold chevron cut across the red, type riding it."""
    H = 360
    body = [f'<rect width="{W}" height="{H}" fill="{RED}"/>']
    # One shape, repeated at the panel's own angle. Hard edges, no shading.
    for i in range(3):
        x = 150 + i * 300
        body.append(f'<path d="M{x} 0 L{x + 120} 0 L{x - 60} {H} L{x - 180} {H}Z" '
                    f'fill="{GOLD}"/>')
    body.append(f'<rect y="{H - 96}" width="{W}" height="96" fill="{DEEP}"/>')
    number, nw = N.run("85", 210, 40, 224, BONE)
    body.append(number)
    word, _ = F.run("CHAMPIONS", 96, 40 + nw + 34, 224, BONE, tracking=-0.015)
    body.append(word)
    body.append(micro(f"ARSENAL   PREMIER LEAGUE {s['short']}", 40, 74, fill=BONE))
    body.append(micro(f"{s['won']} WON   {s['drew']} DRAWN   {s['lost']} LOST",
                      40 + nw + 36, 172, fill=GOLD))
    body.append(strip(s["results"], 40, H - 74, W - 80, 52,
                      colours=(GOLD, BONE, "#5c030b")))
    return H, "".join(body)


def split(s):
    """4. A field cut in two: gold left, red right, the number across the seam."""
    H = 360
    CUT = 372
    body = [f'<rect width="{CUT}" height="{H}" fill="{GOLD}"/>',
            f'<rect x="{CUT}" width="{W - CUT}" height="{H}" fill="{RED}"/>']
    # The number straddles the cut and changes colour where the field does, so the
    # two halves of the panel are held together by one shape rather than butted.
    number, width = N.run("85", 400, 30, 318, RED)
    body.append(number)
    clipped, _ = N.run("85", 400, 30, 318, GOLD)
    body.append(f'<clipPath id="right"><rect x="{CUT}" width="{W - CUT}" '
                f'height="{H}"/></clipPath>'
                f'<g clip-path="url(#right)">{clipped}</g>')
    body.append(micro(f"ARSENAL   PREMIER LEAGUE {s['short']}", CUT + 36, 78))
    word, _ = F.run("CHAMPIONS", 66, CUT + 32, 150, BONE, tracking=-0.015)
    body.append(word)
    body.append(micro(f"{s['won']} WON   {s['drew']} DRAWN   {s['lost']} LOST",
                      CUT + 36, 190, fill=GOLD))
    body.append(slashes(s["results"], CUT + 30, 232, W - CUT - 60, 66))
    return H, "".join(body)


def rows(s):
    """5. The poster: rows at different scales, one slanted, one ruled off."""
    H = 430
    body = [f'<rect width="{W}" height="{H}" fill="{RED}"/>']
    row1, w1 = N.run("CHAMPIONS", 104, -18, 96, BONE, tracking=-0.02)
    body.append(row1)
    body.append(micro(s["short"], w1 - 4, 96, fill=GOLD, size=40, tracking=0))
    row2, _ = F.run("85 POINTS", 128, -24, 214, GOLD, tracking=-0.03)
    body.append(row2)
    body.append(slashes(s["results"], -30, 236, W + 60, 58))
    row3, w3 = F.run(f"{s['won']}-{s['drew']}-{s['lost']}", 88, -20, 386, BONE,
                     tracking=-0.02)
    body.append(row3)
    body.append(micro(f"WON DRAWN LOST   SECURED {s['secured']:%-d %B %Y}".upper(),
                      w3 + 20, 386, fill=GOLD, size=14))
    return H, "".join(body)


def build():
    s = season()
    cards = []
    for name, fn in (("crop", crop), ("stack", stack), ("chevron", chevron),
                     ("split", split), ("rows", rows)):
        height, body = fn(s)
        open(os.path.join(HERE, f"mark-{name}.svg"), "w").write(
            svg(height, body, f"Arsenal, champions of the {s['label']} Premier "
                              f"League with {s['points']} points"))
        cards.append(f'<div class="c"><span>{name}</span>'
                     f'<img src="mark-{name}.svg"></div>')
        print(f"mark-{name}.svg  {W}x{height}")
    open(os.path.join(HERE, "marks.html"), "w").write(
        '<!doctype html><meta charset="utf-8"><style>'
        'body{margin:0;background:#e9e9e9;font:11px/1 -apple-system,sans-serif}'
        '.p{padding:24px 40px;width:900px}.c{margin-bottom:26px}'
        '.c span{display:block;color:#999;text-transform:uppercase;'
        'letter-spacing:.12em;margin-bottom:6px}'
        'img{display:block;width:100%;height:auto}</style>'
        f'<div class="p">{"".join(cards)}</div>')
    print("wrote marks.html")


if __name__ == "__main__":
    build()
