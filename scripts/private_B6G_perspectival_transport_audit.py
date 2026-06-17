#!/usr/bin/env python3
"""Private B6G perspectival transport audit.

Question:
    Does C-state policy mediate A->C->B and B->C->A transport?

Ontology boundary:
    C is not tested as a future self-improving state. C is tested as the
    mediating condition through which A can be transported into B-perspective
    and B can be transported into A-perspective.
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

OPERATORS = [
    "O1_lag0_AB",
    "O2_lag5_AB",
    "O3_A_C_boundary",
    "O4_B_C_boundary",
    "O5_full_TFC",
    "O6_phase_only",
    "O7_suppress_event",
]

OPERATOR_HORIZON = {
    "O1_lag0_AB": 0,
    "O2_lag5_AB": 5,
    "O3_A_C_boundary": 5,
    "O4_B_C_boundary": 5,
    "O5_full_TFC": 5,
    "O6_phase_only": 1,
    "O7_suppress_event": 5,
}

ENDPOINTS = [
    "A_to_C_to_B",
    "B_to_C_to_A",
    "bidirectional_transport",
    "transport_balance",
    "transport_asymmetry",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = np.full_like(x, np.nan, dtype=float)
    mask = np.isfinite(x)
    if mask.sum() < 3:
        return out
    mu = np.nanmean(x[mask])
    sd = np.nanstd(x[mask])
    if not np.isfinite(sd) or sd <= 1e-12:
        out[mask] = 0.0
    else:
        out[mask] = (x[mask] - mu) / sd
    return out


def corr_abs(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 6:
        return np.nan
    xx = zscore(x[mask])
    yy = zscore(y[mask])
    if np.nanstd(xx) <= 1e-12 or np.nanstd(yy) <= 1e-12:
        return np.nan
    return float(abs(np.corrcoef(xx, yy)[0, 1]))


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


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 830)
    labels = np.asarray(sorted(set(map(str, labels))), dtype=object)
    rng.shuffle(labels)
    return [fold for fold in np.array_split(labels, n_folds) if len(fold)]


def reward(row: pd.Series, operator: str, endpoint: str) -> float:
    return float(row.get(f"{endpoint}_{operator}", np.nan))


def weighted_reward(row: pd.Series, weights: dict[str, float], endpoint: str) -> float:
    vals = []
    wts = []
    for op, wt in weights.items():
        val = reward(row, op, endpoint)
        if np.isfinite(val) and wt > 0:
            vals.append(val * wt)
            wts.append(wt)
    if not wts:
        return np.nan
    return float(np.sum(vals) / np.sum(wts))


def operator_frequency_weights(ops: list[str]) -> dict[str, float]:
    counts = {op: 0 for op in OPERATORS}
    for op in ops:
        if op in counts:
            counts[op] += 1
    total = float(sum(counts.values()))
    if total <= 0:
        return {op: 1.0 / len(OPERATORS) for op in OPERATORS}
    return {op: counts[op] / total for op in OPERATORS}


def build_base_table(args: argparse.Namespace) -> pd.DataFrame:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6d = load_module("private_b6d_for_b6g", B6D_SCRIPT)
    robust = load_module("private_b6e_robust_for_b6g", B6E_ROBUST_SCRIPT)
    table = b6d.build_state_table(args)
    annotated = pd.read_csv(args.annotated)
    feature_cols = [
        "label",
        "idx_in_session",
        "kappa",
        "mq",
        "a_x",
        "a_y",
        "phi_loop",
        "dphi_loop",
        "TFC_min",
        "TFC_mean",
        "A_B",
        "A_C",
        "B_C",
    ]
    keep = [col for col in feature_cols if col in annotated.columns]
    table = table.merge(
        annotated[keep],
        on=["label", "idx_in_session"],
        how="left",
        suffixes=("", "_annotated"),
    )
    for col in feature_cols:
        alt = f"{col}_annotated"
        if col not in table.columns and alt in table.columns:
            table[col] = table[alt]
        elif col in table.columns and alt in table.columns:
            table[col] = table[col].combine_first(table[alt])
    table = robust.set_state_variant(table, args.state_variant)
    return add_transport_endpoints(table, args.window)


def local_transport(sub: pd.DataFrame, pos: int, op: str, window: int) -> tuple[float, float]:
    horizon = OPERATOR_HORIZON[op]
    start = pos + horizon
    end = min(len(sub), start + window)
    if start < 0 or start >= len(sub):
        return np.nan, np.nan
    a1 = pd.to_numeric(sub["kappa"], errors="coerce").to_numpy(dtype=float)
    a2 = pd.to_numeric(sub["a_x"], errors="coerce").to_numpy(dtype=float)
    b1 = pd.to_numeric(sub["mq"], errors="coerce").to_numpy(dtype=float)
    b2 = pd.to_numeric(sub["a_y"], errors="coerce").to_numpy(dtype=float)
    c_phase = pd.to_numeric(sub["phi_loop"], errors="coerce").to_numpy(dtype=float)
    c_strength = pd.to_numeric(sub["strength"], errors="coerce").to_numpy(dtype=float) if "strength" in sub.columns else np.ones(len(sub))
    if op == "O7_suppress_event":
        return 0.0, 0.0
    c_weight = np.nan_to_num(np.abs(np.sin(c_phase[start:end])), nan=0.0) + 0.25 * np.nan_to_num(c_strength[start:end], nan=0.0)
    if op in {"O3_A_C_boundary", "O5_full_TFC"}:
        a_proj = zscore(a1[start:end]) * (1.0 + c_weight)
        b_proj = zscore(b1[start:end])
    elif op == "O4_B_C_boundary":
        a_proj = zscore(a1[start:end])
        b_proj = zscore(b1[start:end]) * (1.0 + c_weight)
    elif op == "O6_phase_only":
        a_proj = zscore(a2[start:end]) * np.sign(np.sin(c_phase[start:end]))
        b_proj = zscore(b2[start:end]) * np.sign(np.cos(c_phase[start:end]))
    elif op == "O1_lag0_AB":
        a_proj = zscore(a1[start:end])
        b_proj = zscore(b1[start:end])
    else:
        a_proj = zscore(a1[start:end]) + 0.25 * zscore(a2[start:end])
        b_proj = zscore(b1[start:end]) + 0.25 * zscore(b2[start:end])
    a_to_b = corr_abs(a_proj, b1[start:end])
    b_to_a = corr_abs(b_proj, a1[start:end])
    return a_to_b, b_to_a


def add_transport_endpoints(table: pd.DataFrame, window: int) -> pd.DataFrame:
    out = table.sort_values(["label", "idx_in_session"]).reset_index(drop=True).copy()
    if "strength" not in out.columns:
        out["strength"] = 1.0
    for op in OPERATORS:
        for endpoint in ENDPOINTS:
            out[f"{endpoint}_{op}_raw"] = np.nan
    for _, sub in out.groupby("label", sort=False):
        idxs = sub.index.to_numpy()
        sub = sub.reset_index(drop=False)
        for local_pos, original_index in enumerate(idxs):
            for op in OPERATORS:
                a2b, b2a = local_transport(sub, local_pos, op, window)
                if not (np.isfinite(a2b) and np.isfinite(b2a)):
                    continue
                bidi = min(a2b, b2a)
                balance = -abs(a2b - b2a)
                asym = a2b - b2a
                out.loc[original_index, f"A_to_C_to_B_{op}_raw"] = a2b
                out.loc[original_index, f"B_to_C_to_A_{op}_raw"] = b2a
                out.loc[original_index, f"bidirectional_transport_{op}_raw"] = bidi
                out.loc[original_index, f"transport_balance_{op}_raw"] = balance
                out.loc[original_index, f"transport_asymmetry_{op}_raw"] = asym
    for endpoint in ENDPOINTS:
        for op in OPERATORS:
            out[f"{endpoint}_{op}"] = zscore(out[f"{endpoint}_{op}_raw"].to_numpy(dtype=float))
    return out


def train_policy(train: pd.DataFrame, min_state_events: int, endpoint: str) -> tuple[dict[str, str], str, pd.DataFrame]:
    global_means = {op: float(np.nanmean(train[f"{endpoint}_{op}"])) for op in OPERATORS}
    global_best = max(global_means, key=global_means.get)
    rows = []
    mapping: dict[str, str] = {}
    for state, sub in train.groupby("state_label", sort=False):
        if len(sub) < min_state_events:
            continue
        means = {op: float(np.nanmean(sub[f"{endpoint}_{op}"])) for op in OPERATORS}
        selected = max(means, key=means.get)
        mapping[str(state)] = selected
        row = {
            "state_label": str(state),
            "n_train_events": int(len(sub)),
            "selected_operator": selected,
            "selected_train_reward": means[selected],
            "global_best_operator": global_best,
            "global_best_train_reward": means[global_best],
        }
        row.update({f"train_mean_{op}": means[op] for op in OPERATORS})
        rows.append(row)
    return mapping, global_best, pd.DataFrame(rows)


def within_state_shuffled_policy(policy_table: pd.DataFrame, rng: np.random.Generator) -> dict[str, str]:
    mapping = {}
    op_array = np.asarray(OPERATORS, dtype=object)
    for _, row in policy_table.iterrows():
        shuffled_labels = op_array.copy()
        rng.shuffle(shuffled_labels)
        means = {shuffled_op: float(row[f"train_mean_{op}"]) for op, shuffled_op in zip(OPERATORS, shuffled_labels)}
        mapping[str(row["state_label"])] = max(means, key=means.get)
    return mapping


def performance_strata(train: pd.DataFrame, endpoint: str) -> dict[str, str]:
    means = {op: float(np.nanmean(train[f"{endpoint}_{op}"])) for op in OPERATORS}
    ordered = sorted(OPERATORS, key=lambda op: means[op])
    strata = {}
    chunks = np.array_split(np.asarray(ordered, dtype=object), 3)
    for label, chunk in zip(["low", "mid", "high"], chunks):
        for op in chunk:
            strata[str(op)] = label
    return strata


def stratum_matched_expected_reward(row: pd.Series, selected_op: str, strata: dict[str, str], endpoint: str) -> float:
    stratum = strata.get(selected_op, "missing")
    candidates = [op for op in OPERATORS if strata.get(op) == stratum]
    if not candidates:
        candidates = OPERATORS
    weights = {op: 1.0 / len(candidates) for op in candidates}
    return weighted_reward(row, weights, endpoint)


def cross_validated_transport(table: pd.DataFrame, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 840)
    folds = make_folds(table["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    policies = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = table["label"].astype(str).isin(set(test_labels))
        train = table[~test_mask].copy()
        test = table[test_mask].copy().reset_index(drop=True)
        mapping, fallback, policy_table = train_policy(train, args.min_state_events, "bidirectional_transport")
        if policy_table.empty:
            continue
        policy_table["fold"] = fold_index
        policies.extend(policy_table.to_dict("records"))
        true_ops = [mapping.get(str(row["state_label"]), fallback) for _, row in test.iterrows()]
        freq_weights = operator_frequency_weights(true_ops)
        strata = performance_strata(train, "bidirectional_transport")
        control_names = ["balanced", "within", "between", "label_perm"]
        control_rewards = {name: {endpoint: np.zeros(len(test), dtype=float) for endpoint in ENDPOINTS} for name in control_names}
        control_counts = {name: {endpoint: np.zeros(len(test), dtype=float) for endpoint in ENDPOINTS} for name in control_names}
        for _ in range(args.n_control_draws):
            shuffled_mapping = within_state_shuffled_policy(policy_table, rng)
            states = policy_table["state_label"].astype(str).to_numpy(copy=True)
            ops = policy_table["selected_operator"].astype(str).to_numpy(copy=True)
            rng.shuffle(ops)
            between_mapping = {state: op for state, op in zip(states, ops)}
            op_array = np.asarray(OPERATORS, dtype=object)
            permuted = op_array.copy()
            rng.shuffle(permuted)
            label_map = {op: new for op, new in zip(op_array, permuted)}
            label_mapping = {str(row["state_label"]): label_map[str(row["selected_operator"])] for _, row in policy_table.iterrows()}
            shuffled_ops = np.asarray(true_ops, dtype=object).copy()
            for stratum in ["low", "mid", "high"]:
                idx = [i for i, op in enumerate(shuffled_ops) if strata.get(str(op)) == stratum]
                if len(idx) > 1:
                    vals = shuffled_ops[idx].copy()
                    rng.shuffle(vals)
                    shuffled_ops[idx] = vals
            for i, (_, row) in enumerate(test.iterrows()):
                state = str(row["state_label"])
                op_by_control = {
                    "balanced": str(shuffled_ops[i]),
                    "within": shuffled_mapping.get(state, fallback),
                    "between": between_mapping.get(state, fallback),
                    "label_perm": label_mapping.get(state, fallback),
                }
                for control_name, op in op_by_control.items():
                    for endpoint in ENDPOINTS:
                        val = reward(row, op, endpoint)
                        if np.isfinite(val):
                            control_rewards[control_name][endpoint][i] += val
                            control_counts[control_name][endpoint][i] += 1.0

        for i, (_, row) in enumerate(test.iterrows()):
            true_op = true_ops[i]
            out = row.to_dict()
            out.update(
                {
                    "fold": fold_index,
                    "true_policy_operator": true_op,
                    "true_policy_source": "state_mapping" if str(row["state_label"]) in mapping else "global_fallback",
                    "oracle_transport_operator": max(
                        OPERATORS,
                        key=lambda op: reward(row, op, "bidirectional_transport")
                        if np.isfinite(reward(row, op, "bidirectional_transport"))
                        else -np.inf,
                    ),
                }
            )
            for endpoint in ENDPOINTS:
                out[f"true_policy_{endpoint}"] = reward(row, true_op, endpoint)
                out[f"balanced_pool_shuffle_{endpoint}"] = (
                    float(control_rewards["balanced"][endpoint][i] / control_counts["balanced"][endpoint][i])
                    if control_counts["balanced"][endpoint][i] > 0
                    else np.nan
                )
                out[f"frequency_matched_random_{endpoint}"] = weighted_reward(row, freq_weights, endpoint)
                out[f"performance_matched_random_{endpoint}"] = stratum_matched_expected_reward(row, true_op, strata, endpoint)
                out[f"within_state_shuffle_{endpoint}"] = (
                    float(control_rewards["within"][endpoint][i] / control_counts["within"][endpoint][i])
                    if control_counts["within"][endpoint][i] > 0
                    else np.nan
                )
                out[f"between_state_permutation_{endpoint}"] = (
                    float(control_rewards["between"][endpoint][i] / control_counts["between"][endpoint][i])
                    if control_counts["between"][endpoint][i] > 0
                    else np.nan
                )
                out[f"operator_label_permutation_{endpoint}"] = (
                    float(control_rewards["label_perm"][endpoint][i] / control_counts["label_perm"][endpoint][i])
                    if control_counts["label_perm"][endpoint][i] > 0
                    else np.nan
                )
                out[f"oracle_{endpoint}"] = max(
                    [reward(row, op, endpoint) for op in OPERATORS if np.isfinite(reward(row, op, endpoint))],
                    default=np.nan,
                )
            rows.append(out)
    return pd.DataFrame(rows), pd.DataFrame(policies)


def summarize(cv: pd.DataFrame, n_perm: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 850)
    controls = [
        "balanced_pool_shuffle",
        "frequency_matched_random",
        "performance_matched_random",
        "within_state_shuffle",
        "between_state_permutation",
        "operator_label_permutation",
        "oracle",
    ]
    rows = []
    for endpoint in ENDPOINTS:
        true_values = pd.to_numeric(cv[f"true_policy_{endpoint}"], errors="coerce").to_numpy(dtype=float)
        for control in controls:
            values = pd.to_numeric(cv[f"{control}_{endpoint}"], errors="coerce").to_numpy(dtype=float)
            effect, p = signflip_p(true_values - values, rng, n_perm)
            rows.append(
                {
                    "endpoint": endpoint,
                    "comparison": f"true_transport_C_policy_vs_{control}",
                    "mean_true_policy": float(np.nanmean(true_values)),
                    "mean_comparator": float(np.nanmean(values)),
                    "effect": effect,
                    "p_greater": p,
                    "n_events": int(np.isfinite(true_values - values).sum()),
                    "state_mapping_rate": float(np.nanmean(cv["true_policy_source"].eq("state_mapping"))),
                    "oracle_hit_rate": float(np.nanmean(cv["true_policy_operator"].eq(cv["oracle_transport_operator"]))),
                }
            )
    return pd.DataFrame(rows)


def classify(summary: pd.DataFrame) -> str:
    primary = summary[summary["endpoint"].eq("bidirectional_transport")].set_index("comparison")
    required = [
        "true_transport_C_policy_vs_balanced_pool_shuffle",
        "true_transport_C_policy_vs_frequency_matched_random",
        "true_transport_C_policy_vs_performance_matched_random",
        "true_transport_C_policy_vs_within_state_shuffle",
        "true_transport_C_policy_vs_between_state_permutation",
        "true_transport_C_policy_vs_operator_label_permutation",
    ]
    ok = True
    for name in required:
        if name not in primary.index:
            ok = False
            continue
        row = primary.loc[name]
        ok = ok and bool(row["effect"] > 0 and row["p_greater"] <= 0.05)
    oracle_ok = True
    if "true_transport_C_policy_vs_oracle" in primary.index:
        oracle_ok = bool(primary.loc["true_transport_C_policy_vs_oracle", "effect"] < 0)
    if ok and oracle_ok:
        return "B6G success: true C-state policy improves bidirectional perspectival transport over balanced controls while remaining below oracle."
    if any(
        name in primary.index and primary.loc[name, "effect"] > 0 and primary.loc[name, "p_greater"] <= 0.05
        for name in required
    ):
        return "Partial B6G signal: true C-state policy beats at least one transport control but not the full set."
    return "B6G not supported by this private perspectival transport audit."


def write_report(path: Path, summary: pd.DataFrame, policy_use: pd.DataFrame, policy_summary: pd.DataFrame, classification: str, args: argparse.Namespace) -> None:
    lines = [
        "# Private B6G Perspectival Transport Audit",
        "",
        "Status: local/private screen only. No publication, commit, or push was performed.",
        "",
        "Primary hypothesis: C is not a future self-improving state. C is the mediating condition through which A can be transported into B-perspective and B can be transported into A-perspective.",
        "",
        "Primary endpoint:",
        "",
        "`bidirectional_transport = min(A_to_C_to_B, B_to_C_to_A)` after z-scored operator readout construction.",
        "",
        "Secondary endpoints:",
        "",
        "- A_to_C_to_B",
        "- B_to_C_to_A",
        "- transport_balance",
        "- transport_asymmetry",
        "",
        "## Classification",
        "",
        classification,
        "",
        "## Comparison Summary",
        "",
        summary.to_csv(index=False).strip(),
        "",
        "## Held-Out Policy Use",
        "",
        policy_use.to_csv(index=False).strip(),
        "",
        "## Learned Transport Policy Summary",
        "",
        policy_summary.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- state_variant: {args.state_variant}",
        f"- n_folds: {args.n_folds}",
        f"- min_state_events: {args.min_state_events}",
        f"- n_control_draws: {args.n_control_draws}",
        f"- window: {args.window}",
        f"- n_perm: {args.n_perm}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    table = build_base_table(args)
    cv, policies = cross_validated_transport(table, args)
    summary = summarize(cv, args.n_perm, args.seed)
    classification = classify(summary)
    cv["oracle_match"] = cv["true_policy_operator"].eq(cv["oracle_transport_operator"]).astype(float)
    policy_use = cv.groupby(["true_policy_operator", "true_policy_source"], as_index=False).agg(
        n_events=("true_policy_operator", "size"),
        mean_bidirectional_transport=("true_policy_bidirectional_transport", "mean"),
        mean_A_to_B=("true_policy_A_to_C_to_B", "mean"),
        mean_B_to_A=("true_policy_B_to_C_to_A", "mean"),
        oracle_hit_rate=("oracle_match", "mean"),
    )
    policy_summary = policies.groupby("selected_operator", as_index=False).agg(
        n_state_fold_mappings=("state_label", "size"),
        mean_selected_train_reward=("selected_train_reward", "mean"),
        mean_global_best_train_reward=("global_best_train_reward", "mean"),
    ) if not policies.empty else pd.DataFrame()

    table.to_csv(outdir / "private_B6G_state_transport_table.csv", index=False)
    cv.to_csv(outdir / "private_B6G_heldout_transport_rewards.csv", index=False)
    policies.to_csv(outdir / "private_B6G_learned_transport_policies.csv", index=False)
    summary.to_csv(outdir / "private_B6G_comparison_summary.csv", index=False)
    policy_use.to_csv(outdir / "private_B6G_policy_use_summary.csv", index=False)
    policy_summary.to_csv(outdir / "private_B6G_learned_policy_summary.csv", index=False)
    write_report(outdir / "private_B6G_perspectival_transport_summary.md", summary, policy_use, policy_summary, classification, args)

    print("\nPrivate B6G perspectival transport outputs")
    print(outdir)
    print("\nClassification")
    print(classification)
    print("\nPrimary bidirectional transport summary")
    print(summary[summary["endpoint"].eq("bidirectional_transport")].to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6g_perspectival_transport")
    parser.add_argument("--state-variant", default="side_tfc")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=60610)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
