"""Design-level ZKML circuit review checklist (not a vulnerability study).

The repository does not inspect an EZKL/Halo2 production circuit or construct
an accepted forged proof. The five items below are questions for a future,
compiler- and model-specific audit. The V-I Python example is pedagogical only.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CircuitReviewItem:
    item_id: str
    title: str
    review_question: str
    potential_failure_if_unaddressed: str
    design_checks: list[str]
    relevant_operations: list[str]
    audit_status: str = "NOT_AUDITED_IN_THIS_REPOSITORY"
    circuit_exploit_tested: bool = False


CHECKLIST = [
    CircuitReviewItem(
        item_id="V-I",
        title="Range and representation constraints",
        review_question=(
            "For every bounded integer or quantized wire, does the circuit constrain "
            "the intended signed/unsigned range and its field-to-integer encoding?"
        ),
        potential_failure_if_unaddressed=(
            "If the intended range or encoding is not enforced, field elements may "
            "represent values outside the application's integer semantics. Whether "
            "that affects soundness depends on the actual circuit relation."
        ),
        design_checks=[
            "Document the field-to-integer mapping, bit width, signedness, and overflow behavior.",
            "Use backend-appropriate range-check or lookup constraints and test boundary values.",
            "Inspect compiled constraints; a Python example is not evidence of a circuit exploit.",
        ],
        relevant_operations=["bounded activations", "quantized arithmetic", "lookup-based nonlinearities"],
    ),
    CircuitReviewItem(
        item_id="V-II",
        title="Tie-breaking and output semantics",
        review_question=(
            "If the public output is an index or ordered set, are ties and other boundary "
            "cases defined and is the circuit consistent with that definition?"
        ),
        potential_failure_if_unaddressed=(
            "Unspecified tie-breaking can make outputs implementation-dependent. Multiple "
            "valid internal witnesses alone do not imply unsoundness if the public output "
            "still satisfies the intended relation."
        ),
        design_checks=[
            "Specify deterministic or set-valued semantics for ArgMax/TopK, including ties.",
            "Constrain the public index/set to satisfy the selected semantics.",
            "Test equal logits, near ties, and boundary values against a reference implementation.",
        ],
        relevant_operations=["ArgMax", "TopK", "sorting", "threshold decisions"],
    ),
    CircuitReviewItem(
        item_id="V-III",
        title="Completeness of layer relations",
        review_question=(
            "Does the proof relation constrain every intermediate value needed to establish "
            "the prescribed model's input/output computation?"
        ),
        potential_failure_if_unaddressed=(
            "An omitted or weakly linked relation can permit witnesses that do not represent "
            "the intended graph; this is a review concern, not a finding about a specific backend."
        ),
        design_checks=[
            "Trace each public output dependency through all required layers and residual paths.",
            "Check that intermediate values are constrained by the intended layer relation.",
            "Compare circuit outputs with a trusted reference on adversarial and boundary inputs.",
        ],
        relevant_operations=["linear layers", "activations", "residual connections", "normalization"],
    ),
    CircuitReviewItem(
        item_id="V-IV",
        title="Quantization configuration and semantics",
        review_question=(
            "Are scale, zero point, rounding, signedness, clipping, and overflow rules fixed "
            "to the authorized model/configuration and reflected in the circuit?"
        ),
        potential_failure_if_unaddressed=(
            "A mismatch between the intended and proved quantized function may change outputs; "
            "no such mismatch has been demonstrated here."
        ),
        design_checks=[
            "Bind quantization parameters and configuration version to the authorized model.",
            "Specify exact rounding, clipping, and overflow behavior.",
            "Test the circuit against the same quantized reference implementation.",
        ],
        relevant_operations=["quantized linear/convolution layers", "requantization", "lookup approximations"],
    ),
    CircuitReviewItem(
        item_id="V-V",
        title="Model and version binding",
        review_question=(
            "Does the statement bind the weights and model version used by the circuit to "
            "the authorized model identifier or commitment?"
        ),
        potential_failure_if_unaddressed=(
            "If weights are supplied dynamically but not bound, a proof may concern a "
            "different model. If weights are fixed in the circuit, the circuit/version "
            "identifier still needs to be tied to the protocol's authorized model."
        ),
        design_checks=[
            "Bind public or committed weights to the registered model/version.",
            "If weights are private, constrain their commitment opening in the proof relation.",
            "Test model-version changes and commitment mismatch cases.",
        ],
        relevant_operations=["weight loading", "model commitments", "model-version registry"],
    ),
]

SOUNDNESS_TARGET = (
    "For the specified model, input encoding, and inference semantics, an accepted proof "
    "must imply that the public output satisfies the intended relation."
)


def illustrate_under_range_constraint() -> dict[str, Any]:
    """Show a range mismatch in ordinary Python; this is not a ZK exploit."""
    cases = [(-50.0, 300), (30.0, 0), (100.0, 300), (200.0, 0)]
    rows = []
    for value, injected in cases:
        expected = int(min(255.0, max(0.0, value)))
        candidate = int(injected)
        rows.append({
            "input": value,
            "intended_clamped_value": expected,
            "arbitrary_python_value": candidate,
            "different": candidate != expected,
        })
    return {
        "example_id": "V-I-ILLUSTRATION-001",
        "item_id": "V-I",
        "illustrative_only": True,
        "actual_zk_circuit_built": False,
        "actual_proof_generated_or_verified": False,
        "proof_status": "NOT_TESTED",
        "rows": rows,
        "conclusion": (
            "Shows that an ordinary Python value can differ from a clamped example; "
            "it does not show that a ZK circuit accepts an out-of-range value."
        ),
    }


def build_results() -> dict[str, Any]:
    illustration = illustrate_under_range_constraint()
    return {
        "scope": (
            "Design-level review checklist only. No compiler-specific circuit audit, "
            "proof forgery, or production exploit test was performed."
        ),
        "soundness_target": SOUNDNESS_TARGET,
        "checklist": [asdict(item) for item in CHECKLIST],
        "illustrations": [illustration],
        "rq2_answer": (
            "Five conditional design-review areas are listed for a future ZKML audit. "
            "They are not experimentally verified vulnerability classes or exploit findings."
        ),
    }


def main() -> dict[str, Any]:
    output = Path(__file__).parent / "results" / "zkml_taxonomy.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    results = build_results()
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    print("ZKML design-review checklist (not a circuit audit)")
    for item in CHECKLIST:
        print(f"  [{item.item_id}] {item.title}")
    print("Circuit-level exploit tested: no")
    print("Results saved:", output)
    return results


if __name__ == "__main__":
    main()
