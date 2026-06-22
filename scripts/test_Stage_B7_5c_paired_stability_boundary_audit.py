#!/usr/bin/env python3
"""Stage B7.5c paired stability-boundary audit."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

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


b73a = load_module("b73a_for_b75c", SCRIPTS / "test_Stage_B7_3a_c12_specificity_h24_collective_necessity_audit.py")
b75b = load_module("b75b_for_b75c", SCRIPTS / "test_Stage_B7_5b_c_to_ab_readout_geometry_audit.py")


def zscore(values: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    mu = np.nanmean(arr)
    sd = np.nanstd(arr)
    if not np.isfinite(sd) or sd <= 1e-12:
        return np.zeros_like(arr, dtype=float)
    return (arr - mu) / sd


def add_b75c_scores(features: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    out = b73a.add_representation_scores(features)
    ba_receiver = np.abs(pd.to_numeric(out["ba_receiver_side"], errors="coerce"))
    ba_standpoint = np.abs(pd.to_numeric(out["ba_standpoint_polarity"], errors="coerce"))
    ba_mag = pd.to_numeric(out["ba_standpoint_magnitude"], errors="coerce")

    out["c_to_ab_receiver_only"] = zscore(ba_receiver)
    out["c_to_ab_standpoint_only"] = zscore(ba_standpoint)
    out["c_to_ab_magnitude_only"] = zscore(ba_mag)
    out[REVERSE_ARM] = zscore(ba_receiver + ba_standpoint + ba_mag)
    out[FULL_SELF_ARM] = out["receiver_standpoint_magnitude_c"]

    arms = {
        REVERSE_ARM: "reverse_only_c_to_ab",
        FULL_SELF_ARM: "full_self_consistent_rstar",
        "c_to_ab_receiver_only": "receiver_only",
        "c_to_ab_standpoint_only": "standpoint_only",
        "c_to_ab_magnitude_only": "magnitude_only",
    }
    return out, arms


def simulate_with_seeds(n_nodes: int, edges: list[tuple[int, int]], schedule: list[dict[str, float]], seeds: np.ndarray, steps: int) -> np.ndarray:
    b3 = load_module("b3_sim_for_b75c", SCRIPTS / "test_Stage_B3_endogenous_event_carrier_readout.py")
    vals = []
    for seed in seeds:
        metric = b3.simulate_event_conditioned(n_nodes, edges, schedule, int(seed), steps=steps)
        vals.append(metric.get("differentiated_recovery", np.nan))
    return np.asarray(vals, dtype=float)


def build_events_and_schedules(features: pd.DataFrame, arms: dict[str, str], q: float, steps: int, n_nodes_by_topology: dict[str, int]) -> tuple[dict[str, pd.DataFrame], dict[tuple[str, str], list[dict[str, float]]]]:
    events_by_arm = {arm: b73a.event_rows_for_rep(features, arm, q) for arm in arms}
    schedules = {}
    for arm, events in events_by_arm.items():
        for topology, n_nodes in n_nodes_by_topology.items():
            schedule, _ = b73a.build_event_schedule(events, steps, n_nodes)
            schedules[(arm, topology)] = schedule
    return events_by_arm, schedules


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n_boot: int) -> tuple[float, float]:
    vals = np.asarray(values, dtype=float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return np.nan, np.nan
    draws = rng.choice(vals, size=(n_boot, len(vals)), replace=True).mean(axis=1)
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def run_paired_audit(features: pd.DataFrame, arms: dict[str, str], args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 753)
    topology_defs = {}
    for topology in TOPOLOGY_ARMS:
        n_nodes, edges, notes = b75b.topology_edges(topology, rng)
        topology_defs[topology] = (n_nodes, edges, notes)
    n_nodes_by_topology = {name: spec[0] for name, spec in topology_defs.items()}
    events_by_arm, schedules = build_events_and_schedules(features, arms, args.event_quantile, args.steps, n_nodes_by_topology)

    raw_rows = []
    readout_rows = []
    seed_bank = {
        topology: np.random.default_rng(args.seed + 1100 + i).integers(0, 2**31 - 1, size=args.n_runs)
        for i, topology in enumerate(TOPOLOGY_ARMS)
    }
    for topology, (n_nodes, edges, notes) in topology_defs.items():
        seeds = seed_bank[topology]
        for arm, family in arms.items():
            vals = simulate_with_seeds(n_nodes, edges, schedules[(arm, topology)], seeds, args.steps)
            for run_idx, value in enumerate(vals):
                raw_rows.append({
                    "topology_arm": topology,
                    "representation_arm": arm,
                    "arm_family": family,
                    "run_idx": run_idx,
                    "seed": int(seeds[run_idx]),
                    "differentiated_recovery": float(value),
                })
            readout_rows.append({
                "topology_arm": topology,
                "representation_arm": arm,
                "arm_family": family,
                "n_nodes": n_nodes,
                "n_directed_edges": len(edges),
                "topology_notes": notes,
                "mean_bounded_differentiated_recovery": float(np.nanmean(vals)),
                "sd_bounded_differentiated_recovery": float(np.nanstd(vals)),
                "n_runs": int(len(vals)),
                "n_seed_events": int(len(schedules[(arm, topology)])),
            })
    raw = pd.DataFrame(raw_rows)
    readout = pd.DataFrame(readout_rows)

    paired_rows = []
    raw_lookup = raw.set_index(["topology_arm", "representation_arm", "run_idx"])["differentiated_recovery"]
    boot_rng = np.random.default_rng(args.seed + 1753)
    comparisons = [
        (FULL_SELF_ARM, REVERSE_ARM, "full_minus_reverse"),
        (REVERSE_ARM, FULL_SELF_ARM, "reverse_minus_full"),
        ("c_to_ab_magnitude_only", REVERSE_ARM, "magnitude_minus_reverse"),
        ("c_to_ab_receiver_only", REVERSE_ARM, "receiver_minus_reverse"),
        ("c_to_ab_standpoint_only", REVERSE_ARM, "standpoint_minus_reverse"),
    ]
    for topology in TOPOLOGY_ARMS:
        for left, right, label in comparisons:
            diffs = []
            for run_idx in range(args.n_runs):
                diffs.append(float(raw_lookup[(topology, left, run_idx)] - raw_lookup[(topology, right, run_idx)]))
            diffs_arr = np.asarray(diffs, dtype=float)
            lo, hi = bootstrap_ci(diffs_arr, boot_rng, args.n_boot)
            paired_rows.append({
                "topology_arm": topology,
                "comparison": label,
                "left_arm": left,
                "right_arm": right,
                "mean_delta": float(np.nanmean(diffs_arr)),
                "median_delta": float(np.nanmedian(diffs_arr)),
                "sd_delta": float(np.nanstd(diffs_arr)),
                "p_left_greater_paired": float((1.0 + np.sum(diffs_arr <= 0.0)) / (len(diffs_arr) + 1.0)),
                "left_win_fraction": float(np.mean(diffs_arr > 0.0)),
                "bootstrap_ci_low": lo,
                "bootstrap_ci_high": hi,
                "stable_left_win": bool(lo > 0.0),
                "stable_right_win": bool(hi < 0.0),
            })
    paired = pd.DataFrame(paired_rows)
    return raw, readout, paired


def summarize_boundary(readout: pd.DataFrame, paired: pd.DataFrame) -> pd.DataFrame:
    rows = []
    primary = paired[(paired["topology_arm"].eq(PRIMARY_TOPOLOGY)) & (paired["comparison"].eq("full_minus_reverse"))].iloc[0]
    stable_full_topologies = paired[(paired["comparison"].eq("full_minus_reverse")) & (paired["stable_left_win"])]["topology_arm"].tolist()
    stable_reverse_topologies = paired[(paired["comparison"].eq("full_minus_reverse")) & (paired["stable_right_win"])]["topology_arm"].tolist()
    flip_topologies = paired[
        (paired["comparison"].eq("full_minus_reverse"))
        & (~paired["stable_left_win"])
        & (~paired["stable_right_win"])
    ]["topology_arm"].tolist()

    rows.append({
        "criterion": "primary_c12_prefers_full_self",
        "supported": bool(primary["mean_delta"] > 0.0),
        "basis": f"C12 full-minus-reverse mean delta {primary['mean_delta']:.6g}; CI [{primary['bootstrap_ci_low']:.6g}, {primary['bootstrap_ci_high']:.6g}]",
    })
    rows.append({
        "criterion": "primary_c12_stable_full_self",
        "supported": bool(primary["stable_left_win"]),
        "basis": f"C12 stable_left_win={primary['stable_left_win']}; left_win_fraction {primary['left_win_fraction']:.3f}",
    })
    rows.append({
        "criterion": "primary_c12_stable_reverse",
        "supported": bool(primary["stable_right_win"]),
        "basis": f"C12 stable_right_win={primary['stable_right_win']}; left_win_fraction {primary['left_win_fraction']:.3f}",
    })
    rows.append({
        "criterion": "stability_boundary_present",
        "supported": bool(len(stable_full_topologies) > 0 and (len(stable_reverse_topologies) > 0 or len(flip_topologies) > 0)),
        "basis": f"stable_full={len(stable_full_topologies)}; stable_reverse={len(stable_reverse_topologies)}; boundary_or_flip={len(flip_topologies)}",
    })
    rows.append({
        "criterion": "stable_full_topologies",
        "supported": bool(len(stable_full_topologies) > 0),
        "basis": "|".join(stable_full_topologies) if stable_full_topologies else "none",
    })
    rows.append({
        "criterion": "stable_reverse_topologies",
        "supported": bool(len(stable_reverse_topologies) > 0),
        "basis": "|".join(stable_reverse_topologies) if stable_reverse_topologies else "none",
    })
    return pd.DataFrame(rows)


def write_summary(path: Path, readout: pd.DataFrame, paired: pd.DataFrame, boundary: pd.DataFrame, args: argparse.Namespace) -> None:
    primary_rows = paired[paired["comparison"].eq("full_minus_reverse")].copy()
    c12_component = paired[
        paired["topology_arm"].eq(PRIMARY_TOPOLOGY)
        & paired["comparison"].isin(["magnitude_minus_reverse", "receiver_minus_reverse", "standpoint_minus_reverse"])
    ].copy()
    lines = [
        "# Stage B7.5c Paired Stability-Boundary Audit",
        "",
        "Status: executed after `Stage_B7_5c_preregistration_email_sent.md`.",
        "",
        "## Registered Question",
        "",
        "Under which seed, topology, event-schedule, and ring-sharing conditions does C12 readout prefer reverse-side C->AB, and under which conditions does it prefer full self-consistent R*?",
        "",
        "## Primary Paired Boundary: Full Self Minus Reverse",
        "",
        primary_rows.to_csv(index=False).strip(),
        "",
        "## C12 Component Deltas Against Reverse",
        "",
        c12_component.to_csv(index=False).strip(),
        "",
        "## Boundary Classification",
        "",
        boundary.to_csv(index=False).strip(),
        "",
        "## Readout Means",
        "",
        readout.sort_values(["topology_arm", "mean_bounded_differentiated_recovery"], ascending=[True, False]).to_csv(index=False).strip(),
        "",
        "## Decision Boundary",
        "",
        "- Stable reverse-side readout requires reverse-only C->AB to beat full self-consistent R* under paired seeds, with stable bootstrap direction and C12 specificity.",
        "- Stable self-consistent readout requires full self-consistent R* to beat reverse-only C->AB under paired seeds, with stable bootstrap direction and C12 specificity.",
        "- Boundary result means ordering changes by seed/topology/schedule/ring-sharing, so the object is a stability boundary rather than a global winner.",
        "",
        "## Settings",
        "",
        f"- event_quantile: {args.event_quantile}",
        f"- steps: {args.steps}",
        f"- n_runs: {args.n_runs}",
        f"- n_boot: {args.n_boot}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    features = b73a.load_b72_features(args)
    features, arms = add_b75c_scores(features)
    raw, readout, paired = run_paired_audit(features, arms, args)
    boundary = summarize_boundary(readout, paired)

    features.to_csv(outdir / "Stage_B7_5c_representation_scores.csv", index=False)
    raw.to_csv(outdir / "Stage_B7_5c_paired_raw_runs.csv", index=False)
    readout.to_csv(outdir / "Stage_B7_5c_readout_summary.csv", index=False)
    paired.to_csv(outdir / "Stage_B7_5c_paired_delta_summary.csv", index=False)
    boundary.to_csv(outdir / "Stage_B7_5c_boundary_classification.csv", index=False)
    write_summary(outdir / "Stage_B7_5c_execution_summary.md", readout, paired, boundary, args)

    print(f"output_dir: {outdir}")
    print("\nPrimary full-minus-reverse")
    print(paired[paired["comparison"].eq("full_minus_reverse")].to_string(index=False))
    print("\nC12 component deltas")
    print(paired[paired["topology_arm"].eq(PRIMARY_TOPOLOGY)].to_string(index=False))
    print("\nBoundary classification")
    print(boundary.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_5c")
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
    parser.add_argument("--n-runs", type=int, default=48)
    parser.add_argument("--n-boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=75375)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
