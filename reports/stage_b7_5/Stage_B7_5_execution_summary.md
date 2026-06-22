# Stage B7.5 Relation / Condition Audit With Fractional Diagnostic

Status: executed after `Stage_B7_5_preregistration_email_sent.md`.

## Registered Question

Is the surviving structure reducible to relation(A,B), is it better described as a reverse-dominant C->AB condition, or does it require a self-consistent AB<->C condition?

## Layer 1: Best Arm By Family

representation,arm_family,c12_readout,no_topology_readout,effect_vs_no_topology,n_positive_specificity_controls,min_specificity_margin,effect_vs_c12_reversed,effect_vs_c12_side_broken,effect_vs_c12_shuffled,effect_vs_c10,effect_vs_c11,effect_vs_c13,effect_vs_c14,n_events,survivor_event_fraction,survivor_strength_fraction,top4_labels_by_event_strength,top4_survivor_overlap,top4_precision_vs_registered,top4_recall_vs_registered,top4_jaccard_vs_registered,top4_matches_cyclotomic_x3
self_consistent_rstar_condition,self_consistent_condition,0.028791506059315693,0.023158187510329793,0.0056333185489859,7,0.0003553498378890928,0.0003553498378890928,0.026764822406913344,0.030546128962762688,0.03369449626032552,0.03728060619769337,0.02839927301493907,0.0318863495692111,132,0.1590909090909091,0.17461867504757617,P10|P13|P20|P25,1,0.25,0.25,0.14285714285714285,False
reverse_c_to_ab_condition,reverse_only_condition,0.03261690116792293,0.027143162502239148,0.005473738665683781,7,0.001173597167001425,0.001173597167001425,0.023445294295395033,0.028218052313857815,0.037214814921786424,0.039693986622896145,0.03533385693371305,0.03561636650235104,132,0.1590909090909091,0.1685045237897222,P13|P20|P24|P25,0,0.0,0.0,0.0,False
receiver_standpoint_relation,receiver_standpoint_relation_only,0.028771711558939143,0.025328423870445295,0.0034432876884938485,7,0.0017571686749875762,0.0017571686749875762,0.021740101511944335,0.02098501581562013,0.03253016238021752,0.03469656424431128,0.031713478806356554,0.03137162865883004,132,0.1590909090909091,0.17545789815710283,P3|P10|P13|P25,1,0.25,0.25,0.14285714285714285,False
forward_ab_to_c_condition,forward_only_condition,0.02606726749617482,0.02275931961029616,0.0033079478858786607,7,0.0001727046234639186,0.0001727046234639186,0.02293356749934756,0.029459446493884354,0.03096453758958129,0.032789042401654554,0.02714249995395821,0.029695093571811687,132,0.1590909090909091,0.1823286829817214,P3|P10|P13|P25,1,0.25,0.25,0.14285714285714285,False
endpoint_lag_gap_relation,endpoint_direct_relation_only,0.02702796151942974,0.024842808781751637,0.002185152737678102,7,0.002501872508732711,0.002501872508732711,0.028427312003948088,0.023463749024963287,0.03164213083031581,0.03343594315312493,0.029002088755840427,0.02775524920921433,131,0.16030534351145037,0.1925847384086233,P4|P10|P20|P24,1,0.25,0.25,0.14285714285714285,False
scalar_c,scalar_mediator_control,0.01861172307079414,0.018018136606204545,0.0005935864645895961,7,0.00022376606316358225,0.00022376606316358225,0.021283448353025654,0.020390386664631444,0.02374132701604304,0.027325511643954973,0.02247808217697879,0.022122537959869876,134,0.16417910447761194,0.15480117207124816,P4|P13|P14|P16,0,0.0,0.0,0.0,False

## Classification

criterion,supported,basis
endpoint_direct_relation_reduced,True,endpoint effect 0.00218515; receiver/standpoint 0.00344329; reverse 0.00547374
receiver_standpoint_relation_competitor_live,True,receiver/standpoint relation best effect 0.00344329
reverse_dominant_condition_competitor_live,True,reverse effect 0.00547374; relation 0.00344329; forward 0.00330795
self_consistency_exceeds_reverse,True,self-consistent effect 0.00563332; reverse effect 0.00547374
broad_completion_fractional_signature_present,True,B7.4g broad_group_completion_proxy precision is exact 1/4

## Layer 2: Fractional / Cyclotomic Diagnostic Focus

source,representation_or_proxy,arm_family,metric,value,nearest_fraction,abs_error_to_fraction,is_luke_target_fraction,has_numerator_gt_1
B7.4g_proxy_support,cyclotomic_component,broad_or_survivor_arithmetic_proxy,recall_vs_registered,0.5,1/2,0.0,True,False
B7.4g_proxy_support,cyclotomic_component,broad_or_survivor_arithmetic_proxy,jaccard_vs_registered,0.5,1/2,0.0,True,False
B7.4g_proxy_support,x3_interaction_component,broad_or_survivor_arithmetic_proxy,recall_vs_registered,0.5,1/2,0.0,True,False
B7.4g_proxy_support,x3_interaction_component,broad_or_survivor_arithmetic_proxy,jaccard_vs_registered,0.5,1/2,0.0,True,False
B7.4g_proxy_support,complement_direction_component,broad_or_survivor_arithmetic_proxy,precision_vs_registered,0.5,1/2,0.0,True,False
B7.4g_proxy_support,complement_direction_component,broad_or_survivor_arithmetic_proxy,recall_vs_registered,0.75,3/4,0.0,False,True
B7.4g_proxy_support,complement_direction_component,broad_or_survivor_arithmetic_proxy,jaccard_vs_registered,0.4285714285714285,3/7,5.551115123125783e-17,False,True
B7.4g_proxy_support,complement_direction_component,broad_or_survivor_arithmetic_proxy,weight_on_registered_fraction,0.5,1/2,0.0,True,False
B7.4g_proxy_support,cyclotomic_plus_x3_decomposition,broad_or_survivor_arithmetic_proxy,precision_vs_registered,1.0,1/1,0.0,False,False
B7.4g_proxy_support,cyclotomic_plus_x3_decomposition,broad_or_survivor_arithmetic_proxy,recall_vs_registered,1.0,1/1,0.0,False,False
B7.4g_proxy_support,cyclotomic_plus_x3_decomposition,broad_or_survivor_arithmetic_proxy,jaccard_vs_registered,1.0,1/1,0.0,False,False
B7.4g_proxy_support,cyclotomic_plus_x3_decomposition,broad_or_survivor_arithmetic_proxy,weight_on_registered_fraction,1.0,1/1,0.0,False,False
B7.4g_proxy_support,broad_group_completion_proxy,broad_or_survivor_arithmetic_proxy,precision_vs_registered,0.25,1/4,0.0,True,False
B7.4g_proxy_support,broad_group_completion_proxy,broad_or_survivor_arithmetic_proxy,recall_vs_registered,1.0,1/1,0.0,False,False
B7.4g_proxy_support,broad_group_completion_proxy,broad_or_survivor_arithmetic_proxy,jaccard_vs_registered,0.25,1/4,0.0,True,False
B7.4g_proxy_support,broad_group_completion_proxy,broad_or_survivor_arithmetic_proxy,weight_on_registered_fraction,0.25,1/4,0.0,True,False
B7.4g_proxy_support,arithmetic_completion_composite,broad_or_survivor_arithmetic_proxy,precision_vs_registered,0.25,1/4,0.0,True,False
B7.4g_proxy_support,arithmetic_completion_composite,broad_or_survivor_arithmetic_proxy,jaccard_vs_registered,0.25,1/4,0.0,True,False
B7.4g_proxy_support,arithmetic_completion_composite,broad_or_survivor_arithmetic_proxy,weight_on_registered_fraction,0.4230769230769231,3/7,0.005494505494505475,False,True
B7.5_relation_condition_arm,self_consistent_rstar_condition,self_consistent_condition,top4_precision_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,self_consistent_rstar_condition,self_consistent_condition,top4_recall_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,self_consistent_rstar_condition,self_consistent_condition,survivor_event_fraction,0.1590909090909091,1/6,0.007575757575757569,True,False
B7.5_relation_condition_arm,self_consistent_rstar_condition,self_consistent_condition,survivor_strength_fraction,0.17461867504757617,2/11,0.007199506770605657,False,True
B7.5_relation_condition_arm,reverse_c_to_ab_condition,reverse_only_condition,survivor_event_fraction,0.1590909090909091,1/6,0.007575757575757569,True,False
B7.5_relation_condition_arm,reverse_c_to_ab_condition,reverse_only_condition,survivor_strength_fraction,0.1685045237897222,1/6,0.0018378571230555363,True,False
B7.5_relation_condition_arm,self_consistent_min_condition,self_consistent_condition,top4_precision_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,self_consistent_min_condition,self_consistent_condition,top4_recall_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,self_consistent_min_condition,self_consistent_condition,survivor_event_fraction,0.1590909090909091,1/6,0.007575757575757569,True,False
B7.5_relation_condition_arm,self_consistent_min_condition,self_consistent_condition,survivor_strength_fraction,0.17754227946863166,2/11,0.004275902349550165,False,True
B7.5_relation_condition_arm,receiver_standpoint_relation,receiver_standpoint_relation_only,top4_precision_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,receiver_standpoint_relation,receiver_standpoint_relation_only,top4_recall_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,receiver_standpoint_relation,receiver_standpoint_relation_only,survivor_event_fraction,0.1590909090909091,1/6,0.007575757575757569,True,False
B7.5_relation_condition_arm,receiver_standpoint_relation,receiver_standpoint_relation_only,survivor_strength_fraction,0.17545789815710283,2/11,0.0063602836610789915,False,True
B7.5_relation_condition_arm,forward_ab_to_c_condition,forward_only_condition,top4_precision_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,forward_ab_to_c_condition,forward_only_condition,top4_recall_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,forward_ab_to_c_condition,forward_only_condition,survivor_event_fraction,0.1590909090909091,1/6,0.007575757575757569,True,False
B7.5_relation_condition_arm,forward_ab_to_c_condition,forward_only_condition,survivor_strength_fraction,0.1823286829817214,2/11,0.0005105011635395673,False,True
B7.5_relation_condition_arm,receiver_only_relation,receiver_standpoint_relation_only,top4_precision_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,receiver_only_relation,receiver_standpoint_relation_only,top4_recall_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,receiver_only_relation,receiver_standpoint_relation_only,survivor_event_fraction,0.1590909090909091,1/6,0.007575757575757569,True,False
B7.5_relation_condition_arm,receiver_only_relation,receiver_standpoint_relation_only,survivor_strength_fraction,0.18844096424910803,2/11,0.006622782430926205,False,True
B7.5_relation_condition_arm,endpoint_lag_gap_relation,endpoint_direct_relation_only,top4_precision_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,endpoint_lag_gap_relation,endpoint_direct_relation_only,top4_recall_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,endpoint_lag_gap_relation,endpoint_direct_relation_only,survivor_event_fraction,0.16030534351145037,1/6,0.006361323155216286,True,False
B7.5_relation_condition_arm,endpoint_lag_gap_relation,endpoint_direct_relation_only,survivor_strength_fraction,0.1925847384086233,1/5,0.007415261591376704,True,False
B7.5_relation_condition_arm,endpoint_product_relation,endpoint_direct_relation_only,survivor_event_fraction,0.16030534351145037,1/6,0.006361323155216286,True,False
B7.5_relation_condition_arm,self_consistent_product_condition,self_consistent_condition,top4_precision_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,self_consistent_product_condition,self_consistent_condition,top4_recall_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,self_consistent_product_condition,self_consistent_condition,survivor_event_fraction,0.1590909090909091,1/6,0.007575757575757569,True,False
B7.5_relation_condition_arm,self_consistent_product_condition,self_consistent_condition,survivor_strength_fraction,0.19787656875457485,1/5,0.0021234312454251614,True,False
B7.5_relation_condition_arm,scalar_c,scalar_mediator_control,survivor_event_fraction,0.16417910447761194,1/6,0.002487562189054715,True,False
B7.5_relation_condition_arm,scalar_c,scalar_mediator_control,survivor_strength_fraction,0.15480117207124816,1/6,0.011865494595418496,True,False
B7.5_relation_condition_arm,endpoint_abs_relation,endpoint_direct_relation_only,survivor_event_fraction,0.16030534351145037,1/6,0.006361323155216286,True,False
B7.5_relation_condition_arm,standpoint_only_relation,receiver_standpoint_relation_only,top4_precision_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,standpoint_only_relation,receiver_standpoint_relation_only,top4_recall_vs_registered,0.25,1/4,0.0,True,False
B7.5_relation_condition_arm,standpoint_only_relation,receiver_standpoint_relation_only,survivor_event_fraction,0.1590909090909091,1/6,0.007575757575757569,True,False
B7.5_relation_condition_arm,standpoint_only_relation,receiver_standpoint_relation_only,survivor_strength_fraction,0.17323897749676823,1/6,0.006572310830101569,True,False

## Decision Boundary

- If receiver/standpoint relation-only matches self-consistency, conclude toward refined receiver/standpoint relation(A,B).
- If reverse-only matches or exceeds self-consistency, conclude toward reverse-dominant condition rather than overstating AB<->C.
- If self-consistent AB<->C exceeds relation-only and reverse-only, and best preserves C12/survivor structure, directed-correspondence-condition interpretation strengthens.
- Fractional diagnostics are secondary; broad completion is not adopted as a readout carrier solely from fractional signatures.

## Settings

- event_quantile: 0.75
- steps: 240
- n_runs: 32
- seed: 75075
