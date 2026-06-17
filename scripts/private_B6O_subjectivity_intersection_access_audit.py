#!/usr/bin/env python3
"""Private B6O Subjectivity-Intersection Access Audit.

Private only. Do not publish, stage, commit, or push.

Question:
    Does C/FES-GMR72 change A/B readout only when access is mediated through
    intersection, rather than when C is scored as an object?

Boundary:
    This does not observe subjectivity directly. It measures access-by-
    intersection effects: A-through-C-to-B and B-through-C-to-A readout changes.
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
    "combined_c_fes_gmr72",
    "gmr72_phase_conditioned",
    "fes_string_conditioned",
    "linear_c_state",
]

ENDPOINTS = ["z_reward", "rank_reward", "gmr72_bridge_composite"]

CONTROL_KINDS = [
    "true_intersection",
    "random_intersection",
    "balanced_intersection",
    "performance_matched_intersection",
    "shuffled_c_intersection",
    "phase_rotated_intersection",
]

# These are not subject-position scores. They define which readout components
# are allowed to contribute when access is mediated toward the other side.
A_TO_B_MASK = {
    "O1_lag0_AB": 0.20,
    "O2_lag5_AB": 0.80,
    "O3_A_C_boundary": 0.10,
    "O4_B_C_boundary": 1.00,
    "O5_full_TFC": 0.65,
    "O6_phase_only": 0.35,
    "O7_suppress_event": 0.05,
}

B_TO_A_MASK = {
    "O1_lag0_AB": 0.80,
    "O2_lag5_AB": 0.35,
    "O3_A_C_boundary": 1.00,
    "O4_B_C_boundary": 0.10,
    "O5_full_TFC": 0.65,
    "O6_phase_only": 0.35,
    "O7_suppress_event": 0.05,
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 1510)
    labels = np.asarray(sorted(set(map(str, labels))), dtype=object)
    rng.shuffle(labels)
    return [fold for fold in np.array_split(labels, n_folds) if len(fold)]


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


def normalize_weights(weights: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    weights = np.where(np.isfinite(weights), weights, 0.0)
    weights = np.clip(weights, 0.0, None)
    total = float(np.sum(weights))
    if total <= 1e-12:
        return np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    return weights / total


def masked_weights(weights: np.ndarray, direction: str) -> np.ndarray:
    mask_dict = A_TO_B_MASK if direction == "A_to_C_to_B" else B_TO_A_MASK
    mask = np.asarray([mask_dict[op] for op in OPERATORS], dtype=float)
    return normalize_weights(normalize_weights(weights) * mask)


def rotate_weights(weights: np.ndarray, shift: int = 1) -> np.ndarray:
    out = np.asarray(weights, dtype=float).copy()
    out[:5] = np.roll(out[:5], shift)
    return normalize_weights(out)


def build_table(args: argparse.Namespace):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6l = load_module("private_b6l_for_b6o", B6L_SCRIPT)
    table = b6l.build_table(args)
    return b6l, table


def primitive_reward(row: pd.Series, b6l, op: str, endpoint: str) -> float:
    col = b6l.operator_reward_columns(endpoint)[op]
    return float(pd.to_numeric(row.get(col, np.nan), errors="coerce"))


def weighted_reward(row: pd.Series, b6l, weights: np.ndarray, endpoint: str) -> float:
    return b6l.row_reward(row, normalize_weights(weights), endpoint)


def train_fold_generators(train: pd.DataFrame, b6l, mode: str, endpoint: str, args: argparse.Namespace, rng: np.random.Generator):
    mapping, global_weights, selected_mapping, global_best, policies = b6l.train_weights(
        train,
        mode,
        endpoint,
        args.min_state_events,
        args.temperature,
    )
    policies = policies.copy()
    train = train.copy()
    train["b6o_state_label"] = b6l.state_labels(train, mode)
    true_weights_by_state = {state: normalize_weights(weights) for state, weights in mapping.items()}
    shuffled_weights = list(true_weights_by_state.values())
    rng.shuffle(shuffled_weights)
    shuffled_by_state = {
        state: shuffled_weights[i % len(shuffled_weights)]
        for i, state in enumerate(true_weights_by_state.keys())
    } if shuffled_weights else {}
    perf_weights = normalize_weights(b6l.performance_matched_weights(train, endpoint))
    return {
        "true": true_weights_by_state,
        "shuffled": shuffled_by_state,
        "global": normalize_weights(global_weights),
        "performance": perf_weights,
        "selected_mapping": selected_mapping,
        "global_best": global_best,
        "policies": policies,
    }


def get_state_weights(state: str, fold_info: dict, kind: str, rng: np.random.Generator) -> np.ndarray:
    if kind == "true_intersection":
        return fold_info["true"].get(state, fold_info["global"])
    if kind == "random_intersection":
        return normalize_weights(rng.dirichlet(np.ones(len(OPERATORS))))
    if kind == "balanced_intersection":
        return np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    if kind == "performance_matched_intersection":
        return fold_info["performance"]
    if kind == "shuffled_c_intersection":
        return fold_info["shuffled"].get(state, fold_info["global"])
    if kind == "phase_rotated_intersection":
        return rotate_weights(fold_info["true"].get(state, fold_info["global"]), shift=1)
    raise ValueError(f"unknown control kind {kind}")


def baseline_readouts(row: pd.Series, b6l, endpoint: str) -> dict[str, float]:
    a_alone = primitive_reward(row, b6l, "O3_A_C_boundary", endpoint)
    b_alone = primitive_reward(row, b6l, "O4_B_C_boundary", endpoint)
    neutral = weighted_reward(row, b6l, np.ones(len(OPERATORS)) / len(OPERATORS), endpoint)
    external = primitive_reward(row, b6l, "O5_full_TFC", endpoint)
    return {
        "A_alone": a_alone,
        "B_alone": b_alone,
        "neutral_external": neutral,
        "full_tfc_external": external,
        "baseline_max": float(np.nanmax([a_alone, b_alone, neutral, external])),
    }


def run_condition(table: pd.DataFrame, b6l, mode: str, endpoint: str, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 1520)
    data = table.copy()
    data["b6o_state_label"] = b6l.state_labels(data, mode)
    folds = make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    policies = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy().reset_index(drop=True)
        fold_info = train_fold_generators(train, b6l, mode, endpoint, args, rng)
        policy_table = fold_info["policies"].copy()
        if not policy_table.empty:
            policy_table["fold"] = fold_index
            policy_table["mode"] = mode
            policy_table["endpoint"] = endpoint
            policies.extend(policy_table.to_dict("records"))
        for _, row in test.iterrows():
            state = str(row["b6o_state_label"])
            base = baseline_readouts(row, b6l, endpoint)
            for direction in ["A_to_C_to_B", "B_to_C_to_A"]:
                opposite_alone = base["B_alone"] if direction == "A_to_C_to_B" else base["A_alone"]
                own_alone = base["A_alone"] if direction == "A_to_C_to_B" else base["B_alone"]
                for kind in CONTROL_KINDS:
                    weights = masked_weights(get_state_weights(state, fold_info, kind, rng), direction)
                    access = weighted_reward(row, b6l, weights, endpoint)
                    rows.append(
                        {
                            "mode": mode,
                            "endpoint": endpoint,
                            "fold": fold_index,
                            "label": row["label"],
                            "idx_in_session": row["idx_in_session"],
                            "state_label": state,
                            "direction": direction,
                            "control_kind": kind,
                            "access_readout": access,
                            "A_alone_readout": base["A_alone"],
                            "B_alone_readout": base["B_alone"],
                            "neutral_external_readout": base["neutral_external"],
                            "full_tfc_external_readout": base["full_tfc_external"],
                            "opposite_alone_readout": opposite_alone,
                            "own_alone_readout": own_alone,
                            "baseline_max_readout": base["baseline_max"],
                            "intersection_access_effect": access - base["baseline_max"] if np.isfinite(access) and np.isfinite(base["baseline_max"]) else np.nan,
                            "opposite_access_effect": access - opposite_alone if np.isfinite(access) and np.isfinite(opposite_alone) else np.nan,
                            "own_access_effect": access - own_alone if np.isfinite(access) and np.isfinite(own_alone) else np.nan,
                            **{f"w_{op}": float(weights[i]) for i, op in enumerate(OPERATORS)},
                        }
                    )
    return pd.DataFrame(rows), pd.DataFrame(policies)


def compare_controls(access: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1530)
    rows = []
    controls = [kind for kind in CONTROL_KINDS if kind != "true_intersection"]
    for keys, sub in access.groupby(["mode", "endpoint", "direction"], sort=False):
        mode, endpoint, direction = keys
        true = sub[sub["control_kind"].eq("true_intersection")].set_index(["fold", "label", "idx_in_session", "state_label"])
        for metric in ["access_readout", "intersection_access_effect", "opposite_access_effect", "own_access_effect"]:
            true_vals = true[[metric]]
            for control in controls:
                comp = sub[sub["control_kind"].eq(control)].set_index(["fold", "label", "idx_in_session", "state_label"])
                joined = true_vals.join(comp[[metric]], how="inner", lsuffix="_true", rsuffix="_control")
                diff = joined[f"{metric}_true"].to_numpy(dtype=float) - joined[f"{metric}_control"].to_numpy(dtype=float)
                effect, p = signflip_p(diff, rng, args.n_perm)
                rows.append(
                    {
                        "mode": mode,
                        "endpoint": endpoint,
                        "direction": direction,
                        "metric": metric,
                        "comparison": f"true_vs_{control}",
                        "mean_true": float(np.nanmean(joined[f"{metric}_true"])),
                        "mean_control": float(np.nanmean(joined[f"{metric}_control"])),
                        "effect": effect,
                        "p_greater": p,
                        "n_pairs": int(np.isfinite(diff).sum()),
                    }
                )
    return pd.DataFrame(rows)


def summarize(access: pd.DataFrame, comparisons: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, sub in access.groupby(["mode", "endpoint", "direction"], sort=False):
        mode, endpoint, direction = keys
        true = sub[sub["control_kind"].eq("true_intersection")]
        by = comparisons[
            comparisons["mode"].eq(mode)
            & comparisons["endpoint"].eq(endpoint)
            & comparisons["direction"].eq(direction)
            & comparisons["metric"].eq("intersection_access_effect")
        ].set_index("comparison")
        minimum_names = [
            "true_vs_random_intersection",
            "true_vs_balanced_intersection",
            "true_vs_shuffled_c_intersection",
        ]
        strong_names = [
            "true_vs_performance_matched_intersection",
            "true_vs_phase_rotated_intersection",
        ]
        minimum = all(
            name in by.index and by.loc[name, "effect"] > 0 and by.loc[name, "p_greater"] <= 0.05
            for name in minimum_names
        )
        strong = minimum and all(
            name in by.index and by.loc[name, "effect"] > 0 and by.loc[name, "p_greater"] <= 0.05
            for name in strong_names
        )
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "direction": direction,
                "minimum_success": minimum,
                "strong_success": strong,
                "mean_access_readout": float(np.nanmean(true["access_readout"])),
                "mean_intersection_access_effect": float(np.nanmean(true["intersection_access_effect"])),
                "mean_opposite_access_effect": float(np.nanmean(true["opposite_access_effect"])),
                "mean_own_access_effect": float(np.nanmean(true["own_access_effect"])),
                "n_events": int(len(true)),
                "effect_vs_random": float(by.loc["true_vs_random_intersection", "effect"]) if "true_vs_random_intersection" in by.index else np.nan,
                "p_vs_random": float(by.loc["true_vs_random_intersection", "p_greater"]) if "true_vs_random_intersection" in by.index else np.nan,
                "effect_vs_balanced": float(by.loc["true_vs_balanced_intersection", "effect"]) if "true_vs_balanced_intersection" in by.index else np.nan,
                "p_vs_balanced": float(by.loc["true_vs_balanced_intersection", "p_greater"]) if "true_vs_balanced_intersection" in by.index else np.nan,
                "effect_vs_shuffled_c": float(by.loc["true_vs_shuffled_c_intersection", "effect"]) if "true_vs_shuffled_c_intersection" in by.index else np.nan,
                "p_vs_shuffled_c": float(by.loc["true_vs_shuffled_c_intersection", "p_greater"]) if "true_vs_shuffled_c_intersection" in by.index else np.nan,
                "effect_vs_performance": float(by.loc["true_vs_performance_matched_intersection", "effect"]) if "true_vs_performance_matched_intersection" in by.index else np.nan,
                "p_vs_performance": float(by.loc["true_vs_performance_matched_intersection", "p_greater"]) if "true_vs_performance_matched_intersection" in by.index else np.nan,
                "effect_vs_phase_rotated": float(by.loc["true_vs_phase_rotated_intersection", "effect"]) if "true_vs_phase_rotated_intersection" in by.index else np.nan,
                "p_vs_phase_rotated": float(by.loc["true_vs_phase_rotated_intersection", "p_greater"]) if "true_vs_phase_rotated_intersection" in by.index else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["strong_success", "minimum_success", "mean_intersection_access_effect", "effect_vs_balanced"],
        ascending=[False, False, False, False],
    )


def write_report(path: Path, results: pd.DataFrame, comparisons: pd.DataFrame, args: argparse.Namespace) -> None:
    best = results.iloc[0] if len(results) else None
    best_label = f"{best['mode']} / {best['endpoint']} / {best['direction']}" if best is not None else "none"
    lines = [
        "# Private B6O Subjectivity-Intersection Access Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Question: Does C-mediated intersection change what can be read from A and B, without scoring subjectivity as an object?",
        "",
        "Interpretation boundary: subjectivity is not objectively observed here. Only intersection-access effects are measured.",
        "",
        "## Readouts",
        "",
        "- A-alone: A-C boundary readout.",
        "- B-alone: B-C boundary readout.",
        "- neutral/external: balanced primitive readout and full-TFC readout.",
        "- A-through-C-to-B: C/FES-GMR72 generated weights projected through the B-side access mask.",
        "- B-through-C-to-A: C/FES-GMR72 generated weights projected through the A-side access mask.",
        "",
        "## Main Findings",
        "",
        f"- strongest intersection-access condition: {best_label}",
        f"- minimum-success conditions: {int(results['minimum_success'].sum())} / {len(results)}",
        f"- strong-success conditions: {int(results['strong_success'].sum())} / {len(results)}",
        "",
        "## Condition Results",
        "",
        results.to_csv(index=False).strip(),
        "",
        "## Control Comparisons",
        "",
        comparisons.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- n_folds: {args.n_folds}",
        f"- min_state_events: {args.min_state_events}",
        f"- temperature: {args.temperature}",
        f"- n_perm: {args.n_perm}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    b6l, table = build_table(args)
    table.to_csv(outdir / "private_B6O_intersection_access_state_table.csv", index=False)
    all_access = []
    all_policies = []
    for mode in MODES:
        for endpoint in ENDPOINTS:
            access, policies = run_condition(table, b6l, mode, endpoint, args)
            if access.empty:
                continue
            all_access.append(access)
            all_policies.append(policies)
    access = pd.concat(all_access, ignore_index=True) if all_access else pd.DataFrame()
    policies = pd.concat(all_policies, ignore_index=True) if all_policies else pd.DataFrame()
    comparisons = compare_controls(access, args) if not access.empty else pd.DataFrame()
    results = summarize(access, comparisons) if not access.empty else pd.DataFrame()
    access.to_csv(outdir / "private_B6O_intersection_access_readouts.csv", index=False)
    comparisons.to_csv(outdir / "private_B6O_control_comparison.csv", index=False)
    results.to_csv(outdir / "private_B6O_intersection_access_results.csv", index=False)
    policies.to_csv(outdir / "private_B6O_generated_access_policies.csv", index=False)
    write_report(outdir / "private_B6O_subjectivity_intersection_access_summary.md", results, comparisons, args)
    print("\nPrivate B6O subjectivity-intersection access outputs")
    print(outdir)
    print(results.to_string(index=False, max_rows=80))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6o_subjectivity_intersection_access")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=61420)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
