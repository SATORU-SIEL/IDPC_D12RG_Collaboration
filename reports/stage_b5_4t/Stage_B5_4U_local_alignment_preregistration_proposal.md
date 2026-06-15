# Stage B5.4U Preregistration Proposal

Subject: Proposed B5.4U local alignment and boundary-window audit before B5.5

Dear Luke, C.A.T., Marcel, Thomas, all,

B5.4T is designed to decompose timing, phase, strength, block structure, and event density.

If B5.4T shows that original phi-derived geometry and nearby local shifts remain strong while timing-only, density-only, and block-only controls weaken, then the next required question is not yet B5.5.

The next question is whether the effect is exact-bin specific or whether it occupies a local alignment window around phi-derived phase events.

Therefore, I propose:

B5.4U: Local Alignment and Boundary-Window Audit.

## Purpose

B5.4U tests whether the C12 stabilization effect is tied to:

- exact event timing,
- a local lag window around the event,
- leading versus trailing alignment,
- event-window width,
- or proximity to the h-boundary.

This audit is still a specificity gate before B5.5.

## Fixed Base Event

The base event is the original B5.4T phi-derived event geometry:

```
h_i = g_i - mu*a_i - lambda*a_i^3 + eta*phi_(i-1)
event = closed-loop phi sign-switch
eta = 0.075
```

The primary event class is:

```
b54u_lag_0
```

This condition preserves original timing, phase, and strength.

## Conditions

### 1. Fixed Lag Sweep

Preserve phase and strength, but shift event timing by:

```
-12, -8, -5, -3, -2, -1, 0, +1, +2, +3, +5, +8, +12 bins
```

This tests whether the effect is exact-bin specific or whether it peaks in a local neighborhood.

### 2. Symmetric Event Windows

Preserve phase and strength, but spread each event across symmetric windows:

```
radius = 1, 2, 3, 5, 8 bins
```

Strength is divided by the number of bins in the window so that the event budget is not inflated.

This tests whether a local window representation is stronger than a single-bin event.

### 3. Leading and Trailing Windows

Preserve phase and strength, but spread each event into one-sided windows:

```
leading window: -1, -2, -5 bins through 0
trailing window: 0 through +1, +2, +5 bins
```

Strength is divided by the number of bins in the window.

This tests whether the relevant alignment precedes or follows the nominal phi-derived event.

### 4. Boundary-Distance Strata

Use the original phi-derived event schedule, but split events by local absolute h-boundary distance:

```
near-boundary tercile
middle-boundary tercile
far-boundary tercile
```

The three strata are count-matched to the smallest stratum.

This tests whether events closest to the h-boundary are the ones driving C12 stabilization.

## Primary Readouts

The primary readouts are unchanged:

- C12 vs shifted/random,
- C12 vs C8,
- C12 vs degree-null,
- bounded differentiated recovery,
- late-window stability.

C12 quadrature error remains secondary.

## Interpretation

If lag 0 is uniquely strongest, the effect is exact-event specific.

If nearby lags such as +1, -1, +3, or +5 remain comparable or stronger, then the effect occupies a local alignment window.

If symmetric windows outperform single-bin events, C should be modeled as a local carrier window rather than as a sparse point event.

If leading windows outperform trailing windows, the event may act as a pre-boundary preparation signal.

If trailing windows outperform leading windows, the event may act as post-boundary stabilization.

If near-boundary events outperform middle and far boundary events, then h-boundary proximity is part of the C component.

## B5.5 Gate

B5.5 should use the B5.4U result to define C.

If B5.4U supports a local phase-bearing alignment window, then B5.5 should define:

```
C = phase-bearing event geometry + local boundary-alignment window
```

rather than treating C as phi memory alone or as a single-bin event.

Best,

Satoru
