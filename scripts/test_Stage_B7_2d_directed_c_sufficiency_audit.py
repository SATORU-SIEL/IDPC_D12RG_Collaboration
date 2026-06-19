#!/usr/bin/env python3
"""Stage B7.2d directed-C sufficiency and provenance-dilution audit."""

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
    return load_module("b72c_for_b72d", SCRIPTS / "test_Stage_B7_2c_directed_provenance_reconstruction_audit.py")


ENDPOINTS = b71a.ENDPOINTS
OPERATORS = b71a.OPERATORS
DIRECTIONS = ["A_to_C_to_B", "B_to_C_to_A"]
CONTROL_LEVELS = [
    "directed_c_compact",
    "directed_c_minimal",
    "directed_c_with_side_polarity",
    "directed_c_with_endpoint_free_transport",
    "provenance_add_phase_strength",
    "provenance_add_tfc_memory",
    "provenance_add_fes",
    "full_directed_provenance",
    "regularized_directed_provenance",
    "provenance_shuffled_control",
    "endpoint_o1o2_reference",
    "directed_transport_closure_o1o2",
]
REFERENCE_LEVELS = {
    "endpoint_o1o2_reference": "endpoint_o1o2_reference",
    "directed_transport_closure_o1o2": "directed_transport_closure_o1o2",
}


def qbin(series: pd.Series, q: int = 3) -> pd.Series:
    return b71a.qbin(pd.to_numeric(series, errors="coerce"), q)


def parts_for_level(data: pd.DataFrame, level: str, b72c) -> list[pd.Series]:
    if level == "directed_c_compact":
        return b72c.parts_for_level(data, "directed_c")
    if level == "directed_c_minimal":
        return [
            "dir=" + data["direction_code"].astype(str),
            "side=" + data["side_identity"].astype(str),
        ]
    if level == "directed_c_with_side_polarity":
        return [
            "dir=" + data["direction_code"].astype(str),
            "side=" + data["side_identity"].astype(str),
            "sp=" + qbin(data["standpoint_polarity"], 3).astype(str),
        ]
    if level == "directed_c_with_endpoint_free_transport":
        ac = pd.to_numeric(data.get("A_C", pd.Series(np.nan, index=data.index)), errors="coerce")
        bc = pd.to_numeric(data.get("B_C", pd.Series(np.nan, index=data.index)), errors="coerce")
        return [
            "dir=" + data["direction_code"].astype(str),
            "side=" + data["side_identity"].astype(str),
            "ss=" + qbin(data["standpoint_side"], 3).astype(str),
            "sp=" + qbin(data["standpoint_polarity"], 3).astype(str),
            "acbc=" + qbin(ac - bc, 3).astype(str),
            "ab=" + qbin(data.get("A_B", pd.Series(np.nan, index=data.index)), 3).astype(str),
            "tfc=" + qbin(data.get("TFC_mean", pd.Series(np.nan, index=data.index)), 3).astype(str),
        ]
    if level == "provenance_add_phase_strength":
        return b72c.parts_for_level(data, "directed_c") + [
            "phase=" + qbin(data.get("phase", pd.Series(np.nan, index=data.index)), 3).astype(str),
            "strength=" + qbin(data.get("strength", pd.Series(np.nan, index=data.index)), 3).astype(str),
            "pq=" + data.get("phase_quadrant", pd.Series(["missing"] * len(data), index=data.index)).astype(str),
            "sb=" + data.get("strength_bin", pd.Series(["missing"] * len(data), index=data.index)).astype(str),
        ]
    if level == "provenance_add_tfc_memory":
        return b72c.parts_for_level(data, "directed_c") + [
            "tfcmean=" + qbin(data.get("TFC_mean", pd.Series(np.nan, index=data.index)), 3).astype(str),
            "tfcmin=" + qbin(data.get("TFC_min", pd.Series(np.nan, index=data.index)), 3).astype(str),
            "mem=" + qbin(data.get("C_memory_scalar", pd.Series(np.nan, index=data.index)), 3).astype(str),
            "tfcbin=" + data.get("tfc_bin", pd.Series(["missing"] * len(data), index=data.index)).astype(str),
            "membin=" + data.get("memory_bin", pd.Series(["missing"] * len(data), index=data.index)).astype(str),
        ]
    if level == "provenance_add_fes":
        return b72c.parts_for_level(data, "directed_c") + [
            "fes=" + data.get("fes_phase", pd.Series(["missing"] * len(data), index=data.index)).astype(str),
            "cluster=" + data.get("fes_cluster", pd.Series(["missing"] * len(data), index=data.index)).astype(str),
            "lag=" + data.get("lag_class", pd.Series(["missing"] * len(data), index=data.index)).astype(str),
        ]
    if level == "full_directed_provenance":
        return b72c.parts_for_level(data, "directed_provenance_c")
    if level == "provenance_shuffled_control":
        return b72c.parts_for_level(data, "directed_provenance_side_swapped")
    raise ValueError(f"unknown level {level}")


def state_labels(table: pd.DataFrame, b72c, b72b, direction: str, level: str, seed: int) -> pd.Series:
    data = b72c.add_reconstruction_features(table, b72b, direction, seed)
    parts = parts_for_level(data, level, b72c)
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


def build_regularized_access(table: pd.DataFrame, b6p, b6l, b72c, b72b, endpoint: str, direction: str, args: argparse.Namespace) -> pd.DataFrame:
    data = table.copy()
    data["full_state"] = state_labels(data, b72c, b72b, direction, "full_directed_provenance", args.seed)
    data["compact_state"] = state_labels(data, b72c, b72b, direction, "directed_c_compact", args.seed)
    folds = b71a.make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    reward_cols = b6l.operator_reward_columns(endpoint)
    rows = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy()
        global_means = np.asarray([pd.to_numeric(train[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
        global_weights = b71a.softmax(global_means, args.temperature)
        full_mapping: dict[str, np.ndarray] = {}
        compact_mapping: dict[str, np.ndarray] = {}
        for col, mapping in [("full_state", full_mapping), ("compact_state", compact_mapping)]:
            for state, sub in train.groupby(col, sort=False):
                if len(sub) < args.min_state_events:
                    continue
                means = np.asarray([pd.to_numeric(sub[reward_cols[op]], errors="coerce").mean() for op in OPERATORS], dtype=float)
                mapping[str(state)] = b71a.softmax(means, args.temperature)
        for _, row in test.iterrows():
            if str(row["full_state"]) in full_mapping:
                weights = full_mapping[str(row["full_state"])]
                state = "full|" + str(row["full_state"])
            elif str(row["compact_state"]) in compact_mapping:
                weights = compact_mapping[str(row["compact_state"])]
                state = "compact|" + str(row["compact_state"])
            else:
                weights = global_weights
                state = "global"
            base = b6p.baseline_readouts(row, b6l, endpoint)
            access = b71a.row_reward(row, b6l, weights, endpoint)
            rows.append(
                {
                    "control_level": "regularized_directed_provenance",
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


def build_custom_access(table: pd.DataFrame, b6p, b6l, b72c, b72b, level: str, endpoint: str, direction: str, args: argparse.Namespace) -> pd.DataFrame:
    if level == "regularized_directed_provenance":
        return build_regularized_access(table, b6p, b6l, b72c, b72b, endpoint, direction, args)
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
                    "control_state": str(row["control_state"]),
                    "access_readout": access,
                    "baseline_max": base["baseline_max"],
                    "access_effect": access - base["baseline_max"] if np.isfinite(access) and np.isfinite(base["baseline_max"]) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def build_access(table: pd.DataFrame, b6p, b6l, b72c, b72b, level: str, endpoint: str, direction: str, args: argparse.Namespace) -> pd.DataFrame:
    if level in REFERENCE_LEVELS:
        return b72c.build_access(table, b6p, b6l, b72b, REFERENCE_LEVELS[level], endpoint, direction, args).assign(control_level=level)
    return build_custom_access(table, b6p, b6l, b72c, b72b, level, endpoint, direction, args)


def compare(intersection: pd.DataFrame, controls: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 72040)
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


def classify(summary: pd.DataFrame) -> pd.DataFrame:
    n = int(summary["frozen_regimes"].max()) if not summary.empty else 0
    endpoint_free = [x for x in CONTROL_LEVELS if "o1o2" not in x]
    best_endpoint_free = max([bounds(summary, x) for x in endpoint_free], default=0)
    provenance_levels = [
        "provenance_add_phase_strength",
        "provenance_add_tfc_memory",
        "provenance_add_fes",
        "full_directed_provenance",
    ]
    max_prov = max(bounds(summary, x) for x in provenance_levels)
    rows = [
        ("compact_directed_c_near_sufficient", n > 0 and bounds(summary, "directed_c_compact") >= n - 2, f"directed_c_compact bounds C {bounds(summary, 'directed_c_compact')}/{n}"),
        ("minimal_direction_sufficient", n > 0 and bounds(summary, "directed_c_minimal") == n, f"directed_c_minimal bounds C {bounds(summary, 'directed_c_minimal')}/{n}"),
        ("side_polarity_required", bounds(summary, "directed_c_with_side_polarity") > bounds(summary, "directed_c_minimal"), f"side_polarity bounds C {bounds(summary, 'directed_c_with_side_polarity')}/{n}; minimal bounds C {bounds(summary, 'directed_c_minimal')}/{n}"),
        ("endpoint_free_transport_required", bounds(summary, "directed_c_with_endpoint_free_transport") > bounds(summary, "directed_c_with_side_polarity"), f"endpoint_free_transport bounds C {bounds(summary, 'directed_c_with_endpoint_free_transport')}/{n}; side_polarity bounds C {bounds(summary, 'directed_c_with_side_polarity')}/{n}"),
        ("provenance_dilution_supported", bounds(summary, "directed_c_compact") > max_prov, f"compact bounds C {bounds(summary, 'directed_c_compact')}/{n}; best provenance-addition bounds C {max_prov}/{n}"),
        ("wrong_provenance_supported", max_prov < bounds(summary, "endpoint_o1o2_reference"), f"best provenance-addition bounds C {max_prov}/{n}; endpoint_o1o2_reference bounds C {bounds(summary, 'endpoint_o1o2_reference')}/{n}"),
        ("regularized_provenance_recovers_signal", bounds(summary, "regularized_directed_provenance") >= bounds(summary, "directed_c_compact"), f"regularized bounds C {bounds(summary, 'regularized_directed_provenance')}/{n}; compact bounds C {bounds(summary, 'directed_c_compact')}/{n}"),
        ("endpoint_gap_persists", best_endpoint_free < bounds(summary, "endpoint_o1o2_reference"), f"best endpoint-free bounds C {best_endpoint_free}/{n}; endpoint_o1o2_reference bounds C {bounds(summary, 'endpoint_o1o2_reference')}/{n}"),
        ("unresolved_directed_c_boundary", best_endpoint_free < n and bounds(summary, "endpoint_o1o2_reference") == n, f"best endpoint-free bounds C {best_endpoint_free}/{n}; endpoint_o1o2_reference bounds C {bounds(summary, 'endpoint_o1o2_reference')}/{n}"),
    ]
    return pd.DataFrame([{"criterion": c, "supported": bool(s), "basis": b} for c, s, b in rows])


def write_report(path: Path, summary: pd.DataFrame, classification: pd.DataFrame, pivot: pd.DataFrame, args: argparse.Namespace) -> None:
    lines = [
        "# Stage B7.2d Directed-C Sufficiency and Provenance-Dilution Audit",
        "",
        "Status: executed after writing Stage_B7_2d_preregistration.md.",
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
        "B7.2d diagnoses why compact directed C remained partially strong in B7.2c while full directed provenance collapsed. It is not a C12 confirmation test.",
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
    b6p = b71a.load_module("b6p_for_b72d", b71a.B6P_SCRIPT)
    b71 = b71a.load_module("b71_for_b72d", b71a.B71_SCRIPT)
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
    controls.to_csv(outdir / "Stage_B7_2d_control_events.csv", index=False)
    comparison.to_csv(outdir / "Stage_B7_2d_comparison.csv", index=False)
    summary.to_csv(outdir / "Stage_B7_2d_component_summary.csv", index=False)
    pivot.to_csv(outdir / "Stage_B7_2d_frozen_pass_matrix.csv", index=False)
    classification.to_csv(outdir / "Stage_B7_2d_primary_classification.csv", index=False)
    write_report(outdir / "Stage_B7_2d_preregistered_summary.md", summary, classification, pivot, args)
    print("\nStage B7.2d audit")
    print(f"- output_dir: {outdir}")
    print(summary.to_string(index=False))
    print("\nClassification")
    print(classification.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_2d")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=71204)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
