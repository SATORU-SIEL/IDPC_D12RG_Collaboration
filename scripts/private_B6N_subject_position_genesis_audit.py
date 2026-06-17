#!/usr/bin/env python3
"""Private B6N Subject-Position Genesis Audit.

Private only. Do not publish, stage, commit, or push.

Question:
    Does C/FES-GMR72 generate distinct, coherent, state-specific operator
    standpoints rather than merely optimizing performance?

Boundary:
    This is not AGI, not conscious experience, not qualia generation, and not
    recursive self-improvement. It tests whether generated operator
    configurations behave like an operational subject-position.
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
    "true_generated",
    "random_generated",
    "balanced_generated",
    "frequency_matched_generated",
    "performance_matched_generated",
    "shuffled_c_state_generated",
    "shuffled_fes_string_generated",
    "shuffled_gmr72_phase_generated",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 1410)
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


def zscore(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    out = np.full(len(values), np.nan, dtype=float)
    mask = np.isfinite(values)
    if mask.sum() < 3:
        return out
    mu = float(np.nanmean(values[mask]))
    sd = float(np.nanstd(values[mask]))
    if not np.isfinite(sd) or sd <= 1e-12:
        out[mask] = 0.0
    else:
        out[mask] = (values[mask] - mu) / sd
    return out


def normalize_weights(weights: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    weights = np.where(np.isfinite(weights), weights, 0.0)
    weights = np.clip(weights, 0.0, None)
    total = float(np.sum(weights))
    if total <= 1e-12:
        return np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    return weights / total


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-12:
        return np.nan
    return float(np.dot(a, b) / denom)


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    sim = cosine_similarity(a, b)
    if not np.isfinite(sim):
        return np.nan
    return float(1.0 - sim)


def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(np.asarray(a, dtype=float) - np.asarray(b, dtype=float)))


def one_hot(op: str) -> np.ndarray:
    out = np.zeros(len(OPERATORS), dtype=float)
    out[OPERATORS.index(op)] = 1.0
    return out


def nearest_primitive_distance(weights: np.ndarray) -> tuple[float, float, str]:
    distances = [(op, cosine_distance(weights, one_hot(op)), euclidean_distance(weights, one_hot(op))) for op in OPERATORS]
    op, cos_d, euc_d = min(distances, key=lambda x: x[1])
    return float(cos_d), float(euc_d), op


def parse_fes(state_label: str) -> str:
    for part in str(state_label).split("|"):
        if part.startswith("fes="):
            return part.split("=", 1)[1]
    return "missing"


def parse_phase(state_label: str) -> str:
    for part in str(state_label).split("|"):
        if part.startswith("phase="):
            return part.split("=", 1)[1]
    return "missing"


def rotate_weights(weights: np.ndarray, shift: int = 1) -> np.ndarray:
    # Rotate only the first five active primitives as a GMR72 phase-shuffle proxy;
    # keep phase-only and suppress channels in place.
    out = np.asarray(weights, dtype=float).copy()
    out[:5] = np.roll(out[:5], shift)
    return normalize_weights(out)


def build_table(args: argparse.Namespace):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6l = load_module("private_b6l_for_b6n", B6L_SCRIPT)
    table = b6l.build_table(args)
    return b6l, table


def fold_true_families(train: pd.DataFrame, b6l, mode: str, endpoint: str, args: argparse.Namespace):
    mapping, global_weights, selected_mapping, global_best, policy_table = b6l.train_weights(
        train, mode, endpoint, args.min_state_events, args.temperature
    )
    policy_table = policy_table.copy()
    if policy_table.empty:
        return mapping, global_weights, selected_mapping, global_best, policy_table
    policy_table["fes_string"] = policy_table["state_label"].map(parse_fes)
    policy_table["phase_bin"] = policy_table["state_label"].map(parse_phase)
    return mapping, global_weights, selected_mapping, global_best, policy_table


def control_weight_rows(policy_table: pd.DataFrame, train: pd.DataFrame, b6l, endpoint: str, rng: np.random.Generator) -> list[dict]:
    rows = []
    if policy_table.empty:
        return rows
    weight_cols = [f"w_{op}" for op in OPERATORS]
    selected_ops = policy_table["selected_operator"].astype(str).tolist()
    freq = np.asarray([selected_ops.count(op) for op in OPERATORS], dtype=float)
    freq_weights = normalize_weights(freq)
    perf_weights = normalize_weights(b6l.performance_matched_weights(train, endpoint))
    true_weights = {
        str(row["state_label"]): normalize_weights(row[weight_cols].to_numpy(dtype=float))
        for _, row in policy_table.iterrows()
    }
    shuffled_states = list(true_weights.values())
    rng.shuffle(shuffled_states)
    fes_groups = {
        fes: sub["state_label"].astype(str).tolist()
        for fes, sub in policy_table.groupby("fes_string", sort=False)
    }
    all_states = policy_table["state_label"].astype(str).tolist()

    for i, row in policy_table.reset_index(drop=True).iterrows():
        state = str(row["state_label"])
        true_w = true_weights[state]
        state_pool_same_fes = [
            cand for cand in fes_groups.get(str(row["fes_string"]), [])
            if cand != state
        ]
        if state_pool_same_fes:
            fes_shuffle_state = str(rng.choice(state_pool_same_fes))
            fes_shuffle_w = true_weights[fes_shuffle_state]
        else:
            fes_shuffle_w = shuffled_states[i % len(shuffled_states)]
        controls = {
            "true_generated": true_w,
            "random_generated": normalize_weights(rng.dirichlet(np.ones(len(OPERATORS)))),
            "balanced_generated": np.ones(len(OPERATORS), dtype=float) / len(OPERATORS),
            "frequency_matched_generated": freq_weights,
            "performance_matched_generated": perf_weights,
            "shuffled_c_state_generated": shuffled_states[i % len(shuffled_states)],
            "shuffled_fes_string_generated": fes_shuffle_w,
            "shuffled_gmr72_phase_generated": rotate_weights(true_w, shift=1),
        }
        for kind, weights in controls.items():
            out = {
                "control_kind": kind,
                "state_label": state,
                "fes_string": row["fes_string"],
                "phase_bin": row["phase_bin"],
                "n_train_events": int(row["n_train_events"]),
                "selected_operator": row["selected_operator"],
                "selected_train_reward": float(row["selected_train_reward"]),
                "generated_train_reward": float(row["generated_train_reward"]),
            }
            out.update({f"w_{op}": float(weights[j]) for j, op in enumerate(OPERATORS)})
            rows.append(out)
    return rows


def add_subject_position_metrics(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return rows
    out = rows.copy()
    weight_cols = [f"w_{op}" for op in OPERATORS]
    weights_by_row = out[weight_cols].to_numpy(dtype=float)
    novelty_cos = []
    novelty_euc = []
    nearest_ops = []
    selected_cos = []
    selected_euc = []
    entropy = []
    max_weight = []
    for i, row in out.iterrows():
        weights = normalize_weights(weights_by_row[i])
        cos_d, euc_d, nearest = nearest_primitive_distance(weights)
        novelty_cos.append(cos_d)
        novelty_euc.append(euc_d)
        nearest_ops.append(nearest)
        selected = str(row["selected_operator"])
        selected_cos.append(cosine_distance(weights, one_hot(selected)) if selected in OPERATORS else np.nan)
        selected_euc.append(euclidean_distance(weights, one_hot(selected)) if selected in OPERATORS else np.nan)
        finite = weights[weights > 0]
        entropy.append(float(-np.sum(finite * np.log(finite)) / np.log(len(OPERATORS))))
        max_weight.append(float(np.max(weights)))
    out["novelty_cosine_distance"] = novelty_cos
    out["novelty_euclidean_distance"] = novelty_euc
    out["nearest_primitive_operator"] = nearest_ops
    out["distance_to_best_selected_cosine"] = selected_cos
    out["distance_to_best_selected_euclidean"] = selected_euc
    out["operator_entropy"] = entropy
    out["selection_collapse_rate"] = (np.asarray(max_weight) >= 0.85).astype(float)
    out["non_collapse"] = 1.0 - out["selection_collapse_rate"]

    coherence_rows = []
    specificity_rows = []
    for keys, sub in out.groupby(["mode", "endpoint", "control_kind", "state_label"], sort=False):
        ws = sub[weight_cols].to_numpy(dtype=float)
        sims = []
        for a in range(len(ws)):
            for b in range(a + 1, len(ws)):
                sims.append(cosine_similarity(normalize_weights(ws[a]), normalize_weights(ws[b])))
        coherence_rows.append((*keys, float(np.nanmean(sims)) if sims else np.nan))
    coherence = pd.DataFrame(coherence_rows, columns=["mode", "endpoint", "control_kind", "state_label", "within_state_coherence"])
    out = out.merge(coherence, on=["mode", "endpoint", "control_kind", "state_label"], how="left")

    for keys, sub in out.groupby(["mode", "endpoint", "control_kind"], sort=False):
        state_means = sub.groupby("state_label")[weight_cols].mean()
        global_mean = normalize_weights(sub[weight_cols].mean().to_numpy(dtype=float))
        between = [euclidean_distance(normalize_weights(row.to_numpy(dtype=float)), global_mean) for _, row in state_means.iterrows()]
        specificity_rows.append((*keys, float(np.nanmean(between)) if between else np.nan))
    specificity = pd.DataFrame(specificity_rows, columns=["mode", "endpoint", "control_kind", "state_specificity"])
    out = out.merge(specificity, on=["mode", "endpoint", "control_kind"], how="left")

    for col in [
        "novelty_cosine_distance",
        "within_state_coherence",
        "state_specificity",
        "non_collapse",
        "distance_to_best_selected_cosine",
    ]:
        out[f"z_{col}"] = np.nan
    for (mode, endpoint), idx in out.groupby(["mode", "endpoint"]).groups.items():
        idx = list(idx)
        for col in [
            "novelty_cosine_distance",
            "within_state_coherence",
            "state_specificity",
            "non_collapse",
            "distance_to_best_selected_cosine",
        ]:
            out.loc[idx, f"z_{col}"] = zscore(out.loc[idx, col].to_numpy(dtype=float))
    out["subject_position_score"] = (
        out["z_novelty_cosine_distance"]
        + out["z_within_state_coherence"]
        + out["z_state_specificity"]
        + out["z_non_collapse"]
        + out["z_distance_to_best_selected_cosine"]
    )
    return out


def build_subject_positions(table: pd.DataFrame, b6l, mode: str, endpoint: str, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 1420)
    folds = make_folds(table["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    raw_policies = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = table["label"].astype(str).isin(set(test_labels))
        train = table[~test_mask].copy()
        _, _, _, _, policy_table = fold_true_families(train, b6l, mode, endpoint, args)
        if policy_table.empty:
            continue
        policy_table["fold"] = fold_index
        policy_table["mode"] = mode
        policy_table["endpoint"] = endpoint
        raw_policies.extend(policy_table.to_dict("records"))
        for row in control_weight_rows(policy_table, train, b6l, endpoint, rng):
            row["fold"] = fold_index
            row["mode"] = mode
            row["endpoint"] = endpoint
            rows.append(row)
    return add_subject_position_metrics(pd.DataFrame(rows)), pd.DataFrame(raw_policies)


def compare_controls(scores: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1430)
    rows = []
    controls = [kind for kind in CONTROL_KINDS if kind != "true_generated"]
    for (mode, endpoint), sub in scores.groupby(["mode", "endpoint"], sort=False):
        true = sub[sub["control_kind"].eq("true_generated")].set_index(["fold", "state_label"])
        for control in controls:
            comp = sub[sub["control_kind"].eq(control)].set_index(["fold", "state_label"])
            joined = true[["subject_position_score"]].join(
                comp[["subject_position_score"]],
                how="inner",
                lsuffix="_true",
                rsuffix="_control",
            )
            diff = joined["subject_position_score_true"].to_numpy(dtype=float) - joined["subject_position_score_control"].to_numpy(dtype=float)
            effect, p = signflip_p(diff, rng, args.n_perm)
            rows.append(
                {
                    "mode": mode,
                    "endpoint": endpoint,
                    "comparison": f"true_sps_vs_{control}",
                    "mean_true_sps": float(np.nanmean(joined["subject_position_score_true"])),
                    "mean_control_sps": float(np.nanmean(joined["subject_position_score_control"])),
                    "effect": effect,
                    "p_greater": p,
                    "n_pairs": int(np.isfinite(diff).sum()),
                }
            )
    return pd.DataFrame(rows)


def summarize_conditions(scores: pd.DataFrame, comparisons: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (mode, endpoint), sub in scores.groupby(["mode", "endpoint"], sort=False):
        true = sub[sub["control_kind"].eq("true_generated")]
        by = comparisons[
            comparisons["mode"].eq(mode)
            & comparisons["endpoint"].eq(endpoint)
        ].set_index("comparison")
        minimum = all(
            name in by.index and by.loc[name, "effect"] > 0 and by.loc[name, "p_greater"] <= 0.05
            for name in [
                "true_sps_vs_random_generated",
                "true_sps_vs_balanced_generated",
                "true_sps_vs_shuffled_c_state_generated",
            ]
        )
        strong = minimum and all(
            name in by.index and by.loc[name, "effect"] > 0 and by.loc[name, "p_greater"] <= 0.05
            for name in [
                "true_sps_vs_performance_matched_generated",
                "true_sps_vs_shuffled_fes_string_generated",
                "true_sps_vs_shuffled_gmr72_phase_generated",
            ]
        )
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "minimum_success": minimum,
                "strong_success": strong,
                "mean_true_sps": float(np.nanmean(true["subject_position_score"])),
                "mean_novelty": float(np.nanmean(true["novelty_cosine_distance"])),
                "mean_distance_to_selected": float(np.nanmean(true["distance_to_best_selected_cosine"])),
                "mean_coherence": float(np.nanmean(true["within_state_coherence"])),
                "mean_state_specificity": float(np.nanmean(true["state_specificity"])),
                "mean_non_collapse": float(np.nanmean(true["non_collapse"])),
                "collapse_rate": float(np.nanmean(true["selection_collapse_rate"])),
                "n_subject_positions": int(len(true)),
                "effect_vs_random": float(by.loc["true_sps_vs_random_generated", "effect"]) if "true_sps_vs_random_generated" in by.index else np.nan,
                "p_vs_random": float(by.loc["true_sps_vs_random_generated", "p_greater"]) if "true_sps_vs_random_generated" in by.index else np.nan,
                "effect_vs_balanced": float(by.loc["true_sps_vs_balanced_generated", "effect"]) if "true_sps_vs_balanced_generated" in by.index else np.nan,
                "p_vs_balanced": float(by.loc["true_sps_vs_balanced_generated", "p_greater"]) if "true_sps_vs_balanced_generated" in by.index else np.nan,
                "effect_vs_shuffled_c": float(by.loc["true_sps_vs_shuffled_c_state_generated", "effect"]) if "true_sps_vs_shuffled_c_state_generated" in by.index else np.nan,
                "p_vs_shuffled_c": float(by.loc["true_sps_vs_shuffled_c_state_generated", "p_greater"]) if "true_sps_vs_shuffled_c_state_generated" in by.index else np.nan,
                "effect_vs_performance": float(by.loc["true_sps_vs_performance_matched_generated", "effect"]) if "true_sps_vs_performance_matched_generated" in by.index else np.nan,
                "p_vs_performance": float(by.loc["true_sps_vs_performance_matched_generated", "p_greater"]) if "true_sps_vs_performance_matched_generated" in by.index else np.nan,
                "effect_vs_fes_shuffle": float(by.loc["true_sps_vs_shuffled_fes_string_generated", "effect"]) if "true_sps_vs_shuffled_fes_string_generated" in by.index else np.nan,
                "p_vs_fes_shuffle": float(by.loc["true_sps_vs_shuffled_fes_string_generated", "p_greater"]) if "true_sps_vs_shuffled_fes_string_generated" in by.index else np.nan,
                "effect_vs_gmr72_shuffle": float(by.loc["true_sps_vs_shuffled_gmr72_phase_generated", "effect"]) if "true_sps_vs_shuffled_gmr72_phase_generated" in by.index else np.nan,
                "p_vs_gmr72_shuffle": float(by.loc["true_sps_vs_shuffled_gmr72_phase_generated", "p_greater"]) if "true_sps_vs_shuffled_gmr72_phase_generated" in by.index else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["strong_success", "minimum_success", "mean_true_sps", "effect_vs_random"],
        ascending=[False, False, False, False],
    )


def cluster_summary(scores: pd.DataFrame) -> pd.DataFrame:
    true = scores[scores["control_kind"].eq("true_generated")].copy()
    if true.empty:
        return pd.DataFrame()
    weight_cols = [f"w_{op}" for op in OPERATORS]
    rows = []
    for (mode, endpoint, nearest), sub in true.groupby(["mode", "endpoint", "nearest_primitive_operator"], sort=False):
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "cluster_nearest_primitive": nearest,
                "n": int(len(sub)),
                "mean_subject_position_score": float(np.nanmean(sub["subject_position_score"])),
                "mean_novelty": float(np.nanmean(sub["novelty_cosine_distance"])),
                "mean_distance_to_selected": float(np.nanmean(sub["distance_to_best_selected_cosine"])),
                "mean_coherence": float(np.nanmean(sub["within_state_coherence"])),
                **{f"mean_w_{op}": float(np.nanmean(sub[f"w_{op}"])) for op in OPERATORS},
            }
        )
    return pd.DataFrame(rows).sort_values(["mode", "endpoint", "n"], ascending=[True, True, False])


def write_report(path: Path, condition_results: pd.DataFrame, comparisons: pd.DataFrame, clusters: pd.DataFrame, args: argparse.Namespace) -> None:
    best = condition_results.iloc[0] if len(condition_results) else None
    best_label = f"{best['mode']} / {best['endpoint']}" if best is not None else "none"
    lines = [
        "# Private B6N Subject-Position Genesis Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Question: Does C/FES-GMR72 generate distinct, coherent, state-specific operator standpoints rather than merely optimizing performance?",
        "",
        "Interpretation boundary: this is not AGI, not conscious experience, not qualia generation, and not recursive self-improvement.",
        "",
        "## Operational Subject-Position Metrics",
        "",
        "- novelty: cosine distance from the nearest primitive operator.",
        "- coherence: cross-fold within-state cosine similarity of generated operator weights.",
        "- state specificity: between-state distance of generated operator weights from the global generated profile.",
        "- non-collapse: inverse of collapse into a near-one-hot primitive operator.",
        "- subject_position_score: normalized additive score across novelty, coherence, state specificity, non-collapse, and distance from best selected.",
        "",
        "## Main Findings",
        "",
        f"- strongest subject-position condition: {best_label}",
        f"- minimum-success conditions: {int(condition_results['minimum_success'].sum())} / {len(condition_results)}",
        f"- strong-success conditions: {int(condition_results['strong_success'].sum())} / {len(condition_results)}",
        "",
        "## Condition Results",
        "",
        condition_results.to_csv(index=False).strip(),
        "",
        "## Control Comparisons",
        "",
        comparisons.to_csv(index=False).strip(),
        "",
        "## Subject-Position Clusters",
        "",
        clusters.to_csv(index=False).strip() if not clusters.empty else "none",
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
    table.to_csv(outdir / "private_B6N_subject_position_state_table.csv", index=False)
    all_scores = []
    all_policies = []
    for mode in MODES:
        for endpoint in ENDPOINTS:
            scores, policies = build_subject_positions(table, b6l, mode, endpoint, args)
            if scores.empty:
                continue
            all_scores.append(scores)
            all_policies.append(policies)
    scores = pd.concat(all_scores, ignore_index=True) if all_scores else pd.DataFrame()
    policies = pd.concat(all_policies, ignore_index=True) if all_policies else pd.DataFrame()
    comparisons = compare_controls(scores, args) if not scores.empty else pd.DataFrame()
    condition_results = summarize_conditions(scores, comparisons) if not scores.empty else pd.DataFrame()
    clusters = cluster_summary(scores) if not scores.empty else pd.DataFrame()

    scores.to_csv(outdir / "private_B6N_operator_novelty_coherence.csv", index=False)
    condition_results.to_csv(outdir / "private_B6N_subject_position_scores.csv", index=False)
    clusters.to_csv(outdir / "private_B6N_subject_position_clusters.csv", index=False)
    comparisons.to_csv(outdir / "private_B6N_control_comparison.csv", index=False)
    policies.to_csv(outdir / "private_B6N_generated_operator_policies.csv", index=False)
    write_report(outdir / "private_B6N_subject_position_summary.md", condition_results, comparisons, clusters, args)
    print("\nPrivate B6N subject-position genesis outputs")
    print(outdir)
    print(condition_results.to_string(index=False, max_rows=80))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6n_subject_position_genesis")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=61320)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
