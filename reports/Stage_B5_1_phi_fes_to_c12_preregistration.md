# Stage B5.1 Preregistration: Direct Phi/FES-to-C12 Bridge Audit

## Status

Stage B5.1 is a new independently preregistered hypothesis. It is not a rescue or reinterpretation of B2, B3, B3.1, B3.2, B4, or B4.1.

## Background

The original motivation for this collaboration was the concern that IDPC's Phi definition might be circular: is Phi only an internally defined descriptor, or does it have predictive content outside the IDPC framework itself?

Previous Stage B audits tested adjacent routes, including unseeded autonomous C12(1,2), broad endogenous perturbations, mu-sector diagnostics, real-time cyclic temporal anchoring, and secondary folded-readout / alias diagnostics. None reached a confirmatory gate.

B5.1 returns to the core IDPC structure itself: Phi, FES, and the current D12RG C12(1,2) readout candidate.

## Main Question

Do IDPC Phi/FES switching events condition bounded differentiated recovery in the D12RG C12(1,2) readout topology?

## Event Definitions

B5.1 event definitions are fixed from the formal IDPC pipeline outputs already used in the existing tables and claims.

## Primary Phi/FES Event Classes

The primary event classes are tested separately and are not pooled for the main pass/fail decision:

1. `hybrid_phi_sign_switch`
2. `hybrid_fes_phase_transition`
3. `hybrid_cluster_transition`

A single primary event class may become a candidate if it passes the B5.1 primary gate after correction. A broader Phi/FES-family interpretation requires directionally consistent advantage across the primary Phi/FES event classes.

## Secondary Phi References

The following are secondary references:

1. `chapter7_phi_clean_sign_switch`
2. `chapter7_h_zero_crossing`

They do not define the primary B5.1 success criterion unless explicitly reported as secondary findings.

## Contrast Switch Classes

The contrast switch classes are:

1. `chapter7_dphi_sign_switch`
2. `chapter7_d2phi_curvature_switch`
3. `chapter7_deps_sign_switch`

These are included to test whether any observed effect is specific to Phi/FES switching rather than generic switching. Primary Phi/FES candidates and contrast switch classes are included in the same event-family correction set.

## Topologies And Nulls

- Primary topology: `C12(1,2)`
- Main contrast topology: `C8(1)`
- Null graph controls: degree-matched directed random/null graphs preserving node count and edge count

C12(1,2) is used here as the current D12RG core readout candidate, not as a claim that it is the final biologically plausible topology.

## Conditions

For each event class, compare:

1. endogenous event-conditioned C12(1,2)
2. time-shifted event-conditioned C12(1,2)
3. random-event-conditioned C12(1,2)
4. C8(1) under the same event schedule
5. degree-matched directed null graphs under the same event schedule

## Primary Endpoint

The primary endpoint is `bounded_differentiated_recovery`, operationalized as the B3 differentiated recovery score, which already combines event-conditioned readout improvement with differentiation and bounded non-runaway behavior.

D12 recovery and D24 recovery are reported as component readouts, not alternative primary endpoints.

## Fixed Gates

A primary Phi/FES event class is a B5.1 positive candidate only if all of the following hold:

1. endogenous C12(1,2) bounded differentiated recovery is greater than time-shifted C12(1,2)
2. endogenous C12(1,2) bounded differentiated recovery is greater than random-event C12(1,2)
3. the same pattern is not reproduced by C8(1)
4. degree-matched directed null graphs do not explain the effect
5. the primary Phi/FES event class outperforms or remains distinguishable from contrast switch classes
6. bounded non-runaway score is at least 0.70
7. non-collapsed differentiation score is at least 0.30
8. late-window stability is at least 0.70
9. the result survives FDR correction across the event-family correction set

## Correction Family

The FDR correction family includes all primary Phi/FES event classes, secondary Phi references, and contrast switch classes. Primary claims can only be made for primary Phi/FES event classes.

## Frozen Defaults

- simulation steps: 240
- runs per topology / condition: 500
- degree-matched null graphs per event class: 40
- runs per null graph: 40
- random seed: 20260608

## Frozen Command

```bash
python3 scripts/test_Stage_B5_1_phi_fes_to_c12_bridge.py \
  --input-root /Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction \
  --output-dir reports \
  --n-runs 500 \
  --n-null-graphs 40 \
  --n-null-runs 40 \
  --steps 240 \
  --seed 20260608
```

## Interpretation Rules

If B5.1 is negative:

> Phi/FES switching did not show cross-framework predictive content for C12(1,2) under this preregistered audit.

If B5.1 is positive:

> Phi/FES switching, defined within the formal IDPC pipeline, conditioned recovery in an external D12RG C12(1,2) readout topology beyond controls.

A positive B5.1 result would not prove IDPC, D12RG, C12 as a physical carrier, or a final ontology. It would support only a limited cross-framework predictive-structure claim.
