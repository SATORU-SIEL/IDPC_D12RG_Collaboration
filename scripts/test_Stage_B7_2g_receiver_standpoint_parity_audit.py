#!/usr/bin/env python3
"""Stage B7.2g receiver-standpoint parity mismatch audit."""

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


ENDPOINTS = b71a.ENDPOINTS
OPERATORS = b71a.OPERATORS
DIRECTIONS = ["A_to_C_to_B", "B_to_C_to_A"]
CONTROL_LEVELS = [
    "receiver_preserved__standpoint_preserved",
    "receiver_preserved__standpoint_inverted",
    "receiver_inverted__standpoint_preserved",
    "receiver_inverted__standpoint_inverted",
    "receiver_only",
    "standpoint_only_preserved",
    "standpoint_only_inverted",
    "standpoint_sign_only",
    "standpoint_magnitude_only",
    "receiver_plus_magnitude",
    "receiver_plus_standpoint_sign",
    "complexity_matched_shuffled_pair",
    "parity_label_shuffled",
    "ab_exchange_parity_mismatch",
    "endpoint_o1o2_reference",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_b72c():
    return load_module("b72c_for_b72g", SCRIPTS / "test_Stage_B7_2c_directed_provenance_reconstruction_audit.py")


def qbin(series: pd.Series, q: int = 3) -> pd.Series:
    return b71a.qbin(pd.to_numeric(series, errors="coerce"), q)


def sign_bin(series: pd.Series) -> pd.Series:
    vals = pd.to_numeric(series, errors="coerce")
    return pd.Series(np.where(vals.gt(0), "pos", np.where(vals.lt(0), "neg", "zero")), index=series.index)


def add_features(table: pd.DataFrame, b72c, b72b, direction: str, seed: int) -> pd.DataFrame:
    out = b72c.add_reconstruction_features(table, b72b, direction, seed).copy()
    rng = np.random.default_rng(seed + 72070)
    out["standpoint_sign"] = sign_bin(out["standpoint_polarity"])
    out["standpoint_magnitude"] = pd.to_numeric(out["standpoint_polarity"], errors="coerce").abs()
    out["inverted_standpoint_sign"] = sign_bin(out["inverted_standpoint_polarity"])
    out["inverted_standpoint_magnitude"] = pd.to_numeric(out["inverted_standpoint_polarity"], errors="coerce").abs()
    out["shuffled_receiver_side"] = pd.to_numeric(out["receiver_side"], errors="coerce")
    out["shuffled_standpoint_polarity"] = pd.to_numeric(out["standpoint_polarity"], errors="coerce")
    out["shuffled_standpoint_side"] = pd.to_numeric(out["standpoint_side"], errors="coerce")
    for _, sub in out.groupby("label", sort=False):
        idx = sub.index.to_numpy()
        perm = idx.copy()
        rng.shuffle(perm)
        out.loc[idx, "shuffled_receiver_side"] = pd.to_numeric(out.loc[perm, "receiver_side"], errors="coerce").to_numpy(dtype=float)
        out.loc[idx, "shuffled_standpoint_polarity"] = pd.to_numeric(out.loc[perm, "standpoint_polarity"], errors="coerce").to_numpy(dtype=float)
        out.loc[idx, "shuffled_standpoint_side"] = pd.to_numeric(out.loc[perm, "standpoint_side"], errors="coerce").to_numpy(dtype=float)
    out["shuffled_standpoint_sign"] = sign_bin(out["shuffled_standpoint_polarity"])
    out["shuffled_standpoint_magnitude"] = pd.to_numeric(out["shuffled_standpoint_polarity"], errors="coerce").abs()
    return out


def parts_for_level(data: pd.DataFrame, level: str) -> list[pd.Series]:
    base = [
        "dir=" + data["direction_code"].astype(str),
        "side=" + data["side_identity"].astype(str),
    ]
    receiver_preserved = "recv=" + qbin(data["receiver_side"], 3).astype(str)
    receiver_inverted = "recv=" + qbin(data["sender_side"], 3).astype(str)
    standpoint_preserved = [
        "ss=" + qbin(data["standpoint_side"], 3).astype(str),
        "sp=" + qbin(data["standpoint_polarity"], 3).astype(str),
    ]
    standpoint_inverted = [
        "ss=" + qbin(data["inverted_standpoint_side"], 3).astype(str),
        "sp=" + qbin(data["inverted_standpoint_polarity"], 3).astype(str),
    ]
    if level == "receiver_preserved__standpoint_preserved":
        return base + [receiver_preserved] + standpoint_preserved
    if level == "receiver_preserved__standpoint_inverted":
        return base + [receiver_preserved] + standpoint_inverted
    if level == "receiver_inverted__standpoint_preserved":
        return base + [receiver_inverted] + standpoint_preserved
    if level == "receiver_inverted__standpoint_inverted":
        return base + [receiver_inverted] + standpoint_inverted
    if level == "receiver_only":
        return base + [receiver_preserved]
    if level == "standpoint_only_preserved":
        return base + standpoint_preserved
    if level == "standpoint_only_inverted":
        return base + standpoint_inverted
    if level == "standpoint_sign_only":
        return base + ["sign=" + data["standpoint_sign"].astype(str)]
    if level == "standpoint_magnitude_only":
        return base + ["mag=" + qbin(data["standpoint_magnitude"], 3).astype(str)]
    if level == "receiver_plus_magnitude":
        return base + [receiver_preserved, "mag=" + qbin(data["standpoint_magnitude"], 3).astype(str)]
    if level == "receiver_plus_standpoint_sign":
        return base + [receiver_preserved, "sign=" + data["standpoint_sign"].astype(str)]
    if level == "complexity_matched_shuffled_pair":
        return base + [
            "recv=" + qbin(data["shuffled_receiver_side"], 3).astype(str),
            "ss=" + qbin(data["shuffled_standpoint_side"], 3).astype(str),
            "sp=" + qbin(data["shuffled_standpoint_polarity"], 3).astype(str),
        ]
    if level == "parity_label_shuffled":
        return base + [
            "recv=" + qbin(data["receiver_side"], 3).astype(str),
            "ss=" + qbin(data["shuffled_standpoint_side"], 3).astype(str),
            "sp=" + qbin(data["shuffled_standpoint_polarity"], 3).astype(str),
        ]
    if level == "ab_exchange_parity_mismatch":
        return [
            "dir=" + data["direction_code_swapped"].astype(str),
            "side=" + data["side_identity_swapped"].astype(str),
            "recv=" + qbin(data["sender_side"], 3).astype(str),
            "ss=" + qbin(data["standpoint_side"], 3).astype(str),
            "sp=" + qbin(data["standpoint_polarity"], 3).astype(str),
        ]
    raise ValueError(f"unknown level {level}")


def state_labels(table: pd.DataFrame, b72c, b72b, direction: str, level: str, seed: int) -> pd.Series:
    data = add_features(table, b72c, b72b, direction, seed)
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
    if level == "endpoint_o1o2_reference":
        out = b72c.build_access(table, b6p, b6l, b72b, "endpoint_o1o2_reference", endpoint, direction, args)
        out["control_level"] = level
        return out
    return build_custom_access(table, b6p, b6l, b72c, b72b, level, endpoint, direction, args)


def compare(intersection: pd.DataFrame, controls: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 72080)
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
    matrix = frozen_comp.pivot_table(index=["mode", "endpoint", "direction"], columns="control_level", values="c_beats_control", aggfunc="first").reset_index()
    return summary, matrix, classify(summary)


def mean(summary: pd.DataFrame, level: str) -> float:
    row = summary[summary["control_level"].eq(level)]
    return np.nan if row.empty else float(row.iloc[0]["mean_true_minus_control"])


def bounds(summary: pd.DataFrame, level: str) -> int:
    row = summary[summary["control_level"].eq(level)]
    return 0 if row.empty else int(row.iloc[0]["control_bounds_c_count"])


def classify(summary: pd.DataFrame) -> pd.DataFrame:
    margin = 0.005
    matched = [
        mean(summary, "receiver_preserved__standpoint_preserved"),
        mean(summary, "receiver_inverted__standpoint_inverted"),
    ]
    mismatched = [
        mean(summary, "receiver_preserved__standpoint_inverted"),
        mean(summary, "receiver_inverted__standpoint_preserved"),
    ]
    best_mismatch = float(np.nanmin(mismatched))
    worst_mismatch = float(np.nanmax(mismatched))
    best_matched = float(np.nanmin(matched))
    receiver_only = mean(summary, "receiver_only")
    standpoint_only = min(mean(summary, "standpoint_only_preserved"), mean(summary, "standpoint_only_inverted"))
    sign_mag = min(
        mean(summary, "standpoint_sign_only"),
        mean(summary, "standpoint_magnitude_only"),
        mean(summary, "receiver_plus_magnitude"),
        mean(summary, "receiver_plus_standpoint_sign"),
    )
    shuffle = min(mean(summary, "complexity_matched_shuffled_pair"), mean(summary, "parity_label_shuffled"))
    endpoint = mean(summary, "endpoint_o1o2_reference")
    endpoint_free_min = np.nanmin([mean(summary, x) for x in CONTROL_LEVELS if x != "endpoint_o1o2_reference"])
    parity_supported = bool(worst_mismatch + margin < best_matched)
    receiver_explains = bool(np.isfinite(receiver_only) and receiver_only <= best_mismatch + margin)
    standpoint_explains = bool(np.isfinite(standpoint_only) and standpoint_only <= best_mismatch + margin)
    sign_mag_explains = bool(np.isfinite(sign_mag) and sign_mag <= best_mismatch + margin)
    shuffle_explains = bool(np.isfinite(shuffle) and shuffle <= best_mismatch + margin)
    rows = [
        ("parity_mismatch_supported", parity_supported, f"matched means {matched}; mismatched means {mismatched}; margin {margin}"),
        ("receiver_only_explains_effect", receiver_explains, f"receiver_only mean {receiver_only:.4f}; best mismatch {best_mismatch:.4f}"),
        ("standpoint_only_explains_effect", standpoint_explains, f"best standpoint-only mean {standpoint_only:.4f}; best mismatch {best_mismatch:.4f}"),
        ("sign_or_magnitude_explains_effect", sign_mag_explains, f"best sign/magnitude mean {sign_mag:.4f}; best mismatch {best_mismatch:.4f}"),
        ("complexity_shuffle_explains_effect", shuffle_explains, f"best shuffled mean {shuffle:.4f}; best mismatch {best_mismatch:.4f}"),
        ("ab_exchange_consistent", bounds(summary, "ab_exchange_parity_mismatch") == bounds(summary, "receiver_preserved__standpoint_inverted"), f"ab_exchange bounds {bounds(summary, 'ab_exchange_parity_mismatch')}; mismatch bounds {bounds(summary, 'receiver_preserved__standpoint_inverted')}"),
        ("endpoint_o1o2_effect_size_gap_persists", bool(np.isfinite(endpoint) and endpoint < endpoint_free_min), f"endpoint mean {endpoint:.4f}; endpoint-free min {endpoint_free_min:.4f}"),
    ]
    falsified = (not parity_supported) or receiver_explains or standpoint_explains or sign_mag_explains or shuffle_explains
    rows.append(("parity_hypothesis_falsified", falsified, "parity unsupported or simpler falsification arm explains the effect"))
    rows.append(("unresolved_parity_boundary", not falsified and not parity_supported, "no decisive parity or falsification result"))
    return pd.DataFrame([{"criterion": c, "supported": bool(s), "basis": b} for c, s, b in rows])


def write_report(path: Path, summary: pd.DataFrame, classification: pd.DataFrame, matrix: pd.DataFrame, args: argparse.Namespace) -> None:
    lines = [
        "# Stage B7.2g Receiver-Standpoint Parity Mismatch Audit",
        "",
        "Status: executed after writing Stage_B7_2g_preregistration.md.",
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
        matrix.to_csv(index=False).strip(),
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
    b6p = b71a.load_module("b6p_for_b72g", b71a.B6P_SCRIPT)
    b71 = b71a.load_module("b71_for_b72g", b71a.B71_SCRIPT)
    b6l, table = b6p.build_table(b71a.build_args(args))
    intersection = b71.build_intersection_arms(table, b6p, b6l, b71a.build_args(args))
    controls = pd.concat(
        [
            build_access(table, b6p, b6l, level, b72c, b72b, endpoint, direction, args)
            if False else build_access(table, b6p, b6l, b72c, b72b, level, endpoint, direction, args)
            for level in CONTROL_LEVELS
            for endpoint in ENDPOINTS
            for direction in DIRECTIONS
        ],
        ignore_index=True,
    )
    comparison = compare(intersection, controls, args)
    summary, matrix, classification = summarize(comparison)
    controls.to_csv(outdir / "Stage_B7_2g_control_events.csv", index=False)
    comparison.to_csv(outdir / "Stage_B7_2g_comparison.csv", index=False)
    summary.to_csv(outdir / "Stage_B7_2g_component_summary.csv", index=False)
    matrix.to_csv(outdir / "Stage_B7_2g_frozen_pass_matrix.csv", index=False)
    classification.to_csv(outdir / "Stage_B7_2g_primary_classification.csv", index=False)
    write_report(outdir / "Stage_B7_2g_preregistered_summary.md", summary, classification, matrix, args)
    print("\nStage B7.2g audit")
    print(f"- output_dir: {outdir}")
    print("\nClassification")
    print(classification.to_string(index=False))
    print("\nSummary")
    print(summary.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_2g")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=71208)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
