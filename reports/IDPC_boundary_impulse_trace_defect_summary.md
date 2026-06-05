# Boundary Impulse Trace-Defect Shell Test

## Purpose

This structural-layer test checks the IDPC boundary impulse law and an exploratory trace-defect shell diagnostic.

## Results

- impulse-law tested files: 7
- impulse-law FDR q<=0.05 files: 7
- observed impulse-law FDR q<=0.05 files: 1
- control impulse-law FDR q<=0.05 files: 5
- shell tested rows: 70
- shell FDR q<=0.05 rows vs random shells: 0
- observed shell rows where [1,2,4] ranked first among fixed ladders: 0

## Strongest Impulse-Law Rows

- IDPC_Reproduction/J_dh_kappa_pooled_v2.csv: r=0.887664, slope=4.35092, p=0.000999001, q=0.000999001
- IDPC_Reproduction_random/J_dh_kappa_pooled_v2.csv: r=0.916582, slope=3.83372, p=0.000999001, q=0.000999001
- backups/mm_fullnb_derangement/J_dh_kappa_pooled_v2.csv: r=0.878199, slope=4.44107, p=0.000999001, q=0.000999001

## Interpretation

The observed boundary impulse law J~dh survives FDR, but similar effects also appear in control/back-up files. This reproduces the impulse relation, but does not establish D12RG specificity.
The normalized [1,2,4] shell diagnostic does not survive random shell controls after FDR.
