# Private B6V Access Without C Audit

Status: local/private screen only. No publication, commit, stage, or push was performed.

Question: Does A<->B access without C reproduce intersection access?

Boundary: C is fixed and not redefined. The no-C arm removes C-state conditioning and restricts the access readout to direct AB primitives.

## Main Findings

- C-necessary pattern conditions: 15 / 24
- with-C intersection survival conditions: 15 / 24
- no-C direct failure conditions: 24 / 24

## C vs No-C Contrast

mode,endpoint,path,direction_with_c,arm_type_with_c,pass_count_with_c,core_pass_count_with_c,survives_with_c,fails_with_c,mean_effect_with_c,mean_core_effect_with_c,mean_true_access_effect_with_c,direction_no_c,arm_type_no_c,pass_count_no_c,core_pass_count_no_c,survives_no_c,fails_no_c,mean_effect_no_c,mean_core_effect_no_c,mean_true_access_effect_no_c,c_necessary_pattern,access_effect_gap_with_c_minus_no_c
linear_c_state,rank_reward,B_path,B_to_C_to_A,with_c_intersection,5,3,True,False,0.06808909520533474,0.05684747450858809,-0.6594298734361925,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.003984507592199715,-0.0013154531714615711,-0.7243245405813526,True,0.05816292768004966
gmr72_phase_conditioned,rank_reward,B_path,B_to_C_to_A,with_c_intersection,5,3,True,False,0.06499035767755325,0.053579954262603514,-0.6622754368866695,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.003984507592199715,-0.0013154531714615711,-0.7243245405813526,True,0.05489540743406508
linear_c_state,rank_reward,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.06343311848619923,0.052551579217571774,-0.6645096745245741,A_to_B_no_C,no_c_direct_ab,1,0,False,True,-3.827124193004593e-05,-0.0013154531714615711,-0.7243245405813526,True,0.05386703238903334
gmr72_phase_conditioned,rank_reward,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.06218150956089621,0.050603465903830504,-0.6647165268672198,A_to_B_no_C,no_c_direct_ab,1,0,False,True,-3.827124193004593e-05,-0.0013154531714615711,-0.7243245405813526,True,0.05191891907529207
linear_c_state,z_reward,B_path,B_to_C_to_A,with_c_intersection,5,3,True,False,0.06089694201119731,0.048047379926954605,-0.6667860859214115,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.003968622950746404,-0.0013059481053828215,-0.7290410663847228,True,0.049353328032337426
gmr72_phase_conditioned,z_reward,B_path,B_to_C_to_A,with_c_intersection,5,3,True,False,0.0573503200214344,0.044432703695098684,-0.6702306265480349,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.003968622950746404,-0.0013059481053828215,-0.7290410663847228,True,0.045738651800481506
combined_c_fes_gmr72,rank_reward,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.04547100824986631,0.04274388529251002,-0.6821306903104767,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0037031103857541347,-0.0013154531714615711,-0.7243245405813526,True,0.04405933846397159
combined_c_fes_gmr72,rank_reward,B_path,B_to_C_to_A,with_c_intersection,4,3,True,False,0.03774646762470833,0.04013912709523574,-0.6894363253276026,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.0042734686726179786,-0.0013154531714615711,-0.7243245405813526,True,0.04145458026669731
linear_c_state,z_reward,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.05201315725762075,0.038585722896762535,-0.6758495687440289,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.001639164059824454,-0.0013059481053828215,-0.7290410663847228,True,0.03989167100214536
gmr72_phase_conditioned,z_reward,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.0509744458540598,0.03663690430623879,-0.6755231193671457,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.001639164059824454,-0.0013059481053828215,-0.7290410663847228,True,0.03794285241162161
combined_c_fes_gmr72,z_reward,A_path,A_to_C_to_B,with_c_intersection,4,3,True,False,0.03407220078998384,0.027571517265327816,-0.6927858882126665,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0034825897021147274,-0.0013059481053828215,-0.7290410663847228,True,0.028877465370710637
linear_c_state,gmr72_bridge_composite,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.009059501126938152,0.0073625250212171174,-0.26991542250984546,A_to_B_no_C,no_c_direct_ab,0,0,False,True,0.0005793757554984486,-0.000176026698372063,-0.2851699656780228,True,0.007538551719589181
gmr72_phase_conditioned,gmr72_bridge_composite,A_path,A_to_C_to_B,with_c_intersection,5,3,True,False,0.008240703701693542,0.0065138087823600746,-0.2706893417146714,A_to_B_no_C,no_c_direct_ab,0,0,False,True,0.0005793757554984486,-0.000176026698372063,-0.2851699656780228,True,0.006689835480732138
linear_c_state,gmr72_bridge_composite,B_path,B_to_C_to_A,with_c_intersection,5,3,True,False,0.008513461477880882,0.006244915836255072,-0.27062265151803716,B_to_A_no_C,no_c_direct_ab,0,0,False,True,0.0022352058398368998,-0.000176026698372063,-0.2851699656780228,True,0.006420942534627135
gmr72_phase_conditioned,gmr72_bridge_composite,B_path,B_to_C_to_A,with_c_intersection,5,3,True,False,0.007063480485965917,0.004928310012740001,-0.272272695262552,B_to_A_no_C,no_c_direct_ab,0,0,False,True,0.0022352058398368998,-0.000176026698372063,-0.2851699656780228,True,0.005104336711112064
combined_c_fes_gmr72,z_reward,B_path,B_to_C_to_A,with_c_intersection,3,2,False,False,0.024913842657591657,0.026381001890522487,-0.7004897945439573,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.004360448840639584,-0.0013059481053828215,-0.7290410663847228,False,0.02768694999590531
fes_string_conditioned,rank_reward,B_path,B_to_C_to_A,with_c_intersection,2,0,False,True,0.020054320890887913,0.00930660216619073,-0.709300211120681,B_to_A_no_C,no_c_direct_ab,1,0,False,True,-0.0019183127475109491,-0.0013154531714615711,-0.7243245405813526,False,0.010622055337652302
fes_string_conditioned,rank_reward,A_path,A_to_C_to_B,with_c_intersection,1,0,False,True,0.011925034674714882,0.006444056070190072,-0.7072866127129764,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0016450489544063223,-0.0013154531714615711,-0.7243245405813526,False,0.007759509241651643
combined_c_fes_gmr72,gmr72_bridge_composite,A_path,A_to_C_to_B,with_c_intersection,1,1,False,True,0.006586051209596769,0.006702648715476396,-0.27321696314695076,A_to_B_no_C,no_c_direct_ab,0,0,False,True,0.0017840799156287734,-0.000176026698372063,-0.2851699656780228,False,0.00687867541384846
combined_c_fes_gmr72,gmr72_bridge_composite,B_path,B_to_C_to_A,with_c_intersection,0,0,False,True,0.0004483495748428337,0.002523582781399339,-0.27835514177697535,B_to_A_no_C,no_c_direct_ab,0,0,False,True,0.0018078498206432851,-0.000176026698372063,-0.2851699656780228,False,0.002699609479771402
fes_string_conditioned,z_reward,B_path,B_to_C_to_A,with_c_intersection,2,0,False,True,0.01590173928536521,0.0011131367027420042,-0.717073226283539,B_to_A_no_C,no_c_direct_ab,1,0,False,True,-0.0012916192397700779,-0.0013059481053828215,-0.7290410663847228,False,0.002419084808124826
fes_string_conditioned,gmr72_bridge_composite,A_path,A_to_C_to_B,with_c_intersection,2,2,False,False,0.0027858095800802757,0.0021424989485898625,-0.2745255543030141,A_to_B_no_C,no_c_direct_ab,0,0,False,True,0.0002454779988263815,-0.000176026698372063,-0.2851699656780228,False,0.0023185256469619255
fes_string_conditioned,gmr72_bridge_composite,B_path,B_to_C_to_A,with_c_intersection,2,1,False,True,0.004585315951213234,0.0021289644655387383,-0.275393758967806,B_to_A_no_C,no_c_direct_ab,0,0,False,True,0.0006298669868323913,-0.000176026698372063,-0.2851699656780228,False,0.0023049911639108013
fes_string_conditioned,z_reward,A_path,A_to_C_to_B,with_c_intersection,1,0,False,True,0.006459157367199114,-0.0019945573013720208,-0.7160957188629731,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0014592501016784602,-0.0013059481053828215,-0.7290410663847228,False,-0.0006886091959891992

## With-C Intersection Summary

mode,endpoint,direction,arm_type,pass_count,core_pass_count,survives,fails,mean_effect,mean_core_effect,mean_true_access_effect
combined_c_fes_gmr72,z_reward,A_to_C_to_B,with_c_intersection,4,3,True,False,0.03407220078998384,0.027571517265327816,-0.6927858882126665
combined_c_fes_gmr72,z_reward,B_to_C_to_A,with_c_intersection,3,2,False,False,0.024913842657591657,0.026381001890522487,-0.7004897945439573
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,with_c_intersection,5,3,True,False,0.04547100824986631,0.04274388529251002,-0.6821306903104767
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,with_c_intersection,4,3,True,False,0.03774646762470833,0.04013912709523574,-0.6894363253276026
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,with_c_intersection,1,1,False,True,0.006586051209596769,0.006702648715476396,-0.27321696314695076
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,with_c_intersection,0,0,False,True,0.0004483495748428337,0.002523582781399339,-0.27835514177697535
gmr72_phase_conditioned,z_reward,A_to_C_to_B,with_c_intersection,5,3,True,False,0.0509744458540598,0.03663690430623879,-0.6755231193671457
gmr72_phase_conditioned,z_reward,B_to_C_to_A,with_c_intersection,5,3,True,False,0.0573503200214344,0.044432703695098684,-0.6702306265480349
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,with_c_intersection,5,3,True,False,0.06218150956089621,0.050603465903830504,-0.6647165268672198
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,with_c_intersection,5,3,True,False,0.06499035767755325,0.053579954262603514,-0.6622754368866695
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,with_c_intersection,5,3,True,False,0.008240703701693542,0.0065138087823600746,-0.2706893417146714
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,with_c_intersection,5,3,True,False,0.007063480485965917,0.004928310012740001,-0.272272695262552
fes_string_conditioned,z_reward,A_to_C_to_B,with_c_intersection,1,0,False,True,0.006459157367199114,-0.0019945573013720208,-0.7160957188629731
fes_string_conditioned,z_reward,B_to_C_to_A,with_c_intersection,2,0,False,True,0.01590173928536521,0.0011131367027420042,-0.717073226283539
fes_string_conditioned,rank_reward,A_to_C_to_B,with_c_intersection,1,0,False,True,0.011925034674714882,0.006444056070190072,-0.7072866127129764
fes_string_conditioned,rank_reward,B_to_C_to_A,with_c_intersection,2,0,False,True,0.020054320890887913,0.00930660216619073,-0.709300211120681
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,with_c_intersection,2,2,False,False,0.0027858095800802757,0.0021424989485898625,-0.2745255543030141
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,with_c_intersection,2,1,False,True,0.004585315951213234,0.0021289644655387383,-0.275393758967806
linear_c_state,z_reward,A_to_C_to_B,with_c_intersection,5,3,True,False,0.05201315725762075,0.038585722896762535,-0.6758495687440289
linear_c_state,z_reward,B_to_C_to_A,with_c_intersection,5,3,True,False,0.06089694201119731,0.048047379926954605,-0.6667860859214115
linear_c_state,rank_reward,A_to_C_to_B,with_c_intersection,5,3,True,False,0.06343311848619923,0.052551579217571774,-0.6645096745245741
linear_c_state,rank_reward,B_to_C_to_A,with_c_intersection,5,3,True,False,0.06808909520533474,0.05684747450858809,-0.6594298734361925
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,with_c_intersection,5,3,True,False,0.009059501126938152,0.0073625250212171174,-0.26991542250984546
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,with_c_intersection,5,3,True,False,0.008513461477880882,0.006244915836255072,-0.27062265151803716

## No-C Direct AB Summary

mode,endpoint,direction,arm_type,pass_count,core_pass_count,survives,fails,mean_effect,mean_core_effect,mean_true_access_effect
combined_c_fes_gmr72,z_reward,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0034825897021147274,-0.0013059481053828215,-0.7290410663847228
combined_c_fes_gmr72,z_reward,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.004360448840639584,-0.0013059481053828215,-0.7290410663847228
combined_c_fes_gmr72,rank_reward,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0037031103857541347,-0.0013154531714615711,-0.7243245405813526
combined_c_fes_gmr72,rank_reward,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.0042734686726179786,-0.0013154531714615711,-0.7243245405813526
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_B_no_C,no_c_direct_ab,0,0,False,True,0.0017840799156287734,-0.000176026698372063,-0.2851699656780228
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_A_no_C,no_c_direct_ab,0,0,False,True,0.0018078498206432851,-0.000176026698372063,-0.2851699656780228
gmr72_phase_conditioned,z_reward,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.001639164059824454,-0.0013059481053828215,-0.7290410663847228
gmr72_phase_conditioned,z_reward,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.003968622950746404,-0.0013059481053828215,-0.7290410663847228
gmr72_phase_conditioned,rank_reward,A_to_B_no_C,no_c_direct_ab,1,0,False,True,-3.827124193004593e-05,-0.0013154531714615711,-0.7243245405813526
gmr72_phase_conditioned,rank_reward,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.003984507592199715,-0.0013154531714615711,-0.7243245405813526
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_B_no_C,no_c_direct_ab,0,0,False,True,0.0005793757554984486,-0.000176026698372063,-0.2851699656780228
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_A_no_C,no_c_direct_ab,0,0,False,True,0.0022352058398368998,-0.000176026698372063,-0.2851699656780228
fes_string_conditioned,z_reward,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0014592501016784602,-0.0013059481053828215,-0.7290410663847228
fes_string_conditioned,z_reward,B_to_A_no_C,no_c_direct_ab,1,0,False,True,-0.0012916192397700779,-0.0013059481053828215,-0.7290410663847228
fes_string_conditioned,rank_reward,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.0016450489544063223,-0.0013154531714615711,-0.7243245405813526
fes_string_conditioned,rank_reward,B_to_A_no_C,no_c_direct_ab,1,0,False,True,-0.0019183127475109491,-0.0013154531714615711,-0.7243245405813526
fes_string_conditioned,gmr72_bridge_composite,A_to_B_no_C,no_c_direct_ab,0,0,False,True,0.0002454779988263815,-0.000176026698372063,-0.2851699656780228
fes_string_conditioned,gmr72_bridge_composite,B_to_A_no_C,no_c_direct_ab,0,0,False,True,0.0006298669868323913,-0.000176026698372063,-0.2851699656780228
linear_c_state,z_reward,A_to_B_no_C,no_c_direct_ab,1,0,False,True,0.001639164059824454,-0.0013059481053828215,-0.7290410663847228
linear_c_state,z_reward,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.003968622950746404,-0.0013059481053828215,-0.7290410663847228
linear_c_state,rank_reward,A_to_B_no_C,no_c_direct_ab,1,0,False,True,-3.827124193004593e-05,-0.0013154531714615711,-0.7243245405813526
linear_c_state,rank_reward,B_to_A_no_C,no_c_direct_ab,1,0,False,True,0.003984507592199715,-0.0013154531714615711,-0.7243245405813526
linear_c_state,gmr72_bridge_composite,A_to_B_no_C,no_c_direct_ab,0,0,False,True,0.0005793757554984486,-0.000176026698372063,-0.2851699656780228
linear_c_state,gmr72_bridge_composite,B_to_A_no_C,no_c_direct_ab,0,0,False,True,0.0022352058398368998,-0.000176026698372063,-0.2851699656780228

## With-C Control Comparisons

mode,endpoint,direction,comparison,control_kind,mean_true,mean_control,effect,p_greater,n_pairs,passes
combined_c_fes_gmr72,z_reward,A_to_C_to_B,true_vs_random,random,-0.6927858882126665,-0.7185301738861943,0.02574428567352786,0.08398320335932813,502,False
combined_c_fes_gmr72,z_reward,A_to_C_to_B,true_vs_balanced,balanced,-0.6927858882126665,-0.7140804129272932,0.021294524714626624,0.04239152169566087,502,True
combined_c_fes_gmr72,z_reward,A_to_C_to_B,true_vs_performance_matched,performance_matched,-0.6927858882126665,-0.7546880546930745,0.06190216648040788,0.0001999600079984003,502,True
combined_c_fes_gmr72,z_reward,A_to_C_to_B,true_vs_shuffled_c,shuffled_c,-0.6927858882126665,-0.7272563105846676,0.034470422372001035,0.022195560887822437,502,True
combined_c_fes_gmr72,z_reward,A_to_C_to_B,true_vs_phase_rotated,phase_rotated,-0.6927858882126665,-0.7197354929220224,0.02694960470935579,0.028394321135772844,502,True
combined_c_fes_gmr72,z_reward,B_to_C_to_A,true_vs_random,random,-0.7004897945439573,-0.6896845008324222,-0.010805293711535314,0.7148570285942811,502,False
combined_c_fes_gmr72,z_reward,B_to_C_to_A,true_vs_balanced,balanced,-0.7004897945439573,-0.7179173728310504,0.017427578287093,0.0613877224555089,502,False
combined_c_fes_gmr72,z_reward,B_to_C_to_A,true_vs_performance_matched,performance_matched,-0.7004897945439573,-0.7567212958718835,0.05623150132792613,0.0001999600079984003,502,True
combined_c_fes_gmr72,z_reward,B_to_C_to_A,true_vs_shuffled_c,shuffled_c,-0.7004897945439573,-0.7349495901554239,0.034459795611466615,0.017996400719856028,502,True
combined_c_fes_gmr72,z_reward,B_to_C_to_A,true_vs_phase_rotated,phase_rotated,-0.7004897945439573,-0.7277454263169653,0.027255631773007848,0.02399520095980804,502,True
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,true_vs_random,random,-0.6821306903104767,-0.7187805358486302,0.03664984553815358,0.027394521095780843,502,True
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,true_vs_balanced,balanced,-0.6821306903104767,-0.7143325140564794,0.032201823746002604,0.005398920215956809,502,True
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,true_vs_performance_matched,performance_matched,-0.6821306903104767,-0.7446042301441247,0.062473539833647916,0.0001999600079984003,502,True
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,true_vs_shuffled_c,shuffled_c,-0.6821306903104767,-0.7344538484874517,0.052323158176974964,0.0011997600479904018,502,True
combined_c_fes_gmr72,rank_reward,A_to_C_to_B,true_vs_phase_rotated,phase_rotated,-0.6821306903104767,-0.7258373642650291,0.04370667395455247,0.004199160167966407,502,True
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,true_vs_random,random,-0.6894363253276026,-0.6969841032943356,0.0075477779667330195,0.34513097380523894,502,False
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,true_vs_balanced,balanced,-0.6894363253276026,-0.717347918867321,0.027911593539718397,0.0061987602479504095,502,True
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,true_vs_performance_matched,performance_matched,-0.6894363253276026,-0.750203504198704,0.06076717887110144,0.0001999600079984003,502,True
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,true_vs_shuffled_c,shuffled_c,-0.6894363253276026,-0.7419233812960075,0.052487055968405034,0.0007998400319936012,502,True
combined_c_fes_gmr72,rank_reward,B_to_C_to_A,true_vs_phase_rotated,phase_rotated,-0.6894363253276026,-0.7294550571051862,0.04001873177758379,0.004599080183963208,502,True
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,true_vs_random,random,-0.27321696314695076,-0.2808437819442903,0.007626818797339566,0.1357728454309138,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,true_vs_balanced,balanced,-0.27321696314695076,-0.27687332890592253,0.0036563657589717756,0.1877624475104979,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,true_vs_performance_matched,performance_matched,-0.27321696314695076,-0.27841245425116584,0.005195491104215085,0.15476904619076184,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,true_vs_shuffled_c,shuffled_c,-0.27321696314695076,-0.27979844578580293,0.006581482638852119,0.15156968606278745,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_C_to_B,true_vs_phase_rotated,phase_rotated,-0.27321696314695076,-0.28308706089555613,0.009870097748605295,0.021795640871825634,502,True
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,true_vs_random,random,-0.27835514177697535,-0.27096263867595216,-0.007392503101023115,0.853629274145171,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,true_vs_balanced,balanced,-0.27835514177697535,-0.2773493154866781,-0.0010058262902971577,0.6246750649870026,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,true_vs_performance_matched,performance_matched,-0.27835514177697535,-0.2804186444080146,0.002063502631039268,0.3245350929814037,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,true_vs_shuffled_c,shuffled_c,-0.27835514177697535,-0.2797256239446535,0.0013704821676781718,0.393121375724855,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_C_to_A,true_vs_phase_rotated,phase_rotated,-0.27835514177697535,-0.2855612342437923,0.007206092466817002,0.08438312337532493,502,False
gmr72_phase_conditioned,z_reward,A_to_C_to_B,true_vs_random,random,-0.6755231193671457,-0.7413197003927994,0.06579658102565374,0.0003999200159968006,502,True
gmr72_phase_conditioned,z_reward,A_to_C_to_B,true_vs_balanced,balanced,-0.6755231193671457,-0.7140804129272932,0.038557293560147594,0.0001999600079984003,502,True
gmr72_phase_conditioned,z_reward,A_to_C_to_B,true_vs_performance_matched,performance_matched,-0.6755231193671457,-0.7546880546930745,0.07916493532592886,0.0001999600079984003,502,True
gmr72_phase_conditioned,z_reward,A_to_C_to_B,true_vs_shuffled_c,shuffled_c,-0.6755231193671457,-0.7067257057337186,0.031202586366573103,0.008598280343931213,502,True
gmr72_phase_conditioned,z_reward,A_to_C_to_B,true_vs_phase_rotated,phase_rotated,-0.6755231193671457,-0.7156739523591412,0.040150832991995684,0.002999400119976005,502,True
gmr72_phase_conditioned,z_reward,B_to_C_to_A,true_vs_random,random,-0.6702306265480349,-0.7371934462460621,0.06696281969802731,0.0005998800239952009,502,True
gmr72_phase_conditioned,z_reward,B_to_C_to_A,true_vs_balanced,balanced,-0.6702306265480349,-0.7179173728310504,0.04768674628301548,0.0001999600079984003,502,True
gmr72_phase_conditioned,z_reward,B_to_C_to_A,true_vs_performance_matched,performance_matched,-0.6702306265480349,-0.7567212958718835,0.08649066932384862,0.0001999600079984003,502,True
gmr72_phase_conditioned,z_reward,B_to_C_to_A,true_vs_shuffled_c,shuffled_c,-0.6702306265480349,-0.7126626422605591,0.04243201571252417,0.003999200159968006,502,True
gmr72_phase_conditioned,z_reward,B_to_C_to_A,true_vs_phase_rotated,phase_rotated,-0.6702306265480349,-0.7134099756377913,0.04317934908975641,0.0007998400319936012,502,True
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,true_vs_random,random,-0.6647165268672198,-0.7439259736833045,0.07920944681608467,0.0001999600079984003,502,True
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,true_vs_balanced,balanced,-0.6647165268672198,-0.7143325140564794,0.0496159871892595,0.0001999600079984003,502,True
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,true_vs_performance_matched,performance_matched,-0.6647165268672198,-0.7446042301441247,0.0798877032769048,0.0001999600079984003,502,True
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,true_vs_shuffled_c,shuffled_c,-0.6647165268672198,-0.7101571283806222,0.04544060151340234,0.0011997600479904018,502,True
gmr72_phase_conditioned,rank_reward,A_to_C_to_B,true_vs_phase_rotated,phase_rotated,-0.6647165268672198,-0.7214703358760495,0.05675380900882969,0.0003999200159968006,502,True
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,true_vs_random,random,-0.6622754368866695,-0.7385592951745907,0.07628385828792118,0.0001999600079984003,502,True
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,true_vs_balanced,balanced,-0.6622754368866695,-0.717347918867321,0.055072481980651435,0.0001999600079984003,502,True
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,true_vs_performance_matched,performance_matched,-0.6622754368866695,-0.750203504198704,0.08792806731203447,0.0001999600079984003,502,True
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,true_vs_shuffled_c,shuffled_c,-0.6622754368866695,-0.7177462592227166,0.055470822336047027,0.0003999200159968006,502,True
gmr72_phase_conditioned,rank_reward,B_to_C_to_A,true_vs_phase_rotated,phase_rotated,-0.6622754368866695,-0.7124719953577816,0.050196558471112096,0.0005998800239952009,502,True
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_vs_random,random,-0.2706893417146714,-0.28462832133956445,0.013938979624893032,0.010397920415916816,502,True
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_vs_balanced,balanced,-0.2706893417146714,-0.27687332890592253,0.006183987191251144,0.001999600079984003,502,True
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_vs_performance_matched,performance_matched,-0.2706893417146714,-0.27841245425116584,0.007723112536494452,0.014197160567886422,502,True
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_vs_shuffled_c,shuffled_c,-0.2706893417146714,-0.2761175584648116,0.005428216750140173,0.008998200359928014,502,True
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_vs_phase_rotated,phase_rotated,-0.2706893417146714,-0.2786185641203604,0.007929222405688906,0.004199160167966407,502,True
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_vs_random,random,-0.272272695262552,-0.284659218508699,0.012386523246147004,0.028394321135772844,502,True
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_vs_balanced,balanced,-0.272272695262552,-0.2773493154866781,0.005076620224126158,0.005398920215956809,502,True
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_vs_performance_matched,performance_matched,-0.272272695262552,-0.2804186444080146,0.008145949145462583,0.009798040391921616,502,True
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_vs_shuffled_c,shuffled_c,-0.272272695262552,-0.27682014413699485,0.004547448874442879,0.022595480903819236,502,True
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_vs_phase_rotated,phase_rotated,-0.272272695262552,-0.277433556202203,0.005160860939650966,0.04319136172765447,502,True
fes_string_conditioned,z_reward,A_to_C_to_B,true_vs_random,random,-0.7160957188629731,-0.7157828417729833,-0.00031287708998969477,0.5052989402119576,502,False
fes_string_conditioned,z_reward,A_to_C_to_B,true_vs_balanced,balanced,-0.7160957188629731,-0.7140804129272932,-0.0020153059356799396,0.648870225954809,502,False
fes_string_conditioned,z_reward,A_to_C_to_B,true_vs_performance_matched,performance_matched,-0.7160957188629731,-0.7546880546930745,0.038592335830101326,0.0001999600079984003,502,True
fes_string_conditioned,z_reward,A_to_C_to_B,true_vs_shuffled_c,shuffled_c,-0.7160957188629731,-0.710491716112892,-0.005604002750081142,0.7688462307538493,502,False
fes_string_conditioned,z_reward,A_to_C_to_B,true_vs_phase_rotated,phase_rotated,-0.7160957188629731,-0.7177313556446181,0.0016356367816450189,0.40371925614877024,502,False
fes_string_conditioned,z_reward,B_to_C_to_A,true_vs_random,random,-0.717073226283539,-0.7535944430137945,0.036521216730255456,0.007798440311937612,502,True
fes_string_conditioned,z_reward,B_to_C_to_A,true_vs_balanced,balanced,-0.717073226283539,-0.7179173728310504,0.0008441465475114347,0.4443111377724455,502,False
fes_string_conditioned,z_reward,B_to_C_to_A,true_vs_performance_matched,performance_matched,-0.717073226283539,-0.7567212958718835,0.039648069588344576,0.0011997600479904018,502,True
fes_string_conditioned,z_reward,B_to_C_to_A,true_vs_shuffled_c,shuffled_c,-0.717073226283539,-0.7104365691977436,-0.006636657085795381,0.7990401919616077,502,False
fes_string_conditioned,z_reward,B_to_C_to_A,true_vs_phase_rotated,phase_rotated,-0.717073226283539,-0.7262051469300489,0.009131920646509958,0.1793641271745651,502,False
fes_string_conditioned,rank_reward,A_to_C_to_B,true_vs_random,random,-0.7072866127129764,-0.7102620004448325,0.002975387731855997,0.4335132973405319,502,False
fes_string_conditioned,rank_reward,A_to_C_to_B,true_vs_balanced,balanced,-0.7072866127129764,-0.7143325140564794,0.007045901343502898,0.11417716456708658,502,False
fes_string_conditioned,rank_reward,A_to_C_to_B,true_vs_performance_matched,performance_matched,-0.7072866127129764,-0.7446042301441247,0.0373176174311482,0.0007998400319936012,502,True
fes_string_conditioned,rank_reward,A_to_C_to_B,true_vs_shuffled_c,shuffled_c,-0.7072866127129764,-0.7135600034022804,0.006273390689304131,0.21775644871025795,502,False
fes_string_conditioned,rank_reward,A_to_C_to_B,true_vs_phase_rotated,phase_rotated,-0.7072866127129764,-0.7132994888907395,0.006012876177763185,0.18056388722255548,502,False
fes_string_conditioned,rank_reward,B_to_C_to_A,true_vs_random,random,-0.709300211120681,-0.7407487159985252,0.031448504877844285,0.02579484103179364,502,True
fes_string_conditioned,rank_reward,B_to_C_to_A,true_vs_balanced,balanced,-0.709300211120681,-0.717347918867321,0.008047707746640043,0.11897620475904819,502,False
fes_string_conditioned,rank_reward,B_to_C_to_A,true_vs_performance_matched,performance_matched,-0.709300211120681,-0.750203504198704,0.04090329307802308,0.0009998000399920016,502,True
fes_string_conditioned,rank_reward,B_to_C_to_A,true_vs_shuffled_c,shuffled_c,-0.709300211120681,-0.7127574134986725,0.003457202377991533,0.34493101379724056,502,False
fes_string_conditioned,rank_reward,B_to_C_to_A,true_vs_phase_rotated,phase_rotated,-0.709300211120681,-0.7257151074946215,0.016414896373940616,0.05358928214357129,502,False
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_vs_random,random,-0.2745255543030141,-0.27814020540949413,0.0036146511064800253,0.28834233153369326,502,False
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_vs_balanced,balanced,-0.2745255543030141,-0.27687332890592253,0.002347774602908458,0.02979404119176165,502,True
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_vs_performance_matched,performance_matched,-0.2745255543030141,-0.27841245425116584,0.003886899948151766,0.10057988402319536,502,False
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_vs_shuffled_c,shuffled_c,-0.2745255543030141,-0.2754788978983736,0.0009533435953594802,0.23215356928614278,502,False
fes_string_conditioned,gmr72_bridge_composite,A_to_C_to_B,true_vs_phase_rotated,phase_rotated,-0.2745255543030141,-0.27765193295051577,0.0031263786475016495,0.015396920615876825,502,True
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_vs_random,random,-0.275393758967806,-0.2869085598870474,0.01151480091924138,0.027794441111777646,502,True
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_vs_balanced,balanced,-0.275393758967806,-0.2773493154866781,0.001955556518872151,0.07898420315936813,502,False
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_vs_performance_matched,performance_matched,-0.275393758967806,-0.2804186444080146,0.005024885440208575,0.07218556288742252,502,False
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_vs_shuffled_c,shuffled_c,-0.275393758967806,-0.27590794789071255,0.0005141889229065084,0.34933013397320534,502,False
fes_string_conditioned,gmr72_bridge_composite,B_to_C_to_A,true_vs_phase_rotated,phase_rotated,-0.275393758967806,-0.2793109069226436,0.0039171479548375555,0.04299140171965607,502,True
linear_c_state,z_reward,A_to_C_to_B,true_vs_random,random,-0.6758495687440289,-0.7413197003927994,0.0654701316487705,0.0001999600079984003,502,True
linear_c_state,z_reward,A_to_C_to_B,true_vs_balanced,balanced,-0.6758495687440289,-0.7140804129272932,0.03823084418326437,0.0001999600079984003,502,True
linear_c_state,z_reward,A_to_C_to_B,true_vs_performance_matched,performance_matched,-0.6758495687440289,-0.7546880546930745,0.07883848594904562,0.0001999600079984003,502,True
linear_c_state,z_reward,A_to_C_to_B,true_vs_shuffled_c,shuffled_c,-0.6758495687440289,-0.7136156198469505,0.03776605110292168,0.003199360127974405,502,True
linear_c_state,z_reward,A_to_C_to_B,true_vs_phase_rotated,phase_rotated,-0.6758495687440289,-0.7156098421481304,0.03976027340410154,0.002999400119976005,502,True
linear_c_state,z_reward,B_to_C_to_A,true_vs_random,random,-0.6667860859214115,-0.7371934462460621,0.0704073603246507,0.0001999600079984003,502,True
linear_c_state,z_reward,B_to_C_to_A,true_vs_balanced,balanced,-0.6667860859214115,-0.7179173728310504,0.05113128690963889,0.0001999600079984003,502,True
linear_c_state,z_reward,B_to_C_to_A,true_vs_performance_matched,performance_matched,-0.6667860859214115,-0.7567212958718835,0.08993520995047201,0.0001999600079984003,502,True
linear_c_state,z_reward,B_to_C_to_A,true_vs_shuffled_c,shuffled_c,-0.6667860859214115,-0.7168837257142376,0.050097639792826054,0.0009998000399920016,502,True
linear_c_state,z_reward,B_to_C_to_A,true_vs_phase_rotated,phase_rotated,-0.6667860859214115,-0.7096992989998104,0.04291321307839888,0.0007998400319936012,502,True
linear_c_state,rank_reward,A_to_C_to_B,true_vs_random,random,-0.6645096745245741,-0.7439259736833045,0.07941629915873036,0.0001999600079984003,502,True
linear_c_state,rank_reward,A_to_C_to_B,true_vs_balanced,balanced,-0.6645096745245741,-0.7143325140564794,0.04982283953190517,0.0001999600079984003,502,True
linear_c_state,rank_reward,A_to_C_to_B,true_vs_performance_matched,performance_matched,-0.6645096745245741,-0.7446042301441247,0.08009455561955049,0.0001999600079984003,502,True
linear_c_state,rank_reward,A_to_C_to_B,true_vs_shuffled_c,shuffled_c,-0.6645096745245741,-0.71535052859436,0.050840854069785876,0.0005998800239952009,502,True
linear_c_state,rank_reward,A_to_C_to_B,true_vs_phase_rotated,phase_rotated,-0.6645096745245741,-0.7215007185755984,0.05699104405102426,0.0003999200159968006,502,True
linear_c_state,rank_reward,B_to_C_to_A,true_vs_random,random,-0.6594298734361925,-0.7385592951745907,0.07912942173839807,0.0001999600079984003,502,True
linear_c_state,rank_reward,B_to_C_to_A,true_vs_balanced,balanced,-0.6594298734361925,-0.717347918867321,0.057918045431128336,0.0001999600079984003,502,True
linear_c_state,rank_reward,B_to_C_to_A,true_vs_performance_matched,performance_matched,-0.6594298734361925,-0.750203504198704,0.09077363076251138,0.0001999600079984003,502,True
linear_c_state,rank_reward,B_to_C_to_A,true_vs_shuffled_c,shuffled_c,-0.6594298734361925,-0.721413789681178,0.06198391624498537,0.0001999600079984003,502,True
linear_c_state,rank_reward,B_to_C_to_A,true_vs_phase_rotated,phase_rotated,-0.6594298734361925,-0.7100703352858431,0.050640461849650556,0.0007998400319936012,502,True
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,true_vs_random,random,-0.26991542250984546,-0.28462832133956445,0.014712898829718993,0.0061987602479504095,502,True
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,true_vs_balanced,balanced,-0.26991542250984546,-0.27687332890592253,0.006957906396077107,0.0001999600079984003,502,True
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,true_vs_performance_matched,performance_matched,-0.26991542250984546,-0.27841245425116584,0.008497031741320415,0.004399120175964807,502,True
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,true_vs_shuffled_c,shuffled_c,-0.26991542250984546,-0.2769358024687727,0.0070203799589272295,0.0009998000399920016,502,True
linear_c_state,gmr72_bridge_composite,A_to_C_to_B,true_vs_phase_rotated,phase_rotated,-0.26991542250984546,-0.2780247112184924,0.008109288708647015,0.0009998000399920016,502,True
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,true_vs_random,random,-0.27062265151803716,-0.284659218508699,0.014036566990661806,0.010997800439912017,502,True
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,true_vs_balanced,balanced,-0.27062265151803716,-0.2773493154866781,0.006726663968640967,0.0001999600079984003,502,True
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,true_vs_performance_matched,performance_matched,-0.27062265151803716,-0.2804186444080146,0.009795992889977389,0.0027994401119776045,502,True
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,true_vs_shuffled_c,shuffled_c,-0.27062265151803716,-0.2772748672610078,0.006652215742970586,0.003799240151969606,502,True
linear_c_state,gmr72_bridge_composite,B_to_C_to_A,true_vs_phase_rotated,phase_rotated,-0.27062265151803716,-0.27597851931519085,0.005355867797153665,0.028994201159768047,502,True

## No-C Control Comparisons

mode,endpoint,direction,comparison,control_kind,mean_true,mean_control,effect,p_greater,n_pairs,passes
combined_c_fes_gmr72,z_reward,A_to_B_no_C,true_vs_random,random,-0.7290410663847228,-0.7387215358276098,0.009680469442886953,0.2421515696860628,502,False
combined_c_fes_gmr72,z_reward,A_to_B_no_C,true_vs_balanced,balanced,-0.7290410663847228,-0.7274142830853981,-0.0016267832993247385,0.982003599280144,502,False
combined_c_fes_gmr72,z_reward,A_to_B_no_C,true_vs_performance_matched,performance_matched,-0.7290410663847228,-0.740691389768558,0.011650323383835148,0.03119376124775045,502,True
combined_c_fes_gmr72,z_reward,A_to_B_no_C,true_vs_shuffled_c,shuffled_c,-0.7290410663847228,-0.7290410663847228,0.0,1.0,502,False
combined_c_fes_gmr72,z_reward,A_to_B_no_C,true_vs_phase_rotated,phase_rotated,-0.7290410663847228,-0.726750005367899,-0.0022910610168237256,0.9236152769446111,502,False
combined_c_fes_gmr72,z_reward,B_to_A_no_C,true_vs_random,random,-0.7290410663847228,-0.743110831520234,0.01406976513551124,0.14877024595080984,502,False
combined_c_fes_gmr72,z_reward,B_to_A_no_C,true_vs_balanced,balanced,-0.7290410663847228,-0.7274142830853981,-0.0016267832993247385,0.9828034393121375,502,False
combined_c_fes_gmr72,z_reward,B_to_A_no_C,true_vs_performance_matched,performance_matched,-0.7290410663847228,-0.740691389768558,0.011650323383835148,0.03719256148770246,502,True
combined_c_fes_gmr72,z_reward,B_to_A_no_C,true_vs_shuffled_c,shuffled_c,-0.7290410663847228,-0.7290410663847228,0.0,1.0,502,False
combined_c_fes_gmr72,z_reward,B_to_A_no_C,true_vs_phase_rotated,phase_rotated,-0.7290410663847228,-0.726750005367899,-0.0022910610168237256,0.9336132773445311,502,False
combined_c_fes_gmr72,rank_reward,A_to_B_no_C,true_vs_random,random,-0.7243245405813526,-0.7336245864421863,0.009300045860833665,0.260747850429914,502,False
combined_c_fes_gmr72,rank_reward,A_to_B_no_C,true_vs_balanced,balanced,-0.7243245405813526,-0.7227024024110834,-0.0016221381702692368,0.9802039592081584,502,False
combined_c_fes_gmr72,rank_reward,A_to_B_no_C,true_vs_performance_matched,performance_matched,-0.7243245405813526,-0.7374864061636744,0.013161865582321722,0.03479304139172166,502,True
combined_c_fes_gmr72,rank_reward,A_to_B_no_C,true_vs_shuffled_c,shuffled_c,-0.7243245405813526,-0.7243245405813526,0.0,1.0,502,False
combined_c_fes_gmr72,rank_reward,A_to_B_no_C,true_vs_phase_rotated,phase_rotated,-0.7243245405813526,-0.7220003192372372,-0.002324221344115477,0.9438112377524495,502,False
combined_c_fes_gmr72,rank_reward,B_to_A_no_C,true_vs_random,random,-0.7243245405813526,-0.7364763778765054,0.012151837295152883,0.1833633273345331,502,False
combined_c_fes_gmr72,rank_reward,B_to_A_no_C,true_vs_balanced,balanced,-0.7243245405813526,-0.7227024024110834,-0.0016221381702692368,0.9774045190961808,502,False
combined_c_fes_gmr72,rank_reward,B_to_A_no_C,true_vs_performance_matched,performance_matched,-0.7243245405813526,-0.7374864061636744,0.013161865582321722,0.038592281543691265,502,True
combined_c_fes_gmr72,rank_reward,B_to_A_no_C,true_vs_shuffled_c,shuffled_c,-0.7243245405813526,-0.7243245405813526,0.0,1.0,502,False
combined_c_fes_gmr72,rank_reward,B_to_A_no_C,true_vs_phase_rotated,phase_rotated,-0.7243245405813526,-0.7220003192372372,-0.002324221344115477,0.9372125574885023,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_B_no_C,true_vs_random,random,-0.2851699656780228,-0.2904600103168394,0.005290044638816543,0.16256748650269945,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_B_no_C,true_vs_balanced,balanced,-0.2851699656780228,-0.2849776307066979,-0.00019233497132491455,0.9698060387922416,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_B_no_C,true_vs_performance_matched,performance_matched,-0.2851699656780228,-0.2893284007124663,0.0041584350344435125,0.11297740451909619,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_B_no_C,true_vs_shuffled_c,shuffled_c,-0.2851699656780228,-0.2851699656780228,0.0,1.0,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,A_to_B_no_C,true_vs_phase_rotated,phase_rotated,-0.2851699656780228,-0.2848342205542315,-0.00033574512379127446,0.7536492701459708,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_A_no_C,true_vs_random,random,-0.2851699656780228,-0.2905788598419119,0.005408894163889102,0.12917416516696661,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_A_no_C,true_vs_balanced,balanced,-0.2851699656780228,-0.2849776307066979,-0.00019233497132491455,0.972005598880224,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_A_no_C,true_vs_performance_matched,performance_matched,-0.2851699656780228,-0.2893284007124663,0.0041584350344435125,0.11097780443911218,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_A_no_C,true_vs_shuffled_c,shuffled_c,-0.2851699656780228,-0.2851699656780228,0.0,1.0,502,False
combined_c_fes_gmr72,gmr72_bridge_composite,B_to_A_no_C,true_vs_phase_rotated,phase_rotated,-0.2851699656780228,-0.2848342205542315,-0.00033574512379127446,0.7660467906418716,502,False
gmr72_phase_conditioned,z_reward,A_to_B_no_C,true_vs_random,random,-0.7290410663847228,-0.7295044076161584,0.0004633412314355854,0.47590481903619275,502,False
gmr72_phase_conditioned,z_reward,A_to_B_no_C,true_vs_balanced,balanced,-0.7290410663847228,-0.7274142830853981,-0.0016267832993247385,0.9834033193361328,502,False
gmr72_phase_conditioned,z_reward,A_to_B_no_C,true_vs_performance_matched,performance_matched,-0.7290410663847228,-0.740691389768558,0.011650323383835148,0.03539292141571686,502,True
gmr72_phase_conditioned,z_reward,A_to_B_no_C,true_vs_shuffled_c,shuffled_c,-0.7290410663847228,-0.7290410663847228,0.0,1.0,502,False
gmr72_phase_conditioned,z_reward,A_to_B_no_C,true_vs_phase_rotated,phase_rotated,-0.7290410663847228,-0.726750005367899,-0.0022910610168237256,0.9386122775444911,502,False
gmr72_phase_conditioned,z_reward,B_to_A_no_C,true_vs_random,random,-0.7290410663847228,-0.7411517020707682,0.012110635686045337,0.17896420715856828,502,False
gmr72_phase_conditioned,z_reward,B_to_A_no_C,true_vs_balanced,balanced,-0.7290410663847228,-0.7274142830853981,-0.0016267832993247385,0.982003599280144,502,False
gmr72_phase_conditioned,z_reward,B_to_A_no_C,true_vs_performance_matched,performance_matched,-0.7290410663847228,-0.740691389768558,0.011650323383835148,0.036392721455708855,502,True
gmr72_phase_conditioned,z_reward,B_to_A_no_C,true_vs_shuffled_c,shuffled_c,-0.7290410663847228,-0.7290410663847228,0.0,1.0,502,False
gmr72_phase_conditioned,z_reward,B_to_A_no_C,true_vs_phase_rotated,phase_rotated,-0.7290410663847228,-0.726750005367899,-0.0022910610168237256,0.9322135572885423,502,False
gmr72_phase_conditioned,rank_reward,A_to_B_no_C,true_vs_random,random,-0.7243245405813526,-0.7149176783037654,-0.009406862277587238,0.7470505898820236,502,False
gmr72_phase_conditioned,rank_reward,A_to_B_no_C,true_vs_balanced,balanced,-0.7243245405813526,-0.7227024024110834,-0.0016221381702692368,0.981003799240152,502,False
gmr72_phase_conditioned,rank_reward,A_to_B_no_C,true_vs_performance_matched,performance_matched,-0.7243245405813526,-0.7374864061636744,0.013161865582321722,0.03719256148770246,502,True
gmr72_phase_conditioned,rank_reward,A_to_B_no_C,true_vs_shuffled_c,shuffled_c,-0.7243245405813526,-0.7243245405813526,0.0,1.0,502,False
gmr72_phase_conditioned,rank_reward,A_to_B_no_C,true_vs_phase_rotated,phase_rotated,-0.7243245405813526,-0.7220003192372372,-0.002324221344115477,0.9478104379124175,502,False
gmr72_phase_conditioned,rank_reward,B_to_A_no_C,true_vs_random,random,-0.7243245405813526,-0.7350315724744142,0.010707031893061566,0.22155568886222757,502,False
gmr72_phase_conditioned,rank_reward,B_to_A_no_C,true_vs_balanced,balanced,-0.7243245405813526,-0.7227024024110834,-0.0016221381702692368,0.981003799240152,502,False
gmr72_phase_conditioned,rank_reward,B_to_A_no_C,true_vs_performance_matched,performance_matched,-0.7243245405813526,-0.7374864061636744,0.013161865582321722,0.03699260147970406,502,True
gmr72_phase_conditioned,rank_reward,B_to_A_no_C,true_vs_shuffled_c,shuffled_c,-0.7243245405813526,-0.7243245405813526,0.0,1.0,502,False
gmr72_phase_conditioned,rank_reward,B_to_A_no_C,true_vs_phase_rotated,phase_rotated,-0.7243245405813526,-0.7220003192372372,-0.002324221344115477,0.9478104379124175,502,False
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_B_no_C,true_vs_random,random,-0.2851699656780228,-0.28443648951618766,-0.0007334761618350805,0.5714857028594281,502,False
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_B_no_C,true_vs_balanced,balanced,-0.2851699656780228,-0.2849776307066979,-0.00019233497132491455,0.9696060787842431,502,False
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_B_no_C,true_vs_performance_matched,performance_matched,-0.2851699656780228,-0.2893284007124663,0.0041584350344435125,0.11077784443111378,502,False
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_B_no_C,true_vs_shuffled_c,shuffled_c,-0.2851699656780228,-0.2851699656780228,0.0,1.0,502,False
gmr72_phase_conditioned,gmr72_bridge_composite,A_to_B_no_C,true_vs_phase_rotated,phase_rotated,-0.2851699656780228,-0.2848342205542315,-0.00033574512379127446,0.7538492301539692,502,False
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_A_no_C,true_vs_random,random,-0.2851699656780228,-0.2927156399378799,0.007545674259857176,0.060187962407518496,502,False
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_A_no_C,true_vs_balanced,balanced,-0.2851699656780228,-0.2849776307066979,-0.00019233497132491455,0.9712057588482303,502,False
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_A_no_C,true_vs_performance_matched,performance_matched,-0.2851699656780228,-0.2893284007124663,0.0041584350344435125,0.1191761647670466,502,False
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_A_no_C,true_vs_shuffled_c,shuffled_c,-0.2851699656780228,-0.2851699656780228,0.0,1.0,502,False
gmr72_phase_conditioned,gmr72_bridge_composite,B_to_A_no_C,true_vs_phase_rotated,phase_rotated,-0.2851699656780228,-0.2848342205542315,-0.00033574512379127446,0.7574485102979404,502,False
fes_string_conditioned,z_reward,A_to_B_no_C,true_vs_random,random,-0.7290410663847228,-0.7286048378254285,-0.00043622855929438347,0.5212957408518296,502,False
fes_string_conditioned,z_reward,A_to_B_no_C,true_vs_balanced,balanced,-0.7290410663847228,-0.7274142830853981,-0.0016267832993247385,0.9796040791841631,502,False
fes_string_conditioned,z_reward,A_to_B_no_C,true_vs_performance_matched,performance_matched,-0.7290410663847228,-0.740691389768558,0.011650323383835148,0.03579284143171366,502,True
fes_string_conditioned,z_reward,A_to_B_no_C,true_vs_shuffled_c,shuffled_c,-0.7290410663847228,-0.7290410663847228,0.0,1.0,502,False
fes_string_conditioned,z_reward,A_to_B_no_C,true_vs_phase_rotated,phase_rotated,-0.7290410663847228,-0.726750005367899,-0.0022910610168237256,0.9248150369926015,502,False
fes_string_conditioned,z_reward,B_to_A_no_C,true_vs_random,random,-0.7290410663847228,-0.7148504911181858,-0.014190575266537074,0.8584283143371326,502,False
fes_string_conditioned,z_reward,B_to_A_no_C,true_vs_balanced,balanced,-0.7290410663847228,-0.7274142830853981,-0.0016267832993247385,0.9794041191761648,502,False
fes_string_conditioned,z_reward,B_to_A_no_C,true_vs_performance_matched,performance_matched,-0.7290410663847228,-0.740691389768558,0.011650323383835148,0.03499300139972006,502,True
fes_string_conditioned,z_reward,B_to_A_no_C,true_vs_shuffled_c,shuffled_c,-0.7290410663847228,-0.7290410663847228,0.0,1.0,502,False
fes_string_conditioned,z_reward,B_to_A_no_C,true_vs_phase_rotated,phase_rotated,-0.7290410663847228,-0.726750005367899,-0.0022910610168237256,0.9332133573285343,502,False
fes_string_conditioned,rank_reward,A_to_B_no_C,true_vs_random,random,-0.7243245405813526,-0.7233342792854474,-0.0009902612959053964,0.5212957408518296,502,False
fes_string_conditioned,rank_reward,A_to_B_no_C,true_vs_balanced,balanced,-0.7243245405813526,-0.7227024024110834,-0.0016221381702692368,0.9812037592481504,502,False
fes_string_conditioned,rank_reward,A_to_B_no_C,true_vs_performance_matched,performance_matched,-0.7243245405813526,-0.7374864061636744,0.013161865582321722,0.03939212157568486,502,True
fes_string_conditioned,rank_reward,A_to_B_no_C,true_vs_shuffled_c,shuffled_c,-0.7243245405813526,-0.7243245405813526,0.0,1.0,502,False
fes_string_conditioned,rank_reward,A_to_B_no_C,true_vs_phase_rotated,phase_rotated,-0.7243245405813526,-0.7220003192372372,-0.002324221344115477,0.944011197760448,502,False
fes_string_conditioned,rank_reward,B_to_A_no_C,true_vs_random,random,-0.7243245405813526,-0.7055174707758608,-0.018807069805491752,0.9144171165766847,502,False
fes_string_conditioned,rank_reward,B_to_A_no_C,true_vs_balanced,balanced,-0.7243245405813526,-0.7227024024110834,-0.0016221381702692368,0.979004199160168,502,False
fes_string_conditioned,rank_reward,B_to_A_no_C,true_vs_performance_matched,performance_matched,-0.7243245405813526,-0.7374864061636744,0.013161865582321722,0.03499300139972006,502,True
fes_string_conditioned,rank_reward,B_to_A_no_C,true_vs_shuffled_c,shuffled_c,-0.7243245405813526,-0.7243245405813526,0.0,1.0,502,False
fes_string_conditioned,rank_reward,B_to_A_no_C,true_vs_phase_rotated,phase_rotated,-0.7243245405813526,-0.7220003192372372,-0.002324221344115477,0.9444111177764447,502,False
fes_string_conditioned,gmr72_bridge_composite,A_to_B_no_C,true_vs_random,random,-0.2851699656780228,-0.28276700073282734,-0.0024029649451954163,0.6834633073385323,502,False
fes_string_conditioned,gmr72_bridge_composite,A_to_B_no_C,true_vs_balanced,balanced,-0.2851699656780228,-0.2849776307066979,-0.00019233497132491455,0.9686062787442512,502,False
fes_string_conditioned,gmr72_bridge_composite,A_to_B_no_C,true_vs_performance_matched,performance_matched,-0.2851699656780228,-0.2893284007124663,0.0041584350344435125,0.11157768446310738,502,False
fes_string_conditioned,gmr72_bridge_composite,A_to_B_no_C,true_vs_shuffled_c,shuffled_c,-0.2851699656780228,-0.2851699656780228,0.0,1.0,502,False
fes_string_conditioned,gmr72_bridge_composite,A_to_B_no_C,true_vs_phase_rotated,phase_rotated,-0.2851699656780228,-0.2848342205542315,-0.00033574512379127446,0.7514497100579884,502,False
fes_string_conditioned,gmr72_bridge_composite,B_to_A_no_C,true_vs_random,random,-0.2851699656780228,-0.28468894567285746,-0.00048102000516536745,0.5414917016596681,502,False
fes_string_conditioned,gmr72_bridge_composite,B_to_A_no_C,true_vs_balanced,balanced,-0.2851699656780228,-0.2849776307066979,-0.00019233497132491455,0.9772045590881824,502,False
fes_string_conditioned,gmr72_bridge_composite,B_to_A_no_C,true_vs_performance_matched,performance_matched,-0.2851699656780228,-0.2893284007124663,0.0041584350344435125,0.11677664467106579,502,False
fes_string_conditioned,gmr72_bridge_composite,B_to_A_no_C,true_vs_shuffled_c,shuffled_c,-0.2851699656780228,-0.2851699656780228,0.0,1.0,502,False
fes_string_conditioned,gmr72_bridge_composite,B_to_A_no_C,true_vs_phase_rotated,phase_rotated,-0.2851699656780228,-0.2848342205542315,-0.00033574512379127446,0.7654469106178764,502,False
linear_c_state,z_reward,A_to_B_no_C,true_vs_random,random,-0.7290410663847228,-0.7295044076161584,0.0004633412314355854,0.48930213957208557,502,False
linear_c_state,z_reward,A_to_B_no_C,true_vs_balanced,balanced,-0.7290410663847228,-0.7274142830853981,-0.0016267832993247385,0.9806038792241552,502,False
linear_c_state,z_reward,A_to_B_no_C,true_vs_performance_matched,performance_matched,-0.7290410663847228,-0.740691389768558,0.011650323383835148,0.03939212157568486,502,True
linear_c_state,z_reward,A_to_B_no_C,true_vs_shuffled_c,shuffled_c,-0.7290410663847228,-0.7290410663847228,0.0,1.0,502,False
linear_c_state,z_reward,A_to_B_no_C,true_vs_phase_rotated,phase_rotated,-0.7290410663847228,-0.726750005367899,-0.0022910610168237256,0.9282143571285743,502,False
linear_c_state,z_reward,B_to_A_no_C,true_vs_random,random,-0.7290410663847228,-0.7411517020707682,0.012110635686045337,0.1739652069586083,502,False
linear_c_state,z_reward,B_to_A_no_C,true_vs_balanced,balanced,-0.7290410663847228,-0.7274142830853981,-0.0016267832993247385,0.9824035192961408,502,False
linear_c_state,z_reward,B_to_A_no_C,true_vs_performance_matched,performance_matched,-0.7290410663847228,-0.740691389768558,0.011650323383835148,0.033793241351729654,502,True
linear_c_state,z_reward,B_to_A_no_C,true_vs_shuffled_c,shuffled_c,-0.7290410663847228,-0.7290410663847228,0.0,1.0,502,False
linear_c_state,z_reward,B_to_A_no_C,true_vs_phase_rotated,phase_rotated,-0.7290410663847228,-0.726750005367899,-0.0022910610168237256,0.9276144771045791,502,False
linear_c_state,rank_reward,A_to_B_no_C,true_vs_random,random,-0.7243245405813526,-0.7149176783037654,-0.009406862277587238,0.7484503099380124,502,False
linear_c_state,rank_reward,A_to_B_no_C,true_vs_balanced,balanced,-0.7243245405813526,-0.7227024024110834,-0.0016221381702692368,0.9774045190961808,502,False
linear_c_state,rank_reward,A_to_B_no_C,true_vs_performance_matched,performance_matched,-0.7243245405813526,-0.7374864061636744,0.013161865582321722,0.03659268146370726,502,True
linear_c_state,rank_reward,A_to_B_no_C,true_vs_shuffled_c,shuffled_c,-0.7243245405813526,-0.7243245405813526,0.0,1.0,502,False
linear_c_state,rank_reward,A_to_B_no_C,true_vs_phase_rotated,phase_rotated,-0.7243245405813526,-0.7220003192372372,-0.002324221344115477,0.9456108778244351,502,False
linear_c_state,rank_reward,B_to_A_no_C,true_vs_random,random,-0.7243245405813526,-0.7350315724744142,0.010707031893061566,0.22055588882223556,502,False
linear_c_state,rank_reward,B_to_A_no_C,true_vs_balanced,balanced,-0.7243245405813526,-0.7227024024110834,-0.0016221381702692368,0.9768046390721855,502,False
linear_c_state,rank_reward,B_to_A_no_C,true_vs_performance_matched,performance_matched,-0.7243245405813526,-0.7374864061636744,0.013161865582321722,0.038992201559688064,502,True
linear_c_state,rank_reward,B_to_A_no_C,true_vs_shuffled_c,shuffled_c,-0.7243245405813526,-0.7243245405813526,0.0,1.0,502,False
linear_c_state,rank_reward,B_to_A_no_C,true_vs_phase_rotated,phase_rotated,-0.7243245405813526,-0.7220003192372372,-0.002324221344115477,0.9378124375124975,502,False
linear_c_state,gmr72_bridge_composite,A_to_B_no_C,true_vs_random,random,-0.2851699656780228,-0.28443648951618766,-0.0007334761618350805,0.554489102179564,502,False
linear_c_state,gmr72_bridge_composite,A_to_B_no_C,true_vs_balanced,balanced,-0.2851699656780228,-0.2849776307066979,-0.00019233497132491455,0.9686062787442512,502,False
linear_c_state,gmr72_bridge_composite,A_to_B_no_C,true_vs_performance_matched,performance_matched,-0.2851699656780228,-0.2893284007124663,0.0041584350344435125,0.11137772445510898,502,False
linear_c_state,gmr72_bridge_composite,A_to_B_no_C,true_vs_shuffled_c,shuffled_c,-0.2851699656780228,-0.2851699656780228,0.0,1.0,502,False
linear_c_state,gmr72_bridge_composite,A_to_B_no_C,true_vs_phase_rotated,phase_rotated,-0.2851699656780228,-0.2848342205542315,-0.00033574512379127446,0.7694461107778444,502,False
linear_c_state,gmr72_bridge_composite,B_to_A_no_C,true_vs_random,random,-0.2851699656780228,-0.2927156399378799,0.007545674259857176,0.060787842431513694,502,False
linear_c_state,gmr72_bridge_composite,B_to_A_no_C,true_vs_balanced,balanced,-0.2851699656780228,-0.2849776307066979,-0.00019233497132491455,0.9708058388322336,502,False
linear_c_state,gmr72_bridge_composite,B_to_A_no_C,true_vs_performance_matched,performance_matched,-0.2851699656780228,-0.2893284007124663,0.0041584350344435125,0.11037792441511697,502,False
linear_c_state,gmr72_bridge_composite,B_to_A_no_C,true_vs_shuffled_c,shuffled_c,-0.2851699656780228,-0.2851699656780228,0.0,1.0,502,False
linear_c_state,gmr72_bridge_composite,B_to_A_no_C,true_vs_phase_rotated,phase_rotated,-0.2851699656780228,-0.2848342205542315,-0.00033574512379127446,0.7650469906018796,502,False

## Settings

- n_folds: 5
- min_state_events: 8
- temperature: 0.35
- n_perm: 5000
- seed: 61820
