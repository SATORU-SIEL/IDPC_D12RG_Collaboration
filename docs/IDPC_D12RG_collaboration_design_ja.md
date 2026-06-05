# IDPC × D12RG / Golden Carrier コラボレーション設計メモ

## 目的

本メモは、Satoru Watanabe のIDPC論文と Luke Leighton のD12RG / golden modular carrier 論文を、どの層で接続すべきかを整理するための設計文書である。

中心となる問いは以下である。

```text
IDPCで得られている観測構造が、
D12RG / golden carrier の normalized readout として
再記述可能な層を持つか。
```

したがって、本コラボレーションで扱う対象は、IDPC-derived structural layerである。

IDPC論文の中心は、

```text
EEG-derived Ricci curvature
Quantum-derived Ricci curvature
phase residual
boundary event
FES state structure
phi localized selection
non-closed observational structure
```

が、独立に構成されたあとで同時に現れることである。

したがって、今後のコラボ検定では、IDPC構造量に対してD12RG/golden-carrier readoutの可能性を検討する。

## IDPC側の主要構造

IDPC論文で中心となる構造は以下。

| IDPC構造 | 説明 |
| --- | --- |
| EEG-derived Ricci curvature `rE(t)` | EEGから独立に構成された神経側曲率 |
| Quantum-derived Ricci curvature `rQ(t)` | Quantum probability geometryから独立に構成された量子側曲率 |
| Ricci oscillation phase `psiE(t), psiQ(t)` | Ricci曲率の位相的振る舞い |
| structural phase residual `epsilon_t` | phase alignment / contraction を表す残差 |
| boundary event | 構造が局所的に顕在化する境界点 |
| boundary impulse `J` | boundary event における観測可能なimpulse |
| FES state structure | Five Energy Star の離散状態構造 |
| phi / dphi | intersection variable とその変化 |
| localized selection | phi空間内の特定領域で生じる選択 |
| non-closed observational structure / O3 | phi内部から対応を閉じられないが、観測として一意に実現する構造 |

## Luke側の主要構造

Luke論文側で今回の接続に関係する構造は以下。

| Luke構造 | 説明 |
| --- | --- |
| golden modular carrier `U_phi` | `[[0, 1], [-1, 3]]` |
| trace ladder `A_n = tr(U_phi^n)` | `2, 3, 7, 18, 47, 123, ...` |
| primitive trace defect | `A_2 - A_0 = 5` |
| normalization ladder | `5 -> 10 -> 20` |
| D12 normalized readout closure | `U_phi^12 = I` ではなく、readout levelでのclosure |
| non-literal closure | literal periodicityではなく、normalized / readout closure |
| carrier vs readout distinction | carrierそのものと観測readoutを区別する |

GKS N=24、Vsin/Vcos、Kuramoto topology、C_12(1,2)、cuboctahedron は重要だが、これはStage Bのcarrier-realization layerであり、最初のIDPC-D12RG接続検定には入れない。

## 対応マップ

| IDPC構造 | Luke構造 | 接続仮説 | 検定優先度 |
| --- | --- | --- | --- |
| non-closed O3 | non-literal normalized closure | IDPCの「内部では閉じないが観測として実現する」構造と、D12RGの「literalではなくreadoutで閉じる」構造が対応する | high |
| phi localized selection | normalized readout closure | phi内部から対応は導けないが、readout上では局所選択として現れる | high |
| FES 5-state structure | primitive trace defect 5 | Five Energy Star と trace defect 5 の構造的関係を検討する | medium-high |
| FES transitions | 5->10->20 normalization ladder | 5状態から directed transition / doubled transition / higher-order transition へ拡張されるか | medium |
| boundary impulse `J` | trace defect / ladder step | boundary impulse が5->10->20的な正規化shellやdefect単位を持つか | medium |
| residual contraction | normalized closure | phase residual / structural residual が特定readout位置で局所的に収縮するか | high |
| Ricci phase sync | D12 readout phase | D12 binそのものではなく、phase residual closureとしてD12-like構造が現れるか | medium |

## やるべき検定

### C1. IDPC-D12RG correspondence map の確定

まずp値検定の前に、どのIDPC構造量がLuke構造のどこに対応しうるかを固定する。

出力:

```text
reports/IDPC_D12RG_correspondence_map.csv
reports/IDPC_D12RG_collaboration_design_ja.md
reports/IDPC_D12RG_collaboration_design_en.md
```

### C2. phi localized selection と normalized readout closure

目的:

```text
phi phase space の localized selection が、
golden carrier の normalized readout として再記述可能かを見る。
```

候補データ:

- `IDPC_Reproduction/Chapter7/new_phi_dataset.csv`
- `IDPC_Reproduction/Chapter7/best_true_search_scored_points.csv`
- `IDPC_Reproduction/Chapter7/block_permutation_test.csv`
- `IDPC_Reproduction/Chapter7/temporal_shift_test.csv`
- `IDPC_Reproduction/Chapter7/true_search_train_only_vs_quantum.csv`

候補列:

- `phi`
- `dphi`
- `phi_clean`
- `phi_latent`
- `deltaC_gain`
- `switch_gain`
- `sharp`
- `winner`

検定:

- best point を探索データだけで固定
- test data / block permutation / temporal shift で検証
- 5->10->20 ladderだけでなく alternative ladders と比較
- positiveの場合でも「D12RGを証明」とは書かない

### C3. FES state transition と 5->10->20 ladder

目的:

```text
Five Energy Star の5状態構造が、
primitive trace defect 5 および 5->10->20 normalization ladder と
構造的に対応するかを見る。
```

候補データ:

- `IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv`
- `IDPC_Reproduction/event_level_with_clusters_TRUE_RICCI__HYBRID_PHI.csv`
- `IDPC_Reproduction/fes_phase_summary_TRUE_RICCI__HYBRID_PHI.csv`
- `IDPC_Reproduction/fes_assignment_log_TRUE_RICCI__HYBRID_PHI.csv`

候補列:

- `fes_phase`
- `cluster`
- `phase`
- `phase_z`
- `J`
- `J_tilde`
- `distance`
- `r_local`

検定:

- FES transition matrix
- 5状態、10 directed transitions、20 oriented/entry-exit transitions の自然な出現
- random relabeling null
- transition-count-preserving null
- session/block-aware null

重要:

```text
5という数字合わせではなく、
5-state -> 10/20 transition expansion が構造的に出るかを見る。
```

### C4. boundary impulse と trace defect

目的:

```text
boundary impulse J と phase/residual compression が、
trace defect 5 または 5->10->20 normalization shell と
対応しうるかを見る。
```

候補データ:

- `IDPC_Reproduction/J_dh_kappa_pooled_v2.csv`
- `IDPC_Reproduction/event_level_raw_table_TRUE_RICCI__HYBRID_PHI.csv`
- `IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv`

候補列:

- `J`
- `dphi`
- `J_tilde`
- `g_t`
- `distance`
- `phase`
- `r_local`

検定:

- `J ≈ alpha * Delta h` の再確認
- entry/exit event別の安定性
- normalized shell assignment
- 5->10->20 vs alternative shells
- boundary label shuffle
- within-session circular/block null

### C5. residual closure / contraction と D12 readout

目的:

```text
D12をevent index mod 12として直接見るのではなく、
residual contraction minima や closure residual が
D12-like readout positionsに偏るかを見る。
```

候補データ:

- `IDPC_Reproduction/Chapter3/ricci_phase_sync_summary.csv`
- `IDPC_Reproduction/Chapter3/ricci_eps72_restoring_test.csv`
- `IDPC_Reproduction/event_level_with_fes_phase_TRUE_RICCI.csv`

候補列:

- `phase`
- `phase_z`
- `distance`
- `distance_z`
- `r_local`
- `r_local_z`
- `eps72_deg`
- `deps72_deg`

検定:

- residual minima の分布
- phase residual contraction の局在
- D12 fixed readout positions
- rotation controls
- alternative cyclic partitions
- session-preserving null

## 実装順序

推奨する実装順序:

1. `scripts/build_IDPC_D12RG_correspondence_map.py`
2. `scripts/test_IDPC_phi_selection_d12rg_readout.py`
3. `scripts/test_IDPC_fes_transition_ladder.py`
4. `scripts/test_IDPC_boundary_impulse_trace_defect.py`
5. `scripts/test_IDPC_residual_closure_d12_readout.py`

最初に作るべきレポート:

```text
reports/IDPC_D12RG_correspondence_map.csv
reports/IDPC_D12RG_collaboration_design_ja.md
reports/IDPC_D12RG_collaboration_design_en.md
```

## 科学的な表現

使ってよい表現:

```text
consistent with a D12RG-like normalized readout
supports further testing
suggests a possible correspondence layer
IDPC-derived structure admits a D12RG/golden-carrier readout interpretation
```

避けるべき表現:

```text
proves D12RG
confirms Luke's theory
golden ratio governs EEG and quantum systems
```

## 結論

検定すべきものは、

```text
IDPCで得られた phi / FES / Ricci / boundary / residual / non-closure 構造が、
Lukeの D12RG / golden carrier の normalized readout として
再記述可能かどうか
```

である。

したがって、次の実装はIDPC-derived structural layerを対象にし、D12RG/golden carrierはそのreadout解釈として限定的に導入する。
