# Stage B7.4b Preregistration Email

Status: sent before formal Stage B7.4b-A execution.

- Gmail message id: `19eee06bbf61ef58`
- Gmail thread id: `19eee06bbf61ef58`
- Gmail timestamp: `2026-06-22T06:31:18`
- Subject: `B7.4b Proposal: Held-out C12 Validation and Dynamic Factor-of-12 Route-Carrier Specification Freeze`
- To: `d12rg@googlegroups.com, nunnchris612@gmail.com`

## Sent Body

Dear Luke, Thomas, Marcel, C.A.T., Chris, Alex, all,

Based on the B7.4 / B7.4a results and the subsequent discussion, I would like to organize the next plan as B7.4b.

B7.4 and B7.4a did not support the strong Vacuum-layer / quadrature / explicit 3-fold hypotheses under the current operationalizations.

But I think this was useful, because it clarified which questions should now be separated.

At this point, I think we should split the next step into two parts:

- Strengthen the empirical boundary on the C12 side.
- Redefine the H24 / Phi24 side not as a static edge-level topology, but as a dynamic factor-of-12 route-carrier.

## B7.4b-A: Held-out C12 validation

Goal: validate the B7.3a C12 topology-readout using held-out / leave-one-session testing.

Primary representation:

- `receiver_standpoint_magnitude_c`

Controls:

- no-topology
- reversed C12
- side-broken C12
- shuffled C12
- C10/C11/C13/C14
- time-shifted events
- random event schedules

Primary questions:

- Does frozen R* + C12 survive held-out / leave-one-session validation?
- Does C12 beat no-topology out-of-sample?
- Does side-correspondence remain necessary?
- Does ring-orientation remain unresolved if reversed C12 stays close to forward C12?

Expected interpretation boundary:

If C12 survives held-out validation but reversed remains close, the conclusion should be:

`C12 topology-readout is supported, but ring-orientation specificity remains unresolved.`

## B7.4b-B: Dynamic factor-of-12 route-carrier specification freeze

Goal: do not rerun the old H24 / Phi24 edge-level audit as-is. Instead, update the specification after the Luke / Thomas clarification.

Before execution, freeze deterministic rules for:

- node delay
- edge length / propagation time
- state-dependent drive / suppression
- left/right active ring-set selection rule
- shared node/edge rule for swap / share / write / compare
- Phi^N / Phi^-N pairing rule
- factor-of-12 simultaneous route rule
- whether Hadamard-only primitives are allowed
- whether sqrt(2) normalization is retained, removed, or scaled out
- whether explicit 3-fold primitives are allowed or excluded

Until these rules are frozen, H24 / Phi24-side results remain difficult to interpret.

## Decision Boundary

If B7.4b-A succeeds:

`receiver/magnitude/standpoint-sensitive C with C12 topology-readout becomes more robust.`

If B7.4b-A fails:

`B7.3a's C12 reconnection remains dataset-bound and must be weakened.`

If B7.4b-B produces a clean deterministic specification:

then a later preregistered dynamic factor-of-12 route-carrier audit becomes meaningful.

If B7.4b-B cannot define deterministic rules:

then H24 / Phi24 / route-carrier claims should remain hypothesis motivation only.
