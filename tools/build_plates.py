"""Build the London climate plates for the profile README.

Two modes:

    python3 tools/build_plates.py normals   # rebuild data/normals.json (rarely)
    python3 tools/build_plates.py           # render the plates (daily)

The baselines are large: thirty years of daily weather and eleven years of hourly
air quality, about 2.5MB of JSON. Refetching those every day would be wasteful and
would make the job fragile, so they are reduced once to a day-of-year table of
normals, committed as data/normals.json, and the daily run fetches only the last
year. Normals are smoothed over a +/-7 day window so one freak year cannot distort a
single calendar day.

Colour encodes departure from normal rather than absolute value. That makes the
scale signed, which suits temperature in Celsius, and it means the same palette
carries direction across all three plates. Full-chroma hues with opacity doing the
work, so cells composite against the page and one file serves light and dark; only
text needs a theme override.
"""
import json
import os
import statistics
import sys
import urllib.request
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
LAT, LON = 51.5072, -0.1276          # central London
BASE_FROM, BASE_TO = "1991-01-01", "2020-12-31"   # WMO standard reference period
AQ_FROM, AQ_TO = "2015-01-01", "2025-12-31"       # CAMS European reanalysis starts 2013
LEAD = 30                            # extra days so the first rolling window is whole
REF = date(2001, 1, 1)               # non-leap reference year for day-of-year keys

ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
AIR = "https://air-quality-api.open-meteo.com/v1/air-quality"


def fetch(url):
    with urllib.request.urlopen(url, timeout=180) as fh:
        return json.load(fh)


def doy(d):
    """Day-of-year index on a fixed non-leap year; 29 Feb folds onto 28 Feb."""
    day = 28 if (d.month == 2 and d.day == 29) else d.day
    return (date(REF.year, d.month, day) - REF).days


def smooth_normals(pairs, window=7):
    buckets = {i: [] for i in range(365)}
    for when, value in pairs:
        if value is None:
            continue
        centre = doy(when)
        for offset in range(-window, window + 1):
            buckets[(centre + offset) % 365].append(value)
    return [statistics.mean(v) if v else None for _, v in sorted(buckets.items())]


def daily_means(payload, field):
    out = {}
    for stamp, value in zip(payload["hourly"]["time"], payload["hourly"][field]):
        if value is not None:
            out.setdefault(stamp[:10], []).append(value)
    return {date.fromisoformat(k): statistics.mean(v) for k, v in out.items()}


def as_dates(payload, field):
    return {
        date.fromisoformat(t): v
        for t, v in zip(payload["daily"]["time"], payload["daily"][field])
    }


def rebuild_normals():
    os.makedirs(DATA, exist_ok=True)
    wx = fetch(f"{ARCHIVE}?latitude={LAT}&longitude={LON}&start_date={BASE_FROM}"
               f"&end_date={BASE_TO}&daily=temperature_2m_max,precipitation_sum"
               "&timezone=Europe/London")
    aq = fetch(f"{AIR}?latitude={LAT}&longitude={LON}&start_date={AQ_FROM}"
               f"&end_date={AQ_TO}&hourly=pm2_5&domains=cams_europe"
               "&timezone=Europe/London")
    temp = smooth_normals(list(as_dates(wx, "temperature_2m_max").items()))
    rain = smooth_normals(list(as_dates(wx, "precipitation_sum").items()))
    pm = smooth_normals(list(daily_means(aq, "pm2_5").items()))
    payload = {
        "note": "Day-of-year normals, smoothed over +/-7 days. Index 0 is 1 January.",
        "temperature_baseline": f"{BASE_FROM[:4]}-{BASE_TO[:4]}",
        "particulates_baseline": f"{AQ_FROM[:4]}-{AQ_TO[:4]}",
        "temperature": [round(v, 3) for v in temp],
        "rainfall": [round(v, 4) for v in rain],
        "particulates": [round(v, 3) for v in pm],
    }
    out = os.path.join(DATA, "normals.json")
    json.dump(payload, open(out, "w"), indent=1)
    size = os.path.getsize(out)
    print(f"wrote {out} ({size / 1024:.0f}KB) from {BASE_FROM}-{BASE_TO} "
          f"and {AQ_FROM}-{AQ_TO}")


# --------------------------------------------------------------------- rendering

FONT = ('-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", '
        "Helvetica, Arial, sans-serif")
TEAL, CORAL, NEUTRAL, GREY, GREEN = "#3f8b92", "#fc4b34", "#8c9196", "#57606a", "#3f925d"
ALPHA = [0.75, 0.34, 0.15, 0.34, 0.75]

W, PAD, DAY_GUTTER = 900, 16, 38
CELL, GAP, RADIUS = 12, 3, 2
STEP = CELL + GAP
HEAD_H = 34
GRID_X = PAD + DAY_GUTTER
DAY_LABELS = {0: "Mon", 2: "Wed", 4: "Fri"}


def band(value, cuts):
    return next((i for i, cut in enumerate(cuts) if value < cut), len(cuts))


def month_ticks(start, end):
    marks, seen, cursor = [], set(), start
    while cursor <= end:
        stamp = cursor.strftime("%Y-%m")
        if stamp not in seen:
            seen.add(stamp)
            marks.append((cursor, cursor.strftime("%b")))
        cursor += timedelta(days=1)
    return marks[1:]


def render(key, spec, start, end, path):
    ns, hues, cuts = key[0], spec["hues"], spec["cuts"]
    first_monday = start - timedelta(days=start.weekday())
    parts = [f'<text class="head" x="0" y="{HEAD_H - 12}">{spec["head"]}</text>']

    card_top = HEAD_H
    y = card_top + PAD + 12
    for when, name in month_ticks(start, end):
        col = (when - first_monday).days // 7
        parts.append(f'<text class="axis" x="{GRID_X + col * STEP}" y="{y}">{name}</text>')
    y += 10

    for row, text in DAY_LABELS.items():
        parts.append(f'<text class="axis end" x="{GRID_X - 8}" '
                     f'y="{y + row * STEP + CELL - 2}">{text}</text>')

    cursor = start
    while cursor <= end:
        value = spec["series"].get(cursor)
        x = GRID_X + ((cursor - first_monday).days // 7) * STEP
        cy = y + cursor.weekday() * STEP
        cls = f"{ns}-void" if value is None else f"{ns}{band(value, cuts)}"
        parts.append(f'<rect class="{cls}" x="{x}" y="{cy}" width="{CELL}" '
                     f'height="{CELL}" rx="{RADIUS}"/>')
        cursor += timedelta(days=1)

    foot = y + 7 * STEP - GAP + 20
    parts.append(f'<text class="note" x="{GRID_X}" y="{foot}">{spec["note"]}</text>')
    low, high = spec["ends"]
    sw = len(hues) * (CELL + 3)
    lx = W - PAD - 8 - sw - 46
    parts.append(f'<text class="note end" x="{lx - 6}" y="{foot}">{low}</text>')
    for i in range(len(hues)):
        parts.append(f'<rect class="{ns}{i}" x="{lx + i * (CELL + 3)}" '
                     f'y="{foot - CELL + 2}" width="{CELL}" height="{CELL}" rx="{RADIUS}"/>')
    parts.append(f'<text class="note" x="{lx + sw + 3}" y="{foot}">{high}</text>')

    card_bottom = foot + PAD
    parts.insert(1, f'<rect class="card" x="0.5" y="{card_top + 0.5}" '
                    f'width="{W - 1}" height="{card_bottom - card_top}" rx="6"/>')
    height = card_bottom + 2

    style = (f"text {{ font-family: {FONT}; }}\n"
             ".head { font-size: 16px; fill: #1f2328; }\n"
             ".axis { font-size: 12px; fill: #1f2328; }\n"
             ".note { font-size: 12px; fill: #59636e; }\n"
             ".end { text-anchor: end; }\n"
             ".card { fill: none; stroke: #d1d9e0; stroke-width: 1; }\n"
             ".%s-void { fill: %s; fill-opacity: 0.10; }\n" % (ns, NEUTRAL))
    for i, colour in enumerate(hues):
        style += ".%s%d { fill: %s; fill-opacity: %.2f; }\n" % (ns, i, colour, ALPHA[i])
    style += ("@media (prefers-color-scheme: dark) {\n"
              "  .head, .axis { fill: #f0f6fc; }\n"
              "  .note { fill: #9198a1; }\n"
              "  .card { stroke: #3d444d; }\n"
              "}\n")

    label = f'{spec["title"]} in London. {spec["head"]}. {spec["note"]}.'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" '
           f'width="{W}" height="{height}" role="img" aria-label="{label}">\n'
           f'<title>{spec["title"]} in London</title>\n<style>{style}</style>\n'
           + "\n".join(parts) + "\n</svg>\n")
    open(path, "w").write(svg)
    return height


def main():
    normals = json.load(open(os.path.join(DATA, "normals.json")))
    end = date.today() - timedelta(days=1)      # yesterday is the last complete day
    start = end - timedelta(days=364)

    wx = fetch(f"{ARCHIVE}?latitude={LAT}&longitude={LON}"
               f"&start_date={start - timedelta(days=LEAD)}&end_date={end}"
               "&daily=temperature_2m_max,precipitation_sum&timezone=Europe/London")
    aq = fetch(f"{AIR}?latitude={LAT}&longitude={LON}&start_date={start}&end_date={end}"
               "&hourly=pm2_5&domains=cams_europe&timezone=Europe/London")

    temp = as_dates(wx, "temperature_2m_max")
    rain = as_dates(wx, "precipitation_sum")
    pm = daily_means(aq, "pm2_5")

    temp_anom = {d: v - normals["temperature"][doy(d)]
                 for d, v in temp.items() if v is not None and d >= start}
    pm_anom = {d: v - normals["particulates"][doy(d)]
               for d, v in pm.items() if d >= start}

    # Rainfall deliberately uses a 30-day rolling total rather than a daily anomaly.
    # The median London day is dry while the mean is pulled up by wet days, so a daily
    # anomaly would mark almost every day "below average". Rolling totals show spells,
    # which is how rainfall is actually discussed.
    norm30 = {i: sum(normals["rainfall"][(i - k) % 365] for k in range(30))
              for i in range(365)}
    days = sorted(rain)
    rain_ratio = {}
    for i, d in enumerate(days):
        if d < start or i < LEAD:
            continue
        window = [rain[x] for x in days[i - 29:i + 1] if rain[x] is not None]
        expected = norm30[doy(d)]
        if len(window) == 30 and expected:
            rain_ratio[d] = sum(window) / expected

    tb, pb = normals["temperature_baseline"], normals["particulates_baseline"]
    t_mean = statistics.mean(temp_anom.values())
    r_mean = statistics.mean(rain_ratio.values())
    p_mean = statistics.mean(pm_anom.values())

    specs = {
        "temperature": dict(
            title="Temperature", series=temp_anom, cuts=[-2.5, -1, 1, 3],
            ends=("Cooler", "Warmer"), hues=[TEAL, TEAL, NEUTRAL, CORAL, CORAL],
            head=f"{abs(t_mean):.1f}°C {'above' if t_mean >= 0 else 'below'} "
                 "average in the last year",
            note=f"Daily maximum against the {tb} normal"),
        "rainfall": dict(
            title="Rainfall", series=rain_ratio, cuts=[0.5, 0.8, 1.25, 2.0],
            ends=("Drier", "Wetter"), hues=[GREY, GREY, NEUTRAL, TEAL, TEAL],
            head=f"{abs(r_mean - 1) * 100:.0f}% {'more' if r_mean >= 1 else 'less'} "
                 "rain than average in the last year",
            note=f"30-day totals against the {tb} normal"),
        "particulates": dict(
            title="Fine particulates", series=pm_anom, cuts=[-6, -4, -2, 0],
            ends=("Cleaner", "Dirtier"), hues=[GREEN, GREEN, NEUTRAL, GREY, GREY],
            head=f"{abs(p_mean):.1f} µg/m³ {'cleaner' if p_mean < 0 else 'dirtier'} "
                 "than average in the last year",
            note=f"PM2.5 daily mean against the {pb} normal"),
    }

    for key, spec in specs.items():
        path = os.path.join(ROOT, f"london-{key}.svg")
        h = render(key, spec, start, end, path)
        print(f"london-{key}.svg  {W}x{h}  {len(spec['series'])} days  |  {spec['head']}")

    line = (f"Yesterday in London: {temp[end]:.1f}°C, {rain[end]:.1f}mm of rain, "
            f"PM2.5 at {pm[end]:.0f} µg/m³.")
    update_readme(line)
    print(line)


def update_readme(line):
    """Replace the marked block in README.md, leaving the rest untouched."""
    path = os.path.join(ROOT, "README.md")
    start_tag, end_tag = "<!-- TODAY:START -->", "<!-- TODAY:END -->"
    text = open(path).read()
    if start_tag not in text:
        print("no TODAY markers in README, skipping text update")
        return
    before = text.split(start_tag)[0]
    after = text.split(end_tag)[1]
    open(path, "w").write(f"{before}{start_tag}\n{line}\n{end_tag}{after}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "normals":
        rebuild_normals()
    else:
        main()
