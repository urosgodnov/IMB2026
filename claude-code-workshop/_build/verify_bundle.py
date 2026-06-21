"""
verify_bundle.py
================
Assert that every workshop asset is present and that the sub-checks all pass.

Run:
    python claude-code-workshop/_build/verify_bundle.py

Prints BUNDLE OK and exits 0 on full success; otherwise lists failures and exits 1.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Required files
# ---------------------------------------------------------------------------
REQUIRED_FILES = [
    # Data
    "data/orders.csv",
    # Slides
    "slides/claude-code-workshop.qmd",
    "slides/img/chart_model.png",
    "slides/img/chart_effort.png",
    "slides/img/chart_caching.png",
    # Notebook
    "notebook/token-consumption-lab.ipynb",
    "notebook/token_lab.py",
    "notebook/results.sample.csv",
    "notebook/providers.sample.csv",
    # Three-tier Colab notebook (Gemini / DeepSeek / Claude, same task)
    "notebook/llm-tiers-colab.ipynb",
    "notebook/tier_lab.py",
    # Exercise cards
    "exercises/b1-setup.md",
    "exercises/b2-loop-and-goal.md",
    "exercises/b3-efforts-and-tokens.md",
    "exercises/b4-mcp-and-github.md",
    "exercises/b5-antigravity.md",
    "exercises/b5b-notebooklm.md",
    "exercises/b6-loop-automation.md",
    # Fallbacks
    "fallbacks/b2-sales-summary.py",
    "fallbacks/b2-expected-output.md",
    "fallbacks/b4-mcp-config.json",
    "fallbacks/b4-pr-example.md",
    "fallbacks/b5-antigravity-mcp-config.json",
    # Facilitator docs
    "README.md",
    "pre-work.md",
    "instructor-notes.md",
]

# Facilitator docs that must have at least one H1 and be non-trivial in size.
PROSE_DOCS = ["README.md", "pre-work.md", "instructor-notes.md"]
MIN_BYTES = 200

# Sub-scripts in _build/ to run as integrity checks.
SUB_SCRIPTS = [
    "_build/check_data.py",
    "_build/check_cards.py",
    "_build/check_fallbacks.py",
    "_build/smoke_notebook.py",
    "_build/smoke_tiers.py",
]


def check_files() -> list[str]:
    """Return a list of error strings for any missing required file."""
    errors = []
    for rel in REQUIRED_FILES:
        p = ROOT / rel
        if not p.is_file():
            errors.append(f"MISSING: {rel}")
    return errors


def check_prose_docs() -> list[str]:
    """Return errors if facilitator docs lack an H1 or are too small."""
    errors = []
    for rel in PROSE_DOCS:
        p = ROOT / rel
        if not p.is_file():
            # Already reported as missing above; skip.
            continue
        text = p.read_text(encoding="utf-8")
        size = len(p.read_bytes())
        if "# " not in text:
            errors.append(f"NO H1: {rel}")
        if size < MIN_BYTES:
            errors.append(f"TOO SMALL ({size} bytes, need >{MIN_BYTES}): {rel}")
    return errors


def run_sub_scripts() -> list[str]:
    """Run each sub-script; return error strings for any that fail."""
    errors = []
    for rel in SUB_SCRIPTS:
        script = ROOT / rel
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            output = (result.stdout + result.stderr).strip()
            errors.append(
                f"FAIL {rel}:\n{output}"
            )
        else:
            # Print sub-script's OK line so the caller can see it.
            print(result.stdout.rstrip())
    return errors


def main() -> int:
    all_errors: list[str] = []

    all_errors += check_files()
    all_errors += check_prose_docs()

    if all_errors:
        # Report file / prose errors before running sub-scripts that may
        # depend on the missing files.
        for e in all_errors:
            print(e)
        print(f"\n{len(all_errors)} problem(s) found — fix before sub-scripts run.")
        return 1

    all_errors += run_sub_scripts()

    if all_errors:
        for e in all_errors:
            print(e)
        return 1

    print("BUNDLE OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
