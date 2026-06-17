# Private B6H C-Guided Perspective Transform Audit

Status: local/private screen only. No publication, commit, or push was performed.

Primary hypothesis: C enables perspective-dependent coordinate transformation, not merely cross-prediction.

Transforms:

- A_t | C_state -> B_{t+delta}
- B_t | C_state -> A_{t+delta}

Primary endpoint:

`bidirectional_transform = min(A_to_B_transform, B_to_A_transform)`.

Controls:

- global transform
- shuffled C-state transform
- random transform
- no-C mean transform

## Classification

Partial B6H signal: C-conditioned transform beats at least one transform control but not the full set.

## Comparison Summary

endpoint,comparison,mean_C_conditioned,mean_comparator,effect,p_greater,n_events,state_mapping_rate
A_to_B_transform,C_conditioned_transform_vs_global,-0.878908564948148,-0.7849089182148952,-0.09399964673325276,1.0,475,0.9860557768924303
A_to_B_transform,C_conditioned_transform_vs_shuffled_c_state,-0.878908564948148,-0.8863299496037359,0.007421384655587979,0.34493101379724056,475,0.9860557768924303
A_to_B_transform,C_conditioned_transform_vs_random_transform,-0.878908564948148,-1.0134135952101488,0.13450503026200097,0.0001999600079984003,475,0.9860557768924303
A_to_B_transform,C_conditioned_transform_vs_no_c,-0.878908564948148,-1.010954294937751,0.13204572998960307,0.0001999600079984003,475,0.9860557768924303
B_to_A_transform,C_conditioned_transform_vs_global,-1.0226989335472767,-0.9103886089128096,-0.11231032463446702,1.0,475,0.9860557768924303
B_to_A_transform,C_conditioned_transform_vs_shuffled_c_state,-1.0226989335472767,-1.0118996118693455,-0.010799321677931416,0.6322735452909418,475,0.9860557768924303
B_to_A_transform,C_conditioned_transform_vs_random_transform,-1.0226989335472767,-1.0424911647236828,0.019792231176405984,0.2563487302539492,475,0.9860557768924303
B_to_A_transform,C_conditioned_transform_vs_no_c,-1.0226989335472767,-1.0349322376904033,0.012233304143126554,0.33413317336532694,475,0.9860557768924303
bidirectional_transform,C_conditioned_transform_vs_global,-1.3142089466130285,-1.1813745827812832,-0.1328343638317451,1.0,475,0.9860557768924303
bidirectional_transform,C_conditioned_transform_vs_shuffled_c_state,-1.3142089466130285,-1.318568608205388,0.004359661592359733,0.44631073785242953,475,0.9860557768924303
bidirectional_transform,C_conditioned_transform_vs_random_transform,-1.3142089466130285,-1.3896335242063247,0.07542457759329621,0.012397520495900819,475,0.9860557768924303
bidirectional_transform,C_conditioned_transform_vs_no_c,-1.3142089466130285,-1.384021911541906,0.0698129649288776,0.014797040591881624,475,0.9860557768924303
transform_balance,C_conditioned_transform_vs_global,-0.7268103947306319,-0.6674516384348617,-0.059358756295770455,0.9904019196160768,475,0.9860557768924303
transform_balance,C_conditioned_transform_vs_shuffled_c_state,-0.7268103947306319,-0.738907654937695,0.012097260207062916,0.33553289342131576,475,0.9860557768924303
transform_balance,C_conditioned_transform_vs_random_transform,-0.7268103947306319,-0.7233622884788175,-0.003448106251814569,0.5496900619876025,475,0.9860557768924303
transform_balance,C_conditioned_transform_vs_no_c,-0.7268103947306319,-0.7221572904556576,-0.004653104274974443,0.5566886622675465,475,0.9860557768924303
transform_asymmetry,C_conditioned_transform_vs_global,-0.7268103947306319,-0.6674516384348617,-0.059358756295770455,0.9922015596880623,475,0.9860557768924303
transform_asymmetry,C_conditioned_transform_vs_shuffled_c_state,-0.7268103947306319,-0.738907654937695,0.012097260207062916,0.3489302139572086,475,0.9860557768924303
transform_asymmetry,C_conditioned_transform_vs_random_transform,-0.7268103947306319,-0.7233622884788175,-0.003448106251814569,0.5536892621475705,475,0.9860557768924303
transform_asymmetry,C_conditioned_transform_vs_no_c,-0.7268103947306319,-0.7221572904556576,-0.004653104274974443,0.5614877024595081,475,0.9860557768924303

## Source Summary

c_transform_source,n_events,mean_bidirectional,mean_A_to_B,mean_B_to_A
global_fallback,7,,,
state_mapping,495,-1.3142089466130285,-0.8789085649481481,-1.0226989335472767

## Settings

- state_variant: side_tfc
- delta: 5
- n_folds: 5
- min_state_events: 12
- ridge_alpha: 1.0
- n_perm: 5000
- seed: 60710
