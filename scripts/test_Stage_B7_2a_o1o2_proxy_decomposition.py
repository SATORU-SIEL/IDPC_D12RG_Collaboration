#!/usr/bin/env python3
"""Stage B7.2a O1/O2 proxy provenance decomposition."""

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
DECOMPOSITION_LEVELS = [
    "o1_lag0_only",
    "o2_lag5_only",
    "o1_o2_joint",
    "phase_removed_o1o2",
    "tfc_removed_o1o2",
    "side_shuffled_o1o2",
    "memory_only_o1o2",
    "residual_endpoint_o1o2",
]


def residualize(y: pd.Series, predictors: pd.DataFrame) -> pd.Series:
    yy = pd.to_numeric(y, errors="coerce").to_numpy(dtype=float)
    xcols = []
    for col in predictors.columns:
        vals = pd.to_numeric(predictors[col], errors="coerce").to_numpy(dtype=float)
        if np.isfinite(vals).any():
            med = np.nanmedian(vals)
            vals = np.where(np.isfinite(vals), vals, med)
        else:
            vals = np.zeros(len(yy), dtype=float)
        xcols.append(vals)
    x = np.column_stack([np.ones(len(yy), dtype=float)] + xcols)
    mask = np.isfinite(yy)
    if mask.sum() <= x.shape[1] + 2:
        return pd.Series(np.nan, index=y.index)
    beta, *_ = np.linalg.lstsq(x[mask], yy[mask], rcond=None)
    pred = x @ beta
    return pd.Series(yy - pred, index=y.index)


def add_decomposition_features(table: pd.DataFrame, seed: int) -> pd.DataFrame:
    out = b72.add_hierarchy_features(table).copy()
    out["phase_bin"] = b71a.qbin(out.get("phi_latent", pd.Series(np.nan, index=out.index)), 6)
    out["tfc_bin"] = b71a.qbin(pd.to_numeric(out.get("TFC_min", np.nan), errors="coerce"), 4).astype(str) + ":" + b71a.qbin(pd.to_numeric(out.get("TFC_mean", np.nan), errors="coerce"), 4).astype(str)
    o1 = pd.to_numeric(out["O1_lag0_AB_raw"], errors="coerce")
    o2 = pd.to_numeric(out["O2_lag5_AB_raw"], errors="coerce")
    out["o1_phase_removed"] = o1 - o1.groupby(out["phase_bin"]).transform("mean")
    out["o2_phase_removed"] = o2 - o2.groupby(out["phase_bin"]).transform("mean")
    out["o1_tfc_removed"] = o1 - o1.groupby(out["tfc_bin"]).transform("mean")
    out["o2_tfc_removed"] = o2 - o2.groupby(out["tfc_bin"]).transform("mean")
    out["o1_side_shuffled"] = np.nan
    out["o2_side_shuffled"] = np.nan
    rng = np.random.default_rng(seed + 72020)
    for _, sub in out.groupby("label", sort=False):
        idx = sub.index.to_numpy()
        perm1 = idx.copy()
        perm2 = idx.copy()
        rng.shuffle(perm1)
        rng.shuffle(perm2)
        out.loc[idx, "o1_side_shuffled"] = o1.loc[perm1].to_numpy(dtype=float)
        out.loc[idx, "o2_side_shuffled"] = o2.loc[perm2].to_numpy(dtype=float)
    pred_cols = [
        "ab_lag1", "ab_lag2", "ab_lag3", "ab_roll_mean5", "ab_roll_mean10", "ab_roll_slope5", "ab_roll_vol5",
        "o1_proxy_lag1", "o1_proxy_lag2", "o1_proxy_roll_mean5", "o2_proxy_lag1", "o2_proxy_lag2", "o2_proxy_roll_mean5",
    ]
    out["o1_residual_endpoint"] = residualize(o1, out[pred_cols])
    out["o2_residual_endpoint"] = residualize(o2, out[pred_cols])
    return out


def control_state_labels(table: pd.DataFrame, level: str, seed: int) -> pd.Series:
    data = add_decomposition_features(table, seed)
    if level == "o1_lag0_only":
        cols = ["O1_lag0_AB_raw"]
    elif level == "o2_lag5_only":
        cols = ["O2_lag5_AB_raw"]
    elif level == "o1_o2_joint":
        cols = ["O1_lag0_AB_raw", "O2_lag5_AB_raw"]
    elif level == "phase_removed_o1o2":
        cols = ["o1_phase_removed", "o2_phase_removed"]
    elif level == "tfc_removed_o1o2":
        cols = ["o1_tfc_removed", "o2_tfc_removed"]
    elif level == "side_shuffled_o1o2":
        cols = ["o1_side_shuffled", "o2_side_shuffled"]
    elif level == "memory_only_o1o2":
        cols = ["o1_proxy_lag1", "o1_proxy_lag2", "o1_proxy_roll_mean5", "o2_proxy_lag1", "o2_proxy_lag2", "o2_proxy_roll_mean5"]
    elif level == "residual_endpoint_o1o2":
        cols = ["o1_residual_endpoint", "o2_residual_endpoint"]
    else:
        raise ValueError(f"unknown decomposition level {level}")
    parts = [col + "=" + b71a.qbin(data[col], 3).astype(str) for col in cols]
    return pd.Series(["|".join(vals) for vals in zip(*parts)], index=table.index)


def train_control_policy(train: pd.DataFrame, b6l, endpoint: str, level: str, args: argparse.Namespace) -> tuple[dict[str, np.ndarray], np.ndarray]:
    reward_cols = b6l.operator_reward_columns(endpoint)
    train = train.copy()
    train["control_state"] = control_state_labels(train, level, args.seed)
    global_means = np.asarray([pd.to_numeric(train[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
    global_weights = b71a.softmax(global_means, args.temperature)
    mapping = {}
    for state, sub in train.groupby("control_state", sort=False):
        if len(sub) < args.min_state_events:
            continue
        means = np.asarray([pd.to_numeric(sub[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
        mapping[str(state)] = b71a.softmax(means, args.temperature)
    return mapping, global_weights


def build_control_access(table: pd.DataFrame, b6p, b6l, level: str, endpoint: str, args: argparse.Namespace) -> pd.DataFrame:
    data = table.copy()
    data["control_state"] = control_state_labels(data, level, args.seed)
    folds = b71a.make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy()
        mapping, global_weights = train_control_policy(train, b6l, endpoint, level, args)
        for _, row in test.iterrows():
            state = str(row["control_state"])
            weights = mapping.get(state, global_weights)
            base = b6p.baseline_readouts(row, b6l, endpoint)
            access = b71a.row_reward(row, b6l, weights, endpoint)
            rows.append({
                "control_level": level,
                "endpoint": endpoint,
                "fold": fold_index,
                "label": row["label"],
                "idx_in_session": row["idx_in_session"],
                "control_state": state,
                "access_readout": access,
                "baseline_max": base["baseline_max"],
                "access_effect": access - base["baseline_max"] if np.isfinite(access) and np.isfinite(base["baseline_max"]) else np.nan,
            })
    return pd.DataFrame(rows)


def classify(comparison: pd.DataFrame, frozen: pd.DataFrame) -> pd.DataFrame:
    frozen_idx = frozen.set_index(["mode", "endpoint", "direction_with_c"])
    rows = []
    for (mode, endpoint, direction), sub in comparison.groupby(["mode", "endpoint", "direction"], sort=False):
        key = (mode, endpoint, direction)
        levels = {r["control_level"]: bool(r["passes"]) for _, r in sub.iterrows()}
        effects = {r["control_level"]: float(r["effect_true_minus_control"]) for _, r in sub.iterrows()}
        frozen_pass = bool(frozen_idx.loc[key, "b71_frozen_b6_supported"]) if key in frozen_idx.index else False
        joint_boundary = frozen_pass and not levels.get("o1_o2_joint", False)
        labels = []
        if joint_boundary and (not levels.get("o1_lag0_only", False) or not levels.get("o2_lag5_only", False)):
            labels.append("pure_ab_operator_proxy")
        if joint_boundary and levels.get("phase_removed_o1o2", False):
            labels.append("phase_sensitive_proxy")
        if joint_boundary and levels.get("tfc_removed_o1o2", False):
            labels.append("tfc_compressed_proxy")
        if joint_boundary and levels.get("side_shuffled_o1o2", False):
            labels.append("side_directional_proxy")
        if joint_boundary and not levels.get("memory_only_o1o2", False):
            labels.append("memory_proxy")
        if joint_boundary and not levels.get("residual_endpoint_o1o2", False):
            labels.append("residual_endpoint_proxy")
        component_bounds = [lvl for lvl in ["o1_lag0_only", "o2_lag5_only", "phase_removed_o1o2", "tfc_removed_o1o2", "side_shuffled_o1o2", "memory_only_o1o2", "residual_endpoint_o1o2"] if not levels.get(lvl, False)]
        if joint_boundary and not component_bounds:
            labels.append("compound_proxy")
        if not labels:
            labels.append("no_frozen_joint_boundary" if not joint_boundary else "unclassified_boundary")
        row = {
            "mode": mode,
            "endpoint": endpoint,
            "direction": direction,
            "frozen_b6_supported": frozen_pass,
            "joint_o1o2_boundary": joint_boundary,
            "boundary_classification": ";".join(labels),
        }
        for lvl in DECOMPOSITION_LEVELS:
            row[f"c_beats_{lvl}"] = levels.get(lvl, False)
            row[f"effect_{lvl}"] = effects.get(lvl, np.nan)
        rows.append(row)
    return pd.DataFrame(rows)


def component_summary(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    frozen = summary[summary["frozen_b6_supported"]].copy()
    for lvl in DECOMPOSITION_LEVELS:
        rows.append({
            "component": lvl,
            "frozen_regimes_tested": int(len(frozen)),
            "c_beats_component": int(frozen[f"c_beats_{lvl}"].sum()) if not frozen.empty else 0,
            "component_bounds_c": int((~frozen[f"c_beats_{lvl}"]).sum()) if not frozen.empty else 0,
            "mean_true_minus_component": float(frozen[f"effect_{lvl}"].mean()) if not frozen.empty else np.nan,
        })
    for label in ["pure_ab_operator_proxy", "phase_sensitive_proxy", "tfc_compressed_proxy", "side_directional_proxy", "memory_proxy", "residual_endpoint_proxy", "compound_proxy"]:
        rows.append({
            "component": f"classification:{label}",
            "frozen_regimes_tested": int(len(frozen)),
            "c_beats_component": np.nan,
            "component_bounds_c": int(frozen["boundary_classification"].str.contains(label, regex=False).sum()) if not frozen.empty else 0,
            "mean_true_minus_component": np.nan,
        })
    return pd.DataFrame(rows)


def write_report(path: Path, summary: pd.DataFrame, comparison: pd.DataFrame, comp: pd.DataFrame, args: argparse.Namespace) -> None:
    frozen = summary[summary["frozen_b6_supported"]]
    joint = int(frozen["joint_o1o2_boundary"].sum()) if not frozen.empty else 0
    lines = [
        "# Stage B7.2a O1/O2 Proxy Provenance Decomposition",
        "",
        "Status: executed after writing Stage_B7_2a_preregistration.md and Stage_B7_2a_plan_email_draft.md.",
        "",
        "## Result",
        "",
        f"- frozen B6-supported regimes tested: {len(frozen)} / {len(summary)}",
        f"- regimes where joint endpoint-adjacent O1/O2 still bounds true C: {joint} / {len(frozen)}",
        "",
        "## Component Summary",
        "",
        comp.to_csv(index=False).strip(),
        "",
        "## Boundary Classification",
        "",
        summary.to_csv(index=False).strip(),
        "",
        "## Decomposition Comparison",
        "",
        comparison.to_csv(index=False).strip(),
        "",
        "## Interpretation Rule",
        "",
        "B7.2a does not use C12 as a rescue module. If O1/O2 strength drops after phase, TFC, or side/direction removal, the B6 structure may be compressed into the endpoint-adjacent proxy rather than absent from the system.",
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
    b6p = b71a.load_module("b6p_for_b72a", b71a.B6P_SCRIPT)
    b71 = b71a.load_module("b71_for_b72a", b71a.B71_SCRIPT)
    b6l, table = b6p.build_table(b71a.build_args(args))
    intersection = b71.build_intersection_arms(table, b6p, b6l, b71a.build_args(args))
    controls = pd.concat([build_control_access(table, b6p, b6l, level, endpoint, args) for level in DECOMPOSITION_LEVELS for endpoint in ENDPOINTS], ignore_index=True)
    comparison = b71a.compare_true_to_controls(intersection, controls, args)
    frozen = pd.read_csv(REPO / "reports/stage_b7_1/Stage_B7_1_b6_regime_freeze.csv")
    summary = classify(comparison, frozen)
    comp = component_summary(summary)
    controls.to_csv(outdir / "Stage_B7_2a_decomposition_control_events.csv", index=False)
    comparison.to_csv(outdir / "Stage_B7_2a_decomposition_comparison.csv", index=False)
    summary.to_csv(outdir / "Stage_B7_2a_boundary_classification.csv", index=False)
    comp.to_csv(outdir / "Stage_B7_2a_component_summary.csv", index=False)
    write_report(outdir / "Stage_B7_2a_preregistered_summary.md", summary, comparison, comp, args)
    frozen_summary = summary[summary["frozen_b6_supported"]]
    print("\nStage B7.2a outputs")
    print(f"- output_dir: {outdir}")
    print(f"- frozen_regimes: {len(frozen_summary)} / {len(summary)}")
    print(f"- joint_o1o2_boundary: {int(frozen_summary['joint_o1o2_boundary'].sum())} / {len(frozen_summary)}")
    for _, row in comp.iterrows():
        print(f"- {row['component']}: bounds={row['component_bounds_c']} c_beats={row['c_beats_component']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_2a")
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
