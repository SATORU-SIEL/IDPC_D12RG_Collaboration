#!/usr/bin/env python3
"""Stage B3.2 mu-sector dynamic expectation audit.

This audit tests preregistered temporal-profile expectations for mu sectors.
It is a secondary diagnostic and does not revise the Stage B3 primary result.
"""

from __future__ import annotations

import argparse
import importlib.util
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


B3_SCRIPT = Path(__file__).with_name("test_Stage_B3_endogenous_event_carrier_readout.py")
PRIMARY_TOPOLOGY = "C12(1,2)"
TARGET_MU_SECTORS = (3, 4, 5, 6, 8, 9, 10, 12, 16, 20, 24)
ARTIFACT_MU_SECTORS = (60, 120)
ALL_MU_SECTORS = TARGET_MU_SECTORS + ARTIFACT_MU_SECTORS
CONDITIONS = ("endogenous", "time_shifted", "random_event")

EXPECTATIONS = {
    3: {
        "label": "critical_instability_stability",
        "events": ("FES_phase_transition", "high_boundary_impulse_J"),
        "metric": "variance_spike_score",
        "role": "target",
    },
    4: {
        "label": "eps72_linked_closure",
        "events": ("eps72_restoration_onset",),
        "metric": "post_event_recovery",
        "role": "target",
    },
    5: {
        "label": "transient_lift_dropback",
        "events": ("FES_phase_transition", "h_zero_crossing", "eps72_restoration_onset"),
        "metric": "transient_lift_dropback_score",
        "role": "target",
    },
    6: {
        "label": "dual_chirality_ambiguity",
        "events": ("h_zero_crossing", "FES_phase_transition"),
        "metric": "oscillatory_chirality_score",
        "role": "target",
    },
    8: {
        "label": "contrast_grid_artifact_check",
        "events": ("h_zero_crossing",),
        "metric": "artifact_dominance_score",
        "role": "contrast",
    },
    9: {
        "label": "eps72_dodecahedral_exploratory",
        "events": ("eps72_restoration_onset",),
        "metric": "post_event_recovery",
        "role": "target",
    },
    10: {
        "label": "double_fivefold_transient_lift",
        "events": ("FES_phase_transition", "eps72_restoration_onset"),
        "metric": "transient_lift_dropback_score",
        "role": "target",
    },
    12: {
        "label": "C12_temporal_readout",
        "events": ("h_zero_crossing",),
        "metric": "post_event_recovery",
        "role": "target",
    },
    16: {
        "label": "secondary_artifact_contrast_monitor",
        "events": tuple(),
        "metric": "artifact_dominance_score",
        "role": "contrast",
    },
    20: {
        "label": "fivefold_time_interaction",
        "events": ("h_zero_crossing", "FES_phase_transition"),
        "metric": "transient_or_recovery_score",
        "role": "target",
    },
    24: {
        "label": "D24_lifted_C12_eps72",
        "events": ("eps72_restoration_onset",),
        "metric": "post_event_recovery",
        "role": "target",
    },
    60: {
        "label": "Phi12_derived_artifact_readout",
        "events": tuple(),
        "metric": "artifact_monitor_score",
        "role": "derived_artifact",
    },
    120: {
        "label": "Phi24_derived_artifact_readout",
        "events": tuple(),
        "metric": "artifact_monitor_score",
        "role": "derived_artifact",
    },
}


def load_b3_module():
    spec = importlib.util.spec_from_file_location("stage_b3", B3_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import Stage B3 script: {B3_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def adjacency_matrix(n_nodes: int, edges: list[tuple[int, int]]) -> np.ndarray:
    adj = np.zeros((n_nodes, n_nodes), dtype=np.int64)
    for i, j in edges:
        adj[int(i), int(j)] += 1
    return adj


def closed_walk_counts(n_nodes: int, edges: list[tuple[int, int]]) -> dict[int, int]:
    adj = adjacency_matrix(n_nodes, edges).astype(object)
    power = np.eye(n_nodes, dtype=object)
    counts = {}
    for length in range(1, max(ALL_MU_SECTORS) + 1):
        power = power @ adj
        if length in ALL_MU_SECTORS:
            counts[length] = int(np.trace(power))
    return counts


def circular_jump_count(phases: list[float], threshold: float = np.pi / 2.0) -> float:
    if len(phases) < 2:
        return np.nan
    diffs = np.diff(np.unwrap(np.asarray(phases, dtype=float)))
    return float(np.mean(np.abs(diffs) > threshold))


def simulate_dynamic(
    b3,
    n_nodes: int,
    edges: list[tuple[int, int]],
    event_schedule: list[dict[str, float]],
    seed: int,
    steps: int,
    recovery_window: int,
    dt: float = 0.06,
    coupling: float = 0.34,
    second_harmonic: float = 0.04,
) -> dict[int, dict[str, float]]:
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0.0, 2.0 * np.pi, size=n_nodes)
    omega = rng.normal(0.0, 0.012, size=n_nodes)
    incoming = [[] for _ in range(n_nodes)]
    for i, j in edges:
        incoming[j].append(i)
    by_step: dict[int, list[dict[str, float]]] = defaultdict(list)
    for event in event_schedule:
        by_step[int(event["step"])].append(event)

    score_series = {sector: [] for sector in ALL_MU_SECTORS}
    harmonic_phase = {sector: [] for sector in ALL_MU_SECTORS}
    generic_order = []
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
        generic_order.append(b3.order_parameter(theta))
        for sector in ALL_MU_SECTORS:
            score_series[sector].append(b3.grid_score(theta, sector))
            harmonic_phase[sector].append(float(np.angle(np.mean(np.exp(1j * sector * theta)))))
    return summarize_dynamic(event_schedule, score_series, harmonic_phase, generic_order, recovery_window)


def summarize_dynamic(
    schedule: list[dict[str, float]],
    score_series: dict[int, list[float]],
    harmonic_phase: dict[int, list[float]],
    generic_order: list[float],
    recovery_window: int,
) -> dict[int, dict[str, float]]:
    steps = len(generic_order)
    event_steps = sorted({int(x["step"]) for x in schedule if 0 <= int(x["step"]) < steps})
    out = {}
    for sector, series in score_series.items():
        recovery = []
        peak_delta = []
        onset_latency = []
        dropback = []
        variance_spike = []
        oscillation = []
        chirality_switch = []
        generic_recovery = []
        for step in event_steps:
            pre_start = max(0, step - recovery_window)
            post_end = min(steps, step + recovery_window + 1)
            if step <= pre_start or post_end <= step + 3:
                continue
            pre = np.asarray(series[pre_start:step], dtype=float)
            post = np.asarray(series[step + 1:post_end], dtype=float)
            pre_generic = np.asarray(generic_order[pre_start:step], dtype=float)
            post_generic = np.asarray(generic_order[step + 1:post_end], dtype=float)
            post_phase = harmonic_phase[sector][step + 1:post_end]
            baseline = float(np.mean(pre))
            post_mean = float(np.mean(post))
            peak_idx = int(np.argmax(post))
            peak_value = float(post[peak_idx])
            tail = post[max(1, len(post) - max(3, recovery_window // 3)) :]
            post_diff = np.diff(post)
            recovery.append(post_mean - baseline)
            peak_delta.append(peak_value - baseline)
            onset_latency.append(peak_idx + 1)
            dropback.append(peak_value - float(np.mean(tail)))
            variance_spike.append(float(np.std(post) - np.std(pre)))
            oscillation.append(float(np.mean(np.abs(np.diff(post_diff)))) if len(post_diff) > 1 else np.nan)
            chirality_switch.append(circular_jump_count(post_phase))
            generic_recovery.append(float(np.mean(post_generic) - np.mean(pre_generic)))
        if not recovery:
            out[sector] = {key: np.nan for key in metric_keys()}
            out[sector]["n_events_evaluated"] = 0
            continue
        rec = float(np.mean(recovery))
        pk = float(np.mean(peak_delta))
        db = float(np.mean(dropback))
        var = float(np.mean(variance_spike))
        osc = float(np.mean(oscillation))
        chi = float(np.mean(chirality_switch))
        gen = float(np.mean(generic_recovery))
        out[sector] = {
            "n_events_evaluated": len(recovery),
            "post_event_recovery": rec,
            "peak_delta": pk,
            "onset_latency": float(np.mean(onset_latency)),
            "dropback_score": db,
            "variance_spike_score": var,
            "oscillatory_switching_score": osc,
            "chirality_switching_score": chi,
            "oscillatory_chirality_score": osc + chi,
            "transient_lift_dropback_score": max(pk, 0.0) * max(db, 0.0),
            "transient_or_recovery_score": max(rec, max(pk, 0.0) * max(db, 0.0)),
            "generic_phase_recovery": gen,
            "sector_specificity_score": rec - gen,
            "artifact_monitor_score": max(pk, 0.0) * max(db, 0.0),
            "artifact_dominance_score": rec - gen,
        }
    return out


def metric_keys() -> list[str]:
    return [
        "n_events_evaluated",
        "post_event_recovery",
        "peak_delta",
        "onset_latency",
        "dropback_score",
        "variance_spike_score",
        "oscillatory_switching_score",
        "chirality_switching_score",
        "oscillatory_chirality_score",
        "transient_lift_dropback_score",
        "transient_or_recovery_score",
        "generic_phase_recovery",
        "sector_specificity_score",
        "artifact_monitor_score",
        "artifact_dominance_score",
    ]


def average_runs(items: list[dict[int, dict[str, float]]]) -> dict[int, dict[str, float]]:
    out = {}
    for sector in ALL_MU_SECTORS:
        out[sector] = {}
        for key in metric_keys():
            vals = np.asarray([item[sector].get(key, np.nan) for item in items], dtype=float)
            finite = vals[np.isfinite(vals)]
            out[sector][key] = float(np.mean(finite)) if len(finite) else np.nan
            out[sector][f"{key}_sd"] = float(np.std(finite)) if len(finite) else np.nan
    return out


def p_greater(observed: float, controls: list[float]) -> float:
    control = np.asarray(controls, dtype=float)
    control = control[np.isfinite(control)]
    if not np.isfinite(observed) or len(control) == 0:
        return np.nan
    return float((1.0 + np.sum(control >= observed)) / (len(control) + 1.0))


def bh_fdr(values: list[float]) -> list[float]:
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


def run_audit(
    input_root: Path,
    output_dir: Path,
    n_runs: int,
    seed: int,
    steps: int,
    recovery_window: int,
) -> pd.DataFrame:
    b3 = load_b3_module()
    rng = np.random.default_rng(seed)
    input_hashes = b3.input_hash_manifest(input_root)
    events = b3.load_b3_event_rows(input_root)
    event_classes = [event_class for event_class in b3.EVENT_CLASSES if event_class in set(events["event_class"])]
    topology_names = [PRIMARY_TOPOLOGY, "C8(1)", "dodecahedron", "icosahedron"]
    rows = []
    for topology_name in topology_names:
        topology_class, n_nodes, edges, convention, notes = b3.topology_definition(topology_name)
        walk_counts = closed_walk_counts(n_nodes, edges)
        for event_class in event_classes:
            endogenous, meta = b3.build_event_schedule(events, event_class, steps, n_nodes)
            if not endogenous:
                continue
            schedules = {
                "endogenous": endogenous,
                "time_shifted": b3.shifted_schedule(endogenous, steps, shift=max(7, steps // 5)),
                "random_event": b3.random_schedule(endogenous, steps, rng),
            }
            run_metrics = {
                condition: [
                    simulate_dynamic(
                        b3,
                        n_nodes,
                        edges,
                        schedule,
                        int(rng.integers(0, 2**31 - 1)),
                        steps,
                        recovery_window,
                    )
                    for _ in range(n_runs)
                ]
                for condition, schedule in schedules.items()
            }
            averaged = {condition: average_runs(metrics) for condition, metrics in run_metrics.items()}
            for sector in ALL_MU_SECTORS:
                expectation = EXPECTATIONS[sector]
                metric = expectation["metric"]
                endogenous_score = averaged["endogenous"][sector][metric]
                control_scores = [
                    run[sector][metric]
                    for condition in ("time_shifted", "random_event")
                    for run in run_metrics[condition]
                ]
                p_value = p_greater(endogenous_score, control_scores)
                effect_vs_shifted = endogenous_score - averaged["time_shifted"][sector][metric]
                effect_vs_random = endogenous_score - averaged["random_event"][sector][metric]
                expected_event_match = event_class in expectation["events"]
                for condition in CONDITIONS:
                    row = {
                        "topology_class": topology_class,
                        "topology_name": topology_name,
                        "topology_role": "primary" if topology_name == PRIMARY_TOPOLOGY else "secondary_or_exploratory",
                        "event_class": event_class,
                        "condition": condition,
                        "mu_sector": sector,
                        "expectation_label": expectation["label"],
                        "expectation_role": expectation["role"],
                        "expected_event_match": expected_event_match,
                        "expectation_metric": metric,
                        "expectation_score": averaged[condition][sector][metric],
                        "closed_walk_count": walk_counts[sector],
                        "closed_walks_per_node": walk_counts[sector] / max(1, n_nodes),
                        "n_nodes": n_nodes,
                        "n_directed_edges": len(edges),
                        "edge_convention": convention,
                        "n_seed_events": meta["n_events"],
                        "mean_seed_strength": meta["mean_strength"],
                        "total_impulse_budget": meta["total_impulse_budget"],
                        "effect_vs_time_shifted": effect_vs_shifted if condition == "endogenous" else np.nan,
                        "effect_vs_random_event": effect_vs_random if condition == "endogenous" else np.nan,
                        "dynamic_p_value": p_value if condition == "endogenous" else np.nan,
                        "notes": notes,
                    }
                    row.update(averaged[condition][sector])
                    rows.append(row)
    result = pd.DataFrame(rows)
    endogenous = result["condition"].eq("endogenous")
    confirm_mask = endogenous & result["expected_event_match"] & result["expectation_role"].eq("target")
    result["dynamic_q_value"] = np.nan
    result.loc[confirm_mask, "dynamic_q_value"] = bh_fdr(
        result.loc[confirm_mask, "dynamic_p_value"].astype(float).tolist()
    )
    result["directional_endogenous_gt_both_controls"] = (
        endogenous & (result["effect_vs_time_shifted"] > 0) & (result["effect_vs_random_event"] > 0)
    )
    result["dynamic_interpretation"] = result.apply(interpret_row, axis=1)
    output_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_dir / "Stage_B3_2_mu_sector_dynamic_expectation_results.csv", index=False)
    input_hashes.to_csv(output_dir / "Stage_B3_2_mu_sector_dynamic_expectation_input_hashes.csv", index=False)
    write_manifest(output_dir / "Stage_B3_2_mu_sector_dynamic_expectation_manifest.md", input_root, n_runs, seed, steps, recovery_window, input_hashes)
    write_summary(output_dir / "Stage_B3_2_mu_sector_dynamic_expectation_summary.md", result)
    return result


def interpret_row(row: pd.Series) -> str:
    if row["condition"] != "endogenous":
        return "control_condition"
    if row["expectation_role"] == "derived_artifact":
        return "derived_phi_artifact_monitor_not_success_criterion"
    if row["expectation_role"] == "contrast":
        return "contrast_or_artifact_monitor"
    if not bool(row["expected_event_match"]):
        return "non_preregistered_sector_event_pair"
    if bool(row["directional_endogenous_gt_both_controls"]) and float(row["dynamic_q_value"]) <= 0.05:
        return "confirmed_dynamic_expectation_candidate"
    if bool(row["directional_endogenous_gt_both_controls"]):
        return "directional_dynamic_expectation_not_fdr_confirmed"
    return "no_directional_dynamic_expectation_advantage"


def write_manifest(
    path: Path,
    input_root: Path,
    n_runs: int,
    seed: int,
    steps: int,
    recovery_window: int,
    input_hashes: pd.DataFrame,
) -> None:
    lines = [
        "# Stage B3.2 Mu-Sector Dynamic Expectation Audit Manifest",
        "",
        "Stage B3.2 is a preregistered dynamic diagnostic. It does not replace B3 or B3.1.",
        "",
        f"- input root: `{input_root}`",
        f"- n_runs: {n_runs}",
        f"- random seed: {seed}",
        f"- simulation steps: {steps}",
        f"- recovery window: {recovery_window}",
        "- target mu sectors: " + ", ".join(f"mu{x}" for x in TARGET_MU_SECTORS),
        "- derived artifact monitors: mu60 as Phi^12-derived readout; mu120 as Phi^24-derived readout",
        "",
        "## Input Hashes",
        "",
        input_hashes.to_csv(index=False).strip(),
    ]
    path.write_text("\n".join(lines) + "\n")


def write_summary(path: Path, result: pd.DataFrame) -> None:
    endogenous = result[result["condition"].eq("endogenous")].copy()
    confirmable = endogenous[
        endogenous["expected_event_match"] & endogenous["expectation_role"].eq("target")
    ].copy()
    confirmed = confirmable[
        confirmable["dynamic_interpretation"].eq("confirmed_dynamic_expectation_candidate")
    ].copy()
    directional = confirmable[confirmable["directional_endogenous_gt_both_controls"]].copy()
    artifacts = endogenous[endogenous["expectation_role"].eq("derived_artifact")].copy()
    cols = [
        "topology_name",
        "event_class",
        "mu_sector",
        "expectation_label",
        "expectation_metric",
        "expectation_score",
        "effect_vs_time_shifted",
        "effect_vs_random_event",
        "dynamic_p_value",
        "dynamic_q_value",
        "closed_walk_count",
    ]
    lines = [
        "# Stage B3.2 Mu-Sector Dynamic Expectation Audit Summary",
        "",
        "## Purpose",
        "",
        "Stage B3.2 tests whether the directional mu-sector structure seen in B3.1 follows preregistered dynamic temporal-profile expectations.",
        "",
        "## Boundary",
        "",
        "This does not rescue B3 or B3.1. B2/B3/B3.1 remain negative or inconclusive under their own gates.",
        "",
        "## Overall Result",
        "",
        f"- endogenous rows: {len(endogenous)}",
        f"- confirmable preregistered target rows: {len(confirmable)}",
        f"- FDR-confirmed dynamic expectation candidates: {len(confirmed)}",
        f"- directional preregistered dynamic rows: {len(directional)}",
        "",
        "## Confirmed Dynamic Expectation Candidates",
        "",
    ]
    lines.append(confirmed[cols].to_csv(index=False).strip() if len(confirmed) else "None.")
    lines += [
        "",
        "## Leading Directional Preregistered Rows",
        "",
    ]
    if len(directional):
        lines.append(
            directional.sort_values(["dynamic_q_value", "dynamic_p_value", "topology_name", "mu_sector"])[cols]
            .head(30)
            .to_csv(index=False)
            .strip()
        )
    else:
        lines.append("None.")
    lines += [
        "",
        "## Directional Rows By Topology",
        "",
    ]
    if len(confirmable):
        lines.append(
            confirmable.groupby("topology_name")["directional_endogenous_gt_both_controls"]
            .agg(["sum", "count"])
            .reset_index()
            .to_csv(index=False)
            .strip()
        )
    lines += [
        "",
        "## Derived Artifact Monitors",
        "",
        "mu60 and mu120 are monitored only as Phi^12/Phi^24-derived readouts following Luke's correction. They do not define B3.2 success.",
        "",
    ]
    if len(artifacts):
        lines.append(
            artifacts.sort_values(["dynamic_p_value", "topology_name", "mu_sector"])[
                [
                    "topology_name",
                    "event_class",
                    "mu_sector",
                    "expectation_label",
                    "expectation_score",
                    "effect_vs_time_shifted",
                    "effect_vs_random_event",
                    "dynamic_p_value",
                    "closed_walk_count",
                    "dynamic_interpretation",
                ]
            ]
            .head(20)
            .to_csv(index=False)
            .strip()
        )
    lines += [
        "",
        "## Interpretation Boundary",
        "",
        "A positive B3.2 row requires the expected sector/event pair, the preregistered dynamic metric, endogenous advantage over both controls, and FDR survival. Directional rows without FDR survival remain exploratory.",
    ]
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--n-runs", type=int, default=80)
    parser.add_argument("--seed", type=int, default=20260607)
    parser.add_argument("--steps", type=int, default=240)
    parser.add_argument("--recovery-window", type=int, default=24)
    args = parser.parse_args()
    run_audit(args.input_root, args.output_dir, args.n_runs, args.seed, args.steps, args.recovery_window)


if __name__ == "__main__":
    main()
