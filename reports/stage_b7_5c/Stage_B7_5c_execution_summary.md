# Stage B7.5c Paired Stability-Boundary Audit

Status: executed after `Stage_B7_5c_preregistration_email_sent.md`.

## Registered Question

Under which seed, topology, event-schedule, and ring-sharing conditions does C12 readout prefer reverse-side C->AB, and under which conditions does it prefer full self-consistent R*?

## Primary Paired Boundary: Full Self Minus Reverse

topology_arm,comparison,left_arm,right_arm,mean_delta,median_delta,sd_delta,p_left_greater_paired,left_win_fraction,bootstrap_ci_low,bootstrap_ci_high,stable_left_win,stable_right_win
no_topology_baseline,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.0031895548671317456,-0.0029782896785495363,0.0019251428795576018,0.9591836734693877,0.041666666666666664,-0.003743268881896868,-0.0026284924567367596,False,True
c12_1_2,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.0035944517593319175,-0.0037079642035655353,0.0020935050805358573,0.9183673469387755,0.08333333333333333,-0.004156566088888692,-0.0029688079661344055,False,True
c12_reversed,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.0032033413622713073,-0.002599307662337985,0.0024232142733282723,0.9387755102040817,0.0625,-0.0039053382380338387,-0.0025162989959374724,False,True
c12_side_broken,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.002955231804730304,-0.002451616264575456,0.0020964451535341712,0.9795918367346939,0.020833333333333332,-0.0035721399221880436,-0.0023859561913971757,False,True
c12_shuffled,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.00506645797395915,-0.00508863640782886,0.0025057831909708716,1.0,0.0,-0.0057469829077184025,-0.004375235865054985,False,True
c10,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.00020405301011545943,0.0004427750559317773,0.002550555463084669,0.42857142857142855,0.5833333333333334,-0.000509905284132385,0.0009159079663698095,False,False
c11,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.0011307682444923993,-0.001467445820499954,0.0027909256223871324,0.6938775510204082,0.3125,-0.0019121244134051721,-0.0003351082820214068,False,True
c13,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.002359979046966259,0.0019908955078150915,0.002269375943925506,0.16326530612244897,0.8541666666666666,0.0017127810346297641,0.0030533923224652796,True,False
c14,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.00024676928446109415,0.00036808007734183434,0.0018925481256970957,0.42857142857142855,0.5833333333333334,-0.0002671961984711733,0.0007531700443633128,False,False
degree_matched_null,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.005330224433388546,-0.005888053877109641,0.002392341393236524,1.0,0.0,-0.005992965458524146,-0.004632877406214789,False,True
edge_count_matched_null,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,0.0003233295186728488,0.0006318226516971812,0.002437874494361552,0.42857142857142855,0.5833333333333334,-0.000400705887583435,0.0009611981272883052,False,False
ring_share_c12_plus_5,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.005056587675119591,-0.004281481940025349,0.0031431928966910655,0.9795918367346939,0.020833333333333332,-0.005908312956523267,-0.004213797708114743,False,True
ring_share_c12_plus_7,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.004275872748804571,-0.003985885309945966,0.0023529089396835644,0.9795918367346939,0.020833333333333332,-0.004946015081553743,-0.003622057481975907,False,True
ring_share_c12_plus_10,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.003603805276310957,-0.0035633325238746266,0.0026794135915324054,0.8979591836734694,0.10416666666666667,-0.004357088574637972,-0.0028724393516198882,False,True
ring_share_c12_plus_11,full_minus_reverse,full_self_consistent_rstar,reverse_only_c_to_ab,-0.0038838017946824428,-0.003881493386389148,0.00281988274260318,0.9183673469387755,0.08333333333333333,-0.004666147048324051,-0.0030582970945234613,False,True

## C12 Component Deltas Against Reverse

topology_arm,comparison,left_arm,right_arm,mean_delta,median_delta,sd_delta,p_left_greater_paired,left_win_fraction,bootstrap_ci_low,bootstrap_ci_high,stable_left_win,stable_right_win
c12_1_2,magnitude_minus_reverse,c_to_ab_magnitude_only,reverse_only_c_to_ab,-0.005222961733330593,-0.005516884816604065,0.0029068454035789506,0.9387755102040817,0.0625,-0.006042413109945938,-0.0043377602462127025,False,True
c12_1_2,receiver_minus_reverse,c_to_ab_receiver_only,reverse_only_c_to_ab,0.0023166181418105727,0.002503793792144755,0.00396977720123033,0.32653061224489793,0.6875,0.0011386951695073323,0.003439208674538899,True,False
c12_1_2,standpoint_minus_reverse,c_to_ab_standpoint_only,reverse_only_c_to_ab,-0.005222961733330593,-0.005516884816604065,0.0029068454035789506,0.9387755102040817,0.0625,-0.006046577559785194,-0.004426156067752511,False,True

## Boundary Classification

criterion,supported,basis
primary_c12_prefers_full_self,False,"C12 full-minus-reverse mean delta -0.00359445; CI [-0.00415657, -0.00296881]"
primary_c12_stable_full_self,False,C12 stable_left_win=False; left_win_fraction 0.083
primary_c12_stable_reverse,True,C12 stable_right_win=True; left_win_fraction 0.083
stability_boundary_present,True,stable_full=1; stable_reverse=11; boundary_or_flip=3
stable_full_topologies,True,c13
stable_reverse_topologies,True,no_topology_baseline|c12_1_2|c12_reversed|c12_side_broken|c12_shuffled|c11|degree_matched_null|ring_share_c12_plus_5|ring_share_c12_plus_7|ring_share_c12_plus_10|ring_share_c12_plus_11

## Readout Means

topology_arm,representation_arm,arm_family,n_nodes,n_directed_edges,topology_notes,mean_bounded_differentiated_recovery,sd_bounded_differentiated_recovery,n_runs,n_seed_events
c10,c_to_ab_receiver_only,receiver_only,10,40,"C10(1,2) neighbouring-cycle control",-0.0031878479826135623,0.0039566138536611985,48,132
c10,full_self_consistent_rstar,full_self_consistent_rstar,10,40,"C10(1,2) neighbouring-cycle control",-0.003924315377017017,0.0025449118367776415,48,132
c10,reverse_only_c_to_ab,reverse_only_c_to_ab,10,40,"C10(1,2) neighbouring-cycle control",-0.0041283683871324766,0.002909817507391033,48,132
c10,c_to_ab_standpoint_only,standpoint_only,10,40,"C10(1,2) neighbouring-cycle control",-0.0056000644759287,0.0027824530635626636,48,132
c10,c_to_ab_magnitude_only,magnitude_only,10,40,"C10(1,2) neighbouring-cycle control",-0.0056000644759287,0.0027824530635626636,48,132
c11,c_to_ab_receiver_only,receiver_only,11,44,"C11(1,2) neighbouring-cycle control",-0.004180644260822972,0.004449992657894439,48,132
c11,c_to_ab_standpoint_only,standpoint_only,11,44,"C11(1,2) neighbouring-cycle control",-0.006596881713606305,0.002535704364761674,48,132
c11,c_to_ab_magnitude_only,magnitude_only,11,44,"C11(1,2) neighbouring-cycle control",-0.006596881713606305,0.002535704364761674,48,132
c11,reverse_only_c_to_ab,reverse_only_c_to_ab,11,44,"C11(1,2) neighbouring-cycle control",-0.007886826233803193,0.0034222854279244846,48,132
c11,full_self_consistent_rstar,full_self_consistent_rstar,11,44,"C11(1,2) neighbouring-cycle control",-0.009017594478295594,0.002617646499527613,48,132
c12_1_2,c_to_ab_receiver_only,receiver_only,12,48,primary Luke/D12RG normalized readout candidate,0.03450021896579996,0.0024849197527209905,48,132
c12_1_2,reverse_only_c_to_ab,reverse_only_c_to_ab,12,48,primary Luke/D12RG normalized readout candidate,0.03218360082398938,0.0030078871291537934,48,132
c12_1_2,full_self_consistent_rstar,full_self_consistent_rstar,12,48,primary Luke/D12RG normalized readout candidate,0.028589149064657465,0.0030964327203865443,48,132
c12_1_2,c_to_ab_standpoint_only,standpoint_only,12,48,primary Luke/D12RG normalized readout candidate,0.026960639090658794,0.0033349120186100087,48,132
c12_1_2,c_to_ab_magnitude_only,magnitude_only,12,48,primary Luke/D12RG normalized readout candidate,0.026960639090658794,0.0033349120186100087,48,132
c12_reversed,c_to_ab_receiver_only,receiver_only,12,48,"C12(1,2) with all directed arrows reversed",0.034897009237106785,0.002109867289569478,48,132
c12_reversed,reverse_only_c_to_ab,reverse_only_c_to_ab,12,48,"C12(1,2) with all directed arrows reversed",0.03233211327796304,0.002647084942322466,48,132
c12_reversed,full_self_consistent_rstar,full_self_consistent_rstar,12,48,"C12(1,2) with all directed arrows reversed",0.02912877191569173,0.0036015390016793,48,132
c12_reversed,c_to_ab_standpoint_only,standpoint_only,12,48,"C12(1,2) with all directed arrows reversed",0.02640798460530355,0.0033506402219725968,48,132
c12_reversed,c_to_ab_magnitude_only,magnitude_only,12,48,"C12(1,2) with all directed arrows reversed",0.02640798460530355,0.0033506402219725968,48,132
c12_shuffled,c_to_ab_receiver_only,receiver_only,12,48,C12 capacity-preserving target-shuffled control,0.009362158413278069,0.002486644082898206,48,132
c12_shuffled,reverse_only_c_to_ab,reverse_only_c_to_ab,12,48,C12 capacity-preserving target-shuffled control,0.006036721695971977,0.002299564269763867,48,132
c12_shuffled,full_self_consistent_rstar,full_self_consistent_rstar,12,48,C12 capacity-preserving target-shuffled control,0.0009702637220128275,0.002747771851830957,48,132
c12_shuffled,c_to_ab_standpoint_only,standpoint_only,12,48,C12 capacity-preserving target-shuffled control,0.0007701455546080838,0.0024310532433839305,48,132
c12_shuffled,c_to_ab_magnitude_only,magnitude_only,12,48,C12 capacity-preserving target-shuffled control,0.0007701455546080838,0.0024310532433839305,48,132
c12_side_broken,c_to_ab_receiver_only,receiver_only,12,48,degree-matched C12 side-correspondence-broken control,0.016099510144288797,0.0026793503596504583,48,132
c12_side_broken,reverse_only_c_to_ab,reverse_only_c_to_ab,12,48,degree-matched C12 side-correspondence-broken control,0.010421119269378798,0.002179354960186516,48,132
c12_side_broken,full_self_consistent_rstar,full_self_consistent_rstar,12,48,degree-matched C12 side-correspondence-broken control,0.007465887464648493,0.002741528695227201,48,132
c12_side_broken,c_to_ab_standpoint_only,standpoint_only,12,48,degree-matched C12 side-correspondence-broken control,0.006824869950551323,0.002362179059191698,48,132
c12_side_broken,c_to_ab_magnitude_only,magnitude_only,12,48,degree-matched C12 side-correspondence-broken control,0.006824869950551323,0.002362179059191698,48,132
c13,full_self_consistent_rstar,full_self_consistent_rstar,13,52,"C13(1,2) neighbouring-cycle control",-0.00066133536788985,0.002566414564672706,48,132
c13,c_to_ab_standpoint_only,standpoint_only,13,52,"C13(1,2) neighbouring-cycle control",-0.0007836276527898555,0.002126388585262028,48,132
c13,c_to_ab_magnitude_only,magnitude_only,13,52,"C13(1,2) neighbouring-cycle control",-0.0007836276527898555,0.002126388585262028,48,132
c13,reverse_only_c_to_ab,reverse_only_c_to_ab,13,52,"C13(1,2) neighbouring-cycle control",-0.0030213144148561084,0.0025154539912430928,48,132
c13,c_to_ab_receiver_only,receiver_only,13,52,"C13(1,2) neighbouring-cycle control",-0.006534331144425128,0.0022262644541959542,48,132
c14,c_to_ab_standpoint_only,standpoint_only,14,56,"C14(1,2) neighbouring-cycle control",-0.0016286794886901457,0.0022293690381993535,48,132
c14,c_to_ab_magnitude_only,magnitude_only,14,56,"C14(1,2) neighbouring-cycle control",-0.0016286794886901457,0.0022293690381993535,48,132
c14,full_self_consistent_rstar,full_self_consistent_rstar,14,56,"C14(1,2) neighbouring-cycle control",-0.002822136620904667,0.002415671273104208,48,132
c14,reverse_only_c_to_ab,reverse_only_c_to_ab,14,56,"C14(1,2) neighbouring-cycle control",-0.0030689059053657605,0.0025401547928707805,48,132
c14,c_to_ab_receiver_only,receiver_only,14,56,"C14(1,2) neighbouring-cycle control",-0.005278875011606965,0.001858731888301863,48,132
degree_matched_null,c_to_ab_receiver_only,receiver_only,12,48,C12 node/edge-capacity matched null,0.012690500724450193,0.0030299819536993397,48,132
degree_matched_null,reverse_only_c_to_ab,reverse_only_c_to_ab,12,48,C12 node/edge-capacity matched null,0.00932340795387059,0.0029347053829203266,48,132
degree_matched_null,full_self_consistent_rstar,full_self_consistent_rstar,12,48,C12 node/edge-capacity matched null,0.003993183520482045,0.0025679564189650924,48,132
degree_matched_null,c_to_ab_standpoint_only,standpoint_only,12,48,C12 node/edge-capacity matched null,0.0034228748331756767,0.002746426537755838,48,132
degree_matched_null,c_to_ab_magnitude_only,magnitude_only,12,48,C12 node/edge-capacity matched null,0.0034228748331756767,0.002746426537755838,48,132
edge_count_matched_null,c_to_ab_receiver_only,receiver_only,12,48,C12 edge-count matched random directed null,0.008777954248319718,0.002571941617087388,48,132
edge_count_matched_null,full_self_consistent_rstar,full_self_consistent_rstar,12,48,C12 edge-count matched random directed null,0.004903236844224898,0.002329232334284438,48,132
edge_count_matched_null,reverse_only_c_to_ab,reverse_only_c_to_ab,12,48,C12 edge-count matched random directed null,0.004579907325552049,0.0023217258577620525,48,132
edge_count_matched_null,c_to_ab_standpoint_only,standpoint_only,12,48,C12 edge-count matched random directed null,0.003318011820859478,0.0018105323386999924,48,132
edge_count_matched_null,c_to_ab_magnitude_only,magnitude_only,12,48,C12 edge-count matched random directed null,0.003318011820859478,0.0018105323386999924,48,132
no_topology_baseline,c_to_ab_receiver_only,receiver_only,12,0,12 nodes with no coupling edges,0.03223849687315643,0.003025357634571765,48,132
no_topology_baseline,reverse_only_c_to_ab,reverse_only_c_to_ab,12,0,12 nodes with no coupling edges,0.0261627856992807,0.0028064768666868135,48,132
no_topology_baseline,full_self_consistent_rstar,full_self_consistent_rstar,12,0,12 nodes with no coupling edges,0.022973230832148958,0.002869502300280169,48,132
no_topology_baseline,c_to_ab_standpoint_only,standpoint_only,12,0,12 nodes with no coupling edges,0.021992484590130614,0.002752631584879856,48,132
no_topology_baseline,c_to_ab_magnitude_only,magnitude_only,12,0,12 nodes with no coupling edges,0.021992484590130614,0.002752631584879856,48,132
ring_share_c12_plus_10,c_to_ab_receiver_only,receiver_only,12,48,"C12(1,2) with shared 10-ring proxy edges",0.034771232753971835,0.002691443214290186,48,132
ring_share_c12_plus_10,reverse_only_c_to_ab,reverse_only_c_to_ab,12,48,"C12(1,2) with shared 10-ring proxy edges",0.03198528496391132,0.0031172923228566874,48,132
ring_share_c12_plus_10,full_self_consistent_rstar,full_self_consistent_rstar,12,48,"C12(1,2) with shared 10-ring proxy edges",0.028381479687600363,0.0037635432965777904,48,132
ring_share_c12_plus_10,c_to_ab_standpoint_only,standpoint_only,12,48,"C12(1,2) with shared 10-ring proxy edges",0.0265136344883805,0.003457190253814338,48,132
ring_share_c12_plus_10,c_to_ab_magnitude_only,magnitude_only,12,48,"C12(1,2) with shared 10-ring proxy edges",0.0265136344883805,0.003457190253814338,48,132
ring_share_c12_plus_11,c_to_ab_receiver_only,receiver_only,12,48,"C12(1,2) with shared 11 mod 12 reflective proxy edges",0.03481811544807082,0.0021857487978621257,48,132
ring_share_c12_plus_11,reverse_only_c_to_ab,reverse_only_c_to_ab,12,48,"C12(1,2) with shared 11 mod 12 reflective proxy edges",0.031875593494245714,0.002942201937119361,48,132
ring_share_c12_plus_11,full_self_consistent_rstar,full_self_consistent_rstar,12,48,"C12(1,2) with shared 11 mod 12 reflective proxy edges",0.027991791699563274,0.0037431512377593536,48,132
ring_share_c12_plus_11,c_to_ab_standpoint_only,standpoint_only,12,48,"C12(1,2) with shared 11 mod 12 reflective proxy edges",0.02611324735001587,0.0036424496203473055,48,132
ring_share_c12_plus_11,c_to_ab_magnitude_only,magnitude_only,12,48,"C12(1,2) with shared 11 mod 12 reflective proxy edges",0.02611324735001587,0.0036424496203473055,48,132
ring_share_c12_plus_5,c_to_ab_receiver_only,receiver_only,12,72,"C12(1,2) with shared 5-ring proxy edges",0.03505996590054841,0.0021665505193887665,48,132
ring_share_c12_plus_5,reverse_only_c_to_ab,reverse_only_c_to_ab,12,72,"C12(1,2) with shared 5-ring proxy edges",0.0287002669398909,0.0025678275881785883,48,132
ring_share_c12_plus_5,full_self_consistent_rstar,full_self_consistent_rstar,12,72,"C12(1,2) with shared 5-ring proxy edges",0.023643679264771306,0.003581127693487688,48,132
ring_share_c12_plus_5,c_to_ab_standpoint_only,standpoint_only,12,72,"C12(1,2) with shared 5-ring proxy edges",0.023555439924692417,0.002760334359159055,48,132
ring_share_c12_plus_5,c_to_ab_magnitude_only,magnitude_only,12,72,"C12(1,2) with shared 5-ring proxy edges",0.023555439924692417,0.002760334359159055,48,132
ring_share_c12_plus_7,c_to_ab_receiver_only,receiver_only,12,72,"C12(1,2) with shared 7 mod 12 proxy edges",0.03521970933606741,0.0027044524195041727,48,132
ring_share_c12_plus_7,reverse_only_c_to_ab,reverse_only_c_to_ab,12,72,"C12(1,2) with shared 7 mod 12 proxy edges",0.027523954465638854,0.0026674544527713726,48,132
ring_share_c12_plus_7,full_self_consistent_rstar,full_self_consistent_rstar,12,72,"C12(1,2) with shared 7 mod 12 proxy edges",0.023248081716834287,0.003218730710753115,48,132
ring_share_c12_plus_7,c_to_ab_standpoint_only,standpoint_only,12,72,"C12(1,2) with shared 7 mod 12 proxy edges",0.022709371198399872,0.00276895670725375,48,132
ring_share_c12_plus_7,c_to_ab_magnitude_only,magnitude_only,12,72,"C12(1,2) with shared 7 mod 12 proxy edges",0.022709371198399872,0.00276895670725375,48,132

## Decision Boundary

- Stable reverse-side readout requires reverse-only C->AB to beat full self-consistent R* under paired seeds, with stable bootstrap direction and C12 specificity.
- Stable self-consistent readout requires full self-consistent R* to beat reverse-only C->AB under paired seeds, with stable bootstrap direction and C12 specificity.
- Boundary result means ordering changes by seed/topology/schedule/ring-sharing, so the object is a stability boundary rather than a global winner.

## Settings

- event_quantile: 0.75
- steps: 240
- n_runs: 48
- n_boot: 2000
- seed: 75375
