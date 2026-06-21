"""
smoke_tiers.py
==============
Smoke test for the three-tier notebook helpers (tier_lab.py).

Runs WITHOUT an API key and WITHOUT Colab. Tests the pure helpers and that the
self-gating runners skip gracefully (ok=False) when no tier is available.

Run:
    python claude-code-workshop/_build/smoke_tiers.py
Expected output:
    TIERS SMOKE OK
"""

import os
import pathlib
import sys
import tempfile

NOTEBOOK_DIR = pathlib.Path(__file__).resolve().parent.parent / "notebook"
sys.path.insert(0, str(NOTEBOOK_DIR))

# Make sure no tier is live for this smoke run.
os.environ.pop("DEEPSEEK_API_KEY", None)
os.environ.pop("ANTHROPIC_API_KEY", None)

import matplotlib
matplotlib.use("Agg")

import tier_lab

# ---------------------------------------------------------------------------
# 1. build_prompt — mentions the products and asks for JSON
# ---------------------------------------------------------------------------
prompt = tier_lab.build_prompt()
assert "JSON" in prompt, "prompt should request JSON output"
assert tier_lab.PRODUCTS[0] in prompt, "prompt should list the products"

# ---------------------------------------------------------------------------
# 2. parse_labels — tolerant of plain and ```json-fenced replies
# ---------------------------------------------------------------------------
plain = '[{"product_name": "X", "gift_appeal": "High", "blurb": "Nice."}]'
fenced = "```json\n" + plain + "\n```"
wrapped = '{"products": ' + plain + "}"
prose = "Sure, here you go:\n" + plain + "\nHope that helps!"  # model added prose
for sample in (plain, fenced, wrapped, prose):
    rows = tier_lab.parse_labels(sample)
    assert isinstance(rows, list) and rows[0]["gift_appeal"] == "High", \
        f"parse_labels failed on: {sample!r}"

# ---------------------------------------------------------------------------
# 3. usd_cost — priced tiers compute a positive cost
# ---------------------------------------------------------------------------
c = tier_lab.usd_cost("DeepSeek V4 Flash", 600, 300)
assert c > 0, "DeepSeek cost should be positive"
assert tier_lab.usd_cost("Claude Opus 4.8", 600, 300) > c, "Claude should cost more"

# ---------------------------------------------------------------------------
# 4. runners — self-gate to ok=False with a message (no Colab, no keys)
# ---------------------------------------------------------------------------
for res in (tier_lab.run_gemini(), tier_lab.run_deepseek(), tier_lab.run_claude()):
    assert res["ok"] is False, f"expected skip, got: {res}"
    assert res["note"], "skipped runner should explain why"

# ---------------------------------------------------------------------------
# 5. costs_frame — three rows, illustrative fallback present
# ---------------------------------------------------------------------------
df = tier_lab.costs_frame([])
assert len(df) == 3, "expected three tiers in the cost frame"
assert (df["source"] == "illustrative").all(), "no live runs -> all illustrative"
for col in ("tier", "usd_cost", "source"):
    assert col in df.columns, f"cost frame missing column: {col}"

# ---------------------------------------------------------------------------
# 6. make_cost_chart — writes a non-empty PNG
# ---------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmpdir:
    chart = tier_lab.make_cost_chart(df, tmpdir)
    cpath = pathlib.Path(chart)
    assert cpath.exists() and cpath.stat().st_size > 0, f"chart missing/empty: {chart}"

print("TIERS SMOKE OK")
