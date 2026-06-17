#!/usr/bin/env python3
"""Private B6J FES-guided operator-selection audit.

Boundary:
    Private only. This script does not publish, stage, commit, or push.

Purpose:
    Test whether the canonical IDPC FES state contributes uniquely to
    adaptive operator-selection policy beyond side, TFC, and phase structure.

FES provenance:
    FES labels are reconstructed from the IDPC_Reproduction cluster summary
    using the original semantic assignment rules:
      CoCreation -> max r_local_z
      Surprise   -> max abs(J_z)
      SelfGrowth -> max dphi_z
      Challenge  -> max distance_z
      Activation -> max abs(phi_z)
    with priority order CoCreation, Surprise, SelfGrowth, Challenge,
    Activation and highest-ranked unused cluster selection.
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
B6I_SCRIPT = SCRIPTS / "private_B6I_minimal_c_state_policy_audit.py"

IDPC_REPRO = Path("/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction")
IDPC_DATA = IDPC_REPRO / "IDPC_Reproduction"
IDPC_RICCI = IDPC_REPRO / "IDPC_Reproduction_ricci"
IDPC_CLUSTER_SUMMARY = IDPC_DATA / "cluster_summary_TRUE_RICCI__HYBRID_PHI.csv"
IDPC_CLUSTERED_EVENTS = IDPC_DATA / "event_level_with_clusters_TRUE_RICCI__HYBRID_PHI.csv"


STATE_REPRESENTATIONS = [
    "fes_only",
    "fes_phase",
    "fes_side",
    "fes_tfc",
    "fes_side_phase",
    "fes_tfc_phase",
    "fes_side_tfc",
    "fes_side_tfc_phase",
    "side_tfc_phase",
    "coarse",
    "side_only",
    "tfc_only",
    "phase_only",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_label(x: object) -> str:
    return str(x)


def assign_fes_from_cluster_summary(cluster_summary: pd.DataFrame) -> tuple[dict[int, str], pd.DataFrame]:
    tmp = cluster_summary.set_index("cluster")
    fes_rules = {
        "CoCreation": ("r_local_z", True),
        "Surprise": ("J_z", True),
        "SelfGrowth": ("dphi_z", True),
        "Challenge": ("distance_z", True),
        "Activation": ("phi_z", False),
    }
    priority = ["CoCreation", "Surprise", "SelfGrowth", "Challenge", "Activation"]
    candidate_lists: dict[str, list[int]] = {}
    candidate_scores: dict[str, dict[int, float]] = {}
    for fes_name, (col, descending) in fes_rules.items():
        if fes_name == "Surprise":
            scores = pd.to_numeric(tmp["J_z"], errors="coerce").abs()
        elif fes_name == "Activation":
            scores = pd.to_numeric(tmp["phi_z"], errors="coerce").abs()
        else:
            scores = pd.to_numeric(tmp[col], errors="coerce")
        ordered = list(scores.sort_values(ascending=not descending).index)
        candidate_lists[fes_name] = [int(x) for x in ordered]
        candidate_scores[fes_name] = {int(k): float(v) for k, v in scores.to_dict().items()}

    assigned: set[int] = set()
    final_map: dict[int, str] = {}
    rows = []
    for fes_name in priority:
        chosen_cluster = None
        chosen_rank = None
        chosen_score = np.nan
        for rank_idx, cluster in enumerate(candidate_lists[fes_name], start=1):
            if cluster not in assigned:
                chosen_cluster = cluster
                chosen_rank = rank_idx
                chosen_score = candidate_scores[fes_name].get(cluster, np.nan)
                break
        if chosen_cluster is not None:
            final_map[int(chosen_cluster)] = fes_name
            assigned.add(int(chosen_cluster))
            rows.append(
                {
                    "fes_phase": fes_name,
                    "assigned_cluster": int(chosen_cluster),
                    "candidate_rank_used": int(chosen_rank),
                    "score_used": float(chosen_score) if np.isfinite(chosen_score) else np.nan,
                    "all_candidates_in_order": ",".join(map(str, candidate_lists[fes_name])),
                    "selection_status": "selected",
                }
            )
        else:
            rows.append(
                {
                    "fes_phase": fes_name,
                    "assigned_cluster": np.nan,
                    "candidate_rank_used": np.nan,
                    "score_used": np.nan,
                    "all_candidates_in_order": ",".join(map(str, candidate_lists[fes_name])),
                    "selection_status": "no_available_cluster",
                }
            )
    for cluster in tmp.index:
        cluster_i = int(cluster)
        if cluster_i not in final_map:
            final_map[cluster_i] = "Unassigned"
    return final_map, pd.DataFrame(rows)


def load_recomputed_fes_events() -> tuple[pd.DataFrame, pd.DataFrame]:
    cluster_summary = pd.read_csv(IDPC_CLUSTER_SUMMARY)
    clustered = pd.read_csv(IDPC_CLUSTERED_EVENTS)
    final_map, assignment_log = assign_fes_from_cluster_summary(cluster_summary)
    out = clustered.copy()
    out["label"] = out["label"].map(normalize_label)
    out["task_idx"] = pd.to_numeric(out["task_idx"], errors="coerce")
    out["cluster"] = pd.to_numeric(out["cluster"], errors="coerce")
    out["fes_phase"] = out["cluster"].map(lambda x: final_map.get(int(x), "Unassigned") if np.isfinite(x) else "Unassigned")
    return out, assignment_log


def task_count_for_label(label: str) -> int:
    path = IDPC_RICCI / f"{label}_timeseries.csv"
    if not path.exists():
        return 30
    data = pd.read_csv(path, usecols=["task_idx"])
    vals = pd.to_numeric(data["task_idx"], errors="coerce")
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return 30
    return int(vals.max()) + 1


def add_fes_state(table: pd.DataFrame, annotated_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    annotated = pd.read_csv(annotated_path, usecols=["label", "idx_in_session"])
    point_counts = (
        annotated.groupby("label")["idx_in_session"]
        .max()
        .add(1)
        .astype(int)
        .to_dict()
    )
    fes_events, assignment_log = load_recomputed_fes_events()
    by_label = {lab: sub.sort_values("task_idx").reset_index(drop=True) for lab, sub in fes_events.groupby("label")}
    out = table.copy()
    rows = []
    for _, row in out.iterrows():
        label = str(row["label"])
        point_count = max(int(point_counts.get(label, 418)), 1)
        t_count = max(task_count_for_label(label), 1)
        task_from_point = int(np.clip(np.floor(float(row["idx_in_session"]) / point_count * t_count), 0, t_count - 1))
        fes_sub = by_label.get(label)
        if fes_sub is None or fes_sub.empty:
            rows.append(
                {
                    "fes_phase": "missing",
                    "fes_cluster": np.nan,
                    "fes_task_idx": np.nan,
                    "fes_task_from_point": task_from_point,
                    "fes_task_distance": np.nan,
                }
            )
            continue
        task_vals = pd.to_numeric(fes_sub["task_idx"], errors="coerce").to_numpy(dtype=float)
        idx = int(np.nanargmin(np.abs(task_vals - task_from_point)))
        matched = fes_sub.iloc[idx]
        rows.append(
            {
                "fes_phase": str(matched["fes_phase"]),
                "fes_cluster": int(matched["cluster"]) if np.isfinite(matched["cluster"]) else np.nan,
                "fes_task_idx": float(matched["task_idx"]),
                "fes_task_from_point": task_from_point,
                "fes_task_distance": float(abs(float(matched["task_idx"]) - task_from_point)),
            }
        )
    out = pd.concat([out.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
    return out, assignment_log


def set_state_representation(table: pd.DataFrame, representation: str) -> pd.DataFrame:
    out = table.copy()
    component_cols = {
        "fes": "fes_phase",
        "side": "boundary_side",
        "tfc": "tfc_bin",
        "phase": "phase_quadrant",
    }
    if representation == "coarse":
        out["state_label"] = out["state_label_full"].astype(str)
        return out
    parts = representation.replace("_only", "").split("_")
    labels = []
    for part in parts:
        col = component_cols.get(part)
        if col and col in out.columns:
            labels.append(part + "=" + out[col].astype(str))
    out["state_label"] = labels[0] if labels else "constant"
    for label in labels[1:]:
        out["state_label"] = out["state_label"] + "|" + label
    return out


def build_conditions(args: argparse.Namespace, b6i) -> list[dict[str, object]]:
    pools = b6i.operator_sets()
    conditions = []
    cid = 0
    for state_representation in STATE_REPRESENTATIONS:
        for endpoint_mode in args.endpoint_modes:
            for pool_name, operators in pools.items():
                cid += 1
                conditions.append(
                    {
                        "condition_id": f"b6j_{cid:03d}",
                        "state_representation": state_representation,
                        "endpoint_mode": endpoint_mode,
                        "operator_pool": pool_name,
                        "operators": operators,
                        "seed": args.seed,
                        "n_folds": args.n_folds,
                        "min_state_events": args.min_state_events,
                        "n_control_draws": args.n_control_draws,
                    }
                )
    return conditions


def condition_success(summary: pd.DataFrame) -> bool:
    by = summary.set_index("comparison")
    required = [
        "true_policy_vs_balanced_pool_shuffle",
        "true_policy_vs_frequency_matched_random",
        "true_policy_vs_performance_matched_random",
        "true_policy_vs_within_state_shuffle",
    ]
    for name in required:
        if name not in by.index:
            return False
        row = by.loc[name]
        if not (row["effect"] > 0 and row["p_greater"] <= 0.05):
            return False
    if "true_policy_vs_oracle" in by.index and not (by.loc["true_policy_vs_oracle", "effect"] < 0):
        return False
    return True


def empty_condition_summary(condition: dict[str, object]) -> pd.DataFrame:
    rows = []
    for control in [
        "balanced_pool_shuffle",
        "frequency_matched_random",
        "performance_matched_random",
        "within_state_shuffle",
        "oracle",
    ]:
        rows.append(
            {
                **{k: v for k, v in condition.items() if k != "operators"},
                "comparison": f"true_policy_vs_{control}",
                "mean_true_policy": np.nan,
                "mean_comparator": np.nan,
                "effect": np.nan,
                "p_greater": np.nan,
                "n_events": 0,
                "state_mapping_rate": np.nan,
            }
        )
    return pd.DataFrame(rows)


def state_summary(results: pd.DataFrame) -> pd.DataFrame:
    return results.groupby("state_representation", as_index=False).agg(
        n_conditions=("success", "size"),
        n_success=("success", "sum"),
        success_rate=("success", "mean"),
        mean_effect_vs_balanced=("effect_vs_balanced_pool_shuffle", "mean"),
        mean_effect_vs_frequency=("effect_vs_frequency_matched_random", "mean"),
        mean_effect_vs_performance=("effect_vs_performance_matched_random", "mean"),
        mean_effect_vs_within=("effect_vs_within_state_shuffle", "mean"),
    ).sort_values(["success_rate", "mean_effect_vs_balanced"], ascending=[False, False])


def fes_ablation_summary(results: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for factor in ["fes", "side", "tfc", "phase"]:
        has_factor = results["state_representation"].str.contains(factor, regex=False)
        for present, sub in [(True, results[has_factor]), (False, results[~has_factor])]:
            rows.append(
                {
                    "factor": factor,
                    "present": present,
                    "n_conditions": int(len(sub)),
                    "success_rate": float(np.nanmean(sub["success"].astype(float))) if len(sub) else np.nan,
                    "mean_effect_vs_balanced": float(np.nanmean(sub["effect_vs_balanced_pool_shuffle"])) if len(sub) else np.nan,
                    "mean_effect_vs_frequency": float(np.nanmean(sub["effect_vs_frequency_matched_random"])) if len(sub) else np.nan,
                    "mean_effect_vs_performance": float(np.nanmean(sub["effect_vs_performance_matched_random"])) if len(sub) else np.nan,
                    "mean_effect_vs_within": float(np.nanmean(sub["effect_vs_within_state_shuffle"])) if len(sub) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def comparison_value(states: pd.DataFrame, state: str, col: str):
    row = states[states["state_representation"].eq(state)]
    if row.empty:
        return np.nan
    return row.iloc[0][col]


def write_report(path: Path, states: pd.DataFrame, ablation: pd.DataFrame, condition_results: pd.DataFrame, assignment_log: pd.DataFrame, fes_table: pd.DataFrame, args: argparse.Namespace) -> None:
    winner = states.iloc[0]["state_representation"] if len(states) else "none"
    robust = states[states["n_success"].eq(states["n_conditions"])]
    robust_names = ", ".join(robust["state_representation"].astype(str)) if len(robust) else "none"
    lines = [
        "# Private B6J FES-Guided Operator Selection Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Purpose: test whether canonical IDPC FES contributes uniquely to adaptive operator-selection policy beyond side, TFC, and phase structure.",
        "",
        "Interpretation boundary: this does not redefine C as FES. FES is tested as a candidate operational projection of perspectival state.",
        "",
        "## FES Provenance",
        "",
        "- Source repo: IDPC_Reproduction",
        "- FES labels were reconstructed from cluster_summary_TRUE_RICCI__HYBRID_PHI.csv and event_level_with_clusters_TRUE_RICCI__HYBRID_PHI.csv using the original semantic cluster-to-FES assignment rules.",
        "- Point-to-task mapping for B6D events uses the original IDPC mapping form: task_idx = floor((idx_in_session / n_points) * T_task).",
        f"- mean FES task assignment distance: {float(np.nanmean(fes_table['fes_task_distance'])):.3f}",
        f"- max FES task assignment distance: {float(np.nanmax(fes_table['fes_task_distance'])):.3f}",
        "",
        "## Main Findings",
        "",
        f"- strongest state representation: {winner}",
        f"- fully robust state representations: {robust_names}",
        f"- FES only success rate: {comparison_value(states, 'fes_only', 'success_rate')}",
        f"- side+TFC+phase success rate: {comparison_value(states, 'side_tfc_phase', 'success_rate')}",
        f"- FES+side+TFC+phase success rate: {comparison_value(states, 'fes_side_tfc_phase', 'success_rate')}",
        f"- TFC only success rate: {comparison_value(states, 'tfc_only', 'success_rate')}",
        f"- FES+TFC success rate: {comparison_value(states, 'fes_tfc', 'success_rate')}",
        "- This audit remains about adaptive operator-selection policy, not recursive self-improvement, perspectival transport, or coordinate-transform mediation.",
        "",
        "## Recomputed FES Assignment Log",
        "",
        assignment_log.to_csv(index=False).strip(),
        "",
        "## State Representation Results",
        "",
        states.to_csv(index=False).strip(),
        "",
        "## FES Ablation Summary",
        "",
        ablation.to_csv(index=False).strip(),
        "",
        "## Condition-Level Results",
        "",
        condition_results.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- n_folds: {args.n_folds}",
        f"- min_state_events: {args.min_state_events}",
        f"- n_control_draws: {args.n_control_draws}",
        f"- n_perm: {args.n_perm}",
        f"- seed: {args.seed}",
        f"- endpoint_modes: {args.endpoint_modes}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6i = load_module("private_b6i_for_b6j", B6I_SCRIPT)
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    base = b6i.build_base_table(args)
    base, assignment_log = add_fes_state(base, args.annotated)
    base.to_csv(outdir / "private_B6J_event_table_with_fes_state.csv", index=False)
    assignment_log.to_csv(outdir / "private_B6J_recomputed_fes_assignment_log.csv", index=False)

    conditions = build_conditions(args, b6i)
    all_comparisons = []
    condition_rows = []
    original_set_state = b6i.set_state_representation
    b6i.set_state_representation = set_state_representation
    try:
        for condition in conditions:
            cv, policies = b6i.run_condition(base, condition, args)
            if cv.empty or "true_policy_reward" not in cv.columns:
                summary = empty_condition_summary(condition)
            else:
                summary = b6i.summarize_condition(cv, condition, args)
            all_comparisons.append(summary)
            success = condition_success(summary)
            row = {k: v for k, v in condition.items() if k != "operators"}
            row["n_operators"] = len(condition["operators"])
            row["success"] = success
            for _, srow in summary.iterrows():
                key = srow["comparison"].replace("true_policy_vs_", "")
                row[f"effect_vs_{key}"] = srow["effect"]
                row[f"p_vs_{key}"] = srow["p_greater"]
            condition_rows.append(row)
            cv.to_csv(outdir / f"{condition['condition_id']}_heldout_rewards.csv", index=False)
            policies.to_csv(outdir / f"{condition['condition_id']}_policies.csv", index=False)
    finally:
        b6i.set_state_representation = original_set_state

    comparisons = pd.concat(all_comparisons, ignore_index=True) if all_comparisons else pd.DataFrame()
    condition_results = pd.DataFrame(condition_rows)
    states = state_summary(condition_results)
    ablation = fes_ablation_summary(condition_results)
    comparisons.to_csv(outdir / "private_B6J_all_comparisons.csv", index=False)
    condition_results.to_csv(outdir / "private_B6J_condition_results.csv", index=False)
    states.to_csv(outdir / "private_B6J_state_representation_results.csv", index=False)
    ablation.to_csv(outdir / "private_B6J_fes_ablation_summary.csv", index=False)
    write_report(
        outdir / "private_B6J_fes_guided_operator_selection_summary.md",
        states,
        ablation,
        condition_results,
        assignment_log,
        base,
        args,
    )

    print("\nPrivate B6J FES-guided operator-selection outputs")
    print(outdir)
    print("\nState representation results")
    print(states.to_string(index=False, max_rows=80))
    print("\nFES ablation summary")
    print(ablation.to_string(index=False, max_rows=80))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6j_fes_guided_operator_selection")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--n-control-draws", type=int, default=200)
    parser.add_argument("--n-perm", type=int, default=2500)
    parser.add_argument("--seed", type=int, default=60810)
    parser.add_argument("--endpoint-modes", nargs="+", default=["z_reward", "rank_reward"])
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
