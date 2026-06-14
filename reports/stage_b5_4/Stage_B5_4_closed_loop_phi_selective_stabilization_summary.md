# Stage B5.4 Closed-Loop Phi Selective-Stabilization Audit Summary

## Purpose

B5.4 tests whether weak closed-loop phi improves selective C12 stabilization without collapsing negative controls.

The primary endpoint is narrowed to the closed-loop phi sign-switch. FES phase and cluster transitions are treated as auxiliary coherence probes, not as a required primary family. Full dphi is treated as an event-density warning control, and count-matched dphi is treated as the main negative control.

## Run Parameters

- eta: 0.075
- primary topology: C12(1,2)
- contrast topology: C8(1)
- primary endpoint: bounded_differentiated_recovery
- primary fixed run: 240 runs, 80 degree-null graphs, 8 null runs per graph, 160 temporal-profile runs, seed 54054
- count-matched dphi stress run: 180 runs, 60 degree-null graphs, 8 null runs per graph, 120 temporal-profile runs, seed 54055

## Main Finding

The broad Phi/FES-family claim is not supported, because the FES phase-transition and cluster-transition rows do not reproduce the closed-loop phi sign-switch effect.

The narrower closed-loop phi sign-switch claim is supported as a topology-specific stabilization result:

- p vs shifted/random: 0.043659
- p vs C8: 0.004149
- p vs degree-null: 0.001560
- effect vs degree-null mean: 0.009825
- late-window stability: 0.623026

The count-matched dphi controls remain negative:

- best count-matched recovery: 0.000532
- best count-matched p vs shifted/random: 0.662050
- best count-matched p vs degree-null: 0.309771

## Primary Endpoint

event_class,public_role,n_seed_events,mean_bounded_differentiated_recovery,effect_vs_time_shifted,effect_vs_random_event,effect_vs_C8,effect_vs_degree_null_mean,p_vs_time_shifted_and_random,p_vs_C8,p_vs_degree_null,late_window_stability
closed_loop_phi_sign_switch,primary_endpoint,502,0.0254964369969885,0.0074302093728404,0.0061178766549628,0.0306720547143377,0.0098251599083875,0.0436590436590436,0.0041493775933609,0.0015600624024961,0.6230257712732882
eta075_phi_sign_primary,primary_endpoint_replication,502,0.0254670688620308,0.0071334092245609,0.0054865556232239,0.0307085177036247,0.0098300663016748,0.074792243767313,0.005524861878453,0.002079002079002,0.620254429769156

## Auxiliary Coherence Probes

event_class,public_role,n_seed_events,mean_bounded_differentiated_recovery,effect_vs_time_shifted,effect_vs_random_event,effect_vs_C8,effect_vs_degree_null_mean,p_vs_time_shifted_and_random,p_vs_C8,p_vs_degree_null,late_window_stability
closed_loop_fes_phase_transition,auxiliary_coherence_probe,192,0.0001337463749539,-0.0026811830793151,-0.0004801198573869,0.0008909064098705,0.0006563532388744,0.6985446985446986,0.3195020746887966,0.4274570982839313,0.7623652005035123
closed_loop_cluster_transition,auxiliary_coherence_probe,192,0.000165244916528,-0.0029851139353124,-0.0003601632660492,0.0009006738980153,3.549241742881304e-05,0.7110187110187111,0.3236514522821577,0.5085803432137286,0.7576386126248662

## Warning and Negative Controls

event_class,public_role,n_seed_events,mean_bounded_differentiated_recovery,effect_vs_time_shifted,effect_vs_random_event,effect_vs_C8,effect_vs_degree_null_mean,p_vs_time_shifted_and_random,p_vs_C8,p_vs_degree_null,late_window_stability
closed_loop_dphi_sign_switch,warning_control,1144,0.0029593831364827,0.0019613980924702,0.0023923289793701,0.0019580936768333,0.0008229182560092,0.0353430353430353,0.0373443983402489,0.1950078003120124,0.5165281994639404
eta075_dphi_all_control,warning_control,1144,0.0029208272110202,0.001874795155771,0.0023652714479549,0.0019382165158534,0.0006119997668664,0.0360110803324099,0.0220994475138121,0.2661122661122661,0.5159881239887577
eta075_dphi_interval_control,warning_control,1144,0.0028854891991251,0.0019044783831551,0.0022025092155803,0.0017568317710807,0.0008589318629094,0.0415512465373961,0.0276243093922651,0.1808731808731808,0.5162064737465457
eta075_dphi_interval_count_match_00,main_negative_control,502,-0.0006495773555236,-0.0013457746871953,-0.0010323726087863,-0.0003327310609412,-7.617619012285763e-05,0.8448753462603878,0.6685082872928176,0.5363825363825364,0.6478416279431023
eta075_dphi_interval_count_match_01,main_negative_control,502,-0.0015702795278032,-0.0033407447412221,-0.0020379707564233,-0.0013542808652572,-0.0007426226358704,0.9473684210526316,0.8839779005524862,0.7318087318087318,0.6645158625939921
eta075_dphi_interval_count_match_02,main_negative_control,502,0.0005317799243053,-0.0010976921918304,7.256948074357421e-05,-0.0007149826592432,-1.922390536520844e-05,0.6620498614958449,0.7403314917127072,0.4948024948024948,0.5956558106597762
eta075_dphi_interval_count_match_03,main_negative_control,502,6.000965592791463e-05,-0.0016580149172555,-0.0004611131964781,0.0007899604627243,0.0006629233685072,0.7894736842105263,0.2209944751381215,0.3097713097713098,0.6168540224757695

## Event Inventory

event_class,event_role,source_file,event_rule,n_events,n_labels,min_task_idx,max_task_idx,mean_strength
eta075_dphi_all_control,contrast_switch,closed-loop phi reconstruction from Chapter7/new_phi_dataset.csv,closed-loop dphi warning/control event,1144,26,2.0,417.0,0.0388157983754924
eta075_dphi_interval_control,contrast_switch,closed-loop phi reconstruction from Chapter7/new_phi_dataset.csv,closed-loop dphi warning/control event,1144,26,2.0,417.0,0.0388157983754924
eta075_dphi_interval_count_match_00,contrast_switch,closed-loop phi reconstruction from Chapter7/new_phi_dataset.csv,count-matched dphi negative control,502,26,2.0,416.0,0.0423147023262146
eta075_dphi_interval_count_match_01,contrast_switch,closed-loop phi reconstruction from Chapter7/new_phi_dataset.csv,count-matched dphi negative control,502,26,2.0,416.0,0.037294544828763
eta075_dphi_interval_count_match_02,contrast_switch,closed-loop phi reconstruction from Chapter7/new_phi_dataset.csv,count-matched dphi negative control,502,26,2.0,415.0,0.0382570271935709
eta075_dphi_interval_count_match_03,contrast_switch,closed-loop phi reconstruction from Chapter7/new_phi_dataset.csv,count-matched dphi negative control,502,26,2.0,415.0,0.0391973377272248
eta075_phi_sign_primary,primary_phi_fes,closed-loop phi reconstruction from Chapter7/new_phi_dataset.csv,closed-loop phi sign-switch primary endpoint,502,26,1.0,417.0,0.2259009710696841

## Interpretation

B5.4 should be interpreted as a narrowed positive result for closed-loop phi sign-switch topology-specific stabilization, not as a broad Phi/FES-family positive result.

The key gain relative to B5.2 is degree-null separation. In B5.2, the hybrid phi sign-switch degree-null p-value was approximately 0.092. In B5.4, the closed-loop phi sign-switch degree-null p-value is approximately 0.0016 in the fixed run and 0.0021 in the count-matched stress run.

The full dphi warning control can show shifted/random effects, but the count-matched dphi controls remain negative. This supports the interpretation that the full dphi row is an event-density warning rather than a matched-event specificity failure.

## Output Files

- `reports/stage_b5_4/Stage_B5_4_closed_loop_phi_selective_stabilization_summary.md`
- `reports/stage_b5_4/Stage_B5_4_closed_loop_phi_selective_stabilization_results.csv`
- `reports/stage_b5_4/Stage_B5_4_closed_loop_phi_selective_stabilization_event_inventory.csv`
- `scripts/test_Stage_B5_4_closed_loop_phi_selective_stabilization.py`

## Replication Row

The count-matched stress run gives p vs shifted/random = 0.074792, p vs C8 = 0.005525, and p vs degree-null = 0.002079 for the same eta=0.075 closed-loop phi sign-switch endpoint.
