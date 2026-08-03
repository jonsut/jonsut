"""Three readings of the 1991 away print, side by side, to pick one.

What the photograph actually shows: large solid triangles pointing down on a
lattice, the ground showing between them as a zigzag channel, and groups of short
horizontal bars stacked in a staircase that runs parallel to the triangle edges.
The bars are horizontal but the group is diagonal, which is the bit both of my
earlier attempts missed.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NAVY, TONE = "#17203d", "#242f55"
W, H = 300, 360


def stair(ox, oy, u, fill, count=5, bar=30, thick=4.5, dx=7, dy=9, mirror=False):
    """A group of horizontal bars stepping down a diagonal."""
    out = []
    for i in range(count):
        x = ox + (-i * dx if mirror else i * dx)
        out.append(f'<rect x="{x * u:.1f}" y="{(oy + i * dy) * u:.1f}" '
                   f'width="{bar * u:.1f}" height="{thick * u:.1f}" fill="{fill}"/>')
    return "".join(out)


def tri(cx, top, half, depth, u, fill):
    return (f'<path d="M{(cx - half) * u:.1f} {top * u:.1f} '
            f'L{(cx + half) * u:.1f} {top * u:.1f} '
            f'L{cx * u:.1f} {(top + depth) * u:.1f}Z" fill="{fill}"/>')


def variant_a(tile=120):
    """Big triangle, staircases parallel to each edge."""
    u = tile / 100
    out = []
    for r in range(-1, int(H / (tile * 0.92)) + 2):
        for c in range(-1, int(W / tile) + 3):
            ox = c * 100 + (50 if r % 2 else 0)
            oy = r * 92
            out.append(tri(ox + 50, oy + 4, 26, 52, u, TONE))
            out.append(stair(ox + 4, oy + 10, u, TONE, dx=6, dy=9))
            out.append(stair(ox + 96, oy + 10, u, TONE, dx=6, dy=9, mirror=True))
    return "".join(out)


def variant_b(tile=120):
    """Large and small triangle in each repeat, staircases between."""
    u = tile / 100
    out = []
    for r in range(-1, int(H / (tile * 0.92)) + 2):
        for c in range(-1, int(W / tile) + 3):
            ox = c * 100 + (50 if r % 2 else 0)
            oy = r * 92
            out.append(tri(ox + 34, oy + 2, 24, 54, u, TONE))
            out.append(tri(ox + 84, oy + 30, 13, 28, u, TONE))
            out.append(stair(ox + 62, oy + 4, u, TONE, count=4, bar=24, dx=6, dy=8))
            out.append(stair(ox + 26, oy + 60, u, TONE, count=4, bar=24, dx=6, dy=8))
    return "".join(out)


def variant_c(tile=120):
    """Triangles with the bars grouped into a V under each, arrow-like."""
    u = tile / 100
    out = []
    for r in range(-1, int(H / (tile * 0.92)) + 2):
        for c in range(-1, int(W / tile) + 3):
            ox = c * 100 + (50 if r % 2 else 0)
            oy = r * 92
            out.append(tri(ox + 50, oy, 30, 56, u, TONE))
            for i in range(4):
                y = oy + 60 + i * 8
                out.append(f'<rect x="{(ox + 24 + i * 6) * u:.1f}" y="{y * u:.1f}" '
                           f'width="{22 * u:.1f}" height="{4.5 * u:.1f}" '
                           f'fill="{TONE}"/>')
                out.append(f'<rect x="{(ox + 54 - i * 6) * u:.1f}" y="{y * u:.1f}" '
                           f'width="{22 * u:.1f}" height="{4.5 * u:.1f}" '
                           f'fill="{TONE}"/>')
    return "".join(out)


cards = []
for name, fn in (("A  staircases on the edges", variant_a),
                 ("B  two sizes of triangle", variant_b),
                 ("C  triangle over a V of bars", variant_c)):
    slug = name.split()[0]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}"><rect width="{W}" height="{H}" '
           f'fill="{NAVY}"/><clipPath id="c"><rect width="{W}" height="{H}"/>'
           f'</clipPath><g clip-path="url(#c)">{fn()}</g></svg>\n')
    open(os.path.join(HERE, f"banana-{slug}.svg"), "w").write(svg)
    cards.append(f'<figure><img src="banana-{slug}.svg"><figcaption>{name}'
                 f'</figcaption></figure>')
open(os.path.join(HERE, "banana.html"), "w").write(
    '<!doctype html><meta charset="utf-8"><style>'
    'body{margin:0;background:#e9e9e9;font:11px/1 -apple-system,sans-serif;'
    'display:flex;gap:20px;padding:24px}figure{margin:0}'
    'figcaption{color:#888;text-transform:uppercase;letter-spacing:.1em;'
    'margin-top:8px}img{display:block}</style>' + "".join(cards))
print("wrote banana.html")
