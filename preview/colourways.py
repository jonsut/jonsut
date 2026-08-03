"""Split, in six colourways. One red held constant, the partner colour varied.

The claret and gold was a cascade from one bad decision: gold read as a metal, a
metal is low-chroma ochre, and ochre forced the red down until it was claret. The
references never do that. Wimbledon is not grass and white, it is acid yellow on
deep green; the Premier League is neon green and aubergine. They take one true
colour and pair it with an unexpected bright, both at full strength.

So the red stays at full chroma and the second colour is the variable.
"""
import os
import sys

from parade import Shaper, N7, FORWARD   # noqa: E402
from system import season, M, INSET, W   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import cover  # noqa: E402

RED = "#ef0107"          # Arsenal's own red, undiluted


def ermine(cx, cy, size, fill, opacity=1):
    """An ermine spot: three dots over a tail, the fur that fields the old crest.

    Drawn rather than traced. Ermine is a heraldic fur that predates the club by
    six hundred years and belongs to nobody, where the crest it appears on is
    Arsenal's trademark, so this is the part of that shield that can be borrowed.

    Proportioned on a 24-unit square and scaled, so one definition serves a 9px
    corner mark and a 40px field.
    """
    u = size / 24
    dot = 1.9 * u
    tail = ("M12 7.4 C13.6 12.4 15.2 15.6 18.2 20.2 "
            "C15.4 19 13.4 19.3 12 20.9 "
            "C10.6 19.3 8.6 19 5.8 20.2 "
            "C8.8 15.6 10.4 12.4 12 7.4 Z")
    spots = "".join(
        f'<circle cx="{cx + (x - 12) * u:.2f}" cy="{cy + (y - 12) * u:.2f}" '
        f'r="{dot:.2f}"/>'
        for x, y in ((12, 2.6), (7.6, 6.2), (16.4, 6.2)))
    return (f'<g fill="{fill}" opacity="{opacity}">'
            f'<path d="{tail}" transform="translate({cx - 12 * u:.2f} '
            f'{cy - 12 * u:.2f}) scale({u:.4f})"/>{spots}</g>')


def seme(x, y, width, height, fill, opacity, size=34, step=96):
    """A field strewn with ermine, the way the old crest strews it: rows offset by
    half a step so the eye reads a texture rather than a grid."""
    out, row = [], 0
    cy = y + step * 0.35
    while cy < y + height + step:
        cx = x + (step / 2 if row % 2 else 0) - step * 0.25
        while cx < x + width + step:
            out.append(ermine(cx, cy, size, fill, opacity))
            cx += step
        cy += step * 0.62
        row += 1
    return (f'<clipPath id="s{int(x)}{int(y)}{int(width)}"><rect x="{x}" y="{y}" '
            f'width="{width}" height="{height}"/></clipPath>'
            f'<g clip-path="url(#s{int(x)}{int(y)}{int(width)})">'
            + "".join(out) + "</g>")
L = cover.TABLES["lede"]
N, F = Shaper(N7), Shaper(FORWARD)

# ground, field, ink-on-field, ink-on-ground, quiet, loss
WAYS = [
    ("acid",     RED, "#e9ff3d", RED, "#ffffff", "#ffd9da", "#8c0004"),
    ("hot pink", RED, "#ff2d78", "#ffffff", "#ffffff", "#ffc9d9", "#8c0004"),
    ("mint",     RED, "#00f0a0", "#0a2a1e", "#ffffff", "#ffd0d2", "#8c0004"),
    ("electric", RED, "#3d5bff", "#ffffff", "#ffffff", "#ffd0d2", "#8c0004"),
    ("bone",     RED, "#f2efe6", RED, "#f2efe6", "#ffb3b6", "#8c0004"),
    ("flip",     "#e9ff3d", RED, "#e9ff3d", "#1a1a00", "#6b7a00", "#a30005"),
]


def panel(s, name, ground, field, on_field, on_ground, quiet, loss):
    H, CUT = 400, 392
    body = [f'<rect width="{W}" height="{H}" fill="{ground}"/>',
            f'<rect width="{CUT}" height="{H}" fill="{field}"/>',
            # Strewn quietly on both sides: loud enough to be seen as a fur, faint
            # enough that the 85 stays the thing you read first.
            seme(0, 0, CUT, H, on_field, 0.10),
            seme(CUT, 0, W - CUT, H, field, 0.13)]

    def label(text, x, y, fill, size=10, anchor="start"):
        run, _ = N.run(text, size, x, y, fill, tracking=0.26, anchor=anchor)
        return run

    def point(cx, cy, fill, size=26, gap=0):
        return ermine(cx, cy, size, fill)

    number, width = N.run("85", 268, 0, 262, on_field)
    body.append(number.replace("translate(0.0", f"translate({(CUT - width) / 2:.1f}"))
    pts, pw = N.run("POINTS", 11, 0, 306, on_field, tracking=0.26)
    body.append(pts.replace("translate(0.0", f"translate({(CUT - pw) / 2:.1f}"))
    body += [point(M, M, on_field), point(CUT - M, M, on_field),
             point(M, H - M, on_field), point(CUT - M, H - M, on_field),
             point(W - M, M, field), point(W - M, H - M, field)]
    body.append(label("ARSENAL", CUT + M, M + 5, on_ground))
    body.append(label(s["short"], W - INSET, M + 5, on_ground, anchor="end"))
    word, _ = F.run("CHAMPIONS", 62, CUT + M, 168, on_ground, tracking=-0.015)
    body.append(word)
    body.append(cover.run(f"{s['won']} won, {s['drew']} drawn, {s['lost']} lost.",
                          L, 14, CUT + M, 206, quiet))
    body.append(cover.run(f"Settled on {s['secured']:%-d %B %Y}.", L, 14,
                          CUT + M, 226, quiet))
    body.append(label("SEASON IN FULL", CUT + M, H - M - 44, on_ground, size=9.5))
    unit = (W - CUT - M * 2 - 74) / 38
    for i, match in enumerate(s["run"]):
        fill = field if match["got"] == 3 else on_ground if match["got"] == 1 else loss
        tall = 22 if match["got"] == 3 else 12 if match["got"] == 1 else 6
        body.append(f'<rect x="{CUT + M + i * (unit + 2):.1f}" '
                    f'y="{H - M - 36 + (22 - tall)}" width="{unit:.1f}" '
                    f'height="{tall}" fill="{fill}"/>')
    alt = f"Arsenal, champions with {s['points']} points"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}" role="img" aria-label="{alt}">'
            f"<title>{alt}</title>{''.join(body)}</svg>\n")


def build():
    s = season()
    cards = []
    for way in WAYS:
        name = way[0]
        open(os.path.join(HERE, f"way-{name.replace(' ', '')}.svg"), "w").write(
            panel(s, *way))
        cards.append(f'<div class="c"><span>{name}</span>'
                     f'<img src="way-{name.replace(" ", "")}.svg"></div>')
        print(f"way-{name}")
    open(os.path.join(HERE, "ways.html"), "w").write(
        '<!doctype html><meta charset="utf-8"><style>'
        'body{margin:0;background:#e9e9e9;font:11px/1 -apple-system,sans-serif}'
        '.p{padding:24px 40px;width:900px}.c{margin-bottom:22px}'
        '.c span{display:block;color:#999;text-transform:uppercase;'
        'letter-spacing:.12em;margin-bottom:6px}'
        'img{display:block;width:100%;height:auto}</style>'
        f'<div class="p">{"".join(cards)}</div>')
    print("wrote ways.html")


if __name__ == "__main__":
    build()
