# Stage B7.2 Preregistration: O1/O2 Control-Hierarchy Audit

Date: 2026-06-18

## Purpose

B7.2 tests whether the B7.1/B7.1a boundary is empirically attributable to ordinary A/B history, to causally valid past-only operator estimates, or to endpoint-adjacent O1/O2 operator-proxy information.

This preregistration incorporates two collaborator feedback points before execution:

1. Marcel's feedback: keep B7.2 primary as an O1/O2 causal-validity and control-hierarchy audit, with C12 paused as a confirmatory topology module until the operator-proxy question is resolved.
2. Luke's feedback: add a secondary GMR72 angular-profile stability diagnostic including 75 degrees and local +/-1 degree scans around selected angles, using 0.2 degree increments.

## Frozen Input Set

B7.2 is restricted to the frozen B6-supported regimes used by B7.1/B7.1a.

The unit of analysis is:

- mode
- endpoint
- direction

B7.2 does not expand the B6 exploratory set.

## Primary Question

Does true C-mediated access retain an advantage over causally valid A/B-derived controls after removing endpoint-adjacent O1/O2 information?

## Control Hierarchy

B7.2 evaluates true C-mediated access against the following ordered controls:

1. strict_past_ab_only
   - A/B-current plus short past A/B lags and local past A/B summaries.
   - No O1/O2 operator-proxy features.
2. expanded_past_ab_only
   - strict past A/B plus coarser A/B trend and volatility summaries.
   - No O1/O2 operator-proxy features.
3. causal_past_operator_estimator
   - a past-only A/B-derived operator estimator.
   - It may use past A/B lags and rolling past A/B summaries.
   - It may not use current-row O1/O2 raw operator-proxy features.
4. lag_horizon_separated_o1o2
   - temporally separated O1/O2 proxy summaries using lagged/rolled prior O1/O2 values.
   - This tests whether the O1/O2 advantage survives when current-row endpoint adjacency is removed.
5. operator_proxy_ab
   - the endpoint-adjacent O1/O2 operator-proxy control from B7.1/B7.1a.
   - This is treated as an upper-bound style control, not as simple past A/B history.

## Primary Success Criterion

A regime is B7.2-primary-supported if:

- it is in the frozen B6-supported set;
- true C-mediated access beats strict_past_ab_only;
- true C-mediated access beats expanded_past_ab_only;
- true C-mediated access beats causal_past_operator_estimator;
- true C-mediated access beats lag_horizon_separated_o1o2.

Beating operator_proxy_ab is not required for primary support, because B7.1/B7.1a already showed that this endpoint-adjacent proxy can dominate true C. B7.2 instead asks whether that domination persists after temporal/endpoint adjacency is removed.

## Interpretation Rules

- If true C beats strict/expanded past A/B but not causal_past_operator_estimator, then B7.1a's result is limited to simple A/B history and does not establish an advantage over causally valid A/B-derived operator estimates.
- If true C beats causal_past_operator_estimator but not lag_horizon_separated_o1o2, then the remaining explanatory boundary lies in temporally separated O1/O2 proxy information.
- If true C beats causal_past_operator_estimator and lag_horizon_separated_o1o2 but not operator_proxy_ab, then B7.1's failure is consistent with endpoint-adjacent O1/O2 proxy strength rather than ordinary A/B-history reducibility.
- If true C also beats operator_proxy_ab, then the current C representation exceeds the full tested hierarchy.

## Marcel Feedback Constraint

C12 reconnection remains paused as a confirmatory module during B7.2.

B7.2 may discuss whether a future C12 test has become better motivated, but it must not use C12 stabilization to rescue or reinterpret a failed B7.2 primary result.

Mediation/closure language is secondary. It becomes stronger only if true C remains:

- frozen-B6 supported;
- non-substitutable;
- phase-sensitive;
- held-out stable;
- not explained by causally valid A/B-derived operator estimates.

## Luke Feedback: Secondary GMR72 Angular Diagnostic

B7.2 also freezes a secondary angular-profile diagnostic for the GMR72-conditioned regime.

The secondary diagnostic includes:

- 75 degrees as an explicit candidate angle;
- local scans around selected angles using +/-1 degree windows;
- a 0.2 degree step size;
- the distinction between sharply tuned and broad/noisy angular stability.

This diagnostic is secondary and does not affect the B7.2 primary success criterion.

## Outputs

B7.2 will write:

- Stage_B7_2_control_hierarchy_comparison.csv
- Stage_B7_2_primary_classification.csv
- Stage_B7_2_hierarchy_control_events.csv
- Stage_B7_2_o1o2_provenance_audit.csv
- Stage_B7_2_gmr72_secondary_angle_grid.csv
- Stage_B7_2_preregistered_summary.md

## Non-Claims

B7.2 does not claim that C is independent of all A/B-derived information unless it beats the full hierarchy including operator_proxy_ab.

B7.2 does not claim that the current implementation instantiates the full Phi^24 / eight-2ODE standing/travelling-wave D12RG architecture.

B7.2 does not make C12 confirmatory.

