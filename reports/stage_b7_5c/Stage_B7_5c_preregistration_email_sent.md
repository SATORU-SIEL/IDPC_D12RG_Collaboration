# Stage B7.5c Preregistration Email Sent

- Gmail message ID: `19eefe9b2795d0d6`
- Gmail thread ID: `19eefe9b2795d0d6`
- Sent as new email.
- Subject: `B7.5b Result and B7.5c Proposal: stability boundary between reverse-side and self-consistent readout`
- Recipients: `d12rg@googlegroups.com, nunnchris612@gmail.com`

## Registered Plan

B7.5c is a stability-boundary audit, not a global-winner audit.

Central question:

Under which seed, topology, event-schedule, and ring-sharing conditions does the C12 readout prefer the C -> AB side, and under which conditions does it prefer full self-consistent R*?

Matched conditions:

- identical event schedules where representation permits;
- identical simulation seeds;
- identical topology arms;
- paired delta statistics;
- rerun stability;
- bootstrap confidence intervals.

Primary comparisons:

- reverse-only C -> AB;
- full self-consistent R*;
- C -> AB receiver-only;
- C -> AB standpoint-only;
- C -> AB magnitude-only;
- C -> AB receiver + standpoint + magnitude.

Topology arms:

- C12(1,2);
- C12 reversed;
- side-broken C12;
- shuffled C12;
- C10/C11/C13/C14;
- ring_share_c12_plus_5;
- ring_share_c12_plus_10;
- ring_share_c12_plus_7;
- ring_share_c12_plus_11;
- edge-count matched null;
- degree-matched null.

Decision boundary:

Stable reverse-side readout:

- reverse-only C -> AB exceeds full self-consistent R* under paired seeds;
- the difference remains stable under reruns;
- the difference is C12-specific.

Stable self-consistent readout:

- full self-consistent R* exceeds reverse-only C -> AB under paired seeds;
- the difference remains stable under reruns;
- the difference is C12-specific.

Boundary result:

- the ordering flips by seed, topology, event schedule, or ring-sharing condition;
- in that case, the conclusion is not that one representation is globally dominant, but that the C12 readout has a stability boundary sensitive to implementation geometry.
