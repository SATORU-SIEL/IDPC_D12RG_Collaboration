# Stage B5.4R Replication and Robustness Audit Results

This report summarizes the preregistered B5.4R replication / robustness audit. The preregistration was committed before execution as `reports/stage_b5_4r/Stage_B5_4R_updated_preregistration_proposal.md`.

## Interpretation

B5.4R gives a mixed result.

The narrowed +eta closed-loop phi memory endpoint reproduces the main B5.4 direction: C12 remains stronger than C8 and degree-null, and shifted/random timing is positive at the preregistered audit level.

However, adversarial controls are not fully separated. In particular, the event-block shuffled phi memory control remains close to the +eta phi memory endpoint, and one count-matched dphi control is also positive against shifted/random. Therefore B5.4R should not be interpreted as a clean confirmation of phi-memory specificity.

The conservative reading is:

B5.4R supports the robustness of a narrowed closed-loop phi sign-switch C12 stabilization readout, but it also shows that part of the effect may be carried by event-block structure or matched differential-event structure. This constrains, rather than simply strengthens, the B5.4 interpretation.

## Primary Endpoint

`b54r_plus_phi_memory`

- n seed events: 502
- recovery: 0.025674
- effect vs shifted: +0.007072
- effect vs random: +0.006280
- effect vs C8: +0.030749
- effect vs degree-null mean: +0.009107
- p vs shifted/random: 0.042705
- p vs C8: 0.007092
- p vs degree-null: 0.005540
- mean late-window stability: 0.616069
- quadrature error, full C12(1,2): 0.004037

## Main Warnings

`b54r_event_block_shuffled_phi_memory`

- recovery: 0.024674
- effect vs degree-null mean: +0.009958
- p vs shifted/random: 0.046263
- p vs degree-null: 0.002770
- quadrature error, full C12(1,2): 0.001588

`b54r_countmatched_dphi_1`

- recovery: 0.019509
- p vs shifted/random: 0.032028
- p vs degree-null: 0.011080

These controls prevent a strong claim that the effect is uniquely phi-memory-specific.

## Adversarial Pattern

Selected controls:

- eta = 0: recovery 0.015072, p vs shifted/random 0.227758, p vs degree-null 0.055402
- -eta phi memory: recovery 0.019921, p vs shifted/random 0.743772, p vs degree-null 0.008310
- shuffled phi memory: recovery 0.006185, p vs shifted/random 0.224199, p vs degree-null 0.479224

## Quadrature Audit

The C12 quadrature audit is also mixed. The +eta phi memory condition has low full-topology quadrature error, but it is not uniquely minimal. Event-block shuffled, lag-shifted, and -eta conditions can be comparable or lower.

The hexagonal bypass delta is negative across conditions, meaning the full C12(1,2) topology reduces quadrature error relative to the ring-only readout in this proxy. This suggests that the bypasses may help quadrature-like organization, but the effect is not specific to +eta phi memory.

## Files

- `Stage_B5_4R_replication_robustness_results.csv`
- `Stage_B5_4R_replication_robustness_event_inventory.csv`
- `Stage_B5_4R_replication_robustness_quadrature.csv`
- `Stage_B5_4R_replication_robustness_raw_conditions.csv`
- `scripts/test_Stage_B5_4R_replication_robustness.py`

## Bottom Line

B5.4R is not a clean positive for phi-memory specificity. It is a useful adversarial replication: the +eta phi memory endpoint remains positive, but the nearby adversarial controls show that B5.5 should not proceed as a simple expansion until event-block and count-matched differential-event structure are separated more cleanly.
