# Stage B7.2d Preregistration

## Title

Directed-C Sufficiency and Provenance-Dilution Audit.

## Status

This preregistration is written after the B7.2c result and before B7.2d execution.

## Background

B7.2c attempted to reconstruct the B7.2b endpoint-local O1/O2 boundary without directly using endpoint-adjacent O1/O2 raw values.

The primary Directed-Provenance C reconstruction failed:

- `directed_provenance_c` bounded true C in `0 / 11` frozen B6-supported regimes.
- `endpoint_o1o2_reference` bounded true C in `11 / 11`.
- `directed_transport_closure_o1o2` bounded true C in `11 / 11`.

However, compact `directed_c` was partially strong:

- `directed_c` bounded true C in `9 / 11`.
- `directed_c_side_shuffled` bounded true C in `0 / 11`.

Therefore, the immediate problem is not simply that endpoint-free direction structure failed. The problem is that compact directed C retained substantial signal, while the expanded provenance representation collapsed.

## Central Question

Why does compact `directed_c` bound true C in `9 / 11` frozen regimes, while expanded `directed_provenance_c` collapses to `0 / 11`?

## Working Hypotheses

1. `provenance_dilution`

The added provenance variables fragment the state space and dilute the compact side/direction signal.

2. `wrong_provenance`

The selected provenance variables do not encode the endpoint-local structure that O1/O2 carries.

3. `over_specific_state_failure`

The Directed-Provenance C state is too high-dimensional for the frozen regime sample size, causing unreliable train/test mappings.

4. `compact_direction_boundary`

The useful endpoint-free structure is mostly compact side/direction structure, not expanded provenance.

5. `true_endpoint_gap`

Even optimized endpoint-free directed C cannot reproduce the full O1/O2 boundary, implying that O1/O2 still contains endpoint-adjacent information absent from current C.

## Candidate Arms

The audit compares true C-mediated access against:

- `directed_c_compact`: B7.2c compact directed C reference.
- `directed_c_minimal`: direction identity plus side identity only.
- `directed_c_with_side_polarity`: direction identity, side identity, and side polarity.
- `directed_c_with_endpoint_free_transport`: direction identity, side identity, side polarity, A-C/B-C contrast, A-B, and TFC structure, excluding O1/O2 raw values.
- `provenance_add_phase_strength`: compact directed C plus phase and strength provenance.
- `provenance_add_tfc_memory`: compact directed C plus TFC and memory provenance.
- `provenance_add_fes`: compact directed C plus FES phase/cluster provenance.
- `full_directed_provenance`: B7.2c full Directed-Provenance C.
- `regularized_directed_provenance`: full provenance with fallback to compact directed C when full-state support is sparse.
- `provenance_shuffled_control`: matched provenance control preserving marginal provenance while disrupting side/direction correspondence.
- `endpoint_o1o2_reference`: endpoint-adjacent O1/O2 upper-bound reference.
- `directed_transport_closure_o1o2`: O1/O2-containing directed transport reference.

## O1/O2 Boundary

The endpoint-free arms must not directly use:

- `O1_lag0_AB_raw`
- `O2_lag5_AB_raw`

Arms with names containing `o1o2` are retained only as endpoint-adjacent references.

## Primary Criteria

B7.2d classifies:

- whether compact directed C is near-sufficient;
- whether minimal direction alone is sufficient;
- whether side polarity is required;
- whether endpoint-free transport features improve compact directed C;
- whether provenance additions dilute the compact directed signal;
- whether regularized/backoff provenance recovers the compact directed signal;
- whether the endpoint gap persists after optimized endpoint-free directed C.

## Primary Classification

- `compact_directed_c_near_sufficient`
- `minimal_direction_sufficient`
- `side_polarity_required`
- `endpoint_free_transport_required`
- `provenance_dilution_supported`
- `wrong_provenance_supported`
- `regularized_provenance_recovers_signal`
- `endpoint_gap_persists`
- `unresolved_directed_c_boundary`

## Evaluation Set

The primary evaluation set is the frozen B6-supported regimes from Stage B7.1, as used in B7.1a, B7.2, B7.2a, B7.2b, and B7.2c.

## Fixed Settings

- n_folds: 5
- min_state_events: 8
- temperature: 0.35
- n_perm: 5000
- alpha: 0.05
- seed: 71204

## C12 Positioning

C12 reconnection remains paused for this audit. B7.2d is a directed-C reconstruction diagnostic, not a C12 confirmation test.
