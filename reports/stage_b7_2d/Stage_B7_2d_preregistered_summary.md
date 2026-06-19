# Stage B7.2d Directed-C Sufficiency and Provenance-Dilution Audit

Status: executed after writing Stage_B7_2d_preregistration.md.

## Result

- frozen B6-supported regimes tested: 11 / 24
- directed_c_compact bounds true C: 11 / 11; lets true C win: 0 / 11
- directed_c_minimal bounds true C: 9 / 11; lets true C win: 2 / 11
- directed_c_with_side_polarity bounds true C: 11 / 11; lets true C win: 0 / 11
- directed_c_with_endpoint_free_transport bounds true C: 11 / 11; lets true C win: 0 / 11
- provenance_add_phase_strength bounds true C: 11 / 11; lets true C win: 0 / 11
- provenance_add_tfc_memory bounds true C: 9 / 11; lets true C win: 2 / 11
- provenance_add_fes bounds true C: 11 / 11; lets true C win: 0 / 11
- full_directed_provenance bounds true C: 9 / 11; lets true C win: 2 / 11
- regularized_directed_provenance bounds true C: 11 / 11; lets true C win: 0 / 11
- provenance_shuffled_control bounds true C: 9 / 11; lets true C win: 2 / 11
- endpoint_o1o2_reference bounds true C: 11 / 11; lets true C win: 0 / 11
- directed_transport_closure_o1o2 bounds true C: 11 / 11; lets true C win: 0 / 11

## Primary Classification

criterion,supported,basis
compact_directed_c_near_sufficient,True,directed_c_compact bounds C 11/11
minimal_direction_sufficient,False,directed_c_minimal bounds C 9/11
side_polarity_required,True,side_polarity bounds C 11/11; minimal bounds C 9/11
endpoint_free_transport_required,False,endpoint_free_transport bounds C 11/11; side_polarity bounds C 11/11
provenance_dilution_supported,False,compact bounds C 11/11; best provenance-addition bounds C 11/11
wrong_provenance_supported,False,best provenance-addition bounds C 11/11; endpoint_o1o2_reference bounds C 11/11
regularized_provenance_recovers_signal,True,regularized bounds C 11/11; compact bounds C 11/11
endpoint_gap_persists,False,best endpoint-free bounds C 11/11; endpoint_o1o2_reference bounds C 11/11
unresolved_directed_c_boundary,False,best endpoint-free bounds C 11/11; endpoint_o1o2_reference bounds C 11/11

## Component Summary

control_level,frozen_regimes,c_beats_count,control_bounds_c_count,mean_true_minus_control,median_true_minus_control
directed_c_compact,11,0,11,0.03890508227996258,0.04159201530322596
directed_c_minimal,11,2,9,0.05422571964838913,0.0494829072139058
directed_c_with_side_polarity,11,0,11,0.03340371068530047,0.027685179155321996
directed_c_with_endpoint_free_transport,11,0,11,-0.06589241507066788,-0.0532605093356772
provenance_add_phase_strength,11,0,11,0.03204642183398125,0.024316853731785475
provenance_add_tfc_memory,11,2,9,0.07002115411775213,0.07977213837143252
provenance_add_fes,11,0,11,0.05382119647118742,0.061973427176141516
full_directed_provenance,11,2,9,0.0632191690533376,0.05910817988331549
regularized_directed_provenance,11,0,11,0.03890508227996258,0.04159201530322596
provenance_shuffled_control,11,2,9,0.0632191690533376,0.05910817988331549
endpoint_o1o2_reference,11,0,11,-0.28281785382431274,-0.3442018738178117
directed_transport_closure_o1o2,11,0,11,-0.1260129840390793,-0.15187748300800966

## Frozen-Regime Pass Matrix

mode,endpoint,direction,directed_c_compact,directed_c_minimal,directed_c_with_endpoint_free_transport,directed_c_with_side_polarity,directed_transport_closure_o1o2,endpoint_o1o2_reference,full_directed_provenance,provenance_add_fes,provenance_add_phase_strength,provenance_add_tfc_memory,provenance_shuffled_control,regularized_directed_provenance
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,False,False,False,False,False,False,False,False,False,False,False,False
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,False,True,False,False,False,False,True,False,False,True,True,False
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,False,False,False,False,False,False,False,False,False,False,False,False
gmr72_phase_conditioned,z_reward,A_to_C_to_B,False,False,False,False,False,False,False,False,False,False,False,False
gmr72_phase_conditioned,z_reward,B_to_C_to_A,False,False,False,False,False,False,False,False,False,False,False,False
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,False,False,False,False,False,False,False,False,False,False,False,False
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,False,False,False,False,False,False,False,False,False,False,False,False
linear_c_state,rank_reward,A_to_C_to_B,False,True,False,False,False,False,True,False,False,True,True,False
linear_c_state,rank_reward,B_to_C_to_A,False,False,False,False,False,False,False,False,False,False,False,False
linear_c_state,z_reward,A_to_C_to_B,False,False,False,False,False,False,False,False,False,False,False,False
linear_c_state,z_reward,B_to_C_to_A,False,False,False,False,False,False,False,False,False,False,False,False

## Interpretation Boundary

B7.2d diagnoses why compact directed C remained partially strong in B7.2c while full directed provenance collapsed. It is not a C12 confirmation test.

## Settings

- n_folds: 5
- min_state_events: 8
- temperature: 0.35
- n_perm: 5000
- alpha: 0.05
- seed: 71204
