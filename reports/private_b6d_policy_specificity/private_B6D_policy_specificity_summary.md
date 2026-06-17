# Private B6D Policy Specificity Audit

Status: local/private screen only. No publication, commit, or push was performed.

Question: Does the C-state conditioned selector work because the C-state to operator correspondence is specific?

C remains fixed as the original B5.5 phase-bearing lag+5 event carrier. State classes are readout regimes, not new C definitions.

Controls:

- within-state operator shuffle
- between-state policy permutation
- operator-label permutation
- equal-frequency random policy
- oracle upper bound

## Classification

Partial B6D signal: true C-state policy beats at least one policy-specificity control but not the full set.

## Comparison Summary

comparison,mean_true_policy_reward_z,mean_comparator_reward_z,effect,p_greater,n_events,state_mapping_rate,oracle_hit_rate
true_C_state_policy_vs_within_state_operator_shuffle,-0.00381603433399618,-0.06612055062923114,0.06628909891134276,0.010397920415916816,464,0.5338645418326693,0.1593625498007968
true_C_state_policy_vs_between_state_policy_permutation,-0.00381603433399618,-0.08567754359630314,0.08292671577833519,0.001799640071985603,464,0.5338645418326693,0.1593625498007968
true_C_state_policy_vs_operator_label_permutation,-0.00381603433399618,-0.06800542134176674,0.06809403816605504,0.01199760047990402,464,0.5338645418326693,0.1593625498007968
true_C_state_policy_vs_equal_frequency_random_policy,-0.00381603433399618,-0.024653493741662206,0.016355614706038624,0.34073185362927416,464,0.5338645418326693,0.1593625498007968
true_C_state_policy_vs_oracle_upper_bound,-0.00381603433399618,1.2239410650761156,-1.2627716977637649,1.0,464,0.5338645418326693,0.1593625498007968

## Held-Out Policy Use

true_policy_operator,true_policy_source,n_events,mean_reward_z,oracle_hit_rate
O1_lag0_AB,global_fallback,97,-0.18073496195756195,0.13402061855670103
O1_lag0_AB,state_mapping,52,0.21807360036359916,0.19230769230769232
O2_lag5_AB,global_fallback,47,-0.14695587388800632,0.10638297872340426
O2_lag5_AB,state_mapping,32,0.05055683532763762,0.15625
O3_A_C_boundary,state_mapping,58,0.5153926421552076,0.25862068965517243
O4_B_C_boundary,global_fallback,54,-0.2271690622137822,0.14814814814814814
O4_B_C_boundary,state_mapping,51,-0.11557530628893618,0.0784313725490196
O5_full_TFC,global_fallback,36,-0.20548952210345628,0.1111111111111111
O5_full_TFC,state_mapping,14,0.33492571533903986,0.21428571428571427
O6_phase_only,state_mapping,48,-0.012380615693531565,0.2708333333333333
O7_suppress_event,state_mapping,13,0.0,0.0

## Learned Policy Summary

selected_operator,n_state_fold_mappings,mean_selected_train_reward,mean_global_best_train_reward
O1_lag0_AB,22,0.6705426748389117,0.31702155543691807
O2_lag5_AB,16,0.3845937174351525,0.10262753490982016
O3_A_C_boundary,31,0.6016216050576216,-0.01946610462707691
O4_B_C_boundary,21,0.38005735548723835,0.00998400962725008
O5_full_TFC,4,0.6556365136580181,0.4806926873525633
O6_phase_only,25,0.4959227661721298,-0.0820933083660255
O7_suppress_event,7,0.0,-0.22954238529495283

## Settings

- n_folds: 5
- min_state_events: 8
- n_control_draws: 300
- window: 30
- n_perm: 5000
- seed: 60210
