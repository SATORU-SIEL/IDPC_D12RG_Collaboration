#!/usr/bin/env python3
"""Private B6E replication and robustness audit.

Purpose:
    Replicate B6E across label holdouts, windows, state binning, endpoint
    transforms, and operator-pool variants.

Boundary:
    This consolidates C-state -> operator-selection policy support. It does
    not claim recursive self-updating intelligence.
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
B6E_SCRIPT = SCRIPTS / "private_B6E_balanced_operator_pool_audit.py"

FULL_OPERATORS = [
    "O1_lag0_AB",
    "O2_lag5_AB",
    "O3_A_C_boundary",
    "O4_B_C_boundary",
    "O5_full_TFC",
    "O6_phase_only",
    "O7_suppress_event",
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


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 760)
    labels = np.asarray(sorted(set(map(str, labels))), dtype=object)
    rng.shuffle(labels)
    return [fold for fold in np.array_split(labels, n_folds) if len(fold)]


def reward(row: pd.Series, operator: str, endpoint: str) -> float:
    return float(row.get(f"{endpoint}_{operator}", np.nan))


def weighted_reward(row: pd.Series, weights: dict[str, float], endpoint: str) -> float:
    vals = []
    wts = []
    for op, wt in weights.items():
        val = reward(row, op, endpoint)
        if np.isfinite(val) and wt > 0:
            vals.append(val * wt)
            wts.append(wt)
    if not wts:
        return np.nan
    return float(np.sum(vals) / np.sum(wts))


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


def add_endpoint_columns(table: pd.DataFrame, endpoint_mode: str, operators: list[str]) -> pd.DataFrame:
    out = table.copy()
    for op in operators:
        base = pd.to_numeric(out[f"{op}_z"], errors="coerce").to_numpy(dtype=float)
        if endpoint_mode == "z_reward":
            vals = base
        elif endpoint_mode == "positive_only":
            vals = np.where(np.isfinite(base), np.maximum(base, 0.0), np.nan)
        elif endpoint_mode == "rank_reward":
            vals = pd.Series(base).rank(pct=True).to_numpy(dtype=float)
            vals = zscore(vals)
        else:
            raise ValueError(f"unknown endpoint_mode {endpoint_mode}")
        out[f"policy_reward_{op}"] = vals
    return out


def set_state_variant(table: pd.DataFrame, state_variant: str) -> pd.DataFrame:
    out = table.copy()
    if state_variant == "coarse":
        return out
    if state_variant == "side_tfc":
        out["state_label"] = "side=" + out["boundary_side"].astype(str) + "|tfc=" + out["tfc_bin"].astype(str)
    elif state_variant == "side_tfc_dphi":
        out["state_label"] = (
            "side=" + out["boundary_side"].astype(str)
            + "|tfc=" + out["tfc_bin"].astype(str)
            + "|dphi=" + out["phase_activity_bin"].astype(str)
        )
    elif state_variant == "full":
        out["state_label"] = out["state_label_full"].astype(str)
    else:
        raise ValueError(f"unknown state_variant {state_variant}")
    return out


def train_policy(train: pd.DataFrame, operators: list[str], min_state_events: int) -> tuple[dict[str, str], str, pd.DataFrame]:
    global_means = {op: float(np.nanmean(train[f"policy_reward_{op}"])) for op in operators}
    global_best = max(global_means, key=global_means.get)
    rows = []
    mapping: dict[str, str] = {}
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
    return weighted_reward(row, weights, "policy_reward")


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
    operators = list(condition["operators"])
    table = base_table.copy()
    table = set_state_variant(table, str(condition["state_variant"]))
    table = add_endpoint_columns(table, str(condition["endpoint_mode"]), operators)
    rng = np.random.default_rng(int(condition["seed"]) + 770)
    folds = make_folds(table["label"].astype(str).unique(), int(condition["n_folds"]), int(condition["seed"]))
    rows = []
    policy_rows = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = table["label"].astype(str).isin(set(test_labels))
        train = table[~test_mask].copy()
        test = table[test_mask].copy().reset_index(drop=True)
        mapping, fallback, policy_table = train_policy(train, operators, int(condition["min_state_events"]))
        if policy_table.empty:
            continue
        policy_table["fold"] = fold_index
        policy_rows.extend(policy_table.to_dict("records"))
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
                val = reward(row, shuffled_mapping.get(state, fallback), "policy_reward")
                if np.isfinite(val):
                    within_rewards[i] += val
                    within_counts[i] += 1.0
                val = reward(row, str(shuffled_ops[i]), "policy_reward")
                if np.isfinite(val):
                    balanced_rewards[i] += val
                    balanced_counts[i] += 1.0

        for i, (_, row) in enumerate(test.iterrows()):
            true_op = true_ops[i]
            out = {
                "condition_id": condition["condition_id"],
                "label": row["label"],
                "idx_in_session": row["idx_in_session"],
                "fold": fold_index,
                "state_label": row["state_label"],
                "true_policy_operator": true_op,
                "true_policy_source": "state_mapping" if str(row["state_label"]) in mapping else "global_fallback",
                "true_policy_reward": reward(row, true_op, "policy_reward"),
                "balanced_pool_shuffle_reward": float(balanced_rewards[i] / balanced_counts[i]) if balanced_counts[i] > 0 else np.nan,
                "frequency_matched_random_reward": weighted_reward(row, freq_weights, "policy_reward"),
                "performance_matched_random_reward": stratum_matched_expected_reward(row, true_op, strata, operators),
                "within_state_shuffle_reward": float(within_rewards[i] / within_counts[i]) if within_counts[i] > 0 else np.nan,
                "oracle_reward": max(
                    [reward(row, op, "policy_reward") for op in operators if np.isfinite(reward(row, op, "policy_reward"))],
                    default=np.nan,
                ),
            }
            rows.append(out)
    policy_df = pd.DataFrame(policy_rows)
    if not policy_df.empty:
        policy_df["condition_id"] = condition["condition_id"]
    return pd.DataFrame(rows), policy_df


def summarize_condition(cv: pd.DataFrame, condition: dict[str, object], args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(int(condition["seed"]) + 780)
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
                **condition,
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
    operator_sets = {
        "full": FULL_OPERATORS,
        "no_suppress": [op for op in FULL_OPERATORS if op != "O7_suppress_event"],
        "no_phase_only": [op for op in FULL_OPERATORS if op != "O6_phase_only"],
        "core_5": [op for op in FULL_OPERATORS if op not in {"O6_phase_only", "O7_suppress_event"}],
    }
    conditions = []
    cid = 0
    for seed in args.seeds:
        for n_folds in args.fold_counts:
            for state_variant in args.state_variants:
                for endpoint_mode in args.endpoint_modes:
                    for op_name, operators in operator_sets.items():
                        cid += 1
                        conditions.append(
                            {
                                "condition_id": f"b6e_robust_{cid:03d}",
                                "seed": int(seed),
                                "n_folds": int(n_folds),
                                "state_variant": state_variant,
                                "endpoint_mode": endpoint_mode,
                                "operator_pool": op_name,
                                "operators": operators,
                                "min_state_events": args.min_state_events,
                                "n_control_draws": args.n_control_draws,
                            }
                        )
    return conditions


def write_report(path: Path, aggregate: pd.DataFrame, successes: pd.DataFrame, settings: argparse.Namespace) -> None:
    success_rate = float(np.nanmean(aggregate["success"].astype(float))) if not aggregate.empty else np.nan
    lines = [
        "# Private B6E Replication / Robustness Audit",
        "",
        "Status: local/private screen only. No publication, commit, or push was performed.",
        "",
        "Purpose: test whether B6E survives changes in label holdout, C-state binning, endpoint transform, and operator pool.",
        "",
        "Boundary: this supports or weakens `C-state carries performance-relevant operator-selection policy`; it does not test recursive self-updating intelligence.",
        "",
        "## Aggregate",
        "",
        f"- conditions tested: {len(aggregate)}",
        f"- success rate: {success_rate:.6f}",
        "",
        aggregate.to_csv(index=False).strip(),
        "",
        "## Successful Conditions",
        "",
        successes.to_csv(index=False).strip() if not successes.empty else "none",
        "",
        "## Settings",
        "",
        f"- window: {settings.window}",
        f"- min_state_events: {settings.min_state_events}",
        f"- n_control_draws: {settings.n_control_draws}",
        f"- n_perm: {settings.n_perm}",
        f"- seeds: {settings.seeds}",
        f"- fold_counts: {settings.fold_counts}",
        f"- state_variants: {settings.state_variants}",
        f"- endpoint_modes: {settings.endpoint_modes}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6d = load_module("private_b6d_for_b6e_robustness", B6D_SCRIPT)
    base_table = b6d.build_state_table(args)
    conditions = build_conditions(args)
    all_summary = []
    aggregate_rows = []
    cv_paths = []
    policy_paths = []
    for condition in conditions:
        cv, policies = run_condition(base_table, condition, args)
        summary = summarize_condition(cv, condition, args)
        success = condition_success(summary)
        all_summary.append(summary)
        compact = {
            k: v for k, v in condition.items() if k not in {"operators"}
        }
        compact["n_operators"] = len(condition["operators"])
        compact["success"] = success
        for _, row in summary.iterrows():
            key = row["comparison"].replace("true_policy_vs_", "")
            compact[f"effect_vs_{key}"] = row["effect"]
            compact[f"p_vs_{key}"] = row["p_greater"]
        aggregate_rows.append(compact)
        cv_path = outdir / f"{condition['condition_id']}_heldout_rewards.csv"
        policy_path = outdir / f"{condition['condition_id']}_policies.csv"
        cv.to_csv(cv_path, index=False)
        policies.to_csv(policy_path, index=False)
        cv_paths.append(str(cv_path))
        policy_paths.append(str(policy_path))

    summary_all = pd.concat(all_summary, ignore_index=True) if all_summary else pd.DataFrame()
    aggregate = pd.DataFrame(aggregate_rows)
    successes = aggregate[aggregate["success"].astype(bool)].copy() if not aggregate.empty else pd.DataFrame()
    summary_all.to_csv(outdir / "private_B6E_replication_all_comparisons.csv", index=False)
    aggregate.to_csv(outdir / "private_B6E_replication_aggregate.csv", index=False)
    successes.to_csv(outdir / "private_B6E_replication_successes.csv", index=False)
    write_report(outdir / "private_B6E_replication_robustness_summary.md", aggregate, successes, args)

    print("\nPrivate B6E replication / robustness outputs")
    print(outdir)
    print("\nAggregate")
    print(aggregate.to_string(index=False, max_rows=80))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6e_replication_robustness")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--n-control-draws", type=int, default=250)
    parser.add_argument("--n-perm", type=int, default=2500)
    parser.add_argument("--seeds", type=int, nargs="+", default=[60310, 60311, 60312])
    parser.add_argument("--fold-counts", type=int, nargs="+", default=[5])
    parser.add_argument("--state-variants", nargs="+", default=["coarse", "side_tfc", "side_tfc_dphi"])
    parser.add_argument("--endpoint-modes", nargs="+", default=["z_reward", "rank_reward"])
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
