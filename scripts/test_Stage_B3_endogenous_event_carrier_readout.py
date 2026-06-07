#!/usr/bin/env python3
"""Stage B3 endogenous-event-conditioned carrier-readout audit.

Stage B3 is a frozen transition/recovery audit, not Stage C.  It tests
whether IDPC-derived endogenous event schedules condition bounded,
non-collapsed D12/D24 recovery on the same primary C12(1,2) topology more
than matched time-shifted and random-event controls.
"""

from __future__ import annotations

import argparse
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


PRIMARY_TOPOLOGY = "C12(1,2)"
PRIMARY_CONDITIONS = ("endogenous", "time_shifted", "random_event")
SECONDARY_TOPOLOGIES = ("C8(1)", "dodecahedron", "icosahedron")
EVENT_FILE = "event_level_with_fes_phase_TRUE_RICCI.csv"


def unique_edges(n_nodes: int, jumps: tuple[int, ...]) -> list[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for i in range(n_nodes):
        for jump in jumps:
            j = (i + jump) % n_nodes
            if i != j:
                edges.add((i, j))
    return sorted(edges)


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
    if name == "C8(1)":
        return (
            "standalone Cn(k) directed rings",
            8,
            unique_edges(8, (1,)),
            "directed clockwise 1-jump",
            "primary non-D12 contrast",
        )
    if name == "C12(1,2)":
        return (
            "standalone Cn(k) directed rings",
            12,
            unique_edges(12, (-2, -1, 1, 2)),
            "bidirectional 1-jump and 2-jump; 48 directed arrows",
            "primary Luke/D12RG normalized readout candidate",
        )
    if name == "dodecahedron":
        n = 20
        shifts = [10, 7, 4, -4, -7, 10, -4, 7, -7, 4] * 2
        undirected: set[tuple[int, int]] = set()
        for i in range(n):
            undirected.add(tuple(sorted((i, (i + 1) % n))))
            undirected.add(tuple(sorted((i, (i + shifts[i]) % n))))
        return directed_from_undirected(
            "dodecahedral topology",
            n,
            sorted(undirected),
            "bidirected LCF dodecahedron edges",
            "exploratory FES fivefold-to-12-face bridge family",
        )
    if name == "icosahedron":
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
        return directed_from_undirected(
            "icosahedral topology",
            n,
            sorted(undirected),
            "bidirected icosahedron edges",
            "exploratory 5-12-20 bridge family",
        )
    raise ValueError(f"unknown topology: {name}")


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
    out_degree = {i: 0 for i in range(n_nodes)}
    for i, _ in edges:
        out_degree[i] += 1
    candidate: set[tuple[int, int]] = set()
    for i, deg in out_degree.items():
        choices = [j for j in range(n_nodes) if j != i]
        for j in rng.choice(choices, size=min(deg, len(choices)), replace=False):
            candidate.add((i, int(j)))
    return sorted(candidate)


def order_parameter(theta: np.ndarray, harmonic: int = 1) -> float:
    return float(abs(np.mean(np.exp(1j * harmonic * theta))))


def grid_score(theta: np.ndarray, period: int) -> float:
    step = 2.0 * np.pi / period
    residual = np.mod(theta + step / 2.0, step) - step / 2.0
    return float(np.clip(1.0 - np.mean(np.abs(residual)) / (step / 2.0), 0.0, 1.0))


def differentiation_score(theta: np.ndarray, bins: int = 12) -> float:
    counts = np.bincount(
        np.floor(np.mod(theta, 2.0 * np.pi) / (2.0 * np.pi) * bins).astype(int),
        minlength=bins,
    )
    p = counts[counts > 0] / max(1, np.sum(counts))
    entropy = -float(np.sum(p * np.log(p))) / math.log(bins) if len(p) else 0.0
    occupied = float(np.count_nonzero(counts)) / bins
    return float(np.clip(0.5 * entropy + 0.5 * occupied, 0.0, 1.0))


def stability_score(values: list[float]) -> float:
    arr = np.asarray(values, dtype=float)
    if len(arr) < 4:
        return np.nan
    return float(np.clip(1.0 - np.std(arr) / 0.15, 0.0, 1.0))


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


def load_event_table(input_root: Path) -> pd.DataFrame:
    path = input_root / EVENT_FILE
    if not path.exists():
        raise FileNotFoundError(f"missing primary B3 event file: {path}")
    df = pd.read_csv(path)
    required = {"label", "task_idx", "J", "distance", "phase", "fes_phase"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{path} missing columns: {missing}")
    df = df.sort_values(["label", "task_idx"]).reset_index(drop=True)
    return df


def add_event_classes(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    j_cut = out["J"].abs().quantile(0.75)
    distance_cut = out["distance"].quantile(0.25)
    out["high_boundary_impulse_J"] = out["J"].abs() >= j_cut
    out["residual_contraction_low_distance"] = out["distance"] <= distance_cut
    out["FES_phase_transition"] = False
    for _, idx in out.groupby("label").groups.items():
        sub = out.loc[idx].sort_values("task_idx")
        transitions = sub["fes_phase"].astype(str).ne(sub["fes_phase"].astype(str).shift(1))
        transitions.iloc[0] = False
        out.loc[sub.index, "FES_phase_transition"] = transitions.to_numpy()
    return out


def build_event_schedule(
    df: pd.DataFrame,
    event_class: str,
    steps: int,
    n_nodes: int,
) -> tuple[list[dict[str, float]], dict[str, float]]:
    rows = df[df[event_class].astype(bool)].copy()
    if rows.empty:
        return [], {"n_events": 0}
    min_task = float(df["task_idx"].min())
    max_task = float(df["task_idx"].max())
    denom = max(max_task - min_task, 1.0)
    schedules = []
    for ordinal, (_, row) in enumerate(rows.iterrows()):
        frac = (float(row["task_idx"]) - min_task) / denom
        step = int(np.clip(round(frac * (steps - 1)), 0, steps - 1))
        if event_class == "high_boundary_impulse_J":
            raw_strength = abs(float(row["J"]))
        elif event_class == "residual_contraction_low_distance":
            raw_strength = max(0.0, 1.0 / (1.0 + abs(float(row["distance"]))))
        else:
            raw_strength = 1.0
        phase = float(row.get("phase", 0.0))
        target = int(np.mod(round((np.mod(phase, 2.0 * np.pi) / (2.0 * np.pi)) * n_nodes), n_nodes))
        schedules.append(
            {
                "step": step,
                "strength": raw_strength,
                "target": target,
                "ordinal": ordinal,
            }
        )
    strengths = np.asarray([x["strength"] for x in schedules], dtype=float)
    if np.nanmax(strengths) > np.nanmin(strengths):
        scaled = 0.05 + 0.15 * (strengths - np.nanmin(strengths)) / (np.nanmax(strengths) - np.nanmin(strengths))
    else:
        scaled = np.full_like(strengths, 0.10)
    for item, strength in zip(schedules, scaled):
        item["strength"] = float(strength)
    metadata = {
        "n_events": len(schedules),
        "mean_strength": float(np.mean(scaled)),
        "total_impulse_budget": float(np.sum(scaled)),
    }
    return schedules, metadata


def shifted_schedule(schedule: list[dict[str, float]], steps: int, shift: int) -> list[dict[str, float]]:
    return [{**item, "step": int((item["step"] + shift) % steps)} for item in schedule]


def random_schedule(
    schedule: list[dict[str, float]],
    steps: int,
    rng: np.random.Generator,
) -> list[dict[str, float]]:
    random_steps = rng.choice(np.arange(steps), size=len(schedule), replace=len(schedule) > steps)
    return [{**item, "step": int(step)} for item, step in zip(schedule, random_steps)]


def artificial_schedule(n_nodes: int, steps: int) -> list[dict[str, float]]:
    return [
        {"step": 0, "strength": 0.18, "target": int(i % n_nodes), "ordinal": i}
        for i in range(n_nodes)
    ]


def apply_event_impulse(theta: np.ndarray, event: dict[str, float]) -> np.ndarray:
    n_nodes = len(theta)
    target = int(event["target"]) % n_nodes
    strength = float(event["strength"])
    grid = 2.0 * np.pi * np.arange(n_nodes) / n_nodes
    target_phase = np.roll(grid, target)
    return np.mod((1.0 - strength) * theta + strength * target_phase, 2.0 * np.pi)


def simulate_event_conditioned(
    n_nodes: int,
    edges: list[tuple[int, int]],
    event_schedule: list[dict[str, float]],
    seed: int,
    steps: int = 240,
    dt: float = 0.06,
    coupling: float = 0.34,
    second_harmonic: float = 0.04,
    recovery_window: int = 18,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0.0, 2.0 * np.pi, size=n_nodes)
    omega = rng.normal(0.0, 0.012, size=n_nodes)
    incoming = [[] for _ in range(n_nodes)]
    for i, j in edges:
        incoming[j].append(i)
    by_step: dict[int, list[dict[str, float]]] = defaultdict(list)
    for event in event_schedule:
        by_step[int(event["step"])].append(event)
    d12_series = []
    d24_series = []
    diff_series = []
    order_series = []
    vel_series = []
    for t in range(steps):
        for event in by_step.get(t, []):
            theta = apply_event_impulse(theta, event)
        delta = np.array(omega, dtype=float)
        for j in range(n_nodes):
            if not incoming[j]:
                continue
            diffs = theta[incoming[j]] - theta[j]
            delta[j] += coupling * float(np.mean(np.sin(diffs)))
            delta[j] += second_harmonic * float(np.mean(np.sin(2.0 * diffs)))
        theta = np.mod(theta + dt * delta, 2.0 * np.pi)
        order_series.append(order_parameter(theta))
        d12_series.append(grid_score(theta, 12))
        d24_series.append(grid_score(theta, 24))
        diff_series.append(differentiation_score(theta, 12))
        vel_series.append(float(np.linalg.norm(dt * delta) / max(1, n_nodes)))
    return summarize_recovery(
        event_schedule,
        d12_series,
        d24_series,
        diff_series,
        order_series,
        vel_series,
        recovery_window,
    )


def summarize_recovery(
    schedule: list[dict[str, float]],
    d12: list[float],
    d24: list[float],
    diff: list[float],
    order: list[float],
    vel: list[float],
    recovery_window: int,
) -> dict[str, float]:
    steps = len(d12)
    event_steps = sorted({int(x["step"]) for x in schedule if 0 <= int(x["step"]) < steps})
    improvements = []
    diff_post = []
    d12_post = []
    d24_post = []
    order_post = []
    bounded_post = []
    for step in event_steps:
        pre_start = max(0, step - recovery_window)
        post_end = min(steps, step + recovery_window + 1)
        if step <= pre_start or post_end <= step + 1:
            continue
        pre_d = np.maximum(d12[pre_start:step], d24[pre_start:step])
        post_d = np.maximum(d12[step + 1:post_end], d24[step + 1:post_end])
        improvements.append(float(np.mean(post_d) - np.mean(pre_d)))
        diff_post.append(float(np.mean(diff[step + 1:post_end])))
        d12_post.append(float(np.mean(d12[step + 1:post_end])))
        d24_post.append(float(np.mean(d24[step + 1:post_end])))
        order_post.append(float(np.mean(order[step + 1:post_end])))
        bounded_post.append(float(np.clip(1.0 - np.mean(vel[step + 1:post_end]) / 0.04, 0.0, 1.0)))
    if not improvements:
        return {
            "n_events_evaluated": 0,
            "D12_recovery": np.nan,
            "D24_recovery": np.nan,
            "differentiated_recovery": np.nan,
            "bounded_non_runaway_score": np.nan,
            "non_collapsed_differentiation_score": np.nan,
            "late_window_stability": stability_score(np.maximum(d12[-40:], d24[-40:]).tolist()),
            "mean_phase_locking": float(np.mean(order[-40:])),
        }
    d_recovery = np.maximum(d12_post, d24_post)
    differentiated = np.asarray(improvements) * np.asarray(diff_post) * np.asarray(bounded_post)
    return {
        "n_events_evaluated": len(improvements),
        "D12_recovery": float(np.mean(d12_post)),
        "D24_recovery": float(np.mean(d24_post)),
        "D12_D24_recovery_improvement": float(np.mean(improvements)),
        "differentiated_recovery": float(np.mean(differentiated)),
        "bounded_non_runaway_score": float(np.mean(bounded_post)),
        "non_collapsed_differentiation_score": float(np.mean(diff_post)),
        "late_window_stability": stability_score(np.maximum(d12[-40:], d24[-40:]).tolist()),
        "mean_phase_locking": float(np.mean(order_post)),
        "post_event_readout_score": float(np.mean(d_recovery)),
    }


def average_dicts(items: list[dict[str, float]]) -> dict[str, float]:
    keys = sorted(set().union(*(item.keys() for item in items)))
    out: dict[str, float] = {}
    for key in keys:
        vals = np.asarray([item.get(key, np.nan) for item in items], dtype=float)
        finite = vals[np.isfinite(vals)]
        out[key] = float(np.mean(finite)) if len(finite) else np.nan
        out[f"{key}_sd"] = float(np.std(finite)) if len(finite) else np.nan
    return out


def p_greater(observed: float, controls: list[float]) -> float:
    control = np.asarray(controls, dtype=float)
    control = control[np.isfinite(control)]
    if not np.isfinite(observed) or len(control) == 0:
        return np.nan
    return float((1.0 + np.sum(control >= observed)) / (len(control) + 1.0))


def run_audit(
    input_root: Path,
    output_dir: Path,
    n_runs: int,
    n_null: int,
    seed: int,
    steps: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    events = add_event_classes(load_event_table(input_root))
    event_classes = [
        "high_boundary_impulse_J",
        "residual_contraction_low_distance",
        "FES_phase_transition",
    ]
    topology_names = [PRIMARY_TOPOLOGY, "C8(1)", "dodecahedron", "icosahedron"]
    results = []
    null_rows = []
    for topology_name in topology_names:
        topology_class, n_nodes, edges, convention, notes = topology_definition(topology_name)
        for event_class in event_classes:
            endogenous, meta = build_event_schedule(events, event_class, steps, n_nodes)
            if not endogenous:
                continue
            shifted = shifted_schedule(endogenous, steps, shift=max(7, steps // 5))
            random_event = random_schedule(endogenous, steps, rng)
            artificial = artificial_schedule(n_nodes, steps)
            schedules = {
                "endogenous": endogenous,
                "time_shifted": shifted,
                "random_event": random_event,
                "unseeded": [],
                "artificial_seeded": artificial,
            }
            condition_metrics: dict[str, list[dict[str, float]]] = {}
            for condition, schedule in schedules.items():
                condition_metrics[condition] = [
                    simulate_event_conditioned(
                        n_nodes,
                        edges,
                        schedule,
                        int(rng.integers(0, 2**31 - 1)),
                        steps=steps,
                    )
                    for _ in range(n_runs)
                ]
            averaged = {k: average_dicts(v) for k, v in condition_metrics.items()}
            endogenous_score = averaged["endogenous"]["differentiated_recovery"]
            control_scores = [
                m["differentiated_recovery"]
                for name in ("time_shifted", "random_event")
                for m in condition_metrics[name]
            ]
            p_value = p_greater(endogenous_score, control_scores)
            effect_vs_shifted = endogenous_score - averaged["time_shifted"]["differentiated_recovery"]
            effect_vs_random = endogenous_score - averaged["random_event"]["differentiated_recovery"]
            primary_candidate = (
                topology_name == PRIMARY_TOPOLOGY
                and effect_vs_shifted > 0
                and effect_vs_random > 0
                and averaged["endogenous"]["bounded_non_runaway_score"] >= 0.70
                and averaged["endogenous"]["non_collapsed_differentiation_score"] >= 0.30
                and averaged["endogenous"]["late_window_stability"] >= 0.70
            )
            for condition, metrics in averaged.items():
                row = {
                    "topology_class": topology_class,
                    "topology_name": topology_name,
                    "topology_role": "primary" if topology_name == PRIMARY_TOPOLOGY else "secondary_or_exploratory",
                    "n_nodes": n_nodes,
                    "n_directed_edges": len(edges),
                    "edge_convention": convention,
                    "event_class": event_class,
                    "condition": condition,
                    "n_seed_events": meta["n_events"] if condition != "unseeded" else 0,
                    "mean_seed_strength": meta["mean_strength"] if condition in PRIMARY_CONDITIONS else np.nan,
                    "total_impulse_budget": meta["total_impulse_budget"] if condition in PRIMARY_CONDITIONS else np.nan,
                    "primary_endpoint_name": "differentiated_recovery",
                    "primary_p_value": p_value if condition == "endogenous" else np.nan,
                    "effect_vs_time_shifted": effect_vs_shifted if condition == "endogenous" else np.nan,
                    "effect_vs_random_event": effect_vs_random if condition == "endogenous" else np.nan,
                    "primary_candidate_pre_fdr": primary_candidate if condition == "endogenous" else False,
                    "notes": notes,
                }
                row.update(metrics)
                results.append(row)
            if topology_name == PRIMARY_TOPOLOGY:
                for null_idx in range(n_null):
                    null_edges = degree_matched_random_edges(n_nodes, edges, rng)
                    null_metrics = [
                        simulate_event_conditioned(
                            n_nodes,
                            null_edges,
                            endogenous,
                            int(rng.integers(0, 2**31 - 1)),
                            steps=steps,
                        )
                        for _ in range(max(1, n_runs // 2))
                    ]
                    avg_null = average_dicts(null_metrics)
                    null_rows.append(
                        {
                            "topology_name": topology_name,
                            "event_class": event_class,
                            "null_index": null_idx,
                            "null_model": "degree-matched directed random graph",
                            "n_nodes": n_nodes,
                            "n_directed_edges": len(null_edges),
                            "differentiated_recovery": avg_null["differentiated_recovery"],
                        }
                    )
    result_df = pd.DataFrame(results)
    if len(result_df):
        endogenous_mask = result_df["condition"].eq("endogenous")
        q_values = bh_fdr(result_df.loc[endogenous_mask, "primary_p_value"].astype(float).tolist())
        result_df["primary_q_value"] = np.nan
        result_df.loc[endogenous_mask, "primary_q_value"] = q_values
        result_df["interpretation"] = result_df.apply(interpret_row, axis=1)
    null_df = pd.DataFrame(null_rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_dir / "Stage_B3_endogenous_event_carrier_readout_results.csv", index=False)
    null_df.to_csv(output_dir / "Stage_B3_endogenous_event_carrier_readout_null_graphs.csv", index=False)
    write_run_manifest(output_dir / "Stage_B3_endogenous_event_carrier_readout_run_manifest.md", input_root, n_runs, n_null, seed, steps)
    write_summary(output_dir / "Stage_B3_endogenous_event_carrier_readout_summary.md", result_df, null_df)
    return result_df, null_df


def interpret_row(row: pd.Series) -> str:
    if row["condition"] != "endogenous":
        return "control_or_reference_condition"
    if row["topology_name"] != PRIMARY_TOPOLOGY:
        return "exploratory_polyhedral_or_contrast_result"
    if (
        bool(row["primary_candidate_pre_fdr"])
        and float(row["primary_q_value"]) <= 0.05
    ):
        return "positive_primary_candidate_under_preregistered_B3_thresholds"
    return "negative_or_inconclusive_for_primary_B3_event_conditioned_recovery"


def write_run_manifest(
    path: Path,
    input_root: Path,
    n_runs: int,
    n_null: int,
    seed: int,
    steps: int,
) -> None:
    lines = [
        "# Stage B3 Endogenous-Event-Conditioned Carrier-Readout Audit Run Manifest",
        "",
        "This manifest records the execution parameters used for the run. It does not replace the frozen preregistration document.",
        "",
        "## Frozen Design",
        "",
        f"- input root: `{input_root}`",
        f"- primary event file: `{EVENT_FILE}`",
        f"- n_runs: {n_runs}",
        f"- n_null: {n_null}",
        f"- random seed: {seed}",
        f"- simulation steps: {steps}",
        "- primary topology: C12(1,2)",
        "- primary discriminator: endogenous vs time-shifted vs random-event schedules on the same C12(1,2) graph",
        "- primary endpoint: differentiated_recovery",
        "- primary readout: D12/D24 differentiated recovery",
        "- 72 -> 24 -> 12 descent is not a primary endpoint in this run.",
        "",
        "## Endogenous Event Rules",
        "",
        "- high_boundary_impulse_J: top quartile of absolute J in the event-level IDPC table",
        "- residual_contraction_low_distance: bottom quartile of distance in the event-level IDPC table",
        "- FES_phase_transition: within-label change of FES phase",
        "",
        "## Leakage Guard",
        "",
        "The variables defining event classes are not used directly as the primary recovery score. The primary score is topology-readout recovery from simulated D12/D24 phase-grid behavior.",
        "",
        "## Controls",
        "",
        "- time-shifted event schedule preserving event count and impulse budget",
        "- random-event schedule preserving event count and impulse budget",
        "- unseeded reference",
        "- artificial seeded reference",
        "- C8(1) non-D12 contrast",
        "- dodecahedron / icosahedron exploratory polyhedral complements",
        "- degree-matched directed random graphs as secondary null floors",
        "",
        "## Positive Interpretation Rule",
        "",
        "A primary positive candidate requires endogenous C12(1,2) differentiated recovery to exceed both time-shifted and random-event controls, preserve bounded non-runaway behavior, preserve non-collapsed differentiation, preserve late-window stability, and survive FDR across endogenous primary tests.",
        "",
        "## Negative Interpretation Rule",
        "",
        "A negative result means that the preregistered endogenous IDPC events did not confirm C12/D24 topology-selective differentiated recovery under this B3 audit. It does not reject IDPC, D12RG, or later carrier-readout variants.",
    ]
    path.write_text("\n".join(lines) + "\n")


def write_summary(path: Path, results: pd.DataFrame, nulls: pd.DataFrame) -> None:
    primary = results[
        (results["topology_name"] == PRIMARY_TOPOLOGY)
        & (results["condition"] == "endogenous")
    ] if len(results) else results
    positive = primary[
        primary["interpretation"].eq("positive_primary_candidate_under_preregistered_B3_thresholds")
    ] if len(primary) else primary
    lines = [
        "# Stage B3 Endogenous-Event-Conditioned Carrier-Readout Audit Summary",
        "",
        "## Purpose",
        "",
        "Stage B3 tests whether endogenous IDPC transition events condition bounded, non-collapsed, differentiated D12/D24 recovery on the primary C12(1,2) readout topology.",
        "",
        "## Primary Result",
        "",
        f"- primary endogenous C12 event-class rows: {len(primary)}",
        f"- positive primary rows under preregistered thresholds: {len(positive)}",
        f"- degree-matched null graph rows: {len(nulls)}",
        "",
        "## Primary Endogenous C12 Rows",
        "",
    ]
    if len(primary):
        cols = [
            "event_class",
            "differentiated_recovery",
            "effect_vs_time_shifted",
            "effect_vs_random_event",
            "primary_p_value",
            "primary_q_value",
            "bounded_non_runaway_score",
            "non_collapsed_differentiation_score",
            "late_window_stability",
            "interpretation",
        ]
        lines.append(primary[cols].to_csv(index=False).strip())
    else:
        lines.append("No primary rows were produced.")
    lines += [
        "",
        "## Interpretation Boundary",
        "",
        "This report does not prove D12RG or a physical carrier. A positive row would indicate a candidate event-conditioned carrier-readout recovery signature only. A negative row is reported as negative or inconclusive under the frozen B3 design.",
    ]
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--n-runs", type=int, default=80)
    parser.add_argument("--n-null", type=int, default=80)
    parser.add_argument("--seed", type=int, default=20260607)
    parser.add_argument("--steps", type=int, default=240)
    args = parser.parse_args()
    run_audit(args.input_root, args.output_dir, args.n_runs, args.n_null, args.seed, args.steps)


if __name__ == "__main__":
    main()
