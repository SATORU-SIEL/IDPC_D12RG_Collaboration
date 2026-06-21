#!/usr/bin/env python3
"""Private prescreen for Luke's paired Phi^12 quadrature topology proposal."""

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
from test_Stage_B7_4_phi_invariant_vacuum_layer_c_audit import add_phi_candidates  # noqa: E402


def c12_edges(offset: int = 0, reverse: bool = False) -> list[tuple[int, int]]:
    edges = []
    for i in range(12):
        for jump in (-2, -1, 1, 2):
            src = offset + i
            dst = offset + ((i + jump) % 12)
            edges.append((dst, src) if reverse else (src, dst))
    return sorted(set(edges))


def ring_grid_score(theta: np.ndarray, offset: int, harmonic: int = 12) -> float:
    sub = theta[offset:offset + 12]
    return float(np.abs(np.mean(np.exp(1j * harmonic * sub))))


def circular_mean(theta: np.ndarray, offset: int) -> float:
    sub = theta[offset:offset + 12]
    return float(np.angle(np.mean(np.exp(1j * sub))))


def quadrature_score(theta: np.ndarray) -> float:
    delta = np.angle(np.exp(1j * (circular_mean(theta, 12) - circular_mean(theta, 0))))
    return float(0.5 * (1.0 + np.cos(2.0 * (delta - np.pi / 2.0))))


def apply_ring_local_event_impulse(theta: np.ndarray, event: dict[str, float]) -> np.ndarray:
    n_nodes = len(theta)
    target = int(event["target"]) % n_nodes
    strength = float(event["strength"])
    if n_nodes >= 24:
        ring_offset = 12 if target >= 12 else 0
        local = target - ring_offset
        grid = 2.0 * np.pi * np.arange(12) / 12.0
        target_phase = np.roll(grid, local)
        out = theta.copy()
        sl = slice(ring_offset, ring_offset + 12)
        out[sl] = np.mod((1.0 - strength) * out[sl] + strength * target_phase, 2.0 * np.pi)
        return out
    grid = 2.0 * np.pi * np.arange(n_nodes) / n_nodes
    target_phase = np.roll(grid, target)
    return np.mod((1.0 - strength) * theta + strength * target_phase, 2.0 * np.pi)


def enforce_quadrature(theta: np.ndarray, strength: float) -> np.ndarray:
    if len(theta) < 24 or strength <= 0:
        return theta
    desired = circular_mean(theta, 0) + np.pi / 2.0
    current = circular_mean(theta, 12)
    correction = np.angle(np.exp(1j * (desired - current)))
    out = theta.copy()
    out[12:24] = np.mod(out[12:24] + strength * correction, 2.0 * np.pi)
    return out


def simulate_quadrature_conditioned(
    n_nodes: int,
    edges: list[tuple[int, int]],
    event_schedule: list[dict[str, float]],
    seed: int,
    steps: int,
    dt: float = 0.06,
    coupling: float = 0.34,
    second_harmonic: float = 0.04,
    recovery_window: int = 18,
    regulatory_strength: float = 0.0,
) -> dict[str, float]:
    b3 = b73a.load_module("b3_quad_custom", SCRIPTS / "test_Stage_B3_endogenous_event_carrier_readout.py")
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0.0, 2.0 * np.pi, size=n_nodes)
    omega = rng.normal(0.0, 0.012, size=n_nodes)
    incoming = [[] for _ in range(n_nodes)]
    for i, j in edges:
        incoming[j].append(i)
    by_step: dict[int, list[dict[str, float]]] = {}
    for event in event_schedule:
        by_step.setdefault(int(event["step"]), []).append(event)
    q_series = []
    r1_series = []
    r2_series = []
    joint_series = []
    for t in range(steps):
        for event in by_step.get(t, []):
            theta = apply_ring_local_event_impulse(theta, event)
        delta = np.array(omega, dtype=float)
        for j in range(n_nodes):
            if not incoming[j]:
                continue
            diffs = theta[incoming[j]] - theta[j]
            delta[j] += coupling * float(np.mean(np.sin(diffs)))
            delta[j] += second_harmonic * float(np.mean(np.sin(2.0 * diffs)))
        theta = np.mod(theta + dt * delta, 2.0 * np.pi)
        theta = enforce_quadrature(theta, regulatory_strength)
        if n_nodes >= 24:
            r1 = ring_grid_score(theta, 0)
            r2 = ring_grid_score(theta, 12)
            q = quadrature_score(theta)
            r1_series.append(r1)
            r2_series.append(r2)
            q_series.append(q)
            joint_series.append(float(np.sqrt(max(r1, 0.0) * max(r2, 0.0)) * q))
        else:
            r = ring_grid_score(theta, 0)
            r1_series.append(r)
            r2_series.append(np.nan)
            q_series.append(np.nan)
            joint_series.append(r)
    event_steps = sorted({int(x["step"]) for x in event_schedule if 0 <= int(x["step"]) < steps})
    improvements = []
    post_joint = []
    post_q = []
    post_r1 = []
    post_r2 = []
    for step in event_steps:
        pre_start = max(0, step - recovery_window)
        post_end = min(steps, step + recovery_window + 1)
        if step <= pre_start or post_end <= step + 1:
            continue
        improvements.append(float(np.mean(joint_series[step + 1:post_end]) - np.mean(joint_series[pre_start:step])))
        post_joint.append(float(np.mean(joint_series[step + 1:post_end])))
        post_q.append(float(np.nanmean(q_series[step + 1:post_end])))
        post_r1.append(float(np.nanmean(r1_series[step + 1:post_end])))
        post_r2.append(float(np.nanmean(r2_series[step + 1:post_end])))
    if not improvements:
        return {"quadrature_recovery": np.nan, "post_joint": np.nan, "post_quadrature": np.nan, "post_ring1": np.nan, "post_ring2": np.nan}
    return {
        "quadrature_recovery": float(np.mean(improvements)),
        "post_joint": float(np.mean(post_joint)),
        "post_quadrature": float(np.nanmean(post_q)),
        "post_ring1": float(np.nanmean(post_r1)),
        "post_ring2": float(np.nanmean(post_r2)),
    }


def paired_c12_edges(cross: str = "none", reverse_second: bool = False) -> list[tuple[int, int]]:
    edges = c12_edges(0) + c12_edges(12, reverse=reverse_second)
    if cross == "identity":
        edges += [(i, i + 12) for i in range(12)] + [(i + 12, i) for i in range(12)]
    elif cross == "quadrature":
        edges += [(i, 12 + ((i + 3) % 12)) for i in range(12)]
        edges += [(12 + i, (i + 3) % 12) for i in range(12)]
    elif cross == "broken":
        edges += [(i, 12 + ((i + 5) % 12)) for i in range(12)]
        edges += [(12 + i, (i + 7) % 12) for i in range(12)]
    return sorted(set(edges))


def paired_schedule(rows: pd.DataFrame, steps: int, phase_offset_quarters: int, strength_ratio: float = 1.0) -> tuple[list[dict[str, float]], dict[str, float]]:
    single, meta = b73a.build_event_schedule(rows, steps, 12)
    schedule = []
    for item in single:
        target = int(item["target"]) % 12
        schedule.append({**item, "target": target, "ordinal": 2 * int(item["ordinal"])})
        schedule.append({
            **item,
            "target": 12 + ((target + 3 * phase_offset_quarters) % 12),
            "strength": float(item["strength"]) * strength_ratio,
            "ordinal": 2 * int(item["ordinal"]) + 1,
        })
    meta = dict(meta)
    meta["n_events"] = len(schedule)
    return schedule, meta


def topology_and_schedule(name: str, events: pd.DataFrame, args: argparse.Namespace, rng: np.random.Generator):
    if name == "single_c12":
        n, edges, notes = b73a.topology_edges("c12_1_2", rng)
        schedule, meta = b73a.build_event_schedule(events, args.steps, n)
        return n, edges, schedule, meta, "single C12(1,2)", 0.0
    if name == "paired_c12_90":
        schedule, meta = paired_schedule(events, args.steps, 1)
        return 24, paired_c12_edges("none"), schedule, meta, "two separate C12 rings, second event stream +90 degrees", 0.0
    if name == "paired_c12_90_regulated":
        schedule, meta = paired_schedule(events, args.steps, 1)
        return 24, paired_c12_edges("none"), schedule, meta, "two separate C12 rings plus weak regulatory enforcement of +90 mean phase", args.regulatory_strength
    if name == "regulation_only_90":
        schedule, meta = paired_schedule(events, args.steps, 1)
        return 24, [], schedule, meta, "no architecture edges; weak regulatory enforcement of +90 mean phase only", args.regulatory_strength
    if name == "paired_c12_0":
        schedule, meta = paired_schedule(events, args.steps, 0)
        return 24, paired_c12_edges("none"), schedule, meta, "two separate C12 rings, second event stream +0 degrees", 0.0
    if name == "paired_c12_45_proxy":
        schedule, meta = paired_schedule(events, args.steps, 0)
        for j, item in enumerate(schedule):
            if j % 2 == 1:
                item["strength"] *= 0.5
                item["target"] = 12 + ((int(item["target"]) - 12 + 1) % 12)
        return 24, paired_c12_edges("none"), schedule, meta, "two C12 rings, coarse +45-degree proxy by half-strength one-node offset", 0.0
    if name == "paired_c12_180":
        schedule, meta = paired_schedule(events, args.steps, 2)
        return 24, paired_c12_edges("none"), schedule, meta, "two separate C12 rings, second event stream +180 degrees", 0.0
    if name == "paired_c12_90_cross_coupled":
        schedule, meta = paired_schedule(events, args.steps, 1)
        return 24, paired_c12_edges("quadrature"), schedule, meta, "two C12 rings plus quadrature cross-coupling edges", 0.0
    if name == "paired_c12_90_cross_regulated":
        schedule, meta = paired_schedule(events, args.steps, 1)
        return 24, paired_c12_edges("quadrature"), schedule, meta, "quadrature cross-coupling plus weak regulatory enforcement of +90 mean phase", args.regulatory_strength
    if name == "paired_c12_90_identity_coupled":
        schedule, meta = paired_schedule(events, args.steps, 1)
        return 24, paired_c12_edges("identity"), schedule, meta, "two C12 rings plus same-phase identity cross-coupling", 0.0
    if name == "paired_c12_90_broken_factor12":
        schedule, meta = paired_schedule(events, args.steps, 1)
        return 24, paired_c12_edges("broken"), schedule, meta, "two C12 rings with non-quadrature broken cross-coupling", 0.0
    if name == "paired_c12_90_reversed_second":
        schedule, meta = paired_schedule(events, args.steps, 1)
        return 24, paired_c12_edges("none", reverse_second=True), schedule, meta, "two C12 rings, second ring reversed, +90 event stream", 0.0
    if name == "h24_edge_suite":
        n, edges, notes = b73a.topology_edges("h24_possible_factorisations_168", rng)
        schedule, meta = b73a.build_event_schedule(events, args.steps, n)
        return n, edges, schedule, meta, notes, 0.0
    raise ValueError(name)


def simulate_one(n_nodes: int, edges: list[tuple[int, int]], schedule: list[dict[str, float]], regulatory_strength: float, args: argparse.Namespace, rng: np.random.Generator) -> np.ndarray:
    values = []
    for _ in range(args.n_runs):
        if args.endpoint == "quadrature":
            metric = simulate_quadrature_conditioned(n_nodes, edges, schedule, int(rng.integers(0, 2**31 - 1)), args.steps, regulatory_strength=regulatory_strength)
            values.append(metric.get("quadrature_recovery", np.nan))
        else:
            metric = b73a.load_module("b3_quad_prescreen", SCRIPTS / "test_Stage_B3_endogenous_event_carrier_readout.py").simulate_event_conditioned(
                n_nodes,
                edges,
                schedule,
                int(rng.integers(0, 2**31 - 1)),
                steps=args.steps,
            )
            values.append(metric.get("differentiated_recovery", np.nan))
    return np.asarray(values, dtype=float)


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    features = add_phi_candidates(b73a.load_b72_features(args))
    reps = [x.strip() for x in args.reps.split(",") if x.strip()]
    topologies = [
        "single_c12",
        "paired_c12_90",
        "paired_c12_90_regulated",
        "regulation_only_90",
        "paired_c12_0",
        "paired_c12_45_proxy",
        "paired_c12_180",
        "paired_c12_90_cross_coupled",
        "paired_c12_90_cross_regulated",
        "paired_c12_90_identity_coupled",
        "paired_c12_90_broken_factor12",
        "paired_c12_90_reversed_second",
        "h24_edge_suite",
    ]
    rng = np.random.default_rng(args.seed + 124)
    rows = []
    for rep in reps:
        events = b73a.event_rows_for_rep(features, rep, args.event_quantile)
        for topo in topologies:
            n_nodes, edges, schedule, meta, notes, regulatory_strength = topology_and_schedule(topo, events, args, rng)
            values = simulate_one(n_nodes, edges, schedule, regulatory_strength, args, rng)
            rows.append({
                "c_representation": rep,
                "topology_arm": topo,
                "n_nodes": n_nodes,
                "n_directed_edges": len(edges),
                "n_seed_events": meta["n_events"],
                "mean_bounded_differentiated_recovery": float(np.nanmean(values)),
                "sd_bounded_differentiated_recovery": float(np.nanstd(values)),
                "topology_notes": notes,
            })
    results = pd.DataFrame(rows)
    lookup = results.set_index(["c_representation", "topology_arm"])["mean_bounded_differentiated_recovery"].to_dict()
    controls = [
        "single_c12",
        "paired_c12_0",
        "paired_c12_90_regulated",
        "regulation_only_90",
        "paired_c12_45_proxy",
        "paired_c12_180",
        "paired_c12_90_identity_coupled",
        "paired_c12_90_cross_regulated",
        "paired_c12_90_broken_factor12",
        "paired_c12_90_reversed_second",
        "h24_edge_suite",
    ]
    paired90 = results[results["topology_arm"].eq("paired_c12_90")].copy()
    for ctrl in controls:
        paired90[f"effect_vs_{ctrl}"] = [
            row.mean_bounded_differentiated_recovery - lookup.get((row.c_representation, ctrl), np.nan)
            for row in paired90.itertuples(index=False)
        ]
    effect_cols = [f"effect_vs_{ctrl}" for ctrl in controls]
    paired90["n_positive_controls"] = paired90[effect_cols].gt(0).sum(axis=1)
    paired90["min_control_margin"] = paired90[effect_cols].min(axis=1)
    paired90 = paired90.sort_values(["n_positive_controls", "mean_bounded_differentiated_recovery"], ascending=[False, False])

    results.to_csv(outdir / "private_B7_4_quadrature_phi12_results.csv", index=False)
    paired90.to_csv(outdir / "private_B7_4_quadrature_phi12_paired90_ranking.csv", index=False)
    print(f"output_dir: {outdir}")
    print("\nPaired C12 +90 ranking")
    print(paired90[[
        "c_representation",
        "mean_bounded_differentiated_recovery",
        *effect_cols,
        "n_positive_controls",
        "min_control_margin",
    ]].to_string(index=False))
    print("\nAll means")
    print(results.pivot(index="c_representation", columns="topology_arm", values="mean_bounded_differentiated_recovery").round(6).to_string())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_4/quadrature_phi12")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--event-quantile", type=float, default=0.75)
    parser.add_argument("--steps", type=int, default=140)
    parser.add_argument("--n-runs", type=int, default=10)
    parser.add_argument("--seed", type=int, default=74124)
    parser.add_argument("--reps", type=str, default="phi_eigen_energy_c,phi_differential_invariant_c,receiver_only_c")
    parser.add_argument("--endpoint", choices=["legacy", "quadrature"], default="quadrature")
    parser.add_argument("--regulatory-strength", type=float, default=0.22)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
