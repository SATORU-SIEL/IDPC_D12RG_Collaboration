#!/usr/bin/env python3
"""Stage B5.1 direct Phi/FES-to-C12 bridge audit."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


B3_SCRIPT = Path(__file__).with_name("test_Stage_B3_endogenous_event_carrier_readout.py")
OUTPUT_PREFIX = "Stage_B5_1_phi_fes_to_c12_bridge"

HYBRID_EVENT_FILE = "event_level_with_fes_phase_TRUE_RICCI.csv"
HYBRID_EMBEDDING_SUMMARY = "fes_event_embedding_summary_TRUE_RICCI__HYBRID_PHI.json"
FES_ASSIGNMENT_LOG = "fes_assignment_log_TRUE_RICCI__HYBRID_PHI.csv"
CLUSTER_SUMMARY = "cluster_summary_TRUE_RICCI__HYBRID_PHI.csv"
CHAPTER7_PHI_FILE = "Chapter7/new_phi_dataset.csv"
CHAPTER7_FINAL_CLAIM = "Chapter7/final_claim_table.csv"
CHAPTER7_SESSION_METRICS = "Chapter7/session_wise_metrics_all_models.csv"

INPUT_FILES = [
    HYBRID_EVENT_FILE,
    HYBRID_EMBEDDING_SUMMARY,
    FES_ASSIGNMENT_LOG,
    CLUSTER_SUMMARY,
    CHAPTER7_PHI_FILE,
    CHAPTER7_FINAL_CLAIM,
    CHAPTER7_SESSION_METRICS,
]

PRIMARY_EVENTS = [
    "hybrid_phi_sign_switch",
    "hybrid_fes_phase_transition",
    "hybrid_cluster_transition",
]
SECONDARY_EVENTS = [
    "chapter7_phi_clean_sign_switch",
    "chapter7_h_zero_crossing",
]
CONTRAST_EVENTS = [
    "chapter7_dphi_sign_switch",
    "chapter7_d2phi_curvature_switch",
    "chapter7_deps_sign_switch",
]
EVENT_CLASSES = PRIMARY_EVENTS + SECONDARY_EVENTS + CONTRAST_EVENTS
GATE_BOUNDED = 0.70
GATE_DIFFERENTIATION = 0.30
GATE_LATE_STABILITY = 0.70
FDR_ALPHA = 0.05


def load_b3_module():
    spec = importlib.util.spec_from_file_location("stage_b3", B3_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import Stage B3 script: {B3_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_label(value: object) -> str:
    text = str(value)
    if "_co_recon" in text:
        return text.split("_co_recon", 1)[0]
    return text


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_hash_manifest(input_root: Path) -> pd.DataFrame:
    rows = []
    for rel_path in INPUT_FILES:
        path = input_root / rel_path
        if not path.exists():
            raise FileNotFoundError(f"missing B5.1 input file: {path}")
        rows.append(
            {
                "relative_path": rel_path,
                "absolute_path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return pd.DataFrame(rows)


def sign_switch_mask(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    prev = values.shift(1)
    return (
        values.notna()
        & prev.notna()
        & (np.sign(values) != np.sign(prev))
        & (np.sign(values) != 0)
        & (np.sign(prev) != 0)
    )


def append_event(
    rows: list[dict[str, object]],
    event_class: str,
    source_file: str,
    label: object,
    task_idx: object,
    phase: object,
    strength: object,
    event_role: str,
    event_rule: str,
) -> None:
    rows.append(
        {
            "event_class": event_class,
            "event_role": event_role,
            "source_file": source_file,
            "label": canonical_label(label),
            "task_idx": float(task_idx),
            "phase": float(phase) if pd.notna(phase) else 0.0,
            "strength": float(abs(strength)) if pd.notna(strength) else 1.0,
            "event_rule": event_rule,
        }
    )


def load_b5_1_event_rows(input_root: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    hybrid = pd.read_csv(input_root / HYBRID_EVENT_FILE)
    required_hybrid = {"label", "task_idx", "phi", "dphi", "fes_phase", "cluster"}
    missing_hybrid = sorted(required_hybrid - set(hybrid.columns))
    if missing_hybrid:
        raise ValueError(f"{HYBRID_EVENT_FILE} missing columns: {missing_hybrid}")
    hybrid["label"] = hybrid["label"].map(canonical_label)
    for label, sub in hybrid.sort_values(["label", "task_idx"]).groupby("label"):
        for _, row in sub[sign_switch_mask(sub["phi"])].iterrows():
            append_event(
                rows,
                "hybrid_phi_sign_switch",
                HYBRID_EVENT_FILE,
                label,
                row["task_idx"],
                row["phi"],
                row["dphi"],
                "primary_phi_fes",
                "sign switch of formal hybrid Phi in the FES event-level table",
            )
        fes_change = sub["fes_phase"].astype(str).ne(sub["fes_phase"].astype(str).shift(1))
        fes_change.iloc[0] = False
        for _, row in sub[fes_change].iterrows():
            append_event(
                rows,
                "hybrid_fes_phase_transition",
                HYBRID_EVENT_FILE,
                label,
                row["task_idx"],
                row["phi"],
                1.0,
                "primary_phi_fes",
                "transition of formal FES semantic phase assignment",
            )
        cluster_change = sub["cluster"].ne(sub["cluster"].shift(1))
        cluster_change.iloc[0] = False
        for _, row in sub[cluster_change].iterrows():
            append_event(
                rows,
                "hybrid_cluster_transition",
                HYBRID_EVENT_FILE,
                label,
                row["task_idx"],
                row["phi"],
                1.0,
                "primary_phi_fes",
                "transition of formal FES/hybrid-Phi cluster assignment",
            )

    phi = pd.read_csv(input_root / CHAPTER7_PHI_FILE)
    required_phi = {"label", "idx_in_session", "h", "phi_clean", "dphi", "d2phi", "dh", "deps"}
    missing_phi = sorted(required_phi - set(phi.columns))
    if missing_phi:
        raise ValueError(f"{CHAPTER7_PHI_FILE} missing columns: {missing_phi}")
    phi["label"] = phi["label"].map(canonical_label)
    for label, sub in phi.sort_values(["label", "idx_in_session"]).groupby("label"):
        for column, event_class, strength_col, event_role, rule in [
            ("phi_clean", "chapter7_phi_clean_sign_switch", "dphi", "secondary_phi_reference", "sign switch of Chapter7 phi_clean"),
            ("dphi", "chapter7_dphi_sign_switch", "dphi", "contrast_switch", "sign switch of Chapter7 dphi"),
            ("d2phi", "chapter7_d2phi_curvature_switch", "d2phi", "contrast_switch", "sign switch of Chapter7 d2phi curvature"),
            ("deps", "chapter7_deps_sign_switch", "deps", "contrast_switch", "sign switch of Chapter7 deps"),
        ]:
            for _, row in sub[sign_switch_mask(sub[column])].iterrows():
                append_event(
                    rows,
                    event_class,
                    CHAPTER7_PHI_FILE,
                    label,
                    row["idx_in_session"],
                    row["phi_clean"],
                    row[strength_col],
                    event_role,
                    rule,
                )
        h = pd.to_numeric(sub["h"], errors="coerce")
        h_crossing = (h * h.shift(1) <= 0.0) & h.notna() & h.shift(1).notna()
        for _, row in sub[h_crossing].iterrows():
            append_event(
                rows,
                "chapter7_h_zero_crossing",
                CHAPTER7_PHI_FILE,
                label,
                row["idx_in_session"],
                row["phi_clean"],
                row["dh"],
                "secondary_phi_reference",
                "Chapter7 h=0 availability-boundary crossing",
            )

    events = pd.DataFrame(rows)
    if events.empty:
        raise ValueError("no B5.1 Phi/FES events were extracted")
    return events.sort_values(["event_class", "label", "task_idx"]).reset_index(drop=True)


def p_greater(observed: float, controls: list[float] | np.ndarray) -> float:
    control = np.asarray(controls, dtype=float)
    control = control[np.isfinite(control)]
    if not np.isfinite(observed) or len(control) == 0:
        return np.nan
    return float((1.0 + np.sum(control >= observed)) / (len(control) + 1.0))


def bh_fdr(values: list[float]) -> list[float]:
    p = np.asarray(values, dtype=float)
    q = np.full_like(p, np.nan)
    valid = np.isfinite(p)
    if not valid.any():
        return q.tolist()
    pv = p[valid]
    order = np.argsort(pv)
    ranked = pv[order]
    n = len(ranked)
    ranked_q = ranked * n / np.arange(1, n + 1)
    ranked_q = np.minimum.accumulate(ranked_q[::-1])[::-1]
    out = np.empty_like(ranked_q)
    out[order] = np.clip(ranked_q, 0.0, 1.0)
    q[valid] = out
    return q.tolist()


def simulate_many(b3, n_nodes: int, edges: list[tuple[int, int]], schedule: list[dict[str, float]], n_runs: int, steps: int, rng: np.random.Generator) -> tuple[np.ndarray, dict[str, float]]:
    values = []
    metrics = []
    for _ in range(n_runs):
        metric = b3.simulate_event_conditioned(
            n_nodes,
            edges,
            schedule,
            int(rng.integers(0, 2**31 - 1)),
            steps=steps,
        )
        metrics.append(metric)
        values.append(metric.get("differentiated_recovery", np.nan))
    return np.asarray(values, dtype=float), b3.average_dicts(metrics)


def evaluate_event_class(
    b3,
    events: pd.DataFrame,
    event_class: str,
    steps: int,
    n_runs: int,
    n_null_graphs: int,
    n_null_runs: int,
    rng: np.random.Generator,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    event_rows = events[events["event_class"].eq(event_class)].copy()
    role = str(event_rows["event_role"].iloc[0])
    out_rows: list[dict[str, object]] = []
    null_rows: list[dict[str, object]] = []

    _, c12_nodes, c12_edges, c12_convention, c12_notes = b3.topology_definition("C12(1,2)")
    _, c8_nodes, c8_edges, c8_convention, c8_notes = b3.topology_definition("C8(1)")
    c12_schedule, meta = b3.build_event_schedule(event_rows, event_class, steps, c12_nodes)
    c8_schedule, _ = b3.build_event_schedule(event_rows, event_class, steps, c8_nodes)
    if not c12_schedule:
        return out_rows, null_rows

    shifted = b3.shifted_schedule(c12_schedule, steps, shift=max(7, steps // 5))
    c12_random_values = []
    c12_random_metrics = []
    c12_end_values, c12_end_avg = simulate_many(b3, c12_nodes, c12_edges, c12_schedule, n_runs, steps, rng)
    c12_shift_values, c12_shift_avg = simulate_many(b3, c12_nodes, c12_edges, shifted, n_runs, steps, rng)
    for _ in range(n_runs):
        random_schedule = b3.random_schedule(c12_schedule, steps, rng)
        metric = b3.simulate_event_conditioned(
            c12_nodes,
            c12_edges,
            random_schedule,
            int(rng.integers(0, 2**31 - 1)),
            steps=steps,
        )
        c12_random_metrics.append(metric)
        c12_random_values.append(metric.get("differentiated_recovery", np.nan))
    c12_random_values = np.asarray(c12_random_values, dtype=float)
    c12_random_avg = b3.average_dicts(c12_random_metrics)

    c8_end_values, c8_end_avg = simulate_many(b3, c8_nodes, c8_edges, c8_schedule, n_runs, steps, rng)

    null_values = []
    for null_index in range(n_null_graphs):
        null_edges = b3.degree_matched_random_edges(c12_nodes, c12_edges, rng)
        vals, avg = simulate_many(b3, c12_nodes, null_edges, c12_schedule, n_null_runs, steps, rng)
        null_values.extend(vals[np.isfinite(vals)].tolist())
        null_rows.append(
            {
                "event_class": event_class,
                "event_role": role,
                "null_index": null_index,
                "null_model": "degree-matched directed random graph",
                "n_nodes": c12_nodes,
                "n_directed_edges": len(null_edges),
                "mean_bounded_differentiated_recovery": float(np.nanmean(vals)),
                "sd_bounded_differentiated_recovery": float(np.nanstd(vals)),
                "D12_recovery": avg.get("D12_recovery", np.nan),
                "D24_recovery": avg.get("D24_recovery", np.nan),
            }
        )

    obs = float(np.nanmean(c12_end_values))
    shift_mean = float(np.nanmean(c12_shift_values))
    random_mean = float(np.nanmean(c12_random_values))
    c8_mean = float(np.nanmean(c8_end_values))
    null_mean = float(np.nanmean(null_values)) if null_values else np.nan
    p_vs_controls = p_greater(obs, np.r_[c12_shift_values, c12_random_values])
    p_vs_c8 = p_greater(obs, c8_end_values)
    p_vs_null = p_greater(obs, null_values)

    base = {
        "event_class": event_class,
        "event_role": role,
        "n_seed_events": meta["n_events"],
        "mean_seed_strength": meta["mean_strength"],
        "total_impulse_budget": meta["total_impulse_budget"],
        "primary_endpoint_name": "bounded_differentiated_recovery",
        "topology_class": "standalone Cn(k) directed rings",
        "n_runs": n_runs,
        "steps": steps,
    }
    for condition, topology, n_nodes, edges, convention, notes, values, avg in [
        ("endogenous", "C12(1,2)", c12_nodes, c12_edges, c12_convention, c12_notes, c12_end_values, c12_end_avg),
        ("time_shifted", "C12(1,2)", c12_nodes, c12_edges, c12_convention, c12_notes, c12_shift_values, c12_shift_avg),
        ("random_event", "C12(1,2)", c12_nodes, c12_edges, c12_convention, c12_notes, c12_random_values, c12_random_avg),
        ("c8_same_schedule", "C8(1)", c8_nodes, c8_edges, c8_convention, c8_notes, c8_end_values, c8_end_avg),
    ]:
        row = {
            **base,
            "topology_name": topology,
            "topology_role": "primary" if topology == "C12(1,2)" else "contrast",
            "condition": condition,
            "n_nodes": n_nodes,
            "n_directed_edges": len(edges),
            "edge_convention": convention,
            "topology_notes": notes,
            "mean_bounded_differentiated_recovery": float(np.nanmean(values)),
            "sd_bounded_differentiated_recovery": float(np.nanstd(values)),
            "effect_vs_time_shifted": obs - shift_mean if condition == "endogenous" and topology == "C12(1,2)" else np.nan,
            "effect_vs_random_event": obs - random_mean if condition == "endogenous" and topology == "C12(1,2)" else np.nan,
            "effect_vs_C8": obs - c8_mean if condition == "endogenous" and topology == "C12(1,2)" else np.nan,
            "effect_vs_degree_null_mean": obs - null_mean if condition == "endogenous" and topology == "C12(1,2)" else np.nan,
            "p_vs_time_shifted_and_random": p_vs_controls if condition == "endogenous" and topology == "C12(1,2)" else np.nan,
            "p_vs_C8": p_vs_c8 if condition == "endogenous" and topology == "C12(1,2)" else np.nan,
            "p_vs_degree_null": p_vs_null if condition == "endogenous" and topology == "C12(1,2)" else np.nan,
        }
        row.update(avg)
        out_rows.append(row)
    return out_rows, null_rows


def add_primary_decisions(result: pd.DataFrame) -> pd.DataFrame:
    out = result.copy()
    endogenous = out["condition"].eq("endogenous") & out["topology_name"].eq("C12(1,2)")
    out["primary_q_value"] = np.nan
    out.loc[endogenous, "primary_q_value"] = bh_fdr(out.loc[endogenous, "p_vs_time_shifted_and_random"].astype(float).tolist())

    primary_effects = out[endogenous].set_index("event_class")
    contrast_rows = primary_effects[primary_effects["event_role"].eq("contrast_switch")]
    max_contrast_effect = float(contrast_rows["effect_vs_time_shifted"].max()) if not contrast_rows.empty else np.nan
    out["max_contrast_effect_vs_time_shifted"] = max_contrast_effect
    out["passes_effect_controls"] = (
        (out["effect_vs_time_shifted"] > 0)
        & (out["effect_vs_random_event"] > 0)
        & (out["effect_vs_C8"] > 0)
        & (out["effect_vs_degree_null_mean"] > 0)
    )
    out["passes_stability_gates"] = (
        (out["bounded_non_runaway_score"] >= GATE_BOUNDED)
        & (out["non_collapsed_differentiation_score"] >= GATE_DIFFERENTIATION)
        & (out["late_window_stability"] >= GATE_LATE_STABILITY)
    )
    out["passes_contrast_switch_gate"] = (
        out["event_role"].eq("primary_phi_fes")
        & np.isfinite(max_contrast_effect)
        & (out["effect_vs_time_shifted"] > max_contrast_effect)
    )
    out["positive_candidate"] = (
        endogenous
        & out["event_role"].eq("primary_phi_fes")
        & out["passes_effect_controls"]
        & out["passes_stability_gates"]
        & out["passes_contrast_switch_gate"]
        & (out["primary_q_value"] <= FDR_ALPHA)
        & (out["p_vs_C8"] <= FDR_ALPHA)
        & (out["p_vs_degree_null"] <= FDR_ALPHA)
    )
    out["interpretation"] = out.apply(interpret_row, axis=1)
    return out


def interpret_row(row: pd.Series) -> str:
    if row["condition"] != "endogenous" or row["topology_name"] != "C12(1,2)":
        return "control_or_reference_condition"
    if bool(row.get("positive_candidate", False)):
        return "positive_B5_1_primary_candidate"
    if row["event_role"] == "primary_phi_fes":
        return "primary_phi_fes_negative_or_incomplete_gate"
    if row["event_role"] == "secondary_phi_reference":
        return "secondary_phi_reference_descriptive_only"
    return "contrast_switch_control"


def write_manifest(path: Path, input_root: Path, n_runs: int, n_null_graphs: int, n_null_runs: int, steps: int, seed: int, hashes: pd.DataFrame) -> None:
    lines = [
        "# Stage B5.1 Phi/FES-to-C12 Bridge Audit Manifest",
        "",
        f"- input root: `{input_root}`",
        f"- simulation steps: {steps}",
        f"- runs per topology/condition: {n_runs}",
        f"- degree-matched null graphs per event class: {n_null_graphs}",
        f"- runs per null graph: {n_null_runs}",
        f"- random seed: {seed}",
        "- primary topology: C12(1,2)",
        "- contrast topology: C8(1)",
        "- primary endpoint: bounded_differentiated_recovery",
        "",
        "## Input Hashes",
        "",
        hashes.to_csv(index=False).strip(),
    ]
    path.write_text("\n".join(lines) + "\n")


def write_summary(path: Path, result: pd.DataFrame, inventory: pd.DataFrame, null_df: pd.DataFrame) -> None:
    primary = result[result["condition"].eq("endogenous") & result["topology_name"].eq("C12(1,2)")].copy()
    primary_rows = primary[primary["event_role"].eq("primary_phi_fes")].copy()
    cols = [
        "event_class",
        "event_role",
        "n_seed_events",
        "mean_bounded_differentiated_recovery",
        "effect_vs_time_shifted",
        "effect_vs_random_event",
        "effect_vs_C8",
        "effect_vs_degree_null_mean",
        "p_vs_time_shifted_and_random",
        "primary_q_value",
        "p_vs_C8",
        "p_vs_degree_null",
        "bounded_non_runaway_score",
        "non_collapsed_differentiation_score",
        "late_window_stability",
        "passes_effect_controls",
        "passes_stability_gates",
        "passes_contrast_switch_gate",
        "positive_candidate",
        "interpretation",
    ]
    lines = [
        "# Stage B5.1 Phi/FES-to-C12 Bridge Audit Summary",
        "",
        "## Purpose",
        "",
        "B5.1 tests whether formal IDPC Phi/FES switching events condition bounded differentiated recovery in the external D12RG C12(1,2) readout topology.",
        "",
        "## Overall Result",
        "",
        f"- event classes tested: {primary['event_class'].nunique()}",
        f"- primary Phi/FES event classes: {primary_rows['event_class'].nunique()}",
        f"- positive primary candidates: {int(primary_rows['positive_candidate'].sum())}",
        f"- C12 endogenous rows with q <= 0.05: {int((primary['primary_q_value'] <= FDR_ALPHA).sum())}",
        "",
        "## Primary Phi/FES Rows",
        "",
        primary_rows[cols].sort_values(["positive_candidate", "primary_q_value"], ascending=[False, True]).to_csv(index=False).strip(),
        "",
        "## All Endogenous C12 Rows",
        "",
        primary[cols].sort_values(["event_role", "primary_q_value"]).to_csv(index=False).strip(),
        "",
        "## Event Inventory",
        "",
        inventory.to_csv(index=False).strip(),
        "",
        "## Null Graph Summary",
        "",
        null_df.groupby(["event_class", "event_role"], as_index=False).agg(
            n_null_graphs=("null_index", "nunique"),
            mean_null_recovery=("mean_bounded_differentiated_recovery", "mean"),
            sd_null_recovery=("mean_bounded_differentiated_recovery", "std"),
        ).to_csv(index=False).strip(),
        "",
        "## Interpretation Boundary",
        "",
        "A positive B5.1 result would support only a limited cross-framework predictive-structure claim. It would not prove IDPC, D12RG, C12 as a physical carrier, or a final ontology.",
    ]
    path.write_text("\n".join(lines) + "\n")


def run_audit(input_root: Path, output_dir: Path, n_runs: int, n_null_graphs: int, n_null_runs: int, steps: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    b3 = load_b3_module()
    rng = np.random.default_rng(seed)
    hashes = input_hash_manifest(input_root)
    events = load_b5_1_event_rows(input_root)
    rows: list[dict[str, object]] = []
    null_rows: list[dict[str, object]] = []
    for event_class in EVENT_CLASSES:
        event_result, event_nulls = evaluate_event_class(
            b3,
            events,
            event_class,
            steps,
            n_runs,
            n_null_graphs,
            n_null_runs,
            rng,
        )
        rows.extend(event_result)
        null_rows.extend(event_nulls)
    result = add_primary_decisions(pd.DataFrame(rows))
    null_df = pd.DataFrame(null_rows)
    inventory = (
        events.groupby(["event_class", "event_role", "source_file", "event_rule"], as_index=False)
        .agg(
            n_events=("event_class", "size"),
            n_labels=("label", "nunique"),
            min_task_idx=("task_idx", "min"),
            max_task_idx=("task_idx", "max"),
            mean_strength=("strength", "mean"),
        )
        .sort_values(["event_role", "event_class"])
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_dir / f"{OUTPUT_PREFIX}_results.csv", index=False)
    null_df.to_csv(output_dir / f"{OUTPUT_PREFIX}_null_graphs.csv", index=False)
    inventory.to_csv(output_dir / f"{OUTPUT_PREFIX}_event_inventory.csv", index=False)
    hashes.to_csv(output_dir / f"{OUTPUT_PREFIX}_input_hashes.csv", index=False)
    write_manifest(output_dir / f"{OUTPUT_PREFIX}_manifest.md", input_root, n_runs, n_null_graphs, n_null_runs, steps, seed, hashes)
    write_summary(output_dir / f"{OUTPUT_PREFIX}_summary.md", result, inventory, null_df)
    return result, null_df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--n-runs", type=int, default=500)
    parser.add_argument("--n-null-graphs", type=int, default=40)
    parser.add_argument("--n-null-runs", type=int, default=40)
    parser.add_argument("--steps", type=int, default=240)
    parser.add_argument("--seed", type=int, default=20260608)
    args = parser.parse_args()
    run_audit(args.input_root, args.output_dir, args.n_runs, args.n_null_graphs, args.n_null_runs, args.steps, args.seed)


if __name__ == "__main__":
    main()
