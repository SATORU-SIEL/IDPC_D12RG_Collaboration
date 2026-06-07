# Stage B3 Endogenous-Event-Conditioned Carrier-Readout Audit Run Manifest

This manifest records the execution parameters used for the run. It does not replace the frozen preregistration document.

## Frozen Design

- input root: `/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction`
- primary event file: `event_level_with_fes_phase_TRUE_RICCI.csv`
- h=0 source file: `Chapter7/new_phi_dataset.csv`
- eps72 source file: `Chapter3/ricci_eps72_restoring_test.csv`
- Ricci phase-sync source file: `Chapter3/ricci_phase_sync_summary.csv`
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
- h_zero_crossing: within-session sign crossing of the h=0 availability boundary
- eps72_restoration_onset: within-session restore 0->1 onset in the eps72 restoration table
- ricci_phase_sync_high_lock_session: top-quartile session-level psi_lock_R proxy for Ricci phase-sync increase events, because the available source is a session summary rather than an event-level increase series

## Event Inventory

event_class,source_file,event_rule,n_events,n_labels,min_task_idx,max_task_idx,mean_strength_raw
FES_phase_transition,event_level_with_fes_phase_TRUE_RICCI.csv,within-label change of FES phase,192,26,2.0,27.0,1.0
eps72_restoration_onset,Chapter3/ricci_eps72_restoring_test.csv,within-session restore 0->1 onset in eps72 restoration table,147,26,0.0,27.0,29.686857716802688
h_zero_crossing,Chapter7/new_phi_dataset.csv,within-session sign crossing of h=0 availability boundary,1309,26,1.0,417.0,0.015761526129687082
high_boundary_impulse_J,event_level_with_fes_phase_TRUE_RICCI.csv,top quartile of absolute J in the event-level IDPC table,57,24,1.0,27.0,0.2043949459783551
residual_contraction_low_distance,event_level_with_fes_phase_TRUE_RICCI.csv,bottom quartile of distance in the event-level IDPC table,57,23,1.0,27.0,0.13130340826966425
ricci_phase_sync_high_lock_session,Chapter3/ricci_phase_sync_summary.csv,top quartile session-level Ricci psi_lock_R proxy for phase-sync increase events,7,7,12.0,14.0,0.8280658072221362

## Input Hashes

relative_path,absolute_path,bytes,sha256
event_level_with_fes_phase_TRUE_RICCI.csv,/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv,103144,1096c6797ef8588cf116526f93c45b4225931954f79d44c13e6931bbf6234c13
Chapter7/new_phi_dataset.csv,/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction/Chapter7/new_phi_dataset.csv,2988942,516d766f4b75f37cebae8b3fc2a2d47400f68ac0817feab8576236dc42542500
Chapter3/ricci_eps72_restoring_test.csv,/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction/Chapter3/ricci_eps72_restoring_test.csv,28428,2218aeb2420c286ca155c031c36702002c2bc2abc86b248876f65093c6882029
Chapter3/ricci_phase_sync_summary.csv,/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction/Chapter3/ricci_phase_sync_summary.csv,2756,27b356673793fd51dc359ae6e96265d0c8786d00727cab5a481dac4f08f19e0a

## Luke/C.A.T. Alignment

This rerun keeps C12(1,2) fixed as the primary topology and changes only the IDPC event-conditioning classes. It keeps bounded differentiated recovery as the primary endpoint and does not introduce subthreshold-noise or V4-process variants into the frozen B3 run.

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
