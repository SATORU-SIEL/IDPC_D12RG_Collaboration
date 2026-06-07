# Stage B4 Cyclic-Time Anchored C12 Readout Audit Summary

## Purpose

This run tests the original B4 intuition using real UTC timestamps: C12 as a 12-phase cyclic-time readout basis rather than a session-normalized proxy.

## Anchors

- primary: utc_annual_orbital_phase
- secondary: utc_daily_phase

## Overall Result

- event classes tested: 6
- bases tested: C8, C10, C12, C16, C24
- exploratory real-time C12 candidates: 0

## Real UTC Coverage

- first mapped event UTC: 2025-12-21 23:02:15.876000+00:00
- last mapped event UTC: 2026-02-01 10:12:28.983500+00:00
- this is a real timestamp audit, not a session-normalized proxy audit

## Primary C12 Annual/Orbital Phase Rows

event_class,n_events,readout_score,effect_vs_rotation,effect_vs_scramble,effect_vs_time_shift,effect_vs_event_pool,effect_vs_label_preserved_time,combined_control_p,combined_control_q,C12_vs_best_alternative,D24_Phi24_lift_score,exploratory_candidate,interpretation
FES_phase_transition,192,0.8284543975132115,-0.020330934221512997,0.7900020593403672,-2.220446049250313e-16,0.03336552594729392,-4.2964910484943886e-07,0.6417910447761194,0.9850746268656716,-0.06621021456602838,0.8099128248397268,False,C12_not_exploratory_candidate_under_real_time_B4_pattern
high_boundary_impulse_J,57,0.8272930141754574,-0.016130082636465537,0.7462763100346742,-3.3306690738754696e-16,0.03281867322816423,-4.390900550932386e-06,0.9850746268656716,0.9850746268656716,-0.06854195772494054,0.7845083996662697,False,C12_not_exploratory_candidate_under_real_time_B4_pattern
residual_contraction_low_distance,57,0.7979815408417024,-0.026268362649317867,0.7144494850762809,-1.1102230246251565e-16,0.008543510937799814,2.0053207377968008e-06,0.43283582089552236,0.9850746268656716,-0.07580414534978486,0.7659613478253292,False,C12_not_exploratory_candidate_under_real_time_B4_pattern
eps72_restoration_onset,147,0.7904065331264927,-0.025221130818628867,0.7464792358653608,-1.1102230246251565e-16,-0.001818439560092422,6.314431921783381e-08,0.5323383084577115,0.9850746268656716,-0.07829198715133101,0.7604796962953095,False,C12_not_exploratory_candidate_under_real_time_B4_pattern
h_zero_crossing,1309,0.7858427698921351,-0.02368720204055741,0.7724505694382124,-2.220446049250313e-16,-0.00568909520950045,1.470681603166213e-07,0.7313432835820896,0.9850746268656716,-0.0832789968627734,0.764024535698726,False,C12_not_exploratory_candidate_under_real_time_B4_pattern
ricci_phase_sync_high_lock_session,7,0.6342519777070263,-0.038012373751295514,0.28862982176651325,1.1102230246251565e-16,-0.19731366178815923,7.58529448807721e-07,0.9800995024875622,0.9850746268656716,-0.14470578407474066,0.5860238344030669,False,C12_not_exploratory_candidate_under_real_time_B4_pattern

## Basis Contrast Table

anchor_name,event_class,C12_readout_score,best_alternative_basis,best_alternative_score,C12_vs_best_alternative,D24_Phi24_lift_score,D24_minus_C12
utc_annual_orbital_phase,FES_phase_transition,0.8284543975132115,10,0.8946646120792399,-0.06621021456602838,0.8099128248397268,-0.018541572673484663
utc_annual_orbital_phase,high_boundary_impulse_J,0.8272930141754574,10,0.895834971900398,-0.06854195772494054,0.7845083996662697,-0.04278461450918769
utc_annual_orbital_phase,residual_contraction_low_distance,0.7979815408417024,10,0.8737856861914872,-0.07580414534978486,0.7659613478253292,-0.032020193016373155
utc_annual_orbital_phase,eps72_restoration_onset,0.7904065331264927,10,0.8686985202778237,-0.07829198715133101,0.7604796962953095,-0.029926836831183135
utc_annual_orbital_phase,h_zero_crossing,0.7858427698921351,10,0.8691217667549085,-0.0832789968627734,0.764024535698726,-0.021818234193409114
utc_annual_orbital_phase,ricci_phase_sync_high_lock_session,0.6342519777070263,10,0.778957761781767,-0.14470578407474066,0.5860238344030669,-0.048228143303959414

## Time Mapping Inventory

event_class,source_file,time_mapping_rule,n_events,n_labels,first_utc,last_utc
FES_phase_transition,event_level_with_fes_phase_TRUE_RICCI.csv,event-level task_idx joined to quantum mid_utc,192,26,2025-12-21 23:02:56.659500+00:00,2026-02-01 10:12:10.246500+00:00
eps72_restoration_onset,Chapter3/ricci_eps72_restoring_test.csv,eps72 row index mapped to nearest quantum task real UTC using per-label source length,147,26,2025-12-21 23:02:16.251000+00:00,2026-02-01 10:12:04.097500+00:00
h_zero_crossing,Chapter7/new_phi_dataset.csv,h_zero idx_in_session mapped to nearest EEG bin real UTC using per-label source length,1309,26,2025-12-21 23:02:15.876000+00:00,2026-02-01 10:12:28.983500+00:00
high_boundary_impulse_J,event_level_with_fes_phase_TRUE_RICCI.csv,event-level task_idx joined to quantum mid_utc,57,24,2025-12-21 23:02:28.523000+00:00,2026-02-01 10:00:52.532500+00:00
residual_contraction_low_distance,event_level_with_fes_phase_TRUE_RICCI.csv,event-level task_idx joined to quantum mid_utc,57,23,2025-12-21 23:02:28.523000+00:00,2026-02-01 10:11:57.889500+00:00
ricci_phase_sync_high_lock_session,Chapter3/ricci_phase_sync_summary.csv,Ricci session summary mapped to quantum session midpoint real UTC,7,7,2025-12-21 23:03:33.902500+00:00,2026-02-01 09:49:41.355000+00:00

## Interpretation

A real-time B4 exploratory candidate requires C12 to outperform the other tested temporal bases under the UTC annual/orbital phase anchor, preserve positive contrasts against random phase, event-pool, and label-preserved time controls, and show a D24 / Phi24 lift in the same direction. Rotation and within-basis phase-shift controls are reported as diagnostics but are not treated as decisive because this score is largely rotation-invariant.
