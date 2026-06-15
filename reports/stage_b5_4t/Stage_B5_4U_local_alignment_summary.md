# Stage B5.4U Local Alignment Results

This report summarizes the preregistered B5.4U local alignment and boundary-window audit.

Preregistration:

`reports/stage_b5_4t/Stage_B5_4U_local_alignment_preregistration_proposal.md`

Execution script:

`scripts/test_Stage_B5_4U_local_alignment_audit.py`

## Executive Summary

B5.4U supports a narrow local alignment interpretation, not a broad event-window interpretation.

The strongest condition is lag +5. The original lag 0 remains positive, but broad window spreading weakens the effect.

Thus, the B5.4T/B5.4U result is best described as:

phase-bearing sparse event geometry with a small local response lag.

## Strongest Lag Condition

`b54u_lag_plus5`

- recovery: 0.026879
- p vs shifted/random: 0.039146
- p vs C8: 0.007092
- p vs degree-null: 0.002770
- late-window stability: 0.611997

## Original Lag 0

`b54u_lag_0`

- recovery: 0.025545
- p vs shifted/random: 0.060498
- p vs C8: 0.007092
- p vs degree-null: 0.002770
- late-window stability: 0.619076

## Nearby Negative Lag

`b54u_lag_minus1`

- recovery: 0.025559
- p vs shifted/random: 0.071174
- p vs C8: 0.007092
- p vs degree-null: 0.002770
- late-window stability: 0.615261

## Window Conditions

Window spreading weakens the effect.

`b54u_symmetric_window_r1`

- recovery: 0.012547
- p vs shifted/random: 0.291815
- p vs degree-null: 0.044321

`b54u_symmetric_window_r2`

- recovery: 0.002992
- p vs shifted/random: 0.975089
- p vs degree-null: 0.210526

Larger symmetric windows collapse further.

## Boundary-Distance Conditions

The result does not support a simple near-boundary-only interpretation.

`b54u_boundary_far_matched`

- recovery: 0.032540
- p vs shifted/random: 0.053381
- p vs C8: 0.007092
- p vs degree-null: 0.002770
- late-window stability: 0.649786

`b54u_boundary_near_matched`

- recovery: 0.014855
- p vs shifted/random: 0.295374
- p vs C8: 0.319149
- p vs degree-null: 0.016620
- late-window stability: 0.734623

## Interpretation

B5.4U narrows B5.4T further.

The effect is not:

- broad event-window carrier,
- exact-bin-only event,
- near-h-boundary-only event,
- event density effect,
- or block structure effect.

The effect is more consistent with:

phase-bearing sparse event geometry with a small local response lag.

## Consequence for B5.5

B5.5 should not define C as raw phi memory or as a broad event window.

A safer C definition is:

`C = phase-bearing sparse event geometry with a small local response lag`

## Released Files

- `Stage_B5_4U_local_alignment_preregistration_proposal.md`
- `Stage_B5_4U_local_alignment_summary.md`
- `Stage_B5_4U_local_alignment_results.csv`
- `Stage_B5_4U_local_alignment_event_inventory.csv`
- `Stage_B5_4U_local_alignment_events.csv`
- `Stage_B5_4U_local_alignment_quadrature.csv`
- `Stage_B5_4U_local_alignment_temporal.csv`
- `Stage_B5_4U_local_alignment_raw_conditions.csv`
- `Stage_B5_4U_local_alignment_nulls.csv`
- `Stage_B5_4U_local_alignment_verdict.md`
- `scripts/test_Stage_B5_4U_local_alignment_audit.py`
