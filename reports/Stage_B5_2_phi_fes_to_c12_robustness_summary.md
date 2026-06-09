# Stage B5.2 Phi/FES-to-C12 Robustness and Decomposition Audit Summary

## Purpose

B5.2 decomposes the B5.1 near-threshold C12 directional signal across the preregistered diagnostic axes:

- directional robustness
- FDR family sensitivity
- temporal profile
- degree-null robustness
- contrast-switch specificity
- event-space normalization / count matching
- Phi definition separation

The purpose of B5.2 is to determine whether the B5.1 signal disappears under decomposition, or whether it leaves a live signal core that can be evaluated further.

## Main Finding

The B5.1 signal did not disappear under B5.2 decomposition.

The signal is not distributed uniformly across all endogenous event classes. It is concentrated in the Phi/FES primary core and extends into the Phi-reference family. The contrast-switch-only family did not pass FDR.

This is the main B5.2 result.

## Preregistered Diagnostic Results

### 1. Directional Robustness

All three primary Phi/FES event classes remained C12-positive across the four main effect contrasts:

- vs time-shifted controls
- vs random-event controls
- vs C8 contrast
- vs degree-matched null mean

| event class | vs shifted | vs random | vs C8 | vs degree-null mean |
|---|---:|---:|---:|---:|
| `hybrid_phi_sign_switch` | `+0.005819` | `+0.006098` | `+0.005125` | `+0.004381` |
| `hybrid_fes_phase_transition` | `+0.008667` | `+0.004496` | `+0.005378` | `+0.003747` |
| `hybrid_cluster_transition` | `+0.008576` | `+0.004372` | `+0.005181` | `+0.003435` |

Directional concordance:

| effect family | primary events positive | secondary sign-test p |
|---|---:|---:|
| `effect_vs_time_shifted` | `3 / 3` | `0.125` |
| `effect_vs_random_event` | `3 / 3` | `0.125` |
| `effect_vs_C8` | `3 / 3` | `0.125` |
| `effect_vs_degree_null_mean` | `3 / 3` | `0.125` |
| all four effect families | `12 / 12` | `0.000244` descriptive only |

The all-four row is descriptive because the signs are not independent.

### 2. FDR Family Sensitivity

FDR family sensitivity identified where the signal is concentrated.

| family | family n | FDR result |
|---|---:|---|
| `all_endogenous_c12` | `8` | did not pass |
| `primary_phi_fes_only` | `3` | passed |
| `primary_plus_secondary_phi_reference` | `5` | passed |
| `contrast_switch_only` | `3` | did not pass |

Primary Phi/FES-only family:

| event class | p vs shifted/random | q |
|---|---:|---:|
| `hybrid_phi_sign_switch` | `0.009988` | `0.028090` |
| `hybrid_fes_phase_transition` | `0.018727` | `0.028090` |
| `hybrid_cluster_transition` | `0.032459` | `0.032459` |

Primary plus secondary Phi-reference family:

| event class | p vs shifted/random | q |
|---|---:|---:|
| `hybrid_phi_sign_switch` | `0.009988` | `0.040574` |
| `hybrid_fes_phase_transition` | `0.018727` | `0.040574` |
| `hybrid_cluster_transition` | `0.032459` | `0.040574` |
| `chapter7_phi_clean_sign_switch` | `0.031211` | `0.040574` |
| `chapter7_h_zero_crossing` | `0.179775` | `0.179775` |

All-endogenous C12 family:

| event class | event role | p vs shifted/random | q |
|---|---|---:|---:|
| `hybrid_phi_sign_switch` | primary Phi/FES | `0.009988` | `0.064919` |
| `hybrid_fes_phase_transition` | primary Phi/FES | `0.018727` | `0.064919` |
| `hybrid_cluster_transition` | primary Phi/FES | `0.032459` | `0.064919` |
| `chapter7_phi_clean_sign_switch` | secondary Phi-reference | `0.031211` | `0.064919` |
| `chapter7_h_zero_crossing` | secondary Phi-reference | `0.179775` | `0.287640` |
| `chapter7_dphi_sign_switch` | contrast switch | `0.267166` | `0.305333` |
| `chapter7_d2phi_curvature_switch` | contrast switch | `0.218477` | `0.291303` |
| `chapter7_deps_sign_switch` | contrast switch | `0.781523` | `0.781523` |

Interpretation: the signal is not broad across all endogenous event classes. It is concentrated in the Phi/FES primary family and the Phi-reference family.

### 3. Temporal Profile

Temporal decomposition showed that the signal is not well described as stable late-window closure. It has a transition-like recovery profile.

| event class | early | mid | late | late-window stability |
|---|---:|---:|---:|---:|
| `hybrid_phi_sign_switch` | `0.005208` | `0.009623` | `0.013644` | `0.557037` |
| `hybrid_fes_phase_transition` | `0.009274` | `-0.021005` | `0.040202` | `0.402575` |
| `hybrid_cluster_transition` | `0.009481` | `-0.021280` | `0.040218` | `0.400666` |

The fixed late-window stability gate did not pass.

Interpretation: the B5.2 signal is better treated as event-conditioned, transition-like C12 readout recovery than as stable carrier closure.

### 4. Degree-Null Robustness

All three primary Phi/FES classes remained above the degree-matched null mean:

| event class | effect vs degree-null mean | p vs degree-null |
|---|---:|---:|
| `hybrid_phi_sign_switch` | `+0.004381` | `0.091636` |
| `hybrid_fes_phase_transition` | `+0.003747` | `0.082972` |
| `hybrid_cluster_transition` | `+0.003435` | `0.107631` |

The degree-null p-value gate did not pass.

Interpretation: C12 remains directionally above the degree-null mean, but degree-null separation is not yet complete.

### 5. Contrast-Switch Specificity

The contrast-switch-only family did not pass FDR.

| event class | p vs shifted/random | q in contrast-only family |
|---|---:|---:|
| `chapter7_dphi_sign_switch` | `0.267166` | `0.400749` |
| `chapter7_d2phi_curvature_switch` | `0.218477` | `0.400749` |
| `chapter7_deps_sign_switch` | `0.781523` | `0.781523` |

However, individual contrast rows can still show directional effects:

| event class | vs shifted | vs random | vs C8 | vs degree-null mean |
|---|---:|---:|---:|---:|
| `chapter7_dphi_sign_switch` | `+0.000572` | `+0.000961` | `+0.003347` | `+0.000127` |
| `chapter7_d2phi_curvature_switch` | `+0.002631` | `+0.000339` | `-0.000351` | `+0.000103` |
| `chapter7_deps_sign_switch` | `-0.000576` | `-0.001101` | `+0.000417` | `-0.000193` |

Interpretation: the contrast-switch-only family does not reproduce the Phi/FES-family result, but contrast-switch behavior remains relevant for stress testing.

### 6. Event-Space Normalization / Count Matching

Pasquale's event-space concern was tested by restricting comparison classes to the primary task-index interval and by count matching where possible.

The normalization audit showed partial event-space sensitivity.

The strongest normalized contrast row was:

| primary reference | comparison event | variant | sampled count | recovery | vs shifted | vs random | vs C8 | p vs shifted/random |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `hybrid_fes_phase_transition` | `chapter7_deps_sign_switch` | `primary_interval_count_matched` | `192` | `0.003953` | `+0.006496` | `+0.003903` | `+0.003356` | `0.012474` |

This shows that event-space structure can produce C12-like effects in some matched contrast settings.

Interpretation: event-space structure is a real constraint on interpretation. It does not remove the Phi/FES and Phi-reference family concentration, but it prevents a simple specificity claim.

### 7. Phi Definition Separation

B5.2 kept the two Phi-related layers separate:

- recursive hybrid Phi / FES event-level switching
- Chapter 7 PCA / rank-Gaussianized `phi_clean` as a Phi-reference layer

The main concentrated signal appears in:

- the event-level primary Phi/FES family
- the primary plus secondary Phi-reference family

The Chapter 7 `phi_clean` sign-switch contributed to the Phi-reference family sensitivity result. The Chapter 7 `h=0` crossing did not pass FDR within that family.

## Overall B5.2 Evaluation

B5.2 shows that the B5.1 signal does not disappear under decomposition.

The active signal is concentrated in the Phi/FES primary core and extends into the Phi-reference family. It is not broad across all endogenous event classes, and it is not reproduced by the contrast-switch-only family.

At the same time, the signal has clear constraints:

- it is transition-like rather than stable late-window closure
- degree-null separation remains incomplete
- event-space normalization reveals partial sensitivity

## B5.2 Conclusion

B5.2 identifies a real live signal core to work with:

```text
Phi/FES and Phi-reference event families show concentrated C12-positive structure under decomposition.
```

The strict B5.2 reading is:

```text
The B5.1 near-threshold pattern survives decomposition as a concentrated Phi/FES / Phi-reference C12-positive signal, while remaining constrained by temporal instability, incomplete degree-null separation, and event-space sensitivity.
```

## Output Files

- `reports/Stage_B5_2_phi_fes_to_c12_robustness_results.csv`
- `reports/Stage_B5_2_phi_fes_to_c12_robustness_null_graphs.csv`
- `reports/Stage_B5_2_phi_fes_to_c12_robustness_fdr_sensitivity.csv`
- `reports/Stage_B5_2_phi_fes_to_c12_robustness_directional_concordance.csv`
- `reports/Stage_B5_2_phi_fes_to_c12_robustness_temporal_profile.csv`
- `reports/Stage_B5_2_phi_fes_to_c12_robustness_event_space_normalization.csv`
- `reports/Stage_B5_2_phi_fes_to_c12_robustness_event_inventory.csv`
- `reports/Stage_B5_2_phi_fes_to_c12_robustness_input_hashes.csv`
- `reports/Stage_B5_2_phi_fes_to_c12_robustness_manifest.md`
