# Conference Submission Readiness Checklist

This checklist describes the current repository state, not a promise of acceptance. A specific venue and CFP are required to determine fit, format, page limit, and review policy.

## Repository artifacts currently present

- [x] IEEE-style LaTeX source is present at `paper/main.tex`.
- [x] A fixed-seed and ten-seed trust-score simulation are present.
- [x] Closed-form audit and false-positive sensitivity scripts are present.
- [x] A tiny local EZKL proof-pipeline smoke-test script and result record are present.
- [x] Claims are intended to be scoped as an analytical feasibility study, not a deployed protocol.
- [x] The PQC section is intended to report parameter sizes and modeled payloads, not local PQC primitive timings.
- [x] The ZKML material is intended as a design checklist, not a circuit exploit study.

## Must be completed before submission

- [ ] Re-run the analytical and simulation scripts from a clean environment and check that manuscript numbers match generated outputs.
- [ ] Confirm the trust-score latency expectation uses `E[exp(-lambda L)]` for the stated latency law, not `exp(-lambda E[L])`.
- [ ] Keep the uptime limitation explicit: no missed epochs/outages are modeled, so `U_t=1` in the Monte Carlo.
- [ ] Ensure the toy selected-member vote comparison is never described as an Ethereum or representative PoS benchmark.
- [ ] Keep the Python V-I illustration clearly distinct from a real circuit-level exploit; remove any output/figure/text that implies a proof was forged or accepted.
- [ ] Scope quantum-resistance statements to ML-DSA/ML-KEM interfaces. The tested EZKL/KZG configuration is not established as post-quantum.
- [ ] Verify every citation, DOI, author, venue, year, and URL against primary sources. The 60-entry catalogue is not a completed PRISMA review; do not claim one without search and screening records.
- [ ] Proofread the final manuscript, resolve all TODOs, verify figure paths and values, and compile the final PDF with the target conference template.
- [ ] Confirm venue fit, page limit (including references), template, deadlines, double-blind requirements, originality/copyright policy, and artifact rules against the chosen CFP.
- [ ] Confirm all authors consent to the author list/order and meet the conference's authorship criteria; confirm affiliation and acknowledgements are accurate.
- [ ] Add the appropriate `LICENSE` file before public redistribution; none is currently present.

## Manuscript edits intentionally deferred

`paper/main.tex` was restored to its original `HEAD` version and was not edited in this change, as requested. Reconcile it with the updated scripts and figures before submission:

- [ ] Abstract and Introduction (around lines 30, 45–62): fix the prose/typos; describe the simulation as a proxy model; change “verifies” to “is consistent with”; remove unsupported Sybil/challenge-resistance language; state that the 0.02 toy-vote probability is conditional on selection.
- [ ] Threat Model and Trust Score (around lines 76–84, 132–145): describe latency as floored, not truncated; remove the claim that identity duplication is not rewarded as a Sybil result; remove obsolete PQC timing-spreadsheet claims; clarify that the one-shot maximizer is not truthfulness.
- [ ] Geometric exclusion result (around lines 156–166): repair the definition of the first-slash epoch and the proof wording.
- [ ] Simulation (around lines 184–187): label the false-positive calculation as per-validator under independent trials; refresh the toy vote result from `simulation/results/comparison_pos_poui.json` (15/15 excluded, mean 405.8 epochs among excluded in the current seed-42 run); remove any speedup conclusion.
- [ ] ZKML section and figure caption (around lines 193–220): present V-I–V as a review checklist, not universal necessary/sufficient conditions or an exploit study; state correct tie-breaking and range/quantization semantics.
- [ ] PQC section (around lines 227–249): remove stale TODO/timing claims; rename “Q-safe” to a precise standardization/status heading; describe 242,000 bytes as the unaggregated signature-only subtotal; explain ML-KEM as key encapsulation used with authenticated key registration and an AEAD channel.
- [ ] Layer Contracts, limitations, and conclusion (around lines 254–285): align captions with the regenerated figures; bind signatures to the full canonical transcript; do not slash solely on a verifier rejection; distinguish HNDL confidentiality risk from signature-authentication risk; frame all interfaces as proposed, not validated deployment evidence.
- [ ] Compile the edited manuscript and verify every cited source, figure, value, TODO, and venue-specific requirement before submission.

## Artifact handling

- [ ] Do not upload local EZKL dependencies, the locally generated test SRS, proving key, or other local proving artifacts unless explicitly required and safely prepared.
- [ ] Include reproducibility instructions and exact dependency versions for any artifact submitted to the venue.

## Defensible positioning

Describe the work as an **analytical feasibility study with a reproducible trust-score simulation, a tiny ZKML proof-pipeline smoke test, and PQC parameter/payload sizing**.

Do not describe it as a deployed AI-native blockchain, a complete consensus protocol, a general Sybil-resistance proof, a repeated-game Nash result, a production ZKML audit/exploit, a local PQC performance benchmark, a completed PRISMA systematic review, or a comparison against Ethereum proof of stake.
