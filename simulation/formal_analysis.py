"""Reproduce the numerical quantities used in the trust-score paper.

This script evaluates closed-form expressions from the manuscript. It does
not prove protocol security, solve a repeated validator game, or require a
statistics package. The formal assumptions and proofs are in paper/main.tex.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Parameters:
    alpha: float = 0.5
    beta: float = 0.3
    gamma: float = 1.5
    lambda_decay: float = 0.01
    audit_probability: float = 0.35
    audit_threshold: float = 0.40
    exclusion_threshold: float = -0.5
    uptime_floor: float = 1e-9
    mean_latency_ms: float = 50.0
    honest_accuracy_mean: float = 0.90
    honest_accuracy_std: float = 0.05
    malicious_accuracy_min: float = 0.10
    malicious_accuracy_max: float = 0.30


def uniform_second_moment(low: float, high: float) -> float:
    return (low * low + low * high + high * high) / 3.0


def analyse(params: Parameters) -> dict:
    """Return the manuscript's model quantities under its stated assumptions."""
    latency_factor = math.exp(-params.lambda_decay * params.mean_latency_ms)
    honest_second_moment = (
        params.honest_accuracy_mean ** 2 + params.honest_accuracy_std ** 2
    )
    malicious_second_moment = uniform_second_moment(
        params.malicious_accuracy_min, params.malicious_accuracy_max
    )
    expected_gap = (
        params.alpha * latency_factor
        * (honest_second_moment - malicious_second_moment)
        + params.gamma * params.audit_probability
    )
    probability_by_epoch_8 = 1.0 - (1.0 - params.audit_probability) ** 8

    return {
        "scope": {
            "description": (
                "Closed-form calculations for the independent-audit model in "
                "paper/main.tex; not a repeated-game or network-security proof."
            ),
            "assumptions": [
                "Accuracy and latency are independent.",
                "Fabricated reports remain below the audit threshold.",
                "Each eligible audit is an independent Bernoulli trial.",
                "One slash excludes a node only when U_t = 1 and gamma > alpha - tau_excl.",
            ],
        },
        "parameters": asdict(params),
        "theorem_1_bounds": {
            "upper_bound": params.alpha,
            "lower_bound_with_uptime_floor": round(
                params.beta * math.log(params.uptime_floor) - params.gamma, 6
            ),
        },
        "theorem_2_expected_score_gap": {
            "latency_factor_at_mean_latency": round(latency_factor, 6),
            "honest_accuracy_second_moment_unclipped": round(honest_second_moment, 6),
            "fabricator_accuracy_second_moment": round(malicious_second_moment, 6),
            "expected_gap": round(expected_gap, 6),
            "interpretation": "Positive only for the stated low-quality-fabricator audit model.",
        },
        "theorem_3_one_shot_maximizer": {
            "maximizer": 1.0,
            "interpretation": (
                "The score-only, one-shot objective is maximized at A=1; this is not "
                "a repeated-game Nash equilibrium or proof that an implementation can "
                "measure true accuracy."
            ),
        },
        "theorem_4_geometric_exclusion": {
            "expected_epochs": round(1.0 / params.audit_probability, 6),
            "probability_excluded_by_epoch_8": round(probability_by_epoch_8, 6),
            "distribution": "Geometric(p=0.35) on epochs {1, 2, ...}",
        },
    }


def main() -> None:
    results = analyse(Parameters())
    output = Path(__file__).parent / "results" / "formal_analysis.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    geometric = results["theorem_4_geometric_exclusion"]
    print("Trust-score analytical quantities written to", output)
    print("Expected exclusion epoch:", geometric["expected_epochs"])
    print("P(excluded by epoch 8):", geometric["probability_excluded_by_epoch_8"])


if __name__ == "__main__":
    main()
