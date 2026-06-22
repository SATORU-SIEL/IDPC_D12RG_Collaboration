#!/usr/bin/env python3
"""Stage B7.4a Hadamard-quadrature vs irreducible 3-fold closure audit."""

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


SQRT2 = float(np.sqrt(2.0))


def unique_edges(n_nodes: int, jumps: tuple[int, ...]) -> list[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for i in range(n_nodes):
        for jump in jumps:
            j = (i + jump) % n_nodes
            if i != j:
                edges.add((i, j))
    return sorted(edges)


def scaled_schedule(schedule: list[dict[str, float]], scale: float) -> list[dict[str, float]]:
    return [{**item, "strength": float(item["strength"]) * scale} for item in schedule]


def topology_arm(name: str, rng: np.random.Generator) -> tuple[int, list[tuple[int, int]], str, float]:
    """Return n_nodes, edges, notes, event strength scale.

    Operational convention:
    - Hadamard/quadrature-only is represented by the 4-cycle generators on Z12:
      quarter-turn +/-3 and sign flip 6.
    - Explicit 3-fold availability adds the cube-root / 120-degree generator +/-4.
    - Broken 3-fold uses a neighboring non-cube-root generator to test generic added structure.
    """
    if name == "no_topology_baseline":
        return 12, [], "12 nodes with no coupling edges", 1.0
    if name == "c12_1_2":
        n, edges, notes = b73a.topology_edges("c12_1_2", rng)
        return n, edges, notes, 1.0
    if name == "c12_reversed":
        n, edges, _ = b73a.topology_edges("c12_1_2", rng)
        return n, sorted((j, i) for i, j in edges), "C12(1,2) reversed", 1.0
    if name == "c12_side_broken":
        return (*b73a.topology_edges("c12_side_broken", rng), 1.0)
    if name == "c12_shuffled":
        return (*b73a.topology_edges("c12_shuffled", rng), 1.0)
    if name in {"c10", "c11", "c13", "c14"}:
        return (*b73a.topology_edges(name, rng), 1.0)
    if name == "hadamard_quadrature_only":
        return 12, unique_edges(12, (-6, -3, 3, 6)), "Hadamard/quadrature-only 4-cycle generators on Z12: +/-3 and 6", 1.0
    if name == "hadamard_quadrature_sqrt2_scaled_out":
        return 12, unique_edges(12, (-6, -3, 3, 6)), "Hadamard/quadrature-only with sqrt2 normalization scaled out", 1.0 / SQRT2
    if name == "hadamard_quadrature_sqrt2_unscaled":
        return 12, unique_edges(12, (-6, -3, 3, 6)), "Hadamard/quadrature-only with unnormalized sqrt2 gain retained", SQRT2
    if name == "hadamard_plus_threefold":
        return 12, unique_edges(12, (-6, -4, -3, 3, 4, 6)), "Hadamard 4-cycle plus explicit radix-3 / 120-degree generator +/-4", 1.0
    if name == "hadamard_plus_threefold_sqrt2_scaled_out":
        return 12, unique_edges(12, (-6, -4, -3, 3, 4, 6)), "Hadamard plus explicit 3-fold with sqrt2 normalization scaled out", 1.0 / SQRT2
    if name == "threefold_only":
        return 12, unique_edges(12, (-4, 4)), "explicit radix-3 / 120-degree generator only", 1.0
    if name == "broken_threefold_neighbor":
        return 12, unique_edges(12, (-6, -5, -3, 3, 5, 6)), "Hadamard plus neighboring non-cube-root generator +/-5", 1.0
    if name == "broken_threefold_random":
        _, c_edges, _ = b73a.topology_edges("c12_1_2", rng)
        return 12, b73a.load_module("b3_for_b74a", SCRIPTS / "test_Stage_B3_endogenous_event_carrier_readout.py").degree_matched_random_edges(12, c_edges, rng), "degree-matched random C12 control", 1.0
    raise ValueError(f"unknown topology arm {name}")


def simulate_values(
    n_nodes: int,
    edges: list[tuple[int, int]],
    schedule: list[dict[str, float]],
    args: argparse.Namespace,
    rng: np.random.Generator,
) -> np.ndarray:
    b3 = b73a.load_module("b3_sim_for_b74a", SCRIPTS / "test_Stage_B3_endogenous_event_carrier_readout.py")
    values = []
    for _ in range(args.n_runs):
        metric = b3.simulate_event_conditioned(n_nodes, edges, schedule, int(rng.integers(0, 2**31 - 1)), steps=args.steps)
        values.append(metric.get("differentiated_recovery", np.nan))
    return np.asarray(values, dtype=float)


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed + 744)
    features = add_phi_candidates(b73a.load_b72_features(args))
    reps = [x.strip() for x in args.reps.split(",") if x.strip()]
    arms = [
        "no_topology_baseline",
        "c12_1_2",
        "c12_reversed",
        "c12_side_broken",
        "c12_shuffled",
        "c10",
        "c11",
        "c13",
        "c14",
        "hadamard_quadrature_only",
        "hadamard_quadrature_sqrt2_scaled_out",
        "hadamard_quadrature_sqrt2_unscaled",
        "hadamard_plus_threefold",
        "hadamard_plus_threefold_sqrt2_scaled_out",
        "threefold_only",
        "broken_threefold_neighbor",
        "broken_threefold_random",
    ]
    rows = []
    for rep in reps:
        events = b73a.event_rows_for_rep(features, rep, args.event_quantile)
        base_schedule, meta = b73a.build_event_schedule(events, args.steps, 12)
        shifted_base = b73a.shifted_schedule(base_schedule, args.steps, max(7, args.steps // 5))
        random_base = b73a.random_schedule(base_schedule, args.steps, rng)
        for arm in arms:
            n_nodes, edges, notes, scale = topology_arm(arm, rng)
            schedule = scaled_schedule(base_schedule, scale)
            shifted = scaled_schedule(shifted_base, scale)
            random_event = scaled_schedule(random_base, scale)
            obs_values = simulate_values(n_nodes, edges, schedule, args, rng)
            shifted_values = simulate_values(n_nodes, edges, shifted, args, rng)
            random_values = simulate_values(n_nodes, edges, random_event, args, rng)
            obs = float(np.nanmean(obs_values))
            rows.append({
                "c_representation": rep,
                "topology_arm": arm,
                "n_nodes": n_nodes,
                "n_directed_edges": len(edges),
                "n_seed_events": meta.get("n_events", len(schedule)),
                "event_strength_scale": scale,
                "mean_bounded_differentiated_recovery": obs,
                "sd_bounded_differentiated_recovery": float(np.nanstd(obs_values)),
                "effect_vs_time_shifted": obs - float(np.nanmean(shifted_values)),
                "effect_vs_random_event": obs - float(np.nanmean(random_values)),
                "p_vs_time_shifted_and_random": b73a.p_greater(obs, np.r_[shifted_values, random_values]),
                "topology_notes": notes,
            })
    results = pd.DataFrame(rows)
    lookup = results.set_index(["c_representation", "topology_arm"])["mean_bounded_differentiated_recovery"].to_dict()
    decision_rows = []
    controls = [
        "no_topology_baseline",
        "c12_reversed",
        "c12_side_broken",
        "c12_shuffled",
        "c10",
        "c11",
        "c13",
        "c14",
        "broken_threefold_neighbor",
        "broken_threefold_random",
    ]
    for rep in reps:
        h = lookup.get((rep, "hadamard_quadrature_only"), np.nan)
        h3 = lookup.get((rep, "hadamard_plus_threefold"), np.nan)
        h2out = lookup.get((rep, "hadamard_quadrature_sqrt2_scaled_out"), np.nan)
        c12 = lookup.get((rep, "c12_1_2"), np.nan)
        row = {
            "c_representation": rep,
            "hadamard_only_mean": h,
            "hadamard_plus_threefold_mean": h3,
            "c12_mean": c12,
            "threefold_gain_over_hadamard": h3 - h,
            "sqrt2_scaled_out_effect": h2out - h,
        }
        for ctrl in controls:
            row[f"hadamard_plus_threefold_vs_{ctrl}"] = h3 - lookup.get((rep, ctrl), np.nan)
        ctrl_cols = [f"hadamard_plus_threefold_vs_{ctrl}" for ctrl in controls]
        row["threefold_positive_specificity_controls"] = int(sum(row[col] > 0 for col in ctrl_cols if np.isfinite(row[col])))
        row["threefold_min_specificity_margin"] = float(np.nanmin([row[col] for col in ctrl_cols]))
        decision_rows.append(row)
    decisions = pd.DataFrame(decision_rows).sort_values(
        ["threefold_positive_specificity_controls", "threefold_gain_over_hadamard", "hadamard_plus_threefold_mean"],
        ascending=[False, False, False],
    )
    results.to_csv(outdir / "Stage_B7_4a_hadamard_threefold_results.csv", index=False)
    decisions.to_csv(outdir / "Stage_B7_4a_hadamard_threefold_decision_table.csv", index=False)
    write_summary(outdir / "Stage_B7_4a_execution_summary.md", results, decisions, args)
    print(f"output_dir: {outdir}")
    print("\nDecision table")
    print(decisions.to_string(index=False))
    print("\nTop means")
    print(results.sort_values("mean_bounded_differentiated_recovery", ascending=False).head(20)[[
        "c_representation", "topology_arm", "mean_bounded_differentiated_recovery", "effect_vs_time_shifted", "effect_vs_random_event", "p_vs_time_shifted_and_random"
    ]].to_string(index=False))


def write_summary(path: Path, results: pd.DataFrame, decisions: pd.DataFrame, args: argparse.Namespace) -> None:
    top = results.sort_values("mean_bounded_differentiated_recovery", ascending=False).head(16)
    lines = [
        "# Stage B7.4a Hadamard-Quadrature vs Irreducible 3-Fold Closure Audit",
        "",
        "Status: executed after `Stage_B7_4a_preregistration_email_sent.md`.",
        "",
        "## Decision Table",
        "",
        decisions.to_csv(index=False).strip(),
        "",
        "## Top Means",
        "",
        top[[
            "c_representation",
            "topology_arm",
            "mean_bounded_differentiated_recovery",
            "effect_vs_time_shifted",
            "effect_vs_random_event",
            "p_vs_time_shifted_and_random",
        ]].to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- event_quantile: {args.event_quantile}",
        f"- steps: {args.steps}",
        f"- n_runs: {args.n_runs}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_4a")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--event-quantile", type=float, default=0.75)
    parser.add_argument("--steps", type=int, default=180)
    parser.add_argument("--n-runs", type=int, default=24)
    parser.add_argument("--seed", type=int, default=74412)
    parser.add_argument("--reps", type=str, default="receiver_only_c,receiver_standpoint_magnitude_c,phi_eigen_energy_c,phi_differential_invariant_c")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
