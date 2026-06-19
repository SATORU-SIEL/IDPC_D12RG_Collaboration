# Stage B7.2d Result Report and B7.2e Side-Polarity Proposal

## Status

B7.2d was preregistered and executed after the B7.2c result.

This report summarizes B7.2d and proposes B7.2e as a side-polarity decomposition audit.

## B7.2d Central Question

B7.2d asked why compact `directed_c` was partially strong in B7.2c while expanded `directed_provenance_c` collapsed.

The key B7.2c puzzle was:

- compact `directed_c` bounded true C in `9 / 11`;
- expanded `directed_provenance_c` bounded true C in `0 / 11`;
- endpoint-adjacent O1/O2 references bounded true C in `11 / 11`.

## B7.2d Main Result

Frozen B6-supported regimes tested:

- `11 / 24`

Key results:

- `directed_c_compact`: bounds true C `11 / 11`
- `directed_c_minimal`: bounds true C `9 / 11`
- `directed_c_with_side_polarity`: bounds true C `11 / 11`
- `directed_c_with_endpoint_free_transport`: bounds true C `11 / 11`
- `provenance_add_phase_strength`: bounds true C `11 / 11`
- `provenance_add_tfc_memory`: bounds true C `9 / 11`
- `provenance_add_fes`: bounds true C `11 / 11`
- `full_directed_provenance`: bounds true C `9 / 11`
- `regularized_directed_provenance`: bounds true C `11 / 11`
- `endpoint_o1o2_reference`: bounds true C `11 / 11`
- `directed_transport_closure_o1o2`: bounds true C `11 / 11`

## Primary Classification

- `compact_directed_c_near_sufficient`: supported
- `minimal_direction_sufficient`: not supported
- `side_polarity_required`: supported
- `endpoint_free_transport_required`: not supported
- `provenance_dilution_supported`: not supported
- `wrong_provenance_supported`: not supported
- `regularized_provenance_recovers_signal`: supported
- `endpoint_gap_persists`: not supported by the binary win/loss criterion
- `unresolved_directed_c_boundary`: not supported by the binary win/loss criterion

## Interpretation

B7.2d changes the B7.2c reading.

B7.2c suggested that endpoint-free Directed-Provenance C could not reconstruct the O1/O2 boundary.

B7.2d shows a more precise boundary:

- compact directed C is near-sufficient by the binary criterion;
- minimal direction alone is not sufficient;
- adding side polarity closes the binary gap;
- regularized provenance recovers the compact directed signal;
- unregularized provenance can still weaken the signal.

So the core endpoint-free structure is not broad provenance.

The core endpoint-free structure appears to be:

`direction + side + side polarity`

## Important Caveat

The binary criterion says true C does not significantly outperform the compact directed / side-polarity arms.

That does not mean the endpoint-free arms equal the endpoint-adjacent O1/O2 references in effect size.

Effect-size ordering remains informative:

- `endpoint_o1o2_reference`: mean true-minus-control = `-0.2828`
- `directed_transport_closure_o1o2`: mean true-minus-control = `-0.1260`
- `directed_c_with_endpoint_free_transport`: mean true-minus-control = `-0.0659`
- `directed_c_with_side_polarity`: mean true-minus-control = `0.0334`
- `directed_c_compact`: mean true-minus-control = `0.0389`

Thus, B7.2d does not erase the O1/O2 upper-bound result.

It shows that endpoint-free directed side-polarity structure is sufficient to remove true C's significant advantage under the binary criterion, while O1/O2 remains a stronger upper-bound by effect size.

## Why Side Polarity Now Matters

B7.2d identifies side polarity as the minimal addition that closes the binary gap:

- `directed_c_minimal`: bounds true C `9 / 11`
- `directed_c_with_side_polarity`: bounds true C `11 / 11`

This means that the next empirical question is no longer only:

`Is direction required?`

It is:

`What does side polarity represent?`

Possibilities include:

1. `ac_bc_difference`

Side polarity may simply encode the signed A-C vs B-C contrast.

2. `receiver_giver_polarity`

Side polarity may encode which side is in the receiving/giving role under the directed correspondence.

3. `standpoint_polarity`

Side polarity may encode whose standpoint is preserved in the A-to-C-to-B or B-to-C-to-A crossing.

4. `endpoint_adjacency_proxy`

Side polarity may still be an endpoint-adjacent proxy in disguise, despite not directly using O1/O2 raw values.

5. `phase_or_tfc_surrogate`

Side polarity may be carrying phase/TFC structure indirectly.

## B7.2e Follow-up Proposal

### Title

Stage B7.2e: Side-Polarity Decomposition and Standpoint Meaning Audit.

### Central Question

What does the side-polarity term that closes the B7.2d directed-C gap actually represent?

### Candidate Interpretations

B7.2e should compare:

1. `unsigned_side_gap`

Uses `|A_C - B_C|`.

Question: is magnitude of side asymmetry sufficient?

2. `signed_ac_minus_bc`

Uses `A_C - B_C` without direction-specific standpoint mapping.

Question: is ordinary signed A-C/B-C contrast sufficient?

3. `direction_conditioned_side_polarity`

Uses the B7.2d polarity:

- for `A_to_C_to_B`, B-side standpoint polarity;
- for `B_to_C_to_A`, A-side standpoint polarity.

Question: is direction-conditioned polarity required?

4. `polarity_sign_only`

Keeps only the sign of side polarity.

Question: is sign enough, or is magnitude required?

5. `polarity_magnitude_only`

Keeps only the magnitude of side polarity.

Question: is asymmetry strength enough without orientation?

6. `receiver_side_only`

Keeps the receiving-side identity/value only.

Question: is side polarity just receiver-side access?

7. `giver_side_only`

Keeps the giving-side identity/value only.

Question: is side polarity just giver-side access?

8. `standpoint_polarity_preserved`

Preserves the asymmetric standpoint mapping:

- A-to-C-to-B uses B-side standpoint polarity;
- B-to-C-to-A uses A-side standpoint polarity.

Question: does the polarity correspond to standpoint preservation?

9. `standpoint_polarity_inverted`

Inverts the standpoint polarity mapping while preserving marginal distributions.

Question: does inversion collapse the boundary?

10. `phase_tfc_matched_polarity_control`

Matches phase/TFC bins while disrupting side-polarity mapping.

Question: is side polarity only a phase/TFC surrogate?

11. `endpoint_o1o2_reference`

Retains the endpoint-adjacent upper-bound reference.

### Primary Criteria

B7.2e should classify:

- whether side polarity is magnitude-only or sign-sensitive;
- whether ordinary A-C/B-C contrast is sufficient;
- whether direction-conditioned polarity is required;
- whether receiver/giver polarity explains the effect;
- whether standpoint-preserving polarity is required;
- whether the side-polarity signal survives phase/TFC matching;
- whether O1/O2 remains stronger by effect size.

### Primary Classification

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

### Interpretation Rules

If unsigned magnitude is sufficient, side polarity is likely ordinary side asymmetry.

If sign is required, polarity orientation matters.

If direction-conditioned polarity beats ordinary signed A-C/B-C contrast, then the effect is not merely an A-C/B-C difference.

If standpoint-preserved polarity survives and standpoint-inverted polarity collapses, B7.2e supports the standpoint interpretation.

If phase/TFC-matched controls preserve the signal, side polarity may be a phase/TFC surrogate.

If endpoint O1/O2 remains stronger by effect size, O1/O2 should remain an upper-bound reference even if endpoint-free side polarity is sufficient by binary criterion.

## C12 Positioning

B7.2d makes C12 reconnection more plausible than B7.2c did, because endpoint-free compact directed side-polarity C now bounds true C in the frozen regimes.

However, C12 should still not be reconnected to an uninterpreted side-polarity representation.

B7.2e should first determine what side polarity means.

Only then should the next C12 reconnection compare:

- previous C12 bridge;
- compact directed C;
- side-polarity C;
- standpoint-polarity C, if B7.2e supports it;
- O1/O2 upper-bound diagnostic.

## Conclusion

B7.2d identifies side polarity as the next key variable.

The immediate next step is not broader C12/Phi24 reconnection, but B7.2e:

`What is side polarity?`

If side polarity is merely A-C/B-C asymmetry, the result remains a directional correspondence finding.

If side polarity is standpoint-conditioned and inversion-sensitive, it becomes much closer to the Subjectivity Intersection interpretation.
