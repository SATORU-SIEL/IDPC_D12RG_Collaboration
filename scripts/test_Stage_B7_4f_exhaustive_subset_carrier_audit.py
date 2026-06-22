#!/usr/bin/env python3
"""Stage B7.4f exhaustive subset robustness and arithmetic carrier proxy audit."""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
REGISTERED_SURVIVORS = {"P10", "P5", "P21", "P15"}
ARITHMETIC_MARKERS = [
    "cyclotomic_recognized_marker",
    "x3_interaction_marker",
    "complement_direction_marker",
    "group_completion_proxy",
]
READOUT_COLS = [
    "c12_mean",
    "n_positive_specificity_controls",
    "min_specificity_margin",
    "side_correspondence_margin",
    "ring_orientation_margin",
    "twelvefold_neighbor_margin",
]


def zscore(values: pd.Series) -> pd.Series:
    x = pd.to_numeric(values, errors="coerce")
    sd = x.std(ddof=0)
    if not np.isfinite(sd) or sd == 0:
        return pd.Series(np.zeros(len(x)), index=x.index)
    return (x - x.mean()) / sd


def percentile_ge(null: np.ndarray, observed: float) -> float:
    return float(np.mean(null <= observed))


def rank_desc(null: np.ndarray, observed: float) -> int:
    return int(1 + np.sum(null > observed))


def build_subset_table(merged: pd.DataFrame) -> pd.DataFrame:
    df = merged.copy().reset_index(drop=True)
    for col in ARITHMETIC_MARKERS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(float)
    for col in READOUT_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["joint_arithmetic_score"] = df[ARITHMETIC_MARKERS].mean(axis=1)
    df["readout_score"] = (
        zscore(df["c12_mean"]).fillna(0)
        + zscore(df["n_positive_specificity_controls"]).fillna(0)
        + zscore(df["min_specificity_margin"]).fillna(0)
        + zscore(df["side_correspondence_margin"]).fillna(0)
        + zscore(df["twelvefold_neighbor_margin"]).fillna(0)
    )
    df["joint_readout_arithmetic_score"] = zscore(df["readout_score"]) + zscore(df["joint_arithmetic_score"])

    rows = []
    for combo in itertools.combinations(range(len(df)), 4):
        sub = df.iloc[list(combo)]
        labels = tuple(sorted(sub["heldout_label"].astype(str).tolist(), key=lambda x: int(x[1:])))
        rows.append({
            "subset_labels": "|".join(labels),
            "is_registered_survivor_set": set(labels) == REGISTERED_SURVIVORS,
            "mean_c12": float(sub["c12_mean"].mean()),
            "mean_positive_specificity_controls": float(sub["n_positive_specificity_controls"].mean()),
            "mean_min_specificity_margin": float(sub["min_specificity_margin"].mean()),
            "mean_side_correspondence_margin": float(sub["side_correspondence_margin"].mean()),
            "mean_ring_orientation_margin": float(sub["ring_orientation_margin"].mean()),
            "mean_twelvefold_neighbor_margin": float(sub["twelvefold_neighbor_margin"].mean()),
            "cyclotomic_marker_rate": float(sub["cyclotomic_recognized_marker"].mean()),
            "x3_marker_rate": float(sub["x3_interaction_marker"].mean()),
            "complement_direction_marker_rate": float(sub["complement_direction_marker"].mean()),
            "group_completion_proxy_rate": float(sub["group_completion_proxy"].mean()),
            "joint_arithmetic_score": float(sub["joint_arithmetic_score"].mean()),
            "joint_readout_arithmetic_score": float(sub["joint_readout_arithmetic_score"].mean()),
        })
    return pd.DataFrame(rows)


def summarize_registered_subset(subsets: pd.DataFrame) -> pd.DataFrame:
    obs_row = subsets[subsets["is_registered_survivor_set"]].iloc[0]
    metrics = [
        "mean_c12",
        "mean_positive_specificity_controls",
        "mean_min_specificity_margin",
        "mean_side_correspondence_margin",
        "mean_ring_orientation_margin",
        "mean_twelvefold_neighbor_margin",
        "cyclotomic_marker_rate",
        "x3_marker_rate",
        "complement_direction_marker_rate",
        "group_completion_proxy_rate",
        "joint_arithmetic_score",
        "joint_readout_arithmetic_score",
    ]
    rows = []
    for metric in metrics:
        null = pd.to_numeric(subsets[metric], errors="coerce").dropna().to_numpy(float)
        observed = float(obs_row[metric])
        rows.append({
            "metric": metric,
            "observed_registered_subset": observed,
            "all_subset_mean": float(np.mean(null)),
            "all_subset_sd": float(np.std(null)),
            "percentile_ge": percentile_ge(null, observed),
            "rank_descending": rank_desc(null, observed),
            "n_subsets": int(len(null)),
        })
    return pd.DataFrame(rows)


def carrier_proxy_table(merged: pd.DataFrame) -> pd.DataFrame:
    df = merged.copy()
    for col in ARITHMETIC_MARKERS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(float)
    for col in READOUT_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["registered_survivor_carrier"] = df["heldout_label"].isin(REGISTERED_SURVIVORS).astype(float)
    df["ordinary_c12_carrier"] = 1.0
    df["receiver_standpoint_magnitude_c_proxy"] = zscore(df["mean_receiver_total"]).fillna(0) + zscore(df["selected_b74b_event_count"]).fillna(0)
    df["arithmetic_completion_carrier"] = df[ARITHMETIC_MARKERS].mean(axis=1)
    df["cyclotomic_only_carrier"] = df["cyclotomic_recognized_marker"]
    df["x3_only_carrier"] = df["x3_interaction_marker"]
    df["complement_direction_only_carrier"] = df["complement_direction_marker"]
    df["collapsed_fold_arithmetic_control"] = df["survival_group"].eq("collapsed_or_weak").astype(float) * df["arithmetic_completion_carrier"]

    carriers = [
        "ordinary_c12_carrier",
        "receiver_standpoint_magnitude_c_proxy",
        "registered_survivor_carrier",
        "arithmetic_completion_carrier",
        "cyclotomic_only_carrier",
        "x3_only_carrier",
        "complement_direction_only_carrier",
        "collapsed_fold_arithmetic_control",
    ]
    readouts = [
        "c12_mean",
        "n_positive_specificity_controls",
        "min_specificity_margin",
        "side_correspondence_margin",
        "ring_orientation_margin",
        "twelvefold_neighbor_margin",
    ]
    rows = []
    for carrier in carriers:
        weights = pd.to_numeric(df[carrier], errors="coerce").fillna(0).to_numpy(float)
        active = weights > 0
        row = {
            "carrier": carrier,
            "n_active_folds": int(active.sum()),
            "mean_weight": float(np.mean(weights)),
        }
        for readout in readouts:
            values = pd.to_numeric(df[readout], errors="coerce").to_numpy(float)
            if active.any():
                row[f"active_mean_{readout}"] = float(np.nanmean(values[active]))
            else:
                row[f"active_mean_{readout}"] = np.nan
            if np.nansum(weights) > 0:
                row[f"weighted_mean_{readout}"] = float(np.nansum(weights * np.nan_to_num(values, nan=0.0)) / np.nansum(weights))
            else:
                row[f"weighted_mean_{readout}"] = np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def write_summary(path: Path, subset_summary: pd.DataFrame, carrier_summary: pd.DataFrame, args: argparse.Namespace) -> None:
    top_subset = subset_summary[subset_summary["metric"].isin([
        "joint_arithmetic_score",
        "joint_readout_arithmetic_score",
        "mean_c12",
        "mean_positive_specificity_controls",
        "mean_min_specificity_margin",
        "cyclotomic_marker_rate",
        "x3_marker_rate",
        "complement_direction_marker_rate",
    ])]
    lines = [
        "# Stage B7.4f Exhaustive Four-Index Robustness and Arithmetic-Completion Carrier Audit",
        "",
        "Status: executed after `Stage_B7_4f_preregistration_email_sent.md`.",
        "",
        "## Layer 1: Registered Four-Index Subset Robustness",
        "",
        top_subset.to_csv(index=False).strip(),
        "",
        "## Layer 2: Carrier / Readout Proxy Summary",
        "",
        carrier_summary.to_csv(index=False).strip(),
        "",
        "## Decision Guardrail",
        "",
        "- If Layer 1 passes and Layer 2 passes, C12 survival may require both state condition and arithmetic completion.",
        "- If Layer 1 passes but Layer 2 fails, B7.4e/B7.4f support arithmetic survivor-index enrichment, but not a carrier mechanism.",
        "- If Layer 1 fails, B7.4e remains bounded as an exploratory pre-audit signal.",
        "- B7.4f makes no finite-group-algebra proof, paired Phi12 quadrature confirmation, or Jacobi 12-product mechanism claim.",
        "",
        "## Settings",
        "",
        f"- registered_survivors: {sorted(REGISTERED_SURVIVORS)}",
        f"- b74e_join: {args.b74e_join}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    merged = pd.read_csv(args.b74e_join)
    subsets = build_subset_table(merged)
    subset_summary = summarize_registered_subset(subsets)
    carrier_summary = carrier_proxy_table(merged)

    subsets.to_csv(outdir / "Stage_B7_4f_exhaustive_four_index_subsets.csv", index=False)
    subset_summary.to_csv(outdir / "Stage_B7_4f_registered_subset_percentiles.csv", index=False)
    carrier_summary.to_csv(outdir / "Stage_B7_4f_carrier_proxy_summary.csv", index=False)
    write_summary(outdir / "Stage_B7_4f_execution_summary.md", subset_summary, carrier_summary, args)

    print(f"output_dir: {outdir}")
    print("\nRegistered subset percentiles")
    print(subset_summary.to_string(index=False))
    print("\nCarrier proxy summary")
    print(carrier_summary.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_4f")
    parser.add_argument("--b74e-join", type=Path, default=REPO / "reports/stage_b7_4e/Stage_B7_4e_fold_index_readout_join.csv")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
