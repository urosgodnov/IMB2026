# -*- coding: utf-8 -*-
"""Build lab-a05-vibe-coding-project notebook + smoke test."""
import json
from pathlib import Path

from nb import LOADER, answer, code, md, save, solution, todo, write_smoke

GT = json.loads((Path(__file__).resolve().parent / "ground_truth.json").read_text(encoding="utf-8"))
TOTAL = GT["fy"]["total_revenue"]
BEST_M = "December 2024"
BEST_M_REV = GT["fy"]["best_month_revenue"]

S = {}

S["verify_warmup"] = f'''# The two anchor numbers from A01 (after dropping duplicate rows):
#   total FY revenue ~= {TOTAL:,.2f} EUR
#   best month       =  {BEST_M} (~{BEST_M_REV:,.2f} EUR)
check = orders.drop_duplicates().copy()
check["revenue"] = check["quantity"] * check["unit_price"]
print("total revenue:", round(check["revenue"].sum(), 2))
monthly = check.groupby(pd.to_datetime(check["order_date"]).dt.to_period("M"))["revenue"].sum()
print("best month:   ", monthly.idxmax(), "->", round(monthly.max(), 2))'''

FLAWED = '''# --- "AI-generated" monthly revenue summary --- (it RUNS without errors. Review it.)
import matplotlib.pyplot as plt

summary = orders.copy()
summary["month"] = pd.to_datetime(summary["order_date"]).dt.strftime("%B")
monthly_revenue = summary.groupby("month")["quantity"].sum()
monthly_revenue.plot(kind="bar", title="Adriatica monthly revenue (FY2024/25)")
plt.ylabel("revenue (EUR)")
plt.show()
print("total 'revenue':", monthly_revenue.sum())'''

S["flaw_solution"] = '''# Flaw 1 - WRONG METRIC: it sums `quantity` (units sold) but labels it "revenue".
#          The total printed is ~16,000 - nowhere near the ~815,630 EUR you verified.
# Flaw 2 - SCRAMBLED ORDER: strftime("%B") makes month NAMES, so the x-axis sorts
#          alphabetically (April, August, December, ...) - the trend is unreadable.
# (Bonus)- it never dropped the 30 duplicate rows.
# The fix:
fixed = orders.drop_duplicates().copy()
fixed["revenue"] = fixed["quantity"] * fixed["unit_price"]
fixed["month"] = pd.to_datetime(fixed["order_date"]).dt.to_period("M")
monthly_fixed = fixed.groupby("month")["revenue"].sum()
print("total revenue (fixed):", round(monthly_fixed.sum(), 2))'''

CRASH = '''RUN_BROKEN = False  # <- flip to True, run, and experience the crash (then flip back)

if RUN_BROKEN:
    # --- another "AI-generated" snippet, fresh from a chatbot ---
    df = load_file("orders.csv")
    df["profit"] = df["revenue"] - df["cost"]      # invented columns!
    print(df.groupby("region")["profit"].sum())   # invented column again
else:
    print("(set RUN_BROKEN = True to run the broken snippet)")'''

S["feedback_prompt"] = '''# A good feedback prompt contains: the ERROR, the CONTEXT, the EXPECTATION.
feedback_prompt = """Your code raised:
    KeyError: 'revenue'
The DataFrame comes from orders.csv with columns:
    order_id, order_date, customer_id, product_id, product_name, category, quantity, unit_price
There is no revenue, cost, or region column. Revenue must be computed as
quantity * unit_price; there is no cost data, so drop the profit idea and
summarise revenue by product category instead."""
print(feedback_prompt)'''

cells = [
    md(f"""# A05 · Vibe Coding the MADA Project

**IMB 2026 · MADA · Workshop A05 (Wed 1 Jul 2026, 9:00–12:00) — presentations are Friday.**

Monday you verified an AI's *words*. Today the AI writes **code** for you — and you
stay in charge. This is "vibe coding" done with discipline:

> **specify → prompt → run → review → iterate**

**Your AI surface today** *(free options only)*: Colab's built-in **Gemini chat panel**
(spark icon, bottom-left) — or the tool you used in Vibe coding 1 on Monday. If your
tool has a small daily request budget (e.g. Antigravity's free tier), treat prompts
like money: **plan before you spend.**

By the end your group will have: a working, **verified** slice of your MADA project,
plus an honest prompt log you can show on Friday."""),
    code(LOADER + '\norders = load_file("orders.csv")\nprint("warm-up data:", orders.shape)'),

    # ------------------------------------------------------------- S1
    md("""## 1 · The disciplined warm-up

Vibes produce code; **specs** produce *useful* code. A five-line spec template:

```
INPUT:   which file/data, which columns
TASK:    what transformation, step by step if it matters
OUTPUT:  exactly what should come out (table? chart? number?)
EXAMPLE: one concrete expected result, if you know one
CONSTRAINTS: libraries, style, what NOT to do
```"""),
    todo('write a 5-line spec (as a comment or string) for: "a monthly revenue summary report from orders.csv" — include the duplicate-rows issue you know about',
         'fill the five template lines; mention quantity * unit_price'),
    solution('''spec = """
INPUT:   orders.csv - columns order_id, order_date, customer_id, product_id,
         product_name, category, quantity, unit_price. Contains some duplicate rows.
TASK:    drop duplicate rows; compute revenue = quantity * unit_price;
         aggregate revenue by calendar month of order_date.
OUTPUT:  a table month -> total revenue (chronological), plus a line chart,
         plus the grand total printed.
EXAMPLE: one row like  2024-12 | 96505.68
CONSTRAINTS: pandas + matplotlib only; chronological month order, not alphabetical.
"""
print(spec)'''),
    md("""Now **prompt your AI tool with your spec** (paste the spec, ask for the code),
paste the generated code into the empty cell below, and run it."""),
    code('# ⬇️ paste the AI-generated code from YOUR spec here, then run\n'),
    md(f"""**Before you believe it — verify.** You know two numbers from A01: total FY
revenue ≈ **€{TOTAL:,.0f}** and best month **{BEST_M}** (≈ €{BEST_M_REV:,.0f})."""),
    todo('check the AI code\'s output against the two anchor numbers (compute them independently here)',
         'drop_duplicates, revenue column, groupby month — you have done this before'),
    solution(S["verify_warmup"]),
    md("""**The review checklist** — apply it to *every* AI-generated snippet, forever:

1. **Does it run?** (lowest bar, not the goal)
2. **Right numbers on a case you know?** (anchors!)
3. **Did it invent anything?** (columns, files, business rules)
4. **Anything unused or pointless?** (dead code = misunderstood task)"""),

    # ------------------------------------------------------------- S2
    md("""## 2 · Code-review drill

Below is a snippet "an AI generated" for exactly your warm-up task. It runs without
errors and produces a chart. **It is wrong twice.** Run it, apply the checklist,
find both flaws *before* opening the solution."""),
    code(FLAWED),
    todo('write down the two flaws (and the fix for each) as comments',
         'checklist item 2: compare with your anchor numbers; then look hard at the x-axis'),
    solution(S["flaw_solution"]),
    md("""**The lesson:** AI code fails *quietly*. It ran, it plotted, it printed — and both
headline numbers were garbage. *Running is not the same as right.* Your anchors caught
it in seconds."""),

    # ------------------------------------------------------------- S3
    md("""## 3 · Recover, don't despair

Sometimes AI code crashes outright. That is the *easy* case — if you feed the error
back **with context**. The cell below is set NOT to run by default; flip the flag,
experience the crash, flip it back."""),
    code(CRASH),
    todo('write the feedback prompt you would send the AI: include the error, the real columns, and what you actually want',
         'error + context + expectation'),
    solution(S["feedback_prompt"]),
    md("""**Recovery loop:** reproduce → feed back (error + context + expectation) → re-run
→ re-verify. **Restart rule:** if two recovery rounds haven't fixed it, your *spec*
was the problem — rewrite the spec, start a fresh chat."""),

    # ------------------------------------------------------------- S4
    md("""## 4 · Your project slice — main block (~80 minutes)

Adriatica's chapter is closed. Now: **your MADA project**, Friday's demo, one thin
slice, built today, with AI doing the typing and your group doing the thinking.

**Scope it small.** One input you already have, one output, one screenshot-able
result. "The data part of our demo" — not "our whole project"."""),
    md("""**📋 Spec card** *(double-click, fill in as a group)*

> **Project:** …
> **The slice we build today:** …
> **Input data:** … (file, columns)
> **Output:** … (table / chart / number)
> **Demo line for Friday:** "And here you can see …"
"""),
    md("""**🪵 Prompt log** — keep it honest, fill it as you go *(double-click to edit)*:

| # | What we asked the AI | What came back | How we verified it |
|---|---------------------|----------------|--------------------|
| 1 | … | … | … |
| 2 | … | … | … |

*(This log is your AI-use declaration for the project — same norm as the homework.
On Friday it shows you used AI like professionals: specified, reviewed, verified.)*"""),
    md("""**Work plan for the block:**

1. Spec card (10 min — the thinking happens here)
2. Generate → run → **verify against a number you can hand-check** (the A01/A04 habit)
3. Iterate; log every prompt
4. If the tool budget is tight: draft prompts in the doc first, spend them deliberately

Instructors are circulating — call us at the *spec* stage, not only when code breaks."""),

    # ------------------------------------------------------------- S5
    md("""## 5 · Dry run & wrap-up

**Dry run (last 20 min):** run your slice top-to-bottom as it will run on Friday.
Then **swap notebooks with a neighbouring group**: they check ONE of your numbers
by hand (and you theirs). If it survives a stranger's check, it will survive the demo.

---

### The course, in one breath

**A01** you made data answer questions · **A02** you made it predict · **A03** you
learned when models lie · **A04** you learned when *AI* lies · **A05** the AI worked
for you — and you verified everything. That habit — *trust but verify* — is the whole
strand in three words, and it is what managing AI-assisted teams will demand of you.

**Beyond this course:** deploy your slice as a small app; forecast the monthly trend
(time series); script LLM workflows over real document volumes. The toolkit you have
now is enough to start any of them. Good luck on Friday! 🎓"""),
]

chunks = [
    ("setup", 'orders = load_file("orders.csv")\nimport pandas as pd'),
    ("verify_warmup", S["verify_warmup"] + f'\nassert abs(check["revenue"].sum() - {TOTAL}) < 1.0\nassert str(monthly.idxmax()) == "2024-12"'),
    ("flawed_runs_but_wrong", FLAWED + f'\nassert monthly_revenue.sum() < 20000  # quantity total, nowhere near revenue\nassert list(monthly_revenue.index) == sorted(monthly_revenue.index)  # alphabetical = scrambled'),
    ("flaw_fix", S["flaw_solution"] + f'\nassert abs(monthly_fixed.sum() - {TOTAL}) < 1.0'),
    ("crash_guarded", CRASH),
    ("crash_real", '''try:
    df = load_file("orders.csv")
    df["profit"] = df["revenue"] - df["cost"]
    raise AssertionError("should have raised KeyError")
except KeyError as e:
    print("KeyError as expected:", e)'''),
    ("feedback", S["feedback_prompt"]),
]

if __name__ == "__main__":
    save(cells, "lab-a05-vibe-coding-project", "lab-a05-vibe-coding-project.ipynb")
    write_smoke("a05", "lab-a05-vibe-coding-project/data", chunks)
