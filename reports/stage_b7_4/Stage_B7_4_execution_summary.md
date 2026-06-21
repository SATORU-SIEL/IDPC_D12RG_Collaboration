# Stage B7.4 Execution Summary

Status: executed after `Stage_B7_4_preregistration.md` and `Stage_B7_4_preregistration_email_sent.md`.

## Registered Email

The B7.4 update email itself was preserved as the preregistration trace:

- file: `reports/stage_b7_4/Stage_B7_4_preregistration_email_sent.md`
- Gmail message id: `19eeb645d161f603`
- Gmail thread id: `19eeb22b2ea85c11`
- Gmail timestamp: `2026-06-21T18:14:43`

## Executed Audits

Two audit scripts were registered and executed:

- `scripts/test_Stage_B7_4_phi_invariant_vacuum_layer_c_audit.py`
- `scripts/test_Stage_B7_4_quadrature_phi12_vacuum_layer_audit.py`

Outputs:

- `reports/stage_b7_4/phi_invariant/`
- `reports/stage_b7_4/quadrature_phi12/`

## Phi-Invariant C12 Audit

Command:

```bash
python3 -B scripts/test_Stage_B7_4_phi_invariant_vacuum_layer_c_audit.py --with-neighbor-controls --with-event-nulls --n-runs 24 --steps 180 --rep-filter receiver_only_c,receiver_standpoint_magnitude_c,phi_eigen_energy_c,phi_differential_invariant_c
```

Primary C12 ranking:

| representation | C12 mean | vs no-topology | vs reversed | vs side-broken | vs shuffled | positive controls | p vs event nulls |
|---|---:|---:|---:|---:|---:|---:|---:|
| `phi_eigen_energy_c` | 0.047617 | +0.004801 | -0.000151 | +0.037403 | +0.033320 | 7/8 | 0.020408 |
| `receiver_only_c` | 0.038162 | +0.001570 | -0.000857 | +0.024883 | +0.023213 | 7/8 | 0.020408 |
| `receiver_standpoint_magnitude_c` | 0.037808 | +0.006462 | -0.000533 | +0.039157 | +0.041524 | 7/8 | 0.020408 |
| `phi_differential_invariant_c` | 0.028397 | +0.005845 | -0.000533 | +0.026248 | +0.021105 | 7/8 | 0.489796 |

Interpretation:

- `phi_eigen_energy_c` had the largest C12 mean and beat no-topology, side-broken, shuffled, and neighboring C10/C11/C13/C14 controls.
- All four primary representations narrowly failed the reversed-C12 specificity margin.
- `phi_differential_invariant_c` did not pass the event-null criterion.
- Therefore, the preregistered stronger claim is not supported in this run.

## Quadrature Phi12 / Vacuum-Layer Audit

Command:

```bash
python3 -B scripts/test_Stage_B7_4_quadrature_phi12_vacuum_layer_audit.py --n-runs 24 --steps 180 --reps phi_eigen_energy_c,phi_differential_invariant_c,receiver_only_c,receiver_standpoint_magnitude_c
```

Primary paired-C12 +90 ranking:

| representation | paired +90 mean | vs single C12 | vs +90 regulated | vs regulation-only | positive controls |
|---|---:|---:|---:|---:|---:|
| `receiver_only_c` | 0.000439 | -0.081968 | -0.056970 | -0.054538 | 6/11 |
| `receiver_standpoint_magnitude_c` | -0.000201 | -0.084863 | -0.033639 | -0.034427 | 3/11 |
| `phi_eigen_energy_c` | -0.006890 | -0.098699 | -0.042263 | -0.051223 | 1/11 |
| `phi_differential_invariant_c` | -0.007759 | -0.074862 | -0.057204 | -0.059057 | 1/11 |

Top mean arms by representation:

- `phi_eigen_energy_c`: single C12 0.091809; regulation-only 0.044333; paired +90 regulated 0.035373.
- `phi_differential_invariant_c`: single C12 0.067103; regulation-only 0.051298; paired +90 regulated 0.049445.
- `receiver_only_c`: single C12 0.082407; paired +90 cross-regulated 0.058941; paired +90 regulated 0.057409; regulation-only 0.054977.
- `receiver_standpoint_magnitude_c`: single C12 0.084661; regulation-only 0.034226; paired +90 regulated 0.033438.

Interpretation:

- The unregulated paired-C12 +90 arm did not support the Vacuum-layer quadrature claim.
- Explicit 90-degree regulation improved the paired/quadrature arms, but single C12 remained stronger across all primary representations.
- Regulation-only was comparable to, or stronger than, architecture + regulation in several comparisons.
- Therefore, this run does not support the claim that paired Phi12 / C12 architecture is required.

## Frozen B7.4 Conclusion

B7.4 does not support the strong Vacuum-layer C claim under the current operationalization.

The safer boundary remains:

- B7.3/B7.3a receiver/magnitude/standpoint-sensitive C remains the live empirical boundary.
- `phi_eigen_energy_c` may be a useful diagnostic or sharpening of receiver-side C, but it did not cleanly pass the reversed-C12 specificity condition.
- `phi_differential_invariant_c` did not add sufficient event-null-supported improvement beyond receiver-only C.
- Quadrature regulation remains an interesting hypothesis motivation, but not an empirical conclusion from this B7.4 run.

If the Vacuum-layer hypothesis is pursued further, the next audit should improve the operationalization of two-ring quadrature readout before making stronger claims.
