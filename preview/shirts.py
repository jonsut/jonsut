"""The three numbers as printed shirt backs: home, away, third.

One number a panel, one word a panel, set the way a shirt is actually printed: the
name in small tracked caps across the shoulders, the number huge underneath with a
contrasting outline, on the kit's own colour.

Colours are sampled off the club shop photographs rather than guessed. Home red is
not the brand red, it is the fabric red, and the difference shows next to the away
navy.
"""
import os
import sys

from parade import Shaper, N7, FORWARD   # noqa: E402
from system import season                # noqa: E402
from colourways import seme              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import cover  # noqa: E402

W = 900
N = Shaper(N7)

# ground, pattern, number fill, number outline, name
KITS = {
    "home":  ("#c60922", "#ffffff", "#ffffff", "#1b2340", "#ffffff"),
    "away":  ("#17203d", "#242f55", "#ffffff", "#0d1226", "#ffffff"),
    "third": ("#ead08e", "#dfc074", "#1b2340", "#ffffff", "#1b2340"),
}


def banana(x, width, height, fill, tile=118):
    """The 1991 away print: tessellating triangles with a V of bars beneath each.

    Two earlier attempts got the parts right and the rhythm wrong. The print reads
    as a field of large triangles close enough together that the ground between
    them becomes a zigzag channel, with short bars grouped into an arrow under each
    triangle. Rows offset by half a tile so the triangles interlock rather than
    sitting in columns.
    """
    u = tile / 100
    out = []
    for r in range(-1, int(height / (tile * 0.92)) + 2):
        for c in range(-1, int(width / tile) + 3):
            ox = c * 100 + (50 if r % 2 else 0)
            oy = r * 92
            out.append(f'<path d="M{(ox + 18) * u:.1f} {oy * u:.1f} '
                       f'L{(ox + 82) * u:.1f} {oy * u:.1f} '
                       f'L{(ox + 50) * u:.1f} {(oy + 58) * u:.1f}Z" fill="{fill}"/>')
            for i in range(4):
                y = (oy + 62 + i * 7.6) * u
                out.append(f'<rect x="{(ox + 22 + i * 6) * u:.1f}" y="{y:.1f}" '
                           f'width="{24 * u:.1f}" height="{4.2 * u:.1f}" '
                           f'fill="{fill}"/>')
                out.append(f'<rect x="{(ox + 54 - i * 6) * u:.1f}" y="{y:.1f}" '
                           f'width="{24 * u:.1f}" height="{4.2 * u:.1f}" '
                           f'fill="{fill}"/>')
    return "".join(out)


def zigzag(x, width, height, fill, step=54):
    """The third shirt's diagonals, which were right the first time."""
    out = []
    for i in range(-6, int(width / step) + 10):
        left = x + i * step
        out.append(f'<path d="M{left:.0f} {height} L{left + height * 0.62:.0f} 0 '
                   f'L{left + height * 0.62 + step * 0.42:.0f} 0 '
                   f'L{left + step * 0.42:.0f} {height}Z" fill="{fill}"/>')
    return "".join(out)


PATTERNS = {"away": banana, "third": zigzag}


def panel(x, width, height, kit, word, number):
    ground, pattern, ink, outline, name = KITS[kit]
    # Home takes the ermine from the champions panel, so the strip and the panel
    # above it are wearing the same fur. The other two take their own prints.
    if kit == "home":
        field = seme(x, 0, width, height, pattern, 0.14, size=30, step=86)
    else:
        field = (f'<clipPath id="k{kit}"><rect x="{x}" y="0" width="{width}" '
                 f'height="{height}"/></clipPath>'
                 f'<g clip-path="url(#k{kit})">'
                 + PATTERNS[kit](x, width, height, pattern) + "</g>")
    body = [f'<rect x="{x}" y="0" width="{width}" height="{height}" fill="{ground}"/>',
            field]
    # The name sits where a shirt's does: above the number, small, widely tracked.
    run, w = N.run(word.upper(), 38, 0, 84, name, tracking=0.16)
    run = run.replace(f'fill="{name}"',
                      f'fill="{name}" stroke="{outline}" stroke-width="7" '
                      'stroke-linejoin="round" paint-order="stroke"')
    body.append(run.replace("translate(0.0", f"translate({x + (width - w) / 2:.1f}"))
    # Printed numbers carry an outline in a second colour. paint-order puts the
    # stroke behind the fill so the letterform keeps its true weight.
    digits, dw = N.run(number, 248, 0, height * 0.79, ink)
    body.append(digits.replace("translate(0.0", f"translate({x + (width - dw) / 2:.1f}"))
    return "".join(body)


def build():
    s = season()
    clear = s["top"][0][2] - s["top"][1][2]
    H, GAP = 360, 3
    width = (W - GAP * 2) / 3
    cells = [("home", "Titles", "14"), ("away", "Points", str(s["points"])),
             ("third", "Clear", str(clear))]
    body = []
    for i, (kit, word, number) in enumerate(cells):
        body.append(panel(i * (width + GAP), width, H, kit, word, number))
    alt = "  ".join(f"{n} {w.lower()}" for _, w, n in cells)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" role="img" aria-label="{alt}">'
           f"<title>{alt}</title>{''.join(body)}</svg>\n")
    open(os.path.join(HERE, "shirts.svg"), "w").write(svg)
    print(f"shirts.svg  {W}x{H}  |  {alt}")
    open(os.path.join(HERE, "shirts.html"), "w").write(
        '<!doctype html><meta charset="utf-8"><style>'
        'body{margin:0;background:#e9e9e9;font:11px/1 -apple-system,sans-serif}'
        '.p{padding:24px 40px;width:900px}.c{margin-bottom:22px}'
        '.c span{display:block;color:#999;text-transform:uppercase;'
        'letter-spacing:.12em;margin-bottom:6px}'
        'img{display:block;width:100%;height:auto}</style>'
        '<div class="p"><div class="c"><span>shirt backs</span>'
        '<img src="shirts.svg"></div>'
        '<div class="c"><span>with the champions panel above</span>'
        '<img src="way-bone.svg"><img src="shirts.svg" style="margin-top:3px">'
        '</div></div>')
    print("wrote shirts.html")


if __name__ == "__main__":
    build()
