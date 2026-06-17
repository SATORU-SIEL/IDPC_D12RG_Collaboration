#!/usr/bin/env python3
"""Private B6M C/FES-GMR72 generator-selection coupling audit.

Private only. Do not publish, stage, commit, or push.

Question:
    Does adding C/FES-GMR72 generated operators to the candidate pool improve
    state-conditioned operator selection beyond existing primitive selection?

Boundary:
    This is generator-selection coupling, not AGI, not recursive
    self-improvement, and not a redefinition of C.
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
B6L_SCRIPT = SCRIPTS / "private_B6L_operator_genesis_audit.py"

OPERATORS = [
    "O1_lag0_AB",
    "O2_lag5_AB",
    "O3_A_C_boundary",
    "O4_B_C_boundary",
    "O5_full_TFC",
    "O6_phase_only",
    "O7_suppress_event",
]

MODES = [
    "linear_c_state",
    "gmr72_phase_conditioned",
    "fes_string_conditioned",
    "combined_c_fes_gmr72",
]

ENDPOINTS = ["z_reward", "rank_reward", "gmr72_bridge_composite"]
SELECTION_RULES = ["mean", "stability_adjusted"]


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
    rng = np.random.default_rng(seed + 1310)
    labels = np.asarray(sorted(set(map(str, labels))), dtype=object)
    rng.shuffle(labels)
    return [fold for fold in np.array_split(labels, n_folds) if len(fold)]


def build_table(args: argparse.Namespace):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6l = load_module("private_b6l_for_b6m", B6L_SCRIPT)
    table = b6l.build_table(args)
    return b6l, table


def reward_cols(b6l, endpoint: str) -> dict[str, str]:
    return b6l.operator_reward_columns(endpoint)


def primitive_reward(row: pd.Series, b6l, op: str, endpoint: str) -> float:
    col = reward_cols(b6l, endpoint)[op]
    return float(pd.to_numeric(row.get(col, np.nan), errors="coerce"))


def weighted_reward(row: pd.Series, b6l, weights: np.ndarray, endpoint: str) -> float:
    return b6l.row_reward(row, weights, endpoint)


def candidate_values(sub: pd.DataFrame, b6l, weights: np.ndarray | None, op: str | None, endpoint: str) -> np.ndarray:
    if op is not None:
        col = reward_cols(b6l, endpoint)[op]
        return pd.to_numeric(sub[col], errors="coerce").to_numpy(dtype=float)
    vals = [weighted_reward(row, b6l, weights, endpoint) for _, row in sub.iterrows()]
    return np.asarray(vals, dtype=float)


def candidate_score(values: np.ndarray, selection_rule: str, stderr_lambda: float) -> float:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return -np.inf
    mean = float(np.nanmean(values))
    if selection_rule == "mean":
        return mean
    if selection_rule == "stability_adjusted":
        if len(values) < 2:
            return mean
        stderr = float(np.nanstd(values, ddof=1) / np.sqrt(len(values)))
        return mean - stderr_lambda * stderr
    raise ValueError(f"unknown selection rule {selection_rule}")


def random_state_weights(rng: np.random.Generator) -> np.ndarray:
    return rng.dirichlet(np.ones(len(OPERATORS)))


def performance_matched_weights(train: pd.DataFrame, b6l, endpoint: str) -> np.ndarray:
    return b6l.performance_matched_weights(train, endpoint)


def frequency_weights(selected_ops: list[str]) -> np.ndarray:
    counts = np.asarray([selected_ops.count(op) for op in OPERATORS], dtype=float)
    if np.sum(counts) <= 0:
        return np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    return counts / np.sum(counts)


def train_existing_policy(train: pd.DataFrame, b6l, endpoint: str, state_col: str, min_state_events: int, selection_rule: str, stderr_lambda: float):
    global_scores = {}
    for op in OPERATORS:
        global_scores[op] = candidate_score(candidate_values(train, b6l, None, op, endpoint), selection_rule, stderr_lambda)
    fallback = max(global_scores, key=global_scores.get)
    mapping = {}
    rows = []
    for state, sub in train.groupby(state_col, sort=False):
        if len(sub) < min_state_events:
            continue
        scores = {op: candidate_score(candidate_values(sub, b6l, None, op, endpoint), selection_rule, stderr_lambda) for op in OPERATORS}
        selected = max(scores, key=scores.get)
        mapping[str(state)] = selected
        row = {
            "state_label": str(state),
            "n_train_events": int(len(sub)),
            "selected_candidate": selected,
            "selected_kind": "primitive",
            "selected_score": float(scores[selected]),
            "selection_rule": selection_rule,
        }
        row.update({f"score_{op}": float(scores[op]) for op in OPERATORS})
        rows.append(row)
    return mapping, fallback, pd.DataFrame(rows)


def train_augmented_policy(
    train: pd.DataFrame,
    b6l,
    mode: str,
    endpoint: str,
    state_col: str,
    min_state_events: int,
    temperature: float,
    selection_rule: str,
    stderr_lambda: float,
    generated_kind: str,
    rng: np.random.Generator,
):
    true_mapping, global_weights, selected_mapping, global_best, families = b6l.train_weights(
        train, mode, endpoint, min_state_events, temperature
    )
    train = train.copy()
    train[state_col] = b6l.state_labels(train, mode)
    true_selected_ops = list(selected_mapping.values()) or [global_best]
    freq_w = frequency_weights(true_selected_ops)
    perf_w = performance_matched_weights(train, b6l, endpoint)
    random_global_w = random_state_weights(rng)
    shuffled_weights = list(true_mapping.values())
    rng.shuffle(shuffled_weights)
    shuffled_by_state = {
        state: shuffled_weights[i % len(shuffled_weights)]
        for i, state in enumerate(true_mapping.keys())
    } if shuffled_weights else {}

    global_candidates = {op: ("primitive", None, op) for op in OPERATORS}
    if generated_kind == "true_generated":
        global_candidates["G_true"] = ("generated", global_weights, None)
    elif generated_kind == "random_generated":
        global_candidates["G_random"] = ("generated", random_global_w, None)
    elif generated_kind == "balanced_generated":
        global_candidates["G_balanced"] = ("generated", np.ones(len(OPERATORS)) / len(OPERATORS), None)
    elif generated_kind == "frequency_matched_generated":
        global_candidates["G_frequency"] = ("generated", freq_w, None)
    elif generated_kind == "performance_matched_generated":
        global_candidates["G_performance"] = ("generated", perf_w, None)
    elif generated_kind == "shuffled_true_generated":
        global_candidates["G_shuffled"] = ("generated", global_weights, None)
    else:
        raise ValueError(f"unknown generated kind {generated_kind}")

    global_scores = {}
    for name, (_, weights, op) in global_candidates.items():
        global_scores[name] = candidate_score(candidate_values(train, b6l, weights, op, endpoint), selection_rule, stderr_lambda)
    fallback_name = max(global_scores, key=global_scores.get)

    mapping = {}
    rows = []
    for state, sub in train.groupby(state_col, sort=False):
        if len(sub) < min_state_events:
            continue
        candidates = {op: ("primitive", None, op) for op in OPERATORS}
        if generated_kind == "true_generated":
            weights = true_mapping.get(str(state), global_weights)
            candidates["G_true"] = ("generated", weights, None)
        elif generated_kind == "random_generated":
            candidates["G_random"] = ("generated", random_state_weights(rng), None)
        elif generated_kind == "balanced_generated":
            candidates["G_balanced"] = ("generated", np.ones(len(OPERATORS)) / len(OPERATORS), None)
        elif generated_kind == "frequency_matched_generated":
            candidates["G_frequency"] = ("generated", freq_w, None)
        elif generated_kind == "performance_matched_generated":
            candidates["G_performance"] = ("generated", perf_w, None)
        elif generated_kind == "shuffled_true_generated":
            candidates["G_shuffled"] = ("generated", shuffled_by_state.get(str(state), global_weights), None)

        scores = {}
        for name, (_, weights, op) in candidates.items():
            scores[name] = candidate_score(candidate_values(sub, b6l, weights, op, endpoint), selection_rule, stderr_lambda)
        selected = max(scores, key=scores.get)
        mapping[str(state)] = (selected, candidates[selected])
        row = {
            "state_label": str(state),
            "n_train_events": int(len(sub)),
            "selected_candidate": selected,
            "selected_kind": candidates[selected][0],
            "selected_score": float(scores[selected]),
            "generated_kind": generated_kind,
            "selection_rule": selection_rule,
        }
        row.update({f"score_{name}": float(score) for name, score in scores.items()})
        rows.append(row)

    fallback = (fallback_name, global_candidates[fallback_name])
    return mapping, fallback, pd.DataFrame(rows), families


def eval_candidate(row: pd.Series, b6l, candidate: tuple[str, np.ndarray | None, str | None], endpoint: str) -> float:
    _, weights, op = candidate
    if op is not None:
        return primitive_reward(row, b6l, op, endpoint)
    return weighted_reward(row, b6l, weights, endpoint)


def run_condition(table: pd.DataFrame, b6l, mode: str, endpoint: str, selection_rule: str, args: argparse.Namespace):
    rng = np.random.default_rng(args.seed + 1320)
    data = table.copy()
    state_col = "b6m_state_label"
    data[state_col] = b6l.state_labels(data, mode)
    folds = make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    policies = []
    families_all = []
    generated_kinds = [
        "true_generated",
        "random_generated",
        "balanced_generated",
        "frequency_matched_generated",
        "performance_matched_generated",
        "shuffled_true_generated",
    ]
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy().reset_index(drop=True)
        existing_mapping, existing_fallback, existing_policy = train_existing_policy(
            train, b6l, endpoint, state_col, args.min_state_events, selection_rule, args.stderr_lambda
        )
        existing_policy["mode"] = mode
        existing_policy["endpoint"] = endpoint
        existing_policy["fold"] = fold_index
        existing_policy["policy_type"] = "existing_only"
        policies.extend(existing_policy.to_dict("records"))
        aug = {}
        for generated_kind in generated_kinds:
            mapping, fallback, policy_table, families = train_augmented_policy(
                train,
                b6l,
                mode,
                endpoint,
                state_col,
                args.min_state_events,
                args.temperature,
                selection_rule,
                args.stderr_lambda,
                generated_kind,
                rng,
            )
            policy_table["mode"] = mode
            policy_table["endpoint"] = endpoint
            policy_table["fold"] = fold_index
            policy_table["policy_type"] = generated_kind
            policies.extend(policy_table.to_dict("records"))
            if not families.empty and generated_kind == "true_generated":
                families = families.copy()
                families["fold"] = fold_index
                families_all.extend(families.to_dict("records"))
            aug[generated_kind] = (mapping, fallback)
        for _, row in test.iterrows():
            state = str(row[state_col])
            existing_op = existing_mapping.get(state, existing_fallback)
            existing_reward = primitive_reward(row, b6l, existing_op, endpoint)
            record = {
                "mode": mode,
                "endpoint": endpoint,
                "selection_rule": selection_rule,
                "fold": fold_index,
                "label": row["label"],
                "idx_in_session": row["idx_in_session"],
                "state_label": state,
                "existing_selected_candidate": existing_op,
                "existing_selected_reward": existing_reward,
                "oracle_reward": max([primitive_reward(row, b6l, op, endpoint) for op in OPERATORS if np.isfinite(primitive_reward(row, b6l, op, endpoint))], default=np.nan),
            }
            for generated_kind in generated_kinds:
                mapping, fallback = aug[generated_kind]
                selected_name, selected_candidate = mapping.get(state, fallback)
                record[f"{generated_kind}_selected_candidate"] = selected_name
                record[f"{generated_kind}_selected_kind"] = selected_candidate[0]
                record[f"{generated_kind}_selected_reward"] = eval_candidate(row, b6l, selected_candidate, endpoint)
            rows.append(record)
    return pd.DataFrame(rows), pd.DataFrame(policies), pd.DataFrame(families_all)


def summarize(cv: pd.DataFrame, mode: str, endpoint: str, selection_rule: str, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1330)
    target = pd.to_numeric(cv["true_generated_selected_reward"], errors="coerce").to_numpy(dtype=float)
    comps = [
        ("existing_selected", "existing_selected_reward"),
        ("random_generated_selected", "random_generated_selected_reward"),
        ("balanced_generated_selected", "balanced_generated_selected_reward"),
        ("frequency_matched_generated_selected", "frequency_matched_generated_selected_reward"),
        ("performance_matched_generated_selected", "performance_matched_generated_selected_reward"),
        ("shuffled_true_generated_selected", "shuffled_true_generated_selected_reward"),
        ("oracle", "oracle_reward"),
    ]
    rows = []
    for name, col in comps:
        comp = pd.to_numeric(cv[col], errors="coerce").to_numpy(dtype=float)
        effect, p = signflip_p(target - comp, rng, args.n_perm)
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "selection_rule": selection_rule,
                "comparison": f"true_generated_pool_vs_{name}",
                "mean_true_generated_pool": float(np.nanmean(target)),
                "mean_comparator": float(np.nanmean(comp)),
                "effect": effect,
                "p_greater": p,
                "n_events": int(np.isfinite(target - comp).sum()),
                "generated_selection_rate": float(np.nanmean(cv["true_generated_selected_kind"].eq("generated"))),
            }
        )
    return pd.DataFrame(rows)


def classify(summary: pd.DataFrame) -> tuple[bool, bool, bool]:
    by = summary.set_index("comparison")
    minimum = (
        "true_generated_pool_vs_existing_selected" in by.index
        and by.loc["true_generated_pool_vs_existing_selected", "effect"] > 0
        and by.loc["true_generated_pool_vs_existing_selected", "p_greater"] <= 0.05
    )
    strong_names = [
        "true_generated_pool_vs_random_generated_selected",
        "true_generated_pool_vs_balanced_generated_selected",
        "true_generated_pool_vs_performance_matched_generated_selected",
        "true_generated_pool_vs_shuffled_true_generated_selected",
    ]
    strong = minimum and all(
        name in by.index and by.loc[name, "effect"] > 0 and by.loc[name, "p_greater"] <= 0.05
        for name in strong_names
    )
    very_strong = strong and "true_generated_pool_vs_oracle" in by.index and by.loc["true_generated_pool_vs_oracle", "effect"] < 0
    return minimum, strong, very_strong


def write_report(path: Path, results: pd.DataFrame, summaries: pd.DataFrame, policies: pd.DataFrame, args: argparse.Namespace) -> None:
    best = results.iloc[0] if len(results) else None
    best_label = f"{best['mode']} / {best['endpoint']} / {best['selection_rule']}" if best is not None else "none"
    generated_selected = float(np.nanmax(results["generated_selection_rate"])) if len(results) else 0.0
    lines = [
        "# Private B6M C/FES-GMR72 Generator-Selection Coupling Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Question: Does adding C/FES-GMR72 generated operators to the candidate pool improve state-conditioned selection beyond existing primitive selection?",
        "",
        "Interpretation boundary: this tests generator-selection coupling, not AGI, not recursive self-improvement, and not a redefinition of C.",
        "",
        "## Main Findings",
        "",
        f"- strongest condition: {best_label}",
        f"- minimum-success conditions over existing selected: {int(results['minimum_success'].sum())} / {len(results)}",
        f"- strong-success conditions over generated controls: {int(results['strong_success'].sum())} / {len(results)}",
        f"- very-strong conditions below oracle: {int(results['very_strong_success'].sum())} / {len(results)}",
        f"- max generated-candidate selection rate: {generated_selected:.6f}",
        "",
        "## Condition Results",
        "",
        results.to_csv(index=False).strip(),
        "",
        "## Comparison Summary",
        "",
        summaries.to_csv(index=False).strip(),
        "",
        "## Selected Candidate Diagnostics",
        "",
        policies.groupby(["mode", "endpoint", "selection_rule", "policy_type", "selected_kind"], dropna=False).size().reset_index(name="n").to_csv(index=False).strip() if not policies.empty else "none",
        "",
        "## Settings",
        "",
        f"- n_folds: {args.n_folds}",
        f"- min_state_events: {args.min_state_events}",
        f"- temperature: {args.temperature}",
        f"- stderr_lambda: {args.stderr_lambda}",
        f"- n_perm: {args.n_perm}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    b6l, table = build_table(args)
    table.to_csv(outdir / "private_B6M_generator_selection_state_table.csv", index=False)
    all_cv = []
    all_policies = []
    all_summaries = []
    all_families = []
    result_rows = []
    for mode in MODES:
        for endpoint in ENDPOINTS:
            for selection_rule in SELECTION_RULES:
                cv, policies, families = run_condition(table, b6l, mode, endpoint, selection_rule, args)
                if cv.empty:
                    continue
                summary = summarize(cv, mode, endpoint, selection_rule, args)
                minimum, strong, very_strong = classify(summary)
                by = summary.set_index("comparison")
                result_rows.append(
                    {
                        "mode": mode,
                        "endpoint": endpoint,
                        "selection_rule": selection_rule,
                        "minimum_success": minimum,
                        "strong_success": strong,
                        "very_strong_success": very_strong,
                        "mean_true_generated_pool": float(np.nanmean(cv["true_generated_selected_reward"])),
                        "mean_existing_selected": float(np.nanmean(cv["existing_selected_reward"])),
                        "effect_vs_existing": float(by.loc["true_generated_pool_vs_existing_selected", "effect"]),
                        "p_vs_existing": float(by.loc["true_generated_pool_vs_existing_selected", "p_greater"]),
                        "effect_vs_random_generated": float(by.loc["true_generated_pool_vs_random_generated_selected", "effect"]),
                        "p_vs_random_generated": float(by.loc["true_generated_pool_vs_random_generated_selected", "p_greater"]),
                        "effect_vs_balanced_generated": float(by.loc["true_generated_pool_vs_balanced_generated_selected", "effect"]),
                        "p_vs_balanced_generated": float(by.loc["true_generated_pool_vs_balanced_generated_selected", "p_greater"]),
                        "effect_vs_performance_generated": float(by.loc["true_generated_pool_vs_performance_matched_generated_selected", "effect"]),
                        "p_vs_performance_generated": float(by.loc["true_generated_pool_vs_performance_matched_generated_selected", "p_greater"]),
                        "effect_vs_shuffled_generated": float(by.loc["true_generated_pool_vs_shuffled_true_generated_selected", "effect"]),
                        "p_vs_shuffled_generated": float(by.loc["true_generated_pool_vs_shuffled_true_generated_selected", "p_greater"]),
                        "effect_vs_oracle": float(by.loc["true_generated_pool_vs_oracle", "effect"]),
                        "generated_selection_rate": float(np.nanmean(cv["true_generated_selected_kind"].eq("generated"))),
                    }
                )
                all_cv.append(cv)
                all_policies.append(policies)
                all_summaries.append(summary)
                all_families.append(families)
    results = pd.DataFrame(result_rows).sort_values(
        ["very_strong_success", "strong_success", "minimum_success", "effect_vs_existing", "generated_selection_rate"],
        ascending=[False, False, False, False, False],
    )
    cv_all = pd.concat(all_cv, ignore_index=True) if all_cv else pd.DataFrame()
    policies_all = pd.concat(all_policies, ignore_index=True) if all_policies else pd.DataFrame()
    summaries = pd.concat(all_summaries, ignore_index=True) if all_summaries else pd.DataFrame()
    families_all = pd.concat(all_families, ignore_index=True) if all_families else pd.DataFrame()
    results.to_csv(outdir / "private_B6M_generator_selection_results.csv", index=False)
    summaries.to_csv(outdir / "private_B6M_comparison_summary.csv", index=False)
    cv_all.to_csv(outdir / "private_B6M_heldout_coupling_rewards.csv", index=False)
    policies_all.to_csv(outdir / "private_B6M_learned_coupling_policies.csv", index=False)
    families_all.to_csv(outdir / "private_B6M_generated_operator_families.csv", index=False)
    write_report(outdir / "private_B6M_generator_selection_coupling_summary.md", results, summaries, policies_all, args)
    print("\nPrivate B6M generator-selection coupling outputs")
    print(outdir)
    print(results.to_string(index=False, max_rows=80))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6m_generator_selection_coupling")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--stderr-lambda", type=float, default=1.0)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=61220)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
