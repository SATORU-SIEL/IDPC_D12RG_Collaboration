# Stage B2 Topology-Aware Carrier Audit Preregistration

## Purpose

Stage B2 is a topology-aware refinement of Stage B. It is not Stage C and it is not a confirmation stage.

The purpose is to test whether explicit directed topology/operator families can discriminate between:

- intrinsic autonomous carrier-like behavior
- IDPC-internal restoration artifact
- externally driven synchronization
- transient non-locking behavior

The main deliverable is a clean discriminating test, not a positive result.

## Inputs

Primary context inputs are existing IDPC-derived Stage B outputs when present:

- `reports/Stage_B_ricci_phase_sync_carrier_results.csv`
- `reports/Stage_B_ricci_eps72_restoring_carrier_results.csv`
- `IDPC_Reproduction/Chapter3/ricci_phase_sync_summary.csv`, if an external input root is provided
- `IDPC_Reproduction/Chapter3/ricci_eps72_restoring_test.csv`, if an external input root is provided
- `IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv`, if an external input root is provided

These are structural-layer readouts. They are not treated as direct carrier evidence.

## eps72 Handling

`eps72` is treated as an existing IDPC paper-defined phase-restoration readout. Stage B2 does not redefine eps72.

Because eps72 is an IDPC-internal restoration quantity, eps72 restoring alone is not carrier evidence. Stage B2 asks whether explicit topology families explain behavior beyond an IDPC-internal restoration artifact interpretation.

## Primary Topology Test

The primary held-out discriminating test compares:

- `C12(1,2)` unseeded
- `C12(1,2)` seeded
- `C8(1)` unseeded
- `C8(1)` seeded
- degree-matched random/null controls for `C12(1,2)`
- degree-matched random/null controls for `C8(1)`

`C12(1,2)` is implemented as a directed 12-node graph with arrows:

- `i -> i+1`
- `i -> i-1`
- `i -> i+2`
- `i -> i-2`

with indices modulo 12, giving 48 directed arrows.

`C8(1)` is implemented as a directed 8-node one-jump ring:

- `i -> i+1`

with indices modulo 8.

## Additional Topology Families

Additional reported families are exploratory and must not override the primary test:

- `C6(1,2)`
- `C8(1,2)`
- `C12(1)`
- cuboctahedron
- dodecahedron
- icosahedron

Polyhedral topologies are reported as higher-order carrier candidates, not as equivalents of standalone `Cn(k)` rings.

## Success Criteria

### Auto-locking

Auto-locking requires all of the following:

- no external jump-start
- late-window locking score above the preregistered threshold
- degree-matched null controls do not explain the score
- FDR-corrected q-value remains significant where multiple comparisons apply
- bounded non-runaway behavior is preserved
- non-collapsed differentiation is preserved
- repeated perturbation seeds reproduce the effect

The preregistered thresholds are:

- `late_window_stability >= 0.70`
- `D12_score >= 0.70` or `D24_score >= 0.70`
- `bounded_non_runaway_score >= 0.70`
- `non_collapsed_differentiation_score >= 0.30`
- `q_value <= 0.05` against degree-matched nulls

### Jump-start-dependent locking

Jump-start-dependent locking requires:

- weak or absent unseeded locking
- stronger seeded locking
- seeded-vs-unseeded difference surviving comparison against controls

`C8(1)` is the primary jump-start-dependent contrast.

### Transient Behavior

Transient behavior is reported when early or mid-window structure appears but late-window stability falls below the persistence threshold.

The script records transient score and duration, including possible 5-loop / 10-loop transience when loop inventory permits.

### 2-through-24 / Phi24 Support

Structural support and empirical support are separated.

Structural support means the graph/operator has constructible loop, path, or return-order coverage from 2 through 24 under the implemented convention.

Empirical support requires D12/D24-structured locking or recurrence under the Stage B2 tests. Structural support alone is not carrier evidence.

## Null Controls

Each primary topology is compared with degree-matched directed random/null graphs that preserve, as far as practical:

- node count
- in-degree distribution
- out-degree distribution
- number of directed arrows
- basic density

Null generation details are written to `reports/Stage_B2_topology_null_controls.csv`.

## Interpretation Rules

Positive Stage B2 interpretation requires:

- `C12(1,2)` auto-locks without jump-start
- `C8(1)` does not show the same unseeded auto-locking and locks only under jump-start
- degree-matched controls do not explain the effect
- bounded non-runaway behavior is preserved
- non-collapsed differentiation is preserved

Negative interpretation is reported if:

- `C12(1,2)` does not auto-lock
- `C12(1,2)` behaves like random/null controls
- `C8(1)` fails as a jump-start contrast
- locking appears only under driven conditions
- the system collapses or runs away
- differentiation is not preserved

Negative results are not reinterpreted as confirmation.

## QFT / Knot Theory Boundary

QFT, knot theory, braid theory, field topology, and invisible memory are recorded only as future theoretical bridges. Stage B2 does not test or confirm QFT, consciousness, AGI, or a physical carrier.

## Stage C Boundary

Stage C is not implemented here. It can only be proposed if Stage B2 produces a meaningful carrier/restoration distinction.

