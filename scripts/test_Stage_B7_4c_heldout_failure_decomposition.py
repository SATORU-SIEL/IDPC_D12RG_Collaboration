#!/usr/bin/env python3
"""Stage B7.4c held-out C12 failure decomposition and robustness repair audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import test_Stage_B7_3a_c12_specificity_h24_collective_necessity_audit as b73a  # noqa: E402


PRIMARY_R_STAR = "receiver_standpoint_magnitude_c"
THRESHOLDS = [0.60, 0.70, 0.75, 0.80, 0.90]
FIXED_TOP_K = [1, 2, 3]
TOPOLOGY_ARMS = [
    "no_topology_baseline",
    "c12_1_2",
    "c12_reversed",
    "c12_side_broken",
    "c12_shuffled",
    "c10",
    "c11",
    "c13",
    "c14",
]


def select_events(data: pd.DataFrame, heldout_label: str, mode: str, value: float | int) -> pd.DataFrame:
    train = data[~data["label"].astype(str).eq(str(heldout_label))].copy()
    test = data[data["label"].astype(str).eq(str(heldout_label))].copy()
    if train.empty or test.empty:
        return pd.DataFrame()
    scores = pd.to_numeric(test[PRIMARY_R_STAR], errors="coerce")
    if mode == "quantile":
        cut = pd.to_numeric(train[PRIMARY_R_STAR], errors="coerce").quantile(float(value))
        chosen = test[scores.ge(cut)].copy()
        rule = f"train threshold q={float(value):.2f}"
    elif mode == "fixed_top_k":
        chosen = test.assign(_score=scores).sort_values("_score", ascending=False).head(int(value)).drop(columns=["_score"])
        rule = f"heldout fixed top k={int(value)}"
    else:
        raise ValueError(mode)
    rows = []
    for _, row in chosen.sort_values("idx_in_session").iterrows():
        rows.append({
            "event_class": PRIMARY_R_STAR,
            "label": str(row["label"]),
            "heldout_label": str(heldout_label),
            "task_idx": float(row["idx_in_session"]),
            "phase": float(row["phase"]) if pd.notna(row["phase"]) else 0.0,
            "strength": float(abs(row[PRIMARY_R_STAR])) if pd.notna(row[PRIMARY_R_STAR]) else 1.0,
            "event_rule": rule,
        })
    return pd.DataFrame(rows)


def phase_coverage(events: pd.DataFrame) -> float:
    if events.empty:
        return 0.0
    phase = np.mod(pd.to_numeric(events["phase"], errors="coerce").dropna().to_numpy(float), 2.0 * np.pi)
    if len(phase) == 0:
        return 0.0
    bins = np.floor(12.0 * phase / (2.0 * np.pi)).astype(int)
    return float(len(set(bins.tolist())) / 12.0)


def viability_row(events: pd.DataFrame, heldout_label: str, mode: str, value: float | int, args: argparse.Namespace) -> dict[str, object]:
    n_events = int(len(events))
    mean_strength = float(np.nanmean(events["strength"])) if n_events else np.nan
    coverage = phase_coverage(events)
    valid = (
        n_events >= args.min_heldout_events
        and np.isfinite(mean_strength)
        and mean_strength >= args.min_mean_strength
        and coverage >= args.min_phase_coverage
    )
    diagnostic = (n_events > 0) and not valid
    return {
        "heldout_label": heldout_label,
        "selection_mode": mode,
        "selection_value": value,
        "n_heldout_events": n_events,
        "mean_heldout_strength": mean_strength,
        "phase_coverage_12bin": coverage,
        "fold_status": "valid" if valid else ("diagnostic_only" if diagnostic else "invalid_empty"),
    }


def simulate_values(n_nodes: int, edges: list[tuple[int, int]], schedule: list[dict[str, float]], args: argparse.Namespace, rng: np.random.Generator) -> np.ndarray:
    b3 = b73a.load_module("b3_sim_for_b74c", SCRIPTS / "test_Stage_B3_endogenous_event_carrier_readout.py")
    values = []
    for _ in range(args.n_runs):
        metric = b3.simulate_event_conditioned(n_nodes, edges, schedule, int(rng.integers(0, 2**31 - 1)), steps=args.steps)
        values.append(metric.get("differentiated_recovery", np.nan))
    return np.asarray(values, dtype=float)


def summarize_contrasts(results: pd.DataFrame, viability: pd.DataFrame) -> pd.DataFrame:
    rows = []
    status = viability.set_index(["heldout_label", "selection_mode", "selection_value"])["fold_status"].to_dict()
    keys = results[["heldout_label", "selection_mode", "selection_value"]].drop_duplicates()
    lookup = results.set_index(["heldout_label", "selection_mode", "selection_value", "topology_arm"])["mean_bounded_differentiated_recovery"].to_dict()
    for item in keys.itertuples(index=False):
        key = (item.heldout_label, item.selection_mode, item.selection_value)
        c12 = lookup.get((*key, "c12_1_2"), np.nan)
        row = {
            "heldout_label": item.heldout_label,
            "selection_mode": item.selection_mode,
            "selection_value": item.selection_value,
            "fold_status": status.get(key, "unknown"),
            "c12_mean": c12,
            "effect_vs_no_topology": c12 - lookup.get((*key, "no_topology_baseline"), np.nan),
            "effect_vs_reversed": c12 - lookup.get((*key, "c12_reversed"), np.nan),
            "effect_vs_side_broken": c12 - lookup.get((*key, "c12_side_broken"), np.nan),
            "effect_vs_shuffled": c12 - lookup.get((*key, "c12_shuffled"), np.nan),
            "effect_vs_c10": c12 - lookup.get((*key, "c10"), np.nan),
            "effect_vs_c11": c12 - lookup.get((*key, "c11"), np.nan),
            "effect_vs_c13": c12 - lookup.get((*key, "c13"), np.nan),
            "effect_vs_c14": c12 - lookup.get((*key, "c14"), np.nan),
        }
        cols = [c for c in row if c.startswith("effect_vs_")]
        row["n_positive_specificity_controls"] = int(sum(row[c] > 0 for c in cols if np.isfinite(row[c])))
        row["min_specificity_margin"] = float(np.nanmin([row[c] for c in cols])) if any(np.isfinite(row[c]) for c in cols) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def aggregate_by_selection(contrasts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (mode, value), sub_all in contrasts.groupby(["selection_mode", "selection_value"], sort=False):
        for scope, sub in [
            ("all_folds", sub_all),
            ("valid_folds_only", sub_all[sub_all["fold_status"].eq("valid")]),
            ("diagnostic_only_folds", sub_all[sub_all["fold_status"].eq("diagnostic_only")]),
        ]:
            if sub.empty:
                continue
            row = {
                "selection_mode": mode,
                "selection_value": value,
                "aggregate_scope": scope,
                "n_folds": int(len(sub)),
                "n_valid_folds": int(sub["fold_status"].eq("valid").sum()),
                "c12_mean": float(sub["c12_mean"].mean()),
            }
            for col in [c for c in sub.columns if c.startswith("effect_vs_")]:
                row[col] = float(sub[col].mean())
            effect_cols = [c for c in row if c.startswith("effect_vs_")]
            row["n_positive_specificity_controls"] = int(sum(row[c] > 0 for c in effect_cols if np.isfinite(row[c])))
            row["min_specificity_margin"] = float(np.nanmin([row[c] for c in effect_cols])) if effect_cols else np.nan
            rows.append(row)
    return pd.DataFrame(rows)


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed + 7443)
    features = b73a.add_representation_scores(b73a.load_b72_features(args))
    labels = sorted(features["label"].astype(str).unique())
    selections: list[tuple[str, float | int]] = [("quantile", q) for q in THRESHOLDS] + [("fixed_top_k", k) for k in FIXED_TOP_K]
    viability_rows = []
    result_rows = []
    event_rows = []

    for mode, value in selections:
        for heldout in labels:
            events = select_events(features, heldout, mode, value)
            viability = viability_row(events, heldout, mode, value, args)
            viability_rows.append(viability)
            if events.empty:
                continue
            event_rows.append(events.assign(selection_mode=mode, selection_value=value, fold_status=viability["fold_status"]))
            for topology in TOPOLOGY_ARMS:
                n_nodes, edges, notes = b73a.topology_edges(topology, rng)
                schedule, meta = b73a.build_event_schedule(events, args.steps, n_nodes)
                if not schedule:
                    continue
                values = simulate_values(n_nodes, edges, schedule, args, rng)
                result_rows.append({
                    "heldout_label": heldout,
                    "selection_mode": mode,
                    "selection_value": value,
                    "fold_status": viability["fold_status"],
                    "c_representation": PRIMARY_R_STAR,
                    "topology_arm": topology,
                    "n_nodes": n_nodes,
                    "n_directed_edges": len(edges),
                    "n_seed_events": meta["n_events"],
                    "mean_seed_strength": meta["mean_strength"],
                    "mean_bounded_differentiated_recovery": float(np.nanmean(values)),
                    "sd_bounded_differentiated_recovery": float(np.nanstd(values)),
                    "topology_notes": notes,
                })

    viability = pd.DataFrame(viability_rows)
    results = pd.DataFrame(result_rows)
    events = pd.concat(event_rows, ignore_index=True) if event_rows else pd.DataFrame()
    contrasts = summarize_contrasts(results, viability)
    aggregates = aggregate_by_selection(contrasts)

    viability.to_csv(outdir / "Stage_B7_4c_fold_viability.csv", index=False)
    events.to_csv(outdir / "Stage_B7_4c_selected_events.csv", index=False)
    results.to_csv(outdir / "Stage_B7_4c_topology_results.csv", index=False)
    contrasts.to_csv(outdir / "Stage_B7_4c_fold_contrasts.csv", index=False)
    aggregates.to_csv(outdir / "Stage_B7_4c_threshold_sensitivity.csv", index=False)
    write_summary(outdir / "Stage_B7_4c_execution_summary.md", viability, contrasts, aggregates, args)

    print(f"output_dir: {outdir}")
    print("\nThreshold sensitivity")
    print(aggregates.to_string(index=False))


def write_summary(path: Path, viability: pd.DataFrame, contrasts: pd.DataFrame, aggregates: pd.DataFrame, args: argparse.Namespace) -> None:
    valid = aggregates[aggregates["aggregate_scope"].eq("valid_folds_only")].copy()
    all_folds = aggregates[aggregates["aggregate_scope"].eq("all_folds")].copy()
    lines = [
        "# Stage B7.4c Held-out Failure Decomposition and C12 Readout Robustness Repair",
        "",
        "Status: executed after `Stage_B7_4c_preregistration_email_sent.md`.",
        "",
        "Primary frozen R*: `receiver_standpoint_magnitude_c`.",
        "",
        "## Valid Fold Threshold Sensitivity",
        "",
        valid.to_csv(index=False).strip(),
        "",
        "## All Fold Threshold Sensitivity",
        "",
        all_folds.to_csv(index=False).strip(),
        "",
        "## Fold Viability Counts",
        "",
        viability.groupby(["selection_mode", "selection_value", "fold_status"]).size().reset_index(name="n").to_csv(index=False).strip(),
        "",
        "## Decision Guardrail",
        "",
        "- If C12 recovers across viable folds and thresholds, B7.4b-A was mainly a held-out event-selection failure.",
        "- If C12 remains negative across viable folds and thresholds, B7.3a C12 reconnection remains full-data topology-readout only and is not held-out robust.",
        "- Side-correspondence, structured-topology, ring-orientation, and twelvefold specificity must be reported separately.",
        "",
        "## Settings",
        "",
        f"- thresholds: {THRESHOLDS}",
        f"- fixed_top_k: {FIXED_TOP_K}",
        f"- min_heldout_events: {args.min_heldout_events}",
        f"- min_mean_strength: {args.min_mean_strength}",
        f"- min_phase_coverage: {args.min_phase_coverage}",
        f"- steps: {args.steps}",
        f"- n_runs: {args.n_runs}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_4c")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--steps", type=int, default=150)
    parser.add_argument("--n-runs", type=int, default=12)
    parser.add_argument("--seed", type=int, default=74430)
    parser.add_argument("--min-heldout-events", type=int, default=2)
    parser.add_argument("--min-mean-strength", type=float, default=0.05)
    parser.add_argument("--min-phase-coverage", type=float, default=0.08)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
