"""Proposed PoUI/ZKML/PQC interface contracts and payload arithmetic.

These are design sketches only. No consensus stack, signature aggregation,
network, or production circuit is implemented or measured here. The byte-count
scenarios use explicit illustrative inputs and must not be read as deployment
capacity results.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class InterfaceContract:
    contract_id: str
    caller_layer: str
    callee_layer: str
    operation: str
    preconditions: list[str]
    intended_success_conditions: list[str]
    failure_modes: list[str]
    input_types: dict[str, str]
    output_types: dict[str, str]
    illustrative_latency_budget_ms: float
    illustrative_message_budget_bytes: int


CONTRACTS = [
    InterfaceContract(
        contract_id="IC-01",
        caller_layer="L1 consensus",
        callee_layer="L2 ZKML",
        operation="RequestInferenceProof",
        preconditions=[
            "The epoch challenge and authorized model/version are identified.",
            "The input encoding, model commitment, quantization semantics, and public statement are specified.",
            "The validator is authorized to produce a proof for this challenge.",
        ],
        intended_success_conditions=[
            "The prover returns an output and proof for the requested statement.",
            "A verifier accepts only if the implemented relation and its model/input bindings are sound.",
            "The example 5,000 ms and 200,000-byte limits are planning inputs, not measured guarantees.",
        ],
        failure_modes=[
            "Proof generation exceeds the selected deadline.",
            "The circuit omits or misbinds part of the intended model, input, or inference relation.",
            "Witness generation exhausts memory or fails on the selected hardware.",
        ],
        input_types={
            "epoch": "uint64",
            "validator_id": "bytes32",
            "challenge_commitment": "bytes32",
            "model_version_or_commitment": "bytes32",
            "input_or_input_commitment": "bytes or bytes32",
        },
        output_types={
            "output": "model-defined bytes",
            "proof": "bytes; size depends on circuit and proof system",
            "proof_hash": "bytes32",
        },
        illustrative_latency_budget_ms=5_000.0,
        illustrative_message_budget_bytes=200_000,
    ),
    InterfaceContract(
        contract_id="IC-02",
        caller_layer="L2 ZKML",
        callee_layer="L1 consensus",
        operation="SubmitOutputAndEvidence",
        preconditions=[
            "The submission identifies the epoch, validator, challenge, model version, output, and proof hash.",
            "The signature key is registered and valid for the submission epoch.",
            "The submission arrives before the protocol-defined deadline.",
        ],
        intended_success_conditions=[
            "The receiver verifies the signature, proof, challenge/model bindings, and output before accepting the result.",
            "Any score or slash decision follows a separately specified evidence, false-positive, and appeal policy.",
        ],
        failure_modes=[
            "Late or malformed submission is rejected under the stated protocol rules.",
            "Invalid signature or proof is rejected; rejection alone does not establish malicious intent.",
            "Missing appeal or evidence policy can make a penalty unfair or unauditable.",
        ],
        input_types={
            "epoch": "uint64",
            "validator_id": "bytes32",
            "challenge_commitment": "bytes32",
            "model_version_or_commitment": "bytes32",
            "output": "model-defined bytes",
            "proof": "bytes",
            "signature": "bytes (domain-separated submission digest)",
        },
        output_types={
            "accepted": "bool",
            "verification_reason": "protocol-defined enum or bytes",
            "score_update": "protocol-defined value; not implemented here",
        },
        illustrative_latency_budget_ms=100.0,
        illustrative_message_budget_bytes=10_000,
    ),
    InterfaceContract(
        contract_id="IC-03",
        caller_layer="L1 consensus",
        callee_layer="L3 PQC",
        operation="RegisterAndRotateValidatorKeys",
        preconditions=[
            "The consensus identity and its authority to register keys are authenticated.",
            "The ML-DSA and, if confidential probe delivery is required, ML-KEM public keys are bound to that identity.",
            "The protocol defines key versions, validity intervals, revocation, and rotation overlap.",
        ],
        intended_success_conditions=[
            "Public-key identifiers and versions are recorded against the authorized consensus identity.",
            "Probe encryption uses an authenticated binding to the intended validator; ML-KEM alone does not authenticate that binding.",
        ],
        failure_modes=[
            "An unauthenticated or misbound registration permits key substitution.",
            "Duplicate, revoked, or stale key versions are accepted or rejected inconsistently.",
            "A key-rotation gap makes an otherwise timely submission unverifiable.",
        ],
        input_types={
            "validator_id": "bytes32",
            "mldsa_public_key": "bytes (scheme-specific length)",
            "mlkem_public_key": "bytes (scheme-specific length; optional if KEM is unused)",
            "key_version_and_validity": "protocol-defined structure",
            "registration_authorization": "protocol-defined signature or proof",
        },
        output_types={
            "registry_record": "identity, public-key identifiers, and validity metadata",
            "registration_status": "accepted or rejected with reason",
        },
        illustrative_latency_budget_ms=500.0,
        illustrative_message_budget_bytes=5_000,
    ),
    InterfaceContract(
        contract_id="IC-04",
        caller_layer="L2 ZKML",
        callee_layer="L3 PQC",
        operation="SignSubmissionDigest",
        preconditions=[
            "The validator holds the secret key corresponding to a registered ML-DSA public key.",
            "The digest format is domain-separated and includes epoch, validator identity, challenge, model version, output hash, and proof hash.",
            "The selected key version is valid for the submission under the rotation policy.",
        ],
        intended_success_conditions=[
            "The signature verifies against the registered key for exactly the specified digest and key version.",
            "Signing attributes a message to the key holder; it does not establish circuit soundness or truth of the inference.",
        ],
        failure_modes=[
            "Wrong, expired, or revoked key version produces a rejected signature.",
            "A digest that omits protocol context permits replay or cross-context substitution.",
            "Signing or verification exceeds its separately measured protocol budget.",
        ],
        input_types={
            "domain_separated_digest": "bytes32 or protocol-defined digest",
            "key_version": "protocol-defined identifier",
            "secret_key": "scheme-specific private-key representation",
        },
        output_types={
            "signature": "bytes (size depends on the selected signature scheme)",
        },
        illustrative_latency_budget_ms=1.0,
        illustrative_message_budget_bytes=2_500,
    ),
]


CODESIGN_INTERACTIONS: dict[str, Any] = {
    "scope": "Candidate design observations; not experimentally validated properties.",
    "candidate_cross_layer_properties": [
        {
            "id": "CP-1",
            "name": "Context-bound signed transcript",
            "description": (
                "A domain-separated signature can bind a validator key to an explicitly "
                "encoded epoch, challenge, model version, output, and proof hash. This "
                "provides message integrity/attribution only if all fields are included "
                "and checked; it does not establish that the circuit is sound."
            ),
        },
        {
            "id": "CP-2",
            "name": "PQC protection at selected interfaces",
            "description": (
                "ML-DSA and ML-KEM are standardized post-quantum signature and KEM schemes. "
                "Using them at selected interfaces does not make a stack post-quantum: "
                "the tested EZKL/KZG configuration and the consensus layer are not shown "
                "to have post-quantum security in this repository."
            ),
        },
        {
            "id": "CP-3",
            "name": "Auditable penalty evidence (design goal)",
            "description": (
                "A protocol could retain the signed submission and a verifier's reason "
                "for rejection. This repository implements neither evidence recording, "
                "dispute resolution, nor slashing; a signature alone does not establish "
                "that a penalty is correct or fair."
            ),
        },
    ],
    "design_failure_modes": [
        {
            "id": "FM-CD-1",
            "name": "Proof deadline mismatch",
            "description": (
                "If proof generation is on a consensus-critical path, proving time, "
                "verification time, and network delay must fit the chosen deadline. "
                "The example timing budget is not measured or validated here."
            ),
            "mitigation_options": [
                "Measure on target hardware and model size.",
                "Consider pipelining or asynchronous proof submission with explicit finality rules.",
            ],
        },
        {
            "id": "FM-CD-2",
            "name": "Key-version mismatch during rotation",
            "description": (
                "A proof may be ready when the signing key version is no longer accepted. "
                "No rotation protocol or overlap window is implemented here."
            ),
            "mitigation_options": [
                "Specify key validity intervals, revocation, and a bounded overlap policy.",
                "Test submissions spanning epoch and rotation boundaries.",
            ],
        },
        {
            "id": "FM-CD-3",
            "name": "Enrollment authentication gap",
            "description": (
                "A validator's PQC public keys must be authenticated and bound to its "
                "consensus identity. ML-KEM does not authenticate a public key by itself; "
                "public keys and ciphertexts are not secret. Confidentiality of probes "
                "depends on correct, authenticated key establishment."
            ),
            "mitigation_options": [
                "Define authenticated enrollment and key rotation.",
                "State whether the threat model requires post-quantum or hybrid enrollment authentication.",
            ],
        },
        {
            "id": "FM-CD-4",
            "name": "Payload exceeds an unspecified budget",
            "description": (
                "In the illustrative N=100 scenario, one 200,000-byte proof and one "
                "2,420-byte ML-DSA-44 signature per validator total 20,242,000 bytes "
                "per block before framing. The protocol's actual size limit is not "
                "specified, so this is a payload calculation rather than a finding that "
                "a particular network overflows."
            ),
            "mitigation_options": [
                "Specify the block/message budget and proof submission format.",
                "Evaluate aggregation or off-chain proof availability only with a concrete, reviewed protocol.",
            ],
        },
    ],
    "combined_payload_scenario": {
        "status": "illustrative arithmetic; not measured",
        "validator_count": 100,
        "proof_bytes_per_validator": 200_000,
        "mldsa44_signature_bytes_per_validator": 2_420,
        "public_keys_repeated_per_block": False,
        "transaction_framing_included": False,
        "networking_included": False,
        "per_block_bytes_without_signature_aggregation": 20_242_000,
        "per_block_bytes_if_only_signatures_were_aggregated": 20_002_420,
        "signature_aggregation_implemented": False,
        "proof_payloads_retained_in_both_scenarios": True,
        "aggregation_format_specified": False,
    },
}


def run_codesign_analysis() -> dict[str, Any]:
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "scope": (
            "Proposed interface-contract sketches and explicit payload arithmetic. "
            "No integrated protocol, PQC operations, signature aggregation, or "
            "production ZKML circuit is implemented or benchmarked."
        ),
        "rq4_contracts": [asdict(contract) for contract in CONTRACTS],
        "rq5_analysis": CODESIGN_INTERACTIONS,
        "rq4_answer": (
            "Four proposed interface-contract sketches specify candidate inputs, "
            "success conditions, failure cases, and illustrative planning budgets."
        ),
        "rq5_answer": (
            "Three conditional design observations and four cross-layer failure "
            "scenarios are catalogued. They are not experimentally validated and "
            "do not establish end-to-end quantum safety, fair slashing, or measured "
            "aggregation gains."
        ),
    }
    out_path = output_dir / "codesign_analysis.json"
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    payload = CODESIGN_INTERACTIONS["combined_payload_scenario"]
    print("Proposed interface-contract sketches:", len(CONTRACTS))
    print("Illustrative payload without aggregation:", payload["per_block_bytes_without_signature_aggregation"], "bytes/block")
    print("Signature-only aggregation arithmetic:", payload["per_block_bytes_if_only_signatures_were_aggregated"], "bytes/block")
    print("Signature aggregation implemented: no")
    print("Results saved:", out_path)
    return result


if __name__ == "__main__":
    run_codesign_analysis()
