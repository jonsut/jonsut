# Third-party artwork

## GitHub Actions logo

`github-actions.svg`, used in `section-actions.svg` to refer to the product it
names. `tools/build_panel.py` strips its two brand blues and refills the paths in
the panel's ink colour. GitHub's brand guidelines ask that their logos not be
recoloured, so if strict compliance matters more than the visual fit, the
Octicons `workflow` icon is MIT-licensed and already monochrome.

## Unicons

The three plate headline icons (`uil-temperature`, `uil-cloud-sun-rain-alt`,
`uil-head-side-mask`) are from [Unicons](https://github.com/Iconscout/unicons) by
Iconscout, under the IconScout Simple License. Commercial use and modification
are both permitted; the only recolour applied here is via `currentColor`, so the
path data is unmodified.

Attribution is encouraged rather than required by that licence, and where it is
given it has to be visible to the reader, so the README credits them in the
footer under the plates rather than only in this file.

The path data is held inline in `tools/build_plates.py` rather than read from
disk, so the daily Action has one less file that can go missing and the licence
comment travels inside every rendered plate.
