"""Lint exercise cards against the workshop card schema.
Run: python claude-code-workshop/_build/check_cards.py"""
from pathlib import Path
import sys

CARDS = sorted((Path(__file__).resolve().parents[1] / "exercises").glob("b*.md"))
REQUIRED = ["## Goal", "## Type this", "## You should see", "## If it looks wrong"]

def main() -> int:
    if not CARDS:
        print("FAIL: no exercise cards found")
        return 1
    bad = []
    for card in CARDS:
        text = card.read_text(encoding="utf-8")
        missing = [h for h in REQUIRED if h not in text]
        if missing:
            bad.append((card.name, missing))
    for name, missing in bad:
        print(f"FAIL {name}: missing {missing}")
    if bad:
        return 1
    print(f"CARDS OK  ({len(CARDS)} cards)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
