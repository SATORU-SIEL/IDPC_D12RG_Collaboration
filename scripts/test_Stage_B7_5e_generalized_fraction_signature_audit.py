#!/usr/bin/env python3
"""Stage B7.5e generalized N/M fraction signature audit.

This is a post-registered diagnostic layer over the frozen B7.5d topology
boundary outputs. Fractions are treated as diagnostics, not explanations.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
PRIMARY_COMPARISON = "full_minus_reverse"
FOCUS_FRACTIONS = {"1/4", "1/2", "3/4", "3/7", "2/11"}
CLASS_ORDER = ["reverse-stable", "boundary", "full-stable"]


def bounded_fraction(value: float, max_denominator: int, tol: float) -> tuple[str, int, int, float, bool, bool]:
    if not np.isfinite(value):
        return "nan", 0, 0, np.nan, False, False
    clipped = min(1.0, max(0.0, float(value)))
    frac = Fraction(clipped).limit_denominator(max_denominator)
    frac_value = frac.numerator / frac.denominator
    err = abs(clipped - frac_value)
    label = f"{frac.numerator}/{frac.denominator}"
    return label, frac.numerator, frac.denominator, err, err <= tol, frac.numerator > 1


def topology_tags(row: pd.Series) -> str:
    tags: list[str] = []
    topology = str(row.get("topology_arm", ""))
    base = str(row.get("base_topology", ""))
    kind = str(row.get("perturbation_kind", ""))
    n = int(row.get("node_count_n", row.get("n_nodes", -1)))
    if topology == "c12" or base == "c12":
        tags.append("c12_neighborhood")
    if topology == "c13" or base == "c13":
        tags.append("c13_full_branch")
    if topology == "c10" or base == "c10":
        tags.append("c10_boundary_candidate")
    if topology == "c14" or base == "c14":
        tags.append("c14_transition_probe")
    if kind == "reversed":
        tags.append("reversed")
    if "ring_share" in kind:
        tags.append("ring_sharing")
        jump = kind.rsplit("_", 1)[-1]
        tags.append(f"ring_share_{jump}")
    if n in {5, 10} or "ring_share_5" in tags or "ring_share_10" in tags:
        tags.append("5_or_10_proxy")
    if n in {7, 15, 21} or "ring_share_7" in tags:
        tags.append("x3_or_7mod12_proxy")
    if n % 2:
        tags.append("odd_n")
    else:
        tags.append("even_n")
    return "|".join(dict.fromkeys(tags)) if tags else "unassigned"


def scan_metric(rows: list[dict[str, object]], *, source: str, topology_arm: str, classification: str, metric: str, value: float, max_denominator: int, tol: float, tags: str, representation_arm: str = "", comparison: str = "") -> None:
    frac, numer, denom, err, close, n_gt_1 = bounded_fraction(value, max_denominator, tol)
    rows.append({
        "source": source,
        "topology_arm": topology_arm,
        "classification": classification,
        "representation_arm": representation_arm,
        "comparison": comparison,
        "metric": metric,
        "value": float(value) if np.isfinite(value) else np.nan,
        "nearest_fraction": frac,
        "numerator": numer,
        "denominator": denom,
        "abs_error_to_fraction": err,
        "is_close_to_fraction": close,
        "is_focus_fraction": frac in FOCUS_FRACTIONS,
        "has_numerator_gt_1": n_gt_1,
        "tags": tags,
    })


def build_scan(paired: pd.DataFrame, readout: pd.DataFrame, event_geometry: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    primary = paired[paired["comparison"].eq(PRIMARY_COMPARISON)].copy()
    class_by_topology = dict(zip(primary["topology_arm"], primary["classification"]))
    meta_by_topology = primary.drop_duplicates("topology_arm").set_index("topology_arm")
    rows: list[dict[str, object]] = []

    max_abs_delta = float(primary["mean_delta"].abs().max())
    max_ci_width = float((primary["bootstrap_ci_high"] - primary["bootstrap_ci_low"]).abs().max())
    for _, row in primary.iterrows():
        topology = str(row["topology_arm"])
        cls = str(row["classification"])
        tags = topology_tags(row)
        scan_metric(rows, source="paired_boundary", topology_arm=topology, classification=cls, comparison=PRIMARY_COMPARISON, metric="full_win_fraction", value=float(row["left_win_fraction"]), max_denominator=args.max_denominator, tol=args.tolerance, tags=tags)
        scan_metric(rows, source="paired_boundary", topology_arm=topology, classification=cls, comparison=PRIMARY_COMPARISON, metric="reverse_win_fraction", value=1.0 - float(row["left_win_fraction"]), max_denominator=args.max_denominator, tol=args.tolerance, tags=tags)
        if max_abs_delta > 0:
            scan_metric(rows, source="paired_boundary", topology_arm=topology, classification=cls, comparison=PRIMARY_COMPARISON, metric="abs_mean_delta_scaled", value=abs(float(row["mean_delta"])) / max_abs_delta, max_denominator=args.max_denominator, tol=args.tolerance, tags=tags)
        width = abs(float(row["bootstrap_ci_high"]) - float(row["bootstrap_ci_low"]))
        if max_ci_width > 0:
            scan_metric(rows, source="paired_boundary", topology_arm=topology, classification=cls, comparison=PRIMARY_COMPARISON, metric="ci_width_scaled", value=width / max_ci_width, max_denominator=args.max_denominator, tol=args.tolerance, tags=tags)

    for arm, arm_df in readout.groupby("representation_arm"):
        arm_df = arm_df.copy()
        c12_vals = arm_df[arm_df["topology_arm"].eq("c12")]["mean_bounded_differentiated_recovery"]
        if len(c12_vals) == 0:
            continue
        c12_val = float(c12_vals.iloc[0])
        max_dev = float((arm_df["mean_bounded_differentiated_recovery"] - c12_val).abs().max())
        values = arm_df["mean_bounded_differentiated_recovery"].astype(float)
        min_v, max_v = float(values.min()), float(values.max())
        denom = max_v - min_v
        for _, row in arm_df.iterrows():
            topology = str(row["topology_arm"])
            cls = class_by_topology.get(topology, "unclassified")
            meta = meta_by_topology.loc[topology] if topology in meta_by_topology.index else row
            tags = topology_tags(meta)
            value = float(row["mean_bounded_differentiated_recovery"])
            if max_dev > 0:
                scan_metric(rows, source="readout_deviation_from_c12", topology_arm=topology, classification=cls, representation_arm=str(arm), metric="abs_deviation_from_c12_scaled", value=abs(value - c12_val) / max_dev, max_denominator=args.max_denominator, tol=args.tolerance, tags=tags)
            if denom > 0:
                scan_metric(rows, source="readout_rank_scaled", topology_arm=topology, classification=cls, representation_arm=str(arm), metric="readout_minmax_scaled", value=(value - min_v) / denom, max_denominator=args.max_denominator, tol=args.tolerance, tags=tags)

    for _, row in event_geometry.iterrows():
        arm = str(row.get("representation_arm", ""))
        for col in event_geometry.columns:
            if not (col.endswith("_survivor_strength_fraction") or col.endswith("_phase_concentration") or col.endswith("_top4_survivor_overlap")):
                continue
            value = pd.to_numeric(pd.Series([row[col]]), errors="coerce").iloc[0]
            if not np.isfinite(value):
                continue
            metric = col
            if col.endswith("_top4_survivor_overlap"):
                value = float(value) / 4.0
                metric = col + "_fraction"
            tags = "survivor_strength" if "survivor_strength" in col else "phase_geometry" if "phase" in col else "top4_overlap"
            scan_metric(rows, source="event_geometry", topology_arm="representation_events", classification="representation", representation_arm=arm, metric=metric, value=float(value), max_denominator=args.max_denominator, tol=args.tolerance, tags=tags)

    out = pd.DataFrame(rows)
    if len(out):
        out = out.sort_values(["is_close_to_fraction", "is_focus_fraction", "abs_error_to_fraction", "nearest_fraction"], ascending=[False, False, True, True])
    return out


def summarize_alignment(scan: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    close = scan[scan["is_close_to_fraction"].fillna(False)].copy()
    if close.empty:
        return pd.DataFrame(), pd.DataFrame()
    align = (
        close.groupby(["nearest_fraction", "classification"], as_index=False)
        .agg(n_hits=("metric", "size"), mean_abs_error=("abs_error_to_fraction", "mean"), focus_fraction=("is_focus_fraction", "max"), n_gt_1=("has_numerator_gt_1", "max"))
        .sort_values(["n_hits", "nearest_fraction"], ascending=[False, True])
    )
    totals = align.groupby("nearest_fraction")["n_hits"].sum().rename("fraction_total_hits")
    align = align.merge(totals, on="nearest_fraction", how="left")
    align["class_hit_fraction"] = align["n_hits"] / align["fraction_total_hits"]

    class_summary = (
        close.groupby("classification", as_index=False)
        .agg(n_close_hits=("metric", "size"), n_focus_hits=("is_focus_fraction", "sum"), n_n_gt_1_hits=("has_numerator_gt_1", "sum"), dominant_fraction=("nearest_fraction", lambda s: s.value_counts().idxmax()))
    )
    return align, class_summary


def classify(scan: pd.DataFrame, align: pd.DataFrame) -> pd.DataFrame:
    close = scan[scan["is_close_to_fraction"].fillna(False)].copy()
    focus = close[close["is_focus_fraction"].fillna(False)].copy()
    n_gt_1 = close[close["has_numerator_gt_1"].fillna(False)].copy()
    class_set = set(close["classification"].dropna().astype(str))
    dominant = align[align["class_hit_fraction"].ge(0.6)] if len(align) else pd.DataFrame()
    two_eleven = close[close["nearest_fraction"].eq("2/11")].copy()
    two_eleven_local = bool(len(two_eleven[two_eleven["tags"].str.contains("c12_neighborhood|reversed|ring_sharing|survivor_strength", na=False)]))
    rows = [
        {
            "criterion": "generalized_nm_fraction_scan_present",
            "supported": bool(len(close) > 0),
            "basis": f"close_hits={len(close)}; unique_fractions={close['nearest_fraction'].nunique() if len(close) else 0}",
        },
        {
            "criterion": "n_gt_1_fraction_signatures_present",
            "supported": bool(len(n_gt_1) > 0),
            "basis": f"n_gt_1_close_hits={len(n_gt_1)}; examples={'|'.join(sorted(n_gt_1['nearest_fraction'].unique())[:12]) if len(n_gt_1) else 'none'}",
        },
        {
            "criterion": "focus_fractions_recur",
            "supported": bool(len(focus) > 0),
            "basis": f"focus_hits={len(focus)}; fractions={'|'.join(sorted(focus['nearest_fraction'].unique())) if len(focus) else 'none'}",
        },
        {
            "criterion": "fractions_cover_boundary_classes",
            "supported": {"reverse-stable", "boundary", "full-stable"}.issubset(class_set),
            "basis": f"classes_with_close_hits={'|'.join(sorted(class_set)) if class_set else 'none'}",
        },
        {
            "criterion": "fraction_signatures_class_localized",
            "supported": bool(len(dominant) > 0),
            "basis": "; ".join(f"{r.nearest_fraction}->{r.classification}:{r.class_hit_fraction:.2f}" for r in dominant.itertuples()) if len(dominant) else "no fraction has >=0.60 class concentration",
        },
        {
            "criterion": "two_eleven_localizes_to_registered_targets",
            "supported": two_eleven_local,
            "basis": "2/11 appears near c12/reversed/ring-share/survivor-strength tags" if two_eleven_local else "2/11 does not localize to registered target tags",
        },
        {
            "criterion": "fractions_remain_diagnostics_not_explanations",
            "supported": True,
            "basis": "B7.5e post-processes B7.5d boundary outputs; it does not adopt N/M as a carrier explanation.",
        },
    ]
    return pd.DataFrame(rows)


def write_summary(outdir: Path, scan: pd.DataFrame, align: pd.DataFrame, class_summary: pd.DataFrame, classification: pd.DataFrame, args: argparse.Namespace) -> None:
    close = scan[scan["is_close_to_fraction"].fillna(False)].copy()
    focus = close[close["is_focus_fraction"].fillna(False)].copy()
    lines = [
        "# Stage B7.5e Generalized N/M Fraction Signature Audit",
        "",
        "Status: executed after `Stage_B7_5e_preregistration_email_sent.md`.",
        "",
        "## Registered Question",
        "",
        "Do generalized N/M fractional signatures localize the topology-dependent stability boundary between reverse-side C->AB readout and full self-consistent AB<->C readout?",
        "",
        "## Primary Classification",
        "",
        classification.to_csv(index=False).strip(),
        "",
        "## Boundary Fraction Alignment",
        "",
        align.to_csv(index=False).strip() if len(align) else "no close fraction hits",
        "",
        "## Class Summary",
        "",
        class_summary.to_csv(index=False).strip() if len(class_summary) else "no close fraction hits",
        "",
        "## Focus Fraction Hits",
        "",
        focus.head(80).to_csv(index=False).strip() if len(focus) else "no focus fraction hits",
        "",
        "## Closest N/M Hits",
        "",
        close.head(120).to_csv(index=False).strip() if len(close) else "no close fraction hits",
        "",
        "## Decision Boundary",
        "",
        "- Strong support requires N/M signatures to concentrate at the same topology arms where the reverse/full boundary flips.",
        "- Weak support means N/M signatures recur but do not align with boundary classification or readout strength.",
        "- Negative support means fractional signatures scatter broadly and remain secondary internal diagnostics only.",
        "- Fractions are diagnostics first, explanations later.",
        "",
        "## Settings",
        "",
        f"- max_denominator: {args.max_denominator}",
        f"- tolerance: {args.tolerance}",
        f"- paired_delta: {args.paired_delta}",
        f"- readout_summary: {args.readout_summary}",
        f"- event_geometry: {args.event_geometry}",
    ]
    (outdir / "Stage_B7_5e_execution_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    paired = pd.read_csv(args.paired_delta)
    readout = pd.read_csv(args.readout_summary)
    event_geometry = pd.read_csv(args.event_geometry)
    scan = build_scan(paired, readout, event_geometry, args)
    align, class_summary = summarize_alignment(scan)
    classification = classify(scan, align)
    scan.to_csv(outdir / "Stage_B7_5e_fraction_signature_scan.csv", index=False)
    align.to_csv(outdir / "Stage_B7_5e_boundary_fraction_alignment.csv", index=False)
    class_summary.to_csv(outdir / "Stage_B7_5e_fraction_class_summary.csv", index=False)
    classification.to_csv(outdir / "Stage_B7_5e_primary_classification.csv", index=False)
    write_summary(outdir, scan, align, class_summary, classification, args)
    print(f"output_dir: {outdir}")
    print("\nPrimary classification")
    print(classification.to_string(index=False))
    print("\nTop aligned fractions")
    print(align.head(30).to_string(index=False) if len(align) else "no close fraction hits")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paired-delta", type=Path, default=REPO / "reports/stage_b7_5d/Stage_B7_5d_paired_delta_summary.csv")
    parser.add_argument("--readout-summary", type=Path, default=REPO / "reports/stage_b7_5d/Stage_B7_5d_readout_summary.csv")
    parser.add_argument("--event-geometry", type=Path, default=REPO / "reports/stage_b7_5d/Stage_B7_5d_event_geometry_summary.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_5e")
    parser.add_argument("--max-denominator", type=int, default=24)
    parser.add_argument("--tolerance", type=float, default=0.01)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
