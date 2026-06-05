# FES Transition Ladder Test

## Purpose

This structural-layer test asks whether IDPC FES state sequences show a 5 states -> 10 unordered transitions -> 20 directed transitions expansion more strongly than order-destroying label shuffle nulls.

## Results

- tested sequences: 220
- FDR q<=0.05 sequences: 0
- sequences where 5-10-20 ranked first among fixed ladders: 74

## Interpretation

The 5->10->20 transition expansion did not survive the current shuffle-null and FDR controls.
