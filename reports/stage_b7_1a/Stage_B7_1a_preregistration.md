# Stage B7.1a Preregistration

## Title

A/B-History Control Validity Audit.

## Status

Preregistered follow-up to Stage B7.1. Stage B7.1 did not support true C-mediated intersection access beyond its A/B-history policy control. Stage B7.1a tests whether that A/B-history control was a legitimate past-history control or an endpoint-adjacent operator proxy.

## Motivation

Stage B7.1 kept the frozen B6 structure for non-substitutability and phase sensitivity, but no regime passed the primary criterion because true C-mediated access did not outperform the A/B-history policy control.

The B7.1 A/B-history policy used A_B, O1_lag0_AB_raw, and O2_lag5_AB_raw. This is a strong control, but O1/O2 raw values may be close to the endpoint/operator-reward construction. Stage B7.1a therefore separates A/B controls into three levels.

## Primary Question

Does true C-mediated intersection access outperform strict past A/B-only controls that do not use operator reward columns, future reward columns, C-derived features, TFC-derived features, or A-C/B-C boundary features?

## Control Levels

### Level 1: strict_past_ab_only

Uses only A_B time series history within label:

- A_B(t)
- lagged A_B values
- rolling mean of past A_B
- rolling slope of past A_B
- rolling volatility of past A_B

No operator reward columns, C-derived features, TFC-derived features, or A-C/B-C boundary features are allowed as state features.

### Level 2: expanded_past_ab_only

Uses A_B history plus past-only summaries of A_B dynamics at multiple horizons. This is still restricted to A/B-only history and cannot use C, TFC, A-C, B-C, or operator reward features as state features.

### Level 3: operator_proxy_ab

Uses the B7.1-style A_B plus O1_lag0_AB_raw and O2_lag5_AB_raw state control. This is treated as an endpoint-adjacent upper-bound control, not as ordinary A/B history.

## Primary Endpoint

intersection_access_effect.

## Primary Success Criteria

Stage B7.1a supports renewed C-mediated access only if:

1. True C-mediated access outperforms strict_past_ab_only on held-out folds.
2. True C-mediated access retains B6 frozen support for non-substitutability and phase sensitivity.
3. True C-mediated access remains below oracle.

If true C beats strict_past_ab_only but not operator_proxy_ab, the interpretation is:

true C-mediated access exceeds simple A/B history but does not exceed endpoint-adjacent operator-proxy controls.

If true C does not beat strict_past_ab_only, the interpretation is:

the B6 C effect should be read as A/B-history-derived feature transformation under the current implementation.

## C12 Boundary

C12 is not tested as confirmatory in Stage B7.1a. C12 reconnection should resume only if true C outperforms strict past A/B controls while retaining non-substitutability and phase sensitivity.

## Planned Outputs

- Stage_B7_1a_preregistered_summary.md
- Stage_B7_1a_control_level_comparison.csv
- Stage_B7_1a_primary_classification.csv
- Stage_B7_1a_ab_control_events.csv
- Stage_B7_1a_preregistration.md

