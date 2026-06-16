# -*- coding: utf-8 -*-
"""Shared helpers for building the IMB 2026 MADA workshop notebooks."""
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]  # workshops/

LOADER = '''import os
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
'''


def md(src):
    return nbf.v4.new_markdown_cell(src)


def code(src):
    return nbf.v4.new_code_cell(src)


def todo(task, hint=None):
    src = f"# ✏️ TODO: {task}\n"
    if hint:
        src += f"# Hint: {hint}\n"
    src += "\n"
    return code(src)


def solution(code_str, label="Show solution"):
    return md(
        f"<details><summary><b>\U0001f4a1 {label}</b> "
        "(try it yourself first — ask Gemini Learn Mode for a hint before opening this)"
        f"</summary>\n\n```python\n{code_str}\n```\n\n</details>"
    )


def answer(prompt):
    return md(f"**✍️ Your answer** — {prompt}\n\n> *(double-click this cell and write your answer here)*")


def gemini(task):
    """A [G] exercise performed in the Gemini web app tab."""
    return md(f"### \U0001f310 Gemini exercise\n\n{task}")


def save(cells, dirname, filename):
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
        "colab": {"name": filename, "provenance": []},
    }
    nb.cells = cells
    nbf.validate(nb)
    path = ROOT / dirname / filename
    nbf.write(nb, str(path))
    print(f"wrote {path}  ({len(cells)} cells)")


def write_smoke(name, data_dir, chunks):
    """Write a smoke-test script that runs the setup + all solution code."""
    lines = [
        "# -*- coding: utf-8 -*-",
        "import os",
        "import matplotlib",
        'matplotlib.use("Agg")',
        f'os.chdir(r"{ROOT / data_dir}")',
        LOADER,
    ]
    for label, chunk in chunks:
        lines.append(f'print("-- {label}")')
        lines.append(chunk)
    lines.append(f'print("SMOKE OK {name}")')
    out = ROOT / "_build" / f"smoke_{name}.py"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")
