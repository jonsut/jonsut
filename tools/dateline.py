"""Set the masthead dateline from committed outlines, with no font installed.

tools/build_panel.py runs on Jon's machine, where PP Neue Montreal lives, and
writes data/dateline-glyphs.json. This runs in CI, where it does not, and composes
a line of type out of that table. It is a very small typesetter: advance the pen by
each glyph's width plus the tracking, and place the outline there.

The alternative was letting the one line that changes every day fall back to a
system sans, in a panel whose whole point is that it is set in one voice.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = os.path.join(ROOT, "data", "dateline-glyphs.json")
START, END = "<!--DATELINE-->", "<!--/DATELINE-->"


def load():
    return json.load(open(TABLE))


def measure(text, table):
    """Width in px of the text as it will be set."""
    track = table["tracking"] * table["upem"]
    units = sum(table["glyphs"][c]["w"] + track for c in text)
    # The trailing letterspace is real in the advance but not in the ink, so it is
    # taken back off. Leaving it in makes right-aligned text sit a pixel light.
    return (units - track) * table["size"] / table["upem"]


def run(text, right, baseline, table, cls="ink"):
    """A right-aligned run of outlined type, ending at x=right on the baseline."""
    missing = sorted(set(text) - set(table["glyphs"]))
    if missing:
        raise KeyError(f"no outline for {missing}; add to DATELINE_CHARS and rerun "
                       "tools/build_panel.py on a machine with the font")
    scale = table["size"] / table["upem"]
    track = table["tracking"] * table["upem"]
    pen, parts = 0.0, []
    for char in text:
        glyph = table["glyphs"][char]
        if glyph.get("d"):
            shift = f' transform="translate({round(pen)} 0)"' if pen else ""
            parts.append(f'<path d="{glyph["d"]}"{shift}/>')
        pen += glyph["w"] + track
    x = right - measure(text, table)
    # Font units are y-up and SVG is y-down, hence the negative vertical scale.
    return (f'<g class="{cls}" transform="translate({x:.1f} {baseline}) '
            f'scale({scale:.6f} {-scale:.6f})">' + "".join(parts) + "</g>")


def stamp(path, text, right, baseline):
    """Replace the dateline slot in a panel, leaving the rest of the file alone."""
    svg = open(path).read()
    if START not in svg:
        raise ValueError(f"{path} has no dateline slot; rerun tools/build_panel.py")
    head, rest = svg.split(START, 1)
    _, tail = rest.split(END, 1)
    body = run(text, right, baseline, load())
    open(path, "w").write(f"{head}{START}{body}{END}{tail}")
    return text
