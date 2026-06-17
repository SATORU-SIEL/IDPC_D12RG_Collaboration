#!/usr/bin/env python3
"""Private B6O-S GMR72 Bridge Mechanism Audit.

Private only. Do not publish, stage, commit, or push.

Question:
    Does the B6O-R intersection-access effect depend specifically on the
    true 72-degree forward GMR bridge, rather than reversed, half-step,
    quadrature, skip, random-phase, or no-bridge variants?

Boundary:
    C is kept fixed. FES is not added as a state label. FES/GMR is used only
    inside the bridge endpoint construction.
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

OPERATOR_HORIZON = {
    "O1_lag0_AB": 1,
    "O2_lag5_AB": 5,
    "O3_A_C_boundary": 5,
    "O4_B_C_boundary": 5,
    "O5_full_TFC": 5,
    "O6_phase_only": 1,
    "O7_suppress_event": 5,
}

OPERATOR_POOLS = {
    "full": OPERATORS,
    "core_5": [op for op in OPERATORS if op not in {"O6_phase_only", "O7_suppress_event"}],
    "no_phase_only": [op for op in OPERATORS if op != "O6_phase_only"],
    "no_suppress": [op for op in OPERATORS if op != "O7_suppress_event"],
}

BRIDGE_VARIANTS = [
    "true72_forward",
    "reversed72",
    "half36",
    "quadrature90",
    "skip144",
    "random_phase",
    "no_bridge",
]

BRIDGE_TARGET_STEPS = {
    "true72_forward": 1.0,
    "reversed72": -1.0,
    "half36": 0.5,
    "quadrature90": 1.25,
    "skip144": 2.0,
}

CONTROL_KINDS = ["balanced", "shuffled_c", "phase_rotated", "random", "performance_matched"]

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


def zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = np.full(len(x), np.nan, dtype=float)
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
    rng = np.random.default_rng(seed + 2210)
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
        return np.ones(len(weights), dtype=float) / max(len(weights), 1)
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


def bridge_resonance(step: float, variant: str, rng: np.random.Generator | None = None) -> float:
    if variant == "no_bridge":
        return np.nan
    if not np.isfinite(step):
        return np.nan
    if variant == "random_phase":
        target = float(rng.uniform(0.0, 5.0)) if rng is not None else 0.0
    else:
        target = BRIDGE_TARGET_STEPS[variant]
    return float(np.cos(2.0 * np.pi * ((step - target) % 5.0) / 5.0))


def build_base_table(args: argparse.Namespace) -> tuple[object, pd.DataFrame]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6k = load_module("private_b6k_for_b6os", B6K_SCRIPT)
    table = b6k.build_base_table(args)
    table = add_bridge_variant_endpoints(table, args.seed)
    return b6k, table


def add_bridge_variant_endpoints(table: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 2220)
    out = table.sort_values(["label", "idx_in_session"]).reset_index(drop=True).copy()
    for variant in BRIDGE_VARIANTS:
        for op in OPERATORS:
            out[f"{variant}_resonance_{op}_raw"] = np.nan
            out[f"{variant}_policy_readiness_{op}_raw"] = np.nan

    for _, sub in out.groupby("label", sort=False):
        idxs = sub.index.to_numpy()
        times = pd.to_numeric(sub["idx_in_session"], errors="coerce").to_numpy(dtype=float)
        for local_i, row_index in enumerate(idxs):
            current_t = times[local_i]
            current_fes = out.loc[row_index, "fes_idx"]
            for op in OPERATORS:
                if op == "O7_suppress_event":
                    for variant in BRIDGE_VARIANTS:
                        out.loc[row_index, f"{variant}_resonance_{op}_raw"] = -1.0 if variant != "no_bridge" else np.nan
                        out.loc[row_index, f"{variant}_policy_readiness_{op}_raw"] = -0.25 if variant != "no_bridge" else 0.0
                    continue
                horizon = OPERATOR_HORIZON[op]
                candidates = np.where(times >= current_t + horizon)[0]
                candidates = candidates[candidates > local_i]
                if len(candidates) == 0:
                    continue
                next_index = idxs[int(candidates[0])]
                future_fes = out.loc[next_index, "fes_idx"]
                step = (future_fes - current_fes) % 5.0 if np.isfinite(current_fes) and np.isfinite(future_fes) else np.nan
                base_terms = [
                    out.loc[next_index, "oracle_reward_z"],
                    out.loc[next_index, "operator_margin_raw"],
                    out.loc[next_index, "gmr_c_readiness_raw"],
                ]
                for variant in BRIDGE_VARIANTS:
                    resonance = bridge_resonance(step, variant, rng)
                    out.loc[row_index, f"{variant}_resonance_{op}_raw"] = resonance
                    if variant == "no_bridge":
                        out.loc[row_index, f"{variant}_policy_readiness_{op}_raw"] = np.nanmean(base_terms)
                    else:
                        out.loc[row_index, f"{variant}_policy_readiness_{op}_raw"] = np.nanmean([*base_terms, resonance])

    for variant in BRIDGE_VARIANTS:
        for op in OPERATORS:
            if variant == "no_bridge":
                out[f"{variant}_bridge_{op}"] = pd.to_numeric(out[f"{op}_z"], errors="coerce")
                continue
            out[f"{variant}_resonance_{op}"] = zscore(out[f"{variant}_resonance_{op}_raw"].to_numpy(dtype=float))
            out[f"{variant}_policy_readiness_{op}"] = zscore(out[f"{variant}_policy_readiness_{op}_raw"].to_numpy(dtype=float))
            out[f"{variant}_bridge_{op}"] = np.nanmean(
                np.vstack(
                    [
                        pd.to_numeric(out[f"{op}_z"], errors="coerce").to_numpy(dtype=float),
                        out[f"{variant}_policy_readiness_{op}"].to_numpy(dtype=float),
                        out[f"{variant}_resonance_{op}"].to_numpy(dtype=float),
                    ]
                ),
                axis=0,
            )
    return out


def set_c_state(table: pd.DataFrame) -> pd.DataFrame:
    out = table.copy()
    out["state_label"] = (
        "side=" + out["boundary_side"].astype(str)
        + "|tfc=" + out["tfc_bin"].astype(str)
        + "|phase=" + out["phase_quadrant"].astype(str)
    )
    return out


def reward(row: pd.Series, op: str, bridge_variant: str) -> float:
    return float(pd.to_numeric(row.get(f"{bridge_variant}_bridge_{op}", np.nan), errors="coerce"))


def weighted_reward(row: pd.Series, weights: np.ndarray, bridge_variant: str) -> float:
    vals = np.asarray([reward(row, op, bridge_variant) for op in OPERATORS], dtype=float)
    mask = np.isfinite(vals) & np.isfinite(weights)
    if not mask.any():
        return np.nan
    w = normalize_weights(np.asarray(weights, dtype=float)[mask])
    return float(np.nansum(vals[mask] * w))


def train_weights(train: pd.DataFrame, bridge_variant: str, min_state_events: int, temperature: float) -> tuple[dict[str, np.ndarray], np.ndarray, pd.DataFrame]:
    means = np.asarray([pd.to_numeric(train[f"{bridge_variant}_bridge_{op}"], errors="coerce").mean() for op in OPERATORS], dtype=float)
    global_weights = softmax(means, temperature)
    mapping = {}
    rows = []
    for state, sub in train.groupby("state_label", sort=False):
        if len(sub) < min_state_events:
            continue
        state_means = np.asarray([pd.to_numeric(sub[f"{bridge_variant}_bridge_{op}"], errors="coerce").mean() for op in OPERATORS], dtype=float)
        weights = softmax(state_means, temperature)
        mapping[str(state)] = weights
        row = {
            "bridge_variant": bridge_variant,
            "state_label": str(state),
            "n_train_events": int(len(sub)),
            "selected_operator": OPERATORS[int(np.nanargmax(state_means))],
            "generated_train_reward": float(np.nansum(weights * state_means)),
        }
        row.update({f"w_{op}": float(weights[i]) for i, op in enumerate(OPERATORS)})
        row.update({f"mean_{op}": float(state_means[i]) for i, op in enumerate(OPERATORS)})
        rows.append(row)
    return mapping, global_weights, pd.DataFrame(rows)


def softmax(scores: np.ndarray, temperature: float) -> np.ndarray:
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


def performance_weights(train: pd.DataFrame, bridge_variant: str) -> np.ndarray:
    means = np.asarray([pd.to_numeric(train[f"{bridge_variant}_bridge_{op}"], errors="coerce").mean() for op in OPERATORS], dtype=float)
    ranks = pd.Series(means).rank(pct=True).to_numpy(dtype=float)
    if not np.isfinite(ranks).any() or np.nansum(ranks) <= 0:
        return np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    ranks = np.nan_to_num(ranks, nan=0.0)
    return normalize_weights(ranks)


def weights_for(kind: str, state: str, info: dict, rng: np.random.Generator, pool_name: str) -> np.ndarray:
    if kind == "true":
        weights = info["mapping"].get(state, info["global"])
    elif kind == "balanced":
        weights = np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    elif kind == "shuffled_c":
        weights = info["shuffled"].get(state, info["global"])
    elif kind == "phase_rotated":
        weights = rotate_weights(info["mapping"].get(state, info["global"]), shift=1)
    elif kind == "random":
        weights = rng.dirichlet(np.ones(len(OPERATORS)))
    elif kind == "performance_matched":
        weights = info["performance"]
    else:
        raise ValueError(f"unknown kind {kind}")
    return pool_weights(weights, pool_name)


def baseline(row: pd.Series, pool_name: str, bridge_variant: str) -> dict[str, float]:
    a = reward(row, "O3_A_C_boundary", bridge_variant)
    b = reward(row, "O4_B_C_boundary", bridge_variant)
    neutral = weighted_reward(row, pool_weights(np.ones(len(OPERATORS)), pool_name), bridge_variant)
    full = reward(row, "O5_full_TFC", bridge_variant)
    return {
        "A_alone": a,
        "B_alone": b,
        "neutral": neutral,
        "full_tfc": full,
        "baseline_max": float(np.nanmax([a, b, neutral, full])),
    }


def run_bridge_access(table: pd.DataFrame, bridge_variant: str, pool_name: str, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 2230)
    data = set_c_state(table)
    folds = make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    policy_rows = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy().reset_index(drop=True)
        mapping, global_weights, policies = train_weights(train, bridge_variant, args.min_state_events, args.temperature)
        shuffled_values = list(mapping.values())
        rng.shuffle(shuffled_values)
        shuffled = {state: shuffled_values[i % len(shuffled_values)] for i, state in enumerate(mapping.keys())} if shuffled_values else {}
        info = {
            "mapping": {k: normalize_weights(v) for k, v in mapping.items()},
            "global": normalize_weights(global_weights),
            "shuffled": shuffled,
            "performance": performance_weights(train, bridge_variant),
        }
        if not policies.empty:
            policies["fold"] = fold_index
            policies["operator_pool"] = pool_name
            policy_rows.extend(policies.to_dict("records"))
        for _, row in test.iterrows():
            state = str(row["state_label"])
            for direction in ["A_to_C_to_B", "B_to_C_to_A"]:
                base = baseline(row, pool_name, bridge_variant)
                for kind in ["true", *CONTROL_KINDS]:
                    weights = masked_weights(weights_for(kind, state, info, rng, pool_name), direction, pool_name)
                    access = weighted_reward(row, weights, bridge_variant)
                    rows.append(
                        {
                            "bridge_variant": bridge_variant,
                            "operator_pool": pool_name,
                            "fold": fold_index,
                            "label": row["label"],
                            "idx_in_session": row["idx_in_session"],
                            "state_label": state,
                            "direction": direction,
                            "arm_kind": kind,
                            "access_readout": access,
                            "intersection_access_effect": access - base["baseline_max"] if np.isfinite(access) and np.isfinite(base["baseline_max"]) else np.nan,
                            "baseline_max": base["baseline_max"],
                        }
                    )
    return pd.DataFrame(rows), pd.DataFrame(policy_rows)


def compare_controls(access: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 2240)
    rows = []
    for keys, sub in access.groupby(["bridge_variant", "operator_pool", "direction"], sort=False):
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
                    "bridge_variant": keys[0],
                    "operator_pool": keys[1],
                    "direction": keys[2],
                    "comparison": f"true_vs_{control}",
                    "mean_true": float(np.nanmean(joined["intersection_access_effect_true"])),
                    "mean_control": float(np.nanmean(joined["intersection_access_effect_control"])),
                    "effect": effect,
                    "p_greater": p,
                    "n_pairs": int(np.isfinite(diff).sum()),
                }
            )
    return pd.DataFrame(rows)


def summarize_access(comps: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, sub in comps.groupby(["bridge_variant", "operator_pool", "direction"], sort=False):
        by = sub.set_index("comparison")
        core = ["true_vs_balanced", "true_vs_shuffled_c", "true_vs_phase_rotated"]
        stress = ["true_vs_random", "true_vs_performance_matched"]
        core_count = int(sum(name in by.index and by.loc[name, "effect"] > 0 and by.loc[name, "p_greater"] <= 0.05 for name in core))
        stress_count = int(sum(name in by.index and by.loc[name, "effect"] > 0 and by.loc[name, "p_greater"] <= 0.05 for name in stress))
        rows.append(
            {
                "bridge_variant": keys[0],
                "operator_pool": keys[1],
                "direction": keys[2],
                "robust_access": bool(core_count == 3),
                "strong_access": bool(core_count == 3 and stress_count >= 1),
                "core_pass_count": core_count,
                "stress_pass_count": stress_count,
                "mean_true_intersection": float(np.nanmean(sub["mean_true"])),
                "mean_control_effect": float(np.nanmean(sub["effect"])),
                "effect_vs_balanced": float(by.loc["true_vs_balanced", "effect"]) if "true_vs_balanced" in by.index else np.nan,
                "p_vs_balanced": float(by.loc["true_vs_balanced", "p_greater"]) if "true_vs_balanced" in by.index else np.nan,
                "effect_vs_shuffled_c": float(by.loc["true_vs_shuffled_c", "effect"]) if "true_vs_shuffled_c" in by.index else np.nan,
                "p_vs_shuffled_c": float(by.loc["true_vs_shuffled_c", "p_greater"]) if "true_vs_shuffled_c" in by.index else np.nan,
                "effect_vs_phase_rotated": float(by.loc["true_vs_phase_rotated", "effect"]) if "true_vs_phase_rotated" in by.index else np.nan,
                "p_vs_phase_rotated": float(by.loc["true_vs_phase_rotated", "p_greater"]) if "true_vs_phase_rotated" in by.index else np.nan,
                "effect_vs_random": float(by.loc["true_vs_random", "effect"]) if "true_vs_random" in by.index else np.nan,
                "p_vs_random": float(by.loc["true_vs_random", "p_greater"]) if "true_vs_random" in by.index else np.nan,
                "effect_vs_performance": float(by.loc["true_vs_performance_matched", "effect"]) if "true_vs_performance_matched" in by.index else np.nan,
                "p_vs_performance": float(by.loc["true_vs_performance_matched", "p_greater"]) if "true_vs_performance_matched" in by.index else np.nan,
            }
        )
    return pd.DataFrame(rows)


def compare_bridge_variants(access_summary: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rows = []
    index_cols = ["operator_pool", "direction"]
    true = access_summary[access_summary["bridge_variant"].eq("true72_forward")].set_index(index_cols)
    for variant in [v for v in BRIDGE_VARIANTS if v != "true72_forward"]:
        comp = access_summary[access_summary["bridge_variant"].eq(variant)].set_index(index_cols)
        joined = true[["mean_true_intersection", "core_pass_count", "stress_pass_count"]].join(
            comp[["mean_true_intersection", "core_pass_count", "stress_pass_count"]],
            how="inner",
            lsuffix="_true72",
            rsuffix=f"_{variant}",
        )
        diff = joined["mean_true_intersection_true72"].to_numpy(dtype=float) - joined[f"mean_true_intersection_{variant}"].to_numpy(dtype=float)
        rng = np.random.default_rng(args.seed + 2250 + BRIDGE_VARIANTS.index(variant))
        effect, p = signflip_p(diff, rng, args.n_perm)
        rows.append(
            {
                "comparison": f"true72_forward_vs_{variant}",
                "effect_mean_true_intersection": effect,
                "p_greater": p,
                "n_pairs": int(np.isfinite(diff).sum()),
                "true72_core_pass_total": int(joined["core_pass_count_true72"].sum()),
                "variant_core_pass_total": int(joined[f"core_pass_count_{variant}"].sum()),
                "true72_stress_pass_total": int(joined["stress_pass_count_true72"].sum()),
                "variant_stress_pass_total": int(joined[f"stress_pass_count_{variant}"].sum()),
            }
        )
    return pd.DataFrame(rows)


def aggregate(access_summary: pd.DataFrame) -> pd.DataFrame:
    return access_summary.groupby("bridge_variant", as_index=False).agg(
        conditions=("bridge_variant", "size"),
        robust_accesses=("robust_access", "sum"),
        strong_accesses=("strong_access", "sum"),
        mean_core_pass=("core_pass_count", "mean"),
        mean_stress_pass=("stress_pass_count", "mean"),
        mean_true_intersection=("mean_true_intersection", "mean"),
        mean_control_effect=("mean_control_effect", "mean"),
    ).sort_values(["strong_accesses", "robust_accesses", "mean_true_intersection"], ascending=[False, False, False])


def write_report(path: Path, access_summary: pd.DataFrame, bridge_comp: pd.DataFrame, variant_agg: pd.DataFrame, args: argparse.Namespace) -> None:
    true_rows = access_summary[access_summary["bridge_variant"].eq("true72_forward")]
    lines = [
        "# Private B6O-S GMR72 Bridge Mechanism Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Question: Does B6O-R intersection access specifically depend on true 72-degree forward GMR rotation?",
        "",
        "Boundary: C-state is fixed as side+tfc+phase. FES is not added as a label; it only supplies the bridge phase transition.",
        "",
        "## Main Findings",
        "",
        f"- true72 robust/strong: {int(true_rows['robust_access'].sum())} / {int(true_rows['strong_access'].sum())} of {len(true_rows)}",
        "",
        "## Bridge Variant Aggregate",
        "",
        variant_agg.to_csv(index=False).strip(),
        "",
        "## True72 Direct Comparisons",
        "",
        bridge_comp.to_csv(index=False).strip(),
        "",
        "## Access Summary",
        "",
        access_summary.to_csv(index=False).strip(),
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
    _, table = build_base_table(args)
    table.to_csv(outdir / "private_B6OS_bridge_variant_state_table.csv", index=False)
    access_frames = []
    policy_frames = []
    for variant in BRIDGE_VARIANTS:
        for pool_name in OPERATOR_POOLS:
            access, policies = run_bridge_access(table, variant, pool_name, args)
            if not access.empty:
                access_frames.append(access)
            if not policies.empty:
                policy_frames.append(policies)
    access = pd.concat(access_frames, ignore_index=True) if access_frames else pd.DataFrame()
    policies = pd.concat(policy_frames, ignore_index=True) if policy_frames else pd.DataFrame()
    comps = compare_controls(access, args)
    access_summary = summarize_access(comps)
    bridge_comp = compare_bridge_variants(access_summary, args)
    variant_agg = aggregate(access_summary)

    access.to_csv(outdir / "private_B6OS_bridge_access_events.csv", index=False)
    comps.to_csv(outdir / "private_B6OS_control_comparison.csv", index=False)
    access_summary.to_csv(outdir / "private_B6OS_access_summary.csv", index=False)
    bridge_comp.to_csv(outdir / "private_B6OS_bridge_variant_comparison.csv", index=False)
    variant_agg.to_csv(outdir / "private_B6OS_bridge_variant_aggregate.csv", index=False)
    policies.to_csv(outdir / "private_B6OS_generated_policies.csv", index=False)
    write_report(outdir / "private_B6OS_gmr72_bridge_mechanism_summary.md", access_summary, bridge_comp, variant_agg, args)
    print("\nPrivate B6O-S GMR72 bridge mechanism outputs")
    print(outdir)
    print(variant_agg.to_string(index=False))
    print(bridge_comp.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6os_gmr72_bridge_mechanism")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=62110)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
