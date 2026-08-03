"""The daily cover: yesterday's reading, set as a magazine page.

The plates below this are quiet by design, and quiet turned out to be the problem.
A reader met thirty lines of prose before anything dated, so nothing on the page
said it had been rebuilt that morning. This is the fix: one loud panel that states
what the page is, with the reading as the evidence rather than the argument.

Three things are generated, not decorated:

  - the numerals are yesterday's maximum, repeated and cropped by the frame
  - the ring behind them is the climate spiral, fourteen years of monthly
    temperature plotted with the month as the angle and the departure from that
    month's own long-run mean as the radius
  - the accent is the news. Red when the day ran warm against its own date, blue
    when it ran cold, on the headline and the spiral together, so the panel reads
    before a word of it does

Type is set from the outlines in data/display-glyphs.json and friends, because CI
has no fonts installed and the panel is meant to speak in one voice. See
tools/build_panel.py, which runs where PP Neue Montreal lives and writes them.

The panel brings its own ground, so unlike every other graphic here it needs no
prefers-color-scheme branch: it looks the same in either theme.
"""
import json
import math
import os
from datetime import date

import news

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

W, H = 900, 400
YELLOW = "#f9ff47"     # the site's highlight, here as a full ground
BROWN = "#3d2415"      # the numerals: dark enough to read, warm enough for yellow
CORAL, SKY = "#fc4b34", "#2aa3ef"

HEAD = "Automatically rebuilt every morning."
NOTABLE = 10           # how high a rank for the date still counts as worth saying
COLUMN, LIMIT = 492, 384          # the cleared right-hand column
HEAD_SIZE, HEAD_TOP, LEADING = 44, 146, 0.98
DECK_SIZE, DECK_STEP = 15, 21
STAMP_BASE, DECK_CLEAR = H - 34, 46
NUMERAL, NUMERAL_X, NUMERAL_TOP, NUMERAL_STEP = 205, -46, 118, 158

TABLES = {name: json.load(open(os.path.join(DATA, f"{name}-glyphs.json")))
          for name in ("display", "dateline", "lede")}


# ------------------------------------------------------------------ typesetting

def measure(text, table, size, tracking=None):
    track = (table["tracking"] if tracking is None else tracking) * table["upem"]
    units = sum(table["glyphs"][c]["w"] + track for c in text)
    # The trailing letterspace is in the advance but not in the ink.
    return (units - track) * size / table["upem"]


def run(text, table, size, x, y, fill, tracking=None):
    """One positioned run of outlined type, at any size the outlines allow."""
    missing = sorted(set(text) - set(table["glyphs"]))
    if missing:
        raise KeyError(f"no outline for {missing}; add to PUNCT and rerun "
                       "tools/build_panel.py on a machine with the font")
    track = (table["tracking"] if tracking is None else tracking) * table["upem"]
    pen, parts = 0.0, []
    for char in text:
        glyph = table["glyphs"][char]
        if glyph.get("d"):
            parts.append(f'<path d="{glyph["d"]}" '
                         f'transform="translate({round(pen)} 0)"/>')
        pen += glyph["w"] + track
    scale = size / table["upem"]
    # Font units are y-up and SVG is y-down, hence the negative vertical scale.
    return (f'<g fill="{fill}" transform="translate({x:.1f} {y:.1f}) '
            f'scale({scale:.6f} {-scale:.6f})">' + "".join(parts) + "</g>")


def wrap(text, table, size, limit, tracking=None):
    lines, current = [], ""
    for word in text.split(" "):
        trial = f"{current} {word}".strip()
        if current and measure(trial, table, size, tracking) > limit:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


# ------------------------------------------------------------------- the spiral

def smooth(points):
    """Catmull-Rom through the points as cubic beziers, so the line stays loose."""
    d = [f"M{points[0][0]:.1f} {points[0][1]:.1f}"]
    for i in range(len(points) - 1):
        p0 = points[max(i - 1, 0)]
        p1, p2 = points[i], points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} "
                 f"{p2[0]:.1f} {p2[1]:.1f}")
    return " ".join(d)


def spiral(history, cx, cy, inner, outer, years=14):
    """Monthly temperature drawn radially: angle is the month, radius the anomaly.

    A left-to-right trace reads as a chart line, which is the one thing this is not
    meant to be. Wrapped round a circle each year becomes a loop, and fourteen loops
    at slightly different radii overlap the way a drawn scribble does. It is the
    climate spiral, an established form, so the gesture carries meaning rather than
    being a busy line: a page arguing that its graphics mean something cannot then
    decorate itself with one that does not.
    """
    end_year = max(int(y) for y in history["years"])
    monthly = {}
    for year in range(end_year - years + 1, end_year + 1):
        row = history["years"].get(str(year))
        if not row:
            continue
        for month in range(1, 13):
            first = (date(year, month, 1) - date(year, 1, 1)).days
            last = first + (28 if month == 2 else 30 if month in (4, 6, 9, 11) else 31)
            chunk = [v for v in row[first:last] if v is not None]
            if chunk:
                monthly[(year, month)] = sum(chunk) / len(chunk)
    if not monthly:
        return ""

    # Radius is the departure from that month's own long-run mean, so the loops
    # breathe with the climate rather than with the seasons.
    norms = {}
    for (year, month), value in monthly.items():
        norms.setdefault(month, []).append(value)
    norms = {m: sum(v) / len(v) for m, v in norms.items()}
    gaps = [v - norms[m] for (_, m), v in monthly.items()]
    lo, hi = min(gaps), max(gaps)
    span = (hi - lo) or 1

    points = []
    for (year, month), value in sorted(monthly.items()):
        angle = 2 * math.pi * (month - 1) / 12 - math.pi / 2
        t = (value - norms[month] - lo) / span
        r = inner + (outer - inner) * t
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return smooth(points)


# --------------------------------------------------------------- the sentence

def sentence(history, when):
    """What yesterday was, in words, from the record rather than from a template.

    "Yesterday in London" with the date stamped directly below it: the relative
    word is what makes the panel feel current, and the stamp is what stops it lying
    when someone reads the README a fortnight later.

    Returns (text, warm) where warm decides the accent.
    """
    reading = news.on(history, when)
    same = [(y, v) for y, v in news.same_date_history(history, when) if y != when.year]
    normal = sum(v for _, v in same) / len(same)
    gap = reading - normal
    warm = gap >= 0

    beaten = [y for y, v in same if (v > reading if warm else v < reading)]
    word = "warmest" if warm else "coldest"
    stood = when.year - max(beaten) if beaten else when.year - news.FIRST_YEAR
    rank = len(beaten) + 1

    opening = f"Yesterday in London it was {reading:.1f}°C, which is "
    opening += ("about average." if abs(round(gap, 1)) < 0.05 else
                f"{abs(gap):.1f} degrees {'above' if warm else 'below'} average.")

    # Three ways to place the day, in descending order of how much they say, and
    # nothing at all rather than a fourth. "Warmest in 8 years" is the line worth
    # printing, but it collapses to "in 1 years" the moment last year beat it, and
    # the rank that replaces it is only interesting near the top: "the 37th warmest
    # 18th of August" is true, dull, and would have run on two days in five.
    date_words = f"{news.ordinal(when.day)} of {when:%B}"
    try:
        last = news.on(history, when.replace(year=when.year - 1))
    except ValueError:      # 29 February, whose previous year has no such date
        last = None
    if stood >= 2:
        claim = f"It was the {word} {date_words} in {stood} years."
    elif rank <= NOTABLE:
        claim = (f"It was the {news.ordinal(rank)} {word} {date_words} in "
                 f"{len(same) + 1} years of records.")
    elif last is not None and abs(round(reading - last, 1)) >= 0.1:
        step = "warmer" if reading > last else "cooler"
        claim = (f"That is {abs(reading - last):.1f} degrees {step} than the same "
                 "date last year.")
    elif last is not None:
        claim = "Almost exactly what the same date managed last year."
    else:
        claim = ""
    return f"{opening} {claim}".strip(), warm


# ------------------------------------------------------------------ the panel

def render(history, when, edition, path):
    """Draw the cover for one day. Returns the sentence, for the README's alt text."""
    display, caption, body = TABLES["display"], TABLES["dateline"], TABLES["lede"]
    text, warm = sentence(history, when)
    accent = CORAL if warm else SKY
    reading = f"{news.on(history, when):.1f}°"

    parts = [f'<rect width="{W}" height="{H}" fill="{YELLOW}"/>',
             f'<path d="{spiral(history, 250, 200, 46, 176)}" fill="none" '
             f'stroke="{accent}" stroke-width="9" stroke-linecap="round" '
             'stroke-linejoin="round"/>']

    # Three repeats, running off the top, left and bottom edges. The crop is the
    # point: the number is too big for the frame, which is what makes it an object
    # on the page rather than a label on one.
    for i in range(3):
        parts.append(run(reading, display, NUMERAL, NUMERAL_X,
                         NUMERAL_TOP + i * NUMERAL_STEP, BROWN, tracking=-0.045))

    parts.append(run("LONDON", caption, 11, COLUMN, 84, BROWN, tracking=0.3))
    y = HEAD_TOP
    for line in wrap(HEAD, display, HEAD_SIZE, LIMIT):
        parts.append(run(line, display, HEAD_SIZE, COLUMN, y, accent))
        y += HEAD_SIZE * LEADING

    # Set from the bottom up, so however many lines the sentence takes on a given
    # day, its last one always clears the stamp by the same gap.
    lines = wrap(text, body, DECK_SIZE, LIMIT)
    y = STAMP_BASE - DECK_CLEAR - (len(lines) - 1) * DECK_STEP
    for line in lines:
        parts.append(run(line, body, DECK_SIZE, COLUMN, y, BROWN))
        y += DECK_STEP

    stamp = f"{when:%-d %B %Y}".upper() + f"   NO. {edition}"
    parts.append(run(stamp, caption, 11, COLUMN, STAMP_BASE, BROWN, tracking=0.3))

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" role="img" aria-label="{text}">'
           f"<title>{text}</title>"
           # Everything is drawn oversized and cut by the frame.
           f'<defs><clipPath id="frame"><rect width="{W}" height="{H}"/></clipPath>'
           f'</defs><g clip-path="url(#frame)">{"".join(parts)}</g></svg>\n')
    open(path, "w").write(svg)
    return text
