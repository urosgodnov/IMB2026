# -*- coding: utf-8 -*-
"""Build lab-a02-first-ml-models notebook + smoke test."""
from nb import LOADER, answer, code, md, save, solution, todo, write_smoke

S = {}

S["baseline"] = '''features["repeat_customer"].value_counts(normalize=True).round(3)'''

S["split"] = '''from sklearn.model_selection import train_test_split

X = features.drop(columns=["repeat_customer"])
y = features["repeat_customer"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
print("training customers:", len(X_train), "| test customers:", len(X_test))'''

S["logreg"] = '''from sklearn.linear_model import LogisticRegression

model = LogisticRegression(max_iter=2000)
model.fit(X_train, y_train)
print("accuracy on training data:", round(model.score(X_train, y_train), 3))
print("accuracy on test data:    ", round(model.score(X_test, y_test), 3))'''

S["confusion"] = '''from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

y_pred = model.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
ConfusionMatrixDisplay(cm, display_labels=["no repeat", "repeat"]).plot()
cm'''

S["costs"] = '''missed_returners = cm[1, 0]   # actual repeat, predicted no  -> marketing ignores them
wasted_discounts = cm[0, 1]   # actual no, predicted repeat   -> discount for nothing
print("returners marketing would miss:", missed_returners)
print("discounts sent for nothing:    ", wasted_discounts)'''

S["tree"] = '''from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt

tree = DecisionTreeClassifier(max_depth=3, random_state=42)
tree.fit(X_train, y_train)
print("tree accuracy on test data:", round(tree.score(X_test, y_test), 3))

plt.figure(figsize=(16, 7))
plot_tree(tree, feature_names=X.columns, class_names=["no repeat", "repeat"],
          filled=True, fontsize=8)
plt.show()'''

S["compare"] = '''comparison = pd.DataFrame({
    "model": ["logistic regression", "decision tree (depth 3)"],
    "test_accuracy": [round(model.score(X_test, y_test), 3), round(tree.score(X_test, y_test), 3)],
})
comparison'''

S["drivers"] = '''coef = pd.DataFrame({"feature": X.columns, "logreg_coefficient": model.coef_[0].round(3)})
coef["abs"] = coef["logreg_coefficient"].abs()
print(coef.sort_values("abs", ascending=False).drop(columns="abs").to_string(index=False))

imp = pd.DataFrame({"feature": X.columns, "tree_importance": tree.feature_importances_.round(3)})
print()
print(imp.sort_values("tree_importance", ascending=False).to_string(index=False))'''

S["overfit"] = '''results = []
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
results.round(3)'''

cells = [
    md("""# A02 · First Machine-Learning Models

**IMB 2026 · MADA · Workshop A02 (Wed 17 Jun 2026, 15:00–19:00)**

This morning you *described* Adriatica's business. This afternoon the marketing lead
walks in with a different kind of question:

> *"We get plenty of first-time buyers. **Which of them will come back?** If I knew,
> I'd spend the retention budget only on the ones worth keeping."*

No report of the past answers that. You need a model that **predicts**. By the end
you will be able to:

- explain features, target, and train/test split in business terms,
- train classifiers with scikit-learn's `fit` → `predict` → `score` rhythm,
- read a confusion matrix and explain why accuracy alone misleads,
- compare logistic regression and a decision tree and read what drives their predictions,
- recognise overfitting when you see it."""),
    md("""## 0 · Setup

We prepared a **customer features table** from data like this morning's (one row per
first-time buyer, plus what we knew about them at the time of their first order).
You could build it yourself with `groupby`+`merge` — that derivation is a stretch
exercise at the end; today we focus on the modelling."""),
    code(LOADER + '\nfeatures = load_file("customer_features.csv")\nprint(features.shape)\nfeatures.head()'),

    md("""## 1 · Features, target, and an honest baseline

Machine learning vocabulary, business edition:

- **Target** — the thing we want to predict: `repeat_customer` (1 = came back, 0 = didn't).
- **Features** — what we knew *at prediction time*: first order value, newsletter, support tickets, …
- **Learning** — instead of writing rules by hand ("if newsletter and value > 80 then…"),
  we show the computer past examples and let it find the rules.

Before any model: what would a *zero-effort* prediction score? If most customers
don't return, "predict nobody returns" is already right fairly often. **Every model
must beat that baseline or it is decoration.**"""),
    todo('what share of customers became repeat customers? (this defines the baseline)',
         'features["repeat_customer"].value_counts(normalize=True)'),
    solution(S["baseline"]),
    answer("The majority class is about 56% — so a model scoring 60% accuracy would be… impressive or embarrassing?"),

    md("""## 2 · The first model

**The honesty rule:** never grade a model on the same data it learned from — that is
memorising the answer key. We split: ~75% to learn from, 25% kept in a drawer for the exam."""),
    todo('split X (all feature columns) and y (repeat_customer) into train and test sets, test_size=0.25, random_state=42',
         'from sklearn.model_selection import train_test_split'),
    solution(S["split"]),
    md("""Now the model. **Logistic regression** is the workhorse of business classification:
fast, robust, and it can explain itself. And meet the rhythm you will use for *every*
scikit-learn model, forever:

```
model.fit(X_train, y_train)      # learn
model.predict(X_new)             # apply
model.score(X_test, y_test)      # grade — on unseen data
```"""),
    todo('create a LogisticRegression(max_iter=2000), fit it on the training data, and print its accuracy on BOTH train and test',
         'model.score(X_train, y_train) vs model.score(X_test, y_test)'),
    solution(S["logreg"]),
    answer("Your test accuracy vs. the ~56% baseline: is the model earning its keep?"),

    md("""## 3 · Accuracy is not enough

77% accurate — but *which* 23% is it wrong about? For marketing, the two mistakes
cost completely different amounts:

- a **missed returner** (model said "won't return", they would have) — lost retention opportunity;
- a **wasted discount** (model said "will return", they didn't) — coupon money burned.

The **confusion matrix** splits the errors apart."""),
    todo('compute and display the confusion matrix for the test set',
         'confusion_matrix(y_test, y_pred) and ConfusionMatrixDisplay'),
    solution(S["confusion"]),
    todo('from the matrix: how many actual returners would marketing miss? how many discounts would be wasted?',
         'cm[1, 0] is actual-repeat predicted-no; cm[0, 1] is the opposite'),
    solution(S["costs"]),
    answer("Which of the two errors is more expensive for Adriatica, and what does that mean for how we should use the model? (There is no single right answer — argue it.)"),

    md("""## 4 · A second opinion: the decision tree

A **decision tree** learns a flowchart of yes/no questions — the most *readable*
model there is. Managers love trees because you can print one and argue with it."""),
    todo('fit a DecisionTreeClassifier(max_depth=3, random_state=42), print its test accuracy, and draw it with plot_tree',
         'plot_tree(tree, feature_names=X.columns, filled=True)'),
    solution(S["tree"]),
    todo('collect both models and their test accuracies in a small comparison DataFrame',
         'pd.DataFrame({"model": [...], "test_accuracy": [...]})'),
    solution(S["compare"]),
    answer("Trace one path through the tree out loud, as a business rule ('customers who … and … mostly return'). Does the rule sound plausible?"),

    md("""## 5 · What drives repeat purchase?

Prediction is half the value; the other half is **understanding the drivers**.
Logistic regression exposes *coefficients* (direction and strength per feature);
trees expose *feature importances* (how much each feature was used)."""),
    todo('show the logistic-regression coefficients and the tree feature importances side by side, sorted by strength',
         'model.coef_[0] and tree.feature_importances_, wrapped in DataFrames'),
    solution(S["drivers"]),
    answer("Write the two-sentence summary you would send to marketing: which 2–3 factors drive repeat purchase, and which direction?"),
    md("""**⚠️ Drivers are not causes.** Newsletter subscribers return more — but maybe keen
customers subscribe to newsletters, not the other way round. The model sees
*correlation*; campaigns built on it should be tested, not assumed. (More on honest
analysis on Friday.)"""),

    md("""## 6 · Overfitting, live

What if we let the tree grow as deep as it wants? Run the experiment below —
it trains 15 trees of increasing depth and plots train vs. test accuracy.
*(Pre-written: watch the punchline, don't type it.)*"""),
    code(S["overfit"]),
    md("""Read the two curves: training accuracy marches to 100% — the tree *memorised*
the training customers. Test accuracy **falls**. That gap is **overfitting**: the model
learned the noise, not the pattern. A model is only as good as its performance on
data it has never seen — which is exactly why we made the split in Section 2."""),
    todo('based on the table/plot: which max_depth would YOU deploy? assign your choice to chosen_depth and say why in a comment',
         'look for the depth where test accuracy peaks before the slide'),
    solution('chosen_depth = 4  # test accuracy peaks around here; deeper only helps the train score\n# Reasoning: past depth ~4-5 the test curve flattens then degrades while train keeps climbing.'),

    md("""## 7 · Wrap-up

Marketing now has: a model that beats the baseline by a clear margin, an honest map
of its two error types, and the top drivers of repeat purchase.

**Two confessions before Friday** (A03):

1. We quietly **dropped the text columns** — country, segment, channel. Real signal,
   unusable by models as raw text. Friday: encoding categoricals, properly.
2. We graded everything on **one** train/test split. One split is one opinion —
   what if we got a lucky drawer? Friday: cross-validation, baselines, and the ways
   analyses accidentally lie — *models you can trust*.

**🎯 Stretch:** (a) lower the decision threshold with `model.predict_proba` and watch
the missed-returners count change; (b) try `KNeighborsClassifier`; (c) rebuild
`customer_features.csv` yourself from A01's `orders.csv` + `customers.csv` with
`groupby` + `merge`."""),
]

chunks = [
    ("setup", 'features = load_file("customer_features.csv")\nimport pandas as pd'),
    ("baseline", S["baseline"]),
    ("split", S["split"]),
    ("logreg", S["logreg"] + '\nassert model.score(X_test, y_test) > 0.72'),
    ("confusion", S["confusion"]),
    ("costs", S["costs"]),
    ("tree", S["tree"]),
    ("compare", S["compare"]),
    ("drivers", S["drivers"]),
    ("overfit", S["overfit"] + '\nassert results.loc[15, "train_accuracy"] > 0.97\nassert results.loc[15, "test_accuracy"] < model.score(X_test, y_test)'),
]

if __name__ == "__main__":
    save(cells, "lab-a02-first-ml-models", "lab-a02-first-ml-models.ipynb")
    write_smoke("a02", "lab-a02-first-ml-models/data", chunks)
