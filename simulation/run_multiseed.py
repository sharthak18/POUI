"""Reproduce the ten-seed Monte Carlo summary reported in paper/main.tex."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from run_simulation import run_simulation


SEEDS = (42, 7, 13, 99, 123, 256, 512, 1024, 2024, 31415)


def main() -> None:
    runs = []
    for seed in SEEDS:
        result = run_simulation(seed=seed, verbose=False)
        exclusion = result["malicious_exclusion"]
        honest = result["honest_node_scores"]
        runs.append({
            "seed": seed,
            "malicious_excluded": exclusion["total_excluded"],
            "malicious_total": exclusion["total_malicious"],
            "mean_exclusion_epoch": exclusion["mean_epoch_to_exclusion"],
            "honest_excluded": honest["excluded_count"],
        })

    means = [run["mean_exclusion_epoch"] for run in runs]
    summary = {
        "scope": (
            "Monte Carlo of sampled observables under the independent-audit model; "
            "not a trained-model, ZKML, network, or proof-of-stake evaluation."
        ),
        "seeds": list(SEEDS),
        "runs": runs,
        "summary": {
            "all_malicious_excluded_each_seed": all(
                run["malicious_excluded"] == run["malicious_total"] for run in runs
            ),
            "total_honest_excluded": sum(run["honest_excluded"] for run in runs),
            "mean_of_per_seed_means": round(float(np.mean(means)), 4),
            "sample_std_of_per_seed_means": round(float(np.std(means, ddof=1)), 4),
            "geometric_prediction": round(1 / 0.35, 4),
        },
    }
    output = Path(__file__).parent / "results" / "multiseed_summary.json"
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary["summary"], indent=2))
    print("Wrote", output)


if __name__ == "__main__":
    main()
