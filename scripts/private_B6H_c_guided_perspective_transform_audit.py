#!/usr/bin/env python3
"""Private B6H C-guided perspective transform audit.

Question:
    Does C condition coordinate transforms between A-space and B-space?

This differs from B6G cross-prediction. It learns held-out, C-state-conditioned
maps:
    A_t | C_state -> B_{t+delta}
    B_t | C_state -> A_{t+delta}

and compares them with global, no-C, shuffled-state, and random transforms.
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
B6D_SCRIPT = SCRIPTS / "private_B6D_policy_specificity_audit.py"
B6E_ROBUST_SCRIPT = SCRIPTS / "private_B6E_replication_robustness_audit.py"

A_FEATURES = ["kappa", "a_x", "h_loop", "dphi_loop"]
B_FEATURES = ["mq", "a_y", "phi_loop", "J_tilde_loop"]
ENDPOINTS = ["A_to_B_transform", "B_to_A_transform", "bidirectional_transform", "transform_balance", "transform_asymmetry"]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 860)
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


def standardizer(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = np.nanmean(x, axis=0)
    sd = np.nanstd(x, axis=0)
    sd[~np.isfinite(sd) | (sd <= 1e-12)] = 1.0
    mu[~np.isfinite(mu)] = 0.0
    return mu, sd


def apply_standardizer(x: np.ndarray, mu: np.ndarray, sd: np.ndarray) -> np.ndarray:
    return (x - mu) / sd


def ridge_fit(x: np.ndarray, y: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray]:
    mask = np.isfinite(x).all(axis=1) & np.isfinite(y).all(axis=1)
    x = x[mask]
    y = y[mask]
    if len(x) < x.shape[1] + 2:
        raise ValueError("not enough rows for ridge fit")
    x_aug = np.c_[np.ones(len(x)), x]
    reg = np.eye(x_aug.shape[1]) * alpha
    reg[0, 0] = 0.0
    beta = np.linalg.pinv(x_aug.T @ x_aug + reg) @ x_aug.T @ y
    return beta[0], beta[1:]


def ridge_predict(x: np.ndarray, intercept: np.ndarray, coef: np.ndarray) -> np.ndarray:
    return intercept + x @ coef


def row_score(pred: np.ndarray, target: np.ndarray) -> float:
    if not (np.isfinite(pred).all() and np.isfinite(target).all()):
        return np.nan
    return float(-np.mean((pred - target) ** 2))


def build_base_table(args: argparse.Namespace) -> pd.DataFrame:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6d = load_module("private_b6d_for_b6h", B6D_SCRIPT)
    robust = load_module("private_b6e_robust_for_b6h", B6E_ROBUST_SCRIPT)
    table = b6d.build_state_table(args)
    annotated = pd.read_csv(args.annotated)
    feature_cols = ["label", "idx_in_session", *A_FEATURES, *B_FEATURES]
    keep = [col for col in feature_cols if col in annotated.columns]
    table = table.merge(annotated[keep], on=["label", "idx_in_session"], how="left", suffixes=("", "_annotated"))
    for col in feature_cols:
        alt = f"{col}_annotated"
        if col in {"label", "idx_in_session"}:
            continue
        if col not in table.columns and alt in table.columns:
            table[col] = table[alt]
        elif col in table.columns and alt in table.columns:
            table[col] = table[col].combine_first(table[alt])
    table = robust.set_state_variant(table, args.state_variant)
    return add_future_targets(table, args.delta)


def add_future_targets(table: pd.DataFrame, delta: int) -> pd.DataFrame:
    out = table.sort_values(["label", "idx_in_session"]).reset_index(drop=True).copy()
    for feat in A_FEATURES:
        out[f"future_A_{feat}"] = np.nan
    for feat in B_FEATURES:
        out[f"future_B_{feat}"] = np.nan
    for _, sub in out.groupby("label", sort=False):
        idxs = sub.index.to_numpy()
        times = pd.to_numeric(sub["idx_in_session"], errors="coerce").to_numpy(dtype=float)
        for local_i, row_index in enumerate(idxs):
            candidates = np.where(times >= times[local_i] + delta)[0]
            candidates = candidates[candidates > local_i]
            if len(candidates) == 0:
                continue
            future_index = idxs[int(candidates[0])]
            for feat in A_FEATURES:
                out.loc[row_index, f"future_A_{feat}"] = out.loc[future_index, feat]
            for feat in B_FEATURES:
                out.loc[row_index, f"future_B_{feat}"] = out.loc[future_index, feat]
    return out


def matrices(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    a_x = df[A_FEATURES].to_numpy(dtype=float)
    b_x = df[B_FEATURES].to_numpy(dtype=float)
    future_a = df[[f"future_A_{feat}" for feat in A_FEATURES]].to_numpy(dtype=float)
    future_b = df[[f"future_B_{feat}" for feat in B_FEATURES]].to_numpy(dtype=float)
    return a_x, b_x, future_a, future_b


def fit_pair(train: pd.DataFrame, alpha: float) -> dict[str, object]:
    a_x, b_x, future_a, future_b = matrices(train)
    a_mu, a_sd = standardizer(a_x)
    b_mu, b_sd = standardizer(b_x)
    fa_mu, fa_sd = standardizer(future_a)
    fb_mu, fb_sd = standardizer(future_b)
    ax = apply_standardizer(a_x, a_mu, a_sd)
    bx = apply_standardizer(b_x, b_mu, b_sd)
    fa = apply_standardizer(future_a, fa_mu, fa_sd)
    fb = apply_standardizer(future_b, fb_mu, fb_sd)
    a2b_i, a2b_c = ridge_fit(ax, fb, alpha)
    b2a_i, b2a_c = ridge_fit(bx, fa, alpha)
    return {
        "a_mu": a_mu,
        "a_sd": a_sd,
        "b_mu": b_mu,
        "b_sd": b_sd,
        "fa_mu": fa_mu,
        "fa_sd": fa_sd,
        "fb_mu": fb_mu,
        "fb_sd": fb_sd,
        "a2b_i": a2b_i,
        "a2b_c": a2b_c,
        "b2a_i": b2a_i,
        "b2a_c": b2a_c,
    }


def predict_scores(model: dict[str, object], row: pd.Series) -> tuple[float, float]:
    a = row[A_FEATURES].to_numpy(dtype=float)[None, :]
    b = row[B_FEATURES].to_numpy(dtype=float)[None, :]
    future_a = row[[f"future_A_{feat}" for feat in A_FEATURES]].to_numpy(dtype=float)
    future_b = row[[f"future_B_{feat}" for feat in B_FEATURES]].to_numpy(dtype=float)
    az = apply_standardizer(a, model["a_mu"], model["a_sd"])
    bz = apply_standardizer(b, model["b_mu"], model["b_sd"])
    faz = apply_standardizer(future_a[None, :], model["fa_mu"], model["fa_sd"])[0]
    fbz = apply_standardizer(future_b[None, :], model["fb_mu"], model["fb_sd"])[0]
    pred_b = ridge_predict(az, model["a2b_i"], model["a2b_c"])[0]
    pred_a = ridge_predict(bz, model["b2a_i"], model["b2a_c"])[0]
    return row_score(pred_b, fbz), row_score(pred_a, faz)


def train_models(train: pd.DataFrame, min_state_events: int, alpha: float, rng: np.random.Generator) -> tuple[dict[str, dict[str, object]], dict[str, object], dict[str, dict[str, object]], dict[str, object]]:
    global_model = fit_pair(train, alpha)
    state_models: dict[str, dict[str, object]] = {}
    shuffled_models: dict[str, dict[str, object]] = {}
    shuffled = train.copy()
    state_values = shuffled["state_label"].to_numpy(copy=True)
    rng.shuffle(state_values)
    shuffled["state_label"] = state_values
    for state, sub in train.groupby("state_label", sort=False):
        if len(sub) < min_state_events:
            continue
        try:
            state_models[str(state)] = fit_pair(sub, alpha)
        except ValueError:
            pass
    for state, sub in shuffled.groupby("state_label", sort=False):
        if len(sub) < min_state_events:
            continue
        try:
            shuffled_models[str(state)] = fit_pair(sub, alpha)
        except ValueError:
            pass
    random_model = random_transform_model(train, alpha, rng)
    return state_models, global_model, shuffled_models, random_model


def random_transform_model(train: pd.DataFrame, alpha: float, rng: np.random.Generator) -> dict[str, object]:
    shuffled = train.copy()
    for col in [f"future_A_{feat}" for feat in A_FEATURES]:
        vals = shuffled[col].to_numpy(copy=True)
        rng.shuffle(vals)
        shuffled[col] = vals
    for col in [f"future_B_{feat}" for feat in B_FEATURES]:
        vals = shuffled[col].to_numpy(copy=True)
        rng.shuffle(vals)
        shuffled[col] = vals
    return fit_pair(shuffled, alpha)


def no_c_scores(train: pd.DataFrame, test_row: pd.Series) -> tuple[float, float]:
    _, _, future_a, future_b = matrices(train)
    fa_mu, fa_sd = standardizer(future_a)
    fb_mu, fb_sd = standardizer(future_b)
    target_a = test_row[[f"future_A_{feat}" for feat in A_FEATURES]].to_numpy(dtype=float)
    target_b = test_row[[f"future_B_{feat}" for feat in B_FEATURES]].to_numpy(dtype=float)
    target_a = apply_standardizer(target_a[None, :], fa_mu, fa_sd)[0]
    target_b = apply_standardizer(target_b[None, :], fb_mu, fb_sd)[0]
    return row_score(np.zeros_like(target_b), target_b), row_score(np.zeros_like(target_a), target_a)


def cross_validated_transforms(table: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 870)
    folds = make_folds(table["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = table["label"].astype(str).isin(set(test_labels))
        train = table[~test_mask].copy()
        test = table[test_mask].copy().reset_index(drop=True)
        state_models, global_model, shuffled_models, random_model = train_models(train, args.min_state_events, args.ridge_alpha, rng)
        for _, row in test.iterrows():
            state = str(row["state_label"])
            true_model = state_models.get(state, global_model)
            shuffled_model = shuffled_models.get(state, global_model)
            scores = {}
            for name, model in [
                ("c_conditioned", true_model),
                ("global", global_model),
                ("shuffled_c_state", shuffled_model),
                ("random_transform", random_model),
            ]:
                a2b, b2a = predict_scores(model, row)
                scores[f"{name}_A_to_B"] = a2b
                scores[f"{name}_B_to_A"] = b2a
            no_c_a2b, no_c_b2a = no_c_scores(train, row)
            scores["no_c_A_to_B"] = no_c_a2b
            scores["no_c_B_to_A"] = no_c_b2a
            out = {
                "fold": fold_index,
                "label": row["label"],
                "idx_in_session": row["idx_in_session"],
                "state_label": state,
                "c_transform_source": "state_mapping" if state in state_models else "global_fallback",
            }
            out.update(scores)
            for name in ["c_conditioned", "global", "shuffled_c_state", "random_transform", "no_c"]:
                a2b = out[f"{name}_A_to_B"]
                b2a = out[f"{name}_B_to_A"]
                out[f"{name}_bidirectional"] = min(a2b, b2a) if np.isfinite(a2b) and np.isfinite(b2a) else np.nan
                out[f"{name}_balance"] = -abs(a2b - b2a) if np.isfinite(a2b) and np.isfinite(b2a) else np.nan
                out[f"{name}_asymmetry"] = a2b - b2a if np.isfinite(a2b) and np.isfinite(b2a) else np.nan
            rows.append(out)
    return pd.DataFrame(rows)


def summarize(cv: pd.DataFrame, n_perm: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 880)
    comparisons = ["global", "shuffled_c_state", "random_transform", "no_c"]
    metric_map = {
        "A_to_B_transform": "A_to_B",
        "B_to_A_transform": "B_to_A",
        "bidirectional_transform": "bidirectional",
        "transform_balance": "balance",
        "transform_asymmetry": "asymmetry",
    }
    rows = []
    for endpoint, suffix in metric_map.items():
        true_values = pd.to_numeric(cv[f"c_conditioned_{suffix}"], errors="coerce").to_numpy(dtype=float)
        for comp in comparisons:
            comp_values = pd.to_numeric(cv[f"{comp}_{suffix}"], errors="coerce").to_numpy(dtype=float)
            if endpoint == "transform_asymmetry":
                true_eval = -np.abs(true_values)
                comp_eval = -np.abs(comp_values)
            else:
                true_eval = true_values
                comp_eval = comp_values
            effect, p = signflip_p(true_eval - comp_eval, rng, n_perm)
            rows.append(
                {
                    "endpoint": endpoint,
                    "comparison": f"C_conditioned_transform_vs_{comp}",
                    "mean_C_conditioned": float(np.nanmean(true_eval)),
                    "mean_comparator": float(np.nanmean(comp_eval)),
                    "effect": effect,
                    "p_greater": p,
                    "n_events": int(np.isfinite(true_eval - comp_eval).sum()),
                    "state_mapping_rate": float(np.nanmean(cv["c_transform_source"].eq("state_mapping"))),
                }
            )
    return pd.DataFrame(rows)


def classify(summary: pd.DataFrame) -> str:
    primary = summary[summary["endpoint"].eq("bidirectional_transform")].set_index("comparison")
    required = [
        "C_conditioned_transform_vs_global",
        "C_conditioned_transform_vs_shuffled_c_state",
        "C_conditioned_transform_vs_random_transform",
        "C_conditioned_transform_vs_no_c",
    ]
    ok = True
    for name in required:
        if name not in primary.index:
            ok = False
            continue
        row = primary.loc[name]
        ok = ok and bool(row["effect"] > 0 and row["p_greater"] <= 0.05)
    if ok:
        return "B6H success: C-conditioned bidirectional perspective transform beats global, shuffled-C, random, and no-C transforms."
    if any(
        name in primary.index and primary.loc[name, "effect"] > 0 and primary.loc[name, "p_greater"] <= 0.05
        for name in required
    ):
        return "Partial B6H signal: C-conditioned transform beats at least one transform control but not the full set."
    return "B6H not supported by this private perspective transform audit."


def write_report(path: Path, summary: pd.DataFrame, source_summary: pd.DataFrame, classification: str, args: argparse.Namespace) -> None:
    lines = [
        "# Private B6H C-Guided Perspective Transform Audit",
        "",
        "Status: local/private screen only. No publication, commit, or push was performed.",
        "",
        "Primary hypothesis: C enables perspective-dependent coordinate transformation, not merely cross-prediction.",
        "",
        "Transforms:",
        "",
        "- A_t | C_state -> B_{t+delta}",
        "- B_t | C_state -> A_{t+delta}",
        "",
        "Primary endpoint:",
        "",
        "`bidirectional_transform = min(A_to_B_transform, B_to_A_transform)`.",
        "",
        "Controls:",
        "",
        "- global transform",
        "- shuffled C-state transform",
        "- random transform",
        "- no-C mean transform",
        "",
        "## Classification",
        "",
        classification,
        "",
        "## Comparison Summary",
        "",
        summary.to_csv(index=False).strip(),
        "",
        "## Source Summary",
        "",
        source_summary.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- state_variant: {args.state_variant}",
        f"- delta: {args.delta}",
        f"- n_folds: {args.n_folds}",
        f"- min_state_events: {args.min_state_events}",
        f"- ridge_alpha: {args.ridge_alpha}",
        f"- n_perm: {args.n_perm}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    table = build_base_table(args)
    cv = cross_validated_transforms(table, args)
    summary = summarize(cv, args.n_perm, args.seed)
    classification = classify(summary)
    source_summary = cv.groupby("c_transform_source", as_index=False).agg(
        n_events=("c_transform_source", "size"),
        mean_bidirectional=("c_conditioned_bidirectional", "mean"),
        mean_A_to_B=("c_conditioned_A_to_B", "mean"),
        mean_B_to_A=("c_conditioned_B_to_A", "mean"),
    )
    table.to_csv(outdir / "private_B6H_state_transform_table.csv", index=False)
    cv.to_csv(outdir / "private_B6H_heldout_transform_scores.csv", index=False)
    summary.to_csv(outdir / "private_B6H_comparison_summary.csv", index=False)
    source_summary.to_csv(outdir / "private_B6H_source_summary.csv", index=False)
    write_report(outdir / "private_B6H_perspective_transform_summary.md", summary, source_summary, classification, args)
    print("\nPrivate B6H perspective transform outputs")
    print(outdir)
    print("\nClassification")
    print(classification)
    print("\nPrimary bidirectional transform summary")
    print(summary[summary["endpoint"].eq("bidirectional_transform")].to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6h_perspective_transform")
    parser.add_argument("--state-variant", default="side_tfc")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--delta", type=int, default=5)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=12)
    parser.add_argument("--ridge-alpha", type=float, default=1.0)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=60710)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
