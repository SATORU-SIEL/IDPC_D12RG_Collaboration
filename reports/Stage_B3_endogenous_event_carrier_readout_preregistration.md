# Stage B3 Endogenous-Event-Conditioned Carrier-Readout Audit Preregistration

## Purpose

Stage B3 is a frozen, pre-registered transition/recovery audit. It is not
Stage C and it is not a physical-carrier confirmation stage.

The primary question is whether endogenous IDPC transition events condition
bounded, non-collapsed, differentiated D12/D24 recovery on the primary
C12(1,2) readout topology.

## Stage Boundary

Stage B2 rejected unseeded autonomous C12(1,2) auto-locking under the
previous fixed topology-only audit. Stage B3 does not reinterpret that result
as positive. Instead, it tests a different, narrower hypothesis: event
conditioning by IDPC-internal transition events.

Stage C remains reserved for later recursive-admissibility, memory, knot, or
field-topology audits only if an earlier stage produces a meaningful
carrier/readout distinction.

## Frozen Primary Design

- Primary topology: `C12(1,2)`
- Primary discriminator: three-way comparison on the same C12(1,2) graph
- Primary conditions:
  - endogenous-event conditioned
  - time-shifted-event conditioned
  - random-event conditioned
- Primary endpoint: `differentiated_recovery`
- Primary readout: bounded, non-collapsed D12/D24 differentiated recovery
- Primary success comparison: endogenous condition must exceed both
  time-shifted and random-event controls.

Degree-matched directed random graphs are secondary null-floor controls, not
the primary discriminator.

## Input Data

Primary event source:

- `event_level_with_fes_phase_TRUE_RICCI.csv`

Required columns:

- `label`
- `task_idx`
- `J`
- `distance`
- `phase`
- `fes_phase`

## Endogenous Event Classes

The frozen endogenous event classes are:

1. `high_boundary_impulse_J`
   - top quartile of absolute `J`

2. `residual_contraction_low_distance`
   - bottom quartile of `distance`

3. `FES_phase_transition`
   - within-label change in `fes_phase`

These event definitions are fixed before execution.

## Control Schedules

For each endogenous event class:

- `endogenous`
  - uses the observed event positions and matched impulse strengths

- `time_shifted`
  - preserves event count and impulse budget
  - shifts event positions by a fixed deterministic offset

- `random_event`
  - preserves event count and impulse budget
  - assigns event positions randomly under a fixed random seed

Additional reference conditions:

- `unseeded`
- `artificial_seeded`

## Seed Strength / Impulse Budget Matching

The primary controls preserve the number of events and the total impulse
budget of the endogenous event schedule. Event strength is scaled within a
fixed range before execution and then reused by the time-shifted and
random-event controls.

## Leakage Guard

Variables used to define event classes are not used directly as the primary
recovery score.

The primary endpoint is computed from simulated D12/D24 phase-grid recovery,
bounded non-runaway behavior, and non-collapsed differentiation. This prevents
the audit from simply re-detecting the event-definition variable itself.

## Topology Families

Primary:

- `C12(1,2)`

Secondary contrast:

- `C8(1)`

Exploratory polyhedral complements:

- `dodecahedron`
- `icosahedron`

The dodecahedron and icosahedron are not replacements for C12(1,2), nor are
they evidence against Luke's C12/D12RG framework. They are exploratory
FES-derived bridge families, and multiplicity is handled separately.

## D12/D24 and 72 -> 24 -> 12

The primary endpoint is D12/D24 differentiated recovery.

The `72 -> 24 -> 12` readout descent remains theoretically important, but it
is not the primary endpoint in this run. It may be reported secondarily in a
later run if the required data columns and mapping rules are frozen before
execution.

## Subthreshold Noise

Subthreshold randomness is not included in the primary B3 run.

If tested, it should be treated as a separate B3b variant with fixed amplitude,
distribution, threshold, and random seed before execution.

## Positive Interpretation Rule

A primary positive candidate requires all of the following:

- endogenous C12(1,2) differentiated recovery exceeds both time-shifted and
  random-event controls
- bounded non-runaway behavior is preserved
- non-collapsed differentiation is preserved
- late-window stability is preserved
- the endogenous primary p-value survives FDR correction across the endogenous
  primary tests

## Negative Interpretation Rule

A negative result means that the preregistered endogenous IDPC events did not
confirm C12/D24 topology-selective differentiated recovery under this B3
audit.

It does not reject IDPC, D12RG, Luke's framework, or later carrier-readout
variants.

## Reporting Requirements

The report must include:

- primary condition rows
- time-shifted and random-event controls
- C8(1) contrast rows
- exploratory polyhedral rows
- degree-matched null graph rows
- effect sizes
- uncertainty / run-to-run variability
- negative results when present

If a positive signal appears, a later event-class ablation pass may separate:

- boundary impulse seeds only
- residual contraction seeds only
- FES transition seeds only

## Frozen Execution Defaults

- `n_runs = 80`
- `n_null = 80`
- `seed = 20260607`
- `steps = 240`

These may be changed only before execution and must be recorded in the run
artifact if changed.
