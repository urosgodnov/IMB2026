# Block 3 — Turning the Dials / Reading the Meter

## Goal
Feel the difference between a quick, cheap response and a slow, thorough one — and
learn to read the meter so you know what you are spending. You will switch models,
change the effort level, and check your token usage, all without leaving the chat.

## Type this
**Part A — switch the effort level and re-run the task.**

1. Set effort to low and run the report task quickly:
   `/effort low`
   `Give me the monthly revenue total and best month from data/orders.csv.`
2. Note how fast it responds and how brief the answer is.
3. Now raise the effort:
   `/effort high`
   `Same question — monthly revenue and best month from data/orders.csv. Think it through carefully.`
4. Notice the difference in depth and time.

**Part B — switch the model.**

5. Try the smaller, faster model:
   `/model sonnet`
   `Summarise the monthly sales results in one sentence.`
6. Try the larger model:
   `/model opus`
   `Summarise the monthly sales results in one sentence.`
7. For a speed burst on Opus (faster, slightly higher cost), toggle fast mode:
   `/fast`

**Part C — read the meter.**

8. Check what you have spent so far this session:
   `/usage`
9. See what is filling up Claude's memory:
   `/context`
10. If the context is getting crowded, free up space without losing your work:
    `/compact`

## You should see
- Low effort: a quick, direct answer with minimal explanation.
- High effort: a more considered answer, possibly with intermediate reasoning shown.
- `/model sonnet` vs `/model opus`: similar quality on a simple summary, but Opus
  ($5/M input tokens) costs more than Sonnet ($3/M) — you can see this in `/usage`.
- `/usage` showing input tokens, output tokens, and a dollar amount that climbs as
  you run more tasks or switch to heavier settings.
- `/context` listing the files and messages currently in Claude's memory window.

## If it looks wrong
- `/usage` shows nothing or zero: you need to run at least one task first, then
  check again.
- `/effort` picker shows levels you don't recognise: the valid levels are `low`,
  `medium`, `high`, `xhigh`, and `max` — type one of those exactly.
- `/fast` says it is switching you to Opus: that is expected — fast mode only works
  on Opus models.
- Do not use `/cost` — that is a different plugin command, not the built-in meter.
  Always use `/usage`.
