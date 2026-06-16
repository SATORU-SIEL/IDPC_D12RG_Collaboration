# Updated B5.5 preregistration proposal

## Title

Triadic constraint audit of phi-derived intersection geometry and bounded selective stabilization.

## Status

This preregistration is written before the B5.5 execution. It incorporates:

- Marcel's bounded-selective-stabilization constraint;
- Luke's shared-node ring-layer topology implementation check, now explicitly reported as a secondary result block;
- Luke's triadic-packet 12-clock decomposition B_j={j,j+4,j+8}, now explicitly reported as a secondary result block;
- Pasquale's residual-condensation point as a deferred explanatory audit, not a primary endpoint.

## Primary Question

Does C_t predict a short-lag increase in future A-B consistency?

Definitions:

- A = EEG curvature / phase-curvature structure;
- B = quantum MQ structure;
- C = phi-derived phase-bearing sparse event geometry;
- future A-B consistency = |corr(kappa, MQ)| over a future local window.

The primary delta is fixed at delta=5. Longer deltas 10, 20, and 30 are secondary.

## Primary Endpoint

The primary event class is:

`C event AND high TFC_mean`.

The primary endpoint is future A-B consistency at delta=5.

Primary controls:

- shuffled C timing;
- shuffled C phase;
- density-only C events;
- phase-event-only events;
- pairwise A-C only;
- pairwise B-C only;
- pairwise A-B only.

The pairwise A-C control is central: the result must not reduce to A-C coupling alone.

## Bounded Selective Stabilization Boundary

A positive B5.5 interpretation requires boundedness, preservation of negative controls, and avoidance of generic persistence, drift, runaway amplification, fragmentation, or all-readout amplification.

## Secondary Closure Endpoint

The secondary closure endpoint tests whether the same event family supports:

AB -> C -> future AB.

The closure audit combines pre/current A-B consistency, C consistency, future A-B consistency, and return gain.

## Mandatory C12 Topology Readout

C12 is a topology-sensitive readout, not the ontological intersection itself.

The C12 chain tested is:

AB interaction -> C event geometry -> future A-B consistency -> C12 topology-specific stabilization.

Endpoints include C12 recovery, C12 vs C8, C12 vs degree-null, C12 vs shifted/random timing, late-window stability, bounded non-runaway score, and non-collapsed differentiation score.

## Luke Secondary Topology Implementation Result Block

Luke's topology concern is explicitly reported as a separate secondary result table.

The audit compares:

1. single-ring event-substitution C12(1,2) readout;
2. separate shared-node ring-layer readout, implemented as C12(±1) and C12(±2) ring layers sharing the same 12 node indices.

This check asks whether single-ring C12(1,2) artificially collapses pairwise/control geometries, possibly masking separate cyclic pathways. It is not allowed to replace or move the primary endpoint.

The shared-node ring-layer readout is supportive only if it reproduces or improves topology-specific selectivity without producing generic improvement across controls.

## Luke Triadic-Packet Topology/Algebra Result Block

Luke's newer packet formulation is also explicitly included as a secondary topology implementation check.

The 12-clock is split into four triadic packets:

`B_j = {j, j+4, j+8}, j=0,1,2,3 (mod 12)`.

The corresponding algebraic note is:

`B_j(x) = product_{k=0}^2 (1 + omega^{j+4k} x) = 1 + omega^{3j} x^3`,

and the full packet product recovers:

`product_{j=0}^3 B_j(x) = product_{r=0}^{11}(1 + omega^r x) = 1 - x^12`.

Operationally, this is tested as four separated bidirectional 3-cycle packets on the same 12 node labels. This is a secondary implementation audit designed to distinguish triadic packet closure from single-ring C12(1,2) and shared-node ring-layer readouts. It is not allowed to replace or move the primary endpoint.

## Interpretation Boundary

B5.5 will not claim proof of subjectivity-intersection itself, phi=O3, complete triadic fixed point, D12RG proof, broad Phi/FES confirmation, or stable carrier closure.

B5.5 tests whether the current empirical C candidate behaves as a bounded, selective, short-lag constraint on future A-B consistency.
