# Conference Submission Checklist

## Completed in this repository

- [x] IEEE conference manuscript compiles from `paper/main.tex`.
- [x] The current PDF is five pages and has no unresolved citations or references.
- [x] Claims are scoped as an analytical feasibility study, not a deployed protocol.
- [x] Ten-seed trust-score summary is reproducible with `simulation/run_multiseed.py`.
- [x] Independent-audit calculations and sensitivity results are reproducible.
- [x] A minimal EZKL proof pipeline creates and verifies a proof locally.
- [x] Figures state requirements and risks rather than unsupported PoC or security claims.

## Must be checked against the chosen conference CFP

- [ ] Topic fit: accepts blockchain/security/AI systems analytical or prototype papers.
- [ ] Page limit: the compiled PDF is five pages; check whether references count.
- [ ] Template: replace `IEEEtran` only if the venue provides another template.
- [ ] Review model: remove author names, institution, acknowledgements, repository URL,
      and self-identifying metadata if the venue uses double-blind review.
- [ ] Copyright and originality: confirm the paper is not concurrently submitted and
      does not reuse text/figures that violate the venue's policy.
- [ ] Reference audit: open every cited DOI/URL and correct any inaccurate metadata.
- [ ] Artifact policy: upload source/code only if permitted; do not upload local EZKL
      dependencies, test SRS, proving key, or other ignored build artifacts.

## Recommended submission positioning

Describe the work as: **an analytical feasibility study with a reproducible
trust-score simulation and a minimal ZKML proof-pipeline validation**.

Do not describe it as a deployed AI-native blockchain, a complete consensus
protocol, a production ZKML audit, a PQC performance benchmark, or a comparison
against Ethereum proof of stake.
