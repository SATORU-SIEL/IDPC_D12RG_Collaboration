# Stage B5.4T Timing / Geometry Decomposition Results

This report summarizes the preregistered B5.4T timing / geometry decomposition audit.

Preregistration:

`reports/stage_b5_4t/Stage_B5_4T_timing_geometry_preregistration_proposal.md`

Execution script:

`scripts/test_Stage_B5_4T_timing_geometry_decomposition.py`

## Executive Summary

B5.4T narrows the likely active component behind the B5.4S result.

The effect is not explained by event density, block structure, timing alone, strength alone, or dphi density/block matching.

The strongest remaining components are:

- original phi-derived geometry,
- phi-derived phase,
- and local alignment / near-neighbor shifts.

## Primary Endpoint

`b54t_original_phi_geometry`

- recovery: 0.025557
- p vs shifted/random: 0.046263
- p vs C8: 0.007092
- p vs degree-null: 0.002770
- late-window stability: 0.621711
- full C12 quadrature error: 0.003087

## Strong Nearby Conditions

`b54t_local_shift_plus5`

- recovery: 0.026648
- p vs shifted/random: 0.035587
- p vs C8: 0.007092
- p vs degree-null: 0.002770
- late-window stability: 0.613871

`b54t_local_shift_minus1`

- recovery: 0.025857
- p vs shifted/random: 0.049822
- p vs C8: 0.007092
- p vs degree-null: 0.002770
- late-window stability: 0.619126

`b54t_phase_only`

- recovery: 0.027657
- p vs shifted/random: 0.053381
- p vs C8: 0.007092
- p vs degree-null: 0.002770
- late-window stability: 0.364665

## Weakened Controls

`b54t_timing_only`

- recovery: -0.000267
- p vs shifted/random: 0.398577
- p vs C8: 0.631206
- p vs degree-null: 0.781163

`b54t_strength_only`

- recovery: 0.000014
- p vs shifted/random: 0.355872
- p vs C8: 0.156028
- p vs degree-null: 0.515235

`b54t_block_structure_only`

- recovery: -0.000609
- p vs shifted/random: 0.804270
- p vs C8: 0.489362
- p vs degree-null: 0.609418

`b54t_event_density_only`

- recovery: -0.001491
- p vs shifted/random: 0.935943
- p vs C8: 0.879433
- p vs degree-null: 0.631579

`b54t_dphi_density_block_matched`

- recovery: 0.010996
- p vs shifted/random: 0.185053
- p vs C8: 0.007092
- p vs degree-null: 0.080332

## Interpretation

B5.4T suggests that the operative component is not generic event density or block structure.

The effect appears to require phase-bearing event geometry, with local timing tolerance rather than exact-bin exclusivity.

The strongest caution is that `b54t_local_shift_plus5` is slightly stronger than the original phi geometry on the shifted/random timing readout. This motivates B5.4U.

## Released Files

- `Stage_B5_4T_timing_geometry_preregistration_proposal.md`
- `Stage_B5_4T_timing_geometry_summary.md`
- `Stage_B5_4T_timing_geometry_results.csv`
- `Stage_B5_4T_timing_geometry_event_inventory.csv`
- `Stage_B5_4T_timing_geometry_events.csv`
- `Stage_B5_4T_timing_geometry_quadrature.csv`
- `Stage_B5_4T_timing_geometry_temporal.csv`
- `Stage_B5_4T_timing_geometry_raw_conditions.csv`
- `Stage_B5_4T_timing_geometry_nulls.csv`
- `Stage_B5_4T_timing_geometry_verdict.md`
- `scripts/test_Stage_B5_4T_timing_geometry_decomposition.py`
