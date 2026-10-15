"""Reproduce the numerical quantities used in the trust-score paper.

The latency and honest-accuracy moments match the simulation's sampling rules:
L = max(1 ms, Normal(50 ms, 10 ms)) and A_H = clip(Normal(0.90, 0.05), 0, 1).
This script evaluates closed-form quantities; it does not prove protocol security,
model a repeated validator game, or require a statistics package.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path


def normal_cdf(value: float) -> float:
    """Standard-normal CDF using only the Python standard library."""
    return 0.5 * math.erfc(-value / math.sqrt(2.0))


def normal_pdf(value: float) -> float:
    """Standard-normal density."""
    return math.exp(-0.5 * value * value) / math.sqrt(2.0 * math.pi)


def uniform_second_moment(low: float, high: float) -> float:
    """Return E[X^2] for X uniform on [low, high]."""
    return (low * low + low * high + high * high) / 3.0


def clipped_normal_second_moment(
    mean: float, std: float, lower: float = 0.0, upper: float = 1.0
) -> float:
    """Return E[clip(X, lower, upper)^2] for X ~ Normal(mean, std^2)."""
    if std <= 0 or lower >= upper:
        raise ValueError("std must be positive and lower must be below upper")

    a = (lower - mean) / std
    b = (upper - mean) / std
    probability_between = normal_cdf(b) - normal_cdf(a)
    first_standard_moment = normal_pdf(a) - normal_pdf(b)
    second_standard_moment = (
        probability_between + a * normal_pdf(a) - b * normal_pdf(b)
    )
    middle = (
        mean * mean * probability_between
        + 2.0 * mean * std * first_standard_moment
        + std * std * second_standard_moment
    )
    return (
        lower * lower * normal_cdf(a)
        + middle
        + upper * upper * (1.0 - normal_cdf(b))
    )


def floored_normal_exponential_moment(
    decay: float, mean: float, std: float, floor: float
) -> float:
    """Return E[exp(-decay * max(floor, X))], X ~ Normal(mean, std^2).

    The below-floor probability is a point mass at ``floor``. The remaining
    integral is the exponentially tilted normal tail. This is not the plug-in
    approximation exp(-decay * E[max(floor, X)]).
    """
    if decay < 0 or std <= 0:
        raise ValueError("decay must be nonnegative and std must be positive")
    below_floor_z = (floor - mean) / std
    tilted_tail_z = (mean - decay * std * std - floor) / std
    below_floor = math.exp(-decay * floor) * normal_cdf(below_floor_z)
    above_floor = (
        math.exp(-decay * mean + 0.5 * decay * decay * std * std)
        * normal_cdf(tilted_tail_z)
    )
    return below_floor + above_floor


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
    latency_std_ms: float = 10.0
    latency_floor_ms: float = 1.0
    honest_accuracy_mean: float = 0.90
    honest_accuracy_std: float = 0.05
    malicious_accuracy_min: float = 0.10
    malicious_accuracy_max: float = 0.30


def analyse(params: Parameters) -> dict:
    """Return manuscript quantities under explicit, simulation-matched inputs."""
    if not (0.0 < params.audit_probability <= 1.0):
        raise ValueError("audit_probability must be in (0, 1]")
    if not (0.0 <= params.malicious_accuracy_min < params.malicious_accuracy_max <= 1.0):
        raise ValueError("malicious accuracy bounds must satisfy 0 <= min < max <= 1")
    if params.malicious_accuracy_max >= params.audit_threshold:
        raise ValueError("the expected-gap calculation assumes every fabricator is below the audit threshold")
    if not (0.0 < params.uptime_floor <= 1.0):
        raise ValueError("uptime_floor must be in (0, 1]")
    if min(params.alpha, params.beta, params.gamma) <= 0.0:
        raise ValueError("score weights alpha, beta, and gamma must be positive")
    if params.lambda_decay < 0.0:
        raise ValueError("lambda_decay must be nonnegative")

    latency_factor = floored_normal_exponential_moment(
        params.lambda_decay,
        params.mean_latency_ms,
        params.latency_std_ms,
        params.latency_floor_ms,
    )
    plug_in_latency_factor = math.exp(
        -params.lambda_decay * max(params.latency_floor_ms, params.mean_latency_ms)
    )
    honest_second_moment = clipped_normal_second_moment(
        params.honest_accuracy_mean, params.honest_accuracy_std
    )
    malicious_second_moment = uniform_second_moment(
        params.malicious_accuracy_min, params.malicious_accuracy_max
    )
    expected_gap = (
        params.alpha * latency_factor
        * (honest_second_moment - malicious_second_moment)
        + params.gamma * params.audit_probability
    )
    # Keep the paper's illustrative A_F=0.39 scenario separate from the
    # simulation's uniform [0.10, 0.30] adversary distribution.
    illustrative_probe_accuracy = 0.39
    illustrative_probe_gap = (
        params.alpha * latency_factor
        * (honest_second_moment - illustrative_probe_accuracy ** 2)
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
                "Honest accuracy is a Normal draw clipped to [0, 1].",
                "Latency is a Normal draw floored at the configured minimum, matching the simulator.",
                "The numerical fabricator distribution is Uniform[0.10, 0.30], below the audit threshold.",
                "Each eligible audit is an independent Bernoulli trial.",
                "U_t = 1; no uptime variation is modeled in the Monte Carlo simulation.",
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
            "latency_model": (
                "L = max(latency_floor_ms, Normal(mean_latency_ms, latency_std_ms^2))"
            ),
            "expected_latency_attenuation": round(latency_factor, 9),
            "plug_in_at_mean_latency_not_used_as_expectation": round(
                plug_in_latency_factor, 9
            ),
            "honest_accuracy_second_moment_clipped": round(honest_second_moment, 9),
            "honest_accuracy_second_moment_unclipped": round(
                params.honest_accuracy_mean ** 2 + params.honest_accuracy_std ** 2, 9
            ),
            "fabricator_accuracy_second_moment_uniform": round(malicious_second_moment, 9),
            "expected_gap_uniform_fabricator": round(expected_gap, 9),
            "illustrative_constant_probe_accuracy": illustrative_probe_accuracy,
            "expected_gap_constant_probe": round(illustrative_probe_gap, 9),
            "interpretation": (
                "Positive for the stated low-quality-fabricator audit model only; "
                "the one-shot audit rule is not a deployed accuracy oracle."
            ),
        },
        "theorem_3_one_shot_score_input_maximizer": {
            "maximizer": 1.0,
            "interpretation": (
                "For the toy objective, a freely chosen score input has no cost or "
                "truthfulness constraint, so the maximum is attained at A=1. This is "
                "a direct property of that objective, not an incentive-compatibility "
                "result, a claim about true accuracy, or a repeated-game equilibrium."
            ),
        },
        "theorem_4_geometric_exclusion": {
            "expected_epochs": round(1.0 / params.audit_probability, 6),
            "probability_excluded_by_epoch_8": round(probability_by_epoch_8, 6),
            "distribution": f"Geometric(p={params.audit_probability:g}) on epochs {{1, 2, ...}}",
        },
    }


def main() -> None:
    results = analyse(Parameters())
    output = Path(__file__).parent / "results" / "formal_analysis.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    geometric = results["theorem_4_geometric_exclusion"]
    score_gap = results["theorem_2_expected_score_gap"]
    print("Trust-score analytical quantities written to", output)
    print("Expected exclusion epoch:", geometric["expected_epochs"])
    print("E[exp(-lambda L)] under the floored-normal model:", score_gap["expected_latency_attenuation"])
    print("Expected gap for Uniform[0.10, 0.30] fabricator:", score_gap["expected_gap_uniform_fabricator"])
    print("P(excluded by epoch 8):", geometric["probability_excluded_by_epoch_8"])


if __name__ == "__main__":
    main()
