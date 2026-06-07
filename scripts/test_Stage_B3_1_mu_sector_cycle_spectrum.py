#!/usr/bin/env python3
"""Stage B3.1 cycle-spectrum / mu-sector diagnostic audit.

This is a secondary diagnostic layered after the frozen Stage B3 primary gate.
It does not replace the Stage B3 endpoint.  It asks which loop-length /
mu-sector readouts show event-conditioned recovery on the same frozen event
schedules, topologies, dynamics, and controls.
"""

from __future__ import annotations

import argparse
import importlib.util
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


B3_SCRIPT = Path(__file__).with_name("test_Stage_B3_endogenous_event_carrier_readout.py")
MU_SECTORS = (2, 3, 4, 5, 6, 8, 9, 10, 12, 16, 20, 24)
CONDITIONS = ("endogenous", "time_shifted", "random_event")
PRIMARY_TOPOLOGY = "C12(1,2)"


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
    adj = adjacency_matrix(n_nodes, edges)
    counts = {}
    power = np.eye(n_nodes, dtype=object)
    adj_obj = adj.astype(object)
    for length in range(1, max(MU_SECTORS) + 1):
        power = power @ adj_obj
        if length in MU_SECTORS:
            counts[length] = int(np.trace(power))
    return counts


def simulate_mu_conditioned(
    b3,
    n_nodes: int,
    edges: list[tuple[int, int]],
    event_schedule: list[dict[str, float]],
    seed: int,
    steps: int,
    recovery_window: int = 18,
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

    sector_series = {sector: [] for sector in MU_SECTORS}
    diff_series = []
    vel_series = []
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
        for sector in MU_SECTORS:
            sector_series[sector].append(b3.grid_score(theta, sector))
        diff_series.append(b3.differentiation_score(theta, 12))
        vel_series.append(float(np.linalg.norm(dt * delta) / max(1, n_nodes)))
    return summarize_mu_recovery(event_schedule, sector_series, diff_series, vel_series, recovery_window)


def summarize_mu_recovery(
    schedule: list[dict[str, float]],
    sector_series: dict[int, list[float]],
    diff: list[float],
    vel: list[float],
    recovery_window: int,
) -> dict[int, dict[str, float]]:
    steps = len(diff)
    event_steps = sorted({int(x["step"]) for x in schedule if 0 <= int(x["step"]) < steps})
    out = {}
    for sector, series in sector_series.items():
        improvements = []
        post_scores = []
        weighted = []
        for step in event_steps:
            pre_start = max(0, step - recovery_window)
            post_end = min(steps, step + recovery_window + 1)
            if step <= pre_start or post_end <= step + 1:
                continue
            pre = np.asarray(series[pre_start:step], dtype=float)
            post = np.asarray(series[step + 1:post_end], dtype=float)
            post_diff = np.asarray(diff[step + 1:post_end], dtype=float)
            post_vel = np.asarray(vel[step + 1:post_end], dtype=float)
            bounded = float(np.clip(1.0 - np.mean(post_vel) / 0.04, 0.0, 1.0))
            improvement = float(np.mean(post) - np.mean(pre))
            improvements.append(improvement)
            post_scores.append(float(np.mean(post)))
            weighted.append(improvement * float(np.mean(post_diff)) * bounded)
        late = np.asarray(series[-40:], dtype=float)
        out[sector] = {
            "n_events_evaluated": len(improvements),
            "mu_post_event_score": float(np.mean(post_scores)) if post_scores else np.nan,
            "mu_recovery_improvement": float(np.mean(improvements)) if improvements else np.nan,
            "mu_differentiated_recovery": float(np.mean(weighted)) if weighted else np.nan,
            "mu_late_window_stability": float(np.clip(1.0 - np.std(late) / 0.15, 0.0, 1.0)) if len(late) else np.nan,
        }
    return out


def average_sector_runs(items: list[dict[int, dict[str, float]]]) -> dict[int, dict[str, float]]:
    out = {}
    for sector in MU_SECTORS:
        keys = sorted(set().union(*(item[sector].keys() for item in items)))
        out[sector] = {}
        for key in keys:
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


def run_mu_audit(input_root: Path, output_dir: Path, n_runs: int, seed: int, steps: int) -> pd.DataFrame:
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
            run_metrics = {}
            for condition, schedule in schedules.items():
                run_metrics[condition] = [
                    simulate_mu_conditioned(
                        b3,
                        n_nodes,
                        edges,
                        schedule,
                        int(rng.integers(0, 2**31 - 1)),
                        steps,
                    )
                    for _ in range(n_runs)
                ]
            averaged = {condition: average_sector_runs(metrics) for condition, metrics in run_metrics.items()}
            for sector in MU_SECTORS:
                endogenous_score = averaged["endogenous"][sector]["mu_differentiated_recovery"]
                control_scores = [
                    run[sector]["mu_differentiated_recovery"]
                    for condition in ("time_shifted", "random_event")
                    for run in run_metrics[condition]
                ]
                p_value = p_greater(endogenous_score, control_scores)
                effect_vs_shifted = endogenous_score - averaged["time_shifted"][sector]["mu_differentiated_recovery"]
                effect_vs_random = endogenous_score - averaged["random_event"][sector]["mu_differentiated_recovery"]
                for condition in CONDITIONS:
                    row = {
                        "topology_class": topology_class,
                        "topology_name": topology_name,
                        "topology_role": "primary" if topology_name == PRIMARY_TOPOLOGY else "secondary_or_exploratory",
                        "n_nodes": n_nodes,
                        "n_directed_edges": len(edges),
                        "edge_convention": convention,
                        "event_class": event_class,
                        "condition": condition,
                        "mu_sector": sector,
                        "closed_walk_count": walk_counts[sector],
                        "closed_walks_per_node": walk_counts[sector] / max(1, n_nodes),
                        "n_seed_events": meta["n_events"],
                        "mean_seed_strength": meta["mean_strength"],
                        "total_impulse_budget": meta["total_impulse_budget"],
                        "effect_vs_time_shifted": effect_vs_shifted if condition == "endogenous" else np.nan,
                        "effect_vs_random_event": effect_vs_random if condition == "endogenous" else np.nan,
                        "mu_p_value": p_value if condition == "endogenous" else np.nan,
                        "notes": notes,
                    }
                    row.update(averaged[condition][sector])
                    rows.append(row)
    result = pd.DataFrame(rows)
    endogenous_mask = result["condition"].eq("endogenous")
    result["mu_q_value"] = np.nan
    result.loc[endogenous_mask, "mu_q_value"] = bh_fdr(result.loc[endogenous_mask, "mu_p_value"].astype(float).tolist())
    result["directional_endogenous_gt_both_controls"] = (
        result["condition"].eq("endogenous")
        & (result["effect_vs_time_shifted"] > 0)
        & (result["effect_vs_random_event"] > 0)
    )
    result["mu_diagnostic_interpretation"] = result.apply(interpret_mu_row, axis=1)
    output_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_dir / "Stage_B3_1_mu_sector_cycle_spectrum_results.csv", index=False)
    input_hashes.to_csv(output_dir / "Stage_B3_1_mu_sector_cycle_spectrum_input_hashes.csv", index=False)
    write_manifest(output_dir / "Stage_B3_1_mu_sector_cycle_spectrum_manifest.md", input_root, n_runs, seed, steps, input_hashes)
    write_summary(output_dir / "Stage_B3_1_mu_sector_cycle_spectrum_summary.md", result)
    return result


def interpret_mu_row(row: pd.Series) -> str:
    if row["condition"] != "endogenous":
        return "control_condition"
    if bool(row["directional_endogenous_gt_both_controls"]) and float(row["mu_q_value"]) <= 0.05:
        return "secondary_mu_sector_candidate_after_fdr"
    if bool(row["directional_endogenous_gt_both_controls"]):
        return "directional_mu_sector_signal_not_fdr_confirmed"
    return "no_directional_mu_sector_advantage"


def write_manifest(path: Path, input_root: Path, n_runs: int, seed: int, steps: int, input_hashes: pd.DataFrame) -> None:
    lines = [
        "# Stage B3.1 Mu-Sector / Cycle-Spectrum Diagnostic Manifest",
        "",
        "Stage B3.1 is a secondary diagnostic audit. It does not replace or revise the frozen Stage B3 primary endpoint.",
        "",
        "## Design",
        "",
        f"- input root: `{input_root}`",
        f"- n_runs: {n_runs}",
        f"- random seed: {seed}",
        f"- simulation steps: {steps}",
        "- conditioning regimes: endogenous, time-shifted, random-event",
        "- topologies: C12(1,2), C8(1), dodecahedron, icosahedron",
        "- mu sectors: " + ", ".join(f"mu{sector}" for sector in MU_SECTORS),
        "- graph diagnostic: directed closed-walk count trace(A^mu)",
        "- dynamic diagnostic: post-event mu-sector grid recovery improvement",
        "",
        "## Interpretation Boundary",
        "",
        "The B3 primary result remains negative / inconclusive. B3.1 asks whether any closure sector shows a secondary directional recovery pattern that may explain or stratify the B3 directional effects.",
        "",
        "## Input Hashes",
        "",
        input_hashes.to_csv(index=False).strip(),
    ]
    path.write_text("\n".join(lines) + "\n")


def write_summary(path: Path, result: pd.DataFrame) -> None:
    endogenous = result[result["condition"].eq("endogenous")].copy()
    candidates = endogenous[endogenous["mu_diagnostic_interpretation"].eq("secondary_mu_sector_candidate_after_fdr")]
    directional = endogenous[endogenous["directional_endogenous_gt_both_controls"]].copy()
    leading_cols = [
        "topology_name",
        "event_class",
        "mu_sector",
        "mu_differentiated_recovery",
        "effect_vs_time_shifted",
        "effect_vs_random_event",
        "mu_p_value",
        "mu_q_value",
        "closed_walk_count",
        "closed_walks_per_node",
    ]
    lines = [
        "# Stage B3.1 Mu-Sector / Cycle-Spectrum Diagnostic Summary",
        "",
        "## Purpose",
        "",
        "Stage B3.1 adds a secondary cycle-spectrum diagnostic to the completed Stage B3 audit. It asks which loop-length / mu-sector closures recover under endogenous IDPC event conditioning, compared with time-shifted and random-event controls.",
        "",
        "## Boundary",
        "",
        "This does not change the Stage B3 primary result: no topology reached the preregistered primary positive threshold. B3.1 is diagnostic and exploratory unless a mu-sector row survives its own FDR correction.",
        "",
        "## Overall Result",
        "",
        f"- endogenous mu-sector rows: {len(endogenous)}",
        f"- FDR-confirmed secondary mu-sector candidates: {len(candidates)}",
        f"- directional endogenous > both controls rows: {len(directional)}",
        "- formal interpretation: no FDR-confirmed mu-sector recovery was detected",
        "- exploratory interpretation: directional sector-level structure exists and is not uniformly distributed across event classes or topologies",
        "",
        "## Directional Rows By Topology",
        "",
    ]
    if len(endogenous):
        by_topology = (
            endogenous.groupby("topology_name")["directional_endogenous_gt_both_controls"]
            .agg(["sum", "count"])
            .reset_index()
        )
        lines.append(by_topology.to_csv(index=False).strip())
    if len(candidates):
        lines += [
            "",
            "## FDR-Confirmed Mu-Sector Candidates",
            "",
            candidates[
                [
                    "topology_name",
                    "event_class",
                    "mu_sector",
                    "mu_differentiated_recovery",
                    "effect_vs_time_shifted",
                    "effect_vs_random_event",
                    "mu_p_value",
                    "mu_q_value",
                    "closed_walk_count",
                ]
            ].to_csv(index=False).strip(),
        ]
    else:
        lines += [
            "",
            "## FDR-Confirmed Mu-Sector Candidates",
            "",
            "None. B3.1 therefore remains a secondary, exploratory diagnostic rather than a confirmatory result.",
        ]
    if len(directional):
        leading = directional.sort_values(
            ["mu_q_value", "mu_p_value", "topology_name", "event_class", "mu_sector"]
        ).head(30)
        lines += [
            "",
            "## Leading Directional Rows",
            "",
            "These are the strongest directional rows by raw p-value / q-value. They are not confirmatory because none survives FDR correction.",
            "",
            leading[leading_cols].to_csv(index=False).strip(),
        ]
    c12 = directional[directional["topology_name"].eq(PRIMARY_TOPOLOGY)].copy()
    if len(c12):
        lines += [
            "",
            "## C12(1,2) Diagnostic Readout",
            "",
            "C12(1,2) had no confirmatory B3 primary positive and no FDR-confirmed B3.1 mu-sector candidate. However, it did show directional mu-sector rows in 26 / 72 endogenous sector tests.",
            "",
            "The most relevant C12 directional sectors are:",
            "",
            c12.sort_values(["mu_p_value", "mu_sector"])[leading_cols].head(12).to_csv(index=False).strip(),
            "",
            "Interpretation: C12(1,2) does not currently pass the formal gate, but the h=0 and eps72 directional B3 signals are not featureless. They project onto specific mu sectors, especially eps72-related mu24 / mu4 and h=0-related mu12 in this diagnostic.",
        ]
    dodeca = directional[directional["topology_name"].eq("dodecahedron")].copy()
    if len(dodeca):
        lines += [
            "",
            "## Dodecahedron Diagnostic Readout",
            "",
            "Dodecahedron had the strongest raw B3.1 directional rows. The leading rows were eps72_restoration_onset at mu4, mu9, and mu24, plus h_zero_crossing at mu20. These reached raw p=0.00621 but did not survive FDR correction.",
            "",
            dodeca.sort_values(["mu_p_value", "mu_sector"])[leading_cols].head(12).to_csv(index=False).strip(),
            "",
            "Interpretation: this is not confirmatory evidence for the dodecahedral route, but it is the clearest exploratory place where the Stage B3 directional effects acquire a sector-level shape.",
        ]
    c8 = directional[directional["topology_name"].eq("C8(1)")].copy()
    if len(c8):
        supported = c8[c8["closed_walk_count"] > 0]
        lines += [
            "",
            "## C8(1) Diagnostic Readout",
            "",
            "C8(1) had directional rows in 22 / 72 endogenous sector tests, but many directional readout sectors have zero graph closed-walk support on C8(1). Those rows should be read as phase-grid readout effects rather than graph-supported cycle closures.",
            "",
            "Graph-supported C8 directional rows:",
            "",
            supported[leading_cols].sort_values(["mu_p_value", "mu_sector"]).to_csv(index=False).strip()
            if len(supported)
            else "None.",
        ]
    ico = directional[directional["topology_name"].eq("icosahedron")].copy()
    if len(ico):
        lines += [
            "",
            "## Icosahedron Diagnostic Readout",
            "",
            "Icosahedron had no directional rows in the B3 primary readout, but B3.1 found 28 / 72 directional mu-sector rows. This suggests that scalar D12/D24 recovery and sector-level closure diagnostics can diverge.",
            "",
            ico.sort_values(["mu_p_value", "mu_sector"])[leading_cols].head(12).to_csv(index=False).strip(),
            "",
            "Interpretation: this does not rescue icosahedron as a B3 primary candidate, but it shows why the Tom-style sector audit is useful: sector-level structure can exist even when the coarse B3 primary readout is not directionally positive.",
        ]
    lines += [
        "",
        "## B3 Topology Context",
        "",
        "In the completed B3 primary audit, formal preregistered positives were zero across C12(1,2), C8(1), dodecahedron, and icosahedron. However, exploratory directional effects were present in C12(1,2) for h_zero_crossing and eps72_restoration_onset, in C8(1) for the Ricci phase-sync proxy, and especially in dodecahedron across multiple event classes. Icosahedron showed no directional endogenous > both-controls rows in the B3 primary readout.",
        "",
        "B3.1 is intended to resolve whether those directional effects correspond to specific closure sectors such as mu4, mu6, mu12, or mu24, rather than generic phase concentration.",
        "",
        "## Reporting Boundary",
        "",
        "The complete row-level B3.1 output is in `reports/Stage_B3_1_mu_sector_cycle_spectrum_results.csv`. This summary intentionally separates confirmatory claims from directional diagnostics.",
    ]
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--n-runs", type=int, default=80)
    parser.add_argument("--seed", type=int, default=20260607)
    parser.add_argument("--steps", type=int, default=240)
    args = parser.parse_args()
    run_mu_audit(args.input_root, args.output_dir, args.n_runs, args.seed, args.steps)


if __name__ == "__main__":
    main()
