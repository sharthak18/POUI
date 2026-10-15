# PoUI Protocol Sketch and Security Boundary

This document describes a possible protocol for a future prototype. It is a
design sketch, not an implemented consensus protocol or a validated security
construction. Every cryptographic and timing choice below requires a separate
specification and evaluation.

## Epoch flow (proposed)

1. **Register.** A validator registers a consensus identity, stake, an ML-DSA
   verification key, an optional ML-KEM public key, and an identifier or
   commitment for the authorized model/configuration. The protocol must
   authenticate the identity-to-key binding and define key versioning,
   revocation, and rotation; ML-KEM by itself does not authenticate a public
   key.
2. **Challenge.** At epoch `t`, a coordinator derives a nonce from a finalized
   prior block and selects a challenge input from a committed dataset. The
   validator may receive the input encrypted to its registered ML-KEM key, but
   the key and ciphertext must be authenticated and bound to the validator
   identity. Ground-truth labels must remain unavailable to the validator if
   they are used to score the response. The dataset, sampling method, label
   handling, privacy, and anti-replay rules are not specified here.
3. **Inference and proof.** The validator evaluates the authorized model and
   returns `(y, pi)`. A future circuit would need to bind the challenge input,
   model/version, quantization configuration, and output. This repository does
   not implement that binding or prove the circuit is sound.
4. **Submit.** The validator signs a domain-separated digest that includes the
   epoch, validator identity, challenge commitment, model/configuration
   version, output hash, and proof hash. The validator submits the signed tuple
   before the protocol-defined deadline.
5. **Verify and score.** Verifiers check the identity/key binding, signature,
   challenge and model bindings, proof, and scoring rule. The protocol must
   define false-positive handling, evidence retention, and appeal/dispute rules;
   a failed verification alone does not prove malicious intent.
6. **Select and finalize.** A separately specified consensus protocol selects
   validators and provides finality. The current study does not define leader
   election, stake economics, or finality.

## Candidate bindings to review

- model weights/version and inference configuration through a fixed circuit or
  a commitment that is checked by the proof;
- challenge instance, epoch, validator identity, and anti-replay nonce;
- quantization scale, zero point, rounding, signedness, and overflow semantics;
- all required layer relations and output-selection/tie-breaking semantics;
- public output `y` and proof hash in the signed submission digest.

These are design-review items, not a complete or sufficient circuit-audit
checklist.

## Threat-model boundary

The paper's mathematical results cover low-quality reports below the audit
threshold, independent audit events, and a per-epoch score rule under which one
valid slash is sufficient only for the stated parameter conditions. They do not
establish resistance to cost-free identity creation, adaptive reporting,
collusion, coordinator bias, availability attacks, eclipse attacks, side
channels, compromised key registration, or a malicious trusted setup.

## Deployment requirements

- Use a publicly trusted SRS ceremony or a setup-independent proof system, not
  the local test SRS used by `zkml-prototype/run_tiny_mlp.py`.
- Define an appeal/dispute process, false-positive policy, and evidence rules
  before enabling automatic slashing.
- Measure proving, verification, signing, message delivery, and finality on
  target hardware and workloads before choosing deadlines or block budgets.
  Pipelining or asynchronous proof submission may be considered, but requires
  explicit ordering, availability, and finality rules.
- Specify authenticated validator enrollment and key rotation. If confidential
  challenges are required, document the key-establishment and probe-label
  threat model.
