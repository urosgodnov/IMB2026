# -*- coding: utf-8 -*-
import os
import matplotlib
matplotlib.use("Agg")
os.chdir(r"C:\Onedrive\Personal\OneDrive\Famnit\IMB2026\workshops\lab-a05-vibe-coding-project\data")
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
orders = load_file("orders.csv")
import pandas as pd
print("-- verify_warmup")
# The two anchor numbers from A01 (after dropping duplicate rows):
#   total FY revenue ~= 815,629.71 EUR
#   best month       =  December 2024 (~96,505.68 EUR)
check = orders.drop_duplicates().copy()
check["revenue"] = check["quantity"] * check["unit_price"]
print("total revenue:", round(check["revenue"].sum(), 2))
monthly = check.groupby(pd.to_datetime(check["order_date"]).dt.to_period("M"))["revenue"].sum()
print("best month:   ", monthly.idxmax(), "->", round(monthly.max(), 2))
assert abs(check["revenue"].sum() - 815629.71) < 1.0
assert str(monthly.idxmax()) == "2024-12"
print("-- flawed_runs_but_wrong")
# --- "AI-generated" monthly revenue summary --- (it RUNS without errors. Review it.)
import matplotlib.pyplot as plt

summary = orders.copy()
summary["month"] = pd.to_datetime(summary["order_date"]).dt.strftime("%B")
monthly_revenue = summary.groupby("month")["quantity"].sum()
monthly_revenue.plot(kind="bar", title="Adriatica monthly revenue (FY2024/25)")
plt.ylabel("revenue (EUR)")
plt.show()
print("total 'revenue':", monthly_revenue.sum())
assert monthly_revenue.sum() < 20000  # quantity total, nowhere near revenue
assert list(monthly_revenue.index) == sorted(monthly_revenue.index)  # alphabetical = scrambled
print("-- flaw_fix")
# Flaw 1 - WRONG METRIC: it sums `quantity` (units sold) but labels it "revenue".
#          The total printed is ~16,000 - nowhere near the ~815,630 EUR you verified.
# Flaw 2 - SCRAMBLED ORDER: strftime("%B") makes month NAMES, so the x-axis sorts
#          alphabetically (April, August, December, ...) - the trend is unreadable.
# (Bonus)- it never dropped the 30 duplicate rows.
# The fix:
fixed = orders.drop_duplicates().copy()
fixed["revenue"] = fixed["quantity"] * fixed["unit_price"]
fixed["month"] = pd.to_datetime(fixed["order_date"]).dt.to_period("M")
monthly_fixed = fixed.groupby("month")["revenue"].sum()
print("total revenue (fixed):", round(monthly_fixed.sum(), 2))
assert abs(monthly_fixed.sum() - 815629.71) < 1.0
print("-- crash_guarded")
RUN_BROKEN = False  # <- flip to True, run, and experience the crash (then flip back)

if RUN_BROKEN:
    # --- another "AI-generated" snippet, fresh from a chatbot ---
    df = load_file("orders.csv")
    df["profit"] = df["revenue"] - df["cost"]      # invented columns!
    print(df.groupby("region")["profit"].sum())   # invented column again
else:
    print("(set RUN_BROKEN = True to run the broken snippet)")
print("-- crash_real")
try:
    df = load_file("orders.csv")
    df["profit"] = df["revenue"] - df["cost"]
    raise AssertionError("should have raised KeyError")
except KeyError as e:
    print("KeyError as expected:", e)
print("-- feedback")
# A good feedback prompt contains: the ERROR, the CONTEXT, the EXPECTATION.
feedback_prompt = """Your code raised:
    KeyError: 'revenue'
The DataFrame comes from orders.csv with columns:
    order_id, order_date, customer_id, product_id, product_name, category, quantity, unit_price
There is no revenue, cost, or region column. Revenue must be computed as
quantity * unit_price; there is no cost data, so drop the profit idea and
summarise revenue by product category instead."""
print(feedback_prompt)
print("SMOKE OK a05")