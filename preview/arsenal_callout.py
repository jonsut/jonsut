"""Callout panels for the football section, in the third kit's palette.

The cover works because it is loud in the page's own yellow. Repeating that yellow
under the football would say the two sections are the same thing, so this borrows
the kit instead: butter shirt, navy shorts, maroon trim, cream stripe, all sampled
off the shirt photo rather than guessed.

The tiling comes from the tutu identity: one word repeated across the field with
the cut alternating upright and oblique, colours changing as it goes. There is no
italic in PP Neue Montreal here, so the oblique is synthesised with a skew, which
is exactly what a display treatment can get away with and body text cannot.

Everything stated is computed from the openfootball record. Local exploration.
"""
import os
import sys
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_football as bf   # noqa: E402
import cover                  # noqa: E402

W = 900
NAVY = "#1e2841"      # the shorts
SHIRT = "#e8d48f"     # the shirt
CREAM = "#feefc4"     # the stripe
MAROON = "#6b1526"    # the collar and cuff trim, lifted to read on navy
SLANT = -12           # degrees of synthetic oblique

D, C, L = cover.TABLES["display"], cover.TABLES["dateline"], cover.TABLES["lede"]


def run(text, table, size, x, y, fill, tracking=None, slant=0, opacity=None):
    """cover.run with an optional skew, so a word can be set oblique."""
    track = (table["tracking"] if tracking is None else tracking) * table["upem"]
    pen, parts = 0.0, []
    for char in text:
        glyph = table["glyphs"][char]
        if glyph.get("d"):
            parts.append(f'<path d="{glyph["d"]}" '
                         f'transform="translate({round(pen)} 0)"/>')
        pen += glyph["w"] + track
    scale = size / table["upem"]
    skew = f" skewX({slant})" if slant else ""
    fade = f' opacity="{opacity}"' if opacity is not None else ""
    return (f'<g fill="{fill}"{fade} transform="translate({x:.1f} {y:.1f}){skew} '
            f'scale({scale:.6f} {-scale:.6f})">' + "".join(parts) + "</g>")


def measure(text, table, size, tracking=None):
    return cover.measure(text, table, size, tracking)


def frame(body, height, name):
    return (f'<defs><clipPath id="{name}"><rect width="{W}" height="{height}"/>'
            f'</clipPath></defs><g clip-path="url(#{name})">{body}</g>')


def svg(height, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" '
            f'width="{W}" height="{height}" role="img" aria-label="{label}">'
            f"<title>{label}</title>{body}</svg>\n")


def tiles(height, word="ARSENAL", size=74, rows=None, colours=None, gap=26):
    """The word repeated across the field, alternating upright and oblique."""
    colours = colours or [(SHIRT, 1), (CREAM, 1), (MAROON, 1), (SHIRT, 0.35),
                          (CREAM, 0.28), (MAROON, 0.9)]
    step = size * 1.02
    rows = rows or int(height / step) + 2
    out, n = [], 0
    for r in range(rows):
        y = size * 0.86 + r * step
        # Each row starts further left, so the columns never line up and the field
        # reads as a repeating pattern rather than a table of words.
        x = -220 + (r % 3) * 96
        while x < W:
            fill, alpha = colours[n % len(colours)]
            out.append(run(word, D, size, x, y, fill,
                           tracking=-0.02, slant=SLANT if n % 2 else 0,
                           opacity=None if alpha == 1 else alpha))
            x += measure(word, D, size, -0.02) + gap
            n += 1
    return "".join(out)


# ------------------------------------------------------------------ the facts

def facts():
    """Everything the callout can truthfully say, from the published record."""
    end = date.today() - timedelta(days=1)
    labels = bf.seasons(end)
    league = {label: bf.premier_league(label) for label in labels}
    current = next(label for label in reversed(labels) if league[label])
    matches = league[current]
    ranks, table = bf.table_after(matches, max(m[0] for m in matches))
    played, drawn, goals, count = table[bf.CLUB]
    ours = [m for m in matches if bf.CLUB in (m[1], m[2]) and bf.outcome(m) is not None]
    won = sum(1 for m in ours if bf.outcome(m) > 0)
    drew = sum(1 for m in ours if bf.outcome(m) == 0)
    secured = bf.title_secured(matches)
    spare = len([m for m in ours if secured and m[0] > secured[0]])
    everything = sorted(m for m in ours + bf.champions_league(current)
                        if bf.outcome(m) is not None)
    last = everything[-1]
    other = last[2] if last[1] == bf.CLUB else last[1]
    home, away = last[3]
    ours_score, theirs = (home, away) if last[1] == bf.CLUB else (away, home)
    form = sum(3 if bf.outcome(m) > 0 else (1 if bf.outcome(m) == 0 else 0)
               for m in everything[-5:])
    return {
        "season": current, "points": played, "won": won, "drew": drew,
        "lost": len(ours) - won - drew, "matches": len(ours),
        "rank": ranks[bf.CLUB], "secured": secured[0] if secured else None,
        "spare": spare, "form": form,
        "last": f"{ours_score}-{theirs} to {other.replace(' FC', '')}"
                if theirs > ours_score else
                f"{ours_score}-{theirs} against {other.replace(' FC', '')}",
        "last_date": last[0],
    }


# ----------------------------------------------------------------- the panels

def tiled(f):
    """A. The field of words, with the copy cleared to the right."""
    H = 300
    X, LIM = 520, 340
    body = [f'<rect width="{W}" height="{H}" fill="{NAVY}"/>', tiles(H)]
    # A navy panel over the tiling rather than a gap in it: the words carry on
    # underneath, which is what makes it a field rather than a border.
    body.append(f'<rect x="{X - 40}" y="0" width="{W - X + 40}" height="{H}" '
                f'fill="{NAVY}"/>')
    body.append(run("PREMIER LEAGUE " + f.season, C, 11, X, 74, SHIRT, tracking=0.3))
    body.append(run("Champions.", D, 54, X, 138, CREAM))
    deck = (f"{f.points} points from {f.matches} matches, "
            f"{f.won} won. Secured on {f.secured:%-d %B} with "
            f"{'a match' if f.spare == 1 else f'{f.spare} matches'} to spare.")
    y = 176
    for line in cover.wrap(deck, L, 14.5, LIM):
        body.append(run(line, L, 14.5, X, y, SHIRT))
        y += 20
    # Maroon on navy is the kit's own pairing and it is nearly invisible at
    # caption size, so the trim colour stays on the light grounds only.
    body.append(run(f"LAST PLAYED {f.last_date:%-d %B %Y}".upper(), C, 10.5, X,
                    H - 34, SHIRT, tracking=0.3, opacity=0.6))
    return H, frame("".join(body), H, "a")


def swatch(f):
    """B. The reference stack: two blocks, each a colour and a claim."""
    H, TOP = 260, 130
    body = [f'<rect width="{W}" height="{TOP}" fill="{NAVY}"/>',
            f'<rect y="{TOP}" width="{W}" height="{H - TOP}" fill="{SHIRT}"/>']
    for i, (label, note, ink, sub) in enumerate((
            ("CHAMPIONS", f"{f.season.replace('-', '/')}  ·  "
                          f"SECURED {f.secured:%-d %B %Y}".upper(), SHIRT, CREAM),
            (f"{f.points} POINTS", f"{f.won} WON  ·  {f.drew} DRAWN  ·  "
                                   f"{f.lost} LOST", NAVY, MAROON))):
        top = i * TOP
        size = 44
        width = measure(label, D, size, 0.02)
        body.append(run(label, D, size, (W - width) / 2, top + 74, ink,
                        tracking=0.02))
        note_w = measure(note, C, 10.5)
        body.append(run(note, C, 10.5, (W - note_w) / 2, top + 100, sub,
                        tracking=0.3))
    # The reference marks the second swatch with a small dot. Here it is the one
    # in the kit's own maroon, so the panel carries all four kit colours.
    body.insert(2, f'<circle cx="60" cy="{TOP + 62}" r="9" fill="{MAROON}"/>')
    return H, frame("".join(body), H, "b")


def split(f):
    """C. The word broken across two cuts, the way the reference sets its own."""
    H = 300
    body = [f'<rect width="{W}" height="{H}" fill="{NAVY}"/>',
            tiles(H, word="CHAMPIONS", size=64,
                  colours=[(SHIRT, 0.16), (CREAM, 0.12), (MAROON, 0.5),
                           (SHIRT, 0.1)])]
    # CHAMP upright, IONS oblique, the two halves in different colours: the tutu
    # move, where one word is set in two cuts and reads as a mark rather than type.
    x = 56
    body.append(run("CHAMP", D, 116, x, 176, CREAM, tracking=-0.03))
    x += measure("CHAMP", D, 116, -0.03) + 6
    body.append(run("IONS", D, 116, x, 176, SHIRT, tracking=-0.03, slant=SLANT))
    body.append(run(f"ARSENAL  ·  PREMIER LEAGUE {f.season}", C, 11, 58, 78,
                    SHIRT, tracking=0.3))
    deck = (f"{f.points} points, {f.won} won, {f.drew} drawn, {f.lost} lost. "
            f"Then {f.last} on {f.last_date:%-d %B}, and the season was over.")
    y = 222
    for line in cover.wrap(deck, L, 15, 620):
        body.append(run(line, L, 15, 58, y, CREAM))
        y += 21
    return H, frame("".join(body), H, "c")


def build():
    data = facts()
    f = type("Facts", (), data)
    print({k: str(v) for k, v in data.items()})
    cards = []
    for name, fn in (("tiled", tiled), ("swatch", swatch), ("split", split)):
        height, body = fn(f)
        label = f"Arsenal, champions of the {data['season']} Premier League"
        open(os.path.join(HERE, f"kit-{name}.svg"), "w").write(
            svg(height, body, label))
        cards.append(f'<div class="c"><span>{name}</span>'
                     f'<img src="kit-{name}.svg"></div>')
        print(f"kit-{name}.svg  {W}x{height}")
    open(os.path.join(HERE, "kit.html"), "w").write(
        '<!doctype html><meta charset="utf-8"><style>'
        'body{margin:0;background:#f2f2f2;font:11px/1 -apple-system,sans-serif}'
        '.p{padding:24px 40px;width:900px}.c{margin-bottom:26px}'
        '.c span{display:block;color:#999;text-transform:uppercase;'
        'letter-spacing:.12em;margin-bottom:6px}'
        'img{display:block;width:100%;height:auto}</style>'
        f'<div class="p">{"".join(cards)}</div>')
    print("wrote kit.html")


if __name__ == "__main__":
    build()


# --------------------------------------------------- the cover's grammar, in kit
# The first three panels were wallpaper: a repeated word is not the data, and the
# swatch was a colour card with facts typed onto it. The cover works because the
# graphic IS the reading, the number is an object cropped by the frame, and the
# mark behind it is generated. Same rules here, and the season supplies both.

def race(matches, x, y, width, height):
    """Arsenal's points lead over second place, matchday by matchday.

    The one number that describes a title race and the only one that can go
    negative: level is zero, and the line finishing above it is the season. Drawn
    thick and cropped rather than plotted in an axis box, so it reads as a mark.
    """
    # Sampled after each of Arsenal's own matches rather than on every date in the
    # fixture list. A hundred and twelve snapshots gave a line that jittered with
    # other clubs' results, which is a stock chart; thirty-eight is the season as a
    # supporter counts it.
    days = sorted({m[0] for m in matches if bf.CLUB in (m[1], m[2])})
    series = []
    for day in days:
        ranks, table = bf.table_after(matches, day)
        if bf.CLUB not in table:
            continue
        points = {club: row[0] for club, row in table.items()}
        best = max(v for k, v in points.items() if k != bf.CLUB)
        series.append(points[bf.CLUB] - best)
    lo, hi = min(series), max(series)
    span = (hi - lo) or 1
    points = [(x + width * i / (len(series) - 1),
               y + height - height * (v - lo) / span)
              for i, v in enumerate(series)]
    zero = y + height - height * (0 - lo) / span
    return cover.smooth(points), zero, series[-1]


def wheel(matches, cx, cy, radius, thickness):
    """Every match of the season as one segment of a ring, in result colours.

    A season is a sequence, and a ring keeps it one closed object the way the
    climate spiral does rather than a row of boxes, which the plates below already
    are. Twelve o'clock is the first match of August and it runs clockwise.
    """
    import math
    played = sorted(m for m in matches if bf.outcome(m) is not None)
    step = 2 * math.pi / len(played)
    out = []
    for i, match in enumerate(played):
        got = bf.outcome(match)
        # Draws were cream at low opacity, which on navy is simply grey and read
        # as missing data. A win is the shirt, a loss the trim, a draw the stripe
        # held back a little: three kit colours doing three jobs.
        fill, alpha = ((SHIRT, 1) if got > 0 else
                       (CREAM, 0.75) if got == 0 else (MAROON, 1))
        a0 = -math.pi / 2 + i * step
        a1 = a0 + step * 0.82          # the gap is what makes them read as matches
        outer, inner = radius, radius - thickness
        p = [(cx + outer * math.cos(a0), cy + outer * math.sin(a0)),
             (cx + outer * math.cos(a1), cy + outer * math.sin(a1)),
             (cx + inner * math.cos(a1), cy + inner * math.sin(a1)),
             (cx + inner * math.cos(a0), cy + inner * math.sin(a0))]
        d = (f"M{p[0][0]:.1f} {p[0][1]:.1f}"
             f"A{outer} {outer} 0 0 1 {p[1][0]:.1f} {p[1][1]:.1f}"
             f"L{p[2][0]:.1f} {p[2][1]:.1f}"
             f"A{inner} {inner} 0 0 0 {p[3][0]:.1f} {p[3][1]:.1f}Z")
        out.append(f'<path d="{d}" fill="{fill}" opacity="{alpha}"/>')
    return "".join(out)


def column(f, body, accent=None):
    """The cover's right-hand column, to the pixel, so the two are siblings."""
    X, LIM = 492, 384
    accent = accent or SHIRT
    body.append(run(f"ARSENAL  ·  {f.season}", C, 11, X, 84, SHIRT,
                    tracking=0.3, opacity=0.75))
    y = 146
    for line in cover.wrap("Champions until somebody takes it.", D, 44, LIM):
        body.append(run(line, D, 44, X, y, accent))
        y += 44 * 0.98
    deck = (f"{f.points} points, {f.won} won, {f.drew} drawn, {f.lost} lost. The "
            f"title was settled on {f.secured:%-d %B} with a match to spare, then "
            f"{f.last} closed the season on {f.last_date:%-d %B}.")
    lines = cover.wrap(deck, L, 15, LIM)
    y = 400 - 34 - 46 - (len(lines) - 1) * 21
    for line in lines:
        body.append(run(line, L, 15, X, y, CREAM, opacity=0.85))
        y += 21
    body.append(run(f"{f.last_date:%-d %B %Y}".upper() + "   38 MATCHES", C, 11, X,
                    400 - 34, SHIRT, tracking=0.3, opacity=0.7))


def numerals(text, fill=SHIRT, opacity=None):
    return "".join(run(text, D, 205, -46, 118 + i * 158, fill,
                       tracking=-0.045, opacity=opacity) for i in range(3))


def kit_race(f, matches):
    """D. The title race as the mark, the points total as the object."""
    H = 400
    path, zero, final = race(matches, -80, 60, 620, 280)
    body = [f'<rect width="{W}" height="{H}" fill="{NAVY}"/>',
            f'<line x1="-80" y1="{zero:.1f}" x2="540" y2="{zero:.1f}" '
            f'stroke="{CREAM}" stroke-width="2" stroke-dasharray="3 6" '
            'opacity="0.7"/>',
            f'<path d="{path}" fill="none" stroke="{MAROON}" stroke-width="11" '
            'stroke-linecap="round" stroke-linejoin="round"/>',
            numerals(str(f.points)),
            f'<rect x="452" y="0" width="{W - 452}" height="{H}" fill="{NAVY}"/>']
    column(f, body)
    return H, frame("".join(body), H, "d")


def kit_wheel(f, matches):
    """E. The season as a ring of results, the points total as the object."""
    H = 400
    # Ring behind, number in front, exactly as the cover puts the spiral behind
    # the reading. Navy numerals over the ring looked like a hole punched in the
    # season rather than a number, so the number takes the shirt and the ring
    # shows through its counters.
    body = [f'<rect width="{W}" height="{H}" fill="{NAVY}"/>',
            numerals(str(f.points)),
            # Crisp segments behind a big numeral read as damage where they meet
            # its counters: the spiral gets away with it because a loose line looks
            # like texture and a row of blocks looks broken. So the ring sits in
            # front, stamped over the number, and the collision becomes deliberate.
            wheel(matches, 300, 200, 186, 42)]
    body.append(f'<rect x="452" y="0" width="{W - 452}" height="{H}" fill="{NAVY}"/>')
    column(f, body)
    return H, frame("".join(body), H, "e")


def build_kit():
    data = facts()
    f = type("Facts", (), data)
    matches = bf.premier_league(data["season"])
    both = sorted(m for m in matches + bf.champions_league(data["season"])
                  if bf.outcome(m) is not None)
    cards = []
    for name, fn, arg in (("race", kit_race, matches), ("wheel", kit_wheel, both)):
        height, body = fn(f, arg)
        open(os.path.join(HERE, f"kit-{name}.svg"), "w").write(
            svg(height, body, f"Arsenal, champions of the {data['season']} "
                              "Premier League"))
        cards.append(f'<div class="c"><span>{name}</span>'
                     f'<img src="kit-{name}.svg"></div>')
        print(f"kit-{name}.svg  {W}x{height}")
    open(os.path.join(HERE, "kit2.html"), "w").write(
        '<!doctype html><meta charset="utf-8"><style>'
        'body{margin:0;background:#f2f2f2;font:11px/1 -apple-system,sans-serif}'
        '.p{padding:24px 40px;width:900px}.c{margin-bottom:26px}'
        '.c span{display:block;color:#999;text-transform:uppercase;'
        'letter-spacing:.12em;margin-bottom:6px}'
        'img{display:block;width:100%;height:auto}</style>'
        f'<div class="p">{"".join(cards)}</div>')
    print("wrote kit2.html")
