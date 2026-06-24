# Stage B7.5f C-side Fraction Localization and Projector-Compatibility Audit

Status: executed after `Stage_B7_5f_preregistration_email_sent.md`.

## Registered Question

Do the observed N/M fraction signatures localize systematically to specific C-side conditions, topology arms, survivor structures, or projector-compatible subspaces?

Fractions are treated as diagnostics first, not explanations.

## Decision Ladder

level,criterion,supported,basis
0,exact_fraction_hits_present,True,close_hits=603; unique=139
1,denominator_universe_recovered_for_some_hits,True,recovered_hits=89
1,focus_fractions_remain_visible,True,focus_hits=28; fractions=1/2|1/4|2/11|3/4
2,full_or_punctured_projector_rank_candidate_exists,True,rank_candidate_hits=160
2,registered_c_side_localization_exists,True,registered_target_hits=263
2,one_quarter_stable_near_5_or_10_proxy,True,one_quarter_5_or_10_hits=3
2,two_eleven_is_traceable_but_not_c12_punctured_projector,True,two_eleven_hits=2; c12_punctured_candidates=0
3,member_structure_candidate_present,True,member_candidate_hits=160
4,explicit_projector_idempotence_tested,False,B7.5f classifies projector compatibility from fraction/carrier arithmetic only; no empirical P matrix is constructed here.
5,explicit_topology_commutator_tested,False,No empirical P/T commutator is constructed in B7.5f; this is deferred to a later matrix-level audit.
6,restricted_trace_determinant_confirmed,False,Trace/determinant candidates are annotated but not confirmed without a constructed restricted topology block.
7,perturbation_defeats_matched_controls,False,B7.5f reuses B7.5d perturbation labels; it does not yet run new matched projector controls.

## Main Result

- Close fraction hits analyzed: 603.
- Unique close fractions: 139.
- Raw denominator/count universe recovered for 89 hits.
- Projector-rank arithmetic candidates: 160 hits.
- Registered C-side target localizations: 263 hits.

## Focus Result

- 1/4 hits: 9; 1/4 near 5-or-10 proxy: 3.
- 2/11 hits: 2; punctured C12 inversion-pair candidates: 0.
- The observed 2/11 signatures are traceable as diagnostics, but they do not currently satisfy the stricter C12 punctured-carrier projector interpretation.
- Fraction signatures therefore do not replace the reverse-side C -> AB topology-readout advantage seen in B7.5a/B7.5d; they remain secondary structure to localize.

## Candidate Family Summary

candidate_family,n_hits,n_focus,n_registered_target,fractions,topologies
full_carrier_projector_rank_candidate,105,8,70,0/1|1/1|1/10|1/11|1/12|1/14|1/2|1/3|1/4|1/7|10/11|11/12|11/14|13/14|2/13|2/3|3/14|3/4|3/5|4/5|4/7|5/7|6/13|6/7|9/10,c10_degree_null|c10_ring_share_11|c10_ring_share_5|c10_ring_share_7|c10_shuffled|c10_side_broken|c11|c12|c12_degree_null|c12_edge_count_null|c12_reversed|c12_ring_share_10|c12_ring_share_11|c12_ring_share_5|c12_ring_share_7|c12_shuffled|c12_side_broken|c13_ring_share_10|c13_ring_share_5|c13_side_broken
diagnostic_fraction_only,435,7,167,0/1|1/1|1/10|1/11|1/12|1/13|1/14|1/18|1/19|1/20|1/23|1/24|1/3|1/4|1/5|1/6|1/7|1/8|1/9|10/11|10/13|10/17|10/19|10/21|11/12|11/14|11/15|11/18|11/19|11/20|11/21|11/24|12/13|12/23|13/14|13/15|13/16|13/17|13/18|13/19|13/22|13/24|14/17|14/19|15/17|15/19|15/22|15/23|16/19|16/23|17/18|17/19|17/20|17/21|17/22|17/23|17/24|18/19|18/23|19/20|19/21|19/22|19/23|19/24|2/15|2/17|2/19|2/21|2/23|2/3|2/5|2/9|20/23|21/23|22/23|23/24|3/14|3/16|3/17|3/19|3/20|3/22|3/23|3/4|3/5|4/11|4/15|4/17|4/19|4/21|4/23|4/5|4/9|5/12|5/14|5/17|5/18|5/19|5/21|5/22|5/23|5/24|5/6|5/7|5/8|5/9|6/19|6/23|7/10|7/11|7/12|7/13|7/15|7/18|7/20|7/22|7/23|7/24|7/8|7/9|8/17|8/19|8/9|9/10|9/11|9/13|9/16|9/17|9/19|9/20|9/22,c10|c10_degree_null|c10_edge_count_null|c10_reversed|c10_ring_share_10|c10_ring_share_11|c10_ring_share_5|c10_ring_share_7|c10_shuffled|c10_side_broken|c11|c12|c12_degree_null|c12_edge_count_null|c12_reversed|c12_ring_share_10|c12_ring_share_11|c12_ring_share_5|c12_ring_share_7|c12_shuffled
five_or_ten_proxy_fraction_diagnostic,6,6,2,1/4|3/4,c10_side_broken|c14_ring_share_10
punctured_carrier_projector_rank_candidate,55,5,24,1/12|1/13|1/14|1/2|1/5|1/6|1/9|11/12|12/13|13/15|2/13|2/15|2/3|3/13|3/4|4/11|4/5|4/9|5/12|5/6|5/9|7/11|7/9|8/11|8/9,c10|c10_degree_null|c10_edge_count_null|c10_reversed|c10_ring_share_10|c10_ring_share_11|c10_ring_share_5|c10_side_broken|c12_shuffled|c12_side_broken|c13|c13_reversed|c13_ring_share_5|c13_ring_share_7|c13_shuffled|c14|c14_ring_share_10|c14_ring_share_11|c15|c16
two_eleven_anomaly_not_c12_projector,2,2,0,2/11,c13_degree_null|c13_ring_share_7

## Fraction Localization Summary

nearest_fraction,c_side_localization,n_hits,families
0/1,registered_c_side_target,23,diagnostic_fraction_only|full_carrier_projector_rank_candidate
0/1,five_or_ten_proxy_region,4,full_carrier_projector_rank_candidate
0/1,non_target_or_broad,4,full_carrier_projector_rank_candidate
1/1,registered_c_side_target,20,full_carrier_projector_rank_candidate
1/1,five_or_ten_proxy_region,4,full_carrier_projector_rank_candidate
1/1,non_target_or_broad,4,full_carrier_projector_rank_candidate
1/1,representation_event_geometry,1,diagnostic_fraction_only
1/10,five_or_ten_proxy_region,2,full_carrier_projector_rank_candidate
1/10,registered_c_side_target,1,diagnostic_fraction_only
1/11,registered_c_side_target,2,diagnostic_fraction_only
1/11,non_target_or_broad,1,full_carrier_projector_rank_candidate
1/12,registered_c_side_target,3,diagnostic_fraction_only|full_carrier_projector_rank_candidate
1/12,five_or_ten_proxy_region,2,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
1/12,non_target_or_broad,2,diagnostic_fraction_only
1/13,registered_c_side_target,4,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
1/13,non_target_or_broad,1,punctured_carrier_projector_rank_candidate
1/14,non_target_or_broad,2,diagnostic_fraction_only
1/14,registered_c_side_target,2,full_carrier_projector_rank_candidate
1/14,x3_or_7mod12_proxy_region,1,punctured_carrier_projector_rank_candidate
1/18,non_target_or_broad,3,diagnostic_fraction_only
1/18,registered_c_side_target,1,diagnostic_fraction_only
1/19,non_target_or_broad,1,diagnostic_fraction_only
1/2,registered_c_side_target,7,full_carrier_projector_rank_candidate|punctured_carrier_projector_rank_candidate
1/2,non_target_or_broad,3,punctured_carrier_projector_rank_candidate
1/20,five_or_ten_proxy_region,1,diagnostic_fraction_only
1/20,non_target_or_broad,1,diagnostic_fraction_only
1/23,five_or_ten_proxy_region,1,diagnostic_fraction_only
1/24,five_or_ten_proxy_region,6,diagnostic_fraction_only
1/24,non_target_or_broad,4,diagnostic_fraction_only
1/24,registered_c_side_target,1,diagnostic_fraction_only
1/24,x3_or_7mod12_proxy_region,1,diagnostic_fraction_only
1/3,registered_c_side_target,3,diagnostic_fraction_only|full_carrier_projector_rank_candidate
1/3,non_target_or_broad,1,diagnostic_fraction_only
1/4,registered_c_side_target,6,diagnostic_fraction_only|five_or_ten_proxy_fraction_diagnostic|full_carrier_projector_rank_candidate
1/4,five_or_ten_proxy_region,2,five_or_ten_proxy_fraction_diagnostic
1/4,non_target_or_broad,1,diagnostic_fraction_only
1/5,non_target_or_broad,5,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
1/5,registered_c_side_target,3,diagnostic_fraction_only
1/6,non_target_or_broad,4,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
1/6,registered_c_side_target,3,diagnostic_fraction_only
1/6,five_or_ten_proxy_region,2,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
1/6,x3_or_7mod12_proxy_region,2,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
1/7,registered_c_side_target,6,full_carrier_projector_rank_candidate
1/7,non_target_or_broad,2,full_carrier_projector_rank_candidate
1/7,x3_or_7mod12_proxy_region,2,diagnostic_fraction_only
1/8,registered_c_side_target,4,diagnostic_fraction_only
1/8,non_target_or_broad,3,diagnostic_fraction_only
1/8,five_or_ten_proxy_region,2,diagnostic_fraction_only
1/9,registered_c_side_target,9,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
1/9,five_or_ten_proxy_region,3,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
1/9,non_target_or_broad,2,diagnostic_fraction_only
10/11,registered_c_side_target,2,diagnostic_fraction_only
10/11,non_target_or_broad,1,full_carrier_projector_rank_candidate
10/13,non_target_or_broad,1,diagnostic_fraction_only
10/17,registered_c_side_target,3,diagnostic_fraction_only
10/19,non_target_or_broad,3,diagnostic_fraction_only
10/19,five_or_ten_proxy_region,2,diagnostic_fraction_only
10/19,registered_c_side_target,2,diagnostic_fraction_only
10/21,registered_c_side_target,1,diagnostic_fraction_only
11/12,five_or_ten_proxy_region,2,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
11/12,non_target_or_broad,2,diagnostic_fraction_only
11/12,registered_c_side_target,2,diagnostic_fraction_only|full_carrier_projector_rank_candidate
11/14,non_target_or_broad,4,diagnostic_fraction_only|full_carrier_projector_rank_candidate
11/15,non_target_or_broad,4,diagnostic_fraction_only
11/18,registered_c_side_target,2,diagnostic_fraction_only
11/19,five_or_ten_proxy_region,1,diagnostic_fraction_only
11/20,five_or_ten_proxy_region,1,diagnostic_fraction_only
11/20,non_target_or_broad,1,diagnostic_fraction_only
11/20,registered_c_side_target,1,diagnostic_fraction_only
11/21,registered_c_side_target,1,diagnostic_fraction_only
11/24,non_target_or_broad,1,diagnostic_fraction_only
12/13,registered_c_side_target,3,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
12/13,non_target_or_broad,1,punctured_carrier_projector_rank_candidate
12/23,five_or_ten_proxy_region,1,diagnostic_fraction_only
12/23,registered_c_side_target,1,diagnostic_fraction_only
13/14,registered_c_side_target,2,full_carrier_projector_rank_candidate
13/14,non_target_or_broad,1,diagnostic_fraction_only
13/15,non_target_or_broad,3,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
13/15,five_or_ten_proxy_region,1,diagnostic_fraction_only
13/16,non_target_or_broad,2,diagnostic_fraction_only
13/16,x3_or_7mod12_proxy_region,1,diagnostic_fraction_only
13/17,registered_c_side_target,1,diagnostic_fraction_only
13/18,registered_c_side_target,3,diagnostic_fraction_only
13/19,non_target_or_broad,1,diagnostic_fraction_only
13/22,registered_c_side_target,3,diagnostic_fraction_only
13/22,non_target_or_broad,1,diagnostic_fraction_only
13/24,five_or_ten_proxy_region,1,diagnostic_fraction_only
13/24,registered_c_side_target,1,diagnostic_fraction_only
14/17,non_target_or_broad,4,diagnostic_fraction_only
14/17,x3_or_7mod12_proxy_region,2,diagnostic_fraction_only
14/19,registered_c_side_target,2,diagnostic_fraction_only
14/19,five_or_ten_proxy_region,1,diagnostic_fraction_only
14/19,non_target_or_broad,1,diagnostic_fraction_only
15/17,registered_c_side_target,6,diagnostic_fraction_only
15/17,five_or_ten_proxy_region,1,diagnostic_fraction_only
15/17,non_target_or_broad,1,diagnostic_fraction_only
15/19,non_target_or_broad,2,diagnostic_fraction_only
15/22,non_target_or_broad,1,diagnostic_fraction_only
15/22,registered_c_side_target,1,diagnostic_fraction_only
15/23,non_target_or_broad,1,diagnostic_fraction_only
16/19,registered_c_side_target,3,diagnostic_fraction_only
16/19,non_target_or_broad,2,diagnostic_fraction_only
16/19,five_or_ten_proxy_region,1,diagnostic_fraction_only
16/19,x3_or_7mod12_proxy_region,1,diagnostic_fraction_only
16/23,non_target_or_broad,1,diagnostic_fraction_only
17/18,non_target_or_broad,3,diagnostic_fraction_only
17/18,registered_c_side_target,1,diagnostic_fraction_only
17/19,five_or_ten_proxy_region,1,diagnostic_fraction_only
17/19,non_target_or_broad,1,diagnostic_fraction_only
17/19,x3_or_7mod12_proxy_region,1,diagnostic_fraction_only
17/20,non_target_or_broad,3,diagnostic_fraction_only
17/20,registered_c_side_target,2,diagnostic_fraction_only
17/20,x3_or_7mod12_proxy_region,2,diagnostic_fraction_only
17/21,five_or_ten_proxy_region,2,diagnostic_fraction_only
17/21,non_target_or_broad,2,diagnostic_fraction_only
17/21,registered_c_side_target,1,diagnostic_fraction_only
17/22,non_target_or_broad,2,diagnostic_fraction_only
17/22,five_or_ten_proxy_region,1,diagnostic_fraction_only
17/22,registered_c_side_target,1,diagnostic_fraction_only
17/23,registered_c_side_target,1,diagnostic_fraction_only
17/24,non_target_or_broad,1,diagnostic_fraction_only
17/24,registered_c_side_target,1,diagnostic_fraction_only
18/19,non_target_or_broad,1,diagnostic_fraction_only
18/23,non_target_or_broad,3,diagnostic_fraction_only
19/20,non_target_or_broad,1,diagnostic_fraction_only
19/20,registered_c_side_target,1,diagnostic_fraction_only
19/21,five_or_ten_proxy_region,5,diagnostic_fraction_only
19/21,non_target_or_broad,1,diagnostic_fraction_only
19/22,registered_c_side_target,3,diagnostic_fraction_only
19/22,five_or_ten_proxy_region,1,diagnostic_fraction_only
19/23,non_target_or_broad,3,diagnostic_fraction_only
19/23,five_or_ten_proxy_region,2,diagnostic_fraction_only
19/23,registered_c_side_target,2,diagnostic_fraction_only
19/23,x3_or_7mod12_proxy_region,1,diagnostic_fraction_only
19/24,registered_c_side_target,2,diagnostic_fraction_only
2/11,non_target_or_broad,1,two_eleven_anomaly_not_c12_projector
2/11,x3_or_7mod12_proxy_region,1,two_eleven_anomaly_not_c12_projector
2/13,five_or_ten_proxy_region,1,full_carrier_projector_rank_candidate
2/13,non_target_or_broad,1,punctured_carrier_projector_rank_candidate
2/15,non_target_or_broad,3,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
2/17,registered_c_side_target,4,diagnostic_fraction_only
2/17,five_or_ten_proxy_region,1,diagnostic_fraction_only
2/19,registered_c_side_target,3,diagnostic_fraction_only
2/19,non_target_or_broad,1,diagnostic_fraction_only
2/19,x3_or_7mod12_proxy_region,1,diagnostic_fraction_only
2/21,five_or_ten_proxy_region,7,diagnostic_fraction_only
2/21,non_target_or_broad,1,diagnostic_fraction_only
2/23,registered_c_side_target,3,diagnostic_fraction_only
2/23,five_or_ten_proxy_region,1,diagnostic_fraction_only
2/3,registered_c_side_target,3,diagnostic_fraction_only|full_carrier_projector_rank_candidate
2/3,five_or_ten_proxy_region,1,punctured_carrier_projector_rank_candidate
2/3,non_target_or_broad,1,diagnostic_fraction_only
2/5,registered_c_side_target,3,diagnostic_fraction_only
2/9,registered_c_side_target,1,diagnostic_fraction_only
20/23,registered_c_side_target,4,diagnostic_fraction_only
20/23,non_target_or_broad,1,diagnostic_fraction_only
21/23,registered_c_side_target,3,diagnostic_fraction_only
21/23,five_or_ten_proxy_region,1,diagnostic_fraction_only
22/23,five_or_ten_proxy_region,1,diagnostic_fraction_only
23/24,five_or_ten_proxy_region,6,diagnostic_fraction_only
23/24,non_target_or_broad,4,diagnostic_fraction_only
23/24,registered_c_side_target,1,diagnostic_fraction_only
23/24,x3_or_7mod12_proxy_region,1,diagnostic_fraction_only
3/13,registered_c_side_target,1,punctured_carrier_projector_rank_candidate
3/14,non_target_or_broad,3,diagnostic_fraction_only|full_carrier_projector_rank_candidate
3/16,non_target_or_broad,3,diagnostic_fraction_only
3/17,non_target_or_broad,3,diagnostic_fraction_only
3/19,registered_c_side_target,3,diagnostic_fraction_only
3/19,non_target_or_broad,1,diagnostic_fraction_only
3/19,x3_or_7mod12_proxy_region,1,diagnostic_fraction_only
3/20,non_target_or_broad,3,diagnostic_fraction_only
3/20,registered_c_side_target,1,diagnostic_fraction_only
3/22,registered_c_side_target,4,diagnostic_fraction_only
3/22,five_or_ten_proxy_region,2,diagnostic_fraction_only
3/22,non_target_or_broad,1,diagnostic_fraction_only
3/23,registered_c_side_target,4,diagnostic_fraction_only
3/23,five_or_ten_proxy_region,1,diagnostic_fraction_only
3/23,non_target_or_broad,1,diagnostic_fraction_only
3/4,registered_c_side_target,3,diagnostic_fraction_only|five_or_ten_proxy_fraction_diagnostic|full_carrier_projector_rank_candidate
3/4,five_or_ten_proxy_region,2,five_or_ten_proxy_fraction_diagnostic
3/4,non_target_or_broad,1,diagnostic_fraction_only
3/4,x3_or_7mod12_proxy_region,1,punctured_carrier_projector_rank_candidate
3/5,registered_c_side_target,2,diagnostic_fraction_only
3/5,x3_or_7mod12_proxy_region,1,full_carrier_projector_rank_candidate
4/11,registered_c_side_target,3,punctured_carrier_projector_rank_candidate
4/11,non_target_or_broad,2,diagnostic_fraction_only
4/11,five_or_ten_proxy_region,1,diagnostic_fraction_only
4/15,registered_c_side_target,2,diagnostic_fraction_only
4/17,registered_c_side_target,1,diagnostic_fraction_only
4/19,non_target_or_broad,3,diagnostic_fraction_only
4/21,five_or_ten_proxy_region,3,diagnostic_fraction_only
4/21,non_target_or_broad,3,diagnostic_fraction_only
4/23,non_target_or_broad,6,diagnostic_fraction_only
4/23,registered_c_side_target,5,diagnostic_fraction_only
4/23,x3_or_7mod12_proxy_region,3,diagnostic_fraction_only
4/23,five_or_ten_proxy_region,2,diagnostic_fraction_only
4/5,non_target_or_broad,7,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
4/5,registered_c_side_target,2,diagnostic_fraction_only
4/5,five_or_ten_proxy_region,1,full_carrier_projector_rank_candidate
4/7,non_target_or_broad,1,full_carrier_projector_rank_candidate
4/9,registered_c_side_target,3,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
4/9,non_target_or_broad,2,diagnostic_fraction_only
4/9,five_or_ten_proxy_region,1,punctured_carrier_projector_rank_candidate
4/9,x3_or_7mod12_proxy_region,1,diagnostic_fraction_only
5/12,five_or_ten_proxy_region,1,punctured_carrier_projector_rank_candidate
5/12,non_target_or_broad,1,diagnostic_fraction_only
5/12,registered_c_side_target,1,diagnostic_fraction_only
5/14,non_target_or_broad,2,diagnostic_fraction_only
5/17,registered_c_side_target,1,diagnostic_fraction_only
5/18,non_target_or_broad,1,diagnostic_fraction_only
5/18,registered_c_side_target,1,diagnostic_fraction_only
5/19,non_target_or_broad,5,diagnostic_fraction_only
5/21,registered_c_side_target,1,diagnostic_fraction_only
5/22,non_target_or_broad,3,diagnostic_fraction_only
5/22,registered_c_side_target,1,diagnostic_fraction_only
5/23,five_or_ten_proxy_region,2,diagnostic_fraction_only
5/23,non_target_or_broad,1,diagnostic_fraction_only
5/24,non_target_or_broad,1,diagnostic_fraction_only
5/24,registered_c_side_target,1,diagnostic_fraction_only
5/6,non_target_or_broad,4,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
5/6,registered_c_side_target,3,diagnostic_fraction_only
5/6,five_or_ten_proxy_region,2,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
5/6,x3_or_7mod12_proxy_region,2,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
5/7,non_target_or_broad,3,diagnostic_fraction_only|full_carrier_projector_rank_candidate
5/8,non_target_or_broad,1,diagnostic_fraction_only
5/9,registered_c_side_target,4,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
5/9,five_or_ten_proxy_region,1,punctured_carrier_projector_rank_candidate
5/9,non_target_or_broad,1,diagnostic_fraction_only
5/9,x3_or_7mod12_proxy_region,1,diagnostic_fraction_only
6/13,five_or_ten_proxy_region,1,full_carrier_projector_rank_candidate
6/19,non_target_or_broad,1,diagnostic_fraction_only
6/23,registered_c_side_target,2,diagnostic_fraction_only
6/7,registered_c_side_target,5,full_carrier_projector_rank_candidate
6/7,non_target_or_broad,1,full_carrier_projector_rank_candidate
7/10,registered_c_side_target,1,diagnostic_fraction_only
7/11,non_target_or_broad,5,diagnostic_fraction_only
7/11,registered_c_side_target,3,punctured_carrier_projector_rank_candidate
7/11,five_or_ten_proxy_region,1,diagnostic_fraction_only
7/12,non_target_or_broad,1,diagnostic_fraction_only
7/13,registered_c_side_target,1,diagnostic_fraction_only
7/15,registered_c_side_target,1,diagnostic_fraction_only
7/18,registered_c_side_target,1,diagnostic_fraction_only
7/20,registered_c_side_target,1,diagnostic_fraction_only
7/22,five_or_ten_proxy_region,1,diagnostic_fraction_only
7/23,non_target_or_broad,1,diagnostic_fraction_only
7/24,non_target_or_broad,1,diagnostic_fraction_only
7/8,registered_c_side_target,3,diagnostic_fraction_only
7/8,five_or_ten_proxy_region,2,diagnostic_fraction_only
7/8,non_target_or_broad,2,diagnostic_fraction_only
7/9,five_or_ten_proxy_region,2,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
7/9,registered_c_side_target,1,diagnostic_fraction_only
8/11,registered_c_side_target,2,punctured_carrier_projector_rank_candidate
8/17,registered_c_side_target,1,diagnostic_fraction_only
8/19,non_target_or_broad,1,diagnostic_fraction_only
8/19,registered_c_side_target,1,diagnostic_fraction_only
8/9,registered_c_side_target,8,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
8/9,five_or_ten_proxy_region,3,diagnostic_fraction_only|punctured_carrier_projector_rank_candidate
8/9,non_target_or_broad,3,diagnostic_fraction_only
9/10,five_or_ten_proxy_region,3,diagnostic_fraction_only|full_carrier_projector_rank_candidate
9/10,registered_c_side_target,1,diagnostic_fraction_only
9/11,non_target_or_broad,3,diagnostic_fraction_only
9/13,registered_c_side_target,1,diagnostic_fraction_only
9/16,five_or_ten_proxy_region,1,diagnostic_fraction_only
9/16,non_target_or_broad,1,diagnostic_fraction_only
9/17,registered_c_side_target,1,diagnostic_fraction_only
9/19,non_target_or_broad,3,diagnostic_fraction_only
9/19,registered_c_side_target,2,diagnostic_fraction_only
9/19,five_or_ten_proxy_region,1,diagnostic_fraction_only
9/20,non_target_or_broad,1,diagnostic_fraction_only
9/20,x3_or_7mod12_proxy_region,1,diagnostic_fraction_only
9/22,registered_c_side_target,2,diagnostic_fraction_only
9/22,non_target_or_broad,1,diagnostic_fraction_only

## Target Focus Rows

source,topology_arm,classification,representation_arm,comparison,metric,value,nearest_fraction,numerator,denominator,abs_error_to_fraction,is_close_to_fraction,is_focus_fraction,has_numerator_gt_1,tags,denominator_universe,raw_numerator,raw_denominator,raw_fraction,raw_count_recovered,carrier_dimension_R,reduced_fraction,c12_neighborhood,reversed_region,ring_share_region,survivor_strength_region,five_or_ten_proxy_region,x3_or_7mod12_proxy_region,boundary_or_reverse_side,reverse_side_readout,c_side_localization,c_side_localization_score,candidate_family,full_carrier_rank_integral,punctured_carrier_rank_integral,candidate_rank,projector_level,topology_compatibility_candidate,trace_determinant_candidate,basis
paired_boundary,c14_ring_share_7,reverse-stable,,full_minus_reverse,full_win_fraction,0.25,1/4,1,4,0.0,True,True,False,c14_transition_probe|ring_sharing|ring_share_7|x3_or_7mod12_proxy|even_n,paired_seed_runs,9,36,9/36,True,14,1/4,False,False,True,False,False,True,True,True,registered_c_side_target,3,diagnostic_fraction_only,False,False,,1,False,False,raw=9/36/paired_seed_runs
paired_boundary,c14_ring_share_10,reverse-stable,,full_minus_reverse,full_win_fraction,0.25,1/4,1,4,0.0,True,True,False,c14_transition_probe|ring_sharing|ring_share_10|5_or_10_proxy|even_n,paired_seed_runs,9,36,9/36,True,14,1/4,False,False,True,False,True,False,True,True,registered_c_side_target,3,five_or_ten_proxy_fraction_diagnostic,False,False,,1,False,False,raw=9/36/paired_seed_runs; 1/4 or 3/4 near 5/10 proxy
readout_rank_scaled,c12_degree_null,reverse-stable,full_self_consistent_rstar,,readout_minmax_scaled,0.2487147615857819,1/4,1,4,0.001285238414218,True,True,False,c12_neighborhood|even_n,topology_readout_scaled_metric,1,4,1/4,False,12,1/4,True,False,False,False,False,False,True,True,registered_c_side_target,3,full_carrier_projector_rank_candidate,True,False,3.0,3,True,True,topology_readout_scaled_metric; R=12; rank=3
event_geometry,representation_events,representation,full_self_consistent_rstar,,full_self_consistent_rstar_top4_survivor_overlap_fraction,0.25,1/4,1,4,0.0,True,True,False,top4_overlap,top4_survivor_overlap,1,4,1/4,True,0,1/4,False,False,False,True,False,False,False,False,registered_c_side_target,1,diagnostic_fraction_only,False,False,,1,False,False,raw=1/4/top4_survivor_overlap
event_geometry,representation_events,representation,c_to_ab_magnitude_only,,c_to_ab_magnitude_only_top4_survivor_overlap_fraction,0.25,1/4,1,4,0.0,True,True,False,top4_overlap,top4_survivor_overlap,1,4,1/4,True,0,1/4,False,False,False,True,False,False,False,False,registered_c_side_target,1,diagnostic_fraction_only,False,False,,1,False,False,raw=1/4/top4_survivor_overlap
event_geometry,representation_events,representation,c_to_ab_standpoint_only,,c_to_ab_standpoint_only_top4_survivor_overlap_fraction,0.25,1/4,1,4,0.0,True,True,False,top4_overlap,top4_survivor_overlap,1,4,1/4,True,0,1/4,False,False,False,True,False,False,False,False,registered_c_side_target,1,diagnostic_fraction_only,False,False,,1,False,False,raw=1/4/top4_survivor_overlap
readout_rank_scaled,c10_side_broken,full-stable,c_to_ab_magnitude_only,,readout_minmax_scaled,0.2498028096371051,1/4,1,4,0.0001971903628948,True,True,False,c10_boundary_candidate|5_or_10_proxy|even_n,topology_readout_scaled_metric,1,4,1/4,False,10,1/4,False,False,False,False,True,False,False,False,five_or_ten_proxy_region,0,five_or_ten_proxy_fraction_diagnostic,False,False,,1,False,False,topology_readout_scaled_metric; 1/4 or 3/4 near 5/10 proxy
readout_rank_scaled,c10_side_broken,full-stable,c_to_ab_standpoint_only,,readout_minmax_scaled,0.2498028096371051,1/4,1,4,0.0001971903628948,True,True,False,c10_boundary_candidate|5_or_10_proxy|even_n,topology_readout_scaled_metric,1,4,1/4,False,10,1/4,False,False,False,False,True,False,False,False,five_or_ten_proxy_region,0,five_or_ten_proxy_fraction_diagnostic,False,False,,1,False,False,topology_readout_scaled_metric; 1/4 or 3/4 near 5/10 proxy
readout_rank_scaled,c14_shuffled,full-stable,full_self_consistent_rstar,,readout_minmax_scaled,0.2456738426441636,1/4,1,4,0.0043261573558364,True,True,False,c14_transition_probe|even_n,topology_readout_scaled_metric,1,4,1/4,False,14,1/4,False,False,False,False,False,False,False,False,non_target_or_broad,0,diagnostic_fraction_only,False,False,,0,False,False,topology_readout_scaled_metric
readout_rank_scaled,c13_ring_share_7,full-stable,full_self_consistent_rstar,,readout_minmax_scaled,0.1834614214123698,2/11,2,11,0.001643239594188,True,True,True,c13_full_branch|ring_sharing|ring_share_7|x3_or_7mod12_proxy|odd_n,topology_readout_scaled_metric,2,11,2/11,False,13,2/11,False,False,True,False,False,True,False,False,x3_or_7mod12_proxy_region,1,two_eleven_anomaly_not_c12_projector,False,False,,0,False,False,topology_readout_scaled_metric; R=13; R*2/11=2.3636363636363638; (R-1)*2/11=2.1818181818181817
readout_rank_scaled,c13_degree_null,full-stable,full_self_consistent_rstar,,readout_minmax_scaled,0.1817951271060108,2/11,2,11,2.3054712170983427e-05,True,True,True,c13_full_branch|odd_n,topology_readout_scaled_metric,2,11,2/11,False,13,2/11,False,False,False,False,False,False,False,False,non_target_or_broad,0,two_eleven_anomaly_not_c12_projector,False,False,,0,False,False,topology_readout_scaled_metric; R=13; R*2/11=2.3636363636363638; (R-1)*2/11=2.1818181818181817

## Boundary

B7.5f supports a narrower interpretation: exact fractions are not random noise, and some are recoverable through denominator/candidate-carrier structure. However, the current evidence does not yet construct an empirical projector P, does not test [P,T], and does not confirm a restricted trace/determinant block.

The next matrix-level step would need to build explicit P/T objects and test idempotence, commutator error, and restricted topology trace/determinant directly.

## Inputs

- fraction_scan: /Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration/reports/stage_b7_5e/Stage_B7_5e_fraction_signature_scan.csv
- paired_delta: /Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration/reports/stage_b7_5d/Stage_B7_5d_paired_delta_summary.csv
- readout_summary: /Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration/reports/stage_b7_5d/Stage_B7_5d_readout_summary.csv
