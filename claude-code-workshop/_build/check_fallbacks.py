"""Run the Block 2 fallback and assert the December peak.
Run: python claude-code-workshop/_build/check_fallbacks.py"""
from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "fallbacks" / "b2-sales-summary.py"

def main() -> int:
    out = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
    if out.returncode != 0:
        print("FAIL: fallback script errored\n", out.stderr)
        return 1
    if "Best month: 2024-12" not in out.stdout:
        print("FAIL: December peak missing from output\n", out.stdout)
        return 1
    print("FALLBACKS OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
