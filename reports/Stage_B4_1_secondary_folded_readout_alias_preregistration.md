# Stage B4.1 Preregistration: Secondary Folded-Readout / Alias Diagnostic

## Status

Stage B4 is fixed as negative. B4.1 does not rescue or reinterpret the B4 primary result.

## Purpose

B4.1 asks why C10 descriptively dominated C12 in the real-time annual / orbital B4 readout even though no temporal basis survived the B4 control / FDR gate.

The diagnostic is secondary and Luke-side: it examines folded / normalized readout, alias, and timing-clustering explanations for the descriptive C10-over-C12 pattern.

## Fixed Boundary

- B4 remains negative.
- C12 remains the primary conceptual basis from B4.
- C10 is not treated as positive unless it survives the B4.1 secondary stability checks.
- Any B4.1 positive is explanatory only and does not move the project to Stage C.

## Main Diagnostic Question

Does the descriptive C10-over-C12 pattern reflect a stable secondary folded-readout / alias structure, or is it explained by event timing, date clustering, or scoring geometry?

## Inputs

B4.1 uses the same real-time event mapping and input files as B4.

## Anchors

The primary B4.1 anchor is:

- `utc_annual_orbital_phase`

Secondary sensitivity anchors are:

- `utc_daily_phase`
- `utc_weekly_phase`
- `global_elapsed_phase`

These sensitivity anchors are diagnostic only.

## Bases

Compare:

- C8
- C10
- C12
- C16
- C24

## Diagnostics

B4.1 will compute:

- event-class-wise basis rankings
- C10 minus C12 margins
- label leave-one-out stability
- date leave-one-out stability
- phase-anchor sensitivity
- C10-vs-C12 margin controls using label-preserved time resampling
- D24 / Phi24 lift monitor

## Secondary Stability Pattern

A stable C10 secondary pattern would require:

- C10 is best ranked for most annual/orbital event classes
- C10-over-C12 margin remains positive under label leave-one-out
- C10-over-C12 margin remains positive under date leave-one-out
- C10-over-C12 margin exceeds label-preserved time controls after FDR

If these are not met, B4.1 reports the C10 pattern as descriptive only.

## Frozen Command

```bash
python3 scripts/test_Stage_B4_1_secondary_folded_readout_alias.py \
  --input-root /Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction \
  --output-dir reports \
  --n-random 500 \
  --seed 20260608
```
