# Stage B7.4e Cyclotomic / Finite-Group-Algebra Pre-Audit

Status: executed after `Stage_B7_4e_preregistration_email_sent.md`.

## Registered Question

Are P10/P5/P21/P15 compatible with cyclotomic or finite-group-algebra completion structure around C12?

This is a pre-audit. It is not a proof of finite group algebra, paired Phi12 quadrature, or a Jacobi 12-product mechanism.

## Registered Survivors With Frozen Arithmetic Markers

heldout_label,fold_index,mod12_position,mod12_complement_to_12,mod24_position,prime_factors,cyclotomic_recognized_marker,x3_interaction_marker,complement_direction_marker,group_completion_proxy,any_arithmetic_marker,c12_mean,n_positive_specificity_controls,min_specificity_margin
P5,5,5,7,5,5,True,False,True,True,True,0.0059595702135824,8,0.0006866987598247
P10,10,10,2,10,2x5,True,False,False,True,True,0.0041698718380553,8,0.0009641577779958
P15,15,3,9,15,3x5,False,True,True,True,True,0.0034447601866321,7,-0.0005208108436956
P21,21,9,3,21,3x7,False,True,True,True,True,0.005071639629572,7,-0.0002232997982367

## Group Marker Summary

survival_group,n_folds,mean_c12,mean_positive_specificity_controls,mean_min_specificity_margin,rate_cyclotomic_recognized_marker,rate_x3_interaction_marker,rate_complement_direction_marker,rate_full_mod12_generator,rate_high_order_mod24_generator,rate_group_completion_proxy,rate_any_arithmetic_marker
collapsed_or_weak,16,-0.0040430924322452455,1.6875,-0.012579638113708186,0.0,0.0,0.1875,0.375,0.5625,0.5625,0.5625
registered_survivor,4,0.0046614604669604496,7.5,0.00022668647397205003,0.5,0.5,0.75,0.25,0.5,1.0,1.0
intermediate,6,0.002374158286545825,5.166666666666667,-0.007844216948922733,0.0,0.0,0.0,0.3333333333333333,0.5,0.5,0.5

## Exact Four-Fold Subset Enrichment

marker,observed_survivor_rate,all_fold_rate,exact_subset_p_ge_observed,null_mean,null_sd,n_exact_subsets
cyclotomic_recognized_marker,0.5,0.07692307692307693,0.018461538461538463,0.07692307692307693,0.12498520622516862,14950
x3_interaction_marker,0.5,0.07692307692307693,0.018461538461538463,0.07692307692307693,0.12498520622516861,14950
complement_direction_marker,0.75,0.23076923076923078,0.027759197324414717,0.23076923076923078,0.19761896274869428,14950
full_mod12_generator,0.25,0.34615384615384615,0.8408026755852843,0.34615384615384615,0.2231432262209275,14950
high_order_mod24_generator,0.5,0.5384615384615384,0.7608695652173914,0.5384615384615384,0.2338259100549333,14950
group_completion_proxy,1.0,0.6153846153846154,0.12173913043478261,0.6153846153846154,0.22819072267986654,14950
any_arithmetic_marker,1.0,0.6153846153846154,0.12173913043478261,0.6153846153846154,0.22819072267986654,14950

## Interpretation Guardrail

- Enrichment supports only a sharper next hypothesis: C12 survival may be tied to arithmetic completion structure around the Jacobi 12-product.
- Lack of enrichment would leave the finite-group-algebra intuition mathematically interesting but unsupported by present fold-index evidence.
- B7.4e makes no paired Phi12 quadrature claim and no finite-group-algebra proof claim.

## Settings

- registered_survivors: ['P10', 'P15', 'P21', 'P5']
- b74d_profiles: /Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration/reports/stage_b7_4d/Stage_B7_4d_fold_condition_profiles.csv
