"""London's daily maximum temperature since 1940, and the arithmetic on it.

    python3 tools/news.py history   # refetch 1940-now into data/london-daily.json

"28.2°C" is a reading, not news. Nobody comes back for a reading. It becomes news
next to the numbers it beat, which is what this file exists to supply: the whole
record, and the two questions the cover asks of it every morning, what yesterday
was and what every other year did on the same date.

The table is one array per year, positional from 1 January, rather than a map of
dates to readings. Thirty-one thousand ISO date strings cost more than the readings
themselves; dropping them took the committed file from 394KB to 147KB.

Temperature only. A second 86-year series for rainfall would double the file to say
one more kind of sentence, and the plates already carry a rolling window for that.
"""
import json
import os
import statistics
import sys
import urllib.request

import build_plates
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = os.path.join(ROOT, "data", "london-daily.json")
ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
LAT, LON = 51.5072, -0.1276
FIRST_YEAR = 1940
TAIL = 120


def fetch(start, stop):
    url = (f"{ARCHIVE}?latitude={LAT}&longitude={LON}&start_date={start}"
           f"&end_date={stop}&daily=temperature_2m_max&timezone=Europe/London")
    # Shares build_plates.fetch so the retry behaviour lives in one place.
    payload = build_plates.fetch(url)
    daily = payload["daily"]
    return {t: v for t, v in zip(daily["time"], daily["temperature_2m_max"])
            if v is not None}


def store(values):
    """Group by year into arrays indexed from 1 January.

    Positional rather than keyed by date: thirty-one thousand "MM-DD" labels cost
    more than the readings they label, and dropping them takes the committed file
    from 394KB to about 160KB. It only works because the series has no holes, so
    that is checked on the way in rather than assumed. A gap would silently shift
    every reading after it into the wrong day.
    """
    years = {}
    for stamp, value in sorted(values.items()):
        when = date.fromisoformat(stamp)
        index = (when - date(when.year, 1, 1)).days
        row = years.setdefault(str(when.year), [])
        if len(row) != index:
            raise ValueError(f"gap in the series before {stamp}: expected day "
                             f"{len(row)} of {when.year}, got {index}")
        row.append(round(value, 1))
    return years


def rebuild_history():
    stop = date.today() - timedelta(days=1)
    values = fetch(f"{FIRST_YEAR}-01-01", stop)
    payload = {
        "note": "Daily maximum temperature for central London, degrees Celsius.",
        "source": "Open-Meteo ERA5 reanalysis",
        "years": store(values),
    }
    os.makedirs(os.path.dirname(TABLE), exist_ok=True)
    json.dump(payload, open(TABLE, "w"), separators=(",", ":"))
    print(f"wrote {TABLE} ({os.path.getsize(TABLE) / 1024:.0f}KB), "
          f"{len(values)} days from {min(values)} to {max(values)}")


def load():
    return json.load(open(TABLE))


def update(payload):
    """Refresh the recent tail in place and return how many readings moved.

    The tail is refetched whole and spliced by position, so a year that gained days
    since the last run extends rather than growing holes.
    """
    stop = date.today() - timedelta(days=1)
    changed = 0
    # Spliced by day index, not appended. store() cannot be reused here: it insists
    # a year starts on 1 January, which a rolling tail window does not.
    for stamp, value in sorted(fetch(stop - timedelta(days=TAIL), stop).items()):
        when = date.fromisoformat(stamp)
        index = (when - date(when.year, 1, 1)).days
        row = payload["years"].setdefault(str(when.year), [])
        while len(row) <= index:
            row.append(None)
        reading = round(value, 1)
        if row[index] != reading:
            row[index] = reading
            changed += 1
    return changed


def on(payload, when):
    row = payload["years"].get(f"{when:%Y}")
    index = (when - date(when.year, 1, 1)).days
    return row[index] if row and index < len(row) else None


def same_date_history(payload, when):
    """Every year's reading for this calendar date, oldest first.

    29 February exists in roughly one year in four, so the date is asked for and
    quietly skipped where it does not exist rather than assumed to. Left alone this
    raised on the leap day and would have taken the morning's whole build with it,
    once every four years, which is exactly the kind of failure nobody is watching
    for when it finally happens.
    """
    out = []
    for year, row in payload["years"].items():
        try:
            index = (date(int(year), when.month, when.day)
                     - date(int(year), 1, 1)).days
        except ValueError:
            continue
        if index < len(row) and row[index] is not None:
            out.append((int(year), row[index]))
    return sorted(out)


SUFFIX = {1: "st", 2: "nd", 3: "rd"}


def ordinal(n):
    # 11th, 12th and 13th break the last-digit rule and are the classic slip here.
    suffix = "th" if 11 <= n % 100 <= 13 else SUFFIX.get(n % 10, "th")
    return f"{n}{suffix}"


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "history":
        rebuild_history()
    else:
        print("run with 'history' to rebuild the table")
