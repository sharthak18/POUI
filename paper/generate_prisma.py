"""Generate a bibliography-register status figure (legacy filename).

This script deliberately does not draw a PRISMA flow diagram: the repository
has no auditable database-search exports or screening decisions. Run
``python3 literature/prisma_slr.py`` first to regenerate the candidate register.
The output is an inventory/status graphic and must not be cited as PRISMA evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "literature" / "prisma_database.json"
OUTPUT = Path(__file__).resolve().parent / "figures" / "fig_literature_register_status.png"


def main() -> None:
    if not REGISTER.exists():
        raise SystemExit(
            f"Missing {REGISTER}; run `python3 literature/prisma_slr.py` first."
        )

    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    stats = data["stats"]
    by_domain = stats["by_domain"]
    labels = list(by_domain)
    values = [by_domain[label] for label in labels]

    bg = "#0d1117"
    panel = "#161b22"
    text = "#c9d1d9"
    colors = ["#3fb950", "#58a6ff", "#d29922", "#bc8cff", "#79c0ff"][:len(labels)]

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=bg)
    ax.set_facecolor(panel)
    bars = ax.barh(labels, values, color=colors, edgecolor="#30363d")
    ax.invert_yaxis()
    ax.set_xlabel("Candidate records (not screening/inclusion counts)", color=text)
    ax.tick_params(colors=text)
    ax.xaxis.label.set_color(text)
    for spine in ax.spines.values():
        spine.set_color("#30363d")
    ax.grid(axis="x", linestyle="--", alpha=0.25, color=text)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        ax.text(value + 0.2, bar.get_y() + bar.get_height() / 2, str(value),
                va="center", color=text)

    fig.suptitle(
        "Curated Literature Candidate Register — NOT A PRISMA Flow",
        color="#e6edf3", fontsize=14, fontweight="bold", y=0.96,
    )
    fig.text(
        0.5, 0.87,
        f"{stats['candidate_record_count']} candidate records; "
        f"{stats['source_verified_count']} source-verified; "
        "search exports, deduplication, and screening logs are not present.",
        ha="center", color=text, fontsize=9,
    )
    fig.text(
        0.5, 0.04,
        "Inventory only. Verify every record and document a reproducible search before claiming a systematic review.",
        ha="center", color="#f85149", fontsize=9, fontweight="bold",
    )
    fig.tight_layout(rect=[0.03, 0.10, 0.97, 0.82])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=150, bbox_inches="tight", facecolor=bg)
    plt.close(fig)
    print("Candidate-register status figure saved:", OUTPUT)


if __name__ == "__main__":
    main()
