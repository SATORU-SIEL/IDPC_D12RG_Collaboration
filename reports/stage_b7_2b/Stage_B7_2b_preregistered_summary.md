# Stage B7.2b Side-Direction Correspondence and Factorisation-Path Audit

Status: executed after writing Stage_B7_2b_preregistration.md and Stage_B7_2b_final_plan_email.md.

## Result

- frozen B6-supported regimes tested: 11 / 24
- endpoint_o1o2_reference bounds true C: 11 / 11
- endpoint_o1o2_direction_swapped lets true C win: 11 / 11
- mismatch_train_consistent_test_inverted lets true C win: 11 / 11
- closure_scalar_only lets true C win: 11 / 11
- directed_transport_closure_control bounds true C: 11 / 11
- factorisation_path_consistent lets true C win: 11 / 11
- factorisation_path_shuffled lets true C win: 11 / 11
- factorisation_path_mismatch_train_test lets true C win: 11 / 11

## Primary Classification

criterion,supported,basis
direction_label_only_sufficient,False,direction_label_only: true C wins 11/11
endpoint_direction_pairing_required,True,endpoint_o1o2_reference bounds C 11/11; endpoint_o1o2_direction_swapped lets C win 11/11
train_test_correspondence_required,True,self-consistent standpoint controls bound C; mismatch_train_consistent_test_inverted lets C win 11/11
fixed_mask_sufficient,False,fixed mask controls do not reproduce the endpoint O1/O2 boundary uniformly; several let C win
static_zero_sum_sufficient,False,closure_scalar_only lets C win 11/11
directed_transport_required,True,directed_transport_closure_control bounds C 11/11 while scalar closure does not
factorisation_lift_supported,False,"factorisation_path_consistent, shuffled, and mismatch all let C win 11/11 under the current operationalization"
c12_lift_diagnostic_resolved,False,"B7.2b local correspondence is supported, but the current factorisation-path module does not yet produce a discriminating lift result"

## Component Summary

control_level,frozen_regimes,c_beats_count,control_bounds_c_count,mean_true_minus_control,median_true_minus_control
direction_label_only,11,11,0,0.0805953486579871,0.0886908626213569
communication_direction_only,11,0,11,-0.097871693982076,-0.1217550915559951
symmetric_midpoint_control,11,0,11,-0.084361912017594,-0.1040641019487088
sender_receiver_transfer_control,11,0,11,-0.1228027589986026,-0.1486243196088836
asymmetric_standpoint_control,11,0,11,-0.110785463380716,-0.146141192797186
standpoint_inverted_control,11,0,11,-0.1100103758280604,-0.1235664184192783
endpoint_o1o2_reference,11,0,11,-0.2145116286770407,-0.2814879304394226
endpoint_o1o2_direction_swapped,11,11,0,0.070481503975363,0.0767173344641445
endpoint_o1o2_asymmetric_standpoint,11,0,11,-0.0448074939096429,-0.0596502392368986
endpoint_o1o2_standpoint_inverted,11,0,11,-0.0450043562547972,-0.0364751823650419
standpoint_consistent_split_operator,11,0,11,-0.1120251775431008,-0.1432341335336357
standpoint_inverted_split_operator,11,0,11,-0.1116686400459505,-0.1341608690038012
standpoint_operator_side_only,11,0,11,-0.1104253412641059,-0.1228311580677574
standpoint_wrong_operator_side_only,11,0,11,-0.1107993015940539,-0.1453227947563717
standpoint_consistent_operator_contrast,11,0,11,-0.0584943490238828,-0.0761226089647184
standpoint_inverted_operator_contrast,11,0,11,-0.0585012460699414,-0.0753056272647437
standpoint_contrast_with_side_polarity,11,0,11,-0.0660900530185209,-0.0853740656944813
standpoint_inverted_contrast_with_side_polarity,11,0,11,-0.0661117357613237,-0.0849583992052478
mismatch_train_consistent_test_inverted,11,11,0,0.2579886291378762,0.3301153130205445
mismatch_train_endpoint_test_direction_swapped,11,8,3,0.0688912510335055,0.0832688269597398
fixed_b6p_direction_mask,11,11,0,0.0551883292460593,0.0638413720513296
fixed_b6p_swapped_mask,11,6,5,0.0555260288980937,0.0578321418790103
fixed_receiver_pair_mask,11,9,2,0.0823271159561747,0.1039547940394103
fixed_giver_pair_mask,11,5,6,0.0840318069952818,0.0779699492926044
fixed_ab_receiver_only,11,9,2,0.1093258305366042,0.1299498702548385
fixed_c_receiver_boundary_only,11,0,11,0.0463407083057685,0.056321762694637
closure_scalar_only,11,11,0,0.0826715339999567,0.0917325511074259
closure_2ode_local,11,11,0,0.0637762475413481,0.0656341166893876
directed_transport_closure_control,11,0,11,-0.0660900530185209,-0.0853740656944813
factorisation_3x8,11,0,11,-0.0680983957872839,-0.0952467043480229
factorisation_2x2x6,11,11,0,0.0607634193459237,0.0609635542430738
factorisation_path_consistent,11,11,0,0.0850070620745905,0.094827207939259
factorisation_path_shuffled,11,11,0,0.0850070620745905,0.094827207939259
factorisation_path_mismatch_train_test,11,11,0,0.0850070620745905,0.094827207939259

## Interpretation

B7.2b supports that the endpoint O1/O2 boundary is not reproduced by direction labels alone and is weakened when endpoint-local direction pairing is swapped.

The strongest positive result is train/test correspondence: self-consistent standpoint mappings remain strong, but train-consistent / test-inverted mismatch collapses the O1/O2 advantage and true C wins in all frozen regimes.

Static scalar closure is not sufficient under this implementation: closure_scalar_only lets true C win in all frozen regimes. In contrast, directed_transport_closure_control bounds true C in all frozen regimes, supporting Marcel/Luke's distinction between static balance and directed transport.

The current factorisation-path module does not yet support Luke's lift interpretation. The factorisation_path_consistent, factorisation_path_shuffled, and factorisation_path_mismatch_train_test controls all let true C win with identical aggregate behavior, so this operationalization is not yet discriminating.

C12 remains paused. B7.2b suggests that C12(1,2) may indeed need a directed correspondence representation before reconnection, but the present factorisation-path lift controls are not sufficient to decide whether C12(1,2) is failing specifically at the lift-across-24-factorisation step.

## Output Files

- Stage_B7_2b_component_summary.csv
- Stage_B7_2b_primary_classification.csv
- Stage_B7_2b_frozen_pass_matrix.csv
- Stage_B7_2b_comparison.csv
- Stage_B7_2b_control_events.csv

## Settings

- n_folds: 5
- min_state_events: 8
- temperature: 0.35
- n_perm: 5000
- alpha: 0.05
- seed: 71110
