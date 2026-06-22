#!/usr/bin/env python3
"""Stage B7.4b-A held-out validation of frozen R* C12 topology-readout."""

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


def heldout_events_for_rep(data: pd.DataFrame, rep: str, heldout_label: str, q: float) -> pd.DataFrame:
    train = data[~data["label"].astype(str).eq(str(heldout_label))].copy()
    test = data[data["label"].astype(str).eq(str(heldout_label))].copy()
    if train.empty or test.empty:
        return pd.DataFrame()
    cut = pd.to_numeric(train[rep], errors="coerce").quantile(q)
    chosen = test[pd.to_numeric(test[rep], errors="coerce").ge(cut)].copy()
    if chosen.empty:
        # Preserve a held-out schedule for every fold without changing R*: use the top held-out row.
        chosen = test.sort_values(rep, ascending=False).head(1).copy()
    rows = []
    for _, row in chosen.sort_values("idx_in_session").iterrows():
        rows.append({
            "event_class": rep,
            "label": str(row["label"]),
            "heldout_label": str(heldout_label),
            "task_idx": float(row["idx_in_session"]),
            "phase": float(row["phase"]) if pd.notna(row["phase"]) else 0.0,
            "strength": float(abs(row[rep])) if pd.notna(row[rep]) else 1.0,
            "event_rule": f"train-label top {q:.2f} threshold applied to heldout {heldout_label}",
        })
    return pd.DataFrame(rows)


def simulate_values(n_nodes: int, edges: list[tuple[int, int]], schedule: list[dict[str, float]], args: argparse.Namespace, rng: np.random.Generator) -> np.ndarray:
    b3 = b73a.load_module("b3_sim_for_b74b", SCRIPTS / "test_Stage_B3_endogenous_event_carrier_readout.py")
    values = []
    for _ in range(args.n_runs):
        metric = b3.simulate_event_conditioned(n_nodes, edges, schedule, int(rng.integers(0, 2**31 - 1)), steps=args.steps)
        values.append(metric.get("differentiated_recovery", np.nan))
    return np.asarray(values, dtype=float)


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed + 7442)
    features = b73a.add_representation_scores(b73a.load_b72_features(args))
    labels = sorted(features["label"].astype(str).unique())
    all_events = []
    rows = []
    for heldout in labels:
        events = heldout_events_for_rep(features, PRIMARY_R_STAR, heldout, args.event_quantile)
        if events.empty:
            continue
        all_events.append(events)
        for topology in TOPOLOGY_ARMS:
            n_nodes, edges, notes = b73a.topology_edges(topology, rng)
            schedule, meta = b73a.build_event_schedule(events, args.steps, n_nodes)
            shifted = b73a.shifted_schedule(schedule, args.steps, max(7, args.steps // 5))
            random_event = b73a.random_schedule(schedule, args.steps, rng)
            obs_values = simulate_values(n_nodes, edges, schedule, args, rng)
            shifted_values = simulate_values(n_nodes, edges, shifted, args, rng)
            random_values = simulate_values(n_nodes, edges, random_event, args, rng)
            obs = float(np.nanmean(obs_values))
            rows.append({
                "heldout_label": heldout,
                "c_representation": PRIMARY_R_STAR,
                "topology_arm": topology,
                "n_nodes": n_nodes,
                "n_directed_edges": len(edges),
                "n_seed_events": meta["n_events"],
                "mean_seed_strength": meta["mean_strength"],
                "total_impulse_budget": meta["total_impulse_budget"],
                "mean_bounded_differentiated_recovery": obs,
                "sd_bounded_differentiated_recovery": float(np.nanstd(obs_values)),
                "effect_vs_time_shifted": obs - float(np.nanmean(shifted_values)),
                "effect_vs_random_event": obs - float(np.nanmean(random_values)),
                "p_vs_time_shifted_and_random": b73a.p_greater(obs, np.r_[shifted_values, random_values]),
                "topology_notes": notes,
            })

    results = pd.DataFrame(rows)
    events_df = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    summary = summarize(results)
    events_df.to_csv(outdir / "Stage_B7_4b_heldout_events.csv", index=False)
    results.to_csv(outdir / "Stage_B7_4b_heldout_topology_results.csv", index=False)
    summary.to_csv(outdir / "Stage_B7_4b_heldout_summary_table.csv", index=False)
    write_summary(outdir / "Stage_B7_4b_execution_summary.md", summary, results, args)
    print(f"output_dir: {outdir}")
    print("\nHeld-out summary")
    print(summary.to_string(index=False))


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    rows = []
    labels = sorted(results["heldout_label"].astype(str).unique())
    by = results.set_index(["heldout_label", "topology_arm"])["mean_bounded_differentiated_recovery"].to_dict()
    for label in labels:
        c12 = by.get((label, "c12_1_2"), np.nan)
        row = {
            "heldout_label": label,
            "c12_mean": c12,
            "effect_vs_no_topology": c12 - by.get((label, "no_topology_baseline"), np.nan),
            "effect_vs_reversed": c12 - by.get((label, "c12_reversed"), np.nan),
            "effect_vs_side_broken": c12 - by.get((label, "c12_side_broken"), np.nan),
            "effect_vs_shuffled": c12 - by.get((label, "c12_shuffled"), np.nan),
            "effect_vs_c10": c12 - by.get((label, "c10"), np.nan),
            "effect_vs_c11": c12 - by.get((label, "c11"), np.nan),
            "effect_vs_c13": c12 - by.get((label, "c13"), np.nan),
            "effect_vs_c14": c12 - by.get((label, "c14"), np.nan),
        }
        controls = [k for k in row if k.startswith("effect_vs_")]
        row["n_positive_specificity_controls"] = int(sum(row[k] > 0 for k in controls if np.isfinite(row[k])))
        row["min_specificity_margin"] = float(np.nanmin([row[k] for k in controls]))
        rows.append(row)
    out = pd.DataFrame(rows)
    if not out.empty:
        aggregate = {
            "heldout_label": "AGGREGATE_MEAN",
            "c12_mean": out["c12_mean"].mean(),
        }
        for col in [c for c in out.columns if c.startswith("effect_vs_")]:
            aggregate[col] = out[col].mean()
        controls = [k for k in aggregate if k.startswith("effect_vs_")]
        aggregate["n_positive_specificity_controls"] = int(sum(aggregate[k] > 0 for k in controls if np.isfinite(aggregate[k])))
        aggregate["min_specificity_margin"] = float(np.nanmin([aggregate[k] for k in controls]))
        out = pd.concat([out, pd.DataFrame([aggregate])], ignore_index=True)
    return out


def write_summary(path: Path, summary: pd.DataFrame, results: pd.DataFrame, args: argparse.Namespace) -> None:
    aggregate = summary[summary["heldout_label"].eq("AGGREGATE_MEAN")]
    agg_text = aggregate.to_csv(index=False).strip() if not aggregate.empty else ""
    lines = [
        "# Stage B7.4b-A Held-out C12 Validation",
        "",
        "Status: executed after `Stage_B7_4b_preregistration_email_sent.md`.",
        "",
        "Primary frozen R*: `receiver_standpoint_magnitude_c`.",
        "",
        "## Aggregate Summary",
        "",
        agg_text,
        "",
        "## Held-out Fold Summary",
        "",
        summary.to_csv(index=False).strip(),
        "",
        "## Interpretation Guardrail",
        "",
        "- C12 vs no-topology tests out-of-sample topology-readout.",
        "- C12 vs side-broken/shuffled tests side-correspondence specificity.",
        "- C12 vs reversed tests ring-orientation specificity.",
        "- If reversed remains close while side-broken/shuffled degrade, report C12 topology-readout with unresolved ring-orientation specificity.",
        "",
        "## Settings",
        "",
        f"- event_quantile: {args.event_quantile}",
        f"- steps: {args.steps}",
        f"- n_runs: {args.n_runs}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_4b")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--event-quantile", type=float, default=0.75)
    parser.add_argument("--steps", type=int, default=180)
    parser.add_argument("--n-runs", type=int, default=24)
    parser.add_argument("--seed", type=int, default=74420)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
