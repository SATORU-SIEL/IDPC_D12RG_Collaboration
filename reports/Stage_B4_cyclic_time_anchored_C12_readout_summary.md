# Stage B4 Cyclic-Time Anchored C12 Readout Audit Summary

## Purpose

Stage B4 tests the exploratory intuition that C12 is not a spatial graph that closes by itself, but a 12-phase cyclic-time readout basis.

## Boundary

This does not rescue B2/B3/B3.1/B3.2. Earlier negative / inconclusive results remain unchanged.

## Primary Anchor

- session_normalized_event_position

Absolute calendar / orbital timestamps were not available in the current input bundle, so this first B4 run tests session-normalized cyclic-time anchoring rather than literal annual/orbital anchoring.

## Overall Result

- event classes tested: 6
- bases tested: C8, C10, C12, C16, C24
- exploratory C12 candidates: 0

## C12 Basis Rows

event_class,n_events,readout_score,effect_vs_rotation,effect_vs_scramble,effect_vs_time_shift,combined_control_p,combined_control_q,C12_vs_best_alternative,D24_Phi24_lift_score,exploratory_candidate,interpretation
ricci_phase_sync_high_lock_session,7,0.9978496015164446,0.005015862371834268,0.6492369126117328,1.1102230246251565e-16,1.0,1.0,-0.001194090353979771,0.9914263266466092,False,C12_not_exploratory_candidate_under_B4_pattern
residual_contraction_low_distance,57,0.21743939566707796,0.006145101538369335,0.14051584688722482,-0.0005522862661509198,0.8333333333333334,1.0,-0.10332518823479478,0.32076458390187274,False,C12_not_exploratory_candidate_under_B4_pattern
high_boundary_impulse_J,57,0.20735717853082633,-0.014143406505441714,0.13122214022202414,-0.003501877082314281,0.96,1.0,-0.10023914100625167,0.307596319537078,False,C12_not_exploratory_candidate_under_B4_pattern
eps72_restoration_onset,147,0.11979452484817796,0.01188518383189105,0.07686745559824071,0.0008857276732883029,0.5,1.0,-0.022831199921853118,0.14262572477003108,False,C12_not_exploratory_candidate_under_B4_pattern
FES_phase_transition,192,0.082513037890283,0.0034565743799907234,0.04509919339284338,-0.0007804874639483206,0.75,1.0,-0.04541650562828667,0.12792954351856967,False,C12_not_exploratory_candidate_under_B4_pattern
h_zero_crossing,1309,0.0211032937977675,-0.0005092800036803485,0.008714387022178086,-1.3043925500676873e-05,0.96,1.0,-0.006150267282563508,0.015600435761641886,False,C12_not_exploratory_candidate_under_B4_pattern

## Basis Contrast Table

event_class,C12_readout_score,best_alternative_score,C12_vs_best_alternative,D24_Phi24_lift_score,D24_minus_C12
ricci_phase_sync_high_lock_session,0.9978496015164446,0.9990436918704244,-0.001194090353979771,0.9914263266466092,-0.006423274869835405
h_zero_crossing,0.0211032937977675,0.02725356108033101,-0.006150267282563508,0.015600435761641886,-0.005502858036125614
eps72_restoration_onset,0.11979452484817796,0.14262572477003108,-0.022831199921853118,0.14262572477003108,0.022831199921853118
FES_phase_transition,0.082513037890283,0.12792954351856967,-0.04541650562828667,0.12792954351856967,0.04541650562828667
high_boundary_impulse_J,0.20735717853082633,0.307596319537078,-0.10023914100625167,0.307596319537078,0.10023914100625167
residual_contraction_low_distance,0.21743939566707796,0.32076458390187274,-0.10332518823479478,0.32076458390187274,0.10332518823479478

## Interpretation

A B4 exploratory candidate requires C12 to outperform the other tested temporal bases, preserve positive contrasts against phase-anchor controls, and show a D24 / Phi24 lift in the same direction. This is an exploratory pattern, not a final confirmation.
