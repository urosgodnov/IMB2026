"""
smoke_notebook.py
=================
Smoke test for the token-consumption-lab notebook helpers.

Runs WITHOUT an API key.  Tests:
1. token_lab.load_results() returns a DataFrame with all four expected
   setting_group values.
2. token_lab.make_charts() writes at least one non-empty PNG file.

Run:
    python claude-code-workshop/_build/smoke_notebook.py
Expected output:
    NOTEBOOK SMOKE OK
"""

import os
import pathlib
import sys
import tempfile

# Ensure token_lab is importable from the notebook directory.
NOTEBOOK_DIR = pathlib.Path(__file__).resolve().parent.parent / "notebook"
sys.path.insert(0, str(NOTEBOOK_DIR))

# Explicitly make sure no API key is active for this smoke run.
os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ.pop("DEEPSEEK_API_KEY", None)

# Use the Agg backend before importing token_lab (which also sets it, but
# doing it here is belt-and-braces).
import matplotlib
matplotlib.use("Agg")

import token_lab

# ---------------------------------------------------------------------------
# 1. load_results — should fall back to results.sample.csv
# ---------------------------------------------------------------------------
df = token_lab.load_results(notebook_dir=NOTEBOOK_DIR)

assert df is not None, "load_results() returned None"
assert len(df) > 0, "load_results() returned an empty DataFrame"

expected_groups = {"model", "effort", "caching", "context"}
found_groups = set(df["setting_group"].unique())
missing = expected_groups - found_groups
assert not missing, f"Missing setting_group(s) in sample CSV: {missing}"

# ---------------------------------------------------------------------------
# 2. make_charts — write to a temp dir and check outputs
# ---------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmpdir:
    paths = token_lab.make_charts(df, tmpdir)

    assert paths, "make_charts() returned an empty list"
    for p in paths:
        ppath = pathlib.Path(p)
        assert ppath.exists(), f"Chart file not found: {p}"
        assert ppath.stat().st_size > 0, f"Chart file is empty: {p}"

# ---------------------------------------------------------------------------
# 3. provider comparison — load_providers + make_provider_chart (no key)
# ---------------------------------------------------------------------------
prov = token_lab.load_providers(notebook_dir=NOTEBOOK_DIR)
assert prov is not None and len(prov) > 0, "load_providers() returned empty"
for col in ("provider", "model", "usd_cost"):
    assert col in prov.columns, f"providers CSV missing column: {col}"

with tempfile.TemporaryDirectory() as tmpdir:
    chart = token_lab.make_provider_chart(prov, tmpdir)
    cpath = pathlib.Path(chart)
    assert cpath.exists() and cpath.stat().st_size > 0, f"provider chart missing/empty: {chart}"

# ---------------------------------------------------------------------------
print("NOTEBOOK SMOKE OK")
