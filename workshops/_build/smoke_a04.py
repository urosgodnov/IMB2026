# -*- coding: utf-8 -*-
import os
import matplotlib
matplotlib.use("Agg")
os.chdir(r"C:\Onedrive\Personal\OneDrive\Famnit\IMB2026\workshops\lab-a04-llms-for-decisions\data")
import os
import pandas as pd

DATA_BASE_URL = ""  # INSTRUCTOR: paste the published data folder URL here before class (see instructor-notes.md).

def load_file(name, reader=pd.read_csv, **kw):
    """Load a course data file: published URL -> local file -> Colab upload."""
    if DATA_BASE_URL:
        return reader(DATA_BASE_URL.rstrip("/") + "/" + name, **kw)
    if os.path.exists(name):
        return reader(name, **kw)
    try:
        from google.colab import files
        print(f"'{name}' not found - please upload it now (from this workshop's data/ folder).")
        files.upload()
        return reader(name, **kw)
    except ImportError as exc:
        raise FileNotFoundError(name) from exc

print("-- setup")
orders = load_file("orders.csv").drop_duplicates()
import pandas as pd
print("-- paste_csv")
import io

pasted_csv = """product,issue,severity
EXAMPLE Travel Speaker,damaged on arrival,high
EXAMPLE Desk Pad,wrong item received,medium"""
# ^ replace the example lines with the CSV Gemini produced for you (keep the header row)

complaints = pd.read_csv(io.StringIO(pasted_csv))
complaints
assert list(complaints.columns) == ["product", "issue", "severity"]
print("-- verify")
orders["revenue"] = orders["quantity"] * orders["unit_price"]
orders["month"] = pd.to_datetime(orders["order_date"]).dt.to_period("M")

best_month = orders.groupby("month")["revenue"].sum().idxmax()
top_product = orders.groupby("product_name")["revenue"].sum().idxmax()
avg_order_value = orders["revenue"].mean()

print("best month:      ", best_month)
print("top product:     ", top_product)
print("avg order value: ", round(avg_order_value, 2), "EUR")
assert str(best_month) == "2024-12"
assert abs(avg_order_value - 176.77) < 0.5
assert top_product == "Compact Mirror 042"
print("-- colab_ai_guarded")
complaint_emails = "stub"
# Programmatic prompting with Colab's built-in (free) Gemini access - no API key.
# NOTE: free tier has monthly limits; we use only a few calls today.
try:
    from google.colab import ai
    prompt = """Extract a CSV table with columns product,issue,severity from these
customer emails. Output ONLY the CSV, no explanation.

""" + complaint_emails
    result = ai.generate_text(prompt)
    print(result)
except ImportError:
    print("(google.colab.ai is only available inside Google Colab - skipping here)")
print("-- qdrant_stretch_guarded")
# Last month's reviews (synthetic, like everything at Adriatica). Pre-written - just run it.
last_month_reviews = [
    'The Premium Puzzle 044 arrived in pieces, the box was completely crushed.',
    'Glass front of the Classic Hair Dryer 035 was cracked when I unpacked it.',
    'Box looked fine but the handle of the kettle inside had snapped off.',
    'My Max Building Set 043 fell apart after a single evening of play.',
    'The seams came apart the first time I used it.',
    'One corner of the parcel was smashed and so was the mirror inside.',
    'Three weeks for delivery is simply not acceptable.',
    'Courier kept postponing, the parcel showed up ten days late.',
    'Ordered it for a birthday and it arrived long after the party.',
    'Shipping took forever even though the site promised 48 hours.',
    'Still waiting for the second half of my order.',
    'Tracking said delivered while the parcel was nowhere to be found.',
    'Arrived a day early and neatly packed.',
    'Fast shipping, no complaints there.',
    'Smooth delivery and a lovely unboxing experience.',
    'Support never answered either of my two emails.',
    'The refund took two months and three phone calls.',
    'Chat agent closed my ticket without solving anything.',
    'I was on hold for forty minutes and then got cut off.',
    'They promised a callback that never came.',
    'Customer service replaced my faulty unit within days, brilliant.',
    'The support agent was patient and genuinely helpful.',
    'Return process was completely painless.',
    'Battery of the Travel Speaker 012 dies after barely an hour.',
    'The charge does not even last my short commute.',
    'Buttons feel flimsy, like they will give up within a month.',
    'Cheap materials for a supposedly premium product.',
    'It stopped charging in the second week.',
    'The hinge wobbles - build quality is disappointing.',
    'Great value for money, I would buy it again.',
    'Overpriced for what it actually does.',
    'Half the price of the competitors and works just as well.',
    'Caught it on discount and I am very happy.',
    'Not worth the premium label at all.',
    'The Basic Kettle 020 is quiet and quick, love it.',
    'My nephew adores the Basic Pen Set 053.',
    'Exactly as described, works perfectly.',
    'Five stars, the best purchase I made this year.',
    'The design is gorgeous and it simply works.',
    'Does its job day after day without any fuss.',
    'The manual was confusing but the product itself is fine.',
    'App pairing failed twice before it finally worked.',
    'Wrong colour delivered, decided to keep it anyway.',
    'Sizing runs small, order one size up.',
    "I received someone else's order and had to send it back.",
]
print(len(last_month_reviews), "reviews")
# Build the vector index (pre-written). The first run downloads a small (~67 MB)
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
    print("(qdrant-client/fastembed not installed - run the install cell above first. This section is optional.)")
# Pre-written demo - just run it.
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
    print("(run the install + index cells above first. This section is optional.)")
assert keyword_hits == [], keyword_hits  # the demo premise: Ctrl+F finds nothing
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
    pass
print("SMOKE OK a04")