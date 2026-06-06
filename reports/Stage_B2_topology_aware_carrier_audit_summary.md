# Stage B2 Topology-Aware Carrier Audit Summary

## Purpose

Stage B2 tests explicit directed topology/operator families as an exploratory refinement of Stage B. It is not Stage C.

## Why This Is Stage B2, Not Stage C

Stage B2 asks whether topology-aware behavior can discriminate carrier-like behavior from IDPC-internal restoration artifact. Stage C is reserved for a later recursive-admissibility audit only if Stage B2 produces a meaningful carrier/restoration distinction.

## Inputs Used

- context input files loaded: 4
- topology families tested: 8
- null-control rows: 1280

## eps72 as Existing IDPC Readout

eps72 is treated as an existing IDPC phase-restoration readout. eps72 restoring alone is not treated as carrier evidence in this report.

## Topology Definitions

The primary held-out candidate is C12(1,2), implemented with 12 nodes and bidirectional 1-jump and 2-jump arrows, giving 48 directed arrows. C8(1) is the primary jump-start-dependent contrast.

## Topology Classes

- C8(1): standalone Cn(k) directed rings, nodes=8, edges=8, convention=directed clockwise 1-jump
- C6(1,2): standalone Cn(k) directed rings, nodes=6, edges=24, convention=bidirectional 1-jump and 2-jump
- C8(1,2): standalone Cn(k) directed rings, nodes=8, edges=32, convention=bidirectional 1-jump and 2-jump
- C12(1): standalone Cn(k) directed rings, nodes=12, edges=12, convention=directed clockwise 1-jump
- C12(1,2): standalone Cn(k) directed rings, nodes=12, edges=48, convention=bidirectional 1-jump and 2-jump; 48 directed arrows
- cuboctahedron: cuboctahedral / atom-like flattened structures, nodes=12, edges=48, convention=bidirected cuboctahedron edges
- dodecahedron: dodecahedral topology, nodes=20, edges=60, convention=bidirected LCF dodecahedron edges
- icosahedron: icosahedral topology, nodes=12, edges=60, convention=bidirected icosahedron edges

## Success Criteria

Auto-locking requires unseeded D12/D24 structure, late-window stability, degree-matched null separation, FDR survival, bounded non-runaway behavior, and non-collapsed differentiation.

## Null Controls

Degree-matched directed random graphs preserve node count, in-degree distribution, out-degree distribution, directed-arrow count where possible, and density approximately.

## Results Table

```csv
topology_name,condition,locking_strength,D12_score,D24_score,p_value,q_value,late_window_stability,perturbation_stability,bounded_non_runaway_score,non_collapsed_differentiation_score,supports_2_through_24_structural,supports_2_through_24_empirical,interpretation
C8(1),unseeded,0.8438806502550005,0.48625132037236585,0.49596116301895404,0.9629629629629629,0.9876543209876543,0.9084765078361468,0.7822311548760947,0.9302833134623594,0.3612061155343998,True,False,exploratory_or_control_result
C8(1),seeded,0.027270085711986407,0.4998380565421602,0.502969995995771,0.012345679012345678,0.02821869488536155,0.9975245599432991,0.9750713566175457,0.8515051825744899,0.751747751810028,True,False,seeded_or_jump_start_condition_not_primary_carrier_evidence
"C6(1,2)",unseeded,0.950589012108563,0.5493203437518852,0.49104151451854045,0.9506172839506173,0.9876543209876543,0.948091508825776,0.676371039245887,0.9782929233126939,0.11588366152810115,True,False,exploratory_or_control_result
"C6(1,2)",seeded,0.18700674016351457,0.5159868360128131,0.5263848757817101,0.012345679012345678,0.02821869488536155,0.8591590842047513,0.7904259242317677,0.9722517213750983,0.6077185177756633,True,False,seeded_or_jump_start_condition_not_primary_carrier_evidence
"C8(1,2)",unseeded,0.9081682885226436,0.5025881675908156,0.5204576553679112,0.8024691358024691,0.9876543209876543,0.9210348522177089,0.7775250428113062,0.9719552278434292,0.22757524095320747,True,False,exploratory_or_control_result
"C8(1,2)",seeded,0.05748817866009508,0.4999833425478807,0.502391641849026,0.012345679012345678,0.02821869488536155,0.9793056619555209,0.8847297289532288,0.9951851227275993,0.7511737427984799,True,False,seeded_or_jump_start_condition_not_primary_carrier_evidence
C12(1),unseeded,0.692135731490377,0.5033980522326893,0.506410110027204,0.9506172839506173,0.9876543209876543,0.9063422661336602,0.7076373486874741,0.9363875391800424,0.5102275109569535,True,False,exploratory_or_control_result
C12(1),seeded,0.030023001238727413,0.5110881026697303,0.5029100673884315,0.012345679012345678,0.02821869488536155,0.9967038085432225,0.9816500698578196,0.9113709616772292,0.9739946651998764,True,False,seeded_or_jump_start_condition_not_primary_carrier_evidence
"C12(1,2)",unseeded,0.7311751188611223,0.5032712199109688,0.4862258268120554,0.08641975308641975,0.1728395061728395,0.8678287994840865,0.7366643907079754,0.9712353496759484,0.4358933039994244,True,False,negative_or_inconclusive_for_unseeded_C12_1_2_auto_locking
"C12(1,2)",seeded,0.02577986866969039,0.7642693096694595,0.5674869219071333,0.012345679012345678,0.02821869488536155,0.994418929146913,0.8768042379892087,0.9983014709616039,0.9056748776750585,True,False,seeded_or_jump_start_condition_not_primary_carrier_evidence
cuboctahedron,unseeded,0.805181985440327,0.48432647132624157,0.4951848007228154,0.25925925925925924,0.46090534979423864,0.9048871594755477,0.675728273678416,0.9758605280237562,0.3746809121729405,True,False,exploratory_or_control_result
cuboctahedron,seeded,0.6028042700047036,0.5043671726293575,0.4945422043871206,0.5802469135802469,0.8439955106621774,0.7414770341174923,0.8178227479050297,0.9578393931119151,0.59336277290175,True,False,seeded_or_jump_start_condition_not_primary_carrier_evidence
dodecahedron,unseeded,0.6116921507391107,0.4900534526715516,0.5085120648097944,0.012345679012345678,0.02821869488536155,0.8907775660717341,0.7067095304511402,0.979546948998897,0.6066173482958259,True,False,exploratory_or_control_result
dodecahedron,seeded,0.04060582962765048,0.6046175227006129,0.5149713508494478,0.012345679012345678,0.02821869488536155,0.9843819539268936,0.8979065456335856,0.9933279681161146,0.7771259262945771,True,False,seeded_or_jump_start_condition_not_primary_carrier_evidence
icosahedron,unseeded,0.8534350036671263,0.5247068171930931,0.49954991770754853,0.4691358024691358,0.7506172839506172,0.8910122744865546,0.6895112707022679,0.9731594976935934,0.3180935892485928,True,False,exploratory_or_control_result
icosahedron,seeded,0.7734417285942763,0.49909707900638456,0.4995708221712089,0.9876543209876543,0.9876543209876543,0.6959484310937564,0.9045018634594,0.9523443161499265,0.41246985270174363,True,False,seeded_or_jump_start_condition_not_primary_carrier_evidence
```

## 5-Loop / 10-Loop Transience

- C8(1): 2-through-24 path coverage present, but no length-5/10 closed-walk trace under this convention
- C6(1,2): closed walks: length5=960, length10=1050624; transience interpreted separately from primary carrier test
- C8(1,2): closed walks: length5=960, length10=1050752; transience interpreted separately from primary carrier test
- C12(1): 2-through-24 path coverage present, but no length-5/10 closed-walk trace under this convention
- C12(1,2): closed walks: length5=1200, length10=1099008; transience interpreted separately from primary carrier test
- cuboctahedron: closed walks: length5=960, length10=1056768; transience interpreted separately from primary carrier test
- dodecahedron: closed walks: length5=120, length10=81900; transience interpreted separately from primary carrier test
- icosahedron: closed walks: length5=3120, length10=9784380; transience interpreted separately from primary carrier test

## QFT / Knot Theory Boundary

QFT, knot theory, braid theory, field topology, and invisible memory are future theoretical bridges only. Stage B2 does not confirm QFT, consciousness, AGI, or a physical carrier.

## Interpretation

- empirical-positive topology rows under preregistered thresholds: 0
- C12(1,2) unseeded: D12=0.503, D24=0.486, q=0.173, bounded=0.971, differentiation=0.436, interpretation=negative_or_inconclusive_for_unseeded_C12_1_2_auto_locking
- C8(1) contrast: unseeded carrier score=0.674, seeded carrier score=0.776

## Limitations

- The topology simulation uses fixed exploratory Kuramoto-style dynamics and is not a physical proof of a carrier.
- Existing Ricci / eps72 outputs are context readouts and may contain IDPC-internal restoration structure.
- Polyhedral families are included as higher-order exploratory candidates and are not equivalent to standalone Cn(k) rings.

## Whether Stage C Is Justified

Stage B2 does not yet support moving to Stage C.

