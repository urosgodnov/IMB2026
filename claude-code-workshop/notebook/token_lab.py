"""
token_lab.py — helpers for the token-consumption-lab notebook.

Both the notebook cells and the smoke test import from here (DRY).
No API key required for load_results() or make_charts().
"""

import os
import pathlib
import time

import matplotlib
matplotlib.use("Agg")  # headless backend — must happen before any pyplot import
import matplotlib.pyplot as plt
import pandas as pd

# ---------------------------------------------------------------------------
# Prices per 1 million tokens  (from cc-facts.md, 2026-06-19)
# Key: model short name  →  (input_$/M, output_$/M)
# ---------------------------------------------------------------------------
PRICES = {
    "opus":   (5.0, 25.0),
    "sonnet": (3.0, 15.0),
    "haiku":  (1.0,  5.0),
}

# Model IDs used when calling the API
_MODEL_IDS = {
    "opus":   "claude-opus-4-8",
    "sonnet": "claude-sonnet-4-6",
    "haiku":  "claude-haiku-4-5",
}

RESULTS_HEADER = [
    "setting_group",
    "setting",
    "input_tokens",
    "output_tokens",
    "cached_input_tokens",
    "usd_cost",
    "latency_s",
]

# Directory of this module (used as default search location)
_MODULE_DIR = pathlib.Path(__file__).parent


# ---------------------------------------------------------------------------
# load_results
# ---------------------------------------------------------------------------
def load_results(notebook_dir=None) -> pd.DataFrame:
    """
    Load results.csv if it exists in notebook_dir, otherwise fall back to
    results.sample.csv (illustrative placeholder data).

    Parameters
    ----------
    notebook_dir : str | pathlib.Path | None
        Directory to look in.  Defaults to the directory of this module.
    """
    base = pathlib.Path(notebook_dir) if notebook_dir is not None else _MODULE_DIR

    real = base / "results.csv"
    sample = base / "results.sample.csv"

    if real.exists():
        df = pd.read_csv(real)
        print(f"Loaded measured results from: {real}")
    else:
        df = pd.read_csv(sample)
        print(f"No results.csv found — using illustrative sample: {sample}")

    return df


# ---------------------------------------------------------------------------
# usd_cost
# ---------------------------------------------------------------------------
def usd_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cached_input_tokens: int = 0,
) -> float:
    """
    Compute USD cost for a single API call.

    Pricing rules (from cc-facts.md):
    - Uncached input tokens billed at full input price.
    - Cached (read) input tokens billed at 0.1x input price.
    - Output tokens billed at full output price.

    Parameters
    ----------
    model : str
        One of "opus", "sonnet", "haiku".
    input_tokens : int
        Uncached input tokens (i.e. tokens NOT served from cache).
    output_tokens : int
        Output / completion tokens.
    cached_input_tokens : int
        Cache-read input tokens (billed at 0.1x input rate).
    """
    in_price, out_price = PRICES[model]
    cost = (
        input_tokens * in_price / 1e6
        + cached_input_tokens * in_price * 0.1 / 1e6
        + output_tokens * out_price / 1e6
    )
    return round(cost, 6)


# ---------------------------------------------------------------------------
# make_charts
# ---------------------------------------------------------------------------
def make_charts(df: pd.DataFrame, outdir) -> list:
    """
    Render three bar charts to PNG files and return their paths.

    Charts produced:
    1. USD cost by model      (setting_group == 'model')
    2. USD cost by effort     (setting_group == 'effort', fixed order)
    3. USD cost cached vs un  (setting_group == 'caching')

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with RESULTS_HEADER columns.
    outdir : str | pathlib.Path
        Directory where PNG files are written.
    """
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    paths = []

    # -- Chart 1: cost by model -------------------------------------------
    sub = df[df["setting_group"] == "model"].copy()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(sub["setting"], sub["usd_cost"], color=["#4C72B0", "#55A868", "#C44E52"])
    ax.set_title("Token cost by model\n(same prompt, 1500 input / 600 output tokens)")
    ax.set_xlabel("Model")
    ax.set_ylabel("USD cost")
    ax.set_ylim(0, sub["usd_cost"].max() * 1.3)
    for bar, val in zip(ax.patches, sub["usd_cost"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.0003,
            f"${val:.4f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    fig.tight_layout()
    p1 = outdir / "chart_model.png"
    fig.savefig(p1, dpi=120)
    plt.close(fig)
    paths.append(str(p1))

    # -- Chart 2: cost by effort (opus, fixed order) ----------------------
    effort_order = ["low", "medium", "high", "xhigh", "max"]
    sub = df[df["setting_group"] == "effort"].copy()
    sub["setting"] = pd.Categorical(sub["setting"], categories=effort_order, ordered=True)
    sub = sub.sort_values("setting")
    colors = ["#8DA0CB", "#66C2A5", "#FC8D62", "#E78AC3", "#A6D854"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(sub["setting"].astype(str), sub["usd_cost"], color=colors[: len(sub)])
    ax.set_title("Token cost by reasoning effort\n(Opus 4.8, same prompt)")
    ax.set_xlabel("Effort level")
    ax.set_ylabel("USD cost")
    ax.set_ylim(0, sub["usd_cost"].max() * 1.3)
    for bar, val in zip(ax.patches, sub["usd_cost"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.001,
            f"${val:.4f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    fig.tight_layout()
    p2 = outdir / "chart_effort.png"
    fig.savefig(p2, dpi=120)
    plt.close(fig)
    paths.append(str(p2))

    # -- Chart 3: cached vs uncached --------------------------------------
    sub = df[df["setting_group"] == "caching"].copy()
    colors_cache = ["#E15759", "#4E79A7"]
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(sub["setting"], sub["usd_cost"], color=colors_cache[: len(sub)])
    ax.set_title("Token cost: cached vs uncached\n(8000-token prefix, Opus 4.8)")
    ax.set_xlabel("Cache state")
    ax.set_ylabel("USD cost")
    ax.set_ylim(0, sub["usd_cost"].max() * 1.3)
    for bar, val in zip(ax.patches, sub["usd_cost"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.001,
            f"${val:.4f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    fig.tight_layout()
    p3 = outdir / "chart_caching.png"
    fig.savefig(p3, dpi=120)
    plt.close(fig)
    paths.append(str(p3))

    return paths


# ---------------------------------------------------------------------------
# measure_settings  (REAL API measurement — requires ANTHROPIC_API_KEY)
# ---------------------------------------------------------------------------
# Short business prompt used for all settings.
_BUSINESS_PROMPT = (
    "You are a business analyst. In two sentences, summarise the key takeaway "
    "from this sales figure: total Q2 revenue was $4.2 M, up 18 % year-on-year."
)

# Padded prefix for the caching test. Opus's cache floor is 4096 tokens: below
# it, cache_control is silently ignored and the second call shows no cache hit
# (breaking the lesson). The sentence is ~11 tokens; 600 repeats ~= 6.6k tokens,
# comfortably above the floor. The first (uncached) call costs a few cents.
_CACHE_PREFIX_LONG = ("This is a long business context document for caching. " * 600 + "\n\n")

_SMALL_CONTEXT = "Q2 revenue: $4.2 M, up 18 % YoY."
_STUFFED_CONTEXT = ("Historical quarterly figures: " + ", ".join(
    [f"Q{i % 4 + 1} {2010 + i // 4}: ${(i * 3.7 + 1.1):.1f}M" for i in range(400)]
))


def measure_settings(client) -> pd.DataFrame:
    """
    Send the same short business prompt under each setting group and record
    token usage.  Returns a DataFrame with RESULTS_HEADER columns.

    Parameters
    ----------
    client : anthropic.Anthropic
        An authenticated Anthropic client.

    Notes
    -----
    - Uses claude-opus-4-8 for model, effort, caching, and context groups.
    - Uses claude-sonnet-4-6 and claude-haiku-4-5 for the model group.
    - Caching: sends a >=4096-token prefix with cache_control to warm the cache,
      then sends again to read from cache.
    - Effort: uses output_config={"effort": level} on Opus 4.8.
    - Context: stuffed input sends a long context string.
    """
    rows = []

    def _record(group, setting, model_key, r, t0):
        u = r.usage
        inp = u.input_tokens
        out = u.output_tokens
        cached = getattr(u, "cache_read_input_tokens", 0) or 0
        cost = usd_cost(model_key, inp, out, cached)
        rows.append({
            "setting_group": group,
            "setting": setting,
            "input_tokens": inp,
            "output_tokens": out,
            "cached_input_tokens": cached,
            "usd_cost": cost,
            "latency_s": round(time.time() - t0, 2),
        })

    # -- Group: model ------------------------------------------------------
    for model_key in ("opus", "sonnet", "haiku"):
        model_id = _MODEL_IDS[model_key]
        kwargs = dict(
            model=model_id,
            max_tokens=256,
            messages=[{"role": "user", "content": _BUSINESS_PROMPT}],
        )
        t0 = time.time()
        r = client.messages.create(**kwargs)
        _record("model", model_key, model_key, r, t0)

    # -- Group: effort (Opus 4.8 only) ------------------------------------
    for level in ("low", "medium", "high", "xhigh", "max"):
        t0 = time.time()
        r = client.messages.create(
            model=_MODEL_IDS["opus"],
            max_tokens=1024,
            thinking={"type": "adaptive"},
            output_config={"effort": level},
            messages=[{"role": "user", "content": _BUSINESS_PROMPT}],
        )
        _record("effort", level, "opus", r, t0)

    # -- Group: caching (Opus 4.8, >=4096-token prefix) -------------------
    cached_content = [
        {
            "type": "text",
            "text": _CACHE_PREFIX_LONG,
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": _BUSINESS_PROMPT,
        },
    ]

    # First call — warms the cache (cache_creation_input_tokens > 0)
    t0 = time.time()
    r_uncached = client.messages.create(
        model=_MODEL_IDS["opus"],
        max_tokens=256,
        messages=[{"role": "user", "content": cached_content}],
    )
    _record("caching", "uncached", "opus", r_uncached, t0)

    # Second call — should hit the cache (cache_read_input_tokens > 0)
    t0 = time.time()
    r_cached = client.messages.create(
        model=_MODEL_IDS["opus"],
        max_tokens=256,
        messages=[{"role": "user", "content": cached_content}],
    )
    _record("caching", "cached", "opus", r_cached, t0)

    # -- Group: context size (Opus 4.8) -----------------------------------
    for ctx_name, ctx_text in (("small", _SMALL_CONTEXT), ("stuffed", _STUFFED_CONTEXT)):
        prompt = f"Context:\n{ctx_text}\n\nIn one sentence, what is the key business insight?"
        t0 = time.time()
        r = client.messages.create(
            model=_MODEL_IDS["opus"],
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        _record("context", ctx_name, "opus", r, t0)

    df = pd.DataFrame(rows, columns=RESULTS_HEADER)
    return df


# ===========================================================================
# Provider comparison: Claude vs DeepSeek  (cost for the SAME task)
# ===========================================================================
# Prices per 1M tokens. Claude from cc-facts.md; DeepSeek V4 Flash verified
# 2026-06-19 ($0.14 in / $0.28 out). DeepSeek speaks an OpenAI-compatible API,
# so it is called with the `openai` SDK (base_url swapped), NOT the Anthropic SDK.
PROVIDER_PRICES = {
    "Claude Opus 4.8":   (5.0, 25.0),
    "Claude Haiku 4.5":  (1.0,  5.0),
    "DeepSeek V4 Flash": (0.14, 0.28),
}

PROVIDERS_HEADER = [
    "provider", "model", "input_tokens", "output_tokens", "usd_cost", "latency_s",
]

# (vendor, display model name, model id) — order = chart order
_PROVIDER_CALLS = [
    ("Anthropic", "Claude Opus 4.8",   "claude-opus-4-8"),
    ("Anthropic", "Claude Haiku 4.5",  "claude-haiku-4-5"),
    ("DeepSeek",  "DeepSeek V4 Flash", "deepseek-v4-flash"),  # 'deepseek-chat' retires 2026-07-24
]

# DeepSeek OpenAI-compatible endpoint.
DEEPSEEK_BASE_URL = "https://api.deepseek.com"


def provider_usd_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """Cost of one call using PROVIDER_PRICES (no caching in this comparison)."""
    in_price, out_price = PROVIDER_PRICES[model_name]
    return round(input_tokens * in_price / 1e6 + output_tokens * out_price / 1e6, 8)


def load_providers(notebook_dir=None) -> pd.DataFrame:
    """Load providers.csv if present, else providers.sample.csv (illustrative)."""
    base = pathlib.Path(notebook_dir) if notebook_dir is not None else _MODULE_DIR
    real = base / "providers.csv"
    sample = base / "providers.sample.csv"
    if real.exists():
        df = pd.read_csv(real)
        print(f"Loaded measured provider results from: {real}")
    else:
        df = pd.read_csv(sample)
        print(f"No providers.csv found — using illustrative sample: {sample}")
    return df


def make_provider_chart(df: pd.DataFrame, outdir) -> str:
    """Bar chart of USD cost per task by model (Claude vs DeepSeek). Returns PNG path."""
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    sub = df.copy()
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["#C44E52", "#4C72B0", "#55A868"][: len(sub)]
    ax.bar(sub["model"], sub["usd_cost"], color=colors)
    ax.set_title("Cost of one summary task: Claude vs DeepSeek\n(same prompt; illustrative)")
    ax.set_xlabel("Model")
    ax.set_ylabel("USD per task")
    top = sub["usd_cost"].max()
    ax.set_ylim(0, top * 1.3)
    for bar, val in zip(ax.patches, sub["usd_cost"]):
        label = f"${val:.5f}" if val < 0.01 else f"${val:.4f}"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + top * 0.02,
                label, ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    p = outdir / "chart_providers.png"
    fig.savefig(p, dpi=120)
    plt.close(fig)
    return str(p)


def measure_providers(anthropic_client, deepseek_client) -> pd.DataFrame:
    """
    Send the SAME business prompt to Claude (Anthropic SDK) and DeepSeek
    (OpenAI-compatible SDK), read each provider's own usage fields, and price
    each with its own tariff. Returns a DataFrame (PROVIDERS_HEADER columns).

    Parameters
    ----------
    anthropic_client : anthropic.Anthropic
    deepseek_client  : openai.OpenAI   # built with base_url=DEEPSEEK_BASE_URL
    """
    rows = []
    for vendor, model_name, model_id in _PROVIDER_CALLS:
        t0 = time.time()
        if vendor == "Anthropic":
            r = anthropic_client.messages.create(
                model=model_id, max_tokens=256,
                messages=[{"role": "user", "content": _BUSINESS_PROMPT}],
            )
            inp, out = r.usage.input_tokens, r.usage.output_tokens
        else:  # DeepSeek via OpenAI-compatible Chat Completions API
            r = deepseek_client.chat.completions.create(
                model=model_id, max_tokens=256,
                messages=[{"role": "user", "content": _BUSINESS_PROMPT}],
            )
            inp, out = r.usage.prompt_tokens, r.usage.completion_tokens
        rows.append({
            "provider": vendor,
            "model": model_name,
            "input_tokens": inp,
            "output_tokens": out,
            "usd_cost": provider_usd_cost(model_name, inp, out),
            "latency_s": round(time.time() - t0, 2),
        })
    return pd.DataFrame(rows, columns=PROVIDERS_HEADER)
