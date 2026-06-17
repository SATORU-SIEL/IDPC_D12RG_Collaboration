#!/usr/bin/env python3
"""Private B6S Decoherence-Residual Projection Audit.

Private only. Do not publish, stage, commit, or push.

Question:
    Does C-mediated directional asymmetry appear when the quantum side is
    represented by a decoherence-residual proxy rather than by the decohered
    MQ readout itself?

Boundary:
    Q_residual is not Absolute Subjectivity. It is a less-decohered projection
    proxy: the component of MQ not explained by simple classical/decohered
    predictors in the training fold.
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
READOUTS = ["q_residual", "mq_decohered"]

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


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 1910)
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
        if alternative == "greater":
            passed = stat >= obs
        elif alternative == "two-sided":
            passed = abs(stat) >= abs(obs)
        else:
            raise ValueError(f"unknown alternative {alternative}")
        if passed:
            count += 1
    return obs, count / float(n_perm + 1)


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


def masked_weights(weights: np.ndarray, direction: str) -> np.ndarray:
    mask_dict = A_TO_B_MASK if direction == "Relative_to_Qresidual" else B_TO_A_MASK
    mask = np.asarray([mask_dict[op] for op in OPERATORS], dtype=float)
    return normalize_weights(normalize_weights(weights) * mask)


def build_base_table(args: argparse.Namespace):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6l = load_module("private_b6l_for_b6s", B6L_SCRIPT)
    table = b6l.build_table(args)
    annotated = pd.read_csv(args.annotated)
    keep = ["label", "idx_in_session", "kappa", "mq", "phase", "strength"]
    annotated = annotated[[c for c in keep if c in annotated.columns]].copy()
    out = table.merge(annotated, on=["label", "idx_in_session"], how="left", suffixes=("", "_annot"))
    if "phase_annot" in out.columns:
        out["phase_raw"] = out["phase_annot"].combine_first(out.get("phase"))
    else:
        out["phase_raw"] = out.get("phase")
    if "strength_annot" in out.columns:
        out["strength_raw"] = out["strength_annot"].combine_first(out.get("strength"))
    else:
        out["strength_raw"] = out.get("strength")
    return b6l, out


def design_matrix(df: pd.DataFrame) -> np.ndarray:
    idx = pd.to_numeric(df["idx_in_session"], errors="coerce").to_numpy(dtype=float)
    idx = np.where(np.isfinite(idx), idx, np.nanmedian(idx))
    idx_norm = (idx - np.nanmean(idx)) / (np.nanstd(idx) + 1e-9)
    phase = pd.to_numeric(df.get("phase_raw", df.get("phase")), errors="coerce").to_numpy(dtype=float)
    strength = pd.to_numeric(df.get("strength_raw", df.get("strength")), errors="coerce").to_numpy(dtype=float)
    cols = [
        np.ones(len(df), dtype=float),
        idx_norm,
        np.sin(phase),
        np.cos(phase),
        np.nan_to_num(strength, nan=np.nanmedian(strength) if np.isfinite(strength).any() else 0.0),
    ]
    for name in ["A_B", "A_C", "B_C", "TFC_min", "TFC_mean", "abs_dphi", "C_memory_scalar"]:
        vals = pd.to_numeric(df.get(name, np.nan), errors="coerce").to_numpy(dtype=float)
        med = np.nanmedian(vals) if np.isfinite(vals).any() else 0.0
        vals = np.nan_to_num(vals, nan=med)
        vals = (vals - np.nanmean(vals)) / (np.nanstd(vals) + 1e-9)
        cols.append(vals)
    return np.vstack(cols).T


def fit_residuals(train: pd.DataFrame, test: pd.DataFrame, readout: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    target_col = "mq"
    y = pd.to_numeric(train[target_col], errors="coerce").to_numpy(dtype=float)
    mask = np.isfinite(y)
    x_train = design_matrix(train)
    x_test = design_matrix(test)
    if readout == "mq_decohered":
        train_out = train.copy()
        test_out = test.copy()
        q_train = y
        q_test = pd.to_numeric(test[target_col], errors="coerce").to_numpy(dtype=float)
    else:
        if mask.sum() < x_train.shape[1] + 3:
            beta = np.zeros(x_train.shape[1], dtype=float)
            beta[0] = np.nanmean(y[mask]) if mask.any() else 0.0
        else:
            beta = np.linalg.pinv(x_train[mask]).dot(y[mask])
        q_train = y - x_train.dot(beta)
        q_test = pd.to_numeric(test[target_col], errors="coerce").to_numpy(dtype=float) - x_test.dot(beta)
        train_out = train.copy()
        test_out = test.copy()
    train_out["q_proxy_raw"] = q_train
    test_out["q_proxy_raw"] = q_test
    return train_out, test_out


def z_by_train(train_vals: np.ndarray, vals: np.ndarray) -> np.ndarray:
    train_vals = np.asarray(train_vals, dtype=float)
    vals = np.asarray(vals, dtype=float)
    mu = np.nanmean(train_vals)
    sd = np.nanstd(train_vals)
    if not np.isfinite(sd) or sd <= 1e-12:
        return np.zeros(len(vals), dtype=float)
    return (vals - mu) / sd


def add_residual_primitives(train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = train.sort_values(["label", "idx_in_session"]).copy()
    test = test.sort_values(["label", "idx_in_session"]).copy()
    k_train = pd.to_numeric(train["kappa"], errors="coerce").to_numpy(dtype=float)
    q_train = pd.to_numeric(train["q_proxy_raw"], errors="coerce").to_numpy(dtype=float)
    k_test = pd.to_numeric(test["kappa"], errors="coerce").to_numpy(dtype=float)
    q_test = pd.to_numeric(test["q_proxy_raw"], errors="coerce").to_numpy(dtype=float)
    train["kappa_z_resid"] = z_by_train(k_train, k_train)
    test["kappa_z_resid"] = z_by_train(k_train, k_test)
    train["q_proxy_z"] = z_by_train(q_train, q_train)
    test["q_proxy_z"] = z_by_train(q_train, q_test)

    def future_q(df: pd.DataFrame) -> np.ndarray:
        out = np.full(len(df), np.nan, dtype=float)
        for _, sub in df.groupby("label", sort=False):
            idxs = sub.index.to_numpy()
            times = pd.to_numeric(sub["idx_in_session"], errors="coerce").to_numpy(dtype=float)
            vals = sub["q_proxy_z"].to_numpy(dtype=float)
            for local_i, row_idx in enumerate(idxs):
                candidates = np.where(times >= times[local_i] + 5)[0]
                candidates = candidates[candidates > local_i]
                out[df.index.get_loc(row_idx)] = vals[candidates[0]] if len(candidates) else np.nan
        return out

    # Future lag is computed within each split; held-out labels do not leak into training.
    train["q_future5_z"] = future_q(train)
    test["q_future5_z"] = future_q(test)

    for df in [train, test]:
        phase = pd.to_numeric(df.get("phase_raw", df.get("phase")), errors="coerce").to_numpy(dtype=float)
        df["O1_lag0_AB_resid_raw"] = df["kappa_z_resid"] * df["q_proxy_z"]
        df["O2_lag5_AB_resid_raw"] = df["kappa_z_resid"] * df["q_future5_z"]
        df["O3_A_C_boundary_resid_raw"] = df["kappa_z_resid"] * pd.to_numeric(df["A_C"], errors="coerce")
        df["O4_B_C_boundary_resid_raw"] = df["q_proxy_z"] * pd.to_numeric(df["B_C"], errors="coerce")
        df["O5_full_TFC_resid_raw"] = df["q_proxy_z"] * pd.to_numeric(df["TFC_mean"], errors="coerce")
        df["O6_phase_only_resid_raw"] = df["q_proxy_z"] * np.cos(phase)
        df["O7_suppress_event_resid_raw"] = 0.0

    for op in OPERATORS:
        raw = f"{op}_resid_raw"
        zcol = f"{op}_resid_z"
        train[zcol] = z_by_train(pd.to_numeric(train[raw], errors="coerce").to_numpy(dtype=float), pd.to_numeric(train[raw], errors="coerce").to_numpy(dtype=float))
        test[zcol] = z_by_train(pd.to_numeric(train[raw], errors="coerce").to_numpy(dtype=float), pd.to_numeric(test[raw], errors="coerce").to_numpy(dtype=float))
    return train, test


def train_generators(train: pd.DataFrame, b6l, mode: str, endpoint: str, args: argparse.Namespace, rng: np.random.Generator):
    mapping, global_weights, selected_mapping, global_best, policies = b6l.train_weights(
        train, mode, endpoint, args.min_state_events, args.temperature
    )
    mapping = {state: normalize_weights(weights) for state, weights in mapping.items()}
    shuffled = list(mapping.values())
    rng.shuffle(shuffled)
    shuffled_mapping = {state: shuffled[i % len(shuffled)] for i, state in enumerate(mapping.keys())} if shuffled else {}
    perf_weights = normalize_weights(b6l.performance_matched_weights(train, endpoint))
    return {
        "true": mapping,
        "global": normalize_weights(global_weights),
        "shuffled": shuffled_mapping,
        "performance": perf_weights,
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


def row_reward(row: pd.Series, weights: np.ndarray) -> float:
    vals = np.asarray([pd.to_numeric(row.get(f"{op}_resid_z", np.nan), errors="coerce") for op in OPERATORS], dtype=float)
    mask = np.isfinite(vals) & np.isfinite(weights)
    if not mask.any():
        return np.nan
    w = normalize_weights(np.asarray(weights, dtype=float)[mask])
    return float(np.nansum(w * vals[mask]))


def baseline(row: pd.Series) -> dict[str, float]:
    a = float(pd.to_numeric(row.get("O3_A_C_boundary_resid_z", np.nan), errors="coerce"))
    b = float(pd.to_numeric(row.get("O4_B_C_boundary_resid_z", np.nan), errors="coerce"))
    full = float(pd.to_numeric(row.get("O5_full_TFC_resid_z", np.nan), errors="coerce"))
    neutral = row_reward(row, np.ones(len(OPERATORS)) / len(OPERATORS))
    return {
        "A_alone": a,
        "Q_alone": b,
        "neutral": neutral,
        "full_tfc": full,
        "baseline_max": float(np.nanmax([a, b, neutral, full])),
    }


def run_access(table: pd.DataFrame, b6l, mode: str, endpoint: str, readout: str, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 1920)
    data = table.copy()
    data["b6s_state_label"] = b6l.state_labels(data, mode)
    folds = make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    policies_all = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy().reset_index(drop=True)
        train, test = fit_residuals(train, test, readout)
        train, test = add_residual_primitives(train, test)
        info = train_generators(train, b6l, mode, endpoint, args, rng)
        policies = info["policies"].copy()
        if not policies.empty:
            policies["fold"] = fold_index
            policies["mode"] = mode
            policies["weight_endpoint"] = endpoint
            policies["readout"] = readout
            policies_all.extend(policies.to_dict("records"))
        for _, row in test.iterrows():
            state = str(row["b6s_state_label"])
            base = baseline(row)
            for direction in ["Relative_to_Qresidual", "Qresidual_to_Relative"]:
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
                            "state_label": state,
                            "direction": direction,
                            "control_kind": kind,
                            "access_readout": access,
                            "intersection_access_effect": access - base["baseline_max"] if np.isfinite(access) and np.isfinite(base["baseline_max"]) else np.nan,
                            "relative_alone": base["A_alone"],
                            "q_alone": base["Q_alone"],
                            "neutral": base["neutral"],
                            "full_tfc": base["full_tfc"],
                            "baseline_max": base["baseline_max"],
                            "q_proxy_raw": row.get("q_proxy_raw", np.nan),
                        }
                    )
    return pd.DataFrame(rows), pd.DataFrame(policies_all)


def asymmetry_table(access: pd.DataFrame) -> pd.DataFrame:
    key = ["mode", "weight_endpoint", "readout", "fold", "label", "idx_in_session", "state_label", "control_kind"]
    r2q = access[access["direction"].eq("Relative_to_Qresidual")].set_index(key)
    q2r = access[access["direction"].eq("Qresidual_to_Relative")].set_index(key)
    joined = r2q[["intersection_access_effect", "access_readout"]].join(
        q2r[["intersection_access_effect", "access_readout"]],
        how="inner",
        lsuffix="_relative_to_q",
        rsuffix="_q_to_relative",
    ).reset_index()
    joined["readout_asymmetry"] = joined["intersection_access_effect_q_to_relative"] - joined["intersection_access_effect_relative_to_q"]
    joined["abs_readout_asymmetry"] = joined["readout_asymmetry"].abs()
    return joined


def direction_summary(asym: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1930)
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
                "mean_relative_to_q": float(np.nanmean(sub["intersection_access_effect_relative_to_q"])),
                "mean_q_to_relative": float(np.nanmean(sub["intersection_access_effect_q_to_relative"])),
                "mean_readout_asymmetry": effect,
                "mean_abs_readout_asymmetry": float(np.nanmean(sub["abs_readout_asymmetry"])),
                "p_asymmetry_two_sided": p_two,
                "dominant_direction": "Qresidual_to_Relative" if effect > 0 else "Relative_to_Qresidual",
                "n_events": int(np.isfinite(vals).sum()),
            }
        )
    return pd.DataFrame(rows)


def compare_controls(asym: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1940)
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
            direction = "Qresidual_to_Relative" if pos >= neg else "Relative_to_Qresidual"
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
                "mean_relative_to_q": float(row["mean_relative_to_q"]),
                "mean_q_to_relative": float(row["mean_q_to_relative"]),
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
        ascending=[False, False, False, False, False],
    )


def write_report(path: Path, results: pd.DataFrame, dirs: pd.DataFrame, comps: pd.DataFrame, stability: pd.DataFrame, args: argparse.Namespace) -> None:
    residual = results[results["readout"].eq("q_residual")]
    decohered = results[results["readout"].eq("mq_decohered")]
    best = results.iloc[0] if len(results) else None
    best_label = f"{best['mode']} / {best['weight_endpoint']} / {best['readout']}" if best is not None else "none"
    lines = [
        "# Private B6S Decoherence-Residual Projection Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Question: Does a decoherence-residual quantum proxy reveal C-mediated directional asymmetry not visible in decohered MQ readout?",
        "",
        "Interpretation boundary: Q_residual is not Absolute Subjectivity. It is a less-decohered projection proxy.",
        "",
        "## Residual Construction",
        "",
        "- Q_decohered: mq from the B5.5 annotated table.",
        "- Q_pred: train-fold linear prediction from idx, phase, strength, AB/AC/BC, TFC, dphi, and C-memory predictors.",
        "- Q_residual: mq - Q_pred, evaluated on held-out labels.",
        "",
        "## Main Findings",
        "",
        f"- strongest condition: {best_label}",
        f"- q_residual minimum-success conditions: {int(residual['minimum_success'].sum())} / {len(residual)}",
        f"- q_residual strong-success conditions: {int(residual['strong_success'].sum())} / {len(residual)}",
        f"- mq_decohered minimum-success conditions: {int(decohered['minimum_success'].sum())} / {len(decohered)}",
        f"- mq_decohered strong-success conditions: {int(decohered['strong_success'].sum())} / {len(decohered)}",
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

    table.to_csv(outdir / "private_B6S_base_table_with_mq.csv", index=False)
    access.to_csv(outdir / "private_B6S_residual_intersection_access.csv", index=False)
    asym.to_csv(outdir / "private_B6S_residual_projection_asymmetry_events.csv", index=False)
    dirs.to_csv(outdir / "private_B6S_direction_summary.csv", index=False)
    comps.to_csv(outdir / "private_B6S_control_comparison.csv", index=False)
    stability.to_csv(outdir / "private_B6S_fold_stability.csv", index=False)
    results.to_csv(outdir / "private_B6S_decoherence_residual_projection_results.csv", index=False)
    policies.to_csv(outdir / "private_B6S_generated_policies.csv", index=False)
    write_report(outdir / "private_B6S_decoherence_residual_projection_summary.md", results, dirs, comps, stability, args)
    print("\nPrivate B6S decoherence-residual projection outputs")
    print(outdir)
    print(results.to_string(index=False, max_rows=100))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6s_decoherence_residual_projection")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=61820)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
