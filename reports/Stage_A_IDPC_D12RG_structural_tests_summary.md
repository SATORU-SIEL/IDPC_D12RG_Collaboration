# Stage A IDPC-D12RG Structural Tests Summary

## Purpose

Stage A tested whether IDPC-derived structural quantities can be re-described as narrow D12RG / golden modular carrier readouts.

The target was the IDPC structural layer:

- phi localized selection
- FES state and transition structure
- boundary impulse `J`
- residual closure / contraction
- Ricci / phase-derived readout quantities

The narrow D12RG template used in this stage was limited to:

- golden modular carrier `U_phi = [[0, 1], [-1, 3]]`
- trace ladder / primitive trace defect
- 5 -> 10 -> 20 normalization ladder
- fixed D12 readout structure
- rotation controls, alternative ladders, and random/null controls

GKS N=24, Kuramoto topology, cuboctahedral topology, and broad carrier-realization hypotheses were intentionally excluded from Stage A.

## Tests Completed

| Test | Script | Main target |
| --- | --- | --- |
| C1 correspondence inventory | `scripts/build_IDPC_D12RG_correspondence_map.py` | fix the IDPC-D12RG correspondence map |
| C2 phi selection readout | `scripts/test_IDPC_phi_selection_d12rg_readout.py` | localized phi selection and frozen D12 readout concentration |
| C3 FES transition ladder | `scripts/test_IDPC_fes_transition_ladder.py` | 5 states -> 10 unordered transitions -> 20 directed transitions |
| C4 boundary impulse shell | `scripts/test_IDPC_boundary_impulse_trace_defect.py` | `J ~ dh` and normalized trace-defect shell |
| C5 residual closure readout | `scripts/test_IDPC_residual_closure_d12_readout.py` | residual/contraction subsets near fixed D12 readout positions |

## Main Results

### C1. Correspondence Inventory

- correspondence rows: 7
- inventory rows: 238
- matched file rows: 238
- rows with usable pre-registered columns: 194

Interpretation:

The repository contains enough IDPC-derived structural outputs to run the planned Stage A tests. The correspondence map should be treated as the fixed Stage A target list.

### C2. Phi Localized Selection

Observed Chapter7 robustness:

- `switch_gain`: shift0=0.809793, block p=0.00497512, shift0-best_nonzero=0.233634
- `deltaC_gain`: shift0=0.328706, block p=0.00497512, shift0-best_nonzero=0.094916

D12 readout concentration:

- observed readout tests surviving FDR q<=0.05: 2
- control readout tests surviving FDR q<=0.05: 24

Interpretation:

Phi localized selection is robust in the IDPC Chapter7 outputs. However, similar 12-bin readout concentration appears in control directories. This supports the presence of localized phi selection, but does not establish D12RG / golden-carrier specificity.

### C3. FES Transition Ladder

- tested sequences: 220
- FDR q<=0.05 sequences: 0
- sequences where 5->10->20 ranked first among fixed ladders: 74

Interpretation:

The FES transition expansion does not survive the current shuffle-null and FDR controls as a specific 5->10->20 D12RG-like ladder.

### C4. Boundary Impulse and Trace-Defect Shell

Boundary impulse law:

- impulse-law tested files: 7
- impulse-law FDR q<=0.05 files: 7
- observed impulse-law FDR q<=0.05 files: 1
- control impulse-law FDR q<=0.05 files: 5

Strongest observed row:

- `IDPC_Reproduction/J_dh_kappa_pooled_v2.csv`: r=0.887664, slope=4.35092, p=0.000999001, q=0.000999001

Trace-defect shell:

- shell tested rows: 70
- shell FDR q<=0.05 rows vs random shells: 0
- observed shell rows where [1,2,4] ranked first among fixed ladders: 0

Interpretation:

The IDPC boundary impulse relation `J ~ dh` is strongly reproduced. However, similar effects also appear in control/back-up files, so this is not D12RG-specific. The normalized 5->10->20 shell diagnostic does not survive random shell controls.

### C5. Residual Closure / D12 Readout

- tested rows: 38
- observed tested rows: 5
- FDR q<=0.05 rows: 0
- observed FDR q<=0.05 rows: 0
- observed rows where D12 ranked first among partitions: 0
- observed rows where fixed D12 origin ranked first among rotations: 5

Interpretation:

Observed residual closure / contraction subsets are sometimes close to a fixed D12 origin, but this does not survive random subset, rotation, partition, and FDR checks as D12-specific. In observed rows, alternative partitions such as D16 or D20 can rank better than D12.

## Stage A Conclusion

Stage A supports the following cautious statements:

- IDPC-derived phi localized selection is present and robust against the included block/shift controls.
- The IDPC boundary impulse relation `J ~ dh` is strongly reproducible.
- These positive findings belong to the IDPC structural layer.

Stage A does not support the stronger narrow D12RG-specific claim:

- FES 5->10->20 transition expansion does not survive FDR.
- Boundary impulse magnitudes do not support the normalized [1,2,4] trace-defect shell after random shell controls.
- Residual closure / contraction does not survive as D12-specific after random subset, rotation, partition, and FDR checks.
- Phi D12 readout concentration appears in controls as well as observed data.

Therefore, the current Stage A result is:

```text
IDPC structural motifs are present, but the tested narrow D12RG /
golden-carrier readout diagnostics do not yet show specificity under
the current controls.
```

This does not refute D12RG or Luke Leighton's broader carrier-realization program. It means that the current IDPC-derived CSV outputs do not yet justify claiming a specific D12RG / golden-carrier readout.

## Stage B Recommendation

Stage B should not be used to rescue weak Stage A results.

Stage B may be justified only as a separate exploratory carrier-realization layer, clearly distinguished from Stage A. If pursued, it should be framed as:

```text
Given robust IDPC phi localization and boundary impulse structure,
can a broader GKS / Kuramoto / topology carrier model explain why
these IDPC structures occur, even though narrow D12RG readout
specificity was not established in Stage A?
```

Recommended next actions:

1. Re-run all Stage A scripts with the default 5000 permutations and update the public CSVs.
2. Add a `Stage_A_reproducibility_notes.md` file documenting input directories, controls, and permutation settings.
3. Send the Stage A summary to Luke for interpretation before starting Stage B.
4. If Stage B begins, keep GKS N=24 / Kuramoto / topology in a separate folder and label it exploratory.

## Plain-Language Summary

The IDPC side still looks real: phi selection and boundary impulse are not disappearing.

The D12RG-specific layer is not there yet under these tests. The strongest honest conclusion is not "D12RG confirmed"; it is:

```text
IDPC provides structural phenomena that may be worth comparing with
D12RG, but the current narrow D12RG readout tests are negative or
non-specific.
```
