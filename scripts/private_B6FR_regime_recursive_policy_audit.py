#!/usr/bin/env python3
"""Private B6F-R regime-specific recursive C-policy audit.

Question:
    Does C-policy preserve or improve future policy-capable C-state regimes?

This is a narrower follow-up to B6F. It uses the B6E-supported state variants
instead of global future C quality.
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
    "regime_transition_score",
    "policy_readiness",
    "operator_margin_persistence",
    "policy_regret_reduction",
    "regime_recursive_composite",
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


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 790)
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


def tfc_rank(value: str) -> int:
    return {"low": 0, "mid": 1, "high": 2}.get(str(value), -1)


def regime_status(row: pd.Series) -> str:
    side = str(row.get("boundary_side", "missing"))
    tfc = str(row.get("tfc_bin", "missing"))
    margin = float(row.get("operator_margin", np.nan))
    side_ok = side in {"A_side", "B_side"}
    if side_ok and tfc == "high" and np.isfinite(margin) and margin > 0:
        return "good"
    if (not side_ok) or tfc == "low" or (np.isfinite(margin) and margin <= 0):
        return "bad"
    return "neutral"


def transition_score(current_status: str, next_status: str) -> float:
    if current_status == "bad" and next_status in {"neutral", "good"}:
        return 1.0
    if current_status == "neutral" and next_status == "good":
        return 1.0
    if current_status == "good" and next_status == "good":
        return 1.0
    if current_status == "good" and next_status == "bad":
        return -1.0
    if current_status == "neutral" and next_status == "bad":
        return -1.0
    if current_status == "bad" and next_status == "bad":
        return -1.0
    return 0.0


def operator_frequency_weights(ops: list[str], operators: list[str]) -> dict[str, float]:
    counts = {op: 0 for op in operators}
    for op in ops:
        if op in counts:
            counts[op] += 1
    total = float(sum(counts.values()))
    if total <= 0:
        return {op: 1.0 / len(operators) for op in operators}
    return {op: counts[op] / total for op in operators}


def build_base_table(args: argparse.Namespace) -> pd.DataFrame:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6d = load_module("private_b6d_for_b6fr", B6D_SCRIPT)
    robust = load_module("private_b6e_robust_for_b6fr", B6E_ROBUST_SCRIPT)
    table = b6d.build_state_table(args)
    table = robust.set_state_variant(table, args.state_variant)
    for op in OPERATORS:
        if f"{op}_z" not in table.columns:
            table[f"{op}_z"] = 0.0
    op_cols = [f"{op}_z" for op in OPERATORS]
    table["operator_random_expectation"] = table[op_cols].mean(axis=1, skipna=True)
    table["operator_margin"] = table["oracle_reward_z"] - table["operator_random_expectation"]
    table["regime_status"] = table.apply(regime_status, axis=1)
    return add_regime_operator_endpoints(table)


def add_regime_operator_endpoints(table: pd.DataFrame) -> pd.DataFrame:
    out = table.sort_values(["label", "idx_in_session"]).reset_index(drop=True).copy()
    for op in OPERATORS:
        for endpoint in ENDPOINTS:
            out[f"{endpoint}_{op}_raw"] = np.nan

    for _, sub in out.groupby("label", sort=False):
        idxs = sub.index.to_numpy()
        times = pd.to_numeric(sub["idx_in_session"], errors="coerce").to_numpy(dtype=float)
        for local_i, row_index in enumerate(idxs):
            current = out.loc[row_index]
            current_status = str(current["regime_status"])
            current_rank = tfc_rank(str(current.get("tfc_bin", "missing")))
            current_margin = float(current.get("operator_margin", np.nan))
            for op in OPERATORS:
                horizon = OPERATOR_HORIZON[op]
                candidates = np.where(times >= times[local_i] + horizon)[0]
                candidates = candidates[candidates > local_i]
                if len(candidates) == 0:
                    continue
                next_index = idxs[int(candidates[0])]
                nxt = out.loc[next_index]
                next_status = str(nxt["regime_status"])
                next_rank = tfc_rank(str(nxt.get("tfc_bin", "missing")))
                next_margin = float(nxt.get("operator_margin", np.nan))
                future_op_reward = float(nxt.get(f"{op}_z", np.nan))
                future_oracle = float(nxt.get("oracle_reward_z", np.nan))
                future_random = float(nxt.get("operator_random_expectation", np.nan))
                readiness = 1.0 if next_status in {"neutral", "good"} else 0.0
                side_stable = 1.0 if str(current.get("boundary_side")) == str(nxt.get("boundary_side")) and str(nxt.get("boundary_side")) in {"A_side", "B_side"} else 0.0
                score = transition_score(current_status, next_status)
                if current_rank >= 0 and next_rank >= 0 and next_rank > current_rank:
                    score += 0.5
                if side_stable and next_status != "bad":
                    score += 0.25
                margin_persist = next_margin
                regret_reduce = (future_op_reward - future_oracle) - (float(current.get(f"{op}_z", np.nan)) - float(current.get("oracle_reward_z", np.nan)))
                if np.isfinite(future_op_reward) and np.isfinite(future_random):
                    regret_reduce += 0.25 * (future_op_reward - future_random)
                out.loc[row_index, f"regime_transition_score_{op}_raw"] = score
                out.loc[row_index, f"policy_readiness_{op}_raw"] = readiness
                out.loc[row_index, f"operator_margin_persistence_{op}_raw"] = margin_persist
                out.loc[row_index, f"policy_regret_reduction_{op}_raw"] = regret_reduce

    for endpoint in ENDPOINTS:
        if endpoint == "regime_recursive_composite":
            continue
        for op in OPERATORS:
            out[f"{endpoint}_{op}"] = zscore(out[f"{endpoint}_{op}_raw"].to_numpy(dtype=float))
    for op in OPERATORS:
        out[f"regime_recursive_composite_{op}"] = np.nanmean(
            np.vstack(
                [
                    out[f"regime_transition_score_{op}"].to_numpy(dtype=float),
                    out[f"policy_readiness_{op}"].to_numpy(dtype=float),
                    out[f"operator_margin_persistence_{op}"].to_numpy(dtype=float),
                    out[f"policy_regret_reduction_{op}"].to_numpy(dtype=float),
                ]
            ),
            axis=0,
        )
    return out


def train_policy(train: pd.DataFrame, min_state_events: int, endpoint: str) -> tuple[dict[str, str], str, pd.DataFrame]:
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


def performance_strata(train: pd.DataFrame, endpoint: str) -> dict[str, str]:
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


def cross_validated_regime(table: pd.DataFrame, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 800)
    folds = make_folds(table["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    policies = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = table["label"].astype(str).isin(set(test_labels))
        train = table[~test_mask].copy()
        test = table[test_mask].copy().reset_index(drop=True)
        mapping, fallback, policy_table = train_policy(train, args.min_state_events, "regime_recursive_composite")
        if policy_table.empty:
            continue
        policy_table["fold"] = fold_index
        policies.extend(policy_table.to_dict("records"))
        true_ops = [mapping.get(str(row["state_label"]), fallback) for _, row in test.iterrows()]
        freq_weights = operator_frequency_weights(true_ops, OPERATORS)
        strata = performance_strata(train, "regime_recursive_composite")
        within_rewards = {endpoint: np.zeros(len(test), dtype=float) for endpoint in ENDPOINTS}
        balanced_rewards = {endpoint: np.zeros(len(test), dtype=float) for endpoint in ENDPOINTS}
        within_counts = {endpoint: np.zeros(len(test), dtype=float) for endpoint in ENDPOINTS}
        balanced_counts = {endpoint: np.zeros(len(test), dtype=float) for endpoint in ENDPOINTS}
        between_rewards = {endpoint: np.zeros(len(test), dtype=float) for endpoint in ENDPOINTS}
        between_counts = {endpoint: np.zeros(len(test), dtype=float) for endpoint in ENDPOINTS}

        for _ in range(args.n_control_draws):
            shuffled_mapping = within_state_shuffled_policy(policy_table, rng)
            states = policy_table["state_label"].astype(str).to_numpy(copy=True)
            ops = policy_table["selected_operator"].astype(str).to_numpy(copy=True)
            rng.shuffle(ops)
            between_mapping = {state: op for state, op in zip(states, ops)}
            shuffled_ops = np.asarray(true_ops, dtype=object).copy()
            for stratum in ["low", "mid", "high"]:
                idx = [i for i, op in enumerate(shuffled_ops) if strata.get(str(op)) == stratum]
                if len(idx) > 1:
                    vals = shuffled_ops[idx].copy()
                    rng.shuffle(vals)
                    shuffled_ops[idx] = vals
            for i, (_, row) in enumerate(test.iterrows()):
                state = str(row["state_label"])
                control_ops = {
                    "within": shuffled_mapping.get(state, fallback),
                    "between": between_mapping.get(state, fallback),
                    "balanced": str(shuffled_ops[i]),
                }
                for endpoint in ENDPOINTS:
                    for control_name, control_op in control_ops.items():
                        val = reward(row, control_op, endpoint)
                        if not np.isfinite(val):
                            continue
                        if control_name == "within":
                            within_rewards[endpoint][i] += val
                            within_counts[endpoint][i] += 1.0
                        elif control_name == "between":
                            between_rewards[endpoint][i] += val
                            between_counts[endpoint][i] += 1.0
                        else:
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
                    "oracle_regime_operator": max(
                        OPERATORS,
                        key=lambda op: reward(row, op, "regime_recursive_composite")
                        if np.isfinite(reward(row, op, "regime_recursive_composite"))
                        else -np.inf,
                    ),
                }
            )
            for endpoint in ENDPOINTS:
                out[f"true_policy_{endpoint}"] = reward(row, true_op, endpoint)
                out[f"balanced_pool_shuffle_{endpoint}"] = (
                    float(balanced_rewards[endpoint][i] / balanced_counts[endpoint][i]) if balanced_counts[endpoint][i] > 0 else np.nan
                )
                out[f"frequency_matched_random_{endpoint}"] = weighted_reward(row, freq_weights, endpoint)
                out[f"performance_matched_random_{endpoint}"] = stratum_matched_expected_reward(row, true_op, strata, endpoint)
                out[f"within_state_shuffle_{endpoint}"] = (
                    float(within_rewards[endpoint][i] / within_counts[endpoint][i]) if within_counts[endpoint][i] > 0 else np.nan
                )
                out[f"between_state_permutation_{endpoint}"] = (
                    float(between_rewards[endpoint][i] / between_counts[endpoint][i]) if between_counts[endpoint][i] > 0 else np.nan
                )
                out[f"oracle_{endpoint}"] = max(
                    [reward(row, op, endpoint) for op in OPERATORS if np.isfinite(reward(row, op, endpoint))],
                    default=np.nan,
                )
            rows.append(out)
    return pd.DataFrame(rows), pd.DataFrame(policies)


def summarize(cv: pd.DataFrame, n_perm: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 810)
    controls = [
        "balanced_pool_shuffle",
        "frequency_matched_random",
        "performance_matched_random",
        "within_state_shuffle",
        "between_state_permutation",
        "oracle",
    ]
    rows = []
    for endpoint in ENDPOINTS:
        true_values = pd.to_numeric(cv[f"true_policy_{endpoint}"], errors="coerce").to_numpy(dtype=float)
        for control in controls:
            values = pd.to_numeric(cv[f"{control}_{endpoint}"], errors="coerce").to_numpy(dtype=float)
            effect, p = signflip_p(true_values - values, rng, n_perm)
            rows.append(
                {
                    "endpoint": endpoint,
                    "comparison": f"true_regime_C_policy_vs_{control}",
                    "mean_true_policy": float(np.nanmean(true_values)),
                    "mean_comparator": float(np.nanmean(values)),
                    "effect": effect,
                    "p_greater": p,
                    "n_events": int(np.isfinite(true_values - values).sum()),
                    "state_mapping_rate": float(np.nanmean(cv["true_policy_source"].eq("state_mapping"))),
                    "oracle_hit_rate": float(np.nanmean(cv["true_policy_operator"].eq(cv["oracle_regime_operator"]))),
                }
            )
    return pd.DataFrame(rows)


def classify(summary: pd.DataFrame) -> str:
    primary = summary[summary["endpoint"].eq("regime_recursive_composite")].set_index("comparison")
    required = [
        "true_regime_C_policy_vs_balanced_pool_shuffle",
        "true_regime_C_policy_vs_frequency_matched_random",
        "true_regime_C_policy_vs_performance_matched_random",
        "true_regime_C_policy_vs_within_state_shuffle",
        "true_regime_C_policy_vs_between_state_permutation",
    ]
    ok = True
    for name in required:
        if name not in primary.index:
            ok = False
            continue
        row = primary.loc[name]
        ok = ok and bool(row["effect"] > 0 and row["p_greater"] <= 0.05)
    oracle_ok = True
    if "true_regime_C_policy_vs_oracle" in primary.index:
        oracle_ok = bool(primary.loc["true_regime_C_policy_vs_oracle", "effect"] < 0)
    readiness = summary[summary["endpoint"].eq("policy_readiness")].set_index("comparison")
    readiness_ok = False
    if "true_regime_C_policy_vs_balanced_pool_shuffle" in readiness.index:
        row = readiness.loc["true_regime_C_policy_vs_balanced_pool_shuffle"]
        readiness_ok = bool(row["effect"] > 0 and row["p_greater"] <= 0.05)
    if ok and oracle_ok and readiness_ok:
        return "B6F-R success: regime-specific C-policy preserves/improves policy-capable next C-state over balanced controls while remaining below oracle."
    if ok and oracle_ok:
        return "Partial B6F-R signal: regime recursive composite passes controls, but policy-readiness endpoint is incomplete."
    if any(
        name in primary.index and primary.loc[name, "effect"] > 0 and primary.loc[name, "p_greater"] <= 0.05
        for name in required
    ):
        return "Partial B6F-R signal: regime policy beats at least one recursive control but not the full set."
    return "B6F-R not supported by this private regime-specific recursive audit."


def write_report(path: Path, summary: pd.DataFrame, policy_use: pd.DataFrame, policy_summary: pd.DataFrame, classification: str, args: argparse.Namespace) -> None:
    lines = [
        "# Private B6F-R Regime-Specific Recursive C-Policy Audit",
        "",
        "Status: local/private screen only. No publication, commit, or push was performed.",
        "",
        "Question: Does C-policy preserve or improve future policy-capable C-state regimes?",
        "",
        "This narrows B6F to side+TFC regimes, matching the B6E robustness result. C remains fixed as the original B5.5 phase-bearing lag+5 event carrier.",
        "",
        "Endpoints:",
        "",
        "- regime_transition_score",
        "- policy_readiness",
        "- operator_margin_persistence",
        "- policy_regret_reduction",
        "- regime_recursive_composite",
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
        "## Learned Regime Policy Summary",
        "",
        policy_summary.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- state_variant: {args.state_variant}",
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
    table = build_base_table(args)
    cv, policies = cross_validated_regime(table, args)
    summary = summarize(cv, args.n_perm, args.seed)
    classification = classify(summary)
    cv["oracle_match"] = cv["true_policy_operator"].eq(cv["oracle_regime_operator"]).astype(float)
    policy_use = cv.groupby(["true_policy_operator", "true_policy_source"], as_index=False).agg(
        n_events=("true_policy_operator", "size"),
        mean_regime_composite=("true_policy_regime_recursive_composite", "mean"),
        mean_readiness=("true_policy_policy_readiness", "mean"),
        oracle_hit_rate=("oracle_match", "mean"),
    )
    policy_summary = policies.groupby("selected_operator", as_index=False).agg(
        n_state_fold_mappings=("state_label", "size"),
        mean_selected_train_reward=("selected_train_reward", "mean"),
        mean_global_best_train_reward=("global_best_train_reward", "mean"),
    ) if not policies.empty else pd.DataFrame()

    table.to_csv(outdir / "private_B6FR_state_table.csv", index=False)
    cv.to_csv(outdir / "private_B6FR_heldout_regime_rewards.csv", index=False)
    policies.to_csv(outdir / "private_B6FR_learned_regime_policies.csv", index=False)
    summary.to_csv(outdir / "private_B6FR_comparison_summary.csv", index=False)
    policy_use.to_csv(outdir / "private_B6FR_policy_use_summary.csv", index=False)
    policy_summary.to_csv(outdir / "private_B6FR_learned_policy_summary.csv", index=False)
    write_report(outdir / "private_B6FR_regime_recursive_policy_summary.md", summary, policy_use, policy_summary, classification, args)

    print("\nPrivate B6F-R regime recursive policy outputs")
    print(outdir)
    print("\nClassification")
    print(classification)
    print("\nPrimary regime recursive composite summary")
    print(summary[summary["endpoint"].eq("regime_recursive_composite")].to_string(index=False))
    print("\nPolicy readiness summary")
    print(summary[summary["endpoint"].eq("policy_readiness")].to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6fr_regime_recursive_policy")
    parser.add_argument("--state-variant", default="side_tfc")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=60510)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
