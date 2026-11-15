
#!/usr/bin/env python3
"""CSCI599 Calendar Intelligence: conflicts and alternative times."""

import json
import subprocess
import sys
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("America/Los_Angeles")


def load_events():
    result = subprocess.run(
        [sys.executable, str(ROOT / "calendar/calendar_reader.py")],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )

    data = json.loads(result.stdout)
    events = []

    for event in data.get("events", []):
        events.append({
            "title": event["title"],
            "start": datetime.fromisoformat(
                event["start"]
            ).astimezone(TZ),
            "end": datetime.fromisoformat(
                event["end"]
            ).astimezone(TZ),
        })

    return sorted(events, key=lambda e: e["start"])


def find_conflicts(events):
    conflicts = []

    for index, first in enumerate(events):
        for second in events[index + 1:]:
            start = max(first["start"], second["start"])
            end = min(first["end"], second["end"])

            if start < end:
                minutes = int(
                    (end - start).total_seconds() / 60
                )

                conflicts.append({
                    "first": first,
                    "second": second,
                    "minutes": minutes,
                })

    return conflicts


def suggest_times(event, events, count=3):
    """Find three free slots on the event's original date."""

    target_date = event["start"].date()
    duration = event["end"] - event["start"]

    day_start = datetime.combine(
        target_date, time(9, 0), tzinfo=TZ
    )
    day_end = datetime.combine(
        target_date, time(18, 0), tzinfo=TZ
    )

    suggestions = []
    candidate = day_start

    while candidate + duration <= day_end:
        candidate_end = candidate + duration

        available = True

        for other in events:
            if other is event:
                continue

            overlaps = (
                candidate < other["end"]
                and candidate_end > other["start"]
            )

            if overlaps:
                available = False
                break

        if available:
            suggestions.append((candidate, candidate_end))

            if len(suggestions) >= count:
                break

        candidate += timedelta(minutes=30)

    return suggestions


def main():
    print("=" * 55)
    print("CSCI599 CALENDAR INTELLIGENCE REPORT")
    print("=" * 55)

    try:
        events = load_events()
        conflicts = find_conflicts(events)

        print(f"\nTotal calendar events: {len(events)}")
        print(f"Scheduling conflicts: {len(conflicts)}")

        if not conflicts:
            print("\nNo scheduling conflicts detected.")
        else:
            for index, conflict in enumerate(conflicts, 1):
                first = conflict["first"]
                second = conflict["second"]

                print(f"\nCONFLICT {index}")
                print(f"Event 1: {first['title']}")
                print(f"Event 2: {second['title']}")
                print(
                    f"Overlap: {conflict['minutes']} minutes"
                )

                print("\nSUGGESTED ALTERNATIVE TIMES")
                print(f"Reschedule: {second['title']}")

                alternatives = suggest_times(
                    second, events
                )

                if alternatives:
                    for start, end in alternatives:
                        print(
                            f"- {start:%A, %B %d}: "
                            f"{start:%I:%M %p} - "
                            f"{end:%I:%M %p}"
                        )
                else:
                    print(
                        "No available slots between "
                        "9:00 AM and 6:00 PM."
                    )

        print("\nCalendar access: READ-ONLY")
        print("No events were created or modified.")

    except Exception as error:
        print(
            "Calendar Intelligence unavailable: "
            f"{type(error).__name__}"
        )
        sys.exit(1)

    print("\n" + "=" * 55)
    print("END OF CALENDAR INTELLIGENCE REPORT")
    print("=" * 55)


if __name__ == "__main__":
    main()
