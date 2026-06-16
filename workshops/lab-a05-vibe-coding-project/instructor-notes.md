# Instructor notes — A05 · Vibe Coding the MADA Project

**Session:** Wed 1 Jul 2026, 9:00–12:00 (3h) · **Notebook:** `lab-a05-vibe-coding-project.ipynb`
**Presentations:** Fri 3 Jul. · **Before class:** set `DATA_BASE_URL`; align the AI tool with Aleš (whatever Vibe coding 1 used on 29 Jun) — Colab's Gemini panel is the safe default; **Gemini CLI must not be used** (free tier ended 18 Jun 2026).

## Timing plan (180 min)

| Block | Section | Minutes |
|---|---|---|
| Intro + the loop + tool/budget note | 0 | 10 |
| Disciplined warm-up (spec → generate → verify) | 1 | 35 |
| Code-review drill (quiet failure) | 2 | 20 |
| Crash recovery drill | 3 | 15 |
| **Project slice — main block** | 4 | 80 |
| Dry run + peer check + course wrap | 5 | 20 |

## Verification anchors (exact)

- FY total revenue: **€815,629.71** (after dropping the 30 duplicate rows)
- Best month: **December 2024 = €96,505.68**

## The planted drills

**Section 2 — quiet failure** (runs fine, wrong twice):
1. Sums `quantity` but labels it revenue → prints total ≈ **10,167** "EUR" (vs €815,630 — the anchor catches it instantly);
2. `strftime("%B")` month names → alphabetical x-axis (April, August, December…) — trend unreadable;
3. Bonus: never dropped the duplicates.

**Section 3 — crash:** invented columns (`revenue`, `cost`, `region`) → `KeyError: 'revenue'`. The cell ships with `RUN_BROKEN = False` so Run-all works; students flip it to experience the crash. The drill's deliverable is the *feedback prompt* (error + real columns + expectation).

## Main block coaching (Section 4)

- Insist on the spec card BEFORE any prompting; visit each group at spec stage.
- Every group must verify at least one generated number against something hand-checkable — ask "which number did you check, and how?" on every visit.
- The prompt log is the deliverable norm (their AI-use declaration for Friday) — groups that skip it get reminded it's presentable evidence they used AI *professionally*.
- **Antigravity budget** (if that's the class tool): free tier ≈ 20 agent requests/day (as of mid-2026 — re-verify) → have groups draft prompts in the spec card first, spend deliberately. Colab Gemini panel has no such per-day wall and is the fallback.
- Groups without usable project data: point them at this workshop's `orders.csv` — "build the analysis slice on Adriatica, swap your data tonight".

## Wrap-up

End on the course through-line: A01 describe → A02 predict → A03 honest models → A04 verify the AI's words → A05 verify its code. *Trust but verify* is the exam answer to everything.
