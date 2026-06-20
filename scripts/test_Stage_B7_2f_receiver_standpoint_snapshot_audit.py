#!/usr/bin/env python3
"""Stage B7.2f receiver-standpoint reconstruction and snapshot audit."""

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
SNAPSHOTS = ["t0", "t1", "t2", "tc", "tc_plus_k"]
CONTROL_LEVELS = [
    "unperturbed_baseline",
    "sham_perturbation",
    "receiver_standpoint_reconstruction",
    "receiver_standpoint_reconstruction_shuffled",
    "mapping_inversion",
    "side_shuffle",
    "unsigned_side_gap",
    "polarity_magnitude_only",
    "receiver_side_only",
    "giver_side_only",
    "standpoint_polarity_preserved",
    "standpoint_polarity_inverted",
    "ab_exchange_receiver_standpoint",
    "mirrored_receiver_standpoint",
    "normalization_matched_receiver_standpoint",
    "reward_symmetry_control",
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
    return load_module("b72c_for_b72f", SCRIPTS / "test_Stage_B7_2c_directed_provenance_reconstruction_audit.py")


def qbin(series: pd.Series, q: int = 3) -> pd.Series:
    return b71a.qbin(pd.to_numeric(series, errors="coerce"), q)


def rank_bin_within_label(data: pd.DataFrame, col: str, q: int = 3) -> pd.Series:
    vals = pd.to_numeric(data.get(col, pd.Series(np.nan, index=data.index)), errors="coerce")
    out = pd.Series(index=data.index, dtype=object)
    for _, sub in data.assign(_v=vals).groupby("label", sort=False):
        ranks = sub["_v"].rank(method="average", pct=True)
        bins = np.floor(np.clip(ranks.fillna(0.5).to_numpy() * q, 0, q - 1)).astype(int)
        out.loc[sub.index] = [f"q{x}" for x in bins]
    return out


def circular_phase_delta(a: float, b: float) -> float:
    if not np.isfinite(a) or not np.isfinite(b):
        return np.nan
    return abs(((a - b + 180.0) % 360.0) - 180.0)


def session_thresholds(table: pd.DataFrame) -> dict[str, tuple[float, float]]:
    thresholds: dict[str, tuple[float, float]] = {}
    for label, sub in table.sort_values(["label", "idx_in_session"]).groupby("label", sort=False):
        mem = pd.to_numeric(sub.get("C_memory_scalar", pd.Series(np.nan, index=sub.index)), errors="coerce").to_numpy(dtype=float)
        phase = pd.to_numeric(sub.get("phase", pd.Series(np.nan, index=sub.index)), errors="coerce").to_numpy(dtype=float)
        mem_delta = np.abs(np.diff(mem))
        phase_delta = np.asarray([circular_phase_delta(phase[i], phase[i - 1]) for i in range(1, len(phase))], dtype=float)
        mem_thr = float(np.nanmedian(mem_delta)) if np.isfinite(mem_delta).any() else np.inf
        phase_thr = float(np.nanmedian(phase_delta)) if np.isfinite(phase_delta).any() else np.inf
        thresholds[str(label)] = (mem_thr, phase_thr)
    return thresholds


def snapshot_positions(sub: pd.DataFrame, pos: int, thresholds: tuple[float, float], post_k: int) -> dict[str, int | None]:
    n = len(sub)
    out: dict[str, int | None] = {
        "t0": pos,
        "t1": pos + 1 if pos + 1 < n else None,
        "t2": pos + 2 if pos + 2 < n else None,
        "tc": None,
        "tc_plus_k": None,
    }
    mem_thr, phase_thr = thresholds
    mem = pd.to_numeric(sub.get("C_memory_scalar", pd.Series(np.nan, index=sub.index)), errors="coerce").to_numpy(dtype=float)
    phase = pd.to_numeric(sub.get("phase", pd.Series(np.nan, index=sub.index)), errors="coerce").to_numpy(dtype=float)
    for j in range(pos + 2, n):
        dm = abs(mem[j] - mem[j - 1]) if np.isfinite(mem[j]) and np.isfinite(mem[j - 1]) else np.nan
        dp = circular_phase_delta(phase[j], phase[j - 1])
        if np.isfinite(dm) and np.isfinite(dp) and dm <= mem_thr and dp <= phase_thr:
            out["tc"] = j
            out["tc_plus_k"] = j + post_k if j + post_k < n else None
            break
    return out


def make_snapshot_table(table: pd.DataFrame, post_k: int = 1) -> pd.DataFrame:
    thresholds = session_thresholds(table)
    rows = []
    for label, sub in table.sort_values(["label", "idx_in_session"]).groupby("label", sort=False):
        sub = sub.reset_index(drop=False)
        for pos, origin in sub.iterrows():
            positions = snapshot_positions(sub, pos, thresholds[str(label)], post_k)
            for snapshot, snap_pos in positions.items():
                if snap_pos is None:
                    continue
                snap = sub.iloc[int(snap_pos)].copy()
                row = snap.drop(labels=["index"]).to_dict()
                origin_idx = float(origin["idx_in_session"])
                row["origin_idx_in_session"] = origin_idx
                row["snapshot_source_idx_in_session"] = float(snap["idx_in_session"])
                row["snapshot"] = snapshot
                row["snapshot_order"] = SNAPSHOTS.index(snapshot)
                row["snapshot_lag_events"] = int(snap_pos - pos)
                row["idx_in_session"] = origin_idx + (SNAPSHOTS.index(snapshot) * 0.001)
                rows.append(row)
    return pd.DataFrame(rows)


def add_features(table: pd.DataFrame, b72c, b72b, direction: str, seed: int) -> pd.DataFrame:
    out = b72c.add_reconstruction_features(table, b72b, direction, seed).copy()
    ac = pd.to_numeric(out.get("A_C", pd.Series(np.nan, index=out.index)), errors="coerce")
    bc = pd.to_numeric(out.get("B_C", pd.Series(np.nan, index=out.index)), errors="coerce")
    out["ac_minus_bc"] = ac - bc
    out["abs_ac_minus_bc"] = (ac - bc).abs()
    out["polarity_magnitude"] = pd.to_numeric(out["standpoint_polarity"], errors="coerce").abs()
    out["receiver_rank_bin"] = rank_bin_within_label(out, "receiver_side", 3)
    out["standpoint_rank_bin"] = rank_bin_within_label(out, "standpoint_polarity", 3)
    out["sym_receiver_giver"] = (pd.to_numeric(out["receiver_side"], errors="coerce") + pd.to_numeric(out["sender_side"], errors="coerce")) / 2.0
    return out


def parts_for_level(data: pd.DataFrame, level: str) -> list[pd.Series]:
    base = [
        "dir=" + data["direction_code"].astype(str),
        "side=" + data["side_identity"].astype(str),
    ]
    preserved = base + [
        "recv=" + qbin(data["receiver_side"], 3).astype(str),
        "ss=" + qbin(data["standpoint_side"], 3).astype(str),
        "sp=" + qbin(data["standpoint_polarity"], 3).astype(str),
        "mag=" + qbin(data["polarity_magnitude"], 3).astype(str),
    ]
    if level in {"unperturbed_baseline", "sham_perturbation", "receiver_standpoint_reconstruction"}:
        return preserved
    if level == "receiver_standpoint_reconstruction_shuffled":
        return [
            "dir=" + data["direction_code"].astype(str),
            "side=" + data["side_identity_shuffled"].astype(str),
            "recv=" + qbin(data["receiver_side"], 3).astype(str),
            "ss=" + qbin(data["standpoint_side_shuffled"], 3).astype(str),
            "sp=" + qbin(data["standpoint_polarity_shuffled"], 3).astype(str),
            "mag=" + qbin(pd.to_numeric(data["standpoint_polarity_shuffled"], errors="coerce").abs(), 3).astype(str),
        ]
    if level == "mapping_inversion":
        return base + [
            "recv=" + qbin(data["receiver_side"], 3).astype(str),
            "ss=" + qbin(data["inverted_standpoint_side"], 3).astype(str),
            "sp=" + qbin(data["inverted_standpoint_polarity"], 3).astype(str),
            "mag=" + qbin(pd.to_numeric(data["inverted_standpoint_polarity"], errors="coerce").abs(), 3).astype(str),
        ]
    if level == "side_shuffle":
        return [
            "dir=" + data["direction_code"].astype(str),
            "side=" + data["side_identity_shuffled"].astype(str),
            "ss=" + qbin(data["standpoint_side_shuffled"], 3).astype(str),
            "sp=" + qbin(data["standpoint_polarity_shuffled"], 3).astype(str),
        ]
    if level == "unsigned_side_gap":
        return base + ["gap=" + qbin(data["abs_ac_minus_bc"], 3).astype(str)]
    if level == "polarity_magnitude_only":
        return base + ["mag=" + qbin(data["polarity_magnitude"], 3).astype(str)]
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
    if level == "ab_exchange_receiver_standpoint":
        return [
            "dir=" + data["direction_code_swapped"].astype(str),
            "side=" + data["side_identity_swapped"].astype(str),
            "recv=" + qbin(data["sender_side"], 3).astype(str),
            "ss=" + qbin(data["inverted_standpoint_side"], 3).astype(str),
            "sp=" + qbin(data["inverted_standpoint_polarity"], 3).astype(str),
            "mag=" + qbin(pd.to_numeric(data["inverted_standpoint_polarity"], errors="coerce").abs(), 3).astype(str),
        ]
    if level == "mirrored_receiver_standpoint":
        return base + [
            "recv=" + qbin(data["sender_side"], 3).astype(str),
            "ss=" + qbin(data["standpoint_side"], 3).astype(str),
            "sp=" + qbin(data["standpoint_polarity"], 3).astype(str),
        ]
    if level == "normalization_matched_receiver_standpoint":
        return base + [
            "recv_rank=" + data["receiver_rank_bin"].astype(str),
            "sp_rank=" + data["standpoint_rank_bin"].astype(str),
        ]
    if level == "reward_symmetry_control":
        return base + [
            "sym=" + qbin(data["sym_receiver_giver"], 3).astype(str),
            "mag=" + qbin(data["polarity_magnitude"], 3).astype(str),
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
                    "origin_idx_in_session": row.get("origin_idx_in_session", row["idx_in_session"]),
                    "snapshot": row.get("snapshot", "t0"),
                    "snapshot_order": row.get("snapshot_order", 0),
                    "snapshot_lag_events": row.get("snapshot_lag_events", 0),
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
        out["origin_idx_in_session"] = table["origin_idx_in_session"].to_numpy()
        out["snapshot"] = table["snapshot"].to_numpy()
        out["snapshot_order"] = table["snapshot_order"].to_numpy()
        out["snapshot_lag_events"] = table["snapshot_lag_events"].to_numpy()
        return out
    return build_custom_access(table, b6p, b6l, b72c, b72b, level, endpoint, direction, args)


def compare(intersection: pd.DataFrame, controls: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 72060)
    rows = []
    for (mode, endpoint, direction), sub in intersection.groupby(["mode", "endpoint", "direction"], sort=False):
        true = sub[sub["arm_kind"].eq("true")].set_index(["fold", "label", "idx_in_session"])
        scoped = controls[(controls["endpoint"].eq(endpoint)) & (controls["direction"].eq(direction))]
        for (level, snapshot), ctrl in scoped.groupby(["control_level", "snapshot"], sort=False):
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
                    "snapshot": snapshot,
                    "snapshot_order": SNAPSHOTS.index(snapshot),
                    "mean_true_c": float(np.nanmean(joined["intersection_access_effect"])),
                    "mean_control": float(np.nanmean(joined["access_effect"])),
                    "effect_true_minus_control": effect,
                    "p_true_greater": p,
                    "n_pairs": int(np.isfinite(diff).sum()),
                    "c_beats_control": bool(np.isfinite(effect) and effect > 0 and np.isfinite(p) and p <= args.alpha),
                }
            )
    return pd.DataFrame(rows)


def frozen_filter(comparison: pd.DataFrame) -> pd.DataFrame:
    frozen = pd.read_csv(REPO / "reports/stage_b7_1/Stage_B7_1_b6_regime_freeze.csv")
    frozen_keys = set(tuple(x) for x in frozen[frozen["b71_frozen_b6_supported"]][["mode", "endpoint", "direction_with_c"]].to_numpy())
    comp = comparison.copy()
    comp["frozen_b6_supported"] = [(r.mode, r.endpoint, r.direction) in frozen_keys for r in comp.itertuples(index=False)]
    return comp[comp["frozen_b6_supported"]].copy()


def component_summary(frozen_comp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (level, snapshot), sub in frozen_comp.groupby(["control_level", "snapshot"], sort=False):
        rows.append(
            {
                "control_level": level,
                "snapshot": snapshot,
                "snapshot_order": int(sub["snapshot_order"].iloc[0]),
                "frozen_regimes": int(len(sub)),
                "c_beats_count": int(sub["c_beats_control"].sum()),
                "control_bounds_c_count": int((~sub["c_beats_control"]).sum()),
                "mean_true_minus_control": float(sub["effect_true_minus_control"].mean()),
                "median_true_minus_control": float(sub["effect_true_minus_control"].median()),
            }
        )
    return pd.DataFrame(rows).sort_values(["control_level", "snapshot_order"])


def trajectory_summary(summary: pd.DataFrame) -> pd.DataFrame:
    baseline = summary[summary["control_level"].eq("unperturbed_baseline")][["snapshot", "mean_true_minus_control"]].rename(columns={"mean_true_minus_control": "baseline_effect"})
    rows = []
    for level, sub in summary.groupby("control_level", sort=False):
        merged = sub.merge(baseline, on="snapshot", how="left").sort_values("snapshot_order")
        disruption = merged["baseline_effect"].to_numpy(dtype=float) - merged["mean_true_minus_control"].to_numpy(dtype=float)
        orders = merged["snapshot_order"].to_numpy(dtype=int)
        effects = merged["mean_true_minus_control"].to_numpy(dtype=float)
        if np.isfinite(disruption).any():
            max_i = int(np.nanargmax(disruption))
            max_disruption = float(disruption[max_i])
            time_to_max = int(orders[max_i])
        else:
            max_disruption = np.nan
            time_to_max = -1
        early = float(effects[orders.tolist().index(1)]) if 1 in orders else np.nan
        final = float(effects[orders.tolist().index(4)]) if 4 in orders else (float(effects[-1]) if len(effects) else np.nan)
        convergence = float(effects[orders.tolist().index(3)]) if 3 in orders else np.nan
        area = float(np.nansum(np.clip(disruption, 0, None)))
        overshoot = float(np.nanmin(disruption)) if np.isfinite(disruption).any() else np.nan
        post_resid = float(disruption[orders.tolist().index(4)]) if 4 in orders and np.isfinite(disruption).any() else np.nan
        hysteresis = float(np.nanmax(disruption) - np.nanmin(disruption)) if np.isfinite(disruption).any() else np.nan
        rows.append(
            {
                "control_level": level,
                "max_disruption": max_disruption,
                "time_to_max_disruption": time_to_max,
                "recovery_amount": max_disruption - post_resid if np.isfinite(max_disruption) and np.isfinite(post_resid) else np.nan,
                "overshoot": overshoot,
                "area_under_disruption_curve": area,
                "post_convergence_residual": post_resid,
                "trajectory_hysteresis": hysteresis,
                "early_effect": early,
                "convergence_effect": convergence,
                "final_effect": final,
            }
        )
    return pd.DataFrame(rows)


def val(summary: pd.DataFrame, level: str, snapshot: str, col: str) -> float:
    row = summary[(summary["control_level"].eq(level)) & (summary["snapshot"].eq(snapshot))]
    return np.nan if row.empty else float(row.iloc[0][col])


def bounds(summary: pd.DataFrame, level: str, snapshot: str) -> int:
    row = summary[(summary["control_level"].eq(level)) & (summary["snapshot"].eq(snapshot))]
    return 0 if row.empty else int(row.iloc[0]["control_bounds_c_count"])


def classify(summary: pd.DataFrame, traj: pd.DataFrame) -> pd.DataFrame:
    n = int(summary["frozen_regimes"].max()) if not summary.empty else 0
    prs_final = val(summary, "receiver_standpoint_reconstruction", "tc_plus_k", "mean_true_minus_control")
    shuf_final = val(summary, "receiver_standpoint_reconstruction_shuffled", "tc_plus_k", "mean_true_minus_control")
    inv_final = val(summary, "standpoint_polarity_inverted", "tc_plus_k", "mean_true_minus_control")
    pres_final = val(summary, "standpoint_polarity_preserved", "tc_plus_k", "mean_true_minus_control")
    recv_final = val(summary, "receiver_side_only", "tc_plus_k", "mean_true_minus_control")
    giver_final = val(summary, "giver_side_only", "tc_plus_k", "mean_true_minus_control")
    endpoint_final = val(summary, "endpoint_o1o2_reference", "tc_plus_k", "mean_true_minus_control")
    prs_t1 = val(summary, "receiver_standpoint_reconstruction", "t1", "mean_true_minus_control")
    shuf_t1 = val(summary, "receiver_standpoint_reconstruction_shuffled", "t1", "mean_true_minus_control")
    inv_t1 = val(summary, "standpoint_polarity_inverted", "t1", "mean_true_minus_control")
    endpoint_free_levels = [x for x in CONTROL_LEVELS if x != "endpoint_o1o2_reference"]
    endpoint_free_min = np.nanmin([val(summary, x, "tc_plus_k", "mean_true_minus_control") for x in endpoint_free_levels])
    rows = [
        ("receiver_standpoint_reconstruction_supported", bounds(summary, "receiver_standpoint_reconstruction", "tc_plus_k") == n, f"receiver_standpoint_reconstruction bounds C {bounds(summary, 'receiver_standpoint_reconstruction', 'tc_plus_k')}/{n} at tc_plus_k"),
        ("receiver_only_sufficient", bounds(summary, "receiver_side_only", "tc_plus_k") == n, f"receiver_side_only bounds C {bounds(summary, 'receiver_side_only', 'tc_plus_k')}/{n} at tc_plus_k"),
        ("standpoint_preservation_required", np.isfinite(pres_final) and np.isfinite(inv_final) and pres_final < inv_final, f"preserved mean {pres_final:.4f}; inverted mean {inv_final:.4f} at tc_plus_k"),
        ("standpoint_inversion_breaks_signal", bounds(summary, "standpoint_polarity_preserved", "tc_plus_k") > bounds(summary, "standpoint_polarity_inverted", "tc_plus_k"), f"preserved bounds {bounds(summary, 'standpoint_polarity_preserved', 'tc_plus_k')}/{n}; inverted bounds {bounds(summary, 'standpoint_polarity_inverted', 'tc_plus_k')}/{n}"),
        ("shuffled_mapping_breaks_signal", np.isfinite(prs_final) and np.isfinite(shuf_final) and prs_final < shuf_final, f"reconstruction mean {prs_final:.4f}; shuffled mean {shuf_final:.4f} at tc_plus_k"),
        ("ab_exchange_predictable", bounds(summary, "ab_exchange_receiver_standpoint", "tc_plus_k") >= bounds(summary, "mirrored_receiver_standpoint", "tc_plus_k"), f"ab_exchange bounds {bounds(summary, 'ab_exchange_receiver_standpoint', 'tc_plus_k')}/{n}; mirrored bounds {bounds(summary, 'mirrored_receiver_standpoint', 'tc_plus_k')}/{n}"),
        ("feature_construction_asymmetry_detected", bounds(summary, "normalization_matched_receiver_standpoint", "tc_plus_k") < bounds(summary, "receiver_standpoint_reconstruction", "tc_plus_k"), f"normalization matched bounds {bounds(summary, 'normalization_matched_receiver_standpoint', 'tc_plus_k')}/{n}; raw reconstruction bounds {bounds(summary, 'receiver_standpoint_reconstruction', 'tc_plus_k')}/{n}"),
        ("endpoint_o1o2_effect_size_gap_persists", np.isfinite(endpoint_final) and endpoint_final < endpoint_free_min, f"endpoint_o1o2 mean {endpoint_final:.4f}; endpoint-free min {endpoint_free_min:.4f}"),
        ("stable_correspondence", np.isfinite(prs_t1) and np.isfinite(shuf_t1) and np.isfinite(inv_t1) and prs_t1 < shuf_t1 and prs_t1 < inv_t1 and prs_final < shuf_final and prs_final < inv_final, "receiver-standpoint reconstruction separates from shuffled/inverted at t1 and tc_plus_k"),
        ("recovery_dependent_correspondence", np.isfinite(prs_t1) and np.isfinite(shuf_t1) and abs(prs_t1 - shuf_t1) < 0.01 and np.isfinite(prs_final) and np.isfinite(shuf_final) and abs(prs_final - shuf_final) >= 0.01, "early arms are similar but separate by tc_plus_k"),
        ("transient_disruption_only", np.isfinite(prs_t1) and np.isfinite(shuf_t1) and abs(prs_t1 - shuf_t1) >= 0.01 and np.isfinite(prs_final) and np.isfinite(shuf_final) and abs(prs_final - shuf_final) < 0.01, "early separation disappears by tc_plus_k"),
        ("endpoint_only_effect", bounds(summary, "receiver_standpoint_reconstruction", "tc_plus_k") < n and bounds(summary, "endpoint_o1o2_reference", "tc_plus_k") == n, "endpoint reference bounds C but endpoint-free reconstruction does not"),
        ("final_readout_sufficient", np.isfinite(prs_t1) and np.isfinite(prs_final) and abs(prs_t1 - prs_final) < 0.02, f"receiver-standpoint t1 {prs_t1:.4f}; tc_plus_k {prs_final:.4f}"),
        ("final_readout_insufficient", np.isfinite(prs_t1) and np.isfinite(prs_final) and abs(prs_t1 - prs_final) >= 0.02, f"receiver-standpoint t1 {prs_t1:.4f}; tc_plus_k {prs_final:.4f}"),
    ]
    unresolved = not any(x[1] for x in rows[:12])
    rows.append(("unresolved_receiver_standpoint_boundary", unresolved, "no receiver/standpoint trajectory classification decisively supported"))
    return pd.DataFrame([{"criterion": c, "supported": bool(s), "basis": b} for c, s, b in rows])


def write_report(path: Path, summary: pd.DataFrame, traj: pd.DataFrame, classification: pd.DataFrame, args: argparse.Namespace) -> None:
    lines = [
        "# Stage B7.2f Receiver-Standpoint Reconstruction with Snapshot Audit",
        "",
        "Status: executed after writing Stage_B7_2f_preregistration.md.",
        "",
        "## Important Boundary",
        "",
        "B7.2f uses empirical window snapshots from the sparse-event table. It does not claim to simulate a true iterative convergence process.",
        "",
        "## Primary Classification",
        "",
        classification.to_csv(index=False).strip(),
        "",
        "## Component Summary",
        "",
        summary.to_csv(index=False).strip(),
        "",
        "## Trajectory Summary",
        "",
        traj.to_csv(index=False).strip(),
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
    b6p = b71a.load_module("b6p_for_b72f", b71a.B6P_SCRIPT)
    b71 = b71a.load_module("b71_for_b72f", b71a.B71_SCRIPT)
    b6l, base_table = b6p.build_table(b71a.build_args(args))
    table = make_snapshot_table(base_table, post_k=args.post_convergence_k)
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
    frozen_comp = frozen_filter(comparison)
    summary = component_summary(frozen_comp)
    traj = trajectory_summary(summary)
    classification = classify(summary, traj)
    table.to_csv(outdir / "Stage_B7_2f_snapshot_table.csv", index=False)
    controls.to_csv(outdir / "Stage_B7_2f_control_events.csv", index=False)
    comparison.to_csv(outdir / "Stage_B7_2f_comparison.csv", index=False)
    summary.to_csv(outdir / "Stage_B7_2f_component_summary.csv", index=False)
    traj.to_csv(outdir / "Stage_B7_2f_trajectory_summary.csv", index=False)
    classification.to_csv(outdir / "Stage_B7_2f_primary_classification.csv", index=False)
    write_report(outdir / "Stage_B7_2f_preregistered_summary.md", summary, traj, classification, args)
    print("\nStage B7.2f audit")
    print(f"- output_dir: {outdir}")
    print("\nClassification")
    print(classification.to_string(index=False))
    print("\nTrajectory")
    print(traj.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_2f")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=71206)
    parser.add_argument("--post-convergence-k", type=int, default=1)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
