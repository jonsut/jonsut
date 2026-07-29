# Header panel

`header.svg` is generated, not hand-drawn. Regenerate it with:

    python3 -m venv venv
    ./venv/bin/pip install uharfbuzz fonttools
    ./venv/bin/python tools/build_panel.py

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

## Accessibility

The SVG carries `role="img"`, an `aria-label` and a `<title>`. Because the text
is outlined there is no selectable text layer, so the `alt` attribute in the
README is the only thing a screen reader or a search engine sees. Keep it in
sync with the wording in the panel.
