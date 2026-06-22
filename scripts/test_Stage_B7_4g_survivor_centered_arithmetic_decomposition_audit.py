#!/usr/bin/env python3
"""Stage B7.4g survivor-centered arithmetic decomposition audit."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
REGISTERED_SURVIVORS = {"P10", "P5", "P21", "P15"}
READOUT_COLS = [
    "c12_mean",
    "n_positive_specificity_controls",
    "min_specificity_margin",
    "side_correspondence_margin",
    "ring_orientation_margin",
    "twelvefold_neighbor_margin",
]
REFERENCE_METRICS = [
    "mean_c12",
    "mean_positive_specificity_controls",
    "mean_min_specificity_margin",
    "joint_arithmetic_score",
    "joint_readout_arithmetic_score",
]


def zscore(values: pd.Series) -> pd.Series:
    x = pd.to_numeric(values, errors="coerce")
    sd = x.std(ddof=0)
    if not np.isfinite(sd) or sd == 0:
        return pd.Series(np.zeros(len(x)), index=x.index)
    return (x - x.mean()) / sd


def safe_div(num: float, den: float) -> float:
    if den == 0 or not np.isfinite(den):
        return np.nan
    return float(num / den)


def add_proxy_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    marker_cols = [
        "cyclotomic_recognized_marker",
        "x3_interaction_marker",
        "complement_direction_marker",
        "group_completion_proxy",
    ]
    for col in marker_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0).astype(float)
    out["registered_survivor_set"] = out["heldout_label"].isin(REGISTERED_SURVIVORS).astype(float)
    out["cyclotomic_component"] = out["cyclotomic_recognized_marker"]
    out["x3_interaction_component"] = out["x3_interaction_marker"]
    out["complement_direction_component"] = out["complement_direction_marker"]
    out["cyclotomic_plus_x3_decomposition"] = (
        (out["cyclotomic_component"] > 0) | (out["x3_interaction_component"] > 0)
    ).astype(float)
    out["broad_group_completion_proxy"] = out["group_completion_proxy"]
    out["arithmetic_completion_composite"] = out[marker_cols].mean(axis=1)
    out["collapsed_arithmetic_control"] = (
        out["survival_group"].eq("collapsed_or_weak").astype(float)
        * out["arithmetic_completion_composite"]
    )
    return out


def proxy_support_summary(df: pd.DataFrame) -> pd.DataFrame:
    target = df["registered_survivor_set"].to_numpy(float) > 0
    target_n = int(target.sum())
    proxies = [
        "registered_survivor_set",
        "cyclotomic_component",
        "x3_interaction_component",
        "complement_direction_component",
        "cyclotomic_plus_x3_decomposition",
        "broad_group_completion_proxy",
        "arithmetic_completion_composite",
        "collapsed_arithmetic_control",
    ]
    rows = []
    for proxy in proxies:
        weights = pd.to_numeric(df[proxy], errors="coerce").fillna(0.0).to_numpy(float)
        active = weights > 0
        overlap_active = active & target
        support_n = int(active.sum())
        overlap_n = int(overlap_active.sum())
        precision = safe_div(overlap_n, support_n)
        recall = safe_div(overlap_n, target_n)
        f1 = safe_div(2 * precision * recall, precision + recall)
        union_n = int((active | target).sum())
        rows.append({
            "proxy": proxy,
            "n_active_folds": support_n,
            "n_registered_overlap": overlap_n,
            "n_extra_active_folds": int((active & ~target).sum()),
            "precision_vs_registered": precision,
            "recall_vs_registered": recall,
            "f1_vs_registered": f1,
            "jaccard_vs_registered": safe_div(overlap_n, union_n),
            "weight_on_registered_fraction": safe_div(float(weights[target].sum()), float(weights.sum())),
        })
    return pd.DataFrame(rows)


def proxy_readout_summary(df: pd.DataFrame, support_summary: pd.DataFrame) -> pd.DataFrame:
    proxies = support_summary["proxy"].tolist()
    global_sds = {
        col: pd.to_numeric(df[col], errors="coerce").std(ddof=0)
        for col in READOUT_COLS
    }
    ref = {}
    for col in READOUT_COLS:
        values = pd.to_numeric(df[col], errors="coerce")
        ref[col] = float(values[df["registered_survivor_set"] > 0].mean())

    rows = []
    for proxy in proxies:
        weights = pd.to_numeric(df[proxy], errors="coerce").fillna(0.0).to_numpy(float)
        active = weights > 0
        row = {"proxy": proxy, "n_active_folds": int(active.sum())}
        z_distance_terms = []
        for readout in READOUT_COLS:
            values = pd.to_numeric(df[readout], errors="coerce").to_numpy(float)
            active_mean = float(np.nanmean(values[active])) if active.any() else np.nan
            weighted_mean = (
                float(np.nansum(weights * np.nan_to_num(values, nan=0.0)) / np.nansum(weights))
                if np.nansum(weights) > 0
                else np.nan
            )
            row[f"active_mean_{readout}"] = active_mean
            row[f"weighted_mean_{readout}"] = weighted_mean
            sd = global_sds[readout]
            if np.isfinite(active_mean) and np.isfinite(sd) and sd > 0:
                z_distance_terms.append(((active_mean - ref[readout]) / sd) ** 2)
        row["z_distance_to_registered_readout"] = float(np.sqrt(np.sum(z_distance_terms)))
        row["c12_dilution_vs_registered"] = row["active_mean_c12_mean"] - ref["c12_mean"]
        row["positive_control_dilution_vs_registered"] = (
            row["active_mean_n_positive_specificity_controls"]
            - ref["n_positive_specificity_controls"]
        )
        row["min_margin_dilution_vs_registered"] = (
            row["active_mean_min_specificity_margin"]
            - ref["min_specificity_margin"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def subset_reference_summary(subsets: pd.DataFrame) -> pd.DataFrame:
    registered = subsets[subsets["is_registered_survivor_set"]].iloc[0]
    rows = []
    for metric in REFERENCE_METRICS:
        values = pd.to_numeric(subsets[metric], errors="coerce").dropna().to_numpy(float)
        observed = float(registered[metric])
        rows.append({
            "metric": metric,
            "registered_value": observed,
            "random_four_fold_mean": float(np.mean(values)),
            "random_four_fold_sd": float(np.std(values)),
            "registered_rank_descending": int(1 + np.sum(values > observed)),
            "registered_percentile_ge": float(np.mean(values <= observed)),
            "n_four_fold_subsets": int(len(values)),
        })
    return pd.DataFrame(rows)


def write_summary(
    path: Path,
    support: pd.DataFrame,
    readout: pd.DataFrame,
    random_ref: pd.DataFrame,
    args: argparse.Namespace,
) -> None:
    merged = support.merge(
        readout[[
            "proxy",
            "active_mean_c12_mean",
            "active_mean_n_positive_specificity_controls",
            "active_mean_min_specificity_margin",
            "z_distance_to_registered_readout",
            "c12_dilution_vs_registered",
            "positive_control_dilution_vs_registered",
            "min_margin_dilution_vs_registered",
        ]],
        on="proxy",
        how="left",
    )
    lines = [
        "# Stage B7.4g Survivor-Centered Arithmetic Decomposition Audit",
        "",
        "Status: executed after `Stage_B7_4g_preregistration_email_sent.md`.",
        "",
        "## Registered Question",
        "",
        "Which arithmetic decomposition best explains the registered survivor set?",
        "",
        "B7.4g treats P10/P5/P21/P15 as the empirical target fixed by B7.4f, then compares arithmetic decompositions as explanatory candidates.",
        "",
        "## Proxy Explanation Summary",
        "",
        merged.to_csv(index=False).strip(),
        "",
        "## Random Four-Fold Reference",
        "",
        random_ref.to_csv(index=False).strip(),
        "",
        "## Decision Boundary",
        "",
        "- If the registered survivor set remains strongest, the empirical carrier remains the survivor structure itself.",
        "- If cyclotomic-only and x3-only explain complementary parts and their union approaches the registered set, the survivor structure may decompose into cyclotomic and x3-interaction components.",
        "- If broad group-completion weakens or dilutes the readout, a generalized arithmetic-completion carrier remains unsupported under this operationalization.",
        "- B7.4g does not prove finite group algebra, paired Phi12 quadrature, or a Jacobi 12-product mechanism.",
        "",
        "## Settings",
        "",
        f"- registered_survivors: {sorted(REGISTERED_SURVIVORS)}",
        f"- b74e_join: {args.b74e_join}",
        f"- b74f_subsets: {args.b74f_subsets}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    joined = pd.read_csv(args.b74e_join)
    joined = add_proxy_columns(joined)
    subsets = pd.read_csv(args.b74f_subsets)

    support = proxy_support_summary(joined)
    readout = proxy_readout_summary(joined, support)
    random_ref = subset_reference_summary(subsets)

    support.to_csv(outdir / "Stage_B7_4g_proxy_support_summary.csv", index=False)
    readout.to_csv(outdir / "Stage_B7_4g_proxy_readout_summary.csv", index=False)
    random_ref.to_csv(outdir / "Stage_B7_4g_random_four_fold_reference.csv", index=False)
    write_summary(
        outdir / "Stage_B7_4g_execution_summary.md",
        support,
        readout,
        random_ref,
        args,
    )

    print(f"output_dir: {outdir}")
    print("\nProxy support summary")
    print(support.to_string(index=False))
    print("\nProxy readout summary")
    print(readout.to_string(index=False))
    print("\nRandom four-fold reference")
    print(random_ref.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_4g")
    parser.add_argument(
        "--b74e-join",
        type=Path,
        default=REPO / "reports/stage_b7_4e/Stage_B7_4e_fold_index_readout_join.csv",
    )
    parser.add_argument(
        "--b74f-subsets",
        type=Path,
        default=REPO / "reports/stage_b7_4f/Stage_B7_4f_exhaustive_four_index_subsets.csv",
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
