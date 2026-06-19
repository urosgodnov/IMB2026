"""Verify the workshop's copy of orders.csv and the seasonal signal the
workshop relies on. Run: python claude-code-workshop/_build/check_data.py"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "orders.csv"
EXPECTED_COLS = ["order_id", "order_date", "customer_id", "product_id",
                 "product_name", "category", "quantity", "unit_price"]

def monthly_revenue(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    df["revenue"] = df["quantity"] * df["unit_price"]
    df["month"] = df["order_date"].str.slice(0, 7)
    return df.groupby("month")["revenue"].sum().sort_index()

def main() -> None:
    df = pd.read_csv(DATA)
    assert list(df.columns) == EXPECTED_COLS, f"columns drifted: {list(df.columns)}"
    assert len(df) == 4644, f"expected 4644 rows, got {len(df)}"
    mr = monthly_revenue(DATA)
    best = mr.idxmax()
    assert best == "2024-12", f"expected peak 2024-12, got {best}"
    assert mr["2024-12"] > mr["2024-07"], "December should beat July (seasonal signal)"
    print(f"DATA OK  rows={len(df)}  peak={best}  peak_rev={mr[best]:.2f}")

if __name__ == "__main__":
    main()
