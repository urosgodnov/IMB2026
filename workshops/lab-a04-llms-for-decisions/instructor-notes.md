# Instructor notes — A04 · LLMs for Business Decisions

**Session:** Mon 22 Jun 2026, 9:00–12:00 (3h) · **Notebook:** `lab-a04-llms-for-decisions.ipynb`
**Before class:** set `DATA_BASE_URL`; verify Gemini (gemini.google.com) opens with a plain Google account from the classroom network; run the `google.colab.ai` cells once on YOUR account to confirm availability.

## Timing plan (180 min)

| Block | Section | Minutes |
|---|---|---|
| Intro + two-tab setup | 0 | 15 |
| Summarise / extract / classify + iteration | 1 | 55 |
| *Break* | | 10 |
| Hallucination hunt | 2 | 20 |
| Verification with pandas | 3 | 30 |
| Programmatic prompting (`google.colab.ai`) | 4 | 20 |
| Use-case map + risks + HITL + EU AI Act | 5 | 25 |
| Wrap-up | 6 | 5 |

## Ground truth for the verification exercise (Section 3 — exact, after dedup)

- Best month: **2024-12**, revenue **€96,505.68**
- Top product by revenue: **Compact Mirror 042**
- Average order value: **€176.77**
- (FY total, if asked: **€815,629.71**; top country: **Slovenia** — both also appear in the report, which is internally consistent with the data.)

## What to expect from Gemini in the hallucination hunt

Adriatica is fictional; outcomes vary by day and model version. Typical behaviours, all teachable:
1. **Confident invention** (specific wrong numbers) — the jackpot for the lesson;
2. **Refusal / "I don't have data on Adriatica"** — also a win: "the honest mode exists; you still must verify when it *doesn't* refuse";
3. **Asking for the data** — bridge directly to grounding (Section 1 worked because the report was in context).
If the whole class gets refusals, have them add "make a best estimate" to the prompt — the inventions appear.

## `google.colab.ai` notes (Section 4)

- Free tier, monthly limits; the notebook says pairs may share one run. If quota bites: do the section as a demo from the instructor account; the cells are guarded (try/except) so Run-all never breaks.
- Output is not guaranteed clean CSV — the parse cell prints a friendly message on failure; that *is* the lesson (tighten the prompt).

## Stretch — Section 7: semantic search with Qdrant (optional, added 2026-06-12)

- **Not in the timing plan** — for fast finishers (~15 min) or at home; nothing depends on it.
- Fully free and local: `pip install "qdrant-client[fastembed]"`, `QdrantClient(":memory:")` — no server, no account, no API key. The embedding model (BAAI/bge-small-en-v1.5, ~67 MB) downloads **anonymously from Hugging Face** on first use; budget 1–2 min for install + download + indexing. ⚠ Verify the classroom network allows pip + huggingface.co during the Colab pilot.
- Expected demo output (verified 2026-06-12): keyword search for "shattered" → **0 hits**; semantic query `"my parcel arrived shattered"` → top hit "arrived in pieces, box completely crushed", with the smashed mirror and cracked glass also in the top 5. Two non-breakage parcel problems appear too — **that is deliberate**: the follow-up text teaches "similarity, not truth".
- Teaching hook: this is the retrieval half of RAG — connect it back to Section 2 (the LLM hallucinated *because it had no data*; retrieval is how real systems ground it).
- All cells are guarded (ImportError/NameError) — Run-all stays green even if the install cell was skipped.
- API note: the notebook uses the current qdrant-client pattern (`create_collection` + `upload_collection` with `models.Document` + `query_points`); the older `client.add()`/`client.query()` you may see in tutorials is **deprecated since 1.16** — steer students to the notebook's pattern.

## Sensitive points

- Confidentiality slide: be explicit — no pasting classmates' data, grades, or anything personal into free chat tools. This sets up the homework/AI-declaration norm and the A05 prompt log.
- EU AI Act: keep to the two-line risk-based framing in the notebook; don't drift into legal detail.
