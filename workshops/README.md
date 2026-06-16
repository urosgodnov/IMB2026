# Workshops — operations guide (instructor)

One folder per workshop: the Colab notebook, its `data/`, and `instructor-notes.md`.
`_build/` holds the generator and notebook builders (not student-facing).

## Publishing data (before each class)

Notebooks load data via a `DATA_BASE_URL` constant (first code cell). Three options:

1. **GitHub (recommended):** push this repo (or just the `workshops/` folders) to a public
   GitHub repository, then set e.g.
   `DATA_BASE_URL = "https://raw.githubusercontent.com/<user>/<repo>/main/workshops/lab-a01-pandas-business-data/data"`
   in the workshop's first cell before sharing the notebook.
2. **Any static host** serving the `data/` folder over HTTPS.
3. **Do nothing:** the loader falls back to `files.upload()` — students upload the data
   files at the start (you must distribute them, e.g. via the LMS).

Share notebooks with students as Colab links: upload the `.ipynb` to Drive → Open with
Colab → Share, or publish via GitHub (Colab opens GitHub notebooks directly).

## Rebuilding (if you change anything)

```
cd workshops/_build
python generate_data.py     # regenerate all datasets + ground_truth.json (seed-fixed, deterministic)
python build_a01.py         # rebuild a notebook (a01 ... a05; a03 also builds the homework)
python smoke_a01.py         # run that workshop's solution code end-to-end against the data
```

All smoke tests must print `SMOKE OK` before you ship a change. Ground-truth numbers
for instructor notes live in `_build/ground_truth.json`.

## Free-tier checklist (run ~1 week before 15 Jun 2026)

- Colab free tier: pandas/scikit-learn/matplotlib import OK; `google.colab.ai` available; Learn Mode visible
- Gemini web app accessible with a plain Google account
- A05 tool decision aligned with Aleš (Vibe coding 1) — **not Gemini CLI** (free tier ends 18 Jun 2026)
- Students reminded to bring a personal Google account (18+)
