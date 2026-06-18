#!/usr/bin/env python3
"""Stage B7.2b side-direction correspondence and factorisation-path audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import test_Stage_B7_1a_ab_history_control_validity as b71a  # noqa: E402
import test_Stage_B7_2_o1o2_control_hierarchy as b72  # noqa: E402


ENDPOINTS = b71a.ENDPOINTS
OPERATORS = b71a.OPERATORS
DIRECTIONS = ["A_to_C_to_B", "B_to_C_to_A"]
CONTROL_LEVELS = [
    "direction_label_only",
    "communication_direction_only",
    "symmetric_midpoint_control",
    "sender_receiver_transfer_control",
    "asymmetric_standpoint_control",
    "standpoint_inverted_control",
    "endpoint_o1o2_reference",
    "endpoint_o1o2_direction_swapped",
    "endpoint_o1o2_asymmetric_standpoint",
    "endpoint_o1o2_standpoint_inverted",
    "standpoint_consistent_split_operator",
    "standpoint_inverted_split_operator",
    "standpoint_operator_side_only",
    "standpoint_wrong_operator_side_only",
    "standpoint_consistent_operator_contrast",
    "standpoint_inverted_operator_contrast",
    "standpoint_contrast_with_side_polarity",
    "standpoint_inverted_contrast_with_side_polarity",
    "mismatch_train_consistent_test_inverted",
    "mismatch_train_endpoint_test_direction_swapped",
    "fixed_b6p_direction_mask",
    "fixed_b6p_swapped_mask",
    "fixed_receiver_pair_mask",
    "fixed_giver_pair_mask",
    "fixed_ab_receiver_only",
    "fixed_c_receiver_boundary_only",
    "closure_scalar_only",
    "closure_2ode_local",
    "directed_transport_closure_control",
    "factorisation_3x8",
    "factorisation_2x2x6",
    "factorisation_path_consistent",
    "factorisation_path_shuffled",
    "factorisation_path_mismatch_train_test",
]

MISMATCH_LEVELS = {
    "mismatch_train_consistent_test_inverted": (
        "standpoint_contrast_with_side_polarity",
        "standpoint_inverted_contrast_with_side_polarity",
    ),
    "mismatch_train_endpoint_test_direction_swapped": (
        "endpoint_o1o2_reference",
        "endpoint_o1o2_direction_swapped",
    ),
    "factorisation_path_mismatch_train_test": (
        "factorisation_path_consistent",
        "factorisation_path_shuffled",
    ),
}

FIXED_MASK_LEVELS = {
    "fixed_b6p_direction_mask",
    "fixed_b6p_swapped_mask",
    "fixed_receiver_pair_mask",
    "fixed_giver_pair_mask",
    "fixed_ab_receiver_only",
    "fixed_c_receiver_boundary_only",
}


def side_features(table: pd.DataFrame, direction: str, seed: int = 71110) -> pd.DataFrame:
    out = b72.add_hierarchy_features(table).copy()
    out["midpoint_ac_bc"] = (pd.to_numeric(out["A_C"], errors="coerce") + pd.to_numeric(out["B_C"], errors="coerce")) / 2.0
    out["side_gap_abs"] = (pd.to_numeric(out["A_C"], errors="coerce") - pd.to_numeric(out["B_C"], errors="coerce")).abs()
    if direction == "A_to_C_to_B":
        out["sender_side"] = pd.to_numeric(out["A_C"], errors="coerce")
        out["receiver_side"] = pd.to_numeric(out["B_C"], errors="coerce")
        out["standpoint_side"] = pd.to_numeric(out["B_C"], errors="coerce")
        out["inverted_standpoint_side"] = pd.to_numeric(out["A_C"], errors="coerce")
        out["standpoint_polarity"] = pd.to_numeric(out["B_C"], errors="coerce") - pd.to_numeric(out["A_C"], errors="coerce")
        out["inverted_standpoint_polarity"] = -out["standpoint_polarity"]
        out["standpoint_operator"] = pd.to_numeric(out["O2_lag5_AB_raw"], errors="coerce")
        out["inverted_standpoint_operator"] = pd.to_numeric(out["O1_lag0_AB_raw"], errors="coerce")
        out["standpoint_operator_contrast"] = pd.to_numeric(out["O2_lag5_AB_raw"], errors="coerce") - pd.to_numeric(out["O1_lag0_AB_raw"], errors="coerce")
        out["inverted_standpoint_operator_contrast"] = -out["standpoint_operator_contrast"]
    elif direction == "B_to_C_to_A":
        out["sender_side"] = pd.to_numeric(out["B_C"], errors="coerce")
        out["receiver_side"] = pd.to_numeric(out["A_C"], errors="coerce")
        out["standpoint_side"] = pd.to_numeric(out["A_C"], errors="coerce")
        out["inverted_standpoint_side"] = pd.to_numeric(out["B_C"], errors="coerce")
        out["standpoint_polarity"] = pd.to_numeric(out["A_C"], errors="coerce") - pd.to_numeric(out["B_C"], errors="coerce")
        out["inverted_standpoint_polarity"] = -out["standpoint_polarity"]
        out["standpoint_operator"] = pd.to_numeric(out["O1_lag0_AB_raw"], errors="coerce")
        out["inverted_standpoint_operator"] = pd.to_numeric(out["O2_lag5_AB_raw"], errors="coerce")
        out["standpoint_operator_contrast"] = pd.to_numeric(out["O1_lag0_AB_raw"], errors="coerce") - pd.to_numeric(out["O2_lag5_AB_raw"], errors="coerce")
        out["inverted_standpoint_operator_contrast"] = -out["standpoint_operator_contrast"]
    else:
        raise ValueError(f"unknown direction {direction}")
    out["direction_code"] = 0.0 if direction == "A_to_C_to_B" else 1.0

    ac = pd.to_numeric(out["A_C"], errors="coerce")
    bc = pd.to_numeric(out["B_C"], errors="coerce")
    out["closure_zero"] = (ac - bc) + (bc - ac)
    phi = pd.to_numeric(out.get("phi_latent", pd.Series(np.arange(len(out)), index=out.index)), errors="coerce")
    ranked = phi.rank(method="first").fillna(0).to_numpy(dtype=float)
    order = np.argsort(np.argsort(ranked))
    out["factor24"] = order % 24
    out["factor3"] = out["factor24"] % 3
    out["factor8"] = out["factor24"] % 8
    out["factor2a"] = out["factor24"] % 2
    out["factor2b"] = (out["factor24"] // 2) % 2
    out["factor6"] = out["factor24"] % 6
    out["factor3_shuffled"] = np.nan
    out["factor8_shuffled"] = np.nan
    out["factor6_shuffled"] = np.nan
    rng_factor = np.random.default_rng(seed + 72424)
    for _, sub_factor in out.groupby("label", sort=False):
        idx_factor = sub_factor.index.to_numpy()
        perm_factor = idx_factor.copy()
        rng_factor.shuffle(perm_factor)
        out.loc[idx_factor, "factor3_shuffled"] = out.loc[perm_factor, "factor3"].to_numpy(dtype=float)
        out.loc[idx_factor, "factor8_shuffled"] = out.loc[perm_factor, "factor8"].to_numpy(dtype=float)
        out.loc[idx_factor, "factor6_shuffled"] = out.loc[perm_factor, "factor6"].to_numpy(dtype=float)
    return out


def add_swapped_endpoint_features(table: pd.DataFrame, seed: int) -> pd.DataFrame:
    out = table.copy()
    out["o1_direction_swapped"] = np.nan
    out["o2_direction_swapped"] = np.nan
    rng = np.random.default_rng(seed + 72121)
    for _, sub in out.groupby("label", sort=False):
        idx = sub.index.to_numpy()
        rev = idx[::-1].copy()
        if len(rev) > 2:
            shift = int(rng.integers(1, len(rev)))
            rev = np.roll(rev, shift)
        out.loc[idx, "o1_direction_swapped"] = pd.to_numeric(out.loc[rev, "O2_lag5_AB_raw"], errors="coerce").to_numpy(dtype=float)
        out.loc[idx, "o2_direction_swapped"] = pd.to_numeric(out.loc[rev, "O1_lag0_AB_raw"], errors="coerce").to_numpy(dtype=float)
    return out


def control_state_labels(table: pd.DataFrame, direction: str, level: str, seed: int, generic_names: bool = False) -> pd.Series:
    data = add_swapped_endpoint_features(side_features(table, direction), seed)
    if level == "direction_label_only":
        cols = ["direction_code"]
    elif level == "communication_direction_only":
        cols = ["direction_code", "A_B"]
    elif level == "symmetric_midpoint_control":
        cols = ["midpoint_ac_bc", "side_gap_abs", "A_B"]
    elif level == "sender_receiver_transfer_control":
        cols = ["sender_side", "receiver_side", "A_B"]
    elif level == "asymmetric_standpoint_control":
        cols = ["standpoint_side", "standpoint_polarity", "A_B"]
    elif level == "standpoint_inverted_control":
        cols = ["inverted_standpoint_side", "inverted_standpoint_polarity", "A_B"]
    elif level == "endpoint_o1o2_reference":
        cols = ["O1_lag0_AB_raw", "O2_lag5_AB_raw"]
    elif level == "endpoint_o1o2_direction_swapped":
        cols = ["o1_direction_swapped", "o2_direction_swapped"]
    elif level == "endpoint_o1o2_asymmetric_standpoint":
        cols = ["O1_lag0_AB_raw", "O2_lag5_AB_raw", "standpoint_side", "standpoint_polarity"]
    elif level == "endpoint_o1o2_standpoint_inverted":
        cols = ["O1_lag0_AB_raw", "O2_lag5_AB_raw", "inverted_standpoint_side", "inverted_standpoint_polarity"]
    elif level == "standpoint_consistent_split_operator":
        cols = ["standpoint_operator", "standpoint_side", "standpoint_polarity"]
    elif level == "standpoint_inverted_split_operator":
        cols = ["inverted_standpoint_operator", "inverted_standpoint_side", "inverted_standpoint_polarity"]
    elif level == "standpoint_operator_side_only":
        cols = ["standpoint_operator"]
    elif level == "standpoint_wrong_operator_side_only":
        cols = ["inverted_standpoint_operator"]
    elif level == "standpoint_consistent_operator_contrast":
        cols = ["standpoint_operator_contrast"]
    elif level == "standpoint_inverted_operator_contrast":
        cols = ["inverted_standpoint_operator_contrast"]
    elif level == "standpoint_contrast_with_side_polarity":
        cols = ["standpoint_operator_contrast", "standpoint_polarity"]
    elif level == "standpoint_inverted_contrast_with_side_polarity":
        cols = ["inverted_standpoint_operator_contrast", "inverted_standpoint_polarity"]
    elif level == "closure_scalar_only":
        cols = ["closure_zero"]
    elif level == "closure_2ode_local":
        cols = ["standpoint_polarity"]
    elif level == "directed_transport_closure_control":
        cols = ["standpoint_operator_contrast", "standpoint_polarity"]
    elif level == "factorisation_3x8":
        cols = ["factor3", "factor8", "standpoint_operator_contrast"]
    elif level == "factorisation_2x2x6":
        cols = ["factor2a", "factor2b", "factor6", "standpoint_operator_contrast"]
    elif level == "factorisation_path_consistent":
        cols = ["factor3", "factor8", "factor2a", "factor2b", "factor6", "standpoint_polarity", "standpoint_operator_contrast"]
    elif level == "factorisation_path_shuffled":
        cols = ["factor3_shuffled", "factor8_shuffled", "factor6_shuffled", "standpoint_polarity", "standpoint_operator_contrast"]
    else:
        raise ValueError(f"unknown level {level}")
    if generic_names:
        parts = [f"f{i}=" + b71a.qbin(data[col], 3).astype(str) for i, col in enumerate(cols)]
    else:
        parts = [col + "=" + b71a.qbin(data[col], 3).astype(str) for col in cols]
    return pd.Series(["|".join(vals) for vals in zip(*parts)], index=table.index)


def train_control_policy(train: pd.DataFrame, b6l, endpoint: str, direction: str, level: str, args: argparse.Namespace) -> tuple[dict[str, np.ndarray], np.ndarray]:
    reward_cols = b6l.operator_reward_columns(endpoint)
    train = train.copy()
    train_level = MISMATCH_LEVELS.get(level, (level, level))[0]
    train["control_state"] = control_state_labels(train, direction, train_level, args.seed, generic_names=level in MISMATCH_LEVELS)
    global_means = np.asarray([pd.to_numeric(train[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
    global_weights = b71a.softmax(global_means, args.temperature)
    mapping = {}
    for state, sub in train.groupby("control_state", sort=False):
        if len(sub) < args.min_state_events:
            continue
        means = np.asarray([pd.to_numeric(sub[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
        mapping[str(state)] = b71a.softmax(means, args.temperature)
    return mapping, global_weights


def build_control_access(table: pd.DataFrame, b6p, b6l, level: str, endpoint: str, direction: str, args: argparse.Namespace) -> pd.DataFrame:
    if level in FIXED_MASK_LEVELS:
        return build_fixed_mask_access(table, b6p, b6l, level, endpoint, direction, args)
    data = table.copy()
    test_level = MISMATCH_LEVELS.get(level, (level, level))[1]
    data["control_state"] = control_state_labels(data, direction, test_level, args.seed, generic_names=level in MISMATCH_LEVELS)
    folds = b71a.make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy()
        mapping, global_weights = train_control_policy(train, b6l, endpoint, direction, level, args)
        for _, row in test.iterrows():
            state = str(row["control_state"])
            weights = mapping.get(state, global_weights)
            base = b6p.baseline_readouts(row, b6l, endpoint)
            access = b71a.row_reward(row, b6l, weights, endpoint)
            rows.append(
                {
                    "control_level": level,
                    "endpoint": endpoint,
                    "direction": direction,
                    "fold": fold_index,
                    "label": row["label"],
                    "idx_in_session": row["idx_in_session"],
                    "control_state": state,
                    "access_readout": access,
                    "baseline_max": base["baseline_max"],
                    "access_effect": access - base["baseline_max"] if np.isfinite(access) and np.isfinite(base["baseline_max"]) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def fixed_weights(level: str, direction: str) -> np.ndarray:
    weights = np.zeros(len(OPERATORS), dtype=float)
    if level == "fixed_b6p_direction_mask":
        source = b6p_masks(direction)
        return b71a.normalize(np.asarray([source[op] for op in OPERATORS], dtype=float))
    if level == "fixed_b6p_swapped_mask":
        source = b6p_masks("B_to_C_to_A" if direction == "A_to_C_to_B" else "A_to_C_to_B")
        return b71a.normalize(np.asarray([source[op] for op in OPERATORS], dtype=float))
    if level == "fixed_receiver_pair_mask":
        ops = ["O2_lag5_AB", "O4_B_C_boundary"] if direction == "A_to_C_to_B" else ["O1_lag0_AB", "O3_A_C_boundary"]
    elif level == "fixed_giver_pair_mask":
        ops = ["O1_lag0_AB", "O3_A_C_boundary"] if direction == "A_to_C_to_B" else ["O2_lag5_AB", "O4_B_C_boundary"]
    elif level == "fixed_ab_receiver_only":
        ops = ["O2_lag5_AB"] if direction == "A_to_C_to_B" else ["O1_lag0_AB"]
    elif level == "fixed_c_receiver_boundary_only":
        ops = ["O4_B_C_boundary"] if direction == "A_to_C_to_B" else ["O3_A_C_boundary"]
    else:
        raise ValueError(f"unknown fixed mask level {level}")
    for op in ops:
        weights[OPERATORS.index(op)] = 1.0
    return b71a.normalize(weights)


def b6p_masks(direction: str) -> dict[str, float]:
    if direction == "A_to_C_to_B":
        return {
            "O1_lag0_AB": 0.20,
            "O2_lag5_AB": 0.80,
            "O3_A_C_boundary": 0.10,
            "O4_B_C_boundary": 1.00,
            "O5_full_TFC": 0.65,
            "O6_phase_only": 0.35,
            "O7_suppress_event": 0.05,
        }
    return {
        "O1_lag0_AB": 0.80,
        "O2_lag5_AB": 0.35,
        "O3_A_C_boundary": 1.00,
        "O4_B_C_boundary": 0.10,
        "O5_full_TFC": 0.65,
        "O6_phase_only": 0.35,
        "O7_suppress_event": 0.05,
    }


def build_fixed_mask_access(table: pd.DataFrame, b6p, b6l, level: str, endpoint: str, direction: str, args: argparse.Namespace) -> pd.DataFrame:
    weights = fixed_weights(level, direction)
    folds = b71a.make_folds(table["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    for fold_index, test_labels in enumerate(folds):
        test = table[table["label"].astype(str).isin(set(test_labels))].copy()
        for _, row in test.iterrows():
            base = b6p.baseline_readouts(row, b6l, endpoint)
            access = row_reward_masked(row, b6l, weights, endpoint)
            rows.append(
                {
                    "control_level": level,
                    "endpoint": endpoint,
                    "direction": direction,
                    "fold": fold_index,
                    "label": row["label"],
                    "idx_in_session": row["idx_in_session"],
                    "control_state": level,
                    "access_readout": access,
                    "baseline_max": base["baseline_max"],
                    "access_effect": access - base["baseline_max"] if np.isfinite(access) and np.isfinite(base["baseline_max"]) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def row_reward_masked(row: pd.Series, b6l, weights: np.ndarray, endpoint: str) -> float:
    reward_cols = b6l.operator_reward_columns(endpoint)
    vals = np.asarray([pd.to_numeric(row.get(reward_cols[op], np.nan), errors="coerce") for op in OPERATORS], dtype=float)
    mask = np.isfinite(vals)
    if not mask.any():
        return np.nan
    w = local_normalize(np.asarray(weights, dtype=float)[mask])
    return float(np.sum(vals[mask] * w))


def local_normalize(weights: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    weights = np.where(np.isfinite(weights), weights, 0.0)
    weights = np.clip(weights, 0.0, None)
    total = float(np.sum(weights))
    if total <= 1e-12:
        return np.ones(len(weights), dtype=float) / max(len(weights), 1)
    return weights / total


def compare(intersection: pd.DataFrame, controls: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 72222)
    rows = []
    for (mode, endpoint, direction), sub in intersection.groupby(["mode", "endpoint", "direction"], sort=False):
        true = sub[sub["arm_kind"].eq("true")].set_index(["fold", "label", "idx_in_session"])
        scoped = controls[(controls["endpoint"].eq(endpoint)) & (controls["direction"].eq(direction))]
        for level, ctrl in scoped.groupby("control_level", sort=False):
            control = ctrl.set_index(["fold", "label", "idx_in_session"])
            joined = true[["intersection_access_effect"]].join(control[["access_effect"]], how="inner")
            diff = joined["intersection_access_effect"].to_numpy(dtype=float) - joined["access_effect"].to_numpy(dtype=float)
            effect, p = b71a.signflip_p(diff, rng, args.n_perm)
            rows.append(
                {
                    "mode": mode,
                    "endpoint": endpoint,
                    "direction": direction,
                    "control_level": level,
                    "mean_true_c": float(np.nanmean(joined["intersection_access_effect"])),
                    "mean_control": float(np.nanmean(joined["access_effect"])),
                    "effect_true_minus_control": effect,
                    "p_true_greater": p,
                    "n_pairs": int(np.isfinite(diff).sum()),
                    "c_beats_control": bool(np.isfinite(effect) and effect > 0 and np.isfinite(p) and p <= args.alpha),
                }
            )
    return pd.DataFrame(rows)


def summarize(comparison: pd.DataFrame, frozen: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frozen_keys = set(
        tuple(x)
        for x in frozen[frozen["b71_frozen_b6_supported"]][["mode", "endpoint", "direction_with_c"]].to_numpy()
    )
    comp = comparison.copy()
    comp["frozen_b6_supported"] = [
        (row.mode, row.endpoint, row.direction) in frozen_keys for row in comp.itertuples(index=False)
    ]
    frozen_comp = comp[comp["frozen_b6_supported"]].copy()
    rows = []
    for level, sub in frozen_comp.groupby("control_level", sort=False):
        rows.append(
            {
                "control_level": level,
                "frozen_regimes": int(len(sub)),
                "c_beats_count": int(sub["c_beats_control"].sum()),
                "control_bounds_c_count": int((~sub["c_beats_control"]).sum()),
                "mean_true_minus_control": float(sub["effect_true_minus_control"].mean()),
                "median_true_minus_control": float(sub["effect_true_minus_control"].median()),
            }
        )
    summary = pd.DataFrame(rows)
    pivot = frozen_comp.pivot_table(
        index=["mode", "endpoint", "direction"],
        columns="control_level",
        values="c_beats_control",
        aggfunc="first",
    ).reset_index()
    return summary, pivot


def write_report(path: Path, summary: pd.DataFrame, pivot: pd.DataFrame, comparison: pd.DataFrame, args: argparse.Namespace) -> None:
    lines = [
        "# Private B7.2b Side-Direction / Asymmetric-Standpoint Screen",
        "",
        "Status: private exploratory screen only. Not preregistered, not pushed.",
        "",
        "## Question",
        "",
        "Can the B7.2a side-direction effect be separated from simple communication direction and sender/receiver transfer controls?",
        "",
        "## Component Summary",
        "",
        summary.to_csv(index=False).strip(),
        "",
        "## Frozen-Regime Pass Matrix",
        "",
        pivot.to_csv(index=False).strip(),
        "",
        "## Full Comparison",
        "",
        comparison.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- n_folds: {args.n_folds}",
        f"- min_state_events: {args.min_state_events}",
        f"- temperature: {args.temperature}",
        f"- n_perm: {args.n_perm}",
        f"- alpha: {args.alpha}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    b6p = b71a.load_module("b6p_for_private_b72b", b71a.B6P_SCRIPT)
    b71 = b71a.load_module("b71_for_private_b72b", b71a.B71_SCRIPT)
    b6l, table = b6p.build_table(b71a.build_args(args))
    intersection = b71.build_intersection_arms(table, b6p, b6l, b71a.build_args(args))
    controls = pd.concat(
        [
            build_control_access(table, b6p, b6l, level, endpoint, direction, args)
            for level in CONTROL_LEVELS
            for endpoint in ENDPOINTS
            for direction in DIRECTIONS
        ],
        ignore_index=True,
    )
    comparison = compare(intersection, controls, args)
    frozen = pd.read_csv(REPO / "reports/stage_b7_1/Stage_B7_1_b6_regime_freeze.csv")
    summary, pivot = summarize(comparison, frozen)
    controls.to_csv(outdir / "Stage_B7_2b_control_events.csv", index=False)
    comparison.to_csv(outdir / "Stage_B7_2b_comparison.csv", index=False)
    summary.to_csv(outdir / "Stage_B7_2b_component_summary.csv", index=False)
    pivot.to_csv(outdir / "Stage_B7_2b_frozen_pass_matrix.csv", index=False)
    write_report(outdir / "Stage_B7_2b_preregistered_summary.md", summary, pivot, comparison, args)
    print("\nStage B7.2b audit")
    print(f"- output_dir: {outdir}")
    print(summary.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_2b")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=71110)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
