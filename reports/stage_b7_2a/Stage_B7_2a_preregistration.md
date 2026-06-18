# Stage B7.2a Preregistration: O1/O2 Proxy Provenance Decomposition

Date: 2026-06-18

## Purpose

B7.2a decomposes the endpoint-adjacent O1/O2 operator-proxy control that true C-mediated access failed to beat in B7.2.

B7.2 showed that true C-mediated access exceeds simple past A/B history, the causally valid past-only A/B-derived operator estimator, and lag/horizon-separated O1/O2 summaries. However, true C did not exceed the endpoint-adjacent O1/O2 proxy.

The B7.2a question is:

Is the O1/O2 proxy that C failed to beat genuinely A/B-derived operator information, or does it already contain a compressed representation of the phase-sensitive, non-substitutable, C-mediated structure detected in B6?

## Frozen Input Set

B7.2a uses the same frozen B6/B7 regime frame as B7.2.

The unit of analysis remains:

- mode
- endpoint
- direction

The primary interpretation is restricted to frozen B6-supported regimes.

## Decomposition Controls

B7.2a decomposes endpoint-adjacent O1/O2 into the following controls:

1. `o1_lag0_only`
   - Uses only `O1_lag0_AB_raw`.

2. `o2_lag5_only`
   - Uses only `O2_lag5_AB_raw`.

3. `o1_o2_joint`
   - Uses joint endpoint-adjacent O1/O2 information.

4. `phase_removed_o1o2`
   - Uses O1/O2 after phase-bin structure is removed by within-phase marginalization.

5. `tfc_removed_o1o2`
   - Uses O1/O2 after TFC-bin structure is removed by within-TFC marginalization.

6. `side_shuffled_o1o2`
   - Uses deterministic within-session shuffled O1/O2 pairings to disturb side/direction correspondence while preserving marginal proxy values.

7. `memory_only_o1o2`
   - Uses lagged and rolling past O1/O2 summaries only.

8. `residual_endpoint_o1o2`
   - Uses O1/O2 residuals after removing variance explained by past A/B, causal-estimator features, and lagged O1/O2 summaries.

## Primary Outputs

B7.2a will classify the endpoint-adjacent O1/O2 boundary using the following labels:

- `pure_ab_operator_proxy`
- `phase_sensitive_proxy`
- `tfc_compressed_proxy`
- `side_directional_proxy`
- `memory_proxy`
- `residual_endpoint_proxy`
- `compound_proxy`

## Primary Interpretation Rules

If O1/O2 strength is explained by pure lag0/lag5 A/B operator information, then B7.2's boundary is strengthened: true C is above simple history, but below A/B-derived operator-proxy information.

If O1/O2 strength drops after phase removal, TFC removal, or side/direction shuffling, then B6 and B7 are not in conflict. In that case, the B6 structure may be compressed into the endpoint-adjacent O1/O2 proxy.

If no single decomposed component bounds true C but the joint O1/O2 proxy does, then the endpoint-adjacent advantage is a compound proxy effect rather than a simple single-feature reduction.

If residual endpoint-local O1/O2 still bounds true C after past A/B and lagged O1/O2 are removed, then the current C representation may be missing endpoint-local operator structure.

## C12 Constraint

C12 remains paused in B7.2a.

B7.2a may motivate a future C12 reconnection test, but C12 is not used to rescue or reinterpret the B7.2a result.

## Outputs

B7.2a will write:

- `Stage_B7_2a_decomposition_control_events.csv`
- `Stage_B7_2a_decomposition_comparison.csv`
- `Stage_B7_2a_boundary_classification.csv`
- `Stage_B7_2a_component_summary.csv`
- `Stage_B7_2a_preregistered_summary.md`

## Non-Claims

B7.2a does not claim that C exceeds endpoint-adjacent O1/O2.

B7.2a does not claim C12 confirmation.

B7.2a does not establish the full Phi^24 / eight-2ODE architecture.
