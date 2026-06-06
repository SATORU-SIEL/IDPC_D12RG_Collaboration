#!/usr/bin/env python3
"""Stage B2 topology-aware carrier audit.

This script implements an exploratory topology-aware audit for IDPC x D12RG
Stage B2. It keeps IDPC-derived Ricci / eps72 outputs as context readouts and
tests explicit directed topology families with fixed simulation and null
controls. It does not implement Stage C and does not claim carrier
confirmation.
"""

from __future__ import annotations

import argparse
import math
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd


PRIMARY_TOPOLOGIES = {"C12(1,2)", "C8(1)"}
PRIMARY_CONDITIONS = {("C12(1,2)", "unseeded"), ("C8(1)", "unseeded"), ("C8(1)", "seeded")}


def bh_fdr(p_values: list[float]) -> list[float]:
    p = np.asarray(p_values, dtype=float)
    q = np.full_like(p, np.nan)
    valid = np.isfinite(p)
    if not valid.any():
        return q.tolist()
    pv = p[valid]
    order = np.argsort(pv)
    ranked = pv[order]
    n = len(ranked)
    ranked_q = ranked * n / np.arange(1, n + 1)
    ranked_q = np.minimum.accumulate(ranked_q[::-1])[::-1]
    out = np.empty_like(ranked_q)
    out[order] = np.clip(ranked_q, 0.0, 1.0)
    q[valid] = out
    return q.tolist()


def unique_edges(n_nodes: int, jumps: tuple[int, ...]) -> list[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for i in range(n_nodes):
        for jump in jumps:
            j = (i + jump) % n_nodes
            if i != j:
                edges.add((i, j))
    return sorted(edges)


def ring_topology(name: str) -> tuple[str, int, list[tuple[int, int]], str, str]:
    if name == "C8(1)":
        return "standalone Cn(k) directed rings", 8, unique_edges(8, (1,)), "directed clockwise 1-jump", "jump-start-dependent contrast"
    if name == "C12(1)":
        return "standalone Cn(k) directed rings", 12, unique_edges(12, (1,)), "directed clockwise 1-jump", "standalone D12 ring contrast"
    if name == "C6(1,2)":
        return "standalone Cn(k) directed rings", 6, unique_edges(6, (-2, -1, 1, 2)), "bidirectional 1-jump and 2-jump", "lower-order 2-through-12 candidate"
    if name == "C8(1,2)":
        return "standalone Cn(k) directed rings", 8, unique_edges(8, (-2, -1, 1, 2)), "bidirectional 1-jump and 2-jump", "lower/intermediate Phi8-native candidate"
    if name == "C12(1,2)":
        return "standalone Cn(k) directed rings", 12, unique_edges(12, (-2, -1, 1, 2)), "bidirectional 1-jump and 2-jump; 48 directed arrows", "primary held-out carrier candidate"
    raise ValueError(f"unknown ring topology: {name}")


def cuboctahedron_topology() -> tuple[str, int, list[tuple[int, int]], str, str]:
    # Vertices are sign/permutation positions with one coordinate 0 and two
    # coordinates +/-1. Edges connect Euclidean distance sqrt(2), then doubled.
    verts: list[tuple[int, int, int]] = []
    for zero_idx in range(3):
        for a in (-1, 1):
            for b in (-1, 1):
                coord = [0, 0, 0]
                nonzero = [idx for idx in range(3) if idx != zero_idx]
                coord[nonzero[0]] = a
                coord[nonzero[1]] = b
                verts.append(tuple(coord))
    undirected = []
    for i, vi in enumerate(verts):
        for j, vj in enumerate(verts):
            if i < j:
                dist2 = sum((vi[k] - vj[k]) ** 2 for k in range(3))
                if dist2 == 2:
                    undirected.append((i, j))
    return directed_from_undirected("cuboctahedral / atom-like flattened structures", len(verts), undirected, "bidirected cuboctahedron edges", "higher-order polyhedral candidate")


def dodecahedron_topology() -> tuple[str, int, list[tuple[int, int]], str, str]:
    # NetworkX-free dodecahedral graph in LCF notation [10,7,4,-4,-7,10,-4,7,-7,4]^2.
    n = 20
    shifts = [10, 7, 4, -4, -7, 10, -4, 7, -7, 4] * 2
    undirected: set[tuple[int, int]] = set()
    for i in range(n):
        undirected.add(tuple(sorted((i, (i + 1) % n))))
        undirected.add(tuple(sorted((i, (i + shifts[i]) % n))))
    return directed_from_undirected("dodecahedral topology", n, sorted(undirected), "bidirected LCF dodecahedron edges", "higher-order fivefold/D12/D24 candidate")


def icosahedron_topology() -> tuple[str, int, list[tuple[int, int]], str, str]:
    # 12-vertex icosahedral graph: two poles plus two pentagonal rings.
    n = 12
    top = 0
    bottom = 11
    upper = list(range(1, 6))
    lower = list(range(6, 11))
    undirected: set[tuple[int, int]] = set()
    for i in range(5):
        undirected.add(tuple(sorted((top, upper[i]))))
        undirected.add(tuple(sorted((bottom, lower[i]))))
        undirected.add(tuple(sorted((upper[i], upper[(i + 1) % 5]))))
        undirected.add(tuple(sorted((lower[i], lower[(i + 1) % 5]))))
        undirected.add(tuple(sorted((upper[i], lower[i]))))
        undirected.add(tuple(sorted((upper[i], lower[(i - 1) % 5]))))
    return directed_from_undirected("icosahedral topology", n, sorted(undirected), "bidirected icosahedron edges", "higher-order fivefold local vertex candidate")


def directed_from_undirected(
    topology_class: str,
    n_nodes: int,
    undirected_edges: list[tuple[int, int]],
    convention: str,
    notes: str,
) -> tuple[str, int, list[tuple[int, int]], str, str]:
    edges = []
    for i, j in undirected_edges:
        if i != j:
            edges.append((i, j))
            edges.append((j, i))
    return topology_class, n_nodes, sorted(set(edges)), convention, notes


def topology_definition(name: str) -> tuple[str, int, list[tuple[int, int]], str, str]:
    if name.startswith("C"):
        return ring_topology(name)
    if name == "cuboctahedron":
        return cuboctahedron_topology()
    if name == "dodecahedron":
        return dodecahedron_topology()
    if name == "icosahedron":
        return icosahedron_topology()
    raise ValueError(name)


def adjacency(n_nodes: int, edges: list[tuple[int, int]]) -> np.ndarray:
    a = np.zeros((n_nodes, n_nodes), dtype=float)
    for i, j in edges:
        a[i, j] = 1.0
    return a


def degree_matched_random_edges(
    n_nodes: int,
    edges: list[tuple[int, int]],
    rng: np.random.Generator,
    max_attempts: int = 500,
) -> list[tuple[int, int]]:
    out_stubs = [i for i, _ in edges]
    in_stubs = [j for _, j in edges]
    for _ in range(max_attempts):
        targets = np.array(in_stubs, dtype=int)
        rng.shuffle(targets)
        candidate = [(out_stubs[k], int(targets[k])) for k in range(len(out_stubs))]
        if all(i != j for i, j in candidate) and len(set(candidate)) == len(candidate):
            return sorted(candidate)
    # Fallback preserves out-degree exactly and edge count approximately.
    out_degree = {i: 0 for i in range(n_nodes)}
    for i, _ in edges:
        out_degree[i] += 1
    candidate: set[tuple[int, int]] = set()
    for i, deg in out_degree.items():
        choices = [j for j in range(n_nodes) if j != i]
        for j in rng.choice(choices, size=min(deg, len(choices)), replace=False):
            candidate.add((i, int(j)))
    return sorted(candidate)


def initial_phases(n_nodes: int, condition: str, rng: np.random.Generator) -> np.ndarray:
    if condition == "unseeded":
        return rng.uniform(0.0, 2.0 * np.pi, size=n_nodes)
    if condition == "seeded":
        grid = 2.0 * np.pi * np.arange(n_nodes) / n_nodes
        return np.mod(grid + rng.normal(0.0, 0.04, size=n_nodes), 2.0 * np.pi)
    raise ValueError(condition)


def simulate(
    n_nodes: int,
    edges: list[tuple[int, int]],
    condition: str,
    seed: int,
    steps: int = 240,
    dt: float = 0.06,
    coupling: float = 0.34,
    second_harmonic: float = 0.04,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    theta = initial_phases(n_nodes, condition, rng)
    omega = rng.normal(0.0, 0.012, size=n_nodes)
    incoming = [[] for _ in range(n_nodes)]
    for i, j in edges:
        incoming[j].append(i)
    order = []
    velocity_norm = []
    d12_scores = []
    d24_scores = []
    diff_scores = []
    for t in range(steps):
        delta = np.array(omega, dtype=float)
        for j in range(n_nodes):
            if not incoming[j]:
                continue
            diffs = theta[incoming[j]] - theta[j]
            delta[j] += coupling * float(np.mean(np.sin(diffs)))
            delta[j] += second_harmonic * float(np.mean(np.sin(2.0 * diffs)))
        theta = np.mod(theta + dt * delta, 2.0 * np.pi)
        if t >= steps // 2:
            order.append(order_parameter(theta, 1))
            velocity_norm.append(float(np.linalg.norm(dt * delta) / max(1, n_nodes)))
            d12_scores.append(grid_score(theta, 12))
            d24_scores.append(grid_score(theta, 24))
            diff_scores.append(differentiation_score(theta, 12))
    late_slice = slice(max(0, len(order) - steps // 6), len(order))
    late_lock = float(np.mean(order[late_slice])) if order else np.nan
    early_lock = float(np.mean(order[: max(1, len(order) // 3)])) if order else np.nan
    late_d12 = float(np.mean(np.asarray(d12_scores)[late_slice])) if d12_scores else np.nan
    late_d24 = float(np.mean(np.asarray(d24_scores)[late_slice])) if d24_scores else np.nan
    late_diff = float(np.mean(np.asarray(diff_scores)[late_slice])) if diff_scores else np.nan
    late_vel = float(np.mean(np.asarray(velocity_norm)[late_slice])) if velocity_norm else np.nan
    bounded = float(np.clip(1.0 - late_vel / 0.04, 0.0, 1.0)) if np.isfinite(late_vel) else np.nan
    transient_score = float(max(0.0, early_lock - late_lock)) if np.isfinite(early_lock) and np.isfinite(late_lock) else np.nan
    transient_duration = transient_window(order, threshold=0.55)
    return {
        "locking_strength": late_lock,
        "D12_score": late_d12,
        "D24_score": late_d24,
        "late_window_stability": stability_score(order),
        "perturbation_stability": np.nan,
        "transient_score": transient_score,
        "transient_duration": transient_duration,
        "bounded_non_runaway_score": bounded,
        "non_collapsed_differentiation_score": late_diff,
    }


def order_parameter(theta: np.ndarray, harmonic: int) -> float:
    return float(abs(np.mean(np.exp(1j * harmonic * theta))))


def grid_score(theta: np.ndarray, period: int) -> float:
    step = 2.0 * np.pi / period
    residual = np.mod(theta + step / 2.0, step) - step / 2.0
    return float(np.clip(1.0 - np.mean(np.abs(residual)) / (step / 2.0), 0.0, 1.0))


def differentiation_score(theta: np.ndarray, bins: int) -> float:
    counts = np.bincount(np.floor(np.mod(theta, 2.0 * np.pi) / (2.0 * np.pi) * bins).astype(int), minlength=bins)
    p = counts[counts > 0] / max(1, np.sum(counts))
    entropy = -float(np.sum(p * np.log(p))) / math.log(bins)
    occupied = float(np.count_nonzero(counts)) / bins
    return float(np.clip(0.5 * entropy + 0.5 * occupied, 0.0, 1.0))


def stability_score(values: list[float]) -> float:
    arr = np.asarray(values, dtype=float)
    if len(arr) < 4:
        return np.nan
    tail = arr[-max(4, len(arr) // 3):]
    return float(np.clip(1.0 - np.std(tail) / 0.15, 0.0, 1.0))


def transient_window(values: list[float], threshold: float) -> float:
    longest = 0
    current = 0
    for value in values:
        if value >= threshold:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return float(longest)


def shortest_path_coverage(n_nodes: int, edges: list[tuple[int, int]], max_len: int = 24) -> tuple[int, int, bool]:
    adj = [[] for _ in range(n_nodes)]
    for i, j in edges:
        adj[i].append(j)
    lengths: set[int] = set()
    for src in range(n_nodes):
        queue = deque([(src, 0)])
        seen = {(src, 0)}
        while queue:
            node, depth = queue.popleft()
            if depth >= max_len:
                continue
            for nxt in adj[node]:
                nd = depth + 1
                if nd >= 2:
                    lengths.add(nd)
                state = (nxt, nd)
                if state not in seen:
                    seen.add(state)
                    queue.append(state)
    present = sorted(x for x in lengths if 2 <= x <= max_len)
    if not present:
        return 0, 0, False
    return min(present), max(present), all(x in lengths for x in range(2, 25))


def five_ten_loop_notes(n_nodes: int, edges: list[tuple[int, int]]) -> str:
    _, _, support = shortest_path_coverage(n_nodes, edges, 24)
    adj = adjacency(n_nodes, edges)
    a5 = np.linalg.matrix_power(adj, 5)
    a10 = np.linalg.matrix_power(adj, 10)
    loops5 = int(np.trace(a5))
    loops10 = int(np.trace(a10))
    if loops5 or loops10:
        return f"closed walks: length5={loops5}, length10={loops10}; transience interpreted separately from primary carrier test"
    if support:
        return "2-through-24 path coverage present, but no length-5/10 closed-walk trace under this convention"
    return "no explicit 5/10 loop support under this convention"


def topology_inventory_rows(topology_names: list[str]) -> pd.DataFrame:
    rows = []
    for name in topology_names:
        topology_class, n_nodes, edges, convention, notes = topology_definition(name)
        loop_min, loop_max, support_2_24 = shortest_path_coverage(n_nodes, edges, 24)
        rows.append({
            "topology_class": topology_class,
            "topology_name": name,
            "n_nodes": n_nodes,
            "n_directed_edges": len(edges),
            "edge_convention": convention,
            "loop_support_min": loop_min,
            "loop_support_max": loop_max,
            "supports_2_through_24_structural": support_2_24,
            "notes": notes,
            "five_ten_loop_notes": five_ten_loop_notes(n_nodes, edges),
        })
    return pd.DataFrame(rows)


def summarize_stage_b_context(input_dirs: list[Path]) -> pd.DataFrame:
    rows = []
    seen: set[Path] = set()
    for root in input_dirs:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.csv")):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            if path.name not in {
                "Stage_B_ricci_phase_sync_carrier_results.csv",
                "Stage_B_ricci_eps72_restoring_carrier_results.csv",
                "ricci_phase_sync_summary.csv",
                "ricci_eps72_restoring_test.csv",
                "event_level_with_fes_phase_TRUE_RICCI.csv",
            }:
                continue
            try:
                df = pd.read_csv(path)
            except Exception as exc:
                rows.append({"input_file": safe_path(path, root), "status": "read_error", "notes": str(exc)})
                continue
            rows.append({
                "input_file": safe_path(path, root),
                "status": "loaded",
                "n_rows": len(df),
                "n_columns": len(df.columns),
                "columns": "; ".join(map(str, df.columns[:40])),
                "notes": "IDPC-derived structural readout used as context, not direct carrier evidence",
            })
    return pd.DataFrame(rows)


def safe_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return path.name


def empirical_context_scores(stage_b_context: pd.DataFrame) -> dict[str, float]:
    scores = {"stage_b_context_loaded": float(len(stage_b_context))}
    return scores


def run_topology_audit(
    topology_names: list[str],
    n_runs: int,
    n_null: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    rows = []
    null_rows = []
    for topology_name in topology_names:
        topology_class, n_nodes, edges, convention, notes = topology_definition(topology_name)
        loop_min, loop_max, support_2_24 = shortest_path_coverage(n_nodes, edges, 24)
        null_metrics_by_condition: dict[str, list[float]] = {}
        for condition in ("unseeded", "seeded"):
            null_scores = []
            for null_idx in range(n_null):
                null_edges = degree_matched_random_edges(n_nodes, edges, rng)
                metrics_list = [simulate(n_nodes, null_edges, condition, int(rng.integers(0, 2**31 - 1))) for _ in range(max(1, n_runs // 2))]
                score = float(np.nanmean([carrier_score(m) for m in metrics_list]))
                null_scores.append(score)
                null_rows.append({
                    "topology_name": topology_name,
                    "condition": condition,
                    "null_index": null_idx,
                    "n_nodes": n_nodes,
                    "n_directed_edges": len(null_edges),
                    "null_model": "degree-matched directed random graph",
                    "carrier_score": score,
                })
            null_metrics_by_condition[condition] = null_scores
            run_metrics = [simulate(n_nodes, edges, condition, int(rng.integers(0, 2**31 - 1))) for _ in range(n_runs)]
            averaged = average_metrics(run_metrics)
            run_scores = [carrier_score(m) for m in run_metrics]
            averaged["perturbation_stability"] = perturbation_stability_from_scores(run_scores)
            observed_score = carrier_score(averaged)
            p_value = permutation_p_greater(observed_score, null_scores)
            interpretation = interpret_row(topology_name, condition, averaged, p_value)
            rows.append({
                "topology_class": topology_class,
                "topology_name": topology_name,
                "n_nodes": n_nodes,
                "edge_convention": convention,
                "condition": condition,
                "jump_start": condition == "seeded",
                "input_file": "topology_simulation_fixed_preregistered_parameters",
                "metric_name": "autonomous_topology_carrier_score",
                "locking_strength": averaged["locking_strength"],
                "D12_score": averaged["D12_score"],
                "D24_score": averaged["D24_score"],
                "p_value": p_value,
                "q_value": np.nan,
                "late_window_stability": averaged["late_window_stability"],
                "perturbation_stability": averaged["perturbation_stability"],
                "transient_score": averaged["transient_score"],
                "transient_duration": averaged["transient_duration"],
                "loop_support_min": loop_min,
                "loop_support_max": loop_max,
                "supports_2_through_24_structural": support_2_24,
                "supports_2_through_24_empirical": False,
                "bounded_non_runaway_score": averaged["bounded_non_runaway_score"],
                "non_collapsed_differentiation_score": averaged["non_collapsed_differentiation_score"],
                "null_model": "degree-matched directed random graph",
                "null_mean": float(np.nanmean(null_scores)),
                "null_sd": float(np.nanstd(null_scores)),
                "interpretation": interpretation,
                "notes": notes + "; " + five_ten_loop_notes(n_nodes, edges),
            })
    results = pd.DataFrame(rows)
    if len(results):
        results["q_value"] = bh_fdr(results["p_value"].astype(float).tolist())
        results["supports_2_through_24_empirical"] = results.apply(empirical_support, axis=1)
        results["interpretation"] = results.apply(lambda row: final_interpretation(row), axis=1)
    return results, pd.DataFrame(null_rows)


def average_metrics(metrics_list: list[dict[str, float]]) -> dict[str, float]:
    keys = metrics_list[0].keys()
    averaged: dict[str, float] = {}
    for key in keys:
        values = np.asarray([m[key] for m in metrics_list], dtype=float)
        finite = values[np.isfinite(values)]
        averaged[key] = float(np.mean(finite)) if len(finite) else np.nan
    return averaged


def carrier_score(metrics: dict[str, float]) -> float:
    d_score = max(metrics.get("D12_score", np.nan), metrics.get("D24_score", np.nan))
    parts = [
        d_score,
        metrics.get("late_window_stability", np.nan),
        metrics.get("bounded_non_runaway_score", np.nan),
        metrics.get("non_collapsed_differentiation_score", np.nan),
    ]
    return float(np.nanmean(parts))


def perturbation_stability_from_scores(scores: list[float]) -> float:
    arr = np.asarray(scores, dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) < 2:
        return np.nan
    return float(np.clip(1.0 - np.std(arr) / 0.15, 0.0, 1.0))


def permutation_p_greater(observed: float, null_scores: list[float]) -> float:
    null = np.asarray(null_scores, dtype=float)
    if not np.isfinite(observed) or len(null) == 0:
        return np.nan
    return float((1.0 + np.sum(null >= observed)) / (len(null) + 1.0))


def interpret_row(topology_name: str, condition: str, metrics: dict[str, float], p_value: float) -> str:
    if condition == "seeded":
        return "seeded condition; jump-start dependence assessed against unseeded counterpart"
    if topology_name == "C12(1,2)":
        return "primary unseeded C12(1,2) carrier candidate"
    if topology_name == "C8(1)":
        return "primary unseeded C8(1) contrast"
    return "exploratory topology family"


def empirical_support(row: pd.Series) -> bool:
    d_score = max(float(row["D12_score"]), float(row["D24_score"]))
    return bool(
        d_score >= 0.70
        and float(row["locking_strength"]) >= 0.70
        and float(row["late_window_stability"]) >= 0.70
        and float(row["perturbation_stability"]) >= 0.70
        and float(row["bounded_non_runaway_score"]) >= 0.70
        and float(row["non_collapsed_differentiation_score"]) >= 0.30
        and float(row["q_value"]) <= 0.05
        and not bool(row["jump_start"])
    )


def final_interpretation(row: pd.Series) -> str:
    if empirical_support(row):
        return "positive_candidate_under_preregistered_thresholds"
    if bool(row["jump_start"]):
        return "seeded_or_jump_start_condition_not_primary_carrier_evidence"
    if row["topology_name"] == "C12(1,2)":
        return "negative_or_inconclusive_for_unseeded_C12_1_2_auto_locking"
    return "exploratory_or_control_result"


def write_summary(
    output_path: Path,
    results: pd.DataFrame,
    inventory: pd.DataFrame,
    context: pd.DataFrame,
    nulls: pd.DataFrame,
) -> None:
    primary = results[results["topology_name"].isin(PRIMARY_TOPOLOGIES)] if len(results) else results
    c12_unseeded = primary[(primary["topology_name"] == "C12(1,2)") & (primary["condition"] == "unseeded")] if len(primary) else primary
    c8_unseeded = primary[(primary["topology_name"] == "C8(1)") & (primary["condition"] == "unseeded")] if len(primary) else primary
    c8_seeded = primary[(primary["topology_name"] == "C8(1)") & (primary["condition"] == "seeded")] if len(primary) else primary
    positive = results[results["supports_2_through_24_empirical"].astype(bool)] if len(results) else results

    if len(c12_unseeded) and bool(c12_unseeded.iloc[0]["supports_2_through_24_empirical"]):
        stage_c = "Stage B2 supports moving toward a later Stage C recursive-admissibility audit."
    elif len(c12_unseeded):
        stage_c = "Stage B2 does not yet support moving to Stage C."
    else:
        stage_c = "Stage B2 is inconclusive and requires cleaner inputs or controls."

    lines = [
        "# Stage B2 Topology-Aware Carrier Audit Summary",
        "",
        "## Purpose",
        "",
        "Stage B2 tests explicit directed topology/operator families as an exploratory refinement of Stage B. It is not Stage C.",
        "",
        "## Why This Is Stage B2, Not Stage C",
        "",
        "Stage B2 asks whether topology-aware behavior can discriminate carrier-like behavior from IDPC-internal restoration artifact. Stage C is reserved for a later recursive-admissibility audit only if Stage B2 produces a meaningful carrier/restoration distinction.",
        "",
        "## Inputs Used",
        "",
        f"- context input files loaded: {len(context)}",
        f"- topology families tested: {len(inventory)}",
        f"- null-control rows: {len(nulls)}",
        "",
        "## eps72 as Existing IDPC Readout",
        "",
        "eps72 is treated as an existing IDPC phase-restoration readout. eps72 restoring alone is not treated as carrier evidence in this report.",
        "",
        "## Topology Definitions",
        "",
        "The primary held-out candidate is C12(1,2), implemented with 12 nodes and bidirectional 1-jump and 2-jump arrows, giving 48 directed arrows. C8(1) is the primary jump-start-dependent contrast.",
        "",
        "## Topology Classes",
        "",
    ]
    for _, row in inventory.iterrows():
        lines.append(
            f"- {row['topology_name']}: {row['topology_class']}, nodes={row['n_nodes']}, "
            f"edges={row['n_directed_edges']}, convention={row['edge_convention']}"
        )
    lines += [
        "",
        "## Success Criteria",
        "",
        "Auto-locking requires unseeded D12/D24 structure, late-window stability, degree-matched null separation, FDR survival, bounded non-runaway behavior, and non-collapsed differentiation.",
        "",
        "## Null Controls",
        "",
        "Degree-matched directed random graphs preserve node count, in-degree distribution, out-degree distribution, directed-arrow count where possible, and density approximately.",
        "",
        "## Results Table",
        "",
    ]
    if len(results):
        cols = [
            "topology_name", "condition", "locking_strength", "D12_score", "D24_score",
            "p_value", "q_value", "late_window_stability", "perturbation_stability",
            "bounded_non_runaway_score",
            "non_collapsed_differentiation_score", "supports_2_through_24_structural",
            "supports_2_through_24_empirical", "interpretation",
        ]
        try:
            lines.append(results[cols].to_markdown(index=False))
        except ImportError:
            lines.append("```csv")
            lines.append(results[cols].to_csv(index=False).strip())
            lines.append("```")
    else:
        lines.append("No topology results were produced.")
    lines += [
        "",
        "## 5-Loop / 10-Loop Transience",
        "",
    ]
    for _, row in inventory.iterrows():
        lines.append(f"- {row['topology_name']}: {row['five_ten_loop_notes']}")
    lines += [
        "",
        "## QFT / Knot Theory Boundary",
        "",
        "QFT, knot theory, braid theory, field topology, and invisible memory are future theoretical bridges only. Stage B2 does not confirm QFT, consciousness, AGI, or a physical carrier.",
        "",
        "## Interpretation",
        "",
        f"- empirical-positive topology rows under preregistered thresholds: {len(positive)}",
    ]
    if len(c12_unseeded):
        row = c12_unseeded.iloc[0]
        lines.append(
            f"- C12(1,2) unseeded: D12={row['D12_score']:.3f}, D24={row['D24_score']:.3f}, "
            f"q={row['q_value']:.3g}, bounded={row['bounded_non_runaway_score']:.3f}, "
            f"differentiation={row['non_collapsed_differentiation_score']:.3f}, "
            f"interpretation={row['interpretation']}"
        )
    if len(c8_unseeded) and len(c8_seeded):
        u = c8_unseeded.iloc[0]
        s = c8_seeded.iloc[0]
        lines.append(
            f"- C8(1) contrast: unseeded carrier score={carrier_score_from_row(u):.3f}, "
            f"seeded carrier score={carrier_score_from_row(s):.3f}"
        )
    lines += [
        "",
        "## Limitations",
        "",
        "- The topology simulation uses fixed exploratory Kuramoto-style dynamics and is not a physical proof of a carrier.",
        "- Existing Ricci / eps72 outputs are context readouts and may contain IDPC-internal restoration structure.",
        "- Polyhedral families are included as higher-order exploratory candidates and are not equivalent to standalone Cn(k) rings.",
        "",
        "## Whether Stage C Is Justified",
        "",
        stage_c,
        "",
    ]
    output_path.write_text("\n".join(lines) + "\n")


def carrier_score_from_row(row: pd.Series) -> float:
    metrics = {
        "D12_score": float(row["D12_score"]),
        "D24_score": float(row["D24_score"]),
        "late_window_stability": float(row["late_window_stability"]),
        "bounded_non_runaway_score": float(row["bounded_non_runaway_score"]),
        "non_collapsed_differentiation_score": float(row["non_collapsed_differentiation_score"]),
    }
    return carrier_score(metrics)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Stage B2 topology-aware carrier audit")
    parser.add_argument("--input-root", default=".", help="Repository or IDPC output root to search")
    parser.add_argument("--output-dir", default="reports", help="Output directory")
    parser.add_argument("--n-runs", type=int, default=40, help="Simulation runs per topology/condition")
    parser.add_argument("--n-null", type=int, default=80, help="Degree-matched null graphs per topology/condition")
    parser.add_argument("--seed", type=int, default=20260607)
    args = parser.parse_args()

    input_root = Path(args.input_root).resolve()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    topology_names = [
        "C8(1)",
        "C6(1,2)",
        "C8(1,2)",
        "C12(1)",
        "C12(1,2)",
        "cuboctahedron",
        "dodecahedron",
        "icosahedron",
    ]
    inventory = topology_inventory_rows(topology_names)
    context_dirs = [input_root]
    if input_root.name != "reports" and not (input_root / "reports").exists():
        reports_dir = Path("reports").resolve()
        if reports_dir.exists():
            context_dirs.append(reports_dir)
    context = summarize_stage_b_context(context_dirs)
    results, nulls = run_topology_audit(topology_names, args.n_runs, args.n_null, args.seed)

    inventory.to_csv(output_dir / "Stage_B2_topology_loop_inventory.csv", index=False)
    context.to_csv(output_dir / "Stage_B2_input_context_inventory.csv", index=False)
    nulls.to_csv(output_dir / "Stage_B2_topology_null_controls.csv", index=False)
    results.to_csv(output_dir / "Stage_B2_topology_aware_carrier_audit_results.csv", index=False)
    write_summary(output_dir / "Stage_B2_topology_aware_carrier_audit_summary.md", results, inventory, context, nulls)
    print(f"Wrote Stage B2 outputs to {output_dir}")


if __name__ == "__main__":
    main()
