# Stage B7.3a Preregistration

## Title

C12 Specificity and H24 Collective-Necessity Follow-up.

## Status

This preregistration is written after B7.3 execution and after the post-B7.3 feedback from Marcel, Tom, Luke, and C.A.T.

## Background

B7.3 produced a useful but exploratory boundary.

The strongest B7.3 conclusion was not that one endpoint-free C representation uniquely won. The safer conclusion was:

- scalar C did not reconnect to C12;
- several directed / receiver / standpoint-sensitive endpoint-free C projections reconnected to C12;
- endpoint-adjacent O1/O2 did not dominate the B7.3 C12 incremental criterion;
- canonical H24-168 was not supported under the same criterion;
- H24-216 differed from H24-168 and remains diagnostic only.

Marcel's conservative interpretation is adopted: B7.3 argues more strongly against scalar C than for any single replacement mechanism. Direction, receiver assignment, standpoint inversion, and coupled composite structure remain to be separated.

Tom's path-over-state interpretation is also adopted as a hypothesis to test: C is better treated as an ordered / directed correspondence than as a scalar endpoint. However, B7.3 alone did not establish twelvefold specificity, because C12-reversed remained close in several arms, neighbouring-cycle controls were absent, and held-out validation was absent.

Luke's latest H24/Phi24 clarification is also recorded. The intended carrier may require node-level Renshaw delay, edge-length or propagation-time structure, and state-dependent drive/suppression. Those rules are not yet frozen in deterministic preregisterable form. Therefore B7.3a tests only the current operational edge-level factorisation-suite / junction-coupling structure. It is not a complete test of Luke's full dynamical Phi24 carrier.

## Central Questions

1. Does C12 remain supported when tested against neighbouring cycles, reversed direction, side-broken controls, shuffled controls, and FDR using one frozen endpoint-free representation?

2. Does the current operational H24 factorisation-suite behave as a collectively necessary carrier, rather than merely a static graph containing possible factorisation paths?

## Frozen Primary Representation

Primary R_star:

- `receiver_standpoint_magnitude_c`

Rationale: this is the most theory-facing endpoint-free representation of the coupled receiver / standpoint / magnitude boundary identified across B7.2e-g.

Secondary representations:

- `directed_c`
- `receiver_only_c`
- `standpoint_inversion_c`
- `receiver_magnitude_c`
- `scalar_c`
- `endpoint_o1o2_reference`

The secondary representations are ablations and references. The primary C12 specificity claim is based on frozen R_star only.

For runtime and multiplicity control, the full topology-specific control suite is evaluated only for frozen R_star. Secondary C representations are evaluated only on `no_topology_baseline` and `c12_1_2` as ablation/reference checks.

## Part 1: C12 Specificity Arms

Topology arms:

- `no_topology_baseline`
- `c12_1_2`
- `c12_reversed`
- `c12_side_broken`
- `c12_shuffled`
- `c10`
- `c11`
- `c13`
- `c14`
- `c8_1`
- `topology_capacity_matched_null`
- `path_rewired_control`

## Primary C12 Criterion

C12 specificity is supported only if, for frozen R_star:

- `R_star + c12_1_2` exceeds `R_star + no_topology_baseline`;
- `R_star + c12_1_2` exceeds `c12_reversed`;
- `R_star + c12_1_2` exceeds `c12_side_broken`;
- `R_star + c12_1_2` exceeds `c12_shuffled`;
- `R_star + c12_1_2` exceeds neighbouring-cycle controls `c10`, `c11`, `c13`, and `c14`;
- `c12_1_2` survives Benjamini-Hochberg FDR across the topology-specific family for R_star;
- positive sign is stable where held-out validation is operationally available.

In this implementation, held-out validation is not treated as an independent confirmatory condition unless the available event table supports a clean session-level split. If it is not available, B7.3a remains exploratory.

## Part 2: H24 Collective-Necessity Arms

Canonical edge-level source:

- `h24_minimum_factorisation_suite_168`

Diagnostic only:

- `h24_c8_stitched_derived_216`

Operational H24 arms:

- `h24_possible_factorisations_168`
- `h24_available_factorisations_junction_coupled`
- `h24_one_factorisation_class_removed`
- `h24_one_junction_family_broken`
- `h24_paths_available_but_mutually_disconnected`
- `h24_complete_factorisation_suite_coupled`
- `h24_degree_matched_null`
- `h24_216_diagnostic_only`

These arms test the current edge-level construction only. They do not include node-delay, edge-length, or state-dependent-drive dynamics.

## Primary H24 Criterion

H24 collective necessity is supported only if, for frozen R_star:

- `h24_complete_factorisation_suite_coupled` exceeds no-topology baseline;
- it exceeds the one-factorisation-class-removed control;
- it exceeds the one-junction-family-broken control;
- it exceeds the paths-available-but-mutually-disconnected control;
- it exceeds the H24 degree-matched null;
- it is significant against time-shifted/random schedules at the preregistered empirical threshold.

## Primary Classifications

C12 classifications:

- `c12_specificity_supported`
- `c12_reconnection_without_specificity`
- `c12_directionality_supported`
- `c12_directionality_not_isolated`
- `neighboring_cycle_explains_effect`
- `side_correspondence_required`
- `endpoint_o1o2_reclaims_upper_bound`
- `scalar_c_rejected`
- `unresolved_c12_specificity`

H24 classifications:

- `h24_collective_necessity_supported`
- `h24_possible_only_sufficient`
- `h24_available_but_not_required`
- `h24_junction_coupling_required`
- `h24_factorisation_removal_degrades`
- `h24_restoration_recovers`
- `h24_static_topology_not_sufficient`
- `h24_168_current_carrier_not_supported`
- `h24_216_diagnostic_only`
- `unresolved_h24_boundary`

## Fixed Settings

- event quantile: 0.75
- simulation steps: 240
- runs per representation/topology/condition: 80
- empirical p-value threshold: 0.05
- FDR: Benjamini-Hochberg across the R_star topology-specific family
- seed: 73073

## Interpretation Boundary

B7.3a is not a confirmation test for C12 or H24 by construction.

For C12, it asks whether the B7.3 C12 reconnection survives stricter topology-specific controls using a frozen R_star.

For H24, it asks whether the current operational edge-level factorisation-suite behaves like a collectively necessary structure. A negative result does not test Luke's later full dynamical Phi24 carrier with node delays, edge lengths, and state-dependent drives, because those rules are not yet frozen.
