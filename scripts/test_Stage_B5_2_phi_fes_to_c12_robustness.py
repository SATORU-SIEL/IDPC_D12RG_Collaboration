#!/usr/bin/env python3
"""Stage B5.2 Phi/FES-to-C12 robustness and decomposition audit."""

from __future__ import annotations

import argparse
import importlib.util
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


B5_1_SCRIPT = Path(__file__).with_name("test_Stage_B5_1_phi_fes_to_c12_bridge.py")
OUTPUT_PREFIX = "Stage_B5_2_phi_fes_to_c12_robustness"
FDR_ALPHA = 0.05


def load_b5_1_module():
    spec = importlib.util.spec_from_file_location("stage_b5_1", B5_1_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import Stage B5.1 script: {B5_1_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def rescale_schedule_steps(schedule: list[dict[str, float]], source_min: float, source_max: float, target_min: float, target_max: float, steps: int) -> list[dict[str, float]]:
    source_denom = max(source_max - source_min, 1.0)
    target_denom = max(target_max - target_min, 1.0)
    out = []
    for item in schedule:
        frac = (float(item["task_idx"]) - source_min) / source_denom
        target_task = target_min + frac * target_denom
        step = int(np.clip(round(((target_task - target_min) / target_denom) * (steps - 1)), 0, steps - 1))
        copied = dict(item)
        copied["step"] = step
        out.append(copied)
    return out


def simulate_series(
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
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0.0, 2.0 * np.pi, size=n_nodes)
    omega = rng.normal(0.0, 0.012, size=n_nodes)
    incoming = [[] for _ in range(n_nodes)]
    for i, j in edges:
        incoming[j].append(i)
    by_step: dict[int, list[dict[str, float]]] = defaultdict(list)
    for event in event_schedule:
        by_step[int(event["step"])].append(event)
    d12, d24, diff, order, vel = [], [], [], [], []
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
        order.append(b3.order_parameter(theta))
        d12.append(b3.grid_score(theta, 12))
        d24.append(b3.grid_score(theta, 24))
        diff.append(b3.differentiation_score(theta, 12))
        vel.append(float(np.linalg.norm(dt * delta) / max(1, n_nodes)))
    return {
        "D12": np.asarray(d12, dtype=float),
        "D24": np.asarray(d24, dtype=float),
        "diff": np.asarray(diff, dtype=float),
        "order": np.asarray(order, dtype=float),
        "vel": np.asarray(vel, dtype=float),
    }


def temporal_profile(
    b3,
    event_class: str,
    schedule: list[dict[str, float]],
    n_nodes: int,
    edges: list[tuple[int, int]],
    n_runs: int,
    steps: int,
    rng: np.random.Generator,
    recovery_window: int = 18,
) -> dict[str, object]:
    event_steps = sorted({int(x["step"]) for x in schedule if 0 <= int(x["step"]) < steps})
    if not event_steps:
        return {"event_class": event_class, "n_event_steps": 0}
    cut1, cut2 = np.quantile(event_steps, [1.0 / 3.0, 2.0 / 3.0])
    bucket_values: dict[str, list[float]] = {"early": [], "mid": [], "late": []}
    late_stability = []
    final_readout = []
    for _ in range(n_runs):
        series = simulate_series(
            b3,
            n_nodes,
            edges,
            schedule,
            int(rng.integers(0, 2**31 - 1)),
            steps=steps,
        )
        readout = np.maximum(series["D12"], series["D24"])
        late_stability.append(b3.stability_score(readout[-40:].tolist()))
        final_readout.append(float(np.mean(readout[-40:])))
        for step in event_steps:
            pre_start = max(0, step - recovery_window)
            post_end = min(steps, step + recovery_window + 1)
            if step <= pre_start or post_end <= step + 1:
                continue
            improvement = float(np.mean(readout[step + 1 : post_end]) - np.mean(readout[pre_start:step]))
            bucket = "early" if step <= cut1 else ("mid" if step <= cut2 else "late")
            bucket_values[bucket].append(improvement)
    return {
        "event_class": event_class,
        "n_event_steps": len(event_steps),
        "min_step": int(min(event_steps)),
        "max_step": int(max(event_steps)),
        "early_improvement": float(np.mean(bucket_values["early"])) if bucket_values["early"] else np.nan,
        "mid_improvement": float(np.mean(bucket_values["mid"])) if bucket_values["mid"] else np.nan,
        "late_improvement": float(np.mean(bucket_values["late"])) if bucket_values["late"] else np.nan,
        "early_n": len(bucket_values["early"]),
        "mid_n": len(bucket_values["mid"]),
        "late_n": len(bucket_values["late"]),
        "mean_late_window_stability": float(np.nanmean(late_stability)),
        "mean_final_readout": float(np.nanmean(final_readout)),
    }


def fdr_sensitivity(raw_result: pd.DataFrame, b5_1) -> pd.DataFrame:
    endogenous = raw_result[
        raw_result["condition"].eq("endogenous") & raw_result["topology_name"].eq("C12(1,2)")
    ].copy()
    families = [
        ("all_endogenous_c12", endogenous),
        ("primary_phi_fes_only", endogenous[endogenous["event_role"].eq("primary_phi_fes")]),
        (
            "primary_plus_secondary_phi_reference",
            endogenous[endogenous["event_role"].isin(["primary_phi_fes", "secondary_phi_reference"])],
        ),
        ("contrast_switch_only", endogenous[endogenous["event_role"].eq("contrast_switch")]),
    ]
    rows = []
    for family, sub in families:
        sub = sub.copy()
        sub["family_q_value"] = bh_fdr(sub["p_vs_time_shifted_and_random"].astype(float).tolist())
        for _, row in sub.iterrows():
            rows.append(
                {
                    "family": family,
                    "family_n": len(sub),
                    "event_class": row["event_class"],
                    "event_role": row["event_role"],
                    "p_vs_time_shifted_and_random": row["p_vs_time_shifted_and_random"],
                    "family_q_value": row["family_q_value"],
                    "passes_family_fdr": bool(row["family_q_value"] <= FDR_ALPHA),
                    "primary_interpretation_boundary": "B5.1 primary interpretation remains all_endogenous_c12",
                }
            )
    return pd.DataFrame(rows)


def directional_concordance(raw_result: pd.DataFrame) -> pd.DataFrame:
    primary = raw_result[
        raw_result["condition"].eq("endogenous")
        & raw_result["topology_name"].eq("C12(1,2)")
        & raw_result["event_role"].eq("primary_phi_fes")
    ].copy()
    rows = []
    for effect_col in [
        "effect_vs_time_shifted",
        "effect_vs_random_event",
        "effect_vs_C8",
        "effect_vs_degree_null_mean",
    ]:
        signs = primary[effect_col].astype(float) > 0
        n_positive = int(signs.sum())
        n_total = int(signs.notna().sum())
        rows.append(
            {
                "effect_family": effect_col,
                "n_primary_events": n_total,
                "n_positive_direction": n_positive,
                "all_positive": bool(n_total > 0 and n_positive == n_total),
                "secondary_sign_test_p_all_positive": float(0.5**n_total) if n_total else np.nan,
                "interpretation": "secondary directional concordance only; not confirmatory",
            }
        )
    all_values = []
    for effect_col in [
        "effect_vs_time_shifted",
        "effect_vs_random_event",
        "effect_vs_C8",
        "effect_vs_degree_null_mean",
    ]:
        all_values.extend((primary[effect_col].astype(float) > 0).tolist())
    rows.append(
        {
            "effect_family": "all_four_effect_families",
            "n_primary_events": len(all_values),
            "n_positive_direction": int(np.sum(all_values)),
            "all_positive": bool(all(all_values)),
            "secondary_sign_test_p_all_positive": float(0.5 ** len(all_values)) if all_values else np.nan,
            "interpretation": "descriptive only because signs are not independent",
        }
    )
    return pd.DataFrame(rows)


def event_inventory(events: pd.DataFrame) -> pd.DataFrame:
    return (
        events.groupby(["event_class", "event_role", "source_file", "event_rule"], as_index=False)
        .agg(
            n_events=("task_idx", "size"),
            n_labels=("label", "nunique"),
            min_task_idx=("task_idx", "min"),
            max_task_idx=("task_idx", "max"),
            mean_strength=("strength", "mean"),
        )
        .sort_values(["event_role", "event_class"])
    )


def evaluate_normalized_schedule(
    b3,
    b5_1,
    event_class: str,
    event_role: str,
    rows: pd.DataFrame,
    steps: int,
    n_runs: int,
    rng: np.random.Generator,
) -> dict[str, object]:
    _, c12_nodes, c12_edges, _, _ = b3.topology_definition("C12(1,2)")
    _, c8_nodes, c8_edges, _, _ = b3.topology_definition("C8(1)")
    c12_schedule, meta = b3.build_event_schedule(rows, event_class, steps, c12_nodes)
    c8_schedule, _ = b3.build_event_schedule(rows, event_class, steps, c8_nodes)
    if not c12_schedule:
        return {}
    shifted = b3.shifted_schedule(c12_schedule, steps, shift=max(7, steps // 5))
    c12_end_values, c12_end_avg = b5_1.simulate_many(b3, c12_nodes, c12_edges, c12_schedule, n_runs, steps, rng)
    c12_shift_values, _ = b5_1.simulate_many(b3, c12_nodes, c12_edges, shifted, n_runs, steps, rng)
    random_values = []
    for _ in range(n_runs):
        random_schedule = b3.random_schedule(c12_schedule, steps, rng)
        metric = b3.simulate_event_conditioned(
            c12_nodes,
            c12_edges,
            random_schedule,
            int(rng.integers(0, 2**31 - 1)),
            steps=steps,
        )
        random_values.append(metric.get("differentiated_recovery", np.nan))
    random_values = np.asarray(random_values, dtype=float)
    c8_values, _ = b5_1.simulate_many(b3, c8_nodes, c8_edges, c8_schedule, n_runs, steps, rng)
    obs = float(np.nanmean(c12_end_values))
    shift_mean = float(np.nanmean(c12_shift_values))
    random_mean = float(np.nanmean(random_values))
    c8_mean = float(np.nanmean(c8_values))
    return {
        "event_class": event_class,
        "event_role": event_role,
        "n_runs": n_runs,
        "n_seed_events": meta["n_events"],
        "mean_seed_strength": meta["mean_strength"],
        "total_impulse_budget": meta["total_impulse_budget"],
        "mean_bounded_differentiated_recovery": obs,
        "sd_bounded_differentiated_recovery": float(np.nanstd(c12_end_values)),
        "effect_vs_time_shifted": obs - shift_mean,
        "effect_vs_random_event": obs - random_mean,
        "effect_vs_C8": obs - c8_mean,
        "p_vs_time_shifted_and_random": p_greater(obs, np.r_[c12_shift_values, random_values]),
        "p_vs_C8": p_greater(obs, c8_values),
        "D12_recovery": c12_end_avg.get("D12_recovery", np.nan),
        "D24_recovery": c12_end_avg.get("D24_recovery", np.nan),
        "D12_D24_recovery_improvement": c12_end_avg.get("D12_D24_recovery_improvement", np.nan),
        "bounded_non_runaway_score": c12_end_avg.get("bounded_non_runaway_score", np.nan),
        "non_collapsed_differentiation_score": c12_end_avg.get("non_collapsed_differentiation_score", np.nan),
        "late_window_stability": c12_end_avg.get("late_window_stability", np.nan),
        "post_event_readout_score": c12_end_avg.get("post_event_readout_score", np.nan),
    }


def normalization_audit(
    b3,
    b5_1,
    events: pd.DataFrame,
    steps: int,
    n_runs: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    rows_out = []
    comparison_events = b5_1.SECONDARY_EVENTS + b5_1.CONTRAST_EVENTS
    for primary_class in b5_1.PRIMARY_EVENTS:
        primary_rows = events[events["event_class"].eq(primary_class)].copy()
        primary_min = float(primary_rows["task_idx"].min())
        primary_max = float(primary_rows["task_idx"].max())
        primary_count = int(len(primary_rows))
        for comparison_class in comparison_events:
            base_rows = events[events["event_class"].eq(comparison_class)].copy()
            role = str(base_rows["event_role"].iloc[0])
            interval_rows = base_rows[
                (base_rows["task_idx"].astype(float) >= primary_min)
                & (base_rows["task_idx"].astype(float) <= primary_max)
            ].copy()
            variants = [
                ("primary_interval_only", interval_rows),
                ("primary_interval_count_matched", interval_rows),
            ]
            for variant, candidate_rows in variants:
                candidate_rows = candidate_rows.copy()
                available_count = int(len(candidate_rows))
                count_match_complete = available_count >= primary_count
                if variant == "primary_interval_count_matched" and available_count > primary_count:
                    sample_seed = int(rng.integers(0, 2**31 - 1))
                    candidate_rows = candidate_rows.sample(n=primary_count, replace=False, random_state=sample_seed)
                if candidate_rows.empty:
                    rows_out.append(
                        {
                            "primary_reference_event": primary_class,
                            "comparison_event": comparison_class,
                            "comparison_role": role,
                            "normalization_variant": variant,
                            "primary_task_min": primary_min,
                            "primary_task_max": primary_max,
                            "primary_event_count": primary_count,
                            "available_event_count": available_count,
                            "sampled_event_count": 0,
                            "count_match_complete": False,
                            "normalization_status": "no_events_after_interval_restriction",
                        }
                    )
                    continue
                evaluated = evaluate_normalized_schedule(
                    b3,
                    b5_1,
                    comparison_class,
                    role,
                    candidate_rows,
                    steps,
                    n_runs,
                    rng,
                )
                evaluated.update(
                    {
                        "primary_reference_event": primary_class,
                        "comparison_event": comparison_class,
                        "comparison_role": role,
                        "normalization_variant": variant,
                        "primary_task_min": primary_min,
                        "primary_task_max": primary_max,
                        "primary_event_count": primary_count,
                        "available_event_count": available_count,
                        "sampled_event_count": int(len(candidate_rows)),
                        "count_match_complete": bool(count_match_complete),
                        "normalization_status": "evaluated",
                    }
                )
                rows_out.append(evaluated)
    return pd.DataFrame(rows_out)


def write_manifest(path: Path, args: argparse.Namespace, hashes: pd.DataFrame) -> None:
    lines = [
        "# Stage B5.2 Phi/FES-to-C12 Robustness Audit Manifest",
        "",
        f"- input root: `{args.input_root}`",
        f"- output dir: `{args.output_dir}`",
        f"- simulation steps: {args.steps}",
        f"- runs per raw topology/condition: {args.n_runs}",
        f"- degree-matched null graphs per event class: {args.n_null_graphs}",
        f"- runs per null graph: {args.n_null_runs}",
        f"- temporal profile runs: {args.temporal_runs}",
        f"- normalization runs: {args.normalization_runs}",
        f"- random seed: {args.seed}",
        "- primary topology: C12(1,2)",
        "- contrast topology: C8(1)",
        "- primary endpoint: bounded_differentiated_recovery",
        "",
        "## Input Hashes",
        "",
        hashes.to_csv(index=False).strip(),
    ]
    path.write_text("\n".join(lines) + "\n")


def write_summary(
    path: Path,
    raw: pd.DataFrame,
    fdr: pd.DataFrame,
    concordance: pd.DataFrame,
    temporal: pd.DataFrame,
    normalization: pd.DataFrame,
    inventory: pd.DataFrame,
    null_df: pd.DataFrame,
) -> None:
    primary = raw[
        raw["condition"].eq("endogenous")
        & raw["topology_name"].eq("C12(1,2)")
        & raw["event_role"].eq("primary_phi_fes")
    ].copy()
    contrast = raw[
        raw["condition"].eq("endogenous")
        & raw["topology_name"].eq("C12(1,2)")
        & raw["event_role"].eq("contrast_switch")
    ].copy()
    primary_cols = [
        "event_class",
        "mean_bounded_differentiated_recovery",
        "effect_vs_time_shifted",
        "effect_vs_random_event",
        "effect_vs_C8",
        "effect_vs_degree_null_mean",
        "p_vs_time_shifted_and_random",
        "primary_q_value",
        "p_vs_C8",
        "p_vs_degree_null",
        "bounded_non_runaway_score",
        "non_collapsed_differentiation_score",
        "late_window_stability",
        "passes_effect_controls",
        "passes_stability_gates",
        "passes_contrast_switch_gate",
        "positive_candidate",
    ]
    norm_evaluated = normalization[normalization.get("normalization_status", pd.Series(dtype=str)).eq("evaluated")].copy()
    if not norm_evaluated.empty:
        norm_top = norm_evaluated.sort_values("mean_bounded_differentiated_recovery", ascending=False).head(12)
    else:
        norm_top = norm_evaluated
    positive = int(primary.get("positive_candidate", pd.Series(dtype=bool)).sum()) if not primary.empty else 0
    all_primary_directional = bool(
        not primary.empty
        and (primary["effect_vs_time_shifted"] > 0).all()
        and (primary["effect_vs_random_event"] > 0).all()
        and (primary["effect_vs_C8"] > 0).all()
        and (primary["effect_vs_degree_null_mean"] > 0).all()
    )
    lines = [
        "# Stage B5.2 Phi/FES-to-C12 Robustness and Decomposition Audit Summary",
        "",
        "## Purpose",
        "",
        "B5.2 decomposes the B5.1 near-threshold Phi/FES-to-C12 signal. It does not reinterpret B5.1 as confirmatory positive.",
        "",
        "## Overall Result",
        "",
        f"- positive primary candidates under unchanged B5.1-style gates: {positive}",
        f"- all three primary Phi/FES classes remain C12-directional across four effect contrasts: {all_primary_directional}",
        "",
        "The B5.2 interpretation should remain diagnostic. B5.2 can justify a stricter later replication only if the signal is robust to gate-failure decomposition, null behavior, contrast-switch checks, and event-space normalization.",
        "",
        "## Primary Phi/FES Gate Decomposition",
        "",
        primary[primary_cols].to_csv(index=False).strip(),
        "",
        "## FDR Family Sensitivity",
        "",
        fdr.to_csv(index=False).strip(),
        "",
        "## Directional Concordance",
        "",
        concordance.to_csv(index=False).strip(),
        "",
        "## Temporal Profile",
        "",
        temporal.to_csv(index=False).strip(),
        "",
        "## Contrast Switch Rows",
        "",
        contrast[primary_cols].to_csv(index=False).strip(),
        "",
        "## Event-Space Normalization: strongest evaluated comparison rows",
        "",
        norm_top.to_csv(index=False).strip(),
        "",
        "## Event Inventory",
        "",
        inventory.to_csv(index=False).strip(),
        "",
        "## Null Graph Summary",
        "",
        null_df.groupby(["event_class", "event_role"], as_index=False).agg(
            n_null_graphs=("null_index", "nunique"),
            mean_null_recovery=("mean_bounded_differentiated_recovery", "mean"),
            sd_null_recovery=("mean_bounded_differentiated_recovery", "std"),
        ).to_csv(index=False).strip(),
        "",
        "## Interpretation Boundary",
        "",
        "B5.2 is a robustness/decomposition audit. It does not prove IDPC, D12RG, C12 as a physical carrier, or a final ontology.",
    ]
    path.write_text("\n".join(lines) + "\n")


def run(args: argparse.Namespace) -> None:
    b5_1 = load_b5_1_module()
    b3 = b5_1.load_b3_module()
    input_root = Path(args.input_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    hashes = b5_1.input_hash_manifest(input_root)
    events = b5_1.load_b5_1_event_rows(input_root)
    inventory = event_inventory(events)

    raw_rows: list[dict[str, object]] = []
    null_rows: list[dict[str, object]] = []
    for event_class in b5_1.EVENT_CLASSES:
        rows, nulls = b5_1.evaluate_event_class(
            b3,
            events,
            event_class,
            args.steps,
            args.n_runs,
            args.n_null_graphs,
            args.n_null_runs,
            rng,
        )
        raw_rows.extend(rows)
        null_rows.extend(nulls)
    raw = b5_1.add_primary_decisions(pd.DataFrame(raw_rows))
    null_df = pd.DataFrame(null_rows)

    _, c12_nodes, c12_edges, _, _ = b3.topology_definition("C12(1,2)")
    temporal_rows = []
    for event_class in b5_1.PRIMARY_EVENTS:
        event_rows = events[events["event_class"].eq(event_class)].copy()
        schedule, _ = b3.build_event_schedule(event_rows, event_class, args.steps, c12_nodes)
        temporal_rows.append(
            temporal_profile(
                b3,
                event_class,
                schedule,
                c12_nodes,
                c12_edges,
                args.temporal_runs,
                args.steps,
                rng,
            )
        )
    temporal = pd.DataFrame(temporal_rows)
    fdr = fdr_sensitivity(raw, b5_1)
    concordance = directional_concordance(raw)
    normalization = normalization_audit(
        b3,
        b5_1,
        events,
        args.steps,
        args.normalization_runs,
        rng,
    )

    raw.to_csv(output_dir / f"{OUTPUT_PREFIX}_results.csv", index=False)
    null_df.to_csv(output_dir / f"{OUTPUT_PREFIX}_null_graphs.csv", index=False)
    temporal.to_csv(output_dir / f"{OUTPUT_PREFIX}_temporal_profile.csv", index=False)
    fdr.to_csv(output_dir / f"{OUTPUT_PREFIX}_fdr_sensitivity.csv", index=False)
    concordance.to_csv(output_dir / f"{OUTPUT_PREFIX}_directional_concordance.csv", index=False)
    normalization.to_csv(output_dir / f"{OUTPUT_PREFIX}_event_space_normalization.csv", index=False)
    inventory.to_csv(output_dir / f"{OUTPUT_PREFIX}_event_inventory.csv", index=False)
    hashes.to_csv(output_dir / f"{OUTPUT_PREFIX}_input_hashes.csv", index=False)
    write_manifest(output_dir / f"{OUTPUT_PREFIX}_manifest.md", args, hashes)
    write_summary(
        output_dir / f"{OUTPUT_PREFIX}_summary.md",
        raw,
        fdr,
        concordance,
        temporal,
        normalization,
        inventory,
        null_df,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--n-runs", type=int, default=400)
    parser.add_argument("--n-null-graphs", type=int, default=120)
    parser.add_argument("--n-null-runs", type=int, default=25)
    parser.add_argument("--temporal-runs", type=int, default=240)
    parser.add_argument("--normalization-runs", type=int, default=240)
    parser.add_argument("--steps", type=int, default=240)
    parser.add_argument("--seed", type=int, default=20260609)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
