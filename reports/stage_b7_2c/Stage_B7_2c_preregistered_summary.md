# Stage B7.2c Directed-Provenance C Reconstruction Audit

Status: executed after writing Stage_B7_2c_preregistration.md and Stage_B7_2c_plan_email.md.

## Result

- frozen B6-supported regimes tested: 11 / 24
- scalar_c bounds true C: 0 / 11; lets true C win: 11 / 11
- directed_c bounds true C: 9 / 11; lets true C win: 2 / 11
- directed_c_direction_relabel bounds true C: 9 / 11; lets true C win: 2 / 11
- directed_c_direction_swapped bounds true C: 7 / 11; lets true C win: 4 / 11
- directed_c_side_shuffled bounds true C: 0 / 11; lets true C win: 11 / 11
- directed_provenance_c bounds true C: 0 / 11; lets true C win: 11 / 11
- directed_provenance_side_swapped bounds true C: 0 / 11; lets true C win: 11 / 11
- directed_provenance_endpoint_pair_swapped bounds true C: 0 / 11; lets true C win: 11 / 11
- directed_provenance_train_test_mismatch bounds true C: 0 / 11; lets true C win: 11 / 11
- fixed_mask_control bounds true C: 0 / 11; lets true C win: 11 / 11
- static_scalar_closure bounds true C: 0 / 11; lets true C win: 11 / 11
- directed_transport_closure_o1o2 bounds true C: 11 / 11; lets true C win: 0 / 11
- endpoint_o1o2_reference bounds true C: 11 / 11; lets true C win: 0 / 11

## Primary Classification

criterion,supported,basis
directed_c_sufficient,False,directed_c bounds C 9/11
directed_provenance_required,False,directed_provenance_c bounds C 0/11; directed_c bounds C 9/11
endpoint_pairing_required,False,directed_provenance_c bounds C 0/11; endpoint_pair_swapped bounds C 0/11
train_test_correspondence_required,False,directed_provenance_c bounds C 0/11; train_test_mismatch bounds C 0/11
directed_transport_required,True,directed_transport_closure_o1o2 bounds C 11/11; static_scalar_closure lets C win 11/11
fixed_mask_sufficient,False,fixed_mask_control bounds C 0/11
unresolved_endpoint_structure,True,endpoint_o1o2_reference bounds C 11/11; directed_provenance_c bounds C 0/11

## Component Summary

control_level,frozen_regimes,c_beats_count,control_bounds_c_count,mean_true_minus_control,median_true_minus_control
scalar_c,11,11,0,0.08085664314418708,0.09803644401906743
directed_c,11,2,9,0.027005631096161165,0.022688512528906583
directed_c_direction_relabel,11,2,9,0.027005631096161165,0.022688512528906583
directed_c_direction_swapped,11,4,7,0.027196755038891553,0.031049755221825518
directed_c_side_shuffled,11,11,0,0.08779262897034007,0.10638258998116369
directed_provenance_c,11,11,0,0.08816857574373745,0.10473379547183417
directed_provenance_side_swapped,11,11,0,0.08816857574373745,0.10473379547183417
directed_provenance_endpoint_pair_swapped,11,11,0,0.08816857574373745,0.10473379547183417
directed_provenance_train_test_mismatch,11,11,0,0.08816857574373745,0.10473379547183417
fixed_mask_control,11,11,0,0.06475861341253714,0.0723915466606093
static_scalar_closure,11,11,0,0.09044786998866422,0.10300759596389047
directed_transport_closure_o1o2,11,0,11,-0.05090654254160484,-0.07851608948648503
endpoint_o1o2_reference,11,0,11,-0.2165284157152471,-0.2903876355724564

## Frozen-Regime Pass Matrix

mode,endpoint,direction,directed_c,directed_c_direction_relabel,directed_c_direction_swapped,directed_c_side_shuffled,directed_provenance_c,directed_provenance_endpoint_pair_swapped,directed_provenance_side_swapped,directed_provenance_train_test_mismatch,directed_transport_closure_o1o2,endpoint_o1o2_reference,fixed_mask_control,scalar_c,static_scalar_closure
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,True,True,True,True,True,True,True,True,False,False,True,True,True
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,False,False,False,True,True,True,True,True,False,False,True,True,True
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,False,False,True,True,True,True,True,True,False,False,True,True,True
gmr72_phase_conditioned,z_reward,A_to_C_to_B,False,False,False,True,True,True,True,True,False,False,True,True,True
gmr72_phase_conditioned,z_reward,B_to_C_to_A,False,False,False,True,True,True,True,True,False,False,True,True,True
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,False,False,False,True,True,True,True,True,False,False,True,True,True
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,True,True,True,True,True,True,True,True,False,False,True,True,True
linear_c_state,rank_reward,A_to_C_to_B,False,False,False,True,True,True,True,True,False,False,True,True,True
linear_c_state,rank_reward,B_to_C_to_A,False,False,True,True,True,True,True,True,False,False,True,True,True
linear_c_state,z_reward,A_to_C_to_B,False,False,False,True,True,True,True,True,False,False,True,True,True
linear_c_state,z_reward,B_to_C_to_A,False,False,False,True,True,True,True,True,False,False,True,True,True

## Interpretation

B7.2c tests whether the B7.2b endpoint-local O1/O2 boundary can be reconstructed without directly using endpoint-adjacent O1/O2 raw values.

Arms containing `o1o2` are retained as endpoint-adjacent references. A successful Directed-Provenance C reconstruction requires the non-O1/O2 `directed_provenance_c` arm to bound true C in the frozen regimes.

## Settings

- n_folds: 5
- min_state_events: 8
- temperature: 0.35
- n_perm: 5000
- alpha: 0.05
- seed: 71203
