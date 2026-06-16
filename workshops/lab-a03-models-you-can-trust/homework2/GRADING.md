# Grading — Homework 2: The Win-Back Campaign (ML classification)

**Course:** IMB 2026 · MADA · data analytics & AI strand
**Assigned:** Fri 19 Jun 2026 (Workshop A03) · **Due: Wed 1 Jul 2026, 23:59**
**Deliverable:** completed `homework2-winback.ipynb` as a Colab share link (Anyone with the link → Viewer)
**Total: 100 points** = **objective 70** (criteria-based, reproducible) + **subjective 30** (judgement-based, anchored below)

---

## Part A — Objective criteria (70 points)

| # | Criterion | Points | What earns full points |
|---|-----------|--------|-------------------------|
| A1 | **Exploration** | 10 | Data loaded; shape/dtypes/missing checked; response rate computed; at least one meaningful look at how responders differ from non-responders (groupby or pivot) |
| A2 | **Leak-proof pipeline** | 20 | Categorical columns one-hot encoded via `ColumnTransformer` inside a `Pipeline`; **only information available at campaign-send time used as features**. Using `voucher_redeemed` (or anything derived from the outcome) = 0 points on this criterion |
| A3 | **Honest evaluation** | 20 | Train/test split with `random_state=42`; 5-fold cross-validation reported (mean ± std); comparison against the majority-class baseline; confusion matrix on the test set with both error types read correctly in campaign terms |
| A4 | **Targeting analysis** | 10 | The provided ranking cell executed on the fitted pipeline; top-30% response rate vs. overall response rate reported and correctly interpreted (what does the difference mean for the campaign?) |
| A5 | **Reproducibility & declarations** | 10 | Notebook runs top-to-bottom without errors on Colab free tier; fixed random states; AI-use declaration filled in honestly ("none" is acceptable) |

**Automatic flags (graders check these first):**

- Test/CV accuracy ≳ 0.95 → almost certainly the `voucher_redeemed` leak → A2 = 0, and A3 is graded on what remains.
- Notebook does not run top-to-bottom → A5 capped at 4, and only cells that ran are graded elsewhere.

## Part B — Subjective criteria (30 points)

Graded on judgement, against the anchors below. Two independent reads are recommended where feasible; graders note one sentence of justification per criterion.

### B1 · Business recommendation memo (15 points)

The closing memo to the CMO (~150–250 words): whom to target with the 1,560 available vouchers (of ~5,200 lapsed customers), the expected outcome, and the decision's limits.

| Level | Points | Anchor description |
|---|---|---|
| Excellent | 13–15 | A decision, not a description: concrete targeting rule, quantified expected responses using the student's own numbers, costs/limits acknowledged, a next step (e.g., A/B holdout) proposed |
| Good | 10–12 | Clear recommendation with mostly correct quantification; limitations mentioned but thin |
| Adequate | 6–9 | Restates model outputs and gestures at a recommendation; numbers present but not woven into the decision |
| Weak | 1–5 | Generic prose ("the model is useful for marketing"), no quantification, or recommendation contradicts the student's own evidence |
| Missing | 0 | No memo |

### B2 · Communication & storytelling (10 points)

The whole notebook read as a document for a business audience.

| Level | Points | Anchor description |
|---|---|---|
| Excellent | 9–10 | A reader who skips the code still follows the argument: sections narrate, outputs are interpreted in words, charts/tables labeled, no orphan numbers |
| Good | 7–8 | Mostly narrated; occasional bare outputs left unexplained |
| Adequate | 4–6 | Code-with-comments style; interpretation sparse or formulaic |
| Weak | 1–3 | Output dump; a reader cannot reconstruct the argument |

### B3 · Critical insight beyond the minimum (5 points)

Anything that shows independent thinking: probing a driver's plausibility, testing a second model *with reasoning about the difference*, questioning the pilot's representativeness, noting selection effects or ethical/GDPR angles of targeting, a smarter budget split, etc.

| Level | Points |
|---|---|
| Genuine insight, correctly executed | 4–5 |
| A reasonable extra step, partially developed | 2–3 |
| Token gesture | 1 |
| Nothing beyond the template | 0 |

---

## Grade scale

| Points | Grade (UP 1–10) | ECTS |
|---|---|---|
| 92–100 | 10 | A |
| 84–91 | 9 | A/B |
| 76–83 | 8 | B |
| 68–75 | 7 | C |
| 60–67 | 6 (pass) | D/E |
| < 60 | 5 (fail) | F |

*(Mapping follows common UP practice — adjust to the programme's official scale if it differs.)*

## Policies

- **AI use:** free AI tools (Gemini, Learn Mode, Colab AI) are allowed and encouraged — and must be declared in the final cell. You must be able to explain every line you submit; the instructor may ask you to walk through your notebook (an unexplainable notebook is treated as not your work).
- **Collaboration:** discussing approaches is fine; notebooks are written individually. Identical code/memos are graded as one work split across the submitters.
- **Late submission:** −10 points per started 24 h, up to 48 h; later only by prior agreement.
