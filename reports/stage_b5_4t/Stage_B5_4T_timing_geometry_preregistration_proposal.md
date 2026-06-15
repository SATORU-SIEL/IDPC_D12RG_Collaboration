# Stage B5.4T Preregistration Proposal

Subject: Proposed B5.4T timing / geometry decomposition audit before B5.5

Dear Luke, C.A.T., Marcel, Thomas, all,

B5.4S showed that the narrowed C12 stabilization readout remains visible, but aligned +eta phi memory is not yet isolated as the active component.

The strongest B5.4S warning was that the phase-preserving timing-shuffle control was essentially tied with the +eta phi-memory endpoint. This means that B5.5 would be underidentified if it moved directly to a triadic fixed-point interpretation without first separating timing, phase, strength, block structure, event density, and local boundary alignment.

Therefore, I propose:

B5.4T: Timing / Geometry Decomposition Audit.

## Purpose

B5.4T tests which component of phi-derived event geometry is necessary for C12 stabilization.

The audit does not test the full B5.5 triadic fixed-point model.

It is a decomposition gate before B5.5.

## Central Question

Is the C12 stabilization effect carried by:

- exact event timing,
- phi-derived phase,
- event strength,
- phase plus strength,
- timing plus phase,
- timing plus strength,
- label/block event structure,
- total event density,
- dphi event density,
- or local alignment around the phi-derived event?

## Fixed Primary Endpoint

The primary endpoint is the original B5.4/B5.4S phi-derived event geometry:

```
h_i = g_i - mu*a_i - lambda*a_i^3 + eta*phi_(i-1)
event = closed-loop phi sign-switch
eta = 0.075
```

The primary event class is:

```
b54t_original_phi_geometry
```

This condition preserves event timing, phase, and strength.

## Conditions

B5.4T will use the same C12/C8/degree-null evaluation pipeline as B5.4S and change only the event geometry.

### 1. Original Phi Geometry

Preserve timing, phase, and strength.

```
b54t_original_phi_geometry
```

### 2. Timing Only

Preserve event timing, but randomize phase and strength.

```
b54t_timing_only
```

### 3. Phase / Strength Only

Preserve phase and strength, but shuffle timing within label.

```
b54t_phase_strength_only
```

### 4. Phase Only

Preserve phase, but shuffle timing and randomize strength.

```
b54t_phase_only
```

### 5. Strength Only

Preserve strength, but shuffle timing and randomize phase.

```
b54t_strength_only
```

### 6. Timing + Phase

Preserve timing and phase, but randomize strength.

```
b54t_timing_phase
```

### 7. Timing + Strength

Preserve timing and strength, but randomize phase.

```
b54t_timing_strength
```

### 8. Phase + Strength

Preserve phase and strength, but shuffle timing.

```
b54t_phase_strength
```

### 9. Block Structure Only

Preserve label/block event counts, but randomize timing, phase, and strength within block constraints.

```
b54t_block_structure_only
```

### 10. Event Density Only

Preserve only the total event count.

```
b54t_event_density_only
```

### 11. Dphi Density / Block Matched

Use dphi events matched to the phi event density and label/block distribution.

```
b54t_dphi_density_block_matched
```

### 12. Local Alignment Controls

Preserve phase and strength, but shift event timing by:

```
-5, -2, -1, +1, +2, +5 bins
```

These conditions test whether the effect is exact-bin specific or whether it occupies a local alignment window.

## Primary Readouts

The primary readouts are:

- C12 vs shifted/random,
- C12 vs C8,
- C12 vs degree-null,
- bounded differentiated recovery,
- late-window stability.

C12 quadrature error remains a secondary diagnostic.

## Success / Failure Interpretation

B5.4T is not designed around a single "positive" outcome.

The goal is component identification.

If `b54t_original_phi_geometry` is uniquely strongest, the case for aligned phi geometry improves.

If phase-only or phase/strength-only conditions remain close to the original, the effect should be interpreted as phase-bearing event geometry rather than phi memory alone.

If timing-only remains strong, exact event timing may be the dominant component.

If block-only or density-only remains strong, the interpretation must remain much narrower.

If local-shift controls remain close to or stronger than the original, the effect should be interpreted as occupying a local alignment window rather than an exact event bin.

## B5.5 Gate

B5.5 should not proceed as a triadic fixed-point audit until B5.4T identifies the operative C component.

If B5.4T shows that phase-bearing event geometry and local boundary alignment dominate, then B5.5 should define:

```
C = phase-bearing event geometry + local boundary alignment
```

rather than treating C as phi memory alone.

Best,

Satoru
