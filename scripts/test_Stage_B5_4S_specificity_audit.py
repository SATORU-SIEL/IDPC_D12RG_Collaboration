#!/usr/bin/env python3
"""B5.4S specificity audit.

This audit separates aligned +eta phi memory from event-block structure and
count-matched differential-event structure before any public B5.5 expansion.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
B54R_SCRIPT = REPO / "scripts/test_Stage_B5_4R_replication_robustness.py"
B5_1_SCRIPT = REPO / "scripts/test_Stage_B5_1_phi_fes_to_c12_bridge.py"
B5_2_SCRIPT = REPO / "scripts/test_Stage_B5_2_phi_fes_to_c12_robustness.py"

PRIMARY_EVENT = "b54s_plus_phi_memory"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_b54r():
    module = load_module("stage_b5_4r_for_b54s", B54R_SCRIPT)
    module.REPO = REPO
    module.B5_1_SCRIPT = B5_1_SCRIPT
    module.B5_2_SCRIPT = B5_2_SCRIPT
    module.PRIMARY_EVENT = "b54r_plus_phi_memory"
    return module


def block_id(task_idx: pd.Series, block_size: int) -> pd.Series:
    return np.floor(pd.to_numeric(task_idx, errors="coerce").fillna(-1) / block_size).astype(int)


def relabel(rows: pd.DataFrame, event_class: str, role: str, rule: str) -> pd.DataFrame:
    out = rows.copy()
    out["event_class"] = event_class
    out["event_role"] = role
    out["event_rule"] = rule
    out["source_file"] = "b5_4s_specificity_audit"
    return out


def same_schedule_phase_strength_shuffle(plus: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    out = plus.copy()
    for _, idx in out.groupby("label", sort=False).groups.items():
        idx = list(idx)
        phase = out.loc[idx, "phase"].to_numpy(dtype=float)
        strength = out.loc[idx, "strength"].to_numpy(dtype=float)
        out.loc[idx, "phase"] = rng.permutation(phase)
        out.loc[idx, "strength"] = rng.permutation(strength)
    return relabel(
        out,
        "b54s_same_schedule_phase_strength_shuffle",
        "same_schedule_control",
        "same +eta event schedule with phase and strength permuted within label",
    )


def randomized_phase_strength_same_schedule(plus: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    out = plus.copy()
    phases = out["phase"].to_numpy(dtype=float)
    strengths = out["strength"].to_numpy(dtype=float)
    s_mu = float(np.nanmean(strengths)) if len(strengths) else 1.0
    s_sd = float(np.nanstd(strengths)) if len(strengths) else 0.0
    out["phase"] = rng.uniform(-np.pi, np.pi, size=len(out))
    out["strength"] = np.abs(rng.normal(s_mu, s_sd if s_sd > 1e-12 else 1.0, size=len(out)))
    return relabel(
        out,
        "b54s_same_schedule_random_phase_strength",
        "same_schedule_control",
        "same +eta event schedule with randomized phase and strength",
    )


def phase_preserving_timing_shuffle(plus: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    out = plus.copy()
    for _, idx in out.groupby("label", sort=False).groups.items():
        idx = list(idx)
        out.loc[idx, "task_idx"] = rng.permutation(out.loc[idx, "task_idx"].to_numpy(dtype=float))
    return relabel(
        out,
        "b54s_phase_preserving_timing_shuffle",
        "timing_control",
        "phase and strength preserved, task timing shuffled within label",
    )


def block_permuted_schedule(plus: pd.DataFrame, rng: np.random.Generator, block_size: int, max_task: float) -> pd.DataFrame:
    out = plus.copy()
    out["_block"] = block_id(out["task_idx"], block_size)
    for _, idx in out.groupby("label", sort=False).groups.items():
        idx = list(idx)
        blocks = sorted(out.loc[idx, "_block"].unique().tolist())
        if len(blocks) < 2:
            continue
        permuted = dict(zip(blocks, rng.permutation(blocks)))
        old = out.loc[idx, "_block"].to_numpy(dtype=int)
        within = out.loc[idx, "task_idx"].to_numpy(dtype=float) - old * block_size
        new_task = np.array([permuted[int(b)] for b in old], dtype=float) * block_size + within
        out.loc[idx, "task_idx"] = np.clip(new_task, 0.0, max_task)
    out = out.drop(columns=["_block"])
    return relabel(
        out,
        "b54s_block_permuted_schedule",
        "event_block_control",
        "same +eta events with task blocks permuted within label",
    )


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
    out = pd.concat(pieces, ignore_index=True).drop(columns=["_block"], errors="ignore")
    return relabel(out, event_class, role, rule)


def build_b54s_events(b54r, input_root: Path, eta: float, seed: int, block_size: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_events, series = b54r.build_events(input_root, eta, seed, countmatch_samples=0)
    plus = base_events[base_events["event_class"].eq("b54r_plus_phi_memory")].copy()
    plus = relabel(plus, PRIMARY_EVENT, "primary_phi_memory", "aligned +eta closed-loop phi memory sign-switch")
    max_task = float(pd.to_numeric(series["idx_in_session"], errors="coerce").max())
    rng = np.random.default_rng(seed + 545)

    controls = [
        same_schedule_phase_strength_shuffle(plus, rng),
        randomized_phase_strength_same_schedule(plus, rng),
        phase_preserving_timing_shuffle(plus, rng),
        block_permuted_schedule(plus, rng, block_size, max_task),
    ]

    candidate_specs = [
        (
            "b54r_shuffled_phi_memory",
            "b54s_block_matched_shuffled_phi_memory",
            "block_matched_phi_control",
            "shuffled phi memory sign-switches matched to +eta label/block counts",
        ),
        (
            "b54r_event_block_shuffled_phi_memory",
            "b54s_block_matched_event_block_shuffled_phi",
            "event_block_control",
            "event-block shuffled phi memory matched to +eta label/block counts",
        ),
        (
            "b54r_dphi_feedback",
            "b54s_block_density_matched_dphi",
            "differential_event_control",
            "dphi feedback sign-switches matched to +eta label/block counts",
        ),
        (
            "b54r_d2phi_feedback",
            "b54s_block_density_matched_d2phi",
            "differential_event_control",
            "d2phi feedback sign-switches matched to +eta label/block counts",
        ),
        (
            "b54r_lag_shifted_phi_memory",
            "b54s_block_matched_lag_shifted_phi",
            "timing_control",
            "lag-shifted phi memory sign-switches matched to +eta label/block counts",
        ),
    ]
    for source_class, event_class, role, rule in candidate_specs:
        cand = base_events[base_events["event_class"].eq(source_class)].copy()
        controls.append(match_candidate_to_target_blocks(cand, plus, event_class, role, rule, rng, block_size))

    # Replicate the count-matched differential control several times because B5.4R
    # showed that one random draw could become positive.
    dphi = base_events[base_events["event_class"].eq("b54r_dphi_feedback")].copy()
    for i in range(3):
        controls.append(
            match_candidate_to_target_blocks(
                dphi,
                plus,
                f"b54s_block_density_matched_dphi_rep{i + 1}",
                "differential_event_control",
                f"dphi feedback label/block matched replicate {i + 1}",
                rng,
                block_size,
            )
        )

    events = pd.concat([plus] + controls, ignore_index=True)
    events = events.sort_values(["event_class", "label", "task_idx"]).reset_index(drop=True)
    return events, series


def summarize(raw: pd.DataFrame, temporal: pd.DataFrame, quadrature: pd.DataFrame, b54r) -> pd.DataFrame:
    c12 = raw[raw["condition"].eq("endogenous") & raw["topology_name"].eq("C12(1,2)")].copy()
    c12["b54s_family_q"] = b54r.bh_fdr(c12["p_vs_time_shifted_and_random"].astype(float).tolist())
    if not temporal.empty:
        c12 = c12.merge(
            temporal[["event_class", "early_improvement", "mid_improvement", "late_improvement", "mean_late_window_stability", "mean_final_readout"]],
            on="event_class",
            how="left",
        )
    if not quadrature.empty:
        c12 = c12.merge(quadrature, on="event_class", how="left")
    return c12.sort_values(
        ["p_vs_time_shifted_and_random", "p_vs_degree_null", "mean_bounded_differentiated_recovery"],
        na_position="last",
    )


def write_verdict(outdir: Path, summary: pd.DataFrame, inventory: pd.DataFrame, args: argparse.Namespace) -> None:
    primary = summary[summary["event_class"].eq(PRIMARY_EVENT)]
    controls = summary[~summary["event_class"].eq(PRIMARY_EVENT)].copy()
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
        "b54s_family_q",
        "mean_late_window_stability",
        "quadrature_error_full_mean_last40",
        "hex_bypass_delta_error",
    ]
    show_cols = [c for c in show_cols if c in summary.columns]

    if primary.empty:
        verdict = "primary missing"
    else:
        p = primary.iloc[0]
        stronger_than_controls = bool(
            controls.empty
            or (
                float(p["mean_bounded_differentiated_recovery"])
                > float(controls["mean_bounded_differentiated_recovery"].max())
            )
        )
        p_specific = bool(
            controls.empty
            or (
                float(p["p_vs_time_shifted_and_random"])
                < float(controls["p_vs_time_shifted_and_random"].min())
            )
        )
        degree_specific = bool(
            controls.empty
            or float(p["p_vs_degree_null"]) < float(controls["p_vs_degree_null"].min())
        )
        if stronger_than_controls and p_specific and degree_specific:
            verdict = "strong phi-memory specificity"
        elif stronger_than_controls:
            verdict = "partial phi-memory specificity: recovery lead only"
        else:
            verdict = "not phi-memory-specific under B5.4S controls"

    lines = [
        "# B5.4S Specificity Audit Verdict",
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
        "## Verdict",
        "",
        verdict,
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
    (outdir / "private_B5_4S_specificity_verdict.md").write_text("\n".join(lines) + "\n")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    b54r = load_b54r()
    b5_1 = load_module("stage_b5_1_for_b54s", B5_1_SCRIPT)
    b5_2 = load_module("stage_b5_2_for_b54s", B5_2_SCRIPT)
    b3 = b5_1.load_b3_module()

    events, series = build_b54s_events(b54r, Path(args.input_root), args.eta, args.seed, args.block_size)
    events.to_csv(outdir / "private_B5_4S_events.csv", index=False)
    series.to_csv(outdir / "private_B5_4S_series.csv", index=False)

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
    temporal = pd.DataFrame(
        [b54r.temporal_profile(b3, b5_2, events, c, args.steps, args.temporal_runs, rng) for c in event_classes]
    )
    quadrature = pd.DataFrame(
        [b54r.quadrature_profile(b3, events, c, args.steps, args.quadrature_runs, rng) for c in event_classes]
    )
    summary = summarize(raw, temporal, quadrature, b54r)
    inventory = events.groupby(["event_class", "event_role"], as_index=False).agg(
        n_events=("event_class", "size"),
        n_labels=("label", "nunique"),
        min_task_idx=("task_idx", "min"),
        max_task_idx=("task_idx", "max"),
        mean_strength=("strength", "mean"),
    )

    raw.to_csv(outdir / "private_B5_4S_raw.csv", index=False)
    nulls.to_csv(outdir / "private_B5_4S_nulls.csv", index=False)
    temporal.to_csv(outdir / "private_B5_4S_temporal.csv", index=False)
    quadrature.to_csv(outdir / "private_B5_4S_quadrature.csv", index=False)
    summary.to_csv(outdir / "private_B5_4S_summary.csv", index=False)
    inventory.to_csv(outdir / "private_B5_4S_inventory.csv", index=False)
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
                "b54s_family_q",
                "mean_late_window_stability",
            ]
        ].to_string(index=False)
    )
    print(outdir / "private_B5_4S_specificity_verdict.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path("/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction/IDPC_Reproduction"))
    parser.add_argument("--output-dir", type=Path, default=Path("work/private_B5_4S_specificity_audit"))
    parser.add_argument("--eta", type=float, default=0.075)
    parser.add_argument("--block-size", type=int, default=50)
    parser.add_argument("--n-runs", type=int, default=140)
    parser.add_argument("--n-null-graphs", type=int, default=60)
    parser.add_argument("--n-null-runs", type=int, default=6)
    parser.add_argument("--temporal-runs", type=int, default=100)
    parser.add_argument("--quadrature-runs", type=int, default=80)
    parser.add_argument("--steps", type=int, default=240)
    parser.add_argument("--seed", type=int, default=54501)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
