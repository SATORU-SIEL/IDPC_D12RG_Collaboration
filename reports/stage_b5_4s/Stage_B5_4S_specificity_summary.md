# Stage B5.4S Specificity Audit Results

This report summarizes the preregistered B5.4S specificity audit.

The preregistration was committed before execution as:

`reports/stage_b5_4s/Stage_B5_4S_specificity_preregistration_proposal.md`

## Executive Summary

B5.4S does not support a clean positive claim for aligned phi-memory specificity.

The aligned +eta phi-memory endpoint remains positive in the expected topology-specific directions, especially against C8 and degree-null controls.

However, the phase-preserving timing-shuffle control is essentially tied with the +eta phi-memory endpoint and is slightly stronger on the shifted/random timing readout.

Therefore, the B5.4/B5.4R/B5.4S result should be interpreted conservatively:

B5.4/B5.4R/B5.4S support a robust narrowed C12 stabilization readout, but the active component is not yet isolated as aligned phi memory. The effect may be carried by phi-derived event geometry, especially timing, phase, strength, block structure, or local boundary alignment.

## Execution Settings

- eta: 0.075
- block size: 50
- n_runs: 140
- n_null_graphs: 60
- n_null_runs: 6
- temporal_runs: 100
- quadrature_runs: 80
- steps: 240
- seed: 54501

## Primary Endpoint

`b54s_plus_phi_memory`

- recovery: 0.025281
- p vs shifted/random: 0.060498
- p vs C8: 0.007092
- p vs degree-null: 0.002770
- late-window stability: 0.612153
- full C12 quadrature error: 0.002392

This preserves the narrowed B5.4/B5.4R direction, but it does not isolate phi-memory specificity.

## Strongest Warning Control

`b54s_phase_preserving_timing_shuffle`

- recovery: 0.025291
- p vs shifted/random: 0.039146
- p vs C8: 0.007092
- p vs degree-null: 0.005540
- late-window stability: 0.604022
- full C12 quadrature error: 0.005809

This control preserves phi-derived phase and strength while shuffling timing within label.

Because this control is essentially tied with the primary endpoint, B5.4S does not meet the primary specificity criterion.

## Other Controls

Several adversarial controls weaken substantially:

- same-schedule random phase/strength: recovery -0.000607, p vs shifted/random 0.768683
- block-density matched dphi: recovery -0.002687, p vs shifted/random 0.982206
- block-matched shuffled phi memory: recovery 0.007517, p vs shifted/random 0.163701
- block-matched event-block-shuffled phi: recovery 0.014183, p vs shifted/random 0.843416

This means the effect is not explained by completely random phase/strength, raw event density alone, or the weakest shuffled/differential controls.

The unresolved issue is more specific:

phi-derived phase/strength/timing geometry remains too close to the aligned +eta phi-memory endpoint.

## Interpretation

B5.4S is a useful constraint rather than a failed experiment.

It shows that the narrowed C12 stabilization readout is robust enough to survive multiple adversarial decompositions, but it also shows that the current evidence does not justify moving directly to B5.5 as a clean triadic fixed-point positive.

The active component may be:

- aligned phi memory,
- phi-derived phase/strength geometry,
- local event timing,
- label/block event structure,
- boundary alignment,
- or a combination of these.

These components must be separated before the broader B5.5 triadic fixed-point audit.

## Proposed Next Step

The next audit should be B5.4T:

Timing / Geometry Decomposition Audit.

B5.4T should explicitly decompose:

- exact event timing,
- phase,
- strength,
- label/block event structure,
- event density,
- and local boundary alignment.

The purpose is to identify which component is necessary for C12 stabilization.

If original +eta phi memory is uniquely strongest, phi-memory specificity becomes more plausible.

If timing plus phase/strength explains most of the effect, then B5.5 should be reframed around phi-derived event geometry rather than phi memory alone.

If block structure or event density explains the effect, the interpretation should remain narrower.

## Released Files

- `Stage_B5_4S_specificity_preregistration_proposal.md`
- `Stage_B5_4S_specificity_summary.md`
- `Stage_B5_4S_specificity_results.csv`
- `Stage_B5_4S_specificity_event_inventory.csv`
- `Stage_B5_4S_specificity_events.csv`
- `Stage_B5_4S_specificity_quadrature.csv`
- `Stage_B5_4S_specificity_temporal.csv`
- `Stage_B5_4S_specificity_raw_conditions.csv`
- `Stage_B5_4S_specificity_nulls.csv`
- `scripts/test_Stage_B5_4S_specificity_audit.py`
- `scripts/stage_b5_4_phi_utils.py`
