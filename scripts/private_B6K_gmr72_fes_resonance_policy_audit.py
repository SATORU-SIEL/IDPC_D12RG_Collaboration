#!/usr/bin/env python3
"""Private B6K GMR72 FES resonance policy audit.

Purpose:
    Move beyond B6F by testing an explicit five-string FES resonance engine
    abstracted into a 72-degree GMR operator-selection function.

Boundary:
    Private only. Do not publish, stage, commit, or push.

Interpretation:
    This does not redefine C as FES. FES is used as a five-string
    perspective-mode engine that conditions operator selection through
    GMR72 phase rotation.
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
B6J_SCRIPT = SCRIPTS / "private_B6J_fes_guided_operator_selection_audit.py"

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

FES_ORDER = ["Activation", "Challenge", "Surprise", "SelfGrowth", "CoCreation"]
FES_TO_INDEX = {name: i for i, name in enumerate(FES_ORDER)}

STATE_VARIANTS = [
    "side_tfc_phase",
    "side_tfc_phase_fes_string",
    "tfc_phase_fes_string",
    "fes_string_only",
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


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 1110)
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


def reward(row: pd.Series, op: str, endpoint: str) -> float:
    return float(row.get(f"{endpoint}_{op}", np.nan))


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


def gmr72_forward_resonance(step: float) -> float:
    if not np.isfinite(step):
        return np.nan
    # One string advance is the canonical 72-degree perspective rotation.
    return float(np.cos(2.0 * np.pi * ((step - 1.0) % 5.0) / 5.0))


def fes_index(value: object) -> float:
    return float(FES_TO_INDEX.get(str(value), np.nan))


def set_state_variant(table: pd.DataFrame, variant: str) -> pd.DataFrame:
    out = table.copy()
    base = (
        "side=" + out["boundary_side"].astype(str)
        + "|tfc=" + out["tfc_bin"].astype(str)
        + "|phase=" + out["phase_quadrant"].astype(str)
    )
    if variant == "side_tfc_phase":
        out["state_label"] = base
    elif variant == "side_tfc_phase_fes_string":
        out["state_label"] = base + "|fes=" + out["fes_phase"].astype(str)
    elif variant == "tfc_phase_fes_string":
        out["state_label"] = (
            "tfc=" + out["tfc_bin"].astype(str)
            + "|phase=" + out["phase_quadrant"].astype(str)
            + "|fes=" + out["fes_phase"].astype(str)
        )
    elif variant == "fes_string_only":
        out["state_label"] = "fes=" + out["fes_phase"].astype(str)
    else:
        raise ValueError(f"unknown state variant {variant}")
    return out


def build_base_table(args: argparse.Namespace) -> pd.DataFrame:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6i = load_module("private_b6i_for_b6k", B6I_SCRIPT)
    b6j = load_module("private_b6j_for_b6k", B6J_SCRIPT)
    table = b6i.build_base_table(args)
    table, _ = b6j.add_fes_state(table, args.annotated)
    return add_gmr72_operator_endpoints(table)


def add_gmr72_operator_endpoints(table: pd.DataFrame) -> pd.DataFrame:
    out = table.sort_values(["label", "idx_in_session"]).reset_index(drop=True).copy()
    out["fes_idx"] = out["fes_phase"].map(fes_index)
    op_cols = [f"{op}_z" for op in OPERATORS]
    out["operator_random_expectation"] = out[op_cols].mean(axis=1, skipna=True)
    out["operator_margin_raw"] = out["oracle_reward_z"] - out["operator_random_expectation"]
    out["gmr_c_readiness_raw"] = np.nanmean(
        np.vstack(
            [
                zscore(pd.to_numeric(out["TFC_min"], errors="coerce").to_numpy(dtype=float)),
                zscore(pd.to_numeric(out["TFC_mean"], errors="coerce").to_numpy(dtype=float)),
                zscore(pd.to_numeric(out["C_memory_scalar"], errors="coerce").to_numpy(dtype=float)),
                zscore(pd.to_numeric(out["operator_margin_raw"], errors="coerce").to_numpy(dtype=float)),
            ]
        ),
        axis=0,
    )

    for op in OPERATORS:
        for col in [
            "future_policy_readiness",
            "future_operator_margin",
            "future_tfc_readiness",
            "gmr72_forward_resonance",
            "gmr72_policy_readiness",
        ]:
            out[f"{col}_{op}_raw"] = np.nan

    for _, sub in out.groupby("label", sort=False):
        idxs = sub.index.to_numpy()
        times = pd.to_numeric(sub["idx_in_session"], errors="coerce").to_numpy(dtype=float)
        for local_i, row_index in enumerate(idxs):
            current_t = times[local_i]
            current_fes = out.loc[row_index, "fes_idx"]
            for op in OPERATORS:
                if op == "O7_suppress_event":
                    out.loc[row_index, f"future_policy_readiness_{op}_raw"] = 0.0
                    out.loc[row_index, f"future_operator_margin_{op}_raw"] = 0.0
                    out.loc[row_index, f"future_tfc_readiness_{op}_raw"] = 0.0
                    out.loc[row_index, f"gmr72_forward_resonance_{op}_raw"] = -1.0
                    out.loc[row_index, f"gmr72_policy_readiness_{op}_raw"] = -0.25
                    continue
                horizon = OPERATOR_HORIZON[op]
                candidates = np.where(times >= current_t + horizon)[0]
                candidates = candidates[candidates > local_i]
                if len(candidates) == 0:
                    continue
                next_index = idxs[int(candidates[0])]
                future_fes = out.loc[next_index, "fes_idx"]
                step = (future_fes - current_fes) % 5.0 if np.isfinite(current_fes) and np.isfinite(future_fes) else np.nan
                resonance = gmr72_forward_resonance(step)
                out.loc[row_index, f"future_policy_readiness_{op}_raw"] = out.loc[next_index, "oracle_reward_z"]
                out.loc[row_index, f"future_operator_margin_{op}_raw"] = out.loc[next_index, "operator_margin_raw"]
                out.loc[row_index, f"future_tfc_readiness_{op}_raw"] = out.loc[next_index, "gmr_c_readiness_raw"]
                out.loc[row_index, f"gmr72_forward_resonance_{op}_raw"] = resonance
                out.loc[row_index, f"gmr72_policy_readiness_{op}_raw"] = np.nanmean(
                    [
                        out.loc[next_index, "oracle_reward_z"],
                        out.loc[next_index, "operator_margin_raw"],
                        out.loc[next_index, "gmr_c_readiness_raw"],
                        resonance,
                    ]
                )

    endpoints = [
        "future_policy_readiness",
        "future_operator_margin",
        "future_tfc_readiness",
        "gmr72_forward_resonance",
        "gmr72_policy_readiness",
    ]
    for endpoint in endpoints:
        for op in OPERATORS:
            out[f"{endpoint}_{op}"] = zscore(out[f"{endpoint}_{op}_raw"].to_numpy(dtype=float))
    for op in OPERATORS:
        out[f"gmr72_composite_{op}"] = np.nanmean(
            np.vstack(
                [
                    out[f"future_policy_readiness_{op}"].to_numpy(dtype=float),
                    out[f"future_operator_margin_{op}"].to_numpy(dtype=float),
                    out[f"future_tfc_readiness_{op}"].to_numpy(dtype=float),
                    out[f"gmr72_forward_resonance_{op}"].to_numpy(dtype=float),
                    out[f"gmr72_policy_readiness_{op}"].to_numpy(dtype=float),
                ]
            ),
            axis=0,
        )
        out[f"gmr72_bridge_composite_{op}"] = np.nanmean(
            np.vstack(
                [
                    pd.to_numeric(out[f"{op}_z"], errors="coerce").to_numpy(dtype=float),
                    out[f"gmr72_policy_readiness_{op}"].to_numpy(dtype=float),
                    out[f"gmr72_forward_resonance_{op}"].to_numpy(dtype=float),
                ]
            ),
            axis=0,
        )
    return out


def train_policy(train: pd.DataFrame, endpoint: str, min_state_events: int) -> tuple[dict[str, str], str, pd.DataFrame]:
    global_means = {op: float(np.nanmean(train[f"{endpoint}_{op}"])) for op in OPERATORS}
    fallback = max(global_means, key=global_means.get)
    rows = []
    mapping = {}
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
            "global_best_operator": fallback,
            "global_best_train_reward": means[fallback],
        }
        row.update({f"train_mean_{op}": means[op] for op in OPERATORS})
        rows.append(row)
    return mapping, fallback, pd.DataFrame(rows)


def within_state_shuffled_policy(policy_table: pd.DataFrame, rng: np.random.Generator) -> dict[str, str]:
    mapping = {}
    op_array = np.asarray(OPERATORS, dtype=object)
    for _, row in policy_table.iterrows():
        shuffled = op_array.copy()
        rng.shuffle(shuffled)
        means = {shuffled_op: float(row[f"train_mean_{op}"]) for op, shuffled_op in zip(OPERATORS, shuffled)}
        mapping[str(row["state_label"])] = max(means, key=means.get)
    return mapping


def performance_strata(train: pd.DataFrame, endpoint: str) -> dict[str, str]:
    means = {op: float(np.nanmean(train[f"{endpoint}_{op}"])) for op in OPERATORS}
    ordered = sorted(OPERATORS, key=lambda op: means[op])
    strata = {}
    for label, chunk in zip(["low", "mid", "high"], np.array_split(np.asarray(ordered, dtype=object), 3)):
        for op in chunk:
            strata[str(op)] = label
    return strata


def stratum_matched_expected_reward(row: pd.Series, selected_op: str, strata: dict[str, str], endpoint: str) -> float:
    stratum = strata.get(selected_op, "missing")
    candidates = [op for op in OPERATORS if strata.get(op) == stratum]
    if not candidates:
        candidates = OPERATORS
    return weighted_reward(row, {op: 1.0 / len(candidates) for op in candidates}, endpoint)


def run_condition(table: pd.DataFrame, variant: str, endpoint: str, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 1120)
    data = set_state_variant(table, variant)
    folds = make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    policies = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy().reset_index(drop=True)
        mapping, fallback, policy_table = train_policy(train, endpoint, args.min_state_events)
        if policy_table.empty:
            continue
        policy_table["fold"] = fold_index
        policy_table["state_variant"] = variant
        policy_table["endpoint"] = endpoint
        policies.extend(policy_table.to_dict("records"))
        true_ops = [mapping.get(str(row["state_label"]), fallback) for _, row in test.iterrows()]
        freq_weights = operator_frequency_weights(true_ops)
        strata = performance_strata(train, endpoint)
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
                op = shuffled_mapping.get(str(row["state_label"]), fallback)
                val = reward(row, op, endpoint)
                if np.isfinite(val):
                    within_rewards[i] += val
                    within_counts[i] += 1.0
                val = reward(row, str(shuffled_ops[i]), endpoint)
                if np.isfinite(val):
                    balanced_rewards[i] += val
                    balanced_counts[i] += 1.0
        for i, (_, row) in enumerate(test.iterrows()):
            op = true_ops[i]
            rows.append(
                {
                    "state_variant": variant,
                    "endpoint": endpoint,
                    "fold": fold_index,
                    "label": row["label"],
                    "idx_in_session": row["idx_in_session"],
                    "state_label": row["state_label"],
                    "fes_phase": row["fes_phase"],
                    "selected_operator": op,
                    "true_reward": reward(row, op, endpoint),
                    "balanced_pool_shuffle_reward": float(balanced_rewards[i] / balanced_counts[i]) if balanced_counts[i] > 0 else np.nan,
                    "frequency_matched_random_reward": weighted_reward(row, freq_weights, endpoint),
                    "performance_matched_random_reward": stratum_matched_expected_reward(row, op, strata, endpoint),
                    "within_state_shuffle_reward": float(within_rewards[i] / within_counts[i]) if within_counts[i] > 0 else np.nan,
                    "oracle_reward": max([reward(row, cand, endpoint) for cand in OPERATORS if np.isfinite(reward(row, cand, endpoint))], default=np.nan),
                    "policy_source": "state_mapping" if str(row["state_label"]) in mapping else "global_fallback",
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(policies)


def summarize_condition(cv: pd.DataFrame, variant: str, endpoint: str, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1130)
    controls = [
        "balanced_pool_shuffle",
        "frequency_matched_random",
        "performance_matched_random",
        "within_state_shuffle",
        "oracle",
    ]
    true = pd.to_numeric(cv["true_reward"], errors="coerce").to_numpy(dtype=float)
    rows = []
    for control in controls:
        comp = pd.to_numeric(cv[f"{control}_reward"], errors="coerce").to_numpy(dtype=float)
        effect, p = signflip_p(true - comp, rng, args.n_perm)
        rows.append(
            {
                "state_variant": variant,
                "endpoint": endpoint,
                "comparison": f"gmr72_policy_vs_{control}",
                "mean_true_policy": float(np.nanmean(true)),
                "mean_comparator": float(np.nanmean(comp)),
                "effect": effect,
                "p_greater": p,
                "n_events": int(np.isfinite(true - comp).sum()),
                "state_mapping_rate": float(np.nanmean(cv["policy_source"].eq("state_mapping"))),
            }
        )
    return pd.DataFrame(rows)


def success_for(summary: pd.DataFrame) -> bool:
    by = summary.set_index("comparison")
    for name in [
        "gmr72_policy_vs_balanced_pool_shuffle",
        "gmr72_policy_vs_frequency_matched_random",
        "gmr72_policy_vs_performance_matched_random",
        "gmr72_policy_vs_within_state_shuffle",
    ]:
        if name not in by.index:
            return False
        row = by.loc[name]
        if not (row["effect"] > 0 and row["p_greater"] <= 0.05):
            return False
    return "gmr72_policy_vs_oracle" in by.index and by.loc["gmr72_policy_vs_oracle", "effect"] < 0


def write_report(path: Path, results: pd.DataFrame, summaries: pd.DataFrame, args: argparse.Namespace) -> None:
    successes = results[results["success"]].copy()
    lines = [
        "# Private B6K GMR72 FES Resonance Policy Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Purpose: test whether a five-string FES resonance engine, abstracted as a GMR72 function, can exceed the B6F recursive-policy boundary.",
        "",
        "Interpretation boundary: this does not redefine C as FES. FES is used as an operational perspective-mode resonance engine.",
        "",
        "## GMR72 Engine",
        "",
        "- FES strings: Activation, Challenge, Surprise, SelfGrowth, CoCreation.",
        "- Each string is mapped to a 72-degree phase on a five-state circle.",
        "- One-string forward movement is treated as canonical GMR72 perspective rotation.",
        "- Operator rewards are evaluated by future policy readiness, future operator margin, future TFC/C readiness, and GMR72 forward resonance.",
        "",
        "## Main Results",
        "",
        f"- successful conditions: {int(results['success'].sum())} / {len(results)}",
        f"- successful variants: {', '.join(successes['state_variant'].astype(str).unique()) if len(successes) else 'none'}",
        "",
        "## Condition Results",
        "",
        results.to_csv(index=False).strip(),
        "",
        "## Comparison Summary",
        "",
        summaries.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- n_folds: {args.n_folds}",
        f"- min_state_events: {args.min_state_events}",
        f"- n_control_draws: {args.n_control_draws}",
        f"- n_perm: {args.n_perm}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    table = build_base_table(args)
    table.to_csv(outdir / "private_B6K_gmr72_state_table.csv", index=False)
    result_rows = []
    all_summaries = []
    all_cv = []
    all_policies = []
    endpoints = ["gmr72_policy_readiness", "gmr72_composite", "gmr72_bridge_composite"]
    for variant in STATE_VARIANTS:
        for endpoint in endpoints:
            cv, policies = run_condition(table, variant, endpoint, args)
            if cv.empty:
                continue
            summary = summarize_condition(cv, variant, endpoint, args)
            ok = success_for(summary)
            result_rows.append(
                {
                    "state_variant": variant,
                    "endpoint": endpoint,
                    "success": ok,
                    "mean_true_reward": float(np.nanmean(cv["true_reward"])),
                    "n_events": int(len(cv)),
                    "state_mapping_rate": float(np.nanmean(cv["policy_source"].eq("state_mapping"))),
                    "effect_vs_balanced": float(summary[summary["comparison"].eq("gmr72_policy_vs_balanced_pool_shuffle")]["effect"].iloc[0]),
                    "effect_vs_frequency": float(summary[summary["comparison"].eq("gmr72_policy_vs_frequency_matched_random")]["effect"].iloc[0]),
                    "effect_vs_performance": float(summary[summary["comparison"].eq("gmr72_policy_vs_performance_matched_random")]["effect"].iloc[0]),
                    "effect_vs_within": float(summary[summary["comparison"].eq("gmr72_policy_vs_within_state_shuffle")]["effect"].iloc[0]),
                    "effect_vs_oracle": float(summary[summary["comparison"].eq("gmr72_policy_vs_oracle")]["effect"].iloc[0]),
                }
            )
            all_summaries.append(summary)
            all_cv.append(cv)
            all_policies.append(policies)

    results = pd.DataFrame(result_rows).sort_values(["success", "effect_vs_balanced"], ascending=[False, False])
    summaries = pd.concat(all_summaries, ignore_index=True) if all_summaries else pd.DataFrame()
    cv_all = pd.concat(all_cv, ignore_index=True) if all_cv else pd.DataFrame()
    policies_all = pd.concat(all_policies, ignore_index=True) if all_policies else pd.DataFrame()
    results.to_csv(outdir / "private_B6K_gmr72_condition_results.csv", index=False)
    summaries.to_csv(outdir / "private_B6K_gmr72_comparison_summary.csv", index=False)
    cv_all.to_csv(outdir / "private_B6K_gmr72_heldout_rewards.csv", index=False)
    policies_all.to_csv(outdir / "private_B6K_gmr72_learned_policies.csv", index=False)
    write_report(outdir / "private_B6K_gmr72_fes_resonance_policy_summary.md", results, summaries, args)
    print("\nPrivate B6K GMR72 FES resonance policy outputs")
    print(outdir)
    print(results.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6k_gmr72_fes_resonance_policy")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=61020)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
