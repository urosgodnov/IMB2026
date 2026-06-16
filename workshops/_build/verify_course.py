# -*- coding: utf-8 -*-
"""Step 6 consistency verification for the IMB 2026 MADA course project."""
import re
import subprocess
import sys
from pathlib import Path

import nbformat as nbf

WS = Path(__file__).resolve().parents[1]          # workshops/
ROOT = WS.parent                                   # project root
PLAN = ROOT / "planning"
ERRORS, OK = [], []

def check(cond, label):
    (OK if cond else ERRORS).append(label)

WORKSHOPS = [
    "lab-a01-pandas-business-data",
    "lab-a02-first-ml-models",
    "lab-a03-models-you-can-trust",
    "lab-a04-llms-for-decisions",
    "lab-a05-vibe-coding-project",
]
DATA_FILES = {
    "lab-a01-pandas-business-data": ["orders.csv", "customers.csv", "products.xlsx"],
    "lab-a02-first-ml-models": ["customer_features.csv"],
    "lab-a03-models-you-can-trust": ["customer_value.csv"],
    "lab-a04-llms-for-decisions": ["orders.csv", "quarterly-report.md", "complaint-emails.txt", "reviews.txt"],
    "lab-a05-vibe-coding-project": ["orders.csv"],
}

# --- planning documents exist
for f in ["course-brief.md", "resources.md", "course-topics.md", "course-module-a.md", "tasks.md"]:
    check((PLAN / f).exists(), f"planning/{f} exists")

module = (PLAN / "course-module-a.md").read_text(encoding="utf-8")
tasks = (PLAN / "tasks.md").read_text(encoding="utf-8")
topics = (PLAN / "course-topics.md").read_text(encoding="utf-8")

for name in WORKSHOPS:
    plan_file = PLAN / "workshop-plans" / f"{name}.md"
    check(plan_file.exists(), f"plan {name}.md exists")
    # module file links to the plan + names the directory
    check(f"workshop-plans/{name}.md" in module, f"module links plan {name}")
    check(f"`{name}`" in module, f"module names directory {name}")
    anchor = "workshop-" + name.removeprefix("lab-")
    check(f"tasks.md#{anchor}" in module, f"module status links tasks anchor for {name}")
    check(f"## {anchor}" in tasks, f"tasks.md has section for {name}")
    # plan metadata consistency
    ptxt = plan_file.read_text(encoding="utf-8")
    check(f"- **Name:** {name}" in ptxt, f"plan metadata name matches {name}")
    check(f"../tasks.md#{anchor}" in ptxt, f"plan status links tasks anchor for {name}")
    # implementation
    nb_path = WS / name / f"{name}.ipynb"
    check(nb_path.exists(), f"notebook {name}.ipynb exists")
    if nb_path.exists():
        try:
            nbf.validate(nbf.read(str(nb_path), as_version=4))
            check(True, f"notebook {name} validates (nbformat)")
        except Exception as e:
            check(False, f"notebook {name} validates (nbformat): {e}")
    check((WS / name / "instructor-notes.md").exists(), f"instructor notes {name} exist")
    for d in DATA_FILES[name]:
        check((WS / name / "data" / d).exists(), f"data {name}/data/{d} exists")

# --- homework artifacts
check((WS / "lab-a03-models-you-can-trust" / "homework" / "homework-mada.ipynb").exists(), "homework notebook exists")
check((WS / "lab-a03-models-you-can-trust" / "homework" / "data" / "hw_customers.csv").exists(), "homework data exists")
hw2 = WS / "lab-a03-models-you-can-trust" / "homework2"
check((hw2 / "homework2-winback.ipynb").exists(), "homework2 notebook exists")
check((hw2 / "data" / "hw2_winback.csv").exists(), "homework2 data exists")
check((hw2 / "GRADING.md").exists(), "homework2 GRADING.md exists")
if (hw2 / "GRADING.md").exists():
    g = (hw2 / "GRADING.md").read_text(encoding="utf-8")
    check("objective 70" in g and "subjective 30" in g, "GRADING.md has the 70/30 split")
a03nb = WS / "lab-a03-models-you-can-trust" / "lab-a03-models-you-can-trust.ipynb"
if a03nb.exists():
    txt = a03nb.read_text(encoding="utf-8")
    check("homework2-winback" in txt, "A03 notebook briefs homework 2")

# --- topics 1..17 exist and module references them
for n in range(1, 18):
    check(re.search(rf"^### {n}\. ", topics, re.M) is not None, f"topic {n} exists in course-topics.md")
check("Topics 1–5" in module and "Topics 7–8" in module and "Topics 9–12" in module
      and "Topics 13–15" in module and "Topics 16–17" in module, "module covers-ideas ranges present")

# --- no Educates implementation remnants / forbidden tool
check("workshop.yaml" not in module, "no Educates yaml referenced in module file")
brief = (PLAN / "course-brief.md").read_text(encoding="utf-8")
check("Gemini CLI" in brief and "18 Jun 2026" in brief, "brief records the Gemini CLI exclusion")

# --- ground truth + builders present
for f in ["generate_data.py", "ground_truth.json", "nb.py"] + [f"build_a0{i}.py" for i in range(1, 6)]:
    check((WS / "_build" / f).exists(), f"_build/{f} exists")

# --- rerun all smoke tests (the final gate)
for tag in ["a01", "a02", "a03", "a04", "a05", "hw2"]:
    r = subprocess.run([sys.executable, str(WS / "_build" / f"smoke_{tag}.py")],
                       capture_output=True, text=True)
    check(r.returncode == 0 and f"SMOKE OK {tag}" in r.stdout, f"smoke test {tag} green")
    if r.returncode != 0:
        print(r.stdout[-1500:], r.stderr[-1500:])

print(f"\n{len(OK)} checks passed, {len(ERRORS)} failed")
for e in ERRORS:
    print("FAIL:", e)
sys.exit(1 if ERRORS else 0)
