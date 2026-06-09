# Stage B5.3 Planning Note: Hybrid Phi/FES Sign-Switch and C12 6+6 Dual-Branch Transition

## Status

This is a pre-execution planning note, not an execution report and not a post-run registration of criteria.

The purpose of publishing this note before running B5.3 is to make the agreed framing, scope, contrasts, and failure conditions visible before the mechanism test is implemented or executed.

## Starting Proposal

The original proposed B5.3 direction was:

**Stage B5.3: Recursive Hybrid Phi/FES State-Reorganization Core Validation**

The central question was:

Does the recursive hybrid Phi / FES event-level state-reorganization core project onto the C12 readout direction?

The original proposal focused on the three primary B5.2 events where the C12-positive signal concentrated:

- `hybrid_phi_sign_switch`
- `hybrid_fes_phase_transition`
- `hybrid_cluster_transition`

The working hypothesis was that these three events are not merely local switches, but may represent a layered state-reorganization core within the first-definition recursive hybrid Phi / FES event-level representation.

In that initial framing:

- `hybrid_phi_sign_switch` marks a sign reversal of recursive hybrid Phi, meaning a switch in the direction of the state coordinate.
- `hybrid_fes_phase_transition` marks a transition in the FES semantic phase.
- `hybrid_cluster_transition` marks a reassignment of the organization class in the FES / hybrid-Phi embedding.

The planned checks were:

1. first-definition Phi concentration;
2. three-event core coherence;
3. combined-core projection;
4. null / stress tests;
5. transition-like recovery endpoint rather than stable late-window closure.

The original interpretation boundary was that B5.3 should not ask whether all IDPC perturbations drive C12, should not claim stable autonomous C12 carrier closure, and should not become a Chapter 7 `phi_clean` reference audit.

## C.A.T. / Luke Theoretical Narrowing

C.A.T. and Luke narrowed the theoretical target.

Their key point was that `hybrid_phi_sign_switch` may be the primary mechanistic event. If it marks a sign reversal of recursive hybrid Phi, then the natural D12RG / cyclotomic question is whether this sign-switch localizes to an internal 6+6 structure inside C12(1,2).

In this reading:

- C12(1,2) may contain two 6-cycle branches.
- The Phi_6 / C6 cyclotomic structure naturally carries a +/- root ambiguity.
- A bare C12(1,2) graph may not by itself contain the additional constraint required to select one branch.
- A Phi/FES sign-switch may therefore be the observable event where the system transitions between, or selects between, the two internal branches.

This also explains why B5.2 looked more like transition-like C12 readout recovery than stable late-window carrier closure.

## Marcel Methodological Boundary

Marcel then clarified the methodological acceptance condition.

From the review side, B5.3 should remain a narrow mechanism test of the B5.2 signal. It should not be treated as a new confirmation stage.

The methodological distinction is:

If the signal is real and mechanistic, it should look branch-specific.

If it is generic switching, the same 6+6 branch-transition pattern should also appear in non-Phi switch controls.

Marcel's constrained design requirements are:

- primary event: `hybrid_phi_sign_switch`;
- primary mechanism: C12-internal 6+6 branch transition;
- primary contrast: non-Phi switch events;
- primary failure condition: the same 6+6 pattern appears in contrast switches or nulls;
- interpretation boundary: transition-like readout only, not stable carrier closure.

## Revised B5.3 Question

The revised B5.3 question is:

Does `hybrid_phi_sign_switch` correspond to a C12-internal 6+6 dual-branch transition?

## Revised Working Title

**Stage B5.3: Hybrid Phi/FES Sign-Switch and C12 6+6 Dual-Branch Transition**

## Final Planning Scope

The final planning scope is:

- primary event: `hybrid_phi_sign_switch`;
- coherence probes: `hybrid_fes_phase_transition` and `hybrid_cluster_transition`;
- primary mechanism: C12-internal 6+6 dual-branch transition;
- primary contrasts: non-Phi switch events, especially `dphi`, `d2phi`, and `deps` switches;
- primary failure condition: the same 6+6 branch-transition pattern appears in contrast switches or nulls;
- interpretation boundary: transition-like C12 readout only, not stable carrier closure.

## Planned Mechanism Checks

1. Decompose C12(1,2) into internal 6-cycle / half-turn components.
2. Test whether `hybrid_phi_sign_switch` localizes to the 6+6 branch structure.
3. Test whether it distinguishes + branch versus - branch behavior rather than generic switching.
4. Test whether `hybrid_fes_phase_transition` and `hybrid_cluster_transition` behave as coherence probes around the same branch-transition direction.
5. Test whether non-Phi contrast switches reproduce the same 6+6 branch-transition pattern.
6. Test whether the signal survives shifted schedules, random schedules, C8 contrast, degree-matched null graphs, session/label splits, and event-count / impulse-budget matched controls when measured as branch-transition structure rather than generic C12 recovery.

## Failure Conditions

B5.3 should be treated as inconclusive or negative for the proposed mechanism if:

1. the same 6+6 branch-transition pattern appears in non-Phi contrast switches;
2. the same pattern appears in nulls or shifted/random controls;
3. `hybrid_phi_sign_switch` improves generic C12 recovery but does not distinguish branch-specific behavior;
4. branch-transition metrics do not improve the degree/null problem relative to generic B5.2 recovery metrics;
5. interpretation requires broadening the architecture, moving thresholds, or calling the result stable carrier closure.

## Interpretation Boundary

B5.3 is not asking whether C12 self-locks.

B5.3 is not asking whether generic events recover C12.

B5.3 is not asking whether C12 closes as a stable autonomous carrier.

B5.3 is not a new confirmation stage.

B5.3 asks whether Phi/FES switching reveals a C12-internal transition grammar.

## Repository Organization Note

The current repository keeps most Stage B reports as flat files under `reports/`, with filenames carrying the stage number and test name. This planning note follows that convention for now to avoid breaking existing links.

For future stages, a cleaner organization would be:

```text
reports/
  Stage_B5_3_hybrid_phi_fes_c12_6plus6_transition_plan.md
  stage_b5_3/
    plan.md
    manifest.md
    summary.md
    results.csv
    null_graphs.csv
    branch_transition_metrics.csv
```

Existing published artifact paths should not be moved casually, because GitHub branch links to old paths can break. If artifacts are reorganized later, the preferred migration is:

1. keep the original flat files available as stable public artifacts;
2. add grouped per-stage directories for new outputs;
3. add an index or manifest linking old paths to grouped paths;
4. avoid duplicating result CSVs unless a release requires frozen compatibility copies.

In short: B5.3 can start using a grouped directory for new outputs, while B5.1/B5.2 flat artifacts remain in place.
