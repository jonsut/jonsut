"""The ermine device: a heraldic spot, and a field strewn with them.

This file was a palette study for a CHAMPIONS panel that was explored and dropped,
because it repeated the 85 the shirt strip already carries. What survives is the
device that study produced, which the shipped home shirt uses, so the strip can
still be regenerated from source.

No imports: both functions are pure geometry.
"""


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
