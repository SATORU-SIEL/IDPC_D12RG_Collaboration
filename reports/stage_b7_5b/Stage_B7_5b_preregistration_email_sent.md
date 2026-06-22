# Stage B7.5b Preregistration Email Sent

- Gmail message ID: `19eef9db7d321e8a`
- Gmail thread ID: `19eef9db7d321e8a`
- Sent as new email.
- Subject: `B7.5a Result and B7.5b Proposal: C->AB readout geometry`
- Recipients: `d12rg@googlegroups.com, nunnchris612@gmail.com`

## Registered Plan

B7.5b follows from the B7.5a result that, for topology-readout, C -> AB currently outperforms the tested AB <-> C implementation.

The central question is:

Why does the current C12 topology-readout couple more strongly to the C -> AB side of the self-consistency structure?

The audit will treat fractional signatures as secondary diagnostics, not explanations.

Layer 1: C -> AB component decomposition

Compare:

- C -> AB receiver-only;
- C -> AB standpoint-only;
- C -> AB magnitude-only;
- C -> AB receiver + standpoint;
- C -> AB receiver + magnitude;
- C -> AB standpoint + magnitude;
- C -> AB receiver + standpoint + magnitude;
- current reverse-only C -> AB;
- full self-consistent R*.

Layer 2: topology-side sensitivity

Run the same representations across:

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

Layer 3: alignment diagnostics

Measure:

- phase-target alignment;
- delay / lag alignment;
- receiver-side alignment;
- standpoint polarity alignment;
- magnitude scaling;
- edge direction sensitivity;
- reversed-edge sensitivity;
- ring-sharing amplification.

Layer 4: fractional secondary diagnostic

Preserve the B7.5a boundary:

- fractions as diagnostics: yes;
- fractions as explanations: not yet.

Check whether:

- 1/4 remains around P10 / the 5-or-10 proxy;
- 2/11 remains around c12_reversed, ring_share_c12_plus_10, and survivor strength;
- these signatures co-localize with the main C -> AB readout geometry;
- or remain secondary diagnostics independent of readout strength.

Decision boundary:

Strong support:

- the C -> AB advantage localizes to a specific component or component-combination;
- that component consistently supports the C12 topology-readout;
- the effect weakens under null and shuffled controls;
- fractional diagnostics co-localize around the same geometry.

Intermediate support:

- the C -> AB advantage remains, but component localization is weak;
- topology specificity is partial;
- fractional diagnostics remain, but only weakly align with readout geometry.

Negative result:

- the C -> AB advantage disappears under component decomposition;
- the effect spreads broadly into topology controls;
- fractional diagnostics scatter independently of readout geometry.
