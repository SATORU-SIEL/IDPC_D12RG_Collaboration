# Stage B3.2 Mu-Sector Dynamic Expectation Audit Preregistration

## Purpose

Stage B3.2 is a preregistered dynamic diagnostic following Stage B3.1.
It does not rescue or revise the Stage B3 primary result.

Stage B3.1 asked which mu sectors show directional event-conditioned
recovery. Stage B3.2 asks whether those sectors show the dynamic temporal
profiles expected from the cyclotomic / closure-sector interpretation.

## Frozen Status Of Earlier Stages

- Stage B2 remains negative for unanchored autonomous C12(1,2) self-locking.
- Stage B3 remains negative / inconclusive for endogenous-event-conditioned
  differentiated recovery on fixed C12(1,2).
- Stage B3.1 remains a secondary diagnostic with no FDR-confirmed mu-sector
  candidate, but with directional sector-level structure.

## Conditioning Regimes

- endogenous-event conditioned
- time-shifted-event conditioned
- random-event conditioned

## Topologies

- C12(1,2)
- C8(1)
- dodecahedron
- icosahedron

## Primary Mu-Sector Expectation Table

| mu sector | Expected behavior | Candidate event class | Expected temporal profile | Control prediction | Failure / falsification |
|---|---|---|---|---|---|
| mu3 | critical instability / stability | FES transition, high J | brief event-locked instability or variance spike, followed by settling | absent or weaker in time-shifted/random | no event-locked variance/recovery difference vs controls |
| mu4 | eps72-linked closure sector | eps72 restoration onset | post-event recovery or stabilization | reduced under shifted/random eps72 events | same effect appears under random/shifted controls |
| mu5 | transient lift sector | FES transition, h=0, eps72 | brief higher-speed transient, then decay/drop-back | no event-locked transient in controls | no transient signature, or nonselective generic concentration |
| mu6 | dual-chirality ambiguity | h=0, FES transition | oscillatory / switching profile; semi-stable then destabilizing | less oscillatory or non-event-locked in controls | stable monotonic recovery only, or identical oscillation in controls |
| mu8 | contrast / grid artifact check | C8 contrast, h=0 | should not dominate C12-specific effects | C8 may show phase-grid readout without graph-supported closure | mu8 explains C12/D12 effects better than mu12/mu24 |
| mu9 | eps72 / dodecahedral exploratory sector | eps72 restoration onset | post-event directional recovery, especially in dodecahedron | weakened in shifted/random | same effect appears broadly across controls |
| mu10 | transient lift / double fivefold sector | FES transition, eps72 | brief higher-speed transient, then drop-back | no event-locked transient in controls | no transient/drop-back signature, or nonselective generic concentration |
| mu12 | C12 temporal/readout sector | h=0 crossing | event-locked recovery or stabilization after h=0 | absent under phase/time-shift controls | no h=0-specific mu12 advantage |
| mu16 | secondary high-order artifact/contrast sector | none primary; monitor | should not be primary explanatory sector unless event-specific | if present equally in controls, treat as artifact | dominates without event specificity |
| mu20 | fivefold/time interaction sector | h=0, FES transition, dodecahedron | transient or directional recovery, especially in dodecahedral route | weakened under random/shifted | appears independent of event class/topology |
| mu24 | D24 / lifted C12-eps72 sector | eps72 restoration onset | strongest expected eps72-linked post-event sector recovery | reduced under shifted/random eps72 controls | no eps72-specific mu24 advantage, or generic across all events |

## Derived Artifact / Readout Monitors

Following Luke's correction:

- mu60 is not an independent target sector; it is treated as a Phi^12-derived
  artifact / readout monitor.
- mu120 is not an independent target sector; it is treated as a Phi^24-derived
  artifact / readout monitor.

They may be reported secondarily, but they do not define success criteria.

## Dynamic Metrics

For each topology, event class, conditioning regime, and mu sector, B3.2
records:

- post-event sector recovery
- peak delta relative to pre-event baseline
- onset latency to peak
- decay / drop-back from peak to late post-event window
- variance spike / instability score
- oscillatory switching score
- chirality switching score
- endogenous vs time-shifted contrast
- endogenous vs random-event contrast
- graph closed-walk support
- generic phase concentration control

## Interpretation Caveat

The current C12(1,2) graph is a very small board. Failure of a sector to
stabilize should not automatically be read as evidence that the sector is
meaningless. It may mean that the topology lacks enough interlocking degrees
of freedom for that sector to resolve.

## Positive Interpretation Rule

B3.2 is positive only for a sector-level dynamic expectation if:

- the expected sector/event pair shows the predicted temporal-profile score,
- endogenous exceeds both time-shifted and random-event controls,
- the result survives FDR correction across endogenous expectation tests,
- and the pattern is not better explained as generic phase concentration or a
  derived mu60 / mu120 artifact.

## Negative Interpretation Rule

A negative B3.2 result means that the preregistered sector-level dynamic
expectations were not confirmed under this audit. It does not revise the
negative / inconclusive status of B2, B3, or B3.1.

## Frozen Defaults

- n_runs = 80
- seed = 20260607
- steps = 240
- recovery_window = 24
