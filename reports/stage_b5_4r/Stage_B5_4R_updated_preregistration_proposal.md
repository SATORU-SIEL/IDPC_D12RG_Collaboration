# Updated B5.4R Preregistration Proposal

Subject: Updated B5.4R preregistration proposal: replication, adversarial controls, and C12 quadrature audit

Dear Luke, Marcel, Thomas, C.A.T., all,

Thank you for the careful feedback.

I think the interpretation boundary for B5.4 is now clear.

B5.4 should not be read as broad Phi/FES-family confirmation, D12RG confirmation, C12 carrier closure, or stable topology closure.

The narrower result is:

closed-loop phi sign-switch appears to produce selective C12 stabilization under this audit.

The reason this remains interesting is that the strongest improvements appeared in the topology-specific endpoints:

- degree-null separation improved,
- C12 vs C8 remained strong,
- and count-matched dphi controls remained negative.

At the same time, the caution is also clear:

- the broader FES phase-transition and cluster-transition rows did not reproduce the effect,
- shifted/random timing controls were only partially stable,
- and late-window stability improved but did not justify a claim of stable carrier closure.

So before moving to a broader B5.5 triadic fixed-point architecture, I propose an intermediate preregistered audit:

B5.4R: B5.4 Replication and Robustness Audit.

Here, "R" stands for replication and robustness.

The purpose of B5.4R is not to expand the model.

The purpose is to test whether the B5.4 effect depends specifically on phi memory, or whether any comparable weak autoregressive feedback term can produce the same apparent C12 selectivity.

I will preregister this plan before execution.

The core question is:

Does the stabilization depend specifically on closed-loop phi memory, or is it reproduced by generic weak feedback / self-consistency operators?

## 1. Fixed Baseline Replication

First, reproduce the narrowed B5.4 endpoint exactly:

```text
h_i = g_i - mu*a_i - lambda*a_i^3 + eta*phi_(i-1)
```

```text
event = closed-loop phi sign-switch
```

The primary readouts remain:

- C12 vs degree-null
- C12 vs C8
- shifted/random timing controls
- count-matched dphi controls
- late-window stability

This is the direct B5.4 replication condition.

## 2. Eta Sign And Zero Controls

Run the same endpoint under:

- eta = 0
- eta = +fixed
- eta = -fixed

The expected pattern is:

- eta = +fixed should preserve or improve the B5.4 result.
- eta = 0 should reduce the closed-loop advantage.
- eta = -fixed should weaken or reverse the effect.

This tests whether the result depends on the direction of phi feedback rather than merely on adding a small autoregressive term.

## 3. Phi Memory Disruption Controls

Run:

- shuffled phi_(i-1)
- lag-shifted phi_(i-k)
- session-shuffled phi memory
- event-block-shuffled phi memory

The expected pattern is:

true aligned phi memory should outperform shuffled and misaligned phi memory.

If shuffled or lag-misaligned phi performs equally well, then the B5.4 result may reflect generic smoothing or event-density structure rather than meaningful closed-loop memory.

## 4. Non-Phi Feedback Controls

Replace phi_(i-1) with comparable non-phi feedback terms:

- dphi_(i-1)
- d2phi_(i-1)
- deps_(i-1)
- dh_(i-1)
- a_(i-1)
- random matched autoregressive noise

The form remains fixed:

```text
h_i = g_i - mu*a_i - lambda*a_i^3 + eta*X_(i-1)
```

where X is the tested feedback variable.

The expected pattern is:

phi feedback should outperform non-phi feedback terms on topology-specific endpoints.

If dphi, d2phi, deps, dh, a, or random AR feedback produce the same result, then B5.4 should be interpreted as generic weak-feedback stabilization rather than phi-specific stabilization.

## 5. Split Stability

Evaluate whether the narrowed B5.4 result is stable across:

- session / file splits
- participant-label splits
- early versus late task blocks
- event-count matched subsets
- event-block resampling

The key question is whether the effect is carried by a small number of files or event clusters, or whether it remains visible across independent partitions.

## 6. Luke's C12 Quadrature Audit

Luke raised an important structural point about C12(1,2).

The concern is that C12(1,2) may effectively contain a pair of opposing unidirectional C12 rings, connected through unidirectional hexagonal bypasses that may either support or conflict with one another.

Therefore B5.4R should include an internal C12 quadrature audit.

The question is:

Do the clockwise and anticlockwise components of C12(1,2) settle, or can they be made to settle, into a 90-degree phase difference?

If one clockwise path can be shown to be exactly 90 degrees out of phase with the anticlockwise path, then the C12 response may be interpreted as:

```text
V(GKS) = Vsin(D12RG) + Vcos(D12RG)
```

or equivalently:

```text
exp(i theta) = cos(theta) + i sin(theta)
```

The quadrature audit will therefore test:

- clockwise C12 path component,
- anticlockwise C12 path component,
- phase difference between opposing components,
- distance from 90-degree phase separation,
- and whether the hexagonal bypasses help or hinder that separation.

A possible readout is:

```text
quadrature_error = abs(wrap(delta_phase - pi/2))
```

A stronger B5.4R result would show:

- quadrature_error decreases after closed-loop phi sign-switch events,
- and this decrease is stronger for +eta phi feedback than for eta = 0, -eta, shuffled phi, lagged phi, and non-phi feedback controls.

This quadrature audit remains secondary, but it may explain why C12(1,2), rather than C8 or degree-null topologies, responds to the narrowed closed-loop phi endpoint.

## 7. Primary Success Criteria

A strong B5.4R result would show:

- +eta phi feedback reproduces the B5.4 pattern,
- eta = 0 is weaker,
- -eta is weaker or reversed,
- shuffled / lagged phi memory is weaker,
- non-phi feedback controls are weaker,
- count-matched dphi remains negative,
- C12 vs C8 remains positive,
- degree-null separation remains positive,
- shifted/random timing controls improve or remain directionally supportive,
- and C12 quadrature error decreases specifically under the +eta phi condition.

## 8. Failure Criteria

B5.4R should be considered weakened if:

- eta = 0 performs the same as +eta,
- -eta performs the same as +eta,
- shuffled phi performs the same as aligned phi,
- dphi / d2phi / deps / dh / a feedback performs the same as phi feedback,
- random AR feedback performs the same as phi feedback,
- the result is carried by only one file, one participant group, or one event block,
- or quadrature error does not improve under the +eta phi condition.

## 9. Interpretation Boundary

If B5.4R succeeds, the interpretation becomes stronger:

closed-loop phi memory appears to contribute specifically to selective C12 stabilization, and may organize the internal C12(1,2) response toward quadrature-like structure.

If B5.4R fails, the interpretation becomes narrower:

B5.4 may reflect generic weak-feedback stabilization, event-schedule structure, or a topology readout that is not phi-memory specific.

Either outcome is useful.

B5.4R therefore functions as an adversarial replication step before B5.5.

Only after B5.4R should we move to the broader triadic fixed-point audit:

```text
A = P_A(C)
B = P_B(C)
C = I(A,B)
```

In that sense, B5.4R is not a new architecture.

It is the preregistered robustness gate that decides whether B5.5 is justified.

Best,

Satoru
