#!/usr/bin/env python3
"""Private B6O-R Intersection Access Robustness Audit.

Private only. Do not publish, stage, commit, or push.

Question:
    Is the B6O intersection-access operation robust across access direction,
    endpoint, C/FES/GMR72 generation mode, label holdout, and operator-pool
    holdout, while remaining stronger than objectification?

Boundary:
    This does not score subjectivity as an object. The object arm is included
    only as a contrast arm. The tested claim is operational access by
    intersection.
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

OPERATOR_POOLS = {
    "full": OPERATORS,
    "core_5": [op for op in OPERATORS if op not in {"O6_phase_only", "O7_suppress_event"}],
    "no_phase_only": [op for op in OPERATORS if op != "O6_phase_only"],
    "no_suppress": [op for op in OPERATORS if op != "O7_suppress_event"],
}

MODES = [
    "combined_c_fes_gmr72",
    "gmr72_phase_conditioned",
    "fes_string_conditioned",
    "linear_c_state",
]

ENDPOINTS = ["z_reward", "rank_reward", "gmr72_bridge_composite"]

CONTROL_KINDS = [
    "random",
    "balanced",
    "performance_matched",
    "shuffled_c",
    "phase_rotated",
]

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
    rng = np.random.default_rng(seed + 2110)
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


def pool_weights(weights: np.ndarray, pool_name: str) -> np.ndarray:
    allowed = set(OPERATOR_POOLS[pool_name])
    mask = np.asarray([1.0 if op in allowed else 0.0 for op in OPERATORS], dtype=float)
    return normalize_weights(normalize_weights(weights) * mask)


def rotate_weights(weights: np.ndarray, shift: int = 1) -> np.ndarray:
    out = np.asarray(weights, dtype=float).copy()
    out[:5] = np.roll(out[:5], shift)
    return normalize_weights(out)


def masked_weights(weights: np.ndarray, direction: str, pool_name: str) -> np.ndarray:
    mask_dict = A_TO_B_MASK if direction == "A_to_C_to_B" else B_TO_A_MASK
    mask = np.asarray([mask_dict[op] for op in OPERATORS], dtype=float)
    return pool_weights(normalize_weights(weights) * mask, pool_name)


def one_hot(op: str) -> np.ndarray:
    out = np.zeros(len(OPERATORS), dtype=float)
    out[OPERATORS.index(op)] = 1.0
    return out


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-12:
        return np.nan
    return float(np.dot(a, b) / denom)


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    sim = cosine_similarity(a, b)
    return float(1.0 - sim) if np.isfinite(sim) else np.nan


def nearest_primitive(weights: np.ndarray, pool_name: str) -> tuple[str, float]:
    distances = [(op, cosine_distance(weights, one_hot(op))) for op in OPERATOR_POOLS[pool_name]]
    op, dist = min(distances, key=lambda item: item[1])
    return op, float(dist)


def build_table(args: argparse.Namespace):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6l = load_module("private_b6l_for_b6or", B6L_SCRIPT)
    table = b6l.build_table(args)
    return b6l, table


def weighted_reward(row: pd.Series, b6l, weights: np.ndarray, endpoint: str) -> float:
    return b6l.row_reward(row, normalize_weights(weights), endpoint)


def primitive_reward(row: pd.Series, b6l, op: str, endpoint: str) -> float:
    col = b6l.operator_reward_columns(endpoint)[op]
    return float(pd.to_numeric(row.get(col, np.nan), errors="coerce"))


def train_generators(train: pd.DataFrame, b6l, mode: str, endpoint: str, args: argparse.Namespace, rng: np.random.Generator):
    mapping, global_weights, selected_mapping, global_best, policies = b6l.train_weights(
        train, mode, endpoint, args.min_state_events, args.temperature
    )
    mapping = {state: normalize_weights(weights) for state, weights in mapping.items()}
    shuffled = list(mapping.values())
    rng.shuffle(shuffled)
    shuffled_mapping = {state: shuffled[i % len(shuffled)] for i, state in enumerate(mapping.keys())} if shuffled else {}
    return {
        "true": mapping,
        "global": normalize_weights(global_weights),
        "shuffled": shuffled_mapping,
        "performance": normalize_weights(b6l.performance_matched_weights(train, endpoint)),
        "selected_mapping": selected_mapping,
        "global_best": global_best,
        "policies": policies,
    }


def weights_for(kind: str, state: str, info: dict, rng: np.random.Generator, pool_name: str) -> np.ndarray:
    if kind == "true":
        weights = info["true"].get(state, info["global"])
    elif kind == "random":
        weights = rng.dirichlet(np.ones(len(OPERATORS)))
    elif kind == "balanced":
        weights = np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    elif kind == "performance_matched":
        weights = info["performance"]
    elif kind == "shuffled_c":
        weights = info["shuffled"].get(state, info["global"])
    elif kind == "phase_rotated":
        weights = rotate_weights(info["true"].get(state, info["global"]), shift=1)
    else:
        raise ValueError(f"unknown kind {kind}")
    return pool_weights(weights, pool_name)


def baseline_readouts(row: pd.Series, b6l, endpoint: str, pool_name: str) -> dict[str, float]:
    a_alone = primitive_reward(row, b6l, "O3_A_C_boundary", endpoint)
    b_alone = primitive_reward(row, b6l, "O4_B_C_boundary", endpoint)
    neutral = weighted_reward(row, b6l, pool_weights(np.ones(len(OPERATORS)), pool_name), endpoint)
    full_tfc = primitive_reward(row, b6l, "O5_full_TFC", endpoint)
    return {
        "A_alone": a_alone,
        "B_alone": b_alone,
        "neutral_external": neutral,
        "full_tfc_external": full_tfc,
        "baseline_max": float(np.nanmax([a_alone, b_alone, neutral, full_tfc])),
    }


def add_object_scores(object_df: pd.DataFrame) -> pd.DataFrame:
    out = object_df.copy()
    weight_cols = [f"w_{op}" for op in OPERATORS]
    coherence_rows = []
    specificity_rows = []
    for keys, sub in out.groupby(["mode", "endpoint", "operator_pool", "arm_kind", "state_label"], sort=False):
        ws = sub[weight_cols].to_numpy(dtype=float)
        sims = []
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                sims.append(cosine_similarity(normalize_weights(ws[i]), normalize_weights(ws[j])))
        coherence_rows.append((*keys, float(np.nanmean(sims)) if sims else np.nan))
    coherence = pd.DataFrame(coherence_rows, columns=["mode", "endpoint", "operator_pool", "arm_kind", "state_label", "coherence"])
    out = out.merge(coherence, on=["mode", "endpoint", "operator_pool", "arm_kind", "state_label"], how="left")
    for keys, sub in out.groupby(["mode", "endpoint", "operator_pool", "arm_kind"], sort=False):
        state_means = sub.groupby("state_label")[weight_cols].mean()
        global_mean = normalize_weights(sub[weight_cols].mean().to_numpy(dtype=float))
        distances = [
            float(np.linalg.norm(normalize_weights(row.to_numpy(dtype=float)) - global_mean))
            for _, row in state_means.iterrows()
        ]
        specificity_rows.append((*keys, float(np.nanmean(distances)) if distances else np.nan))
    specificity = pd.DataFrame(specificity_rows, columns=["mode", "endpoint", "operator_pool", "arm_kind", "state_specificity"])
    out = out.merge(specificity, on=["mode", "endpoint", "operator_pool", "arm_kind"], how="left")
    components = ["novelty", "distance_to_selected", "entropy", "non_collapse", "coherence", "state_specificity"]
    for col in components:
        out[f"z_{col}"] = np.nan
    for _, idx in out.groupby(["mode", "endpoint", "operator_pool"]).groups.items():
        idx = list(idx)
        for col in components:
            out.loc[idx, f"z_{col}"] = zscore(out.loc[idx, col].to_numpy(dtype=float))
    out["object_score"] = sum(out[f"z_{col}"] for col in components)
    return out


def build_arms(table: pd.DataFrame, b6l, mode: str, endpoint: str, pool_name: str, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 2120)
    data = table.copy()
    data["b6or_state_label"] = b6l.state_labels(data, mode)
    folds = make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    object_rows = []
    intersection_rows = []
    policy_rows = []
    weight_cols = [f"w_{op}" for op in OPERATORS]

    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy().reset_index(drop=True)
        info = train_generators(train, b6l, mode, endpoint, args, rng)
        policies = info["policies"].copy()
        if not policies.empty:
            policies["fold"] = fold_index
            policies["mode"] = mode
            policies["endpoint"] = endpoint
            policies["operator_pool"] = pool_name
            policy_rows.extend(policies.to_dict("records"))

        for state in sorted(set(test["b6or_state_label"].astype(str))):
            selected_op = info["selected_mapping"].get(state, info["global_best"])
            if selected_op not in OPERATOR_POOLS[pool_name]:
                selected_op = max(
                    OPERATOR_POOLS[pool_name],
                    key=lambda op: float(pd.to_numeric(train[b6l.operator_reward_columns(endpoint)[op]], errors="coerce").mean()),
                )
            for kind in ["true", *CONTROL_KINDS]:
                weights = weights_for(kind, state, info, rng, pool_name)
                near_op, novelty = nearest_primitive(weights, pool_name)
                distance_selected = cosine_distance(weights, one_hot(selected_op))
                positive = weights[weights > 0]
                entropy = float(-np.sum(positive * np.log(positive)) / np.log(len(OPERATOR_POOLS[pool_name]))) if len(positive) else np.nan
                object_rows.append(
                    {
                        "mode": mode,
                        "endpoint": endpoint,
                        "operator_pool": pool_name,
                        "fold": fold_index,
                        "state_label": state,
                        "arm_kind": kind,
                        "selected_operator": selected_op,
                        "nearest_primitive": near_op,
                        "novelty": novelty,
                        "distance_to_selected": distance_selected,
                        "entropy": entropy,
                        "non_collapse": float(np.max(weights) < 0.85),
                        **{weight_cols[i]: float(weights[i]) for i in range(len(OPERATORS))},
                    }
                )

        for _, row in test.iterrows():
            state = str(row["b6or_state_label"])
            base = baseline_readouts(row, b6l, endpoint, pool_name)
            for direction in ["A_to_C_to_B", "B_to_C_to_A"]:
                for kind in ["true", *CONTROL_KINDS]:
                    weights = masked_weights(weights_for(kind, state, info, rng, pool_name), direction, pool_name)
                    access = weighted_reward(row, b6l, weights, endpoint)
                    intersection_rows.append(
                        {
                            "mode": mode,
                            "endpoint": endpoint,
                            "operator_pool": pool_name,
                            "fold": fold_index,
                            "label": row["label"],
                            "idx_in_session": row["idx_in_session"],
                            "state_label": state,
                            "direction": direction,
                            "arm_kind": kind,
                            "access_readout": access,
                            "baseline_max": base["baseline_max"],
                            "intersection_access_effect": access - base["baseline_max"] if np.isfinite(access) and np.isfinite(base["baseline_max"]) else np.nan,
                            "A_alone": base["A_alone"],
                            "B_alone": base["B_alone"],
                            "neutral_external": base["neutral_external"],
                            "full_tfc_external": base["full_tfc_external"],
                            **{weight_cols[i]: float(weights[i]) for i in range(len(OPERATORS))},
                        }
                    )
    object_df = pd.DataFrame(object_rows)
    if not object_df.empty:
        object_df = add_object_scores(object_df)
    return object_df, pd.DataFrame(intersection_rows), pd.DataFrame(policy_rows)


def compare_object(object_df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 2130)
    rows = []
    for keys, sub in object_df.groupby(["mode", "endpoint", "operator_pool"], sort=False):
        true = sub[sub["arm_kind"].eq("true")].set_index(["fold", "state_label"])
        for control in CONTROL_KINDS:
            comp = sub[sub["arm_kind"].eq(control)].set_index(["fold", "state_label"])
            joined = true[["object_score"]].join(comp[["object_score"]], how="inner", lsuffix="_true", rsuffix="_control")
            diff = joined["object_score_true"].to_numpy(dtype=float) - joined["object_score_control"].to_numpy(dtype=float)
            effect, p = signflip_p(diff, rng, args.n_perm)
            rows.append(
                {
                    "mode": keys[0],
                    "endpoint": keys[1],
                    "operator_pool": keys[2],
                    "arm": "object",
                    "comparison": f"true_vs_{control}",
                    "mean_true": float(np.nanmean(joined["object_score_true"])),
                    "mean_control": float(np.nanmean(joined["object_score_control"])),
                    "effect": effect,
                    "p_greater": p,
                    "n_pairs": int(np.isfinite(diff).sum()),
                }
            )
    return pd.DataFrame(rows)


def compare_intersection(intersection_df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 2140)
    rows = []
    for keys, sub in intersection_df.groupby(["mode", "endpoint", "operator_pool", "direction"], sort=False):
        true = sub[sub["arm_kind"].eq("true")].set_index(["fold", "label", "idx_in_session", "state_label"])
        for control in CONTROL_KINDS:
            comp = sub[sub["arm_kind"].eq(control)].set_index(["fold", "label", "idx_in_session", "state_label"])
            joined = true[["intersection_access_effect"]].join(
                comp[["intersection_access_effect"]],
                how="inner",
                lsuffix="_true",
                rsuffix="_control",
            )
            diff = joined["intersection_access_effect_true"].to_numpy(dtype=float) - joined["intersection_access_effect_control"].to_numpy(dtype=float)
            effect, p = signflip_p(diff, rng, args.n_perm)
            rows.append(
                {
                    "mode": keys[0],
                    "endpoint": keys[1],
                    "operator_pool": keys[2],
                    "direction": keys[3],
                    "arm": "intersection",
                    "comparison": f"true_vs_{control}",
                    "mean_true": float(np.nanmean(joined["intersection_access_effect_true"])),
                    "mean_control": float(np.nanmean(joined["intersection_access_effect_control"])),
                    "effect": effect,
                    "p_greater": p,
                    "n_pairs": int(np.isfinite(diff).sum()),
                }
            )
    return pd.DataFrame(rows)


def pass_map(comp: pd.DataFrame) -> dict[str, bool]:
    out = {}
    for _, row in comp.iterrows():
        out[str(row["comparison"]).replace("true_vs_", "")] = bool(row["effect"] > 0 and row["p_greater"] <= 0.05)
    return out


def summarize(object_comp: pd.DataFrame, intersection_comp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    object_groups = {
        (mode, endpoint, pool): sub
        for (mode, endpoint, pool), sub in object_comp.groupby(["mode", "endpoint", "operator_pool"], sort=False)
    }
    for keys, inter in intersection_comp.groupby(["mode", "endpoint", "operator_pool", "direction"], sort=False):
        mode, endpoint, pool, direction = keys
        obj = object_groups.get((mode, endpoint, pool), pd.DataFrame())
        inter_pass = pass_map(inter)
        obj_pass = pass_map(obj) if not obj.empty else {}
        core_controls = ["balanced", "shuffled_c", "phase_rotated"]
        stress_controls = ["random", "performance_matched"]
        core_count = int(sum(inter_pass.get(c, False) for c in core_controls))
        stress_count = int(sum(inter_pass.get(c, False) for c in stress_controls))
        object_count = int(sum(obj_pass.get(c, False) for c in CONTROL_KINDS))
        robust = bool(core_count == len(core_controls) and object_count <= 2)
        strong = bool(robust and stress_count >= 1)
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "operator_pool": pool,
                "direction": direction,
                "robust_success": robust,
                "strong_success": strong,
                "intersection_core_pass_count": core_count,
                "intersection_stress_pass_count": stress_count,
                "object_pass_count": object_count,
                "objectification_gap": core_count + stress_count - object_count,
                "pass_balanced": inter_pass.get("balanced", False),
                "pass_shuffled_c": inter_pass.get("shuffled_c", False),
                "pass_phase_rotated": inter_pass.get("phase_rotated", False),
                "pass_random": inter_pass.get("random", False),
                "pass_performance": inter_pass.get("performance_matched", False),
                "mean_intersection_effect": float(np.nanmean(inter["effect"])),
                "mean_true_intersection": float(np.nanmean(inter["mean_true"])),
                "mean_object_effect": float(np.nanmean(obj["effect"])) if not obj.empty else np.nan,
                "mean_true_object": float(np.nanmean(obj["mean_true"])) if not obj.empty else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["strong_success", "robust_success", "intersection_core_pass_count", "intersection_stress_pass_count", "objectification_gap", "mean_intersection_effect"],
        ascending=[False, False, False, False, False, False],
    )


def aggregate_results(results: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    by_mode = results.groupby("mode", as_index=False).agg(
        conditions=("mode", "size"),
        robust_successes=("robust_success", "sum"),
        strong_successes=("strong_success", "sum"),
        mean_core_pass=("intersection_core_pass_count", "mean"),
        mean_object_pass=("object_pass_count", "mean"),
    )
    by_pool = results.groupby("operator_pool", as_index=False).agg(
        conditions=("operator_pool", "size"),
        robust_successes=("robust_success", "sum"),
        strong_successes=("strong_success", "sum"),
        mean_core_pass=("intersection_core_pass_count", "mean"),
        mean_object_pass=("object_pass_count", "mean"),
    )
    by_direction = results.groupby("direction", as_index=False).agg(
        conditions=("direction", "size"),
        robust_successes=("robust_success", "sum"),
        strong_successes=("strong_success", "sum"),
        mean_core_pass=("intersection_core_pass_count", "mean"),
        mean_object_pass=("object_pass_count", "mean"),
    )
    return by_mode, by_pool, by_direction


def write_report(path: Path, results: pd.DataFrame, object_comp: pd.DataFrame, intersection_comp: pd.DataFrame, by_mode: pd.DataFrame, by_pool: pd.DataFrame, by_direction: pd.DataFrame, args: argparse.Namespace) -> None:
    best = results.iloc[0] if len(results) else None
    best_label = f"{best['mode']} / {best['endpoint']} / {best['operator_pool']} / {best['direction']}" if best is not None else "none"
    lines = [
        "# Private B6O-R Intersection Access Robustness Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Question: Is the B6O intersection-access operation robust across directions, endpoints, generation modes, label folds, and operator-pool holdouts?",
        "",
        "Interpretation boundary: subjectivity is not scored as an object. The object arm is a contrast arm only.",
        "",
        "## Main Findings",
        "",
        f"- strongest condition: {best_label}",
        f"- robust-success conditions: {int(results['robust_success'].sum())} / {len(results)}",
        f"- strong-success conditions: {int(results['strong_success'].sum())} / {len(results)}",
        "",
        "## Robustness By Mode",
        "",
        by_mode.to_csv(index=False).strip(),
        "",
        "## Robustness By Operator Pool",
        "",
        by_pool.to_csv(index=False).strip(),
        "",
        "## Robustness By Direction",
        "",
        by_direction.to_csv(index=False).strip(),
        "",
        "## Condition Results",
        "",
        results.to_csv(index=False).strip(),
        "",
        "## Object Arm Comparisons",
        "",
        object_comp.to_csv(index=False).strip(),
        "",
        "## Intersection Arm Comparisons",
        "",
        intersection_comp.to_csv(index=False).strip(),
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
    table.to_csv(outdir / "private_B6OR_state_table.csv", index=False)
    object_frames = []
    intersection_frames = []
    policy_frames = []
    for mode in MODES:
        for endpoint in ENDPOINTS:
            for pool_name in OPERATOR_POOLS:
                obj, inter, policies = build_arms(table, b6l, mode, endpoint, pool_name, args)
                if not obj.empty:
                    object_frames.append(obj)
                if not inter.empty:
                    intersection_frames.append(inter)
                if not policies.empty:
                    policy_frames.append(policies)
    object_df = pd.concat(object_frames, ignore_index=True) if object_frames else pd.DataFrame()
    intersection_df = pd.concat(intersection_frames, ignore_index=True) if intersection_frames else pd.DataFrame()
    policies = pd.concat(policy_frames, ignore_index=True) if policy_frames else pd.DataFrame()
    object_comp = compare_object(object_df, args) if not object_df.empty else pd.DataFrame()
    intersection_comp = compare_intersection(intersection_df, args) if not intersection_df.empty else pd.DataFrame()
    results = summarize(object_comp, intersection_comp) if not object_comp.empty and not intersection_comp.empty else pd.DataFrame()
    by_mode, by_pool, by_direction = aggregate_results(results) if not results.empty else (pd.DataFrame(), pd.DataFrame(), pd.DataFrame())

    object_df.to_csv(outdir / "private_B6OR_object_arm_scores.csv", index=False)
    intersection_df.to_csv(outdir / "private_B6OR_intersection_arm_effects.csv", index=False)
    object_comp.to_csv(outdir / "private_B6OR_object_control_comparison.csv", index=False)
    intersection_comp.to_csv(outdir / "private_B6OR_intersection_control_comparison.csv", index=False)
    results.to_csv(outdir / "private_B6OR_intersection_access_robustness_results.csv", index=False)
    by_mode.to_csv(outdir / "private_B6OR_robustness_by_mode.csv", index=False)
    by_pool.to_csv(outdir / "private_B6OR_robustness_by_operator_pool.csv", index=False)
    by_direction.to_csv(outdir / "private_B6OR_robustness_by_direction.csv", index=False)
    policies.to_csv(outdir / "private_B6OR_generated_policies.csv", index=False)
    write_report(
        outdir / "private_B6OR_intersection_access_robustness_summary.md",
        results,
        object_comp,
        intersection_comp,
        by_mode,
        by_pool,
        by_direction,
        args,
    )
    print("\nPrivate B6O-R intersection access robustness outputs")
    print(outdir)
    print(results.to_string(index=False, max_rows=120))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6or_intersection_access_robustness")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=62010)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
