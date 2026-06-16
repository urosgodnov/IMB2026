# -*- coding: utf-8 -*-
import os
import matplotlib
matplotlib.use("Agg")
os.chdir(r"C:\Onedrive\Personal\OneDrive\Famnit\IMB2026\workshops\lab-a02-first-ml-models\data")
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
features = load_file("customer_features.csv")
import pandas as pd
print("-- baseline")
features["repeat_customer"].value_counts(normalize=True).round(3)
print("-- split")
from sklearn.model_selection import train_test_split

X = features.drop(columns=["repeat_customer"])
y = features["repeat_customer"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
print("training customers:", len(X_train), "| test customers:", len(X_test))
print("-- logreg")
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(max_iter=2000)
model.fit(X_train, y_train)
print("accuracy on training data:", round(model.score(X_train, y_train), 3))
print("accuracy on test data:    ", round(model.score(X_test, y_test), 3))
assert model.score(X_test, y_test) > 0.72
print("-- confusion")
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

y_pred = model.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
ConfusionMatrixDisplay(cm, display_labels=["no repeat", "repeat"]).plot()
cm
print("-- costs")
missed_returners = cm[1, 0]   # actual repeat, predicted no  -> marketing ignores them
wasted_discounts = cm[0, 1]   # actual no, predicted repeat   -> discount for nothing
print("returners marketing would miss:", missed_returners)
print("discounts sent for nothing:    ", wasted_discounts)
print("-- tree")
from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt

tree = DecisionTreeClassifier(max_depth=3, random_state=42)
tree.fit(X_train, y_train)
print("tree accuracy on test data:", round(tree.score(X_test, y_test), 3))

plt.figure(figsize=(16, 7))
plot_tree(tree, feature_names=X.columns, class_names=["no repeat", "repeat"],
          filled=True, fontsize=8)
plt.show()
print("-- compare")
comparison = pd.DataFrame({
    "model": ["logistic regression", "decision tree (depth 3)"],
    "test_accuracy": [round(model.score(X_test, y_test), 3), round(tree.score(X_test, y_test), 3)],
})
comparison
print("-- drivers")
coef = pd.DataFrame({"feature": X.columns, "logreg_coefficient": model.coef_[0].round(3)})
coef["abs"] = coef["logreg_coefficient"].abs()
print(coef.sort_values("abs", ascending=False).drop(columns="abs").to_string(index=False))

imp = pd.DataFrame({"feature": X.columns, "tree_importance": tree.feature_importances_.round(3)})
print()
print(imp.sort_values("tree_importance", ascending=False).to_string(index=False))
print("-- overfit")
results = []
for depth in range(1, 16):
    t = DecisionTreeClassifier(max_depth=depth, random_state=42).fit(X_train, y_train)
    results.append({"max_depth": depth,
                    "train_accuracy": t.score(X_train, y_train),
                    "test_accuracy": t.score(X_test, y_test)})
results = pd.DataFrame(results).set_index("max_depth")
results.plot(marker="o", title="The overfitting curve: deeper is not better")
import matplotlib.pyplot as plt
plt.ylabel("accuracy")
plt.show()
results.round(3)
assert results.loc[15, "train_accuracy"] > 0.97
assert results.loc[15, "test_accuracy"] < model.score(X_test, y_test)
print("SMOKE OK a02")