# -*- coding: utf-8 -*-
"""Build lab-a03-models-you-can-trust notebook + homework notebook + smoke test."""
from nb import LOADER, answer, code, md, save, solution, todo, write_smoke

S = {}

S["setup_cols"] = '''categorical = ["country", "segment", "acquisition_channel"]
numeric = ["first_order_value", "first_order_items", "newsletter",
           "support_tickets", "website_visits_first_month"]
target = "six_month_spend"
customers[categorical + numeric + [target]].head()'''

S["first_reg"] = '''from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

X = customers[numeric]
y = customers[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

reg = LinearRegression().fit(X_train, y_train)
pred = reg.predict(X_test)
print("MAE:", round(mean_absolute_error(y_test, pred), 2), "EUR")
print("R^2:", round(r2_score(y_test, pred), 3))'''

S["coefs"] = '''pd.DataFrame({"feature": numeric, "coefficient": reg.coef_.round(2)}) \\
    .sort_values("coefficient", key=abs, ascending=False)'''

S["cat_fail"] = '''# DEMO - run me: what happens if we feed the model text columns as-is?
try:
    LinearRegression().fit(customers[categorical + numeric], y)
except Exception as e:
    print(type(e).__name__, "-", str(e)[:120], "...")'''

S["pipeline"] = '''from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

prep = ColumnTransformer(
    [("cat", OneHotEncoder(handle_unknown="ignore"), categorical)],
    remainder="passthrough")

pipe = Pipeline([("prep", prep), ("model", LinearRegression())])

X2 = customers[categorical + numeric]
X2_train, X2_test, y2_train, y2_test = train_test_split(X2, y, test_size=0.25, random_state=42)
pipe.fit(X2_train, y2_train)
pred2 = pipe.predict(X2_test)
print("MAE:", round(mean_absolute_error(y2_test, pred2), 2), "EUR")
print("R^2:", round(r2_score(y2_test, pred2), 3))'''

S["cv"] = '''from sklearn.model_selection import cross_val_score

scores = cross_val_score(pipe, X2, y, cv=5)
print("five R^2 scores:", scores.round(3))
print("mean:", round(scores.mean(), 3), "| std:", round(scores.std(), 3))'''

S["compare"] = '''from sklearn.dummy import DummyRegressor
from sklearn.tree import DecisionTreeRegressor

def make_pipe(model):
    return Pipeline([("prep", ColumnTransformer(
        [("cat", OneHotEncoder(handle_unknown="ignore"), categorical)],
        remainder="passthrough")), ("model", model)])

candidates = {
    "always predict the mean (dummy)": DummyRegressor(),
    "linear regression": LinearRegression(),
    "decision tree (depth 4)": DecisionTreeRegressor(max_depth=4, random_state=42),
}
rows = []
for name, m in candidates.items():
    s = cross_val_score(make_pipe(m), X2, y, cv=5)
    rows.append({"model": name, "cv_r2_mean": round(s.mean(), 3), "cv_r2_std": round(s.std(), 3)})
comparison = pd.DataFrame(rows).sort_values("cv_r2_mean", ascending=False)
comparison'''

S["leak"] = '''# DEMO - run me. THE WRONG WAY vs THE HONEST WAY. Do not copy part (a) into real work.
# Our table contains "orders_in_period" - the number of orders DURING the six months
# we are predicting. At prediction time, that number does not exist yet.

# (a) WRONG: include the future
X_leak = customers[categorical + numeric + ["orders_in_period"]]
Xl_tr, Xl_te, yl_tr, yl_te = train_test_split(X_leak, y, test_size=0.25, random_state=42)
leaky = make_pipe(LinearRegression()).fit(Xl_tr, yl_tr)
print("(a) WITH the future column   R^2 =", round(r2_score(yl_te, leaky.predict(Xl_te)), 3), " <- looks amazing")

# (b) HONEST: only what we know at prediction time
print("(b) WITHOUT it (our pipeline) R^2 =", round(cross_val_score(make_pipe(LinearRegression()), X2, y, cv=5).mean(), 3))'''

cells = [
    md("""# A03 · Models You Can Trust

**IMB 2026 · MADA · Workshop A03 (Fri 19 Jun 2026, 9:00–12:00)**

Wednesday's model predicted a *category* (returns / doesn't). Today the CFO wants a
**number**:

> *"For each new customer — how much will they spend with us over the next six
> months? And before you bet my budget on it: how do I know your model isn't lying?"*

Both halves of that question matter. By the end you will be able to:

- train and evaluate a regression model with business-readable metrics (MAE, R²),
- use the text columns we skipped on Wednesday (one-hot encoding, `ColumnTransformer`, `Pipeline`),
- compare models honestly with cross-validation and a dummy baseline,
- spot **data leakage** — the classic way analyses lie by accident,
- and take home the end-to-end homework (due **30 Jun 2026**)."""),
    md("""## 0 · Setup

One row per customer; the familiar features **plus** the text columns we dropped on
Wednesday — and the target `six_month_spend` in euros."""),
    code(LOADER + '\ncustomers = load_file("customer_value.csv")\nprint(customers.shape)\ncustomers.head()'),
    code(S["setup_cols"]),

    md("""## 1 · First regression, in euros

Same rhythm as Wednesday — split, fit, score — new model (`LinearRegression`) and new
metrics:

- **MAE** (mean absolute error): *"on average we're off by € this much per customer"* — a
  number a CFO can use directly;
- **R²**: roughly, the share of spend variation the model explains (1.0 = perfect, 0 = useless)."""),
    todo('using only the numeric features: split (test_size=0.25, random_state=42), fit LinearRegression, print MAE and R² on the test set',
         'mean_absolute_error(y_test, pred) and r2_score(y_test, pred)'),
    solution(S["first_reg"]),
    todo('inspect the coefficients: which feature moves predicted spend the most per unit?',
         'pd.DataFrame with numeric and reg.coef_'),
    solution(S["coefs"]),
    answer("Finish the sentence for the CFO: 'Customers who … spend about €… more.' Then add the caveat from Wednesday: why might that NOT be a causal lever?"),

    md("""## 2 · The columns we keep ignoring

`country`, `segment`, `acquisition_channel` — Wednesday we dropped them. Watch what
happens if we feed them to the model raw *(pre-written demo — read the error, that's
the exercise)*:"""),
    code(S["cat_fail"]),
    md("""Models eat numbers. **One-hot encoding** turns `country` into six 0/1 columns
(`country_Slovenia`, `country_Italy`, …). Doing that by hand invites mistakes, so
scikit-learn gives us:

- `ColumnTransformer` — *which* preparation applies to *which* columns;
- `Pipeline` — preparation + model glued into **one object**: one `fit`, one `predict`,
  preparation impossible to forget or apply twice."""),
    todo('build the ColumnTransformer (OneHotEncoder for the categorical columns, passthrough for the rest), wrap it with LinearRegression in a Pipeline, fit on a fresh split of ALL features, print MAE and R²',
         'Pipeline([("prep", prep), ("model", LinearRegression())])'),
    solution(S["pipeline"]),
    answer("Compare Section 1 vs Section 2: how much did the text columns improve MAE and R²? Was ignoring them on Wednesday costly?"),

    md("""## 3 · One split is one opinion

What if our 25% test drawer was *lucky*? **Cross-validation** rotates the drawer:
5 splits, 5 scores — a mean **and** a spread instead of one opinion. And every
comparison needs a **dummy baseline** (always predicts the average): any model that
can't beat it is decoration."""),
    todo('run 5-fold cross_val_score on your pipeline and print the five R² scores, their mean and std',
         'cross_val_score(pipe, X2, y, cv=5)'),
    solution(S["cv"]),
    todo('compare three pipelines with cross-validation: DummyRegressor, LinearRegression, DecisionTreeRegressor(max_depth=4) — collect results in a DataFrame (this exact table format is what the homework expects)',
         'loop over a dict of models, cross_val_score each inside the same pipeline'),
    solution(S["compare"]),

    md("""## 4 · How analyses lie by accident

Our table hides a trap — a column called `orders_in_period`: the number of orders the
customer placed **during the six months we are predicting**. Including it means using
information from the *future*. The demo below shows what that does to the score
*(pre-written — this is the WRONG way, watch it, don't copy it)*:"""),
    code(S["leak"]),
    todo('name the mistake: in one sentence, why is the score in (a) a lie even though the code runs perfectly?',
         'think: would orders_in_period exist at the moment of prediction?'),
    solution('# (a) "predicts" spend from the order count of the SAME six months - information\n# that does not exist at prediction time. The model explains the past, it cannot\n# predict the future. This is data leakage (here: future information / target leakage).'),
    md("""**Leakage is the #1 way smart people produce impressive, useless models.** It is
why pipelines matter (all preparation learned inside the cross-validation loop), and
why your first question about any amazing score should be: *"what did the model know,
and when did it know it?"* — **trust but verify.** Remember that phrase; it returns
on Monday."""),

    md("""## 5 · The recommendation

Time to commit. Based on your comparison table: which model do you recommend the CFO
deploy, and why? A CFO-grade justification has four parts: the **metric** (in euros),
the **baseline comparison**, the **stability** (std across folds), and one honest
**limitation**."""),
    answer("My recommendation (3 sentences): model, evidence (MAE/R² vs dummy, stability), limitation."),

    md("""## 6 · 🏠 The homeworks (two!)

**Homework 1 — Expansion markets (regression) · due Tue 30 Jun 2026.**
Adriatica is expanding into **France, Czechia and Poland**. In `homework-mada.ipynb`:
explore the pilot customer table, build a leak-proof pipeline, compare at least two
models against the dummy with cross-validation, and end with a 3-sentence
recommendation. Rubric and scaffolding are in the notebook.

**Homework 2 — The win-back campaign (classification) · due Wed 1 Jul 2026.**
Marketing piloted a win-back voucher on 804 lapsed customers. In
`homework2-winback.ipynb`: predict who responds, evaluate honestly, and tell the CMO
whom to target with a budget of 1,560 vouchers. This one is graded **70% on objective
criteria and 30% on judgement** (your recommendation memo, communication, insight) —
the full rubric is in `GRADING.md` next to the notebook.

**Open both now**, run their setup cells, and **File → Save a copy in Drive** —
confirm they work before you leave. Help session for both: **Tue 30 Jun, 13:00–17:00**.

**AI policy (both):** free AI tools (Gemini, Learn Mode) are allowed and encouraged —
and must be declared in the final cell. You must be able to explain every line.
And watch out: each homework table contains a certain kind of column you now know
better than to use…"""),

    md("""## 7 · Wrap-up

You now own the honest-ML toolkit: encode → pipeline → cross-validate → beat the
dummy → suspect leakage → recommend with limitations. That *is* professional applied ML.

**Monday (A04):** a different kind of model — one that *talks*. Large language models
for business decisions: what they're brilliant at, how confidently they lie, and how
an analyst (you) verifies them. Same refrain, new subject: **trust but verify**."""),
]

# --------------------------------------------------------------- homework
hw_cells = [
    md("""# MADA Homework — Expansion Markets

**Assigned:** Fri 19 Jun 2026 (Workshop A03) · **Due: Tue 30 Jun 2026, 23:59** ·
Help session: Tue 30 Jun, 13:00–17:00

Adriatica's pilot in **France, Czechia and Poland** produced the customer table
`hw_customers.csv` (same structure as the A03 table, new markets). Management asks:
**how much will a pilot customer spend in six months, and which model should we use
to predict it?**

## Deliverable

This notebook, completed, as a **Colab share link** (Anyone with the link → Viewer).
Work through the four sections below; keep all cells you ran.

## Rubric (20 points)

- **Exploration** (4) — data loaded, shapes/types checked, at least one meaningful look at the new markets
- **Leak-proof pipeline** (6) — correct one-hot encoding via ColumnTransformer inside a Pipeline; *only information available at prediction time used as features*
- **Honest comparison** (6) — ≥ 2 real models + dummy baseline, 5-fold cross-validation, results in a table
- **Recommendation** (3) — 3 sentences: model, evidence, limitation
- **AI-use declaration** (1) — filled in, honest ("none" is a fine answer)

## AI policy

Free AI tools (Gemini, Learn Mode, Colab AI) are **allowed and encouraged** for hints
and debugging. You must understand and be able to explain every line you submit.
Declare what you used in the final cell."""),
    md("""## 1 · Setup and exploration"""),
    code(LOADER + '\ncustomers = load_file("hw_customers.csv")\nprint(customers.shape)\ncustomers.head()'),
    todo('explore: dtypes, missing values, and at least one summary that tells management something about the three new markets',
         'think A01: info(), isna().sum(), groupby("country")'),
    md("""## 2 · A leak-proof pipeline

Define your feature lists and build the pipeline. Think carefully about **which
columns a model may legitimately use** — what do we actually know about a customer
at prediction time?"""),
    todo('define categorical and numeric feature lists and the target; build a Pipeline with ColumnTransformer + OneHotEncoder for the categoricals'),
    md("""## 3 · Honest comparison"""),
    todo('compare at least two real models plus DummyRegressor using 5-fold cross-validation; collect mean and std of R² in a results DataFrame (the A03 Section 3 table format)'),
    md("""## 4 · Recommendation"""),
    md("""**✍️ My recommendation (3 sentences — model, evidence, limitation):**

> *(double-click and write here)*"""),
    md("""## 5 · AI-use declaration

**Tools used and for what:**

> *(e.g. "Gemini Learn Mode for a hint on ColumnTransformer syntax; Colab autocomplete." — or "none")*"""),
]

chunks = [
    ("setup", 'customers = load_file("customer_value.csv")\nimport pandas as pd\n' + S["setup_cols"]),
    ("first_reg", S["first_reg"] + '\nassert 0.5 < r2_score(y_test, pred) < 0.8'),
    ("coefs", S["coefs"]),
    ("cat_fail", S["cat_fail"]),
    ("pipeline", S["pipeline"] + '\nassert r2_score(y2_test, pred2) > r2_score(y_test, pred) + 0.05'),
    ("cv", S["cv"]),
    ("compare", S["compare"] + '\nassert comparison.iloc[0]["model"] == "linear regression"\nassert comparison.iloc[-1]["cv_r2_mean"] < 0.05'),
    ("leak", S["leak"] + '\nassert r2_score(yl_te, leaky.predict(Xl_te)) > 0.9'),
    ("hw_setup", 'hw = load_file(r"../homework/data/hw_customers.csv")\nassert hw.shape == (420, 11), hw.shape'),
]

if __name__ == "__main__":
    save(cells, "lab-a03-models-you-can-trust", "lab-a03-models-you-can-trust.ipynb")
    save(hw_cells, "lab-a03-models-you-can-trust/homework", "homework-mada.ipynb")
    write_smoke("a03", "lab-a03-models-you-can-trust/data", chunks)
