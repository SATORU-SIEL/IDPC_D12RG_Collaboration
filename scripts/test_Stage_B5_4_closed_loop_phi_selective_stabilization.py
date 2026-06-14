#!/usr/bin/env python3
"""Render the Stage B5.4 closed-loop phi selective-stabilization summary.

The public B5.4 release is intentionally conservative. The result is reported
as a narrowed closed-loop phi sign-switch finding, not as a broad Phi/FES-family
positive result.

This script reads the published B5.4 CSV files from reports/stage_b5_4 and
rewrites the Markdown summary in the same public-report style as B5.2/B5.3.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PREFIX = "Stage_B5_4_closed_loop_phi_selective_stabilization"


def fmt(value: object, digits: int = 6) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return ""


def write_summary(report_dir: Path) -> Path:
    results_path = report_dir / f"{PREFIX}_results.csv"
    inventory_path = report_dir / f"{PREFIX}_event_inventory.csv"
    summary_path = report_dir / f"{PREFIX}_summary.md"

    results = pd.read_csv(results_path)
    inventory = pd.read_csv(inventory_path)

    primary = results[results["event_class"].eq("closed_loop_phi_sign_switch")].iloc[0]
    replication = results[results["event_class"].eq("eta075_phi_sign_primary")].iloc[0]
    coherence = results[results["public_role"].eq("auxiliary_coherence_probe")].copy()
    warning = results[results["public_role"].eq("warning_control")].copy()
    count = results[results["public_role"].eq("main_negative_control")].copy()

    best_count_recovery = count["mean_bounded_differentiated_recovery"].astype(float).max()
    best_count_p = count["p_vs_time_shifted_and_random"].astype(float).min()
    best_count_degree = count["p_vs_degree_null"].astype(float).min()

    core_cols = [
        "event_class",
        "public_role",
        "n_seed_events",
        "mean_bounded_differentiated_recovery",
        "effect_vs_time_shifted",
        "effect_vs_random_event",
        "effect_vs_C8",
        "effect_vs_degree_null_mean",
        "p_vs_time_shifted_and_random",
        "p_vs_C8",
        "p_vs_degree_null",
        "late_window_stability",
    ]

    lines = [
        "# Stage B5.4 Closed-Loop Phi Selective-Stabilization Audit Summary",
        "",
        "## Purpose",
        "",
        "B5.4 tests whether weak closed-loop phi improves selective C12 stabilization without collapsing negative controls.",
        "",
        "The primary endpoint is narrowed to the closed-loop phi sign-switch. FES phase and cluster transitions are treated as auxiliary coherence probes, not as a required primary family. Full dphi is treated as an event-density warning control, and count-matched dphi is treated as the main negative control.",
        "",
        "## Run Parameters",
        "",
        "- eta: 0.075",
        "- primary topology: C12(1,2)",
        "- contrast topology: C8(1)",
        "- primary endpoint: bounded_differentiated_recovery",
        "- primary fixed run: 240 runs, 80 degree-null graphs, 8 null runs per graph, 160 temporal-profile runs, seed 54054",
        "- count-matched dphi stress run: 180 runs, 60 degree-null graphs, 8 null runs per graph, 120 temporal-profile runs, seed 54055",
        "",
        "## Main Finding",
        "",
        "The broad Phi/FES-family claim is not supported, because the FES phase-transition and cluster-transition rows do not reproduce the closed-loop phi sign-switch effect.",
        "",
        "The narrower closed-loop phi sign-switch claim is supported as a topology-specific stabilization result:",
        "",
        f"- p vs shifted/random: {fmt(primary['p_vs_time_shifted_and_random'])}",
        f"- p vs C8: {fmt(primary['p_vs_C8'])}",
        f"- p vs degree-null: {fmt(primary['p_vs_degree_null'])}",
        f"- effect vs degree-null mean: {fmt(primary['effect_vs_degree_null_mean'])}",
        f"- late-window stability: {fmt(primary['late_window_stability'])}",
        "",
        "The count-matched dphi controls remain negative:",
        "",
        f"- best count-matched recovery: {fmt(best_count_recovery)}",
        f"- best count-matched p vs shifted/random: {fmt(best_count_p)}",
        f"- best count-matched p vs degree-null: {fmt(best_count_degree)}",
        "",
        "## Primary Endpoint",
        "",
        results[results["event_class"].isin(["closed_loop_phi_sign_switch", "eta075_phi_sign_primary"])][core_cols].to_csv(index=False).strip(),
        "",
        "## Auxiliary Coherence Probes",
        "",
        coherence[core_cols].to_csv(index=False).strip(),
        "",
        "## Warning and Negative Controls",
        "",
        pd.concat([warning, count], ignore_index=True)[core_cols].to_csv(index=False).strip(),
        "",
        "## Event Inventory",
        "",
        inventory.to_csv(index=False).strip(),
        "",
        "## Interpretation",
        "",
        "B5.4 should be interpreted as a narrowed positive result for closed-loop phi sign-switch topology-specific stabilization, not as a broad Phi/FES-family positive result.",
        "",
        "The key gain relative to B5.2 is degree-null separation. In B5.2, the hybrid phi sign-switch degree-null p-value was approximately 0.092. In B5.4, the closed-loop phi sign-switch degree-null p-value is approximately 0.0016 in the fixed run and 0.0021 in the count-matched stress run.",
        "",
        "The full dphi warning control can show shifted/random effects, but the count-matched dphi controls remain negative. This supports the interpretation that the full dphi row is an event-density warning rather than a matched-event specificity failure.",
        "",
        "## Output Files",
        "",
        f"- `reports/stage_b5_4/{PREFIX}_summary.md`",
        f"- `reports/stage_b5_4/{PREFIX}_results.csv`",
        f"- `reports/stage_b5_4/{PREFIX}_event_inventory.csv`",
        f"- `scripts/test_Stage_B5_4_closed_loop_phi_selective_stabilization.py`",
        "",
        "## Replication Row",
        "",
        f"The count-matched stress run gives p vs shifted/random = {fmt(replication['p_vs_time_shifted_and_random'])}, p vs C8 = {fmt(replication['p_vs_C8'])}, and p vs degree-null = {fmt(replication['p_vs_degree_null'])} for the same eta=0.075 closed-loop phi sign-switch endpoint.",
    ]
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "reports" / "stage_b5_4",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(write_summary(args.report_dir))


if __name__ == "__main__":
    main()
