#!/usr/bin/env python3
"""Stage B7.2 O1/O2 control-hierarchy audit."""

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


ENDPOINTS = b71a.ENDPOINTS
OPERATORS = b71a.OPERATORS
CONTROL_LEVELS = [
    "strict_past_ab_only",
    "expanded_past_ab_only",
    "causal_past_operator_estimator",
    "lag_horizon_separated_o1o2",
    "operator_proxy_ab",
]


def add_hierarchy_features(table: pd.DataFrame) -> pd.DataFrame:
    out = b71a.add_past_ab_features(table)
    for col in [
        "ab_lag3",
        "ab_roll_mean10",
        "ab_roll_slope10",
        "ab_roll_vol10",
        "o1_proxy_lag1",
        "o1_proxy_lag2",
        "o1_proxy_roll_mean5",
        "o2_proxy_lag1",
        "o2_proxy_lag2",
        "o2_proxy_roll_mean5",
    ]:
        out[col] = np.nan
    for _, sub in out.groupby("label", sort=False):
        idx = sub.index
        ab = pd.to_numeric(sub["A_B"], errors="coerce")
        ab_shifted = ab.shift(1)
        out.loc[idx, "ab_lag3"] = ab.shift(3)
        out.loc[idx, "ab_roll_mean10"] = ab_shifted.rolling(10, min_periods=1).mean()
        out.loc[idx, "ab_roll_vol10"] = ab_shifted.rolling(10, min_periods=2).std()
        out.loc[idx, "ab_roll_slope10"] = rolling_slope(ab_shifted, 10)
        o1 = pd.to_numeric(sub["O1_lag0_AB_raw"], errors="coerce")
        o2 = pd.to_numeric(sub["O2_lag5_AB_raw"], errors="coerce")
        out.loc[idx, "o1_proxy_lag1"] = o1.shift(1)
        out.loc[idx, "o1_proxy_lag2"] = o1.shift(2)
        out.loc[idx, "o1_proxy_roll_mean5"] = o1.shift(1).rolling(5, min_periods=1).mean()
        out.loc[idx, "o2_proxy_lag1"] = o2.shift(1)
        out.loc[idx, "o2_proxy_lag2"] = o2.shift(2)
        out.loc[idx, "o2_proxy_roll_mean5"] = o2.shift(1).rolling(5, min_periods=1).mean()
    return out


def rolling_slope(values: pd.Series, window: int) -> list[float]:
    vals = values.to_numpy(dtype=float)
    slopes = []
    for i in range(len(vals)):
        start = max(0, i - window + 1)
        y = vals[start : i + 1]
        x = np.arange(len(y), dtype=float)
        mask = np.isfinite(y)
        if mask.sum() < 2:
            slopes.append(np.nan)
        else:
            slopes.append(float(np.polyfit(x[mask], y[mask], 1)[0]))
    return slopes


def control_state_labels(table: pd.DataFrame, level: str) -> pd.Series:
    data = add_hierarchy_features(table)
    if level == "strict_past_ab_only":
        cols = ["A_B", "ab_lag1", "ab_roll_mean5", "ab_roll_slope5", "ab_roll_vol5"]
    elif level == "expanded_past_ab_only":
        cols = ["A_B", "ab_lag1", "ab_lag2", "ab_roll_mean3", "ab_roll_mean5", "ab_roll_slope5", "ab_roll_vol5"]
    elif level == "causal_past_operator_estimator":
        cols = [
            "ab_lag1",
            "ab_lag2",
            "ab_lag3",
            "ab_roll_mean5",
            "ab_roll_mean10",
            "ab_roll_slope5",
            "ab_roll_slope10",
            "ab_roll_vol5",
            "ab_roll_vol10",
        ]
    elif level == "lag_horizon_separated_o1o2":
        cols = [
            "ab_lag1",
            "ab_lag2",
            "ab_roll_mean5",
            "o1_proxy_lag1",
            "o1_proxy_lag2",
            "o1_proxy_roll_mean5",
            "o2_proxy_lag1",
            "o2_proxy_lag2",
            "o2_proxy_roll_mean5",
        ]
    elif level == "operator_proxy_ab":
        data["lag0_proxy"] = pd.to_numeric(data["O1_lag0_AB_raw"], errors="coerce")
        data["lag5_proxy"] = pd.to_numeric(data["O2_lag5_AB_raw"], errors="coerce")
        cols = ["A_B", "lag0_proxy", "lag5_proxy"]
    else:
        raise ValueError(f"unknown control level {level}")
    parts = [col + "=" + b71a.qbin(data[col], 3).astype(str) for col in cols]
    return pd.Series(["|".join(vals) for vals in zip(*parts)], index=table.index)


def train_control_policy(train: pd.DataFrame, b6l, endpoint: str, level: str, args: argparse.Namespace) -> tuple[dict[str, np.ndarray], np.ndarray]:
    reward_cols = b6l.operator_reward_columns(endpoint)
    train = train.copy()
    train["control_state"] = control_state_labels(train, level)
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
    data["control_state"] = control_state_labels(data, level)
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
            rows.append(
                {
                    "control_level": level,
                    "endpoint": endpoint,
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


def classify(comparison: pd.DataFrame, frozen: pd.DataFrame) -> pd.DataFrame:
    frozen_idx = frozen.set_index(["mode", "endpoint", "direction_with_c"])
    rows = []
    for (mode, endpoint, direction), sub in comparison.groupby(["mode", "endpoint", "direction"], sort=False):
        key = (mode, endpoint, direction)
        levels = {row["control_level"]: bool(row["passes"]) for _, row in sub.iterrows()}
        frozen_pass = bool(frozen_idx.loc[key, "b71_frozen_b6_supported"]) if key in frozen_idx.index else False
        strict_pass = levels.get("strict_past_ab_only", False)
        expanded_pass = levels.get("expanded_past_ab_only", False)
        causal_pass = levels.get("causal_past_operator_estimator", False)
        lagged_pass = levels.get("lag_horizon_separated_o1o2", False)
        proxy_pass = levels.get("operator_proxy_ab", False)
        supported = bool(frozen_pass and strict_pass and expanded_pass and causal_pass and lagged_pass)
        if supported and proxy_pass:
            interpretation = "exceeds_full_tested_hierarchy_including_endpoint_proxy"
        elif supported and not proxy_pass:
            interpretation = "endpoint_adjacent_o1o2_boundary_not_simple_ab_history"
        elif frozen_pass and strict_pass and expanded_pass and not causal_pass:
            interpretation = "simple_ab_history_insufficient_but_causal_operator_estimator_explains"
        elif frozen_pass and strict_pass and expanded_pass and causal_pass and not lagged_pass:
            interpretation = "causal_estimator_beaten_but_lagged_o1o2_explains"
        elif frozen_pass and not strict_pass:
            interpretation = "does_not_exceed_strict_past_ab"
        else:
            interpretation = "not_frozen_b6_supported_or_incomplete"
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "direction": direction,
                "frozen_b6_supported": frozen_pass,
                "passes_strict_past_ab_only": strict_pass,
                "passes_expanded_past_ab_only": expanded_pass,
                "passes_causal_past_operator_estimator": causal_pass,
                "passes_lag_horizon_separated_o1o2": lagged_pass,
                "passes_operator_proxy_ab": proxy_pass,
                "b72_primary_supported": supported,
                "interpretation": interpretation,
            }
        )
    return pd.DataFrame(rows)


def provenance_audit() -> pd.DataFrame:
    rows = [
        {
            "feature": "A_B",
            "temporal_status": "current observed A/B relation",
            "endpoint_adjacency_risk": "medium",
            "used_in_levels": "strict_past_ab_only; expanded_past_ab_only; operator_proxy_ab",
            "b72_role": "ordinary A/B-history baseline continuity with B7.1a",
        },
        {
            "feature": "past A/B lags and rolling summaries",
            "temporal_status": "past-only within session",
            "endpoint_adjacency_risk": "low",
            "used_in_levels": "strict_past_ab_only; expanded_past_ab_only; causal_past_operator_estimator; lag_horizon_separated_o1o2",
            "b72_role": "causally valid A/B-derived operator-estimator substrate",
        },
        {
            "feature": "O1_lag0_AB_raw",
            "temporal_status": "current-row operator proxy",
            "endpoint_adjacency_risk": "high",
            "used_in_levels": "operator_proxy_ab",
            "b72_role": "endpoint-adjacent upper-bound style control",
        },
        {
            "feature": "O2_lag5_AB_raw",
            "temporal_status": "current-row lag-5 operator proxy as encoded in source table",
            "endpoint_adjacency_risk": "high",
            "used_in_levels": "operator_proxy_ab",
            "b72_role": "endpoint-adjacent upper-bound style control",
        },
        {
            "feature": "lagged/rolled O1/O2 proxy summaries",
            "temporal_status": "prior rows only",
            "endpoint_adjacency_risk": "medium",
            "used_in_levels": "lag_horizon_separated_o1o2",
            "b72_role": "tests whether O1/O2 advantage survives endpoint-adjacency removal",
        },
    ]
    return pd.DataFrame(rows)


def gmr72_angle_grid(step: float) -> pd.DataFrame:
    rows = []
    base_angles = [-72.0, 0.0, 22.5, 36.0, 45.0, 60.0, 72.0, 75.0, 90.0, 144.0]
    for angle in base_angles:
        rows.append({"angle_degrees": angle, "role": "base_preregistered", "scan_center": np.nan, "scan_step_degrees": np.nan})
    for center in [72.0, 75.0]:
        for offset in np.round(np.arange(-1.0, 1.0 + step / 2.0, step), 10):
            rows.append(
                {
                    "angle_degrees": round(center + float(offset), 10),
                    "role": "luke_local_scan",
                    "scan_center": center,
                    "scan_step_degrees": step,
                }
            )
    return pd.DataFrame(rows).drop_duplicates(["angle_degrees", "role", "scan_center"]).sort_values(["role", "angle_degrees"])


def write_report(path: Path, summary: pd.DataFrame, comparison: pd.DataFrame, args: argparse.Namespace) -> None:
    supported = int(summary["b72_primary_supported"].sum()) if not summary.empty else 0
    causal = int(summary["passes_causal_past_operator_estimator"].sum()) if not summary.empty else 0
    lagged = int(summary["passes_lag_horizon_separated_o1o2"].sum()) if not summary.empty else 0
    proxy = int(summary["passes_operator_proxy_ab"].sum()) if not summary.empty else 0
    lines = [
        "# Stage B7.2 O1/O2 Control-Hierarchy Audit",
        "",
        "Status: executed after writing Stage_B7_2_preregistration.md and Stage_B7_2_revised_plan_email_draft.md.",
        "",
        "## Result",
        "",
        f"- B7.2-primary-supported regimes: {supported} / {len(summary)}",
        f"- regimes passing causal_past_operator_estimator: {causal} / {len(summary)}",
        f"- regimes passing lag_horizon_separated_o1o2: {lagged} / {len(summary)}",
        f"- regimes passing endpoint-adjacent operator_proxy_ab: {proxy} / {len(summary)}",
        "",
        "## Primary Classification",
        "",
        summary.to_csv(index=False).strip(),
        "",
        "## Control-Level Comparison",
        "",
        comparison.to_csv(index=False).strip(),
        "",
        "## Interpretation Boundary",
        "",
        "B7.2 keeps C12 paused. A C12 reconnection test is not used to rescue any B7.2 primary failure.",
        "",
        "If true C beats causal_past_operator_estimator and lag_horizon_separated_o1o2 but not operator_proxy_ab, the strongest supported reading is that B7.1's failure reflects endpoint-adjacent O1/O2 proxy strength rather than simple A/B-history reducibility.",
        "",
        "## Settings",
        "",
        f"- n_folds: {args.n_folds}",
        f"- min_state_events: {args.min_state_events}",
        f"- temperature: {args.temperature}",
        f"- n_perm: {args.n_perm}",
        f"- alpha: {args.alpha}",
        f"- seed: {args.seed}",
        f"- gmr72_angle_scan_step: {args.gmr72_angle_scan_step}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    b6p = b71a.load_module("b6p_for_b72", b71a.B6P_SCRIPT)
    b71 = b71a.load_module("b71_for_b72", b71a.B71_SCRIPT)
    b6l, table = b6p.build_table(b71a.build_args(args))
    intersection = b71.build_intersection_arms(table, b6p, b6l, b71a.build_args(args))
    controls = pd.concat(
        [
            build_control_access(table, b6p, b6l, level, endpoint, args)
            for level in CONTROL_LEVELS
            for endpoint in ENDPOINTS
        ],
        ignore_index=True,
    )
    comparison = b71a.compare_true_to_controls(intersection, controls, args)
    frozen = pd.read_csv(REPO / "reports/stage_b7_1/Stage_B7_1_b6_regime_freeze.csv")
    summary = classify(comparison, frozen)
    provenance = provenance_audit()
    angle_grid = gmr72_angle_grid(args.gmr72_angle_scan_step)
    controls.to_csv(outdir / "Stage_B7_2_hierarchy_control_events.csv", index=False)
    comparison.to_csv(outdir / "Stage_B7_2_control_hierarchy_comparison.csv", index=False)
    summary.to_csv(outdir / "Stage_B7_2_primary_classification.csv", index=False)
    provenance.to_csv(outdir / "Stage_B7_2_o1o2_provenance_audit.csv", index=False)
    angle_grid.to_csv(outdir / "Stage_B7_2_gmr72_secondary_angle_grid.csv", index=False)
    write_report(outdir / "Stage_B7_2_preregistered_summary.md", summary, comparison, args)
    print("\nStage B7.2 outputs")
    print(f"- output_dir: {outdir}")
    print(f"- b72_primary_supported: {int(summary['b72_primary_supported'].sum())} / {len(summary)}")
    print(f"- causal_past_operator_estimator_pass: {int(summary['passes_causal_past_operator_estimator'].sum())} / {len(summary)}")
    print(f"- lag_horizon_separated_o1o2_pass: {int(summary['passes_lag_horizon_separated_o1o2'].sum())} / {len(summary)}")
    print(f"- operator_proxy_ab_pass: {int(summary['passes_operator_proxy_ab'].sum())} / {len(summary)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_2")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=71110)
    parser.add_argument("--gmr72-angle-scan-step", type=float, default=0.2)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())

