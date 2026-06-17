#!/usr/bin/env python3
"""Stage B7.1 preregistered C-mediated intersection access audit.

This script executes the frozen B7.1 discrimination audit derived from B6.
It is intentionally conservative: the primary endpoint is C-mediated
intersection access, while GMR72 and C12 are secondary modules.
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

B6P_SCRIPT = SCRIPTS / "private_B6P_objectification_vs_intersection_audit.py"
B6V_SCRIPT = SCRIPTS / "private_B6V_access_without_c_audit.py"
B6W_SCRIPT = SCRIPTS / "private_B6W_c_substitution_audit.py"
B6Z_SCRIPT = SCRIPTS / "private_B6Z_phase_collapse_boundary_audit.py"

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
CORE_FAKE_CONTROLS = ["shuffled_c", "phase_rotated_c", "random_c", "balanced_c", "foreign_label_c"]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 710)
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


def normalize(weights: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    weights = np.where(np.isfinite(weights), weights, 0.0)
    weights = np.clip(weights, 0.0, None)
    total = float(np.sum(weights))
    if total <= 1e-12:
        return np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    return weights / total


def operator_values(row: pd.Series, b6l, endpoint: str) -> np.ndarray:
    cols = b6l.operator_reward_columns(endpoint)
    return np.asarray([pd.to_numeric(row.get(cols[op], np.nan), errors="coerce") for op in OPERATORS], dtype=float)


def weighted_reward(row: pd.Series, b6l, weights: np.ndarray, endpoint: str) -> float:
    vals = operator_values(row, b6l, endpoint)
    mask = np.isfinite(vals) & np.isfinite(weights)
    if not mask.any():
        return np.nan
    w = normalize(weights[mask])
    return float(np.sum(vals[mask] * w))


def softmax(scores: np.ndarray, temperature: float) -> np.ndarray:
    scores = np.asarray(scores, dtype=float)
    finite = np.isfinite(scores)
    if not finite.any():
        return np.ones(len(scores), dtype=float) / len(scores)
    fill = float(np.nanmin(scores[finite]))
    s = np.where(finite, scores, fill)
    s = s / max(float(temperature), 1e-6)
    s = s - float(np.nanmax(s))
    e = np.exp(s)
    if not np.isfinite(np.sum(e)) or np.sum(e) <= 0:
        return np.ones(len(scores), dtype=float) / len(scores)
    return e / np.sum(e)


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


def build_table(args: argparse.Namespace):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6p = load_module("b6p_for_b71", B6P_SCRIPT)
    b6l, table = b6p.build_table(build_args(args))
    return b6p, b6l, table


def ab_history_state_labels(table: pd.DataFrame) -> pd.Series:
    out = table.copy()
    for source, name in [
        ("A_B", "ab_hist"),
        ("O1_lag0_AB_raw", "lag0_hist"),
        ("O2_lag5_AB_raw", "lag5_hist"),
    ]:
        vals = pd.to_numeric(out[source], errors="coerce")
        try:
            out[name] = pd.qcut(vals.rank(method="first"), 3, labels=["low", "mid", "high"])
        except ValueError:
            out[name] = "flat"
    return (
        "ab=" + out["ab_hist"].astype(str)
        + "|lag0=" + out["lag0_hist"].astype(str)
        + "|lag5=" + out["lag5_hist"].astype(str)
    )


def train_ab_history_policy(train: pd.DataFrame, b6l, endpoint: str, min_state_events: int, temperature: float) -> tuple[dict[str, np.ndarray], np.ndarray]:
    reward_cols = b6l.operator_reward_columns(endpoint)
    ab_ops = ["O1_lag0_AB", "O2_lag5_AB"]
    train = train.copy()
    train["ab_history_state"] = ab_history_state_labels(train)
    global_means = np.asarray([pd.to_numeric(train[reward_cols[op]], errors="coerce").mean() if op in ab_ops else -np.inf for op in OPERATORS], dtype=float)
    global_weights = softmax(global_means, temperature)
    mapping: dict[str, np.ndarray] = {}
    for state, sub in train.groupby("ab_history_state", sort=False):
        if len(sub) < min_state_events:
            continue
        means = np.asarray([pd.to_numeric(sub[reward_cols[op]], errors="coerce").mean() if op in ab_ops else -np.inf for op in OPERATORS], dtype=float)
        mapping[str(state)] = softmax(means, temperature)
    return mapping, global_weights


def build_ab_history_access(table: pd.DataFrame, b6p, b6l, endpoint: str, args: argparse.Namespace) -> pd.DataFrame:
    rows = []
    data = table.copy()
    data["ab_history_state"] = ab_history_state_labels(data)
    folds = make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    for fold_index, labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy()
        mapping, global_weights = train_ab_history_policy(train, b6l, endpoint, args.min_state_events, args.temperature)
        for _, row in test.iterrows():
            state = str(row["ab_history_state"])
            weights = mapping.get(state, global_weights)
            base = b6p.baseline_readouts(row, b6l, endpoint)
            access = weighted_reward(row, b6l, weights, endpoint)
            rows.append(
                {
                    "endpoint": endpoint,
                    "fold": fold_index,
                    "label": row["label"],
                    "idx_in_session": row["idx_in_session"],
                    "ab_history_state": state,
                    "access_readout": access,
                    "baseline_max": base["baseline_max"],
                    "access_effect": access - base["baseline_max"] if np.isfinite(access) and np.isfinite(base["baseline_max"]) else np.nan,
                    "control_kind": "ab_history_policy",
                }
            )
    return pd.DataFrame(rows)


def compare_true_to_ab_history(intersection: pd.DataFrame, ab_history: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 720)
    rows = []
    for (mode, endpoint, direction), sub in intersection.groupby(["mode", "endpoint", "direction"], sort=False):
        true = sub[sub["arm_kind"].eq("true")].set_index(["fold", "label", "idx_in_session"])
        ab = ab_history[ab_history["endpoint"].eq(endpoint)].set_index(["fold", "label", "idx_in_session"])
        joined = true[["intersection_access_effect"]].join(ab[["access_effect"]], how="inner")
        diff = joined["intersection_access_effect"].to_numpy(dtype=float) - joined["access_effect"].to_numpy(dtype=float)
        effect, p = signflip_p(diff, rng, args.n_perm)
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "direction": direction,
                "comparison": "true_c_intersection_vs_ab_history_policy",
                "mean_true_c": float(np.nanmean(joined["intersection_access_effect"])),
                "mean_ab_history": float(np.nanmean(joined["access_effect"])),
                "effect": effect,
                "p_greater": p,
                "n_pairs": int(np.isfinite(diff).sum()),
                "passes": bool(np.isfinite(effect) and effect > 0 and np.isfinite(p) and p <= args.alpha),
            }
        )
    return pd.DataFrame(rows)


def build_intersection_arms(table: pd.DataFrame, b6p, b6l, args: argparse.Namespace) -> pd.DataFrame:
    frames = []
    b6_args = build_args(args)
    for mode in MODES:
        for endpoint in ENDPOINTS:
            _, inter, _ = b6p.build_arms(table, b6l, mode, endpoint, b6_args)
            frames.append(inter)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def load_existing_regime_summaries() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    b6v = pd.read_csv(REPO / "reports/private_b6v_access_without_c/private_B6V_access_without_c_contrast.csv")
    b6w = pd.read_csv(REPO / "reports/private_b6w_c_substitution/private_B6W_c_substitution_summary.csv")
    b6z = pd.read_csv(REPO / "reports/private_b6z_phase_collapse_boundary/private_B6Z_phase_collapse_boundary_summary.csv")
    return b6v, b6w, b6z


def freeze_b6_regimes() -> pd.DataFrame:
    b6v, b6w, b6z = load_existing_regime_summaries()
    out = b6v.merge(
        b6w[["mode", "endpoint", "direction", "true_c_non_substitutable", "mean_effect_true_minus_fake"]],
        left_on=["mode", "endpoint", "direction_with_c"],
        right_on=["mode", "endpoint", "direction"],
        how="left",
    )
    out = out.merge(
        b6z[["mode", "endpoint", "direction", "phase_collapse_detected", "first_significant_collapse_degrees", "narrow_boundary_supported"]],
        left_on=["mode", "endpoint", "direction_with_c"],
        right_on=["mode", "endpoint", "direction"],
        how="left",
        suffixes=("_w", "_z"),
    )
    out["b71_frozen_b6_supported"] = (
        out["c_necessary_pattern"].fillna(False)
        & out["true_c_non_substitutable"].fillna(False)
        & out["phase_collapse_detected"].fillna(False)
    )
    return out


def summarize_fake_controls() -> pd.DataFrame:
    _, b6w, _ = load_existing_regime_summaries()
    rows = []
    for _, row in b6w.iterrows():
        passes = [bool(row.get(f"passes_{kind}", False)) for kind in CORE_FAKE_CONTROLS]
        rows.append(
            {
                "mode": row["mode"],
                "endpoint": row["endpoint"],
                "direction": row["direction"],
                "comparison": "true_c_vs_core_fake_c_controls",
                "passes_all_core_fake_controls": bool(all(passes)),
                "n_core_fake_controls_passed": int(sum(passes)),
                "mean_effect_true_minus_fake": row["mean_effect_true_minus_fake"],
            }
        )
    return pd.DataFrame(rows)


def summarize_phase_controls() -> pd.DataFrame:
    _, _, b6z = load_existing_regime_summaries()
    return b6z.rename(columns={"direction": "direction"})[
        [
            "mode",
            "endpoint",
            "direction",
            "phase_collapse_detected",
            "first_significant_collapse_degrees",
            "mean_true_minus_shift",
            "narrow_boundary_supported",
        ]
    ].copy()


def summarize_gmr72_angles(args: argparse.Namespace) -> pd.DataFrame:
    path = REPO / "reports/private_b6os_gmr72_bridge_mechanism/private_B6OS_bridge_variant_aggregate.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    return df.copy()


def c12_reconnection_screen() -> pd.DataFrame:
    rows = []
    b55 = pd.read_csv(REPO / "reports/stage_b5_5/Stage_B5_5_c12_single_ring_summary.csv")
    future = pd.read_csv(REPO / "reports/stage_b5_5/Stage_B5_5_future_ab_summary.csv")
    b56_path = REPO / "reports/private_b5_6_ontological_c_projection_audit/private_B5_6_projection_c12_summary.csv"
    b56 = pd.read_csv(b56_path) if b56_path.exists() else pd.DataFrame()
    for _, row in b55.sort_values("mean_bounded_differentiated_recovery", ascending=False).iterrows():
        rows.append(
            {
                "module": "b55_c12_single_ring",
                "condition": row["event_class"],
                "role": row["event_role"],
                "metric": "mean_bounded_differentiated_recovery",
                "value": row["mean_bounded_differentiated_recovery"],
                "q_value": row.get("b55_c12_q", np.nan),
                "interpretation": "C12 ranking differs from future_AB ranking; topology readout is not identical to future AB optimizer.",
            }
        )
    for _, row in future[future["delta"].eq(5)].sort_values("mean_future_AB", ascending=False).iterrows():
        rows.append(
            {
                "module": "b55_future_ab_delta5",
                "condition": row["event_class"],
                "role": "future_ab",
                "metric": "mean_future_AB",
                "value": row["mean_future_AB"],
                "q_value": row.get("future_ab_primary_q", np.nan),
                "interpretation": "Future AB comparator for C12 reconnection boundary.",
            }
        )
    if not b56.empty:
        for _, row in b56.sort_values("mean_bounded_differentiated_recovery", ascending=False).iterrows():
            rows.append(
                {
                    "module": "b56_projection_c12",
                    "condition": row["event_class"],
                    "role": row["event_role"],
                    "metric": "mean_bounded_differentiated_recovery",
                    "value": row["mean_bounded_differentiated_recovery"],
                    "q_value": row.get("b56_projection_q", np.nan),
                    "interpretation": "Projection screen for secondary C12 topology-readout module.",
                }
            )
    return pd.DataFrame(rows)


def classify_primary(ab_comp: pd.DataFrame, fake: pd.DataFrame, phase: pd.DataFrame, frozen: pd.DataFrame) -> pd.DataFrame:
    rows = []
    fake_idx = fake.set_index(["mode", "endpoint", "direction"])
    phase_idx = phase.set_index(["mode", "endpoint", "direction"])
    frozen_idx = frozen.set_index(["mode", "endpoint", "direction_with_c"])
    for _, row in ab_comp.iterrows():
        key = (row["mode"], row["endpoint"], row["direction"])
        fake_pass = bool(fake_idx.loc[key, "passes_all_core_fake_controls"]) if key in fake_idx.index else False
        phase_pass = bool(phase_idx.loc[key, "phase_collapse_detected"]) if key in phase_idx.index else False
        frozen_pass = bool(frozen_idx.loc[key, "b71_frozen_b6_supported"]) if key in frozen_idx.index else False
        supported = bool(row["passes"] and fake_pass and phase_pass and frozen_pass)
        rows.append(
            {
                "mode": row["mode"],
                "endpoint": row["endpoint"],
                "direction": row["direction"],
                "passes_ab_history": bool(row["passes"]),
                "passes_fake_c": fake_pass,
                "passes_phase_collapse": phase_pass,
                "frozen_b6_supported": frozen_pass,
                "b71_primary_supported": supported,
                "effect_vs_ab_history": row["effect"],
                "p_vs_ab_history": row["p_greater"],
            }
        )
    return pd.DataFrame(rows)


def write_report(path: Path, primary: pd.DataFrame, ab_comp: pd.DataFrame, fake: pd.DataFrame, phase: pd.DataFrame, frozen: pd.DataFrame, c12: pd.DataFrame, gmr: pd.DataFrame, args: argparse.Namespace) -> None:
    n_primary = int(primary["b71_primary_supported"].sum()) if not primary.empty else 0
    lines = [
        "# Stage B7.1 Preregistered Intersection Access Audit",
        "",
        "Status: executed after writing Stage_B7_1_preregistration.md.",
        "",
        "## Primary Result",
        "",
        f"- B7.1 primary-supported regimes: {n_primary} / {len(primary)}",
        f"- frozen B6-supported regimes carried into B7.1: {int(frozen['b71_frozen_b6_supported'].sum())} / {len(frozen)}",
        "",
        "Primary support requires: true C-mediated access > A/B-history policy, fake-C non-substitutability, phase-collapse, and frozen B6-supported status.",
        "",
        "## Primary Discrimination Summary",
        "",
        primary.to_csv(index=False).strip(),
        "",
        "## A/B-History Control Comparison",
        "",
        ab_comp.to_csv(index=False).strip(),
        "",
        "## Fake-C Control Summary",
        "",
        fake.to_csv(index=False).strip(),
        "",
        "## Phase-Collapse Summary",
        "",
        phase.to_csv(index=False).strip(),
        "",
        "## Frozen B6 Regime Table",
        "",
        frozen.to_csv(index=False).strip(),
        "",
        "## Secondary GMR72 Module",
        "",
        gmr.to_csv(index=False).strip() if not gmr.empty else "No B6OS angular aggregate table found.",
        "",
        "## Secondary C12 Reconnection Screen",
        "",
        c12.to_csv(index=False).strip(),
        "",
        "## Interpretation Boundary",
        "",
        "C12 is secondary. B7.1 tests C-mediated intersection access first, then screens whether C12 remains a candidate downstream topology-readout surface.",
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
    b6p, b6l, table = build_table(args)
    table.to_csv(outdir / "Stage_B7_1_state_table.csv", index=False)

    intersection = build_intersection_arms(table, b6p, b6l, args)
    intersection.to_csv(outdir / "Stage_B7_1_intersection_access_events.csv", index=False)

    ab_frames = [build_ab_history_access(table, b6p, b6l, endpoint, args) for endpoint in ENDPOINTS]
    ab_history = pd.concat(ab_frames, ignore_index=True)
    ab_history.to_csv(outdir / "Stage_B7_1_ab_history_access_events.csv", index=False)

    ab_comp = compare_true_to_ab_history(intersection, ab_history, args)
    fake = summarize_fake_controls()
    phase = summarize_phase_controls()
    frozen = freeze_b6_regimes()
    primary = classify_primary(ab_comp, fake, phase, frozen)
    gmr = summarize_gmr72_angles(args)
    c12 = c12_reconnection_screen()

    ab_comp.to_csv(outdir / "Stage_B7_1_ab_history_control_comparison.csv", index=False)
    fake.to_csv(outdir / "Stage_B7_1_fake_c_control_summary.csv", index=False)
    phase.to_csv(outdir / "Stage_B7_1_phase_control_summary.csv", index=False)
    frozen.to_csv(outdir / "Stage_B7_1_b6_regime_freeze.csv", index=False)
    primary.to_csv(outdir / "Stage_B7_1_primary_discrimination_summary.csv", index=False)
    gmr.to_csv(outdir / "Stage_B7_1_gmr72_angular_response_summary.csv", index=False)
    c12.to_csv(outdir / "Stage_B7_1_c12_reconnection_screen.csv", index=False)
    write_report(outdir / "Stage_B7_1_preregistered_summary.md", primary, ab_comp, fake, phase, frozen, c12, gmr, args)

    print("\nStage B7.1 outputs")
    print(f"- output_dir: {outdir}")
    print(f"- primary_supported: {int(primary['b71_primary_supported'].sum())} / {len(primary)}")
    print(f"- frozen_b6_supported: {int(frozen['b71_frozen_b6_supported'].sum())} / {len(frozen)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_1")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=71010)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
