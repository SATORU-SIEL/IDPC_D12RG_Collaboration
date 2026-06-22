#!/usr/bin/env python3
"""Stage B7.5a self-consistency, topology, and fractional tracing audit."""

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
REVERSE_ARM = "reverse_only_c_to_ab"
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
    "phase_target_shuffled_c12",
    "ring_edge_swapped_c12_1_5",
    "ring_edge_swapped_c12_1_7",
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


b73a = load_module("b73a_for_b75a", SCRIPTS / "test_Stage_B7_3a_c12_specificity_h24_collective_necessity_audit.py")


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
        _, n, c12_edges, _, _ = load_module("b3_for_b75a", SCRIPTS / "test_Stage_B3_endogenous_event_carrier_readout.py").topology_definition("C12(1,2)")
        edges: set[tuple[int, int]] = set()
        while len(edges) < len(c12_edges):
            i = int(rng.integers(0, n))
            j = int(rng.integers(0, n))
            if i != j:
                edges.add((i, j))
        return n, sorted(edges), "C12 edge-count matched random directed null"
    if name == "phase_target_shuffled_c12":
        n, edges, _ = b73a.topology_edges("c12_1_2", rng)
        return n, edges, "C12(1,2) edges with event targets phase-shuffled before simulation"
    if name == "ring_edge_swapped_c12_1_5":
        return 12, unique_edges(12, (-5, -1, 1, 5)), "C12 ring-edge-swapped control using 1/5 jumps"
    if name == "ring_edge_swapped_c12_1_7":
        return 12, unique_edges(12, (-7, -1, 1, 7)), "C12 ring-edge-swapped control using 1/7 jumps"
    if name == "ring_share_c12_plus_5":
        return 12, unique_edges(12, (-5, -2, -1, 1, 2, 5)), "C12(1,2) with shared 5-ring proxy edges"
    if name == "ring_share_c12_plus_7":
        return 12, unique_edges(12, (-7, -2, -1, 1, 2, 7)), "C12(1,2) with shared 7 mod 12 proxy edges"
    if name == "ring_share_c12_plus_10":
        return 12, unique_edges(12, (-10, -2, -1, 1, 2, 10)), "C12(1,2) with shared 10-ring proxy edges"
    if name == "ring_share_c12_plus_11":
        return 12, unique_edges(12, (-11, -2, -1, 1, 2, 11)), "C12(1,2) with shared 11 mod 12 reflective proxy edges"
    raise ValueError(f"unknown topology {name}")


def add_b75a_scores(features: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    out = b73a.add_representation_scores(features)
    ab_receiver = np.abs(pd.to_numeric(out["ab_receiver_side"], errors="coerce"))
    ba_receiver = np.abs(pd.to_numeric(out["ba_receiver_side"], errors="coerce"))
    ab_standpoint = np.abs(pd.to_numeric(out["ab_standpoint_polarity"], errors="coerce"))
    ba_standpoint = np.abs(pd.to_numeric(out["ba_standpoint_polarity"], errors="coerce"))
    ab_mag = pd.to_numeric(out["ab_standpoint_magnitude"], errors="coerce")
    ba_mag = pd.to_numeric(out["ba_standpoint_magnitude"], errors="coerce")
    o1 = pd.to_numeric(out["O1_lag0_AB_raw"], errors="coerce")
    o2 = pd.to_numeric(out["O2_lag5_AB_raw"], errors="coerce")

    reverse_raw = zscore(ba_receiver + ba_standpoint + ba_mag)
    endpoint = zscore(np.abs(o1) + np.abs(o2) + np.abs(o1 - o2))
    forward_receiver = zscore(ab_receiver)
    forward_standpoint = zscore(ab_standpoint)
    forward_magnitude = zscore(ab_mag)

    out[REVERSE_ARM] = reverse_raw
    out["reverse_plus_endpoint_direct_ab"] = zscore(reverse_raw + endpoint)
    out["reverse_plus_receiver_ab"] = zscore(reverse_raw + forward_receiver)
    out["reverse_plus_standpoint_ab"] = zscore(reverse_raw + forward_standpoint)
    out["reverse_plus_magnitude_ab"] = zscore(reverse_raw + forward_magnitude)
    out["reverse_plus_receiver_standpoint_ab"] = zscore(reverse_raw + forward_receiver + forward_standpoint)
    out["reverse_plus_receiver_magnitude_ab"] = zscore(reverse_raw + forward_receiver + forward_magnitude)
    out["reverse_plus_standpoint_magnitude_ab"] = zscore(reverse_raw + forward_standpoint + forward_magnitude)
    out["reverse_plus_receiver_standpoint_magnitude_ab"] = zscore(reverse_raw + forward_receiver + forward_standpoint + forward_magnitude)
    out[FULL_SELF_ARM] = out["receiver_standpoint_magnitude_c"]

    arms = {
        REVERSE_ARM: "reverse_only",
        "reverse_plus_endpoint_direct_ab": "reverse_plus_endpoint_direct_ab",
        "reverse_plus_receiver_ab": "reverse_plus_receiver_ab",
        "reverse_plus_standpoint_ab": "reverse_plus_standpoint_ab",
        "reverse_plus_magnitude_ab": "reverse_plus_magnitude_ab",
        "reverse_plus_receiver_standpoint_ab": "reverse_plus_receiver_standpoint_ab",
        "reverse_plus_receiver_magnitude_ab": "reverse_plus_receiver_magnitude_ab",
        "reverse_plus_standpoint_magnitude_ab": "reverse_plus_standpoint_magnitude_ab",
        "reverse_plus_receiver_standpoint_magnitude_ab": "reverse_plus_receiver_standpoint_magnitude_ab",
        FULL_SELF_ARM: "full_self_consistent_rstar",
    }
    return out, arms


def maybe_phase_shuffle_schedule(
    schedule: list[dict[str, float]],
    topology: str,
    n_nodes: int,
    rng: np.random.Generator,
) -> list[dict[str, float]]:
    if topology != "phase_target_shuffled_c12":
        return schedule
    targets = rng.permutation(np.arange(n_nodes))
    return [{**item, "target": int(targets[int(item["target"]) % n_nodes])} for item in schedule]


def run_topology_audit(events_by_arm: dict[str, pd.DataFrame], args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 751)
    rows = []
    for arm, events in events_by_arm.items():
        for topology in TOPOLOGY_ARMS:
            n_nodes, edges, notes = topology_edges(topology, rng)
            schedule, meta = b73a.build_event_schedule(events, args.steps, n_nodes)
            schedule = maybe_phase_shuffle_schedule(schedule, topology, n_nodes, rng)
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
    rows = []
    controls = [
        "c12_reversed",
        "c12_side_broken",
        "c12_shuffled",
        "c10",
        "c11",
        "c13",
        "c14",
        "degree_matched_null",
        "edge_count_matched_null",
        "phase_target_shuffled_c12",
    ]
    for arm, family in arm_families.items():
        c12 = lookup.get((arm, PRIMARY_TOPOLOGY), np.nan)
        no_top = lookup.get((arm, "no_topology_baseline"), np.nan)
        control_values = [lookup.get((arm, name), np.nan) for name in controls]
        ring_values = [lookup.get((arm, name), np.nan) for name in TOPOLOGY_ARMS if name.startswith("ring_share")]
        swapped_values = [lookup.get((arm, name), np.nan) for name in TOPOLOGY_ARMS if name.startswith("ring_edge_swapped")]
        rows.append({
            "representation_arm": arm,
            "arm_family": family,
            "c12_readout": c12,
            "no_topology_readout": no_top,
            "effect_vs_no_topology": c12 - no_top if np.isfinite(c12) and np.isfinite(no_top) else np.nan,
            "n_positive_specificity_controls": int(sum((c12 - v) > 0 for v in control_values if np.isfinite(v))) if np.isfinite(c12) else 0,
            "min_specificity_margin": float(np.nanmin([c12 - v for v in control_values if np.isfinite(v)])) if np.isfinite(c12) else np.nan,
            "mean_ring_share_readout": float(np.nanmean(ring_values)) if ring_values else np.nan,
            "mean_swapped_ring_readout": float(np.nanmean(swapped_values)) if swapped_values else np.nan,
            "effect_vs_ring_share_mean": c12 - float(np.nanmean(ring_values)) if ring_values and np.isfinite(c12) else np.nan,
            "effect_vs_swapped_ring_mean": c12 - float(np.nanmean(swapped_values)) if swapped_values and np.isfinite(c12) else np.nan,
        })
    return pd.DataFrame(rows).merge(event_summary, on=["representation_arm", "arm_family"], how="left")


def summarize_increment(readout: pd.DataFrame) -> pd.DataFrame:
    reverse = readout[readout["representation_arm"].eq(REVERSE_ARM)].iloc[0]
    rows = []
    for _, row in readout.iterrows():
        rows.append({
            "representation_arm": row["representation_arm"],
            "arm_family": row["arm_family"],
            "increment_vs_reverse_c12": row["c12_readout"] - reverse["c12_readout"],
            "increment_vs_reverse_effect_no_topology": row["effect_vs_no_topology"] - reverse["effect_vs_no_topology"],
            "increment_vs_reverse_specificity_controls": row["n_positive_specificity_controls"] - reverse["n_positive_specificity_controls"],
            "top4_survivor_overlap": row["top4_survivor_overlap"],
            "survivor_strength_fraction": row["survivor_strength_fraction"],
        })
    return pd.DataFrame(rows).sort_values(
        ["increment_vs_reverse_effect_no_topology", "increment_vs_reverse_c12"],
        ascending=False,
    )


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
    if topology_arm.startswith("ring_share"):
        tags.append("ring_sharing")
    if topology_arm.startswith("ring_edge_swapped"):
        tags.append("ring_edge_swapped")
    return "|".join(tags) if tags else "unassigned"


def fractional_tracing(readout: pd.DataFrame, topology: pd.DataFrame, increment: pd.DataFrame) -> pd.DataFrame:
    rows = []
    event_metrics = [
        "top4_precision_vs_registered",
        "top4_recall_vs_registered",
        "top4_jaccard_vs_registered",
        "survivor_event_fraction",
        "survivor_strength_fraction",
    ]
    for _, row in readout.iterrows():
        for metric in event_metrics:
            value = float(row[metric]) if pd.notna(row[metric]) else np.nan
            frac, err, close = nearest_registered_fraction(value)
            if close or frac in {"3/7", "2/11"}:
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
    reverse_top = topology[topology["representation_arm"].eq(REVERSE_ARM)].set_index("topology_arm")
    for _, row in topology.iterrows():
        if row["representation_arm"] == REVERSE_ARM:
            continue
        top = row["topology_arm"]
        if top not in reverse_top.index:
            continue
        inc = float(row["mean_bounded_differentiated_recovery"] - reverse_top.loc[top, "mean_bounded_differentiated_recovery"])
        scaled = abs(inc) / max(abs(float(reverse_top.loc[top, "mean_bounded_differentiated_recovery"])), 1e-12)
        frac, err, close = nearest_registered_fraction(scaled)
        rows.append({
            "source": "topology_increment_vs_reverse_scaled",
            "representation_arm": row["representation_arm"],
            "topology_arm": top,
            "metric": "abs_increment_over_reverse_fraction",
            "value": scaled,
            "nearest_target_fraction": frac,
            "abs_error_to_target": err,
            "is_close_to_target": close,
            "top4_labels_by_event_strength": "",
            "resonance_tags": resonance_tags(top, ""),
        })
    for _, row in increment.iterrows():
        value = float(row["survivor_strength_fraction"]) if pd.notna(row["survivor_strength_fraction"]) else np.nan
        frac, err, close = nearest_registered_fraction(value)
        rows.append({
            "source": "survivor_strength_fraction_increment_arm",
            "representation_arm": row["representation_arm"],
            "topology_arm": "representation_events",
            "metric": "survivor_strength_fraction",
            "value": value,
            "nearest_target_fraction": frac,
            "abs_error_to_target": err,
            "is_close_to_target": close,
            "top4_labels_by_event_strength": "",
            "resonance_tags": "survivor_strength",
        })
    return pd.DataFrame(rows).sort_values(["is_close_to_target", "nearest_target_fraction", "abs_error_to_target"], ascending=[False, True, True])


def classify(readout: pd.DataFrame, increment: pd.DataFrame, frac: pd.DataFrame) -> pd.DataFrame:
    reverse = readout[readout["representation_arm"].eq(REVERSE_ARM)].iloc[0]
    full = readout[readout["representation_arm"].eq(FULL_SELF_ARM)].iloc[0]
    best_inc = increment[increment["representation_arm"].ne(REVERSE_ARM)].iloc[0]
    strong_fractional_localization = bool(
        frac["is_close_to_target"].fillna(False).any()
        and (
            frac["resonance_tags"].str.contains("two_step_c12|ring_sharing|5_or_10_ring_proxy|x3_or_7mod12_proxy|11mod12", regex=True).any()
        )
    )
    rows = [
        {
            "criterion": "self_consistency_increment_over_reverse",
            "supported": bool(full["effect_vs_no_topology"] > reverse["effect_vs_no_topology"]),
            "basis": f"full effect {full['effect_vs_no_topology']:.6g}; reverse effect {reverse['effect_vs_no_topology']:.6g}",
        },
        {
            "criterion": "best_forward_component_identified",
            "supported": bool(best_inc["increment_vs_reverse_effect_no_topology"] > 0),
            "basis": f"best arm {best_inc['representation_arm']} increment {best_inc['increment_vs_reverse_effect_no_topology']:.6g}",
        },
        {
            "criterion": "topology_specificity_present",
            "supported": bool(full["n_positive_specificity_controls"] >= 7 and full["min_specificity_margin"] > 0),
            "basis": f"full self arm {int(full['n_positive_specificity_controls'])} positive controls; min margin {full['min_specificity_margin']:.6g}",
        },
        {
            "criterion": "fractional_signatures_as_diagnostics_localized",
            "supported": strong_fractional_localization,
            "basis": "fractional targets detected with topology/survivor resonance tags" if strong_fractional_localization else "no localized close fractional target detected",
        },
        {
            "criterion": "two_eleven_anomaly_tracked",
            "supported": bool((frac["nearest_target_fraction"].eq("2/11") & frac["is_close_to_target"].fillna(False)).any()),
            "basis": "at least one metric is within 0.01 of 2/11" if bool((frac["nearest_target_fraction"].eq("2/11") & frac["is_close_to_target"].fillna(False)).any()) else "2/11 not localized within tolerance",
        },
    ]
    return pd.DataFrame(rows)


def write_summary(
    path: Path,
    readout: pd.DataFrame,
    increment: pd.DataFrame,
    classification: pd.DataFrame,
    frac: pd.DataFrame,
    args: argparse.Namespace,
) -> None:
    best = increment.head(8)
    frac_focus = frac[
        frac["is_close_to_target"].fillna(False)
        | frac["nearest_target_fraction"].isin(["2/11", "3/7"])
        | frac["resonance_tags"].str.contains("11mod12|ring_sharing|two_step_c12", regex=True, na=False)
    ].head(80)
    lines = [
        "# Stage B7.5a Self-Consistency / Topology / Fractional Diagnostic Audit",
        "",
        "Status: executed after `Stage_B7_5a_preregistration_email_sent.md`.",
        "",
        "## Registered Question",
        "",
        "Can the exact fractional signatures be shown to be robust, localized, and predictably transformable diagnostics of the survivor structure before assigning them to a specific cyclotomic or ring-resonance interpretation?",
        "",
        "## Layer 1: Increment Over Reverse-Only",
        "",
        best.to_csv(index=False).strip(),
        "",
        "## Layer 2: Readout Summary",
        "",
        readout.sort_values(["effect_vs_no_topology", "c12_readout"], ascending=False).to_csv(index=False).strip(),
        "",
        "## Layer 3: Classification",
        "",
        classification.to_csv(index=False).strip(),
        "",
        "## Layer 4: Fractional Diagnostic Focus",
        "",
        frac_focus.to_csv(index=False).strip(),
        "",
        "## Decision Boundary",
        "",
        "- Strong support requires self-consistency increment over reverse-only, topology-specific gain, and localized fractional diagnostics.",
        "- Intermediate support allows an increment with only partial topology or fractional localization.",
        "- Negative support means reverse-only remains equal or stronger, topology controls behave similarly, or fractional signatures appear without readout strength.",
        "- Fractions are treated as diagnostics, not explanations.",
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
    features, arm_families = add_b75a_scores(features)
    events_by_arm = {arm: b73a.event_rows_for_rep(features, arm, args.event_quantile) for arm in arm_families}
    events = pd.concat(events_by_arm.values(), ignore_index=True)
    event_summary = summarize_events(events_by_arm, arm_families)
    topology = run_topology_audit(events_by_arm, args)
    readout = summarize_readout(topology, event_summary, arm_families)
    increment = summarize_increment(readout)
    frac = fractional_tracing(readout, topology, increment)
    classification = classify(readout, increment, frac)

    features.to_csv(outdir / "Stage_B7_5a_representation_scores.csv", index=False)
    events.to_csv(outdir / "Stage_B7_5a_representation_events.csv", index=False)
    topology.to_csv(outdir / "Stage_B7_5a_topology_results.csv", index=False)
    event_summary.to_csv(outdir / "Stage_B7_5a_event_survivor_summary.csv", index=False)
    readout.to_csv(outdir / "Stage_B7_5a_readout_summary.csv", index=False)
    increment.to_csv(outdir / "Stage_B7_5a_increment_summary.csv", index=False)
    frac.to_csv(outdir / "Stage_B7_5a_fractional_tracing_diagnostic.csv", index=False)
    classification.to_csv(outdir / "Stage_B7_5a_primary_classification.csv", index=False)
    write_summary(outdir / "Stage_B7_5a_execution_summary.md", readout, increment, classification, frac, args)

    print(f"output_dir: {outdir}")
    print("\nIncrement over reverse-only")
    print(increment.head(10).to_string(index=False))
    print("\nClassification")
    print(classification.to_string(index=False))
    print("\nFractional focus")
    print(frac[frac["is_close_to_target"].fillna(False)].head(30).to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_5a")
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
    parser.add_argument("--seed", type=int, default=75175)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
