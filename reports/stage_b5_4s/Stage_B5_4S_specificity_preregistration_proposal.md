# Stage B5.4S Preregistration Proposal

Subject: Proposed B5.4S specificity audit: phi-memory specificity under block-matched and differential-event controls

Dear Luke, Marcel, Thomas, C.A.T., all,

B5.4R constrained the B5.4 interpretation rather than simply strengthening it.

The +eta closed-loop phi memory endpoint reproduced the narrowed B5.4 direction, but adversarial controls were not fully separated. In particular, event-block shuffled phi memory and one count-matched dphi control remained close enough that B5.4R should not be read as a clean confirmation of phi-memory specificity.

Therefore, before moving to B5.5, I propose an intermediate audit:

B5.4S: B5.4 Specificity Audit.

Here, "S" stands for specificity.

The purpose of B5.4S is to test whether aligned +eta phi memory remains stronger when event count, event-block distribution, and differential-event density are explicitly controlled.

## Primary Question

Does the B5.4/B5.4R closed-loop phi-memory effect depend specifically on aligned phi memory, or can it be reproduced by:

- the same event schedule with phase/strength disruption,
- event-block structure,
- timing permutation,
- or count-matched differential-event structure?

## Fixed Primary Endpoint

The primary endpoint remains the narrowed B5.4/B5.4R endpoint:

```
h_i = g_i - mu*a_i - lambda*a_i^3 + eta*phi_(i-1)
event = closed-loop phi sign-switch
eta = 0.075
```

The primary event class is:

```
b54s_plus_phi_memory
```

This is the aligned +eta closed-loop phi-memory sign-switch condition.

## Controls

B5.4S will keep the C12 evaluation pipeline fixed and change only the event schedule / phase / strength structure.

### 1. Same-Schedule Phase/Strength Shuffle

Use the same task timing as the +eta phi-memory event schedule, but permute phase and strength within label.

This tests whether timing alone explains the effect.

Expected specificity pattern:

```
b54s_plus_phi_memory > b54s_same_schedule_phase_strength_shuffle
```

### 2. Same-Schedule Random Phase/Strength

Use the same task timing as the +eta phi-memory event schedule, but replace phase and strength with random matched values.

This tests whether the effect depends on phi-derived phase and strength rather than only on event timing.

Expected specificity pattern:

```
b54s_plus_phi_memory > b54s_same_schedule_random_phase_strength
```

### 3. Phase-Preserving Timing Shuffle

Preserve the original phase and strength values but shuffle event timing within label.

This tests whether aligned timing is required.

Expected specificity pattern:

```
b54s_plus_phi_memory > b54s_phase_preserving_timing_shuffle
```

### 4. Block-Permuted Event Schedule

Permute event blocks within label while preserving within-block event structure.

This tests whether the B5.4/B5.4R result is carried mainly by event-block structure.

Expected specificity pattern:

```
b54s_plus_phi_memory > b54s_block_permuted_schedule
```

### 5. Block-Matched Shuffled Phi Memory

Use shuffled phi-memory sign-switches, sampled to match the +eta phi-memory label/block event counts.

Expected specificity pattern:

```
b54s_plus_phi_memory > b54s_block_matched_shuffled_phi_memory
```

### 6. Block-Matched Event-Block-Shuffled Phi Memory

Use event-block-shuffled phi-memory sign-switches, sampled to match the +eta phi-memory label/block event counts.

This directly targets the strongest warning control from B5.4R.

Expected specificity pattern:

```
b54s_plus_phi_memory > b54s_block_matched_event_block_shuffled_phi
```

### 7. Block/Density-Matched Differential Events

Use dphi and d2phi feedback sign-switch schedules sampled to match the +eta phi-memory label/block event counts.

This directly targets the count-matched dphi warning from B5.4R.

Expected specificity pattern:

```
b54s_plus_phi_memory > b54s_block_density_matched_dphi
b54s_plus_phi_memory > b54s_block_density_matched_d2phi
```

The dphi block/density-matched control will also be repeated across several random matched draws because B5.4R showed that one count-matched dphi draw could become positive.

### 8. Block-Matched Lag-Shifted Phi Memory

Use lag-shifted phi-memory sign-switches, sampled to match the +eta phi-memory label/block event counts.

This tests whether the memory term must be temporally aligned.

Expected specificity pattern:

```
b54s_plus_phi_memory > b54s_block_matched_lag_shifted_phi
```

## Primary Readouts

The primary readouts remain the same as B5.4R:

- C12 vs shifted/random timing controls,
- C12 vs C8,
- C12 vs degree-null,
- late-window stability,
- bounded differentiated recovery,
- C12 quadrature error as a secondary diagnostic.

## Success Criteria

B5.4S supports phi-memory specificity only if:

```
b54s_plus_phi_memory
```

remains stronger than the block-matched and differential-event controls on the topology-specific endpoints.

The most important comparisons are:

```
b54s_plus_phi_memory > b54s_block_matched_event_block_shuffled_phi
b54s_plus_phi_memory > b54s_block_density_matched_dphi
b54s_plus_phi_memory > b54s_same_schedule_phase_strength_shuffle
```

A strong result would show:

- lower p vs shifted/random for +eta phi memory,
- lower p vs degree-null for +eta phi memory,
- stronger C12 vs C8 separation for +eta phi memory,
- improved late-window stability for +eta phi memory,
- and no comparable improvement under block-matched shuffled phi or block/density-matched dphi controls.

## Failure Criteria

B5.4S weakens the phi-memory-specific interpretation if any of the following occur:

- same-schedule phase/strength shuffle performs as well as +eta phi memory,
- block-permuted events perform as well as +eta phi memory,
- block-matched shuffled phi memory performs as well as +eta phi memory,
- block-matched event-block-shuffled phi memory performs as well as +eta phi memory,
- block/density-matched dphi performs as well as +eta phi memory,
- lag-shifted phi memory performs as well as aligned phi memory.

In that case, B5.4/B5.4R should be interpreted more narrowly as structured event-block or differential-event stabilization, not as phi-memory-specific stabilization.

## Interpretation Boundary

B5.4S is not B5.5.

It does not introduce a broader triadic fixed-point architecture and does not introduce C12-aware adaptive weighting.

It is a specificity gate.

If B5.4S succeeds, then B5.5 becomes better justified as a triadic fixed-point audit.

If B5.4S fails, then the B5.4/B5.4R interpretation should remain narrowed to event-structure-sensitive C12 stabilization.

Best,

Satoru
