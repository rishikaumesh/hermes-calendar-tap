#!/usr/bin/env python3
"""Read synthetic calendar events for a portable skill demonstration."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    with (ROOT / "sample_events.json").open() as file:
        print(json.dumps(json.load(file)))
