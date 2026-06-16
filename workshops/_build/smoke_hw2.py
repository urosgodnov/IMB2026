# -*- coding: utf-8 -*-
import os
import matplotlib
matplotlib.use("Agg")
os.chdir(r"C:\Onedrive\Personal\OneDrive\Famnit\IMB2026\workshops\lab-a03-models-you-can-trust\homework2\data")
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

print("-- load")
pilot = load_file("hw2_winback.csv")
import pandas as pd
assert pilot.shape == (804, 13), pilot.shape
print("-- reference_solution")
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

categorical = ["country", "segment", "acquisition_channel"]
numeric = ["months_since_last_order", "n_past_orders", "total_past_spend",
           "avg_past_order_value", "newsletter", "opened_last_3_newsletters",
           "past_support_tickets"]
# voucher_redeemed EXCLUDED: only known after the campaign (leakage)
X = pilot[categorical + numeric]
y = pilot["responded"]
pipe = Pipeline([("prep", ColumnTransformer(
    [("cat", OneHotEncoder(handle_unknown="ignore"), categorical)],
    remainder="passthrough")), ("model", LogisticRegression(max_iter=2000))])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
pipe.fit(X_train, y_train)
acc = pipe.score(X_test, y_test)
cv = cross_val_score(pipe, X, y, cv=5)
baseline = 1 - y.mean()
print("test acc:", round(acc, 3), "| cv:", round(cv.mean(), 3), "| baseline:", round(baseline, 3))
assert acc > baseline + 0.10, (acc, baseline)
print("-- ranking")
# --- PROVIDED CELL: run AFTER your pipeline is fitted. Requires these exact names:
#     pipe     - your fitted Pipeline
#     X_test, y_test - from your train_test_split(random_state=42)
proba = pipe.predict_proba(X_test)[:, 1]
ranked = X_test.copy()
ranked["responded"] = y_test.values
ranked["proba"] = proba
top30 = ranked.sort_values("proba", ascending=False).head(int(0.30 * len(ranked)))
print("overall test response rate:", round(ranked["responded"].mean(), 3))
print("top-30% response rate:     ", round(top30["responded"].mean(), 3))
lift = top30["responded"].mean() / ranked["responded"].mean()
print("lift:", round(lift, 2))
assert lift > 1.5, lift
print("-- leak_flag_works")
X_leak = pilot[categorical + numeric + ["voucher_redeemed"]]
Xl_tr, Xl_te, yl_tr, yl_te = train_test_split(X_leak, y, test_size=0.25, random_state=42)
leaky = Pipeline([("prep", ColumnTransformer(
    [("cat", OneHotEncoder(handle_unknown="ignore"), categorical)],
    remainder="passthrough")), ("model", LogisticRegression(max_iter=2000))]).fit(Xl_tr, yl_tr)
leak_acc = leaky.score(Xl_te, yl_te)
print("accuracy WITH the leak column:", round(leak_acc, 3), " -> grader flag threshold 0.95 works")
assert leak_acc > 0.95, leak_acc
print("SMOKE OK hw2")