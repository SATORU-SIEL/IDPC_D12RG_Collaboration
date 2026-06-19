# Stage B7.2c Result Report and B7.2d Follow-up Proposal

## Status

B7.2c was proposed by email, preregistered, and executed.

This report summarizes the result and proposes B7.2d as a follow-up diagnostic.

## B7.2c Question

B7.2c asked whether the endpoint-local O1/O2 advantage that survived B7.2b could be reconstructed without directly using endpoint-adjacent O1/O2 raw values.

The primary reconstruction arm was:

`directed_provenance_c`

This arm preserved side identity, direction identity, endpoint-pairing proxy, train/test state preservation, and construction provenance, but did not directly use:

- `O1_lag0_AB_raw`
- `O2_lag5_AB_raw`

## Main Result

Frozen B6-supported regimes tested:

- `11 / 24`

Key results:

- `scalar_c`: true C wins `11 / 11`
- `directed_c`: true C wins `2 / 11`; control bounds true C `9 / 11`
- `directed_c_direction_swapped`: true C wins `4 / 11`; control bounds true C `7 / 11`
- `directed_c_side_shuffled`: true C wins `11 / 11`
- `directed_provenance_c`: true C wins `11 / 11`
- `directed_provenance_side_swapped`: true C wins `11 / 11`
- `directed_provenance_endpoint_pair_swapped`: true C wins `11 / 11`
- `directed_provenance_train_test_mismatch`: true C wins `11 / 11`
- `fixed_mask_control`: true C wins `11 / 11`
- `static_scalar_closure`: true C wins `11 / 11`
- `directed_transport_closure_o1o2`: O1/O2 reference bounds true C `11 / 11`
- `endpoint_o1o2_reference`: O1/O2 reference bounds true C `11 / 11`

## Primary Classification

- `directed_c_sufficient`: not supported
- `directed_provenance_required`: not supported
- `endpoint_pairing_required`: not supported under this implementation
- `train_test_correspondence_required`: not supported under this implementation
- `directed_transport_required`: supported, but only in the O1/O2-containing reference arm
- `fixed_mask_sufficient`: not supported
- `unresolved_endpoint_structure`: supported

## Interpretation

B7.2c did not reconstruct the endpoint-local O1/O2 boundary from non-O1/O2 Directed-Provenance C features.

The important asymmetry is:

- O1/O2-containing references remain strong.
- Compact endpoint-free `directed_c` is partially strong.
- Expanded endpoint-free `directed_provenance_c` collapses completely.

This means that the B7.2b endpoint-local structure is still not captured by the current C-side provenance reconstruction.

The result should not be read as showing that direction is irrelevant. In fact, `directed_c` was the strongest non-O1/O2 reconstruction arm, bounding true C in `9 / 11` frozen regimes.

The sharper result is:

`directed_c` is close but incomplete, while the current expanded `directed_provenance_c` is not a valid reconstruction of the endpoint-local O1/O2 boundary.

## Why This Matters

B7.2c blocks an immediate C12 reconnection using the current Directed-Provenance C representation.

The reason is not that all endpoint-free direction structure failed. The reason is more specific:

- compact direction/side structure retained substantial explanatory power;
- side shuffling destroyed that power;
- provenance expansion destroyed that power;
- O1/O2 endpoint-adjacent references still bounded true C fully.

So the immediate problem is not simply:

`C lacks direction`

It is:

`the current provenance expansion does not preserve the useful compact directed structure and does not recover the missing endpoint-local O1/O2 structure`

## B7.2d Follow-up Proposal

### Title

Stage B7.2d: Directed-C Sufficiency and Provenance-Dilution Audit.

### Central Question

Why does compact `directed_c` bound true C in `9 / 11` frozen regimes, while expanded `directed_provenance_c` collapses to `0 / 11`?

### Working Hypotheses

1. `provenance_dilution`

The added provenance variables fragment the state space and dilute the compact side/direction signal.

2. `wrong_provenance`

The selected provenance variables do not encode the endpoint-local structure that O1/O2 carries.

3. `over-specific_state_failure`

The Directed-Provenance C state is too high-dimensional for the frozen regime sample size, causing unreliable train/test mappings.

4. `compact_direction_boundary`

The useful endpoint-free structure is mostly compact side/direction structure, not expanded provenance.

5. `true_endpoint_gap`

Even optimized endpoint-free directed C cannot reproduce the full O1/O2 boundary, implying that O1/O2 still contains endpoint-adjacent information absent from C.

### Planned Arms

1. `directed_c_compact`

The B7.2c `directed_c` arm, retained as the reference endpoint-free reconstruction.

2. `directed_c_minimal`

Direction identity plus side identity only.

3. `directed_c_with_side_polarity`

Direction identity, side identity, and side polarity only.

4. `directed_c_with_endpoint_free_transport`

Direction identity, side identity, side polarity, A-C/B-C contrast, and TFC structure, excluding O1/O2 raw.

5. `provenance_add_phase_strength`

Compact directed C plus phase and strength provenance.

6. `provenance_add_tfc_memory`

Compact directed C plus TFC and memory provenance.

7. `provenance_add_fes`

Compact directed C plus FES phase/cluster provenance.

8. `full_directed_provenance`

The B7.2c `directed_provenance_c` arm.

9. `regularized_directed_provenance`

A backoff version of directed provenance that falls back from full provenance to compact directed C when state support is too sparse.

10. `provenance_shuffled_controls`

Matched controls that preserve marginal provenance distributions while breaking side/direction correspondence.

11. `endpoint_o1o2_reference`

The endpoint-adjacent upper-bound reference.

12. `directed_transport_closure_o1o2`

The O1/O2-containing directed transport reference from B7.2b/B7.2c.

### Primary Criteria

B7.2d should classify:

- whether compact directed C is genuinely near-sufficient;
- whether provenance expansion fails because of state fragmentation;
- whether any endpoint-free provenance component improves over compact directed C;
- whether regularized/backoff provenance recovers the compact directed signal;
- whether the remaining endpoint gap persists even after optimized endpoint-free directed C.

### Primary Classification

- `compact_directed_c_near_sufficient`
- `minimal_direction_sufficient`
- `side_polarity_required`
- `endpoint_free_transport_required`
- `provenance_dilution_supported`
- `wrong_provenance_supported`
- `regularized_provenance_recovers_signal`
- `endpoint_gap_persists`
- `unresolved_directed_c_boundary`

### Interpretation Rules

If compact directed C remains strong and all provenance additions weaken it, then B7.2d supports `provenance_dilution`.

If one provenance family improves over compact directed C, then that family becomes the candidate reconstruction path.

If regularized provenance recovers the compact signal, then B7.2c failed because the full provenance state was too sparse or over-specific.

If optimized endpoint-free directed C still cannot match O1/O2 references, then the endpoint-local O1/O2 boundary remains unresolved.

### C12 Positioning

C12 reconnection should remain paused until B7.2d resolves whether the endpoint-free directed C representation can be improved beyond the compact `directed_c` result.

The next C12 comparison should not use the failed B7.2c full Directed-Provenance C arm.

The viable candidates after B7.2c are:

- compact directed C, if B7.2d confirms near-sufficiency;
- regularized directed provenance, if B7.2d recovers the signal;
- or O1/O2-boundary-aware diagnostic C, if the endpoint gap persists.

## Conclusion

B7.2c gives a useful negative result.

It shows that the current Directed-Provenance C reconstruction does not recover the endpoint-local O1/O2 boundary.

But it also shows that compact directed C is not dead: it bounds true C in `9 / 11` frozen regimes, and side shuffling destroys the signal.

Therefore the right next step is B7.2d, not immediate C12 reconnection.

B7.2d should diagnose whether the compact directed C signal can be made sufficient, or whether the remaining O1/O2 boundary reflects endpoint-adjacent information still absent from C.
