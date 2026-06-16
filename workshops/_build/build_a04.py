# -*- coding: utf-8 -*-
"""Build lab-a04-llms-for-decisions notebook + smoke test."""
from pathlib import Path

from nb import LOADER, answer, code, gemini, md, save, solution, todo, write_smoke

DATA = Path(__file__).resolve().parents[1] / "lab-a04-llms-for-decisions" / "data"
REPORT = (DATA / "quarterly-report.md").read_text(encoding="utf-8")
EMAILS = (DATA / "complaint-emails.txt").read_text(encoding="utf-8")
REVIEWS = (DATA / "reviews.txt").read_text(encoding="utf-8")

S = {}

S["paste_csv"] = '''import io

pasted_csv = """product,issue,severity
EXAMPLE Travel Speaker,damaged on arrival,high
EXAMPLE Desk Pad,wrong item received,medium"""
# ^ replace the example lines with the CSV Gemini produced for you (keep the header row)

complaints = pd.read_csv(io.StringIO(pasted_csv))
complaints'''

S["verify"] = '''orders["revenue"] = orders["quantity"] * orders["unit_price"]
orders["month"] = pd.to_datetime(orders["order_date"]).dt.to_period("M")

best_month = orders.groupby("month")["revenue"].sum().idxmax()
top_product = orders.groupby("product_name")["revenue"].sum().idxmax()
avg_order_value = orders["revenue"].mean()

print("best month:      ", best_month)
print("top product:     ", top_product)
print("avg order value: ", round(avg_order_value, 2), "EUR")'''

S["colab_ai"] = '''# Programmatic prompting with Colab's built-in (free) Gemini access - no API key.
# NOTE: free tier has monthly limits; we use only a few calls today.
try:
    from google.colab import ai
    prompt = """Extract a CSV table with columns product,issue,severity from these
customer emails. Output ONLY the CSV, no explanation.

""" + complaint_emails
    result = ai.generate_text(prompt)
    print(result)
except ImportError:
    print("(google.colab.ai is only available inside Google Colab - skipping here)")'''

S["colab_ai_parse"] = '''try:
    from google.colab import ai  # noqa: F401
    complaints_auto = pd.read_csv(io.StringIO(result))
    print(complaints_auto)
except ImportError:
    print("(skipped outside Colab)")
except Exception as e:
    print("Parsing failed - LLM output was not clean CSV. This is normal; tighten the prompt.")
    print(type(e).__name__, str(e)[:100])'''

# --- Section 7 stretch: semantic search over reviews with Qdrant (local mode) ----
# Corpus deliberately avoids the words "broken", "damaged", "shattered" so the
# keyword-vs-meaning demo lands: Ctrl+F finds nothing, the vector search finds all
# the breakage reviews. Synonym families: breakage, slow/good delivery, bad/good
# service, battery/build quality, price/value, delight, misc.
STRETCH_REVIEWS = [
    "The Premium Puzzle 044 arrived in pieces, the box was completely crushed.",
    "Glass front of the Classic Hair Dryer 035 was cracked when I unpacked it.",
    "Box looked fine but the handle of the kettle inside had snapped off.",
    "My Max Building Set 043 fell apart after a single evening of play.",
    "The seams came apart the first time I used it.",
    "One corner of the parcel was smashed and so was the mirror inside.",
    "Three weeks for delivery is simply not acceptable.",
    "Courier kept postponing, the parcel showed up ten days late.",
    "Ordered it for a birthday and it arrived long after the party.",
    "Shipping took forever even though the site promised 48 hours.",
    "Still waiting for the second half of my order.",
    "Tracking said delivered while the parcel was nowhere to be found.",
    "Arrived a day early and neatly packed.",
    "Fast shipping, no complaints there.",
    "Smooth delivery and a lovely unboxing experience.",
    "Support never answered either of my two emails.",
    "The refund took two months and three phone calls.",
    "Chat agent closed my ticket without solving anything.",
    "I was on hold for forty minutes and then got cut off.",
    "They promised a callback that never came.",
    "Customer service replaced my faulty unit within days, brilliant.",
    "The support agent was patient and genuinely helpful.",
    "Return process was completely painless.",
    "Battery of the Travel Speaker 012 dies after barely an hour.",
    "The charge does not even last my short commute.",
    "Buttons feel flimsy, like they will give up within a month.",
    "Cheap materials for a supposedly premium product.",
    "It stopped charging in the second week.",
    "The hinge wobbles - build quality is disappointing.",
    "Great value for money, I would buy it again.",
    "Overpriced for what it actually does.",
    "Half the price of the competitors and works just as well.",
    "Caught it on discount and I am very happy.",
    "Not worth the premium label at all.",
    "The Basic Kettle 020 is quiet and quick, love it.",
    "My nephew adores the Basic Pen Set 053.",
    "Exactly as described, works perfectly.",
    "Five stars, the best purchase I made this year.",
    "The design is gorgeous and it simply works.",
    "Does its job day after day without any fuss.",
    "The manual was confusing but the product itself is fine.",
    "App pairing failed twice before it finally worked.",
    "Wrong colour delivered, decided to keep it anyway.",
    "Sizing runs small, order one size up.",
    "I received someone else's order and had to send it back.",
]
# The keyword-vs-meaning demo only lands if Ctrl+F genuinely finds nothing:
_forbidden = sorted({w for r in STRETCH_REVIEWS for w in ("shattered", "broken", "damaged") if w in r.lower()})
assert not _forbidden, f"stretch corpus must avoid the demo keywords, found: {_forbidden}"

S["stretch_corpus"] = (
    "# Last month's reviews (synthetic, like everything at Adriatica). Pre-written - just run it.\n"
    "last_month_reviews = [\n"
    + "".join(f"    {r!r},\n" for r in STRETCH_REVIEWS)
    + "]\nprint(len(last_month_reviews), \"reviews\")"
)

S["stretch_index"] = '''# Build the vector index (pre-written). The first run downloads a small (~67 MB)
# embedding model and embeds the reviews - allow a minute or two on Colab.
try:
    import fastembed  # noqa: F401  (the embedding engine - comes with the install cell)
    from qdrant_client import QdrantClient, models

    MODEL = "BAAI/bge-small-en-v1.5"  # turns text into 384 numbers - "meaning coordinates"
    client = QdrantClient(":memory:")  # a real vector database, running inside this notebook

    client.create_collection(
        collection_name="reviews",
        vectors_config=models.VectorParams(
            size=client.get_embedding_size(MODEL), distance=models.Distance.COSINE),
    )
    client.upload_collection(
        collection_name="reviews",
        vectors=[models.Document(text=r, model=MODEL) for r in last_month_reviews],
        payload=[{"review": r} for r in last_month_reviews],
        ids=range(len(last_month_reviews)),
    )
    print("indexed", len(last_month_reviews), "reviews")
except ImportError:
    print("(qdrant-client/fastembed not installed - run the install cell above first. This section is optional.)")'''

S["stretch_search"] = '''# Pre-written demo - just run it.
try:
    def search(question, top=5):
        """Ask the review pile a question in plain English."""
        hits = client.query_points(
            collection_name="reviews",
            query=models.Document(text=question, model=MODEL),
            limit=top,
        ).points
        for h in hits:
            print(f"{h.score:.3f}  {h.payload['review']}")

    # The Ctrl+F way first - keyword search for the customer's own word:
    keyword_hits = [r for r in last_month_reviews if "shattered" in r.lower()]
    print("keyword hits for 'shattered':", keyword_hits)
    print()

    # The meaning way - the customer's complaint, verbatim:
    search("my parcel arrived shattered")
except (NameError, ImportError):
    print("(run the install + index cells above first. This section is optional.)")'''

S["stretch_solution"] = '''search("complaints about slow delivery and parcels arriving late", top=10)

# The top hits are all delivery complaints, from several DIFFERENT customers
# -> a pattern, not a one-off.
# Watch the scores fall: below roughly 0.70 the results drift off-topic (a wrong
# order, even a POSITIVE delivery review) - that drop is your "how many hits are
# really about my question?" signal. And one genuinely late delivery ("ordered it
# for a birthday...") hides far down the list: meaning search is a better net than
# Ctrl+F, not a perfect one. Before the board acts on this, count the orders
# actually affected (pandas, Section 3 style).'''

S["stretch_assert"] = '''assert keyword_hits == [], keyword_hits  # the demo premise: Ctrl+F finds nothing
try:
    hits = client.query_points(
        collection_name="reviews",
        query=models.Document(text="my parcel arrived shattered", model=MODEL),
        limit=5,
    ).points
    texts = [h.payload["review"].lower() for h in hits]
    breakage = [t for t in texts
                if any(w in t for w in ["pieces", "cracked", "snapped", "crushed", "smashed", "came apart"])]
    assert len(breakage) >= 2, texts  # the demo's point: breakage reviews rank top despite zero shared keywords
    assert any(w in texts[0] for w in ["pieces", "crushed", "smashed"]), texts[0]  # top hit is a true breakage review
    print("qdrant semantic search assert passed")
except (NameError, ImportError):
    pass'''

cells = [
    md("""# A04 · LLMs for Business Decisions

**IMB 2026 · MADA · Workshop A04 (Mon 22 Jun 2026, 9:00–12:00)**

Adriatica's board has discovered AI and wants it *everywhere*. Your job today: find
out what large language models are **actually** good for in management — hands-on,
not from headlines.

You will work in **two tabs**:

1. **[Gemini](https://gemini.google.com)** (free, your Google account) — where you talk to the model
2. **this notebook** — your artifacts, your verification code, your notes

By the end you will be able to:

- use an LLM for summarising, extraction, classification and drafting on business documents,
- iterate on prompts deliberately and judge output quality,
- explain tokens, context windows and hallucination in management terms,
- **verify an LLM's claims against data with pandas** instead of trusting them,
- map where LLMs belong — and don't — in business decisions (risks, human-in-the-loop, EU AI Act basics)."""),
    code(LOADER + '\n# As in A01: the export contains duplicate rows - drop them before any analysis.\norders = load_file("orders.csv").drop_duplicates()\nprint("orders loaded:", orders.shape)'),

    # ---------------------------------------------------------------- S1
    md("""## 1 · What LLMs are good at

### 1a · Summarise

Below is Adriatica's annual management report. Copy it into Gemini with this prompt,
then **iterate twice**: once on *format* ("as a table of 5 rows: topic | key fact"),
once on *audience* ("rewrite for the sales team — what should they do differently?").

> **Prompt:** *You are an analyst. Summarise this report in 5 bullet points for the
> board. Each bullet ≤ 15 words.*

---

""" + REPORT + "\n\n---"),
    answer("Paste your best board summary here. What did the format iteration change? What did the audience iteration change?"),
    md("""**Prompt anatomy** — what you just used, named: **role** ("you are an analyst") +
**task** ("summarise in 5 bullets") + **format** ("≤ 15 words each") + optionally an
**example**. Four knobs; iterate one at a time."""),

    md("""### 1b · Extract structure from mess

Eight raw customer complaint emails. Ask Gemini to turn them into a **table** —
prompt: *"Extract a table with columns product | issue | severity (low/medium/high)
from these emails."* Then ask for **the same as CSV, output only the CSV**.

```
""" + EMAILS + """```"""),
    todo('paste the CSV Gemini gave you into the pasted_csv string below and load it with pandas — the round-trip proof: chat output became analysable data',
         'replace the EXAMPLE lines; keep the header'),
    code(S["paste_csv"]),
    md("""*(If the load failed: Gemini wrapped the CSV in prose or backticks — tell it
"output ONLY the raw CSV". Welcome to working with LLMs.)*"""),

    md("""### 1c · Classify

Ten product reviews. Ask Gemini to label each with **sentiment** (positive / negative
/ mixed) and **topic** (product quality / delivery / service / price). Then run a
**second prompt variant** (e.g. add "explain each label in ≤ 5 words") and count
where the two runs *disagree*.

```
""" + REVIEWS + """```"""),
    answer("How many labels disagreed between your two runs? Which reviews were genuinely ambiguous — and would two humans have agreed on them?"),

    # ---------------------------------------------------------------- S2
    md("""## 2 · Where it breaks

**Open a fresh Gemini chat** (no report pasted — that matters). Ask it these three
questions about Adriatica, *as if it knew*:

1. *Which month was Adriatica's best by revenue in FY2024/25, and what was the revenue?*
2. *What was Adriatica's single best-selling product by revenue in FY2024/25?*
3. *What was Adriatica's average order value in FY2024/25?*

Adriatica is our fictional company — **Gemini has never seen its data.** Note what it
does: refuse? hedge? or answer with confident, specific, plausible numbers?"""),
    answer("Record the three answers (or refusals) here, word for word if you can."),
    md("""**Why would it answer at all?** An LLM is not a database. It generates the *most
plausible next words* given your prompt — from patterns in its training data, within
a limited **context window** (what's in the conversation), one **token** (word piece)
at a time. Plausible ≠ true. When the data isn't in the context, a confident answer
is a **hallucination** — and in 1a the data *was* in the context, which is why
summaries mostly work while "facts from nowhere" don't."""),

    # ---------------------------------------------------------------- S3
    md("""## 3 · The analyst who can verify

You have `orders.csv` and you have pandas (A01). The LLM made claims; **check them.**"""),
    todo('compute the true answers: best month by revenue, top product by revenue, average order value',
         'A01 patterns: groupby month / product_name on a revenue column; .idxmax(); .mean()'),
    solution(S["verify"]),
    answer("Score the LLM: how many of its three claims were right? And the report from 1a contains the same three facts — were THOSE right? (Yes — but now you've verified rather than assumed.)"),
    md("""**The signature lesson of this course:**

> *The analyst who can verify beats the analyst who can only ask.*

Friday you learned to distrust amazing R² scores (**trust but verify**). Same refrain
today: an LLM's fluency is not evidence. You — with twenty lines of pandas — are the
fact-checker the board doesn't know it needs."""),

    # ---------------------------------------------------------------- S4
    md("""## 4 · From chatting to building

Chat is fine for one document. For **800 complaint emails a month** you script it.
Colab has free built-in Gemini access from Python — `google.colab.ai`, no API key.
*(Pre-written — run both cells. Free tier has monthly limits, so we spend calls
sparingly: pairs can share one run.)*"""),
    code('complaint_emails = """' + EMAILS.replace('"""', '\\"\\"\\"') + '"""'),
    code(S["colab_ai"]),
    code(S["colab_ai_parse"]),
    md("""Same prompt anatomy, now in a loop-able cell: volume, repeatability, integration
into reports. *That* is when LLM use stops being a toy — and when verification
(Section 3) stops being optional."""),

    # ---------------------------------------------------------------- S5
    md("""## 5 · Where LLMs belong in decisions

### 5a · Use-case map"""),
    answer("For each function — marketing, HR, finance, operations — write ONE high-value LLM use and ONE inappropriate use at Adriatica. (Eight lines total.)"),
    md("""### 5b · The risk list, from today's evidence

- **Hallucination** — you watched it (Section 2). Mitigation: ground it (give it the data) + verify.
- **Confidentiality** — what you paste into a free chat tool leaves the company. Personal
  data, unpublished financials, classmates' graded work: **no**. (This is why the homework
  asks you to *declare* AI use, not hide it.)
- **Bias** — the model inherits its training data's patterns; HR screening is where this bites hardest.
- **Over-reliance** — fluent ≠ correct; the danger grows as the output gets better.

### 5c · Human-in-the-loop + the law

Pattern for any consequential use: **AI drafts → human verifies (against data!) →
human decides → decision is logged with its evidence.**

EU context, in two lines: the **EU AI Act** regulates AI by *risk level* — most of
what you did today is minimal/limited risk (transparency duties: people should know
AI was involved), while HR screening or credit scoring sit in *high-risk* territory
with real obligations. The habit that keeps you on the right side of all of it is the
one you practised today: human verification, documented."""),
    answer("Apply it: Gemini drafts Adriatica's new customer-refund policy. List 4 things a human MUST verify before it ships, and who should sign off."),

    # ---------------------------------------------------------------- S6
    md("""## 6 · Wrap-up

Today: LLMs summarise, extract, classify and draft impressively **when the data is in
front of them**; they hallucinate confidently when it isn't; and you can tell the
difference, because you can verify.

**Next week (A05, Wed 1 Jul):** the AI writes **code** for your MADA project. Same
rule applies — you'll verify its code against numbers you already trust. Bring your
project group and your project data."""),

    # ---------------------------------------------------------------- S7 (stretch)
    md("""## 7 · Going further (optional) — search by *meaning*, not keywords

*For fast finishers — or at home. Everything below is free and runs inside this
notebook; nothing later depends on it.*

A support-desk moment: a customer writes *"my parcel arrived shattered."* Has this
happened before? Ctrl+F through last month's reviews for "shattered" finds **nothing**
— people wrote "in pieces", "cracked", "fell apart". Keyword search reads letters;
you need something that reads *meaning*.

That something is an **embedding**: a model turns each text into a list of numbers so
that texts with similar meaning get nearby numbers. A **vector database** stores those
vectors and finds the nearest ones to your question. This is the retrieval half of
every "chat with your company documents" product (the industry calls it **RAG**) — and
it is the missing link between today's two lessons: in Section 2 the LLM hallucinated
*because it had no data*; retrieval is how real systems put the right data in front
of it.

We'll use **Qdrant** — a real vector database with a free local mode: it runs entirely
inside this notebook. No server, no account, no API key."""),
    code('%pip install -q "qdrant-client[fastembed]"\n'
         '# ^ one-time per Colab session (~1 minute). Free, no account, no API key.'),
    code(S["stretch_corpus"]),
    code(S["stretch_index"]),
    code(S["stretch_search"]),
    md("""Zero keyword hits — yet the meaning search found the crushed box, the smashed mirror
and the cracked glass, although they share **no important words** with the query: the
embedding placed "arrived shattered" and "arrived in pieces" close together because
they *mean* nearly the same thing.

Look closer, though: two of the five hits are *other* parcel problems — a wrong order
even lands near the top, and a lost parcel is in there too. The database measures
**similarity, not truth**: it read "trouble with an arriving parcel" in all of them.
The course refrain applies even here: a high score is a lead, not a verdict."""),
    todo('the board asks: "are customers unhappy with our delivery times?" — query the review pile, read the top hits and judge: real pattern or one-off?',
         'search("...") — describe the complaint in plain English, e.g. delivery took too long'),
    solution(S["stretch_solution"]),
    answer("Where would meaning-search earn its keep at Adriatica — support-ticket triage? finding similar past complaints? FAQ lookup? Name one place, and one catch (hint: *similar* is not *true* — the refrain applies here too)."),
    md("""*If your MADA project data includes free text (reviews, emails, tickets), this
pattern is a legitimate stretch goal for the project — bring it up in A05.*"""),
]

chunks = [
    ("setup", 'orders = load_file("orders.csv").drop_duplicates()\nimport pandas as pd'),
    ("paste_csv", S["paste_csv"] + '\nassert list(complaints.columns) == ["product", "issue", "severity"]'),
    ("verify", S["verify"] + '\nassert str(best_month) == "2024-12"\nassert abs(avg_order_value - 176.77) < 0.5\nassert top_product == "Compact Mirror 042"'),
    ("colab_ai_guarded", 'complaint_emails = "stub"\n' + S["colab_ai"]),
    # Stretch section: runs fully only where qdrant-client is installed (e.g. the
    # Colab pilot); otherwise every cell prints its friendly skip and the chunk
    # stays green - same guard pattern students see in the notebook.
    ("qdrant_stretch_guarded",
     S["stretch_corpus"] + "\n" + S["stretch_index"] + "\n" + S["stretch_search"]
     + "\n" + S["stretch_assert"]),
]

if __name__ == "__main__":
    save(cells, "lab-a04-llms-for-decisions", "lab-a04-llms-for-decisions.ipynb")
    write_smoke("a04", "lab-a04-llms-for-decisions/data", chunks)
