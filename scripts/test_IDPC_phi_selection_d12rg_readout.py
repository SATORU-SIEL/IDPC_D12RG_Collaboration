#!/usr/bin/env python3
"""Test IDPC phi localized selection as a D12 readout candidate.

This structural-layer test has two parts:

1. Reuse IDPC Chapter7 block-permutation and temporal-shift outputs to test
   whether localized phi selection is robust.
2. Apply a frozen 12-bin readout diagnostic on the phi coordinate and test
   whether selection weights concentrate non-randomly across readout bins.

The output is a frozen structural readout diagnostic for phi-localized selection.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


SCORE_COLUMNS = ("sharp", "deltaC")


def bh_fdr(p_values: list[float]) -> list[float]:
    p = np.asarray(p_values, dtype=float)
    out = np.full_like(p, np.nan)
    valid = np.isfinite(p)
    if not valid.any():
        return out.tolist()
    pv = p[valid]
    order = np.argsort(pv)
    ranked = pv[order]
    n = len(ranked)
    q_ranked = ranked * n / np.arange(1, n + 1)
    q_ranked = np.minimum.accumulate(q_ranked[::-1])[::-1]
    q = np.empty_like(q_ranked)
    q[order] = np.clip(q_ranked, 0, 1)
    out[valid] = q
    return out.tolist()


def chapter7_dirs(input_root: Path) -> list[Path]:
    return sorted(path for path in input_root.rglob("Chapter7") if path.is_dir())


def condition_from_path(path: Path) -> str:
    text = str(path).lower()
    if "idpc_reproduction/IDPC_Reproduction/Chapter7".lower() in text:
        return "observed"
    if any(token in text for token in ["surrogate", "random", "derangement", "shift", "reverse"]):
        return "control"
    return "other"


def display_path(path: Path, input_root: Path) -> str:
    try:
        return str(path.relative_to(input_root))
    except ValueError:
        return path.name


def empirical_p_high(observed: float, null_values: np.ndarray) -> float:
    null_values = null_values[np.isfinite(null_values)]
    if not np.isfinite(observed) or len(null_values) == 0:
        return np.nan
    return float((1.0 + np.sum(null_values >= observed)) / (len(null_values) + 1.0))


def fixed_phi_bins(phi: pd.Series, n_bins: int = 12) -> np.ndarray:
    ranks = phi.rank(method="first", pct=True).to_numpy()
    bins = np.floor(np.clip(ranks, 0, 1 - 1e-12) * n_bins).astype(int)
    return bins


def weighted_resultant(bin_ids: np.ndarray, weights: np.ndarray, n_bins: int = 12) -> float:
    weights = np.asarray(weights, dtype=float)
    weights = np.where(np.isfinite(weights), weights, 0.0)
    weights = weights - min(float(np.min(weights)), 0.0)
    total = float(np.sum(weights))
    if total <= 0:
        return np.nan
    angles = 2.0 * np.pi * np.asarray(bin_ids, dtype=float) / n_bins
    vector = np.sum(weights * np.exp(1j * angles)) / total
    return float(np.abs(vector))


def readout_concentration_test(
    df: pd.DataFrame,
    score_col: str,
    n_perm: int,
    rng: np.random.Generator,
) -> dict[str, object]:
    needed = {"phi", score_col}
    if not needed.issubset(df.columns):
        return {
            "score_column": score_col,
            "status": "excluded",
            "exclusion_reason": f"missing columns: {sorted(needed - set(df.columns))}",
        }
    part = df[["phi", score_col]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(part) < 12:
        return {
            "score_column": score_col,
            "status": "excluded",
            "exclusion_reason": "fewer than 12 valid rows",
        }

    bins = fixed_phi_bins(part["phi"], 12)
    weights = part[score_col].to_numpy(dtype=float)
    observed = weighted_resultant(bins, weights, 12)
    null = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        shuffled = np.array(weights, copy=True)
        rng.shuffle(shuffled)
        null[i] = weighted_resultant(bins, shuffled, 12)
    raw_p = empirical_p_high(observed, null)
    counts = np.bincount(bins, weights=np.maximum(weights, 0), minlength=12)
    sd = float(np.std(null, ddof=1)) if n_perm > 1 else np.nan
    z = (observed - float(np.mean(null))) / sd if sd and np.isfinite(sd) else np.nan
    return {
        "score_column": score_col,
        "status": "tested",
        "exclusion_reason": "",
        "n_rows": len(part),
        "observed_resultant": observed,
        "null_mean": float(np.mean(null)),
        "null_sd": sd,
        "z_score": z,
        "raw_p": raw_p,
        "weighted_12bin_counts": ";".join(f"{x:.8g}" for x in counts),
    }


def run_tests(input_root: Path, n_perm: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    robustness_rows = []
    readout_rows = []

    for directory in chapter7_dirs(input_root):
        condition = condition_from_path(directory)
        block_path = directory / "block_permutation_test.csv"
        shift_path = directory / "temporal_shift_test.csv"
        scored_path = directory / "best_true_search_scored_points.csv"

        if block_path.exists() and shift_path.exists():
            block = pd.read_csv(block_path)
            shift = pd.read_csv(shift_path)
            shift0 = shift[shift.get("shift", pd.Series(dtype=float)).eq(0)]
            for metric in ["switch_gain", "deltaC_gain"]:
                if metric not in block.columns or metric not in shift.columns or shift0.empty:
                    continue
                observed = float(shift0.iloc[0][metric])
                nonzero = shift[~shift.get("shift", pd.Series(dtype=float)).eq(0)]
                robustness_rows.append({
                    "chapter7_dir": display_path(directory, input_root),
                    "condition": condition,
                    "metric": metric,
                    "observed_shift0": observed,
                    "block_null_mean": float(block[metric].mean()),
                    "block_null_sd": float(block[metric].std(ddof=1)),
                    "block_empirical_p": empirical_p_high(observed, block[metric].to_numpy(dtype=float)),
                    "best_nonzero_shift": float(nonzero[metric].max()) if len(nonzero) else np.nan,
                    "shift0_minus_best_nonzero_shift": (
                        observed - float(nonzero[metric].max()) if len(nonzero) else np.nan
                    ),
                })

        if scored_path.exists():
            scored = pd.read_csv(scored_path)
            for score_col in SCORE_COLUMNS:
                row = readout_concentration_test(scored, score_col, n_perm, rng)
                row.update({
                    "chapter7_dir": display_path(directory, input_root),
                    "condition": condition,
                    "n_perm": n_perm,
                })
                readout_rows.append(row)

    robustness = pd.DataFrame(robustness_rows)
    readout = pd.DataFrame(readout_rows)
    if "raw_p" in readout.columns:
        tested = readout["status"].eq("tested")
        q_values = [np.nan] * len(readout)
        tested_q = bh_fdr(readout.loc[tested, "raw_p"].astype(float).tolist())
        for idx, q in zip(readout.index[tested], tested_q):
            q_values[idx] = q
        readout["fdr_q"] = q_values
    return robustness, readout


def write_summary(output_path: Path, robustness: pd.DataFrame, readout: pd.DataFrame) -> None:
    obs_robust = robustness[robustness.get("condition", pd.Series(dtype=str)).eq("observed")]
    obs_readout = readout[
        readout.get("condition", pd.Series(dtype=str)).eq("observed")
        & readout.get("status", pd.Series(dtype=str)).eq("tested")
    ]
    control_readout = readout[
        readout.get("condition", pd.Series(dtype=str)).eq("control")
        & readout.get("status", pd.Series(dtype=str)).eq("tested")
    ]
    readout_hits = obs_readout[obs_readout.get("fdr_q", pd.Series(dtype=float)).le(0.05)]
    control_hits = control_readout[
        control_readout.get("fdr_q", pd.Series(dtype=float)).le(0.05)
    ]
    lines = [
        "# Phi Localized Selection D12 Readout Test",
        "",
        "## Purpose",
        "",
        (
            "This structural-layer test checks whether Chapter7 phi localized "
            "selection is robust against IDPC block/shift controls and whether "
            "selection weights concentrate across a frozen 12-bin phi readout."
        ),
        "",
        "## Results",
        "",
        f"- robustness rows: {len(robustness)}",
        f"- observed robustness rows: {len(obs_robust)}",
        f"- readout tests: {len(readout)}",
        f"- observed readout tests: {len(obs_readout)}",
        f"- observed readout tests surviving FDR q<=0.05: {len(readout_hits)}",
        f"- control readout tests surviving FDR q<=0.05: {len(control_hits)}",
        "",
    ]
    if len(obs_robust):
        for _, row in obs_robust.iterrows():
            lines.append(
                f"- observed {row['metric']}: shift0={row['observed_shift0']:.6g}, "
                f"block p={row['block_empirical_p']:.6g}, "
                f"shift0-best_nonzero={row['shift0_minus_best_nonzero_shift']:.6g}"
            )
    lines.extend([
        "",
        "## Interpretation",
        "",
    ])
    if len(readout_hits) and len(control_hits) == 0:
        lines.append(
            "At least one observed phi readout concentration test survives FDR. "
            "This supports further D12 readout testing at the IDPC structural "
            "layer, but does not prove D12RG."
        )
    elif len(readout_hits) and len(control_hits):
        lines.append(
            "Observed phi readout concentration survives FDR, but similar "
            "concentration also appears in control Chapter7 directories. This "
            "supports the presence of localized phi selection, but does not yet "
            "establish specificity to a D12RG/golden-carrier readout."
        )
    else:
        lines.append(
            "The observed phi selection robustness can be evaluated separately "
            "from the 12-bin readout diagnostic. The current D12 readout "
            "concentration test does not survive FDR for observed Chapter7 rows."
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260606)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    robustness, readout = run_tests(args.input_root, args.n_perm, args.seed)

    robustness_path = args.output_dir / "IDPC_phi_selection_robustness_results.csv"
    readout_path = args.output_dir / "IDPC_phi_selection_d12_readout_results.csv"
    summary_path = args.output_dir / "IDPC_phi_selection_d12_readout_summary.md"
    robustness.to_csv(robustness_path, index=False)
    readout.to_csv(readout_path, index=False)
    write_summary(summary_path, robustness, readout)

    print(f"wrote {robustness_path}")
    print(f"wrote {readout_path}")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
