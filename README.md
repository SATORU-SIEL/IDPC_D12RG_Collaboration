# IDPC D12RG Collaboration

Public collaboration notes for testing possible correspondences between Satoru Watanabe's IDPC observational-structure framework and Luke Leighton's D12RG / golden modular carrier framework.

This repository starts from the collaboration-design layer and focuses on IDPC-derived structural readouts as the common ground for comparison with the D12RG / golden modular carrier framework.

## Core Question

Can IDPC-derived structural quantities be re-described, at the appropriate structural layer, as normalized readouts of a D12RG / golden modular carrier structure?

The target is the IDPC-derived structural layer:

- EEG-derived and Quantum-derived Ricci curvature
- phase residual / contraction
- boundary events and boundary impulse
- FES state structure
- phi localized selection
- non-closed observational structure / O3

## Initial Public Materials

- [English collaboration design memo](docs/IDPC_D12RG_collaboration_design_en.md)
- [Japanese collaboration design memo](docs/IDPC_D12RG_collaboration_design_ja.md)
- [IDPC-D12RG correspondence map](data/IDPC_D12RG_correspondence_map.csv)
- [Correspondence inventory summary](reports/IDPC_D12RG_correspondence_inventory_summary.md)
- [Phi selection D12 readout summary](reports/IDPC_phi_selection_d12_readout_summary.md)
- [FES transition ladder summary](reports/IDPC_FES_transition_ladder_summary.md)
- [Boundary impulse trace-defect summary](reports/IDPC_boundary_impulse_trace_defect_summary.md)
- [Residual closure D12 readout summary](reports/IDPC_residual_closure_d12_readout_summary.md)
- [Stage A structural tests summary](reports/Stage_A_IDPC_D12RG_structural_tests_summary.md)
- [Stage A+ structural holonomy loop summary](reports/Stage_A_plus_structural_holonomy_loop_summary.md)
- [Stage B exploratory GKS / Kuramoto summary](reports/Stage_B_exploratory_gks_kuramoto_summary.md)
- [Stage B Ricci phase-sync carrier summary](reports/Stage_B_ricci_phase_sync_carrier_summary.md)
- [Stage B audit ledger](reports/Stage_B_audit_ledger.md)
- [Stage B2 topology-aware carrier audit summary](reports/Stage_B2_topology_aware_carrier_audit_summary.md)

Published result files:

- [Correspondence map CSV](reports/IDPC_D12RG_correspondence_map.csv)
- [Candidate data inventory CSV](reports/IDPC_D12RG_candidate_data_inventory.csv)
- [Theoretical template JSON](reports/IDPC_D12RG_theoretical_template.json)
- [Phi selection robustness CSV](reports/IDPC_phi_selection_robustness_results.csv)
- [Phi selection D12 readout CSV](reports/IDPC_phi_selection_d12_readout_results.csv)
- [FES transition ladder CSV](reports/IDPC_FES_transition_ladder_results.csv)
- [FES alternative ladder CSV](reports/IDPC_FES_transition_ladder_alternatives.csv)
- [Boundary impulse law CSV](reports/IDPC_boundary_impulse_law_results.csv)
- [Boundary impulse trace-shell CSV](reports/IDPC_boundary_impulse_trace_shell_results.csv)
- [Residual closure D12 readout CSV](reports/IDPC_residual_closure_d12_readout_results.csv)
- [Stage A+ structural holonomy loop CSV](reports/Stage_A_plus_structural_holonomy_loop_results.csv)
- [Stage A+ structural holonomy roots CSV](reports/Stage_A_plus_structural_holonomy_roots.csv)
- [Stage B GKS N=24 phase dual CSV](reports/Stage_B_gks24_phase_dual_results.csv)
- [Stage B 8/12/24 lift overlap CSV](reports/Stage_B_lift_overlap_8_12_24_results.csv)
- [Stage B Kuramoto/Ricci summary CSV](reports/Stage_B_kuramoto_ricci_summary_results.csv)
- [Stage B Ricci phase-sync carrier CSV](reports/Stage_B_ricci_phase_sync_carrier_results.csv)
- [Stage B Ricci eps72 restoring carrier CSV](reports/Stage_B_ricci_eps72_restoring_carrier_results.csv)
- [Stage B2 topology-aware carrier audit CSV](reports/Stage_B2_topology_aware_carrier_audit_results.csv)
- [Stage B2 topology loop inventory CSV](reports/Stage_B2_topology_loop_inventory.csv)
- [Stage B2 topology null controls CSV](reports/Stage_B2_topology_null_controls.csv)

## Scope

Included in the first public pass:

- IDPC structural-layer mapping
- D12RG / golden carrier readout hypotheses
- falsifiable analysis design
- separation between readout-level tests and later carrier-realization tests

## Scientific Stance

This repository is for hypothesis design and falsifiable testing. It should not be read as claiming that D12RG is proven, or that the golden carrier governs EEG or quantum systems. Positive, negative, and null results are all useful if they clarify which structural correspondences survive strict controls.

## Reference Papers

- Satoru Watanabe, [Intersection-Defined Phase Coordinates Reveal Localized Selection and a Non-Internal Observational Structure](https://doi.org/10.5281/zenodo.19416761)
- Luke Kenneth Casson Leighton and Alex Hankey, [Paper 6.4: The PSL(2,Z) Golden Carrier for GKS and the monodromy-free Renormalised RCFT D12RG: Phi^8 Quadratic Lift and Phi^12 Normalized Modular Closure](https://www.researchgate.net/publication/405812058_Paper_64_The_P_SL2_Z_Golden_Carrier_for_GKS_and_the_monodromy-free_Renormalised_RCFT_D12RG_PH_8_Quadratic_Lift_and_PH_12_Normalized_Modular_Closure)

## Scripts

Implemented:

- `scripts/build_IDPC_D12RG_correspondence_map.py`
- `scripts/test_IDPC_fes_transition_ladder.py`
- `scripts/test_IDPC_phi_selection_d12rg_readout.py`
- `scripts/test_IDPC_boundary_impulse_trace_defect.py`
- `scripts/test_IDPC_residual_closure_d12_readout.py`
- `scripts/test_IDPC_structural_holonomy_loop.py`
- `scripts/test_Stage_B_gks_kuramoto_exploratory.py`
- `scripts/test_Stage_B_ricci_phase_sync_carrier.py`
- `scripts/test_Stage_B2_topology_aware_carrier_audit.py`

Example:

```bash
python3 scripts/build_IDPC_D12RG_correspondence_map.py \
  --input-root /path/to/IDPC_Reproduction \
  --output-dir reports/generated

python3 scripts/test_IDPC_fes_transition_ladder.py \
  --input-root /path/to/IDPC_Reproduction \
  --output-dir reports/generated

python3 scripts/test_IDPC_phi_selection_d12rg_readout.py \
  --input-root /path/to/IDPC_Reproduction \
  --output-dir reports/generated

python3 scripts/test_IDPC_boundary_impulse_trace_defect.py \
  --input-root /path/to/IDPC_Reproduction \
  --output-dir reports/generated

python3 scripts/test_IDPC_residual_closure_d12_readout.py \
  --input-root /path/to/IDPC_Reproduction \
  --output-dir reports/generated

python3 scripts/test_IDPC_structural_holonomy_loop.py \
  --input-root /path/to/IDPC_Reproduction \
  --output-dir reports/generated

python3 scripts/test_Stage_B_gks_kuramoto_exploratory.py \
  --input-root /path/to/IDPC_Reproduction \
  --output-dir reports/generated

python3 scripts/test_Stage_B_ricci_phase_sync_carrier.py \
  --input-root /path/to/IDPC_Reproduction \
  --output-dir reports/generated

python3 scripts/test_Stage_B2_topology_aware_carrier_audit.py \
  --input-root . \
  --output-dir reports
```
