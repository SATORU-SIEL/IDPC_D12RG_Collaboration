#!/usr/bin/env python3
"""Private B6E balanced operator pool audit.

Question:
    Does C-state policy performance come from state-operator matching rather
    than operator strength, operator difficulty, or operator frequency?

This extends B6D with balanced controls:
    - within-state shuffle;
    - frequency-matched random policy;
    - performance-stratum matched random policy;
    - balanced operator-pool shuffle preserving operator frequency and
      train-performance strata.
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

OPERATORS = [
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


def reward(row: pd.Series, operator: str) -> float:
    return float(row.get(f"{operator}_z", np.nan))


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


def operator_frequency_weights(ops: list[str]) -> dict[str, float]:
    counts = {op: 0 for op in OPERATORS}
    for op in ops:
        if op in counts:
            counts[op] += 1
    total = float(sum(counts.values()))
    if total <= 0:
        return {op: 1.0 / len(OPERATORS) for op in OPERATORS}
    return {op: counts[op] / total for op in OPERATORS}


def performance_strata(train: pd.DataFrame) -> tuple[dict[str, str], dict[str, float]]:
    means = {op: float(np.nanmean(train[f"{op}_z"])) for op in OPERATORS}
    ordered = sorted(OPERATORS, key=lambda op: means[op])
    strata = {}
    chunks = np.array_split(np.asarray(ordered, dtype=object), 3)
    for label, chunk in zip(["low", "mid", "high"], chunks):
        for op in chunk:
            strata[str(op)] = label
    return strata, means


def within_state_shuffled_policy(policy_table: pd.DataFrame, rng: np.random.Generator) -> dict[str, str]:
    mapping = {}
    op_array = np.asarray(OPERATORS, dtype=object)
    for _, row in policy_table.iterrows():
        shuffled_labels = op_array.copy()
        rng.shuffle(shuffled_labels)
        means = {shuffled_op: float(row[f"train_mean_{op}"]) for op, shuffled_op in zip(OPERATORS, shuffled_labels)}
        mapping[str(row["state_label"])] = max(means, key=means.get)
    return mapping


def apply_mapping_reward(row: pd.Series, mapping: dict[str, str], fallback: str) -> float:
    op = mapping.get(str(row["state_label"]), fallback)
    return reward(row, op)


def train_policy(train: pd.DataFrame, min_state_events: int) -> tuple[dict[str, str], str, pd.DataFrame]:
    global_means = {op: float(np.nanmean(train[f"{op}_z"])) for op in OPERATORS}
    global_best = max(global_means, key=global_means.get)
    rows = []
    mapping: dict[str, str] = {}
    for state, sub in train.groupby("state_label", sort=False):
        if len(sub) < min_state_events:
            continue
        means = {op: float(np.nanmean(sub[f"{op}_z"])) for op in OPERATORS}
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
        row.update({f"train_mean_{op}": means[op] for op in OPERATORS})
        rows.append(row)
    return mapping, global_best, pd.DataFrame(rows)


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 690)
    labels = np.asarray(sorted(set(map(str, labels))), dtype=object)
    rng.shuffle(labels)
    return [fold for fold in np.array_split(labels, n_folds) if len(fold)]


def stratum_matched_expected_reward(row: pd.Series, selected_op: str, strata: dict[str, str]) -> float:
    stratum = strata.get(selected_op, "missing")
    candidates = [op for op in OPERATORS if strata.get(op) == stratum]
    if not candidates:
        candidates = OPERATORS
    weights = {op: 1.0 / len(candidates) for op in candidates}
    return weighted_reward(row, weights)


def cross_validated_balanced(table: pd.DataFrame, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 700)
    folds = make_folds(table["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    policies = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = table["label"].astype(str).isin(set(test_labels))
        train = table[~test_mask].copy()
        test = table[test_mask].copy().reset_index(drop=True)
        mapping, fallback, policy_table = train_policy(train, args.min_state_events)
        if policy_table.empty:
            continue
        strata, train_global_means = performance_strata(train)
        policy_table["fold"] = fold_index
        policy_table["selected_performance_stratum"] = policy_table["selected_operator"].map(strata)
        policies.extend(policy_table.to_dict("records"))

        true_ops = [mapping.get(str(row["state_label"]), fallback) for _, row in test.iterrows()]
        freq_weights = operator_frequency_weights(true_ops)

        within_rewards = np.zeros(len(test), dtype=float)
        within_counts = np.zeros(len(test), dtype=float)
        balanced_rewards = np.zeros(len(test), dtype=float)
        balanced_counts = np.zeros(len(test), dtype=float)

        for _ in range(args.n_control_draws):
            shuffled_mapping = within_state_shuffled_policy(policy_table, rng)
            shuffled_ops = np.asarray(true_ops, dtype=object).copy()
            for stratum in ["low", "mid", "high"]:
                idx = [i for i, op in enumerate(shuffled_ops) if strata.get(str(op)) == stratum]
                if len(idx) > 1:
                    vals = shuffled_ops[idx].copy()
                    rng.shuffle(vals)
                    shuffled_ops[idx] = vals
            for i, (_, row) in enumerate(test.iterrows()):
                val = apply_mapping_reward(row, shuffled_mapping, fallback)
                if np.isfinite(val):
                    within_rewards[i] += val
                    within_counts[i] += 1.0
                val = reward(row, str(shuffled_ops[i]))
                if np.isfinite(val):
                    balanced_rewards[i] += val
                    balanced_counts[i] += 1.0

        for i, (_, row) in enumerate(test.iterrows()):
            true_op = true_ops[i]
            out = row.to_dict()
            out.update(
                {
                    "fold": fold_index,
                    "true_policy_operator": true_op,
                    "true_policy_source": "state_mapping" if str(row["state_label"]) in mapping else "global_fallback",
                    "true_policy_reward_z": reward(row, true_op),
                    "true_operator_train_performance": train_global_means.get(true_op, np.nan),
                    "true_operator_performance_stratum": strata.get(true_op, "missing"),
                    "frequency_matched_random_policy_reward_z": weighted_reward(row, freq_weights),
                    "performance_matched_random_policy_reward_z": stratum_matched_expected_reward(row, true_op, strata),
                    "balanced_operator_pool_shuffle_reward_z": float(balanced_rewards[i] / balanced_counts[i]) if balanced_counts[i] > 0 else np.nan,
                    "within_state_operator_shuffle_reward_z": float(within_rewards[i] / within_counts[i]) if within_counts[i] > 0 else np.nan,
                    "oracle_reward_z": reward(row, str(row["oracle_operator"])) if pd.notna(row["oracle_operator"]) else np.nan,
                }
            )
            rows.append(out)
    return pd.DataFrame(rows), pd.DataFrame(policies)


def summarize(cv: pd.DataFrame, n_perm: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 710)
    true_reward = pd.to_numeric(cv["true_policy_reward_z"], errors="coerce").to_numpy(dtype=float)
    comparisons = [
        ("balanced_operator_pool_shuffle", pd.to_numeric(cv["balanced_operator_pool_shuffle_reward_z"], errors="coerce").to_numpy(dtype=float)),
        ("frequency_matched_random_policy", pd.to_numeric(cv["frequency_matched_random_policy_reward_z"], errors="coerce").to_numpy(dtype=float)),
        ("performance_matched_random_policy", pd.to_numeric(cv["performance_matched_random_policy_reward_z"], errors="coerce").to_numpy(dtype=float)),
        ("within_state_operator_shuffle", pd.to_numeric(cv["within_state_operator_shuffle_reward_z"], errors="coerce").to_numpy(dtype=float)),
        ("oracle_upper_bound", pd.to_numeric(cv["oracle_reward_z"], errors="coerce").to_numpy(dtype=float)),
    ]
    rows = []
    for name, values in comparisons:
        effect, p = signflip_p(true_reward - values, rng, n_perm)
        rows.append(
            {
                "comparison": f"true_C_state_policy_vs_{name}",
                "mean_true_policy_reward_z": float(np.nanmean(true_reward)),
                "mean_comparator_reward_z": float(np.nanmean(values)),
                "effect": effect,
                "p_greater": p,
                "n_events": int(np.isfinite(true_reward - values).sum()),
                "state_mapping_rate": float(np.nanmean(cv["true_policy_source"].eq("state_mapping"))),
                "oracle_hit_rate": float(np.nanmean(cv["true_policy_operator"].eq(cv["oracle_operator"]))),
            }
        )
    return pd.DataFrame(rows)


def classify(summary: pd.DataFrame) -> str:
    by = summary.set_index("comparison")
    required = [
        "true_C_state_policy_vs_balanced_operator_pool_shuffle",
        "true_C_state_policy_vs_frequency_matched_random_policy",
        "true_C_state_policy_vs_performance_matched_random_policy",
        "true_C_state_policy_vs_within_state_operator_shuffle",
    ]
    ok = True
    for name in required:
        if name not in by.index:
            ok = False
            continue
        row = by.loc[name]
        ok = ok and bool(row["effect"] > 0 and row["p_greater"] <= 0.05)
    oracle_ok = True
    if "true_C_state_policy_vs_oracle_upper_bound" in by.index:
        oracle_ok = bool(by.loc["true_C_state_policy_vs_oracle_upper_bound", "effect"] < 0)
    if ok and oracle_ok:
        return "B6E success: true C-state policy beats balanced, frequency-matched, performance-matched, and within-state shuffle controls while remaining below oracle."
    if any(
        name in by.index and by.loc[name, "effect"] > 0 and by.loc[name, "p_greater"] <= 0.05
        for name in required
    ):
        return "Partial B6E signal: true C-state policy beats at least one balanced-pool control but not the full set."
    return "B6E not supported by this private balanced operator pool audit."


def write_report(path: Path, summary: pd.DataFrame, policy_use: pd.DataFrame, strata_summary: pd.DataFrame, classification: str, args: argparse.Namespace) -> None:
    lines = [
        "# Private B6E Balanced Operator Pool Audit",
        "",
        "Status: local/private screen only. No publication, commit, or push was performed.",
        "",
        "Question: Does C-state policy performance come from state-operator matching rather than operator strength, difficulty, or frequency?",
        "",
        "C remains fixed as the original B5.5 phase-bearing lag+5 event carrier. State classes are readout regimes, not new C definitions.",
        "",
        "Controls:",
        "",
        "- balanced operator-pool shuffle preserving selected-operator frequency and train-performance stratum",
        "- frequency-matched random policy",
        "- performance-stratum matched random policy",
        "- within-state operator shuffle",
        "- oracle upper bound",
        "",
        "## Classification",
        "",
        classification,
        "",
        "## Comparison Summary",
        "",
        summary.to_csv(index=False).strip(),
        "",
        "## Held-Out Policy Use",
        "",
        policy_use.to_csv(index=False).strip(),
        "",
        "## Train Performance Strata Summary",
        "",
        strata_summary.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- n_folds: {args.n_folds}",
        f"- min_state_events: {args.min_state_events}",
        f"- n_control_draws: {args.n_control_draws}",
        f"- window: {args.window}",
        f"- n_perm: {args.n_perm}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6d = load_module("private_b6d_for_b6e", B6D_SCRIPT)
    table = b6d.build_state_table(args)
    cv, policies = cross_validated_balanced(table, args)
    summary = summarize(cv, args.n_perm, args.seed)
    classification = classify(summary)
    cv["oracle_match"] = cv["true_policy_operator"].eq(cv["oracle_operator"]).astype(float)
    policy_use = cv.groupby(["true_policy_operator", "true_policy_source", "true_operator_performance_stratum"], as_index=False).agg(
        n_events=("true_policy_operator", "size"),
        mean_reward_z=("true_policy_reward_z", "mean"),
        oracle_hit_rate=("oracle_match", "mean"),
    )
    strata_summary = policies.groupby(["fold", "selected_performance_stratum", "selected_operator"], as_index=False).agg(
        n_state_mappings=("state_label", "size"),
        mean_selected_train_reward=("selected_train_reward", "mean"),
    ) if not policies.empty else pd.DataFrame()

    table.to_csv(outdir / "private_B6E_state_table.csv", index=False)
    cv.to_csv(outdir / "private_B6E_heldout_balanced_rewards.csv", index=False)
    policies.to_csv(outdir / "private_B6E_learned_policies.csv", index=False)
    summary.to_csv(outdir / "private_B6E_comparison_summary.csv", index=False)
    policy_use.to_csv(outdir / "private_B6E_policy_use_summary.csv", index=False)
    strata_summary.to_csv(outdir / "private_B6E_train_performance_strata_summary.csv", index=False)
    write_report(outdir / "private_B6E_balanced_operator_pool_summary.md", summary, policy_use, strata_summary, classification, args)

    print("\nPrivate B6E balanced operator pool outputs")
    print(outdir)
    print("\nClassification")
    print(classification)
    print("\nComparison summary")
    print(summary.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6e_balanced_operator_pool")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=60310)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
