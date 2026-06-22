#!/usr/bin/env python3
"""Stage B7.5b C->AB readout geometry audit."""

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
FRACTION_TARGETS = [Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(3, 7), Fraction(2, 11)]
PRIMARY_TOPOLOGY = "c12_1_2"
REVERSE_ARM = "c_to_ab_receiver_standpoint_magnitude"
FULL_SELF_ARM = "full_self_consistent_rstar"

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
    "degree_matched_null",
    "edge_count_matched_null",
    "ring_share_c12_plus_5",
    "ring_share_c12_plus_7",
    "ring_share_c12_plus_10",
    "ring_share_c12_plus_11",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


b73a = load_module("b73a_for_b75b", SCRIPTS / "test_Stage_B7_3a_c12_specificity_h24_collective_necessity_audit.py")


def zscore(values: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    mu = np.nanmean(arr)
    sd = np.nanstd(arr)
    if not np.isfinite(sd) or sd <= 1e-12:
        return np.zeros_like(arr, dtype=float)
    return (arr - mu) / sd


def unique_edges(n_nodes: int, jumps: tuple[int, ...]) -> list[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for i in range(n_nodes):
        for jump in jumps:
            j = (i + jump) % n_nodes
            if i != j:
                edges.add((i, j))
    return sorted(edges)


def topology_edges(name: str, rng: np.random.Generator) -> tuple[int, list[tuple[int, int]], str]:
    if name in {
        "no_topology_baseline",
        "c12_1_2",
        "c12_reversed",
        "c12_side_broken",
        "c12_shuffled",
        "c10",
        "c11",
        "c13",
        "c14",
    }:
        return b73a.topology_edges(name, rng)
    if name == "degree_matched_null":
        return b73a.topology_edges("topology_capacity_matched_null", rng)
    if name == "edge_count_matched_null":
        b3 = load_module("b3_for_b75b", SCRIPTS / "test_Stage_B3_endogenous_event_carrier_readout.py")
        _, n, c12_edges, _, _ = b3.topology_definition("C12(1,2)")
        edges: set[tuple[int, int]] = set()
        while len(edges) < len(c12_edges):
            i = int(rng.integers(0, n))
            j = int(rng.integers(0, n))
            if i != j:
                edges.add((i, j))
        return n, sorted(edges), "C12 edge-count matched random directed null"
    if name == "ring_share_c12_plus_5":
        return 12, unique_edges(12, (-5, -2, -1, 1, 2, 5)), "C12(1,2) with shared 5-ring proxy edges"
    if name == "ring_share_c12_plus_7":
        return 12, unique_edges(12, (-7, -2, -1, 1, 2, 7)), "C12(1,2) with shared 7 mod 12 proxy edges"
    if name == "ring_share_c12_plus_10":
        return 12, unique_edges(12, (-10, -2, -1, 1, 2, 10)), "C12(1,2) with shared 10-ring proxy edges"
    if name == "ring_share_c12_plus_11":
        return 12, unique_edges(12, (-11, -2, -1, 1, 2, 11)), "C12(1,2) with shared 11 mod 12 reflective proxy edges"
    raise ValueError(f"unknown topology {name}")


def add_b75b_scores(features: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    out = b73a.add_representation_scores(features)
    ba_receiver = np.abs(pd.to_numeric(out["ba_receiver_side"], errors="coerce"))
    ba_standpoint = np.abs(pd.to_numeric(out["ba_standpoint_polarity"], errors="coerce"))
    ba_mag = pd.to_numeric(out["ba_standpoint_magnitude"], errors="coerce")

    out["c_to_ab_receiver_only"] = zscore(ba_receiver)
    out["c_to_ab_standpoint_only"] = zscore(ba_standpoint)
    out["c_to_ab_magnitude_only"] = zscore(ba_mag)
    out["c_to_ab_receiver_standpoint"] = zscore(ba_receiver + ba_standpoint)
    out["c_to_ab_receiver_magnitude"] = zscore(ba_receiver + ba_mag)
    out["c_to_ab_standpoint_magnitude"] = zscore(ba_standpoint + ba_mag)
    out[REVERSE_ARM] = zscore(ba_receiver + ba_standpoint + ba_mag)
    out[FULL_SELF_ARM] = out["receiver_standpoint_magnitude_c"]

    arms = {
        "c_to_ab_receiver_only": "receiver_only",
        "c_to_ab_standpoint_only": "standpoint_only",
        "c_to_ab_magnitude_only": "magnitude_only",
        "c_to_ab_receiver_standpoint": "receiver_standpoint",
        "c_to_ab_receiver_magnitude": "receiver_magnitude",
        "c_to_ab_standpoint_magnitude": "standpoint_magnitude",
        REVERSE_ARM: "current_reverse_only_receiver_standpoint_magnitude",
        FULL_SELF_ARM: "full_self_consistent_rstar",
    }
    return out, arms


def run_topology_audit(events_by_arm: dict[str, pd.DataFrame], args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 752)
    rows = []
    for arm, events in events_by_arm.items():
        for topology in TOPOLOGY_ARMS:
            n_nodes, edges, notes = topology_edges(topology, rng)
            schedule, meta = b73a.build_event_schedule(events, args.steps, n_nodes)
            shifted = b73a.shifted_schedule(schedule, args.steps, max(7, args.steps // 5))
            random_event = b73a.random_schedule(schedule, args.steps, rng)
            endogenous_values, endogenous_avg = b73a.simulate_many(n_nodes, edges, schedule, args, rng)
            shifted_values, _ = b73a.simulate_many(n_nodes, edges, shifted, args, rng)
            random_values, _ = b73a.simulate_many(n_nodes, edges, random_event, args, rng)
            obs = float(np.nanmean(endogenous_values))
            rows.append({
                "representation_arm": arm,
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


def summarize_events(events_by_arm: dict[str, pd.DataFrame], arm_families: dict[str, str]) -> pd.DataFrame:
    rows = []
    for arm, events in events_by_arm.items():
        labels = events["label"].astype(str)
        strength = pd.to_numeric(events["strength"], errors="coerce").fillna(0.0)
        survivor = labels.isin(REGISTERED_SURVIVORS)
        by_label = events.assign(strength=strength).groupby("label", as_index=False)["strength"].agg(["count", "mean", "sum"]).reset_index()
        by_label["label"] = by_label["label"].astype(str)
        top4 = set(by_label.sort_values(["sum", "mean", "count"], ascending=False).head(4)["label"])
        overlap = top4 & REGISTERED_SURVIVORS
        rows.append({
            "representation_arm": arm,
            "arm_family": arm_families[arm],
            "n_events": int(len(events)),
            "survivor_event_fraction": float(survivor.mean()) if len(events) else np.nan,
            "survivor_strength_fraction": float(strength[survivor].sum() / strength.sum()) if float(strength.sum()) > 0 else np.nan,
            "top4_labels_by_event_strength": "|".join(sorted(top4, key=lambda x: int(x[1:]))),
            "top4_survivor_overlap": int(len(overlap)),
            "top4_precision_vs_registered": float(len(overlap) / 4.0),
            "top4_recall_vs_registered": float(len(overlap) / 4.0),
            "top4_jaccard_vs_registered": float(len(overlap) / len(top4 | REGISTERED_SURVIVORS)) if top4 else np.nan,
        })
    return pd.DataFrame(rows)


def summarize_readout(topology: pd.DataFrame, event_summary: pd.DataFrame, arm_families: dict[str, str]) -> pd.DataFrame:
    lookup = topology.set_index(["representation_arm", "topology_arm"])["mean_bounded_differentiated_recovery"].to_dict()
    controls = ["c12_reversed", "c12_side_broken", "c12_shuffled", "c10", "c11", "c13", "c14", "degree_matched_null", "edge_count_matched_null"]
    rows = []
    for arm, family in arm_families.items():
        c12 = lookup.get((arm, PRIMARY_TOPOLOGY), np.nan)
        no_top = lookup.get((arm, "no_topology_baseline"), np.nan)
        reversed_c12 = lookup.get((arm, "c12_reversed"), np.nan)
        ring10 = lookup.get((arm, "ring_share_c12_plus_10"), np.nan)
        control_values = [lookup.get((arm, name), np.nan) for name in controls]
        ring_values = [lookup.get((arm, name), np.nan) for name in TOPOLOGY_ARMS if name.startswith("ring_share")]
        rows.append({
            "representation_arm": arm,
            "arm_family": family,
            "c12_readout": c12,
            "no_topology_readout": no_top,
            "effect_vs_no_topology": c12 - no_top if np.isfinite(c12) and np.isfinite(no_top) else np.nan,
            "c12_reversed_readout": reversed_c12,
            "effect_vs_c12_reversed": c12 - reversed_c12 if np.isfinite(c12) and np.isfinite(reversed_c12) else np.nan,
            "ring_share_c12_plus_10_readout": ring10,
            "effect_vs_ring_share_c12_plus_10": c12 - ring10 if np.isfinite(c12) and np.isfinite(ring10) else np.nan,
            "mean_ring_share_readout": float(np.nanmean(ring_values)) if ring_values else np.nan,
            "effect_vs_ring_share_mean": c12 - float(np.nanmean(ring_values)) if ring_values and np.isfinite(c12) else np.nan,
            "n_positive_specificity_controls": int(sum((c12 - v) > 0 for v in control_values if np.isfinite(v))) if np.isfinite(c12) else 0,
            "min_specificity_margin": float(np.nanmin([c12 - v for v in control_values if np.isfinite(v)])) if np.isfinite(c12) else np.nan,
        })
    return pd.DataFrame(rows).merge(event_summary, on=["representation_arm", "arm_family"], how="left").sort_values(
        ["effect_vs_no_topology", "c12_readout"], ascending=False
    )


def phase_concentration(phases: pd.Series) -> float:
    vals = pd.to_numeric(phases, errors="coerce").dropna().to_numpy(dtype=float)
    if len(vals) == 0:
        return np.nan
    return float(abs(np.mean(np.exp(1j * vals))))


def corr_abs(a: pd.Series, b: pd.Series) -> float:
    x = pd.to_numeric(a, errors="coerce")
    y = pd.to_numeric(b, errors="coerce")
    mask = x.notna() & y.notna()
    if int(mask.sum()) < 3:
        return np.nan
    return float(abs(np.corrcoef(x[mask], y[mask])[0, 1]))


def alignment_diagnostics(features: pd.DataFrame, events_by_arm: dict[str, pd.DataFrame], arm_families: dict[str, str]) -> pd.DataFrame:
    rows = []
    feature_key = features.copy()
    feature_key["label"] = feature_key["label"].astype(str)
    for arm, events in events_by_arm.items():
        ev = events.copy()
        ev["label"] = ev["label"].astype(str)
        joined = ev.merge(
            feature_key,
            left_on=["label", "task_idx"],
            right_on=["label", "idx_in_session"],
            how="left",
            suffixes=("", "_feature"),
        )
        phase_targets = np.mod(np.round((np.mod(pd.to_numeric(joined["phase"], errors="coerce").fillna(0.0), 2.0 * np.pi) / (2.0 * np.pi)) * 12), 12)
        target_counts = phase_targets.value_counts(normalize=True)
        rows.append({
            "representation_arm": arm,
            "arm_family": arm_families[arm],
            "phase_target_concentration": phase_concentration(joined["phase"]),
            "phase_target_max_fraction": float(target_counts.max()) if len(target_counts) else np.nan,
            "lag_gap_alignment": corr_abs(joined["strength"], (pd.to_numeric(joined["O1_lag0_AB_raw"], errors="coerce") - pd.to_numeric(joined["O2_lag5_AB_raw"], errors="coerce")).abs()),
            "receiver_side_alignment": corr_abs(joined["strength"], pd.to_numeric(joined["ba_receiver_side"], errors="coerce").abs()),
            "standpoint_polarity_alignment": corr_abs(joined["strength"], pd.to_numeric(joined["ba_standpoint_polarity"], errors="coerce").abs()),
            "magnitude_scaling_alignment": corr_abs(joined["strength"], pd.to_numeric(joined["ba_standpoint_magnitude"], errors="coerce")),
        })
    return pd.DataFrame(rows)


def nearest_registered_fraction(value: float) -> tuple[str, float, bool]:
    if not np.isfinite(value):
        return "", np.nan, False
    best = min(FRACTION_TARGETS, key=lambda frac: abs(float(frac) - value))
    return f"{best.numerator}/{best.denominator}", abs(float(best) - value), abs(float(best) - value) <= 0.01


def resonance_tags(topology_arm: str, labels_text: object) -> str:
    labels = set(str(labels_text).split("|"))
    tags = []
    if {"P5", "P10"} & labels or "5" in topology_arm or "10" in topology_arm:
        tags.append("5_or_10_ring_proxy")
    if {"P15", "P21"} & labels or "7" in topology_arm:
        tags.append("x3_or_7mod12_proxy")
    if "11" in topology_arm:
        tags.append("11mod12_reflective_proxy")
    if topology_arm == "c12_1_2":
        tags.append("two_step_c12")
    if topology_arm == "c12_reversed":
        tags.append("reversed_c12")
    if topology_arm.startswith("ring_share"):
        tags.append("ring_sharing")
    return "|".join(tags) if tags else "unassigned"


def fractional_secondary(readout: pd.DataFrame, topology: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in readout.iterrows():
        for metric in ["top4_precision_vs_registered", "top4_recall_vs_registered", "top4_jaccard_vs_registered", "survivor_strength_fraction"]:
            value = float(row[metric]) if pd.notna(row[metric]) else np.nan
            frac, err, close = nearest_registered_fraction(value)
            rows.append({
                "source": "representation_event_localization",
                "representation_arm": row["representation_arm"],
                "topology_arm": "representation_events",
                "metric": metric,
                "value": value,
                "nearest_target_fraction": frac,
                "abs_error_to_target": err,
                "is_close_to_target": close,
                "top4_labels_by_event_strength": row["top4_labels_by_event_strength"],
                "resonance_tags": resonance_tags("representation_events", row["top4_labels_by_event_strength"]),
            })
    primary = topology[topology["topology_arm"].eq(PRIMARY_TOPOLOGY)].set_index("representation_arm")
    for _, row in topology.iterrows():
        arm = row["representation_arm"]
        if arm not in primary.index or row["topology_arm"] == PRIMARY_TOPOLOGY:
            continue
        denom = max(abs(float(primary.loc[arm, "mean_bounded_differentiated_recovery"])), 1e-12)
        value = abs(float(row["mean_bounded_differentiated_recovery"] - primary.loc[arm, "mean_bounded_differentiated_recovery"])) / denom
        frac, err, close = nearest_registered_fraction(value)
        rows.append({
            "source": "topology_deviation_from_c12_scaled",
            "representation_arm": arm,
            "topology_arm": row["topology_arm"],
            "metric": "abs_topology_deviation_from_c12_fraction",
            "value": value,
            "nearest_target_fraction": frac,
            "abs_error_to_target": err,
            "is_close_to_target": close,
            "top4_labels_by_event_strength": "",
            "resonance_tags": resonance_tags(row["topology_arm"], ""),
        })
    return pd.DataFrame(rows).sort_values(["is_close_to_target", "nearest_target_fraction", "abs_error_to_target"], ascending=[False, True, True])


def classify(readout: pd.DataFrame, align: pd.DataFrame, frac: pd.DataFrame) -> pd.DataFrame:
    best = readout.iloc[0]
    reverse = readout[readout["representation_arm"].eq(REVERSE_ARM)].iloc[0]
    full = readout[readout["representation_arm"].eq(FULL_SELF_ARM)].iloc[0]
    component_localized = best["representation_arm"] not in {REVERSE_ARM, FULL_SELF_ARM}
    nulls_weaker = bool(best["n_positive_specificity_controls"] >= 7 and best["min_specificity_margin"] > 0)
    frac_local = bool(
        frac["is_close_to_target"].fillna(False).any()
        and frac["resonance_tags"].str.contains("5_or_10_ring_proxy|reversed_c12|ring_sharing", regex=True).any()
    )
    rows = [
        {
            "criterion": "c_to_ab_component_localized",
            "supported": bool(component_localized),
            "basis": f"best arm {best['representation_arm']} effect {best['effect_vs_no_topology']:.6g}",
        },
        {
            "criterion": "reverse_composite_remains_above_full_self",
            "supported": bool(reverse["effect_vs_no_topology"] > full["effect_vs_no_topology"]),
            "basis": f"reverse composite {reverse['effect_vs_no_topology']:.6g}; full self {full['effect_vs_no_topology']:.6g}",
        },
        {
            "criterion": "topology_specificity_for_best_arm",
            "supported": nulls_weaker,
            "basis": f"best arm {int(best['n_positive_specificity_controls'])} positive controls; min margin {best['min_specificity_margin']:.6g}",
        },
        {
            "criterion": "fractional_secondary_colocalizes",
            "supported": frac_local,
            "basis": "1/4 or 2/11 target appears near P10/5-or-10, reversed C12, or ring-sharing tags" if frac_local else "fractional targets do not localize with registered tags",
        },
    ]
    return pd.DataFrame(rows)


def write_summary(path: Path, readout: pd.DataFrame, align: pd.DataFrame, frac: pd.DataFrame, classification: pd.DataFrame, args: argparse.Namespace) -> None:
    frac_focus = frac[
        frac["is_close_to_target"].fillna(False)
        | frac["nearest_target_fraction"].isin(["1/4", "2/11"])
        | frac["resonance_tags"].str.contains("5_or_10|reversed_c12|ring_sharing", regex=True, na=False)
    ].head(80)
    lines = [
        "# Stage B7.5b C->AB Readout Geometry Audit",
        "",
        "Status: executed after `Stage_B7_5b_preregistration_email_sent.md`.",
        "",
        "## Registered Question",
        "",
        "Why does the current C12 topology-readout couple more strongly to the C -> AB side of the self-consistency structure?",
        "",
        "## Layer 1: C->AB Component Readout",
        "",
        readout.to_csv(index=False).strip(),
        "",
        "## Layer 2: Alignment Diagnostics",
        "",
        align.sort_values("representation_arm").to_csv(index=False).strip(),
        "",
        "## Layer 3: Classification",
        "",
        classification.to_csv(index=False).strip(),
        "",
        "## Layer 4: Fractional Secondary Diagnostic Focus",
        "",
        frac_focus.to_csv(index=False).strip(),
        "",
        "## Decision Boundary",
        "",
        "- Strong support requires C -> AB advantage to localize to a specific component, retain C12 topology specificity, and optionally co-localize fractional diagnostics.",
        "- Intermediate support means the C -> AB advantage remains but component or topology localization is weak.",
        "- Negative support means decomposition removes the C -> AB advantage or spreads it into controls.",
        "- Fractional signatures remain secondary diagnostics, not explanations.",
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
    features, arm_families = add_b75b_scores(features)
    events_by_arm = {arm: b73a.event_rows_for_rep(features, arm, args.event_quantile) for arm in arm_families}
    events = pd.concat(events_by_arm.values(), ignore_index=True)
    event_summary = summarize_events(events_by_arm, arm_families)
    topology = run_topology_audit(events_by_arm, args)
    readout = summarize_readout(topology, event_summary, arm_families)
    align = alignment_diagnostics(features, events_by_arm, arm_families)
    frac = fractional_secondary(readout, topology)
    classification = classify(readout, align, frac)

    features.to_csv(outdir / "Stage_B7_5b_representation_scores.csv", index=False)
    events.to_csv(outdir / "Stage_B7_5b_representation_events.csv", index=False)
    event_summary.to_csv(outdir / "Stage_B7_5b_event_survivor_summary.csv", index=False)
    topology.to_csv(outdir / "Stage_B7_5b_topology_results.csv", index=False)
    readout.to_csv(outdir / "Stage_B7_5b_readout_summary.csv", index=False)
    align.to_csv(outdir / "Stage_B7_5b_alignment_diagnostics.csv", index=False)
    frac.to_csv(outdir / "Stage_B7_5b_fractional_secondary_diagnostic.csv", index=False)
    classification.to_csv(outdir / "Stage_B7_5b_primary_classification.csv", index=False)
    write_summary(outdir / "Stage_B7_5b_execution_summary.md", readout, align, frac, classification, args)

    print(f"output_dir: {outdir}")
    print("\nReadout summary")
    print(readout.head(12).to_string(index=False))
    print("\nAlignment diagnostics")
    print(align.to_string(index=False))
    print("\nClassification")
    print(classification.to_string(index=False))
    print("\nFractional focus")
    print(frac[frac["is_close_to_target"].fillna(False)].head(30).to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_5b")
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
    parser.add_argument("--n-runs", type=int, default=24)
    parser.add_argument("--seed", type=int, default=75275)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
