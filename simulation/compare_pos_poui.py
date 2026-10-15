"""Compare two deliberately simplified malicious-node exclusion rules.

The first data series is replayed from the PoUI independent-audit simulation.
The second is a toy selected-member vote model: a malicious validator has a
0.02 exclusion probability only after selection for a 10-member committee.
This is not a comparison with Ethereum or a representative proof-of-stake
protocol, and the two models use different assumptions.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

SEED = 42
N_NODES = 100
N_EPOCHS = 1_000
N_HONEST = 70
N_HIGH_LATENCY = 15
N_MALICIOUS = 15
COMMITTEE_SIZE = 10
P_EXCLUDE_GIVEN_SELECTED = 0.02


def simulate_selected_member_vote(rng: np.random.Generator) -> dict[str, Any]:
    """Run the explicitly toy vote rule with equal initial stake."""
    active = np.ones(N_NODES, dtype=bool)
    node_types = np.array(
        ["honest"] * N_HONEST
        + ["high_latency"] * N_HIGH_LATENCY
        + ["malicious"] * N_MALICIOUS
    )
    exclusion_epoch: dict[int, int] = {}

    for epoch in range(1, N_EPOCHS + 1):
        active_indices = np.flatnonzero(active)
        committee_size = min(COMMITTEE_SIZE, len(active_indices))
        selected = rng.choice(active_indices, size=committee_size, replace=False)
        for node_id in selected:
            if node_types[node_id] == "malicious" and rng.random() < P_EXCLUDE_GIVEN_SELECTED:
                active[node_id] = False
                exclusion_epoch[int(node_id)] = epoch
    times = list(exclusion_epoch.values())
    return {
        "rule": "toy selected-member vote",
        "representative_pos_protocol": False,
        "validator_count": N_NODES,
        "committee_size": COMMITTEE_SIZE,
        "malicious_validator_count": N_MALICIOUS,
        "conditional_exclusion_probability": P_EXCLUDE_GIVEN_SELECTED,
        "exclusion_probability_is_conditional_on_selection": True,
        "epochs": N_EPOCHS,
        "excluded_count": len(times),
        "exclusion_rate_pct": round(100.0 * len(times) / N_MALICIOUS, 2),
        "mean_exclusion_epoch_among_excluded": round(float(np.mean(times)), 2) if times else None,
        "median_exclusion_epoch_among_excluded": round(float(np.median(times)), 2) if times else None,
        "exclusion_epoch_by_node": exclusion_epoch,
    }


def load_poui_results() -> dict[str, Any]:
    path = Path(__file__).parent / "results" / "simulation_raw_results.json"
    return json.loads(path.read_text(encoding="utf-8"))


def make_figure(poui: dict[str, Any], vote: dict[str, Any]) -> Path:
    import matplotlib.pyplot as plt

    bg = "#0d1117"
    panel = "#161b22"
    edge = "#30363d"
    text = "#c9d1d9"
    text_hi = "#e6edf3"
    green = "#3fb950"
    red = "#f85149"
    grid = "#21262d"
    plt.rcParams.update({
        "figure.facecolor": bg,
        "axes.facecolor": panel,
        "axes.edgecolor": edge,
        "axes.labelcolor": text,
        "axes.titlecolor": text_hi,
        "xtick.color": "#8b949e",
        "ytick.color": "#8b949e",
        "text.color": text,
        "grid.color": grid,
        "grid.linestyle": "--",
        "grid.alpha": 0.6,
    })

    def cumulative_curve(exclusion_epochs: list[int]) -> list[int]:
        counts = Counter(exclusion_epochs)
        total = 0
        result = []
        for epoch in range(1, N_EPOCHS + 1):
            total += counts[epoch]
            result.append(total)
        return result

    poui_times = [int(v) for v in poui["malicious_exclusion"]["epoch_breakdown"].values()]
    vote_times = list(vote["exclusion_epoch_by_node"].values())
    poui_curve = cumulative_curve(poui_times)
    vote_curve = cumulative_curve(vote_times)

    fig, (ax_curve, ax_note) = plt.subplots(
        1, 2, figsize=(13, 5.5), gridspec_kw={"width_ratios": [1.5, 1]},
    )
    fig.suptitle(
        "Two toy malicious-node exclusion rules\n"
        "Descriptive single-run illustration — not a PoUI-vs-PoS performance comparison",
        color=text_hi, fontsize=13, fontweight="bold",
    )
    epochs = np.arange(1, N_EPOCHS + 1)
    ax_curve.step(epochs, poui_curve, where="post", color=green, linewidth=2,
                  label="Independent-audit score model")
    ax_curve.step(epochs, vote_curve, where="post", color=red, linewidth=2,
                  linestyle="--", label="Selected-member vote toy model")
    ax_curve.axhline(N_MALICIOUS, color="#8b949e", linestyle=":", linewidth=1)
    ax_curve.set_xlim(1, N_EPOCHS)
    ax_curve.set_ylim(0, N_MALICIOUS + 1)
    ax_curve.set_xlabel("Epoch")
    ax_curve.set_ylabel("Cumulative excluded malicious nodes")
    ax_curve.set_title("Seed 42; N=100; 15 simulated malicious nodes")
    ax_curve.grid(True)
    ax_curve.legend(fontsize=8, loc="lower right")

    ax_note.axis("off")
    p_mean = poui["malicious_exclusion"]["mean_epoch_to_exclusion"]
    v_mean = vote["mean_exclusion_epoch_among_excluded"]
    note = (
        "ASSUMPTIONS\n"
        "• Audit model: independent p=0.35 each eligible low-quality epoch.\n"
        "• Vote toy: p=0.02 only after selection for a 10-member committee.\n"
        "• Both use N=100 and the same simulated node counts.\n\n"
        "SEED-42 OUTCOMES\n"
        f"• Audit model: {poui['malicious_exclusion']['total_excluded']}/15 excluded; "
        f"mean epoch {p_mean}.\n"
        f"• Vote toy: {vote['excluded_count']}/15 excluded; "
        f"mean among excluded {v_mean if v_mean is not None else 'N/A'}.\n\n"
        "These are different toy rules, not matched consensus protocols. "
        "The result does not establish a general speedup, security advantage, "
        "or claim about Ethereum/production PoS."
    )
    ax_note.text(0.03, 0.95, note, va="top", ha="left", color=text, fontsize=9.5,
                 linespacing=1.45, wrap=True)
    ax_note.set_title("Model scope and outcome", color=text_hi, fontweight="bold")

    fig.tight_layout(rect=[0, 0, 1, 0.88])
    output = Path(__file__).parent.parent / "paper" / "figures" / "fig_comparison_pos_poui.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=150, bbox_inches="tight", facecolor=bg)
    plt.close(fig)
    return output


def run_comparison() -> dict[str, Any]:
    poui = load_poui_results()
    rng = np.random.default_rng(SEED)
    vote = simulate_selected_member_vote(rng)
    figure = make_figure(poui, vote)

    results = {
        "scope": (
            "Single-seed comparison of two deliberately simplified exclusion rules. "
            "Not a representative PoS benchmark, protocol security result, or general speedup claim."
        ),
        "seed": SEED,
        "poui_independent_audit_model": {
            "rule": "Trust-score threshold with independent eligible-epoch audit probability 0.35",
            "excluded_count": poui["malicious_exclusion"]["total_excluded"],
            "malicious_node_count": poui["malicious_exclusion"]["total_malicious"],
            "mean_exclusion_epoch": poui["malicious_exclusion"]["mean_epoch_to_exclusion"],
        },
        "selected_member_vote_toy_model": vote,
        "figure": str(figure.relative_to(Path(__file__).parent.parent)),
    }
    output = Path(__file__).parent / "results" / "comparison_pos_poui.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print("Toy-rule comparison figure saved:", figure)
    print("Toy-rule comparison data saved:", output)
    print("No ratio or representative PoS performance claim is calculated.")
    return results


if __name__ == "__main__":
    run_comparison()
