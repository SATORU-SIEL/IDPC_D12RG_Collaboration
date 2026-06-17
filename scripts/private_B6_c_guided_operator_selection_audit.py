#!/usr/bin/env python3
"""Private B6 C-guided operator selection audit.

B6B question:
    Does C_t select the next interpretation operator better than a fixed,
    random, or shuffled-C selection rule?

This keeps C fixed as the original B5.5 phase-bearing lag+5 event carrier and
tests whether current C-state can choose the next operator/readout.
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
B55_SCRIPT = SCRIPTS / "test_Stage_B5_5_triadic_constraint_audit.py"

OPERATORS = [
    "O1_lag0_AB",
    "O2_lag5_AB",
    "O3_A_C_boundary",
    "O4_B_C_boundary",
    "O5_full_TFC",
    "O6_phase_only",
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


def local_corr(b55, sub: pd.DataFrame, pos: int, window: int, lag: int) -> float:
    start = pos + lag
    end = min(len(sub), start + window)
    if start < 0 or start >= len(sub):
        return np.nan
    kappa = pd.to_numeric(sub["kappa"], errors="coerce").to_numpy(dtype=float)
    mq = pd.to_numeric(sub["mq"], errors="coerce").to_numpy(dtype=float)
    return b55.corr_abs(kappa[start:end], mq[start:end])


def value_at(sub: pd.DataFrame, col: str, pos: int, lag: int) -> float:
    idx = pos + lag
    if idx < 0 or idx >= len(sub):
        return np.nan
    return float(pd.to_numeric(sub[col], errors="coerce").iloc[idx])


def add_label_quantiles(annotated: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for _, sub in annotated.sort_values(["label", "idx_in_session"]).groupby("label", sort=False):
        sub = sub.copy()
        for col in ["A_B", "A_C", "B_C", "TFC_min", "TFC_mean"]:
            v = pd.to_numeric(sub[col], errors="coerce")
            sub[f"{col}_q60"] = v.ge(v.quantile(0.60))
            sub[f"{col}_q75"] = v.ge(v.quantile(0.75))
        dphi_abs = pd.to_numeric(sub["dphi_loop"], errors="coerce").abs()
        sub["abs_dphi_q75"] = dphi_abs.ge(dphi_abs.quantile(0.75))
        phi_abs = pd.to_numeric(sub["phi_loop"], errors="coerce").abs()
        h_abs = pd.to_numeric(sub["h_loop"], errors="coerce").abs()
        sub["C_memory_scalar"] = phi_abs + h_abs
        sub["C_memory_q75"] = sub["C_memory_scalar"].ge(sub["C_memory_scalar"].quantile(0.75))
        parts.append(sub)
    return pd.concat(parts, ignore_index=True)


def choose_operator(row: pd.Series) -> tuple[str, str]:
    """C-state rule fixed before outcome inspection."""
    if bool(row.get("TFC_min_q75", False)):
        return "O5_full_TFC", "full triadic projection is already active"
    ac = float(row.get("A_C", np.nan))
    bc = float(row.get("B_C", np.nan))
    if bool(row.get("A_C_q60", False)) and (not np.isfinite(bc) or ac >= bc):
        return "O3_A_C_boundary", "A-side boundary projection dominates current C-state"
    if bool(row.get("B_C_q60", False)) and (not np.isfinite(ac) or bc > ac):
        return "O4_B_C_boundary", "B-side boundary projection dominates current C-state"
    if bool(row.get("abs_dphi_q75", False)) or bool(row.get("C_memory_q75", False)):
        return "O6_phase_only", "phase or closed-loop memory is high"
    if bool(row.get("A_B_q60", False)):
        return "O2_lag5_AB", "current AB is active; read short-lag future AB"
    return "O1_lag0_AB", "default immediate AB readout"


def build_event_operator_table(b55, annotated: pd.DataFrame, b55_events: pd.DataFrame, window: int) -> pd.DataFrame:
    ann = add_label_quantiles(annotated)
    base = b55_events[b55_events["event_class"].eq("b55_phase_event_only_lag5")][
        ["label", "task_idx", "phase", "strength"]
    ].copy()
    base = base.rename(columns={"task_idx": "idx_in_session"})
    rows = []
    for label, sub in ann.sort_values(["label", "idx_in_session"]).groupby("label", sort=False):
        sub = sub.reset_index(drop=True)
        by_idx = {float(v): i for i, v in enumerate(sub["idx_in_session"].astype(float).tolist())}
        ev_sub = base[base["label"].astype(str).eq(str(label))]
        for _, ev in ev_sub.iterrows():
            idx = float(ev["idx_in_session"])
            if idx not in by_idx:
                continue
            pos = by_idx[idx]
            state = sub.iloc[pos]
            selected, reason = choose_operator(state)
            row = {
                "label": str(label),
                "idx_in_session": idx,
                "phase": float(ev["phase"]),
                "strength": float(abs(ev["strength"])),
                "selected_operator": selected,
                "selection_reason": reason,
                "A_B": float(state.get("A_B", np.nan)),
                "A_C": float(state.get("A_C", np.nan)),
                "B_C": float(state.get("B_C", np.nan)),
                "TFC_min": float(state.get("TFC_min", np.nan)),
                "TFC_mean": float(state.get("TFC_mean", np.nan)),
                "abs_dphi": float(abs(state.get("dphi_loop", np.nan))) if pd.notna(state.get("dphi_loop", np.nan)) else np.nan,
                "C_memory_scalar": float(state.get("C_memory_scalar", np.nan)),
                "O1_lag0_AB_raw": local_corr(b55, sub, pos, window, 0),
                "O2_lag5_AB_raw": local_corr(b55, sub, pos, window, 5),
                "O3_A_C_boundary_raw": value_at(sub, "A_C", pos, 5),
                "O4_B_C_boundary_raw": value_at(sub, "B_C", pos, 5),
                "O5_full_TFC_raw": value_at(sub, "TFC_min", pos, 5),
                "O6_phase_only_raw": abs(value_at(sub, "dphi_loop", pos, 5)),
            }
            rows.append(row)
    table = pd.DataFrame(rows)
    for op in OPERATORS:
        table[f"{op}_z"] = zscore(table[f"{op}_raw"].to_numpy(dtype=float))
    z_cols = [f"{op}_z" for op in OPERATORS]
    finite_any = table[z_cols].notna().any(axis=1)
    oracle = table[z_cols].fillna(-np.inf).idxmax(axis=1).str.replace("_z", "", regex=False)
    table["oracle_operator"] = np.where(finite_any, oracle, np.nan)
    table["oracle_reward_z"] = table[z_cols].max(axis=1, skipna=True)
    table["selected_reward_z"] = [
        row[f"{row['selected_operator']}_z"] if pd.notna(row["selected_operator"]) else np.nan for _, row in table.iterrows()
    ]
    table["selected_matches_oracle"] = table["selected_operator"].eq(table["oracle_operator"])
    return table


def add_control_rewards(table: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 610)
    out = table.copy()
    selected = out["selected_operator"].to_numpy(copy=True)
    shuffled = selected.copy()
    rng.shuffle(shuffled)
    random_ops = rng.choice(np.asarray(OPERATORS, dtype=object), size=len(out), replace=True)
    out["shuffled_selected_operator"] = shuffled
    out["random_operator"] = random_ops
    out["shuffled_selected_reward_z"] = [row[f"{row['shuffled_selected_operator']}_z"] for _, row in out.iterrows()]
    out["random_reward_z"] = [row[f"{row['random_operator']}_z"] for _, row in out.iterrows()]
    for op in OPERATORS:
        out[f"fixed_{op}_reward_z"] = out[f"{op}_z"]
    return out


def summarize(table: pd.DataFrame, n_perm: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed + 620)
    fixed_means = {op: float(np.nanmean(table[f"fixed_{op}_reward_z"])) for op in OPERATORS}
    best_fixed = max(fixed_means, key=fixed_means.get)
    best_fixed_values = table[f"fixed_{best_fixed}_reward_z"].to_numpy(dtype=float)
    selected = table["selected_reward_z"].to_numpy(dtype=float)
    random_values = table["random_reward_z"].to_numpy(dtype=float)
    shuffled_values = table["shuffled_selected_reward_z"].to_numpy(dtype=float)
    oracle = table["oracle_reward_z"].to_numpy(dtype=float)

    comparisons = []
    for name, values in [
        (f"best_fixed_{best_fixed}", best_fixed_values),
        ("random_operator", random_values),
        ("shuffled_C_selected_operator", shuffled_values),
        ("oracle_upper_bound", oracle),
    ]:
        effect, p = signflip_p(selected - values, rng, n_perm)
        comparisons.append(
            {
                "comparison": f"C_selected_vs_{name}",
                "mean_C_selected_reward_z": float(np.nanmean(selected)),
                "mean_comparator_reward_z": float(np.nanmean(values)),
                "effect": effect,
                "p_greater": p,
                "n_events": int(np.isfinite(selected - values).sum()),
            }
        )

    operator_rows = []
    for op in OPERATORS:
        op_rows = table[table["selected_operator"].eq(op)]
        operator_rows.append(
            {
                "operator": op,
                "n_selected": int(len(op_rows)),
                "mean_selected_reward_z_when_selected": float(np.nanmean(op_rows["selected_reward_z"])) if len(op_rows) else np.nan,
                "fixed_mean_reward_z": fixed_means[op],
                "oracle_selection_count": int(table["oracle_operator"].eq(op).sum()),
            }
        )
    operator_summary = pd.DataFrame(operator_rows)
    comparison_summary = pd.DataFrame(comparisons)
    comparison_summary["hit_rate_selected_equals_oracle"] = float(np.nanmean(table["selected_matches_oracle"].astype(float)))
    comparison_summary["best_fixed_operator"] = best_fixed
    return comparison_summary, operator_summary


def classify(comparison: pd.DataFrame) -> str:
    by = comparison.set_index("comparison")
    needed = [
        "C_selected_vs_best_fixed_" + str(comparison["best_fixed_operator"].iloc[0]),
        "C_selected_vs_random_operator",
        "C_selected_vs_shuffled_C_selected_operator",
    ]
    ok = True
    for name in needed:
        if name not in by.index:
            ok = False
            continue
        row = by.loc[name]
        ok = ok and bool(row["effect"] > 0 and row["p_greater"] <= 0.05)
    if ok:
        return "B6B success: C-selected next operator beats best fixed, random, and shuffled-C selection."
    random_ok = "C_selected_vs_random_operator" in by.index and by.loc["C_selected_vs_random_operator", "effect"] > 0 and by.loc["C_selected_vs_random_operator", "p_greater"] <= 0.05
    shuffled_ok = "C_selected_vs_shuffled_C_selected_operator" in by.index and by.loc["C_selected_vs_shuffled_C_selected_operator", "effect"] > 0 and by.loc["C_selected_vs_shuffled_C_selected_operator", "p_greater"] <= 0.05
    if random_ok and shuffled_ok:
        return "Partial B6B signal: C-selected beats random and shuffled-C but not best fixed."
    return "B6B not supported by this private operator-selection rule."


def write_report(path: Path, comparison: pd.DataFrame, operator_summary: pd.DataFrame, inventory: pd.DataFrame, classification: str, args: argparse.Namespace) -> None:
    lines = [
        "# Private B6 C-Guided Operator Selection Audit",
        "",
        "Status: local/private screen only. No publication, commit, or push was performed.",
        "",
        "Question: Can C_t select the next interpretation operator better than fixed, random, or shuffled-C selection?",
        "",
        "C is fixed as the original B5.5 phase-bearing lag+5 event carrier. This audit does not redefine C.",
        "",
        "Operators:",
        "",
        "- O1_lag0_AB: immediate A-B readout.",
        "- O2_lag5_AB: short-lag future A-B readout.",
        "- O3_A_C_boundary: future A-side boundary readout.",
        "- O4_B_C_boundary: future B-side boundary readout.",
        "- O5_full_TFC: future full triadic projection readout.",
        "- O6_phase_only: future phase-only readout.",
        "",
        "The reward for each operator is z-scored across events before selection comparisons.",
        "",
        "## Classification",
        "",
        classification,
        "",
        "## Comparison Summary",
        "",
        comparison.to_csv(index=False).strip(),
        "",
        "## Operator Summary",
        "",
        operator_summary.to_csv(index=False).strip(),
        "",
        "## Selection Inventory",
        "",
        inventory.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
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
    b55 = load_module("stage_b5_5_for_b6_operator_selection", B55_SCRIPT)
    annotated = pd.read_csv(args.annotated)
    b55_events = pd.read_csv(args.events)
    table = build_event_operator_table(b55, annotated, b55_events, args.window)
    table = add_control_rewards(table, args.seed)
    comparison, operator_summary = summarize(table, args.n_perm, args.seed)
    classification = classify(comparison)
    inventory = table.groupby(["selected_operator", "selection_reason"], as_index=False).agg(
        n_events=("selected_operator", "size"),
        mean_selected_reward_z=("selected_reward_z", "mean"),
        oracle_match_rate=("selected_matches_oracle", "mean"),
    )
    table.to_csv(outdir / "private_B6_operator_event_rewards.csv", index=False)
    comparison.to_csv(outdir / "private_B6_operator_comparison_summary.csv", index=False)
    operator_summary.to_csv(outdir / "private_B6_operator_summary.csv", index=False)
    inventory.to_csv(outdir / "private_B6_operator_selection_inventory.csv", index=False)
    write_report(outdir / "private_B6_operator_selection_summary.md", comparison, operator_summary, inventory, classification, args)

    print("\nPrivate B6 C-guided operator selection outputs")
    print(outdir)
    print("\nClassification")
    print(classification)
    print("\nComparison summary")
    print(comparison.to_string(index=False))
    print("\nOperator summary")
    print(operator_summary.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6_c_guided_operator_selection")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=60010)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
