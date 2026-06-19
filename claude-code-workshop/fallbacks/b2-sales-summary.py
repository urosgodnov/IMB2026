"""Known-good monthly sales summary (fallback if live generation fails).
Run: python claude-code-workshop/fallbacks/b2-sales-summary.py"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "orders.csv"

def main() -> None:
    df = pd.read_csv(DATA)
    df["revenue"] = df["quantity"] * df["unit_price"]
    df["month"] = df["order_date"].str.slice(0, 7)
    monthly = df.groupby("month")["revenue"].sum().sort_index()
    best = monthly.idxmax()
    print("Monthly revenue:")
    for month, rev in monthly.items():
        print(f"  {month}  {rev:>12,.2f}")
    print(f"\nBest month: {best}  ({monthly[best]:,.2f})")
    print(f"Total revenue (raw, incl. duplicate orders): {monthly.sum():,.2f}")

if __name__ == "__main__":
    main()
