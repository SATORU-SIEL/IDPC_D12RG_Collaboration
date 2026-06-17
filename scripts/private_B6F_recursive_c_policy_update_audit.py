#!/usr/bin/env python3
"""Private B6F recursive C-policy update audit.

Question:
    Does the C-state policy improve the next C-state, not only the immediate
    operator readout?

Private screen only. C remains fixed as the original B5.5 phase-bearing lag+5
event carrier. State classes are observational regimes, not new C definitions.
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

OPERATOR_HORIZON = {
    "O1_lag0_AB": 1,
    "O2_lag5_AB": 5,
    "O3_A_C_boundary": 5,
    "O4_B_C_boundary": 5,
    "O5_full_TFC": 5,
    "O6_phase_only": 1,
    "O7_suppress_event": 5,
}

ENDPOINTS = [
    "future_C_quality",
    "future_policy_score",
    "future_ABC_consistency",
    "future_operator_advantage",
    "recursive_composite",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def reward(row: pd.Series, operator: str, endpoint: str = "recursive_composite") -> float:
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


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 720)
    labels = np.asarray(sorted(set(map(str, labels))), dtype=object)
    rng.shuffle(labels)
    return [fold for fold in np.array_split(labels, n_folds) if len(fold)]


def operator_frequency_weights(ops: list[str]) -> dict[str, float]:
    counts = {op: 0 for op in OPERATORS}
    for op in ops:
        if op in counts:
            counts[op] += 1
    total = float(sum(counts.values()))
    if total <= 0:
        return {op: 1.0 / len(OPERATORS) for op in OPERATORS}
    return {op: counts[op] / total for op in OPERATORS}


def build_state_table(args: argparse.Namespace) -> pd.DataFrame:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6d = load_module("private_b6d_for_b6f", B6D_SCRIPT)
    table = b6d.build_state_table(args).copy()
    table["C_quality_raw"] = np.nanmean(
        np.vstack(
            [
                zscore(pd.to_numeric(table["TFC_mean"], errors="coerce").to_numpy(dtype=float)),
                zscore(pd.to_numeric(table["TFC_min"], errors="coerce").to_numpy(dtype=float)),
                zscore(pd.to_numeric(table["C_memory_scalar"], errors="coerce").to_numpy(dtype=float)),
                zscore(pd.to_numeric(table["abs_dphi"], errors="coerce").to_numpy(dtype=float)),
            ]
        ),
        axis=0,
    )
    table["ABC_consistency_raw"] = np.nanmean(
        np.vstack(
            [
                zscore(pd.to_numeric(table["A_B"], errors="coerce").to_numpy(dtype=float)),
                zscore(pd.to_numeric(table["A_C"], errors="coerce").to_numpy(dtype=float)),
                zscore(pd.to_numeric(table["B_C"], errors="coerce").to_numpy(dtype=float)),
                zscore(pd.to_numeric(table["TFC_min"], errors="coerce").to_numpy(dtype=float)),
            ]
        ),
        axis=0,
    )
    op_cols = [f"{op}_z" for op in OPERATORS]
    table["operator_random_expectation"] = table[op_cols].mean(axis=1, skipna=True)
    table["operator_advantage_raw"] = table["oracle_reward_z"] - table["operator_random_expectation"]
    table["future_policy_score_raw"] = table["oracle_reward_z"]
    return add_recursive_operator_endpoints(table)


def add_recursive_operator_endpoints(table: pd.DataFrame) -> pd.DataFrame:
    out = table.sort_values(["label", "idx_in_session"]).reset_index(drop=True).copy()
    endpoint_source = {
        "future_C_quality": "C_quality_raw",
        "future_policy_score": "future_policy_score_raw",
        "future_ABC_consistency": "ABC_consistency_raw",
        "future_operator_advantage": "operator_advantage_raw",
    }
    for op in OPERATORS:
        for endpoint in endpoint_source:
            out[f"{endpoint}_{op}_raw"] = np.nan

    for _, sub in out.groupby("label", sort=False):
        idxs = sub.index.to_numpy()
        times = pd.to_numeric(sub["idx_in_session"], errors="coerce").to_numpy(dtype=float)
        for local_i, row_index in enumerate(idxs):
            current_t = times[local_i]
            for op in OPERATORS:
                if op == "O7_suppress_event":
                    for endpoint in endpoint_source:
                        out.loc[row_index, f"{endpoint}_{op}_raw"] = 0.0
                    continue
                horizon = OPERATOR_HORIZON[op]
                candidates = np.where(times >= current_t + horizon)[0]
                candidates = candidates[candidates > local_i]
                if len(candidates) == 0:
                    continue
                next_index = idxs[int(candidates[0])]
                for endpoint, source_col in endpoint_source.items():
                    out.loc[row_index, f"{endpoint}_{op}_raw"] = out.loc[next_index, source_col]

    for endpoint in endpoint_source:
        for op in OPERATORS:
            out[f"{endpoint}_{op}"] = zscore(out[f"{endpoint}_{op}_raw"].to_numpy(dtype=float))
    for op in OPERATORS:
        out[f"recursive_composite_{op}"] = np.nanmean(
            np.vstack([out[f"{endpoint}_{op}"].to_numpy(dtype=float) for endpoint in endpoint_source]),
            axis=0,
        )
    return out


def train_policy(train: pd.DataFrame, min_state_events: int, endpoint: str = "recursive_composite") -> tuple[dict[str, str], str, pd.DataFrame]:
    global_means = {op: float(np.nanmean(train[f"{endpoint}_{op}"])) for op in OPERATORS}
    global_best = max(global_means, key=global_means.get)
    rows = []
    mapping: dict[str, str] = {}
    for state, sub in train.groupby("state_label", sort=False):
        if len(sub) < min_state_events:
            continue
        means = {op: float(np.nanmean(sub[f"{endpoint}_{op}"])) for op in OPERATORS}
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


def performance_strata(train: pd.DataFrame, endpoint: str = "recursive_composite") -> dict[str, str]:
    means = {op: float(np.nanmean(train[f"{endpoint}_{op}"])) for op in OPERATORS}
    ordered = sorted(OPERATORS, key=lambda op: means[op])
    strata = {}
    chunks = np.array_split(np.asarray(ordered, dtype=object), 3)
    for label, chunk in zip(["low", "mid", "high"], chunks):
        for op in chunk:
            strata[str(op)] = label
    return strata


def stratum_matched_expected_reward(row: pd.Series, selected_op: str, strata: dict[str, str], endpoint: str) -> float:
    stratum = strata.get(selected_op, "missing")
    candidates = [op for op in OPERATORS if strata.get(op) == stratum]
    if not candidates:
        candidates = OPERATORS
    weights = {op: 1.0 / len(candidates) for op in candidates}
    return weighted_reward(row, weights, endpoint)


def cross_validated_recursive(table: pd.DataFrame, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 730)
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
        policy_table["fold"] = fold_index
        policies.extend(policy_table.to_dict("records"))
        true_ops = [mapping.get(str(row["state_label"]), fallback) for _, row in test.iterrows()]
        freq_weights = operator_frequency_weights(true_ops)
        strata = performance_strata(train)

        within_rewards = {endpoint: np.zeros(len(test), dtype=float) for endpoint in ENDPOINTS}
        balanced_rewards = {endpoint: np.zeros(len(test), dtype=float) for endpoint in ENDPOINTS}
        within_counts = {endpoint: np.zeros(len(test), dtype=float) for endpoint in ENDPOINTS}
        balanced_counts = {endpoint: np.zeros(len(test), dtype=float) for endpoint in ENDPOINTS}
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
                shuffled_op = shuffled_mapping.get(str(row["state_label"]), fallback)
                balanced_op = str(shuffled_ops[i])
                for endpoint in ENDPOINTS:
                    val = reward(row, shuffled_op, endpoint)
                    if np.isfinite(val):
                        within_rewards[endpoint][i] += val
                        within_counts[endpoint][i] += 1.0
                    val = reward(row, balanced_op, endpoint)
                    if np.isfinite(val):
                        balanced_rewards[endpoint][i] += val
                        balanced_counts[endpoint][i] += 1.0

        for i, (_, row) in enumerate(test.iterrows()):
            true_op = true_ops[i]
            out = row.to_dict()
            out.update(
                {
                    "fold": fold_index,
                    "true_policy_operator": true_op,
                    "true_policy_source": "state_mapping" if str(row["state_label"]) in mapping else "global_fallback",
                    "oracle_recursive_operator": max(OPERATORS, key=lambda op: reward(row, op, "recursive_composite") if np.isfinite(reward(row, op, "recursive_composite")) else -np.inf),
                }
            )
            for endpoint in ENDPOINTS:
                out[f"true_policy_{endpoint}"] = reward(row, true_op, endpoint)
                out[f"frequency_matched_random_{endpoint}"] = weighted_reward(row, freq_weights, endpoint)
                out[f"performance_matched_random_{endpoint}"] = stratum_matched_expected_reward(row, true_op, strata, endpoint)
                out[f"within_state_shuffle_{endpoint}"] = (
                    float(within_rewards[endpoint][i] / within_counts[endpoint][i]) if within_counts[endpoint][i] > 0 else np.nan
                )
                out[f"balanced_pool_shuffle_{endpoint}"] = (
                    float(balanced_rewards[endpoint][i] / balanced_counts[endpoint][i]) if balanced_counts[endpoint][i] > 0 else np.nan
                )
                out[f"oracle_{endpoint}"] = max(
                    [reward(row, op, endpoint) for op in OPERATORS if np.isfinite(reward(row, op, endpoint))],
                    default=np.nan,
                )
            rows.append(out)
    return pd.DataFrame(rows), pd.DataFrame(policies)


def summarize(cv: pd.DataFrame, n_perm: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 740)
    rows = []
    controls = [
        "balanced_pool_shuffle",
        "frequency_matched_random",
        "performance_matched_random",
        "within_state_shuffle",
        "oracle",
    ]
    for endpoint in ENDPOINTS:
        true_values = pd.to_numeric(cv[f"true_policy_{endpoint}"], errors="coerce").to_numpy(dtype=float)
        for control in controls:
            control_values = pd.to_numeric(cv[f"{control}_{endpoint}"], errors="coerce").to_numpy(dtype=float)
            effect, p = signflip_p(true_values - control_values, rng, n_perm)
            rows.append(
                {
                    "endpoint": endpoint,
                    "comparison": f"true_recursive_C_policy_vs_{control}",
                    "mean_true_policy": float(np.nanmean(true_values)),
                    "mean_comparator": float(np.nanmean(control_values)),
                    "effect": effect,
                    "p_greater": p,
                    "n_events": int(np.isfinite(true_values - control_values).sum()),
                    "state_mapping_rate": float(np.nanmean(cv["true_policy_source"].eq("state_mapping"))),
                    "oracle_hit_rate": float(np.nanmean(cv["true_policy_operator"].eq(cv["oracle_recursive_operator"]))),
                }
            )
    return pd.DataFrame(rows)


def classify(summary: pd.DataFrame) -> str:
    primary = summary[summary["endpoint"].eq("recursive_composite")].set_index("comparison")
    required = [
        "true_recursive_C_policy_vs_balanced_pool_shuffle",
        "true_recursive_C_policy_vs_frequency_matched_random",
        "true_recursive_C_policy_vs_performance_matched_random",
        "true_recursive_C_policy_vs_within_state_shuffle",
    ]
    ok = True
    for name in required:
        if name not in primary.index:
            ok = False
            continue
        row = primary.loc[name]
        ok = ok and bool(row["effect"] > 0 and row["p_greater"] <= 0.05)
    oracle_ok = True
    if "true_recursive_C_policy_vs_oracle" in primary.index:
        oracle_ok = bool(primary.loc["true_recursive_C_policy_vs_oracle", "effect"] < 0)
    future_c = summary[
        summary["endpoint"].eq("future_C_quality")
        & summary["comparison"].isin(
            [
                "true_recursive_C_policy_vs_balanced_pool_shuffle",
                "true_recursive_C_policy_vs_frequency_matched_random",
                "true_recursive_C_policy_vs_performance_matched_random",
            ]
        )
    ]
    future_c_ok = bool((future_c["effect"] > 0).all()) if not future_c.empty else False
    if ok and oracle_ok and future_c_ok:
        return "B6F success: recursive C-policy improves future C quality/composite over balanced controls while remaining below oracle."
    if ok and oracle_ok:
        return "Partial B6F signal: recursive C-policy composite beats balanced controls and remains below oracle, but endpoint-specific future C quality is incomplete."
    if any(
        name in primary.index and primary.loc[name, "effect"] > 0 and primary.loc[name, "p_greater"] <= 0.05
        for name in required
    ):
        return "Partial B6F signal: recursive C-policy beats at least one balanced control but not the full set."
    return "B6F not supported by this private recursive policy update audit."


def write_report(path: Path, summary: pd.DataFrame, policy_use: pd.DataFrame, policy_summary: pd.DataFrame, classification: str, args: argparse.Namespace) -> None:
    lines = [
        "# Private B6F Recursive C-Policy Update Audit",
        "",
        "Status: local/private screen only. No publication, commit, or push was performed.",
        "",
        "Question: Does C_t -> operator_{t+1} improve the next C-state, rather than only immediate operator readout?",
        "",
        "C remains fixed as the original B5.5 phase-bearing lag+5 event carrier. State classes are readout regimes, not new C definitions.",
        "",
        "Endpoints:",
        "",
        "- future_C_quality",
        "- future_policy_score",
        "- future_ABC_consistency",
        "- future_operator_advantage",
        "- recursive_composite",
        "",
        "Controls:",
        "",
        "- balanced random policy",
        "- performance-matched random policy",
        "- frequency-matched random policy",
        "- shuffled C-state policy",
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
        "## Learned Recursive Policy Summary",
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
    cv, policies = cross_validated_recursive(table, args)
    summary = summarize(cv, args.n_perm, args.seed)
    classification = classify(summary)
    cv["oracle_match"] = cv["true_policy_operator"].eq(cv["oracle_recursive_operator"]).astype(float)
    policy_use = cv.groupby(["true_policy_operator", "true_policy_source"], as_index=False).agg(
        n_events=("true_policy_operator", "size"),
        mean_recursive_composite=("true_policy_recursive_composite", "mean"),
        mean_future_C_quality=("true_policy_future_C_quality", "mean"),
        oracle_hit_rate=("oracle_match", "mean"),
    )
    policy_summary = policies.groupby("selected_operator", as_index=False).agg(
        n_state_fold_mappings=("state_label", "size"),
        mean_selected_train_reward=("selected_train_reward", "mean"),
        mean_global_best_train_reward=("global_best_train_reward", "mean"),
    ) if not policies.empty else pd.DataFrame()

    table.to_csv(outdir / "private_B6F_state_table.csv", index=False)
    cv.to_csv(outdir / "private_B6F_heldout_recursive_rewards.csv", index=False)
    policies.to_csv(outdir / "private_B6F_learned_recursive_policies.csv", index=False)
    summary.to_csv(outdir / "private_B6F_comparison_summary.csv", index=False)
    policy_use.to_csv(outdir / "private_B6F_policy_use_summary.csv", index=False)
    policy_summary.to_csv(outdir / "private_B6F_learned_policy_summary.csv", index=False)
    write_report(outdir / "private_B6F_recursive_c_policy_update_summary.md", summary, policy_use, policy_summary, classification, args)

    print("\nPrivate B6F recursive C-policy update outputs")
    print(outdir)
    print("\nClassification")
    print(classification)
    print("\nPrimary recursive composite summary")
    print(summary[summary["endpoint"].eq("recursive_composite")].to_string(index=False))
    print("\nFuture C quality summary")
    print(summary[summary["endpoint"].eq("future_C_quality")].to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6f_recursive_c_policy_update")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=60410)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
