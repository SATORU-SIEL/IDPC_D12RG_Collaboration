# Stage B7.1 Preregistration

## Title

Preregistered C-Mediated Intersection Access Replication and Discrimination Audit.

## Status

This is a preregistered hypothesis-testing audit derived from the exploratory B6 series. The B6 regime definitions are frozen before Stage B7.1 execution. This audit is intended to test whether the B6 intersection-access signal survives out-of-sample discrimination against A/B-history-only models, matched fake-C controls, and phase-displaced C controls.

## Motivation

B6 was exploratory. It produced a repeatable pattern in which object-like scoring and direct A-B access failed, while C-mediated intersection access survived in selected regimes. B6W and B6Z sharpened this: the result was not simply that C-mediated access survives, but that true C was not freely substitutable and C-mediated access was phase-sensitive.

Stage B7.1 therefore tests the stricter claim:

True C-mediated intersection access requires the specific C construction, is not freely substitutable, is phase-sensitive, and retains information beyond complete A/B-history controls.

## Primary Question

Does true C retain out-of-sample intersection-access information after conditioning on the available histories of A and B?

## Primary Endpoint

The primary endpoint is intersection_access_effect.

The primary-compatible secondary endpoint is operator_selection_advantage.

C12 is not the primary endpoint. C12 is included only as a prespecified secondary topology-readout module.

## Frozen B6-Supported Regime Definition

A regime counts as B6-supported only if all three criteria are met:

1. C-necessary: no-C direct A-B access fails while C-mediated access survives.
2. Non-substitutable: true C outperforms matched fake-C controls.
3. Phase-sensitive: preregistered phase displacement reduces or collapses access.

The B6 exploratory overlap was 11 / 24 regimes. In B7.1 this definition is fixed before execution and is not modified after inspecting B7.1 outcomes.

## Primary Controls

The primary discrimination controls are:

- direct A-B access
- lag-matched A-B access
- A/B-history policy using A_B, O1_lag0_AB, and O2_lag5_AB history bins only
- shuffled C
- random C
- balanced C
- foreign-label C
- spectrum/density/autocorrelation matched fake-C summary controls when available
- phase-rotated C
- fine phase-displaced C
- objectification-style C scores
- oracle access/operator upper bound

The strongest required control is whether true C retains information after conditioning on the available A/B histories.

## Primary Success Criteria

Stage B7.1 is supported only if all of the following hold on held-out label folds:

1. True C-mediated access outperforms the best A/B-history-only control.
2. True C-mediated access outperforms matched fake-C controls.
3. True C-mediated access outperforms phase-displaced C controls.
4. The phase-collapse profile is reproducible out-of-sample.
5. True C remains below oracle.

## Failure Criteria

Stage B7.1 is downgraded if:

- A/B-history-only controls explain the effect.
- matched fake-C controls reproduce the effect.
- phase-displaced C controls reproduce the effect.
- the effect does not survive held-out label folds.
- regime success depends on post-hoc selection.
- true C reaches or exceeds oracle in a way suggesting leakage.

If downgraded, the B6 exploratory pattern should be read as nonlinear A/B mediation, compressed A/B-history statistics, a phase-conditioned feature transformation, or a lagged relational state rather than a distinct C-mediated intersection-access condition.

## Secondary GMR72 / RG4x5 Module

GMR72/RG4x5 is tested as a secondary mechanistic module.

Question: does the structured GMR72 phase bridge produce a reproducible angular response profile?

The audit fixes these angular controls:

- -72 degrees
- 0 degrees
- 22.5 degrees
- 36 degrees
- 45 degrees
- 60 degrees
- 72 degrees
- 90 degrees
- 144 degrees
- random phase
- phase-reversed control

The GMR72/RG4x5 module is supported only if the forward 72-degree bridge is part of a reproducible angular response profile, random and reversed controls degrade, neighboring angles show the expected profile shape, circular multiple-testing correction is satisfied, and the pattern replicates on held-out data.

## Secondary C12 Reconnection Module

C12 is included as a prespecified secondary topology-readout module, not as the center or optimizer of B7.1.

Question: does C12 stabilization concentrate prospectively in regimes that are simultaneously C-necessary, non-substitutable, and phase-sensitive?

The C12 module compares:

- B6-supported true C regimes
- no-C direct A-B regimes
- shuffled/random/balanced/foreign C regimes
- phase-shifted C regimes
- objectification-style C-score regimes
- A/B-history-only regimes

The C12 endpoints are:

- C12 bounded differentiated recovery
- C12 stability
- C12 phase/readout persistence
- shared-node C12
- triadic-packet C12

The C12 module is supported only if B6-supported true C regimes outperform no-C, matched fake-C, phase-shifted C, and objectification-style controls, with directionally consistent evidence in at least one secondary topology readout.

If the C12 module fails, the B6 intersection-access result may still be useful, but C12 should not be invoked as its readout geometry under the current implementation.

## Planned Output

Outputs will be written to reports/stage_b7_1/:

- Stage_B7_1_preregistered_summary.md
- Stage_B7_1_primary_discrimination_summary.csv
- Stage_B7_1_ab_history_control_comparison.csv
- Stage_B7_1_b6_regime_freeze.csv
- Stage_B7_1_gmr72_angular_response_summary.csv
- Stage_B7_1_c12_reconnection_screen.csv

