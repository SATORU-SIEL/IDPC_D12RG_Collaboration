#!/usr/bin/env python3
"""Private B6I minimal C-state policy audit.

Purpose:
    Identify the minimal operational C-state representation required to
    preserve the B6E operator-selection advantage.

Boundary:
    This does not redefine C. It tests which C-state readout components are
    necessary for adaptive operator selection.
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
B6D_SCRIPT = SCRIPTS / "private_B6D_policy_specificity_audit.py"
B6E_ROBUST_SCRIPT = SCRIPTS / "private_B6E_replication_robustness_audit.py"

FULL_OPERATORS = [
    "O1_lag0_AB",
    "O2_lag5_AB",
    "O3_A_C_boundary",
    "O4_B_C_boundary",
    "O5_full_TFC",
    "O6_phase_only",
    "O7_suppress_event",
]

STATE_REPRESENTATIONS = [
    "side_only",
    "tfc_only",
    "dphi_only",
    "phase_quadrant_only",
    "lag_class_only",
    "strength_bin_only",
    "side_tfc",
    "side_dphi",
    "tfc_dphi",
    "side_phase",
    "side_lag",
    "side_strength",
    "tfc_phase",
    "tfc_lag",
    "tfc_strength",
    "side_tfc_dphi",
    "side_tfc_phase",
    "side_tfc_lag",
    "side_tfc_strength",
    "side_tfc_dphi_phase",
    "coarse",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def signflip_p(diff: np.ndarray, rng: np.random.Generator, n_perm: int) -> tuple[float, float]:
    diff = np.asarray(diff, dtype=float)
    diff = diff[np.isfinite(diff)]
    if len(diff) < 6:
        return np.nan, np.nan
    obs = float(np.nanmean(diff))
    count = 1
    for _ in range(n_perm):
        signs = rng.choice([-1.0, 1.0], size=len(diff), replace=True)
        if float(np.nanmean(diff * signs)) >= obs:
            count += 1
    return obs, count / float(n_perm + 1)


def zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = np.full_like(x, np.nan, dtype=float)
    mask = np.isfinite(x)
    if mask.sum() < 3:
        return out
    mu = np.nanmean(x[mask])
    sd = np.nanstd(x[mask])
    if not np.isfinite(sd) or sd <= 1e-12:
        out[mask] = 0.0
    else:
        out[mask] = (x[mask] - mu) / sd
    return out


def bin_series(values: pd.Series, labels: list[str]) -> pd.Series:
    v = pd.to_numeric(values, errors="coerce")
    valid = v[np.isfinite(v)]
    if len(valid) < len(labels) + 1 or valid.nunique() < len(labels):
        return pd.Series(["missing" if not np.isfinite(x) else "mid" for x in v], index=v.index)
    qs = np.linspace(0, 1, len(labels) + 1)[1:-1]
    edges = np.unique(np.nanquantile(valid, qs))
    if len(edges) < len(labels) - 1:
        return pd.Series(["missing" if not np.isfinite(x) else "mid" for x in v], index=v.index)
    return pd.cut(v, bins=[-np.inf, *edges, np.inf], labels=labels[: len(edges) + 1]).astype(str).fillna("missing")


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 890)
    labels = np.asarray(sorted(set(map(str, labels))), dtype=object)
    rng.shuffle(labels)
    return [fold for fold in np.array_split(labels, n_folds) if len(fold)]


def reward(row: pd.Series, operator: str) -> float:
    return float(row.get(f"policy_reward_{operator}", np.nan))


def weighted_reward(row: pd.Series, weights: dict[str, float]) -> float:
    vals = []
    wts = []
    for op, wt in weights.items():
        val = reward(row, op)
        if np.isfinite(val) and wt > 0:
            vals.append(val * wt)
            wts.append(wt)
    if not wts:
        return np.nan
    return float(np.sum(vals) / np.sum(wts))


def operator_sets() -> dict[str, list[str]]:
    return {
        "full": FULL_OPERATORS,
        "core_5": [op for op in FULL_OPERATORS if op not in {"O6_phase_only", "O7_suppress_event"}],
        "no_phase_only": [op for op in FULL_OPERATORS if op != "O6_phase_only"],
        "no_suppress": [op for op in FULL_OPERATORS if op != "O7_suppress_event"],
    }


def add_lag_class(table: pd.DataFrame) -> pd.DataFrame:
    out = table.sort_values(["label", "idx_in_session"]).copy()
    pieces = []
    for _, sub in out.groupby("label", sort=False):
        sub = sub.copy()
        gap = pd.to_numeric(sub["idx_in_session"], errors="coerce").diff()
        sub["lag_class"] = bin_series(gap, ["short", "mid", "long"])
        pieces.append(sub)
    return pd.concat(pieces, ignore_index=True)


def build_base_table(args: argparse.Namespace) -> pd.DataFrame:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6d = load_module("private_b6d_for_b6i", B6D_SCRIPT)
    robust = load_module("private_b6e_robust_for_b6i", B6E_ROBUST_SCRIPT)
    table = b6d.build_state_table(args)
    table = add_lag_class(table)
    # Ensure the previous known variants are present for compatibility.
    table = robust.set_state_variant(table, "coarse")
    return table


def set_state_representation(table: pd.DataFrame, representation: str) -> pd.DataFrame:
    out = table.copy()
    component_cols = {
        "side": "boundary_side",
        "tfc": "tfc_bin",
        "dphi": "phase_activity_bin",
        "phase": "phase_quadrant",
        "lag": "lag_class",
        "strength": "strength_bin",
    }
    if representation == "coarse":
        out["state_label"] = (
            "side=" + out["boundary_side"].astype(str)
            + "|tfc=" + out["tfc_bin"].astype(str)
            + "|dphi=" + out["phase_activity_bin"].astype(str)
            + "|str=" + out["strength_bin"].astype(str)
        )
        return out
    parts = representation.replace("_only", "").split("_")
    labels = []
    for part in parts:
        col = component_cols.get(part)
        if col is not None and col in out.columns:
            labels.append(part + "=" + out[col].astype(str))
    if not labels:
        out["state_label"] = "constant"
    else:
        state = labels[0]
        for label in labels[1:]:
            state = state + "|" + label
        out["state_label"] = state
    return out


def add_endpoint_columns(table: pd.DataFrame, endpoint_mode: str, operators: list[str]) -> pd.DataFrame:
    out = table.copy()
    for op in operators:
        base = pd.to_numeric(out[f"{op}_z"], errors="coerce").to_numpy(dtype=float)
        if endpoint_mode == "z_reward":
            vals = base
        elif endpoint_mode == "rank_reward":
            vals = pd.Series(base).rank(pct=True).to_numpy(dtype=float)
            vals = zscore(vals)
        else:
            raise ValueError(f"unknown endpoint mode {endpoint_mode}")
        out[f"policy_reward_{op}"] = vals
    return out


def train_policy(train: pd.DataFrame, operators: list[str], min_state_events: int) -> tuple[dict[str, str], str, pd.DataFrame]:
    global_means = {op: float(np.nanmean(train[f"policy_reward_{op}"])) for op in operators}
    global_best = max(global_means, key=global_means.get)
    mapping = {}
    rows = []
    for state, sub in train.groupby("state_label", sort=False):
        if len(sub) < min_state_events:
            continue
        means = {op: float(np.nanmean(sub[f"policy_reward_{op}"])) for op in operators}
        selected = max(means, key=means.get)
        mapping[str(state)] = selected
        row = {
            "state_label": str(state),
            "n_train_events": int(len(sub)),
            "selected_operator": selected,
            "selected_train_reward": means[selected],
            "global_best_operator": global_best,
            "global_best_train_reward": means[global_best],
        }
        row.update({f"train_mean_{op}": means[op] for op in operators})
        rows.append(row)
    return mapping, global_best, pd.DataFrame(rows)


def operator_frequency_weights(ops: list[str], operators: list[str]) -> dict[str, float]:
    counts = {op: 0 for op in operators}
    for op in ops:
        if op in counts:
            counts[op] += 1
    total = float(sum(counts.values()))
    if total <= 0:
        return {op: 1.0 / len(operators) for op in operators}
    return {op: counts[op] / total for op in operators}


def performance_strata(train: pd.DataFrame, operators: list[str]) -> dict[str, str]:
    means = {op: float(np.nanmean(train[f"policy_reward_{op}"])) for op in operators}
    ordered = sorted(operators, key=lambda op: means[op])
    strata = {}
    chunks = np.array_split(np.asarray(ordered, dtype=object), min(3, len(ordered)))
    for label, chunk in zip(["low", "mid", "high"], chunks):
        for op in chunk:
            strata[str(op)] = label
    return strata


def stratum_matched_expected_reward(row: pd.Series, selected_op: str, strata: dict[str, str], operators: list[str]) -> float:
    stratum = strata.get(selected_op, "missing")
    candidates = [op for op in operators if strata.get(op) == stratum]
    if not candidates:
        candidates = operators
    weights = {op: 1.0 / len(candidates) for op in candidates}
    return weighted_reward(row, weights)


def within_state_shuffled_policy(policy_table: pd.DataFrame, operators: list[str], rng: np.random.Generator) -> dict[str, str]:
    mapping = {}
    op_array = np.asarray(operators, dtype=object)
    for _, row in policy_table.iterrows():
        shuffled_labels = op_array.copy()
        rng.shuffle(shuffled_labels)
        means = {shuffled_op: float(row[f"train_mean_{op}"]) for op, shuffled_op in zip(operators, shuffled_labels)}
        mapping[str(row["state_label"])] = max(means, key=means.get)
    return mapping


def run_condition(base_table: pd.DataFrame, condition: dict[str, object], args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(int(condition["seed"]) + 900)
    operators = list(condition["operators"])
    table = set_state_representation(base_table, str(condition["state_representation"]))
    table = add_endpoint_columns(table, str(condition["endpoint_mode"]), operators)
    folds = make_folds(table["label"].astype(str).unique(), int(condition["n_folds"]), int(condition["seed"]))
    rows = []
    policies = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = table["label"].astype(str).isin(set(test_labels))
        train = table[~test_mask].copy()
        test = table[test_mask].copy().reset_index(drop=True)
        mapping, fallback, policy_table = train_policy(train, operators, int(condition["min_state_events"]))
        if policy_table.empty:
            continue
        policy_table["fold"] = fold_index
        policies.extend(policy_table.to_dict("records"))
        true_ops = [mapping.get(str(row["state_label"]), fallback) for _, row in test.iterrows()]
        freq_weights = operator_frequency_weights(true_ops, operators)
        strata = performance_strata(train, operators)
        within_rewards = np.zeros(len(test), dtype=float)
        within_counts = np.zeros(len(test), dtype=float)
        balanced_rewards = np.zeros(len(test), dtype=float)
        balanced_counts = np.zeros(len(test), dtype=float)
        for _ in range(int(condition["n_control_draws"])):
            shuffled_mapping = within_state_shuffled_policy(policy_table, operators, rng)
            shuffled_ops = np.asarray(true_ops, dtype=object).copy()
            for stratum in ["low", "mid", "high"]:
                idx = [i for i, op in enumerate(shuffled_ops) if strata.get(str(op)) == stratum]
                if len(idx) > 1:
                    vals = shuffled_ops[idx].copy()
                    rng.shuffle(vals)
                    shuffled_ops[idx] = vals
            for i, (_, row) in enumerate(test.iterrows()):
                state = str(row["state_label"])
                op = shuffled_mapping.get(state, fallback)
                val = reward(row, op)
                if np.isfinite(val):
                    within_rewards[i] += val
                    within_counts[i] += 1.0
                val = reward(row, str(shuffled_ops[i]))
                if np.isfinite(val):
                    balanced_rewards[i] += val
                    balanced_counts[i] += 1.0
        for i, (_, row) in enumerate(test.iterrows()):
            true_op = true_ops[i]
            rows.append(
                {
                    "condition_id": condition["condition_id"],
                    "fold": fold_index,
                    "label": row["label"],
                    "idx_in_session": row["idx_in_session"],
                    "state_label": row["state_label"],
                    "true_policy_operator": true_op,
                    "true_policy_source": "state_mapping" if str(row["state_label"]) in mapping else "global_fallback",
                    "true_policy_reward": reward(row, true_op),
                    "balanced_pool_shuffle_reward": float(balanced_rewards[i] / balanced_counts[i]) if balanced_counts[i] > 0 else np.nan,
                    "frequency_matched_random_reward": weighted_reward(row, freq_weights),
                    "performance_matched_random_reward": stratum_matched_expected_reward(row, true_op, strata, operators),
                    "within_state_shuffle_reward": float(within_rewards[i] / within_counts[i]) if within_counts[i] > 0 else np.nan,
                    "oracle_reward": max(
                        [reward(row, op) for op in operators if np.isfinite(reward(row, op))],
                        default=np.nan,
                    ),
                }
            )
    policies_df = pd.DataFrame(policies)
    if not policies_df.empty:
        policies_df["condition_id"] = condition["condition_id"]
    return pd.DataFrame(rows), policies_df


def summarize_condition(cv: pd.DataFrame, condition: dict[str, object], args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(int(condition["seed"]) + 910)
    true_values = pd.to_numeric(cv["true_policy_reward"], errors="coerce").to_numpy(dtype=float)
    controls = [
        "balanced_pool_shuffle",
        "frequency_matched_random",
        "performance_matched_random",
        "within_state_shuffle",
        "oracle",
    ]
    rows = []
    for control in controls:
        values = pd.to_numeric(cv[f"{control}_reward"], errors="coerce").to_numpy(dtype=float)
        effect, p = signflip_p(true_values - values, rng, args.n_perm)
        rows.append(
            {
                **{k: v for k, v in condition.items() if k != "operators"},
                "comparison": f"true_policy_vs_{control}",
                "mean_true_policy": float(np.nanmean(true_values)),
                "mean_comparator": float(np.nanmean(values)),
                "effect": effect,
                "p_greater": p,
                "n_events": int(np.isfinite(true_values - values).sum()),
                "state_mapping_rate": float(np.nanmean(cv["true_policy_source"].eq("state_mapping"))),
            }
        )
    return pd.DataFrame(rows)


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


def build_conditions(args: argparse.Namespace) -> list[dict[str, object]]:
    pools = operator_sets()
    conditions = []
    cid = 0
    for state_representation in STATE_REPRESENTATIONS:
        for endpoint_mode in args.endpoint_modes:
            for pool_name, operators in pools.items():
                cid += 1
                conditions.append(
                    {
                        "condition_id": f"b6i_{cid:03d}",
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


def factor_summary(results: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for factor in ["side", "tfc", "dphi", "phase", "lag", "strength"]:
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


def minimal_successful_state(states: pd.DataFrame) -> pd.DataFrame:
    successful = states[states["n_success"].gt(0)].copy()
    successful["n_components"] = successful["state_representation"].apply(
        lambda s: 4 if s == "coarse" else len(str(s).replace("_only", "").split("_"))
    )
    return successful.sort_values(["n_components", "success_rate", "mean_effect_vs_balanced"], ascending=[True, False, False]).head(10)


def write_report(path: Path, state_results: pd.DataFrame, factor_results: pd.DataFrame, top_states: pd.DataFrame, condition_results: pd.DataFrame, args: argparse.Namespace) -> None:
    minimal_partial = top_states.iloc[0]["state_representation"] if not top_states.empty else "none"
    robust = state_results[state_results["n_success"].eq(state_results["n_conditions"])].copy()
    if not robust.empty:
        robust["n_components"] = robust["state_representation"].apply(
            lambda s: 4 if s == "coarse" else len(str(s).replace("_only", "").split("_"))
        )
        minimal_robust = robust.sort_values(
            ["n_components", "mean_effect_vs_balanced"], ascending=[True, False]
        ).iloc[0]["state_representation"]
    else:
        minimal_robust = "none"
    strongest = state_results.iloc[0]["state_representation"] if not state_results.empty else "none"
    side_needed = factor_results[(factor_results["factor"].eq("side")) & (factor_results["present"].eq(True))]["success_rate"].iloc[0] > factor_results[(factor_results["factor"].eq("side")) & (factor_results["present"].eq(False))]["success_rate"].iloc[0]
    tfc_needed = factor_results[(factor_results["factor"].eq("tfc")) & (factor_results["present"].eq(True))]["success_rate"].iloc[0] > factor_results[(factor_results["factor"].eq("tfc")) & (factor_results["present"].eq(False))]["success_rate"].iloc[0]
    lines = [
        "# Private B6I Minimal C-State Policy Audit",
        "",
        "Status: local/private screen only. No publication, commit, or push was performed.",
        "",
        "Purpose: identify the minimal operational C-state representation needed for performance-relevant operator selection.",
        "",
        "Interpretation boundary: this does not redefine C as side, TFC, dphi, phase, lag, or strength. These are operational C-state components only.",
        "",
        "## Main Findings",
        "",
        f"- minimal partially successful state representation: {minimal_partial}",
        f"- minimal fully robust state representation: {minimal_robust}",
        f"- strongest state representation: {strongest}",
        f"- side improves success rate: {side_needed}",
        f"- TFC improves success rate: {tfc_needed}",
        "- This audit remains about adaptive meta-control policy, not recursive self-improvement or perspectival transport.",
        "",
        "## State Representation Results",
        "",
        state_results.to_csv(index=False).strip(),
        "",
        "## Factor Ablation Summary",
        "",
        factor_results.to_csv(index=False).strip(),
        "",
        "## Top Successful States",
        "",
        top_states.to_csv(index=False).strip() if not top_states.empty else "none",
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
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    base_table = build_base_table(args)
    conditions = build_conditions(args)
    all_comparisons = []
    condition_rows = []
    for condition in conditions:
        cv, policies = run_condition(base_table, condition, args)
        summary = summarize_condition(cv, condition, args)
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

    comparisons = pd.concat(all_comparisons, ignore_index=True) if all_comparisons else pd.DataFrame()
    condition_results = pd.DataFrame(condition_rows)
    state_results = state_summary(condition_results)
    factors = factor_summary(condition_results)
    top_states = minimal_successful_state(state_results)
    comparisons.to_csv(outdir / "private_B6I_all_comparisons.csv", index=False)
    condition_results.to_csv(outdir / "private_B6I_condition_results.csv", index=False)
    state_results.to_csv(outdir / "private_B6I_state_representation_results.csv", index=False)
    factors.to_csv(outdir / "private_B6I_factor_ablation_summary.csv", index=False)
    top_states.to_csv(outdir / "private_B6I_top_successful_states.csv", index=False)
    write_report(outdir / "private_B6I_minimal_c_state_policy_summary.md", state_results, factors, top_states, condition_results, args)

    print("\nPrivate B6I minimal C-state policy outputs")
    print(outdir)
    print("\nState representation results")
    print(state_results.to_string(index=False, max_rows=80))
    print("\nTop successful states")
    print(top_states.to_string(index=False, max_rows=20))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6i_minimal_c_state_policy")
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
