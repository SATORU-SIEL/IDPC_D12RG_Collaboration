#!/usr/bin/env python3
"""B5.4U local alignment and boundary-window audit."""

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

PRIMARY_EVENT = "b54u_lag_0"
LAGS = [-12, -8, -5, -3, -2, -1, 0, 1, 2, 3, 5, 8, 12]
SYMMETRIC_RADII = [1, 2, 3, 5, 8]
ONE_SIDED_RADII = [1, 2, 5]


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
    module = load_module("stage_b5_4r_for_b54u", B54R_SCRIPT)
    module.REPO = REPO
    module.B5_1_SCRIPT = B5_1_SCRIPT
    module.B5_2_SCRIPT = B5_2_SCRIPT
    return module


def relabel(rows: pd.DataFrame, event_class: str, role: str, rule: str) -> pd.DataFrame:
    out = rows.copy()
    out["event_class"] = event_class
    out["event_role"] = role
    out["event_rule"] = rule
    out["source_file"] = "b5_4u_local_alignment_audit"
    return out


def class_suffix(value: int) -> str:
    if value == 0:
        return "0"
    return ("plus" if value > 0 else "minus") + str(abs(value))


def shifted(base: pd.DataFrame, lag: int, max_task: float) -> pd.DataFrame:
    out = base.copy()
    out["task_idx"] = np.clip(pd.to_numeric(out["task_idx"], errors="coerce").to_numpy(dtype=float) + lag, 0.0, max_task)
    return relabel(out, f"b54u_lag_{class_suffix(lag)}", "lag_sweep", f"phase/strength preserved; event timing shifted by {lag} bins")


def expanded_window(base: pd.DataFrame, offsets: list[int], event_class: str, role: str, rule: str, max_task: float) -> pd.DataFrame:
    pieces = []
    scale = float(len(offsets))
    for offset in offsets:
        piece = base.copy()
        piece["task_idx"] = np.clip(pd.to_numeric(piece["task_idx"], errors="coerce").to_numpy(dtype=float) + offset, 0.0, max_task)
        piece["strength"] = pd.to_numeric(piece["strength"], errors="coerce").to_numpy(dtype=float) / scale
        pieces.append(piece)
    return relabel(pd.concat(pieces, ignore_index=True), event_class, role, rule)


def annotate_boundary_distance(plus: pd.DataFrame, series: pd.DataFrame) -> pd.DataFrame:
    ref = series[series["feedback_condition"].eq("plus_phi_memory")].copy()
    ref = ref[["label", "idx_in_session", "h_loop"]].copy()
    ref["task_idx"] = pd.to_numeric(ref["idx_in_session"], errors="coerce")
    ref["boundary_distance"] = np.abs(pd.to_numeric(ref["h_loop"], errors="coerce"))
    out = plus.merge(ref[["label", "task_idx", "boundary_distance"]], on=["label", "task_idx"], how="left")
    if out["boundary_distance"].isna().any():
        filled = []
        for _, row in out.iterrows():
            sub = ref[ref["label"].eq(row["label"])]
            if sub.empty:
                filled.append(np.nan)
            else:
                idx = (sub["task_idx"].astype(float) - float(row["task_idx"])).abs().idxmin()
                filled.append(float(sub.loc[idx, "boundary_distance"]))
        out["boundary_distance"] = out["boundary_distance"].fillna(pd.Series(filled, index=out.index))
    return out


def boundary_strata(plus: pd.DataFrame, series: pd.DataFrame, rng: np.random.Generator) -> list[pd.DataFrame]:
    annotated = annotate_boundary_distance(plus, series)
    ranked = annotated.sort_values("boundary_distance", na_position="last").copy()
    split_indices = np.array_split(np.arange(len(ranked)), 3)
    chunks = [ranked.iloc[idx].copy() for idx in split_indices]
    n = min(len(c) for c in chunks if len(c) > 0)
    names = [
        ("b54u_boundary_near_matched", "near-boundary tercile; count matched"),
        ("b54u_boundary_middle_matched", "middle-boundary tercile; count matched"),
        ("b54u_boundary_far_matched", "far-boundary tercile; count matched"),
    ]
    out = []
    for chunk, (event_class, rule) in zip(chunks, names):
        sample = chunk.sample(n=n, replace=False, random_state=int(rng.integers(0, 2**31 - 1)))
        out.append(relabel(sample.drop(columns=["boundary_distance"], errors="ignore"), event_class, "boundary_distance_stratum", rule))
    return out


def build_b54u_events(b54r, input_root: Path, eta: float, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_events, series = b54r.build_events(input_root, eta, seed, countmatch_samples=0)
    plus = base_events[base_events["event_class"].eq("b54r_plus_phi_memory")].copy()
    max_task = float(pd.to_numeric(series["idx_in_session"], errors="coerce").max())
    rng = np.random.default_rng(seed + 54_000)

    conditions = [shifted(plus, lag, max_task) for lag in LAGS]

    for radius in SYMMETRIC_RADII:
        offsets = list(range(-radius, radius + 1))
        conditions.append(
            expanded_window(
                plus,
                offsets,
                f"b54u_symmetric_window_r{radius}",
                "symmetric_window",
                f"symmetric window radius {radius}; strength normalized by window size",
                max_task,
            )
        )

    for radius in ONE_SIDED_RADII:
        conditions.append(
            expanded_window(
                plus,
                list(range(-radius, 1)),
                f"b54u_leading_window_r{radius}",
                "one_sided_window",
                f"leading window radius {radius}; strength normalized by window size",
                max_task,
            )
        )
        conditions.append(
            expanded_window(
                plus,
                list(range(0, radius + 1)),
                f"b54u_trailing_window_r{radius}",
                "one_sided_window",
                f"trailing window radius {radius}; strength normalized by window size",
                max_task,
            )
        )

    conditions.extend(boundary_strata(relabel(plus, PRIMARY_EVENT, "lag_sweep", "lag 0 original event geometry"), series, rng))

    events = pd.concat(conditions, ignore_index=True)
    return events.sort_values(["event_class", "label", "task_idx"]).reset_index(drop=True), series


def summarize(raw: pd.DataFrame, temporal: pd.DataFrame, quadrature: pd.DataFrame, b54r) -> pd.DataFrame:
    c12 = raw[raw["condition"].eq("endogenous") & raw["topology_name"].eq("C12(1,2)")].copy()
    c12["b54u_family_q"] = b54r.bh_fdr(c12["p_vs_time_shifted_and_random"].astype(float).tolist())
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
    show_cols = [
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
        "b54u_family_q",
        "mean_late_window_stability",
        "quadrature_error_full_mean_last40",
        "hex_bypass_delta_error",
    ]
    show_cols = [c for c in show_cols if c in summary.columns]
    primary = summary[summary["event_class"].eq(PRIMARY_EVENT)]
    lines = [
        "# B5.4U Local Alignment Audit Verdict",
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
    (outdir / "B5_4U_local_alignment_verdict.md").write_text("\n".join(lines) + "\n")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    b54r = load_b54r()
    b5_1 = load_module("stage_b5_1_for_b54u", B5_1_SCRIPT)
    b5_2 = load_module("stage_b5_2_for_b54u", B5_2_SCRIPT)
    b3 = b5_1.load_b3_module()

    events, series = build_b54u_events(b54r, Path(args.input_root), args.eta, args.seed)
    events.to_csv(outdir / "B5_4U_events.csv", index=False)
    series.to_csv(outdir / "B5_4U_series.csv", index=False)

    raw_rows = []
    null_rows = []
    event_classes = events["event_class"].drop_duplicates().tolist()
    for event_class in event_classes:
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
    nulls = pd.DataFrame(null_rows)
    temporal = pd.DataFrame([b54r.temporal_profile(b3, b5_2, events, c, args.steps, args.temporal_runs, rng) for c in event_classes])
    quadrature = pd.DataFrame([b54r.quadrature_profile(b3, events, c, args.steps, args.quadrature_runs, rng) for c in event_classes])
    summary = summarize(raw, temporal, quadrature, b54r)
    inventory = events.groupby(["event_class", "event_role"], as_index=False).agg(
        n_events=("event_class", "size"),
        n_labels=("label", "nunique"),
        min_task_idx=("task_idx", "min"),
        max_task_idx=("task_idx", "max"),
        mean_strength=("strength", "mean"),
    )

    raw.to_csv(outdir / "B5_4U_raw.csv", index=False)
    nulls.to_csv(outdir / "B5_4U_nulls.csv", index=False)
    temporal.to_csv(outdir / "B5_4U_temporal.csv", index=False)
    quadrature.to_csv(outdir / "B5_4U_quadrature.csv", index=False)
    summary.to_csv(outdir / "B5_4U_summary.csv", index=False)
    inventory.to_csv(outdir / "B5_4U_inventory.csv", index=False)
    write_verdict(outdir, summary, inventory, args)

    print(
        summary[
            [
                "event_class",
                "event_role",
                "n_seed_events",
                "mean_bounded_differentiated_recovery",
                "effect_vs_degree_null_mean",
                "p_vs_time_shifted_and_random",
                "p_vs_C8",
                "p_vs_degree_null",
                "b54u_family_q",
                "mean_late_window_stability",
            ]
        ].to_string(index=False)
    )
    print(outdir / "B5_4U_local_alignment_verdict.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path("/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/stage_b5_4t/recomputed_b5_4u"))
    parser.add_argument("--eta", type=float, default=0.075)
    parser.add_argument("--n-runs", type=int, default=140)
    parser.add_argument("--n-null-graphs", type=int, default=60)
    parser.add_argument("--n-null-runs", type=int, default=6)
    parser.add_argument("--temporal-runs", type=int, default=100)
    parser.add_argument("--quadrature-runs", type=int, default=80)
    parser.add_argument("--steps", type=int, default=240)
    parser.add_argument("--seed", type=int, default=54701)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
