# Typeset panels

`header.svg` and `section-actions.svg` are generated, not hand-drawn. Both come
out of one run:

    python3 -m venv preview/.venv
    ./preview/.venv/bin/pip install uharfbuzz fonttools
    ./preview/.venv/bin/python tools/build_panel.py

`preview/` is gitignored, so the venv lives beside the other scratch artefacts
rather than in the repo root. Building needs PP Neue Montreal installed locally,
which is why this is a manual step and not part of the daily Action.

To check both themes, `preview/section_preview.py` writes flattened light and
dark copies. Headless Chrome reports `prefers-color-scheme: dark`, so a naive
screenshot only ever shows one branch of the media query.

## Why it is built this way

The panel is committed as a static file rather than fetched at view time. That is
the only arrangement that fails softly: if the generator breaks, the last good
file keeps rendering, instead of the profile showing a broken image.

Text is shaped with HarfBuzz and written out as outlines. Fonts are never loaded
when an SVG renders inside an `<img>` tag, which is how GitHub embeds images, so
live text would fall back to Times New Roman. Outlining also avoids shipping a
font binary, which the PP Neue Montreal licence would not permit.

Colours are set by CSS inside the SVG. GitHub strips `<style>` from the README
document itself, but not from a proxied image, so the file carries its own
`prefers-color-scheme` rules and adapts to light and dark. Note this follows the
reader's browser or OS theme, not their GitHub theme picker, so the two can
disagree if someone has overridden it in GitHub settings.

The mark uses fixed colours rather than `currentColor`, because CSS custom
properties and `currentColor` do not cross the `img` document boundary. The
source of truth for the identity assets is `site/public/identity/` in the
website repo.

## Plates

`build_plates.py` renders the London plates and owns the shared drawing code:
the grid, the bands, the legend and the headline icons. `build_football.py`
imports it and supplies its own series. Both are standard library only, so the
daily Action installs nothing and there is no dependency to rot.

`build_football.py` loads two seasons rather than one, because a rolling 365-day
window straddles the summer. That also stops the plates emptying when openfootball
is slow to publish, which it is: the 2025-26 Premier League file was updated 22
times all season and once went 97 days without a change. Treat these as a season
in review, not a live scoreboard. A missing season directory returns 404 and is
handled as an ordinary state.

## Third-party artwork

`assets/github-actions.svg` is GitHub's Actions logo, used here to refer to the
product it names. The build strips its two brand blues and refills the paths in
the panel's ink colour so it reads as a glyph beside the type. GitHub's brand
guidelines ask that their logos not be recoloured; if that matters, the Octicons
`workflow` icon is MIT-licensed and already monochrome.

## Accessibility

The SVG carries `role="img"`, an `aria-label` and a `<title>`. Because the text
is outlined there is no selectable text layer, so the `alt` attribute in the
README is the only thing a screen reader or a search engine sees. Keep it in
sync with the wording in the panel.
