# PoUI Protocol Sketch and Security Boundary

This document makes the protocol assumed by the paper explicit. It is a design
specification for a future prototype, not an implemented consensus protocol.

## Epoch flow

1. **Register.** A validator registers a stake, an ML-DSA verification key,
   an ML-KEM encryption key, and a commitment to the approved model parameters.
   The registry rejects duplicate keys and records the model/version identifier.
2. **Challenge.** At epoch `t`, the coordinator derives a public epoch nonce
   from the finalized prior block. It samples a hidden, labelled probe from a
   committed dataset, encrypts the probe to the validator's registered ML-KEM
   key, and records a commitment to `(epoch, validator, probe_nonce, model_id)`.
3. **Inference and proof.** The validator decrypts the probe, evaluates the
   committed model, and produces `(y, pi)`. The circuit must bind the probe
   commitment, model commitment, quantization parameters, and output `y`.
4. **Submit.** The validator signs `H(epoch || model_id || probe_commitment ||
   y || H(pi))` with ML-DSA and submits the signed tuple before its deadline.
5. **Verify and score.** Verifiers check the epoch binding, ML-DSA signature,
   model/version commitment, proof, and score against the hidden label. The
   protocol updates `T_t` only after these checks. A verifier rejection creates
   auditable evidence; it must not automatically be treated as malicious if a
   dispute/availability rule applies.
6. **Select and finalize.** A separately specified, stake-aware consensus
   protocol uses only active validators. The current paper does not define a
   leader-election or finality algorithm.

## Required bindings

The submitted proof must bind all of the following:

- model weights/version through a collision-resistant commitment;
- challenge instance, epoch, validator identity, and anti-replay nonce;
- quantization scale and zero point;
- every inference layer and the output-selection/tie-breaking rule;
- public output `y` and the proof hash signed by the validator.

## Threat-model boundary

The paper's theorems cover low-quality reports that remain below the audit
threshold, independent audit events, and an exclusion rule where one valid
slash is enough. They do not establish resistance to free identity creation,
adaptive model substitution, collusion, coordinator bias, availability attacks,
eclipse attacks, side channels, or a malicious trusted setup.

## Deployment requirements

- Use a ceremony-derived or otherwise publicly trusted SRS, never the local
  test SRS used by `zkml-prototype/run_tiny_mlp.py`.
- Define an appeal/dispute process and false-positive policy before automatic
  slashing is enabled.
- Use asynchronous commit--reveal rather than requiring proof generation in a
  short BFT slot.
- Benchmark the selected model, circuit, proving backend, PQC implementation,
  hardware, and network separately before choosing a deadline or block budget.
