# Handover, 3 August 2026

Two separate pieces of work. One is live on the profile. The other is a design
exploration preserved on `prototype/arsenal-callout`; it is not wired into the
README or present on `main`.

---

## 1. Shipped: the daily cover

**Commit `1f6c036`, live on github.com/jonsut, CI verified green (run 30812864193).**

### The problem it solves

The README opened with about thirty lines of prose before anything dated. Nothing
said the page had been rebuilt that morning, so a reader had no reason to believe
any of it was current. The plates below are deliberately quiet, and quiet turned
out to be indistinguishable from stale.

### What it is

A 900x400 panel at the top of the London section, on the site's yellow, carrying:

- **The reading** as three cropped repeats of yesterday's maximum at 205px
- **The climate spiral** behind it: fourteen years of monthly temperature, month as
  the angle, departure from that month's long-run mean as the radius
- **The headline** "Automatically rebuilt every morning." in the accent colour
- **One generated sentence** stating the reading, the anomaly and where the day
  placed for the date
- **A date stamp and edition number**

The accent is the news: red when the day ran warm against its own date, blue when
it ran cold, on the headline and the spiral together, so the panel reads before a
word of it does. It brings its own ground, so unlike every other graphic on the
page it needs no `prefers-color-scheme` branch.

### Files

| File | What it does |
|---|---|
| `tools/cover.py` | The panel. Typesetting, spiral, sentence, render. |
| `tools/news.py` | London daily maxima since 1940. Fetch, store, update, query. |
| `tools/dateline.py` | Sets the masthead dateline from committed outlines. |
| `tools/build_panel.py` | Runs on Jon's machine where PP Neue Montreal lives; writes `header.svg`, `section-actions.svg` and the three glyph tables. |
| `tools/build_plates.py` | The daily job. Plates, then the cover, then the dateline. |
| `data/*-glyphs.json` | Outlines for display, text and caption. 32KB total. |
| `data/london-daily.json` | 86 years of readings, 147KB. |

### Why the glyph tables exist

CI has no fonts installed and fonts never load inside an `<img>` tag, which is how
GitHub embeds SVG. So `build_panel.py` runs locally, outlines a fixed character
set, and commits the paths. The Action composes type from that table. No font
binary is redistributed, and the panel speaks in one voice rather than falling
back to a system sans.

### The sentence

Generated, never templated. It places the day three ways in descending order of
how much they say, and says nothing rather than reaching for a fourth:

1. `warmest 2nd of August in 8 years` when a record has stood two years or more
2. `the 4th warmest 12th of August in 86 years of records` when it has not, and
   the rank is inside the top ten
3. `That is 3.5 degrees cooler than the same date last year` otherwise

The middle tier used to run down to any rank, which produced "the 37th warmest
18th of August" on two days in five. True, dull, and cut.

Swept over 3,652 days: no failures, never more than three lines, so the layout
cannot overflow.

### Bug fixed on the way

`news.same_date_history` asked every year in the record for 29 February. On 29
February 2028 that would have raised and taken down the whole morning build,
weather and football together, once every four years. Now skipped where the date
does not exist.

### Also changed

- `fetch-depth: 0` in the workflow, because the edition number counts the bot's own
  commits and a shallow clone would publish NO. 1 forever
- Fetches retry with backoff; Open-Meteo returns the occasional 502
- The newest cell on each weather plate is ringed

### Retired

`tools/lede.py` and the sweep-highlight panel it drew are superseded by the cover.
Moved to `preview/lede.py`, unshipped rather than deleted. The candidate-ranking
engine that used to pick the daily sentence moved to `preview/ranking.py` for the
same reason: nothing ships that nothing uses.

---

## 2. Prototype: the Arsenal callout

**Preserved on `prototype/arsenal-callout`. Nothing is wired into the live
profile.** The selected files under `preview/` are force-tracked on this branch;
the rest of the scratch directory remains gitignored.

### Where it got to

Three panels styled as printed shirt backs, in one 900x360 strip:

- **TITLES 14** on home red, with the ermine field
- **POINTS 85** on away navy, with the 1991 print
- **CLEAR 7** on third pale yellow, with diagonals

Plus a CHAMPIONS panel (`way-bone.svg`) that can sit above it.

### Files

| File | What it does |
|---|---|
| `preview/shirts.py` | The three shirt backs. **This is the live one.** |
| `preview/colourways.py` | The split panel in six palettes; defines `ermine()` and `seme()`. |
| `preview/trio.py` | The earlier bone-and-red number strip. |
| `preview/system.py` | The Wimbledon-discipline round: rules, corner marks, edge labels. |
| `preview/parade.py` | The `Shaper` class that sets Northbank. Imported by all of the above. |
| `preview/banana.py` | Three constructions of the away print, side by side, to choose from. |
| `preview/marks.py`, `arsenal_callout.py` | Earlier rounds, superseded. |

The original exports remain in `~/Desktop/Arsenal/exports/`; branch-local copies
are in `preview/exports/` so the remote branch contains the exact review files.

### The route, and the wrong turns

Worth recording because two of them were real errors.

1. **Kit colours, tutu-style tiling.** Rejected: a repeated word is wallpaper, not
   data.
2. **The cover's grammar in kit colours.** Rejected: made the football look like a
   second helping of the weather.
3. **Parade: red, gold, smoke.** Rejected: the gold gradient was overpowering.
4. **Claret and gold, flat.** *Wrong.* Taking "gold" literally as a metal meant
   low-chroma ochre, which forced the red down until it was claret, which is Villa
   and West Ham. One bad decision cascaded into a palette. The deeper error was
   anchoring on the parade photographs instead of the design references, and
   retreating to dark-ground-plus-muted-accent whenever contrast felt risky.
5. **Six colourways, red held at full chroma.** The references never use a
   heritage palette straight: Wimbledon is acid yellow on deep green, the Premier
   League is neon green and aubergine. Bone won.
6. **Shirt backs.** Current.

### Decisions made

- **Ermine, not a crest.** Ermine is a heraldic fur that predates the club by six
  hundred years and belongs to nobody; the crest it appears on is Arsenal's
  trademark. Drawn from scratch on a 24-unit square, so one definition serves a
  26px corner mark and a 30px field.
- **No opponent named.** "Points clear of second place" is true whoever finishes
  there, and recomputes itself. "Ahead of Manchester City" would need maintaining.
- **Colours sampled from shop photographs**, not guessed. Home `#c60922`, away
  `#17203d`, third `#ead08e`, navy `#1b2340`. The fabric red is warmer than the
  brand red.
- **Outline on the words, not the numbers.**

### Open questions

- **Which colourway**, if the CHAMPIONS panel is used above the strip. Bone was
  picked, but the panel's 85 and the away shirt's 85 are the same number twice in
  one composition. Either the panel drops its number, or the strip drops to two.
- **Northbank.** Arsenal's bespoke face. Outlining it into a public README
  distributes the letterforms. Fine as fan use; worth knowing before it ships.
- **14 is hand-maintained.** openfootball only carries recent seasons, so the title
  count and the year of the previous title are constants declared at the top of
  `trio.py`. Everything else on the panel recomputes. On a page whose argument is
  that nothing is stale, that is the one thing a human has to touch.
- **The away pattern** is on its third construction and is close but not exact. The
  bars could step further along the diagonal.
- **Nothing is wired in.** To ship, it follows the cover's path: move the generator
  to `tools/`, commit the Northbank glyph tables it needs, have the Action redraw
  it, splice into the README.

---

## Running things

```bash
cd preview
./.venv/bin/python shirts.py          # or trio.py, colourways.py, banana.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --screenshot=shirts.png \
  --window-size=980,1300 --hide-scrollbars shirts.html
```

The venv lives at `preview/.venv` and is gitignored. It carries `uharfbuzz`,
`fonttools` and `pillow`.

The daily job:

```bash
python3 tools/build_plates.py         # standard library only, no venv needed
python3 tools/build_football.py
./preview/.venv/bin/python tools/build_panel.py   # only when type changes
```

## Gotchas worth remembering

- **Headless Chrome always reports `prefers-color-scheme: dark`.** Screenshots of
  anything with a dark-mode branch come out dark unless the media query is split
  into flat copies first.
- **`--virtual-time-budget` does not advance CSS animations.** A comparison of four
  highlight opacities once came back with four different pill widths because each
  screenshot froze the sweep at a different point.
- **GitHub strips `class`, `style`, `<style>` and `<script>` from README markdown.**
  `<mark>`, `<img>`, `<br>` and `<details>` survive. CSS inside an embedded SVG
  works, because the SVG is its own document.
- **Raw SVG is served with `default-src 'none'; sandbox`.** CSS animation and SMIL
  run; scripts never do.
