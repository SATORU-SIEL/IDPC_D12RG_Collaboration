# Stage B7.2a O1/O2 Proxy Provenance Decomposition

Status: executed after writing Stage_B7_2a_preregistration.md and Stage_B7_2a_plan_email_draft.md.

## Result

- frozen B6-supported regimes tested: 11 / 24
- regimes where joint endpoint-adjacent O1/O2 still bounds true C: 11 / 11

## Component Summary

component,frozen_regimes_tested,c_beats_component,component_bounds_c,mean_true_minus_component
o1_lag0_only,11,0.0,11,-0.10035179434037457
o2_lag5_only,11,0.0,11,-0.12087284851778532
o1_o2_joint,11,0.0,11,-0.2145116286770407
phase_removed_o1o2,11,0.0,11,-0.2145116286770407
tfc_removed_o1o2,11,0.0,11,-0.2015876857631057
side_shuffled_o1o2,11,11.0,0,0.06832167627892018
memory_only_o1o2,11,11.0,0,0.08623385658766722
residual_endpoint_o1o2,11,0.0,11,-0.21094844067170537
classification:pure_ab_operator_proxy,11,,11,
classification:phase_sensitive_proxy,11,,0,
classification:tfc_compressed_proxy,11,,0,
classification:side_directional_proxy,11,,11,
classification:memory_proxy,11,,0,
classification:residual_endpoint_proxy,11,,11,
classification:compound_proxy,11,,0,

## Boundary Classification

mode,endpoint,direction,frozen_b6_supported,joint_o1o2_boundary,boundary_classification,c_beats_o1_lag0_only,effect_o1_lag0_only,c_beats_o2_lag5_only,effect_o2_lag5_only,c_beats_o1_o2_joint,effect_o1_o2_joint,c_beats_phase_removed_o1o2,effect_phase_removed_o1o2,c_beats_tfc_removed_o1o2,effect_tfc_removed_o1o2,c_beats_side_shuffled_o1o2,effect_side_shuffled_o1o2,c_beats_memory_only_o1o2,effect_memory_only_o1o2,c_beats_residual_endpoint_o1o2,effect_residual_endpoint_o1o2
linear_c_state,z_reward,A_to_C_to_B,True,True,pure_ab_operator_proxy;side_directional_proxy;residual_endpoint_proxy,False,-0.15451260529766234,False,-0.17268856506517644,False,-0.28516226310355647,False,-0.28516226310355647,False,-0.2747311534589554,True,0.06244366417738017,True,0.08803385534856856,False,-0.28345537210602967
linear_c_state,z_reward,B_to_C_to_A,True,True,pure_ab_operator_proxy;side_directional_proxy;residual_endpoint_proxy,False,-0.1197288017347796,False,-0.1379047615022937,False,-0.2503784595406738,False,-0.2503784595406738,False,-0.2399473498960726,True,0.09722746774026289,True,0.12281765891145129,False,-0.24867156854314693
linear_c_state,rank_reward,A_to_C_to_B,True,True,pure_ab_operator_proxy;side_directional_proxy;residual_endpoint_proxy,False,-0.14347611617982028,False,-0.17864788267811418,False,-0.3056827120150917,False,-0.3056827120150917,False,-0.2847921321510606,True,0.08066793667512323,True,0.10141515971421236,False,-0.2986608837727693
linear_c_state,rank_reward,B_to_C_to_A,True,True,pure_ab_operator_proxy;side_directional_proxy;residual_endpoint_proxy,False,-0.11928133460415116,False,-0.15445310110244503,False,-0.2814879304394226,False,-0.2814879304394226,False,-0.2605973505753914,True,0.10486271825079237,True,0.1256099412898815,False,-0.27446610219710016
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,True,True,pure_ab_operator_proxy;side_directional_proxy;residual_endpoint_proxy,False,-0.007033454604466362,False,-0.011147018233895101,False,-0.0351445089840215,False,-0.0351445089840215,False,-0.029518970977769243,True,0.023302174559633078,True,0.027196950078002168,False,-0.0337177786175909
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,True,True,pure_ab_operator_proxy;side_directional_proxy;residual_endpoint_proxy,False,-7.526686217975162e-05,False,-0.004188830491608496,False,-0.028186321241734903,False,-0.028186321241734903,False,-0.02256078323548264,True,0.030260362301919683,True,0.03415513782028877,False,-0.02675959087530429
gmr72_phase_conditioned,z_reward,A_to_C_to_B,True,True,pure_ab_operator_proxy;side_directional_proxy;residual_endpoint_proxy,False,-0.15911472209578137,False,-0.1772906818632955,False,-0.28976437990167553,False,-0.28976437990167553,False,-0.27933327025707444,True,0.0578415473792611,True,0.08343173855044948,False,-0.2880574889041488
gmr72_phase_conditioned,z_reward,B_to_C_to_A,True,True,pure_ab_operator_proxy;side_directional_proxy;residual_endpoint_proxy,False,-0.12714683498885762,False,-0.1453227947563717,False,-0.2577964927947518,False,-0.2577964927947518,False,-0.24736538315015066,True,0.08980943448618488,True,0.11539962565737329,False,-0.25608960179722495
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,True,True,pure_ab_operator_proxy;side_directional_proxy;residual_endpoint_proxy,False,-0.14807664402328594,False,-0.18324841052157984,False,-0.3102832398585573,False,-0.3102832398585573,False,-0.28939265999452624,True,0.07606740883165758,True,0.09681463187074671,False,-0.30326141161623493
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,True,True,pure_ab_operator_proxy;side_directional_proxy;residual_endpoint_proxy,False,-0.12283115806775742,False,-0.15800292456605125,False,-0.2850377539030289,False,-0.2850377539030289,False,-0.26414717403899773,True,0.10131289478718611,True,0.12206011782627524,False,-0.2780159256607064
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,False,False,no_frozen_joint_boundary,False,-0.00929257745047283,False,-0.013406141079901566,False,-0.03740363183002798,False,-0.03740363183002798,False,-0.031778093823775715,True,0.02104305171362661,True,0.024937827231995703,False,-0.03597690146359737
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,True,True,pure_ab_operator_proxy;side_directional_proxy;residual_endpoint_proxy,False,-0.0025927992853784975,False,-0.006706362914807244,False,-0.03070385366493364,False,-0.03070385366493364,False,-0.02507831565868139,True,0.027742829878720936,True,0.031637605397090034,False,-0.029277123298503037
fes_string_conditioned,z_reward,A_to_C_to_B,False,False,no_frozen_joint_boundary,False,-0.2047511150341162,False,-0.22292707480163032,False,-0.33540077284001035,False,-0.33540077284001035,False,-0.32496966319540926,False,0.012205154440926316,False,0.037795345612114714,False,-0.33369388184248355
fes_string_conditioned,z_reward,B_to_C_to_A,False,False,no_frozen_joint_boundary,False,-0.19389418068563244,False,-0.21207014045314654,False,-0.32454383849152657,False,-0.32454383849152657,False,-0.31411272884692554,False,0.02306208878941007,True,0.04865227996059845,False,-0.32283694749399977
fes_string_conditioned,rank_reward,A_to_C_to_B,False,False,no_frozen_joint_boundary,False,-0.19458679143872887,False,-0.22975855793702274,False,-0.3567933872740003,False,-0.3567933872740003,False,-0.3359028074099691,False,0.029557261416214675,True,0.050304484455303805,False,-0.34977155903167784
fes_string_conditioned,rank_reward,B_to_C_to_A,False,False,no_frozen_joint_boundary,False,-0.18590961433209632,False,-0.2210813808303902,False,-0.3481162101673678,False,-0.3481162101673678,False,-0.3272256303033366,False,0.0382344385228472,True,0.05898166156193632,False,-0.34109438192504526
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,False,False,no_frozen_joint_boundary,False,-0.01511466795380562,False,-0.019228231583234362,False,-0.043225722333360764,False,-0.043225722333360764,False,-0.0376001843271085,False,0.015220961210293819,True,0.01911573672866291,False,-0.04179899196693016
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,False,False,no_frozen_joint_boundary,False,-0.01228602483267831,False,-0.016399588462107054,False,-0.040397079212233455,False,-0.040397079212233455,False,-0.034771541205981187,True,0.01804960433142113,True,0.02194437984979022,False,-0.03897034884580284
combined_c_fes_gmr72,z_reward,A_to_C_to_B,False,False,no_frozen_joint_boundary,False,-0.20157890545755805,False,-0.21975486522507218,False,-0.33222856326345224,False,-0.33222856326345224,False,-0.32179745361885115,False,0.015377364017484414,False,0.040967555188672795,False,-0.3305216722659254
combined_c_fes_gmr72,z_reward,B_to_C_to_A,False,False,no_frozen_joint_boundary,False,-0.21142187424299344,False,-0.22959783401050757,False,-0.34207153204888757,False,-0.34207153204888757,False,-0.33164042240428643,False,0.005534395232049061,False,0.031124586403237463,False,-0.3403646410513608
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,False,False,no_frozen_joint_boundary,False,-0.1952335018920586,False,-0.2304052683903525,False,-0.35744009772733004,False,-0.35744009772733004,False,-0.3365495178632989,False,0.028910550962884942,True,0.04965777400197407,False,-0.35041826948500754
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,False,False,no_frozen_joint_boundary,False,-0.2047652389019064,False,-0.23993700540020024,False,-0.3669718347371778,False,-0.3669718347371778,False,-0.3460812548731467,False,0.019378813953037147,True,0.04012603699212628,False,-0.35995000649485537
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,False,False,no_frozen_joint_boundary,False,-0.01957956603687851,False,-0.023693129666307256,False,-0.047690620416433654,False,-0.047690620416433654,False,-0.0420650824101814,False,0.010756063127220923,False,0.014650838645590015,False,-0.04626389005000305
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,False,False,no_frozen_joint_boundary,False,-0.020813043950160634,False,-0.02492660757958937,False,-0.04892409832971578,False,-0.04892409832971578,False,-0.04329856032346352,False,0.009522585213938804,False,0.013417360732307896,False,-0.04749736796328517

## Decomposition Comparison

mode,endpoint,direction,control_level,mean_true_c,mean_control,effect_true_minus_control,p_true_greater,n_pairs,passes
linear_c_state,z_reward,A_to_C_to_B,o1_lag0_only,-0.6485108812946611,-0.4939982759969987,-0.15451260529766234,1.0,145,False
linear_c_state,z_reward,A_to_C_to_B,o2_lag5_only,-0.6485108812946611,-0.4758223162294845,-0.17268856506517644,1.0,145,False
linear_c_state,z_reward,A_to_C_to_B,o1_o2_joint,-0.6485108812946611,-0.36334861819110453,-0.28516226310355647,1.0,145,False
linear_c_state,z_reward,A_to_C_to_B,phase_removed_o1o2,-0.6485108812946611,-0.36334861819110453,-0.28516226310355647,1.0,145,False
linear_c_state,z_reward,A_to_C_to_B,tfc_removed_o1o2,-0.6485108812946611,-0.3737797278357056,-0.2747311534589554,1.0,145,False
linear_c_state,z_reward,A_to_C_to_B,side_shuffled_o1o2,-0.6485108812946611,-0.7109545454720411,0.06244366417738017,0.015996800639872025,145,True
linear_c_state,z_reward,A_to_C_to_B,memory_only_o1o2,-0.6485108812946611,-0.7365447366432295,0.08803385534856856,0.0007998400319936012,145,True
linear_c_state,z_reward,A_to_C_to_B,residual_endpoint_o1o2,-0.6485108812946611,-0.36505550918863133,-0.28345537210602967,1.0,145,False
linear_c_state,z_reward,B_to_C_to_A,o1_lag0_only,-0.6137270777317783,-0.4939982759969987,-0.1197288017347796,1.0,145,False
linear_c_state,z_reward,B_to_C_to_A,o2_lag5_only,-0.6137270777317783,-0.4758223162294845,-0.1379047615022937,0.9994001199760048,145,False
linear_c_state,z_reward,B_to_C_to_A,o1_o2_joint,-0.6137270777317783,-0.36334861819110453,-0.2503784595406738,1.0,145,False
linear_c_state,z_reward,B_to_C_to_A,phase_removed_o1o2,-0.6137270777317783,-0.36334861819110453,-0.2503784595406738,1.0,145,False
linear_c_state,z_reward,B_to_C_to_A,tfc_removed_o1o2,-0.6137270777317783,-0.3737797278357056,-0.2399473498960726,1.0,145,False
linear_c_state,z_reward,B_to_C_to_A,side_shuffled_o1o2,-0.6137270777317783,-0.7109545454720411,0.09722746774026289,0.0021995600879824036,145,True
linear_c_state,z_reward,B_to_C_to_A,memory_only_o1o2,-0.6137270777317783,-0.7365447366432295,0.12281765891145129,0.0001999600079984003,145,True
linear_c_state,z_reward,B_to_C_to_A,residual_endpoint_o1o2,-0.6137270777317783,-0.36505550918863133,-0.24867156854314693,1.0,145,False
linear_c_state,rank_reward,A_to_C_to_B,o1_lag0_only,-0.6064597123342564,-0.4629835961544362,-0.14347611617982028,1.0,145,False
linear_c_state,rank_reward,A_to_C_to_B,o2_lag5_only,-0.6064597123342564,-0.4278118296561423,-0.17864788267811418,1.0,145,False
linear_c_state,rank_reward,A_to_C_to_B,o1_o2_joint,-0.6064597123342564,-0.3007770003191647,-0.3056827120150917,1.0,145,False
linear_c_state,rank_reward,A_to_C_to_B,phase_removed_o1o2,-0.6064597123342564,-0.3007770003191647,-0.3056827120150917,1.0,145,False
linear_c_state,rank_reward,A_to_C_to_B,tfc_removed_o1o2,-0.6064597123342564,-0.32166758018319586,-0.2847921321510606,1.0,145,False
linear_c_state,rank_reward,A_to_C_to_B,side_shuffled_o1o2,-0.6064597123342564,-0.6871276490093796,0.08066793667512323,0.0033993201359728054,145,True
linear_c_state,rank_reward,A_to_C_to_B,memory_only_o1o2,-0.6064597123342564,-0.7078748720484688,0.10141515971421236,0.0001999600079984003,145,True
linear_c_state,rank_reward,A_to_C_to_B,residual_endpoint_o1o2,-0.6064597123342564,-0.30779882856148716,-0.2986608837727693,1.0,145,False
linear_c_state,rank_reward,B_to_C_to_A,o1_lag0_only,-0.5822649307585873,-0.4629835961544362,-0.11928133460415116,1.0,145,False
linear_c_state,rank_reward,B_to_C_to_A,o2_lag5_only,-0.5822649307585873,-0.4278118296561423,-0.15445310110244503,1.0,145,False
linear_c_state,rank_reward,B_to_C_to_A,o1_o2_joint,-0.5822649307585873,-0.3007770003191647,-0.2814879304394226,1.0,145,False
linear_c_state,rank_reward,B_to_C_to_A,phase_removed_o1o2,-0.5822649307585873,-0.3007770003191647,-0.2814879304394226,1.0,145,False
linear_c_state,rank_reward,B_to_C_to_A,tfc_removed_o1o2,-0.5822649307585873,-0.32166758018319586,-0.2605973505753914,1.0,145,False
linear_c_state,rank_reward,B_to_C_to_A,side_shuffled_o1o2,-0.5822649307585873,-0.6871276490093796,0.10486271825079237,0.0003999200159968006,145,True
linear_c_state,rank_reward,B_to_C_to_A,memory_only_o1o2,-0.5822649307585873,-0.7078748720484688,0.1256099412898815,0.0001999600079984003,145,True
linear_c_state,rank_reward,B_to_C_to_A,residual_endpoint_o1o2,-0.5822649307585873,-0.30779882856148716,-0.27446610219710016,1.0,145,False
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,o1_lag0_only,-0.27285085973688367,-0.26581740513241725,-0.007033454604466362,0.7408518296340731,145,False
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,o2_lag5_only,-0.27285085973688367,-0.2617038415029886,-0.011147018233895101,0.8356328734253149,145,False
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,o1_o2_joint,-0.27285085973688367,-0.23770635075286214,-0.0351445089840215,0.9998000399920016,145,False
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,phase_removed_o1o2,-0.27285085973688367,-0.23770635075286214,-0.0351445089840215,0.9994001199760048,145,False
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,tfc_removed_o1o2,-0.27285085973688367,-0.24333188875911443,-0.029518970977769243,0.9964007198560288,145,False
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,side_shuffled_o1o2,-0.27285085973688367,-0.29615303429651674,0.023302174559633078,0.019596080783843232,145,True
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,memory_only_o1o2,-0.27285085973688367,-0.3000478098148858,0.027196950078002168,0.007798440311937612,145,True
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,residual_endpoint_o1o2,-0.27285085973688367,-0.23913308111929277,-0.0337177786175909,0.9998000399920016,145,False
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,o1_lag0_only,-0.26589267199459704,-0.26581740513241725,-7.526686217975162e-05,0.495500899820036,145,False
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,o2_lag5_only,-0.26589267199459704,-0.2617038415029886,-0.004188830491608496,0.6282743451309738,145,False
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,o1_o2_joint,-0.26589267199459704,-0.23770635075286214,-0.028186321241734903,0.99500099980004,145,False
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,phase_removed_o1o2,-0.26589267199459704,-0.23770635075286214,-0.028186321241734903,0.9928014397120576,145,False
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,tfc_removed_o1o2,-0.26589267199459704,-0.24333188875911443,-0.02256078323548264,0.9722055588882224,145,False
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,side_shuffled_o1o2,-0.26589267199459704,-0.29615303429651674,0.030260362301919683,0.005598880223955209,145,True
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,memory_only_o1o2,-0.26589267199459704,-0.3000478098148858,0.03415513782028877,0.004399120175964807,145,True
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,residual_endpoint_o1o2,-0.26589267199459704,-0.23913308111929277,-0.02675959087530429,0.9936012797440512,145,False
gmr72_phase_conditioned,z_reward,A_to_C_to_B,o1_lag0_only,-0.6531129980927801,-0.4939982759969987,-0.15911472209578137,1.0,145,False
gmr72_phase_conditioned,z_reward,A_to_C_to_B,o2_lag5_only,-0.6531129980927801,-0.4758223162294845,-0.1772906818632955,1.0,145,False
gmr72_phase_conditioned,z_reward,A_to_C_to_B,o1_o2_joint,-0.6531129980927801,-0.36334861819110453,-0.28976437990167553,1.0,145,False
gmr72_phase_conditioned,z_reward,A_to_C_to_B,phase_removed_o1o2,-0.6531129980927801,-0.36334861819110453,-0.28976437990167553,1.0,145,False
gmr72_phase_conditioned,z_reward,A_to_C_to_B,tfc_removed_o1o2,-0.6531129980927801,-0.3737797278357056,-0.27933327025707444,1.0,145,False
gmr72_phase_conditioned,z_reward,A_to_C_to_B,side_shuffled_o1o2,-0.6531129980927801,-0.7109545454720411,0.0578415473792611,0.023395320935812838,145,True
gmr72_phase_conditioned,z_reward,A_to_C_to_B,memory_only_o1o2,-0.6531129980927801,-0.7365447366432295,0.08343173855044948,0.0015996800639872025,145,True
gmr72_phase_conditioned,z_reward,A_to_C_to_B,residual_endpoint_o1o2,-0.6531129980927801,-0.36505550918863133,-0.2880574889041488,1.0,145,False
gmr72_phase_conditioned,z_reward,B_to_C_to_A,o1_lag0_only,-0.6211451109858563,-0.4939982759969987,-0.12714683498885762,1.0,145,False
gmr72_phase_conditioned,z_reward,B_to_C_to_A,o2_lag5_only,-0.6211451109858563,-0.4758223162294845,-0.1453227947563717,0.9996000799840032,145,False
gmr72_phase_conditioned,z_reward,B_to_C_to_A,o1_o2_joint,-0.6211451109858563,-0.36334861819110453,-0.2577964927947518,1.0,145,False
gmr72_phase_conditioned,z_reward,B_to_C_to_A,phase_removed_o1o2,-0.6211451109858563,-0.36334861819110453,-0.2577964927947518,1.0,145,False
gmr72_phase_conditioned,z_reward,B_to_C_to_A,tfc_removed_o1o2,-0.6211451109858563,-0.3737797278357056,-0.24736538315015066,1.0,145,False
gmr72_phase_conditioned,z_reward,B_to_C_to_A,side_shuffled_o1o2,-0.6211451109858563,-0.7109545454720411,0.08980943448618488,0.0013997200559888023,145,True
gmr72_phase_conditioned,z_reward,B_to_C_to_A,memory_only_o1o2,-0.6211451109858563,-0.7365447366432295,0.11539962565737329,0.0001999600079984003,145,True
gmr72_phase_conditioned,z_reward,B_to_C_to_A,residual_endpoint_o1o2,-0.6211451109858563,-0.36505550918863133,-0.25608960179722495,1.0,145,False
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,o1_lag0_only,-0.611060240177722,-0.4629835961544362,-0.14807664402328594,1.0,145,False
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,o2_lag5_only,-0.611060240177722,-0.4278118296561423,-0.18324841052157984,1.0,145,False
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,o1_o2_joint,-0.611060240177722,-0.3007770003191647,-0.3102832398585573,1.0,145,False
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,phase_removed_o1o2,-0.611060240177722,-0.3007770003191647,-0.3102832398585573,1.0,145,False
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,tfc_removed_o1o2,-0.611060240177722,-0.32166758018319586,-0.28939265999452624,1.0,145,False
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,side_shuffled_o1o2,-0.611060240177722,-0.6871276490093796,0.07606740883165758,0.004199160167966407,145,True
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,memory_only_o1o2,-0.611060240177722,-0.7078748720484688,0.09681463187074671,0.0009998000399920016,145,True
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,residual_endpoint_o1o2,-0.611060240177722,-0.30779882856148716,-0.30326141161623493,1.0,145,False
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,o1_lag0_only,-0.5858147542221935,-0.4629835961544362,-0.12283115806775742,1.0,145,False
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,o2_lag5_only,-0.5858147542221935,-0.4278118296561423,-0.15800292456605125,1.0,145,False
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,o1_o2_joint,-0.5858147542221935,-0.3007770003191647,-0.2850377539030289,1.0,145,False
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,phase_removed_o1o2,-0.5858147542221935,-0.3007770003191647,-0.2850377539030289,1.0,145,False
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,tfc_removed_o1o2,-0.5858147542221935,-0.32166758018319586,-0.26414717403899773,1.0,145,False
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,side_shuffled_o1o2,-0.5858147542221935,-0.6871276490093796,0.10131289478718611,0.0007998400319936012,145,True
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,memory_only_o1o2,-0.5858147542221935,-0.7078748720484688,0.12206011782627524,0.0001999600079984003,145,True
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,residual_endpoint_o1o2,-0.5858147542221935,-0.30779882856148716,-0.2780159256607064,1.0,145,False
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,o1_lag0_only,-0.2751099825828901,-0.26581740513241725,-0.00929257745047283,0.8108378324335133,145,False
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,o2_lag5_only,-0.2751099825828901,-0.2617038415029886,-0.013406141079901566,0.8782243551289742,145,False
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,o1_o2_joint,-0.2751099825828901,-0.23770635075286214,-0.03740363183002798,0.9996000799840032,145,False
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,phase_removed_o1o2,-0.2751099825828901,-0.23770635075286214,-0.03740363183002798,0.9998000399920016,145,False
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,tfc_removed_o1o2,-0.2751099825828901,-0.24333188875911443,-0.031778093823775715,0.9982003599280144,145,False
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,side_shuffled_o1o2,-0.2751099825828901,-0.29615303429651674,0.02104305171362661,0.03839232153569286,145,True
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,memory_only_o1o2,-0.2751099825828901,-0.3000478098148858,0.024937827231995703,0.015796840631873626,145,True
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,residual_endpoint_o1o2,-0.2751099825828901,-0.23913308111929277,-0.03597690146359737,0.999000199960008,145,False
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,o1_lag0_only,-0.2684102044177958,-0.26581740513241725,-0.0025927992853784975,0.5838832233553289,145,False
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,o2_lag5_only,-0.2684102044177958,-0.2617038415029886,-0.006706362914807244,0.7028594281143771,145,False
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,o1_o2_joint,-0.2684102044177958,-0.23770635075286214,-0.03070385366493364,0.9978004399120176,145,False
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,phase_removed_o1o2,-0.2684102044177958,-0.23770635075286214,-0.03070385366493364,0.997000599880024,145,False
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,tfc_removed_o1o2,-0.2684102044177958,-0.24333188875911443,-0.02507831565868139,0.9818036392721455,145,False
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,side_shuffled_o1o2,-0.2684102044177958,-0.29615303429651674,0.027742829878720936,0.008798240351929614,145,True
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,memory_only_o1o2,-0.2684102044177958,-0.3000478098148858,0.031637605397090034,0.00639872025594881,145,True
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,residual_endpoint_o1o2,-0.2684102044177958,-0.23913308111929277,-0.029277123298503037,0.9952009598080384,145,False
fes_string_conditioned,z_reward,A_to_C_to_B,o1_lag0_only,-0.6987493910311149,-0.4939982759969987,-0.2047511150341162,1.0,145,False
fes_string_conditioned,z_reward,A_to_C_to_B,o2_lag5_only,-0.6987493910311149,-0.4758223162294845,-0.22292707480163032,1.0,145,False
fes_string_conditioned,z_reward,A_to_C_to_B,o1_o2_joint,-0.6987493910311149,-0.36334861819110453,-0.33540077284001035,1.0,145,False
fes_string_conditioned,z_reward,A_to_C_to_B,phase_removed_o1o2,-0.6987493910311149,-0.36334861819110453,-0.33540077284001035,1.0,145,False
fes_string_conditioned,z_reward,A_to_C_to_B,tfc_removed_o1o2,-0.6987493910311149,-0.3737797278357056,-0.32496966319540926,1.0,145,False
fes_string_conditioned,z_reward,A_to_C_to_B,side_shuffled_o1o2,-0.6987493910311149,-0.7109545454720411,0.012205154440926316,0.3223355328934213,145,False
fes_string_conditioned,z_reward,A_to_C_to_B,memory_only_o1o2,-0.6987493910311149,-0.7365447366432295,0.037795345612114714,0.05398920215956809,145,False
fes_string_conditioned,z_reward,A_to_C_to_B,residual_endpoint_o1o2,-0.6987493910311149,-0.36505550918863133,-0.33369388184248355,1.0,145,False
fes_string_conditioned,z_reward,B_to_C_to_A,o1_lag0_only,-0.6878924566826311,-0.4939982759969987,-0.19389418068563244,1.0,145,False
fes_string_conditioned,z_reward,B_to_C_to_A,o2_lag5_only,-0.6878924566826311,-0.4758223162294845,-0.21207014045314654,1.0,145,False
fes_string_conditioned,z_reward,B_to_C_to_A,o1_o2_joint,-0.6878924566826311,-0.36334861819110453,-0.32454383849152657,1.0,145,False
fes_string_conditioned,z_reward,B_to_C_to_A,phase_removed_o1o2,-0.6878924566826311,-0.36334861819110453,-0.32454383849152657,1.0,145,False
fes_string_conditioned,z_reward,B_to_C_to_A,tfc_removed_o1o2,-0.6878924566826311,-0.3737797278357056,-0.31411272884692554,1.0,145,False
fes_string_conditioned,z_reward,B_to_C_to_A,side_shuffled_o1o2,-0.6878924566826311,-0.7109545454720411,0.02306208878941007,0.1803639272145571,145,False
fes_string_conditioned,z_reward,B_to_C_to_A,memory_only_o1o2,-0.6878924566826311,-0.7365447366432295,0.04865227996059845,0.03579284143171366,145,True
fes_string_conditioned,z_reward,B_to_C_to_A,residual_endpoint_o1o2,-0.6878924566826311,-0.36505550918863133,-0.32283694749399977,1.0,145,False
fes_string_conditioned,rank_reward,A_to_C_to_B,o1_lag0_only,-0.657570387593165,-0.4629835961544362,-0.19458679143872887,1.0,145,False
fes_string_conditioned,rank_reward,A_to_C_to_B,o2_lag5_only,-0.657570387593165,-0.4278118296561423,-0.22975855793702274,1.0,145,False
fes_string_conditioned,rank_reward,A_to_C_to_B,o1_o2_joint,-0.657570387593165,-0.3007770003191647,-0.3567933872740003,1.0,145,False
fes_string_conditioned,rank_reward,A_to_C_to_B,phase_removed_o1o2,-0.657570387593165,-0.3007770003191647,-0.3567933872740003,1.0,145,False
fes_string_conditioned,rank_reward,A_to_C_to_B,tfc_removed_o1o2,-0.657570387593165,-0.32166758018319586,-0.3359028074099691,1.0,145,False
fes_string_conditioned,rank_reward,A_to_C_to_B,side_shuffled_o1o2,-0.657570387593165,-0.6871276490093796,0.029557261416214675,0.11977604479104179,145,False
fes_string_conditioned,rank_reward,A_to_C_to_B,memory_only_o1o2,-0.657570387593165,-0.7078748720484688,0.050304484455303805,0.020395920815836834,145,True
fes_string_conditioned,rank_reward,A_to_C_to_B,residual_endpoint_o1o2,-0.657570387593165,-0.30779882856148716,-0.34977155903167784,1.0,145,False
fes_string_conditioned,rank_reward,B_to_C_to_A,o1_lag0_only,-0.6488932104865325,-0.4629835961544362,-0.18590961433209632,1.0,145,False
fes_string_conditioned,rank_reward,B_to_C_to_A,o2_lag5_only,-0.6488932104865325,-0.4278118296561423,-0.2210813808303902,1.0,145,False
fes_string_conditioned,rank_reward,B_to_C_to_A,o1_o2_joint,-0.6488932104865325,-0.3007770003191647,-0.3481162101673678,1.0,145,False
fes_string_conditioned,rank_reward,B_to_C_to_A,phase_removed_o1o2,-0.6488932104865325,-0.3007770003191647,-0.3481162101673678,1.0,145,False
fes_string_conditioned,rank_reward,B_to_C_to_A,tfc_removed_o1o2,-0.6488932104865325,-0.32166758018319586,-0.3272256303033366,1.0,145,False
fes_string_conditioned,rank_reward,B_to_C_to_A,side_shuffled_o1o2,-0.6488932104865325,-0.6871276490093796,0.0382344385228472,0.07138572285542892,145,False
fes_string_conditioned,rank_reward,B_to_C_to_A,memory_only_o1o2,-0.6488932104865325,-0.7078748720484688,0.05898166156193632,0.005598880223955209,145,True
fes_string_conditioned,rank_reward,B_to_C_to_A,residual_endpoint_o1o2,-0.6488932104865325,-0.30779882856148716,-0.34109438192504526,1.0,145,False
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,o1_lag0_only,-0.2809320730862229,-0.26581740513241725,-0.01511466795380562,0.935612877424515,145,False
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,o2_lag5_only,-0.2809320730862229,-0.2617038415029886,-0.019228231583234362,0.9646070785842832,145,False
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,o1_o2_joint,-0.2809320730862229,-0.23770635075286214,-0.043225722333360764,1.0,145,False
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,phase_removed_o1o2,-0.2809320730862229,-0.23770635075286214,-0.043225722333360764,1.0,145,False
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,tfc_removed_o1o2,-0.2809320730862229,-0.24333188875911443,-0.0376001843271085,1.0,145,False
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,side_shuffled_o1o2,-0.2809320730862229,-0.29615303429651674,0.015220961210293819,0.0621875624875025,145,False
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,memory_only_o1o2,-0.2809320730862229,-0.3000478098148858,0.01911573672866291,0.026794641071785644,145,True
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,residual_endpoint_o1o2,-0.2809320730862229,-0.23913308111929277,-0.04179899196693016,1.0,145,False
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,o1_lag0_only,-0.2781034299650956,-0.26581740513241725,-0.01228602483267831,0.9022195560887822,145,False
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,o2_lag5_only,-0.2781034299650956,-0.2617038415029886,-0.016399588462107054,0.9398120375924816,145,False
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,o1_o2_joint,-0.2781034299650956,-0.23770635075286214,-0.040397079212233455,1.0,145,False
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,phase_removed_o1o2,-0.2781034299650956,-0.23770635075286214,-0.040397079212233455,1.0,145,False
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,tfc_removed_o1o2,-0.2781034299650956,-0.24333188875911443,-0.034771541205981187,0.9992001599680064,145,False
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,side_shuffled_o1o2,-0.2781034299650956,-0.29615303429651674,0.01804960433142113,0.03719256148770246,145,True
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,memory_only_o1o2,-0.2781034299650956,-0.3000478098148858,0.02194437984979022,0.020995800839832032,145,True
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,residual_endpoint_o1o2,-0.2781034299650956,-0.23913308111929277,-0.03897034884580284,1.0,145,False
combined_c_fes_gmr72,z_reward,A_to_C_to_B,o1_lag0_only,-0.6955771814545567,-0.4939982759969987,-0.20157890545755805,1.0,145,False
combined_c_fes_gmr72,z_reward,A_to_C_to_B,o2_lag5_only,-0.6955771814545567,-0.4758223162294845,-0.21975486522507218,1.0,145,False
combined_c_fes_gmr72,z_reward,A_to_C_to_B,o1_o2_joint,-0.6955771814545567,-0.36334861819110453,-0.33222856326345224,1.0,145,False
combined_c_fes_gmr72,z_reward,A_to_C_to_B,phase_removed_o1o2,-0.6955771814545567,-0.36334861819110453,-0.33222856326345224,1.0,145,False
combined_c_fes_gmr72,z_reward,A_to_C_to_B,tfc_removed_o1o2,-0.6955771814545567,-0.3737797278357056,-0.32179745361885115,1.0,145,False
combined_c_fes_gmr72,z_reward,A_to_C_to_B,side_shuffled_o1o2,-0.6955771814545567,-0.7109545454720411,0.015377364017484414,0.2959408118376325,145,False
combined_c_fes_gmr72,z_reward,A_to_C_to_B,memory_only_o1o2,-0.6955771814545567,-0.7365447366432295,0.040967555188672795,0.07858428314337132,145,False
combined_c_fes_gmr72,z_reward,A_to_C_to_B,residual_endpoint_o1o2,-0.6955771814545567,-0.36505550918863133,-0.3305216722659254,1.0,145,False
combined_c_fes_gmr72,z_reward,B_to_C_to_A,o1_lag0_only,-0.7054201502399922,-0.4939982759969987,-0.21142187424299344,1.0,145,False
combined_c_fes_gmr72,z_reward,B_to_C_to_A,o2_lag5_only,-0.7054201502399922,-0.4758223162294845,-0.22959783401050757,1.0,145,False
combined_c_fes_gmr72,z_reward,B_to_C_to_A,o1_o2_joint,-0.7054201502399922,-0.36334861819110453,-0.34207153204888757,1.0,145,False
combined_c_fes_gmr72,z_reward,B_to_C_to_A,phase_removed_o1o2,-0.7054201502399922,-0.36334861819110453,-0.34207153204888757,1.0,145,False
combined_c_fes_gmr72,z_reward,B_to_C_to_A,tfc_removed_o1o2,-0.7054201502399922,-0.3737797278357056,-0.33164042240428643,1.0,145,False
combined_c_fes_gmr72,z_reward,B_to_C_to_A,side_shuffled_o1o2,-0.7054201502399922,-0.7109545454720411,0.005534395232049061,0.4039192161567686,145,False
combined_c_fes_gmr72,z_reward,B_to_C_to_A,memory_only_o1o2,-0.7054201502399922,-0.7365447366432295,0.031124586403237463,0.10497900419916016,145,False
combined_c_fes_gmr72,z_reward,B_to_C_to_A,residual_endpoint_o1o2,-0.7054201502399922,-0.36505550918863133,-0.3403646410513608,1.0,145,False
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,o1_lag0_only,-0.6582170980464946,-0.4629835961544362,-0.1952335018920586,1.0,145,False
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,o2_lag5_only,-0.6582170980464946,-0.4278118296561423,-0.2304052683903525,1.0,145,False
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,o1_o2_joint,-0.6582170980464946,-0.3007770003191647,-0.35744009772733004,1.0,145,False
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,phase_removed_o1o2,-0.6582170980464946,-0.3007770003191647,-0.35744009772733004,1.0,145,False
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,tfc_removed_o1o2,-0.6582170980464946,-0.32166758018319586,-0.3365495178632989,1.0,145,False
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,side_shuffled_o1o2,-0.6582170980464946,-0.6871276490093796,0.028910550962884942,0.17336532693461307,145,False
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,memory_only_o1o2,-0.6582170980464946,-0.7078748720484688,0.04965777400197407,0.04839032193561288,145,True
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,residual_endpoint_o1o2,-0.6582170980464946,-0.30779882856148716,-0.35041826948500754,1.0,145,False
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,o1_lag0_only,-0.6677488350563425,-0.4629835961544362,-0.2047652389019064,1.0,145,False
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,o2_lag5_only,-0.6677488350563425,-0.4278118296561423,-0.23993700540020024,1.0,145,False
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,o1_o2_joint,-0.6677488350563425,-0.3007770003191647,-0.3669718347371778,1.0,145,False
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,phase_removed_o1o2,-0.6677488350563425,-0.3007770003191647,-0.3669718347371778,1.0,145,False
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,tfc_removed_o1o2,-0.6677488350563425,-0.32166758018319586,-0.3460812548731467,1.0,145,False
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,side_shuffled_o1o2,-0.6677488350563425,-0.6871276490093796,0.019378813953037147,0.21855628874225155,145,False
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,memory_only_o1o2,-0.6677488350563425,-0.7078748720484688,0.04012603699212628,0.04839032193561288,145,True
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,residual_endpoint_o1o2,-0.6677488350563425,-0.30779882856148716,-0.35995000649485537,1.0,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,o1_lag0_only,-0.2853969711692958,-0.26581740513241725,-0.01957956603687851,0.9604079184163168,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,o2_lag5_only,-0.2853969711692958,-0.2617038415029886,-0.023693129666307256,0.9828034393121375,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,o1_o2_joint,-0.2853969711692958,-0.23770635075286214,-0.047690620416433654,1.0,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,phase_removed_o1o2,-0.2853969711692958,-0.23770635075286214,-0.047690620416433654,1.0,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,tfc_removed_o1o2,-0.2853969711692958,-0.24333188875911443,-0.0420650824101814,1.0,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,side_shuffled_o1o2,-0.2853969711692958,-0.29615303429651674,0.010756063127220923,0.15776844631073786,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,memory_only_o1o2,-0.2853969711692958,-0.3000478098148858,0.014650838645590015,0.08918216356728655,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,residual_endpoint_o1o2,-0.2853969711692958,-0.23913308111929277,-0.04626389005000305,1.0,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,o1_lag0_only,-0.28663044908257795,-0.26581740513241725,-0.020813043950160634,0.9708058388322336,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,o2_lag5_only,-0.28663044908257795,-0.2617038415029886,-0.02492660757958937,0.9850029994001199,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,o1_o2_joint,-0.28663044908257795,-0.23770635075286214,-0.04892409832971578,1.0,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,phase_removed_o1o2,-0.28663044908257795,-0.23770635075286214,-0.04892409832971578,1.0,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,tfc_removed_o1o2,-0.28663044908257795,-0.24333188875911443,-0.04329856032346352,0.9998000399920016,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,side_shuffled_o1o2,-0.28663044908257795,-0.29615303429651674,0.009522585213938804,0.19696060787842432,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,memory_only_o1o2,-0.28663044908257795,-0.3000478098148858,0.013417360732307896,0.130373925214957,145,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,residual_endpoint_o1o2,-0.28663044908257795,-0.23913308111929277,-0.04749736796328517,1.0,145,False

## Interpretation Rule

B7.2a does not use C12 as a rescue module. If O1/O2 strength drops after phase, TFC, or side/direction removal, the B6 structure may be compressed into the endpoint-adjacent proxy rather than absent from the system.

## Settings

- n_folds: 5
- min_state_events: 8
- temperature: 0.35
- n_perm: 5000
- alpha: 0.05
- seed: 71110
