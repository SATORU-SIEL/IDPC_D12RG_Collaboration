# Stage B5.1 Phi/FES-to-C12 Bridge Audit Summary

## Purpose

B5.1 tests whether formal IDPC Phi/FES switching events condition bounded differentiated recovery in the external D12RG C12(1,2) readout topology.

## Overall Result

- event classes tested: 8
- primary Phi/FES event classes: 3
- positive primary candidates: 0
- C12 endogenous rows with q <= 0.05: 0

The B5.1 result is not a confirmatory positive under the preregistered gate.
However, it should not be interpreted as a clear negative. It is a
borderline / near-threshold result: all three primary Phi/FES event classes
showed consistent directional C12(1,2) advantage, but the preregistered
confirmatory gate was narrowly missed.

All three primary Phi/FES event classes showed a consistent directional
C12(1,2) advantage over shifted controls, random-event controls, C8 contrast,
and degree-matched null means.

## Primary C12 Directional Signal

event_class,p_vs_time_shifted_and_random,primary_q_value,effect_vs_C8,effect_vs_degree_null_mean
hybrid_phi_sign_switch,0.015984015984015984,0.055944055944055944,0.005226778731405966,0.0037164602263079103
hybrid_fes_phase_transition,0.027972027972027972,0.055944055944055944,0.005185815486128078,0.003429826928152562
hybrid_cluster_transition,0.01998001998001998,0.055944055944055944,0.005139807555098615,0.003509410201690399

The correct interpretation is:

```text
B5.1 did not confirm a positive Phi/FES-to-C12 bridge under the
preregistered gate, but it produced a consistent near-threshold directional
C12(1,2) signal across all three primary Phi/FES event classes.
```

The confirmatory gate failed because the FDR threshold q <= 0.05 was missed
slightly, late-window stability did not pass the fixed gate, and the
degree-null p-value gate did not pass.

## Primary Phi/FES Rows

event_class,event_role,n_seed_events,mean_bounded_differentiated_recovery,effect_vs_time_shifted,effect_vs_random_event,effect_vs_C8,effect_vs_degree_null_mean,p_vs_time_shifted_and_random,primary_q_value,p_vs_C8,p_vs_degree_null,bounded_non_runaway_score,non_collapsed_differentiation_score,late_window_stability,passes_effect_controls,passes_stability_gates,passes_contrast_switch_gate,positive_candidate,interpretation
hybrid_phi_sign_switch,primary_phi_fes,120,0.006338659384197923,0.005812622080752901,0.005995716492435459,0.005226778731405966,0.0037164602263079103,0.015984015984015984,0.055944055944055944,0.005988023952095809,0.12367270455965022,0.954715762868663,0.651379353197774,0.5573858154868523,True,False,True,False,primary_phi_fes_negative_or_incomplete_gate
hybrid_fes_phase_transition,primary_phi_fes,192,0.004996439874588683,0.00865298176087137,0.004315168711681334,0.005185815486128078,0.003429826928152562,0.027972027972027972,0.055944055944055944,0.003992015968063872,0.1061836352279825,0.9569611465107275,0.6911113573209393,0.4034481140212195,True,False,True,False,primary_phi_fes_negative_or_incomplete_gate
hybrid_cluster_transition,primary_phi_fes,192,0.005133004314082436,0.008416804377244819,0.004514177593639095,0.005139807555098615,0.003509410201690399,0.01998001998001998,0.055944055944055944,0.003992015968063872,0.07807620237351655,0.9571140117498663,0.6916394188979222,0.40249167944414654,True,False,True,False,primary_phi_fes_negative_or_incomplete_gate

## All Endogenous C12 Rows

event_class,event_role,n_seed_events,mean_bounded_differentiated_recovery,effect_vs_time_shifted,effect_vs_random_event,effect_vs_C8,effect_vs_degree_null_mean,p_vs_time_shifted_and_random,primary_q_value,p_vs_C8,p_vs_degree_null,bounded_non_runaway_score,non_collapsed_differentiation_score,late_window_stability,passes_effect_controls,passes_stability_gates,passes_contrast_switch_gate,positive_candidate,interpretation
chapter7_d2phi_curvature_switch,contrast_switch,6731,0.000524561104947343,0.0025804540678846456,0.0002976493802449849,-0.00040630108673168637,0.0001028280983230067,0.21978021978021978,0.29304029304029305,0.7145708582834331,0.4634603372891943,0.952453498929184,0.6100798196786175,0.3260360598956787,False,False,False,False,contrast_switch_control
chapter7_dphi_sign_switch,contrast_switch,4741,0.0011105530070494123,0.0003935769531771615,0.0008039007180163033,0.003298985553398858,-7.971975159301679e-05,0.3146853146853147,0.3596403596403596,0.001996007984031936,0.5421611492816989,0.9527335696643628,0.6092137712078627,0.393827276230545,False,False,False,False,contrast_switch_control
chapter7_deps_sign_switch,contrast_switch,4650,-0.0007681404918835553,-0.0005460097098880179,-0.0011871975663415482,0.0003209531755030455,-0.00019750405230456024,0.7762237762237763,0.7762237762237763,0.3313373253493014,0.6114928169893816,0.9540137980869149,0.5943527410705183,0.44867267207950934,False,False,False,False,contrast_switch_control
hybrid_phi_sign_switch,primary_phi_fes,120,0.006338659384197923,0.005812622080752901,0.005995716492435459,0.005226778731405966,0.0037164602263079103,0.015984015984015984,0.055944055944055944,0.005988023952095809,0.12367270455965022,0.954715762868663,0.651379353197774,0.5573858154868523,True,False,True,False,primary_phi_fes_negative_or_incomplete_gate
hybrid_fes_phase_transition,primary_phi_fes,192,0.004996439874588683,0.00865298176087137,0.004315168711681334,0.005185815486128078,0.003429826928152562,0.027972027972027972,0.055944055944055944,0.003992015968063872,0.1061836352279825,0.9569611465107275,0.6911113573209393,0.4034481140212195,True,False,True,False,primary_phi_fes_negative_or_incomplete_gate
hybrid_cluster_transition,primary_phi_fes,192,0.005133004314082436,0.008416804377244819,0.004514177593639095,0.005139807555098615,0.003509410201690399,0.01998001998001998,0.055944055944055944,0.003992015968063872,0.07807620237351655,0.9571140117498663,0.6916394188979222,0.40249167944414654,True,False,True,False,primary_phi_fes_negative_or_incomplete_gate
chapter7_phi_clean_sign_switch,secondary_phi_reference,1578,0.00809086263983797,0.0028288715417570907,0.005098726896367361,0.00593273634085476,0.0006962853644803205,0.022977022977022976,0.055944055944055944,0.001996007984031936,0.2567145534041224,0.9589889661209459,0.7694698684893357,0.018674519572548395,True,False,False,False,secondary_phi_reference_descriptive_only
chapter7_h_zero_crossing,secondary_phi_reference,1309,0.008076558022313877,0.0009651589350376218,0.0035296907864432155,0.00986367294894204,0.0007465953672351174,0.18281718281718282,0.29250749250749253,0.001996007984031936,0.33853841349156777,0.9622822534330212,0.7780410974922104,0.14743763336166882,True,False,False,False,secondary_phi_reference_descriptive_only

## Event Inventory

event_class,event_role,source_file,event_rule,n_events,n_labels,min_task_idx,max_task_idx,mean_strength
chapter7_d2phi_curvature_switch,contrast_switch,Chapter7/new_phi_dataset.csv,sign switch of Chapter7 d2phi curvature,6731,26,3.0,417.0,0.5707575318168661
chapter7_deps_sign_switch,contrast_switch,Chapter7/new_phi_dataset.csv,sign switch of Chapter7 deps,4650,26,2.0,417.0,0.007698070655891552
chapter7_dphi_sign_switch,contrast_switch,Chapter7/new_phi_dataset.csv,sign switch of Chapter7 dphi,4741,26,2.0,417.0,0.40650323045115333
hybrid_cluster_transition,primary_phi_fes,event_level_with_fes_phase_TRUE_RICCI.csv,transition of formal FES/hybrid-Phi cluster assignment,192,26,2.0,27.0,1.0
hybrid_fes_phase_transition,primary_phi_fes,event_level_with_fes_phase_TRUE_RICCI.csv,transition of formal FES semantic phase assignment,192,26,2.0,27.0,1.0
hybrid_phi_sign_switch,primary_phi_fes,event_level_with_fes_phase_TRUE_RICCI.csv,sign switch of formal hybrid Phi in the FES event-level table,120,26,2.0,27.0,0.8808924362318745
chapter7_h_zero_crossing,secondary_phi_reference,Chapter7/new_phi_dataset.csv,Chapter7 h=0 availability-boundary crossing,1309,26,1.0,417.0,0.015761526129687082
chapter7_phi_clean_sign_switch,secondary_phi_reference,Chapter7/new_phi_dataset.csv,sign switch of Chapter7 phi_clean,1578,26,1.0,417.0,0.6554987532125558

## Null Graph Summary

event_class,event_role,n_null_graphs,mean_null_recovery,sd_null_recovery
chapter7_d2phi_curvature_switch,contrast_switch,40,0.0004217330066243363,0.0001514166391669625
chapter7_deps_sign_switch,contrast_switch,40,-0.0005706364395789951,0.00017785485886790897
chapter7_dphi_sign_switch,contrast_switch,40,0.001190272758642429,0.00036764918384627165
chapter7_h_zero_crossing,secondary_phi_reference,40,0.00732996265507876,0.001247772987684367
chapter7_phi_clean_sign_switch,secondary_phi_reference,40,0.007394577275357648,0.00042839563148649513
hybrid_cluster_transition,primary_phi_fes,40,0.0016235941123920374,0.0010591039455370634
hybrid_fes_phase_transition,primary_phi_fes,40,0.0015666129464361207,0.0014305830200360419
hybrid_phi_sign_switch,primary_phi_fes,40,0.0026221991578900127,0.002064363920568614

## Interpretation Boundary

A positive B5.1 result would support only a limited cross-framework predictive-structure claim. It would not prove IDPC, D12RG, C12 as a physical carrier, or a final ontology.
