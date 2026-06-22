#!/usr/bin/env python3
"""Stage B7.5d topology-flip localization audit."""

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

REGISTERED_SURVIVORS = {"P10", "P5", "P21", "P15"}
REVERSE_ARM = "reverse_only_c_to_ab"
FULL_SELF_ARM = "full_self_consistent_rstar"
PRIMARY_COMPARISON = "full_minus_reverse"

SWEEP_TOPOLOGIES = [f"c{n}" for n in range(8, 17)]
PERTURB_BASES = ["c10", "c12", "c13", "c14"]
PERTURB_KINDS = ["reversed", "side_broken", "shuffled", "degree_null", "edge_count_null", "ring_share_5", "ring_share_7", "ring_share_10", "ring_share_11"]
TOPOLOGY_ARMS = SWEEP_TOPOLOGIES + [f"{base}_{kind}" for base in PERTURB_BASES for kind in PERTURB_KINDS]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


b73a = load_module("b73a_for_b75d", SCRIPTS / "test_Stage_B7_3a_c12_specificity_h24_collective_necessity_audit.py")


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


def degree_matched_edges(n: int, edges: list[tuple[int, int]], rng: np.random.Generator) -> list[tuple[int, int]]:
    b3 = load_module("b3_for_b75d", SCRIPTS / "test_Stage_B3_endogenous_event_carrier_readout.py")
    return b3.degree_matched_random_edges(n, edges, rng)


def edge_count_null(n: int, m: int, rng: np.random.Generator) -> list[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    while len(edges) < m:
        i = int(rng.integers(0, n))
        j = int(rng.integers(0, n))
        if i != j:
            edges.add((i, j))
    return sorted(edges)


def topology_edges(name: str, rng: np.random.Generator) -> tuple[int, list[tuple[int, int]], str]:
    if name in SWEEP_TOPOLOGIES:
        n = int(name[1:])
        return n, unique_edges(n, (-2, -1, 1, 2)), f"C{n}(1,2) topology sweep"
    base, kind = name.split("_", 1)
    n = int(base[1:])
    base_edges = unique_edges(n, (-2, -1, 1, 2))
    if kind == "reversed":
        return n, sorted((j, i) for i, j in base_edges), f"C{n}(1,2) reversed"
    if kind == "side_broken":
        return n, degree_matched_edges(n, base_edges, rng), f"C{n}(1,2) degree-matched side-broken"
    if kind == "shuffled":
        src = [i for i, _ in base_edges]
        dst = np.array([j for _, j in base_edges], dtype=int)
        rng.shuffle(dst)
        shuffled = sorted({(int(i), int(j)) for i, j in zip(src, dst) if int(i) != int(j)})
        while len(shuffled) < len(base_edges):
            i = int(rng.integers(0, n))
            j = int(rng.integers(0, n))
            if i != j:
                shuffled = sorted(set(shuffled + [(i, j)]))
        return n, shuffled[: len(base_edges)], f"C{n}(1,2) target-shuffled"
    if kind == "degree_null":
        return n, degree_matched_edges(n, base_edges, rng), f"C{n}(1,2) degree-matched null"
    if kind == "edge_count_null":
        return n, edge_count_null(n, len(base_edges), rng), f"C{n}(1,2) edge-count null"
    if kind.startswith("ring_share_"):
        jump = int(kind.rsplit("_", 1)[1])
        return n, unique_edges(n, tuple(sorted({-2, -1, 1, 2, -jump, jump}))), f"C{n}(1,2) ring-share plus {jump}"
    raise ValueError(f"unknown topology {name}")


def add_scores(features: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    out = b73a.add_representation_scores(features)
    ba_receiver = np.abs(pd.to_numeric(out["ba_receiver_side"], errors="coerce"))
    ba_standpoint = np.abs(pd.to_numeric(out["ba_standpoint_polarity"], errors="coerce"))
    ba_mag = pd.to_numeric(out["ba_standpoint_magnitude"], errors="coerce")
    out[REVERSE_ARM] = zscore(ba_receiver + ba_standpoint + ba_mag)
    out[FULL_SELF_ARM] = out["receiver_standpoint_magnitude_c"]
    out["c_to_ab_receiver_only"] = zscore(ba_receiver)
    out["c_to_ab_magnitude_only"] = zscore(ba_mag)
    out["c_to_ab_standpoint_only"] = zscore(ba_standpoint)
    return out, {
        REVERSE_ARM: "reverse_only",
        FULL_SELF_ARM: "full_self_consistent",
        "c_to_ab_receiver_only": "receiver_only",
        "c_to_ab_magnitude_only": "magnitude_only",
        "c_to_ab_standpoint_only": "standpoint_only",
    }


def simulate_with_seeds(n_nodes: int, edges: list[tuple[int, int]], schedule: list[dict[str, float]], seeds: np.ndarray, steps: int) -> np.ndarray:
    b3 = load_module("b3_sim_for_b75d", SCRIPTS / "test_Stage_B3_endogenous_event_carrier_readout.py")
    vals = []
    for seed in seeds:
        metric = b3.simulate_event_conditioned(n_nodes, edges, schedule, int(seed), steps=steps)
        vals.append(metric.get("differentiated_recovery", np.nan))
    return np.asarray(vals, dtype=float)


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n_boot: int) -> tuple[float, float]:
    vals = np.asarray(values, dtype=float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return np.nan, np.nan
    draws = rng.choice(vals, size=(n_boot, len(vals)), replace=True).mean(axis=1)
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def topology_features(name: str, n_nodes: int, n_edges: int) -> dict[str, object]:
    if name in SWEEP_TOPOLOGIES:
        base = name
        kind = "sweep"
    else:
        base, kind = name.split("_", 1)
    n = int(base[1:])
    return {
        "base_topology": base,
        "perturbation_kind": kind,
        "node_count_n": n,
        "distance_from_12": abs(n - 12),
        "signed_distance_from_12": n - 12,
        "is_odd": bool(n % 2),
        "edge_count": n_edges,
        "is_ring_sharing": bool("ring_share" in kind),
        "is_reversed": bool(kind == "reversed"),
        "is_null": bool("null" in kind),
    }


def summarize_events(features: pd.DataFrame, arm: str, q: float) -> dict[str, object]:
    events = b73a.event_rows_for_rep(features, arm, q)
    labels = events["label"].astype(str)
    strength = pd.to_numeric(events["strength"], errors="coerce").fillna(0.0)
    survivor = labels.isin(REGISTERED_SURVIVORS)
    by_label = events.assign(strength=strength).groupby("label", as_index=False)["strength"].sum()
    top4 = set(by_label.sort_values("strength", ascending=False).head(4)["label"].astype(str))
    overlap = top4 & REGISTERED_SURVIVORS
    phase = pd.to_numeric(events["phase"], errors="coerce").dropna().to_numpy(dtype=float)
    phase_conc = float(abs(np.mean(np.exp(1j * phase)))) if len(phase) else np.nan
    return {
        f"{arm}_top4": "|".join(sorted(top4, key=lambda x: int(x[1:]))),
        f"{arm}_top4_survivor_overlap": int(len(overlap)),
        f"{arm}_survivor_strength_fraction": float(strength[survivor].sum() / strength.sum()) if float(strength.sum()) > 0 else np.nan,
        f"{arm}_phase_concentration": phase_conc,
    }


def run_audit(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    topo_rng = np.random.default_rng(args.seed + 755)
    boot_rng = np.random.default_rng(args.seed + 2755)
    features = b73a.load_b72_features(args)
    features, arms = add_scores(features)
    events_by_arm = {arm: b73a.event_rows_for_rep(features, arm, args.event_quantile) for arm in arms}

    topo_defs = {}
    for topology in TOPOLOGY_ARMS:
        topo_defs[topology] = topology_edges(topology, topo_rng)
    seed_bank = {
        topology: np.random.default_rng(args.seed + 3100 + i).integers(0, 2**31 - 1, size=args.n_runs)
        for i, topology in enumerate(TOPOLOGY_ARMS)
    }
    raw_rows = []
    readout_rows = []
    for topology, (n_nodes, edges, notes) in topo_defs.items():
        seeds = seed_bank[topology]
        for arm, family in arms.items():
            schedule, meta = b73a.build_event_schedule(events_by_arm[arm], args.steps, n_nodes)
            vals = simulate_with_seeds(n_nodes, edges, schedule, seeds, args.steps)
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
                "n_seed_events": int(meta["n_events"]),
                **topology_features(topology, n_nodes, len(edges)),
            })
    raw = pd.DataFrame(raw_rows)
    readout = pd.DataFrame(readout_rows)
    raw_lookup = raw.set_index(["topology_arm", "representation_arm", "run_idx"])["differentiated_recovery"]
    comparisons = [
        (FULL_SELF_ARM, REVERSE_ARM, PRIMARY_COMPARISON),
        ("c_to_ab_receiver_only", REVERSE_ARM, "receiver_minus_reverse"),
        ("c_to_ab_magnitude_only", REVERSE_ARM, "magnitude_minus_reverse"),
        ("c_to_ab_standpoint_only", REVERSE_ARM, "standpoint_minus_reverse"),
    ]
    paired_rows = []
    for topology in TOPOLOGY_ARMS:
        topo_n, topo_edges, _ = topo_defs[topology]
        topo_meta = topology_features(topology, topo_n, len(topo_edges))
        for left, right, label in comparisons:
            diffs = np.asarray([raw_lookup[(topology, left, run_idx)] - raw_lookup[(topology, right, run_idx)] for run_idx in range(args.n_runs)], dtype=float)
            lo, hi = bootstrap_ci(diffs, boot_rng, args.n_boot)
            if lo > 0:
                cls = "full-stable" if label == PRIMARY_COMPARISON else "left-stable"
            elif hi < 0:
                cls = "reverse-stable" if label == PRIMARY_COMPARISON else "right-stable"
            else:
                cls = "boundary"
            paired_rows.append({
                "topology_arm": topology,
                "comparison": label,
                "left_arm": left,
                "right_arm": right,
                "mean_delta": float(np.nanmean(diffs)),
                "median_delta": float(np.nanmedian(diffs)),
                "sd_delta": float(np.nanstd(diffs)),
                "left_win_fraction": float(np.mean(diffs > 0)),
                "bootstrap_ci_low": lo,
                "bootstrap_ci_high": hi,
                "classification": cls,
                **topo_meta,
            })
    paired = pd.DataFrame(paired_rows)
    primary = paired[paired["comparison"].eq(PRIMARY_COMPARISON)].copy()
    event_rows = []
    for arm in arms:
        event_rows.append({"representation_arm": arm, **summarize_events(features, arm, args.event_quantile)})
    event_summary = pd.DataFrame(event_rows)
    return raw, readout, paired, event_summary


def classify(primary: pd.DataFrame) -> pd.DataFrame:
    def cls(topology: str) -> str:
        rows = primary[primary["topology_arm"].eq(topology)]
        return str(rows.iloc[0]["classification"]) if len(rows) else "missing"

    stable_full = primary[primary["classification"].eq("full-stable")]["topology_arm"].tolist()
    stable_reverse = primary[primary["classification"].eq("reverse-stable")]["topology_arm"].tolist()
    boundary = primary[primary["classification"].eq("boundary")]["topology_arm"].tolist()
    rows = [
        {
            "criterion": "c13_full_self_reproduces",
            "supported": cls("c13") == "full-stable",
            "basis": f"c13 classification={cls('c13')}",
        },
        {
            "criterion": "c12_reverse_reproduces",
            "supported": cls("c12") == "reverse-stable",
            "basis": f"c12 classification={cls('c12')}",
        },
        {
            "criterion": "c10_c14_boundary_reproduce",
            "supported": cls("c10") == "boundary" and cls("c14") == "boundary",
            "basis": f"c10={cls('c10')}; c14={cls('c14')}",
        },
        {
            "criterion": "topology_dependent_boundary_present",
            "supported": bool(stable_full and stable_reverse and boundary),
            "basis": f"full={len(stable_full)}; reverse={len(stable_reverse)}; boundary={len(boundary)}",
        },
        {
            "criterion": "stable_full_topologies",
            "supported": bool(stable_full),
            "basis": "|".join(stable_full) if stable_full else "none",
        },
        {
            "criterion": "stable_reverse_topologies",
            "supported": bool(stable_reverse),
            "basis": "|".join(stable_reverse) if stable_reverse else "none",
        },
        {
            "criterion": "boundary_topologies",
            "supported": bool(boundary),
            "basis": "|".join(boundary) if boundary else "none",
        },
    ]
    return pd.DataFrame(rows)


def write_summary(path: Path, paired: pd.DataFrame, readout: pd.DataFrame, event_summary: pd.DataFrame, classification: pd.DataFrame, args: argparse.Namespace) -> None:
    primary = paired[paired["comparison"].eq(PRIMARY_COMPARISON)].copy()
    sweep = primary[primary["perturbation_kind"].eq("sweep")].copy()
    perturb_focus = primary[~primary["perturbation_kind"].eq("sweep")].copy()
    lines = [
        "# Stage B7.5d Topology-Flip Localization Audit",
        "",
        "Status: executed after `Stage_B7_5d_preregistration_email_sent.md`.",
        "",
        "## Registered Question",
        "",
        "Under which topology conditions does the ordering between reverse-side C->AB and full self-consistent R* flip?",
        "",
        "## Layer 1: C8-C16 Sweep",
        "",
        sweep.to_csv(index=False).strip(),
        "",
        "## Layer 2: Perturbation Focus",
        "",
        perturb_focus.to_csv(index=False).strip(),
        "",
        "## Boundary Classification",
        "",
        classification.to_csv(index=False).strip(),
        "",
        "## Event Geometry Summary",
        "",
        event_summary.to_csv(index=False).strip(),
        "",
        "## Readout Means",
        "",
        readout.sort_values(["topology_arm", "mean_bounded_differentiated_recovery"], ascending=[True, False]).to_csv(index=False).strip(),
        "",
        "## Decision Boundary",
        "",
        "- Strong support requires C13 full-self advantage, C12 reverse advantage, C10/C14 boundary behavior, and topology-dependent classification to reproduce.",
        "- Intermediate support means flips appear but are not cleanly explained by N, ring-sharing, or receiver geometry.",
        "- Negative support means C13 or C10/C14 classifications collapse under rerun.",
        "- Fractional signatures remain secondary diagnostics, not explanations.",
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
    raw, readout, paired, event_summary = run_audit(args)
    primary = paired[paired["comparison"].eq(PRIMARY_COMPARISON)].copy()
    classification = classify(primary)
    raw.to_csv(outdir / "Stage_B7_5d_paired_raw_runs.csv", index=False)
    readout.to_csv(outdir / "Stage_B7_5d_readout_summary.csv", index=False)
    paired.to_csv(outdir / "Stage_B7_5d_paired_delta_summary.csv", index=False)
    event_summary.to_csv(outdir / "Stage_B7_5d_event_geometry_summary.csv", index=False)
    classification.to_csv(outdir / "Stage_B7_5d_boundary_classification.csv", index=False)
    write_summary(outdir / "Stage_B7_5d_execution_summary.md", paired, readout, event_summary, classification, args)

    print(f"output_dir: {outdir}")
    print("\nC8-C16 primary sweep")
    print(primary[primary["perturbation_kind"].eq("sweep")].to_string(index=False))
    print("\nClassification")
    print(classification.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_5d")
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
    parser.add_argument("--n-runs", type=int, default=36)
    parser.add_argument("--n-boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=75575)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
