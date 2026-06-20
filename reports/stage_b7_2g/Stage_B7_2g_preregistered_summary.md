# Stage B7.2g Receiver-Standpoint Parity Mismatch Audit

Status: executed after writing Stage_B7_2g_preregistration.md.

## Primary Classification

criterion,supported,basis
parity_mismatch_supported,True,"matched means [0.028916789042785364, 0.028787585657049697]; mismatched means [0.022324548395431524, 0.022315283393250382]; margin 0.005"
receiver_only_explains_effect,True,receiver_only mean 0.0244; best mismatch 0.0223
standpoint_only_explains_effect,False,best standpoint-only mean 0.0288; best mismatch 0.0223
sign_or_magnitude_explains_effect,True,best sign/magnitude mean 0.0206; best mismatch 0.0223
complexity_shuffle_explains_effect,False,best shuffled mean 0.0464; best mismatch 0.0223
ab_exchange_consistent,True,ab_exchange bounds 11; mismatch bounds 11
endpoint_o1o2_effect_size_gap_persists,True,endpoint mean -0.2417; endpoint-free min 0.0206
parity_hypothesis_falsified,True,parity unsupported or simpler falsification arm explains the effect
unresolved_parity_boundary,False,no decisive parity or falsification result

## Component Summary

control_level,frozen_regimes,c_beats_count,control_bounds_c_count,mean_true_minus_control,median_true_minus_control
receiver_preserved__standpoint_preserved,11,4,7,0.028916789042785364,0.01878992773380159
receiver_preserved__standpoint_inverted,11,0,11,0.022324548395431524,0.015266979676917201
receiver_inverted__standpoint_preserved,11,0,11,0.022315283393250382,0.015095757331174775
receiver_inverted__standpoint_inverted,11,0,11,0.028787585657049697,0.02811912391760916
receiver_only,11,4,7,0.024382741962516018,0.013559809245982182
standpoint_only_preserved,11,4,7,0.028916789042785364,0.01878992773380159
standpoint_only_inverted,11,0,11,0.028787585657049697,0.02811912391760916
standpoint_sign_only,11,5,6,0.04128600550949257,0.042124768927194536
standpoint_magnitude_only,11,2,9,0.029506339881372277,0.031381056553871745
receiver_plus_magnitude,11,0,11,0.020602516634416077,0.01573893337601093
receiver_plus_standpoint_sign,11,4,7,0.024470583386602195,0.013559809245982182
complexity_matched_shuffled_pair,11,8,3,0.07079554633363762,0.06551835666076063
parity_label_shuffled,11,5,6,0.04640965038868847,0.021305127668651596
ab_exchange_parity_mismatch,11,0,11,0.022315283393250382,0.015095757331174775
endpoint_o1o2_reference,11,0,11,-0.24166787086369682,-0.3046154780792147

## Frozen-Regime Pass Matrix

mode,endpoint,direction,ab_exchange_parity_mismatch,complexity_matched_shuffled_pair,endpoint_o1o2_reference,parity_label_shuffled,receiver_inverted__standpoint_inverted,receiver_inverted__standpoint_preserved,receiver_only,receiver_plus_magnitude,receiver_plus_standpoint_sign,receiver_preserved__standpoint_inverted,receiver_preserved__standpoint_preserved,standpoint_magnitude_only,standpoint_only_inverted,standpoint_only_preserved,standpoint_sign_only
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,False,True,False,True,False,False,True,False,True,False,True,True,False,True,True
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,False,True,False,False,False,False,False,False,False,False,False,False,False,False,False
gmr72_phase_conditioned,z_reward,A_to_C_to_B,False,True,False,True,False,False,True,False,True,False,True,False,False,True,True
gmr72_phase_conditioned,z_reward,B_to_C_to_A,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,False,True,False,True,False,False,False,False,False,False,False,False,False,False,False
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False
linear_c_state,rank_reward,A_to_C_to_B,False,True,False,True,False,False,True,False,True,False,True,True,False,True,True
linear_c_state,rank_reward,B_to_C_to_A,False,True,False,False,False,False,False,False,False,False,False,False,False,False,True
linear_c_state,z_reward,A_to_C_to_B,False,True,False,True,False,False,True,False,True,False,True,False,False,True,True
linear_c_state,z_reward,B_to_C_to_A,False,True,False,False,False,False,False,False,False,False,False,False,False,False,False

## Settings

- n_folds: 5
- min_state_events: 8
- temperature: 0.35
- n_perm: 5000
- alpha: 0.05
- seed: 71208
