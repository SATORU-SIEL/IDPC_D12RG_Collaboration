# Private B6C State-Conditioned Operator Selection Audit

Status: local/private screen only. No publication, commit, or push was performed.

Question: Does C select different optimal operators in different C-state regimes, and does this outperform the best global fixed operator?

C remains fixed as the original B5.5 phase-bearing lag+5 event carrier. The C-state classes are observational regimes, not new C definitions.

Selection is cross-validated by held-out labels. The state-to-operator mapping is learned on training labels only.

Operators include the six B6B readout operators plus O7_suppress_event, whose reward is fixed at zero.

## Classification

Partial B6C signal: held-out state-conditioned C selection beats best global fixed and shuffled state labels, but not random operator expectation.

## Comparison Summary

comparison,mean_state_conditioned_reward_z,mean_comparator_reward_z,effect,p_greater,n_events,state_mapping_rate,oracle_hit_rate
state_conditioned_C_selected_vs_best_global_fixed,0.011879729080989361,-0.14797928679763303,0.15902299955046825,0.0003999200159968006,441,0.545816733067729,0.14741035856573706
state_conditioned_C_selected_vs_shuffled_state_labels,0.011879729080989361,-0.09316473010496226,0.1060408173223962,0.009398120375924815,440,0.545816733067729,0.14741035856573706
state_conditioned_C_selected_vs_random_operator,0.011879729080989361,0.005702245590587459,0.005973377660138871,0.4443111377724455,458,0.545816733067729,0.14741035856573706
state_conditioned_C_selected_vs_oracle_upper_bound,0.011879729080989361,1.2239410650761156,-1.2389445373781087,1.0,458,0.545816733067729,0.14741035856573706

## Held-Out Operator Use

cv_selected_operator,cv_selection_source,n_events,mean_reward_z,oracle_hit_rate
O1_lag0_AB,global_fallback,34,-0.20214426005277344,0.058823529411764705
O1_lag0_AB,state_mapping,57,0.3054799272760649,0.19298245614035087
O2_lag5_AB,state_mapping,32,-0.16770604095138428,0.09375
O3_A_C_boundary,global_fallback,88,-0.15732047738015106,0.09090909090909091
O3_A_C_boundary,state_mapping,49,0.3765814217542308,0.22448979591836735
O4_B_C_boundary,global_fallback,52,-0.3285847732983411,0.11538461538461539
O4_B_C_boundary,state_mapping,56,-0.0779440497903503,0.17857142857142858
O5_full_TFC,state_mapping,13,0.3794320575858261,0.15384615384615385
O6_phase_only,state_mapping,64,0.11671701087641789,0.234375
O7_suppress_event,global_fallback,54,0.0,0.1111111111111111
O7_suppress_event,state_mapping,3,0.0,0.0

## Learned Mapping Summary

mapping_type,selected_operator,n_state_fold_mappings,mean_train_reward_z,mean_train_effect_vs_global_best
shuffled_state_labels,O1_lag0_AB,14,0.43605290653948053,0.24898774371595364
shuffled_state_labels,O2_lag5_AB,18,0.43980234792849066,0.4477020785562713
shuffled_state_labels,O3_A_C_boundary,25,0.5244514330315312,0.3685876063339952
shuffled_state_labels,O4_B_C_boundary,24,0.42300467664370617,0.3422620125158336
shuffled_state_labels,O5_full_TFC,20,0.408249870598527,0.37633250090274173
shuffled_state_labels,O6_phase_only,17,0.4543234956891705,0.5066098903325958
shuffled_state_labels,O7_suppress_event,5,0.0,0.20109539797334489
state_conditioned,O1_lag0_AB,26,0.6430036268127897,0.5204944775156792
state_conditioned,O2_lag5_AB,16,0.3718593421914674,0.482698195534852
state_conditioned,O3_A_C_boundary,26,0.6733662587447531,0.3133651746599534
state_conditioned,O4_B_C_boundary,23,0.3537143211350108,0.4093052187295477
state_conditioned,O5_full_TFC,4,0.6390738089962564,0.7095966771130422
state_conditioned,O6_phase_only,25,0.4905651895855372,0.5834954384289559
state_conditioned,O7_suppress_event,3,0.0,0.1748932588745911

## Settings

- n_folds: 5
- min_state_events: 8
- window: 30
- n_perm: 5000
- seed: 60110
