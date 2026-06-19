"""
build_token_notebook.py
=======================
Builds claude-code-workshop/notebook/token-consumption-lab.ipynb.

Deterministic output: no timestamps, no random seeds.
Run from any working directory:
    python claude-code-workshop/_build/build_token_notebook.py
"""

import pathlib
import sys

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
THIS_FILE = pathlib.Path(__file__).resolve()
WORKSHOP_ROOT = THIS_FILE.parent.parent          # .../claude-code-workshop/
NOTEBOOK_DIR = WORKSHOP_ROOT / "notebook"
OUT_PATH = NOTEBOOK_DIR / "token-consumption-lab.ipynb"

# ---------------------------------------------------------------------------
# Cell content
# ---------------------------------------------------------------------------

CELL_1_MD = """\
# Token Consumption Lab

## What this shows

Claude's token cost changes with four settings you control as a Claude Code user:

| Setting group | What varies |
|---|---|
| **Model** | `haiku` vs `sonnet` vs `opus` — different price-per-token |
| **Effort** | `low` → `max` — more reasoning = more output tokens |
| **Caching** | A long repeated prefix read from cache vs re-billed as new input |
| **Context size** | A short vs a stuffed context window |

## How to read this notebook

You are reading **measured numbers** (or clearly-labelled illustrative samples
until a real run replaces them).  The presentation cells below — the table and
the charts — run **without an API key** from a committed CSV file.

Re-running the live measurement is optional and is gated behind its own cell
near the bottom.  It needs your own `ANTHROPIC_API_KEY` and costs a few US cents.
"""

CELL_2_CODE = """\
# Load and display the tidy results table.
# Reads results.csv (real run) if present, else results.sample.csv (placeholder).
import sys, pathlib
sys.path.insert(0, str(pathlib.Path().resolve()))  # ensure token_lab is importable

import token_lab
import pandas as pd

df = token_lab.load_results()
df
"""

CELL_3_CODE = """\
# Render the three comparison charts and display them inline.
import os
import token_lab
from IPython.display import Image, display

chart_paths = token_lab.make_charts(df, '.')
for p in chart_paths:
    print(p)
    display(Image(filename=p))
"""

CELL_4_MD = """\
## Optional: measure it yourself

The cell below sends real API requests and overwrites `results.csv` with fresh
measurements.

**Requirements:**
- Set the environment variable `ANTHROPIC_API_KEY` to your key before running.
- The live sweep covers ~10 API calls across all setting groups.
  Estimated cost: **< $0.10** with default prompts.
- After running, re-execute the cells above to see your real numbers.

If `ANTHROPIC_API_KEY` is not set, the cell skips gracefully and the notebook
continues to display the committed results.
"""

CELL_5_CODE = """\
# GATED: live API measurement — only runs when ANTHROPIC_API_KEY is set.
import os
import token_lab
import anthropic

KEY = os.environ.get("ANTHROPIC_API_KEY")
if not KEY:
    print("No ANTHROPIC_API_KEY found — skipping live measurement; reading committed results.")
else:
    print("API key found — starting live measurement (may take ~60 s) ...")
    client = anthropic.Anthropic()
    res = token_lab.measure_settings(client)
    res.to_csv("results.csv", index=False)
    print("Wrote results.csv")
    print(res.to_string(index=False))
"""

CELL_6_MD = """\
## Bonus: Claude vs DeepSeek — the same task, a different bill

The "DeepSeek moment" of January 2025 showed that **capability and price came
apart**: a far cheaper model can do a similar job. Here we make that concrete —
the *same* summary prompt sent to Claude and to **DeepSeek V4 Flash**, each
priced with its own tariff.

DeepSeek exposes an **OpenAI-compatible API**, so it is called with the `openai`
SDK (only the `base_url` and model name change) — not the Anthropic SDK.

As above, the table and chart read a committed CSV and need **no key**; the live
measurement is gated and needs BOTH `ANTHROPIC_API_KEY` and `DEEPSEEK_API_KEY`.
"""

CELL_7_CODE = """\
# Provider comparison — reads providers.csv (real run) or providers.sample.csv.
import token_lab
from IPython.display import Image, display

prov = token_lab.load_providers()
prov_display = prov.copy()
# "per 1,000 runs" makes the tiny per-task numbers tangible for a business reader.
prov_display["usd_per_1000_runs"] = (prov_display["usd_cost"] * 1000).round(2)
display(prov_display)

chart = token_lab.make_provider_chart(prov, '.')
print(chart)
display(Image(filename=chart))
"""

CELL_8_MD = """\
## Optional: measure the provider comparison yourself

The cell below sends the same prompt to Claude and DeepSeek live and overwrites
`providers.csv`.

**Requirements:**
- `ANTHROPIC_API_KEY` (Claude) and `DEEPSEEK_API_KEY` (DeepSeek — get one at
  platform.deepseek.com) set in your environment.
- 3 tiny API calls total; a fraction of a US cent.

If either key is missing, the cell skips gracefully and the committed results stay.
"""

CELL_9_CODE = """\
# GATED: live provider comparison — needs ANTHROPIC_API_KEY and DEEPSEEK_API_KEY.
import os
import token_lab

A_KEY = os.environ.get("ANTHROPIC_API_KEY")
D_KEY = os.environ.get("DEEPSEEK_API_KEY")
if not (A_KEY and D_KEY):
    missing = [k for k, v in [("ANTHROPIC_API_KEY", A_KEY), ("DEEPSEEK_API_KEY", D_KEY)] if not v]
    print(f"Missing {missing} — skipping live provider comparison; reading committed results.")
else:
    import anthropic
    from openai import OpenAI
    anthropic_client = anthropic.Anthropic()
    deepseek_client = OpenAI(api_key=D_KEY, base_url=token_lab.DEEPSEEK_BASE_URL)
    prov = token_lab.measure_providers(anthropic_client, deepseek_client)
    prov.to_csv("providers.csv", index=False)
    print("Wrote providers.csv")
    print(prov.to_string(index=False))
"""

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build() -> None:
    nb = new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nb.metadata["language_info"] = {
        "name": "python",
        "version": "3.13.0",
    }

    nb.cells = [
        new_markdown_cell(CELL_1_MD),
        new_code_cell(CELL_2_CODE),
        new_code_cell(CELL_3_CODE),
        new_markdown_cell(CELL_4_MD),
        new_code_cell(CELL_5_CODE),
        new_markdown_cell(CELL_6_MD),
        new_code_cell(CELL_7_CODE),
        new_markdown_cell(CELL_8_MD),
        new_code_cell(CELL_9_CODE),
    ]

    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        nbformat.write(nb, fh)

    print(f"Notebook written: {OUT_PATH}")
    print(f"Cells: {len(nb.cells)}")


if __name__ == "__main__":
    build()
