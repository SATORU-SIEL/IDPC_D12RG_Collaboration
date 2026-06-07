# Stage B Audit Ledger

## Purpose

This ledger is an updateable working record of the exploratory tests completed so far in the Stage B series. It is intended to make explicit, before and after additional experiments, what has been tested, what failed or remains negative, what remains exploratory, and what would require a new independent preregistration.

Following Marcel's suggestion, the purpose of this ledger is to preserve the value of negative results while making future experiments and next hypotheses easier to justify as independent tests rather than post-hoc continuations.

## Current Position

Stage B was opened as an exploratory layer, not as a rescue of the negative Stage A result. Its question is whether broader carrier-realization motifs show descriptive structure in existing IDPC-derived structural outputs.

At the current point, the allowed conclusions are limited to the following:

- Some IDPC-derived phase / Ricci / restoration readouts show strong structure under periodic or phase-like descriptions such as D24, D12, and C12.
- Many of these quantities are already constructed inside IDPC as phase synchronization or restoration readouts, so they do not confirm a physical carrier, GKS, D12RG, or C12 topology.
- The B2 and later topology-aware / endogenous-event / mu-sector / cyclic-time audits have not reached confirmatory positives under their current preregistered gates.
- Moving to Stage C or another numbered stage requires an independent preregistration separated from the Stage B exploratory results.

## Stage B Audit Ledger

| Item | Main files | Test scope | Result | Ledger status |
| --- | --- | --- | --- | --- |
| B0 / Stage A boundary | `reports/Stage_A_IDPC_D12RG_structural_tests_summary.md` | Stage A result for narrow D12RG / golden modular carrier readouts | IDPC phi selection and boundary impulse are reproducible, but D12RG-specific readouts are not supported under the current controls | Starting boundary for Stage B. Stage B does not rescue Stage A |
| B1 exploratory GKS / Kuramoto | `reports/Stage_B_exploratory_gks_kuramoto_summary.md` | GKS N=24, sin/cos dual readouts, 8/12/24 lift overlap, Kuramoto/Ricci summaries | Some observed rows survive FDR, especially Ricci phase / eps72 / phase rows | Exploratory candidate only, not confirmation |
| B1 Ricci phase-sync carrier | `reports/Stage_B_ricci_phase_sync_carrier_summary.md` | Relationship between Ricci oscillation, phase synchronization, eps72 restoring outputs, and D24/D12 readouts | One observed phase-sync file and two eps72 rows show strong D24/D12 concentration | Most direct Stage B candidate so far, but likely confounded with existing IDPC-internal readout structure |
| B2 topology-aware carrier audit | `reports/Stage_B2_topology_aware_carrier_audit_summary.md` | C12(1,2), C8, polyhedral topologies, and degree-matched null controls | Empirical-positive topology rows: 0. C12(1,2) unseeded is negative/inconclusive at q=0.173 | No basis for moving to Stage C |
| B3 endogenous-event-conditioned readout | `reports/Stage_B3_endogenous_event_carrier_readout_summary.md` | Whether endogenous IDPC events condition D12/D24 recovery on C12(1,2) | Primary endogenous C12 rows: 6. Positive primary rows: 0. Null graph rows: 480 | Negative/inconclusive under the preregistered gate |
| B3.1 mu-sector / cycle-spectrum | `reports/Stage_B3_1_mu_sector_cycle_spectrum_summary.md` | Whether event-conditioned recovery projects onto specific mu sectors | Endogenous mu-sector rows: 288. FDR-confirmed candidates: 0. Directional rows: 104 | Secondary exploratory diagnostic only. Sector-level shape exists, but is not confirmatory |
| B3.2 mu-sector dynamic expectation | `reports/Stage_B3_2_mu_sector_dynamic_expectation_summary.md` | Whether the B3.1 directional structure follows preregistered temporal-profile expectations | Endogenous rows: 312. Confirmable target rows: 60. FDR-confirmed candidates: 0 | Does not rescue B3/B3.1. Directional rows remain exploratory |
| B4 cyclic-time anchored C12 | `reports/Stage_B4_cyclic_time_anchored_C12_readout_summary.md` | C12 cyclic-time readout based on real UTC timestamps | Event classes: 6. Exploratory real-time C12 candidates: 0. C12 does not outperform other bases | Negative for the real-time C12 anchor |
| B4.1 secondary folded-readout alias | `reports/Stage_B4_1_secondary_folded_readout_alias_summary.md` | Stability and margin controls for the C10-over-C12 descriptive pattern seen in B4 | C10 is the best descriptive basis in 6/6 cases, but C10-C12 margin controls with q<0.10: 0 | Descriptive only. Requires independent preregistration to become a new hypothesis |

## What Is Currently Preserved As Tested

- Stage A does not support narrow D12RG-specific readouts under the current controls.
- Stage B1 shows strong D24/D12/D24-like concentration in Ricci phase synchronization / eps72 restoration / phase rows.
- Stage B2 shows that C12(1,2) unseeded auto-locking does not pass the current topology-aware gate.
- Stage B3 shows that endogenous IDPC events do not produce primary C12(1,2) recovery under the preregistered primary threshold.
- Stage B3.1 and B3.2 show directional mu-sector / temporal-expectation rows, but FDR-confirmed candidates remain 0.
- Stage B4 produces no exploratory candidate for real UTC annual/orbital C12 readout.
- Stage B4.1 shows C10 as a descriptive best basis, but not as a stable secondary pattern under label-preserved / date-stability / margin controls.

## What Is Currently Negative Or Failed

- Stage B does not rescue the Stage A D12RG-specific negative result.
- GKS N=24 / D24 / D12 concentration has not been shown to be independent of IDPC-internal phase / restoration readouts.
- C12(1,2) topology has not passed the B2/B3 confirmatory gates.
- Mu-sector diagnostics have not produced FDR-confirmed candidates.
- Real-time anchored C12 is not superior to alternatives such as C10.
- The C10-over-C12 pattern is currently a descriptive alias, not carrier evidence.

## What Remains Exploratory

The following observations should be preserved, but none should be treated as a confirmed claim.

- Strong D24/D12 concentration in Ricci phase-sync / eps72 restoration.
- C12(1,2) directional sector rows from B3.1, especially eps72-related mu24 / mu4 and h=0-related mu12.
- Dodecahedron raw directional rows, especially eps72_restoration_onset mu4 / mu9 / mu24 and h_zero_crossing mu20.
- B3.2 directional dynamic rows such as C12(1,2) h_zero_crossing mu20 / mu12 and eps72_restoration_onset mu24.
- The annual/orbital C10 descriptive best-basis pattern that appears consistently in B4/B4.1.

## What Requires A New Independent Preregistration

If any of the following are turned into the next research hypothesis, they should be defined as independent preregistrations rather than post-hoc Stage B continuations.

1. A carrier-readout follow-up using Ricci phase-sync / eps72 restoration as primary endpoints.
2. A C12(1,2) specific mu-sector hypothesis, especially eps72 mu24 / mu4 and h=0 mu12 / mu20.
3. A primary topology hypothesis based on dodecahedron, icosahedron, or another polyhedral topology.
4. A separate basis hypothesis for the C10-over-C12 annual/orbital alias after the negative C12 result.
5. Any proposal to include D24/Phi24 lift, mu60, mu120, or other derived artifact monitors as success criteria.

A new preregistration should at minimum fix the following:

- primary endpoint and secondary endpoint separation
- input files, exclusion rules, hashes, and manifests
- the number of topology or basis candidates and the family-wise/FDR correction method
- null controls such as time-shift, label-preserved, event-pool, and degree-matched graph controls
- a reporting rule that prevents exploratory rows from being promoted to confirmatory claims
- treatment of the existing Stage A / Stage B results as a training or hypothesis-generation set

## Provisional Conclusion

Stage B has exploratory value because it shows that IDPC phase / Ricci / restoration structures can project onto periodic or carrier-like readout descriptions. However, the current Stage B series does not confirm D12RG, GKS N=24, C12(1,2), polyhedral topology, or a physical carrier.

The current Stage B ledger conclusion is therefore:

```text
Stage B preserves several candidate readout patterns, especially around
Ricci phase synchronization and eps72 restoration, but all carrier/topology
interpretations remain exploratory. Additional experiments can be appended
to this ledger, but any confirmatory claim or new numbered stage should be
based on an independent preregistered hypothesis.
```
