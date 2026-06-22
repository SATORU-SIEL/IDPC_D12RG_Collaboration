#!/usr/bin/env python3
"""Stage B7.5 relation/condition audit with fractional diagnostic."""

from __future__ import annotations

import argparse
from fractions import Fraction
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

REGISTERED_SURVIVORS = {"P10", "P5", "P21", "P15"}
CYCLOTOMIC_X3 = {"P10", "P5", "P21", "P15"}
TOPOLOGY_ARMS = [
    "no_topology_baseline",
    "c12_1_2",
    "c12_reversed",
    "c12_side_broken",
    "c12_shuffled",
    "c10",
    "c11",
    "c13",
    "c14",
]
FRACTION_TARGETS = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 4), Fraction(1, 5), Fraction(1, 6)]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


b73a = load_module("b73a_for_b75", SCRIPTS / "test_Stage_B7_3a_c12_specificity_h24_collective_necessity_audit.py")


def zscore(values: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    mu = np.nanmean(arr)
    sd = np.nanstd(arr)
    if not np.isfinite(sd) or sd <= 1e-12:
        return np.zeros_like(arr, dtype=float)
    return (arr - mu) / sd


def add_b75_scores(features: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    out = b73a.add_representation_scores(features)
    ab_receiver = np.abs(pd.to_numeric(out["ab_receiver_side"], errors="coerce"))
    ba_receiver = np.abs(pd.to_numeric(out["ba_receiver_side"], errors="coerce"))
    ab_standpoint = np.abs(pd.to_numeric(out["ab_standpoint_polarity"], errors="coerce"))
    ba_standpoint = np.abs(pd.to_numeric(out["ba_standpoint_polarity"], errors="coerce"))
    ab_mag = pd.to_numeric(out["ab_standpoint_magnitude"], errors="coerce")
    ba_mag = pd.to_numeric(out["ba_standpoint_magnitude"], errors="coerce")
    o1 = pd.to_numeric(out["O1_lag0_AB_raw"], errors="coerce")
    o2 = pd.to_numeric(out["O2_lag5_AB_raw"], errors="coerce")

    out["endpoint_abs_relation"] = zscore(np.abs(o1) + np.abs(o2))
    out["endpoint_lag_gap_relation"] = zscore(np.abs(o1 - o2))
    out["endpoint_product_relation"] = zscore(o1 * o2)
    out["receiver_only_relation"] = out["receiver_only_c"]
    out["standpoint_only_relation"] = zscore(ab_standpoint + ba_standpoint)
    out["receiver_standpoint_relation"] = zscore(out["receiver_only_relation"] + out["standpoint_only_relation"])
    out["forward_ab_to_c_condition"] = zscore(ab_receiver + ab_standpoint + ab_mag)
    out["reverse_c_to_ab_condition"] = zscore(ba_receiver + ba_standpoint + ba_mag)
    forward_raw = zscore(ab_receiver + ab_standpoint + ab_mag)
    reverse_raw = zscore(ba_receiver + ba_standpoint + ba_mag)
    out["self_consistent_min_condition"] = zscore(np.minimum(forward_raw, reverse_raw))
    out["self_consistent_product_condition"] = zscore(forward_raw * reverse_raw)
    out["self_consistent_rstar_condition"] = out["receiver_standpoint_magnitude_c"]

    families = {
        "endpoint_abs_relation": "endpoint_direct_relation_only",
        "endpoint_lag_gap_relation": "endpoint_direct_relation_only",
        "endpoint_product_relation": "endpoint_direct_relation_only",
        "receiver_only_relation": "receiver_standpoint_relation_only",
        "standpoint_only_relation": "receiver_standpoint_relation_only",
        "receiver_standpoint_relation": "receiver_standpoint_relation_only",
        "forward_ab_to_c_condition": "forward_only_condition",
        "reverse_c_to_ab_condition": "reverse_only_condition",
        "self_consistent_min_condition": "self_consistent_condition",
        "self_consistent_product_condition": "self_consistent_condition",
        "self_consistent_rstar_condition": "self_consistent_condition",
        "scalar_c": "scalar_mediator_control",
    }
    return out, families


def run_topology_audit(events_by_rep: dict[str, pd.DataFrame], args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 750)
    rows = []
    for rep, events in events_by_rep.items():
        for topology in TOPOLOGY_ARMS:
            n_nodes, edges, notes = b73a.topology_edges(topology, rng)
            schedule, meta = b73a.build_event_schedule(events, args.steps, n_nodes)
            shifted = b73a.shifted_schedule(schedule, args.steps, max(7, args.steps // 5))
            random_event = b73a.random_schedule(schedule, args.steps, rng)
            endogenous_values, endogenous_avg = b73a.simulate_many(n_nodes, edges, schedule, args, rng)
            shifted_values, _ = b73a.simulate_many(n_nodes, edges, shifted, args, rng)
            random_values, _ = b73a.simulate_many(n_nodes, edges, random_event, args, rng)
            obs = float(np.nanmean(endogenous_values))
            rows.append({
                "representation": rep,
                "topology_arm": topology,
                "n_nodes": n_nodes,
                "n_directed_edges": len(edges),
                "topology_notes": notes,
                "n_seed_events": meta["n_events"],
                "mean_seed_strength": meta["mean_strength"],
                "total_impulse_budget": meta["total_impulse_budget"],
                "mean_bounded_differentiated_recovery": obs,
                "sd_bounded_differentiated_recovery": float(np.nanstd(endogenous_values)),
                "effect_vs_time_shifted": obs - float(np.nanmean(shifted_values)),
                "effect_vs_random_event": obs - float(np.nanmean(random_values)),
                "p_vs_time_shifted_and_random": b73a.p_greater(obs, np.r_[shifted_values, random_values]),
                **endogenous_avg,
            })
    return pd.DataFrame(rows)


def summarize_events(events_by_rep: dict[str, pd.DataFrame], families: dict[str, str]) -> pd.DataFrame:
    rows = []
    for rep, events in events_by_rep.items():
        labels = events["label"].astype(str)
        strength = pd.to_numeric(events["strength"], errors="coerce").fillna(0.0)
        survivor = labels.isin(REGISTERED_SURVIVORS)
        by_label = events.assign(strength=strength).groupby("label", as_index=False)["strength"].agg(["count", "mean", "sum"]).reset_index()
        by_label["label"] = by_label["label"].astype(str)
        top4 = set(by_label.sort_values(["sum", "mean", "count"], ascending=False).head(4)["label"])
        overlap = top4 & REGISTERED_SURVIVORS
        rows.append({
            "representation": rep,
            "arm_family": families[rep],
            "n_events": int(len(events)),
            "survivor_event_fraction": float(survivor.mean()) if len(events) else np.nan,
            "survivor_strength_fraction": float(strength[survivor].sum() / strength.sum()) if float(strength.sum()) > 0 else np.nan,
            "top4_labels_by_event_strength": "|".join(sorted(top4, key=lambda x: int(x[1:]))),
            "top4_survivor_overlap": int(len(overlap)),
            "top4_precision_vs_registered": float(len(overlap) / 4.0),
            "top4_recall_vs_registered": float(len(overlap) / 4.0),
            "top4_jaccard_vs_registered": float(len(overlap) / len(top4 | REGISTERED_SURVIVORS)) if top4 else np.nan,
            "top4_matches_cyclotomic_x3": top4 == CYCLOTOMIC_X3,
        })
    return pd.DataFrame(rows)


def summarize_readout(results: pd.DataFrame, event_summary: pd.DataFrame, families: dict[str, str]) -> pd.DataFrame:
    lookup = results.set_index(["representation", "topology_arm"])["mean_bounded_differentiated_recovery"].to_dict()
    rows = []
    for rep, family in families.items():
        c12 = lookup.get((rep, "c12_1_2"), np.nan)
        no_top = lookup.get((rep, "no_topology_baseline"), np.nan)
        controls = {
            name: lookup.get((rep, name), np.nan)
            for name in ["c12_reversed", "c12_side_broken", "c12_shuffled", "c10", "c11", "c13", "c14"]
        }
        finite_controls = [v for v in controls.values() if np.isfinite(v)]
        margins = {f"effect_vs_{name}": c12 - value if np.isfinite(c12) and np.isfinite(value) else np.nan for name, value in controls.items()}
        rows.append({
            "representation": rep,
            "arm_family": family,
            "c12_readout": c12,
            "no_topology_readout": no_top,
            "effect_vs_no_topology": c12 - no_top if np.isfinite(c12) and np.isfinite(no_top) else np.nan,
            "n_positive_specificity_controls": int(sum((c12 - v) > 0 for v in finite_controls)) if np.isfinite(c12) else 0,
            "min_specificity_margin": float(np.nanmin([c12 - v for v in finite_controls])) if finite_controls and np.isfinite(c12) else np.nan,
            **margins,
        })
    out = pd.DataFrame(rows)
    return out.merge(event_summary, on=["representation", "arm_family"], how="left").sort_values(
        ["n_positive_specificity_controls", "effect_vs_no_topology", "c12_readout"],
        ascending=False,
    )


def best_by_family(readout: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for family, sub in readout.groupby("arm_family", sort=False):
        best = sub.sort_values(["n_positive_specificity_controls", "effect_vs_no_topology", "c12_readout"], ascending=False).iloc[0]
        rows.append(best)
    return pd.DataFrame(rows).sort_values(["n_positive_specificity_controls", "effect_vs_no_topology"], ascending=False)


def nearest_fraction(value: float, max_denominator: int = 12) -> tuple[str, float, bool, bool]:
    if not np.isfinite(value):
        return "", np.nan, False, False
    frac = Fraction(float(value)).limit_denominator(max_denominator)
    approx = float(frac)
    is_target = frac in FRACTION_TARGETS
    has_n_gt_1 = frac.numerator > 1
    return f"{frac.numerator}/{frac.denominator}", abs(value - approx), is_target, has_n_gt_1


def fractional_diagnostic(readout: pd.DataFrame, b74g_support: Path) -> pd.DataFrame:
    rows = []
    if b74g_support.exists():
        b74g = pd.read_csv(b74g_support)
        for _, row in b74g.iterrows():
            for metric in ["precision_vs_registered", "recall_vs_registered", "jaccard_vs_registered", "weight_on_registered_fraction"]:
                value = float(row[metric]) if pd.notna(row[metric]) else np.nan
                frac, err, is_target, has_n_gt_1 = nearest_fraction(value)
                rows.append({
                    "source": "B7.4g_proxy_support",
                    "representation_or_proxy": row["proxy"],
                    "arm_family": "broad_or_survivor_arithmetic_proxy",
                    "metric": metric,
                    "value": value,
                    "nearest_fraction": frac,
                    "abs_error_to_fraction": err,
                    "is_luke_target_fraction": is_target,
                    "has_numerator_gt_1": has_n_gt_1,
                })
    for _, row in readout.iterrows():
        for metric in ["top4_precision_vs_registered", "top4_recall_vs_registered", "top4_jaccard_vs_registered", "survivor_event_fraction", "survivor_strength_fraction"]:
            value = float(row[metric]) if pd.notna(row[metric]) else np.nan
            frac, err, is_target, has_n_gt_1 = nearest_fraction(value)
            rows.append({
                "source": "B7.5_relation_condition_arm",
                "representation_or_proxy": row["representation"],
                "arm_family": row["arm_family"],
                "metric": metric,
                "value": value,
                "nearest_fraction": frac,
                "abs_error_to_fraction": err,
                "is_luke_target_fraction": is_target,
                "has_numerator_gt_1": has_n_gt_1,
            })
    return pd.DataFrame(rows)


def classify(best: pd.DataFrame, frac: pd.DataFrame) -> pd.DataFrame:
    best_lookup = best.set_index("arm_family")
    def row_value(family: str, col: str) -> float:
        if family not in best_lookup.index:
            return np.nan
        return float(best_lookup.loc[family, col])

    rs_relation = row_value("receiver_standpoint_relation_only", "effect_vs_no_topology")
    reverse = row_value("reverse_only_condition", "effect_vs_no_topology")
    selfc = row_value("self_consistent_condition", "effect_vs_no_topology")
    endpoint = row_value("endpoint_direct_relation_only", "effect_vs_no_topology")
    forward = row_value("forward_only_condition", "effect_vs_no_topology")
    broad_025 = bool(
        ((frac["representation_or_proxy"].eq("broad_group_completion_proxy"))
         & (frac["metric"].eq("precision_vs_registered"))
         & (frac["nearest_fraction"].eq("1/4"))
         & (frac["abs_error_to_fraction"].le(1e-12))).any()
    )
    rows = [
        {
            "criterion": "endpoint_direct_relation_reduced",
            "supported": bool(endpoint < rs_relation and endpoint < reverse),
            "basis": f"endpoint effect {endpoint:.6g}; receiver/standpoint {rs_relation:.6g}; reverse {reverse:.6g}",
        },
        {
            "criterion": "receiver_standpoint_relation_competitor_live",
            "supported": bool(np.isfinite(rs_relation) and rs_relation > endpoint),
            "basis": f"receiver/standpoint relation best effect {rs_relation:.6g}",
        },
        {
            "criterion": "reverse_dominant_condition_competitor_live",
            "supported": bool(np.isfinite(reverse) and reverse >= max(rs_relation, forward)),
            "basis": f"reverse effect {reverse:.6g}; relation {rs_relation:.6g}; forward {forward:.6g}",
        },
        {
            "criterion": "self_consistency_exceeds_reverse",
            "supported": bool(np.isfinite(selfc) and selfc > reverse),
            "basis": f"self-consistent effect {selfc:.6g}; reverse effect {reverse:.6g}",
        },
        {
            "criterion": "broad_completion_fractional_signature_present",
            "supported": broad_025,
            "basis": "B7.4g broad_group_completion_proxy precision is exact 1/4" if broad_025 else "no exact 1/4 broad-completion precision detected",
        },
    ]
    return pd.DataFrame(rows)


def write_summary(path: Path, best: pd.DataFrame, classification: pd.DataFrame, frac: pd.DataFrame, args: argparse.Namespace) -> None:
    frac_focus = frac[
        frac["representation_or_proxy"].isin(["broad_group_completion_proxy", "cyclotomic_plus_x3_decomposition"])
        | frac["is_luke_target_fraction"]
        | frac["has_numerator_gt_1"]
    ].copy()
    lines = [
        "# Stage B7.5 Relation / Condition Audit With Fractional Diagnostic",
        "",
        "Status: executed after `Stage_B7_5_preregistration_email_sent.md`.",
        "",
        "## Registered Question",
        "",
        "Is the surviving structure reducible to relation(A,B), is it better described as a reverse-dominant C->AB condition, or does it require a self-consistent AB<->C condition?",
        "",
        "## Layer 1: Best Arm By Family",
        "",
        best.to_csv(index=False).strip(),
        "",
        "## Classification",
        "",
        classification.to_csv(index=False).strip(),
        "",
        "## Layer 2: Fractional / Cyclotomic Diagnostic Focus",
        "",
        frac_focus.to_csv(index=False).strip(),
        "",
        "## Decision Boundary",
        "",
        "- If receiver/standpoint relation-only matches self-consistency, conclude toward refined receiver/standpoint relation(A,B).",
        "- If reverse-only matches or exceeds self-consistency, conclude toward reverse-dominant condition rather than overstating AB<->C.",
        "- If self-consistent AB<->C exceeds relation-only and reverse-only, and best preserves C12/survivor structure, directed-correspondence-condition interpretation strengthens.",
        "- Fractional diagnostics are secondary; broad completion is not adopted as a readout carrier solely from fractional signatures.",
        "",
        "## Settings",
        "",
        f"- event_quantile: {args.event_quantile}",
        f"- steps: {args.steps}",
        f"- n_runs: {args.n_runs}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    features = b73a.load_b72_features(args)
    features, families = add_b75_scores(features)
    events_by_rep = {rep: b73a.event_rows_for_rep(features, rep, args.event_quantile) for rep in families}
    events = pd.concat(events_by_rep.values(), ignore_index=True)
    event_summary = summarize_events(events_by_rep, families)
    topology = run_topology_audit(events_by_rep, args)
    readout = summarize_readout(topology, event_summary, families)
    best = best_by_family(readout)
    frac = fractional_diagnostic(readout, args.b74g_support)
    classification = classify(best, frac)

    features.to_csv(outdir / "Stage_B7_5_representation_scores.csv", index=False)
    events.to_csv(outdir / "Stage_B7_5_representation_events.csv", index=False)
    topology.to_csv(outdir / "Stage_B7_5_topology_results.csv", index=False)
    event_summary.to_csv(outdir / "Stage_B7_5_event_survivor_summary.csv", index=False)
    readout.to_csv(outdir / "Stage_B7_5_relation_condition_readout.csv", index=False)
    best.to_csv(outdir / "Stage_B7_5_best_by_family.csv", index=False)
    frac.to_csv(outdir / "Stage_B7_5_fractional_diagnostic.csv", index=False)
    classification.to_csv(outdir / "Stage_B7_5_primary_classification.csv", index=False)
    write_summary(outdir / "Stage_B7_5_execution_summary.md", best, classification, frac, args)

    print(f"output_dir: {outdir}")
    print("\nBest by family")
    print(best.to_string(index=False))
    print("\nClassification")
    print(classification.to_string(index=False))
    print("\nFractional focus")
    print(frac[(frac["representation_or_proxy"].eq("broad_group_completion_proxy")) | frac["is_luke_target_fraction"]].to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_5")
    parser.add_argument("--b74g-support", type=Path, default=REPO / "reports/stage_b7_4g/Stage_B7_4g_proxy_support_summary.csv")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--event-quantile", type=float, default=0.75)
    parser.add_argument("--steps", type=int, default=240)
    parser.add_argument("--n-runs", type=int, default=32)
    parser.add_argument("--seed", type=int, default=75075)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
