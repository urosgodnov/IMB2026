# Instructor notes — A02 · First Machine-Learning Models

**Session:** Wed 17 Jun 2026, 15:00–19:00 (4h, same day as A01) · **Notebook:** `lab-a02-first-ml-models.ipynb`
**Before class:** set `DATA_BASE_URL`; run all cells once.

## Timing plan (240 min)

| Block | Section | Minutes |
|---|---|---|
| Setup + ML vocabulary + baseline | 0–1 | 40 |
| Split + first logistic regression | 2 | 40 |
| *Break* | | 10 |
| Confusion matrix + cost debate | 3 | 45 |
| Decision tree + comparison | 4 | 40 |
| Drivers + marketing summary | 5 | 30 |
| Overfitting demo + choose depth | 6 | 20 |
| Wrap-up + the two confessions | 7 | 15 |

It is hour 5–8 of the students' day: keep lecture moments short, lean on the pre-written cells.

## Ground truth (random_state=42 everywhere — numbers are exact)

- Dataset: **1,093** customers; repeat rate **43.7%** (baseline majority class = 56.3%)
- Split: 819 train / 274 test
- Logistic regression: train **0.829**, test **0.770**
- Confusion matrix: **25** missed returners, **38** wasted discounts
- Tree depth 3: test **0.693**; full-depth tree: train 1.000, test ≈ **0.72** (clearly below logistic)
- Drivers (logreg, by |coef|): newsletter +2.01, support_tickets −1.73, used_discount +0.48, visits +0.37; tree importances led by first_order_value 0.40, support_tickets 0.34
- Overfitting curve peaks around depth 3–5 then slides

## Pitfalls

- The coefficient table: `first_order_value` has a tiny coefficient (0.014) **because it is per-euro and unscaled**, while the tree ranks it top — great discussion fuel ("strength per unit ≠ importance"; scaling is deliberately out of scope today).
- Students comparing train vs test the wrong way round — anchor the vocabulary early ("exam on unseen data").
- Cost-asymmetry debate has no right answer; push groups to commit and defend.

## Talking points

- Name the two confessions explicitly at the end (dropped text columns; one split) — A03's opening assumes the promise was made.
