#!/usr/bin/env python3
"""Stage B5.5 triadic constraint audit.

Preregistered B5.5 execution script.

Primary endpoint:
    TFC_mean-gated phi-derived C events predict future A-B consistency
    at delta=5.

Secondary endpoints:
    - empirical AB -> C -> future AB closure;
    - C12 topology-specific stabilization;
    - Luke shared-node ring-layer topology implementation check.
    - Luke triadic-packet topology/algebra implementation check.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
SCRIPTS = REPO / "scripts"
B54R_SCRIPT = SCRIPTS / "test_Stage_B5_4R_replication_robustness.py"
B5_1_SCRIPT = SCRIPTS / "test_Stage_B5_1_phi_fes_to_c12_bridge.py"
B5_2_SCRIPT = SCRIPTS / "test_Stage_B5_2_phi_fes_to_c12_robustness.py"

PRIMARY_EVENT = "b55_tfc_mean_gated_c_event"
FDR_ALPHA = 0.05


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_b54r():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    module = load_module("stage_b5_4r_for_b55", B54R_SCRIPT)
    module.REPO = REPO
    module.B5_1_SCRIPT = B5_1_SCRIPT
    module.B5_2_SCRIPT = B5_2_SCRIPT
    return module


def zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    mu = np.nanmean(x)
    sd = np.nanstd(x)
    if not np.isfinite(sd) or sd <= 1e-12:
        return np.zeros_like(x, dtype=float)
    return (x - mu) / sd


def corr_abs(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 6:
        return np.nan
    xx = zscore(x[mask])
    yy = zscore(y[mask])
    if np.nanstd(xx) <= 1e-12 or np.nanstd(yy) <= 1e-12:
        return np.nan
    return float(abs(np.corrcoef(xx, yy)[0, 1]))


def p_greater(observed: float, controls: np.ndarray | list[float]) -> float:
    control = np.asarray(controls, dtype=float)
    control = control[np.isfinite(control)]
    if not np.isfinite(observed) or len(control) == 0:
        return np.nan
    return float((1.0 + np.sum(control >= observed)) / (len(control) + 1.0))


def permutation_p(a: np.ndarray, b: np.ndarray, rng: np.random.Generator, n_perm: int) -> tuple[float, float]:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3:
        return np.nan, np.nan
    obs = float(np.nanmean(a) - np.nanmean(b))
    pooled = np.concatenate([a, b]).copy()
    n_a = len(a)
    count = 1
    for _ in range(n_perm):
        rng.shuffle(pooled)
        diff = float(np.nanmean(pooled[:n_a]) - np.nanmean(pooled[n_a:]))
        if diff >= obs:
            count += 1
    return obs, count / float(n_perm + 1)


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


def sign_switch_mask(values: pd.Series) -> pd.Series:
    v = pd.to_numeric(values, errors="coerce")
    prev = v.shift(1)
    return v.notna() & prev.notna() & (np.sign(v) != np.sign(prev)) & (np.sign(v) != 0) & (np.sign(prev) != 0)


def local_max_mask(values: pd.Series) -> pd.Series:
    v = pd.to_numeric(values, errors="coerce")
    return v.notna() & v.ge(v.shift(1).fillna(-np.inf)) & v.gt(v.shift(-1).fillna(-np.inf))


def load_series_with_features(b54r, input_root: Path, eta: float, seed: int) -> pd.DataFrame:
    series = b54r.build_condition_series(input_root, eta, "plus_phi_memory", seed)
    pieces = []
    for label, sub in series.sort_values(["label", "idx_in_session"]).groupby("label", sort=False):
        feat = pd.read_csv(input_root / f"{label}_co_recon_features_W30.csv")
        if "idx_in_session" not in feat.columns and "t" in feat.columns:
            feat = feat.rename(columns={"t": "idx_in_session"})
        keep = feat[["idx_in_session", "kappa", "mq", "a", "h"]].rename(columns={"h": "h_original"})
        pieces.append(sub.merge(keep, on="idx_in_session", how="left"))
    return pd.concat(pieces, ignore_index=True)


def build_c_kernel(sub: pd.DataFrame, lag: int, mode: str, rng: np.random.Generator) -> tuple[np.ndarray, pd.DataFrame]:
    n = len(sub)
    c = np.zeros(n, dtype=float)
    switches = sign_switch_mask(sub["phi_loop"]).to_numpy(dtype=bool)
    source_idx = np.where(switches)[0]
    target_idx = np.clip(source_idx + lag, 0, n - 1)
    if mode == "timing_shuffle":
        target_idx = target_idx.copy()
        rng.shuffle(target_idx)
    phases = pd.to_numeric(sub["phi_loop"], errors="coerce").to_numpy(dtype=float)[source_idx]
    strengths = np.abs(pd.to_numeric(sub["dphi_loop"], errors="coerce").to_numpy(dtype=float)[source_idx])
    if mode == "phase_shuffle":
        phases = phases.copy()
        rng.shuffle(phases)
    elif mode == "density_only":
        phases = rng.uniform(-np.pi, np.pi, size=len(source_idx))
        sd = np.nanstd(strengths)
        strengths = np.abs(rng.normal(np.nanmean(strengths), sd if sd > 1e-12 else 1.0, size=len(source_idx)))
        target_idx = rng.choice(np.arange(n), size=len(source_idx), replace=len(source_idx) > n)
    rows = []
    for src, tgt, phase, strength in zip(source_idx, target_idx, phases, strengths):
        val = np.sin(phase) * (strength if np.isfinite(strength) else 1.0)
        c[int(tgt)] += val
        rows.append(
            {
                "source_idx": float(sub.iloc[src]["idx_in_session"]),
                "target_idx": float(sub.iloc[tgt]["idx_in_session"]),
                "phase": float(phase) if np.isfinite(phase) else 0.0,
                "strength": float(abs(strength)) if np.isfinite(strength) else 1.0,
            }
        )
    return c, pd.DataFrame(rows)


def rolling_consistency(sub: pd.DataFrame, c_signal: np.ndarray, window: int) -> pd.DataFrame:
    out = sub.copy()
    n = len(out)
    kappa = pd.to_numeric(out["kappa"], errors="coerce").to_numpy(dtype=float)
    mq = pd.to_numeric(out["mq"], errors="coerce").to_numpy(dtype=float)
    ac = np.full(n, np.nan)
    bc = np.full(n, np.nan)
    ab = np.full(n, np.nan)
    for i in range(n):
        j = min(n, i + window)
        ac[i] = corr_abs(kappa[i:j], c_signal[i:j])
        bc[i] = corr_abs(mq[i:j], c_signal[i:j])
        ab[i] = corr_abs(kappa[i:j], mq[i:j])
    out["A_C"] = ac
    out["B_C"] = bc
    out["A_B"] = ab
    out["TFC_min"] = np.nanmin(np.vstack([ac, bc, ab]), axis=0)
    out["TFC_mean"] = np.nanmean(np.vstack([ac, bc, ab]), axis=0)
    return out


def threshold_mask(sub: pd.DataFrame, col: str, q: float) -> pd.Series:
    v = pd.to_numeric(sub[col], errors="coerce")
    return v.ge(v.quantile(q))


def append_event(rows: list[dict[str, object]], event_class: str, role: str, label: str, task_idx: float, phase: float, strength: float, rule: str) -> None:
    rows.append(
        {
            "event_class": event_class,
            "event_role": role,
            "source_file": "test_Stage_B5_5_triadic_constraint_audit",
            "label": str(label),
            "task_idx": float(task_idx),
            "phase": float(phase) if np.isfinite(phase) else 0.0,
            "strength": float(abs(strength)) if np.isfinite(strength) else 1.0,
            "event_rule": rule,
        }
    )


def add_events_from_mask(rows: list[dict[str, object]], sub: pd.DataFrame, event_map: pd.DataFrame, mask: pd.Series, event_class: str, role: str, rule: str) -> None:
    by_target = event_map.groupby("target_idx", sort=False).first() if not event_map.empty else pd.DataFrame()
    for _, row in sub[mask].iterrows():
        idx = float(row["idx_in_session"])
        if not by_target.empty and idx in by_target.index:
            phase = by_target.loc[idx, "phase"]
            strength = by_target.loc[idx, "strength"]
        else:
            phase = row.get("phi_loop", 0.0)
            strength = row.get("TFC_mean", 1.0)
        append_event(rows, event_class, role, row["label"], idx, phase, strength, rule)


def build_events_and_annotation(b54r, input_root: Path, eta: float, seed: int, lag: int, q: float, window: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    full = load_series_with_features(b54r, input_root, eta, seed)
    rng = np.random.default_rng(seed + 55_500)
    event_rows: list[dict[str, object]] = []
    annotated_parts = []
    for label, sub in full.sort_values(["label", "idx_in_session"]).groupby("label", sort=False):
        sub = sub.copy().reset_index(drop=True)
        aligned_kernel, aligned_events = build_c_kernel(sub, lag, "aligned", rng)
        phase_kernel, phase_events = build_c_kernel(sub, lag, "phase_shuffle", rng)
        timing_kernel, timing_events = build_c_kernel(sub, lag, "timing_shuffle", rng)
        density_kernel, density_events = build_c_kernel(sub, lag, "density_only", rng)
        annotated = rolling_consistency(sub, aligned_kernel, window)
        phase_shuf = rolling_consistency(sub, phase_kernel, window)
        timing_shuf = rolling_consistency(sub, timing_kernel, window)
        density_only = rolling_consistency(sub, density_kernel, window)
        annotated["TFC_phase_shuffle"] = phase_shuf["TFC_min"]
        annotated["TFC_timing_shuffle"] = timing_shuf["TFC_min"]
        annotated["TFC_density_only"] = density_only["TFC_min"]

        target_indices = set(aligned_events["target_idx"].astype(float).tolist()) if not aligned_events.empty else set()
        c_event = annotated["idx_in_session"].astype(float).isin(target_indices)
        high_tfc = threshold_mask(annotated, "TFC_min", q)
        high_mean = threshold_mask(annotated, "TFC_mean", q)
        high_ac = threshold_mask(annotated, "A_C", q)
        high_bc = threshold_mask(annotated, "B_C", q)
        high_ab = threshold_mask(annotated, "A_B", q)
        high_phase = pd.to_numeric(annotated["TFC_phase_shuffle"], errors="coerce").ge(pd.to_numeric(annotated["TFC_phase_shuffle"], errors="coerce").quantile(q))
        high_timing = pd.to_numeric(annotated["TFC_timing_shuffle"], errors="coerce").ge(pd.to_numeric(annotated["TFC_timing_shuffle"], errors="coerce").quantile(q))
        high_density = pd.to_numeric(annotated["TFC_density_only"], errors="coerce").ge(pd.to_numeric(annotated["TFC_density_only"], errors="coerce").quantile(q))

        add_events_from_mask(event_rows, annotated, aligned_events, c_event & high_mean, PRIMARY_EVENT, "primary_constraint", f"C event AND TFC_mean per-label top {int(q*100)}%")
        add_events_from_mask(event_rows, annotated, aligned_events, c_event & high_tfc, "b55_tfc_min_gated_c_event", "secondary_closure", f"C event AND TFC_min per-label top {int(q*100)}%")
        add_events_from_mask(event_rows, annotated, aligned_events, c_event, "b55_phase_event_only_lag5", "c_event_control", "phase-bearing sparse C event at lag +5")
        add_events_from_mask(event_rows, annotated, aligned_events, c_event & high_ac & ~high_tfc, "b55_pairwise_ac_only", "pairwise_control", "C event AND A-C high but not TFC-min high")
        add_events_from_mask(event_rows, annotated, aligned_events, c_event & high_bc & ~high_tfc, "b55_pairwise_bc_only", "pairwise_control", "C event AND B-C high but not TFC-min high")
        add_events_from_mask(event_rows, annotated, aligned_events, c_event & high_ab & ~high_tfc, "b55_pairwise_ab_only", "pairwise_control", "C event AND A-B high but not TFC-min high")
        add_events_from_mask(event_rows, annotated, phase_events, c_event & high_phase, "b55_shuffled_c_phase_gate", "shuffle_control", "C event timing with shuffled phase gate")
        add_events_from_mask(event_rows, annotated, timing_events, high_timing & local_max_mask(annotated["TFC_timing_shuffle"]), "b55_shuffled_c_timing_gate", "shuffle_control", "timing-shuffled C kernel local TFC maxima")
        add_events_from_mask(event_rows, annotated, density_events, high_density & local_max_mask(annotated["TFC_density_only"]), "b55_density_only_gate", "density_control", "density-only C kernel local TFC maxima")

        annotated["c_event_lag5"] = c_event
        annotated["high_tfc_mean"] = high_mean
        annotated["high_tfc_min"] = high_tfc
        annotated_parts.append(annotated)

    events = pd.DataFrame(event_rows).sort_values(["event_class", "label", "task_idx"]).reset_index(drop=True)
    if events.empty:
        raise RuntimeError("no B5.5 events generated")
    return events, pd.concat(annotated_parts, ignore_index=True)


def future_ab_for_row(sub: pd.DataFrame, pos: int, delta: int, window: int) -> tuple[float, float]:
    start = pos + delta
    end = min(len(sub), start + window)
    if start >= len(sub):
        return np.nan, np.nan
    kappa = pd.to_numeric(sub["kappa"], errors="coerce").to_numpy(dtype=float)
    mq = pd.to_numeric(sub["mq"], errors="coerce").to_numpy(dtype=float)
    future = corr_abs(kappa[start:end], mq[start:end])
    pre = corr_abs(kappa[max(0, pos - window) : pos], mq[max(0, pos - window) : pos])
    return future, future - pre if np.isfinite(future) and np.isfinite(pre) else np.nan


def build_future_readouts(annotated: pd.DataFrame, events: pd.DataFrame, deltas: list[int], window: int) -> pd.DataFrame:
    rows = []
    for label, sub in annotated.sort_values(["label", "idx_in_session"]).groupby("label", sort=False):
        sub = sub.reset_index(drop=True)
        by_idx = {float(v): i for i, v in enumerate(sub["idx_in_session"].astype(float).tolist())}
        ev_sub = events[events["label"].astype(str).eq(str(label))]
        for _, ev in ev_sub.iterrows():
            idx = float(ev["task_idx"])
            if idx not in by_idx:
                continue
            pos = by_idx[idx]
            state = sub.iloc[pos]
            for delta in deltas:
                future, gain = future_ab_for_row(sub, pos, delta, window)
                rows.append(
                    {
                        "label": label,
                        "idx_in_session": idx,
                        "event_class": ev["event_class"],
                        "event_role": ev["event_role"],
                        "delta": delta,
                        "future_AB": future,
                        "return_gain": gain,
                        "pre_AB": future - gain if np.isfinite(future) and np.isfinite(gain) else np.nan,
                        "TFC_mean": float(state.get("TFC_mean", np.nan)),
                        "TFC_min": float(state.get("TFC_min", np.nan)),
                        "A_C": float(state.get("A_C", np.nan)),
                        "B_C": float(state.get("B_C", np.nan)),
                        "A_B_at_t": float(state.get("A_B", np.nan)),
                    }
                )
    return pd.DataFrame(rows)


def add_closure_scores(readouts: pd.DataFrame) -> pd.DataFrame:
    out = readouts.copy()
    pieces = []
    for _, sub in out.groupby(["label", "delta"], sort=False):
        sub = sub.copy()
        pre_z = zscore(sub["pre_AB"].to_numpy(dtype=float))
        c_z = zscore(sub["TFC_mean"].to_numpy(dtype=float))
        fut_z = zscore(sub["future_AB"].to_numpy(dtype=float))
        ret_z = zscore(sub["return_gain"].to_numpy(dtype=float))
        sub["closure_min_z"] = np.nanmin(np.vstack([pre_z, c_z, fut_z]), axis=0)
        sub["constraint_closure_min_z"] = np.nanmin(np.vstack([pre_z, c_z, ret_z]), axis=0)
        pieces.append(sub)
    return pd.concat(pieces, ignore_index=True)


def summarize_future(readouts: pd.DataFrame, n_perm: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 990)
    candidates = [
        PRIMARY_EVENT,
        "b55_tfc_min_gated_c_event",
        "b55_phase_event_only_lag5",
        "b55_pairwise_ac_only",
        "b55_pairwise_bc_only",
        "b55_pairwise_ab_only",
    ]
    baselines = [
        "b55_shuffled_c_timing_gate",
        "b55_shuffled_c_phase_gate",
        "b55_density_only_gate",
        "b55_pairwise_ac_only",
        "b55_phase_event_only_lag5",
    ]
    rows = []
    for delta, dsub in readouts.groupby("delta", sort=True):
        for candidate in candidates:
            csub = dsub[dsub["event_class"].eq(candidate)]
            if csub.empty:
                continue
            row: dict[str, object] = {
                "delta": int(delta),
                "event_class": candidate,
                "n_events": int(csub["future_AB"].notna().sum()),
                "mean_future_AB": float(np.nanmean(csub["future_AB"])),
                "mean_return_gain": float(np.nanmean(csub["return_gain"])),
                "mean_closure_min_z": float(np.nanmean(csub["closure_min_z"])),
                "mean_constraint_closure_min_z": float(np.nanmean(csub["constraint_closure_min_z"])),
            }
            for baseline in baselines:
                bsub = dsub[dsub["event_class"].eq(baseline)]
                if bsub.empty:
                    continue
                for metric in ["future_AB", "return_gain", "constraint_closure_min_z"]:
                    eff, p = permutation_p(csub[metric].to_numpy(dtype=float), bsub[metric].to_numpy(dtype=float), rng, n_perm)
                    row[f"effect_{metric}_vs_{baseline}"] = eff
                    row[f"p_{metric}_vs_{baseline}"] = p
            rows.append(row)
    out = pd.DataFrame(rows)
    primary = out["delta"].eq(5)
    out["future_ab_primary_q"] = np.nan
    out.loc[primary, "future_ab_primary_q"] = bh_fdr(out.loc[primary, "p_future_AB_vs_b55_shuffled_c_timing_gate"].astype(float).tolist())
    return out


def schedule_for(b3, events: pd.DataFrame, event_class: str, steps: int, n_nodes: int) -> list[dict[str, float]]:
    rows = events[events["event_class"].eq(event_class)].copy()
    schedule, _ = b3.build_event_schedule(rows, event_class, steps, n_nodes)
    return schedule


def simulate_values(b5_1, b3, n_nodes: int, edges: list[tuple[int, int]], schedule: list[dict[str, float]], n_runs: int, steps: int, rng: np.random.Generator) -> tuple[np.ndarray, dict[str, float]]:
    return b5_1.simulate_many(b3, n_nodes, edges, schedule, n_runs, steps, rng)


def c12_layer_edges(jump: int) -> list[tuple[int, int]]:
    edges = set()
    for i in range(12):
        edges.add((i, (i + jump) % 12))
        edges.add((i, (i - jump) % 12))
    return sorted(edges)


def triadic_packet_edges() -> list[tuple[int, int]]:
    """Four triadic packets B_j={j,j+4,j+8} on the 12-clock.

    This implements Luke's packet decomposition as four separated bidirectional
    3-cycles on the same 12 node labels. It is a secondary topology readout,
    not a replacement for the primary C -> future AB endpoint.
    """
    edges = set()
    for j in range(4):
        packet = [j, (j + 4) % 12, (j + 8) % 12]
        for a, b in zip(packet, packet[1:] + packet[:1]):
            edges.add((a, b))
            edges.add((b, a))
    return sorted(edges)


def evaluate_shared_node_layers(b5_1, b3, events: pd.DataFrame, event_class: str, steps: int, n_runs: int, rng: np.random.Generator) -> dict[str, object]:
    schedule = schedule_for(b3, events, event_class, steps, 12)
    if not schedule:
        return {"event_class": event_class, "topology_readout": "shared_node_ring_layers", "n_seed_events": 0}
    shifted = b3.shifted_schedule(schedule, steps, shift=max(7, steps // 5))
    random_schedules = [b3.random_schedule(schedule, steps, rng) for _ in range(n_runs)]
    layer_edges = [c12_layer_edges(1), c12_layer_edges(2)]

    def layer_values(local_schedule: list[dict[str, float]]) -> np.ndarray:
        vals = []
        for edges in layer_edges:
            v, _ = simulate_values(b5_1, b3, 12, edges, local_schedule, n_runs, steps, rng)
            vals.append(v)
        return np.nanmean(np.vstack(vals), axis=0)

    obs_vals = layer_values(schedule)
    shifted_vals = layer_values(shifted)
    random_vals = []
    for rs in random_schedules:
        vals = []
        for edges in layer_edges:
            metric = b3.simulate_event_conditioned(12, edges, rs, int(rng.integers(0, 2**31 - 1)), steps=steps)
            vals.append(metric.get("differentiated_recovery", np.nan))
        random_vals.append(float(np.nanmean(vals)))
    random_vals = np.asarray(random_vals, dtype=float)
    _, c8_nodes, c8_edges, _, _ = b3.topology_definition("C8(1)")
    c8_schedule = schedule_for(b3, events, event_class, steps, c8_nodes)
    c8_vals, _ = simulate_values(b5_1, b3, c8_nodes, c8_edges, c8_schedule, n_runs, steps, rng)
    return {
        "event_class": event_class,
        "topology_readout": "separate_shared_node_ring_layers_C12_pm1_plus_C12_pm2",
        "n_seed_events": len(schedule),
        "mean_bounded_differentiated_recovery": float(np.nanmean(obs_vals)),
        "effect_vs_time_shifted": float(np.nanmean(obs_vals) - np.nanmean(shifted_vals)),
        "effect_vs_random_event": float(np.nanmean(obs_vals) - np.nanmean(random_vals)),
        "effect_vs_C8": float(np.nanmean(obs_vals) - np.nanmean(c8_vals)),
        "p_vs_time_shifted_and_random": p_greater(float(np.nanmean(obs_vals)), np.r_[shifted_vals, random_vals]),
        "p_vs_C8": p_greater(float(np.nanmean(obs_vals)), c8_vals),
        "implementation_note": "Luke secondary check: separate ring layers share the same 12 node indices; compared against single-ring C12(1,2).",
    }


def evaluate_triadic_packet_layers(b5_1, b3, events: pd.DataFrame, event_class: str, steps: int, n_runs: int, rng: np.random.Generator) -> dict[str, object]:
    schedule = schedule_for(b3, events, event_class, steps, 12)
    if not schedule:
        return {"event_class": event_class, "topology_readout": "triadic_packet_decomposition", "n_seed_events": 0}
    shifted = b3.shifted_schedule(schedule, steps, shift=max(7, steps // 5))
    random_schedules = [b3.random_schedule(schedule, steps, rng) for _ in range(n_runs)]
    packet_edges = triadic_packet_edges()

    obs_vals, _ = simulate_values(b5_1, b3, 12, packet_edges, schedule, n_runs, steps, rng)
    shifted_vals, _ = simulate_values(b5_1, b3, 12, packet_edges, shifted, n_runs, steps, rng)
    random_vals = np.asarray(
        [
            b3.simulate_event_conditioned(12, packet_edges, rs, int(rng.integers(0, 2**31 - 1)), steps=steps).get("differentiated_recovery", np.nan)
            for rs in random_schedules
        ],
        dtype=float,
    )
    _, c8_nodes, c8_edges, _, _ = b3.topology_definition("C8(1)")
    c8_schedule = schedule_for(b3, events, event_class, steps, c8_nodes)
    c8_vals, _ = simulate_values(b5_1, b3, c8_nodes, c8_edges, c8_schedule, n_runs, steps, rng)
    return {
        "event_class": event_class,
        "topology_readout": "triadic_packets_Bj_j_jplus4_jplus8",
        "n_seed_events": len(schedule),
        "mean_bounded_differentiated_recovery": float(np.nanmean(obs_vals)),
        "effect_vs_time_shifted": float(np.nanmean(obs_vals) - np.nanmean(shifted_vals)),
        "effect_vs_random_event": float(np.nanmean(obs_vals) - np.nanmean(random_vals)),
        "effect_vs_C8": float(np.nanmean(obs_vals) - np.nanmean(c8_vals)),
        "p_vs_time_shifted_and_random": p_greater(float(np.nanmean(obs_vals)), np.r_[shifted_vals, random_vals]),
        "p_vs_C8": p_greater(float(np.nanmean(obs_vals)), c8_vals),
        "packet_definition": "B_j={j,j+4,j+8}, j=0,1,2,3 mod 12",
        "algebraic_note": "omega^4 is a cube root of unity; packet product collapses to 1+omega^(3j)x^3 and full product recovers 1-x^12.",
        "implementation_note": "Luke secondary check: triadic packet decomposition of the 12-clock as four separated bidirectional 3-cycles.",
    }


def summarize_c12(raw: pd.DataFrame, temporal: pd.DataFrame, b54r) -> pd.DataFrame:
    c12 = raw[raw["condition"].eq("endogenous") & raw["topology_name"].eq("C12(1,2)")].copy()
    c12["b55_c12_q"] = b54r.bh_fdr(c12["p_vs_time_shifted_and_random"].astype(float).tolist())
    if not temporal.empty:
        c12 = c12.merge(
            temporal[["event_class", "early_improvement", "mid_improvement", "late_improvement", "mean_late_window_stability", "mean_final_readout"]],
            on="event_class",
            how="left",
        )
    return c12.sort_values(["p_vs_time_shifted_and_random", "p_vs_degree_null", "mean_bounded_differentiated_recovery"], na_position="last")


def write_preregistration(path: Path) -> None:
    text = """# Updated B5.5 preregistration proposal

## Title

Triadic constraint audit of phi-derived intersection geometry and bounded selective stabilization.

## Status

This preregistration is written before the B5.5 execution. It incorporates:

- Marcel's bounded-selective-stabilization constraint;
- Luke's shared-node ring-layer topology implementation check, now explicitly reported as a secondary result block;
- Luke's triadic-packet 12-clock decomposition B_j={j,j+4,j+8}, now explicitly reported as a secondary result block;
- Pasquale's residual-condensation point as a deferred explanatory audit, not a primary endpoint.

## Primary Question

Does C_t predict a short-lag increase in future A-B consistency?

Definitions:

- A = EEG curvature / phase-curvature structure;
- B = quantum MQ structure;
- C = phi-derived phase-bearing sparse event geometry;
- future A-B consistency = |corr(kappa, MQ)| over a future local window.

The primary delta is fixed at delta=5. Longer deltas 10, 20, and 30 are secondary.

## Primary Endpoint

The primary event class is:

`C event AND high TFC_mean`.

The primary endpoint is future A-B consistency at delta=5.

Primary controls:

- shuffled C timing;
- shuffled C phase;
- density-only C events;
- phase-event-only events;
- pairwise A-C only;
- pairwise B-C only;
- pairwise A-B only.

The pairwise A-C control is central: the result must not reduce to A-C coupling alone.

## Bounded Selective Stabilization Boundary

A positive B5.5 interpretation requires boundedness, preservation of negative controls, and avoidance of generic persistence, drift, runaway amplification, fragmentation, or all-readout amplification.

## Secondary Closure Endpoint

The secondary closure endpoint tests whether the same event family supports:

AB -> C -> future AB.

The closure audit combines pre/current A-B consistency, C consistency, future A-B consistency, and return gain.

## Mandatory C12 Topology Readout

C12 is a topology-sensitive readout, not the ontological intersection itself.

The C12 chain tested is:

AB interaction -> C event geometry -> future A-B consistency -> C12 topology-specific stabilization.

Endpoints include C12 recovery, C12 vs C8, C12 vs degree-null, C12 vs shifted/random timing, late-window stability, bounded non-runaway score, and non-collapsed differentiation score.

## Luke Secondary Topology Implementation Result Block

Luke's topology concern is explicitly reported as a separate secondary result table.

The audit compares:

1. single-ring event-substitution C12(1,2) readout;
2. separate shared-node ring-layer readout, implemented as C12(±1) and C12(±2) ring layers sharing the same 12 node indices.

This check asks whether single-ring C12(1,2) artificially collapses pairwise/control geometries, possibly masking separate cyclic pathways. It is not allowed to replace or move the primary endpoint.

The shared-node ring-layer readout is supportive only if it reproduces or improves topology-specific selectivity without producing generic improvement across controls.

## Luke Triadic-Packet Topology/Algebra Result Block

Luke's newer packet formulation is also explicitly included as a secondary topology implementation check.

The 12-clock is split into four triadic packets:

`B_j = {j, j+4, j+8}, j=0,1,2,3 (mod 12)`.

The corresponding algebraic note is:

`B_j(x) = product_{k=0}^2 (1 + omega^{j+4k} x) = 1 + omega^{3j} x^3`,

and the full packet product recovers:

`product_{j=0}^3 B_j(x) = product_{r=0}^{11}(1 + omega^r x) = 1 - x^12`.

Operationally, this is tested as four separated bidirectional 3-cycle packets on the same 12 node labels. This is a secondary implementation audit designed to distinguish triadic packet closure from single-ring C12(1,2) and shared-node ring-layer readouts. It is not allowed to replace or move the primary endpoint.

## Interpretation Boundary

B5.5 will not claim proof of subjectivity-intersection itself, phi=O3, complete triadic fixed point, D12RG proof, broad Phi/FES confirmation, or stable carrier closure.

B5.5 tests whether the current empirical C candidate behaves as a bounded, selective, short-lag constraint on future A-B consistency.
"""
    path.write_text(text)


def write_summary(path: Path, future: pd.DataFrame, c12: pd.DataFrame, shared: pd.DataFrame, packets: pd.DataFrame, inventory: pd.DataFrame, args: argparse.Namespace) -> None:
    future_cols = [
        "delta",
        "event_class",
        "n_events",
        "mean_future_AB",
        "mean_return_gain",
        "effect_future_AB_vs_b55_shuffled_c_timing_gate",
        "p_future_AB_vs_b55_shuffled_c_timing_gate",
        "effect_future_AB_vs_b55_pairwise_ac_only",
        "p_future_AB_vs_b55_pairwise_ac_only",
        "future_ab_primary_q",
    ]
    future_cols = [c for c in future_cols if c in future.columns]
    c12_cols = [
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
        "b55_c12_q",
        "mean_late_window_stability",
        "bounded_non_runaway_score",
        "non_collapsed_differentiation_score",
    ]
    c12_cols = [c for c in c12_cols if c in c12.columns]
    lines = [
        "# Stage B5.5 Triadic Constraint Audit Summary",
        "",
        "Execution after preregistration.",
        "",
        "## Settings",
        "",
        f"- eta: {args.eta}",
        f"- lag: {args.lag}",
        f"- TFC quantile: {args.quantile}",
        f"- rolling window: {args.window}",
        f"- future window: {args.future_window}",
        f"- deltas: {args.deltas}",
        f"- primary delta: 5",
        f"- n_runs: {args.n_runs}",
        f"- n_null_graphs: {args.n_null_graphs}",
        f"- n_null_runs: {args.n_null_runs}",
        f"- temporal_runs: {args.temporal_runs}",
        f"- shared_layer_runs: {args.shared_layer_runs}",
        f"- packet_runs: {args.packet_runs}",
        f"- seed: {args.seed}",
        "",
        "## Primary Future A-B Result",
        "",
        future[(future["delta"].eq(5)) & future["event_class"].eq(PRIMARY_EVENT)][future_cols].to_csv(index=False).strip(),
        "",
        "## Future A-B Summary",
        "",
        future[future_cols].to_csv(index=False).strip(),
        "",
        "## C12 Single-Ring Summary",
        "",
        c12[c12_cols].to_csv(index=False).strip(),
        "",
        "## Luke Shared-Node Ring-Layer Result Block",
        "",
        shared.to_csv(index=False).strip(),
        "",
        "## Luke Triadic-Packet Result Block",
        "",
        packets.to_csv(index=False).strip(),
        "",
        "## Event Inventory",
        "",
        inventory.to_csv(index=False).strip(),
    ]
    path.write_text("\n".join(lines) + "\n")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    b54r = load_b54r()
    b5_1 = load_module("stage_b5_1_for_b55", B5_1_SCRIPT)
    b5_2 = load_module("stage_b5_2_for_b55", B5_2_SCRIPT)
    b3 = b5_1.load_b3_module()

    write_preregistration(outdir / "Stage_B5_5_triadic_constraint_preregistration.md")

    events, annotated = build_events_and_annotation(b54r, Path(args.input_root), args.eta, args.seed, args.lag, args.quantile, args.window)
    readouts = add_closure_scores(build_future_readouts(annotated, events, [int(x) for x in args.deltas.split(",")], args.future_window))
    future_summary = summarize_future(readouts, args.n_perm, args.seed)

    raw_rows = []
    null_rows = []
    event_classes = events["event_class"].drop_duplicates().tolist()
    for event_class in event_classes:
        rows, nulls = b5_1.evaluate_event_class(b3, events, event_class, args.steps, args.n_runs, args.n_null_graphs, args.n_null_runs, rng)
        raw_rows.extend(rows)
        null_rows.extend(nulls)
    raw = b5_1.add_primary_decisions(pd.DataFrame(raw_rows))
    nulls = pd.DataFrame(null_rows)
    temporal = pd.DataFrame([b54r.temporal_profile(b3, b5_2, events, c, args.steps, args.temporal_runs, rng) for c in event_classes])
    c12_summary = summarize_c12(raw, temporal, b54r)
    shared = pd.DataFrame([evaluate_shared_node_layers(b5_1, b3, events, c, args.steps, args.shared_layer_runs, rng) for c in event_classes])
    packets = pd.DataFrame([evaluate_triadic_packet_layers(b5_1, b3, events, c, args.steps, args.packet_runs, rng) for c in event_classes])
    inventory = events.groupby(["event_class", "event_role"], as_index=False).agg(
        n_events=("event_class", "size"),
        n_labels=("label", "nunique"),
        min_task_idx=("task_idx", "min"),
        max_task_idx=("task_idx", "max"),
        mean_strength=("strength", "mean"),
    )

    events.to_csv(outdir / "Stage_B5_5_triadic_constraint_events.csv", index=False)
    annotated.to_csv(outdir / "Stage_B5_5_triadic_constraint_annotated.csv", index=False)
    readouts.to_csv(outdir / "Stage_B5_5_future_ab_readouts.csv", index=False)
    future_summary.to_csv(outdir / "Stage_B5_5_future_ab_summary.csv", index=False)
    raw.to_csv(outdir / "Stage_B5_5_c12_single_ring_raw_conditions.csv", index=False)
    nulls.to_csv(outdir / "Stage_B5_5_c12_single_ring_nulls.csv", index=False)
    temporal.to_csv(outdir / "Stage_B5_5_c12_single_ring_temporal.csv", index=False)
    c12_summary.to_csv(outdir / "Stage_B5_5_c12_single_ring_summary.csv", index=False)
    shared.to_csv(outdir / "Stage_B5_5_shared_node_ring_layer_summary.csv", index=False)
    packets.to_csv(outdir / "Stage_B5_5_triadic_packet_summary.csv", index=False)
    inventory.to_csv(outdir / "Stage_B5_5_event_inventory.csv", index=False)
    write_summary(outdir / "Stage_B5_5_triadic_constraint_summary.md", future_summary, c12_summary, shared, packets, inventory, args)
    print(future_summary[future_summary["delta"].eq(5)][["event_class", "n_events", "mean_future_AB", "p_future_AB_vs_b55_shuffled_c_timing_gate", "p_future_AB_vs_b55_pairwise_ac_only", "future_ab_primary_q"]].to_string(index=False))
    print(outdir / "Stage_B5_5_triadic_constraint_summary.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path("/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction"))
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b5_5")
    parser.add_argument("--eta", type=float, default=0.075)
    parser.add_argument("--lag", type=int, default=5)
    parser.add_argument("--quantile", type=float, default=0.60)
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--future-window", type=int, default=30)
    parser.add_argument("--deltas", default="5,10,20,30")
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--n-runs", type=int, default=120)
    parser.add_argument("--n-null-graphs", type=int, default=50)
    parser.add_argument("--n-null-runs", type=int, default=6)
    parser.add_argument("--temporal-runs", type=int, default=80)
    parser.add_argument("--shared-layer-runs", type=int, default=80)
    parser.add_argument("--packet-runs", type=int, default=80)
    parser.add_argument("--steps", type=int, default=240)
    parser.add_argument("--seed", type=int, default=55550)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
