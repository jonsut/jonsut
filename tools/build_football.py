"""Build the Arsenal plates for the profile README.

    python3 tools/build_football.py

Two sources, two formats, both CC0 and neither needing a key. The Premier League
comes from openfootball/football.json as JSON. The Champions League has no JSON
mirror, so it comes from openfootball/champions-league in their own text format
and is parsed here. The FA Cup and the League Cup are not published by openfootball
in any format, so this is the league and Europe only.

Two seasons are loaded, not one. A rolling 365-day window straddles the summer, so
in August it holds the tail of last season and the first weeks of the new one, and
by spring it is a single campaign. Loading both is also what keeps the plates from
emptying out when openfootball is slow to publish a new season, which it is: across
2025-26 the Premier League file was touched 22 times, and the longest gap between
updates was 97 days. These plates are a season in review, not a live scoreboard.

Bands are deliberately not a linear slice of the number. A league position is not a
quantity, it is a set of thresholds that mean different things to a supporter, and
form is counted in wins rather than deciles so one season reads against another.
"""
import json
import os
import re
import urllib.error
import urllib.request
from datetime import date, timedelta

import build_plates as bp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLUB = "Arsenal FC"
SIZE = 38                            # matches in a Premier League season
PL = "https://raw.githubusercontent.com/openfootball/football.json/master/{}/en.1.json"
CL = "https://raw.githubusercontent.com/openfootball/champions-league/master/{}/cl.txt"

# Arsenal's red, navy and gold.
RED, NAVY, GOLD = "#ef0107", "#063672", "#9c824a"

MONTHS = {m: i + 1 for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
DAY_LINE = re.compile(
    r"^\s{2}(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(\w{3})\s+(\d{1,2})(?:\s+(\d{4}))?\s*$")
MATCH_LINE = re.compile(r"^\s+(?:\d{2}:\d{2}\s+)?(.+?)\s+v\s+(.+?)\s{2,}(\S.*)$")
COUNTRY = re.compile(r"\s*\([A-Z]{3}\)\s*$")


def seasons(today):
    """The season labels a 365-day window ending today can touch, oldest first.

    A season is named for the calendar year it starts in, and starts in August.
    """
    first = today.year if today.month >= 8 else today.year - 1
    return [f"{y}-{str(y + 1)[2:]}" for y in (first - 1, first)]


def fetch(url):
    """The body, or None if the file is not published yet.

    A season directory appears some weeks before its first match and a whole
    competition can be missing, so a 404 is an ordinary state here, not a fault.
    """
    try:
        with urllib.request.urlopen(url, timeout=60) as fh:
            return fh.read().decode()
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return None
        raise


def full_time(match):
    """Final score from a football.json record, or None if not yet played.

    The feed is not internally consistent: most records carry score as
    {"ft": [h, a], "ht": [h, a]}, but 27 of the 380 in 2025-26 carry a bare
    [h, a] instead. Anything reading this source has to handle both.
    """
    score = match.get("score")
    if isinstance(score, dict):
        return score.get("ft")
    return score if isinstance(score, list) else None


def premier_league(label):
    """Every played match as (date, home, away, [goals, goals])."""
    body = fetch(PL.format(label))
    if not body:
        return []
    out = []
    for m in json.loads(body)["matches"]:
        ft = full_time(m)
        if ft:
            out.append((date.fromisoformat(m["date"]), m["team1"], m["team2"], ft))
    return sorted(out)


def champions_league(label):
    """The same shape, parsed out of openfootball's text format.

    Scores appear as "2-0 (1-0)", as "0-0", or for a tie settled on penalties as
    "4-3 pen. 1-1 a.e.t. (1-1, 0-1)". A shootout decides who goes through, so the
    numbers before "pen." are the result that counts, not the 1-1 behind them.
    """
    body = fetch(CL.format(label))
    if not body:
        return []
    out, year, when = [], None, None
    for line in body.splitlines():
        if line.startswith("▪"):
            continue
        day = DAY_LINE.match(line)
        if day:
            month, dom, maybe_year = day.groups()
            year = int(maybe_year) if maybe_year else year
            # A continuation line carries no year, so it inherits the last one.
            when = date(year, MONTHS[month], int(dom)) if year else None
            continue
        game = MATCH_LINE.match(line)
        if not game or when is None:
            continue
        home, away, tail = game.groups()
        pens = re.match(r"(\d+)-(\d+)\s+pen\.", tail)
        goals = pens or re.match(r"(\d+)-(\d+)", tail)
        if goals:
            out.append((when, COUNTRY.sub("", home), COUNTRY.sub("", away),
                        [int(goals.group(1)), int(goals.group(2))]))
    return sorted(out)


def outcome(match, club=CLUB):
    """+1 won, 0 drawn, -1 lost, or None if the club did not play."""
    _, home, away, (hg, ag) = match
    if club == home:
        ours, theirs = hg, ag
    elif club == away:
        ours, theirs = ag, hg
    else:
        return None
    return (ours > theirs) - (ours < theirs)


def table_after(matches, cutoff):
    """Standings and games played, from the matches up to and including cutoff."""
    rows = {}
    for when, home, away, (hg, ag) in matches:
        if when > cutoff:
            continue
        for team, scored, against in ((home, hg, ag), (away, ag, hg)):
            r = rows.setdefault(team, [0, 0, 0, 0])   # points, GD, scored, played
            r[1] += scored - against
            r[2] += scored
            r[3] += 1
            r[0] += 3 if scored > against else (1 if scored == against else 0)
    # Points, then goal difference, then goals scored. The Premier League's real
    # next tiebreak is a playoff, which has never been needed.
    order = sorted(rows, key=lambda t: (-rows[t][0], -rows[t][1], -rows[t][2]))
    return {team: i + 1 for i, team in enumerate(order)}, rows


def title_secured(matches):
    """(date, club) for the moment the league was won, or None if still open.

    Not "who finished first": a title is won when the best case for everyone else
    falls short, which is usually weeks before the last game is played.
    """
    for when in sorted({m[0] for m in matches}):
        ranks, rows = table_after(matches, when)
        leader = min(ranks, key=ranks.get)
        points = rows[leader][0]
        ceiling = max((r[0] + 3 * (SIZE - r[3])
                       for team, r in rows.items() if team != leader), default=0)
        if points > ceiling:
            return when, leader
    return None


def carry(values, until, limit=None):
    """Hold each value forward to the next one, and the last one to `until`.

    Between matches the fact does not change, so carrying it is reporting it
    rather than inventing it. `limit` caps how many days a value may be held for,
    which matters across the summer: a league position survives the close season
    but current form does not, and holding May's figure through July would be an
    answer to a question nobody asked.
    """
    out, days = {}, sorted(values)
    for i, day in enumerate(days):
        nxt = days[i + 1] if i + 1 < len(days) else until + timedelta(days=1)
        stop = min(nxt - timedelta(days=1), until)
        if limit is not None:
            stop = min(stop, day + timedelta(days=limit))
        cursor = day
        while cursor <= stop:
            out[cursor] = values[day]
            cursor += timedelta(days=1)
    return out


# Position is stored as merit rather than rank, so first place is the largest
# number. Bands are cut on ascending values and the legend is drawn in band order,
# so encoding it the other way would put the trophy on the left, against the
# reading of "Won" and "Perfect" on the other two plates.
CHAMPION = 22


def merit(rank):
    return 21 - rank                  # 1st -> 20, 20th -> 1


def main():
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=364)
    labels = seasons(end)

    league = {label: premier_league(label) for label in labels}
    played = sorted(m for label in labels
                    for m in league[label] + champions_league(label)
                    if outcome(m) is not None)
    if not played:
        raise SystemExit(f"no played matches found for {labels}")

    # 1. Results. Four states and no gradation: a 3-0 and a 1-0 are both a win.
    results = {m[0]: outcome(m) for m in played if start <= m[0] <= end}
    won = sum(1 for v in results.values() if v > 0)
    drew = sum(1 for v in results.values() if v == 0)

    # 2. Position, with champions as a state rather than a rank. Gold means
    # holding the trophy, which outlives the season that won it and ends only when
    # someone else takes it, so it runs through the summer into the next campaign.
    position, reign = {}, None
    for label in labels:
        matches = league[label]
        if not matches:
            continue
        ours = {}
        for day in sorted({m[0] for m in matches}):
            ranks, _ = table_after(matches, day)
            if CLUB in ranks:
                ours[day] = merit(ranks[CLUB])
        position.update(carry(ours, min(end, max(ours) if ours else end)))
        won_by = title_secured(matches)
        if won_by:
            # A new champion ends the previous reign, whoever it is.
            reign = won_by if won_by[1] == CLUB else None
    if reign:
        cursor = max(reign[0], start)
        while cursor <= end:
            position[cursor] = CHAMPION
            cursor += timedelta(days=1)
    position = {d: v for d, v in position.items() if start <= d <= end}

    # 3. Form. Points from the last five matches out of a possible fifteen, across
    # both competitions, so a European run counts the way a supporter counts it.
    run, by_match = [], {}
    for m in played:
        got = outcome(m)
        run.append(3 if got > 0 else (1 if got == 0 else 0))
        if len(run) >= 5:
            by_match[m[0]] = sum(run[-5:])
    # Capped twice. 28 days is longer than any in-season gap (the longest in
    # 2025-26 was 21, over an international break) and far shorter than the close
    # season, so an interior break holds but the summer does not. Stopping at the
    # last match played also keeps the plate blank once the season is over, which
    # is honest: with no next fixture there is no current form.
    form = {d: v for d, v in carry(by_match, max(by_match), limit=28).items()
            if start <= d <= end}

    champion_line = (f"Champions. Title secured on {reign[0]:%-d %B %Y}"
                     if reign else "Season in progress")
    specs = {
        "results": dict(
            title="Arsenal results", label="Arsenal Results.", series=results,
            cuts=[0, 1], ends=("Lost", "Won"),
            hues=[NAVY, NAVY, RED], alpha=[0.80, 0.38, 0.85],
            head=f"{won} won, {drew} drawn, {len(results) - won - drew} lost "
                 f"in {len(results)} matches",
            note="Premier League and Champions League. Blank days had no match"),
        "position": dict(
            title="Arsenal league position", label="Arsenal Position.", series=position,
            # Bottom half, mid-table, top six, 2nd, 1st, champions. Written as
            # merit() so the thresholds still read as league positions here.
            cuts=[merit(11) + 1, merit(7) + 1, merit(3) + 1, merit(2) + 1, CHAMPION],
            ends=("Bottom half", "Champions"),
            hues=[bp.GREY, bp.NEUTRAL, RED, RED, RED, GOLD],
            alpha=[0.55, 0.30, 0.24, 0.52, 0.85, 0.95],
            head=champion_line,
            note="Position after each matchday, held until the next. "
                 "Gold is the trophy, not the table"),
        "form": dict(
            title="Arsenal form", label="Arsenal Form.", series=form,
            # Counted in wins: a win or fewer, two, three, four, then a perfect
            # five. Absolute thresholds mean one season reads against another,
            # which banding on this season's own spread would destroy.
            cuts=[5, 9, 12, 15], ends=("Poor", "Perfect"),
            hues=[NAVY, NAVY, bp.NEUTRAL, RED, RED],
            # The middle band carries more weight than on the weather plates.
            # There a faint neutral means "nothing to see"; here a dip in form is
            # the thing worth seeing, and at 0.15 it vanished into the empty cells.
            alpha=[0.75, 0.40, 0.30, 0.55, 0.90],
            # Described from the plate, not the source: by_match spans both loaded
            # seasons, and quoting its range would caption days that are not drawn.
            head=f"Best run {max(form.values())} points from five, "
                 f"worst {min(form.values())}, across {len(results)} matches",
            note="Points won in the previous five matches, out of a possible 15. "
                 "Three for a win, one for a draw"),
    }

    for key, spec in specs.items():
        path = os.path.join(ROOT, f"arsenal-{key}.svg")
        h = bp.render(key, spec, start, end, path)
        filled = len(spec["series"])
        print(f"arsenal-{key}.svg  {bp.W}x{h}  {filled}/365 days  |  {spec['head']}")
    print(f"seasons {labels}, {len(played)} matches played")


if __name__ == "__main__":
    main()
