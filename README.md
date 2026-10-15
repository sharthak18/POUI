# Towards an AI-Native Blockchain Framework

This repository contains simulation code, a ZKML circuit checklist, PQC sizing spreadsheets, and an IEEE conference-style manuscript on trust scoring for proof-of-useful-intelligence (PoUI) consensus. The paper is a **model and analysis**, not a deployed blockchain.

Authors: **Md. Mehedi Hasan**, **Asraful Islam Sharthak**, and **Prof. Dr. Md. Abdul Based**, Principal Investigator

---

## 📂 Repository Structure

The project is structured into modular research components:

```
├── simulation/            # PoUI Consensus Simulation & Theorems (RQ1)
│   ├── trust_score_model.py     # Trust Score mathematical implementation
│   ├── run_simulation.py        # 1,000-epoch simulation engine (N=100 nodes)
│   ├── compare_pos_poui.py      # Efficiency comparison of PoUI vs. PoS
│   ├── formal_analysis.py       # Formal bounds, Sybil-resistance, & Nash Eq. proofs
│   └── results/                 # JSON outputs of simulation runs
│
├── zkml-analysis/         # ZKML Underconstrained Circuit Taxonomy (RQ2)
│   ├── zkml_taxonomy.py         # Formulations of V-I through V-V vulnerability classes
│   └── results/                 # JSON output of the ZKML security taxonomy
│
├── pqc-benchmarks/        # Post-Quantum Cryptography (PQC) Benchmarking (RQ3)
│   └── results/                 # ML-DSA and ML-KEM network and sizing overhead benchmarks
│
├── architecture/          # Co-Design Interface Contracts & Failures (RQ4, RQ5)
│   └── codesign_analysis.py     # Co-design model, slots budgets, and overhead mitigations
│
├── literature/            # PRISMA 2020 Systematic Literature Review (SLR)
│   ├── prisma_slr.py            # Automated SLR database manager (60 papers included)
│   └── prisma_database.json     # Compiled database of literature review
│
└── paper/                 # IEEE TDSC Manuscript & Figure Generators
    ├── main.tex                 # LaTeX manuscript
    ├── references.bib           # BibTeX references
    ├── generate_figures.py      # Script generating key research figures
    ├── generate_prisma.py       # Script generating the PRISMA 2020 flowchart
    └── figures/                 # PNG outputs of generated figures
```

---

## 🚀 How to Run the Simulations

### 1. Prerequisite Packages
Install dependencies (principally NumPy, SciPy, Matplotlib):
```bash
pip install numpy scipy matplotlib
```

### 2. Run PoUI vs. PoS Comparison Simulation
Evaluate the performance and security bounds of the Proof of Useful Intelligence (PoUI) Trust Score against baseline Proof of Stake (PoS):
```bash
python3 simulation/compare_pos_poui.py
```
*Note:* The large speed-up in `compare_pos_poui.py` is against a **toy 2%-per-epoch governance vote**, not Ethereum-style proof of stake. The conference paper states this explicitly.

### 2a. Reproduce the paper's trust-score results
```bash
# Fixed-seed result used for the per-run summary (seed 42)
python3 simulation/run_simulation.py

# Ten-seed aggregate reported in the paper
python3 simulation/run_multiseed.py

# Closed-form quantities for the stated independent-audit model
python3 simulation/formal_analysis.py

# Audit-probability and false-positive sensitivity calculations
python3 simulation/sensitivity_analysis.py
```
The resulting JSON files distinguish analytical quantities from the sampled Monte Carlo. They are not evidence of a trained model, ZKML prover, deployed network, or live PoS comparison.

### 2b. Run the minimal ZKML proof-pipeline smoke test
```bash
# One-time local dependencies (installed under zkml-prototype/.deps)
python3 -m pip install --target zkml-prototype/.deps ezkl==23.0.5 onnx==1.16.2

# Deterministic Gemm(2×2) → ReLU ONNX model, then EZKL setup/prove/verify
PYTHONPATH=zkml-prototype/.deps python3 zkml-prototype/run_tiny_mlp.py
```
This creates [artifacts](zkml-prototype/artifacts/) and `zkml-prototype/results.json`. It is a local smoke test only: its model is intentionally tiny, timings are machine-specific, and its locally generated SRS must never be used in deployment.

### 3. Generate Paper Figures
To regenerate all research figures (Fig. 1-4 and PRISMA Flowchart) in the `paper/figures/` folder:
```bash
# Generate core research figures
python3 paper/generate_figures.py

# Generate PRISMA flow diagram
python3 paper/generate_prisma.py
```

### 4. Regenerate PRISMA Literature Database
To recompile the systematic review stats and update the PRISMA JSON database:
```bash
python3 literature/prisma_slr.py
```

---

## Summary of results (what the code actually measures)

### PoUI trust score
*   **Simulation:** $N=100$ (70 honest, 15 high-latency, 15 malicious), 1,000 epochs, seed 42. Accuracy/latency are **sampled distributions**, not a trained MobileNet.
*   **Exclusion:** 15/15 malicious on every one of 10 seeds; 0 honest excluded. Seed 42 mean epoch **2.53**; mean-of-means **3.12** (std 0.71) vs geometric $1/0.35\approx 2.86$.
*   **Sybil gap:** $\Delta=\alpha\phi_L(\mathbb{E}[A_H^2]-\mathbb{E}[A_F^2])+\gamma p$ under independent $A,L$ (not $e^{-\lambda\mathbb{E}[L]}$).
*   **One-shot maximizer:** unique at $A_t=1$ (not a repeated-game Nash theorem).
*   **Exclusion time:** geometric waiting time $M\sim\mathrm{Geo}(p=0.35)$, $\mathbb{E}[M]=1/p\approx 2.86$; sim mean $2.53$ on 15 nodes.
*   **vs ``PoS'':** toy vote with $p=0.02$/epoch (86.7% excluded, mean epoch 568). Do not report this as Ethereum PoS.

### ZKML checklist
Five underconstraint patterns (range, witness choice, missing layers, quantization slack, wrong-model commitment). Design requirements, **not** an EZKL/Halo2 exploit study.

### PQC sizing
ML-DSA / ML-KEM **parameter tables + published timings**, not a local liboqs benchmark. Aggregation to ~200 KB/block is an assumption, not a measured aggregator.

### Co-design
Interface contracts IC-01–IC-04 and failure modes (slot race, key-rotation desync, classical bootstrap, size overflow). Architecture notes, not a running node.

---

*This project is released under the MIT License.*
