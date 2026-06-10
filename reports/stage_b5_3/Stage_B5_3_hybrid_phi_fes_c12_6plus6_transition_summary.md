# Stage B5.3 Hybrid Phi/FES Sign-Switch and C12 6+6 Dual-Branch Transition Summary

## Purpose

B5.3 tests whether `hybrid_phi_sign_switch` corresponds to a C12-internal 6+6 dual-branch transition. The endpoint is branch-transition structure, not stable C12 carrier closure.

## Run Parameters

- input root: `/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction`
- output dir: `reports/stage_b5_3`
- steps: 240
- runs per condition: 400
- degree-null graphs per event class: 80
- runs per degree-null graph: 5
- recovery window: 18
- seed: 53053

## Overall Result

- primary mechanism candidate: False
- interpretation boundary: transition-like C12 branch readout only; not stable carrier closure.

## Primary Event

event_class,event_role,mean_branch_transition_differentiated,effect_vs_time_shifted,effect_vs_random_event,effect_vs_degree_null_mean,p_vs_time_shifted_and_random,branch_transition_q_value,p_vs_degree_null,p_vs_non_phi_contrast_switches,branch_transition_score,branch_flip_fraction,branch_minus_abs_generic_improvement,late_branch_stability,passes_branch_specificity_gate,passes_null_gate,mechanism_candidate
hybrid_phi_sign_switch,primary_phi_fes,0.05881581568393855,0.010928650295601194,0.0031318152640479394,0.008039311918955537,0.18352059925093633,0.36704119850187267,0.13216957605985039,0.0008326394671107411,0.09807649453540197,0.04576086956521738,0.08836071111728121,0.5165246272587772,True,False,False

## Coherence Probes

event_class,event_role,mean_branch_transition_differentiated,effect_vs_time_shifted,effect_vs_random_event,effect_vs_degree_null_mean,p_vs_time_shifted_and_random,branch_transition_q_value,p_vs_degree_null,p_vs_non_phi_contrast_switches,branch_transition_score,branch_flip_fraction,branch_minus_abs_generic_improvement,late_branch_stability,passes_branch_specificity_gate,passes_null_gate,mechanism_candidate
hybrid_fes_phase_transition,primary_phi_fes,0.09433671212547369,0.009263942492448676,0.02978596080286057,0.009454101926209019,0.04244694132334582,0.12734082397003746,0.11970074812967581,,0.14385548489048922,0.03114583333333333,0.13451647500630476,0.6087207105448447,False,False,False
hybrid_cluster_transition,primary_phi_fes,0.09359748027862783,0.009034579751728847,0.02694734424542558,0.008763377014243096,0.04119850187265917,0.12734082397003746,0.16209476309226933,,0.14269830800751498,0.02770833333333333,0.1329389958820549,0.6089555955949713,False,False,False

## Non-Phi Contrast Switches

event_class,event_role,mean_branch_transition_differentiated,effect_vs_time_shifted,effect_vs_random_event,effect_vs_degree_null_mean,p_vs_time_shifted_and_random,branch_transition_q_value,p_vs_degree_null,p_vs_non_phi_contrast_switches,branch_transition_score,branch_flip_fraction,branch_minus_abs_generic_improvement,late_branch_stability,passes_branch_specificity_gate,passes_null_gate,mechanism_candidate
chapter7_dphi_sign_switch,contrast_switch,0.02379131003286867,-0.0014271075837864362,0.006800031057174517,0.0010036069244809057,0.5056179775280899,0.5593008739076155,0.0199501246882793,,0.04083433695347985,0.0029726890756302513,0.03894338444144597,0.44422257292226114,False,True,False
chapter7_d2phi_curvature_switch,contrast_switch,0.018695813369860134,-0.0036439979671432435,0.003141149987700785,0.0006369278004105076,0.5593008739076155,0.5593008739076155,0.10723192019950124,,0.03206315205823546,0.0013970588235294118,0.03079283422422974,0.3828430386611908,False,False,False
chapter7_deps_sign_switch,contrast_switch,0.026693454308472697,-0.002082011472431769,0.01103589973967099,0.0010845409335025168,0.5006242197253433,0.5593008739076155,0.09975062344139651,,0.04740220432532098,0.0076995798319327725,0.04494516110542613,0.5162897276119799,False,False,False

## All Endogenous Rows

event_class,event_role,mean_branch_transition_differentiated,effect_vs_time_shifted,effect_vs_random_event,effect_vs_degree_null_mean,p_vs_time_shifted_and_random,branch_transition_q_value,p_vs_degree_null,p_vs_non_phi_contrast_switches,branch_transition_score,branch_flip_fraction,branch_minus_abs_generic_improvement,late_branch_stability,passes_branch_specificity_gate,passes_null_gate,mechanism_candidate
hybrid_phi_sign_switch,primary_phi_fes,0.05881581568393855,0.010928650295601194,0.0031318152640479394,0.008039311918955537,0.18352059925093633,0.36704119850187267,0.13216957605985039,0.0008326394671107411,0.09807649453540197,0.04576086956521738,0.08836071111728121,0.5165246272587772,True,False,False
hybrid_fes_phase_transition,primary_phi_fes,0.09433671212547369,0.009263942492448676,0.02978596080286057,0.009454101926209019,0.04244694132334582,0.12734082397003746,0.11970074812967581,,0.14385548489048922,0.03114583333333333,0.13451647500630476,0.6087207105448447,False,False,False
hybrid_cluster_transition,primary_phi_fes,0.09359748027862783,0.009034579751728847,0.02694734424542558,0.008763377014243096,0.04119850187265917,0.12734082397003746,0.16209476309226933,,0.14269830800751498,0.02770833333333333,0.1329389958820549,0.6089555955949713,False,False,False
chapter7_dphi_sign_switch,contrast_switch,0.02379131003286867,-0.0014271075837864362,0.006800031057174517,0.0010036069244809057,0.5056179775280899,0.5593008739076155,0.0199501246882793,,0.04083433695347985,0.0029726890756302513,0.03894338444144597,0.44422257292226114,False,True,False
chapter7_d2phi_curvature_switch,contrast_switch,0.018695813369860134,-0.0036439979671432435,0.003141149987700785,0.0006369278004105076,0.5593008739076155,0.5593008739076155,0.10723192019950124,,0.03206315205823546,0.0013970588235294118,0.03079283422422974,0.3828430386611908,False,False,False
chapter7_deps_sign_switch,contrast_switch,0.026693454308472697,-0.002082011472431769,0.01103589973967099,0.0010845409335025168,0.5006242197253433,0.5593008739076155,0.09975062344139651,,0.04740220432532098,0.0076995798319327725,0.04494516110542613,0.5162897276119799,False,False,False

## Event Inventory

event_class,event_role,source_file,event_rule,n_events,n_labels,min_task_idx,max_task_idx,mean_strength
chapter7_d2phi_curvature_switch,contrast_switch,Chapter7/new_phi_dataset.csv,sign switch of Chapter7 d2phi curvature,6731,26,3.0,417.0,0.5707575318168661
chapter7_deps_sign_switch,contrast_switch,Chapter7/new_phi_dataset.csv,sign switch of Chapter7 deps,4650,26,2.0,417.0,0.007698070655891552
chapter7_dphi_sign_switch,contrast_switch,Chapter7/new_phi_dataset.csv,sign switch of Chapter7 dphi,4741,26,2.0,417.0,0.40650323045115333
hybrid_cluster_transition,primary_phi_fes,event_level_with_fes_phase_TRUE_RICCI.csv,transition of formal FES/hybrid-Phi cluster assignment,192,26,2.0,27.0,1.0
hybrid_fes_phase_transition,primary_phi_fes,event_level_with_fes_phase_TRUE_RICCI.csv,transition of formal FES semantic phase assignment,192,26,2.0,27.0,1.0
hybrid_phi_sign_switch,primary_phi_fes,event_level_with_fes_phase_TRUE_RICCI.csv,sign switch of formal hybrid Phi in the FES event-level table,120,26,2.0,27.0,0.8808924362318745

## Degree-Null Summary

event_class,event_role,n_null_graphs,mean_null_branch_transition,sd_null_branch_transition
chapter7_d2phi_curvature_switch,contrast_switch,80,0.01805888556944963,0.0002505969234534167
chapter7_deps_sign_switch,contrast_switch,80,0.025608913374970184,0.0004299000684882948
chapter7_dphi_sign_switch,contrast_switch,80,0.022787703108387763,0.00025411997751744326
hybrid_cluster_transition,primary_phi_fes,80,0.08483410326438472,0.005143254856642059
hybrid_fes_phase_transition,primary_phi_fes,80,0.08488261019926467,0.004960328146163076
hybrid_phi_sign_switch,primary_phi_fes,80,0.050776503764983015,0.005119961190502637

## Interpretation Boundary

B5.3 remains negative or inconclusive for the proposed mechanism if non-Phi switches or nulls reproduce the same 6+6 branch-transition pattern, or if the effect is generic C12 recovery rather than branch-specific transition structure.
