#!/usr/bin/env python3
"""Private B6C state-conditioned operator selection audit.

Question:
    Does C select different optimal operators in different C-state regimes, and
    does this outperform the best global fixed operator?

The mapping from C-state class to operator is learned only on training labels
and evaluated on held-out labels.
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
B6B_SCRIPT = SCRIPTS / "private_B6_c_guided_operator_selection_audit.py"
B55_SCRIPT = SCRIPTS / "test_Stage_B5_5_triadic_constraint_audit.py"

BASE_OPERATORS = [
    "O1_lag0_AB",
    "O2_lag5_AB",
    "O3_A_C_boundary",
    "O4_B_C_boundary",
    "O5_full_TFC",
    "O6_phase_only",
]
OPERATORS = BASE_OPERATORS + ["O7_suppress_event"]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bin_series(values: pd.Series, labels: list[str]) -> pd.Series:
    v = pd.to_numeric(values, errors="coerce")
    valid = v[np.isfinite(v)]
    if len(valid) < len(labels) + 1 or valid.nunique() < len(labels):
        return pd.Series(["missing" if not np.isfinite(x) else "mid" for x in v], index=v.index)
    qs = np.linspace(0, 1, len(labels) + 1)[1:-1]
    edges = np.unique(np.nanquantile(valid, qs))
    if len(edges) < len(labels) - 1:
        return pd.Series(["missing" if not np.isfinite(x) else "mid" for x in v], index=v.index)
    return pd.cut(v, bins=[-np.inf, *edges, np.inf], labels=labels[: len(edges) + 1]).astype(str).fillna("missing")


def add_state_classes(table: pd.DataFrame) -> pd.DataFrame:
    out = table.copy()
    phase = np.mod(pd.to_numeric(out["phase"], errors="coerce"), 2.0 * np.pi)
    out["phase_quadrant"] = pd.cut(
        phase,
        bins=[0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi],
        labels=["q1", "q2", "q3", "q4"],
        include_lowest=True,
    ).astype(str).fillna("missing")
    out["strength_bin"] = bin_series(out["strength"], ["low", "mid", "high"])
    out["ab_bin"] = bin_series(out["A_B"], ["low", "mid", "high"])
    out["ac_bin"] = bin_series(out["A_C"], ["low", "mid", "high"])
    out["bc_bin"] = bin_series(out["B_C"], ["low", "mid", "high"])
    out["tfc_bin"] = bin_series(out["TFC_min"], ["low", "mid", "high"])
    out["memory_bin"] = bin_series(out["C_memory_scalar"], ["low", "mid", "high"])
    out["phase_activity_bin"] = bin_series(out["abs_dphi"], ["low", "mid", "high"])
    ac = pd.to_numeric(out["A_C"], errors="coerce")
    bc = pd.to_numeric(out["B_C"], errors="coerce")
    out["boundary_side"] = np.where(ac >= bc, "A_side", "B_side")
    out.loc[~np.isfinite(ac) & ~np.isfinite(bc), "boundary_side"] = "missing"
    out["boundary_distance_bin"] = bin_series((ac - bc).abs(), ["near", "mid", "far"])
    out["state_label_full"] = (
        "phase=" + out["phase_quadrant"].astype(str)
        + "|str=" + out["strength_bin"].astype(str)
        + "|ab=" + out["ab_bin"].astype(str)
        + "|ac=" + out["ac_bin"].astype(str)
        + "|bc=" + out["bc_bin"].astype(str)
        + "|tfc=" + out["tfc_bin"].astype(str)
        + "|mem=" + out["memory_bin"].astype(str)
        + "|dphi=" + out["phase_activity_bin"].astype(str)
        + "|side=" + out["boundary_side"].astype(str)
        + "|dist=" + out["boundary_distance_bin"].astype(str)
    )
    out["state_label"] = (
        "side=" + out["boundary_side"].astype(str)
        + "|tfc=" + out["tfc_bin"].astype(str)
        + "|dphi=" + out["phase_activity_bin"].astype(str)
        + "|str=" + out["strength_bin"].astype(str)
    )
    return out


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


def reward(row: pd.Series, operator: str) -> float:
    return float(row.get(f"{operator}_z", np.nan))


def learn_mapping(train: pd.DataFrame, state_col: str, min_state_events: int, rng: np.random.Generator, shuffle_states: bool = False) -> tuple[dict[str, str], str, pd.DataFrame]:
    local = train.copy()
    if shuffle_states:
        shuffled = local[state_col].to_numpy(copy=True)
        rng.shuffle(shuffled)
        local[state_col] = shuffled

    fixed_means = {op: float(np.nanmean(local[f"{op}_z"])) for op in OPERATORS}
    global_best = max(fixed_means, key=fixed_means.get)
    rows = []
    mapping: dict[str, str] = {}
    for state, sub in local.groupby(state_col, sort=False):
        if len(sub) < min_state_events:
            continue
        means = {op: float(np.nanmean(sub[f"{op}_z"])) for op in OPERATORS}
        best = max(means, key=means.get)
        mapping[str(state)] = best
        rows.append(
            {
                "state_label": str(state),
                "n_train_events": int(len(sub)),
                "selected_operator": best,
                "train_mean_reward_z": means[best],
                "global_best_operator": global_best,
                "train_effect_vs_global_best": means[best] - means[global_best],
            }
        )
    return mapping, global_best, pd.DataFrame(rows)


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 630)
    labels = np.asarray(sorted(set(map(str, labels))), dtype=object)
    rng.shuffle(labels)
    return [fold for fold in np.array_split(labels, n_folds) if len(fold)]


def cross_validated_selection(table: pd.DataFrame, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed + 640)
    folds = make_folds(table["label"].astype(str).unique(), args.n_folds, args.seed)
    out_rows = []
    map_rows = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = table["label"].astype(str).isin(set(test_labels))
        train = table[~test_mask].copy()
        test = table[test_mask].copy()
        mapping, global_best, learned = learn_mapping(train, "state_label", args.min_state_events, rng, shuffle_states=False)
        shuffled_mapping, shuffled_global_best, shuffled_learned = learn_mapping(train, "state_label", args.min_state_events, rng, shuffle_states=True)
        if not learned.empty:
            learned["fold"] = fold_index
            learned["mapping_type"] = "state_conditioned"
            map_rows.extend(learned.to_dict("records"))
        if not shuffled_learned.empty:
            shuffled_learned["fold"] = fold_index
            shuffled_learned["mapping_type"] = "shuffled_state_labels"
            map_rows.extend(shuffled_learned.to_dict("records"))

        random_ops = rng.choice(np.asarray(OPERATORS, dtype=object), size=len(test), replace=True)
        for random_op, (_, row) in zip(random_ops, test.iterrows()):
            state = str(row["state_label"])
            selected = mapping.get(state, global_best)
            shuffled_selected = shuffled_mapping.get(state, shuffled_global_best)
            expected_random_reward = float(np.nanmean([reward(row, op) for op in OPERATORS]))
            out = row.to_dict()
            out.update(
                {
                    "fold": fold_index,
                    "cv_selected_operator": selected,
                    "cv_selection_source": "state_mapping" if state in mapping else "global_fallback",
                    "cv_selected_reward_z": reward(row, selected),
                    "cv_best_fixed_operator": global_best,
                    "cv_best_fixed_reward_z": reward(row, global_best),
                    "cv_shuffled_state_operator": shuffled_selected,
                    "cv_shuffled_state_reward_z": reward(row, shuffled_selected),
                    "cv_random_operator": random_op,
                    "cv_random_sampled_reward_z": reward(row, random_op),
                    "cv_random_reward_z": expected_random_reward,
                }
            )
            out_rows.append(out)
    return pd.DataFrame(out_rows), pd.DataFrame(map_rows)


def summarize(cv: pd.DataFrame, n_perm: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 650)
    selected = pd.to_numeric(cv["cv_selected_reward_z"], errors="coerce").to_numpy(dtype=float)
    comparisons = [
        ("best_global_fixed", pd.to_numeric(cv["cv_best_fixed_reward_z"], errors="coerce").to_numpy(dtype=float)),
        ("shuffled_state_labels", pd.to_numeric(cv["cv_shuffled_state_reward_z"], errors="coerce").to_numpy(dtype=float)),
        ("random_operator", pd.to_numeric(cv["cv_random_reward_z"], errors="coerce").to_numpy(dtype=float)),
        ("oracle_upper_bound", pd.to_numeric(cv["oracle_reward_z"], errors="coerce").to_numpy(dtype=float)),
    ]
    rows = []
    for name, values in comparisons:
        effect, p = signflip_p(selected - values, rng, n_perm)
        rows.append(
            {
                "comparison": f"state_conditioned_C_selected_vs_{name}",
                "mean_state_conditioned_reward_z": float(np.nanmean(selected)),
                "mean_comparator_reward_z": float(np.nanmean(values)),
                "effect": effect,
                "p_greater": p,
                "n_events": int(np.isfinite(selected - values).sum()),
                "state_mapping_rate": float(np.nanmean(cv["cv_selection_source"].eq("state_mapping"))),
                "oracle_hit_rate": float(np.nanmean(cv["cv_selected_operator"].eq(cv["oracle_operator"]))),
            }
        )
    return pd.DataFrame(rows)


def classify(summary: pd.DataFrame) -> str:
    by = summary.set_index("comparison")
    needed = [
        "state_conditioned_C_selected_vs_best_global_fixed",
        "state_conditioned_C_selected_vs_shuffled_state_labels",
        "state_conditioned_C_selected_vs_random_operator",
    ]
    ok = True
    for name in needed:
        if name not in by.index:
            ok = False
            continue
        row = by.loc[name]
        ok = ok and bool(row["effect"] > 0 and row["p_greater"] <= 0.05)
    if ok:
        return "B6C success: held-out state-conditioned C selection beats best global fixed, shuffled state labels, and random operator."
    best_ok = (
        "state_conditioned_C_selected_vs_best_global_fixed" in by.index
        and by.loc["state_conditioned_C_selected_vs_best_global_fixed", "effect"] > 0
        and by.loc["state_conditioned_C_selected_vs_best_global_fixed", "p_greater"] <= 0.05
    )
    shuffled_ok = (
        "state_conditioned_C_selected_vs_shuffled_state_labels" in by.index
        and by.loc["state_conditioned_C_selected_vs_shuffled_state_labels", "effect"] > 0
        and by.loc["state_conditioned_C_selected_vs_shuffled_state_labels", "p_greater"] <= 0.05
    )
    random_ok = (
        "state_conditioned_C_selected_vs_random_operator" in by.index
        and by.loc["state_conditioned_C_selected_vs_random_operator", "effect"] > 0
        and by.loc["state_conditioned_C_selected_vs_random_operator", "p_greater"] <= 0.05
    )
    if best_ok and shuffled_ok and not random_ok:
        return "Partial B6C signal: held-out state-conditioned C selection beats best global fixed and shuffled state labels, but not random operator expectation."
    if shuffled_ok:
        return "Partial B6C signal: held-out state-conditioned C selection beats shuffled state labels but not all required controls."
    return "B6C not supported by this private state-conditioned selector."


def write_report(path: Path, summary: pd.DataFrame, operator_use: pd.DataFrame, mapping_summary: pd.DataFrame, classification: str, args: argparse.Namespace) -> None:
    lines = [
        "# Private B6C State-Conditioned Operator Selection Audit",
        "",
        "Status: local/private screen only. No publication, commit, or push was performed.",
        "",
        "Question: Does C select different optimal operators in different C-state regimes, and does this outperform the best global fixed operator?",
        "",
        "C remains fixed as the original B5.5 phase-bearing lag+5 event carrier. The C-state classes are observational regimes, not new C definitions.",
        "",
        "Selection is cross-validated by held-out labels. The state-to-operator mapping is learned on training labels only.",
        "",
        "Operators include the six B6B readout operators plus O7_suppress_event, whose reward is fixed at zero.",
        "",
        "## Classification",
        "",
        classification,
        "",
        "## Comparison Summary",
        "",
        summary.to_csv(index=False).strip(),
        "",
        "## Held-Out Operator Use",
        "",
        operator_use.to_csv(index=False).strip(),
        "",
        "## Learned Mapping Summary",
        "",
        mapping_summary.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- n_folds: {args.n_folds}",
        f"- min_state_events: {args.min_state_events}",
        f"- window: {args.window}",
        f"- n_perm: {args.n_perm}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    b6b = load_module("private_b6b_for_b6c", B6B_SCRIPT)
    b55 = load_module("stage_b5_5_for_b6c", B55_SCRIPT)

    annotated = pd.read_csv(args.annotated)
    events = pd.read_csv(args.events)
    table = b6b.build_event_operator_table(b55, annotated, events, args.window)
    table["O7_suppress_event_raw"] = 0.0
    table["O7_suppress_event_z"] = 0.0
    table = add_state_classes(table)
    z_cols = [f"{op}_z" for op in OPERATORS]
    finite_any = table[z_cols].notna().any(axis=1)
    table["oracle_operator"] = np.where(
        finite_any,
        table[z_cols].fillna(-np.inf).idxmax(axis=1).str.replace("_z", "", regex=False),
        np.nan,
    )
    table["oracle_reward_z"] = table[z_cols].max(axis=1, skipna=True)

    cv, mappings = cross_validated_selection(table, args)
    summary = summarize(cv, args.n_perm, args.seed)
    classification = classify(summary)
    cv["cv_oracle_match"] = cv["cv_selected_operator"].eq(cv["oracle_operator"]).astype(float)
    operator_use = cv.groupby(["cv_selected_operator", "cv_selection_source"], as_index=False).agg(
        n_events=("cv_selected_operator", "size"),
        mean_reward_z=("cv_selected_reward_z", "mean"),
        oracle_hit_rate=("cv_oracle_match", "mean"),
    )
    mapping_summary = mappings.groupby(["mapping_type", "selected_operator"], as_index=False).agg(
        n_state_fold_mappings=("state_label", "size"),
        mean_train_reward_z=("train_mean_reward_z", "mean"),
        mean_train_effect_vs_global_best=("train_effect_vs_global_best", "mean"),
    ) if not mappings.empty else pd.DataFrame()

    table.to_csv(outdir / "private_B6C_state_table.csv", index=False)
    cv.to_csv(outdir / "private_B6C_heldout_event_rewards.csv", index=False)
    mappings.to_csv(outdir / "private_B6C_learned_state_operator_mappings.csv", index=False)
    summary.to_csv(outdir / "private_B6C_comparison_summary.csv", index=False)
    operator_use.to_csv(outdir / "private_B6C_operator_use_summary.csv", index=False)
    mapping_summary.to_csv(outdir / "private_B6C_mapping_summary.csv", index=False)
    write_report(outdir / "private_B6C_state_conditioned_summary.md", summary, operator_use, mapping_summary, classification, args)

    print("\nPrivate B6C state-conditioned operator selection outputs")
    print(outdir)
    print("\nClassification")
    print(classification)
    print("\nComparison summary")
    print(summary.to_string(index=False))
    print("\nHeld-out operator use")
    print(operator_use.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6c_state_conditioned_operator_selection")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=60110)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
