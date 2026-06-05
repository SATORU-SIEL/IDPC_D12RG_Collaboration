# Phi Localized Selection D12 Readout Test

## Purpose

This structural-layer test checks whether Chapter7 phi localized selection is robust against IDPC block/shift controls and whether selection weights concentrate across a frozen 12-bin phi readout.

## Results

- robustness rows: 28
- observed robustness rows: 2
- readout tests: 28
- observed readout tests: 2
- observed readout tests surviving FDR q<=0.05: 2
- control readout tests surviving FDR q<=0.05: 24

Observed Chapter7 robustness:

- observed `switch_gain`: shift0=0.809793, block p=0.00497512, shift0-best_nonzero=0.233634
- observed `deltaC_gain`: shift0=0.328706, block p=0.00497512, shift0-best_nonzero=0.094916

## Interpretation

Observed phi readout concentration survives FDR, but similar concentration also appears in control Chapter7 directories. This supports the presence of localized phi selection, but does not yet establish specificity to a D12RG/golden-carrier readout.
