# Private B6E Balanced Operator Pool Audit

Status: local/private screen only. No publication, commit, or push was performed.

Question: Does C-state policy performance come from state-operator matching rather than operator strength, difficulty, or frequency?

C remains fixed as the original B5.5 phase-bearing lag+5 event carrier. State classes are readout regimes, not new C definitions.

Controls:

- balanced operator-pool shuffle preserving selected-operator frequency and train-performance stratum
- frequency-matched random policy
- performance-stratum matched random policy
- within-state operator shuffle
- oracle upper bound

## Classification

B6E success: true C-state policy beats balanced, frequency-matched, performance-matched, and within-state shuffle controls while remaining below oracle.

## Comparison Summary

comparison,mean_true_policy_reward_z,mean_comparator_reward_z,effect,p_greater,n_events,state_mapping_rate,oracle_hit_rate
true_C_state_policy_vs_balanced_operator_pool_shuffle,0.024100344252909255,-0.008365426427953584,0.03771193177385075,0.03719256148770246,447,0.545816733067729,0.1752988047808765
true_C_state_policy_vs_frequency_matched_random_policy,0.024100344252909255,-0.0658866479667461,0.07945838985257524,0.01279744051189762,447,0.545816733067729,0.1752988047808765
true_C_state_policy_vs_performance_matched_random_policy,0.024100344252909255,-0.031684737095699564,0.0674387349161576,0.008198360327934412,447,0.545816733067729,0.1752988047808765
true_C_state_policy_vs_within_state_operator_shuffle,0.024100344252909255,-0.04898798319448221,0.07759741267582666,0.007598480303939212,447,0.545816733067729,0.1752988047808765
true_C_state_policy_vs_oracle_upper_bound,0.024100344252909255,1.2239410650761156,-1.2246477262727624,1.0,447,0.545816733067729,0.1752988047808765

## Held-Out Policy Use

true_policy_operator,true_policy_source,true_operator_performance_stratum,n_events,mean_reward_z,oracle_hit_rate
O1_lag0_AB,global_fallback,high,44,-0.4201712686453015,0.06818181818181818
O1_lag0_AB,state_mapping,high,25,0.07921345055303859,0.16
O1_lag0_AB,state_mapping,low,35,0.6154177267766441,0.2857142857142857
O2_lag5_AB,state_mapping,high,7,0.032126211060722096,0.2857142857142857
O2_lag5_AB,state_mapping,low,21,-0.1366091029431941,0.09523809523809523
O2_lag5_AB,state_mapping,mid,5,-0.18909943940744117,0.2
O3_A_C_boundary,global_fallback,high,112,-0.041527017450261064,0.13392857142857142
O3_A_C_boundary,state_mapping,high,37,0.2173468055315916,0.24324324324324326
O3_A_C_boundary,state_mapping,low,17,0.6454573613996264,0.35294117647058826
O4_B_C_boundary,global_fallback,high,72,-0.14037936988911756,0.1527777777777778
O4_B_C_boundary,state_mapping,high,14,-0.18052599567262242,0.2857142857142857
O4_B_C_boundary,state_mapping,low,30,-0.11884490455620432,0.06666666666666667
O4_B_C_boundary,state_mapping,mid,9,0.04321403360115957,0.2222222222222222
O5_full_TFC,state_mapping,high,8,-0.4886503856844942,0.0
O5_full_TFC,state_mapping,low,4,0.3236580489983155,0.25
O6_phase_only,state_mapping,high,7,0.9177112719278703,0.2857142857142857
O6_phase_only,state_mapping,low,16,0.07714130709147747,0.3125
O6_phase_only,state_mapping,mid,29,0.09018510805071686,0.3103448275862069
O7_suppress_event,state_mapping,high,4,0.0,0.0
O7_suppress_event,state_mapping,mid,6,0.0,0.0

## Train Performance Strata Summary

fold,selected_performance_stratum,selected_operator,n_state_mappings,mean_selected_train_reward
0,high,O4_B_C_boundary,5,0.4418181780980528
0,high,O6_phase_only,4,0.34882636624777735
0,low,O1_lag0_AB,4,0.4795603246834457
0,low,O2_lag5_AB,1,0.48430815278471123
0,low,O3_A_C_boundary,5,0.6881644014907204
0,mid,O7_suppress_event,1,0.0
1,high,O3_A_C_boundary,7,0.6737891080979433
1,high,O7_suppress_event,2,0.0
1,low,O1_lag0_AB,6,0.6482884848523377
1,low,O4_B_C_boundary,5,0.3821576554124424
1,low,O5_full_TFC,1,0.6034159778349985
1,mid,O2_lag5_AB,3,0.37277735482532215
1,mid,O6_phase_only,2,0.5581148246885645
2,high,O3_A_C_boundary,7,0.5514426301607421
2,high,O5_full_TFC,2,0.9649679570440843
2,low,O1_lag0_AB,4,0.7512709210125723
2,low,O2_lag5_AB,3,0.5659818451622605
2,low,O6_phase_only,4,0.42552606399109105
2,mid,O4_B_C_boundary,4,0.2988255827380213
2,mid,O7_suppress_event,1,0.0
3,high,O1_lag0_AB,7,0.5793329793103
3,high,O2_lag5_AB,3,0.357929977010151
3,low,O3_A_C_boundary,5,0.561251740252702
3,low,O4_B_C_boundary,5,0.2761225551509633
3,low,O5_full_TFC,1,0.7153191493696716
3,mid,O6_phase_only,4,0.5116784232721657
3,mid,O7_suppress_event,1,0.0
4,high,O1_lag0_AB,6,0.6355105330433242
4,high,O3_A_C_boundary,5,0.7479698820367214
4,low,O2_lag5_AB,6,0.29420013322119626
4,low,O4_B_C_boundary,2,0.19694550870477992
4,mid,O6_phase_only,7,0.5988377886546228

## Settings

- n_folds: 5
- min_state_events: 8
- n_control_draws: 500
- window: 30
- n_perm: 5000
- seed: 60310
