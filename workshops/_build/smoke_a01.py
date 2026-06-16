# -*- coding: utf-8 -*-
import os
import matplotlib
matplotlib.use("Agg")
os.chdir(r"C:\Onedrive\Personal\OneDrive\Famnit\IMB2026\workshops\lab-a01-pandas-business-data\data")
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

print("-- excel")
products = load_file("products.xlsx", reader=pd.read_excel)
products.head()
print("-- revenue")
orders["revenue"] = orders["quantity"] * orders["unit_price"]
orders.head(3)
print("-- filters")
big_orders = orders[orders["revenue"] > 500]
electronics = orders[orders["category"] == "Electronics"]
print(len(big_orders), "orders above 500 EUR")
print(len(electronics), "Electronics orders")
print("-- top10")
orders.sort_values("revenue", ascending=False).head(10)
print("-- missing")
customers = load_file("customers.csv")
customers.isna().sum()
print("-- dedup_cust")
print("before:", len(customers))
customers = customers.drop_duplicates()
print("after: ", len(customers))
assert len(customers) == 1200, len(customers)
print("-- dates")
customers["signup_date"] = pd.to_datetime(customers["signup_date"])
customers.dtypes
print("-- countries")
mapping = {"SI": "Slovenia", "slovenia": "Slovenia", "Italia": "Italy", "HR": "Croatia"}
customers["country"] = customers["country"].replace(mapping)
customers["country"] = customers["country"].fillna("Unknown")
customers["country"].value_counts()
assert set(customers["country"].unique()) <= {"Slovenia", "Italy", "Croatia", "Austria", "Germany", "Hungary", "Unknown"}
print("-- dedup_orders")
print("duplicate order rows:", orders.duplicated().sum())
orders = orders.drop_duplicates()
print("orders after cleaning:", len(orders))
assert len(orders) == 4614, len(orders)
print("-- monthly")
orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["month"] = orders["order_date"].dt.to_period("M")
monthly_revenue = orders.groupby("month")["revenue"].sum()
monthly_revenue
assert str(monthly_revenue.idxmax()) == "2024-12", monthly_revenue.idxmax()
assert abs(monthly_revenue.sum() - 815629.71) < 1.0, monthly_revenue.sum()
print("-- by_country")
orders_c = orders.merge(customers[["customer_id", "country"]], on="customer_id")
revenue_by_country = orders_c.groupby("country")["revenue"].sum().sort_values(ascending=False)
revenue_by_country
assert revenue_by_country.index[0] == "Slovenia"
print("-- pivot")
orders_s = orders.merge(customers[["customer_id", "segment"]], on="customer_id")
orders_s.pivot_table(values="revenue", index="segment", aggfunc="mean").round(2)
print("-- chart_line")
import matplotlib.pyplot as plt
monthly_revenue.plot(kind="line", marker="o", title="Adriatica monthly revenue (FY 2024/25)")
plt.ylabel("revenue (EUR)")
plt.show()
print("-- chart_bar")
top10_products = orders.groupby("product_name")["revenue"].sum().nlargest(10)
top10_products.plot(kind="barh", title="Top 10 products by revenue")
plt.xlabel("revenue (EUR)")
plt.show()
print("-- chart_hist")
orders["revenue"].plot(kind="hist", bins=40, title="Order value distribution")
plt.xlabel("order value (EUR)")
plt.show()
print("-- stretch")
def country_summary(name):
    sub = orders_c[orders_c["country"] == name]
    return {"orders": len(sub), "revenue": round(sub["revenue"].sum(), 2),
            "avg_order": round(sub["revenue"].mean(), 2)}

country_summary("Slovenia")
print("SMOKE OK a01")