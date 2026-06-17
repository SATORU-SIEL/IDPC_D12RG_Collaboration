#!/usr/bin/env python3
"""Private B6L C/FES-GMR72 guided operator genesis audit.

Private only. Do not publish, stage, commit, or push.

Question:
    Can C/FES-GMR72 generate weighted operator families that outperform
    random/balanced generated operators and existing selected/fixed operators?

Boundary:
    This is operator synthesis, not operator selection. C is not redefined.
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
B6K_SCRIPT = SCRIPTS / "private_B6K_gmr72_fes_resonance_policy_audit.py"

OPERATORS = [
    "O1_lag0_AB",
    "O2_lag5_AB",
    "O3_A_C_boundary",
    "O4_B_C_boundary",
    "O5_full_TFC",
    "O6_phase_only",
    "O7_suppress_event",
]

OPERATOR_PHASE_OFFSETS = {
    "O1_lag0_AB": 0.0,
    "O2_lag5_AB": 1.0,
    "O3_A_C_boundary": 2.0,
    "O4_B_C_boundary": 3.0,
    "O5_full_TFC": 4.0,
    "O6_phase_only": 1.0,
    "O7_suppress_event": 0.0,
}

MODES = [
    "linear_c_state",
    "gmr72_phase_conditioned",
    "fes_string_conditioned",
    "combined_c_fes_gmr72",
]

ENDPOINTS = ["z_reward", "rank_reward", "gmr72_bridge_composite"]


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


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 1210)
    labels = np.asarray(sorted(set(map(str, labels))), dtype=object)
    rng.shuffle(labels)
    return [fold for fold in np.array_split(labels, n_folds) if len(fold)]


def softmax(scores: np.ndarray, temperature: float = 0.35) -> np.ndarray:
    scores = np.asarray(scores, dtype=float)
    finite = np.isfinite(scores)
    if not finite.any():
        return np.ones(len(scores), dtype=float) / len(scores)
    fill = np.nanmin(scores[finite])
    s = np.where(finite, scores, fill)
    s = s / max(float(temperature), 1e-6)
    s = s - np.nanmax(s)
    e = np.exp(s)
    total = np.sum(e)
    if not np.isfinite(total) or total <= 0:
        return np.ones(len(scores), dtype=float) / len(scores)
    return e / total


def state_labels(table: pd.DataFrame, mode: str) -> pd.Series:
    base = (
        "side=" + table["boundary_side"].astype(str)
        + "|tfc=" + table["tfc_bin"].astype(str)
        + "|phase=" + table["phase_quadrant"].astype(str)
    )
    if mode == "linear_c_state":
        return base
    if mode == "gmr72_phase_conditioned":
        return base
    if mode == "fes_string_conditioned":
        return "fes=" + table["fes_phase"].astype(str)
    if mode == "combined_c_fes_gmr72":
        return base + "|fes=" + table["fes_phase"].astype(str)
    raise ValueError(f"unknown mode {mode}")


def operator_reward_columns(endpoint: str) -> dict[str, str]:
    if endpoint == "z_reward":
        return {op: f"{op}_z" for op in OPERATORS}
    if endpoint == "rank_reward":
        return {op: f"rank_reward_{op}" for op in OPERATORS}
    if endpoint == "gmr72_bridge_composite":
        return {op: f"gmr72_bridge_composite_{op}" for op in OPERATORS}
    raise ValueError(f"unknown endpoint {endpoint}")


def add_rank_rewards(table: pd.DataFrame) -> pd.DataFrame:
    out = table.copy()
    for op in OPERATORS:
        vals = pd.to_numeric(out[f"{op}_z"], errors="coerce")
        out[f"rank_reward_{op}"] = zscore(vals.rank(pct=True).to_numpy(dtype=float))
    return out


def build_table(args: argparse.Namespace) -> pd.DataFrame:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6k = load_module("private_b6k_for_b6l", B6K_SCRIPT)
    table = b6k.build_base_table(args)
    return add_rank_rewards(table)


def resonance_prior_for_state(row: pd.Series) -> np.ndarray:
    fes_idx = float(row.get("fes_idx", np.nan))
    if not np.isfinite(fes_idx):
        return np.ones(len(OPERATORS), dtype=float)
    vals = []
    for op in OPERATORS:
        offset = OPERATOR_PHASE_OFFSETS[op]
        # Prefer operators whose primitive phase advances the FES string by one.
        vals.append(1.0 + np.cos(2.0 * np.pi * (((offset - fes_idx) - 1.0) % 5.0) / 5.0))
    arr = np.asarray(vals, dtype=float)
    return np.clip(arr, 0.05, None)


def train_weights(train: pd.DataFrame, mode: str, endpoint: str, min_state_events: int, temperature: float) -> tuple[dict[str, np.ndarray], np.ndarray, dict[str, str], str, pd.DataFrame]:
    reward_cols = operator_reward_columns(endpoint)
    global_means = np.asarray([pd.to_numeric(train[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
    global_weights = softmax(global_means, temperature)
    global_best = OPERATORS[int(np.nanargmax(global_means))]
    mapping = {}
    selected_mapping = {}
    rows = []
    train = train.copy()
    train["gen_state_label"] = state_labels(train, mode)
    for state, sub in train.groupby("gen_state_label", sort=False):
        if len(sub) < min_state_events:
            continue
        means = np.asarray([pd.to_numeric(sub[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
        weights = softmax(means, temperature)
        if mode in {"gmr72_phase_conditioned", "combined_c_fes_gmr72"}:
            prior = np.nanmean(np.vstack([resonance_prior_for_state(row) for _, row in sub.iterrows()]), axis=0)
            weights = weights * prior
            weights = weights / np.sum(weights)
        mapping[str(state)] = weights
        selected_mapping[str(state)] = OPERATORS[int(np.nanargmax(means))]
        row = {
            "mode": mode,
            "endpoint": endpoint,
            "state_label": str(state),
            "n_train_events": int(len(sub)),
            "selected_operator": selected_mapping[str(state)],
            "selected_train_reward": float(np.nanmax(means)),
            "generated_train_reward": float(np.nansum(weights * means)),
        }
        row.update({f"w_{op}": float(weights[i]) for i, op in enumerate(OPERATORS)})
        row.update({f"mean_{op}": float(means[i]) for i, op in enumerate(OPERATORS)})
        rows.append(row)
    return mapping, global_weights, selected_mapping, global_best, pd.DataFrame(rows)


def row_reward(row: pd.Series, weights: np.ndarray, endpoint: str) -> float:
    reward_cols = operator_reward_columns(endpoint)
    vals = np.asarray([pd.to_numeric(row.get(reward_cols[op], np.nan), errors="coerce") for op in OPERATORS], dtype=float)
    mask = np.isfinite(vals) & np.isfinite(weights)
    if not mask.any():
        return np.nan
    w = np.asarray(weights, dtype=float)[mask]
    if not np.isfinite(np.sum(w)) or np.sum(w) <= 1e-12:
        w = np.ones(mask.sum(), dtype=float)
    w = w / np.sum(w)
    return float(np.nansum(w * vals[mask]))


def selected_reward(row: pd.Series, op: str, endpoint: str) -> float:
    reward_cols = operator_reward_columns(endpoint)
    return float(pd.to_numeric(row.get(reward_cols[op], np.nan), errors="coerce"))


def random_generated_rewards(row: pd.Series, endpoint: str, rng: np.random.Generator, n_draws: int) -> float:
    vals = []
    for _ in range(n_draws):
        weights = rng.dirichlet(np.ones(len(OPERATORS)))
        vals.append(row_reward(row, weights, endpoint))
    return float(np.nanmean(vals)) if vals else np.nan


def performance_matched_weights(train: pd.DataFrame, endpoint: str) -> np.ndarray:
    reward_cols = operator_reward_columns(endpoint)
    means = np.asarray([pd.to_numeric(train[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
    ranks = pd.Series(means).rank(pct=True).to_numpy(dtype=float)
    weights = ranks / np.nansum(ranks)
    if not np.isfinite(weights).all() or np.nansum(weights) <= 0:
        return np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    return weights


def cross_validate(table: pd.DataFrame, mode: str, endpoint: str, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 1220)
    folds = make_folds(table["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    policies = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = table["label"].astype(str).isin(set(test_labels))
        train = table[~test_mask].copy()
        test = table[test_mask].copy().reset_index(drop=True)
        mapping, global_weights, selected_mapping, global_best, policy_table = train_weights(
            train, mode, endpoint, args.min_state_events, args.temperature
        )
        if policy_table.empty:
            continue
        policy_table["fold"] = fold_index
        policies.extend(policy_table.to_dict("records"))
        train_state = train.copy()
        train_state["gen_state_label"] = state_labels(train_state, mode)
        selected_ops = list(selected_mapping.values()) or [global_best]
        freq = np.asarray([selected_ops.count(op) for op in OPERATORS], dtype=float)
        freq_weights = freq / np.sum(freq) if np.sum(freq) > 0 else np.ones(len(OPERATORS)) / len(OPERATORS)
        perf_weights = performance_matched_weights(train, endpoint)
        reward_cols = operator_reward_columns(endpoint)
        global_means = np.asarray([pd.to_numeric(train[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
        fixed_best = OPERATORS[int(np.nanargmax(global_means))]
        test["gen_state_label"] = state_labels(test, mode)
        for _, row in test.iterrows():
            state = str(row["gen_state_label"])
            weights = mapping.get(state, global_weights)
            selected_op = selected_mapping.get(state, global_best)
            generated = row_reward(row, weights, endpoint)
            selected = selected_reward(row, selected_op, endpoint)
            fixed = selected_reward(row, fixed_best, endpoint)
            oracle = max([selected_reward(row, op, endpoint) for op in OPERATORS if np.isfinite(selected_reward(row, op, endpoint))], default=np.nan)
            rows.append(
                {
                    "mode": mode,
                    "endpoint": endpoint,
                    "fold": fold_index,
                    "label": row["label"],
                    "idx_in_session": row["idx_in_session"],
                    "state_label": state,
                    "policy_source": "state_generated" if state in mapping else "global_generated",
                    "selected_operator": selected_op,
                    "fixed_operator": fixed_best,
                    "generated_reward": generated,
                    "best_selected_reward": selected,
                    "best_fixed_reward": fixed,
                    "random_generated_reward": random_generated_rewards(row, endpoint, rng, args.n_random_draws),
                    "balanced_generated_reward": row_reward(row, np.ones(len(OPERATORS)) / len(OPERATORS), endpoint),
                    "frequency_matched_generated_reward": row_reward(row, freq_weights, endpoint),
                    "performance_matched_generated_reward": row_reward(row, perf_weights, endpoint),
                    "oracle_reward": oracle,
                    **{f"w_{op}": float(weights[i]) for i, op in enumerate(OPERATORS)},
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(policies)


def summarize(cv: pd.DataFrame, mode: str, endpoint: str, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1230)
    generated = pd.to_numeric(cv["generated_reward"], errors="coerce").to_numpy(dtype=float)
    comps = [
        "random_generated",
        "balanced_generated",
        "frequency_matched_generated",
        "performance_matched_generated",
        "best_selected",
        "best_fixed",
        "oracle",
    ]
    rows = []
    for comp in comps:
        vals = pd.to_numeric(cv[f"{comp}_reward"], errors="coerce").to_numpy(dtype=float)
        effect, p = signflip_p(generated - vals, rng, args.n_perm)
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "comparison": f"generated_vs_{comp}",
                "mean_generated": float(np.nanmean(generated)),
                "mean_comparator": float(np.nanmean(vals)),
                "effect": effect,
                "p_greater": p,
                "n_events": int(np.isfinite(generated - vals).sum()),
                "state_generation_rate": float(np.nanmean(cv["policy_source"].eq("state_generated"))),
            }
        )
    return pd.DataFrame(rows)


def classify(summary: pd.DataFrame) -> tuple[bool, bool, bool]:
    by = summary.set_index("comparison")
    minimum = all(
        name in by.index and by.loc[name, "effect"] > 0 and by.loc[name, "p_greater"] <= 0.05
        for name in ["generated_vs_random_generated", "generated_vs_balanced_generated"]
    )
    strong = minimum and "generated_vs_best_selected" in by.index and by.loc["generated_vs_best_selected", "effect"] > 0 and by.loc["generated_vs_best_selected", "p_greater"] <= 0.05
    very_strong = strong and "generated_vs_best_fixed" in by.index and by.loc["generated_vs_best_fixed", "effect"] > 0 and by.loc["generated_vs_best_fixed", "p_greater"] <= 0.05 and by.loc["generated_vs_oracle", "effect"] < 0
    return minimum, strong, very_strong


def write_report(path: Path, results: pd.DataFrame, summaries: pd.DataFrame, families: pd.DataFrame, best_ops: pd.DataFrame, args: argparse.Namespace) -> None:
    strongest = results.iloc[0]["mode"] + " / " + results.iloc[0]["endpoint"] if len(results) else "none"
    lines = [
        "# Private B6L C/FES-GMR72 Guided Operator Genesis Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Question: Can C/FES-GMR72 generate weighted operator families that outperform existing operator selection?",
        "",
        "Interpretation boundary: this is operator synthesis, not AGI, not recursive self-improvement, and not a redefinition of C.",
        "",
        "## Main Findings",
        "",
        f"- strongest synthesis mode: {strongest}",
        f"- minimum-success conditions: {int(results['minimum_success'].sum())} / {len(results)}",
        f"- strong-success conditions over best selected: {int(results['strong_success'].sum())} / {len(results)}",
        f"- very-strong conditions over best fixed and best selected while below oracle: {int(results['very_strong_success'].sum())} / {len(results)}",
        "",
        "## Generated Operator Results",
        "",
        results.to_csv(index=False).strip(),
        "",
        "## Operator Family Ranking",
        "",
        families.to_csv(index=False).strip(),
        "",
        "## Best Generated Operators",
        "",
        best_ops.to_csv(index=False).strip(),
        "",
        "## Comparison Summary",
        "",
        summaries.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- n_folds: {args.n_folds}",
        f"- min_state_events: {args.min_state_events}",
        f"- temperature: {args.temperature}",
        f"- n_random_draws: {args.n_random_draws}",
        f"- n_perm: {args.n_perm}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    table = build_table(args)
    table.to_csv(outdir / "private_B6L_operator_genesis_state_table.csv", index=False)
    result_rows = []
    all_summaries = []
    all_cv = []
    all_policies = []
    for mode in MODES:
        for endpoint in ENDPOINTS:
            cv, policies = cross_validate(table, mode, endpoint, args)
            if cv.empty:
                continue
            summary = summarize(cv, mode, endpoint, args)
            minimum, strong, very_strong = classify(summary)
            by = summary.set_index("comparison")
            result_rows.append(
                {
                    "mode": mode,
                    "endpoint": endpoint,
                    "minimum_success": minimum,
                    "strong_success": strong,
                    "very_strong_success": very_strong,
                    "mean_generated": float(np.nanmean(cv["generated_reward"])),
                    "effect_vs_random": float(by.loc["generated_vs_random_generated", "effect"]),
                    "p_vs_random": float(by.loc["generated_vs_random_generated", "p_greater"]),
                    "effect_vs_balanced": float(by.loc["generated_vs_balanced_generated", "effect"]),
                    "p_vs_balanced": float(by.loc["generated_vs_balanced_generated", "p_greater"]),
                    "effect_vs_selected": float(by.loc["generated_vs_best_selected", "effect"]),
                    "p_vs_selected": float(by.loc["generated_vs_best_selected", "p_greater"]),
                    "effect_vs_fixed": float(by.loc["generated_vs_best_fixed", "effect"]),
                    "p_vs_fixed": float(by.loc["generated_vs_best_fixed", "p_greater"]),
                    "effect_vs_oracle": float(by.loc["generated_vs_oracle", "effect"]),
                    "state_generation_rate": float(np.nanmean(cv["policy_source"].eq("state_generated"))),
                }
            )
            all_summaries.append(summary)
            all_cv.append(cv)
            all_policies.append(policies)
    results = pd.DataFrame(result_rows).sort_values(
        ["very_strong_success", "strong_success", "minimum_success", "effect_vs_selected", "effect_vs_balanced"],
        ascending=[False, False, False, False, False],
    )
    summaries = pd.concat(all_summaries, ignore_index=True) if all_summaries else pd.DataFrame()
    cv_all = pd.concat(all_cv, ignore_index=True) if all_cv else pd.DataFrame()
    policies_all = pd.concat(all_policies, ignore_index=True) if all_policies else pd.DataFrame()
    families = policies_all.groupby(["mode", "endpoint"], as_index=False).agg(
        n_generated_families=("state_label", "size"),
        mean_generated_train_reward=("generated_train_reward", "mean"),
        mean_selected_train_reward=("selected_train_reward", "mean"),
    ) if not policies_all.empty else pd.DataFrame()
    weight_cols = [f"w_{op}" for op in OPERATORS]
    best_ops = policies_all.sort_values("generated_train_reward", ascending=False).head(50) if not policies_all.empty else pd.DataFrame()
    keep_cols = ["mode", "endpoint", "state_label", "n_train_events", "generated_train_reward", "selected_train_reward", "selected_operator", *weight_cols]
    if not best_ops.empty:
        best_ops = best_ops[[c for c in keep_cols if c in best_ops.columns]]

    results.to_csv(outdir / "private_B6L_generated_operator_results.csv", index=False)
    families.to_csv(outdir / "private_B6L_operator_family_ranking.csv", index=False)
    best_ops.to_csv(outdir / "private_B6L_best_generated_operators.csv", index=False)
    summaries.to_csv(outdir / "private_B6L_comparison_summary.csv", index=False)
    cv_all.to_csv(outdir / "private_B6L_heldout_generated_rewards.csv", index=False)
    policies_all.to_csv(outdir / "private_B6L_learned_generated_operator_families.csv", index=False)
    write_report(outdir / "private_B6L_operator_genesis_summary.md", results, summaries, families, best_ops, args)
    print("\nPrivate B6L operator genesis outputs")
    print(outdir)
    print(results.to_string(index=False, max_rows=60))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6l_operator_genesis")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=61120)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
