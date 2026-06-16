# -*- coding: utf-8 -*-
"""Build homework2-winback notebook + smoke test (reference solution)."""
from nb import LOADER, code, md, save, todo, write_smoke

RANKING = '''# --- PROVIDED CELL: run AFTER your pipeline is fitted. Requires these exact names:
#     pipe     - your fitted Pipeline
#     X_test, y_test - from your train_test_split(random_state=42)
proba = pipe.predict_proba(X_test)[:, 1]
ranked = X_test.copy()
ranked["responded"] = y_test.values
ranked["proba"] = proba
top30 = ranked.sort_values("proba", ascending=False).head(int(0.30 * len(ranked)))
print("overall test response rate:", round(ranked["responded"].mean(), 3))
print("top-30% response rate:     ", round(top30["responded"].mean(), 3))'''

cells = [
    md("""# Homework 2 — The Win-Back Campaign (ML classification)

**IMB 2026 · MADA** · Assigned Fri 19 Jun 2026 (Workshop A03) · **Due: Wed 1 Jul 2026, 23:59**

## The brief

Adriatica has ~**5,200 lapsed customers** (no order in 3+ months). Marketing ran a
**pilot**: 804 randomly chosen lapsed customers received a win-back e-mail with a 15%
voucher, and we recorded who **responded** (placed an order within 30 days).

For the full rollout the budget covers only **1,560 vouchers (~30%)** of the lapsed
pool. The CMO's question:

> *"Whom should we target, and what results should I promise the board?"*

## Your task

1. **Explore** the pilot data (`hw2_winback.csv`).
2. Build a **leak-proof classification pipeline** (one-hot encoded categoricals inside
   a `Pipeline`) that predicts `responded`. Think hard about **which columns the model
   may legitimately use — what did we know at the moment the campaign e-mail was sent?**
3. **Evaluate honestly**: train/test split (`random_state=42`), 5-fold cross-validation,
   comparison with the majority baseline, confusion matrix with both error types read
   in campaign terms.
4. Run the **provided targeting cell** and interpret it: what does the top-30% response
   rate mean for a budget of 1,560 vouchers?
5. Write the **recommendation memo** to the CMO (~150–250 words).
6. Fill in the **AI-use declaration**.

## Grading — 100 points (see GRADING.md for the full rubric)

**Objective, 70 pts:** exploration 10 · leak-proof pipeline 20 · honest evaluation 20 ·
targeting analysis 10 · reproducibility & declarations 10.
**Subjective, 30 pts:** recommendation memo 15 · communication & storytelling 10 ·
critical insight beyond the minimum 5.

Deliverable: this notebook, completed, as a Colab share link. It must run
**top-to-bottom** on the free tier. Free AI tools allowed **and declared**; you must be
able to explain every line."""),

    md("""## 1 · Setup and exploration"""),
    code(LOADER + '\npilot = load_file("hw2_winback.csv")\nprint(pilot.shape)\npilot.head()'),
    todo('explore: dtypes and missing values; the overall response rate; and at least one comparison of responders vs non-responders (e.g. groupby("responded") on a few features) — say in one sentence what you notice'),

    md("""## 2 · A leak-proof pipeline

Define your feature lists and the target, then build the pipeline
(`ColumnTransformer` + `OneHotEncoder` for the categoricals, wrapped with a
classifier — `LogisticRegression(max_iter=2000)` is a fine choice).

⚠️ **Feature legitimacy check (graded heavily):** for every column, ask — *was this
known when the e-mail was sent?* Columns that record what happened **after** sending
describe the outcome; using them is data leakage (A03, Section 4)."""),
    todo('define categorical + numeric feature lists (justify any column you EXCLUDE in a comment) and build your pipeline; name it pipe'),

    md("""## 3 · Honest evaluation

Required names for the provided cell below: `X_train, X_test, y_train, y_test`
from `train_test_split(..., test_size=0.25, random_state=42)`."""),
    todo('split, fit pipe, report: test accuracy, 5-fold cross-validation (mean ± std), the majority baseline, and the confusion matrix — then read BOTH error types in campaign terms (a missed responder costs…, a wasted voucher costs…)'),

    md("""## 4 · Targeting under a budget

The rollout budget covers ~30% of the lapsed pool. The cell below ranks test
customers by your model's predicted response probability and compares the top-30%
response rate with the overall rate. **Run it, then interpret it** — this number is
the heart of your memo."""),
    code(RANKING),
    todo('interpret the two numbers: if the full lapsed pool behaves like the test set, roughly how many responses do 1,560 model-targeted vouchers buy vs 1,560 random ones? (simple arithmetic in a comment or markdown is fine)'),

    md("""## 5 · Recommendation memo to the CMO

**✍️ Memo (~150–250 words)** — a decision, not a description: whom to target, the
expected outcome in numbers, what could go wrong, and one next step you propose
(e.g., keeping a small random holdout to measure true lift).

> *(double-click and write here)*"""),

    md("""## 6 · AI-use declaration

**Tools used and for what:**

> *(e.g. "Gemini Learn Mode for a hint on predict_proba; Colab autocomplete." — or "none")*"""),
]

# Reference solution as the smoke test (validates the assignment is solvable as specified)
chunks = [
    ("load", 'pilot = load_file("hw2_winback.csv")\nimport pandas as pd\nassert pilot.shape == (804, 13), pilot.shape'),
    ("reference_solution", '''from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

categorical = ["country", "segment", "acquisition_channel"]
numeric = ["months_since_last_order", "n_past_orders", "total_past_spend",
           "avg_past_order_value", "newsletter", "opened_last_3_newsletters",
           "past_support_tickets"]
# voucher_redeemed EXCLUDED: only known after the campaign (leakage)
X = pilot[categorical + numeric]
y = pilot["responded"]
pipe = Pipeline([("prep", ColumnTransformer(
    [("cat", OneHotEncoder(handle_unknown="ignore"), categorical)],
    remainder="passthrough")), ("model", LogisticRegression(max_iter=2000))])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
pipe.fit(X_train, y_train)
acc = pipe.score(X_test, y_test)
cv = cross_val_score(pipe, X, y, cv=5)
baseline = 1 - y.mean()
print("test acc:", round(acc, 3), "| cv:", round(cv.mean(), 3), "| baseline:", round(baseline, 3))
assert acc > baseline + 0.10, (acc, baseline)'''),
    ("ranking", RANKING + '''
lift = top30["responded"].mean() / ranked["responded"].mean()
print("lift:", round(lift, 2))
assert lift > 1.5, lift'''),
    ("leak_flag_works", '''X_leak = pilot[categorical + numeric + ["voucher_redeemed"]]
Xl_tr, Xl_te, yl_tr, yl_te = train_test_split(X_leak, y, test_size=0.25, random_state=42)
leaky = Pipeline([("prep", ColumnTransformer(
    [("cat", OneHotEncoder(handle_unknown="ignore"), categorical)],
    remainder="passthrough")), ("model", LogisticRegression(max_iter=2000))]).fit(Xl_tr, yl_tr)
leak_acc = leaky.score(Xl_te, yl_te)
print("accuracy WITH the leak column:", round(leak_acc, 3), " -> grader flag threshold 0.95 works")
assert leak_acc > 0.95, leak_acc'''),
]

if __name__ == "__main__":
    save(cells, "lab-a03-models-you-can-trust/homework2", "homework2-winback.ipynb")
    write_smoke("hw2", "lab-a03-models-you-can-trust/homework2/data", chunks)
