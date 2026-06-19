# Block 2 — The Loop & The Goal

## Goal
Give Claude a real business goal and watch it figure out how to achieve it step by
step. Claude will read the data, plan its approach, write and run Python, and report
back — all without you touching any code. Your job is to approve each step and
verify the result.

## Type this
1. Start Claude Code if it is not already running:
   `claude`
2. Paste this into the chat:
   `Here is a sales file: data/orders.csv. I want a monthly sales report — total revenue per month, and which month was best. Plan your approach first, then do it.`
3. Claude will show you a short plan (something like "I'll read the file, compute
   quantity × unit_price, group by month, and find the maximum"). When it pauses and
   asks whether to continue, type:
   `Yes, go ahead.`
4. Once it finishes and shows you numbers, ask it to confirm the key result:
   `What was the best month, and what was its revenue?`

**Tip — plan mode.** If you want Claude to *only* plan and never act without an
explicit green light, press `Shift+Tab` twice before sending your first message.
That switches to plan mode (`Shift+Tab` cycles: default → acceptEdits → plan). In
plan mode Claude reads and proposes, but makes no changes until you say so.

## You should see
- A short, plain-English plan before any code runs.
- Claude writing a small Python script and executing it on its own.
- A monthly table with one row per month and a "best month" callout.
- The answer to your verification question: **the best month is 2024-12 (December)**.

## If it looks wrong
- The numbers don't add up, or December is not the best month:
  `That doesn't match — December should be the best month. Re-check how you computed revenue (quantity times unit_price).`
- Claude asks for a file path it can't find:
  `The file is at data/orders.csv relative to this folder. Try again.`
- Claude stops mid-task:
  `Please continue where you left off.`
