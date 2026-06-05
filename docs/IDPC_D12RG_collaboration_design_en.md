# IDPC x D12RG / Golden Carrier Collaboration Design Memo

## Purpose

This memo redesigns the collaboration between Satoru Watanabe's IDPC paper and Luke Leighton's D12RG / golden modular carrier paper.

The guiding question is:

```text
Can the observational structure produced by IDPC be re-described,
at the appropriate structural layer, as a normalized readout of
D12RG / golden carrier dynamics?
```

Therefore, the collaboration target is the IDPC-derived structural layer.

The IDPC paper is about the co-occurrence of independently constructed structures:

```text
EEG-derived Ricci curvature
Quantum-derived Ricci curvature
phase residual
boundary event
FES state structure
phi localized selection
non-closed observational structure
```

Therefore, future collaboration tests should ask whether IDPC-derived structural quantities admit a D12RG/golden-carrier readout interpretation.

## Main IDPC Structures

| IDPC structure | Description |
| --- | --- |
| EEG-derived Ricci curvature `rE(t)` | neural-side curvature independently constructed from EEG |
| Quantum-derived Ricci curvature `rQ(t)` | quantum-side curvature independently constructed from probability geometry |
| Ricci oscillation phases `psiE(t), psiQ(t)` | phase behavior of Ricci curvature |
| structural phase residual `epsilon_t` | residual describing phase alignment / contraction |
| boundary event | localized point where structure becomes observable |
| boundary impulse `J` | observable impulse at boundary events |
| FES state structure | Five Energy Star discrete state structure |
| phi / dphi | intersection variable and its variation |
| localized selection | selection localized in phi phase space |
| non-closed observational structure / O3 | correspondence cannot be closed internally in phi, but is empirically realized |

## Main Luke / D12RG Structures

| Luke structure | Description |
| --- | --- |
| golden modular carrier `U_phi` | `[[0, 1], [-1, 3]]` |
| trace ladder `A_n = tr(U_phi^n)` | `2, 3, 7, 18, 47, 123, ...` |
| primitive trace defect | `A_2 - A_0 = 5` |
| normalization ladder | `5 -> 10 -> 20` |
| D12 normalized readout closure | readout-level closure, not `U_phi^12 = I` |
| non-literal closure | normalized/readout closure rather than literal periodicity |
| carrier vs readout distinction | the carrier itself must be distinguished from observable readouts |

GKS N=24, Vsin/Vcos, Kuramoto topology, `C_12(1,2)`, and cuboctahedra may be important, but they belong to a later carrier-realization layer. They should not be used in the first IDPC-D12RG evidential pass.

## Correspondence Map

| IDPC structure | Luke structure | Connection hypothesis | Priority |
| --- | --- | --- | --- |
| non-closed O3 | non-literal normalized closure | IDPC's "not internally closed but empirically realized" structure may correspond to D12RG readout closure without literal closure | high |
| phi localized selection | normalized readout closure | correspondence is not derived inside phi, but localized selection appears at the readout level | high |
| FES 5-state structure | primitive trace defect 5 | Five Energy Star may correspond structurally to trace defect 5 | medium-high |
| FES transitions | 5->10->20 normalization ladder | 5 states may expand into 10 directed transitions and 20 oriented/entry-exit transitions | medium |
| boundary impulse `J` | trace defect / ladder step | boundary impulse may show normalized shells related to trace defect or ladder steps | medium |
| residual contraction | normalized closure | phase/structural residual may contract at specific readout positions | high |
| Ricci phase synchronization | D12 readout phase | D12 should be tested as residual closure rather than literal event-bin periodicity | medium |

## Tests To Run

### C1. Fix the IDPC-D12RG Correspondence Map

Before p-value testing, fix which IDPC structures can correspond to which D12RG/golden-carrier structures.

Outputs:

```text
reports/IDPC_D12RG_correspondence_map.csv
reports/IDPC_D12RG_collaboration_design_ja.md
reports/IDPC_D12RG_collaboration_design_en.md
```

### C2. Phi Localized Selection vs Normalized Readout Closure

Purpose:

```text
Test whether localized selection in phi phase space can be re-described
as a golden-carrier normalized readout.
```

Candidate data:

- `IDPC_Reproduction/Chapter7/new_phi_dataset.csv`
- `IDPC_Reproduction/Chapter7/best_true_search_scored_points.csv`
- `IDPC_Reproduction/Chapter7/block_permutation_test.csv`
- `IDPC_Reproduction/Chapter7/temporal_shift_test.csv`
- `IDPC_Reproduction/Chapter7/true_search_train_only_vs_quantum.csv`

Candidate columns:

- `phi`
- `dphi`
- `phi_clean`
- `phi_latent`
- `deltaC_gain`
- `switch_gain`
- `sharp`
- `winner`

Tests:

- fix the best point using discovery data only
- validate on test data / block permutation / temporal shift
- compare 5->10->20 against alternative ladders
- do not describe positive results as proof of D12RG

### C3. FES State Transitions and the 5->10->20 Ladder

Purpose:

```text
Test whether the Five Energy Star structure has a structural relation to
primitive trace defect 5 and the 5->10->20 normalization ladder.
```

Candidate data:

- `IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv`
- `IDPC_Reproduction/event_level_with_clusters_TRUE_RICCI__HYBRID_PHI.csv`
- `IDPC_Reproduction/fes_phase_summary_TRUE_RICCI__HYBRID_PHI.csv`
- `IDPC_Reproduction/fes_assignment_log_TRUE_RICCI__HYBRID_PHI.csv`

Candidate columns:

- `fes_phase`
- `cluster`
- `phase`
- `phase_z`
- `J`
- `J_tilde`
- `distance`
- `r_local`

Tests:

- FES transition matrix
- natural emergence of 5 states, 10 directed transitions, or 20 oriented/entry-exit transitions
- random relabeling null
- transition-count-preserving null
- session/block-aware null

Important:

```text
Do not merely match the number 5.
Test whether 5-state -> 10/20 transition expansion appears structurally.
```

### C4. Boundary Impulse and Trace Defect

Purpose:

```text
Test whether boundary impulse J and phase/residual compression relate to
trace defect 5 or 5->10->20 normalization shells.
```

Candidate data:

- `IDPC_Reproduction/J_dh_kappa_pooled_v2.csv`
- `IDPC_Reproduction/event_level_raw_table_TRUE_RICCI__HYBRID_PHI.csv`
- `IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv`

Candidate columns:

- `J`
- `dphi`
- `J_tilde`
- `g_t`
- `distance`
- `phase`
- `r_local`

Tests:

- reproduce `J ≈ alpha * Delta h`
- entry/exit stability
- normalized shell assignment
- 5->10->20 vs alternative shells
- boundary-label shuffle
- within-session circular/block null

### C5. Residual Closure / Contraction and D12 Readout

Purpose:

```text
Do not test D12 as event_index mod 12 directly.
Test whether residual contraction minima or closure residuals are biased
toward D12-like readout positions.
```

Candidate data:

- `IDPC_Reproduction/Chapter3/ricci_phase_sync_summary.csv`
- `IDPC_Reproduction/Chapter3/ricci_eps72_restoring_test.csv`
- `IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv`

Candidate columns:

- `phase`
- `phase_z`
- `distance`
- `distance_z`
- `r_local`
- `r_local_z`
- `eps72_deg`
- `deps72_deg`

Tests:

- residual minima distribution
- localized phase-residual contraction
- fixed D12 readout positions
- rotation controls
- alternative cyclic partitions
- session-preserving null

## Implementation Order

Recommended implementation order:

1. `scripts/build_IDPC_D12RG_correspondence_map.py`
2. `scripts/test_IDPC_phi_selection_d12rg_readout.py`
3. `scripts/test_IDPC_fes_transition_ladder.py`
4. `scripts/test_IDPC_boundary_impulse_trace_defect.py`
5. `scripts/test_IDPC_residual_closure_d12_readout.py`

First reports to create:

```text
reports/IDPC_D12RG_correspondence_map.csv
reports/IDPC_D12RG_collaboration_design_ja.md
reports/IDPC_D12RG_collaboration_design_en.md
```

## Scientific Language

Acceptable language:

```text
consistent with a D12RG-like normalized readout
supports further testing
suggests a possible correspondence layer
IDPC-derived structure admits a D12RG/golden-carrier readout interpretation
```

Avoid:

```text
proves D12RG
confirms Luke's theory
golden ratio governs EEG and quantum systems
```

## Conclusion

The collaboration should test:

```text
Whether IDPC-derived phi / FES / Ricci / boundary / residual /
non-closure structures can be re-described as normalized readouts of
Luke's D12RG / golden carrier framework.
```

The next implementation should therefore target the IDPC-derived structural layer and introduce D12RG/golden carrier only as a constrained readout interpretation.
