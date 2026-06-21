#!/usr/bin/env python3
"""Private B7.4 prescreen for Luke-style phi-invariant C candidates."""

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


PHI = (1.0 + np.sqrt(5.0)) / 2.0


def signed_power(x: np.ndarray, p: int) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return np.sign(x) * np.power(np.abs(x), p)


def group_diff(df: pd.DataFrame, values: np.ndarray) -> np.ndarray:
    s = pd.Series(values, index=df.index, dtype=float)
    return (
        s.groupby(df["label"], sort=False)
        .diff()
        .fillna(0.0)
        .to_numpy(dtype=float)
    )


def group_centered_cumsum(df: pd.DataFrame, values: np.ndarray) -> np.ndarray:
    s = pd.Series(values, index=df.index, dtype=float)
    cs = s.groupby(df["label"], sort=False).cumsum()
    return (cs - cs.groupby(df["label"], sort=False).transform("mean")).to_numpy(dtype=float)


def min_agreement_score(columns: list[np.ndarray]) -> np.ndarray:
    zs = [b73a.zscore(col) for col in columns]
    stack = np.vstack(zs)
    sign_vote = np.abs(np.nanmean(np.sign(stack), axis=0))
    min_abs = np.nanmin(np.abs(stack), axis=0)
    return b73a.zscore(sign_vote * min_abs)


def add_phi_candidates(data: pd.DataFrame) -> pd.DataFrame:
    out = b73a.add_representation_scores(data)
    ab = pd.to_numeric(out["ab_receiver_side"], errors="coerce").to_numpy(dtype=float)
    ba = pd.to_numeric(out["ba_receiver_side"], errors="coerce").to_numpy(dtype=float)
    ab_mag = np.abs(ab)
    ba_mag = np.abs(ba)
    mag = np.nanmean(
        np.vstack([
            pd.to_numeric(out["ab_standpoint_magnitude"], errors="coerce"),
            pd.to_numeric(out["ba_standpoint_magnitude"], errors="coerce"),
        ]),
        axis=0,
    )
    inv = pd.to_numeric(out["standpoint_inversion_c"], errors="coerce").to_numpy(dtype=float)

    # Luke-style complementary eigenmode probes: phi and -1/phi modes should cancel or close.
    phi_signed_residual = PHI * ab - (1.0 / PHI) * ba
    phi_opposite_residual = PHI * ab + (1.0 / PHI) * ba
    phi_magnitude_residual = PHI * ab_mag - (1.0 / PHI) * ba_mag
    phi_energy = PHI * ab_mag + (1.0 / PHI) * ba_mag
    phi_ratio_closure = -np.abs(np.log((ab_mag + 1e-9) / (ba_mag + 1e-9)) - np.log(1.0 / (PHI * PHI)))

    out["phi_signed_balance_c"] = b73a.zscore(-np.abs(phi_signed_residual))
    out["phi_opposite_balance_c"] = b73a.zscore(-np.abs(phi_opposite_residual))
    out["phi_magnitude_balance_c"] = b73a.zscore(-np.abs(phi_magnitude_residual))
    out["phi_eigen_energy_c"] = b73a.zscore(phi_energy)
    out["phi_ratio_closure_c"] = b73a.zscore(phi_ratio_closure)

    # De Vries-Jordan bridge proxy: 1 -> sqrt(alpha) -> alpha becomes a geometric middle.
    bridge = np.sqrt(np.maximum(phi_energy, 0.0) * np.maximum(mag, 0.0))
    out["dvj_half_shift_bridge_c"] = b73a.zscore(bridge + inv)

    base = b73a.zscore(phi_energy + mag + inv)
    d_base = group_diff(out, base)
    i_base = group_centered_cumsum(out, base)
    x2 = signed_power(base, 2)
    x6 = signed_power(base, 6)
    out["phi_differential_invariant_c"] = min_agreement_score([base, d_base, i_base])
    out["phi_substitution_invariant_c"] = min_agreement_score([base, x2, x6])
    out["phi_full_invariant_c"] = min_agreement_score([base, d_base, i_base, x2, x6])

    # Finite C12 shell proxy: the candidate should sharpen when paired with phase modulo 12.
    phase = pd.to_numeric(out["phase"], errors="coerce").to_numpy(dtype=float)
    c12_shell = np.cos(12.0 * phase)
    out["phi_c12_product_shell_c"] = b73a.zscore(base * c12_shell)
    out["phi_c12_abs_shell_c"] = b73a.zscore(np.abs(base) * (1.0 + c12_shell))
    return out


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    features = add_phi_candidates(b73a.load_b72_features(args))

    reps = [
        "scalar_c",
        "receiver_only_c",
        "receiver_standpoint_magnitude_c",
        "phi_signed_balance_c",
        "phi_opposite_balance_c",
        "phi_magnitude_balance_c",
        "phi_eigen_energy_c",
        "phi_ratio_closure_c",
        "dvj_half_shift_bridge_c",
        "phi_differential_invariant_c",
        "phi_substitution_invariant_c",
        "phi_full_invariant_c",
        "phi_c12_product_shell_c",
        "phi_c12_abs_shell_c",
    ]
    if args.rep_filter:
        keep = {x.strip() for x in args.rep_filter.split(",") if x.strip()}
        reps = [rep for rep in reps if rep in keep]
    topologies = [
        "no_topology_baseline",
        "c12_1_2",
        "c12_reversed",
        "c12_side_broken",
        "c12_shuffled",
    ]
    if args.with_neighbor_controls:
        topologies.extend(["c10", "c11", "c13", "c14"])

    events_by_rep = {rep: b73a.event_rows_for_rep(features, rep, args.event_quantile) for rep in reps}
    rng = np.random.default_rng(args.seed + 740)
    rows = []
    for rep, events in events_by_rep.items():
        for topology in topologies:
            n_nodes, edges, notes = b73a.topology_edges(topology, rng)
            schedule, meta = b73a.build_event_schedule(events, args.steps, n_nodes)
            endogenous_values, _ = b73a.simulate_many(n_nodes, edges, schedule, args, rng)
            obs = float(np.nanmean(endogenous_values))
            if args.with_event_nulls:
                shifted = b73a.shifted_schedule(schedule, args.steps, max(7, args.steps // 5))
                random_event = b73a.random_schedule(schedule, args.steps, rng)
                shifted_values, _ = b73a.simulate_many(n_nodes, edges, shifted, args, rng)
                random_values, _ = b73a.simulate_many(n_nodes, edges, random_event, args, rng)
                effect_vs_time_shifted = obs - float(np.nanmean(shifted_values))
                effect_vs_random_event = obs - float(np.nanmean(random_values))
                p_value = b73a.p_greater(obs, np.r_[shifted_values, random_values])
            else:
                effect_vs_time_shifted = np.nan
                effect_vs_random_event = np.nan
                p_value = np.nan
            rows.append({
                "c_representation": rep,
                "topology_arm": topology,
                "n_nodes": n_nodes,
                "n_directed_edges": len(edges),
                "n_seed_events": meta["n_events"],
                "mean_bounded_differentiated_recovery": obs,
                "effect_vs_time_shifted": effect_vs_time_shifted,
                "effect_vs_random_event": effect_vs_random_event,
                "p_vs_time_shifted_and_random": p_value,
                "topology_notes": notes,
            })

    results = b73a.add_effect_contrasts(pd.DataFrame(rows))
    c12 = results[results["topology_arm"].eq("c12_1_2")].copy()
    control_cols = [
        "effect_vs_no_topology_baseline",
        "effect_vs_c12_reversed",
        "effect_vs_c12_side_broken",
        "effect_vs_c12_shuffled",
    ]
    if args.with_neighbor_controls:
        control_cols.extend(["effect_vs_c10", "effect_vs_c11", "effect_vs_c13", "effect_vs_c14"])
    c12["n_positive_specificity_controls"] = c12[control_cols].gt(0).sum(axis=1)
    c12["min_specificity_margin"] = c12[control_cols].min(axis=1)
    c12 = c12.sort_values(
        ["n_positive_specificity_controls", "mean_bounded_differentiated_recovery", "min_specificity_margin"],
        ascending=[False, False, False],
    )

    corr_cols = reps
    corr = features[corr_cols].corr(method="spearman")
    features.to_csv(outdir / "private_B7_4_phi_candidate_features.csv", index=False)
    results.to_csv(outdir / "private_B7_4_phi_prescreen_topology_results.csv", index=False)
    c12.to_csv(outdir / "private_B7_4_phi_prescreen_c12_ranking.csv", index=False)
    corr.to_csv(outdir / "private_B7_4_phi_candidate_spearman.csv")

    print(f"output_dir: {outdir}")
    print("\nC12 ranking")
    print(c12[[
        "c_representation",
        "mean_bounded_differentiated_recovery",
        "effect_vs_no_topology_baseline",
        "effect_vs_c12_reversed",
        "effect_vs_c12_side_broken",
        "effect_vs_c12_shuffled",
        *([ "effect_vs_c10", "effect_vs_c11", "effect_vs_c13", "effect_vs_c14"] if args.with_neighbor_controls else []),
        "n_positive_specificity_controls",
        "min_specificity_margin",
        "p_vs_time_shifted_and_random",
    ]].to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_4/phi_invariant")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--event-quantile", type=float, default=0.75)
    parser.add_argument("--steps", type=int, default=120)
    parser.add_argument("--n-runs", type=int, default=8)
    parser.add_argument("--seed", type=int, default=74074)
    parser.add_argument("--with-event-nulls", action="store_true")
    parser.add_argument("--with-neighbor-controls", action="store_true")
    parser.add_argument("--rep-filter", type=str, default="")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
