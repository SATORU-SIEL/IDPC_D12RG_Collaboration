# Stage B7.2e Preregistration

## Title

Side-Polarity Decomposition and Standpoint Meaning Audit.

## Status

This preregistration is written after B7.2d and before B7.2e execution.

## Background

B7.2d showed that endpoint-free compact directed C becomes near-sufficient when side polarity is included:

- `directed_c_minimal` bounded true C in `9 / 11` frozen B6-supported regimes.
- `directed_c_with_side_polarity` bounded true C in `11 / 11`.

This makes side polarity the next key unresolved variable.

## Central Question

What does the side-polarity term that closes the B7.2d directed-C gap actually represent?

## Candidate Interpretations

B7.2e compares whether side polarity is:

- ordinary A-C/B-C asymmetry;
- sign-only polarity;
- magnitude-only polarity;
- receiver-side or giver-side access;
- direction-conditioned standpoint polarity;
- a phase/TFC surrogate;
- or an endpoint O1/O2 proxy in another form.

## Candidate Arms

The audit compares true C-mediated access against:

- `unsigned_side_gap`
- `signed_ac_minus_bc`
- `polarity_sign_only`
- `polarity_magnitude_only`
- `direction_conditioned_side_polarity`
- `receiver_side_only`
- `giver_side_only`
- `standpoint_polarity_preserved`
- `standpoint_polarity_inverted`
- `phase_tfc_matched_polarity_control`
- `endpoint_o1o2_reference`

## O1/O2 Boundary

Endpoint-free arms must not directly use:

- `O1_lag0_AB_raw`
- `O2_lag5_AB_raw`

`endpoint_o1o2_reference` is retained only as an endpoint-adjacent upper-bound reference.

## Primary Criteria

B7.2e classifies:

- whether unsigned side asymmetry is sufficient;
- whether ordinary signed A-C/B-C contrast is sufficient;
- whether polarity sign or magnitude is sufficient;
- whether receiver-side or giver-side access is sufficient;
- whether direction-conditioned side polarity is required;
- whether standpoint-preserved polarity survives better than standpoint-inverted polarity;
- whether phase/TFC matched controls explain the signal;
- whether O1/O2 remains stronger by effect size.

## Primary Classification

- `unsigned_side_gap_sufficient`
- `signed_ac_bc_contrast_sufficient`
- `polarity_sign_sufficient`
- `polarity_magnitude_sufficient`
- `direction_conditioned_polarity_required`
- `receiver_side_sufficient`
- `giver_side_sufficient`
- `standpoint_polarity_supported`
- `standpoint_inversion_breaks_signal`
- `phase_tfc_surrogate_supported`
- `endpoint_o1o2_effect_size_gap_persists`
- `unresolved_side_polarity_meaning`

## Evaluation Set

The primary evaluation set is the frozen B6-supported regimes from Stage B7.1, as used in B7.1a through B7.2d.

## Fixed Settings

- n_folds: 5
- min_state_events: 8
- temperature: 0.35
- n_perm: 5000
- alpha: 0.05
- seed: 71205

## C12 Positioning

C12 reconnection remains paused for this audit. B7.2e determines what side polarity means before side-polarity C is used in a C12 reconnection test.
