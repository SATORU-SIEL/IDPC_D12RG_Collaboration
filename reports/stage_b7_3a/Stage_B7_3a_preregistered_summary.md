# Stage B7.3a C12 Specificity and H24 Collective-Necessity Audit

Status: executed after Stage_B7_3a_preregistration.md.

Primary R_star: `receiver_standpoint_magnitude_c`.

Scope note: the H24 arms test the current operational edge-level factorisation-suite / junction-coupling structure. Luke's later node-delay, edge-length, and state-dependent-drive requirements are not included because deterministic preregisterable rules are not yet frozen.

## Primary Classification

criterion,supported,basis
c12_specificity_supported,True,"receiver_standpoint_magnitude_c + c12_1_2 beats no-topology, reversed, side-broken, shuffled, C10/C11/C13/C14 and passes topology-family FDR"
c12_reconnection_without_specificity,False,C12 improves over no-topology but fails at least one specificity control
c12_directionality_supported,True,c12_1_2 exceeds c12_reversed for frozen R_star
c12_directionality_not_isolated,False,c12_reversed is equal or stronger than c12_1_2 for frozen R_star
neighboring_cycle_explains_effect,False,at least one C10/C11/C13/C14 neighbouring cycle equals or exceeds C12 for frozen R_star
side_correspondence_required,True,c12_1_2 exceeds c12_side_broken for frozen R_star
endpoint_o1o2_reclaims_upper_bound,False,endpoint best 0.028595; endpoint-free best 0.030976
scalar_c_rejected,True,scalar_c does not produce a significant C12 reconnection over controls
unresolved_c12_specificity,False,frozen R_star C12 specificity was not established under the full B7.3a control set
h24_collective_necessity_supported,False,"complete suite beats no-topology, removal, broken-junction, disconnected, and degree-null controls"
h24_possible_only_sufficient,False,possible/static 168 arm is equal or stronger than complete-suite-coupled arm
h24_available_but_not_required,True,removal or broken-junction controls did not degrade relative to complete-suite-coupled arm
h24_junction_coupling_required,False,complete-suite-coupled exceeds one-junction-family-broken control
h24_factorisation_removal_degrades,False,complete-suite-coupled exceeds one-factorisation-class-removed control
h24_restoration_recovers,False,restoring the complete operational suite improves over both removal and broken-junction controls
h24_static_topology_not_sufficient,True,current operational H24 edge-level suite did not satisfy collective necessity
h24_168_current_carrier_not_supported,True,current edge-level H24 carrier failed the collective-necessity rule
h24_216_diagnostic_only,True,216-edge C8-stitched object is retained only as a derived diagnostic arm
unresolved_h24_boundary,True,H24 collective necessity remains unresolved under the current operational edge-level implementation

## Top Results

c_representation,topology_arm,n_nodes,n_directed_edges,n_seed_events,mean_bounded_differentiated_recovery,effect_vs_no_topology_baseline,effect_vs_time_shifted,effect_vs_random_event,p_vs_time_shifted_and_random
receiver_only_c,c12_1_2,12,48,132,0.03097648517275391,0.002822698672301043,0.014933044867801032,0.008351348292571815,0.006211180124223602
endpoint_o1o2_reference,no_topology_baseline,12,0,131,0.028594890030371422,0.0,0.013898627169309638,0.0035127900658632784,0.043478260869565216
endpoint_o1o2_reference,c12_1_2,12,48,131,0.02857803147068212,-1.6858559689303387e-05,0.01149651403334253,0.016258306379611953,0.006211180124223602
receiver_standpoint_magnitude_c,c12_1_2,12,48,132,0.028442721492044402,0.0051389162478432115,0.013522100551380374,0.016138411501976962,0.006211180124223602
receiver_only_c,no_topology_baseline,12,0,132,0.028153786500452867,0.0,0.017184438257947302,0.009862802784343896,0.006211180124223602
receiver_standpoint_magnitude_c,c12_reversed,12,48,132,0.028151540561902756,0.004847735317701565,0.013009873682376955,0.006532698512515839,0.006211180124223602
receiver_magnitude_c,c12_1_2,12,48,132,0.02713762441747224,0.0024546242795700675,0.0115333211855905,0.009439787902125407,0.006211180124223602
directed_c,c12_1_2,12,48,132,0.02711904568259562,0.00250203243566878,0.010333846932715433,0.001334777239485871,0.18633540372670807
standpoint_inversion_c,c12_1_2,12,48,132,0.02640682222294975,0.003629486425953437,0.01101337292107559,0.0056343868052733115,0.018633540372670808
receiver_magnitude_c,no_topology_baseline,12,0,132,0.024683000137902172,0.0,0.013057050837209986,0.0031463832932316672,0.049689440993788817
directed_c,no_topology_baseline,12,0,132,0.02461701324692684,0.0,0.01130341314270051,0.004576865536827471,0.006211180124223602
receiver_standpoint_magnitude_c,no_topology_baseline,12,0,132,0.02330380524420119,0.0,0.01249816668032968,0.006922066314414818,0.006211180124223602
standpoint_inversion_c,no_topology_baseline,12,0,132,0.022777335796996312,0.0,0.011046299225451108,0.0019769242331384752,0.14285714285714285
scalar_c,c12_1_2,12,48,134,0.018092920991618477,0.00041572199766839665,0.0012401389921663855,0.0020635742606914705,0.2422360248447205
scalar_c,no_topology_baseline,12,0,134,0.01767719899395008,0.0,-0.0032982186255017323,0.0011270567482662454,0.5962732919254659
receiver_standpoint_magnitude_c,topology_capacity_matched_null,12,48,132,0.0016272299749381645,-0.021676575269263025,-0.00042574482295227667,-0.0015390833801936037,0.639751552795031
receiver_standpoint_magnitude_c,c12_side_broken,12,48,132,0.0010879374309797113,-0.02221586781322148,-0.003427023916965161,0.002972199155335054,0.4968944099378882
receiver_standpoint_magnitude_c,c12_shuffled,12,48,132,0.0008731807189205755,-0.022430624525280614,-4.039364740772292e-05,-0.0008680371606896457,0.5962732919254659
receiver_standpoint_magnitude_c,h24_paths_available_but_mutually_disconnected,24,144,132,0.00016225577917747727,-0.023141549465023715,-0.00030827298490506186,-0.0074525880706816745,0.7888198757763976
receiver_standpoint_magnitude_c,c8_1,8,8,132,-0.0003296245484238845,-0.023633429792625074,-0.0008885869148286863,-0.0010526998943288248,0.6273291925465838

## H24 Edge Manifest

edge_set,n_edges,sha256,file
h24_minimum_factorisation_suite_168,168,74820de5910430840c9e67b758433bd97d46d3558e34ec0b607526c2ed520ada,Stage_B7_3a_h24_minimum_factorisation_suite_168_edges.csv
h24_effective_ring_edges_144,144,b436ca17f59a34c5d43a584733296fe1a5d07df52e070ca6d5cf07adc2774b84,Stage_B7_3a_h24_effective_ring_edges_144_edges.csv
h24_c8_stitched_derived_216,216,f8a01c25cc8ed58ce9575f2938597a962b60649be4164ab8277a1941d574d665,Stage_B7_3a_h24_c8_stitched_derived_216_edges.csv
E216_minus_E168,48,1e290363b9f1f5aea5de2596e4b9e2052d6868b44fcd69dc06d722bc0dbdb92c,Stage_B7_3a_E216_minus_E168.csv
E168_minus_E216,0,01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b,Stage_B7_3a_E168_minus_E216.csv

## Settings

- event_quantile: 0.75
- steps: 240
- n_runs: 80
- seed: 73073
