# Block 2 — what a correct monthly report looks like

Running `b2-sales-summary.py` on `data/orders.csv` prints a 12-row monthly
table for **July 2024 → June 2025**, with revenue rising into the holiday
season and peaking in December.

- **Best month: 2024-12** — revenue **97,138.60** (raw file, which keeps the
  duplicate orders; a de-duplicated total would be slightly lower).
- Total revenue (raw): about **820,000**.

**The lesson (say it out loud):** the report *ran* — but running is not the
same as *right*. Always check a known number. Here the known number is the
December peak: if the AI's "best month" is not 2024-12, its revenue formula is
wrong (it probably summed `quantity` instead of `quantity * unit_price`).
