"""Sensitivity calculations for the independent-audit exclusion model.

The output quantifies how the audit probability changes exclusion time and why
false positives require a dispute policy when one slash is sufficient.
"""

from __future__ import annotations

import json
from pathlib import Path


AUDIT_PROBABILITIES = (0.10, 0.20, 0.35, 0.50, 0.75)
HORIZONS = (10, 100, 1_000)
FALSE_POSITIVE_RATES = (0.0, 1e-5, 1e-4, 1e-3)


def main() -> None:
    audit_rows = [
        {
            "audit_probability": p,
            "expected_exclusion_epochs": round(1 / p, 4),
            "probability_excluded_by_epoch_8": round(1 - (1 - p) ** 8, 6),
        }
        for p in AUDIT_PROBABILITIES
    ]
    false_positive_rows = [
        {
            "per_epoch_false_positive_rate": rate,
            "probability_of_at_least_one_false_slash": {
                str(horizon): round(1 - (1 - rate) ** horizon, 8) for horizon in HORIZONS
            },
        }
        for rate in FALSE_POSITIVE_RATES
    ]
    output = {
        "scope": (
            "Closed-form sensitivity calculations under independent epochs and the "
            "one-slash exclusion rule; not a network or adversarial simulation."
        ),
        "audit_probability_sweep": audit_rows,
        "false_positive_sweep": false_positive_rows,
        "interpretation": (
            "Higher audit probability reduces expected malicious exclusion time. With "
            "one-slash exclusion, even small false-positive rates accumulate over long "
            "horizons; a deployed protocol needs appeal, repeated-evidence, or calibrated "
            "slashing rules."
        ),
    }
    path = Path(__file__).parent / "results" / "sensitivity_analysis.json"
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    print("Wrote", path)


if __name__ == "__main__":
    main()
