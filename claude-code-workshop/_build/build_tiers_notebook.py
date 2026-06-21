"""
build_tiers_notebook.py
=======================
Builds claude-code-workshop/notebook/llm-tiers-colab.ipynb.

A self-contained Colab notebook: the SAME catalogue-labelling task run on three
tiers — Gemini (free, in Colab), DeepSeek (cheap, key), Claude (premium, key).

Self-containment trick: an early `%%writefile tier_lab.py` cell embeds the helper
module (read from notebook/tier_lab.py) so that opening the notebook in Colab and
running setup materialises the module — no external files, no data URL needed.
tier_lab.py stays the single source of truth; this cell is generated from it.

Deterministic output: no timestamps, no random seeds. Run from any directory:
    python claude-code-workshop/_build/build_tiers_notebook.py
"""

import pathlib

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

THIS_FILE = pathlib.Path(__file__).resolve()
WORKSHOP_ROOT = THIS_FILE.parent.parent
NOTEBOOK_DIR = WORKSHOP_ROOT / "notebook"
TIER_LAB_PATH = NOTEBOOK_DIR / "tier_lab.py"
OUT_PATH = NOTEBOOK_DIR / "llm-tiers-colab.ipynb"

# ---------------------------------------------------------------------------
# Cell content
# ---------------------------------------------------------------------------
CELL_0_MD = """\
# Three Tiers, One Task — Free vs. Cheap vs. Premium

**Run this notebook in Google Colab.** It sends the *same* small business task to
three AI tiers and shows what each one costs.

| Tier | How | API key? | When it's the right choice |
|---|---|---|---|
| **Gemini** | `google.colab.ai` (built into Colab) | no | exploring, learning — **free** |
| **DeepSeek** | OpenAI-compatible API | yes (cheap) | **automation** — it runs *without you* |
| **Claude** | Anthropic API | yes | the hardest, highest-stakes jobs |

**The task:** label each product with a *gift appeal* (High / Medium / Low) and a
one-line marketing blurb — judgement no formula in your data can compute.

**The lesson:** free Gemini is perfect while *you* sit in the notebook and click
**Run**. The moment AI must run **without you** — a nightly script, an app, a
scheduled job (Block 6!) — you need a real API key, and DeepSeek shows that can
cost a *fraction of a cent*.

> **Sending data out?** These product names aren't sensitive. For real customer or
> financial data, remember DeepSeek's API is China-hosted — right-size *what data*
> you send, not just which model.
"""

CELL_1_CODE = """\
# One-time setup (Colab): install the two SDKs the paid tiers use.
# Gemini needs nothing extra — it is built into Colab.
!pip install -q openai anthropic
"""

# CELL_2 is generated below: `%%writefile tier_lab.py` + the module source.

CELL_3_CODE = """\
# Load the helper module written above, plus a small display helper.
import pandas as pd
from IPython.display import Image, display
import tier_lab

def show(res):
    print(f"{res['tier']} — {res['note']}")
    if not res["ok"]:
        print("  (skipped — see the message above)")
        return
    display(pd.DataFrame(res["rows"]))
    if res["usd_cost"] is not None:
        print(f"  {res['n']} products | cost ${res['usd_cost']:.6f} | {res['latency_s']}s")

print("The same task prompt is sent to every tier:\\n")
print(tier_lab.build_prompt())
"""

CELL_4_MD = """\
## Tier 1 — Gemini (free, inside Colab)

No API key. Works **only** in Colab (`from google.colab import ai`). This is your
*exploring* tier — great for learning, capped by a monthly free limit.
"""

CELL_5_CODE = """\
gemini = tier_lab.run_gemini()
show(gemini)
"""

CELL_6_MD = """\
## Tier 2 — DeepSeek (cheap, needs a key)

This is the tier that **runs without you** — the same call works from a script or a
scheduled job, not just this notebook. First give Colab your key, then run the cell.

Set it once (cleanest: use Colab's **Secrets** 🔑 panel, or just run this in a cell):

```python
import os
os.environ["DEEPSEEK_API_KEY"] = "sk-..."   # your key from platform.deepseek.com
```
"""

CELL_7_CODE = """\
deepseek = tier_lab.run_deepseek()
show(deepseek)
"""

CELL_8_MD = """\
## Tier 3 — Claude (premium, needs a key)

Premium capability and reliability for the hardest jobs. Set your key the same way:

```python
import os
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
```
"""

CELL_9_CODE = """\
claude = tier_lab.run_claude()
show(claude)
"""

CELL_10_MD = """\
## Compare: the same task, three bills

The bar below uses your live numbers for whichever tiers ran, and clearly-labelled
*illustrative* figures for the rest — so the picture is complete even with no keys.
"""

CELL_11_CODE = """\
costs = tier_lab.costs_frame([gemini, deepseek, claude])
display(costs)
chart = tier_lab.make_cost_chart(costs, ".")
display(Image(filename=chart))

print("Free for exploring          -> Gemini, inside Colab.")
print("A key for automating         -> DeepSeek runs without you, ~a fraction of a cent.")
print("Premium for the hardest jobs -> Claude.")
"""


def build() -> None:
    tier_lab_source = TIER_LAB_PATH.read_text(encoding="utf-8")
    writefile_cell = "%%writefile tier_lab.py\n" + tier_lab_source

    nb = new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nb.metadata["language_info"] = {"name": "python", "version": "3.13.0"}

    nb.cells = [
        new_markdown_cell(CELL_0_MD),
        new_code_cell(CELL_1_CODE),
        new_code_cell(writefile_cell),
        new_code_cell(CELL_3_CODE),
        new_markdown_cell(CELL_4_MD),
        new_code_cell(CELL_5_CODE),
        new_markdown_cell(CELL_6_MD),
        new_code_cell(CELL_7_CODE),
        new_markdown_cell(CELL_8_MD),
        new_code_cell(CELL_9_CODE),
        new_markdown_cell(CELL_10_MD),
        new_code_cell(CELL_11_CODE),
    ]

    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        nbformat.write(nb, fh)

    print(f"Notebook written: {OUT_PATH}")
    print(f"Cells: {len(nb.cells)}")


if __name__ == "__main__":
    build()
