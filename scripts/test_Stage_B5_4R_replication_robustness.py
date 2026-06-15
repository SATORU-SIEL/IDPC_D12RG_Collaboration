#!/usr/bin/env python3
"""B5.4R replication / robustness audit.

Execution script for the preregistered B5.4R plan.
"""

from __future__ import annotations

import argparse
import importlib.util
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

import private_b5_4_closed_loop_prescreen as b54


REPO = Path("/Users/satoru/Documents/Codex/IDPC_D12RG_Collaboration")
B5_1_SCRIPT = REPO / "scripts/test_Stage_B5_1_phi_fes_to_c12_bridge.py"
B5_2_SCRIPT = REPO / "scripts/test_Stage_B5_2_phi_fes_to_c12_robustness.py"
CHAPTER7_PHI_FILE = "Chapter7/new_phi_dataset.csv"


PRIMARY_EVENT = "b54r_plus_phi_memory"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    mu = np.nanmean(x)
    sd = np.nanstd(x)
    if not np.isfinite(sd) or sd <= 1e-12:
        return np.zeros_like(x, dtype=float)
    return (x - mu) / sd


def finite_diff(x: np.ndarray) -> np.ndarray:
    return b54.finite_diff(np.asarray(x, dtype=float))


def lagged(x: np.ndarray, lag: int = 1) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = np.full_like(x, np.nan, dtype=float)
    if lag <= 0:
        return x.copy()
    out[lag:] = x[:-lag]
    out[:lag] = 0.0
    return out


def phi_from_h(h_loop: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    h_loop = np.asarray(h_loop, dtype=float)
    j_tilde = b54.compute_j_tilde(h_loop)
    s_h = np.nanstd(h_loop)
    s_j = np.nanstd(j_tilde)
    rho = np.nanstd(np.abs(h_loop))
    h_term = h_loop / s_h if np.isfinite(s_h) and s_h > 1e-12 else np.zeros_like(h_loop)
    j_term = j_tilde / s_j if np.isfinite(s_j) and s_j > 1e-12 else np.zeros_like(j_tilde)
    gate = np.exp(-np.abs(h_loop) / rho) if np.isfinite(rho) and rho > 1e-12 else np.zeros_like(h_loop)
    base = (1.0 - gate) * h_term + gate * j_term
    phi = np.zeros_like(base)
    if len(base):
        phi[0] = base[0]
        for i in range(1, len(base)):
            phi[i] = 0.7 * phi[i - 1] + 0.3 * base[i]
    return j_tilde, phi


def build_condition_series(input_root: Path, eta: float, condition: str, seed: int, lag_k: int = 5) -> pd.DataFrame:
    phi = pd.read_csv(input_root / CHAPTER7_PHI_FILE)
    phi["label"] = phi["label"].map(b54.canonical_label)
    rng = np.random.default_rng(seed)
    pieces = []
    for label, sub in phi.sort_values(["label", "idx_in_session"]).groupby("label", sort=False):
        sub = sub.copy()
        h = pd.to_numeric(sub["h"], errors="coerce").to_numpy(dtype=float)
        a = pd.to_numeric(sub["a"], errors="coerce").to_numpy(dtype=float)
        eps = pd.to_numeric(sub["eps"], errors="coerce").to_numpy(dtype=float)
        dphi = pd.to_numeric(sub["dphi"], errors="coerce").to_numpy(dtype=float)
        d2phi = pd.to_numeric(sub["d2phi"], errors="coerce").to_numpy(dtype=float)
        dh = pd.to_numeric(sub["dh"], errors="coerce").to_numpy(dtype=float)
        deps = pd.to_numeric(sub["deps"], errors="coerce").to_numpy(dtype=float)

        if condition == "plus_phi_memory":
            h_loop, j_tilde, phi_loop = b54.recursive_phi_from_h(h, eta)
        elif condition == "eta_zero":
            h_loop, j_tilde, phi_loop = b54.recursive_phi_from_h(h, 0.0)
        elif condition == "minus_phi_memory":
            h_loop, j_tilde, phi_loop = b54.recursive_phi_from_h(h, -abs(eta))
        else:
            _, _, ref_phi = b54.recursive_phi_from_h(h, abs(eta))
            if condition == "shuffled_phi_memory":
                x = ref_phi.copy()
                valid = np.isfinite(x)
                x[valid] = rng.permutation(x[valid])
            elif condition == "lag_shifted_phi_memory":
                x = lagged(ref_phi, lag_k)
            elif condition == "session_shuffled_phi_memory":
                x = ref_phi.copy()
                valid = np.isfinite(x)
                x[valid] = rng.permutation(x[valid])
            elif condition == "event_block_shuffled_phi_memory":
                x = ref_phi.copy()
                block = max(3, len(x) // 10)
                blocks = [x[i : i + block].copy() for i in range(0, len(x), block)]
                order = rng.permutation(len(blocks))
                x = np.concatenate([blocks[i] for i in order])[: len(ref_phi)]
            elif condition == "dphi_feedback":
                x = dphi
            elif condition == "d2phi_feedback":
                x = d2phi
            elif condition == "deps_feedback":
                x = deps
            elif condition == "dh_feedback":
                x = dh
            elif condition == "a_feedback":
                x = a
            elif condition == "random_ar_feedback":
                noise = rng.normal(0.0, 1.0, size=len(h))
                x = np.zeros_like(noise)
                for i in range(1, len(x)):
                    x[i] = 0.7 * x[i - 1] + 0.3 * noise[i]
            else:
                raise ValueError(f"unknown condition: {condition}")
            xz = zscore(x)
            xz = np.where(np.isfinite(xz), xz, 0.0)
            h_loop = h + eta * lagged(xz, 1)
            j_tilde, phi_loop = phi_from_h(h_loop)

        piece = sub.copy()
        piece["feedback_condition"] = condition
        piece["h_loop"] = h_loop
        piece["J_tilde_loop"] = j_tilde
        piece["phi_loop"] = phi_loop
        piece["dphi_loop"] = finite_diff(phi_loop)
        piece["d2phi_loop"] = finite_diff(piece["dphi_loop"].to_numpy(dtype=float))
        pieces.append(piece)
    return pd.concat(pieces, ignore_index=True)


def sign_switch_mask(values: pd.Series) -> pd.Series:
    return b54.sign_switch_mask(values)


def event_rows_from_series(series: pd.DataFrame, event_class: str, role: str, rule: str) -> pd.DataFrame:
    rows = []
    for label, sub in series.sort_values(["label", "idx_in_session"]).groupby("label", sort=False):
        for _, row in sub[sign_switch_mask(sub["phi_loop"])].iterrows():
            rows.append(
                {
                    "event_class": event_class,
                    "event_role": role,
                    "source_file": "b5_4r_replication_robustness",
                    "label": label,
                    "task_idx": float(row["idx_in_session"]),
                    "phase": float(row["phi_loop"]) if pd.notna(row["phi_loop"]) else 0.0,
                    "strength": float(abs(row["dphi_loop"])) if pd.notna(row["dphi_loop"]) else 1.0,
                    "event_rule": rule,
                }
            )
    return pd.DataFrame(rows)


def clone_rows(rows: pd.DataFrame, event_class: str, role: str, rule: str) -> pd.DataFrame:
    out = rows.copy()
    out["event_class"] = event_class
    out["event_role"] = role
    out["event_rule"] = rule
    return out


def build_events(input_root: Path, eta: float, seed: int, countmatch_samples: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    conditions = [
        "plus_phi_memory",
        "eta_zero",
        "minus_phi_memory",
        "shuffled_phi_memory",
        "lag_shifted_phi_memory",
        "session_shuffled_phi_memory",
        "event_block_shuffled_phi_memory",
        "dphi_feedback",
        "d2phi_feedback",
        "deps_feedback",
        "dh_feedback",
        "a_feedback",
        "random_ar_feedback",
    ]
    series_parts = []
    event_parts = []
    for idx, condition in enumerate(conditions):
        series = build_condition_series(input_root, eta, condition, seed + idx)
        series_parts.append(series)
        event_class = "b54r_" + condition
        role = "primary_phi_fes" if condition == "plus_phi_memory" else "adversarial_control"
        event_parts.append(event_rows_from_series(series, event_class, role, f"B5.4R phi sign-switch under {condition}"))

    events = pd.concat(event_parts, ignore_index=True)
    series_all = pd.concat(series_parts, ignore_index=True)

    plus = events[events["event_class"].eq(PRIMARY_EVENT)].copy()
    dphi = events[events["event_class"].eq("b54r_dphi_feedback")].copy()
    rng = np.random.default_rng(seed + 1234)
    for i in range(countmatch_samples):
        if len(dphi) >= len(plus) and len(plus) > 0:
            sampled = dphi.sample(n=len(plus), replace=False, random_state=int(rng.integers(0, 2**31 - 1)))
            events = pd.concat(
                [
                    events,
                    clone_rows(sampled, f"b54r_countmatched_dphi_{i+1}", "countmatched_control", "dphi feedback count-matched to +eta phi memory"),
                ],
                ignore_index=True,
            )
    return events.sort_values(["event_class", "label", "task_idx"]).reset_index(drop=True), series_all


def wrap_angle(x: np.ndarray | float) -> np.ndarray | float:
    return (np.asarray(x) + np.pi) % (2.0 * np.pi) - np.pi


def quadrature_error(theta: np.ndarray, include_bypass: bool = True) -> float:
    n = len(theta)
    idx = np.arange(n)
    cw = np.mean(np.exp(1j * wrap_angle(theta[(idx + 1) % n] - theta[idx])))
    ccw = np.mean(np.exp(1j * wrap_angle(theta[(idx - 1) % n] - theta[idx])))
    if include_bypass:
        bypass_cw = np.mean(np.exp(1j * wrap_angle(theta[(idx + 2) % n] - theta[idx])))
        bypass_ccw = np.mean(np.exp(1j * wrap_angle(theta[(idx - 2) % n] - theta[idx])))
        cw = 0.5 * (cw + bypass_cw)
        ccw = 0.5 * (ccw + bypass_ccw)
    delta = float(wrap_angle(np.angle(cw) - np.angle(ccw)))
    return float(abs(wrap_angle(delta - np.pi / 2.0)))


def simulate_quadrature_series(b3, n_nodes: int, edges: list[tuple[int, int]], schedule: list[dict[str, float]], seed: int, steps: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0.0, 2.0 * np.pi, size=n_nodes)
    omega = rng.normal(0.0, 0.012, size=n_nodes)
    incoming = [[] for _ in range(n_nodes)]
    for i, j in edges:
        incoming[j].append(i)
    by_step: dict[int, list[dict[str, float]]] = defaultdict(list)
    for event in schedule:
        by_step[int(event["step"])].append(event)
    full = []
    ring = []
    for t in range(steps):
        for event in by_step.get(t, []):
            theta = b3.apply_event_impulse(theta, event)
        delta = np.array(omega, dtype=float)
        for j in range(n_nodes):
            if incoming[j]:
                diffs = theta[incoming[j]] - theta[j]
                delta[j] += 0.34 * float(np.mean(np.sin(diffs)))
                delta[j] += 0.04 * float(np.mean(np.sin(2.0 * diffs)))
        theta = np.mod(theta + 0.06 * delta, 2.0 * np.pi)
        full.append(quadrature_error(theta, include_bypass=True))
        ring.append(quadrature_error(theta, include_bypass=False))
    return {
        "quadrature_error_full_mean_last40": float(np.nanmean(full[-40:])),
        "quadrature_error_ring_mean_last40": float(np.nanmean(ring[-40:])),
        "hex_bypass_delta_error": float(np.nanmean(full[-40:]) - np.nanmean(ring[-40:])),
    }


def quadrature_profile(b3, events: pd.DataFrame, event_class: str, steps: int, n_runs: int, rng: np.random.Generator) -> dict[str, object]:
    _, n_nodes, edges, _, _ = b3.topology_definition("C12(1,2)")
    schedule, _ = b3.build_event_schedule(events[events["event_class"].eq(event_class)].copy(), event_class, steps, n_nodes)
    if not schedule:
        return {"event_class": event_class}
    metrics = [simulate_quadrature_series(b3, n_nodes, edges, schedule, int(rng.integers(0, 2**31 - 1)), steps) for _ in range(n_runs)]
    out = {"event_class": event_class}
    for key in metrics[0]:
        vals = [m[key] for m in metrics if np.isfinite(m[key])]
        out[key] = float(np.nanmean(vals)) if vals else np.nan
    return out


def temporal_profile(b3, b5_2, events: pd.DataFrame, event_class: str, steps: int, n_runs: int, rng: np.random.Generator) -> dict[str, object]:
    _, c12_nodes, c12_edges, _, _ = b3.topology_definition("C12(1,2)")
    schedule, _ = b3.build_event_schedule(events[events["event_class"].eq(event_class)].copy(), event_class, steps, c12_nodes)
    return b5_2.temporal_profile(b3, event_class, schedule, c12_nodes, c12_edges, n_runs, steps, rng)


def bh_fdr(values: list[float] | np.ndarray) -> list[float]:
    return b54.bh_fdr(values)


def summarize(raw: pd.DataFrame, temporal: pd.DataFrame, quadrature: pd.DataFrame) -> pd.DataFrame:
    c12 = raw[raw["condition"].eq("endogenous") & raw["topology_name"].eq("C12(1,2)")].copy()
    c12["b54r_family_q"] = bh_fdr(c12["p_vs_time_shifted_and_random"].astype(float).tolist())
    if not temporal.empty:
        c12 = c12.merge(
            temporal[["event_class", "early_improvement", "mid_improvement", "late_improvement", "mean_late_window_stability", "mean_final_readout"]],
            on="event_class",
            how="left",
        )
    if not quadrature.empty:
        c12 = c12.merge(quadrature, on="event_class", how="left")
    return c12.sort_values(["p_vs_time_shifted_and_random", "p_vs_degree_null", "mean_bounded_differentiated_recovery"], na_position="last")


def write_verdict(outdir: Path, summary: pd.DataFrame, inventory: pd.DataFrame, args: argparse.Namespace) -> None:
    cols = [
        "event_class",
        "event_role",
        "n_seed_events",
        "mean_bounded_differentiated_recovery",
        "effect_vs_time_shifted",
        "effect_vs_random_event",
        "effect_vs_C8",
        "effect_vs_degree_null_mean",
        "p_vs_time_shifted_and_random",
        "p_vs_C8",
        "p_vs_degree_null",
        "mean_late_window_stability",
        "quadrature_error_full_mean_last40",
        "quadrature_error_ring_mean_last40",
        "hex_bypass_delta_error",
    ]
    show_cols = [c for c in cols if c in summary.columns]
    primary = summary[summary["event_class"].eq(PRIMARY_EVENT)]
    lines = [
        "# B5.4R Execution Check Verdict",
        "",
        "Execution after preregistration. Review before public result-sharing.",
        "",
        "## Settings",
        "",
        f"- eta: {args.eta}",
        f"- n_runs: {args.n_runs}",
        f"- n_null_graphs: {args.n_null_graphs}",
        f"- n_null_runs: {args.n_null_runs}",
        f"- temporal_runs: {args.temporal_runs}",
        f"- quadrature_runs: {args.quadrature_runs}",
        f"- seed: {args.seed}",
        "",
        "## Primary Row",
        "",
        primary[show_cols].to_csv(index=False).strip() if not primary.empty else "missing primary row",
        "",
        "## Sorted Summary",
        "",
        summary[show_cols].to_csv(index=False).strip(),
        "",
        "## Inventory",
        "",
        inventory.to_csv(index=False).strip(),
    ]
    (outdir / "B5_4R_execution_check_verdict.md").write_text("\n".join(lines) + "\n")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    b5_1 = load_module("stage_b5_1_for_b54r", B5_1_SCRIPT)
    b5_2 = load_module("stage_b5_2_for_b54r", B5_2_SCRIPT)
    b3 = b5_1.load_b3_module()
    events, series = build_events(Path(args.input_root), args.eta, args.seed, args.countmatch_samples)
    if args.include_events:
        events = events[events["event_class"].isin(set(args.include_events))].copy()
    events.to_csv(outdir / "B5_4R_events.csv", index=False)
    series.to_csv(outdir / "B5_4R_series.csv", index=False)

    raw_rows = []
    null_rows = []
    event_classes = events["event_class"].drop_duplicates().tolist()
    for event_class in event_classes:
        rows, nulls = b5_1.evaluate_event_class(b3, events, event_class, args.steps, args.n_runs, args.n_null_graphs, args.n_null_runs, rng)
        raw_rows.extend(rows)
        null_rows.extend(nulls)
    raw = b5_1.add_primary_decisions(pd.DataFrame(raw_rows))
    nulls = pd.DataFrame(null_rows)
    temporal = pd.DataFrame([temporal_profile(b3, b5_2, events, c, args.steps, args.temporal_runs, rng) for c in event_classes])
    quadrature = pd.DataFrame([quadrature_profile(b3, events, c, args.steps, args.quadrature_runs, rng) for c in event_classes])
    summary = summarize(raw, temporal, quadrature)
    inventory = events.groupby(["event_class", "event_role"], as_index=False).agg(
        n_events=("event_class", "size"),
        n_labels=("label", "nunique"),
        min_task_idx=("task_idx", "min"),
        max_task_idx=("task_idx", "max"),
        mean_strength=("strength", "mean"),
    )
    raw.to_csv(outdir / "B5_4R_raw.csv", index=False)
    nulls.to_csv(outdir / "B5_4R_nulls.csv", index=False)
    temporal.to_csv(outdir / "B5_4R_temporal.csv", index=False)
    quadrature.to_csv(outdir / "B5_4R_quadrature.csv", index=False)
    summary.to_csv(outdir / "B5_4R_summary.csv", index=False)
    inventory.to_csv(outdir / "B5_4R_inventory.csv", index=False)
    write_verdict(outdir, summary, inventory, args)
    print(summary[["event_class", "event_role", "n_seed_events", "mean_bounded_differentiated_recovery", "effect_vs_degree_null_mean", "p_vs_time_shifted_and_random", "p_vs_C8", "p_vs_degree_null", "mean_late_window_stability", "quadrature_error_full_mean_last40", "hex_bypass_delta_error"]].to_string(index=False))
    print(outdir / "B5_4R_execution_check_verdict.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path("/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/stage_b5_4r/recomputed"))
    parser.add_argument("--eta", type=float, default=0.075)
    parser.add_argument("--countmatch-samples", type=int, default=3)
    parser.add_argument("--include-events", nargs="+")
    parser.add_argument("--n-runs", type=int, default=140)
    parser.add_argument("--n-null-graphs", type=int, default=60)
    parser.add_argument("--n-null-runs", type=int, default=6)
    parser.add_argument("--temporal-runs", type=int, default=100)
    parser.add_argument("--quadrature-runs", type=int, default=80)
    parser.add_argument("--steps", type=int, default=240)
    parser.add_argument("--seed", type=int, default=54064)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
