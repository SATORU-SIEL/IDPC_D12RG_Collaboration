#!/usr/bin/env python3
"""Stage B7.2e side-polarity decomposition and standpoint meaning audit."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import test_Stage_B7_1a_ab_history_control_validity as b71a  # noqa: E402


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_b72c():
    return load_module("b72c_for_b72e", SCRIPTS / "test_Stage_B7_2c_directed_provenance_reconstruction_audit.py")


ENDPOINTS = b71a.ENDPOINTS
OPERATORS = b71a.OPERATORS
DIRECTIONS = ["A_to_C_to_B", "B_to_C_to_A"]
CONTROL_LEVELS = [
    "unsigned_side_gap",
    "signed_ac_minus_bc",
    "polarity_sign_only",
    "polarity_magnitude_only",
    "direction_conditioned_side_polarity",
    "receiver_side_only",
    "giver_side_only",
    "standpoint_polarity_preserved",
    "standpoint_polarity_inverted",
    "phase_tfc_matched_polarity_control",
    "endpoint_o1o2_reference",
]


def qbin(series: pd.Series, q: int = 3) -> pd.Series:
    return b71a.qbin(pd.to_numeric(series, errors="coerce"), q)


def sign_bin(series: pd.Series) -> pd.Series:
    vals = pd.to_numeric(series, errors="coerce")
    return pd.Series(np.where(vals.gt(0), "pos", np.where(vals.lt(0), "neg", "zero")), index=series.index)


def features(table: pd.DataFrame, b72c, b72b, direction: str, seed: int) -> pd.DataFrame:
    out = b72c.add_reconstruction_features(table, b72b, direction, seed).copy()
    ac = pd.to_numeric(out.get("A_C", pd.Series(np.nan, index=out.index)), errors="coerce")
    bc = pd.to_numeric(out.get("B_C", pd.Series(np.nan, index=out.index)), errors="coerce")
    out["ac_minus_bc"] = ac - bc
    out["abs_ac_minus_bc"] = (ac - bc).abs()
    out["polarity_sign"] = sign_bin(out["standpoint_polarity"])
    out["polarity_magnitude"] = pd.to_numeric(out["standpoint_polarity"], errors="coerce").abs()
    return out


def parts_for_level(data: pd.DataFrame, level: str) -> list[pd.Series]:
    base = [
        "dir=" + data["direction_code"].astype(str),
        "side=" + data["side_identity"].astype(str),
    ]
    if level == "unsigned_side_gap":
        return base + ["gap=" + qbin(data["abs_ac_minus_bc"], 3).astype(str)]
    if level == "signed_ac_minus_bc":
        return base + ["signed=" + qbin(data["ac_minus_bc"], 3).astype(str)]
    if level == "polarity_sign_only":
        return base + ["sign=" + data["polarity_sign"].astype(str)]
    if level == "polarity_magnitude_only":
        return base + ["mag=" + qbin(data["polarity_magnitude"], 3).astype(str)]
    if level == "direction_conditioned_side_polarity":
        return base + ["sp=" + qbin(data["standpoint_polarity"], 3).astype(str)]
    if level == "receiver_side_only":
        return base + ["receiver=" + qbin(data["receiver_side"], 3).astype(str)]
    if level == "giver_side_only":
        return base + ["giver=" + qbin(data["sender_side"], 3).astype(str)]
    if level == "standpoint_polarity_preserved":
        return base + [
            "ss=" + qbin(data["standpoint_side"], 3).astype(str),
            "sp=" + qbin(data["standpoint_polarity"], 3).astype(str),
        ]
    if level == "standpoint_polarity_inverted":
        return base + [
            "ss=" + qbin(data["inverted_standpoint_side"], 3).astype(str),
            "sp=" + qbin(data["inverted_standpoint_polarity"], 3).astype(str),
        ]
    if level == "phase_tfc_matched_polarity_control":
        return [
            "phase=" + data.get("phase_quadrant", pd.Series(["missing"] * len(data), index=data.index)).astype(str),
            "tfc=" + data.get("tfc_bin", pd.Series(["missing"] * len(data), index=data.index)).astype(str),
            "dir=" + data["direction_code"].astype(str),
            "shufsp=" + qbin(data["standpoint_polarity_shuffled"], 3).astype(str),
        ]
    raise ValueError(f"unknown level {level}")


def state_labels(table: pd.DataFrame, b72c, b72b, direction: str, level: str, seed: int) -> pd.Series:
    data = features(table, b72c, b72b, direction, seed)
    parts = parts_for_level(data, level)
    return pd.Series(["|".join(vals) for vals in zip(*[p.astype(str) for p in parts])], index=table.index)


def train_mapping(train: pd.DataFrame, b6l, endpoint: str, args: argparse.Namespace) -> tuple[dict[str, np.ndarray], np.ndarray]:
    reward_cols = b6l.operator_reward_columns(endpoint)
    global_means = np.asarray([pd.to_numeric(train[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
    global_weights = b71a.softmax(global_means, args.temperature)
    mapping: dict[str, np.ndarray] = {}
    for state, sub in train.groupby("control_state", sort=False):
        if len(sub) < args.min_state_events:
            continue
        means = np.asarray([pd.to_numeric(sub[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
        mapping[str(state)] = b71a.softmax(means, args.temperature)
    return mapping, global_weights


def build_custom_access(table: pd.DataFrame, b6p, b6l, b72c, b72b, level: str, endpoint: str, direction: str, args: argparse.Namespace) -> pd.DataFrame:
    data = table.copy()
    data["control_state"] = state_labels(data, b72c, b72b, direction, level, args.seed)
    folds = b71a.make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy()
        mapping, global_weights = train_mapping(train, b6l, endpoint, args)
        for _, row in test.iterrows():
            weights = mapping.get(str(row["control_state"]), global_weights)
            base_readouts = b6p.baseline_readouts(row, b6l, endpoint)
            access = b71a.row_reward(row, b6l, weights, endpoint)
            rows.append(
                {
                    "control_level": level,
                    "endpoint": endpoint,
                    "direction": direction,
                    "fold": fold_index,
                    "label": row["label"],
                    "idx_in_session": row["idx_in_session"],
                    "control_state": str(row["control_state"]),
                    "access_readout": access,
                    "baseline_max": base_readouts["baseline_max"],
                    "access_effect": access - base_readouts["baseline_max"] if np.isfinite(access) and np.isfinite(base_readouts["baseline_max"]) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def build_access(table: pd.DataFrame, b6p, b6l, b72c, b72b, level: str, endpoint: str, direction: str, args: argparse.Namespace) -> pd.DataFrame:
    if level == "endpoint_o1o2_reference":
        out = b72c.build_access(table, b6p, b6l, b72b, "endpoint_o1o2_reference", endpoint, direction, args)
        out["control_level"] = level
        return out
    return build_custom_access(table, b6p, b6l, b72c, b72b, level, endpoint, direction, args)


def compare(intersection: pd.DataFrame, controls: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 72050)
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


def summarize(comparison: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frozen = pd.read_csv(REPO / "reports/stage_b7_1/Stage_B7_1_b6_regime_freeze.csv")
    frozen_keys = set(tuple(x) for x in frozen[frozen["b71_frozen_b6_supported"]][["mode", "endpoint", "direction_with_c"]].to_numpy())
    comp = comparison.copy()
    comp["frozen_b6_supported"] = [(r.mode, r.endpoint, r.direction) in frozen_keys for r in comp.itertuples(index=False)]
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
    pivot = frozen_comp.pivot_table(index=["mode", "endpoint", "direction"], columns="control_level", values="c_beats_control", aggfunc="first").reset_index()
    return summary, pivot, classify(summary)


def bounds(summary: pd.DataFrame, level: str) -> int:
    row = summary[summary["control_level"].eq(level)]
    return 0 if row.empty else int(row.iloc[0]["control_bounds_c_count"])


def mean_effect(summary: pd.DataFrame, level: str) -> float:
    row = summary[summary["control_level"].eq(level)]
    return np.nan if row.empty else float(row.iloc[0]["mean_true_minus_control"])


def classify(summary: pd.DataFrame) -> pd.DataFrame:
    n = int(summary["frozen_regimes"].max()) if not summary.empty else 0
    rows = [
        ("unsigned_side_gap_sufficient", bounds(summary, "unsigned_side_gap") == n, f"unsigned_side_gap bounds C {bounds(summary, 'unsigned_side_gap')}/{n}"),
        ("signed_ac_bc_contrast_sufficient", bounds(summary, "signed_ac_minus_bc") == n, f"signed_ac_minus_bc bounds C {bounds(summary, 'signed_ac_minus_bc')}/{n}"),
        ("polarity_sign_sufficient", bounds(summary, "polarity_sign_only") == n, f"polarity_sign_only bounds C {bounds(summary, 'polarity_sign_only')}/{n}"),
        ("polarity_magnitude_sufficient", bounds(summary, "polarity_magnitude_only") == n, f"polarity_magnitude_only bounds C {bounds(summary, 'polarity_magnitude_only')}/{n}"),
        ("direction_conditioned_polarity_required", bounds(summary, "direction_conditioned_side_polarity") > max(bounds(summary, "signed_ac_minus_bc"), bounds(summary, "unsigned_side_gap")), f"direction_conditioned_side_polarity bounds C {bounds(summary, 'direction_conditioned_side_polarity')}/{n}; signed bounds C {bounds(summary, 'signed_ac_minus_bc')}/{n}; unsigned bounds C {bounds(summary, 'unsigned_side_gap')}/{n}"),
        ("receiver_side_sufficient", bounds(summary, "receiver_side_only") == n, f"receiver_side_only bounds C {bounds(summary, 'receiver_side_only')}/{n}"),
        ("giver_side_sufficient", bounds(summary, "giver_side_only") == n, f"giver_side_only bounds C {bounds(summary, 'giver_side_only')}/{n}"),
        ("standpoint_polarity_supported", bounds(summary, "standpoint_polarity_preserved") == n, f"standpoint_polarity_preserved bounds C {bounds(summary, 'standpoint_polarity_preserved')}/{n}"),
        ("standpoint_inversion_breaks_signal", bounds(summary, "standpoint_polarity_preserved") > bounds(summary, "standpoint_polarity_inverted"), f"preserved bounds C {bounds(summary, 'standpoint_polarity_preserved')}/{n}; inverted bounds C {bounds(summary, 'standpoint_polarity_inverted')}/{n}"),
        ("phase_tfc_surrogate_supported", bounds(summary, "phase_tfc_matched_polarity_control") == n, f"phase_tfc_matched_polarity_control bounds C {bounds(summary, 'phase_tfc_matched_polarity_control')}/{n}"),
        ("endpoint_o1o2_effect_size_gap_persists", mean_effect(summary, "endpoint_o1o2_reference") < min(mean_effect(summary, x) for x in CONTROL_LEVELS if x != "endpoint_o1o2_reference"), f"endpoint_o1o2 mean true-minus-control {mean_effect(summary, 'endpoint_o1o2_reference'):.4f}"),
    ]
    unresolved = not any(r[1] for r in rows[:10])
    rows.append(("unresolved_side_polarity_meaning", unresolved, "no endpoint-free side-polarity interpretation uniquely supported"))
    return pd.DataFrame([{"criterion": c, "supported": bool(s), "basis": b} for c, s, b in rows])


def write_report(path: Path, summary: pd.DataFrame, classification: pd.DataFrame, pivot: pd.DataFrame, args: argparse.Namespace) -> None:
    lines = [
        "# Stage B7.2e Side-Polarity Decomposition and Standpoint Meaning Audit",
        "",
        "Status: executed after writing Stage_B7_2e_preregistration.md.",
        "",
        "## Result",
        "",
    ]
    if not summary.empty:
        n = int(summary["frozen_regimes"].max())
        lines.append(f"- frozen B6-supported regimes tested: {n} / 24")
        for level in CONTROL_LEVELS:
            row = summary[summary["control_level"].eq(level)]
            if not row.empty:
                r = row.iloc[0]
                lines.append(f"- {level} bounds true C: {int(r['control_bounds_c_count'])} / {int(r['frozen_regimes'])}; lets true C win: {int(r['c_beats_count'])} / {int(r['frozen_regimes'])}")
    lines += [
        "",
        "## Primary Classification",
        "",
        classification.to_csv(index=False).strip(),
        "",
        "## Component Summary",
        "",
        summary.to_csv(index=False).strip(),
        "",
        "## Frozen-Regime Pass Matrix",
        "",
        pivot.to_csv(index=False).strip(),
        "",
        "## Interpretation Boundary",
        "",
        "B7.2e decomposes side polarity. It is not a C12 confirmation test.",
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
    b72c = load_b72c()
    b72b = b72c.load_b72b()
    b6p = b71a.load_module("b6p_for_b72e", b71a.B6P_SCRIPT)
    b71 = b71a.load_module("b71_for_b72e", b71a.B71_SCRIPT)
    b6l, table = b6p.build_table(b71a.build_args(args))
    intersection = b71.build_intersection_arms(table, b6p, b6l, b71a.build_args(args))
    controls = pd.concat(
        [
            build_access(table, b6p, b6l, b72c, b72b, level, endpoint, direction, args)
            for level in CONTROL_LEVELS
            for endpoint in ENDPOINTS
            for direction in DIRECTIONS
        ],
        ignore_index=True,
    )
    comparison = compare(intersection, controls, args)
    summary, pivot, classification = summarize(comparison)
    controls.to_csv(outdir / "Stage_B7_2e_control_events.csv", index=False)
    comparison.to_csv(outdir / "Stage_B7_2e_comparison.csv", index=False)
    summary.to_csv(outdir / "Stage_B7_2e_component_summary.csv", index=False)
    pivot.to_csv(outdir / "Stage_B7_2e_frozen_pass_matrix.csv", index=False)
    classification.to_csv(outdir / "Stage_B7_2e_primary_classification.csv", index=False)
    write_report(outdir / "Stage_B7_2e_preregistered_summary.md", summary, classification, pivot, args)
    print("\nStage B7.2e audit")
    print(f"- output_dir: {outdir}")
    print(summary.to_string(index=False))
    print("\nClassification")
    print(classification.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_2e")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=71205)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
