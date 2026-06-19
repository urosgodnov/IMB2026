# Worked Example: ML Analysis with Claude Code

This folder contains a standalone, polished machine-learning analysis of the Adriatica retail dataset (`orders.csv`). It is a self-contained template showing what a non-technical person can produce by directing Claude Code — building a model ladder from a simple baseline to advanced gradient boosting, for both a classification task (will a first-time buyer return?) and a regression task (how much revenue will they generate?). The analysis follows honest-evaluation principles throughout: train/test splitting, 5-fold cross-validation, and an explicit overfitting check.

Claude Code generated the entire `.qmd` document — feature engineering, five models per task, charts, and business interpretation — when given the data schema and design principles as instructions. No manual sklearn coding was required.

## How to Render

```bash
quarto render ml-analysis.qmd
```

This produces `ml-analysis.html` (the primary output). To also try PDF:

```bash
quarto render ml-analysis.qmd --to pdf
```

**Requirements:** [Quarto](https://quarto.org) must be installed (version 1.3+ recommended). The document uses the **jupyter engine** (`jupyter: python3` in the front matter), so Python 3 with the following packages is needed: `pandas`, `numpy`, `matplotlib`, `scikit-learn`, and `ipykernel`. All are available in the standard Colab / Anaconda environments.
