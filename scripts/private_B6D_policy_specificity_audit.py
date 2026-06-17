#!/usr/bin/env python3
"""Private B6D policy specificity audit.

Question:
    Does the C-state conditioned selector work because the state->operator
    correspondence is specific, rather than because the candidate operator set
    is generally strong?

Controls:
    - within-state operator-label shuffle;
    - between-state policy permutation;
    - global operator-label permutation;
    - equal-frequency random policy expectation;
    - oracle upper bound.
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
B6B_SCRIPT = SCRIPTS / "private_B6_c_guided_operator_selection_audit.py"
B6C_SCRIPT = SCRIPTS / "private_B6C_state_conditioned_operator_selection_audit.py"
B55_SCRIPT = SCRIPTS / "test_Stage_B5_5_triadic_constraint_audit.py"

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


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 660)
    labels = np.asarray(sorted(set(map(str, labels))), dtype=object)
    rng.shuffle(labels)
    return [fold for fold in np.array_split(labels, n_folds) if len(fold)]


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


def within_state_shuffled_policy(policy_table: pd.DataFrame, rng: np.random.Generator) -> dict[str, str]:
    mapping = {}
    op_array = np.asarray(OPERATORS, dtype=object)
    for _, row in policy_table.iterrows():
        shuffled_labels = op_array.copy()
        rng.shuffle(shuffled_labels)
        means = {shuffled_op: float(row[f"train_mean_{op}"]) for op, shuffled_op in zip(OPERATORS, shuffled_labels)}
        mapping[str(row["state_label"])] = max(means, key=means.get)
    return mapping


def between_state_permuted_policy(policy_table: pd.DataFrame, rng: np.random.Generator) -> dict[str, str]:
    states = policy_table["state_label"].astype(str).to_numpy(copy=True)
    ops = policy_table["selected_operator"].astype(str).to_numpy(copy=True)
    rng.shuffle(ops)
    return {state: op for state, op in zip(states, ops)}


def operator_label_permuted_policy(policy_table: pd.DataFrame, rng: np.random.Generator) -> dict[str, str]:
    op_array = np.asarray(OPERATORS, dtype=object)
    permuted = op_array.copy()
    rng.shuffle(permuted)
    label_map = {op: new_op for op, new_op in zip(op_array, permuted)}
    return {str(row["state_label"]): label_map[str(row["selected_operator"])] for _, row in policy_table.iterrows()}


def equal_frequency_weights(mapping: dict[str, str]) -> dict[str, float]:
    counts = {op: 0 for op in OPERATORS}
    for op in mapping.values():
        counts[op] += 1
    total = float(sum(counts.values()))
    if total <= 0:
        return {op: 1.0 / len(OPERATORS) for op in OPERATORS}
    return {op: counts[op] / total for op in OPERATORS}


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


def apply_mapping_reward(row: pd.Series, mapping: dict[str, str], fallback: str) -> float:
    op = mapping.get(str(row["state_label"]), fallback)
    return reward(row, op)


def build_state_table(args: argparse.Namespace) -> pd.DataFrame:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6b = load_module("private_b6b_for_b6d", B6B_SCRIPT)
    b6c = load_module("private_b6c_for_b6d", B6C_SCRIPT)
    b55 = load_module("stage_b5_5_for_b6d", B55_SCRIPT)
    annotated = pd.read_csv(args.annotated)
    events = pd.read_csv(args.events)
    table = b6b.build_event_operator_table(b55, annotated, events, args.window)
    table["O7_suppress_event_raw"] = 0.0
    table["O7_suppress_event_z"] = 0.0
    table = b6c.add_state_classes(table)
    z_cols = [f"{op}_z" for op in OPERATORS]
    finite_any = table[z_cols].notna().any(axis=1)
    table["oracle_operator"] = np.where(
        finite_any,
        table[z_cols].fillna(-np.inf).idxmax(axis=1).str.replace("_z", "", regex=False),
        np.nan,
    )
    table["oracle_reward_z"] = table[z_cols].max(axis=1, skipna=True)
    return table


def cross_validated_policy_specificity(table: pd.DataFrame, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 670)
    folds = make_folds(table["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    policies = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = table["label"].astype(str).isin(set(test_labels))
        train = table[~test_mask].copy()
        test = table[test_mask].copy()
        mapping, fallback, policy_table = train_policy(train, args.min_state_events)
        if policy_table.empty:
            continue
        policy_table["fold"] = fold_index
        policies.extend(policy_table.to_dict("records"))
        weights = equal_frequency_weights(mapping)

        control_rewards = {
            "within_state_operator_shuffle": np.zeros(len(test), dtype=float),
            "between_state_policy_permutation": np.zeros(len(test), dtype=float),
            "operator_label_permutation": np.zeros(len(test), dtype=float),
        }
        control_counts = {k: np.zeros(len(test), dtype=float) for k in control_rewards}
        for _ in range(args.n_control_draws):
            controls = {
                "within_state_operator_shuffle": within_state_shuffled_policy(policy_table, rng),
                "between_state_policy_permutation": between_state_permuted_policy(policy_table, rng),
                "operator_label_permutation": operator_label_permuted_policy(policy_table, rng),
            }
            for control_name, control_mapping in controls.items():
                for i, (_, row) in enumerate(test.iterrows()):
                    val = apply_mapping_reward(row, control_mapping, fallback)
                    if np.isfinite(val):
                        control_rewards[control_name][i] += val
                        control_counts[control_name][i] += 1.0

        for i, (_, row) in enumerate(test.iterrows()):
            state = str(row["state_label"])
            true_op = mapping.get(state, fallback)
            out = row.to_dict()
            out.update(
                {
                    "fold": fold_index,
                    "true_policy_operator": true_op,
                    "true_policy_source": "state_mapping" if state in mapping else "global_fallback",
                    "true_policy_reward_z": reward(row, true_op),
                    "equal_frequency_random_policy_reward_z": weighted_reward(row, weights),
                    "oracle_reward_z": reward(row, str(row["oracle_operator"])) if pd.notna(row["oracle_operator"]) else np.nan,
                }
            )
            for control_name in control_rewards:
                denom = control_counts[control_name][i]
                out[f"{control_name}_reward_z"] = (
                    float(control_rewards[control_name][i] / denom) if denom > 0 else np.nan
                )
            rows.append(out)
    return pd.DataFrame(rows), pd.DataFrame(policies)


def summarize(cv: pd.DataFrame, n_perm: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 680)
    true_reward = pd.to_numeric(cv["true_policy_reward_z"], errors="coerce").to_numpy(dtype=float)
    comparisons = [
        ("within_state_operator_shuffle", pd.to_numeric(cv["within_state_operator_shuffle_reward_z"], errors="coerce").to_numpy(dtype=float)),
        ("between_state_policy_permutation", pd.to_numeric(cv["between_state_policy_permutation_reward_z"], errors="coerce").to_numpy(dtype=float)),
        ("operator_label_permutation", pd.to_numeric(cv["operator_label_permutation_reward_z"], errors="coerce").to_numpy(dtype=float)),
        ("equal_frequency_random_policy", pd.to_numeric(cv["equal_frequency_random_policy_reward_z"], errors="coerce").to_numpy(dtype=float)),
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
        "true_C_state_policy_vs_within_state_operator_shuffle",
        "true_C_state_policy_vs_between_state_policy_permutation",
        "true_C_state_policy_vs_operator_label_permutation",
        "true_C_state_policy_vs_equal_frequency_random_policy",
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
        row = by.loc["true_C_state_policy_vs_oracle_upper_bound"]
        oracle_ok = bool(row["effect"] < 0)
    if ok and oracle_ok:
        return "B6D success: true C-state policy beats policy-specificity controls while remaining below oracle."
    if any(
        name in by.index and by.loc[name, "effect"] > 0 and by.loc[name, "p_greater"] <= 0.05
        for name in required
    ):
        return "Partial B6D signal: true C-state policy beats at least one policy-specificity control but not the full set."
    return "B6D not supported by this private policy-specificity audit."


def write_report(path: Path, summary: pd.DataFrame, policy_use: pd.DataFrame, policy_summary: pd.DataFrame, classification: str, args: argparse.Namespace) -> None:
    lines = [
        "# Private B6D Policy Specificity Audit",
        "",
        "Status: local/private screen only. No publication, commit, or push was performed.",
        "",
        "Question: Does the C-state conditioned selector work because the C-state to operator correspondence is specific?",
        "",
        "C remains fixed as the original B5.5 phase-bearing lag+5 event carrier. State classes are readout regimes, not new C definitions.",
        "",
        "Controls:",
        "",
        "- within-state operator shuffle",
        "- between-state policy permutation",
        "- operator-label permutation",
        "- equal-frequency random policy",
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
        "## Learned Policy Summary",
        "",
        policy_summary.to_csv(index=False).strip(),
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
    table = build_state_table(args)
    cv, policies = cross_validated_policy_specificity(table, args)
    summary = summarize(cv, args.n_perm, args.seed)
    classification = classify(summary)
    cv["oracle_match"] = cv["true_policy_operator"].eq(cv["oracle_operator"]).astype(float)
    policy_use = cv.groupby(["true_policy_operator", "true_policy_source"], as_index=False).agg(
        n_events=("true_policy_operator", "size"),
        mean_reward_z=("true_policy_reward_z", "mean"),
        oracle_hit_rate=("oracle_match", "mean"),
    )
    policy_summary = policies.groupby("selected_operator", as_index=False).agg(
        n_state_fold_mappings=("state_label", "size"),
        mean_selected_train_reward=("selected_train_reward", "mean"),
        mean_global_best_train_reward=("global_best_train_reward", "mean"),
    ) if not policies.empty else pd.DataFrame()

    table.to_csv(outdir / "private_B6D_state_table.csv", index=False)
    cv.to_csv(outdir / "private_B6D_heldout_policy_rewards.csv", index=False)
    policies.to_csv(outdir / "private_B6D_learned_policies.csv", index=False)
    summary.to_csv(outdir / "private_B6D_comparison_summary.csv", index=False)
    policy_use.to_csv(outdir / "private_B6D_policy_use_summary.csv", index=False)
    policy_summary.to_csv(outdir / "private_B6D_learned_policy_summary.csv", index=False)
    write_report(outdir / "private_B6D_policy_specificity_summary.md", summary, policy_use, policy_summary, classification, args)

    print("\nPrivate B6D policy specificity outputs")
    print(outdir)
    print("\nClassification")
    print(classification)
    print("\nComparison summary")
    print(summary.to_string(index=False))
    print("\nHeld-out policy use")
    print(policy_use.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6d_policy_specificity")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--n-control-draws", type=int, default=300)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=60210)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
