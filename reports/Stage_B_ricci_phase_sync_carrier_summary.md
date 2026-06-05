# Stage B Ricci Oscillation / Phase Synchronization Carrier Summary

## Purpose

This exploratory Stage B test connects the carrier-realization question directly to the IDPC paper's Ricci oscillation, phase synchronization, and eps72 restoring outputs.

## Scope

The results are exploratory. They can suggest a follow-up target, but they do not confirm D12RG, GKS N=24, or a physical carrier.

## Results

- Ricci phase-sync files tested: 10
- observed phase-sync files tested: 1
- observed phase-sync files with D24/D12 FDR q<=0.05: 1
- eps72 restoring rows tested: 20
- observed eps72 restoring rows tested: 2
- observed eps72 restoring rows with D24 FDR q<=0.05: 2

## Observed Ricci Phase Sync

- IDPC_Reproduction/Chapter3/ricci_phase_sync_summary.csv: psi_lock_R_mean=0.694143, mean_abs_dpsi=38.991 deg, D24 q=1.7256e-43, D12 q=1.41523e-22, R_D24=0.988846, R_D12=0.966131

## Observed eps72 Restoring

- IDPC_Reproduction/Chapter3/ricci_eps72_restoring_test.csv / eps72_deg: restore_rate=0.733846, D24 q=0, R_D24=0.922248, restore_D24_distance=3.47643 deg
- IDPC_Reproduction/Chapter3/ricci_eps72_restoring_test.csv / deps72_deg: restore_rate=0.733846, D24 q=5.71676e-186, R_D24=0.843552, restore_D24_distance=3.53415 deg

## Interpretation

Ricci phase synchronization / eps72 restoration shows strong D24/D12-structured concentration in observed files. This is the most direct Stage B connection to the IDPC paper so far.
However, these quantities are already phase-synchronization and restoration readouts inside IDPC. The result therefore supports a carrier-readout follow-up hypothesis, not a confirmation of the carrier.
