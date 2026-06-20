# Stage B7.2g Preregistration

## Title

Receiver-Standpoint Parity Mismatch and Falsification Audit.

## Status

This preregistration is written after the private B7.2g parity screen and before formal B7.2g execution.

## Background

B7.2f showed a near miss:

- `receiver_side_only` bounded true C in `11 / 11`.
- `receiver_standpoint_reconstruction` bounded true C in `10 / 11`.
- `standpoint_polarity_preserved` bounded true C in `11 / 11`.
- `standpoint_polarity_inverted` bounded true C in `9 / 11`.

This makes a simple receiver-only explanation too weak. Standpoint inversion changes the result, but the earlier receiver-standpoint reconstruction did not cleanly improve over receiver-only.

A private local screen suggested that the key may be the parity relation between receiver assignment and standpoint assignment:

- receiver preserved + standpoint preserved;
- receiver preserved + standpoint inverted;
- receiver inverted + standpoint preserved;
- receiver inverted + standpoint inverted.

In the private screen, the mismatched cross terms were stronger by effect size than the matched terms.

## Central Question

Is the B7.2f residual boundary driven by receiver-only structure, or by receiver-standpoint parity/mismatch?

## Conservative Interpretation Boundary

B7.2g does not assume that parity/mismatch is the correct explanatory object.

It explicitly tests whether the B7.2f residual can instead be explained by two partially overlapping simpler effects:

- receiver-side structure;
- weaker standpoint-related structure.

Only if the parity/mismatch arms survive the receiver-only, standpoint-only, sign-only, magnitude-only, complexity-shuffled, and A/B-exchange falsification arms should a parity/mismatch interpretation be considered strengthened.

## Primary Hypothesis

The relevant endpoint-free structure is not receiver alone and not standpoint alone, but the parity relation between receiver assignment and standpoint assignment.

Specifically, the effect should change when receiver and standpoint assignments are mismatched:

- receiver preserved + standpoint inverted;
- receiver inverted + standpoint preserved.

## Primary 2x2 Arms

- `receiver_preserved__standpoint_preserved`
- `receiver_preserved__standpoint_inverted`
- `receiver_inverted__standpoint_preserved`
- `receiver_inverted__standpoint_inverted`

## Falsification Arms

B7.2g includes falsification controls intended to reject the parity interpretation if simpler explanations suffice:

- `receiver_only`
- `standpoint_only_preserved`
- `standpoint_only_inverted`
- `standpoint_sign_only`
- `standpoint_magnitude_only`
- `receiver_plus_magnitude`
- `receiver_plus_standpoint_sign`
- `complexity_matched_shuffled_pair`
- `parity_label_shuffled`
- `ab_exchange_parity_mismatch`
- `endpoint_o1o2_reference`

## Falsification Logic

The parity interpretation is weakened if:

- receiver-only matches or exceeds the mismatched parity arms;
- standpoint-only matches or exceeds the mismatched parity arms;
- sign-only or magnitude-only explains the effect;
- complexity-matched shuffled states match or exceed the mismatched parity arms;
- A/B exchange does not transform the effect predictably;
- endpoint O1/O2 is the only strong arm.

## Primary Classifications

- `parity_mismatch_supported`
- `receiver_only_explains_effect`
- `standpoint_only_explains_effect`
- `sign_or_magnitude_explains_effect`
- `complexity_shuffle_explains_effect`
- `ab_exchange_consistent`
- `endpoint_o1o2_effect_size_gap_persists`
- `parity_hypothesis_falsified`
- `unresolved_parity_boundary`

## Decision Rules

### Parity Mismatch Supported

Supported if both mismatched arms have more negative mean true-minus-control effects than both matched arms by at least `0.005`.

### Receiver-Only Explains Effect

Supported if `receiver_only` is as strong as or stronger than the best mismatched arm within `0.005`.

### Standpoint-Only Explains Effect

Supported if either standpoint-only arm is as strong as or stronger than the best mismatched arm within `0.005`.

### Sign/Magnitude Explains Effect

Supported if sign-only, magnitude-only, or receiver-plus-magnitude arms are as strong as or stronger than the best mismatched arm within `0.005`.

### Complexity Shuffle Explains Effect

Supported if complexity-matched shuffled controls are as strong as or stronger than the best mismatched arm within `0.005`.

### Parity Hypothesis Falsified

Supported if parity mismatch is not supported or if any simpler falsification arm explains the effect.

## Evaluation Set

The primary evaluation set is the frozen B6-supported regimes from Stage B7.1, as used in B7.1a through B7.2f.

## Fixed Settings

- n_folds: 5
- min_state_events: 8
- temperature: 0.35
- n_perm: 5000
- alpha: 0.05
- seed: 71208

## C12 Positioning

C12 remains paused. B7.2g tests whether the receiver/standpoint residual boundary is a parity/mismatch effect before any C12 reconnection is attempted.
