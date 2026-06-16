# -*- coding: utf-8 -*-
"""Build lab-a01-pandas-business-data notebook + smoke test."""
from nb import LOADER, answer, code, md, save, solution, todo, write_smoke

S = {}  # solution code, reused for the smoke test

S["excel"] = '''products = load_file("products.xlsx", reader=pd.read_excel)
products.head()'''

S["revenue"] = '''orders["revenue"] = orders["quantity"] * orders["unit_price"]
orders.head(3)'''

S["filters"] = '''big_orders = orders[orders["revenue"] > 500]
electronics = orders[orders["category"] == "Electronics"]
print(len(big_orders), "orders above 500 EUR")
print(len(electronics), "Electronics orders")'''

S["top10"] = '''orders.sort_values("revenue", ascending=False).head(10)'''

S["missing"] = '''customers = load_file("customers.csv")
customers.isna().sum()'''

S["dedup_cust"] = '''print("before:", len(customers))
customers = customers.drop_duplicates()
print("after: ", len(customers))'''

S["dates"] = '''customers["signup_date"] = pd.to_datetime(customers["signup_date"])
customers.dtypes'''

S["countries"] = '''mapping = {"SI": "Slovenia", "slovenia": "Slovenia", "Italia": "Italy", "HR": "Croatia"}
customers["country"] = customers["country"].replace(mapping)
customers["country"] = customers["country"].fillna("Unknown")
customers["country"].value_counts()'''

S["dedup_orders"] = '''print("duplicate order rows:", orders.duplicated().sum())
orders = orders.drop_duplicates()
print("orders after cleaning:", len(orders))'''

S["monthly"] = '''orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["month"] = orders["order_date"].dt.to_period("M")
monthly_revenue = orders.groupby("month")["revenue"].sum()
monthly_revenue'''

S["by_country"] = '''orders_c = orders.merge(customers[["customer_id", "country"]], on="customer_id")
revenue_by_country = orders_c.groupby("country")["revenue"].sum().sort_values(ascending=False)
revenue_by_country'''

S["pivot"] = '''orders_s = orders.merge(customers[["customer_id", "segment"]], on="customer_id")
orders_s.pivot_table(values="revenue", index="segment", aggfunc="mean").round(2)'''

S["chart_line"] = '''import matplotlib.pyplot as plt
monthly_revenue.plot(kind="line", marker="o", title="Adriatica monthly revenue (FY 2024/25)")
plt.ylabel("revenue (EUR)")
plt.show()'''

S["chart_bar"] = '''top10_products = orders.groupby("product_name")["revenue"].sum().nlargest(10)
top10_products.plot(kind="barh", title="Top 10 products by revenue")
plt.xlabel("revenue (EUR)")
plt.show()'''

S["chart_hist"] = '''orders["revenue"].plot(kind="hist", bins=40, title="Order value distribution")
plt.xlabel("order value (EUR)")
plt.show()'''

S["stretch"] = '''def country_summary(name):
    sub = orders_c[orders_c["country"] == name]
    return {"orders": len(sub), "revenue": round(sub["revenue"].sum(), 2),
            "avg_order": round(sub["revenue"].mean(), 2)}

country_summary("Slovenia")'''

cells = [
    # ---------------------------------------------------------- Section 0
    md("""# A01 · Pandas — Working with Business Data

**IMB 2026 · MADA · Workshop A01 (Wed 17 Jun 2026, 9:00–13:00)**

Welcome to your first day as a data analyst at **Adriatica**, an e-commerce retailer
selling across the Adriatic region. The CEO wants to know how the business is *really*
doing — but all you have is a messy export from the order system.

By the end of this workshop you will be able to:

- load CSV and Excel files into pandas and inspect them,
- filter, sort, and create calculated columns,
- diagnose and fix dirty data (missing values, duplicates, wrong types, inconsistent labels),
- answer real management questions with `groupby`, pivot tables, and `merge`,
- draw and critically read basic charts,
- read a Python error message without panic."""),
    md("""## 0 · Working in Colab — 10 minutes

1. **File → Save a copy in Drive** — do this *now*, so your work is yours.
2. A notebook is a sequence of **cells**: text cells (like this one) and code cells. Run a code cell with the ▶ button or **Ctrl+Enter**.
3. Exercises are marked **✏️ TODO** — you type the code. Below each exercise there is a collapsed **💡 Show solution**. Etiquette: *try first*, then ask **Gemini Learn Mode** for a hint (spark icon → Learn Mode), and only then open the solution.
4. If a cell errors: read the **last line** of the message first, then find the line it points at. Errors are normal; they are how analysts talk to computers."""),
    code('print("Hello, Adriatica!")  # run me: Ctrl+Enter'),

    # ---------------------------------------------------------- Section 1
    md("""## 1 · First contact with the data

A pandas **DataFrame** is a spreadsheet with superpowers: rows, named columns, and
every operation repeatable in code. The cell below defines a small loader and reads
`orders.csv` — one row per order."""),
    code(LOADER + '\norders = load_file("orders.csv")\nprint("rows, columns:", orders.shape)\norders.head()'),
    md("""Three inspection tools you will use on *every* dataset you ever meet:

- `head()` — what does it look like?
- `info()` — column types and missing values
- `describe()` — quick statistics for the numeric columns

Run the next cell and answer for yourself: *how many rows? which columns are text,
which are numbers? anything suspicious?*"""),
    code('orders.info()\norders.describe()'),
    md("""**Python aside #1.** `orders` is a *variable* — a name we chose. `orders.head()`
*calls a method* on it. `load_file("orders.csv")` passed an *argument* to a function.
That is 80% of the Python you need today."""),
    todo('load the product catalogue from the Excel file "products.xlsx" into a variable called products, and show its first rows',
         'load_file can use a different reader: load_file("products.xlsx", reader=pd.read_excel)'),
    solution(S["excel"]),

    # ---------------------------------------------------------- Section 2
    md("""## 2 · Questions you can already answer

Each order row has `quantity` and `unit_price` — but the CEO thinks in **revenue**.
A calculated column is one line of code."""),
    todo('create a new column orders["revenue"] = quantity × unit_price, then look at head() to check it',
         'multiply two columns: orders["quantity"] * orders["unit_price"]'),
    solution(S["revenue"]),
    md("""**Python aside #2.** `orders["revenue"] > 500` produces a column of `True`/`False`
values — a *boolean mask*. Putting a mask inside `orders[...]` keeps only the `True` rows.
That is filtering, and you will use it daily."""),
    todo('filter: (a) orders with revenue above 500 EUR, (b) orders in the "Electronics" category — print how many of each',
         'mask = orders["category"] == "Electronics"; then orders[mask]'),
    solution(S["filters"]),
    todo('show the 10 largest orders by revenue', 'sort_values("revenue", ascending=False) and head(10)'),
    solution(S["top10"]),
    md("""**🎯 Stretch (if you are ahead):** merge `products` (it has `unit_cost`) onto `orders`
and compute a `margin` column = revenue − quantity × unit_cost. Which category has the
best total margin?"""),

    # ---------------------------------------------------------- Section 3
    md("""## 3 · Reality check: dirty data

Now the customer file — and your first taste of real-world data. **Dirty data is the
norm, not the exception.** Every fix below is a *business decision*, not just code."""),
    todo('load "customers.csv" into a variable customers and count the missing values in every column',
         'customers.isna().sum()'),
    solution(S["missing"]),
    answer("~40 customers have no e-mail and ~25 have no country. For each: drop the rows, fill the gaps, or keep as-is? What would each choice do to a mailing campaign vs. a revenue-by-country report?"),
    todo('some customers appear twice — count and remove duplicate rows, printing the row count before and after',
         'customers.duplicated().sum(), then drop_duplicates()'),
    solution(S["dedup_cust"]),
    todo('check customers.dtypes — signup_date is stored as text; convert it to a real date',
         'pd.to_datetime(customers["signup_date"])'),
    solution(S["dates"]),
    md("""Look at `customers["country"].value_counts()` — Slovenia appears as `Slovenia`,
`SI` **and** `slovenia`; Italy also as `Italia`; Croatia as `HR`. To a computer those are
five different countries. A *mapping dictionary* + `replace` fixes labels; `fillna`
handles the missing ones."""),
    todo('normalise the country labels using the mapping {"SI": "Slovenia", "slovenia": "Slovenia", "Italia": "Italy", "HR": "Croatia"}, fill missing countries with "Unknown", and show value_counts()',
         'customers["country"].replace(mapping) then .fillna("Unknown")'),
    solution(S["countries"]),
    md("""One more skeleton in the closet: the **orders** file contains some duplicated
rows too (the export ran twice for a few orders). If we don't remove them, every
revenue number we report will be silently wrong."""),
    todo('count duplicate rows in orders, remove them, and print the new row count',
         'orders.duplicated().sum() / orders.drop_duplicates()'),
    solution(S["dedup_orders"]),

    # ---------------------------------------------------------- Section 4
    md("""## 4 · Management questions at scale

The pattern for the rest of your career: **management question → groupby**.

> *"How is revenue developing month by month?"* → group orders by month, sum revenue."""),
    todo('compute monthly revenue: convert order_date to datetime, derive a month column with .dt.to_period("M"), then groupby month and sum revenue',
         'orders.groupby("month")["revenue"].sum()'),
    solution(S["monthly"]),
    md("""**📌 Remember this number.** Note your **December 2024** revenue and the **total**
for the year — you will meet them again in workshops A04 and A05 (no spoilers)."""),
    answer("In one sentence for the CEO: what happened to revenue over the year?"),
    md("""> *"Which market makes us the most money?"* — `orders` has no country column;
`customers` does. Two tables, one question → **merge** (pandas' version of a join)."""),
    todo('merge orders with customers[["customer_id", "country"]] on customer_id, then compute revenue by country, sorted descending',
         'orders.merge(customers[["customer_id", "country"]], on="customer_id")'),
    solution(S["by_country"]),
    answer("Which two markets would you prioritise next year, and why?"),
    todo('average order value by customer segment (consumer vs business) using a pivot table',
         'pivot_table(values="revenue", index="segment", aggfunc="mean")'),
    solution(S["pivot"]),

    # ---------------------------------------------------------- Section 5
    md("""## 5 · Show, don't tell

Numbers convince analysts; **charts convince boards**. pandas plots directly from
a DataFrame or Series."""),
    todo('draw the monthly revenue as a line chart (add a title and a y-axis label)',
         'monthly_revenue.plot(kind="line", marker="o", title=...)'),
    solution(S["chart_line"]),
    todo('draw the top-10 products by total revenue as a horizontal bar chart',
         'groupby product_name, sum revenue, .nlargest(10), .plot(kind="barh")'),
    solution(S["chart_bar"]),
    todo('draw a histogram of order values (try bins=40)', 'orders["revenue"].plot(kind="hist", bins=40)'),
    solution(S["chart_hist"]),
    answer("Pick one of your three charts: what does it NOT tell you? (Think: averages hide distributions; a rising line hides *why*; axes can mislead.)"),

    # ---------------------------------------------------------- Section 6
    md("""## 6 · Wrap-up

You walked in with a messy export. You now have: clean tables, a revenue trend,
your top markets and products, and three board-ready charts — all *repeatable*:
rerun the notebook on next month's export and everything updates.

**This afternoon (A02):** you can now *describe what happened*. Next we **predict
what happens next** — which first-time buyers will come back? Same data, new superpower.

**🎯 Self-paced stretch:**"""),
    todo('write a function country_summary(name) that returns the number of orders, total revenue and average order value for one country',
         'def country_summary(name): sub = orders_c[orders_c["country"] == name] ...'),
    solution(S["stretch"]),
]

chunks = [
    ("excel", S["excel"]),
    ("revenue", S["revenue"]),
    ("filters", S["filters"]),
    ("top10", S["top10"]),
    ("missing", S["missing"]),
    ("dedup_cust", S["dedup_cust"] + '\nassert len(customers) == 1200, len(customers)'),
    ("dates", S["dates"]),
    ("countries", S["countries"] + '\nassert set(customers["country"].unique()) <= {"Slovenia", "Italy", "Croatia", "Austria", "Germany", "Hungary", "Unknown"}'),
    ("dedup_orders", S["dedup_orders"] + '\nassert len(orders) == 4614, len(orders)'),
    ("monthly", S["monthly"] + '\nassert str(monthly_revenue.idxmax()) == "2024-12", monthly_revenue.idxmax()\nassert abs(monthly_revenue.sum() - 815629.71) < 1.0, monthly_revenue.sum()'),
    ("by_country", S["by_country"] + '\nassert revenue_by_country.index[0] == "Slovenia"'),
    ("pivot", S["pivot"]),
    ("chart_line", S["chart_line"]),
    ("chart_bar", S["chart_bar"]),
    ("chart_hist", S["chart_hist"]),
    ("stretch", S["stretch"]),
]

if __name__ == "__main__":
    save(cells, "lab-a01-pandas-business-data", "lab-a01-pandas-business-data.ipynb")
    smoke_pre = 'orders = load_file("orders.csv")\n'
    write_smoke("a01", "lab-a01-pandas-business-data/data", [("setup", smoke_pre)] + chunks)
