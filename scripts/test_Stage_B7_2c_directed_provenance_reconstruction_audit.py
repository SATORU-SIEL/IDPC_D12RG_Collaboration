#!/usr/bin/env python3
"""Stage B7.2c directed-provenance C reconstruction audit."""

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


def load_b72b():
    path = SCRIPTS / "test_Stage_B7_2b_side_direction_factorisation_audit.py"
    spec = importlib.util.spec_from_file_location("b72b_for_b72c", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["b72b_for_b72c"] = mod
    spec.loader.exec_module(mod)
    return mod


ENDPOINTS = b71a.ENDPOINTS
OPERATORS = b71a.OPERATORS
DIRECTIONS = ["A_to_C_to_B", "B_to_C_to_A"]
CUSTOM_LEVELS = [
    "scalar_c",
    "directed_c",
    "directed_c_direction_relabel",
    "directed_c_direction_swapped",
    "directed_c_side_shuffled",
    "directed_provenance_c",
    "directed_provenance_side_swapped",
    "directed_provenance_endpoint_pair_swapped",
    "directed_provenance_train_test_mismatch",
]
REFERENCE_LEVELS = {
    "fixed_mask_control": "fixed_b6p_direction_mask",
    "static_scalar_closure": "closure_scalar_only",
    "directed_transport_closure_o1o2": "directed_transport_closure_control",
    "endpoint_o1o2_reference": "endpoint_o1o2_reference",
}
CONTROL_LEVELS = CUSTOM_LEVELS + list(REFERENCE_LEVELS)
MISMATCH_LEVELS = {
    "directed_provenance_train_test_mismatch": (
        "directed_provenance_c",
        "directed_provenance_side_swapped",
    ),
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def qbin(series: pd.Series, q: int = 3) -> pd.Series:
    return b71a.qbin(pd.to_numeric(series, errors="coerce"), q)


def swap_side_string(values: pd.Series) -> pd.Series:
    return values.astype(str).map(lambda x: x.replace("A_side", "TMP").replace("B_side", "A_side").replace("TMP", "B_side"))


def add_reconstruction_features(table: pd.DataFrame, b72b, direction: str, seed: int) -> pd.DataFrame:
    out = b72b.side_features(table, direction, seed).copy()
    rng = np.random.default_rng(seed + 7203)
    out["direction_code_swapped"] = 1.0 - pd.to_numeric(out["direction_code"], errors="coerce")
    out["side_identity"] = out.get("boundary_side", pd.Series(["missing"] * len(out), index=out.index)).astype(str)
    out["side_identity_swapped"] = swap_side_string(out["side_identity"])
    out["standpoint_side_swapped"] = pd.to_numeric(out["inverted_standpoint_side"], errors="coerce")
    out["standpoint_polarity_swapped"] = pd.to_numeric(out["inverted_standpoint_polarity"], errors="coerce")
    out["endpoint_pair_proxy"] = (
        qbin(out["standpoint_side"], 3).astype(str)
        + ":"
        + qbin(out["standpoint_polarity"], 3).astype(str)
        + ":"
        + qbin(out.get("A_B", pd.Series(np.nan, index=out.index)), 3).astype(str)
    )
    out["endpoint_pair_proxy_swapped"] = (
        qbin(out["standpoint_side_swapped"], 3).astype(str)
        + ":"
        + qbin(out["standpoint_polarity_swapped"], 3).astype(str)
        + ":"
        + qbin(out.get("A_B", pd.Series(np.nan, index=out.index)), 3).astype(str)
    )
    out["construction_provenance"] = (
        "phase=" + out.get("phase_quadrant", pd.Series(["missing"] * len(out), index=out.index)).astype(str)
        + "|str=" + out.get("strength_bin", pd.Series(["missing"] * len(out), index=out.index)).astype(str)
        + "|tfc=" + out.get("tfc_bin", pd.Series(["missing"] * len(out), index=out.index)).astype(str)
        + "|mem=" + out.get("memory_bin", pd.Series(["missing"] * len(out), index=out.index)).astype(str)
        + "|fes=" + out.get("fes_phase", pd.Series(["missing"] * len(out), index=out.index)).astype(str)
        + "|cluster=" + out.get("fes_cluster", pd.Series(["missing"] * len(out), index=out.index)).astype(str)
        + "|lag=" + out.get("lag_class", pd.Series(["missing"] * len(out), index=out.index)).astype(str)
    )
    out["side_identity_shuffled"] = out["side_identity"]
    out["standpoint_side_shuffled"] = np.nan
    out["standpoint_polarity_shuffled"] = np.nan
    for _, sub in out.groupby("label", sort=False):
        idx = sub.index.to_numpy()
        perm = idx.copy()
        rng.shuffle(perm)
        out.loc[idx, "side_identity_shuffled"] = out.loc[perm, "side_identity"].to_numpy()
        out.loc[idx, "standpoint_side_shuffled"] = pd.to_numeric(out.loc[perm, "standpoint_side"], errors="coerce").to_numpy(dtype=float)
        out.loc[idx, "standpoint_polarity_shuffled"] = pd.to_numeric(out.loc[perm, "standpoint_polarity"], errors="coerce").to_numpy(dtype=float)
    return out


def parts_for_level(data: pd.DataFrame, level: str) -> list[pd.Series]:
    if level == "scalar_c":
        return ["mem=" + qbin(data.get("C_memory_scalar", pd.Series(np.nan, index=data.index)), 3).astype(str)]
    if level == "directed_c":
        return [
            "dir=" + data["direction_code"].astype(str),
            "side=" + data["side_identity"].astype(str),
            "ss=" + qbin(data["standpoint_side"], 3).astype(str),
            "sp=" + qbin(data["standpoint_polarity"], 3).astype(str),
        ]
    if level == "directed_c_direction_relabel":
        return [
            "dir=" + data["direction_code_swapped"].astype(str),
            "side=" + data["side_identity"].astype(str),
            "ss=" + qbin(data["standpoint_side"], 3).astype(str),
            "sp=" + qbin(data["standpoint_polarity"], 3).astype(str),
        ]
    if level == "directed_c_direction_swapped":
        return [
            "dir=" + data["direction_code_swapped"].astype(str),
            "side=" + data["side_identity_swapped"].astype(str),
            "ss=" + qbin(data["standpoint_side_swapped"], 3).astype(str),
            "sp=" + qbin(data["standpoint_polarity_swapped"], 3).astype(str),
        ]
    if level == "directed_c_side_shuffled":
        return [
            "dir=" + data["direction_code"].astype(str),
            "side=" + data["side_identity_shuffled"].astype(str),
            "ss=" + qbin(data["standpoint_side_shuffled"], 3).astype(str),
            "sp=" + qbin(data["standpoint_polarity_shuffled"], 3).astype(str),
        ]
    if level == "directed_provenance_c":
        return [
            "dir=" + data["direction_code"].astype(str),
            "side=" + data["side_identity"].astype(str),
            "pair=" + data["endpoint_pair_proxy"].astype(str),
            "prov=" + data["construction_provenance"].astype(str),
            "phase=" + qbin(data.get("phase", pd.Series(np.nan, index=data.index)), 3).astype(str),
            "strength=" + qbin(data.get("strength", pd.Series(np.nan, index=data.index)), 3).astype(str),
            "tfcmean=" + qbin(data.get("TFC_mean", pd.Series(np.nan, index=data.index)), 3).astype(str),
        ]
    if level == "directed_provenance_side_swapped":
        return [
            "dir=" + data["direction_code"].astype(str),
            "side=" + data["side_identity_swapped"].astype(str),
            "pair=" + data["endpoint_pair_proxy_swapped"].astype(str),
            "prov=" + data["construction_provenance"].astype(str),
            "phase=" + qbin(data.get("phase", pd.Series(np.nan, index=data.index)), 3).astype(str),
            "strength=" + qbin(data.get("strength", pd.Series(np.nan, index=data.index)), 3).astype(str),
            "tfcmean=" + qbin(data.get("TFC_mean", pd.Series(np.nan, index=data.index)), 3).astype(str),
        ]
    if level == "directed_provenance_endpoint_pair_swapped":
        return [
            "dir=" + data["direction_code"].astype(str),
            "side=" + data["side_identity"].astype(str),
            "pair=" + data["endpoint_pair_proxy_swapped"].astype(str),
            "prov=" + data["construction_provenance"].astype(str),
            "phase=" + qbin(data.get("phase", pd.Series(np.nan, index=data.index)), 3).astype(str),
            "strength=" + qbin(data.get("strength", pd.Series(np.nan, index=data.index)), 3).astype(str),
            "tfcmean=" + qbin(data.get("TFC_mean", pd.Series(np.nan, index=data.index)), 3).astype(str),
        ]
    raise ValueError(f"unknown custom level {level}")


def control_state_labels(table: pd.DataFrame, b72b, direction: str, level: str, seed: int, generic_names: bool = False) -> pd.Series:
    data = add_reconstruction_features(table, b72b, direction, seed)
    parts = parts_for_level(data, level)
    if generic_names:
        parts = ["f" + str(i) + "=" + part.astype(str).str.split("=", n=1).str[-1] for i, part in enumerate(parts)]
    return pd.Series(["|".join(vals) for vals in zip(*[p.astype(str) for p in parts])], index=table.index)


def train_policy(train: pd.DataFrame, b6l, b72b, endpoint: str, direction: str, level: str, args: argparse.Namespace) -> tuple[dict[str, np.ndarray], np.ndarray]:
    train_level = MISMATCH_LEVELS.get(level, (level, level))[0]
    train = train.copy()
    train["control_state"] = control_state_labels(train, b72b, direction, train_level, args.seed, generic_names=level in MISMATCH_LEVELS)
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


def build_custom_access(table: pd.DataFrame, b6p, b6l, b72b, level: str, endpoint: str, direction: str, args: argparse.Namespace) -> pd.DataFrame:
    test_level = MISMATCH_LEVELS.get(level, (level, level))[1]
    data = table.copy()
    data["control_state"] = control_state_labels(data, b72b, direction, test_level, args.seed, generic_names=level in MISMATCH_LEVELS)
    folds = b71a.make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy()
        mapping, global_weights = train_policy(train, b6l, b72b, endpoint, direction, level, args)
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


def build_access(table: pd.DataFrame, b6p, b6l, b72b, level: str, endpoint: str, direction: str, args: argparse.Namespace) -> pd.DataFrame:
    if level in REFERENCE_LEVELS:
        out = b72b.build_control_access(table, b6p, b6l, REFERENCE_LEVELS[level], endpoint, direction, args)
        out["control_level"] = level
        return out
    return build_custom_access(table, b6p, b6l, b72b, level, endpoint, direction, args)


def compare(intersection: pd.DataFrame, controls: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 72022)
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
    classification = classify(summary)
    return summary, pivot, classification


def count_bounds(summary: pd.DataFrame, level: str) -> int:
    row = summary[summary["control_level"].eq(level)]
    if row.empty:
        return 0
    return int(row.iloc[0]["control_bounds_c_count"])


def count_beats(summary: pd.DataFrame, level: str) -> int:
    row = summary[summary["control_level"].eq(level)]
    if row.empty:
        return 0
    return int(row.iloc[0]["c_beats_count"])


def classify(summary: pd.DataFrame) -> pd.DataFrame:
    n = int(summary["frozen_regimes"].max()) if not summary.empty else 0
    directed_bounds = count_bounds(summary, "directed_c")
    provenance_bounds = count_bounds(summary, "directed_provenance_c")
    endpoint_bounds = count_bounds(summary, "endpoint_o1o2_reference")
    rows = [
        {
            "criterion": "directed_c_sufficient",
            "supported": bool(n > 0 and directed_bounds == n),
            "basis": f"directed_c bounds C {directed_bounds}/{n}",
        },
        {
            "criterion": "directed_provenance_required",
            "supported": bool(n > 0 and provenance_bounds == n and directed_bounds < n),
            "basis": f"directed_provenance_c bounds C {provenance_bounds}/{n}; directed_c bounds C {directed_bounds}/{n}",
        },
        {
            "criterion": "endpoint_pairing_required",
            "supported": bool(provenance_bounds > count_bounds(summary, "directed_provenance_endpoint_pair_swapped")),
            "basis": f"directed_provenance_c bounds C {provenance_bounds}/{n}; endpoint_pair_swapped bounds C {count_bounds(summary, 'directed_provenance_endpoint_pair_swapped')}/{n}",
        },
        {
            "criterion": "train_test_correspondence_required",
            "supported": bool(provenance_bounds > count_bounds(summary, "directed_provenance_train_test_mismatch")),
            "basis": f"directed_provenance_c bounds C {provenance_bounds}/{n}; train_test_mismatch bounds C {count_bounds(summary, 'directed_provenance_train_test_mismatch')}/{n}",
        },
        {
            "criterion": "directed_transport_required",
            "supported": bool(count_bounds(summary, "directed_transport_closure_o1o2") == n and count_beats(summary, "static_scalar_closure") == n),
            "basis": f"directed_transport_closure_o1o2 bounds C {count_bounds(summary, 'directed_transport_closure_o1o2')}/{n}; static_scalar_closure lets C win {count_beats(summary, 'static_scalar_closure')}/{n}",
        },
        {
            "criterion": "fixed_mask_sufficient",
            "supported": bool(n > 0 and count_bounds(summary, "fixed_mask_control") == n),
            "basis": f"fixed_mask_control bounds C {count_bounds(summary, 'fixed_mask_control')}/{n}",
        },
        {
            "criterion": "unresolved_endpoint_structure",
            "supported": bool(endpoint_bounds == n and provenance_bounds < n),
            "basis": f"endpoint_o1o2_reference bounds C {endpoint_bounds}/{n}; directed_provenance_c bounds C {provenance_bounds}/{n}",
        },
    ]
    return pd.DataFrame(rows)


def write_report(path: Path, summary: pd.DataFrame, classification: pd.DataFrame, pivot: pd.DataFrame, args: argparse.Namespace) -> None:
    lines = [
        "# Stage B7.2c Directed-Provenance C Reconstruction Audit",
        "",
        "Status: executed after writing Stage_B7_2c_preregistration.md and Stage_B7_2c_plan_email.md.",
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
        "## Interpretation",
        "",
        "B7.2c tests whether the B7.2b endpoint-local O1/O2 boundary can be reconstructed without directly using endpoint-adjacent O1/O2 raw values.",
        "",
        "Arms containing `o1o2` are retained as endpoint-adjacent references. A successful Directed-Provenance C reconstruction requires the non-O1/O2 `directed_provenance_c` arm to bound true C in the frozen regimes.",
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
    b72b = load_b72b()
    b6p = b71a.load_module("b6p_for_b72c", b71a.B6P_SCRIPT)
    b71 = b71a.load_module("b71_for_b72c", b71a.B71_SCRIPT)
    b6l, table = b6p.build_table(b71a.build_args(args))
    intersection = b71.build_intersection_arms(table, b6p, b6l, b71a.build_args(args))
    controls = pd.concat(
        [
            build_access(table, b6p, b6l, b72b, level, endpoint, direction, args)
            for level in CONTROL_LEVELS
            for endpoint in ENDPOINTS
            for direction in DIRECTIONS
        ],
        ignore_index=True,
    )
    comparison = compare(intersection, controls, args)
    summary, pivot, classification = summarize(comparison)
    controls.to_csv(outdir / "Stage_B7_2c_control_events.csv", index=False)
    comparison.to_csv(outdir / "Stage_B7_2c_comparison.csv", index=False)
    summary.to_csv(outdir / "Stage_B7_2c_component_summary.csv", index=False)
    pivot.to_csv(outdir / "Stage_B7_2c_frozen_pass_matrix.csv", index=False)
    classification.to_csv(outdir / "Stage_B7_2c_primary_classification.csv", index=False)
    write_report(outdir / "Stage_B7_2c_preregistered_summary.md", summary, classification, pivot, args)
    print("\nStage B7.2c audit")
    print(f"- output_dir: {outdir}")
    print(summary.to_string(index=False))
    print("\nClassification")
    print(classification.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_2c")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=71203)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
