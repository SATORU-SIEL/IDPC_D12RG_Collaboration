# Stage B7.1 Preregistered Intersection Access Audit

Status: executed after writing Stage_B7_1_preregistration.md.

## Primary Result

- B7.1 primary-supported regimes: 0 / 24
- frozen B6-supported regimes carried into B7.1: 11 / 24

Primary support requires: true C-mediated access > A/B-history policy, fake-C non-substitutability, phase-collapse, and frozen B6-supported status.

## Primary Discrimination Summary

mode,endpoint,direction,passes_ab_history,passes_fake_c,passes_phase_collapse,frozen_b6_supported,b71_primary_supported,effect_vs_ab_history,p_vs_ab_history
linear_c_state,z_reward,A_to_C_to_B,False,True,True,True,False,-0.17875534840763826,0.9974005198960207
linear_c_state,z_reward,B_to_C_to_A,False,True,True,True,False,-0.2382599068104253,1.0
linear_c_state,rank_reward,A_to_C_to_B,False,True,True,True,False,-0.21815926191800106,0.9996000799840032
linear_c_state,rank_reward,B_to_C_to_A,False,True,True,True,False,-0.2669892663361465,1.0
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,False,True,True,True,False,-0.015479716789813854,0.8464307138572286
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,False,True,True,True,False,-0.03411364875597781,0.9906018796240752
gmr72_phase_conditioned,z_reward,A_to_C_to_B,False,True,True,True,False,-0.1790735956739478,0.9968006398720256
gmr72_phase_conditioned,z_reward,B_to_C_to_A,False,True,True,True,False,-0.24275052433238184,1.0
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,False,True,True,True,False,-0.2174923680488864,0.999000199960008
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,False,True,True,True,False,-0.2690860373089625,1.0
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,False,False,True,False,False,-0.015046704758284627,0.8202359528094381
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,False,True,True,True,False,-0.03560947271304031,0.994001199760048
fes_string_conditioned,z_reward,A_to_C_to_B,False,False,False,False,False,-0.21982495965341062,1.0
fes_string_conditioned,z_reward,B_to_C_to_A,False,False,False,False,False,-0.2688654108704679,1.0
fes_string_conditioned,rank_reward,A_to_C_to_B,False,False,False,False,False,-0.27708264379972997,1.0
fes_string_conditioned,rank_reward,B_to_C_to_A,False,False,False,False,False,-0.3119580422702673,1.0
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,False,False,False,False,False,-0.020306581289366424,0.9200159968006398
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,False,False,False,False,False,-0.035331110336318014,0.9946010797840432
combined_c_fes_gmr72,z_reward,A_to_C_to_B,False,False,True,False,False,-0.19870823919552982,0.9998000399920016
combined_c_fes_gmr72,z_reward,B_to_C_to_A,False,False,False,False,False,-0.2091108109370212,1.0
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,False,False,True,False,False,-0.2369302609844031,1.0
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,False,False,True,False,False,-0.23181417924489775,0.9998000399920016
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,False,False,False,False,False,-0.026687619052105836,0.9316136772645471
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,False,False,False,False,False,-0.02962601289606093,0.9744051189762047

## A/B-History Control Comparison

mode,endpoint,direction,comparison,mean_true_c,mean_ab_history,effect,p_greater,n_pairs,passes
linear_c_state,z_reward,A_to_C_to_B,true_c_intersection_vs_ab_history_policy,-0.6043177364472337,-0.4255623880395955,-0.17875534840763826,0.9974005198960207,79,False
linear_c_state,z_reward,B_to_C_to_A,true_c_intersection_vs_ab_history_policy,-0.6638222948500208,-0.4255623880395955,-0.2382599068104253,1.0,79,False
linear_c_state,rank_reward,A_to_C_to_B,true_c_intersection_vs_ab_history_policy,-0.567879015034395,-0.34971975311639397,-0.21815926191800106,0.9996000799840032,79,False
linear_c_state,rank_reward,B_to_C_to_A,true_c_intersection_vs_ab_history_policy,-0.6167090194525405,-0.34971975311639397,-0.2669892663361465,1.0,79,False
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,true_c_intersection_vs_ab_history_policy,-0.23268078060079295,-0.21720106381097906,-0.015479716789813854,0.8464307138572286,79,False
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,true_c_intersection_vs_ab_history_policy,-0.25131471256695687,-0.21720106381097906,-0.03411364875597781,0.9906018796240752,79,False
gmr72_phase_conditioned,z_reward,A_to_C_to_B,true_c_intersection_vs_ab_history_policy,-0.6046359837135435,-0.4255623880395955,-0.1790735956739478,0.9968006398720256,79,False
gmr72_phase_conditioned,z_reward,B_to_C_to_A,true_c_intersection_vs_ab_history_policy,-0.6683129123719772,-0.4255623880395955,-0.24275052433238184,1.0,79,False
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,true_c_intersection_vs_ab_history_policy,-0.5672121211652803,-0.34971975311639397,-0.2174923680488864,0.999000199960008,79,False
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,true_c_intersection_vs_ab_history_policy,-0.6188057904253564,-0.34971975311639397,-0.2690860373089625,1.0,79,False
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_c_intersection_vs_ab_history_policy,-0.2322477685692637,-0.21720106381097906,-0.015046704758284627,0.8202359528094381,79,False
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_c_intersection_vs_ab_history_policy,-0.25281053652401936,-0.21720106381097906,-0.03560947271304031,0.994001199760048,79,False
fes_string_conditioned,z_reward,A_to_C_to_B,true_c_intersection_vs_ab_history_policy,-0.6453873476930061,-0.4255623880395955,-0.21982495965341062,1.0,79,False
fes_string_conditioned,z_reward,B_to_C_to_A,true_c_intersection_vs_ab_history_policy,-0.6944277989100636,-0.4255623880395955,-0.2688654108704679,1.0,79,False
fes_string_conditioned,rank_reward,A_to_C_to_B,true_c_intersection_vs_ab_history_policy,-0.626802396916124,-0.34971975311639397,-0.27708264379972997,1.0,79,False
fes_string_conditioned,rank_reward,B_to_C_to_A,true_c_intersection_vs_ab_history_policy,-0.6616777953866614,-0.34971975311639397,-0.3119580422702673,1.0,79,False
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_c_intersection_vs_ab_history_policy,-0.23750764510034553,-0.21720106381097906,-0.020306581289366424,0.9200159968006398,79,False
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_c_intersection_vs_ab_history_policy,-0.25253217414729706,-0.21720106381097906,-0.035331110336318014,0.9946010797840432,79,False
combined_c_fes_gmr72,z_reward,A_to_C_to_B,true_c_intersection_vs_ab_history_policy,-0.6242706272351255,-0.4255623880395955,-0.19870823919552982,0.9998000399920016,79,False
combined_c_fes_gmr72,z_reward,B_to_C_to_A,true_c_intersection_vs_ab_history_policy,-0.6346731989766168,-0.4255623880395955,-0.2091108109370212,1.0,79,False
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,true_c_intersection_vs_ab_history_policy,-0.5866500141007969,-0.34971975311639397,-0.2369302609844031,1.0,79,False
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,true_c_intersection_vs_ab_history_policy,-0.5815339323612918,-0.34971975311639397,-0.23181417924489775,0.9998000399920016,79,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,true_c_intersection_vs_ab_history_policy,-0.2438886828630849,-0.21720106381097906,-0.026687619052105836,0.9316136772645471,79,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,true_c_intersection_vs_ab_history_policy,-0.24682707670704002,-0.21720106381097906,-0.02962601289606093,0.9744051189762047,79,False

## Fake-C Control Summary

mode,endpoint,direction,comparison,passes_all_core_fake_controls,n_core_fake_controls_passed,mean_effect_true_minus_fake
linear_c_state,rank_reward,B_to_C_to_A,true_c_vs_core_fake_c_controls,True,5,0.0682173737170786
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,true_c_vs_core_fake_c_controls,True,5,0.0642062880216323
linear_c_state,z_reward,B_to_C_to_A,true_c_vs_core_fake_c_controls,True,5,0.0616690330346876
gmr72_phase_conditioned,z_reward,B_to_C_to_A,true_c_vs_core_fake_c_controls,True,5,0.0565517862493825
linear_c_state,rank_reward,A_to_C_to_B,true_c_vs_core_fake_c_controls,True,5,0.039781039105865
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,true_c_vs_core_fake_c_controls,True,5,0.037301458971436
linear_c_state,z_reward,A_to_C_to_B,true_c_vs_core_fake_c_controls,True,5,0.0324092553852126
gmr72_phase_conditioned,z_reward,A_to_C_to_B,true_c_vs_core_fake_c_controls,True,5,0.0298850988052655
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,true_c_vs_core_fake_c_controls,True,5,0.0084388628639925
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_c_vs_core_fake_c_controls,True,5,0.0062809307925805
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,true_c_vs_core_fake_c_controls,True,5,0.0062383463832846
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,true_c_vs_core_fake_c_controls,False,3,0.0235450571691784
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,true_c_vs_core_fake_c_controls,False,3,0.0180195674245186
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_c_vs_core_fake_c_controls,False,3,0.0047051847385076
fes_string_conditioned,rank_reward,A_to_C_to_B,true_c_vs_core_fake_c_controls,False,2,0.0098603078325291
fes_string_conditioned,rank_reward,B_to_C_to_A,true_c_vs_core_fake_c_controls,False,1,0.0053084457083818
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_c_vs_core_fake_c_controls,False,1,0.0008996910055599
combined_c_fes_gmr72,z_reward,B_to_C_to_A,true_c_vs_core_fake_c_controls,False,0,0.0123433308457103
combined_c_fes_gmr72,z_reward,A_to_C_to_B,true_c_vs_core_fake_c_controls,False,0,0.0072348767243094
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,true_c_vs_core_fake_c_controls,False,0,0.0016623611220053
fes_string_conditioned,z_reward,B_to_C_to_A,true_c_vs_core_fake_c_controls,False,0,0.0013716824510713
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_c_vs_core_fake_c_controls,False,0,0.001063057358188
fes_string_conditioned,z_reward,A_to_C_to_B,true_c_vs_core_fake_c_controls,False,0,0.0006704154636776
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,true_c_vs_core_fake_c_controls,False,0,0.0005921127999546

## Phase-Collapse Summary

mode,endpoint,direction,phase_collapse_detected,first_significant_collapse_degrees,mean_true_minus_shift,narrow_boundary_supported
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,True,22.5,0.0040002198126898,True
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,True,22.5,0.0045364658737056,True
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,True,22.5,0.0040231378500666,True
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,True,22.5,0.0029442156179596,True
linear_c_state,rank_reward,B_to_C_to_A,True,22.5,0.0246760772975807,True
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,True,22.5,0.0247694688406424,True
linear_c_state,z_reward,B_to_C_to_A,True,22.5,0.0253272367584596,True
gmr72_phase_conditioned,z_reward,B_to_C_to_A,True,22.5,0.0241440118283232,True
linear_c_state,rank_reward,A_to_C_to_B,True,22.5,0.0219398932922889,True
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,True,22.5,0.0217120930824022,True
gmr72_phase_conditioned,z_reward,A_to_C_to_B,True,22.5,0.0241588449729235,True
linear_c_state,z_reward,A_to_C_to_B,True,22.5,0.0240181124994741,True
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,True,22.5,0.0198274177346307,True
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,True,22.5,0.0155981816631691,True
combined_c_fes_gmr72,z_reward,A_to_C_to_B,True,22.5,0.0167138137715247,True
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,False,,0.0030620444796074,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,False,,0.000599778822364,False
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,False,,7.153142620063727e-19,False
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,False,,-2.488049606978687e-19,False
combined_c_fes_gmr72,z_reward,B_to_C_to_A,False,,0.0108391322384529,False
fes_string_conditioned,rank_reward,B_to_C_to_A,False,,1.7001672314354365e-18,False
fes_string_conditioned,rank_reward,A_to_C_to_B,False,,2.539883973790744e-18,False
fes_string_conditioned,z_reward,B_to_C_to_A,False,,-2.2807121397304634e-19,False
fes_string_conditioned,z_reward,A_to_C_to_B,False,,1.4513622707375677e-18,False

## Frozen B6 Regime Table

mode,endpoint,path,direction_with_c,arm_type_with_c,pass_count_with_c,core_pass_count_with_c,survives_with_c,fails_with_c,mean_effect_with_c,mean_core_effect_with_c,mean_true_access_effect_with_c,direction_no_c,arm_type_no_c,pass_count_no_c,core_pass_count_no_c,survives_no_c,fails_no_c,mean_effect_no_c,mean_core_effect_no_c,mean_true_access_effect_no_c,c_necessary_pattern,access_effect_gap_with_c_minus_no_c,direction_w,true_c_non_substitutable,mean_effect_true_minus_fake,direction_z,phase_collapse_detected,first_significant_collapse_degrees,narrow_boundary_supported,b71_frozen_b6_supported
linear_c_state,rank_reward,B_path,B_to_C_to_A,with_c_intersection,5,3,True,False,0.0680890952053347,0.056847474508588,-0.6594298734361925,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.0039845075921997,-0.0013154531714615,-0.7243245405813526,True,0.0581629276800496,B_to_C_to_A,True,0.0682173737170786,B_to_C_to_A,True,22.5,True,True
gmr72_phase_conditioned,rank_reward,B_path,B_to_C_to_A,with_c_intersection,5,3,True,False,0.0649903576775532,0.0535799542626035,-0.6622754368866695,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.0039845075921997,-0.0013154531714615,-0.7243245405813526,True,0.054895407434065,B_to_C_to_A,True,0.0642062880216323,B_to_C_to_A,True,22.5,True,True
linear_c_state,rank_reward,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.0634331184861992,0.0525515792175717,-0.6645096745245741,A_to_B_no_C,no_c_direct_ab,1,0,False,True,-3.827124193004593e-05,-0.0013154531714615,-0.7243245405813526,True,0.0538670323890333,A_to_C_to_B,True,0.039781039105865,A_to_C_to_B,True,22.5,True,True
gmr72_phase_conditioned,rank_reward,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.0621815095608962,0.0506034659038305,-0.6647165268672198,A_to_B_no_C,no_c_direct_ab,1,0,False,True,-3.827124193004593e-05,-0.0013154531714615,-0.7243245405813526,True,0.051918919075292,A_to_C_to_B,True,0.037301458971436,A_to_C_to_B,True,22.5,True,True
linear_c_state,z_reward,B_path,B_to_C_to_A,with_c_intersection,5,3,True,False,0.0608969420111973,0.0480473799269546,-0.6667860859214115,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.0039686229507464,-0.0013059481053828,-0.7290410663847228,True,0.0493533280323374,B_to_C_to_A,True,0.0616690330346876,B_to_C_to_A,True,22.5,True,True
gmr72_phase_conditioned,z_reward,B_path,B_to_C_to_A,with_c_intersection,5,3,True,False,0.0573503200214344,0.0444327036950986,-0.6702306265480349,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.0039686229507464,-0.0013059481053828,-0.7290410663847228,True,0.0457386518004815,B_to_C_to_A,True,0.0565517862493825,B_to_C_to_A,True,22.5,True,True
combined_c_fes_gmr72,rank_reward,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.0454710082498663,0.04274388529251,-0.6821306903104767,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0037031103857541,-0.0013154531714615,-0.7243245405813526,True,0.0440593384639715,A_to_C_to_B,False,0.0180195674245186,A_to_C_to_B,True,22.5,True,False
combined_c_fes_gmr72,rank_reward,B_path,B_to_C_to_A,with_c_intersection,4,3,True,False,0.0377464676247083,0.0401391270952357,-0.6894363253276026,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.0042734686726179,-0.0013154531714615,-0.7243245405813526,True,0.0414545802666973,B_to_C_to_A,False,0.0235450571691784,B_to_C_to_A,True,22.5,True,False
linear_c_state,z_reward,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.0520131572576207,0.0385857228967625,-0.6758495687440289,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0016391640598244,-0.0013059481053828,-0.7290410663847228,True,0.0398916710021453,A_to_C_to_B,True,0.0324092553852126,A_to_C_to_B,True,22.5,True,True
gmr72_phase_conditioned,z_reward,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.0509744458540598,0.0366369043062387,-0.6755231193671457,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0016391640598244,-0.0013059481053828,-0.7290410663847228,True,0.0379428524116216,A_to_C_to_B,True,0.0298850988052655,A_to_C_to_B,True,22.5,True,True
combined_c_fes_gmr72,z_reward,A_path,A_to_C_to_B,with_c_intersection,4,3,True,False,0.0340722007899838,0.0275715172653278,-0.6927858882126665,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0034825897021147,-0.0013059481053828,-0.7290410663847228,True,0.0288774653707106,A_to_C_to_B,False,0.0072348767243094,A_to_C_to_B,True,22.5,True,False
linear_c_state,gmr72_bridge_composite,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.0090595011269381,0.0073625250212171,-0.2699154225098454,A_to_B_no_C,no_c_direct_ab,0,0,False,True,0.0005793757554984,-0.000176026698372,-0.2851699656780228,True,0.0075385517195891,A_to_C_to_B,True,0.0062383463832846,A_to_C_to_B,True,22.5,True,True
gmr72_phase_conditioned,gmr72_bridge_composite,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.0082407037016935,0.00651380878236,-0.2706893417146714,A_to_B_no_C,no_c_direct_ab,0,0,False,True,0.0005793757554984,-0.000176026698372,-0.2851699656780228,True,0.0066898354807321,A_to_C_to_B,False,0.0047051847385076,A_to_C_to_B,True,22.5,True,False
linear_c_state,gmr72_bridge_composite,B_path,B_to_C_to_A,with_c_intersection,5,3,True,False,0.0085134614778808,0.006244915836255,-0.2706226515180371,B_to_A_no_C,no_c_direct_ab,0,0,False,True,0.0022352058398368,-0.000176026698372,-0.2851699656780228,True,0.0064209425346271,B_to_C_to_A,True,0.0084388628639925,B_to_C_to_A,True,22.5,True,True
gmr72_phase_conditioned,gmr72_bridge_composite,B_path,B_to_C_to_A,with_c_intersection,5,3,True,False,0.0070634804859659,0.00492831001274,-0.272272695262552,B_to_A_no_C,no_c_direct_ab,0,0,False,True,0.0022352058398368,-0.000176026698372,-0.2851699656780228,True,0.005104336711112,B_to_C_to_A,True,0.0062809307925805,B_to_C_to_A,True,22.5,True,True
combined_c_fes_gmr72,z_reward,B_path,B_to_C_to_A,with_c_intersection,3,2,False,False,0.0249138426575916,0.0263810018905224,-0.7004897945439573,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.0043604488406395,-0.0013059481053828,-0.7290410663847228,False,0.0276869499959053,B_to_C_to_A,False,0.0123433308457103,B_to_C_to_A,False,,False,False
fes_string_conditioned,rank_reward,B_path,B_to_C_to_A,with_c_intersection,2,0,False,True,0.0200543208908879,0.0093066021661907,-0.709300211120681,B_to_A_no_C,no_c_direct_ab,1,0,False,True,-0.0019183127475109,-0.0013154531714615,-0.7243245405813526,False,0.0106220553376523,B_to_C_to_A,False,0.0053084457083818,B_to_C_to_A,False,,False,False
fes_string_conditioned,rank_reward,A_path,A_to_C_to_B,with_c_intersection,1,0,False,True,0.0119250346747148,0.00644405607019,-0.7072866127129764,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0016450489544063,-0.0013154531714615,-0.7243245405813526,False,0.0077595092416516,A_to_C_to_B,False,0.0098603078325291,A_to_C_to_B,False,,False,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_path,A_to_C_to_B,with_c_intersection,1,1,False,True,0.0065860512095967,0.0067026487154763,-0.2732169631469507,A_to_B_no_C,no_c_direct_ab,0,0,False,True,0.0017840799156287,-0.000176026698372,-0.2851699656780228,False,0.0068786754138484,A_to_C_to_B,False,0.0005921127999546,A_to_C_to_B,False,,False,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_path,B_to_C_to_A,with_c_intersection,0,0,False,True,0.0004483495748428,0.0025235827813993,-0.2783551417769753,B_to_A_no_C,no_c_direct_ab,0,0,False,True,0.0018078498206432,-0.000176026698372,-0.2851699656780228,False,0.0026996094797714,B_to_C_to_A,False,0.0016623611220053,B_to_C_to_A,False,,False,False
fes_string_conditioned,z_reward,B_path,B_to_C_to_A,with_c_intersection,2,0,False,True,0.0159017392853652,0.001113136702742,-0.717073226283539,B_to_A_no_C,no_c_direct_ab,1,0,False,True,-0.00129161923977,-0.0013059481053828,-0.7290410663847228,False,0.0024190848081248,B_to_C_to_A,False,0.0013716824510713,B_to_C_to_A,False,,False,False
fes_string_conditioned,gmr72_bridge_composite,A_path,A_to_C_to_B,with_c_intersection,2,2,False,False,0.0027858095800802,0.0021424989485898,-0.2745255543030141,A_to_B_no_C,no_c_direct_ab,0,0,False,True,0.0002454779988263,-0.000176026698372,-0.2851699656780228,False,0.0023185256469619,A_to_C_to_B,False,0.0008996910055599,A_to_C_to_B,False,,False,False
fes_string_conditioned,gmr72_bridge_composite,B_path,B_to_C_to_A,with_c_intersection,2,1,False,True,0.0045853159512132,0.0021289644655387,-0.275393758967806,B_to_A_no_C,no_c_direct_ab,0,0,False,True,0.0006298669868323,-0.000176026698372,-0.2851699656780228,False,0.0023049911639108,B_to_C_to_A,False,0.001063057358188,B_to_C_to_A,False,,False,False
fes_string_conditioned,z_reward,A_path,A_to_C_to_B,with_c_intersection,1,0,False,True,0.0064591573671991,-0.001994557301372,-0.7160957188629731,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0014592501016784,-0.0013059481053828,-0.7290410663847228,False,-0.0006886091959891,A_to_C_to_B,False,0.0006704154636776,A_to_C_to_B,False,,False,False

## Secondary GMR72 Module

bridge_variant,conditions,robust_accesses,strong_accesses,mean_core_pass,mean_stress_pass,mean_true_intersection,mean_control_effect
true72_forward,8,8,8,3.0,1.625,-0.2643750774739903,0.0085374030535813
half36,8,8,8,3.0,1.5,-0.264817854317667,0.0083922961972783
quadrature90,8,8,8,3.0,1.875,-0.2651778196159832,0.0085237477002502
reversed72,8,8,8,3.0,2.0,-0.2667391445705633,0.0088704192215953
skip144,8,8,8,3.0,1.625,-0.2670096446356534,0.0086591507206447
no_bridge,8,8,8,3.0,2.0,-0.6636221643031903,0.0504090126223821
random_phase,8,0,0,0.0,1.125,-0.4579201774173933,0.0067831909998723

## Secondary C12 Reconnection Screen

module,condition,role,metric,value,q_value,interpretation
b55_c12_single_ring,b55_pairwise_ac_only,pairwise_control,mean_bounded_differentiated_recovery,0.0380149671595839,0.1680497925311203,C12 ranking differs from future_AB ranking; topology readout is not identical to future AB optimizer.
b55_c12_single_ring,b55_tfc_min_gated_c_event,secondary_closure,mean_bounded_differentiated_recovery,0.0356410600811313,0.441908713692946,C12 ranking differs from future_AB ranking; topology readout is not identical to future AB optimizer.
b55_c12_single_ring,b55_shuffled_c_phase_gate,shuffle_control,mean_bounded_differentiated_recovery,0.0280324683498542,0.233402489626556,C12 ranking differs from future_AB ranking; topology readout is not identical to future AB optimizer.
b55_c12_single_ring,b55_phase_event_only_lag5,c_event_control,mean_bounded_differentiated_recovery,0.0264343140750126,0.1680497925311203,C12 ranking differs from future_AB ranking; topology readout is not identical to future AB optimizer.
b55_c12_single_ring,b55_pairwise_ab_only,pairwise_control,mean_bounded_differentiated_recovery,0.0182710269452569,0.3809128630705394,C12 ranking differs from future_AB ranking; topology readout is not identical to future AB optimizer.
b55_c12_single_ring,b55_pairwise_bc_only,pairwise_control,mean_bounded_differentiated_recovery,0.0166595860675906,0.4714730290456431,C12 ranking differs from future_AB ranking; topology readout is not identical to future AB optimizer.
b55_c12_single_ring,b55_tfc_mean_gated_c_event,primary_constraint,mean_bounded_differentiated_recovery,0.0161232330113207,0.4714730290456431,C12 ranking differs from future_AB ranking; topology readout is not identical to future AB optimizer.
b55_c12_single_ring,b55_shuffled_c_timing_gate,shuffle_control,mean_bounded_differentiated_recovery,0.0031298440950295,0.233402489626556,C12 ranking differs from future_AB ranking; topology readout is not identical to future AB optimizer.
b55_c12_single_ring,b55_density_only_gate,density_control,mean_bounded_differentiated_recovery,-0.002123330408663,0.975103734439834,C12 ranking differs from future_AB ranking; topology readout is not identical to future AB optimizer.
b55_future_ab_delta5,b55_pairwise_ab_only,future_ab,mean_future_AB,0.2528878444481199,0.0011997600479904,Future AB comparator for C12 reconnection boundary.
b55_future_ab_delta5,b55_tfc_mean_gated_c_event,future_ab,mean_future_AB,0.2295628311023768,0.0011997600479904,Future AB comparator for C12 reconnection boundary.
b55_future_ab_delta5,b55_tfc_min_gated_c_event,future_ab,mean_future_AB,0.2192093014764181,0.0403919216156768,Future AB comparator for C12 reconnection boundary.
b55_future_ab_delta5,b55_phase_event_only_lag5,future_ab,mean_future_AB,0.1979941816299631,0.598380323935213,Future AB comparator for C12 reconnection boundary.
b55_future_ab_delta5,b55_pairwise_bc_only,future_ab,mean_future_AB,0.1806152452371477,0.9854029194161168,Future AB comparator for C12 reconnection boundary.
b55_future_ab_delta5,b55_pairwise_ac_only,future_ab,mean_future_AB,0.1640410982123807,0.9854029194161168,Future AB comparator for C12 reconnection boundary.
b56_projection_c12,b56_C_boundary_A_projection,boundary_projection,mean_bounded_differentiated_recovery,0.0405503514611333,0.0869565217391304,Projection screen for secondary C12 topology-readout module.
b56_projection_c12,b56_C_boundary_B_swapped_control,ab_symmetry_control,mean_bounded_differentiated_recovery,0.0398811075087122,0.0869565217391304,Projection screen for secondary C12 topology-readout module.
b56_projection_c12,b56_C_phase_projection,phase_projection,mean_bounded_differentiated_recovery,0.0267085069945686,0.0869565217391304,Projection screen for secondary C12 topology-readout module.
b56_projection_c12,b56_C_full_projection,primary_projection,mean_bounded_differentiated_recovery,0.0246518413978093,0.2971014492753623,Projection screen for secondary C12 topology-readout module.
b56_projection_c12,b56_C_boundary_B_projection,boundary_projection,mean_bounded_differentiated_recovery,0.0217436919290297,0.2521739130434782,Projection screen for secondary C12 topology-readout module.
b56_projection_c12,b56_C_boundary_A_swapped_control,ab_symmetry_control,mean_bounded_differentiated_recovery,0.0215829477005767,0.2521739130434782,Projection screen for secondary C12 topology-readout module.
b56_projection_c12,b56_C_memory_projection,memory_projection,mean_bounded_differentiated_recovery,0.0153033057586198,0.4099378881987577,Projection screen for secondary C12 topology-readout module.

## Interpretation Boundary

C12 is secondary. B7.1 tests C-mediated intersection access first, then screens whether C12 remains a candidate downstream topology-readout surface.

## Settings

- n_folds: 5
- min_state_events: 8
- temperature: 0.35
- n_perm: 5000
- alpha: 0.05
- seed: 71010
