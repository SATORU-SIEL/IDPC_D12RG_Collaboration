# Stage B Exploratory GKS / Kuramoto Carrier-Realization Summary

## Purpose

Stage B is exploratory. It asks whether broader carrier-realization motifs, including GKS N=24, sin/cos dual readouts, 8/12/24 lift overlap, and Kuramoto/Ricci synchronization summaries, show descriptive structure in IDPC-derived outputs.

## Scope

These tests do not rescue Stage A negative D12-specific results and do not confirm D12RG. They are hypothesis-generating only.

## Results

- GKS N=24 phase rows: 96
- GKS N=24 phase rows with FDR q<=0.05: 47
- observed GKS phase rows with FDR q<=0.05: 5
- 8/12/24 lift rows: 96
- 8/12/24 lift rows with FDR q<=0.05: 47
- observed lift rows with FDR q<=0.05: 5
- Kuramoto / oscillator summary rows: 20

## Strongest Observed GKS Phase Rows

- IDPC_Reproduction/Chapter3/ricci_eps72_restoring_test.csv / eps72_deg: p=0, q=0, R_D24=0.933895, R_D12=0.752933, R_D8=0.503374
- IDPC_Reproduction/Chapter3/ricci_eps72_restoring_test.csv / deps72_deg: p=0, q=0, R_D24=0.877665, R_D12=0.584163, R_D8=0.284453
- IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv / phase: p=2.14605e-197, q=8.58422e-197, R_D24=0.0289147, R_D12=0.925183, R_D8=0.0164119
- IDPC_Reproduction/Chapter3/ricci_phase_sync_summary.csv / circ_mean_deg: p=1.55304e-43, q=4.14144e-43, R_D24=0.988846, R_D12=0.955975, R_D8=0.903105
- IDPC_Reproduction/Chapter3/ricci_phase_sync_summary.csv / mean_abs_dpsi_deg: p=1.19237e-37, q=2.60154e-37, R_D24=0.985634, R_D12=0.943514, R_D8=0.876506
- IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv / phase_z: p=1, q=1, R_D24=0.0011551, R_D12=0.00061372, R_D8=0.00338658
- IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv / phi: p=1, q=1, R_D24=0.0011551, R_D12=0.00061372, R_D8=0.00338658
- IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv / dphi: p=1, q=1, R_D24=0.0011551, R_D12=0.00061372, R_D8=0.00338658

## Strongest Observed 8/12/24 Lift Rows

- IDPC_Reproduction/Chapter3/ricci_eps72_restoring_test.csv / eps72_deg: score=2.83669, p=0.000999001, q=0.00204051
- IDPC_Reproduction/Chapter3/ricci_eps72_restoring_test.csv / deps72_deg: score=1.19414, p=0.000999001, q=0.00204051
- IDPC_Reproduction/Chapter3/ricci_phase_sync_summary.csv / circ_mean_deg: score=5.87299, p=0.000999001, q=0.00204051
- IDPC_Reproduction/Chapter3/ricci_phase_sync_summary.csv / mean_abs_dpsi_deg: score=6.77314, p=0.000999001, q=0.00204051
- IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv / phase: score=0.954635, p=0.000999001, q=0.00204051
- IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv / phase_z: score=3.15451e-11, p=1, q=1
- IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv / phi: score=3.15451e-11, p=1, q=1
- IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv / dphi: score=3.15451e-11, p=1, q=1

## Interpretation

Some observed Stage B exploratory rows survive FDR. Because Stage B was explicitly exploratory and uses broader carrier-realization motifs, these results should be treated as candidates for a new pre-registered follow-up, not as confirmation.
The strongest rows are phase/restoration quantities that are already constructed to express phase locking or residual restoration, so the signal may reflect IDPC's existing phase geometry rather than a specific GKS/D12RG carrier.
Kuramoto/Ricci synchronization rows are summarized descriptively; they should not be interpreted as topology confirmation without a separate network-level model.
