# Private B6 C-Guided Operator Selection Audit

Status: local/private screen only. No publication, commit, or push was performed.

Question: Can C_t select the next interpretation operator better than fixed, random, or shuffled-C selection?

C is fixed as the original B5.5 phase-bearing lag+5 event carrier. This audit does not redefine C.

Operators:

- O1_lag0_AB: immediate A-B readout.
- O2_lag5_AB: short-lag future A-B readout.
- O3_A_C_boundary: future A-side boundary readout.
- O4_B_C_boundary: future B-side boundary readout.
- O5_full_TFC: future full triadic projection readout.
- O6_phase_only: future phase-only readout.

The reward for each operator is z-scored across events before selection comparisons.

## Classification

Partial B6B signal: C-selected beats random and shuffled-C but not best fixed.

## Comparison Summary

comparison,mean_C_selected_reward_z,mean_comparator_reward_z,effect,p_greater,n_events,hit_rate_selected_equals_oracle,best_fixed_operator
C_selected_vs_best_fixed_O6_phase_only,0.11514699430949046,1.1483518961779397e-16,0.07658998095750184,0.14237152569486103,450,0.20119521912350596,O6_phase_only
C_selected_vs_random_operator,0.11514699430949046,0.010569375378170905,0.10415841715290208,0.04039192161567687,432,0.20119521912350596,O6_phase_only
C_selected_vs_shuffled_C_selected_operator,0.11514699430949046,-0.08575838237945674,0.1632736611604612,0.001799640071985603,428,0.20119521912350596,O6_phase_only
C_selected_vs_oracle_upper_bound,0.11514699430949046,1.2219141327632144,-1.1379029768241828,1.0,450,0.20119521912350596,O6_phase_only

## Operator Summary

operator,n_selected,mean_selected_reward_z_when_selected,fixed_mean_reward_z,oracle_selection_count
O1_lag0_AB,78,-0.719956614768451,-2.2657612747452175e-16,91
O2_lag5_AB,49,0.4308186311727679,7.691441985032012e-17,62
O3_A_C_boundary,91,0.5102310522822723,3.466062125659025e-17,71
O4_B_C_boundary,158,0.030746369396011552,-1.6625999974682147e-16,89
O5_full_TFC,100,0.40946439025539183,3.6326315734156453e-17,85
O6_phase_only,26,0.030814817452294602,1.1483518961779397e-16,97

## Selection Inventory

selected_operator,selection_reason,n_events,mean_selected_reward_z,oracle_match_rate
O1_lag0_AB,default immediate AB readout,78,-0.7199566147684511,0.02564102564102564
O2_lag5_AB,current AB is active; read short-lag future AB,49,0.43081863117276803,0.1836734693877551
O3_A_C_boundary,A-side boundary projection dominates current C-state,91,0.5102310522822723,0.3076923076923077
O4_B_C_boundary,B-side boundary projection dominates current C-state,158,0.030746369396011546,0.21518987341772153
O5_full_TFC,full triadic projection is already active,100,0.40946439025539183,0.24
O6_phase_only,phase or closed-loop memory is high,26,0.030814817452294564,0.15384615384615385

## Settings

- window: 30
- n_perm: 5000
- seed: 60010
