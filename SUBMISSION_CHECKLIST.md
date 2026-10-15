# Conference Submission Readiness Checklist

This checklist describes the repository state, not a promise of acceptance. A specific venue and CFP are required to determine fit, format, page limit, and review policy.

## Repository work completed

- [x] Manuscript wording now matches the simulation: availability is not sampled and $U_t=1$ throughout.
- [x] The toy committee-vote probability is explicitly conditional on selection and is not presented as a representative PoS result.
- [x] The score maximization result is described as one-agent and does not claim truthful reporting or a repeated-game equilibrium.
- [x] The first-slash epoch and geometric exclusion argument are stated explicitly.
- [x] The ZKML material is framed as a design-review checklist, including range, tie-breaking, layer linkage, quantization, and model-binding questions.
- [x] PQC content is described as standards-based sizing, not a local primitive benchmark; the signature subtotal and ML-KEM/AEAD roles are clarified.
- [x] Protocol text binds signatures to a context-specific transcript and does not treat verifier rejection alone as slashing evidence.
- [x] The architecture and ZKML figures were redesigned to remove overlapping labels and placeholder text.
- [x] The accidentally tracked local Python virtual environment was removed from version control and added to `.gitignore`.
- [x] LaTeX auxiliary files are ignored.

## Must be completed before submission

- [ ] Re-run the analytical and simulation scripts from a clean environment and verify that manuscript numbers match generated outputs.
- [ ] Compile the final manuscript with the selected venue's template; check figure placement, citations, page count, and PDF metadata.
- [ ] Verify every citation, DOI, author, venue, year, and URL against the primary publication. The 60-entry catalogue is not a completed PRISMA review; do not claim one without search and screening records.
- [ ] Confirm venue fit, page limit (including references), template, deadlines, double-blind rules, originality/copyright policy, and artifact rules against the chosen CFP.
- [ ] Confirm all authors consent to the author list/order and meet the venue's authorship criteria; confirm affiliation and acknowledgements.
- [ ] Choose and add an appropriate `LICENSE` before public redistribution.
- [ ] Include reproducibility instructions and exact dependency versions for any submitted artifact. Do not upload local EZKL dependencies, test SRS, proving keys, or other local proving artifacts unless required and safely prepared.

## Defensible positioning

Describe the work as an **analytical feasibility study with a reproducible trust-score simulation, a tiny ZKML proof-pipeline smoke test, and PQC parameter/payload sizing**.

Do not describe it as a deployed AI-native blockchain, a complete consensus protocol, a general Sybil-resistance proof, a repeated-game Nash result, a production ZKML audit/exploit, a local PQC performance benchmark, a completed PRISMA systematic review, or a comparison against Ethereum proof of stake.
