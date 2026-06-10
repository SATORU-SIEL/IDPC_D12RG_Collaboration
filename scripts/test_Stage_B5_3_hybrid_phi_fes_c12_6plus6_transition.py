#!/usr/bin/env python3
"""Stage B5.3 C12 6+6 dual-branch transition test."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


B5_1_SCRIPT = Path(__file__).with_name("test_Stage_B5_1_phi_fes_to_c12_bridge.py")
OUTPUT_PREFIX = "Stage_B5_3_hybrid_phi_fes_c12_6plus6_transition"
PRIMARY_EVENT = "hybrid_phi_sign_switch"
COHERENCE_EVENTS = ["hybrid_fes_phase_transition", "hybrid_cluster_transition"]
CONTRAST_EVENTS = [
    "chapter7_dphi_sign_switch",
    "chapter7_d2phi_curvature_switch",
    "chapter7_deps_sign_switch",
]
EVENT_CLASSES = [PRIMARY_EVENT] + COHERENCE_EVENTS + CONTRAST_EVENTS
FDR_ALPHA = 0.05


def load_b5_1_module():
    spec = importlib.util.spec_from_file_location("stage_b5_1", B5_1_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import Stage B5.1 script: {B5_1_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def p_greater(observed: float, controls: list[float] | np.ndarray) -> float:
    control = np.asarray(controls, dtype=float)
    control = control[np.isfinite(control)]
    if not np.isfinite(observed) or len(control) == 0:
        return np.nan
    return float((1.0 + np.sum(control >= observed)) / (len(control) + 1.0))


def bh_fdr(values: list[float] | np.ndarray) -> list[float]:
    p = np.asarray(values, dtype=float)
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


def branch_alignment(theta: np.ndarray, nodes: list[int], direction: int) -> float:
    expected = direction * 2.0 * np.pi * np.arange(len(nodes)) / len(nodes)
    observed = np.asarray(theta[nodes], dtype=float)
    return float(abs(np.mean(np.exp(1j * (observed - expected)))))


def c12_branch_scores(theta: np.ndarray) -> dict[str, float]:
    even_nodes = [0, 2, 4, 6, 8, 10]
    odd_nodes = [1, 3, 5, 7, 9, 11]
    even_plus = branch_alignment(theta, even_nodes, 1)
    even_minus = branch_alignment(theta, even_nodes, -1)
    odd_plus = branch_alignment(theta, odd_nodes, 1)
    odd_minus = branch_alignment(theta, odd_nodes, -1)
    plus = float(np.mean([even_plus, odd_plus]))
    minus = float(np.mean([even_minus, odd_minus]))
    return {
        "even_plus_alignment": even_plus,
        "even_minus_alignment": even_minus,
        "odd_plus_alignment": odd_plus,
        "odd_minus_alignment": odd_minus,
        "plus_branch_alignment": plus,
        "minus_branch_alignment": minus,
        "branch_contrast": plus - minus,
        "branch_selectivity": abs(plus - minus),
        "even_branch_contrast": even_plus - even_minus,
        "odd_branch_contrast": odd_plus - odd_minus,
    }


def simulate_branch_series(
    b3,
    n_nodes: int,
    edges: list[tuple[int, int]],
    event_schedule: list[dict[str, float]],
    seed: int,
    steps: int,
    dt: float = 0.06,
    coupling: float = 0.34,
    second_harmonic: float = 0.04,
) -> dict[str, np.ndarray]:
    if n_nodes != 12:
        raise ValueError("B5.3 branch metrics require a 12-node topology")
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0.0, 2.0 * np.pi, size=n_nodes)
    omega = rng.normal(0.0, 0.012, size=n_nodes)
    incoming = [[] for _ in range(n_nodes)]
    for i, j in edges:
        incoming[j].append(i)
    by_step: dict[int, list[dict[str, float]]] = defaultdict(list)
    for event in event_schedule:
        by_step[int(event["step"])].append(event)

    out: dict[str, list[float]] = defaultdict(list)
    for t in range(steps):
        for event in by_step.get(t, []):
            theta = b3.apply_event_impulse(theta, event)
        delta = np.array(omega, dtype=float)
        for j in range(n_nodes):
            if not incoming[j]:
                continue
            diffs = theta[incoming[j]] - theta[j]
            delta[j] += coupling * float(np.mean(np.sin(diffs)))
            delta[j] += second_harmonic * float(np.mean(np.sin(2.0 * diffs)))
        theta = np.mod(theta + dt * delta, 2.0 * np.pi)
        scores = c12_branch_scores(theta)
        for key, value in scores.items():
            out[key].append(value)
        out["D12"].append(b3.grid_score(theta, 12))
        out["D24"].append(b3.grid_score(theta, 24))
        out["diff"].append(b3.differentiation_score(theta, 12))
        out["order"].append(b3.order_parameter(theta))
        out["vel"].append(float(np.linalg.norm(dt * delta) / max(1, n_nodes)))
    return {key: np.asarray(values, dtype=float) for key, values in out.items()}


def summarize_branch_transition(
    b3,
    schedule: list[dict[str, float]],
    series: dict[str, np.ndarray],
    recovery_window: int,
) -> dict[str, float]:
    steps = len(series["D12"])
    event_steps = sorted({int(x["step"]) for x in schedule if 0 <= int(x["step"]) < steps})
    transition_scores = []
    signed_deltas = []
    flip_flags = []
    pre_contrasts = []
    post_contrasts = []
    selectivity_post = []
    even_delta = []
    odd_delta = []
    generic_improvements = []
    differentiated_branch = []
    bounded_post = []
    diff_post = []

    readout = np.maximum(series["D12"], series["D24"])
    for step in event_steps:
        pre_start = max(0, step - recovery_window)
        post_end = min(steps, step + recovery_window + 1)
        if step <= pre_start or post_end <= step + 1:
            continue
        pre_branch = float(np.mean(series["branch_contrast"][pre_start:step]))
        post_branch = float(np.mean(series["branch_contrast"][step + 1 : post_end]))
        signed_delta = post_branch - pre_branch
        transition = abs(signed_delta)
        pre_readout = float(np.mean(readout[pre_start:step]))
        post_readout = float(np.mean(readout[step + 1 : post_end]))
        diff_score = float(np.mean(series["diff"][step + 1 : post_end]))
        bounded = float(np.clip(1.0 - np.mean(series["vel"][step + 1 : post_end]) / 0.04, 0.0, 1.0))

        pre_contrasts.append(pre_branch)
        post_contrasts.append(post_branch)
        signed_deltas.append(signed_delta)
        transition_scores.append(transition)
        flip_flags.append(float(np.sign(pre_branch) != np.sign(post_branch) and abs(pre_branch) > 0.01 and abs(post_branch) > 0.01))
        selectivity_post.append(float(np.mean(series["branch_selectivity"][step + 1 : post_end])))
        even_delta.append(float(np.mean(series["even_branch_contrast"][step + 1 : post_end]) - np.mean(series["even_branch_contrast"][pre_start:step])))
        odd_delta.append(float(np.mean(series["odd_branch_contrast"][step + 1 : post_end]) - np.mean(series["odd_branch_contrast"][pre_start:step])))
        generic_improvements.append(post_readout - pre_readout)
        bounded_post.append(bounded)
        diff_post.append(diff_score)
        differentiated_branch.append(transition * diff_score * bounded)

    if not transition_scores:
        return {
            "n_events_evaluated": 0,
            "branch_transition_score": np.nan,
            "branch_transition_differentiated": np.nan,
            "branch_flip_fraction": np.nan,
            "generic_readout_improvement": np.nan,
            "late_branch_stability": b3.stability_score(series["branch_contrast"][-40:].tolist()),
        }
    branch_transition = float(np.mean(transition_scores))
    generic_improvement = float(np.mean(generic_improvements))
    return {
        "n_events_evaluated": len(transition_scores),
        "branch_transition_score": branch_transition,
        "branch_transition_differentiated": float(np.mean(differentiated_branch)),
        "branch_signed_delta": float(np.mean(signed_deltas)),
        "branch_flip_fraction": float(np.mean(flip_flags)),
        "pre_branch_contrast": float(np.mean(pre_contrasts)),
        "post_branch_contrast": float(np.mean(post_contrasts)),
        "post_branch_selectivity": float(np.mean(selectivity_post)),
        "even_branch_delta": float(np.mean(even_delta)),
        "odd_branch_delta": float(np.mean(odd_delta)),
        "even_odd_delta_concordance": bool(np.sign(np.mean(even_delta)) == np.sign(np.mean(odd_delta))),
        "generic_readout_improvement": generic_improvement,
        "branch_minus_abs_generic_improvement": branch_transition - abs(generic_improvement),
        "bounded_non_runaway_score": float(np.mean(bounded_post)),
        "non_collapsed_differentiation_score": float(np.mean(diff_post)),
        "late_branch_stability": b3.stability_score(series["branch_contrast"][-40:].tolist()),
        "late_generic_readout_stability": b3.stability_score(np.maximum(series["D12"][-40:], series["D24"][-40:]).tolist()),
        "mean_final_branch_selectivity": float(np.mean(series["branch_selectivity"][-40:])),
        "mean_final_readout": float(np.mean(np.maximum(series["D12"][-40:], series["D24"][-40:]))),
    }


def simulate_branch_many(
    b3,
    n_nodes: int,
    edges: list[tuple[int, int]],
    schedule: list[dict[str, float]],
    n_runs: int,
    steps: int,
    rng: np.random.Generator,
    recovery_window: int,
) -> tuple[np.ndarray, pd.DataFrame, dict[str, float]]:
    rows = []
    values = []
    for run_index in range(n_runs):
        series = simulate_branch_series(
            b3,
            n_nodes,
            edges,
            schedule,
            int(rng.integers(0, 2**31 - 1)),
            steps,
        )
        row = summarize_branch_transition(b3, schedule, series, recovery_window)
        row["run_index"] = run_index
        rows.append(row)
        values.append(row.get("branch_transition_differentiated", np.nan))
    run_df = pd.DataFrame(rows)
    avg = {
        key: float(run_df[key].mean())
        for key in run_df.columns
        if key != "run_index" and pd.api.types.is_numeric_dtype(run_df[key])
    }
    return np.asarray(values, dtype=float), run_df, avg


def evaluate_event_class(
    b3,
    events: pd.DataFrame,
    event_class: str,
    steps: int,
    n_runs: int,
    n_null_graphs: int,
    n_null_runs: int,
    rng: np.random.Generator,
    recovery_window: int,
) -> tuple[list[dict[str, object]], list[pd.DataFrame], list[dict[str, object]]]:
    event_rows = events[events["event_class"].eq(event_class)].copy()
    event_role = str(event_rows["event_role"].iloc[0])
    _, c12_nodes, c12_edges, _, _ = b3.topology_definition("C12(1,2)")
    schedule, meta = b3.build_event_schedule(event_rows, event_class, steps, c12_nodes)
    if not schedule:
        return [], [], []
    shifted = b3.shifted_schedule(schedule, steps, shift=max(7, steps // 5))

    condition_specs = [
        ("endogenous", schedule),
        ("time_shifted", shifted),
    ]
    random_schedules = [b3.random_schedule(schedule, steps, rng) for _ in range(n_runs)]

    rows: list[dict[str, object]] = []
    run_dfs: list[pd.DataFrame] = []
    condition_values: dict[str, np.ndarray] = {}
    condition_avgs: dict[str, dict[str, float]] = {}

    for condition, condition_schedule in condition_specs:
        values, run_df, avg = simulate_branch_many(
            b3,
            c12_nodes,
            c12_edges,
            condition_schedule,
            n_runs,
            steps,
            rng,
            recovery_window,
        )
        run_df.insert(0, "condition", condition)
        run_df.insert(0, "event_class", event_class)
        run_dfs.append(run_df)
        condition_values[condition] = values
        condition_avgs[condition] = avg

    random_rows = []
    random_values = []
    for run_index, random_schedule in enumerate(random_schedules):
        series = simulate_branch_series(
            b3,
            c12_nodes,
            c12_edges,
            random_schedule,
            int(rng.integers(0, 2**31 - 1)),
            steps,
        )
        row = summarize_branch_transition(b3, random_schedule, series, recovery_window)
        row["run_index"] = run_index
        random_rows.append(row)
        random_values.append(row.get("branch_transition_differentiated", np.nan))
    random_df = pd.DataFrame(random_rows)
    random_df.insert(0, "condition", "random_event")
    random_df.insert(0, "event_class", event_class)
    run_dfs.append(random_df)
    condition_values["random_event"] = np.asarray(random_values, dtype=float)
    condition_avgs["random_event"] = {
        key: float(random_df[key].mean())
        for key in random_df.columns
        if key not in {"event_class", "condition", "run_index"} and pd.api.types.is_numeric_dtype(random_df[key])
    }

    null_values = []
    null_rows: list[dict[str, object]] = []
    for null_index in range(n_null_graphs):
        null_edges = b3.degree_matched_random_edges(c12_nodes, c12_edges, rng)
        values, _, avg = simulate_branch_many(
            b3,
            c12_nodes,
            null_edges,
            schedule,
            n_null_runs,
            steps,
            rng,
            recovery_window,
        )
        null_values.extend(values[np.isfinite(values)].tolist())
        null_rows.append(
            {
                "event_class": event_class,
                "event_role": event_role,
                "null_index": null_index,
                "null_model": "degree-matched directed random graph",
                "n_null_runs": n_null_runs,
                "mean_branch_transition_differentiated": float(np.nanmean(values)),
                "sd_branch_transition_differentiated": float(np.nanstd(values)),
                "mean_branch_transition_score": avg.get("branch_transition_score", np.nan),
                "mean_branch_flip_fraction": avg.get("branch_flip_fraction", np.nan),
                "mean_late_branch_stability": avg.get("late_branch_stability", np.nan),
            }
        )

    obs = float(np.nanmean(condition_values["endogenous"]))
    shift_mean = float(np.nanmean(condition_values["time_shifted"]))
    random_mean = float(np.nanmean(condition_values["random_event"]))
    null_mean = float(np.nanmean(null_values)) if null_values else np.nan
    for condition in ["endogenous", "time_shifted", "random_event"]:
        avg = condition_avgs[condition]
        row = {
            "event_class": event_class,
            "event_role": event_role,
            "condition": condition,
            "topology_name": "C12(1,2)",
            "primary_endpoint_name": "branch_transition_differentiated",
            "n_seed_events": meta["n_events"],
            "mean_seed_strength": meta["mean_strength"],
            "total_impulse_budget": meta["total_impulse_budget"],
            "n_runs": n_runs,
            "steps": steps,
            "mean_branch_transition_differentiated": float(np.nanmean(condition_values[condition])),
            "sd_branch_transition_differentiated": float(np.nanstd(condition_values[condition])),
            "effect_vs_time_shifted": obs - shift_mean if condition == "endogenous" else np.nan,
            "effect_vs_random_event": obs - random_mean if condition == "endogenous" else np.nan,
            "effect_vs_degree_null_mean": obs - null_mean if condition == "endogenous" else np.nan,
            "p_vs_time_shifted_and_random": p_greater(obs, np.r_[condition_values["time_shifted"], condition_values["random_event"]]) if condition == "endogenous" else np.nan,
            "p_vs_degree_null": p_greater(obs, null_values) if condition == "endogenous" else np.nan,
        }
        row.update(avg)
        rows.append(row)
    return rows, run_dfs, null_rows


def add_cross_event_decisions(results: pd.DataFrame, run_values: pd.DataFrame) -> pd.DataFrame:
    out = results.copy()
    endogenous = out["condition"].eq("endogenous")
    out["branch_transition_q_value"] = np.nan
    out.loc[endogenous, "branch_transition_q_value"] = bh_fdr(out.loc[endogenous, "p_vs_time_shifted_and_random"].astype(float).tolist())

    primary_obs = out[endogenous & out["event_class"].eq(PRIMARY_EVENT)]
    contrast_runs = run_values[
        run_values["condition"].eq("endogenous") & run_values["event_class"].isin(CONTRAST_EVENTS)
    ]["branch_transition_differentiated"].astype(float)
    primary_value = float(primary_obs["mean_branch_transition_differentiated"].iloc[0]) if not primary_obs.empty else np.nan
    out["p_vs_non_phi_contrast_switches"] = np.nan
    out.loc[endogenous & out["event_class"].eq(PRIMARY_EVENT), "p_vs_non_phi_contrast_switches"] = p_greater(primary_value, contrast_runs.to_numpy())
    max_contrast = float(contrast_runs.mean()) if len(contrast_runs) else np.nan
    out["mean_non_phi_contrast_run_value"] = max_contrast
    out["passes_branch_specificity_gate"] = (
        endogenous
        & out["event_class"].eq(PRIMARY_EVENT)
        & (out["effect_vs_time_shifted"] > 0)
        & (out["effect_vs_random_event"] > 0)
        & (out["effect_vs_degree_null_mean"] > 0)
        & (out["branch_minus_abs_generic_improvement"] > 0)
        & (out["p_vs_non_phi_contrast_switches"] <= FDR_ALPHA)
    )
    out["passes_null_gate"] = endogenous & (out["p_vs_degree_null"] <= FDR_ALPHA)
    out["passes_shift_random_fdr_gate"] = endogenous & (out["branch_transition_q_value"] <= FDR_ALPHA)
    out["mechanism_candidate"] = (
        out["event_class"].eq(PRIMARY_EVENT)
        & out["passes_branch_specificity_gate"]
        & out["passes_null_gate"]
        & out["passes_shift_random_fdr_gate"]
    )
    return out


def event_inventory(events: pd.DataFrame) -> pd.DataFrame:
    return (
        events[events["event_class"].isin(EVENT_CLASSES)]
        .groupby(["event_class", "event_role", "source_file", "event_rule"], as_index=False)
        .agg(
            n_events=("task_idx", "size"),
            n_labels=("label", "nunique"),
            min_task_idx=("task_idx", "min"),
            max_task_idx=("task_idx", "max"),
            mean_strength=("strength", "mean"),
        )
        .sort_values(["event_role", "event_class"])
    )


def input_hash_manifest(input_root: Path, b5_1) -> pd.DataFrame:
    rows = []
    for rel_path in b5_1.INPUT_FILES:
        path = input_root / rel_path
        if not path.exists():
            raise FileNotFoundError(f"missing input file: {path}")
        rows.append(
            {
                "relative_path": rel_path,
                "absolute_path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return pd.DataFrame(rows)


def write_summary(
    path: Path,
    results: pd.DataFrame,
    inventory: pd.DataFrame,
    nulls: pd.DataFrame,
    args: argparse.Namespace,
) -> None:
    endogenous = results[results["condition"].eq("endogenous")].copy()
    primary = endogenous[endogenous["event_class"].eq(PRIMARY_EVENT)].copy()
    contrast = endogenous[endogenous["event_class"].isin(CONTRAST_EVENTS)].copy()
    coherence = endogenous[endogenous["event_class"].isin(COHERENCE_EVENTS)].copy()
    primary_candidate = bool(primary["mechanism_candidate"].iloc[0]) if not primary.empty else False
    primary_cols = [
        "event_class",
        "event_role",
        "mean_branch_transition_differentiated",
        "effect_vs_time_shifted",
        "effect_vs_random_event",
        "effect_vs_degree_null_mean",
        "p_vs_time_shifted_and_random",
        "branch_transition_q_value",
        "p_vs_degree_null",
        "p_vs_non_phi_contrast_switches",
        "branch_transition_score",
        "branch_flip_fraction",
        "branch_minus_abs_generic_improvement",
        "late_branch_stability",
        "passes_branch_specificity_gate",
        "passes_null_gate",
        "mechanism_candidate",
    ]
    null_summary = (
        nulls.groupby(["event_class", "event_role"], as_index=False)
        .agg(
            n_null_graphs=("null_index", "nunique"),
            mean_null_branch_transition=("mean_branch_transition_differentiated", "mean"),
            sd_null_branch_transition=("mean_branch_transition_differentiated", "std"),
        )
        if not nulls.empty
        else pd.DataFrame()
    )
    lines = [
        "# Stage B5.3 Hybrid Phi/FES Sign-Switch and C12 6+6 Dual-Branch Transition Summary",
        "",
        "## Purpose",
        "",
        "B5.3 tests whether `hybrid_phi_sign_switch` corresponds to a C12-internal 6+6 dual-branch transition. The endpoint is branch-transition structure, not stable C12 carrier closure.",
        "",
        "## Run Parameters",
        "",
        f"- input root: `{args.input_root}`",
        f"- output dir: `{args.output_dir}`",
        f"- steps: {args.steps}",
        f"- runs per condition: {args.n_runs}",
        f"- degree-null graphs per event class: {args.n_null_graphs}",
        f"- runs per degree-null graph: {args.n_null_runs}",
        f"- recovery window: {args.recovery_window}",
        f"- seed: {args.seed}",
        "",
        "## Overall Result",
        "",
        f"- primary mechanism candidate: {primary_candidate}",
        "- interpretation boundary: transition-like C12 branch readout only; not stable carrier closure.",
        "",
        "## Primary Event",
        "",
        primary[primary_cols].to_csv(index=False).strip() if not primary.empty else "missing primary row",
        "",
        "## Coherence Probes",
        "",
        coherence[primary_cols].to_csv(index=False).strip() if not coherence.empty else "missing coherence rows",
        "",
        "## Non-Phi Contrast Switches",
        "",
        contrast[primary_cols].to_csv(index=False).strip() if not contrast.empty else "missing contrast rows",
        "",
        "## All Endogenous Rows",
        "",
        endogenous[primary_cols].to_csv(index=False).strip(),
        "",
        "## Event Inventory",
        "",
        inventory.to_csv(index=False).strip(),
        "",
        "## Degree-Null Summary",
        "",
        null_summary.to_csv(index=False).strip(),
        "",
        "## Interpretation Boundary",
        "",
        "B5.3 remains negative or inconclusive for the proposed mechanism if non-Phi switches or nulls reproduce the same 6+6 branch-transition pattern, or if the effect is generic C12 recovery rather than branch-specific transition structure.",
    ]
    path.write_text("\n".join(lines) + "\n")


def run(args: argparse.Namespace) -> None:
    b5_1 = load_b5_1_module()
    b3 = b5_1.load_b3_module()
    input_root = Path(args.input_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    events = b5_1.load_b5_1_event_rows(input_root)
    hashes = input_hash_manifest(input_root, b5_1)
    inventory = event_inventory(events)

    result_rows: list[dict[str, object]] = []
    run_tables: list[pd.DataFrame] = []
    null_rows: list[dict[str, object]] = []
    for event_class in EVENT_CLASSES:
        rows, run_dfs, nulls = evaluate_event_class(
            b3,
            events,
            event_class,
            args.steps,
            args.n_runs,
            args.n_null_graphs,
            args.n_null_runs,
            rng,
            args.recovery_window,
        )
        result_rows.extend(rows)
        run_tables.extend(run_dfs)
        null_rows.extend(nulls)

    run_values = pd.concat(run_tables, ignore_index=True)
    null_df = pd.DataFrame(null_rows)
    results = add_cross_event_decisions(pd.DataFrame(result_rows), run_values)

    results.to_csv(output_dir / f"{OUTPUT_PREFIX}_results.csv", index=False)
    run_values.to_csv(output_dir / f"{OUTPUT_PREFIX}_run_values.csv", index=False)
    null_df.to_csv(output_dir / f"{OUTPUT_PREFIX}_null_graphs.csv", index=False)
    inventory.to_csv(output_dir / f"{OUTPUT_PREFIX}_event_inventory.csv", index=False)
    hashes.to_csv(output_dir / f"{OUTPUT_PREFIX}_input_hashes.csv", index=False)
    write_summary(output_dir / f"{OUTPUT_PREFIX}_summary.md", results, inventory, null_df, args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output-dir", default="reports/stage_b5_3")
    parser.add_argument("--n-runs", type=int, default=400)
    parser.add_argument("--n-null-graphs", type=int, default=80)
    parser.add_argument("--n-null-runs", type=int, default=5)
    parser.add_argument("--steps", type=int, default=240)
    parser.add_argument("--recovery-window", type=int, default=18)
    parser.add_argument("--seed", type=int, default=53053)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
