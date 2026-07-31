"""Generate the profile header panel as a self-contained SVG.

Text is shaped with HarfBuzz and emitted as outlines, because fonts are never
loaded when an SVG renders inside an <img> tag, which is how GitHub embeds it.
Outlines also mean no font binary is redistributed.
"""

import os

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Paths are derived rather than absolute: this file is public, and hard-coded
# home directories disclose a username and local layout for no benefit.
FONTS = os.path.expanduser("~/Library/Fonts")
# Identity assets live in the website repo; override if it sits elsewhere.
IDENTITY = os.environ.get(
    "JONMARK_SVG",
    os.path.expanduser("~/IdeaProjects/jonsut/site/public/identity/jon-avatar.svg"),
)
DISPLAY_SEMIBOLD = f"{FONTS}/PPNeueMontreal-Semibold.otf"
DISPLAY_REGULAR = f"{FONTS}/PPNeueMontreal-Regular.otf"
TEXT_BOOK = f"{FONTS}/PPNeueMontrealText-Book.otf"


class Shaper:
    def __init__(self, path):
        self.face = hb.Face(hb.Blob.from_file_path(path))
        self.hbfont = hb.Font(self.face)
        self.tt = TTFont(path)
        self.upem = self.face.upem
        self.glyphset = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()

    def run(self, text, size, x, y, tracking=0.0, cls=None):
        """Return (svg_group, advance_width). Tracking is in em, like CSS letter-spacing."""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        # House style disables ligatures so shapes stay predictable.
        hb.shape(self.hbfont, buf, {"liga": False, "clig": False, "dlig": False})

        track_units = tracking * self.upem
        pen_x = 0.0
        glyphs = []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            name = self.order[info.codepoint]
            pen = SVGPathPen(self.glyphset)
            self.glyphset[name].draw(pen)
            d = pen.getCommands()
            if d:
                gx = round(pen_x + pos.x_offset)
                gy = round(pos.y_offset)
                shift = f' transform="translate({gx} {gy})"' if (gx or gy) else ""
                glyphs.append(f'<path d="{d}"{shift}/>')
            pen_x += pos.x_advance + track_units

        scale = size / self.upem
        attrs = f' class="{cls}"' if cls else ""
        group = (
            f'<g{attrs} transform="translate({x} {y}) scale({scale:.6f} {-scale:.6f})">'
            + "".join(glyphs)
            + "</g>"
        )
        return group, pen_x * scale


# ---------------------------------------------------------------- composition

W, H = 900, 176
MARK_SIZE = 68
TEXT_X = 92

name_run, _ = Shaper(DISPLAY_SEMIBOLD).run("Jon Sutton", 44, TEXT_X, 58, cls="ink")
tagline_run, _ = Shaper(TEXT_BOOK).run(
    "Software engineer with roots in research, design and creative technology",
    17.5,
    TEXT_X,
    88,
    cls="muted",
)
label_run, label_w = Shaper(DISPLAY_REGULAR).run(
    "APPLIED AI · REAL-TIME SYSTEMS · INTERFACE DESIGN",
    11.5,
    0,
    154,
    tracking=0.11,
    cls="label",
)

# The two-colour mark, fixed-colour because CSS variables and currentColor do not
# cross the img document boundary (see site/public/identity/README.md).
BLOB = (
    "M81.115 5.46564C155.505 -2.35309 166.716 6.72484 174.534 81.1151C182.353 155.505 "
    "173.275 166.716 98.8849 174.534C24.4946 182.353 13.2843 173.275 5.46561 "
    "98.8849C-2.35312 24.4947 6.72481 13.2844 81.115 5.46564Z"
)

with open(IDENTITY) as fh:
    avatar = fh.read()
face_path = avatar.split('class="jon-avatar__foreground" d="')[1].split('"')[0]

mark_scale = MARK_SIZE / 180
mark = (
    f'<g transform="translate(0 6) scale({mark_scale:.6f})">'
    f'<path d="{BLOB}" fill="#f9ff47"/>'
    f'<path d="{face_path}" fill="#171717"/>'
    "</g>"
)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Jon Sutton, software engineer with roots in research, design and creative technology">
<title>Jon Sutton</title>
<style>
.ink {{ fill: #111111; }}
.muted {{ fill: #63656f; }}
.label {{ fill: #55575f; }}
.rule {{ stroke: #b5b5b5; }}
@media (prefers-color-scheme: dark) {{
  .ink {{ fill: #e8e8ea; }}
  .muted {{ fill: #9ea0a9; }}
  .label {{ fill: #8b8d96; }}
  .rule {{ stroke: #33383f; }}
}}
</style>
{mark}
{name_run}
{tagline_run}
<line class="rule" x1="0" y1="126" x2="{W}" y2="126" stroke-width="1"/>
{label_run}
</svg>
"""

out = os.path.join(ROOT, "header.svg")
with open(out, "w") as fh:
    fh.write(svg)
print(f"wrote {out} ({len(svg)} bytes), label run width {label_w:.1f}px")
