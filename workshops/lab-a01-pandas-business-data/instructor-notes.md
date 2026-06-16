# Instructor notes — A01 · Pandas — Working with Business Data

**Session:** Wed 17 Jun 2026, 9:00–13:00 (4h) · **Notebook:** `lab-a01-pandas-business-data.ipynb`
**Before class:** set `DATA_BASE_URL` in the first code cell (see `../README.md`), run all cells once yourself.

## Timing plan (240 min)

| Block | Section | Minutes |
|---|---|---|
| Welcome + Colab orientation | 0 | 20 |
| First contact (load/inspect/Excel) | 1 | 35 |
| Filtering, revenue, top-10 | 2 | 35 |
| *Break* | | 10 |
| Dirty data sequence | 3 | 55 |
| Management questions (groupby/merge/pivot) | 4 | 50 |
| Charts | 5 | 25 |
| Wrap-up + bridge to A02 | 6 | 10 |

If behind schedule: compress Section 5 to the line chart only (bar+histogram become self-paced).

## Ground truth (deterministic — students with random_state-free code get these exactly)

- Raw sizes: orders **4,644** rows (incl. **30** duplicates → 4,614 clean); customers **1,215** (incl. **15** duplicates → 1,200 clean)
- Missing: **40** emails, **25** countries; label variants: SI 43, slovenia 15, Italia 23, HR 17
- Filters: **79** orders > €500; **933** Electronics orders
- Monthly revenue: total **€815,629.71**; best month **2024-12 = €96,505.68** (clear Nov–Dec holiday peak, mild upward trend)
- Revenue by country: **Slovenia first (€247,057.14)**, then Italy, Germany
- Top product by revenue: **Compact Mirror 042**
- AOV consumer vs business: business clearly higher (pivot exercise)

## Pitfalls to expect

- Students running cells out of order → "NameError: orders is not defined": teach Runtime → Run all / run-from-top recovery early.
- `to_period("M")` is given as a hint — don't let groups burn time discovering it.
- In Section 4, students who skipped the orders dedup get slightly different revenue numbers — that *is* the teaching moment (point at the 30 duplicates).
- The "📌 remember this number" callout (December revenue, FY total) matters: A04 and A05 verify against these anchors.

## Talking points

- Frame every fix in Section 3 as a business decision (drop vs fill vs flag), not syntax.
- Section 5 reflection: averages hide distributions (histogram shows the long tail driving AOV).
