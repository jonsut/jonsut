"""Count daily Claude Code activity from local session transcripts.

Parked, but kept running as a log. Its output, data/agent-days.json, is gitignored
and stays on this machine. Publishing a daily activity graph would disclose working
patterns, and gaps in it invite inference, so nothing here goes public until that is
a deliberate decision rather than a side effect of the file existing.

Worth running periodically regardless: Claude Code deletes transcripts older than
cleanupPeriodDays (default 30), so anything not captured before then is gone for
good. This file is the only durable record.

This cannot run in CI either way, because the transcripts live on Jon's machine and
not in the repo.

Deliberately narrow output. It records a date, a number of prompts and a number of
sessions, and nothing else. No project names, no paths, no message content, no
timing within the day. That keeps the published artefact to "how much" rather than
"what" or "when", which matters because the plate ends up on a public profile.
"""
import collections
import glob
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SESSIONS = os.path.expanduser("~/.claude/projects/**/*.jsonl")
LOCAL = ZoneInfo("Europe/London")


def is_human_turn(record):
    """True for something Jon actually typed or pasted.

    Transcripts record tool results as type "user" too, and they outnumber real
    prompts roughly sixteen to one, so counting the type alone overstates activity
    by an order of magnitude. A genuine turn has string content, or block content
    with no tool_result in it.
    """
    if record.get("type") != "user":
        return False
    content = (record.get("message") or {}).get("content")
    if isinstance(content, str):
        # Echoes of local command runs are not prompts.
        return not content.lstrip().startswith("<local-command-")
    if isinstance(content, list):
        return not any(
            isinstance(block, dict) and block.get("type") == "tool_result"
            for block in content
        )
    return False


def collect():
    prompts = collections.Counter()
    sessions = collections.defaultdict(set)
    files = glob.glob(SESSIONS, recursive=True)

    for path in files:
        with open(path, errors="ignore") as fh:
            for line in fh:
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                if not is_human_turn(record):
                    continue
                stamp = record.get("timestamp")
                if not stamp:
                    continue
                # Timestamps are UTC. Convert before bucketing, otherwise late-night
                # work lands on the wrong day for eight months of the year.
                when = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(LOCAL)
                day = when.date().isoformat()
                prompts[day] += 1
                if record.get("sessionId"):
                    sessions[day].add(record["sessionId"])

    return prompts, sessions, len(files)


def main():
    prompts, sessions, file_count = collect()
    os.makedirs(DATA, exist_ok=True)
    out = os.path.join(DATA, "agent-days.json")

    # Accumulate rather than overwrite. Claude Code's cleanupPeriodDays defaults to
    # 30, so it deletes session files older than a month at startup: the transcripts
    # are a rolling window, not an archive. Snapshotting them would mean the graph
    # could never show more than the last thirty days, however long it ran. Merging
    # means a day survives here once seen, so history accumulates from now on.
    existing = {}
    if os.path.exists(out):
        existing = json.load(open(out)).get("days", {})

    merged = dict(existing)
    for day in prompts:
        found = {"prompts": prompts[day], "sessions": len(sessions[day])}
        was = merged.get(day)
        # Take the higher of the two: a day still in progress grows as it goes, and a
        # partially pruned day must never overwrite a complete earlier reading.
        if was is None or found["prompts"] >= was["prompts"]:
            merged[day] = found

    payload = {
        "note": "Daily Claude Code activity. Counts only: no projects, paths or content.",
        "timezone": "Europe/London",
        "days": {day: merged[day] for day in sorted(merged)},
    }
    json.dump(payload, open(out, "w"), indent=1)

    days = payload["days"]
    added = len(merged) - len(existing)
    total = sum(v["prompts"] for v in days.values())
    busiest = max(days.items(), key=lambda kv: kv[1]["prompts"])
    print(f"scanned {file_count} session files, {len(prompts)} days visible on disk")
    print(f"archive now {len(days)} days ({added} new), {min(days)} to {max(days)}")
    print(f"{total} prompts, {sum(v['sessions'] for v in days.values())} sessions")
    print(f"busiest day: {busiest[0]} with {busiest[1]['prompts']} prompts")
    print(f"wrote {out} ({os.path.getsize(out) / 1024:.0f}KB)")


if __name__ == "__main__":
    main()
