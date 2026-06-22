# Stage B7.4g Survivor-Centered Arithmetic Decomposition Audit

Status: executed after `Stage_B7_4g_preregistration_email_sent.md`.

## Registered Question

Which arithmetic decomposition best explains the registered survivor set?

B7.4g treats P10/P5/P21/P15 as the empirical target fixed by B7.4f, then compares arithmetic decompositions as explanatory candidates.

## Proxy Explanation Summary

proxy,n_active_folds,n_registered_overlap,n_extra_active_folds,precision_vs_registered,recall_vs_registered,f1_vs_registered,jaccard_vs_registered,weight_on_registered_fraction,active_mean_c12_mean,active_mean_n_positive_specificity_controls,active_mean_min_specificity_margin,z_distance_to_registered_readout,c12_dilution_vs_registered,positive_control_dilution_vs_registered,min_margin_dilution_vs_registered
registered_survivor_set,4,4,0,1.0,1.0,1.0,1.0,1.0,0.0046614604669604496,7.5,0.00022668647397205003,0.0,0.0,0.0,0.0
cyclotomic_component,2,2,0,1.0,0.5,0.6666666666666666,0.5,1.0,0.00506472102581885,8.0,0.00082542826891025,0.28767749103323315,0.00040326055885840043,0.5,0.0005987417949382
x3_interaction_component,2,2,0,1.0,0.5,0.6666666666666666,0.5,1.0,0.00425819990810205,7.0,-0.00037205532096614997,0.287677491033233,-0.00040326055885839956,-0.5,-0.0005987417949382
complement_direction_component,6,3,3,0.5,0.75,0.6,0.42857142857142855,0.5,0.00034180641508704986,4.666666666666667,-0.007975372168393583,2.3371709382795194,-0.0043196540518734,-2.833333333333333,-0.008202058642365633
cyclotomic_plus_x3_decomposition,4,4,0,1.0,1.0,1.0,1.0,1.0,0.0046614604669604496,7.5,0.00022668647397205003,0.0,0.0,0.0,0.0
broad_group_completion_proxy,16,4,12,0.25,1.0,0.4,0.25,0.25,-0.00084980557322489,3.6875,-0.009164811916564718,2.787347468822313,-0.005511266040185339,-3.8125,-0.009391498390536768
arithmetic_completion_composite,16,4,12,0.25,1.0,0.4,0.25,0.4230769230769231,-0.00084980557322489,3.6875,-0.009164811916564718,2.787347468822313,-0.005511266040185339,-3.8125,-0.009391498390536768
collapsed_arithmetic_control,9,0,9,0.0,0.0,,0.0,0.0,-0.004478655446697525,1.6666666666666667,-0.013271819974961636,4.4399380550105745,-0.009140115913657975,-5.833333333333333,-0.013498506448933686

## Random Four-Fold Reference

metric,registered_value,random_four_fold_mean,random_four_fold_sd,registered_rank_descending,registered_percentile_ge,n_four_fold_subsets
mean_c12,0.0046614604669604,-0.0008551917405248358,0.0023006759073040126,106,0.9929765886287626,14950
mean_positive_specificity_controls,7.5,3.3846153846153846,1.2617729613195712,1,1.0,14950
mean_min_specificity_margin,0.000226686473972,-0.009117123968515377,0.0038235228066857566,18,0.9988628762541806,14950
joint_arithmetic_score,0.6875,0.25,0.11726039399558574,1,1.0,14950
joint_readout_arithmetic_score,3.260368150383132,7.604470750609768e-18,0.7523077434456736,1,1.0,14950

## Decision Boundary

- If the registered survivor set remains strongest, the empirical carrier remains the survivor structure itself.
- If cyclotomic-only and x3-only explain complementary parts and their union approaches the registered set, the survivor structure may decompose into cyclotomic and x3-interaction components.
- If broad group-completion weakens or dilutes the readout, a generalized arithmetic-completion carrier remains unsupported under this operationalization.
- B7.4g does not prove finite group algebra, paired Phi12 quadrature, or a Jacobi 12-product mechanism.

## Settings

- registered_survivors: ['P10', 'P15', 'P21', 'P5']
- b74e_join: /Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration/reports/stage_b7_4e/Stage_B7_4e_fold_index_readout_join.csv
- b74f_subsets: /Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration/reports/stage_b7_4f/Stage_B7_4f_exhaustive_four_index_subsets.csv
