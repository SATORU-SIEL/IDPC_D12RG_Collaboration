# Stage B4 Preregistration: Real-Time Cyclic-Phase Anchored C12 Readout Audit

## Status

This preregistration supersedes the earlier session-normalized proxy version. Stage B4 must be run on real UTC timestamps.

## Central Intuition

C12 may not be an autonomous spatial topology. It may function as a cyclic temporal readout basis only when anchored to an orbital / annual time-phase axis.

In this framing:

- C12 is the 12-phase temporal vessel.
- D24 / Phi24 is the half-phase or lifted readout reference.
- FES / eps72 remains the fivefold selection or energy-side structure.
- The exploratory question is whether IDPC events become organized when read through the real cyclic-time axis.

## Primary Anchor

The primary anchor is `utc_annual_orbital_phase`, computed directly from each event's real UTC timestamp as year-fraction phase.

This is the formal Stage B4 target.

## Secondary Anchor

The secondary anchor is `utc_daily_phase`, computed directly from each event's real UTC timestamp as day-fraction phase.

This is a monitor only. It must not replace the primary annual / orbital interpretation.

## Event UTC Mapping Rules

- `event_level_with_fes_phase_TRUE_RICCI.csv`: join `label` and `task_idx` to `P*_quantum_timeseries.csv` `mid_utc`.
- `Chapter7/new_phi_dataset.csv` h=0 crossings: map `idx_in_session` to the nearest `P*_eeg_timeseries.csv` bin midpoint using per-label source length.
- `Chapter3/ricci_eps72_restoring_test.csv` eps72 restoration onsets: map per-label row index to the nearest `P*_quantum_timeseries.csv` `mid_utc` using per-label source length.
- `Chapter3/ricci_phase_sync_summary.csv`: map session-level rows to the midpoint quantum task UTC for that label.

## Bases

Compare temporal readout bases:

- C8
- C10
- C12
- C16
- C24

C12 is the main basis. C24 is the D24 / Phi24 lift reference.

## Controls

For each event class and basis, compare observed real-time phase organization against:

- random phase-scramble controls
- event-pool time resampling controls
- label-preserved time resampling controls

Phase-rotation and within-basis phase-shift diagnostics may be reported, but they are not decisive controls because the concentration score is largely rotation-invariant.

## Exploratory Candidate Pattern

A Stage B4 exploratory C12 candidate requires:

- primary anchor is `utc_annual_orbital_phase`
- basis is C12
- C12 outperforms the best tested alternative basis for the same event class
- C12 has positive contrast against random phase, event-pool, and label-preserved time controls
- D24 / Phi24 lift remains directionally present

This is exploratory, not a Stage C gate.

## Negative Boundary

If no candidate appears, the result means:

> No C12 temporal readout candidate was confirmed under the current real-UTC annual/orbital mapping and event set.

It does not by itself reject the broader intuition that C12 may be a cyclic temporal readout basis.

## Frozen Command

```bash
python3 scripts/test_Stage_B4_cyclic_time_anchored_C12_readout.py \
  --input-root /Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction \
  --output-dir reports \
  --n-rotations 24 \
  --n-random 200 \
  --seed 20260608
```
