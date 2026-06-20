# Stage B7.2f Preregistration

## Title

Receiver-Standpoint Reconstruction with Preregistered Snapshot and Trajectory Controls.

## Status

This preregistration is written after the updated B7.2f plan email and before B7.2f execution.

## Background

B7.2e narrowed the side-polarity interpretation. The following arms bounded true C in all frozen B6-supported regimes:

- `unsigned_side_gap`
- `polarity_magnitude_only`
- `receiver_side_only`
- `standpoint_polarity_preserved`

The following arms did not:

- `signed_ac_minus_bc`
- `polarity_sign_only`
- `giver_side_only`
- `standpoint_polarity_inverted`
- `phase_tfc_matched_polarity_control`

The next question is whether the surviving structure is a genuine endpoint-free receiver/standpoint correspondence, and whether that correspondence is continuously present or only visible after stabilization.

## Central Questions

1. Can receiver-side / standpoint-preserved structure bound true C without endpoint-adjacent O1/O2 values?
2. Is the surviving structure stable across empirical snapshots, recovery-dependent, transient-only, or endpoint-only?

## Important Operational Boundary

B7.2f does not claim to simulate a true iterative dynamical convergence process.

The available table is an empirical sparse-event table. Therefore, B7.2f uses preregistered empirical window snapshots around each evaluated event. These snapshots are used to test whether final-state B7 conclusions are robust to nearby trajectory readouts.

## Snapshot Definitions

For each event within each session, B7.2f evaluates:

- `t0`: event row itself.
- `t1`: first available later event row in the same session.
- `t2`: fixed preregistered second later event row in the same session.
- `tc`: first later event row, after at least two updates, satisfying an outcome-independent stabilization criterion.
- `tc_plus_k`: fixed first available event row after `tc`.

The `tc` stabilization criterion is defined only from C-memory and phase:

- absolute C-memory change from the previous candidate is at or below the session-level median absolute C-memory change;
- absolute circular phase change from the previous candidate is at or below the session-level median absolute phase change.

No reward endpoint, operator reward, true-C effect, or O1/O2 endpoint value is used to define `tc`.

Rows without a valid future snapshot for a given snapshot label are omitted for that snapshot.

## Structure Arms

B7.2f compares:

- `unperturbed_baseline`
- `sham_perturbation`
- `receiver_standpoint_reconstruction`
- `receiver_standpoint_reconstruction_shuffled`
- `mapping_inversion`
- `side_shuffle`
- `unsigned_side_gap`
- `polarity_magnitude_only`
- `receiver_side_only`
- `giver_side_only`
- `standpoint_polarity_preserved`
- `standpoint_polarity_inverted`
- `ab_exchange_receiver_standpoint`
- `mirrored_receiver_standpoint`
- `normalization_matched_receiver_standpoint`
- `reward_symmetry_control`
- `endpoint_o1o2_reference`

Endpoint-free arms do not directly use:

- `O1_lag0_AB_raw`
- `O2_lag5_AB_raw`

`endpoint_o1o2_reference` remains an endpoint-adjacent upper-bound reference only.

## Baselines

B7.2f includes:

- unperturbed baseline;
- sham perturbation;
- mapping inversion;
- side shuffle;
- endpoint-adjacent O1/O2 reference.

These distinguish true disruption from natural drift or construction noise.

## Trajectory Metrics

For each arm and frozen B6-supported regime, B7.2f computes:

- final snapshot effect;
- maximum disruption;
- time to maximum disruption;
- recovery amount;
- overshoot;
- area under disruption curve;
- post-convergence residual;
- trajectory hysteresis proxy;
- mean true-minus-control effect;
- binary count of whether true C beats the control.

The generic disruption curve is:

`D(t) = baseline_effect(t) - arm_effect(t)`

where baseline is `unperturbed_baseline` at the same mode, endpoint, direction, and snapshot.

## Primary Classifications

- `receiver_standpoint_reconstruction_supported`
- `receiver_only_sufficient`
- `standpoint_preservation_required`
- `standpoint_inversion_breaks_signal`
- `shuffled_mapping_breaks_signal`
- `ab_exchange_predictable`
- `feature_construction_asymmetry_detected`
- `endpoint_o1o2_effect_size_gap_persists`
- `stable_correspondence`
- `recovery_dependent_correspondence`
- `transient_disruption_only`
- `endpoint_only_effect`
- `final_readout_sufficient`
- `final_readout_insufficient`
- `unresolved_receiver_standpoint_boundary`

## Interpretation Rules

### Stable Correspondence

Supported if preserved receiver/standpoint reconstruction is already stronger than inverted/shuffled controls at `t1` and remains stronger through `tc` and `tc_plus_k`.

### Recovery-Dependent Correspondence

Supported if preserved and inverted/shuffled arms are similar early, but preserved receiver/standpoint reconstruction separates at `tc` or `tc_plus_k`.

### Transient-Disruption-Only Effect

Supported if inverted/shuffled controls show large disruption at `t1` or `t2`, but converge to the same final readout by `tc_plus_k`.

### Endpoint-Only Effect

Supported if endpoint-free arms show no robust trajectory distinction while `endpoint_o1o2_reference` remains clearly stronger.

### Receiver-Side Interpretation Boundary

The receiver-side interpretation is not treated as ontologically established unless:

- receiver/standpoint reconstruction is stronger than giver-only and mirrored controls;
- A/B exchange transforms the effect predictably;
- normalization-matched and reward-symmetry controls do not remove the effect;
- the result is not driven by a single session subset.

## Evaluation Set

The primary evaluation set is the frozen B6-supported regimes from Stage B7.1, as used in B7.1a through B7.2e.

## Fixed Settings

- n_folds: 5
- min_state_events: 8
- temperature: 0.35
- n_perm: 5000
- alpha: 0.05
- seed: 71206

## C12 Positioning

C12 remains paused during B7.2f.

If B7.2f supports stable correspondence, the next C12 audit should use a directed receiver-standpoint C carrier.

If B7.2f supports recovery-dependent correspondence, the next C12 audit should test whether the directed ring acts as an attractor that restores correspondence after perturbation.

If B7.2f supports transient-disruption-only effects, prior C12 readouts may have missed mechanism by sampling only after relaxation.
