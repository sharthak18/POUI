# Towards an AI-Native Blockchain Framework

This repository contains an **analytical feasibility study** of a Proof of Useful Intelligence (PoUI) trust score, a ZKML design checklist, post-quantum cryptography (PQC) parameter-size scenarios, interface-contract sketches, and an IEEE conference-style manuscript. It is **not** a deployed blockchain, a consensus implementation, a production ZKML audit, or a local ML-DSA/ML-KEM benchmark.

Authors currently listed in the manuscript: **Md. Mehedi Hasan**, **Asraful Islam Sharthak**, and **Prof. Dr. Md. Abdul Based**. Confirm that every listed author has agreed to authorship and that the author order, affiliation, and contribution statements meet the chosen venue's policy before submission.

`AI_Native_Blockchain_Research_Proposal.docx` is the earlier, broader proposal. Its projected work and claims are aspirational. The README and companion artifacts describe the narrower scope of this repository; `paper/main.tex` remains a draft and still needs the author edits listed in `SUBMISSION_CHECKLIST.md` before submission.

## Repository map

```
├── simulation/            # Trust-score model, sampled observables, analysis scripts/results
├── zkml-analysis/         # Design-level soundness risks; no circuit exploit study
├── zkml-prototype/        # Tiny ONNX → EZKL local proof/verification smoke test
├── pqc-benchmarks/        # FIPS parameter sizes and illustrative payload scenarios
├── architecture/          # Interface-contract and byte-count design sketches
├── literature/            # Candidate bibliography register; not a PRISMA review
├── paper/                 # IEEE-style manuscript, bibliography, and figure generators
├── protocol_spec.md       # Future-protocol sketch and explicit security boundary
├── reference.md           # Candidate literature catalogue requiring verification
└── SUBMISSION_CHECKLIST.md
```

## What the artifacts measure

### PoUI trust-score model

The score is

\[
T_t=\alpha A_t^2 e^{-\lambda L_t}+\beta\ln U_t-\gamma S_t.
\]

The Monte Carlo samples accuracy and latency proxies for 100 nodes over 1,000 epochs (70 honest, 15 high-latency, 15 malicious). It does **not** execute a neural network, model a network topology, or implement consensus. Every active node participates every epoch, so `U_t = 1` throughout; availability failures and the uptime term are not exercised. A malicious report below the audit threshold is independently slashed with probability 0.35; the model assumes no honest false positives.

Reproduce the checked-in results with:

```bash
python3 -m pip install numpy
python3 simulation/run_simulation.py
python3 simulation/run_multiseed.py
python3 simulation/formal_analysis.py
python3 simulation/sensitivity_analysis.py
```

The independent-audit calculations are conditional on their stated assumptions. In particular, the formal script computes `E[exp(-lambda L)]` for the simulator's floored-normal latency law; it does not substitute `exp(-lambda E[L])` for that expectation.

### Toy exclusion-rule comparison

```bash
python3 -m pip install numpy matplotlib
python3 simulation/compare_pos_poui.py
```

This compares two deliberately simplified toy rules, **not PoUI against Ethereum or a representative PoS protocol**. In the vote model, the 0.02 removal probability applies only after a malicious validator is selected for the 10-member committee; it is not a 0.02 per-node-per-epoch probability. Any ratio between the two models is descriptive of those particular assumptions, not a general consensus speedup or security result.

### ZKML materials

`zkml-analysis/zkml_taxonomy.py` lists five design-level circuit-review questions and possible checks. Its V-I Python example is a pedagogical illustration only: it does not construct a ZK circuit, run a prover/verifier, or demonstrate an exploit. The checklist is not an audited or experimentally validated vulnerability study.

The separate smoke test builds a deterministic 2×2 `Gemm → ReLU` ONNX model and runs EZKL setup, proving, and verification:

```bash
python3 -m pip install --target zkml-prototype/.deps ezkl==23.0.5 onnx==1.16.2
PYTHONPATH=zkml-prototype/.deps python3 zkml-prototype/run_tiny_mlp.py
```

This is a local toolchain smoke test, not a general ZKML performance/security evaluation. It uses a locally generated test SRS, which must not be used for deployment. The tested EZKL/KZG proof configuration is not established as post-quantum.

### PQC parameter sizing

```bash
python3 pqc-benchmarks/pqc_benchmark.py
```

FIPS/RFC parameter lengths are used in a simplified scenario with one signature per validator per block. Registered public keys are not counted as repeated block payload; ZK proofs, transaction framing, and networking are excluded. The script does not time any cryptographic primitive. Signature aggregation and hardware acceleration are research options, not implemented or measured reductions.

### Architecture sketches

```bash
python3 architecture/codesign_analysis.py
```

The four interface contracts, candidate cross-layer properties, and payload arithmetic are design artifacts, not a running stack. The illustrative 100-validator payload keeps all 100 proof payloads even in the signature-only aggregation scenario; Merkle/committee payload is not computed because its format is unspecified.

### Literature catalogue (not PRISMA)

```bash
python3 literature/prisma_slr.py
python3 paper/generate_prisma.py
```

The legacy script names are retained, but these commands only summarize the manually maintained candidate bibliography and generate an inventory graphic. Search queries/results, dates, deduplication records, full-text screening, and exclusion decisions are **not** present. The 60 entries are not verified as a set and must not be presented as a completed PRISMA systematic review. Verify every source against its primary publication before citing it.

## Figures and manuscript

Install `numpy` and `matplotlib`, then regenerate the figures from the checked-in result data:

```bash
python3 -m pip install numpy matplotlib
python3 paper/generate_figures.py
```

The taxonomy generator writes `paper/figures/fig_zkml_taxonomy.jpg`, matching the manuscript's include path. The PQC plot reads `pqc-benchmarks/results/pqc_benchmark_results.json`; regenerate that JSON first if scheme parameters change. The literature inventory graphic is explicitly marked **not a PRISMA flow**.

`paper/main.tex` is the manuscript source. A LaTeX installation is required to compile it; no current PDF is committed. The exact page limit, template, double-blind rules, artifact policy, and submission eligibility must be checked against the selected conference CFP. The repository's submission checklist is not a substitute for that venue-specific review.

## Current reference results

- Seed 42: 15/15 malicious nodes excluded; mean exclusion epoch 2.53; no honest nodes excluded under the zero-false-positive model.
- Ten seeds: all 15 malicious nodes excluded in each run; mean of per-seed means 3.12 epochs (sample standard deviation 0.71), compared with the independent geometric model's `1/0.35 ≈ 2.86` epochs.
- The comparison script's stored vote-model outcome is a toy-model result only; do not report it as a PoS benchmark.
- EZKL smoke test: one tiny model only; timings are machine-specific and its SRS is for local testing only.
- PQC: parameter sizing and scenario arithmetic only; no local PQC primitive benchmark.

## Submission hygiene

Before public distribution, verify all references and author details, compile the final manuscript with the chosen conference template, and ensure figures/results are regenerated from the final sources. **No `LICENSE` file is currently included**, despite earlier repository text describing an MIT license; settle and add the appropriate license before redistributing the code.
