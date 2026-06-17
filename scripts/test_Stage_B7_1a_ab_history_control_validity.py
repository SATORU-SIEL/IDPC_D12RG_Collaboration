#!/usr/bin/env python3
"""Stage B7.1a A/B-history control validity audit."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
SCRIPTS = REPO / "scripts"
B6P_SCRIPT = SCRIPTS / "private_B6P_objectification_vs_intersection_audit.py"
B71_SCRIPT = SCRIPTS / "test_Stage_B7_1_preregistered_intersection_access.py"

OPERATORS = [
    "O1_lag0_AB",
    "O2_lag5_AB",
    "O3_A_C_boundary",
    "O4_B_C_boundary",
    "O5_full_TFC",
    "O6_phase_only",
    "O7_suppress_event",
]
MODES = ["linear_c_state", "gmr72_phase_conditioned", "fes_string_conditioned", "combined_c_fes_gmr72"]
ENDPOINTS = ["z_reward", "rank_reward", "gmr72_bridge_composite"]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 731)
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


def softmax(scores: np.ndarray, temperature: float) -> np.ndarray:
    scores = np.asarray(scores, dtype=float)
    finite = np.isfinite(scores)
    if not finite.any():
        return np.ones(len(scores), dtype=float) / len(scores)
    fill = float(np.nanmin(scores[finite]))
    s = np.where(finite, scores, fill)
    s = s / max(float(temperature), 1e-6)
    s = s - float(np.nanmax(s))
    exp = np.exp(s)
    if not np.isfinite(exp.sum()) or exp.sum() <= 0:
        return np.ones(len(scores), dtype=float) / len(scores)
    return exp / exp.sum()


def normalize(weights: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    weights = np.where(np.isfinite(weights), weights, 0.0)
    weights = np.clip(weights, 0.0, None)
    total = float(np.sum(weights))
    if total <= 1e-12:
        return np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    return weights / total


def qbin(values: pd.Series, n_bins: int = 3) -> pd.Series:
    vals = pd.to_numeric(values, errors="coerce")
    if vals.notna().sum() < n_bins:
        return pd.Series(["missing"] * len(vals), index=values.index)
    try:
        labels = pd.qcut(vals.rank(method="first"), n_bins, labels=[f"q{i+1}" for i in range(n_bins)])
        return pd.Series(labels, index=values.index).astype(object).where(vals.notna(), "missing").astype(str)
    except ValueError:
        return pd.Series(["flat"] * len(vals), index=values.index)


def add_past_ab_features(table: pd.DataFrame) -> pd.DataFrame:
    out = table.sort_values(["label", "idx_in_session"]).reset_index(drop=True).copy()
    out["ab_lag1"] = np.nan
    out["ab_lag2"] = np.nan
    out["ab_roll_mean3"] = np.nan
    out["ab_roll_mean5"] = np.nan
    out["ab_roll_slope5"] = np.nan
    out["ab_roll_vol5"] = np.nan
    for _, sub in out.groupby("label", sort=False):
        idx = sub.index
        ab = pd.to_numeric(sub["A_B"], errors="coerce")
        shifted = ab.shift(1)
        out.loc[idx, "ab_lag1"] = shifted
        out.loc[idx, "ab_lag2"] = ab.shift(2)
        out.loc[idx, "ab_roll_mean3"] = shifted.rolling(3, min_periods=1).mean()
        out.loc[idx, "ab_roll_mean5"] = shifted.rolling(5, min_periods=1).mean()
        out.loc[idx, "ab_roll_vol5"] = shifted.rolling(5, min_periods=2).std()
        slopes = []
        vals = shifted.to_numpy(dtype=float)
        for i in range(len(vals)):
            start = max(0, i - 4)
            y = vals[start : i + 1]
            x = np.arange(len(y), dtype=float)
            mask = np.isfinite(y)
            if mask.sum() < 2:
                slopes.append(np.nan)
            else:
                slopes.append(float(np.polyfit(x[mask], y[mask], 1)[0]))
        out.loc[idx, "ab_roll_slope5"] = slopes
    return out


def control_state_labels(table: pd.DataFrame, level: str) -> pd.Series:
    data = add_past_ab_features(table)
    if level == "strict_past_ab_only":
        cols = ["A_B", "ab_lag1", "ab_roll_mean5", "ab_roll_slope5", "ab_roll_vol5"]
    elif level == "expanded_past_ab_only":
        cols = ["A_B", "ab_lag1", "ab_lag2", "ab_roll_mean3", "ab_roll_mean5", "ab_roll_slope5", "ab_roll_vol5"]
    elif level == "operator_proxy_ab":
        data["lag0_proxy"] = pd.to_numeric(data["O1_lag0_AB_raw"], errors="coerce")
        data["lag5_proxy"] = pd.to_numeric(data["O2_lag5_AB_raw"], errors="coerce")
        cols = ["A_B", "lag0_proxy", "lag5_proxy"]
    else:
        raise ValueError(f"unknown control level {level}")
    parts = []
    for col in cols:
        parts.append(col + "=" + qbin(data[col], 3).astype(str))
    return pd.Series(["|".join(vals) for vals in zip(*parts)], index=table.index)


def build_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        annotated=args.annotated,
        events=args.events,
        output_dir=args.output_dir,
        window=args.window,
        n_folds=args.n_folds,
        min_state_events=args.min_state_events,
        temperature=args.temperature,
        n_random_draws=args.n_random_draws,
        n_control_draws=args.n_control_draws,
        n_perm=args.n_perm,
        seed=args.seed,
    )


def train_control_policy(train: pd.DataFrame, b6l, endpoint: str, level: str, args: argparse.Namespace) -> tuple[dict[str, np.ndarray], np.ndarray]:
    reward_cols = b6l.operator_reward_columns(endpoint)
    train = train.copy()
    train["control_state"] = control_state_labels(train, level)
    global_means = np.asarray([pd.to_numeric(train[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
    global_weights = softmax(global_means, args.temperature)
    mapping = {}
    for state, sub in train.groupby("control_state", sort=False):
        if len(sub) < args.min_state_events:
            continue
        means = np.asarray([pd.to_numeric(sub[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
        mapping[str(state)] = softmax(means, args.temperature)
    return mapping, global_weights


def row_reward(row: pd.Series, b6l, weights: np.ndarray, endpoint: str) -> float:
    vals = np.asarray([pd.to_numeric(row.get(b6l.operator_reward_columns(endpoint)[op], np.nan), errors="coerce") for op in OPERATORS], dtype=float)
    mask = np.isfinite(vals)
    if not mask.any():
        return np.nan
    w = normalize(np.asarray(weights, dtype=float)[mask])
    return float(np.sum(vals[mask] * w))


def build_control_access(table: pd.DataFrame, b6p, b6l, level: str, endpoint: str, args: argparse.Namespace) -> pd.DataFrame:
    data = table.copy()
    data["control_state"] = control_state_labels(data, level)
    folds = make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
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
            access = row_reward(row, b6l, weights, endpoint)
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


def compare_true_to_controls(intersection: pd.DataFrame, controls: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 732)
    rows = []
    for (mode, endpoint, direction), sub in intersection.groupby(["mode", "endpoint", "direction"], sort=False):
        true = sub[sub["arm_kind"].eq("true")].set_index(["fold", "label", "idx_in_session"])
        for level, ctrl in controls[controls["endpoint"].eq(endpoint)].groupby("control_level", sort=False):
            control = ctrl.set_index(["fold", "label", "idx_in_session"])
            joined = true[["intersection_access_effect"]].join(control[["access_effect"]], how="inner")
            diff = joined["intersection_access_effect"].to_numpy(dtype=float) - joined["access_effect"].to_numpy(dtype=float)
            effect, p = signflip_p(diff, rng, args.n_perm)
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
                    "passes": bool(np.isfinite(effect) and effect > 0 and np.isfinite(p) and p <= args.alpha),
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
        proxy_pass = levels.get("operator_proxy_ab", False)
        if strict_pass and not proxy_pass and frozen_pass:
            interpretation = "exceeds_strict_past_ab_but_not_operator_proxy"
        elif strict_pass and expanded_pass and proxy_pass and frozen_pass:
            interpretation = "exceeds_all_ab_controls"
        elif not strict_pass and frozen_pass:
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
                "passes_operator_proxy_ab": proxy_pass,
                "b71a_supported": bool(strict_pass and frozen_pass),
                "interpretation": interpretation,
            }
        )
    return pd.DataFrame(rows)


def write_report(path: Path, summary: pd.DataFrame, comparison: pd.DataFrame, args: argparse.Namespace) -> None:
    supported = int(summary["b71a_supported"].sum()) if not summary.empty else 0
    strict = int(summary["passes_strict_past_ab_only"].sum()) if not summary.empty else 0
    lines = [
        "# Stage B7.1a A/B-History Control Validity Audit",
        "",
        "Status: executed after writing Stage_B7_1a_preregistration.md.",
        "",
        "## Result",
        "",
        f"- B7.1a-supported regimes: {supported} / {len(summary)}",
        f"- regimes passing strict_past_ab_only: {strict} / {len(summary)}",
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
        "If true C does not beat strict_past_ab_only, the B6 C effect should be read as A/B-history-derived feature transformation under the current implementation.",
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
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6p = load_module("b6p_for_b71a", B6P_SCRIPT)
    b71 = load_module("b71_for_b71a", B71_SCRIPT)
    b6l, table = b6p.build_table(build_args(args))
    intersection = b71.build_intersection_arms(table, b6p, b6l, build_args(args))
    control_frames = []
    for level in ["strict_past_ab_only", "expanded_past_ab_only", "operator_proxy_ab"]:
        for endpoint in ENDPOINTS:
            control_frames.append(build_control_access(table, b6p, b6l, level, endpoint, args))
    controls = pd.concat(control_frames, ignore_index=True)
    comparison = compare_true_to_controls(intersection, controls, args)
    frozen = pd.read_csv(REPO / "reports/stage_b7_1/Stage_B7_1_b6_regime_freeze.csv")
    summary = classify(comparison, frozen)
    controls.to_csv(outdir / "Stage_B7_1a_ab_control_events.csv", index=False)
    comparison.to_csv(outdir / "Stage_B7_1a_control_level_comparison.csv", index=False)
    summary.to_csv(outdir / "Stage_B7_1a_primary_classification.csv", index=False)
    write_report(outdir / "Stage_B7_1a_preregistered_summary.md", summary, comparison, args)
    print("\nStage B7.1a outputs")
    print(f"- output_dir: {outdir}")
    print(f"- b71a_supported: {int(summary['b71a_supported'].sum())} / {len(summary)}")
    print(f"- strict_past_ab_pass: {int(summary['passes_strict_past_ab_only'].sum())} / {len(summary)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_1a")
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
