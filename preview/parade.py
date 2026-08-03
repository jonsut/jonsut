"""The football callout as the parade, not as a chart.

The weather cover's grammar is a cropped numeral, a generated mark and a cleared
column. Repeating it here would make the football a second helping of the same
dish, so this borrows nothing from it: red ground, smoke, gold, centred type, and
the season laid along the bottom edge as the only measured thing on the panel.

Type is Northbank, Arsenal's own face, which is why this stays a local experiment
until Jon decides what to do about that. The crest is deliberately absent.

The data is still real. Every league match of the season is a bar: gold for a win,
white for a draw, and a burnt stub for a defeat, in the order they were played.
"""
import os
import sys
from datetime import date, timedelta

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_football as bf   # noqa: E402
import cover                  # noqa: E402

FONTS = os.path.expanduser("~/Desktop/fonts")
N7 = f"{FONTS}/Northbank-N7.ttf"
FORWARD = f"{FONTS}/Northbank-Forward.ttf"

W = 900
RED = "#e40b16"        # the parade bus, a shade deeper than the shirt red
DEEP = "#8e0009"       # the shadow side of the smoke
GOLD_DARK, GOLD_MID, GOLD_LIGHT = "#8a6a12", "#e8c65c", "#fff3c4"
WHITE = "#ffffff"

L = cover.TABLES["lede"]


class Shaper:
    def __init__(self, path):
        self.face = hb.Face(hb.Blob.from_file_path(path))
        self.font = hb.Font(self.face)
        self.tt = TTFont(path)
        self.upem = self.face.upem
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()

    def run(self, text, size, x, y, fill, tracking=0.0, anchor="start"):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {"liga": False, "clig": False})
        track = tracking * self.upem
        pen, parts = 0.0, []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            pathpen = SVGPathPen(self.glyphs)
            self.glyphs[self.order[info.codepoint]].draw(pathpen)
            d = pathpen.getCommands()
            if d:
                parts.append(f'<path d="{d}" transform="translate('
                             f'{round(pen + pos.x_offset)} {round(pos.y_offset)})"/>')
            pen += pos.x_advance + track
        width = (pen - track) * size / self.upem
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        scale = size / self.upem
        return (f'<g fill="{fill}" transform="translate({x:.1f} {y:.1f}) '
                f'scale({scale:.6f} {-scale:.6f})">' + "".join(parts) + "</g>"), width

    def width(self, text, size, tracking=0.0):
        _, w = self.run(text, size, 0, 0, "#000", tracking)
        return w


def defs():
    """Gold leaf, and the smoke that hangs over a parade."""
    return f"""<defs>
<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{GOLD_LIGHT}"/>
  <stop offset="0.34" stop-color="{GOLD_MID}"/>
  <stop offset="0.52" stop-color="{GOLD_DARK}"/>
  <stop offset="0.62" stop-color="{GOLD_MID}"/>
  <stop offset="1" stop-color="{GOLD_LIGHT}"/>
</linearGradient>
<radialGradient id="plumeA" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="#ff9aa2" stop-opacity="0.85"/>
  <stop offset="1" stop-color="#ff9aa2" stop-opacity="0"/>
</radialGradient>
<radialGradient id="plumeB" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="{DEEP}" stop-opacity="0.8"/>
  <stop offset="1" stop-color="{DEEP}" stop-opacity="0"/>
</radialGradient>
<filter id="smoke" x="-20%" y="-20%" width="140%" height="140%">
  <!-- Real turbulence rather than a blurred blob: flare smoke has grain, and a
       gradient alone reads as a lighting effect. -->
  <feTurbulence type="fractalNoise" baseFrequency="0.008 0.014" numOctaves="4"
                seed="7" result="noise"/>
  <feColorMatrix in="noise" type="matrix" result="tinted"
     values="0 0 0 0 1
             0 0 0 0 0.62
             0 0 0 0 0.66
             0 0 0 0.55 -0.08"/>
  <feGaussianBlur in="tinted" stdDeviation="6" result="soft"/>
  <feComposite in="soft" in2="SourceGraphic" operator="in"/>
</filter>
</defs>"""


def haze(height):
    """Plumes drifting across the red, cropped by the frame like the photographs."""
    return (f'<ellipse cx="120" cy="{height * 0.22:.0f}" rx="330" ry="200" '
            'fill="url(#plumeA)" opacity="0.55"/>'
            f'<ellipse cx="760" cy="{height * 0.8:.0f}" rx="380" ry="230" '
            'fill="url(#plumeA)" opacity="0.45"/>'
            f'<ellipse cx="470" cy="{height * 1.05:.0f}" rx="420" ry="180" '
            'fill="url(#plumeB)" opacity="0.7"/>'
            f'<rect width="{W}" height="{height}" filter="url(#smoke)" '
            'opacity="0.72"/>')


def season():
    end = date.today() - timedelta(days=1)
    labels = bf.seasons(end)
    league = {label: bf.premier_league(label) for label in labels}
    current = next(label for label in reversed(labels) if league[label])
    matches = league[current]
    ranks, table = bf.table_after(matches, max(m[0] for m in matches))
    ours = sorted(m for m in matches
                  if bf.CLUB in (m[1], m[2]) and bf.outcome(m) is not None)
    secured = bf.title_secured(matches)
    return {
        "label": current, "short": current[2:4] + "/" + current[-2:],
        "points": table[bf.CLUB][0],
        "won": sum(1 for m in ours if bf.outcome(m) > 0),
        "drew": sum(1 for m in ours if bf.outcome(m) == 0),
        "lost": sum(1 for m in ours if bf.outcome(m) < 0),
        "results": [bf.outcome(m) for m in ours],
        "secured": secured[0] if secured else None,
        "matches": len(ours),
    }


def bars(results, x, baseline, width, tall):
    """Every match of the season, in order, as a bar of the points it won.

    Along the bottom edge rather than in a chart: it is a strip of colour first and
    a record second, which is the right way round for a panel about a parade. Three
    heights, three colours, thirty-eight of them, and you can find the run that won
    it without being told where to look.
    """
    gap = 3
    unit = (width - gap * (len(results) - 1)) / len(results)
    out = []
    for i, got in enumerate(results):
        points = 3 if got > 0 else (1 if got == 0 else 0)
        height = {3: tall, 1: tall * 0.45, 0: tall * 0.18}[points]
        fill = {3: "url(#gold)", 1: WHITE, 0: DEEP}[points]
        out.append(f'<rect x="{x + i * (unit + gap):.1f}" '
                   f'y="{baseline - height:.1f}" width="{unit:.1f}" '
                   f'height="{height:.1f}" fill="{fill}" '
                   f'opacity="{1 if points else 0.85}"/>')
    return "".join(out)


def svg(height, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" '
            f'width="{W}" height="{height}" role="img" aria-label="{label}">'
            f"<title>{label}</title>{defs()}"
            f'<clipPath id="f"><rect width="{W}" height="{height}"/></clipPath>'
            f'<g clip-path="url(#f)">{body}</g></svg>\n')


def bus(s, forward, n7):
    """A. The bus livery: one word, gold, with the season stacked beside it."""
    H = 330
    body = [f'<rect width="{W}" height="{H}" fill="{RED}"/>', haze(H)]
    word, width = forward.run("CHAMPIONS", 128, 48, 196, "url(#gold)",
                              tracking=-0.01)
    body.append(word)
    x = 48 + width + 26
    top, _ = n7.run(s["short"][:2], 76, x, 148, "url(#gold)")
    bottom, _ = n7.run(s["short"][3:], 76, x, 214, "url(#gold)")
    body += [top, bottom]
    line = (f"{s['points']} points. {s['won']} won, {s['drew']} drawn, "
            f"{s['lost']} lost. Title secured {s['secured']:%-d %B %Y}.")
    body.append(cover.run(line, L, 15, 48, 246, WHITE))
    body.append(bars(s["results"], 48, H - 34, W - 96, 44))
    return H, "".join(body)


def flare(s, forward, n7):
    """B. Centred, with the season burning along the bottom edge."""
    H = 360
    body = [f'<rect width="{W}" height="{H}" fill="{RED}"/>', haze(H)]
    # The bars are the floor the type stands on, so they stop where the copy
    # starts. Running the caption across them put white text on gold and lost both.
    body.append(bars(s["results"], 40, H - 28, W - 80, 92))
    word, _ = forward.run("CHAMPIONS", 132, W / 2, 172, "url(#gold)",
                          tracking=-0.01, anchor="middle")
    body.append(word)
    label, _ = n7.run(f"ARSENAL  {s['short']}", 21, W / 2, 78, WHITE,
                      tracking=0.22, anchor="middle")
    body.append(label)
    line = (f"{s['points']} points. {s['won']} won, {s['drew']} drawn, "
            f"{s['lost']} lost. Title secured {s['secured']:%-d %B %Y}.")
    width = cover.measure(line, L, 15)
    body.append(cover.run(line, L, 15, (W - width) / 2, 214, WHITE))
    return H, "".join(body)


def build():
    s = season()
    print({k: v for k, v in s.items() if k != "results"})
    forward, n7 = Shaper(FORWARD), Shaper(N7)
    cards = []
    for name, fn in (("bus", bus), ("flare", flare)):
        height, body = fn(s, forward, n7)
        label = (f"Arsenal, champions of the {s['label']} Premier League with "
                 f"{s['points']} points")
        open(os.path.join(HERE, f"parade-{name}.svg"), "w").write(
            svg(height, body, label))
        cards.append(f'<div class="c"><span>{name}</span>'
                     f'<img src="parade-{name}.svg"></div>')
        print(f"parade-{name}.svg  {W}x{height}")
    open(os.path.join(HERE, "parade.html"), "w").write(
        '<!doctype html><meta charset="utf-8"><style>'
        'body{margin:0;background:#f2f2f2;font:11px/1 -apple-system,sans-serif}'
        '.p{padding:24px 40px;width:900px}.c{margin-bottom:26px}'
        '.c span{display:block;color:#999;text-transform:uppercase;'
        'letter-spacing:.12em;margin-bottom:6px}'
        'img{display:block;width:100%;height:auto}</style>'
        f'<div class="p">{"".join(cards)}</div>')
    print("wrote parade.html")


if __name__ == "__main__":
    build()
