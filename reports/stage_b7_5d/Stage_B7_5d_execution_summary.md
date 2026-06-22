# Stage B7.5d Topology-Flip Localization Audit

Status: executed after `Stage_B7_5d_preregistration_email_sent.md`.

## Registered Question

Under which topology conditions does the ordering between reverse-side C->AB and full self-consistent R* flip?

## Layer 1: C8-C16 Sweep

topology_arm,comparison,left_arm,right_arm,mean_delta,median_delta,sd_delta,left_win_fraction,bootstrap_ci_low,bootstrap_ci_high,classification,base_topology,perturbation_kind,node_count_n,distance_from_12,signed_distance_from_12,is_odd,edge_count,is_ring_sharing,is_reversed,is_null
c8,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.004707537156492543,-0.004970466128519806,0.0042545997663096255,0.05555555555555555,-0.0060111026477154324,-0.0031803715259995737,reverse-stable,c8,sweep,8,4,-4,False,32,False,False,False
c9,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.00015600182204748706,-0.00040571185446879585,0.0024555086135106255,0.4722222222222222,-0.0009157490393244619,0.0006751898004425405,boundary,c9,sweep,9,3,-3,True,36,False,False,False
c10,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.00014643711446370552,-9.893236357209814e-05,0.0028465282814008524,0.4722222222222222,-0.0008143757392624441,0.0010538276956574247,boundary,c10,sweep,10,2,-2,False,40,False,False,False
c11,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,1.5328161397065247e-05,-0.0004203030156357474,0.0034254148202004582,0.4722222222222222,-0.0011081140319892395,0.0011094582697948943,boundary,c11,sweep,11,1,-1,True,44,False,False,False
c12,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.004485799567179342,-0.0043943210685787135,0.0034983740329806176,0.05555555555555555,-0.005654719123585501,-0.0033631294509038493,reverse-stable,c12,sweep,12,0,0,False,48,False,False,False
c13,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.002647637560376963,0.0027810186313598547,0.00277933248849285,0.8333333333333334,0.0017669224682359973,0.0035387672446484824,full-stable,c13,sweep,13,1,1,True,52,False,False,False
c14,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.000657284044251341,0.0007014039893039681,0.002003624440726313,0.5833333333333334,1.7213553396760166e-06,0.0012800945653080812,full-stable,c14,sweep,14,2,2,False,56,False,False,False
c15,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.0003909338657384039,-0.0007074967099377693,0.0025391088464629644,0.4444444444444444,-0.0012334792303282597,0.0004556469801436214,boundary,c15,sweep,15,3,3,True,60,False,False,False
c16,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0009116453733583268,0.0003469701287771814,0.0020306565915240156,0.6388888888888888,0.000281820370687038,0.0015802742234054437,full-stable,c16,sweep,16,4,4,False,64,False,False,False

## Layer 2: Perturbation Focus

topology_arm,comparison,left_arm,right_arm,mean_delta,median_delta,sd_delta,left_win_fraction,bootstrap_ci_low,bootstrap_ci_high,classification,base_topology,perturbation_kind,node_count_n,distance_from_12,signed_distance_from_12,is_odd,edge_count,is_ring_sharing,is_reversed,is_null
c10_reversed,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.0001618053416596698,-0.0002601846851103184,0.0026001699860179997,0.4444444444444444,-0.0009785301230461978,0.0006825474618526615,boundary,c10,reversed,10,2,-2,False,40,False,True,False
c10_side_broken,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0041123907225288445,0.0042243551282507815,0.002274406243822468,1.0,0.0033412045525837144,0.004872810933797183,full-stable,c10,side_broken,10,2,-2,False,40,False,False,False
c10_shuffled,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0002668087713661282,0.0003384282378594547,0.0024560904303105417,0.6388888888888888,-0.0005574621580216012,0.0010291652290137137,boundary,c10,shuffled,10,2,-2,False,40,False,False,False
c10_degree_null,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.005206938883737573,-0.005223647595984966,0.00243259499844357,0.0,-0.005985030095782545,-0.004426490921695479,reverse-stable,c10,degree_null,10,2,-2,False,40,False,False,True
c10_edge_count_null,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.0007218326879154512,-0.0006060307300177559,0.003244528394176855,0.4444444444444444,-0.0017620446015817579,0.0003193249917626108,boundary,c10,edge_count_null,10,2,-2,False,40,False,False,True
c10_ring_share_5,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0004615519682978857,-0.00016292508510398166,0.002142213330955508,0.5,-0.00022102490525591505,0.0011720700182687,boundary,c10,ring_share_5,10,2,-2,False,50,True,False,False
c10_ring_share_7,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.001729417995076966,0.0014810501323162736,0.0022589281728964817,0.8055555555555556,0.0009730574400517308,0.0024631588882417016,full-stable,c10,ring_share_7,10,2,-2,False,60,True,False,False
c10_ring_share_10,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0001056811254580008,0.0006938108993646538,0.0023603213866764017,0.5555555555555556,-0.0006821702314065729,0.0008482734328939748,boundary,c10,ring_share_10,10,2,-2,False,40,True,False,False
c10_ring_share_11,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0006725379925218478,0.00017658481437699447,0.0023374592140239297,0.5277777777777778,-6.604567047572273e-05,0.0014560536637217324,boundary,c10,ring_share_11,10,2,-2,False,40,True,False,False
c12_reversed,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.0037682451846607484,-0.003758433640361769,0.0031648690465289294,0.1111111111111111,-0.004864101976292966,-0.002765780262169419,reverse-stable,c12,reversed,12,0,0,False,48,False,True,False
c12_side_broken,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0036945403863254955,0.0044525183796605295,0.0024936403445708372,0.9166666666666666,0.00290116930882437,0.004469258068182951,full-stable,c12,side_broken,12,0,0,False,48,False,False,False
c12_shuffled,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.002824942513068923,-0.002895934509778675,0.002578429260443478,0.1388888888888889,-0.0037044973992257746,-0.0020247461378792514,reverse-stable,c12,shuffled,12,0,0,False,48,False,False,False
c12_degree_null,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.0021366045400590524,-0.0021485132891222412,0.002648897870077126,0.2222222222222222,-0.0029409194897683844,-0.0012574906001782881,reverse-stable,c12,degree_null,12,0,0,False,48,False,False,True
c12_edge_count_null,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0006439654738914648,0.0008306702296838892,0.002312867451354641,0.6111111111111112,-0.00012012079154245465,0.0014407457322166727,boundary,c12,edge_count_null,12,0,0,False,48,False,False,True
c12_ring_share_5,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.005323998450993851,-0.00566429900205849,0.003173714211698952,0.027777777777777776,-0.006355333373170891,-0.00431289010596217,reverse-stable,c12,ring_share_5,12,0,0,False,72,True,False,False
c12_ring_share_7,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.005051192952251759,-0.005199150715991835,0.0026566370180119083,0.0,-0.005908445500564288,-0.004199793630994333,reverse-stable,c12,ring_share_7,12,0,0,False,72,True,False,False
c12_ring_share_10,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.003248150476473982,-0.003242037360302902,0.002575441164004111,0.1111111111111111,-0.004076979692343309,-0.002407218801021382,reverse-stable,c12,ring_share_10,12,0,0,False,48,True,False,False
c12_ring_share_11,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.003610357206673733,-0.003272338152236898,0.003100375444954206,0.1111111111111111,-0.0046588664491023085,-0.0026210870174678503,reverse-stable,c12,ring_share_11,12,0,0,False,48,True,False,False
c13_reversed,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.002142824819179852,0.0021303259557330177,0.0022023732721158963,0.8611111111111112,0.0014422662328236874,0.002872001240043137,full-stable,c13,reversed,13,1,1,True,52,False,True,False
c13_side_broken,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0038227590605215004,0.003849138257152342,0.0018418484617580984,0.9722222222222222,0.0032059775837020945,0.004406639475132765,full-stable,c13,side_broken,13,1,1,True,52,False,False,False
c13_shuffled,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0003849666875096371,-6.069036406220721e-05,0.002806853032468369,0.5,-0.0005353239344456992,0.0012695392097039212,boundary,c13,shuffled,13,1,1,True,52,False,False,False
c13_degree_null,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.00364916812140865,0.004508573337911549,0.0029436656132344214,0.8055555555555556,0.0026795578456921395,0.0045384406066197565,full-stable,c13,degree_null,13,1,1,True,52,False,False,True
c13_edge_count_null,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0007943468001926332,0.0009689655811565053,0.0022321360322380738,0.6388888888888888,3.847038645851869e-05,0.001524852217219264,full-stable,c13,edge_count_null,13,1,1,True,52,False,False,True
c13_ring_share_5,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0022267841959522842,0.0018228380011085143,0.002481925530958434,0.8333333333333334,0.0014151866479772848,0.0030446254998955256,full-stable,c13,ring_share_5,13,1,1,True,78,True,False,False
c13_ring_share_7,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.002406868303477406,0.0026626868826099374,0.0033009353295532545,0.8333333333333334,0.001375289984473523,0.0034870780443667848,full-stable,c13,ring_share_7,13,1,1,True,78,True,False,False
c13_ring_share_10,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.00245648266564911,0.0025518366476726707,0.002263020466546402,0.8888888888888888,0.0016876368474514952,0.0031562738164995887,full-stable,c13,ring_share_10,13,1,1,True,78,True,False,False
c13_ring_share_11,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0025260193062747924,0.002448420369581159,0.0018298052145094554,0.8888888888888888,0.0019277474931956773,0.0030849664937457667,full-stable,c13,ring_share_11,13,1,1,True,52,True,False,False
c14_reversed,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.00012390850160220925,0.00012539448485488413,0.001452204075610174,0.5,-0.0006183727859178027,0.0003741131523468106,boundary,c14,reversed,14,2,2,False,56,False,True,False
c14_side_broken,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.000732276493777806,0.0004797122148135417,0.0035892647426621046,0.5555555555555556,-0.0004277466063156549,0.0019144947589739341,boundary,c14,side_broken,14,2,2,False,56,False,False,False
c14_shuffled,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0031516643714585026,0.0034208566294751637,0.002260296291797638,0.9166666666666666,0.0023445446968896446,0.003895607538489385,full-stable,c14,shuffled,14,2,2,False,56,False,False,False
c14_degree_null,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.004735436523744291,0.00499743163992959,0.0020138205524491038,0.9722222222222222,0.004054047564404373,0.005315258924388366,full-stable,c14,degree_null,14,2,2,False,56,False,False,True
c14_edge_count_null,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0037909574462235943,0.0036472263875039525,0.0025777183911404327,0.9166666666666666,0.002962357809464114,0.004578899834240841,full-stable,c14,edge_count_null,14,2,2,False,56,False,False,True
c14_ring_share_5,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0005533247662385086,0.000562979615585891,0.0022068623230776328,0.5555555555555556,-0.00012422271847817485,0.0012708010930731679,boundary,c14,ring_share_5,14,2,2,False,84,True,False,False
c14_ring_share_7,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.001284198611125648,-0.0012752831261621045,0.0018664314205775244,0.25,-0.0018702851793047626,-0.0006839967837468777,reverse-stable,c14,ring_share_7,14,2,2,False,70,True,False,False
c14_ring_share_10,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.0012327936492796795,-0.0013240576880540502,0.0017864449282024224,0.25,-0.0018140592839380263,-0.0006309621403986607,reverse-stable,c14,ring_share_10,14,2,2,False,84,True,False,False
c14_ring_share_11,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.00039950640259105966,-0.0005746801213487174,0.002069315434022713,0.3333333333333333,-0.0010415078852062738,0.00028212538134742514,boundary,c14,ring_share_11,14,2,2,False,84,True,False,False

## Boundary Classification

criterion,supported,basis
c13_full_self_reproduces,True,c13 classification=full-stable
c12_reverse_reproduces,True,c12 classification=reverse-stable
c10_c14_boundary_reproduce,False,c10=boundary; c14=full-stable
topology_dependent_boundary_present,True,full=17; reverse=12; boundary=16
stable_full_topologies,True,c13|c14|c16|c10_side_broken|c10_ring_share_7|c12_side_broken|c13_reversed|c13_side_broken|c13_degree_null|c13_edge_count_null|c13_ring_share_5|c13_ring_share_7|c13_ring_share_10|c13_ring_share_11|c14_shuffled|c14_degree_null|c14_edge_count_null
stable_reverse_topologies,True,c8|c12|c10_degree_null|c12_reversed|c12_shuffled|c12_degree_null|c12_ring_share_5|c12_ring_share_7|c12_ring_share_10|c12_ring_share_11|c14_ring_share_7|c14_ring_share_10
boundary_topologies,True,c9|c10|c11|c15|c10_reversed|c10_shuffled|c10_edge_count_null|c10_ring_share_5|c10_ring_share_10|c10_ring_share_11|c12_edge_count_null|c13_shuffled|c14_reversed|c14_side_broken|c14_ring_share_5|c14_ring_share_11

## Event Geometry Summary

representation_arm,reverse_only_c_to_ab_top4,reverse_only_c_to_ab_top4_survivor_overlap,reverse_only_c_to_ab_survivor_strength_fraction,reverse_only_c_to_ab_phase_concentration,full_self_consistent_rstar_top4,full_self_consistent_rstar_top4_survivor_overlap,full_self_consistent_rstar_survivor_strength_fraction,full_self_consistent_rstar_phase_concentration,c_to_ab_receiver_only_top4,c_to_ab_receiver_only_top4_survivor_overlap,c_to_ab_receiver_only_survivor_strength_fraction,c_to_ab_receiver_only_phase_concentration,c_to_ab_magnitude_only_top4,c_to_ab_magnitude_only_top4_survivor_overlap,c_to_ab_magnitude_only_survivor_strength_fraction,c_to_ab_magnitude_only_phase_concentration,c_to_ab_standpoint_only_top4,c_to_ab_standpoint_only_top4_survivor_overlap,c_to_ab_standpoint_only_survivor_strength_fraction,c_to_ab_standpoint_only_phase_concentration
reverse_only_c_to_ab,P13|P20|P24|P25,0.0,0.1685045237897222,0.9892719713297378,,,,,,,,,,,,,,,,
full_self_consistent_rstar,,,,,P10|P13|P20|P25,1.0,0.17461867504757617,0.9877699551988811,,,,,,,,,,,,
c_to_ab_receiver_only,,,,,,,,,P13|P17|P20|P24,0.0,0.169646224942726,0.9917686476748779,,,,,,,,
c_to_ab_magnitude_only,,,,,,,,,,,,,P10|P13|P20|P25,1.0,0.17323897749676823,0.987982521185344,,,,
c_to_ab_standpoint_only,,,,,,,,,,,,,,,,,P10|P13|P20|P25,1.0,0.17323897749676823,0.987982521185344

## Readout Means

topology_arm,representation_arm,arm_family,n_nodes,n_directed_edges,topology_notes,mean_bounded_differentiated_recovery,sd_bounded_differentiated_recovery,n_runs,n_seed_events,base_topology,perturbation_kind,node_count_n,distance_from_12,signed_distance_from_12,is_odd,edge_count,is_ring_sharing,is_reversed,is_null
c10,c_to_ab_receiver_only,receiver_only,10,40,"C10(1,2) topology sweep",-0.0026316867464844323,0.0037016847697183657,36,132,c10,sweep,10,2,-2,False,40,False,False,False
c10,full_self_consistent_rstar,full_self_consistent,10,40,"C10(1,2) topology sweep",-0.004645945388917922,0.003470924075415277,36,132,c10,sweep,10,2,-2,False,40,False,False,False
c10,reverse_only_c_to_ab,reverse_only,10,40,"C10(1,2) topology sweep",-0.0047923825033816285,0.002738886067859046,36,132,c10,sweep,10,2,-2,False,40,False,False,False
c10,c_to_ab_magnitude_only,magnitude_only,10,40,"C10(1,2) topology sweep",-0.005863005410348588,0.002968254751826054,36,132,c10,sweep,10,2,-2,False,40,False,False,False
c10,c_to_ab_standpoint_only,standpoint_only,10,40,"C10(1,2) topology sweep",-0.005863005410348588,0.002968254751826054,36,132,c10,sweep,10,2,-2,False,40,False,False,False
c10_degree_null,reverse_only_c_to_ab,reverse_only,10,40,"C10(1,2) degree-matched null",-0.001509672065081696,0.003800762937088068,36,132,c10,degree_null,10,2,-2,False,40,False,False,True
c10_degree_null,c_to_ab_receiver_only,receiver_only,10,40,"C10(1,2) degree-matched null",-0.003558508436456356,0.0034251099462957887,36,132,c10,degree_null,10,2,-2,False,40,False,False,True
c10_degree_null,c_to_ab_magnitude_only,magnitude_only,10,40,"C10(1,2) degree-matched null",-0.0057654046186357945,0.002823493810469623,36,132,c10,degree_null,10,2,-2,False,40,False,False,True
c10_degree_null,c_to_ab_standpoint_only,standpoint_only,10,40,"C10(1,2) degree-matched null",-0.0057654046186357945,0.002823493810469623,36,132,c10,degree_null,10,2,-2,False,40,False,False,True
c10_degree_null,full_self_consistent_rstar,full_self_consistent,10,40,"C10(1,2) degree-matched null",-0.0067166109488192675,0.0030945024425150956,36,132,c10,degree_null,10,2,-2,False,40,False,False,True
c10_edge_count_null,c_to_ab_receiver_only,receiver_only,10,40,"C10(1,2) edge-count null",6.233371583474718e-05,0.0032257842481323473,36,132,c10,edge_count_null,10,2,-2,False,40,False,False,True
c10_edge_count_null,reverse_only_c_to_ab,reverse_only,10,40,"C10(1,2) edge-count null",-0.003430086405572465,0.004356042484999208,36,132,c10,edge_count_null,10,2,-2,False,40,False,False,True
c10_edge_count_null,c_to_ab_magnitude_only,magnitude_only,10,40,"C10(1,2) edge-count null",-0.00405359708888536,0.0026085865808572234,36,132,c10,edge_count_null,10,2,-2,False,40,False,False,True
c10_edge_count_null,c_to_ab_standpoint_only,standpoint_only,10,40,"C10(1,2) edge-count null",-0.00405359708888536,0.0026085865808572234,36,132,c10,edge_count_null,10,2,-2,False,40,False,False,True
c10_edge_count_null,full_self_consistent_rstar,full_self_consistent,10,40,"C10(1,2) edge-count null",-0.0041519190934879175,0.00254678483641619,36,132,c10,edge_count_null,10,2,-2,False,40,False,False,True
c10_reversed,c_to_ab_receiver_only,receiver_only,10,40,"C10(1,2) reversed",-0.003480714547843788,0.0038191878350683863,36,132,c10,reversed,10,2,-2,False,40,False,True,False
c10_reversed,reverse_only_c_to_ab,reverse_only,10,40,"C10(1,2) reversed",-0.00502080756458712,0.0029194705232130167,36,132,c10,reversed,10,2,-2,False,40,False,True,False
c10_reversed,full_self_consistent_rstar,full_self_consistent,10,40,"C10(1,2) reversed",-0.005182612906246788,0.00317710973704475,36,132,c10,reversed,10,2,-2,False,40,False,True,False
c10_reversed,c_to_ab_magnitude_only,magnitude_only,10,40,"C10(1,2) reversed",-0.0064963910083651625,0.0027459463642421746,36,132,c10,reversed,10,2,-2,False,40,False,True,False
c10_reversed,c_to_ab_standpoint_only,standpoint_only,10,40,"C10(1,2) reversed",-0.0064963910083651625,0.0027459463642421746,36,132,c10,reversed,10,2,-2,False,40,False,True,False
c10_ring_share_10,c_to_ab_receiver_only,receiver_only,10,40,"C10(1,2) ring-share plus 10",-0.0029836521738644275,0.00426960574513997,36,132,c10,ring_share_10,10,2,-2,False,40,True,False,False
c10_ring_share_10,full_self_consistent_rstar,full_self_consistent,10,40,"C10(1,2) ring-share plus 10",-0.004871295936240413,0.003003549671266099,36,132,c10,ring_share_10,10,2,-2,False,40,True,False,False
c10_ring_share_10,reverse_only_c_to_ab,reverse_only,10,40,"C10(1,2) ring-share plus 10",-0.0049769770616984125,0.0028861135633413016,36,132,c10,ring_share_10,10,2,-2,False,40,True,False,False
c10_ring_share_10,c_to_ab_magnitude_only,magnitude_only,10,40,"C10(1,2) ring-share plus 10",-0.006158635789239097,0.003224551117475843,36,132,c10,ring_share_10,10,2,-2,False,40,True,False,False
c10_ring_share_10,c_to_ab_standpoint_only,standpoint_only,10,40,"C10(1,2) ring-share plus 10",-0.006158635789239097,0.003224551117475843,36,132,c10,ring_share_10,10,2,-2,False,40,True,False,False
c10_ring_share_11,c_to_ab_receiver_only,receiver_only,10,40,"C10(1,2) ring-share plus 11",-0.002776770505259573,0.0029594417023699787,36,132,c10,ring_share_11,10,2,-2,False,40,True,False,False
c10_ring_share_11,full_self_consistent_rstar,full_self_consistent,10,40,"C10(1,2) ring-share plus 11",-0.0040157771876838085,0.0035527130515799637,36,132,c10,ring_share_11,10,2,-2,False,40,True,False,False
c10_ring_share_11,reverse_only_c_to_ab,reverse_only,10,40,"C10(1,2) ring-share plus 11",-0.004688315180205656,0.002723872543663364,36,132,c10,ring_share_11,10,2,-2,False,40,True,False,False
c10_ring_share_11,c_to_ab_magnitude_only,magnitude_only,10,40,"C10(1,2) ring-share plus 11",-0.007012804206500373,0.002488084583732938,36,132,c10,ring_share_11,10,2,-2,False,40,True,False,False
c10_ring_share_11,c_to_ab_standpoint_only,standpoint_only,10,40,"C10(1,2) ring-share plus 11",-0.007012804206500373,0.002488084583732938,36,132,c10,ring_share_11,10,2,-2,False,40,True,False,False
c10_ring_share_5,c_to_ab_receiver_only,receiver_only,10,50,"C10(1,2) ring-share plus 5",-0.003478311891446926,0.0029484508443192023,36,132,c10,ring_share_5,10,2,-2,False,50,True,False,False
c10_ring_share_5,full_self_consistent_rstar,full_self_consistent,10,50,"C10(1,2) ring-share plus 5",-0.0040828525154621665,0.0031154541566721272,36,132,c10,ring_share_5,10,2,-2,False,50,True,False,False
c10_ring_share_5,reverse_only_c_to_ab,reverse_only,10,50,"C10(1,2) ring-share plus 5",-0.004544404483760051,0.002767314497768089,36,132,c10,ring_share_5,10,2,-2,False,50,True,False,False
c10_ring_share_5,c_to_ab_magnitude_only,magnitude_only,10,50,"C10(1,2) ring-share plus 5",-0.007184376297343465,0.0026695070791481327,36,132,c10,ring_share_5,10,2,-2,False,50,True,False,False
c10_ring_share_5,c_to_ab_standpoint_only,standpoint_only,10,50,"C10(1,2) ring-share plus 5",-0.007184376297343465,0.0026695070791481327,36,132,c10,ring_share_5,10,2,-2,False,50,True,False,False
c10_ring_share_7,c_to_ab_receiver_only,receiver_only,10,60,"C10(1,2) ring-share plus 7",-0.0039343058641037425,0.0044533542339668915,36,132,c10,ring_share_7,10,2,-2,False,60,True,False,False
c10_ring_share_7,full_self_consistent_rstar,full_self_consistent,10,60,"C10(1,2) ring-share plus 7",-0.004676783279681941,0.0026394241767550984,36,132,c10,ring_share_7,10,2,-2,False,60,True,False,False
c10_ring_share_7,c_to_ab_magnitude_only,magnitude_only,10,60,"C10(1,2) ring-share plus 7",-0.006401816730461157,0.0019312073043704558,36,132,c10,ring_share_7,10,2,-2,False,60,True,False,False
c10_ring_share_7,c_to_ab_standpoint_only,standpoint_only,10,60,"C10(1,2) ring-share plus 7",-0.006401816730461157,0.0019312073043704558,36,132,c10,ring_share_7,10,2,-2,False,60,True,False,False
c10_ring_share_7,reverse_only_c_to_ab,reverse_only,10,60,"C10(1,2) ring-share plus 7",-0.006406201274758907,0.0026655673767468735,36,132,c10,ring_share_7,10,2,-2,False,60,True,False,False
c10_shuffled,c_to_ab_receiver_only,receiver_only,10,40,"C10(1,2) target-shuffled",0.00012050780033189322,0.0027895376366845535,36,132,c10,shuffled,10,2,-2,False,40,False,False,False
c10_shuffled,c_to_ab_magnitude_only,magnitude_only,10,40,"C10(1,2) target-shuffled",-0.002988821781163009,0.002479610650873769,36,132,c10,shuffled,10,2,-2,False,40,False,False,False
c10_shuffled,c_to_ab_standpoint_only,standpoint_only,10,40,"C10(1,2) target-shuffled",-0.002988821781163009,0.002479610650873769,36,132,c10,shuffled,10,2,-2,False,40,False,False,False
c10_shuffled,full_self_consistent_rstar,full_self_consistent,10,40,"C10(1,2) target-shuffled",-0.0044095772959071924,0.003158253496580335,36,132,c10,shuffled,10,2,-2,False,40,False,False,False
c10_shuffled,reverse_only_c_to_ab,reverse_only,10,40,"C10(1,2) target-shuffled",-0.004676386067273321,0.002563645052324591,36,132,c10,shuffled,10,2,-2,False,40,False,False,False
c10_side_broken,c_to_ab_magnitude_only,magnitude_only,10,40,"C10(1,2) degree-matched side-broken",0.001214136508161017,0.002520015925117754,36,132,c10,side_broken,10,2,-2,False,40,False,False,False
c10_side_broken,c_to_ab_standpoint_only,standpoint_only,10,40,"C10(1,2) degree-matched side-broken",0.001214136508161017,0.002520015925117754,36,132,c10,side_broken,10,2,-2,False,40,False,False,False
c10_side_broken,full_self_consistent_rstar,full_self_consistent,10,40,"C10(1,2) degree-matched side-broken",-0.00018109414153400007,0.0029966121725253114,36,132,c10,side_broken,10,2,-2,False,40,False,False,False
c10_side_broken,reverse_only_c_to_ab,reverse_only,10,40,"C10(1,2) degree-matched side-broken",-0.004293484864062846,0.002840175179761198,36,132,c10,side_broken,10,2,-2,False,40,False,False,False
c10_side_broken,c_to_ab_receiver_only,receiver_only,10,40,"C10(1,2) degree-matched side-broken",-0.00837447766003858,0.0019059794445062958,36,132,c10,side_broken,10,2,-2,False,40,False,False,False
c11,c_to_ab_receiver_only,receiver_only,11,44,"C11(1,2) topology sweep",-0.004375932508316343,0.004853469466830744,36,132,c11,sweep,11,1,-1,True,44,False,False,False
c11,c_to_ab_magnitude_only,magnitude_only,11,44,"C11(1,2) topology sweep",-0.0057913529024118445,0.0029839441865256457,36,132,c11,sweep,11,1,-1,True,44,False,False,False
c11,c_to_ab_standpoint_only,standpoint_only,11,44,"C11(1,2) topology sweep",-0.0057913529024118445,0.0029839441865256457,36,132,c11,sweep,11,1,-1,True,44,False,False,False
c11,full_self_consistent_rstar,full_self_consistent,11,44,"C11(1,2) topology sweep",-0.008121255622013596,0.0031903552194464486,36,132,c11,sweep,11,1,-1,True,44,False,False,False
c11,reverse_only_c_to_ab,reverse_only,11,44,"C11(1,2) topology sweep",-0.008136583783410664,0.003917969232125457,36,132,c11,sweep,11,1,-1,True,44,False,False,False
c12,c_to_ab_receiver_only,receiver_only,12,48,"C12(1,2) topology sweep",0.03508349103151967,0.0023531924601059603,36,132,c12,sweep,12,0,0,False,48,False,False,False
c12,reverse_only_c_to_ab,reverse_only,12,48,"C12(1,2) topology sweep",0.03219718918439085,0.0029700394892338946,36,132,c12,sweep,12,0,0,False,48,False,False,False
c12,full_self_consistent_rstar,full_self_consistent,12,48,"C12(1,2) topology sweep",0.027711389617211504,0.004019455194250662,36,132,c12,sweep,12,0,0,False,48,False,False,False
c12,c_to_ab_magnitude_only,magnitude_only,12,48,"C12(1,2) topology sweep",0.026176908323013004,0.004143902694994243,36,132,c12,sweep,12,0,0,False,48,False,False,False
c12,c_to_ab_standpoint_only,standpoint_only,12,48,"C12(1,2) topology sweep",0.026176908323013004,0.004143902694994243,36,132,c12,sweep,12,0,0,False,48,False,False,False
c12_degree_null,c_to_ab_receiver_only,receiver_only,12,48,"C12(1,2) degree-matched null",0.01466793632659719,0.00246578114963482,36,132,c12,degree_null,12,0,0,False,48,False,False,True
c12_degree_null,reverse_only_c_to_ab,reverse_only,12,48,"C12(1,2) degree-matched null",0.003017729098411739,0.0020274889396347685,36,132,c12,degree_null,12,0,0,False,48,False,False,True
c12_degree_null,c_to_ab_magnitude_only,magnitude_only,12,48,"C12(1,2) degree-matched null",0.0016225422697994077,0.002237533724263109,36,132,c12,degree_null,12,0,0,False,48,False,False,True
c12_degree_null,c_to_ab_standpoint_only,standpoint_only,12,48,"C12(1,2) degree-matched null",0.0016225422697994077,0.002237533724263109,36,132,c12,degree_null,12,0,0,False,48,False,False,True
c12_degree_null,full_self_consistent_rstar,full_self_consistent,12,48,"C12(1,2) degree-matched null",0.0008811245583526858,0.002624457464197216,36,132,c12,degree_null,12,0,0,False,48,False,False,True
c12_edge_count_null,c_to_ab_receiver_only,receiver_only,12,48,"C12(1,2) edge-count null",0.012504416085203404,0.0020447683096474563,36,132,c12,edge_count_null,12,0,0,False,48,False,False,True
c12_edge_count_null,c_to_ab_magnitude_only,magnitude_only,12,48,"C12(1,2) edge-count null",0.006572960733722488,0.0026827730118035016,36,132,c12,edge_count_null,12,0,0,False,48,False,False,True
c12_edge_count_null,c_to_ab_standpoint_only,standpoint_only,12,48,"C12(1,2) edge-count null",0.006572960733722488,0.0026827730118035016,36,132,c12,edge_count_null,12,0,0,False,48,False,False,True
c12_edge_count_null,full_self_consistent_rstar,full_self_consistent,12,48,"C12(1,2) edge-count null",0.00622190210060376,0.003144468459407259,36,132,c12,edge_count_null,12,0,0,False,48,False,False,True
c12_edge_count_null,reverse_only_c_to_ab,reverse_only,12,48,"C12(1,2) edge-count null",0.005577936626712295,0.0022879943011831685,36,132,c12,edge_count_null,12,0,0,False,48,False,False,True
c12_reversed,c_to_ab_receiver_only,receiver_only,12,48,"C12(1,2) reversed",0.03481858218697712,0.0026685046509857487,36,132,c12,reversed,12,0,0,False,48,False,True,False
c12_reversed,reverse_only_c_to_ab,reverse_only,12,48,"C12(1,2) reversed",0.031145023963863896,0.0029160510082873515,36,132,c12,reversed,12,0,0,False,48,False,True,False
c12_reversed,full_self_consistent_rstar,full_self_consistent,12,48,"C12(1,2) reversed",0.027376778779203147,0.004125781723920435,36,132,c12,reversed,12,0,0,False,48,False,True,False
c12_reversed,c_to_ab_magnitude_only,magnitude_only,12,48,"C12(1,2) reversed",0.025584994468356277,0.003455543954896341,36,132,c12,reversed,12,0,0,False,48,False,True,False
c12_reversed,c_to_ab_standpoint_only,standpoint_only,12,48,"C12(1,2) reversed",0.025584994468356277,0.003455543954896341,36,132,c12,reversed,12,0,0,False,48,False,True,False
c12_ring_share_10,c_to_ab_receiver_only,receiver_only,12,48,"C12(1,2) ring-share plus 10",0.03495778499386629,0.0023574621573912444,36,132,c12,ring_share_10,12,0,0,False,48,True,False,False
c12_ring_share_10,reverse_only_c_to_ab,reverse_only,12,48,"C12(1,2) ring-share plus 10",0.031087629816398097,0.0031040646372987772,36,132,c12,ring_share_10,12,0,0,False,48,True,False,False
c12_ring_share_10,full_self_consistent_rstar,full_self_consistent,12,48,"C12(1,2) ring-share plus 10",0.02783947933992412,0.003832936552364594,36,132,c12,ring_share_10,12,0,0,False,48,True,False,False
c12_ring_share_10,c_to_ab_magnitude_only,magnitude_only,12,48,"C12(1,2) ring-share plus 10",0.02620599292521473,0.0034921301279711254,36,132,c12,ring_share_10,12,0,0,False,48,True,False,False
c12_ring_share_10,c_to_ab_standpoint_only,standpoint_only,12,48,"C12(1,2) ring-share plus 10",0.02620599292521473,0.0034921301279711254,36,132,c12,ring_share_10,12,0,0,False,48,True,False,False
c12_ring_share_11,c_to_ab_receiver_only,receiver_only,12,48,"C12(1,2) ring-share plus 11",0.03538482098978861,0.0024864462737362045,36,132,c12,ring_share_11,12,0,0,False,48,True,False,False
c12_ring_share_11,reverse_only_c_to_ab,reverse_only,12,48,"C12(1,2) ring-share plus 11",0.03168470221153005,0.0022733372726165195,36,132,c12,ring_share_11,12,0,0,False,48,True,False,False
c12_ring_share_11,full_self_consistent_rstar,full_self_consistent,12,48,"C12(1,2) ring-share plus 11",0.028074345004856324,0.0034624890470499065,36,132,c12,ring_share_11,12,0,0,False,48,True,False,False
c12_ring_share_11,c_to_ab_magnitude_only,magnitude_only,12,48,"C12(1,2) ring-share plus 11",0.026436193534137474,0.003915981497493127,36,132,c12,ring_share_11,12,0,0,False,48,True,False,False
c12_ring_share_11,c_to_ab_standpoint_only,standpoint_only,12,48,"C12(1,2) ring-share plus 11",0.026436193534137474,0.003915981497493127,36,132,c12,ring_share_11,12,0,0,False,48,True,False,False
c12_ring_share_5,c_to_ab_receiver_only,receiver_only,12,72,"C12(1,2) ring-share plus 5",0.03503281281308579,0.0024572215517536865,36,132,c12,ring_share_5,12,0,0,False,72,True,False,False
c12_ring_share_5,reverse_only_c_to_ab,reverse_only,12,72,"C12(1,2) ring-share plus 5",0.0280950950588117,0.0027981215644469607,36,132,c12,ring_share_5,12,0,0,False,72,True,False,False
c12_ring_share_5,full_self_consistent_rstar,full_self_consistent,12,72,"C12(1,2) ring-share plus 5",0.022771096607817853,0.0031520860781190283,36,132,c12,ring_share_5,12,0,0,False,72,True,False,False
c12_ring_share_5,c_to_ab_magnitude_only,magnitude_only,12,72,"C12(1,2) ring-share plus 5",0.022466864369199712,0.0026543913614904104,36,132,c12,ring_share_5,12,0,0,False,72,True,False,False
c12_ring_share_5,c_to_ab_standpoint_only,standpoint_only,12,72,"C12(1,2) ring-share plus 5",0.022466864369199712,0.0026543913614904104,36,132,c12,ring_share_5,12,0,0,False,72,True,False,False
c12_ring_share_7,c_to_ab_receiver_only,receiver_only,12,72,"C12(1,2) ring-share plus 7",0.0350627490476534,0.0027932813176034907,36,132,c12,ring_share_7,12,0,0,False,72,True,False,False
c12_ring_share_7,reverse_only_c_to_ab,reverse_only,12,72,"C12(1,2) ring-share plus 7",0.02743425890482922,0.0034170436748877453,36,132,c12,ring_share_7,12,0,0,False,72,True,False,False
c12_ring_share_7,c_to_ab_magnitude_only,magnitude_only,12,72,"C12(1,2) ring-share plus 7",0.022683492269765265,0.0028598965536748293,36,132,c12,ring_share_7,12,0,0,False,72,True,False,False
c12_ring_share_7,c_to_ab_standpoint_only,standpoint_only,12,72,"C12(1,2) ring-share plus 7",0.022683492269765265,0.0028598965536748293,36,132,c12,ring_share_7,12,0,0,False,72,True,False,False
c12_ring_share_7,full_self_consistent_rstar,full_self_consistent,12,72,"C12(1,2) ring-share plus 7",0.022383065952577462,0.0035074048952877315,36,132,c12,ring_share_7,12,0,0,False,72,True,False,False
c12_shuffled,c_to_ab_receiver_only,receiver_only,12,48,"C12(1,2) target-shuffled",0.012323722388307902,0.002446873814435669,36,132,c12,shuffled,12,0,0,False,48,False,False,False
c12_shuffled,reverse_only_c_to_ab,reverse_only,12,48,"C12(1,2) target-shuffled",0.005395978959062602,0.0016979028452208864,36,132,c12,shuffled,12,0,0,False,48,False,False,False
c12_shuffled,full_self_consistent_rstar,full_self_consistent,12,48,"C12(1,2) target-shuffled",0.0025710364459936796,0.003065675822409922,36,132,c12,shuffled,12,0,0,False,48,False,False,False
c12_shuffled,c_to_ab_magnitude_only,magnitude_only,12,48,"C12(1,2) target-shuffled",0.001867123278756145,0.0023723827204872503,36,132,c12,shuffled,12,0,0,False,48,False,False,False
c12_shuffled,c_to_ab_standpoint_only,standpoint_only,12,48,"C12(1,2) target-shuffled",0.001867123278756145,0.0023723827204872503,36,132,c12,shuffled,12,0,0,False,48,False,False,False
c12_side_broken,full_self_consistent_rstar,full_self_consistent,12,48,"C12(1,2) degree-matched side-broken",0.0049613638555656425,0.0024861789609560685,36,132,c12,side_broken,12,0,0,False,48,False,False,False
c12_side_broken,c_to_ab_magnitude_only,magnitude_only,12,48,"C12(1,2) degree-matched side-broken",0.004938110524565579,0.0024882460217383866,36,132,c12,side_broken,12,0,0,False,48,False,False,False
c12_side_broken,c_to_ab_standpoint_only,standpoint_only,12,48,"C12(1,2) degree-matched side-broken",0.004938110524565579,0.0024882460217383866,36,132,c12,side_broken,12,0,0,False,48,False,False,False
c12_side_broken,c_to_ab_receiver_only,receiver_only,12,48,"C12(1,2) degree-matched side-broken",0.0014837373447195753,0.0023127142555022457,36,132,c12,side_broken,12,0,0,False,48,False,False,False
c12_side_broken,reverse_only_c_to_ab,reverse_only,12,48,"C12(1,2) degree-matched side-broken",0.0012668234692401474,0.0023988905697641056,36,132,c12,side_broken,12,0,0,False,48,False,False,False
c13,c_to_ab_magnitude_only,magnitude_only,13,52,"C13(1,2) topology sweep",-0.0003860780632995739,0.002276299269849288,36,132,c13,sweep,13,1,1,True,52,False,False,False
c13,c_to_ab_standpoint_only,standpoint_only,13,52,"C13(1,2) topology sweep",-0.0003860780632995739,0.002276299269849288,36,132,c13,sweep,13,1,1,True,52,False,False,False
c13,full_self_consistent_rstar,full_self_consistent,13,52,"C13(1,2) topology sweep",-0.0005652811855991685,0.002637312628423229,36,132,c13,sweep,13,1,1,True,52,False,False,False
c13,reverse_only_c_to_ab,reverse_only,13,52,"C13(1,2) topology sweep",-0.003212918745976132,0.0031972315453896154,36,132,c13,sweep,13,1,1,True,52,False,False,False
c13,c_to_ab_receiver_only,receiver_only,13,52,"C13(1,2) topology sweep",-0.00623187965802411,0.0022128649509919203,36,132,c13,sweep,13,1,1,True,52,False,False,False
c13_degree_null,c_to_ab_magnitude_only,magnitude_only,13,52,"C13(1,2) degree-matched null",0.0016948951205671002,0.002473732857938103,36,132,c13,degree_null,13,1,1,True,52,False,False,True
c13_degree_null,c_to_ab_standpoint_only,standpoint_only,13,52,"C13(1,2) degree-matched null",0.0016948951205671002,0.002473732857938103,36,132,c13,degree_null,13,1,1,True,52,False,False,True
c13_degree_null,full_self_consistent_rstar,full_self_consistent,13,52,"C13(1,2) degree-matched null",-0.001541071805373396,0.0026359898743685524,36,132,c13,degree_null,13,1,1,True,52,False,False,True
c13_degree_null,reverse_only_c_to_ab,reverse_only,13,52,"C13(1,2) degree-matched null",-0.005190239926782046,0.0036993535140850274,36,132,c13,degree_null,13,1,1,True,52,False,False,True
c13_degree_null,c_to_ab_receiver_only,receiver_only,13,52,"C13(1,2) degree-matched null",-0.006761979304321627,0.003981085599563764,36,132,c13,degree_null,13,1,1,True,52,False,False,True
c13_edge_count_null,full_self_consistent_rstar,full_self_consistent,13,52,"C13(1,2) edge-count null",-0.0002473401933613969,0.003069944460269897,36,132,c13,edge_count_null,13,1,1,True,52,False,False,True
c13_edge_count_null,reverse_only_c_to_ab,reverse_only,13,52,"C13(1,2) edge-count null",-0.00104168699355403,0.002823699755937778,36,132,c13,edge_count_null,13,1,1,True,52,False,False,True
c13_edge_count_null,c_to_ab_magnitude_only,magnitude_only,13,52,"C13(1,2) edge-count null",-0.0012071128924794115,0.0027563375959276685,36,132,c13,edge_count_null,13,1,1,True,52,False,False,True
c13_edge_count_null,c_to_ab_standpoint_only,standpoint_only,13,52,"C13(1,2) edge-count null",-0.0012071128924794115,0.0027563375959276685,36,132,c13,edge_count_null,13,1,1,True,52,False,False,True
c13_edge_count_null,c_to_ab_receiver_only,receiver_only,13,52,"C13(1,2) edge-count null",-0.0025988106311161,0.0020852601549539453,36,132,c13,edge_count_null,13,1,1,True,52,False,False,True
c13_reversed,c_to_ab_magnitude_only,magnitude_only,13,52,"C13(1,2) reversed",-0.00046925456910804227,0.0023400197072082655,36,132,c13,reversed,13,1,1,True,52,False,True,False
c13_reversed,c_to_ab_standpoint_only,standpoint_only,13,52,"C13(1,2) reversed",-0.00046925456910804227,0.0023400197072082655,36,132,c13,reversed,13,1,1,True,52,False,True,False
c13_reversed,full_self_consistent_rstar,full_self_consistent,13,52,"C13(1,2) reversed",-0.0006753693982239244,0.0019264450641182987,36,132,c13,reversed,13,1,1,True,52,False,True,False
c13_reversed,reverse_only_c_to_ab,reverse_only,13,52,"C13(1,2) reversed",-0.0028181942174037764,0.002401761813024137,36,132,c13,reversed,13,1,1,True,52,False,True,False
c13_reversed,c_to_ab_receiver_only,receiver_only,13,52,"C13(1,2) reversed",-0.006870556719849674,0.0020624501646979102,36,132,c13,reversed,13,1,1,True,52,False,True,False
c13_ring_share_10,full_self_consistent_rstar,full_self_consistent,13,78,"C13(1,2) ring-share plus 10",-0.00020026271891250972,0.0029463743351707725,36,132,c13,ring_share_10,13,1,1,True,78,True,False,False
c13_ring_share_10,c_to_ab_magnitude_only,magnitude_only,13,78,"C13(1,2) ring-share plus 10",-0.0013626652790588905,0.002812375326215307,36,132,c13,ring_share_10,13,1,1,True,78,True,False,False
c13_ring_share_10,c_to_ab_standpoint_only,standpoint_only,13,78,"C13(1,2) ring-share plus 10",-0.0013626652790588905,0.002812375326215307,36,132,c13,ring_share_10,13,1,1,True,78,True,False,False
c13_ring_share_10,reverse_only_c_to_ab,reverse_only,13,78,"C13(1,2) ring-share plus 10",-0.00265674538456162,0.003474603545155414,36,132,c13,ring_share_10,13,1,1,True,78,True,False,False
c13_ring_share_10,c_to_ab_receiver_only,receiver_only,13,78,"C13(1,2) ring-share plus 10",-0.006669597346031345,0.0030679895987103245,36,132,c13,ring_share_10,13,1,1,True,78,True,False,False
c13_ring_share_11,full_self_consistent_rstar,full_self_consistent,13,52,"C13(1,2) ring-share plus 11",-0.0003213088532453187,0.002572179756309239,36,132,c13,ring_share_11,13,1,1,True,52,True,False,False
c13_ring_share_11,c_to_ab_magnitude_only,magnitude_only,13,52,"C13(1,2) ring-share plus 11",-0.0006584922224795981,0.0021594373094245664,36,132,c13,ring_share_11,13,1,1,True,52,True,False,False
c13_ring_share_11,c_to_ab_standpoint_only,standpoint_only,13,52,"C13(1,2) ring-share plus 11",-0.0006584922224795981,0.0021594373094245664,36,132,c13,ring_share_11,13,1,1,True,52,True,False,False
c13_ring_share_11,reverse_only_c_to_ab,reverse_only,13,52,"C13(1,2) ring-share plus 11",-0.0028473281595201108,0.003222054662448408,36,132,c13,ring_share_11,13,1,1,True,52,True,False,False
c13_ring_share_11,c_to_ab_receiver_only,receiver_only,13,52,"C13(1,2) ring-share plus 11",-0.006125224471901419,0.0017528029898852794,36,132,c13,ring_share_11,13,1,1,True,52,True,False,False
c13_ring_share_5,full_self_consistent_rstar,full_self_consistent,13,78,"C13(1,2) ring-share plus 5",-0.0024954167316145154,0.0030951201471828096,36,132,c13,ring_share_5,13,1,1,True,78,True,False,False
c13_ring_share_5,c_to_ab_magnitude_only,magnitude_only,13,78,"C13(1,2) ring-share plus 5",-0.0039220564936381895,0.002922151423137412,36,132,c13,ring_share_5,13,1,1,True,78,True,False,False
c13_ring_share_5,c_to_ab_standpoint_only,standpoint_only,13,78,"C13(1,2) ring-share plus 5",-0.0039220564936381895,0.002922151423137412,36,132,c13,ring_share_5,13,1,1,True,78,True,False,False
c13_ring_share_5,reverse_only_c_to_ab,reverse_only,13,78,"C13(1,2) ring-share plus 5",-0.0047222009275668,0.0031476936072578187,36,132,c13,ring_share_5,13,1,1,True,78,True,False,False
c13_ring_share_5,c_to_ab_receiver_only,receiver_only,13,78,"C13(1,2) ring-share plus 5",-0.00794901121120462,0.0026261540637932492,36,132,c13,ring_share_5,13,1,1,True,78,True,False,False
c13_ring_share_7,full_self_consistent_rstar,full_self_consistent,13,78,"C13(1,2) ring-share plus 7",-0.001480759282133566,0.0025699445760244944,36,132,c13,ring_share_7,13,1,1,True,78,True,False,False
c13_ring_share_7,c_to_ab_magnitude_only,magnitude_only,13,78,"C13(1,2) ring-share plus 7",-0.002288093492161525,0.002170945190481959,36,132,c13,ring_share_7,13,1,1,True,78,True,False,False
c13_ring_share_7,c_to_ab_standpoint_only,standpoint_only,13,78,"C13(1,2) ring-share plus 7",-0.002288093492161525,0.002170945190481959,36,132,c13,ring_share_7,13,1,1,True,78,True,False,False
c13_ring_share_7,reverse_only_c_to_ab,reverse_only,13,78,"C13(1,2) ring-share plus 7",-0.003887627585610972,0.002825848290515525,36,132,c13,ring_share_7,13,1,1,True,78,True,False,False
c13_ring_share_7,c_to_ab_receiver_only,receiver_only,13,78,"C13(1,2) ring-share plus 7",-0.006837938658430747,0.002523543964864695,36,132,c13,ring_share_7,13,1,1,True,78,True,False,False
c13_shuffled,full_self_consistent_rstar,full_self_consistent,13,52,"C13(1,2) target-shuffled",0.0028380920283913986,0.00314744291277462,36,132,c13,shuffled,13,1,1,True,52,False,False,False
c13_shuffled,reverse_only_c_to_ab,reverse_only,13,52,"C13(1,2) target-shuffled",0.002453125340881761,0.0025838721304825493,36,132,c13,shuffled,13,1,1,True,52,False,False,False
c13_shuffled,c_to_ab_magnitude_only,magnitude_only,13,52,"C13(1,2) target-shuffled",0.0004273899307572385,0.0028185120186853536,36,132,c13,shuffled,13,1,1,True,52,False,False,False
c13_shuffled,c_to_ab_standpoint_only,standpoint_only,13,52,"C13(1,2) target-shuffled",0.0004273899307572385,0.0028185120186853536,36,132,c13,shuffled,13,1,1,True,52,False,False,False
c13_shuffled,c_to_ab_receiver_only,receiver_only,13,52,"C13(1,2) target-shuffled",-0.0037014040331463114,0.002958843064906139,36,132,c13,shuffled,13,1,1,True,52,False,False,False
c13_side_broken,full_self_consistent_rstar,full_self_consistent,13,52,"C13(1,2) degree-matched side-broken",0.0032797814389058846,0.002183772782458345,36,132,c13,side_broken,13,1,1,True,52,False,False,False
c13_side_broken,c_to_ab_magnitude_only,magnitude_only,13,52,"C13(1,2) degree-matched side-broken",-8.045150057073347e-05,0.0023301381998348854,36,132,c13,side_broken,13,1,1,True,52,False,False,False
c13_side_broken,c_to_ab_standpoint_only,standpoint_only,13,52,"C13(1,2) degree-matched side-broken",-8.045150057073347e-05,0.0023301381998348854,36,132,c13,side_broken,13,1,1,True,52,False,False,False
c13_side_broken,reverse_only_c_to_ab,reverse_only,13,52,"C13(1,2) degree-matched side-broken",-0.0005429776216156169,0.002394012148032773,36,132,c13,side_broken,13,1,1,True,52,False,False,False
c13_side_broken,c_to_ab_receiver_only,receiver_only,13,52,"C13(1,2) degree-matched side-broken",-0.008283063890834892,0.0030407325565651065,36,132,c13,side_broken,13,1,1,True,52,False,False,False
c14,c_to_ab_magnitude_only,magnitude_only,14,56,"C14(1,2) topology sweep",-0.001304297210207596,0.0021432767583039326,36,132,c14,sweep,14,2,2,False,56,False,False,False
c14,c_to_ab_standpoint_only,standpoint_only,14,56,"C14(1,2) topology sweep",-0.001304297210207596,0.0021432767583039326,36,132,c14,sweep,14,2,2,False,56,False,False,False
c14,full_self_consistent_rstar,full_self_consistent,14,56,"C14(1,2) topology sweep",-0.002498785598919936,0.0023123989261128047,36,132,c14,sweep,14,2,2,False,56,False,False,False
c14,reverse_only_c_to_ab,reverse_only,14,56,"C14(1,2) topology sweep",-0.0031560696431712763,0.0020193694026831477,36,132,c14,sweep,14,2,2,False,56,False,False,False
c14,c_to_ab_receiver_only,receiver_only,14,56,"C14(1,2) topology sweep",-0.005020481353255578,0.002693622606435136,36,132,c14,sweep,14,2,2,False,56,False,False,False
c14_degree_null,full_self_consistent_rstar,full_self_consistent,14,56,"C14(1,2) degree-matched null",0.001987857890293131,0.002642180168350379,36,132,c14,degree_null,14,2,2,False,56,False,False,True
c14_degree_null,c_to_ab_magnitude_only,magnitude_only,14,56,"C14(1,2) degree-matched null",0.001697601593256078,0.002273480807399536,36,132,c14,degree_null,14,2,2,False,56,False,False,True
c14_degree_null,c_to_ab_standpoint_only,standpoint_only,14,56,"C14(1,2) degree-matched null",0.001697601593256078,0.002273480807399536,36,132,c14,degree_null,14,2,2,False,56,False,False,True
c14_degree_null,reverse_only_c_to_ab,reverse_only,14,56,"C14(1,2) degree-matched null",-0.002747578633451162,0.0023736806566531073,36,132,c14,degree_null,14,2,2,False,56,False,False,True
c14_degree_null,c_to_ab_receiver_only,receiver_only,14,56,"C14(1,2) degree-matched null",-0.004223943618247303,0.0024432456755920824,36,132,c14,degree_null,14,2,2,False,56,False,False,True
c14_edge_count_null,full_self_consistent_rstar,full_self_consistent,14,56,"C14(1,2) edge-count null",-0.002044311166003345,0.0026770836874036555,36,132,c14,edge_count_null,14,2,2,False,56,False,False,True
c14_edge_count_null,c_to_ab_magnitude_only,magnitude_only,14,56,"C14(1,2) edge-count null",-0.002117724488709444,0.0025785538074330505,36,132,c14,edge_count_null,14,2,2,False,56,False,False,True
c14_edge_count_null,c_to_ab_standpoint_only,standpoint_only,14,56,"C14(1,2) edge-count null",-0.002117724488709444,0.0025785538074330505,36,132,c14,edge_count_null,14,2,2,False,56,False,False,True
c14_edge_count_null,reverse_only_c_to_ab,reverse_only,14,56,"C14(1,2) edge-count null",-0.005835268612226938,0.0028718769881314926,36,132,c14,edge_count_null,14,2,2,False,56,False,False,True
c14_edge_count_null,c_to_ab_receiver_only,receiver_only,14,56,"C14(1,2) edge-count null",-0.005961217280178415,0.0022899941103743486,36,132,c14,edge_count_null,14,2,2,False,56,False,False,True
c14_reversed,c_to_ab_magnitude_only,magnitude_only,14,56,"C14(1,2) reversed",-0.001761778364150276,0.001854507980982605,36,132,c14,reversed,14,2,2,False,56,False,True,False
c14_reversed,c_to_ab_standpoint_only,standpoint_only,14,56,"C14(1,2) reversed",-0.001761778364150276,0.001854507980982605,36,132,c14,reversed,14,2,2,False,56,False,True,False
c14_reversed,reverse_only_c_to_ab,reverse_only,14,56,"C14(1,2) reversed",-0.0030954067792784323,0.0020250787801660026,36,132,c14,reversed,14,2,2,False,56,False,True,False
c14_reversed,full_self_consistent_rstar,full_self_consistent,14,56,"C14(1,2) reversed",-0.003219315280880641,0.002094385277918554,36,132,c14,reversed,14,2,2,False,56,False,True,False
c14_reversed,c_to_ab_receiver_only,receiver_only,14,56,"C14(1,2) reversed",-0.005158283410984216,0.002222717505263882,36,132,c14,reversed,14,2,2,False,56,False,True,False
c14_ring_share_10,reverse_only_c_to_ab,reverse_only,14,84,"C14(1,2) ring-share plus 10",-0.00163636652677902,0.0019730374020736382,36,132,c14,ring_share_10,14,2,2,False,84,True,False,False
c14_ring_share_10,c_to_ab_magnitude_only,magnitude_only,14,84,"C14(1,2) ring-share plus 10",-0.002839170649367743,0.0019077760202653056,36,132,c14,ring_share_10,14,2,2,False,84,True,False,False
c14_ring_share_10,c_to_ab_standpoint_only,standpoint_only,14,84,"C14(1,2) ring-share plus 10",-0.002839170649367743,0.0019077760202653056,36,132,c14,ring_share_10,14,2,2,False,84,True,False,False
c14_ring_share_10,full_self_consistent_rstar,full_self_consistent,14,84,"C14(1,2) ring-share plus 10",-0.0028691601760586992,0.0021185317499015097,36,132,c14,ring_share_10,14,2,2,False,84,True,False,False
c14_ring_share_10,c_to_ab_receiver_only,receiver_only,14,84,"C14(1,2) ring-share plus 10",-0.004605332059746689,0.002349207633858687,36,132,c14,ring_share_10,14,2,2,False,84,True,False,False
c14_ring_share_11,c_to_ab_magnitude_only,magnitude_only,14,84,"C14(1,2) ring-share plus 11",-0.0023642245782180375,0.0018579136761193674,36,132,c14,ring_share_11,14,2,2,False,84,True,False,False
c14_ring_share_11,c_to_ab_standpoint_only,standpoint_only,14,84,"C14(1,2) ring-share plus 11",-0.0023642245782180375,0.0018579136761193674,36,132,c14,ring_share_11,14,2,2,False,84,True,False,False
c14_ring_share_11,reverse_only_c_to_ab,reverse_only,14,84,"C14(1,2) ring-share plus 11",-0.0024926462623986513,0.0017075646947816321,36,132,c14,ring_share_11,14,2,2,False,84,True,False,False
c14_ring_share_11,full_self_consistent_rstar,full_self_consistent,14,84,"C14(1,2) ring-share plus 11",-0.002892152664989711,0.0019793408759084937,36,132,c14,ring_share_11,14,2,2,False,84,True,False,False
c14_ring_share_11,c_to_ab_receiver_only,receiver_only,14,84,"C14(1,2) ring-share plus 11",-0.0051038961541943146,0.002251419042150088,36,132,c14,ring_share_11,14,2,2,False,84,True,False,False
c14_ring_share_5,full_self_consistent_rstar,full_self_consistent,14,84,"C14(1,2) ring-share plus 5",-0.0007495398350797053,0.002485531172083146,36,132,c14,ring_share_5,14,2,2,False,84,True,False,False
c14_ring_share_5,reverse_only_c_to_ab,reverse_only,14,84,"C14(1,2) ring-share plus 5",-0.001302864601318214,0.0023132929511143164,36,132,c14,ring_share_5,14,2,2,False,84,True,False,False
c14_ring_share_5,c_to_ab_magnitude_only,magnitude_only,14,84,"C14(1,2) ring-share plus 5",-0.001452156558668702,0.0022413491432860914,36,132,c14,ring_share_5,14,2,2,False,84,True,False,False
c14_ring_share_5,c_to_ab_standpoint_only,standpoint_only,14,84,"C14(1,2) ring-share plus 5",-0.001452156558668702,0.0022413491432860914,36,132,c14,ring_share_5,14,2,2,False,84,True,False,False
c14_ring_share_5,c_to_ab_receiver_only,receiver_only,14,84,"C14(1,2) ring-share plus 5",-0.0051761270807555776,0.0026027448625825294,36,132,c14,ring_share_5,14,2,2,False,84,True,False,False
c14_ring_share_7,reverse_only_c_to_ab,reverse_only,14,70,"C14(1,2) ring-share plus 7",-0.0023843106246068373,0.002245526779537888,36,132,c14,ring_share_7,14,2,2,False,70,True,False,False
c14_ring_share_7,c_to_ab_magnitude_only,magnitude_only,14,70,"C14(1,2) ring-share plus 7",-0.0031484619783494895,0.002176417980842954,36,132,c14,ring_share_7,14,2,2,False,70,True,False,False
c14_ring_share_7,c_to_ab_standpoint_only,standpoint_only,14,70,"C14(1,2) ring-share plus 7",-0.0031484619783494895,0.002176417980842954,36,132,c14,ring_share_7,14,2,2,False,70,True,False,False
c14_ring_share_7,full_self_consistent_rstar,full_self_consistent,14,70,"C14(1,2) ring-share plus 7",-0.0036685092357324847,0.002543340479756626,36,132,c14,ring_share_7,14,2,2,False,70,True,False,False
c14_ring_share_7,c_to_ab_receiver_only,receiver_only,14,70,"C14(1,2) ring-share plus 7",-0.004656138374997998,0.0029313475955466683,36,132,c14,ring_share_7,14,2,2,False,70,True,False,False
c14_shuffled,full_self_consistent_rstar,full_self_consistent,14,56,"C14(1,2) target-shuffled",0.0007710566708031135,0.002670227852695347,36,132,c14,shuffled,14,2,2,False,56,False,False,False
c14_shuffled,c_to_ab_magnitude_only,magnitude_only,14,56,"C14(1,2) target-shuffled",1.5710650020281924e-05,0.0021729427066072174,36,132,c14,shuffled,14,2,2,False,56,False,False,False
c14_shuffled,c_to_ab_standpoint_only,standpoint_only,14,56,"C14(1,2) target-shuffled",1.5710650020281924e-05,0.0021729427066072174,36,132,c14,shuffled,14,2,2,False,56,False,False,False
c14_shuffled,reverse_only_c_to_ab,reverse_only,14,56,"C14(1,2) target-shuffled",-0.0023806077006553886,0.002535891001679066,36,132,c14,shuffled,14,2,2,False,56,False,False,False
c14_shuffled,c_to_ab_receiver_only,receiver_only,14,56,"C14(1,2) target-shuffled",-0.006714260333864038,0.0027777013697279414,36,132,c14,shuffled,14,2,2,False,56,False,False,False
c14_side_broken,c_to_ab_receiver_only,receiver_only,14,56,"C14(1,2) degree-matched side-broken",0.000826081269684547,0.0026517400997152383,36,132,c14,side_broken,14,2,2,False,56,False,False,False
c14_side_broken,c_to_ab_magnitude_only,magnitude_only,14,56,"C14(1,2) degree-matched side-broken",-0.0015131165146317939,0.002017206114247986,36,132,c14,side_broken,14,2,2,False,56,False,False,False
c14_side_broken,c_to_ab_standpoint_only,standpoint_only,14,56,"C14(1,2) degree-matched side-broken",-0.0015131165146317939,0.002017206114247986,36,132,c14,side_broken,14,2,2,False,56,False,False,False
c14_side_broken,full_self_consistent_rstar,full_self_consistent,14,56,"C14(1,2) degree-matched side-broken",-0.0028678887246103746,0.0030849214962272607,36,132,c14,side_broken,14,2,2,False,56,False,False,False
c14_side_broken,reverse_only_c_to_ab,reverse_only,14,56,"C14(1,2) degree-matched side-broken",-0.003600165218388181,0.002836036496707924,36,132,c14,side_broken,14,2,2,False,56,False,False,False
c15,c_to_ab_receiver_only,receiver_only,15,60,"C15(1,2) topology sweep",-0.0008215313887230039,0.002009202531120953,36,132,c15,sweep,15,3,3,True,60,False,False,False
c15,c_to_ab_magnitude_only,magnitude_only,15,60,"C15(1,2) topology sweep",-0.0013002832445095148,0.002185049594752208,36,132,c15,sweep,15,3,3,True,60,False,False,False
c15,c_to_ab_standpoint_only,standpoint_only,15,60,"C15(1,2) topology sweep",-0.0013002832445095148,0.002185049594752208,36,132,c15,sweep,15,3,3,True,60,False,False,False
c15,reverse_only_c_to_ab,reverse_only,15,60,"C15(1,2) topology sweep",-0.001847562139046831,0.0022165230193615525,36,132,c15,sweep,15,3,3,True,60,False,False,False
c15,full_self_consistent_rstar,full_self_consistent,15,60,"C15(1,2) topology sweep",-0.0022384960047852343,0.002602135844592748,36,132,c15,sweep,15,3,3,True,60,False,False,False
c16,c_to_ab_magnitude_only,magnitude_only,16,64,"C16(1,2) topology sweep",-0.00037851527840686945,0.001725533203850919,36,132,c16,sweep,16,4,4,False,64,False,False,False
c16,c_to_ab_standpoint_only,standpoint_only,16,64,"C16(1,2) topology sweep",-0.00037851527840686945,0.001725533203850919,36,132,c16,sweep,16,4,4,False,64,False,False,False
c16,c_to_ab_receiver_only,receiver_only,16,64,"C16(1,2) topology sweep",-0.0014934399417064926,0.0022814448990046954,36,132,c16,sweep,16,4,4,False,64,False,False,False
c16,full_self_consistent_rstar,full_self_consistent,16,64,"C16(1,2) topology sweep",-0.0018055106262902937,0.002115718023203925,36,132,c16,sweep,16,4,4,False,64,False,False,False
c16,reverse_only_c_to_ab,reverse_only,16,64,"C16(1,2) topology sweep",-0.00271715599964862,0.0020164440900538655,36,132,c16,sweep,16,4,4,False,64,False,False,False
c8,c_to_ab_receiver_only,receiver_only,8,32,"C8(1,2) topology sweep",0.025241519764627143,0.004337163840629678,36,132,c8,sweep,8,4,-4,False,32,False,False,False
c8,reverse_only_c_to_ab,reverse_only,8,32,"C8(1,2) topology sweep",0.020511136598944428,0.005818956381035643,36,132,c8,sweep,8,4,-4,False,32,False,False,False
c8,full_self_consistent_rstar,full_self_consistent,8,32,"C8(1,2) topology sweep",0.015803599442451886,0.005490719782415021,36,132,c8,sweep,8,4,-4,False,32,False,False,False
c8,c_to_ab_magnitude_only,magnitude_only,8,32,"C8(1,2) topology sweep",0.01426392466954549,0.006146177479073515,36,132,c8,sweep,8,4,-4,False,32,False,False,False
c8,c_to_ab_standpoint_only,standpoint_only,8,32,"C8(1,2) topology sweep",0.01426392466954549,0.006146177479073515,36,132,c8,sweep,8,4,-4,False,32,False,False,False
c9,c_to_ab_receiver_only,receiver_only,9,36,"C9(1,2) topology sweep",-0.0001048846759120338,0.0026889468594409912,36,132,c9,sweep,9,3,-3,True,36,False,False,False
c9,reverse_only_c_to_ab,reverse_only,9,36,"C9(1,2) topology sweep",-0.0006612569839876349,0.0029459656141976116,36,132,c9,sweep,9,3,-3,True,36,False,False,False
c9,full_self_consistent_rstar,full_self_consistent,9,36,"C9(1,2) topology sweep",-0.0008172588060351217,0.0033400717180704855,36,132,c9,sweep,9,3,-3,True,36,False,False,False
c9,c_to_ab_magnitude_only,magnitude_only,9,36,"C9(1,2) topology sweep",-0.0013929442279614643,0.003272045453444779,36,132,c9,sweep,9,3,-3,True,36,False,False,False
c9,c_to_ab_standpoint_only,standpoint_only,9,36,"C9(1,2) topology sweep",-0.0013929442279614643,0.003272045453444779,36,132,c9,sweep,9,3,-3,True,36,False,False,False

## Decision Boundary

- Strong support requires C13 full-self advantage, C12 reverse advantage, C10/C14 boundary behavior, and topology-dependent classification to reproduce.
- Intermediate support means flips appear but are not cleanly explained by N, ring-sharing, or receiver geometry.
- Negative support means C13 or C10/C14 classifications collapse under rerun.
- Fractional signatures remain secondary diagnostics, not explanations.

## Settings

- event_quantile: 0.75
- steps: 240
- n_runs: 36
- n_boot: 2000
- seed: 75575
