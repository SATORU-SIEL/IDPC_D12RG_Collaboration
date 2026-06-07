# Stage B3 Endogenous-Event-Conditioned Carrier-Readout Audit Run Manifest

This manifest records the execution parameters used for the run. It does not replace the frozen preregistration document.

## Frozen Design

- input root: `/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction`
- primary event file: `event_level_with_fes_phase_TRUE_RICCI.csv`
- n_runs: 80
- n_null: 80
- random seed: 20260607
- simulation steps: 240
- primary topology: C12(1,2)
- primary discriminator: endogenous vs time-shifted vs random-event schedules on the same C12(1,2) graph
- primary endpoint: differentiated_recovery
- primary readout: D12/D24 differentiated recovery
- 72 -> 24 -> 12 descent is not a primary endpoint in this run.

## Endogenous Event Rules

- high_boundary_impulse_J: top quartile of absolute J in the event-level IDPC table
- residual_contraction_low_distance: bottom quartile of distance in the event-level IDPC table
- FES_phase_transition: within-label change of FES phase

## Leakage Guard

The variables defining event classes are not used directly as the primary recovery score. The primary score is topology-readout recovery from simulated D12/D24 phase-grid behavior.

## Controls

- time-shifted event schedule preserving event count and impulse budget
- random-event schedule preserving event count and impulse budget
- unseeded reference
- artificial seeded reference
- C8(1) non-D12 contrast
- dodecahedron / icosahedron exploratory polyhedral complements
- degree-matched directed random graphs as secondary null floors

## Positive Interpretation Rule

A primary positive candidate requires endogenous C12(1,2) differentiated recovery to exceed both time-shifted and random-event controls, preserve bounded non-runaway behavior, preserve non-collapsed differentiation, preserve late-window stability, and survive FDR across endogenous primary tests.

## Negative Interpretation Rule

A negative result means that the preregistered endogenous IDPC events did not confirm C12/D24 topology-selective differentiated recovery under this B3 audit. It does not reject IDPC, D12RG, or later carrier-readout variants.
