# Stage B5.2 Preregistration: Phi/FES-to-C12 Near-Threshold Signal Robustness and Decomposition Audit

## Purpose

Stage B5.2 is a diagnostic robustness and decomposition audit of the Stage B5.1 Phi/FES-to-C12 near-threshold signal.

B5.2 does not reinterpret B5.1 as a confirmatory positive. B5.1 remains:

```text
near-threshold, directionally consistent, but not confirmatory under the preregistered gate.
```

B5.2 asks whether the B5.1 signal is robust, specific, and decomposable, or whether it is explained by event-space mismatch, contrast-switch effects, degree/null behavior, temporal instability, or weak exploratory drift.

## Frozen B5.1 Baseline

B5.1 showed that all three primary Phi/FES event classes had a consistent directional C12(1,2) advantage over shifted controls, random-event controls, C8 contrast, and degree-matched null means.

However, B5.1 did not pass the confirmatory gate because:

- FDR was narrowly missed: `q = 0.055944` against `q <= 0.05`
- late-window stability did not pass
- degree-null p-value did not pass

## Fixed Primary Event Classes

B5.2 keeps the same primary Phi/FES event set:

1. `hybrid_phi_sign_switch`
2. `hybrid_fes_phase_transition`
3. `hybrid_cluster_transition`

## Fixed Secondary and Contrast Event Classes

Secondary Phi references:

1. `chapter7_phi_clean_sign_switch`
2. `chapter7_h_zero_crossing`

Contrast switch classes:

1. `chapter7_dphi_sign_switch`
2. `chapter7_d2phi_curvature_switch`
3. `chapter7_deps_sign_switch`

## Fixed Topologies and Controls

- Primary topology: `C12(1,2)`
- Topology contrast: `C8(1)`
- Event controls: time-shifted and random-event controls
- Null controls: degree-matched directed random graphs preserving node count and directed edge count

## Fixed Endpoint

The primary diagnostic endpoint remains:

```text
bounded_differentiated_recovery
```

The component readouts are:

- D12 recovery
- D24 recovery
- D12/D24 recovery improvement
- bounded non-runaway behavior
- non-collapsed differentiation
- late-window stability
- post-event readout score

## B5.2 Diagnostic Items

### 1. Gate-Failure Decomposition

Report which components of the B5.1 gate failed:

- FDR
- late-window stability
- degree-null p-value
- C8 contrast
- contrast-switch specificity

### 2. Component-Level Endpoint Report

Report the component readouts for each endogenous C12(1,2) event class.

### 3. Temporal Profile Audit

Decompose event-conditioned recovery into early, mid, and late event-position windows.

This tests whether the B5.1 signal is better interpreted as persistent closure or transient transition-like recovery.

### 4. Degree-Null Robustness

Increase degree-matched null repetitions and report whether the C12 advantage survives null variability.

### 5. Directional Concordance Across Primary Phi/FES Events

Report whether all three primary Phi/FES event classes point in the same C12-positive direction for:

- effect vs time-shifted controls
- effect vs random-event controls
- effect vs C8
- effect vs degree-matched null mean

This is secondary evidence only and is not treated as primary confirmation.

### 6. Contrast-Switch Specificity

Report whether `dphi`, `d2phi`, and `deps` switch classes reproduce the primary Phi/FES pattern.

### 7. Event-Space Normalization and Count-Matched Contrast Audit

Following Pasquale's concern, B5.2 freezes the following event-space normalization variants before execution:

1. `raw_full_range`
   - the original B5.1 event-space comparison

2. `primary_interval_only`
   - for each primary Phi/FES event class, restrict secondary/reference and contrast events to the same numeric task-index interval as that primary class
   - do not downsample

3. `primary_interval_count_matched`
   - restrict secondary/reference and contrast events to the same numeric task-index interval as the corresponding primary class
   - downsample without replacement to the corresponding primary event count when enough events are available
   - if fewer events are available, use all available events and mark the match as incomplete

For all variants, report failed or weakened outcomes as well as outcomes that preserve the C12 signal.

### 8. Impulse-Budget and Density Reporting

For each normalization row, report:

- task-index interval
- available event count
- sampled event count
- mean seed strength
- total impulse budget
- whether event-count matching was complete

Impulse budgets are not tuned after outcomes are inspected.

### 9. Phi Definition Separation

Keep the two Phi definitions separated:

- recursive hybrid phi for FES event-level switching
- Chapter 7 PCA / rank-Gaussianized `phi_clean` for the Chapter 7 reference layer

Do not merge them into a single ambiguous Phi claim.

## FDR Family Sensitivity

B5.2 reports FDR sensitivity for documented families:

1. all endogenous C12 rows
2. primary Phi/FES rows only
3. primary Phi/FES plus secondary Phi-reference rows
4. contrast-switch rows only

The primary interpretation remains tied to the B5.1 all-endogenous C12 family unless explicitly stated otherwise.

## Guardrails

B5.2 must:

- keep B5.1 non-confirmatory
- keep the FDR threshold fixed at `q <= 0.05`
- keep the primary event set fixed
- keep the C12(1,2) topology definition fixed
- keep C8 and degree-matched null controls
- keep contrast-switch controls
- report all predefined normalization variants
- report failed or weakened normalization outcomes
- avoid choosing the best normalization variant after seeing outcomes

## Possible Conclusions

B5.2 must end with one of the following interpretations:

1. B5.1 near-threshold signal is robust enough to justify a stricter replication test.
2. B5.1 signal is weak or unstable and should remain exploratory.
3. B5.1 signal appears driven by transient transition-like recovery rather than stable carrier closure.
4. B5.1 signal is not topology-specific beyond degree-matched nulls.
5. B5.1 signal is not Phi/FES-specific because contrast switches reproduce the same pattern.
6. B5.1 signal is explained by event-density, task-coverage, or event-space mismatch.

## Planned Command

```bash
python3 scripts/test_Stage_B5_2_phi_fes_to_c12_robustness.py \
  --input-root /Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction \
  --output-dir reports \
  --n-runs 400 \
  --n-null-graphs 120 \
  --n-null-runs 25 \
  --temporal-runs 240 \
  --normalization-runs 240 \
  --steps 240 \
  --seed 20260609
```
