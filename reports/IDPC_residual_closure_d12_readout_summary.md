# Residual Closure D12 Readout Test

## Purpose

This structural-layer test asks whether IDPC residual closure or contraction subsets are closer to fixed D12 readout positions than matched random subsets, phase rotations, and alternative cyclic partitions.

## Results

- tested rows: 38
- observed tested rows: 5
- control tested rows: 28
- FDR q<=0.05 rows: 0
- observed FDR q<=0.05 rows: 0
- control FDR q<=0.05 rows: 0
- observed rows where D12 ranked first among partitions: 0
- observed rows where fixed D12 origin ranked first among rotations: 5

## Observed Rows

- IDPC_Reproduction/Chapter3/ricci_eps72_restoring_test.csv / eps72_restore: distance=6.65767 deg, p=0.123876, q=0.65959, D12 partition rank=4, rotation rank=1
- IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv / low_distance_q25: distance=1.72321 deg, p=0.723277, q=0.996247, D12 partition rank=4, rotation rank=1
- IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv / high_r_local_q25: distance=1.78054 deg, p=0.789211, q=0.996247, D12 partition rank=3, rotation rank=1
- IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv / high_r_local_z_q25: distance=1.91704 deg, p=0.887113, q=0.996247, D12 partition rank=3, rotation rank=1
- IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv / low_distance_z_q25: distance=1.89424 deg, p=0.888112, q=0.996247, D12 partition rank=3, rotation rank=1

## Interpretation

Observed residual-closure rows do not survive the combined random subset, rotation, partition, and FDR checks as D12-specific.
