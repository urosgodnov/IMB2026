# -*- coding: utf-8 -*-
"""Generate the Adriatica course datasets for IMB 2026 MADA.

Deterministic (seed 42). Writes per-workshop data folders and a ground-truth
JSON used to fill instructor notes. Run from anywhere:
    python generate_data.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
ROOT = Path(__file__).resolve().parents[1]  # workshops/

# ---------------------------------------------------------------- products
CATS = {
    "Electronics": 12, "Home & Kitchen": 12, "Sports & Outdoor": 10,
    "Beauty": 8, "Toys": 8, "Office": 10,
}
ADJ = ["Pro", "Classic", "Mini", "Max", "Eco", "Smart", "Travel", "Family",
       "Premium", "Basic", "Compact", "Deluxe"]
NOUN = {
    "Electronics": ["Headphones", "Speaker", "Power Bank", "Webcam", "Mouse", "Keyboard"],
    "Home & Kitchen": ["Blender", "Kettle", "Pan Set", "Coffee Maker", "Lamp", "Organizer"],
    "Sports & Outdoor": ["Yoga Mat", "Backpack", "Water Bottle", "Running Belt", "Tent"],
    "Beauty": ["Hair Dryer", "Skincare Set", "Trimmer", "Mirror"],
    "Toys": ["Building Set", "Puzzle", "Plush Bear", "Race Track"],
    "Office": ["Notebook Set", "Desk Pad", "Pen Set", "Monitor Stand", "Chair Cushion"],
}

def make_products():
    rows, pid = [], 1
    for cat, n in CATS.items():
        for i in range(n):
            name = f"{RNG.choice(ADJ)} {NOUN[cat][i % len(NOUN[cat])]}"
            cost = float(np.round(RNG.uniform(4, 90), 2))
            price = float(np.round(cost * RNG.uniform(1.5, 2.2), 2))
            rows.append([f"P-{pid:03d}", name, cat, cost, price])
            pid += 1
    df = pd.DataFrame(rows, columns=["product_id", "product_name", "category",
                                     "unit_cost", "list_price"])
    df["product_name"] = df["product_name"] + " " + df["product_id"].str[-3:]
    return df

# ---------------------------------------------------------------- customers
FIRST = ["Ana", "Luka", "Marta", "Jan", "Eva", "Marko", "Nina", "Tomaž", "Sara",
         "Matej", "Petra", "Giulia", "Marco", "Francesca", "Ivana", "Karlo",
         "Hannah", "Felix", "Anna", "Lukas", "Réka", "Bence", "Maja", "Žiga"]
LAST = ["Novak", "Horvat", "Kovačič", "Zupan", "Potočnik", "Rossi", "Russo",
        "Bianchi", "Ferrari", "Kovač", "Babić", "Jurić", "Gruber", "Huber",
        "Wagner", "Müller", "Schmidt", "Nagy", "Tóth", "Szabó", "Krajnc",
        "Vidmar", "Golob", "Turk", "Hribar", "Kos", "Mlakar", "Oblak", "Žagar", "Bizjak"]
COUNTRIES = ["Slovenia", "Italy", "Croatia", "Austria", "Germany", "Hungary"]
C_W = [0.30, 0.20, 0.15, 0.12, 0.15, 0.08]
CITY = {
    "Slovenia": ["Ljubljana", "Maribor", "Koper", "Celje"],
    "Italy": ["Trieste", "Milan", "Padua", "Bologna"],
    "Croatia": ["Zagreb", "Rijeka", "Split"],
    "Austria": ["Vienna", "Graz", "Klagenfurt"],
    "Germany": ["Munich", "Berlin", "Hamburg"],
    "Hungary": ["Budapest", "Győr", "Pécs"],
}
CHANNELS = ["organic", "ads", "referral", "social"]
CH_W = [0.35, 0.30, 0.20, 0.15]

def make_customers(n=1200):
    ids = [f"C-{i:04d}" for i in range(1, n + 1)]
    country = RNG.choice(COUNTRIES, n, p=C_W)
    rows = []
    for i, cid in enumerate(ids):
        fn, ln = RNG.choice(FIRST), RNG.choice(LAST)
        c = country[i]
        signup = pd.Timestamp("2023-06-01") + pd.Timedelta(days=int(RNG.beta(1.0, 1.4) * 660))
        rows.append([cid, f"{fn} {ln}", f"{fn.lower()}.{ln.lower()}{i}@example.com",
                     c, RNG.choice(CITY[c]),
                     "business" if RNG.random() < 0.28 else "consumer",
                     signup.date().isoformat(),
                     "yes" if RNG.random() < 0.45 else "no",
                     RNG.choice(CHANNELS, p=CH_W)])
    return pd.DataFrame(rows, columns=["customer_id", "full_name", "email", "country",
                                       "city", "segment", "signup_date", "newsletter",
                                       "acquisition_channel"])

# ---------------------------------------------------------------- orders
MONTHS = pd.period_range("2024-07", "2025-06", freq="M")
SEASON = np.array([0.95, 0.92, 1.00, 1.08, 1.45, 1.65, 0.85, 0.88, 0.98, 1.04, 1.08, 1.12])
TREND = np.linspace(1.0, 1.12, 12)
M_W = SEASON * TREND
M_W = M_W / M_W.sum()

def make_orders(customers, products):
    rows, oid = [], 10001
    for _, c in customers.iterrows():
        lam = 5.2 if c["segment"] == "business" else 4.0
        n_orders = int(RNG.poisson(lam))
        if RNG.random() < 0.06:
            n_orders = 0  # some customers never order
        for _ in range(n_orders):
            m = MONTHS[RNG.choice(12, p=M_W)]
            start = max(pd.Timestamp(m.start_time), pd.Timestamp(c["signup_date"]))
            end = pd.Timestamp(m.end_time).normalize()
            if start > end:
                continue
            day = start + pd.Timedelta(days=int(RNG.integers(0, (end - start).days + 1)))
            p = products.iloc[int(RNG.integers(0, len(products)))]
            qty = int(RNG.integers(1, 4)) + (1 if c["segment"] == "business" and RNG.random() < 0.5 else 0)
            price = float(np.round(p["list_price"] * RNG.uniform(0.92, 1.0), 2))
            rows.append([f"O-{oid}", day.date().isoformat(), c["customer_id"],
                         p["product_id"], p["product_name"], p["category"], qty, price])
            oid += 1
    df = pd.DataFrame(rows, columns=["order_id", "order_date", "customer_id", "product_id",
                                     "product_name", "category", "quantity", "unit_price"])
    return df.sort_values("order_date").reset_index(drop=True)

# ----------------------------------------------------- A02 features + target
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def make_features(customers, orders):
    first = (orders.assign(revenue=orders["quantity"] * orders["unit_price"])
                   .sort_values("order_date").groupby("customer_id").first().reset_index())
    n_orders = orders.groupby("customer_id").size().rename("n_orders")
    df = first.merge(customers, on="customer_id").merge(n_orders, on="customer_id")
    n = len(df)
    fov = df["revenue"].to_numpy()
    days = (pd.to_datetime(df["order_date"]) - pd.to_datetime(df["signup_date"])).dt.days.clip(0).to_numpy()
    nl = (df["newsletter"] == "yes").astype(int).to_numpy()
    disc = (RNG.random(n) < 0.30).astype(int)
    tickets = np.minimum(RNG.poisson(0.7, n), 5)
    visits = RNG.poisson(6, n) + 1

    def std(x):
        return (x - x.mean()) / x.std()

    z = 1.9 * (-0.80 + 1.10 * nl + 0.85 * std(fov) + 0.55 * std(visits)
               - 0.70 * std(tickets) - 0.35 * std(days) + 0.20 * disc) \
        + RNG.normal(0, 0.6, n)
    y = (RNG.random(n) < sigmoid(z)).astype(int)
    feat = pd.DataFrame({
        "customer_id": df["customer_id"],
        "first_order_value": np.round(fov, 2),
        "first_order_items": df["quantity"],
        "days_signup_to_first_order": days,
        "newsletter": nl, "used_discount": disc, "support_tickets": tickets,
        "website_visits_first_month": visits, "repeat_customer": y,
    })
    return feat, df  # df keeps merged info for A03

# ----------------------------------------------------- A03 value + homework
CTRY_EFF = {"Slovenia": 0, "Italy": 25, "Croatia": -15, "Austria": 55, "Germany": 85, "Hungary": -35}
CHAN_EFF = {"organic": 10, "ads": -10, "referral": 40, "social": -30}

def make_value(feat, merged):
    n = len(feat)
    ctry = merged["country"].map(CTRY_EFF).to_numpy(float)
    seg = (merged["segment"] == "business").astype(int).to_numpy()
    chan = merged["acquisition_channel"].map(CHAN_EFF).to_numpy(float)
    spend = (120 + ctry + 160 * seg + chan
             + 1.6 * feat["first_order_value"].to_numpy()
             + 9.0 * feat["website_visits_first_month"].to_numpy()
             + 45 * feat["newsletter"].to_numpy()
             + RNG.normal(0, 125, n)).clip(20)
    aov = 70.0
    leak = np.maximum(1, np.round(spend / aov + RNG.normal(0, 0.7, n))).astype(int)
    return pd.DataFrame({
        "customer_id": feat["customer_id"],
        "country": merged["country"].to_numpy(),
        "segment": merged["segment"].to_numpy(),
        "acquisition_channel": merged["acquisition_channel"].to_numpy(),
        "first_order_value": feat["first_order_value"],
        "first_order_items": feat["first_order_items"],
        "newsletter": feat["newsletter"],
        "support_tickets": feat["support_tickets"],
        "website_visits_first_month": feat["website_visits_first_month"],
        "orders_in_period": leak,
        "six_month_spend": np.round(spend, 2),
    })

HW_CTRY = {"France": 70, "Czechia": -10, "Poland": -25}
HW_CHAN = {"organic": -5, "ads": 25, "referral": 15, "social": -40}

def make_homework(n=420):
    ctry = RNG.choice(list(HW_CTRY), n, p=[0.40, 0.35, 0.25])
    seg = RNG.choice(["consumer", "business"], n, p=[0.70, 0.30])
    chan = RNG.choice(CHANNELS, n, p=CH_W)
    fov = np.round(RNG.gamma(3.2, 32, n), 2)
    items = RNG.integers(1, 5, n)
    nl = (RNG.random(n) < 0.5).astype(int)
    tickets = np.minimum(RNG.poisson(0.8, n), 5)
    visits = RNG.poisson(5, n) + 1
    spend = (140 + pd.Series(ctry).map(HW_CTRY).to_numpy(float)
             + 150 * (seg == "business").astype(int)
             + pd.Series(chan).map(HW_CHAN).to_numpy(float)
             + 1.2 * fov + 11.0 * visits + 30 * nl
             + RNG.normal(0, 95, n)).clip(20)
    leak = np.maximum(1, np.round(spend / 75 + RNG.normal(0, 0.6, n))).astype(int)
    return pd.DataFrame({
        "customer_id": [f"X-{i:04d}" for i in range(1, n + 1)],
        "country": ctry, "segment": seg, "acquisition_channel": chan,
        "first_order_value": fov, "first_order_items": items, "newsletter": nl,
        "support_tickets": tickets, "website_visits_first_month": visits,
        "orders_in_period": leak, "six_month_spend": np.round(spend, 2),
    })

# ----------------------------------------------------- HW2: win-back pilot (classification)
def make_winback(n=804):
    rng = np.random.default_rng(2026)  # independent stream: existing datasets stay identical
    ctry = rng.choice(COUNTRIES, n, p=C_W)
    seg = rng.choice(["consumer", "business"], n, p=[0.74, 0.26])
    chan = rng.choice(CHANNELS, n, p=CH_W)
    months = rng.integers(3, 19, n)
    past_orders = rng.integers(1, 13, n)
    spend = np.round(rng.gamma(2.6, 95, n), 2)
    aov = np.round(spend / np.maximum(past_orders, 1) * rng.uniform(0.8, 1.2, n), 2)
    nl = (rng.random(n) < 0.42).astype(int)
    opened = (rng.random(n) < (0.25 + 0.40 * nl)).astype(int)
    tickets = np.minimum(rng.poisson(0.9, n), 5)

    def std(x):
        return (x - x.mean()) / x.std()

    z = 1.9 * (-1.10 + 1.05 * opened + 0.55 * nl + 0.45 * std(past_orders)
               - 0.55 * std(months) + 0.30 * std(spend) - 0.35 * std(tickets)) \
        + rng.normal(0, 0.6, n)
    y = (rng.random(n) < sigmoid(z)).astype(int)
    redeemed = ((y == 1) & (rng.random(n) < 0.9)).astype(int)  # leak: only known AFTER the campaign
    return pd.DataFrame({
        "customer_id": [f"W-{i:04d}" for i in range(1, n + 1)],
        "country": ctry, "segment": seg, "acquisition_channel": chan,
        "months_since_last_order": months, "n_past_orders": past_orders,
        "total_past_spend": spend, "avg_past_order_value": aov,
        "newsletter": nl, "opened_last_3_newsletters": opened,
        "past_support_tickets": tickets,
        "voucher_redeemed": redeemed, "responded": y,
    })

# ----------------------------------------------------- dirt for A01 CSVs
VARIANT = {"Slovenia": [("SI", 0.12), ("slovenia", 0.05)],
           "Italy": [("Italia", 0.10)], "Croatia": [("HR", 0.10)]}

def dirty_customers(cust):
    d = cust.copy()
    idx = RNG.choice(d.index, 40, replace=False)
    d.loc[idx, "email"] = np.nan
    idx2 = RNG.choice(d.index.difference(idx), 25, replace=False)
    d.loc[idx2, "country"] = np.nan
    for ctry, variants in VARIANT.items():
        pool = d.index[d["country"] == ctry]
        for label, frac in variants:
            take = RNG.choice(pool, int(len(pool) * frac), replace=False)
            d.loc[take, "country"] = label
            pool = pool.difference(take)
    dups = d.sample(15, random_state=7)
    return pd.concat([d, dups]).sample(frac=1, random_state=7).reset_index(drop=True)

def dirty_orders(orders):
    dups = orders.sample(30, random_state=7)
    return pd.concat([orders, dups]).sort_values("order_date").reset_index(drop=True)

# ----------------------------------------------------- A04 text artifacts
def fy_stats(orders):
    o = orders.drop_duplicates().assign(revenue=lambda d: d["quantity"] * d["unit_price"],
                                        month=lambda d: pd.to_datetime(d["order_date"]).dt.to_period("M"))
    monthly = o.groupby("month")["revenue"].sum()
    return {
        "total_revenue": round(float(o["revenue"].sum()), 2),
        "n_orders": int(o["order_id"].nunique()),
        "n_customers": int(o["customer_id"].nunique()),
        "aov": round(float(o.groupby("order_id")["revenue"].sum().mean()), 2),
        "best_month": str(monthly.idxmax()),
        "best_month_revenue": round(float(monthly.max()), 2),
        "top_category": str(o.groupby("category")["revenue"].sum().idxmax()),
        "top_product": str(o.groupby("product_name")["revenue"].sum().idxmax()),
        "h1": round(float(monthly[:6].sum()), 2),
        "h2": round(float(monthly[6:].sum()), 2),
        "monthly": {str(k): round(float(v), 2) for k, v in monthly.items()},
    }

def top_country(orders, customers):
    o = orders.drop_duplicates().assign(revenue=lambda d: d["quantity"] * d["unit_price"])
    m = o.merge(customers[["customer_id", "country"]], on="customer_id")
    by = m.groupby("country")["revenue"].sum().sort_values(ascending=False)
    return str(by.index[0]), round(float(by.iloc[0]), 2)

REPORT = """# Adriatica — Management Report FY2024/25 (July 2024 – June 2025)

## Overview

Adriatica closed financial year 2024/25 with total revenue of EUR {total_revenue:,.0f}
across {n_orders:,} orders from {n_customers:,} active customers. The average order
value for the year was EUR {aov:,.2f}. Revenue in the second half of the year reached
EUR {h2:,.0f}, compared with EUR {h1:,.0f} in the first half, confirming the positive
trajectory the board set out last summer.

## Sales highlights

The strongest month of the year was {best_month_name}, driven by the holiday
campaign, with revenue of EUR {best_month_revenue:,.0f}. Our largest market by
revenue remains {top_country}, and the strongest category was {top_category},
with the single best-selling product being the {top_product}.

## Operations and outlook

Fulfilment times improved over the year and customer-service load remained stable.
For FY2025/26 management proposes: (1) doubling down on the holiday-quarter
campaign that produced the {best_month_name} peak, (2) a loyalty programme to
lift repeat purchasing, and (3) expansion into two new EU markets, building on
the strength of our {top_country} business. The board is asked to approve the
expansion budget at the September meeting.
"""

EMAILS = """From: ana.k@example.com
Subject: Damaged on arrival
Ordered the {p1} last week. The box arrived crushed and the product does not turn on.
I expect a replacement or a full refund. Order O-12345.
---
From: m.weiss@example.org
Subject: Wrong item received
I ordered a {p2} but received some kind of kitchen scale instead. Please advise how to
return it. Mildly annoyed but mistakes happen.
---
From: luca.b@example.com
Subject: STILL WAITING
Three weeks!!! Three weeks and my {p3} has not arrived. Tracking has not moved since
day 2. This is unacceptable, cancel the order if it has not shipped.
---
From: petra.n@example.org
Subject: Battery question / possible defect
The {p4} I bought a month ago now only lasts about 20 minutes on a charge. Is this
normal? If not I would like to claim warranty.
---
From: t.horvat@example.com
Subject: Refund not received
I returned the {p5} 12 days ago (you confirmed receipt) but no refund has appeared on
my card. Please check.
---
From: julia.f@example.org
Subject: Small part missing
Love the {p6}, but the small connector piece listed in the manual was not in the box.
Could you send just that part? No rush.
---
From: d.kos@example.com
Subject: Charged twice
My card statement shows two charges for one {p7} order. One of them needs to be
reversed, please.
---
From: s.varga@example.org
Subject: Item smells of chemicals
The {p8} has a very strong chemical smell even after airing it for a week. Is it safe
for children? Considering returning it.
"""

REVIEWS = """1. "Honestly better than expected for the price. The {p1} just works." (5/5)
2. "The {p2} broke after two weeks. Disappointed." (1/5)
3. "Delivery was fast, packaging fine. The product itself is okay, nothing special." (3/5)
4. "I WANTED to love the {p3}, and mostly I do, but the app is a mess." (3/5)
5. "Perfect gift for my nephew, the {p4} kept him busy all weekend." (5/5)
6. "Not sure yet. Battery life seems short but maybe I am using it wrong?" (3/5)
7. "Customer service was rude when I asked about the {p5}. Product fine, service awful." (2/5)
8. "Five stars for the {p6}, minus one for the late delivery. So four." (4/5)
9. "It does what it says. I guess that is all you can ask." (4/5)
10. "Cheap feel, flimsy buttons, returned it the next day. Avoid the {p7}." (1/5)
"""

# ----------------------------------------------------- verification
def verify(feat, value, hw, wb):
    from sklearn.compose import ColumnTransformer
    from sklearn.dummy import DummyRegressor
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.metrics import mean_absolute_error
    from sklearn.model_selection import cross_val_score, train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.tree import DecisionTreeClassifier

    out = {}
    X = feat.drop(columns=["customer_id", "repeat_customer"])
    y = feat["repeat_customer"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)
    lr = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
    out["a02_base_rate"] = round(float(1 - y.mean()), 3)
    out["a02_logreg_train"] = round(float(lr.score(Xtr, ytr)), 3)
    out["a02_logreg_test"] = round(float(lr.score(Xte, yte)), 3)
    t3 = DecisionTreeClassifier(max_depth=3, random_state=42).fit(Xtr, ytr)
    out["a02_tree3_test"] = round(float(t3.score(Xte, yte)), 3)
    deep = DecisionTreeClassifier(random_state=42).fit(Xtr, ytr)
    out["a02_deeptree_train"] = round(float(deep.score(Xtr, ytr)), 3)
    out["a02_deeptree_test"] = round(float(deep.score(Xte, yte)), 3)

    cats = ["country", "segment", "acquisition_channel"]
    nums = ["first_order_value", "first_order_items", "newsletter",
            "support_tickets", "website_visits_first_month"]
    Xv = value[cats + nums]
    yv = value["six_month_spend"]

    def pipe(cols_cat):
        return Pipeline([("prep", ColumnTransformer(
            [("cat", OneHotEncoder(handle_unknown="ignore"), cols_cat)],
            remainder="passthrough")), ("model", LinearRegression())])

    Xtr, Xte, ytr, yte = train_test_split(Xv, yv, test_size=0.25, random_state=42)
    num_only = LinearRegression().fit(Xtr[nums], ytr)
    out["a03_r2_numeric_only"] = round(float(num_only.score(Xte[nums], yte)), 3)
    full = pipe(cats).fit(Xtr, ytr)
    out["a03_r2_with_cats"] = round(float(full.score(Xte, yte)), 3)
    out["a03_mae_with_cats"] = round(float(mean_absolute_error(yte, full.predict(Xte))), 2)
    out["a03_cv_r2_mean"] = round(float(cross_val_score(pipe(cats), Xv, yv, cv=5).mean()), 3)
    dummy = DummyRegressor().fit(Xtr, ytr)
    out["a03_mae_dummy"] = round(float(mean_absolute_error(yte, dummy.predict(Xte))), 2)
    Xleak = value[cats + nums + ["orders_in_period"]]
    Xtr2, Xte2, ytr2, yte2 = train_test_split(Xleak, yv, test_size=0.25, random_state=42)
    leaky = pipe(cats).fit(Xtr2, ytr2)
    out["a03_r2_with_leak"] = round(float(leaky.score(Xte2, yte2)), 3)

    Xh = hw[cats + nums]  # same col names except country values differ
    out["hw_cv_r2_mean"] = round(float(cross_val_score(pipe(cats), Xh, hw["six_month_spend"], cv=5).mean()), 3)

    # HW2 win-back classification
    wcats = ["country", "segment", "acquisition_channel"]
    wnums = ["months_since_last_order", "n_past_orders", "total_past_spend",
             "avg_past_order_value", "newsletter", "opened_last_3_newsletters",
             "past_support_tickets"]

    def wpipe():
        return Pipeline([("prep", ColumnTransformer(
            [("cat", OneHotEncoder(handle_unknown="ignore"), wcats)],
            remainder="passthrough")), ("model", LogisticRegression(max_iter=2000))])

    yw = wb["responded"]
    out["hw2_base_rate"] = round(float(1 - yw.mean()), 3)
    out["hw2_response_rate"] = round(float(yw.mean()), 3)
    out["hw2_cv_acc"] = round(float(cross_val_score(wpipe(), wb[wcats + wnums], yw, cv=5).mean()), 3)
    Xw_tr, Xw_te, yw_tr, yw_te = train_test_split(wb[wcats + wnums], yw, test_size=0.25, random_state=42)
    fitted = wpipe().fit(Xw_tr, yw_tr)
    out["hw2_test_acc"] = round(float(fitted.score(Xw_te, yw_te)), 3)
    proba = fitted.predict_proba(Xw_te)[:, 1]
    order = np.argsort(-proba)
    top = order[: int(0.30 * len(order))]
    out["hw2_overall_test_rate"] = round(float(yw_te.mean()), 3)
    out["hw2_top30_rate"] = round(float(yw_te.to_numpy()[top].mean()), 3)
    Xl_tr2, Xl_te2, yl_tr2, yl_te2 = train_test_split(
        wb[wcats + wnums + ["voucher_redeemed"]], yw, test_size=0.25, random_state=42)
    out["hw2_acc_with_leak"] = round(float(wpipe().fit(Xl_tr2, yl_tr2).score(Xl_te2, yl_te2)), 3)
    return out

# ----------------------------------------------------- main
def main():
    products = make_products()
    customers = make_customers()
    orders = make_orders(customers, products)
    feat, merged = make_features(customers, orders)
    value = make_value(feat, merged)
    hw = make_homework()
    wb = make_winback()

    a01 = ROOT / "lab-a01-pandas-business-data" / "data"
    a02 = ROOT / "lab-a02-first-ml-models" / "data"
    a03 = ROOT / "lab-a03-models-you-can-trust" / "data"
    hw_dir = ROOT / "lab-a03-models-you-can-trust" / "homework" / "data"
    hw2_dir = ROOT / "lab-a03-models-you-can-trust" / "homework2" / "data"
    a04 = ROOT / "lab-a04-llms-for-decisions" / "data"
    a05 = ROOT / "lab-a05-vibe-coding-project" / "data"
    for d in (a01, a02, a03, hw_dir, hw2_dir, a04, a05):
        d.mkdir(parents=True, exist_ok=True)

    orders_dirty = dirty_orders(orders)
    customers_dirty = dirty_customers(customers)
    orders_dirty.to_csv(a01 / "orders.csv", index=False)
    customers_dirty.to_csv(a01 / "customers.csv", index=False)
    products.to_excel(a01 / "products.xlsx", index=False)
    feat.drop(columns=["customer_id"]).to_csv(a02 / "customer_features.csv", index=False)
    value.to_csv(a03 / "customer_value.csv", index=False)
    hw.to_csv(hw_dir / "hw_customers.csv", index=False)
    wb.to_csv(hw2_dir / "hw2_winback.csv", index=False)
    orders_dirty.to_csv(a04 / "orders.csv", index=False)
    orders_dirty.to_csv(a05 / "orders.csv", index=False)

    stats = fy_stats(orders_dirty)
    tc, tc_rev = top_country(orders_dirty, customers)
    best_month_name = pd.Period(stats["best_month"]).strftime("%B %Y")
    report = REPORT.format(best_month_name=best_month_name, top_country=tc, **stats)
    (a04 / "quarterly-report.md").write_text(report, encoding="utf-8")
    pnames = products["product_name"].sample(8, random_state=3).tolist()
    (a04 / "complaint-emails.txt").write_text(
        EMAILS.format(**{f"p{i+1}": pnames[i] for i in range(8)}), encoding="utf-8")
    rnames = products["product_name"].sample(7, random_state=5).tolist()
    (a04 / "reviews.txt").write_text(
        REVIEWS.format(**{f"p{i+1}": rnames[i] for i in range(7)}), encoding="utf-8")

    metrics = verify(feat, value, hw, wb)
    gt = {
        "fy": stats, "top_country": tc, "top_country_revenue": tc_rev,
        "metrics": metrics,
        "dirt": {
            "orders_duplicates": int(orders_dirty.duplicated().sum()),
            "customers_duplicates": int(customers_dirty.duplicated().sum()),
            "customers_missing_email": int(customers_dirty["email"].isna().sum()),
            "customers_missing_country": int(customers_dirty["country"].isna().sum()),
            "country_label_counts": customers_dirty["country"].value_counts(dropna=False).to_dict(),
        },
        "sizes": {"orders": len(orders_dirty), "customers": len(customers_dirty),
                  "products": len(products), "features": len(feat),
                  "value": len(value), "homework": len(hw), "winback": len(wb)},
        "a02_repeat_rate": round(float(feat["repeat_customer"].mean()), 3),
    }
    (ROOT / "_build" / "ground_truth.json").write_text(
        json.dumps(gt, indent=2, default=str), encoding="utf-8")
    print(json.dumps(gt, indent=2, default=str))

if __name__ == "__main__":
    main()
