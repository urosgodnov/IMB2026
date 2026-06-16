# -*- coding: utf-8 -*-
import os
import matplotlib
matplotlib.use("Agg")
os.chdir(r"C:\Onedrive\Personal\OneDrive\Famnit\IMB2026\workshops\lab-a03-models-you-can-trust\data")
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
customers = load_file("customer_value.csv")
import pandas as pd
categorical = ["country", "segment", "acquisition_channel"]
numeric = ["first_order_value", "first_order_items", "newsletter",
           "support_tickets", "website_visits_first_month"]
target = "six_month_spend"
customers[categorical + numeric + [target]].head()
print("-- first_reg")
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

X = customers[numeric]
y = customers[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

reg = LinearRegression().fit(X_train, y_train)
pred = reg.predict(X_test)
print("MAE:", round(mean_absolute_error(y_test, pred), 2), "EUR")
print("R^2:", round(r2_score(y_test, pred), 3))
assert 0.5 < r2_score(y_test, pred) < 0.8
print("-- coefs")
pd.DataFrame({"feature": numeric, "coefficient": reg.coef_.round(2)}) \
    .sort_values("coefficient", key=abs, ascending=False)
print("-- cat_fail")
# DEMO - run me: what happens if we feed the model text columns as-is?
try:
    LinearRegression().fit(customers[categorical + numeric], y)
except Exception as e:
    print(type(e).__name__, "-", str(e)[:120], "...")
print("-- pipeline")
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

prep = ColumnTransformer(
    [("cat", OneHotEncoder(handle_unknown="ignore"), categorical)],
    remainder="passthrough")

pipe = Pipeline([("prep", prep), ("model", LinearRegression())])

X2 = customers[categorical + numeric]
X2_train, X2_test, y2_train, y2_test = train_test_split(X2, y, test_size=0.25, random_state=42)
pipe.fit(X2_train, y2_train)
pred2 = pipe.predict(X2_test)
print("MAE:", round(mean_absolute_error(y2_test, pred2), 2), "EUR")
print("R^2:", round(r2_score(y2_test, pred2), 3))
assert r2_score(y2_test, pred2) > r2_score(y_test, pred) + 0.05
print("-- cv")
from sklearn.model_selection import cross_val_score

scores = cross_val_score(pipe, X2, y, cv=5)
print("five R^2 scores:", scores.round(3))
print("mean:", round(scores.mean(), 3), "| std:", round(scores.std(), 3))
print("-- compare")
from sklearn.dummy import DummyRegressor
from sklearn.tree import DecisionTreeRegressor

def make_pipe(model):
    return Pipeline([("prep", ColumnTransformer(
        [("cat", OneHotEncoder(handle_unknown="ignore"), categorical)],
        remainder="passthrough")), ("model", model)])

candidates = {
    "always predict the mean (dummy)": DummyRegressor(),
    "linear regression": LinearRegression(),
    "decision tree (depth 4)": DecisionTreeRegressor(max_depth=4, random_state=42),
}
rows = []
for name, m in candidates.items():
    s = cross_val_score(make_pipe(m), X2, y, cv=5)
    rows.append({"model": name, "cv_r2_mean": round(s.mean(), 3), "cv_r2_std": round(s.std(), 3)})
comparison = pd.DataFrame(rows).sort_values("cv_r2_mean", ascending=False)
comparison
assert comparison.iloc[0]["model"] == "linear regression"
assert comparison.iloc[-1]["cv_r2_mean"] < 0.05
print("-- leak")
# DEMO - run me. THE WRONG WAY vs THE HONEST WAY. Do not copy part (a) into real work.
# Our table contains "orders_in_period" - the number of orders DURING the six months
# we are predicting. At prediction time, that number does not exist yet.

# (a) WRONG: include the future
X_leak = customers[categorical + numeric + ["orders_in_period"]]
Xl_tr, Xl_te, yl_tr, yl_te = train_test_split(X_leak, y, test_size=0.25, random_state=42)
leaky = make_pipe(LinearRegression()).fit(Xl_tr, yl_tr)
print("(a) WITH the future column   R^2 =", round(r2_score(yl_te, leaky.predict(Xl_te)), 3), " <- looks amazing")

# (b) HONEST: only what we know at prediction time
print("(b) WITHOUT it (our pipeline) R^2 =", round(cross_val_score(make_pipe(LinearRegression()), X2, y, cv=5).mean(), 3))
assert r2_score(yl_te, leaky.predict(Xl_te)) > 0.9
print("-- hw_setup")
hw = load_file(r"../homework/data/hw_customers.csv")
assert hw.shape == (420, 11), hw.shape
print("SMOKE OK a03")