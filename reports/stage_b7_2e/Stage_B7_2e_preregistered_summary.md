# Stage B7.2e Side-Polarity Decomposition and Standpoint Meaning Audit

Status: executed after writing Stage_B7_2e_preregistration.md.

## Result

- frozen B6-supported regimes tested: 11 / 24
- unsigned_side_gap bounds true C: 11 / 11; lets true C win: 0 / 11
- signed_ac_minus_bc bounds true C: 5 / 11; lets true C win: 6 / 11
- polarity_sign_only bounds true C: 6 / 11; lets true C win: 5 / 11
- polarity_magnitude_only bounds true C: 11 / 11; lets true C win: 0 / 11
- direction_conditioned_side_polarity bounds true C: 5 / 11; lets true C win: 6 / 11
- receiver_side_only bounds true C: 11 / 11; lets true C win: 0 / 11
- giver_side_only bounds true C: 5 / 11; lets true C win: 6 / 11
- standpoint_polarity_preserved bounds true C: 11 / 11; lets true C win: 0 / 11
- standpoint_polarity_inverted bounds true C: 7 / 11; lets true C win: 4 / 11
- phase_tfc_matched_polarity_control bounds true C: 7 / 11; lets true C win: 4 / 11
- endpoint_o1o2_reference bounds true C: 11 / 11; lets true C win: 0 / 11

## Primary Classification

criterion,supported,basis
unsigned_side_gap_sufficient,True,unsigned_side_gap bounds C 11/11
signed_ac_bc_contrast_sufficient,False,signed_ac_minus_bc bounds C 5/11
polarity_sign_sufficient,False,polarity_sign_only bounds C 6/11
polarity_magnitude_sufficient,True,polarity_magnitude_only bounds C 11/11
direction_conditioned_polarity_required,False,direction_conditioned_side_polarity bounds C 5/11; signed bounds C 5/11; unsigned bounds C 11/11
receiver_side_sufficient,True,receiver_side_only bounds C 11/11
giver_side_sufficient,False,giver_side_only bounds C 5/11
standpoint_polarity_supported,True,standpoint_polarity_preserved bounds C 11/11
standpoint_inversion_breaks_signal,True,preserved bounds C 11/11; inverted bounds C 7/11
phase_tfc_surrogate_supported,False,phase_tfc_matched_polarity_control bounds C 7/11
endpoint_o1o2_effect_size_gap_persists,True,endpoint_o1o2 mean true-minus-control -0.2314
unresolved_side_polarity_meaning,False,no endpoint-free side-polarity interpretation uniquely supported

## Component Summary

control_level,frozen_regimes,c_beats_count,control_bounds_c_count,mean_true_minus_control,median_true_minus_control
unsigned_side_gap,11,0,11,-0.031176410859243452,-0.002547831462513645
signed_ac_minus_bc,11,6,5,0.03607589340925038,0.018756104829862022
polarity_sign_only,11,5,6,0.033518491801330826,0.017662847169743895
polarity_magnitude_only,11,0,11,-0.031176410859243452,-0.002547831462513645
direction_conditioned_side_polarity,11,6,5,0.03543555499264472,0.018756104829862022
receiver_side_only,11,0,11,0.005380561194694871,0.011577339194660701
giver_side_only,11,6,5,0.005973896434234385,0.01810402682959531
standpoint_polarity_preserved,11,0,11,0.00811329772108211,0.012395424448780687
standpoint_polarity_inverted,11,4,7,0.008536588201576488,0.017051619734218836
phase_tfc_matched_polarity_control,11,4,7,0.03573304455839241,0.014006358200864568
endpoint_o1o2_reference,11,0,11,-0.23144781388282556,-0.24858932538534545

## Frozen-Regime Pass Matrix

mode,endpoint,direction,direction_conditioned_side_polarity,endpoint_o1o2_reference,giver_side_only,phase_tfc_matched_polarity_control,polarity_magnitude_only,polarity_sign_only,receiver_side_only,signed_ac_minus_bc,standpoint_polarity_inverted,standpoint_polarity_preserved,unsigned_side_gap
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,True,False,True,False,False,True,False,True,False,False,False
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,False,False,False,False,False,False,False,False,False,False,False
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,True,False,True,True,False,True,False,True,True,False,False
gmr72_phase_conditioned,z_reward,A_to_C_to_B,False,False,False,False,False,False,False,False,False,False,False
gmr72_phase_conditioned,z_reward,B_to_C_to_A,True,False,True,True,False,True,False,True,True,False,False
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,False,False,False,False,False,False,False,False,False,False,False
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,True,False,True,False,False,False,False,True,False,False,False
linear_c_state,rank_reward,A_to_C_to_B,False,False,False,False,False,False,False,False,False,False,False
linear_c_state,rank_reward,B_to_C_to_A,True,False,True,True,False,True,False,True,True,False,False
linear_c_state,z_reward,A_to_C_to_B,False,False,False,False,False,False,False,False,False,False,False
linear_c_state,z_reward,B_to_C_to_A,True,False,True,True,False,True,False,True,True,False,False

## Interpretation Boundary

B7.2e decomposes side polarity. It is not a C12 confirmation test.

## Settings

- n_folds: 5
- min_state_events: 8
- temperature: 0.35
- n_perm: 5000
- alpha: 0.05
- seed: 71205
