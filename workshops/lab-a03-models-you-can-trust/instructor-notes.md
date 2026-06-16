# Instructor notes — A03 · Models You Can Trust

**Session:** Fri 19 Jun 2026, 9:00–12:00 (3h) · **Notebook:** `lab-a03-models-you-can-trust.ipynb`
**Homework:** `homework/homework-mada.ipynb` (due Tue 30 Jun 2026; help session 30 Jun 13:00–17:00)
**Before class:** set `DATA_BASE_URL` in BOTH notebooks; run all cells once.

## Timing plan (180 min)

| Block | Section | Minutes |
|---|---|---|
| Setup + first regression in euros | 0–1 | 35 |
| Categorical fail → encoder → pipeline | 2 | 40 |
| Cross-validation + 3-model comparison | 3 | 35 |
| *Break* | | 10 |
| Leakage demo + naming the mistake | 4 | 25 |
| Recommendation writing | 5 | 15 |
| Homework briefing (open it live!) | 6 | 15 |
| Wrap-up | 7 | 5 |

## Ground truth (random_state=42, cv=5 — exact)

- Numeric-only regression: MAE **€127.66**, R² **0.642**
- Pipeline with one-hot categoricals: MAE **€99.65**, R² **0.785** (the payoff: ~€28/customer better)
- Cross-validation (LR pipeline): **0.767 ± 0.028**
- Comparison: linear regression > tree(4) > dummy (dummy R² ≈ 0, MAE €210.21)
- **Leakage demo: R² 0.969 with `orders_in_period` vs 0.767 honest** — the punchline number
- Biggest legit coefficient direction: business segment / country effects (Germany high, Hungary low), newsletter ≈ +€45

## Homework 1 grading notes (regression, due 30 Jun)

- `hw_customers.csv`: 420 rows, France/Czechia/Poland, **different coefficients** — workshop numbers don't transfer (by design)
- Expected honest result: CV R² ≈ **0.5–0.65** with a proper pipeline
- **Leakage flag:** any submission with R² ≳ 0.9 almost certainly used `orders_in_period` — that is the rubric's "leak-proof" criterion failing, not a brilliant model. The notebook hints at the trap without naming the column.
- AI-use declaration is worth 1 point and sets the A05 norm — grade it generously, but require it.

## Homework 2 grading notes (classification "win-back", due 1 Jul)

Full rubric (students see it too): `homework2/GRADING.md` — 100 pts, **objective 70 / subjective 30**.

Reference-solution ground truth (`hw2_winback.csv`, 804 rows, response rate **38.4%**):
- Honest pipeline (logistic regression, all legitimate features): test accuracy **0.781**, 5-fold CV **0.774**, vs majority baseline **0.616**
- Provided targeting cell: overall test response rate **0.358**, top-30% **0.750** → lift ≈ **2.1×**
- Expected memo arithmetic: 1,560 targeted vouchers ≈ 1,560 × 0.75 ≈ **1,170 responses** vs ≈ 560 for random targeting — students whose numbers differ slightly (different model/threshold) are fine; the *reasoning* is what B1 grades
- **Leakage flag: accuracy ≳ 0.95 ⇒ `voucher_redeemed` was used** (reference leaky model: 0.98) → A2 = 0 per the rubric
- Subjective part (30 pts): use the anchors in GRADING.md, write one justification sentence per criterion; if two readers are feasible, average B1–B3. Calibration tip: grade three notebooks, then revisit the first.
- Acceptable model variety: tree/k-NN instead of logistic regression is fine if evaluated honestly; reward (B3) reasoning about *why* results differ, not the mere extra model.

## Pitfalls

- The `cat_fail` demo cell is try/except so Run-all works — make sure students *read* the ValueError, that's the exercise.
- Some students will one-hot encode by hand with `pd.get_dummies` — accept it, then show why the pipeline version survives cross-validation and new data (`handle_unknown="ignore"`).
- Keep the leakage language precise: the column is *future information*; "target leakage" is the term to leave them with.
