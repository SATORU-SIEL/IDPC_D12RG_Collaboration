# Stage B7.2b Preregistration: Side-Direction Correspondence, Directed Closure, and Factorisation-Path Lift

Date: 2026-06-19

## Purpose

B7.2b tests whether the remaining endpoint-adjacent O1/O2 boundary from B7.2a depends on preserving endpoint-local side-direction / asymmetric-standpoint correspondence across training and evaluation.

The primary target is not simply whether true C beats O1/O2. The target is to classify what kind of correspondence is required for the O1/O2 boundary to remain.

## Frozen Input Set

B7.2b uses the same frozen B6-supported regime frame used in B7.1, B7.1a, B7.2, and B7.2a.

The primary interpretation is restricted to frozen B6-supported regimes.

## Primary Empirical Module

B7.2b distinguishes:

- direction label only;
- fixed mask controls;
- endpoint-local O1/O2 direction pairing;
- train/test side-direction correspondence;
- static closure versus directed transport.

## Primary Controls

B7.2b includes:

- `direction_label_only`
- `communication_direction_only`
- `symmetric_midpoint_control`
- `sender_receiver_transfer_control`
- `asymmetric_standpoint_control`
- `standpoint_inverted_control`
- `endpoint_o1o2_reference`
- `endpoint_o1o2_direction_swapped`
- `standpoint_consistent_split_operator`
- `standpoint_inverted_split_operator`
- `standpoint_consistent_operator_contrast`
- `standpoint_inverted_operator_contrast`
- `standpoint_contrast_with_side_polarity`
- `standpoint_inverted_contrast_with_side_polarity`
- `mismatch_train_consistent_test_inverted`
- `mismatch_train_endpoint_test_direction_swapped`
- `fixed_b6p_direction_mask`
- `fixed_b6p_swapped_mask`
- `fixed_receiver_pair_mask`
- `fixed_giver_pair_mask`
- `fixed_ab_receiver_only`
- `fixed_c_receiver_boundary_only`

## Closure and Factorisation Architecture Module

B7.2b adds Luke's final architecture constraint.

The scalar expression `(A - B) + (B - A) = 0` is treated as one closure readout, or one possible 2ODE-local closure, not the full closure structure.

The stronger D12RG question is whether side-direction / asymmetric-standpoint correspondence survives lift across admissible 24-factorisation paths.

Secondary controls:

- `closure_scalar_only`
- `closure_2ode_local`
- `directed_transport_closure_control`
- `factorisation_3x8`
- `factorisation_2x2x6`
- `factorisation_path_consistent`
- `factorisation_path_shuffled`
- `factorisation_path_mismatch_train_test`

## C12 Diagnostic Layer

C12 remains paused as a confirmatory module.

B7.2b will nevertheless diagnose whether the apparent C12(1,2) difficulty is located at the same lift-across-factorisation-paths step tested here.

Interpretation:

1. If side-direction correspondence is preserved locally but fails across admissible 24-factorisation paths, then a later C12(1,2) failure should not be read immediately as a failure of the broader theory. It may indicate that the current C12(1,2) implementation lacks the required lift.

2. If side-direction correspondence remains stable across admissible factorisation paths, then C12(1,2) becomes a sharper confirmatory target.

3. If side-direction correspondence itself fails before factorisation-path lift, then the issue is prior to C12.

## Primary Classification

B7.2b classifies the boundary as one or more of:

- `direction_label_only_sufficient`
- `fixed_mask_sufficient`
- `endpoint_direction_pairing_required`
- `train_test_correspondence_required`
- `static_zero_sum_sufficient`
- `directed_transport_required`
- `factorisation_lift_required`
- `factorisation_lift_supported`
- `asymmetric_standpoint_required`
- `unresolved_side_direction_boundary`

## Outputs

B7.2b writes:

- `Stage_B7_2b_control_events.csv`
- `Stage_B7_2b_comparison.csv`
- `Stage_B7_2b_component_summary.csv`
- `Stage_B7_2b_frozen_pass_matrix.csv`
- `Stage_B7_2b_primary_classification.csv`
- `Stage_B7_2b_preregistered_summary.md`

## Non-Claims

B7.2b does not resume C12.

B7.2b does not claim direct proof of asymmetric standpoint ontology.

B7.2b tests whether the empirical O1/O2 boundary requires preserved side-direction correspondence, directed closure, and/or factorisation-path lift.
