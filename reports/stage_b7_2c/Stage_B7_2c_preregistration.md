# Stage B7.2c Preregistration

## Title

Directed-Provenance C Reconstruction Audit.

## Status

This preregistration is written after the B7.2c proposal email and before execution.

## Background

B7.2a and B7.2b showed that true C-mediated access exceeds simple past/memory controls and several degraded side/direction controls, but does not exceed endpoint-adjacent O1/O2 proxy controls. B7.2b further showed that the boundary is not explained by direction labels, fixed masks, or static scalar closure alone. Endpoint-local direction pairing, train/test correspondence, and directed transport structure remained important.

## Central Question

Can a Directed-Provenance C representation reproduce the endpoint-local O1/O2 advantage without directly using endpoint-adjacent O1/O2 raw values?

## Frozen Evaluation Set

The primary evaluation set is the frozen B6-supported regimes from Stage B7.1, as used in B7.1a, B7.2, B7.2a, and B7.2b.

## Candidate Arms

The audit compares true C-mediated access against the following reconstruction and control arms:

- `scalar_c`: scalar C/memory/state only.
- `directed_c`: side identity and direction identity without endpoint-adjacent O1/O2 raw values.
- `directed_c_direction_swapped`: direction correspondence disrupted without O1/O2 raw values.
- `directed_provenance_c`: side identity, direction identity, construction provenance, phase/strength/TFC/memory bins, FES phase/cluster provenance, and train/test state preservation, without endpoint-adjacent O1/O2 raw values.
- `directed_provenance_side_swapped`: side/provenance mapping disrupted.
- `directed_provenance_endpoint_pair_swapped`: endpoint-pairing proxy disrupted without O1/O2 raw values.
- `directed_provenance_train_test_mismatch`: train uses directed-provenance C while test uses disrupted provenance state.
- `fixed_mask_control`: fixed side/direction mask baseline.
- `static_scalar_closure`: static scalar closure baseline.
- `directed_transport_closure_o1o2`: B7.2b directed transport closure using O1/O2 raw values, retained as an endpoint-adjacent upper-bound reference.
- `endpoint_o1o2_reference`: endpoint-adjacent O1/O2 raw reference.

## O1/O2 Boundary

Arms whose names include `o1o2` are endpoint-adjacent references and are not treated as successful non-endpoint reconstructions. The primary Directed-Provenance C arm must not directly use `O1_lag0_AB_raw` or `O2_lag5_AB_raw` in its state construction.

## Primary Criterion

The primary criterion is whether `directed_provenance_c` bounds true C in the frozen B6-supported regimes at the same directional level as `endpoint_o1o2_reference`, while not directly using endpoint-adjacent O1/O2 raw values.

Operationally, for each frozen regime, true C is compared against each candidate arm by paired sign-flip testing across held-out event pairs. A candidate bounds true C when true C does not significantly outperform the candidate at alpha = 0.05.

## Primary Classification Rules

- `directed_c_sufficient`: `directed_c` bounds true C in all frozen regimes.
- `directed_provenance_required`: `directed_provenance_c` bounds true C where `directed_c` does not.
- `endpoint_pairing_required`: endpoint-pairing disruption causes true C to win where directed-provenance C bounds it.
- `train_test_correspondence_required`: train/test mismatch causes true C to win where directed-provenance C bounds it.
- `directed_transport_required`: directed transport reference bounds true C while static scalar closure does not.
- `fixed_mask_sufficient`: fixed mask bounds true C in all frozen regimes.
- `unresolved_endpoint_structure`: endpoint O1/O2 reference bounds true C but directed-provenance C does not.

## Interpretation Boundary

B7.2c is a reconstruction audit, not an ontology comparison and not a C12 confirmation test. C12/Phi24 reconnection remains outside the primary criterion for this audit.

## Fixed Settings

- n_folds: 5
- min_state_events: 8
- temperature: 0.35
- n_perm: 5000
- alpha: 0.05
- seed: 71203
