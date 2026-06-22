#!/usr/bin/env python3
"""Stage B7.4d survival-condition audit for held-out C12 folds."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import test_Stage_B7_3a_c12_specificity_h24_collective_necessity_audit as b73a  # noqa: E402


PRIMARY_R_STAR = "receiver_standpoint_magnitude_c"
REGISTERED_SURVIVORS = ["P10", "P5", "P21", "P15"]
TOPOLOGY_EFFECTS = [
    "effect_vs_no_topology",
    "effect_vs_reversed",
    "effect_vs_side_broken",
    "effect_vs_shuffled",
    "effect_vs_c10",
    "effect_vs_c11",
    "effect_vs_c13",
    "effect_vs_c14",
]
PROFILE_COLUMNS = [
    "event_count",
    "mean_abs_rstar",
    "q75_abs_rstar",
    "mean_receiver_asymmetry",
    "mean_receiver_total",
    "mean_standpoint_separation",
    "mean_magnitude_balance",
    "mean_magnitude_total",
    "selected_b74b_event_count",
    "selected_b74b_mean_strength",
    "selected_b74b_phase_coverage",
    "selected_b74b_phase_concentration",
]


def phase_coverage(phase: pd.Series | np.ndarray) -> float:
    values = np.mod(pd.to_numeric(pd.Series(phase), errors="coerce").dropna().to_numpy(float), 2.0 * np.pi)
    if len(values) == 0:
        return 0.0
    bins = np.floor(12.0 * values / (2.0 * np.pi)).astype(int)
    return float(len(set(bins.tolist())) / 12.0)


def phase_concentration(phase: pd.Series | np.ndarray) -> float:
    values = pd.to_numeric(pd.Series(phase), errors="coerce").dropna().to_numpy(float)
    if len(values) == 0:
        return np.nan
    return float(np.abs(np.mean(np.exp(1j * values))))


def cohen_d(a: pd.Series, b: pd.Series) -> float:
    av = pd.to_numeric(a, errors="coerce").dropna().to_numpy(float)
    bv = pd.to_numeric(b, errors="coerce").dropna().to_numpy(float)
    if len(av) < 2 or len(bv) < 2:
        return np.nan
    pooled = np.sqrt(((len(av) - 1) * np.nanvar(av, ddof=1) + (len(bv) - 1) * np.nanvar(bv, ddof=1)) / (len(av) + len(bv) - 2))
    if not np.isfinite(pooled) or pooled == 0.0:
        return np.nan
    return float((np.nanmean(av) - np.nanmean(bv)) / pooled)


def load_features(args: argparse.Namespace) -> pd.DataFrame:
    return b73a.add_representation_scores(b73a.load_b72_features(args))


def classify_from_b74b(summary: pd.DataFrame) -> pd.DataFrame:
    table = summary[summary["heldout_label"].ne("AGGREGATE_MEAN")].copy()
    for col in TOPOLOGY_EFFECTS + ["c12_mean", "n_positive_specificity_controls", "min_specificity_margin"]:
        table[col] = pd.to_numeric(table[col], errors="coerce")
    table["is_registered_survivor"] = table["heldout_label"].isin(REGISTERED_SURVIVORS)
    table["is_strict_survivor"] = (
        table["c12_mean"].gt(0)
        & table["n_positive_specificity_controls"].ge(7)
        & table["min_specificity_margin"].ge(-0.001)
    )
    table["is_collapsed"] = (
        table["n_positive_specificity_controls"].le(1)
        | table["c12_mean"].lt(0) & table["min_specificity_margin"].lt(-0.005)
    )
    table["survival_group"] = np.select(
        [table["is_registered_survivor"], table["is_collapsed"]],
        ["registered_survivor", "collapsed_or_weak"],
        default="intermediate",
    )
    table["side_correspondence_margin"] = table[["effect_vs_side_broken", "effect_vs_shuffled"]].mean(axis=1)
    table["ring_orientation_margin"] = table["effect_vs_reversed"]
    table["twelvefold_neighbor_margin"] = table[["effect_vs_c10", "effect_vs_c11", "effect_vs_c13", "effect_vs_c14"]].mean(axis=1)
    return table


def build_condition_profiles(features: pd.DataFrame, selected_events: pd.DataFrame) -> pd.DataFrame:
    selected = selected_events.copy()
    selected["heldout_label"] = selected["heldout_label"].astype(str)
    rows = []
    for label, sub in features.groupby(features["label"].astype(str), sort=True):
        rstar = pd.to_numeric(sub[PRIMARY_R_STAR], errors="coerce")
        ab_recv = pd.to_numeric(sub["ab_receiver_side"], errors="coerce").abs()
        ba_recv = pd.to_numeric(sub["ba_receiver_side"], errors="coerce").abs()
        ab_pol = pd.to_numeric(sub["ab_standpoint_polarity"], errors="coerce")
        ba_pol = pd.to_numeric(sub["ba_standpoint_polarity"], errors="coerce")
        ab_mag = pd.to_numeric(sub["ab_standpoint_magnitude"], errors="coerce")
        ba_mag = pd.to_numeric(sub["ba_standpoint_magnitude"], errors="coerce")
        ev = selected[selected["heldout_label"].eq(label)]
        rows.append({
            "heldout_label": label,
            "event_count": int(len(sub)),
            "mean_abs_rstar": float(rstar.abs().mean()),
            "q75_abs_rstar": float(rstar.abs().quantile(0.75)),
            "mean_receiver_asymmetry": float((ab_recv - ba_recv).mean()),
            "mean_receiver_total": float((ab_recv + ba_recv).mean()),
            "mean_standpoint_separation": float((ab_pol - ba_pol).abs().mean()),
            "mean_magnitude_balance": float(-1.0 * (ab_mag - ba_mag).abs().mean()),
            "mean_magnitude_total": float((ab_mag + ba_mag).mean()),
            "selected_b74b_event_count": int(len(ev)),
            "selected_b74b_mean_strength": float(pd.to_numeric(ev["strength"], errors="coerce").mean()) if len(ev) else np.nan,
            "selected_b74b_phase_coverage": phase_coverage(ev["phase"]) if len(ev) else 0.0,
            "selected_b74b_phase_concentration": phase_concentration(ev["phase"]) if len(ev) else np.nan,
        })
    return pd.DataFrame(rows)


def summarize_b74c_stability(contrasts: pd.DataFrame) -> pd.DataFrame:
    q = contrasts[contrasts["selection_mode"].eq("quantile")].copy()
    for col in TOPOLOGY_EFFECTS + ["c12_mean", "n_positive_specificity_controls", "min_specificity_margin"]:
        q[col] = pd.to_numeric(q[col], errors="coerce")
    rows = []
    for label, sub in q.groupby("heldout_label", sort=True):
        rows.append({
            "heldout_label": label,
            "b74c_n_thresholds": int(sub["selection_value"].nunique()),
            "b74c_mean_c12": float(sub["c12_mean"].mean()),
            "b74c_mean_positive_controls": float(sub["n_positive_specificity_controls"].mean()),
            "b74c_max_positive_controls": float(sub["n_positive_specificity_controls"].max()),
            "b74c_mean_min_margin": float(sub["min_specificity_margin"].mean()),
            "b74c_best_min_margin": float(sub["min_specificity_margin"].max()),
            "b74c_mean_side_margin": float(sub[["effect_vs_side_broken", "effect_vs_shuffled"]].mean(axis=1).mean()),
            "b74c_mean_orientation_margin": float(sub["effect_vs_reversed"].mean()),
            "b74c_mean_neighbor_margin": float(sub[["effect_vs_c10", "effect_vs_c11", "effect_vs_c13", "effect_vs_c14"]].mean(axis=1).mean()),
        })
    return pd.DataFrame(rows)


def compare_groups(merged: pd.DataFrame) -> pd.DataFrame:
    survivors = merged[merged["survival_group"].eq("registered_survivor")]
    collapsed = merged[merged["survival_group"].eq("collapsed_or_weak")]
    rows = []
    compare_cols = PROFILE_COLUMNS + [
        "c12_mean",
        "n_positive_specificity_controls",
        "min_specificity_margin",
        "side_correspondence_margin",
        "ring_orientation_margin",
        "twelvefold_neighbor_margin",
        "b74c_mean_c12",
        "b74c_mean_positive_controls",
        "b74c_mean_min_margin",
        "b74c_mean_side_margin",
        "b74c_mean_orientation_margin",
        "b74c_mean_neighbor_margin",
    ]
    for col in compare_cols:
        if col not in merged.columns:
            continue
        s = pd.to_numeric(survivors[col], errors="coerce")
        c = pd.to_numeric(collapsed[col], errors="coerce")
        rows.append({
            "metric": col,
            "survivor_mean": float(s.mean()),
            "collapsed_mean": float(c.mean()),
            "survivor_minus_collapsed": float(s.mean() - c.mean()),
            "cohen_d_survivor_vs_collapsed": cohen_d(s, c),
            "n_survivor": int(s.notna().sum()),
            "n_collapsed": int(c.notna().sum()),
        })
    return pd.DataFrame(rows)


def write_summary(path: Path, merged: pd.DataFrame, group_compare: pd.DataFrame, args: argparse.Namespace) -> None:
    survivors = merged[merged["survival_group"].eq("registered_survivor")].copy()
    collapsed = merged[merged["survival_group"].eq("collapsed_or_weak")].copy()
    top_metrics = group_compare.reindex(group_compare["cohen_d_survivor_vs_collapsed"].abs().sort_values(ascending=False).index).head(12)
    survivor_cols = [
        "heldout_label",
        "c12_mean",
        "n_positive_specificity_controls",
        "min_specificity_margin",
        "side_correspondence_margin",
        "ring_orientation_margin",
        "twelvefold_neighbor_margin",
        "mean_abs_rstar",
        "selected_b74b_event_count",
        "selected_b74b_mean_strength",
        "selected_b74b_phase_coverage",
        "b74c_mean_positive_controls",
        "b74c_mean_min_margin",
    ]
    lines = [
        "# Stage B7.4d Survival-Condition Audit",
        "",
        "Status: executed after `Stage_B7_4d_preregistration_email_sent.md`.",
        "",
        "Primary frozen R*: `receiver_standpoint_magnitude_c`.",
        "",
        "## Registered Question",
        "",
        "B7.4d asks why P10/P5/P21/P15 survived comparatively in B7.4b, before adding a new Phi12 x Phi12 carrier hypothesis.",
        "",
        "## Registered Survivors",
        "",
        survivors[survivor_cols].to_csv(index=False).strip(),
        "",
        "## Collapsed Or Weak Comparison Set",
        "",
        collapsed[["heldout_label", "c12_mean", "n_positive_specificity_controls", "min_specificity_margin", "mean_abs_rstar", "selected_b74b_event_count", "selected_b74b_phase_coverage"]].to_csv(index=False).strip(),
        "",
        "## Survivor vs Collapsed Condition Differences",
        "",
        group_compare.to_csv(index=False).strip(),
        "",
        "## Largest Standardized Differences",
        "",
        top_metrics.to_csv(index=False).strip(),
        "",
        "## Interpretation Guardrail",
        "",
        "- If registered survivors share a reproducible condition profile, B7.4b/B7.4c revealed conditional C12 readout rather than simply falsifying C12.",
        "- If no condition profile separates survivors from collapsed folds, B7.3a remains bounded as a full-data topology-readout result without held-out robustness.",
        "- No paired Phi12 quadrature claim is made in B7.4d.",
        "",
        "## Settings",
        "",
        f"- registered_survivors: {REGISTERED_SURVIVORS}",
        f"- b74b_summary: {args.b74b_summary}",
        f"- b74b_events: {args.b74b_events}",
        f"- b74c_contrasts: {args.b74c_contrasts}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    features = load_features(args)
    b74b = classify_from_b74b(pd.read_csv(args.b74b_summary))
    profiles = build_condition_profiles(features, pd.read_csv(args.b74b_events))
    b74c = summarize_b74c_stability(pd.read_csv(args.b74c_contrasts))
    merged = b74b.merge(profiles, on="heldout_label", how="left").merge(b74c, on="heldout_label", how="left")
    group_compare = compare_groups(merged)

    merged.to_csv(outdir / "Stage_B7_4d_fold_condition_profiles.csv", index=False)
    group_compare.to_csv(outdir / "Stage_B7_4d_survivor_vs_collapsed_differences.csv", index=False)
    write_summary(outdir / "Stage_B7_4d_execution_summary.md", merged, group_compare, args)

    print(f"output_dir: {outdir}")
    print("\nRegistered survivors")
    print(merged[merged["survival_group"].eq("registered_survivor")][[
        "heldout_label",
        "c12_mean",
        "n_positive_specificity_controls",
        "min_specificity_margin",
        "mean_abs_rstar",
        "selected_b74b_event_count",
        "selected_b74b_phase_coverage",
        "b74c_mean_positive_controls",
        "b74c_mean_min_margin",
    ]].to_string(index=False))
    print("\nLargest standardized condition differences")
    top = group_compare.reindex(group_compare["cohen_d_survivor_vs_collapsed"].abs().sort_values(ascending=False).index).head(12)
    print(top.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_4d")
    parser.add_argument("--b74b-summary", type=Path, default=REPO / "reports/stage_b7_4b/Stage_B7_4b_heldout_summary_table.csv")
    parser.add_argument("--b74b-events", type=Path, default=REPO / "reports/stage_b7_4b/Stage_B7_4b_heldout_events.csv")
    parser.add_argument("--b74c-contrasts", type=Path, default=REPO / "reports/stage_b7_4c/Stage_B7_4c_fold_contrasts.csv")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=74440)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
