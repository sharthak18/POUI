"""FIPS parameter sizes and illustrative PoUI message-payload arithmetic.

This legacy-named script is not a PQC performance benchmark. It reports
published parameter lengths for Ed25519, ECDSA-P256, ML-DSA, and ML-KEM, then
calculates message bytes under explicit validator-count assumptions. It does
not time cryptographic operations or implement signature aggregation.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SignatureProfile:
    name: str
    family: str
    public_key_bytes: int
    secret_key_bytes: int
    signature_bytes: int
    standard: str
    pqc_standardized: bool
    nist_category: int | None
    encoding_note: str


@dataclass(frozen=True)
class KemProfile:
    name: str
    public_key_bytes: int
    secret_key_bytes: int
    ciphertext_bytes: int
    shared_secret_bytes: int
    standard: str
    nist_category: int


SIGNATURE_SCHEMES: dict[str, SignatureProfile] = {
    "Ed25519": SignatureProfile(
        name="Ed25519",
        family="classical signature",
        public_key_bytes=32,
        secret_key_bytes=32,
        signature_bytes=64,
        standard="RFC 8032",
        pqc_standardized=False,
        nist_category=None,
        encoding_note="32-byte seed, 32-byte public key, 64-byte signature.",
    ),
    "ECDSA-P256": SignatureProfile(
        name="ECDSA-P256",
        family="classical signature",
        public_key_bytes=64,
        secret_key_bytes=32,
        signature_bytes=64,
        standard="FIPS 186-5",
        pqc_standardized=False,
        nist_category=None,
        encoding_note=(
            "Raw x||y public-key coordinates and fixed-width r||s signature; "
            "wire encodings such as SEC1/DER have different lengths."
        ),
    ),
    "ML-DSA-44": SignatureProfile(
        name="ML-DSA-44",
        family="post-quantum signature",
        public_key_bytes=1_312,
        secret_key_bytes=2_560,
        signature_bytes=2_420,
        standard="FIPS 204, Table 2",
        pqc_standardized=True,
        nist_category=2,
        encoding_note="FIPS 204 parameter-set lengths.",
    ),
    "ML-DSA-65": SignatureProfile(
        name="ML-DSA-65",
        family="post-quantum signature",
        public_key_bytes=1_952,
        secret_key_bytes=4_032,
        signature_bytes=3_309,
        standard="FIPS 204, Table 2",
        pqc_standardized=True,
        nist_category=3,
        encoding_note="FIPS 204 parameter-set lengths.",
    ),
    "ML-DSA-87": SignatureProfile(
        name="ML-DSA-87",
        family="post-quantum signature",
        public_key_bytes=2_592,
        secret_key_bytes=4_896,
        signature_bytes=4_627,
        standard="FIPS 204, Table 2",
        pqc_standardized=True,
        nist_category=5,
        encoding_note="FIPS 204 parameter-set lengths.",
    ),
}

KEM_SCHEMES: dict[str, KemProfile] = {
    "ML-KEM-512": KemProfile(
        name="ML-KEM-512",
        public_key_bytes=800,
        secret_key_bytes=1_632,
        ciphertext_bytes=768,
        shared_secret_bytes=32,
        standard="FIPS 203, Table 2",
        nist_category=1,
    ),
    "ML-KEM-768": KemProfile(
        name="ML-KEM-768",
        public_key_bytes=1_184,
        secret_key_bytes=2_400,
        ciphertext_bytes=1_088,
        shared_secret_bytes=32,
        standard="FIPS 203, Table 2",
        nist_category=3,
    ),
    "ML-KEM-1024": KemProfile(
        name="ML-KEM-1024",
        public_key_bytes=1_568,
        secret_key_bytes=3_168,
        ciphertext_bytes=1_568,
        shared_secret_bytes=32,
        standard="FIPS 203, Table 2",
        nist_category=5,
    ),
}

VALIDATOR_COUNTS = (100,)
TPS_CONTEXTS = (100, 1_000, 10_000)

MITIGATIONS = [
    {
        "id": "M1",
        "name": "Signature aggregation",
        "status": "not implemented or measured",
        "note": (
            "Standard ML-DSA does not itself specify generic signature aggregation. "
            "A concrete, reviewed protocol and signer-accountability format are required."
        ),
    },
    {
        "id": "M2",
        "name": "Hybrid migration",
        "status": "design option only",
        "note": (
            "A hybrid transition may protect selected interfaces, but retaining a "
            "classical authentication path is not full post-quantum authentication."
        ),
    },
    {
        "id": "M3",
        "name": "Off-chain signature batching or Merkle commitments",
        "status": "not computed",
        "note": (
            "Payload depends on the attestation, audit-data availability, and proof format; "
            "no size reduction is assumed."
        ),
    },
    {
        "id": "M4",
        "name": "Hardware acceleration",
        "status": "not evaluated",
        "note": "Performance requires a specified implementation, device, and measurement procedure.",
    },
]


def signature_payload_scenarios(
    schemes: dict[str, SignatureProfile] = SIGNATURE_SCHEMES,
    validator_counts: tuple[int, ...] = VALIDATOR_COUNTS,
    tps_contexts: tuple[int, ...] = TPS_CONTEXTS,
) -> list[dict[str, Any]]:
    """Calculate signature bytes under one-signature-per-validator-per-block."""
    baseline_bytes = schemes["Ed25519"].signature_bytes
    rows = []
    for tps in tps_contexts:
        for n_validators in validator_counts:
            for key, scheme in schemes.items():
                total = n_validators * scheme.signature_bytes
                rows.append({
                    "scheme_key": key,
                    "scheme_name": scheme.name,
                    "tps_context_only": tps,
                    "validator_count": n_validators,
                    "signatures_per_validator_per_block": 1,
                    "total_signature_bytes_per_block": total,
                    "registered_public_keys_repeated_per_block": False,
                    "transaction_framing_included": False,
                    "zk_proofs_included": False,
                    "bytes_per_block_change_with_tps_under_this_model": False,
                    "amplification_vs_ed25519": round(
                        scheme.signature_bytes / baseline_bytes, 4
                    ),
                })
    return rows


def build_results() -> dict[str, Any]:
    return {
        "scope": (
            "FIPS/RFC parameter lengths and illustrative signature-payload arithmetic only. "
            "No ML-DSA, ML-KEM, Ed25519, or ECDSA operation is timed by this script. "
            "Proofs, transaction framing, networking, and aggregation are excluded."
        ),
        "payload_assumptions": {
            "signatures_per_validator_per_block": 1,
            "validator_public_keys_repeated_per_block": False,
            "zkml_proofs_included": False,
            "transaction_framing_included": False,
            "networking_included": False,
            "tps_changes_signature_bytes_per_block": False,
            "signature_aggregation_implemented": False,
        },
        "signature_schemes": {
            key: asdict(profile) for key, profile in SIGNATURE_SCHEMES.items()
        },
        "kem_schemes": {
            key: asdict(profile) for key, profile in KEM_SCHEMES.items()
        },
        "signature_payload_scenarios": signature_payload_scenarios(),
        "mitigations": MITIGATIONS,
        "parameter_examples_not_deployment_recommendations": {
            "signature_profile": "ML-DSA-44",
            "key_encapsulation_profile": "ML-KEM-768",
            "note": "Parameter selection requires protocol-specific security and workload analysis.",
        },
    }


def main() -> dict[str, Any]:
    output = Path(__file__).parent / "results" / "pqc_benchmark_results.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    results = build_results()
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    print("PQC parameter sizes and payload arithmetic (no primitive benchmarking)")
    print(f"{'Scheme':<14} {'PK (B)':>9} {'SK (B)':>9} {'Signature (B)':>15} {'PQC standardized':>18}")
    for profile in SIGNATURE_SCHEMES.values():
        print(
            f"{profile.name:<14} {profile.public_key_bytes:>9} "
            f"{profile.secret_key_bytes:>9} {profile.signature_bytes:>15} "
            f"{str(profile.pqc_standardized):>18}"
        )
    print("Results saved:", output)
    return results


if __name__ == "__main__":
    main()
