# Stage A+ Structural Holonomy Loop Test

## Purpose

This test adapts the closed-loop / holonomy idea to the IDPC structural layer. It tests the fixed loop phi_t -> J_t -> residual_t -> FES_t -> phi_(t+1).

## Loop Definition

`H = phi_phase_t + J_phase_t + residual_phase_t + FES_phase_t - phi_phase_(t+1)`

The null model circularly shifts J, residual, and FES phases within each label/session while keeping phi order fixed.

## Results

- tested files: 7
- observed tested files: 1
- control tested files: 5
- holonomy concentration FDR q<=0.05 files: 0
- closure-error FDR q<=0.05 files: 0
- roots-uniformity FDR q<=0.05 files: 0
- observed files where D12 ranked first among ring controls: 0

## Observed Rows

- IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv: loops=200, R=0.0976707, R p=0.153846, R q=0.54021, closure p=0.0679321, D12 ring rank=3.0, best ring=D8

## Interpretation

The fixed Stage A+ structural loop does not survive the current circular-shift FDR controls as a positive holonomy/closure result.
D12 does not rank first among the tested ring controls for observed files, so this run does not support D12-specific loop closure.
