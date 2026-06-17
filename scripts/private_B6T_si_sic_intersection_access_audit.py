#!/usr/bin/env python3
"""Private B6T SI/SIC Intersection-Access Audit.

Private only. Do not publish, stage, commit, or push.

Question:
    Does C-mediated intersection access survive when the B-side proxy is SI/SIC
    structure from the original IDPC reproduction rather than MQ or an MQ
    residual?

Boundary:
    SI/SIC here is not treated as observable subjectivity. It is an operational
    intersection signature/proxy already frozen in the IDPC_Reproduction reports.
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
B6L_SCRIPT = SCRIPTS / "private_B6L_operator_genesis_audit.py"
B6S_SCRIPT = SCRIPTS / "private_B6S_decoherence_residual_projection_audit.py"

IDPC_REPRO = Path("/Users/satoru/Documents/Codex/2026-04-20-github-github-plugin-github-openai-curated/IDPC_Reproduction")
SIC_TASKS = IDPC_REPRO / "reports/internal_sic_closure_signature_v01_tasks.csv"

OPERATORS = [
    "O1_lag0_AB",
    "O2_lag5_AB",
    "O3_A_C_boundary",
    "O4_B_C_boundary",
    "O5_full_TFC",
    "O6_phase_only",
    "O7_suppress_event",
]

MODES = [
    "combined_c_fes_gmr72",
    "gmr72_phase_conditioned",
    "fes_string_conditioned",
    "linear_c_state",
]

WEIGHT_ENDPOINTS = ["z_reward", "rank_reward", "gmr72_bridge_composite"]

READOUTS = [
    "sic_continuous",
    "si_projection_reception",
    "sic_signature_binary",
    "mq_decohered_reference",
]

CONTROL_KINDS = [
    "true_intersection",
    "random_intersection",
    "balanced_intersection",
    "performance_matched_intersection",
    "shuffled_c_intersection",
    "phase_rotated_intersection",
]

A_TO_B_MASK = {
    "O1_lag0_AB": 0.20,
    "O2_lag5_AB": 0.80,
    "O3_A_C_boundary": 0.10,
    "O4_B_C_boundary": 1.00,
    "O5_full_TFC": 0.65,
    "O6_phase_only": 0.35,
    "O7_suppress_event": 0.05,
}

B_TO_A_MASK = {
    "O1_lag0_AB": 0.80,
    "O2_lag5_AB": 0.35,
    "O3_A_C_boundary": 1.00,
    "O4_B_C_boundary": 0.10,
    "O5_full_TFC": 0.65,
    "O6_phase_only": 0.35,
    "O7_suppress_event": 0.05,
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def z_by_train(train_vals: np.ndarray, vals: np.ndarray) -> np.ndarray:
    train_vals = np.asarray(train_vals, dtype=float)
    vals = np.asarray(vals, dtype=float)
    mu = np.nanmean(train_vals)
    sd = np.nanstd(train_vals)
    if not np.isfinite(sd) or sd <= 1e-12:
        return np.zeros(len(vals), dtype=float)
    return (vals - mu) / sd


def z_series(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").astype(float)
    med = x.median()
    x = x.fillna(med if np.isfinite(med) else 0.0)
    sd = x.std(ddof=0)
    if not np.isfinite(sd) or sd <= 1e-12:
        return pd.Series(np.zeros(len(x)), index=s.index)
    return (x - x.mean()) / sd


def bool_num(s: pd.Series) -> pd.Series:
    return s.fillna(False).astype(bool).astype(float)


def normalize_weights(weights: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    weights = np.where(np.isfinite(weights), weights, 0.0)
    weights = np.clip(weights, 0.0, None)
    total = float(np.sum(weights))
    if total <= 1e-12:
        return np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    return weights / total


def rotate_weights(weights: np.ndarray, shift: int = 1) -> np.ndarray:
    out = np.asarray(weights, dtype=float).copy()
    out[:5] = np.roll(out[:5], shift)
    return normalize_weights(out)


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 2010)
    labels = np.asarray(sorted(set(map(str, labels))), dtype=object)
    rng.shuffle(labels)
    return [fold for fold in np.array_split(labels, n_folds) if len(fold)]


def signflip_p(diff: np.ndarray, rng: np.random.Generator, n_perm: int, alternative: str = "greater") -> tuple[float, float]:
    diff = np.asarray(diff, dtype=float)
    diff = diff[np.isfinite(diff)]
    if len(diff) < 6:
        return np.nan, np.nan
    obs = float(np.nanmean(diff))
    count = 1
    for _ in range(n_perm):
        signs = rng.choice([-1.0, 1.0], size=len(diff), replace=True)
        stat = float(np.nanmean(diff * signs))
        passed = stat >= obs if alternative == "greater" else abs(stat) >= abs(obs)
        if passed:
            count += 1
    return obs, count / float(n_perm + 1)


def task_count_for_sic(label: str, sic: pd.DataFrame) -> int:
    sub = sic[sic["label"].astype(str).eq(str(label))]
    if sub.empty:
        return 30
    vals = pd.to_numeric(sub["task_idx"], errors="coerce")
    vals = vals[np.isfinite(vals)]
    return int(vals.max()) + 1 if len(vals) else 30


def load_sic_tasks() -> pd.DataFrame:
    sic = pd.read_csv(SIC_TASKS)
    sic["label"] = sic["label"].astype(str)
    for col in [
        "task_projection_reception_score",
        "task_pressure_score",
        "task_pressure_abs_score",
        "pressure_high_rate",
        "j_correction_score",
    ]:
        if col not in sic:
            sic[col] = np.nan
    sic["si_projection_reception_raw"] = pd.to_numeric(sic["task_projection_reception_score"], errors="coerce")
    sic["sic_signature_binary_raw"] = bool_num(sic.get("signature_any", pd.Series(False, index=sic.index)))
    sic["sic_continuous_raw"] = (
        z_series(sic["task_projection_reception_score"])
        + z_series(sic["task_pressure_abs_score"])
        + z_series(sic["pressure_high_rate"])
        + z_series(sic["j_correction_score"])
        + 0.5 * bool_num(sic.get("gate_closed", pd.Series(False, index=sic.index)))
        + 0.5 * bool_num(sic.get("closure_event", pd.Series(False, index=sic.index)))
        + bool_num(sic.get("signature_any", pd.Series(False, index=sic.index)))
        - 0.5 * bool_num(sic.get("near_miss_candidate_any", pd.Series(False, index=sic.index)))
        - 0.5 * bool_num(sic.get("is_absorbed_closure", pd.Series(False, index=sic.index)))
    )
    keep = [
        "label",
        "task_idx",
        "si_projection_reception_raw",
        "sic_continuous_raw",
        "sic_signature_binary_raw",
        "rule_state",
        "sic_v01_strict",
        "sic_v01_relaxed",
        "signature_any",
    ]
    return sic[[c for c in keep if c in sic.columns]].copy()


def build_base_table(args: argparse.Namespace):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6l = load_module("private_b6l_for_b6t", B6L_SCRIPT)
    table = b6l.build_table(args)
    annotated = pd.read_csv(args.annotated)
    keep = ["label", "idx_in_session", "kappa", "mq", "phase", "strength"]
    annotated = annotated[[c for c in keep if c in annotated.columns]].copy()
    annotated["label"] = annotated["label"].astype(str)
    point_counts = annotated.groupby("label")["idx_in_session"].max().add(1).astype(int).to_dict()

    out = table.merge(annotated, on=["label", "idx_in_session"], how="left", suffixes=("", "_annot"))
    out["label"] = out["label"].astype(str)
    sic = load_sic_tasks()
    task_rows = []
    for _, row in out.iterrows():
        label = str(row["label"])
        point_count = max(int(point_counts.get(label, 418)), 1)
        t_count = max(task_count_for_sic(label, sic), 1)
        task_idx = int(np.clip(np.floor(float(row["idx_in_session"]) / point_count * t_count), 0, t_count - 1))
        task_rows.append({"label": label, "idx_in_session": row["idx_in_session"], "sic_task_idx": task_idx})
    task_map = pd.DataFrame(task_rows)
    out = out.merge(task_map, on=["label", "idx_in_session"], how="left")
    sic = sic.rename(columns={"task_idx": "sic_task_idx"})
    out = out.merge(sic, on=["label", "sic_task_idx"], how="left")
    out["mq_decohered_reference_raw"] = pd.to_numeric(out.get("mq"), errors="coerce")
    if "phase_annot" in out.columns:
        out["phase_raw"] = out["phase_annot"].combine_first(out.get("phase"))
    else:
        out["phase_raw"] = out.get("phase")
    return b6l, out


def future_by_label(df: pd.DataFrame, col: str, delta: int = 5) -> np.ndarray:
    out = np.full(len(df), np.nan, dtype=float)
    for _, sub in df.groupby("label", sort=False):
        idxs = sub.index.to_numpy()
        times = pd.to_numeric(sub["idx_in_session"], errors="coerce").to_numpy(dtype=float)
        vals = pd.to_numeric(sub[col], errors="coerce").to_numpy(dtype=float)
        for local_i, row_idx in enumerate(idxs):
            candidates = np.where(times >= times[local_i] + delta)[0]
            candidates = candidates[candidates > local_i]
            out[df.index.get_loc(row_idx)] = vals[candidates[0]] if len(candidates) else np.nan
    return out


def add_proxy_primitives(train: pd.DataFrame, test: pd.DataFrame, readout: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = f"{readout}_raw"
    train = train.sort_values(["label", "idx_in_session"]).copy()
    test = test.sort_values(["label", "idx_in_session"]).copy()
    k_train = pd.to_numeric(train["kappa"], errors="coerce").to_numpy(dtype=float)
    b_train = pd.to_numeric(train[raw], errors="coerce").to_numpy(dtype=float)
    k_test = pd.to_numeric(test["kappa"], errors="coerce").to_numpy(dtype=float)
    b_test = pd.to_numeric(test[raw], errors="coerce").to_numpy(dtype=float)
    train["relative_z"] = z_by_train(k_train, k_train)
    test["relative_z"] = z_by_train(k_train, k_test)
    train["b_proxy_z"] = z_by_train(b_train, b_train)
    test["b_proxy_z"] = z_by_train(b_train, b_test)
    train["b_future5_z"] = future_by_label(train, "b_proxy_z")
    test["b_future5_z"] = future_by_label(test, "b_proxy_z")
    for df in [train, test]:
        phase = pd.to_numeric(df.get("phase_raw", df.get("phase")), errors="coerce").to_numpy(dtype=float)
        df["O1_lag0_AB_sisic_raw"] = df["relative_z"] * df["b_proxy_z"]
        df["O2_lag5_AB_sisic_raw"] = df["relative_z"] * df["b_future5_z"]
        df["O3_A_C_boundary_sisic_raw"] = df["relative_z"] * pd.to_numeric(df["A_C"], errors="coerce")
        df["O4_B_C_boundary_sisic_raw"] = df["b_proxy_z"] * pd.to_numeric(df["B_C"], errors="coerce")
        df["O5_full_TFC_sisic_raw"] = df["b_proxy_z"] * pd.to_numeric(df["TFC_mean"], errors="coerce")
        df["O6_phase_only_sisic_raw"] = df["b_proxy_z"] * np.cos(phase)
        df["O7_suppress_event_sisic_raw"] = 0.0
    for op in OPERATORS:
        raw_col = f"{op}_sisic_raw"
        zcol = f"{op}_sisic_z"
        train[zcol] = z_by_train(pd.to_numeric(train[raw_col], errors="coerce").to_numpy(dtype=float), pd.to_numeric(train[raw_col], errors="coerce").to_numpy(dtype=float))
        test[zcol] = z_by_train(pd.to_numeric(train[raw_col], errors="coerce").to_numpy(dtype=float), pd.to_numeric(test[raw_col], errors="coerce").to_numpy(dtype=float))
    return train, test


def train_generators(train: pd.DataFrame, b6l, mode: str, endpoint: str, args: argparse.Namespace, rng: np.random.Generator):
    mapping, global_weights, _, _, policies = b6l.train_weights(train, mode, endpoint, args.min_state_events, args.temperature)
    mapping = {state: normalize_weights(weights) for state, weights in mapping.items()}
    shuffled = list(mapping.values())
    rng.shuffle(shuffled)
    shuffled_mapping = {state: shuffled[i % len(shuffled)] for i, state in enumerate(mapping.keys())} if shuffled else {}
    return {
        "true": mapping,
        "global": normalize_weights(global_weights),
        "shuffled": shuffled_mapping,
        "performance": normalize_weights(b6l.performance_matched_weights(train, endpoint)),
        "policies": policies,
    }


def weights_for(kind: str, state: str, info: dict, rng: np.random.Generator) -> np.ndarray:
    if kind == "true_intersection":
        return info["true"].get(state, info["global"])
    if kind == "random_intersection":
        return normalize_weights(rng.dirichlet(np.ones(len(OPERATORS))))
    if kind == "balanced_intersection":
        return np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    if kind == "performance_matched_intersection":
        return info["performance"]
    if kind == "shuffled_c_intersection":
        return info["shuffled"].get(state, info["global"])
    if kind == "phase_rotated_intersection":
        return rotate_weights(info["true"].get(state, info["global"]), shift=1)
    raise ValueError(f"unknown kind {kind}")


def masked_weights(weights: np.ndarray, direction: str) -> np.ndarray:
    mask_dict = A_TO_B_MASK if direction == "Relative_to_SI_SIC" else B_TO_A_MASK
    mask = np.asarray([mask_dict[op] for op in OPERATORS], dtype=float)
    return normalize_weights(normalize_weights(weights) * mask)


def row_reward(row: pd.Series, weights: np.ndarray) -> float:
    vals = np.asarray([pd.to_numeric(row.get(f"{op}_sisic_z", np.nan), errors="coerce") for op in OPERATORS], dtype=float)
    mask = np.isfinite(vals) & np.isfinite(weights)
    if not mask.any():
        return np.nan
    w = normalize_weights(np.asarray(weights, dtype=float)[mask])
    return float(np.nansum(w * vals[mask]))


def baseline(row: pd.Series) -> dict[str, float]:
    a = float(pd.to_numeric(row.get("O3_A_C_boundary_sisic_z", np.nan), errors="coerce"))
    b = float(pd.to_numeric(row.get("O4_B_C_boundary_sisic_z", np.nan), errors="coerce"))
    full = float(pd.to_numeric(row.get("O5_full_TFC_sisic_z", np.nan), errors="coerce"))
    neutral = row_reward(row, np.ones(len(OPERATORS)) / len(OPERATORS))
    return {
        "relative_alone": a,
        "si_sic_alone": b,
        "neutral": neutral,
        "full_tfc": full,
        "baseline_max": float(np.nanmax([a, b, neutral, full])),
    }


def run_access(table: pd.DataFrame, b6l, mode: str, endpoint: str, readout: str, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 2020)
    data = table.copy()
    data["b6t_state_label"] = b6l.state_labels(data, mode)
    valid_labels = data.loc[np.isfinite(pd.to_numeric(data[f"{readout}_raw"], errors="coerce")), "label"].astype(str).unique()
    folds = make_folds(valid_labels, min(args.n_folds, max(len(valid_labels), 1)), args.seed)
    rows = []
    policies_all = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy().reset_index(drop=True)
        train, test = add_proxy_primitives(train, test, readout)
        test = test[np.isfinite(pd.to_numeric(test[f"{readout}_raw"], errors="coerce"))].copy()
        if test.empty:
            continue
        info = train_generators(train, b6l, mode, endpoint, args, rng)
        policies = info["policies"].copy()
        if not policies.empty:
            policies["fold"] = fold_index
            policies["mode"] = mode
            policies["weight_endpoint"] = endpoint
            policies["readout"] = readout
            policies_all.extend(policies.to_dict("records"))
        for _, row in test.iterrows():
            state = str(row["b6t_state_label"])
            base = baseline(row)
            for direction in ["Relative_to_SI_SIC", "SI_SIC_to_Relative"]:
                for kind in CONTROL_KINDS:
                    weights = masked_weights(weights_for(kind, state, info, rng), direction)
                    access = row_reward(row, weights)
                    rows.append(
                        {
                            "mode": mode,
                            "weight_endpoint": endpoint,
                            "readout": readout,
                            "fold": fold_index,
                            "label": row["label"],
                            "idx_in_session": row["idx_in_session"],
                            "sic_task_idx": row.get("sic_task_idx", np.nan),
                            "state_label": state,
                            "direction": direction,
                            "control_kind": kind,
                            "access_readout": access,
                            "intersection_access_effect": access - base["baseline_max"] if np.isfinite(access) and np.isfinite(base["baseline_max"]) else np.nan,
                            "relative_alone": base["relative_alone"],
                            "si_sic_alone": base["si_sic_alone"],
                            "neutral": base["neutral"],
                            "full_tfc": base["full_tfc"],
                            "baseline_max": base["baseline_max"],
                            "b_proxy_raw": row.get(f"{readout}_raw", np.nan),
                            "rule_state": row.get("rule_state", "missing"),
                            "signature_any": row.get("signature_any", np.nan),
                        }
                    )
    return pd.DataFrame(rows), pd.DataFrame(policies_all)


def asymmetry_table(access: pd.DataFrame) -> pd.DataFrame:
    key = ["mode", "weight_endpoint", "readout", "fold", "label", "idx_in_session", "state_label", "control_kind"]
    r2b = access[access["direction"].eq("Relative_to_SI_SIC")].set_index(key)
    b2r = access[access["direction"].eq("SI_SIC_to_Relative")].set_index(key)
    joined = r2b[["intersection_access_effect", "access_readout"]].join(
        b2r[["intersection_access_effect", "access_readout"]],
        how="inner",
        lsuffix="_relative_to_sisic",
        rsuffix="_sisic_to_relative",
    ).reset_index()
    joined["readout_asymmetry"] = joined["intersection_access_effect_sisic_to_relative"] - joined["intersection_access_effect_relative_to_sisic"]
    joined["abs_readout_asymmetry"] = joined["readout_asymmetry"].abs()
    return joined


def direction_summary(asym: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 2030)
    rows = []
    for keys, sub in asym.groupby(["mode", "weight_endpoint", "readout", "control_kind"], sort=False):
        vals = pd.to_numeric(sub["readout_asymmetry"], errors="coerce").to_numpy(dtype=float)
        effect, p_two = signflip_p(vals, rng, args.n_perm, alternative="two-sided")
        rows.append(
            {
                "mode": keys[0],
                "weight_endpoint": keys[1],
                "readout": keys[2],
                "control_kind": keys[3],
                "mean_relative_to_sisic": float(np.nanmean(sub["intersection_access_effect_relative_to_sisic"])),
                "mean_sisic_to_relative": float(np.nanmean(sub["intersection_access_effect_sisic_to_relative"])),
                "mean_readout_asymmetry": effect,
                "mean_abs_readout_asymmetry": float(np.nanmean(sub["abs_readout_asymmetry"])),
                "p_asymmetry_two_sided": p_two,
                "dominant_direction": "SI_SIC_to_Relative" if effect > 0 else "Relative_to_SI_SIC",
                "n_events": int(np.isfinite(vals).sum()),
            }
        )
    return pd.DataFrame(rows)


def compare_controls(asym: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 2040)
    rows = []
    controls = [c for c in CONTROL_KINDS if c != "true_intersection"]
    for keys, sub in asym.groupby(["mode", "weight_endpoint", "readout"], sort=False):
        true = sub[sub["control_kind"].eq("true_intersection")].set_index(["fold", "label", "idx_in_session", "state_label"])
        for metric in ["abs_readout_asymmetry", "readout_asymmetry"]:
            for control in controls:
                comp = sub[sub["control_kind"].eq(control)].set_index(["fold", "label", "idx_in_session", "state_label"])
                joined = true[[metric]].join(comp[[metric]], how="inner", lsuffix="_true", rsuffix="_control")
                diff = joined[f"{metric}_true"].to_numpy(dtype=float) - joined[f"{metric}_control"].to_numpy(dtype=float)
                effect, p = signflip_p(diff, rng, args.n_perm, alternative="greater")
                rows.append(
                    {
                        "mode": keys[0],
                        "weight_endpoint": keys[1],
                        "readout": keys[2],
                        "metric": metric,
                        "comparison": f"true_vs_{control}",
                        "mean_true": float(np.nanmean(joined[f"{metric}_true"])),
                        "mean_control": float(np.nanmean(joined[f"{metric}_control"])),
                        "effect": effect,
                        "p_greater": p,
                        "n_pairs": int(np.isfinite(diff).sum()),
                    }
                )
    return pd.DataFrame(rows)


def compare_access_controls(access: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 2045)
    rows = []
    controls = [c for c in CONTROL_KINDS if c != "true_intersection"]
    for keys, sub in access.groupby(["mode", "weight_endpoint", "readout", "direction"], sort=False):
        true = sub[sub["control_kind"].eq("true_intersection")].set_index(["fold", "label", "idx_in_session", "state_label"])
        for metric in ["access_readout", "intersection_access_effect"]:
            for control in controls:
                comp = sub[sub["control_kind"].eq(control)].set_index(["fold", "label", "idx_in_session", "state_label"])
                joined = true[[metric]].join(comp[[metric]], how="inner", lsuffix="_true", rsuffix="_control")
                diff = joined[f"{metric}_true"].to_numpy(dtype=float) - joined[f"{metric}_control"].to_numpy(dtype=float)
                effect, p = signflip_p(diff, rng, args.n_perm, alternative="greater")
                rows.append(
                    {
                        "mode": keys[0],
                        "weight_endpoint": keys[1],
                        "readout": keys[2],
                        "direction": keys[3],
                        "metric": metric,
                        "comparison": f"true_vs_{control}",
                        "mean_true": float(np.nanmean(joined[f"{metric}_true"])),
                        "mean_control": float(np.nanmean(joined[f"{metric}_control"])),
                        "effect": effect,
                        "p_greater": p,
                        "n_pairs": int(np.isfinite(diff).sum()),
                    }
                )
    return pd.DataFrame(rows)


def summarize_access(access: pd.DataFrame, comparisons: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, sub in access.groupby(["mode", "weight_endpoint", "readout", "direction"], sort=False):
        mode, endpoint, readout, direction = keys
        true = sub[sub["control_kind"].eq("true_intersection")]
        by = comparisons[
            comparisons["mode"].eq(mode)
            & comparisons["weight_endpoint"].eq(endpoint)
            & comparisons["readout"].eq(readout)
            & comparisons["direction"].eq(direction)
            & comparisons["metric"].eq("intersection_access_effect")
        ].set_index("comparison")
        minimum_names = [
            "true_vs_random_intersection",
            "true_vs_balanced_intersection",
            "true_vs_shuffled_c_intersection",
        ]
        strong_names = [
            "true_vs_performance_matched_intersection",
            "true_vs_phase_rotated_intersection",
        ]
        minimum = all(
            name in by.index and by.loc[name, "effect"] > 0 and by.loc[name, "p_greater"] <= 0.05
            for name in minimum_names
        )
        strong = minimum and all(
            name in by.index and by.loc[name, "effect"] > 0 and by.loc[name, "p_greater"] <= 0.05
            for name in strong_names
        )
        rows.append(
            {
                "mode": mode,
                "weight_endpoint": endpoint,
                "readout": readout,
                "direction": direction,
                "minimum_access_success": minimum,
                "strong_access_success": strong,
                "mean_intersection_access_effect": float(np.nanmean(true["intersection_access_effect"])),
                "mean_access_readout": float(np.nanmean(true["access_readout"])),
                "n_events": int(len(true)),
                "effect_vs_random": float(by.loc["true_vs_random_intersection", "effect"]) if "true_vs_random_intersection" in by.index else np.nan,
                "p_vs_random": float(by.loc["true_vs_random_intersection", "p_greater"]) if "true_vs_random_intersection" in by.index else np.nan,
                "effect_vs_balanced": float(by.loc["true_vs_balanced_intersection", "effect"]) if "true_vs_balanced_intersection" in by.index else np.nan,
                "p_vs_balanced": float(by.loc["true_vs_balanced_intersection", "p_greater"]) if "true_vs_balanced_intersection" in by.index else np.nan,
                "effect_vs_shuffled_c": float(by.loc["true_vs_shuffled_c_intersection", "effect"]) if "true_vs_shuffled_c_intersection" in by.index else np.nan,
                "p_vs_shuffled_c": float(by.loc["true_vs_shuffled_c_intersection", "p_greater"]) if "true_vs_shuffled_c_intersection" in by.index else np.nan,
                "effect_vs_performance": float(by.loc["true_vs_performance_matched_intersection", "effect"]) if "true_vs_performance_matched_intersection" in by.index else np.nan,
                "p_vs_performance": float(by.loc["true_vs_performance_matched_intersection", "p_greater"]) if "true_vs_performance_matched_intersection" in by.index else np.nan,
                "effect_vs_phase_rotated": float(by.loc["true_vs_phase_rotated_intersection", "effect"]) if "true_vs_phase_rotated_intersection" in by.index else np.nan,
                "p_vs_phase_rotated": float(by.loc["true_vs_phase_rotated_intersection", "p_greater"]) if "true_vs_phase_rotated_intersection" in by.index else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["strong_access_success", "minimum_access_success", "mean_intersection_access_effect", "effect_vs_balanced"],
        ascending=[False, False, False, False],
    )


def fold_stability(asym: pd.DataFrame) -> pd.DataFrame:
    true = asym[asym["control_kind"].eq("true_intersection")]
    rows = []
    for keys, sub in true.groupby(["mode", "weight_endpoint", "readout"], sort=False):
        fold_means = sub.groupby("fold")["readout_asymmetry"].mean()
        signs = np.sign(fold_means.to_numpy(dtype=float))
        nonzero = signs[signs != 0]
        if len(nonzero):
            pos = float(np.mean(nonzero > 0))
            neg = float(np.mean(nonzero < 0))
            rate = max(pos, neg)
            direction = "SI_SIC_to_Relative" if pos >= neg else "Relative_to_SI_SIC"
        else:
            rate = np.nan
            direction = "none"
        rows.append(
            {
                "mode": keys[0],
                "weight_endpoint": keys[1],
                "readout": keys[2],
                "fold_dominant_direction": direction,
                "fold_direction_stability": rate,
                "n_folds": int(len(fold_means)),
                "fold_mean_asymmetry_min": float(np.nanmin(fold_means)),
                "fold_mean_asymmetry_max": float(np.nanmax(fold_means)),
            }
        )
    return pd.DataFrame(rows)


def summarize(dirs: pd.DataFrame, comps: pd.DataFrame, stability: pd.DataFrame) -> pd.DataFrame:
    rows = []
    true_dirs = dirs[dirs["control_kind"].eq("true_intersection")]
    stab = stability.set_index(["mode", "weight_endpoint", "readout"]) if not stability.empty else pd.DataFrame()
    for _, row in true_dirs.iterrows():
        key = (row["mode"], row["weight_endpoint"], row["readout"])
        comp = comps[
            comps["mode"].eq(key[0])
            & comps["weight_endpoint"].eq(key[1])
            & comps["readout"].eq(key[2])
            & comps["metric"].eq("abs_readout_asymmetry")
        ].set_index("comparison")
        names = [
            "true_vs_random_intersection",
            "true_vs_balanced_intersection",
            "true_vs_performance_matched_intersection",
            "true_vs_shuffled_c_intersection",
            "true_vs_phase_rotated_intersection",
        ]
        pass_count = int(sum(name in comp.index and comp.loc[name, "effect"] > 0 and comp.loc[name, "p_greater"] <= 0.05 for name in names))
        stability_rate = np.nan
        fold_direction = "missing"
        if not stab.empty and key in stab.index:
            stability_rate = float(stab.loc[key, "fold_direction_stability"])
            fold_direction = str(stab.loc[key, "fold_dominant_direction"])
        nonzero = bool(row["p_asymmetry_two_sided"] <= 0.05)
        minimum = bool(nonzero and pass_count >= 3)
        strong = bool(minimum and pass_count >= 4 and stability_rate >= 0.8)
        rows.append(
            {
                "mode": key[0],
                "weight_endpoint": key[1],
                "readout": key[2],
                "minimum_success": minimum,
                "strong_success": strong,
                "control_asymmetry_pass_count": pass_count,
                "true_asymmetry_nonzero": nonzero,
                "fold_direction_stability": stability_rate,
                "dominant_direction": row["dominant_direction"],
                "fold_dominant_direction": fold_direction,
                "mean_relative_to_sisic": float(row["mean_relative_to_sisic"]),
                "mean_sisic_to_relative": float(row["mean_sisic_to_relative"]),
                "mean_readout_asymmetry": float(row["mean_readout_asymmetry"]),
                "mean_abs_readout_asymmetry": float(row["mean_abs_readout_asymmetry"]),
                "p_asymmetry_two_sided": float(row["p_asymmetry_two_sided"]),
                "effect_vs_random_abs": float(comp.loc["true_vs_random_intersection", "effect"]) if "true_vs_random_intersection" in comp.index else np.nan,
                "p_vs_random_abs": float(comp.loc["true_vs_random_intersection", "p_greater"]) if "true_vs_random_intersection" in comp.index else np.nan,
                "effect_vs_balanced_abs": float(comp.loc["true_vs_balanced_intersection", "effect"]) if "true_vs_balanced_intersection" in comp.index else np.nan,
                "p_vs_balanced_abs": float(comp.loc["true_vs_balanced_intersection", "p_greater"]) if "true_vs_balanced_intersection" in comp.index else np.nan,
                "effect_vs_shuffled_c_abs": float(comp.loc["true_vs_shuffled_c_intersection", "effect"]) if "true_vs_shuffled_c_intersection" in comp.index else np.nan,
                "p_vs_shuffled_c_abs": float(comp.loc["true_vs_shuffled_c_intersection", "p_greater"]) if "true_vs_shuffled_c_intersection" in comp.index else np.nan,
                "effect_vs_phase_rotated_abs": float(comp.loc["true_vs_phase_rotated_intersection", "effect"]) if "true_vs_phase_rotated_intersection" in comp.index else np.nan,
                "p_vs_phase_rotated_abs": float(comp.loc["true_vs_phase_rotated_intersection", "p_greater"]) if "true_vs_phase_rotated_intersection" in comp.index else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["readout", "strong_success", "minimum_success", "control_asymmetry_pass_count", "mean_abs_readout_asymmetry"],
        ascending=[True, False, False, False, False],
    )


def write_report(
    path: Path,
    results: pd.DataFrame,
    dirs: pd.DataFrame,
    comps: pd.DataFrame,
    stability: pd.DataFrame,
    access_results: pd.DataFrame,
    access_comps: pd.DataFrame,
    args: argparse.Namespace,
) -> None:
    sic_rows = results[results["readout"].str.startswith("sic")]
    si_rows = results[results["readout"].eq("si_projection_reception")]
    mq_rows = results[results["readout"].eq("mq_decohered_reference")]
    best = results.iloc[0] if len(results) else None
    best_label = f"{best['mode']} / {best['weight_endpoint']} / {best['readout']}" if best is not None else "none"
    lines = [
        "# Private B6T SI/SIC Intersection-Access Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Question: Does C-mediated intersection access survive when the readout uses SI/SIC structure rather than MQ residual or decohered MQ?",
        "",
        "Interpretation boundary: SI/SIC is not scored as observed subjectivity. It is used as a frozen operational intersection signature/proxy from IDPC_Reproduction.",
        "",
        "## SI/SIC Construction",
        "",
        "- `si_projection_reception`: original `task_projection_reception_score`.",
        "- `sic_continuous`: z-composite of projection-reception score, pressure, pressure-high rate, J correction, gate/closure/signature bonuses, and near-miss/absorbed penalties.",
        "- `sic_signature_binary`: original frozen `signature_any` flag. Sparse; treated as secondary.",
        "- `mq_decohered_reference`: decohered MQ reference arm, not an Absolute Subjectivity proxy.",
        "",
        "## Main Findings",
        "",
        f"- strongest condition: {best_label}",
        f"- SI rows minimum/strong: {int(si_rows['minimum_success'].sum())} / {int(si_rows['strong_success'].sum())} of {len(si_rows)}",
        f"- SIC rows minimum/strong: {int(sic_rows['minimum_success'].sum())} / {int(sic_rows['strong_success'].sum())} of {len(sic_rows)}",
        f"- MQ reference minimum/strong: {int(mq_rows['minimum_success'].sum())} / {int(mq_rows['strong_success'].sum())} of {len(mq_rows)}",
        f"- access-survival minimum/strong: {int(access_results['minimum_access_success'].sum())} / {int(access_results['strong_access_success'].sum())} of {len(access_results)}",
        "",
        "## Condition Results",
        "",
        results.to_csv(index=False).strip(),
        "",
        "## Direction Summary",
        "",
        dirs.to_csv(index=False).strip(),
        "",
        "## Control Comparisons",
        "",
        comps.to_csv(index=False).strip(),
        "",
        "## Fold Stability",
        "",
        stability.to_csv(index=False).strip(),
        "",
        "## Access-Survival Results",
        "",
        access_results.to_csv(index=False).strip(),
        "",
        "## Access-Survival Control Comparisons",
        "",
        access_comps.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- n_folds: {args.n_folds}",
        f"- min_state_events: {args.min_state_events}",
        f"- temperature: {args.temperature}",
        f"- n_perm: {args.n_perm}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    b6l, table = build_base_table(args)
    all_access = []
    all_policies = []
    for readout in READOUTS:
        for mode in MODES:
            for endpoint in WEIGHT_ENDPOINTS:
                access, policies = run_access(table, b6l, mode, endpoint, readout, args)
                if not access.empty:
                    all_access.append(access)
                if not policies.empty:
                    all_policies.append(policies)
    access = pd.concat(all_access, ignore_index=True) if all_access else pd.DataFrame()
    policies = pd.concat(all_policies, ignore_index=True) if all_policies else pd.DataFrame()
    asym = asymmetry_table(access)
    dirs = direction_summary(asym, args)
    comps = compare_controls(asym, args)
    stability = fold_stability(asym)
    results = summarize(dirs, comps, stability)
    access_comps = compare_access_controls(access, args)
    access_results = summarize_access(access, access_comps)

    table.to_csv(outdir / "private_B6T_base_table_with_si_sic.csv", index=False)
    access.to_csv(outdir / "private_B6T_si_sic_intersection_access.csv", index=False)
    asym.to_csv(outdir / "private_B6T_si_sic_asymmetry_events.csv", index=False)
    dirs.to_csv(outdir / "private_B6T_direction_summary.csv", index=False)
    comps.to_csv(outdir / "private_B6T_control_comparison.csv", index=False)
    stability.to_csv(outdir / "private_B6T_fold_stability.csv", index=False)
    results.to_csv(outdir / "private_B6T_si_sic_intersection_access_results.csv", index=False)
    access_comps.to_csv(outdir / "private_B6T_access_survival_control_comparison.csv", index=False)
    access_results.to_csv(outdir / "private_B6T_access_survival_results.csv", index=False)
    policies.to_csv(outdir / "private_B6T_generated_policies.csv", index=False)
    write_report(outdir / "private_B6T_si_sic_intersection_access_summary.md", results, dirs, comps, stability, access_results, access_comps, args)
    print("\nPrivate B6T SI/SIC intersection-access outputs")
    print(outdir)
    print(results.to_string(index=False, max_rows=100))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6t_si_sic_intersection_access")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=61940)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
