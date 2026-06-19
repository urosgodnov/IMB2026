# Block 6 — Make It Run Itself + Wrap

## Goal
Tell Claude to schedule the monthly report so it runs automatically, then step back
and reflect on what you built today. You will see two scheduling options: a
session-scoped loop (great for right now) and a persistent cloud schedule (survives
closing your laptop).

## Type this
**Part A — schedule the report.**

1. Inside Claude Code, paste:
   `Set up the monthly report to run on a schedule, every Monday morning, and tell me how it will run.`
2. Claude will likely suggest `/loop` for a session-based schedule or `/schedule`
   for a persistent one. To try the session loop yourself:
   `/loop 1h Generate the monthly sales report from data/orders.csv and summarise the best month.`
   (Press `Esc` at any time to stop the loop.)
3. For a schedule that persists after you close the terminal, ask:
   `Set this up as a persistent weekly schedule using /schedule.`

**Part B — wrap up.**

4. Finally, ask Claude to reflect on the whole session:
   `Summarise what we built today and what I should always double-check before trusting your output.`

## You should see
- `/loop` starting a repeating task on an interval you set (units: s/m/h/d). Claude
  confirms the interval and runs the task on that cadence until you press `Esc`.
  Note: loop tasks expire after 7 days and are session-scoped — they stop if you
  close the terminal.
- `/schedule` pointing to a cloud Routine (minimum interval: 1 hour) that keeps
  running even after your laptop is off.
- A plain-English wrap-up from Claude covering: what was built, what the agent can
  get wrong, and which numbers you should always verify yourself (especially the
  revenue formula and the "best month" result).

## If it looks wrong
- `/loop` or `/schedule` is not available in your setup: that is fine — ask Claude
  to explain how the feature works conceptually, and it will walk you through it.
  The commands exist in the full Claude Code CLI; some restricted environments
  disable cloud features.
- The loop runs but produces different numbers each time: say
  `The report should always show December 2024 as the best month. If it doesn't, re-check the revenue calculation.`
- Claude's wrap-up sounds vague: prompt it further with
  `Be specific — what are three things I should verify before sharing this report with a colleague?`
