#!/usr/bin/env python3
"""B5.4T timing / geometry decomposition audit."""

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

PRIMARY_EVENT = "b54t_original_phi_geometry"


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
    module = load_module("stage_b5_4r_for_b54t", B54R_SCRIPT)
    module.REPO = REPO
    module.B5_1_SCRIPT = B5_1_SCRIPT
    module.B5_2_SCRIPT = B5_2_SCRIPT
    return module


def block_id(task_idx: pd.Series, block_size: int) -> pd.Series:
    return np.floor(pd.to_numeric(task_idx, errors="coerce").fillna(-1) / block_size).astype(int)


def relabel(rows: pd.DataFrame, event_class: str, role: str, rule: str) -> pd.DataFrame:
    out = rows.copy()
    out["event_class"] = event_class
    out["event_role"] = role
    out["event_rule"] = rule
    out["source_file"] = "b5_4t_timing_geometry_decomposition"
    return out


def random_strength_like(strengths: pd.Series, rng: np.random.Generator, n: int) -> np.ndarray:
    x = pd.to_numeric(strengths, errors="coerce").to_numpy(dtype=float)
    mu = float(np.nanmean(x)) if len(x) else 1.0
    sd = float(np.nanstd(x)) if len(x) else 1.0
    return np.abs(rng.normal(mu, sd if sd > 1e-12 else 1.0, size=n))


def randomize_phase(out: pd.DataFrame, rng: np.random.Generator) -> None:
    out["phase"] = rng.uniform(-np.pi, np.pi, size=len(out))


def randomize_strength(out: pd.DataFrame, base: pd.DataFrame, rng: np.random.Generator) -> None:
    out["strength"] = random_strength_like(base["strength"], rng, len(out))


def shuffle_timing_within_label(out: pd.DataFrame, rng: np.random.Generator) -> None:
    for _, idx in out.groupby("label", sort=False).groups.items():
        idx = list(idx)
        out.loc[idx, "task_idx"] = rng.permutation(out.loc[idx, "task_idx"].to_numpy(dtype=float))


def shuffle_phase_strength_within_label(out: pd.DataFrame, rng: np.random.Generator) -> None:
    for _, idx in out.groupby("label", sort=False).groups.items():
        idx = list(idx)
        out.loc[idx, "phase"] = rng.permutation(out.loc[idx, "phase"].to_numpy(dtype=float))
        out.loc[idx, "strength"] = rng.permutation(out.loc[idx, "strength"].to_numpy(dtype=float))


def global_density_only(base: pd.DataFrame, rng: np.random.Generator, max_task: float) -> pd.DataFrame:
    out = base.copy()
    labels = base["label"].drop_duplicates().to_numpy()
    out["label"] = rng.choice(labels, size=len(out), replace=True)
    out["task_idx"] = rng.uniform(0.0, max_task, size=len(out))
    randomize_phase(out, rng)
    randomize_strength(out, base, rng)
    return relabel(out, "b54t_event_density_only", "density_control", "total event count only; label, timing, phase, and strength randomized")


def block_structure_only(base: pd.DataFrame, rng: np.random.Generator, block_size: int) -> pd.DataFrame:
    out = base.copy()
    out["_block"] = block_id(out["task_idx"], block_size)
    new_task = []
    for _, row in out.iterrows():
        lo = max(0.0, float(row["_block"]) * block_size)
        hi = lo + block_size - 1.0
        new_task.append(float(rng.uniform(lo, hi)))
    out["task_idx"] = new_task
    randomize_phase(out, rng)
    randomize_strength(out, base, rng)
    out = out.drop(columns=["_block"])
    return relabel(out, "b54t_block_structure_only", "block_control", "label/block counts preserved; timing, phase, and strength randomized inside blocks")


def shifted(base: pd.DataFrame, shift: int, max_task: float) -> pd.DataFrame:
    out = base.copy()
    out["task_idx"] = np.clip(pd.to_numeric(out["task_idx"], errors="coerce").to_numpy(dtype=float) + shift, 0.0, max_task)
    sign = "plus" if shift > 0 else "minus"
    return relabel(out, f"b54t_local_shift_{sign}{abs(shift)}", "local_alignment_control", f"original phase/strength shifted by {shift} bins")


def match_candidate_to_target_blocks(
    candidate: pd.DataFrame,
    target: pd.DataFrame,
    event_class: str,
    role: str,
    rule: str,
    rng: np.random.Generator,
    block_size: int,
) -> pd.DataFrame:
    cand = candidate.copy()
    tgt = target.copy()
    cand["_block"] = block_id(cand["task_idx"], block_size)
    tgt["_block"] = block_id(tgt["task_idx"], block_size)
    pieces = []
    for (label, blk), sub_tgt in tgt.groupby(["label", "_block"], sort=False):
        sub_cand = cand[cand["label"].eq(label) & cand["_block"].eq(blk)]
        if sub_cand.empty:
            sub_cand = cand[cand["label"].eq(label)]
        if sub_cand.empty:
            sub_cand = cand
        replace = len(sub_cand) < len(sub_tgt)
        sample = sub_cand.sample(
            n=len(sub_tgt),
            replace=replace,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        pieces.append(sample)
    return relabel(pd.concat(pieces, ignore_index=True).drop(columns=["_block"], errors="ignore"), event_class, role, rule)


def make_condition(base: pd.DataFrame, event_class: str, role: str, rule: str, rng: np.random.Generator, keep_timing: bool, keep_phase: bool, keep_strength: bool) -> pd.DataFrame:
    out = base.copy()
    if not keep_timing:
        shuffle_timing_within_label(out, rng)
    if not keep_phase:
        randomize_phase(out, rng)
    if not keep_strength:
        randomize_strength(out, base, rng)
    return relabel(out, event_class, role, rule)


def build_b54t_events(b54r, input_root: Path, eta: float, seed: int, block_size: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_events, series = b54r.build_events(input_root, eta, seed, countmatch_samples=0)
    plus = base_events[base_events["event_class"].eq("b54r_plus_phi_memory")].copy()
    plus = relabel(plus, PRIMARY_EVENT, "primary_phi_geometry", "original +eta phi-derived timing, phase, and strength")
    max_task = float(pd.to_numeric(series["idx_in_session"], errors="coerce").max())
    rng = np.random.default_rng(seed + 54_000)

    conditions = [
        plus,
        make_condition(plus, "b54t_timing_only", "factorial_ablation", "timing kept; phase and strength randomized", rng, True, False, False),
        make_condition(plus, "b54t_phase_strength_only", "factorial_ablation", "phase/strength kept; timing shuffled within label", rng, False, True, True),
        make_condition(plus, "b54t_phase_only", "factorial_ablation", "phase kept; timing shuffled and strength randomized", rng, False, True, False),
        make_condition(plus, "b54t_strength_only", "factorial_ablation", "strength kept; timing shuffled and phase randomized", rng, False, False, True),
        make_condition(plus, "b54t_timing_phase", "factorial_ablation", "timing and phase kept; strength randomized", rng, True, True, False),
        make_condition(plus, "b54t_timing_strength", "factorial_ablation", "timing and strength kept; phase randomized", rng, True, False, True),
        make_condition(plus, "b54t_phase_strength", "factorial_ablation", "phase and strength kept; timing shuffled", rng, False, True, True),
        block_structure_only(plus, rng, block_size),
        global_density_only(plus, rng, max_task),
    ]

    dphi = base_events[base_events["event_class"].eq("b54r_dphi_feedback")].copy()
    conditions.append(
        match_candidate_to_target_blocks(
            dphi,
            plus,
            "b54t_dphi_density_block_matched",
            "differential_event_control",
            "dphi event schedule matched to +eta label/block counts",
            rng,
            block_size,
        )
    )

    for shift_value in [-5, -2, -1, 1, 2, 5]:
        conditions.append(shifted(plus, shift_value, max_task))

    events = pd.concat(conditions, ignore_index=True)
    return events.sort_values(["event_class", "label", "task_idx"]).reset_index(drop=True), series


def summarize(raw: pd.DataFrame, temporal: pd.DataFrame, quadrature: pd.DataFrame, b54r) -> pd.DataFrame:
    c12 = raw[raw["condition"].eq("endogenous") & raw["topology_name"].eq("C12(1,2)")].copy()
    c12["b54t_family_q"] = b54r.bh_fdr(c12["p_vs_time_shifted_and_random"].astype(float).tolist())
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
        "b54t_family_q",
        "mean_late_window_stability",
        "quadrature_error_full_mean_last40",
        "hex_bypass_delta_error",
    ]
    show_cols = [c for c in show_cols if c in summary.columns]
    primary = summary[summary["event_class"].eq(PRIMARY_EVENT)]
    lines = [
        "# B5.4T Timing / Geometry Decomposition Verdict",
        "",
        "Execution after preregistration. Review before public result-sharing.",
        "",
        "## Settings",
        "",
        f"- eta: {args.eta}",
        f"- block_size: {args.block_size}",
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
    (outdir / "B5_4T_timing_geometry_verdict.md").write_text("\n".join(lines) + "\n")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    b54r = load_b54r()
    b5_1 = load_module("stage_b5_1_for_b54t", B5_1_SCRIPT)
    b5_2 = load_module("stage_b5_2_for_b54t", B5_2_SCRIPT)
    b3 = b5_1.load_b3_module()

    events, series = build_b54t_events(b54r, Path(args.input_root), args.eta, args.seed, args.block_size)
    events.to_csv(outdir / "B5_4T_events.csv", index=False)
    series.to_csv(outdir / "B5_4T_series.csv", index=False)

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

    raw.to_csv(outdir / "B5_4T_raw.csv", index=False)
    nulls.to_csv(outdir / "B5_4T_nulls.csv", index=False)
    temporal.to_csv(outdir / "B5_4T_temporal.csv", index=False)
    quadrature.to_csv(outdir / "B5_4T_quadrature.csv", index=False)
    summary.to_csv(outdir / "B5_4T_summary.csv", index=False)
    inventory.to_csv(outdir / "B5_4T_inventory.csv", index=False)
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
                "b54t_family_q",
                "mean_late_window_stability",
            ]
        ].to_string(index=False)
    )
    print(outdir / "B5_4T_timing_geometry_verdict.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path("/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/stage_b5_4t/recomputed"))
    parser.add_argument("--eta", type=float, default=0.075)
    parser.add_argument("--block-size", type=int, default=50)
    parser.add_argument("--n-runs", type=int, default=140)
    parser.add_argument("--n-null-graphs", type=int, default=60)
    parser.add_argument("--n-null-runs", type=int, default=6)
    parser.add_argument("--temporal-runs", type=int, default=100)
    parser.add_argument("--quadrature-runs", type=int, default=80)
    parser.add_argument("--steps", type=int, default=240)
    parser.add_argument("--seed", type=int, default=54601)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
