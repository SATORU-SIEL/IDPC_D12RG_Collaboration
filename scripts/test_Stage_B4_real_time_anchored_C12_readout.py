#!/usr/bin/env python3
"""Stage B4 real-time anchored C12 readout audit.

This run uses real UTC timestamps rather than session-normalized proxy phase.
The primary anchor is UTC annual/orbital phase, preserving the original B4
intuition: C12 as a 12-phase cyclic-time readout basis.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd


B3_SCRIPT = Path(__file__).with_name("test_Stage_B3_endogenous_event_carrier_readout.py")
BASES = (8, 10, 12, 16, 24)
PRIMARY_BASIS = 12
LIFT_BASIS = 24
PRIMARY_ANCHOR = "utc_annual_orbital_phase"
SECONDARY_ANCHOR = "utc_daily_phase"
OUTPUT_PREFIX = "Stage_B4_cyclic_time_anchored_C12_readout"


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


def load_quantum_time_table(input_root: Path) -> pd.DataFrame:
    rows = []
    for path in sorted(input_root.glob("P*_quantum_timeseries.csv")):
        label = path.name.split("_", 1)[0]
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            rows.append(
                {
                    "label": label,
                    "task_idx": int(row["task_idx"]),
                    "event_utc": pd.to_datetime(row["mid_utc"], utc=True, format="mixed"),
                    "time_source": path.name,
                }
            )
    return pd.DataFrame(rows)


def load_eeg_time_table(input_root: Path) -> pd.DataFrame:
    rows = []
    for path in sorted(input_root.glob("P*_eeg_timeseries.csv")):
        label = path.name.split("_", 1)[0]
        df = pd.read_csv(path)
        start = pd.to_datetime(df["bin_start_utc"], utc=True, format="mixed")
        end = pd.to_datetime(df["bin_end_utc"], utc=True, format="mixed")
        mid = start + (end - start) / 2
        for idx, timestamp in enumerate(mid):
            rows.append(
                {
                    "label": label,
                    "idx_in_session": idx,
                    "event_utc": timestamp,
                    "time_source": path.name,
                }
            )
    return pd.DataFrame(rows)


def nearest_by_fraction(index_value: float, source_count: int, target_count: int) -> int:
    if source_count <= 1:
        return 0
    frac = index_value / (source_count - 1)
    return int(np.clip(round(frac * (target_count - 1)), 0, target_count - 1))


def add_real_time_to_events(input_root: Path, b3) -> tuple[pd.DataFrame, pd.DataFrame]:
    events = b3.load_b3_event_rows(input_root).copy()
    quantum = load_quantum_time_table(input_root)
    eeg = load_eeg_time_table(input_root)
    phi = pd.read_csv(input_root / b3.PHI_FILE)
    phi["label"] = phi["label"].map(canonical_label)
    phi_counts = phi.groupby("label")["idx_in_session"].max().add(1).to_dict()
    eps72 = pd.read_csv(input_root / b3.EPS72_FILE)
    eps72["label"] = eps72["label"].map(canonical_label)
    eps72_counts = eps72.groupby("label").size().to_dict()
    rows = []
    for _, event in events.iterrows():
        label = canonical_label(event["label"])
        source = str(event["source_file"])
        task = float(event["task_idx"])
        timestamp = pd.NaT
        time_source = ""
        mapping_rule = ""
        if source == b3.PHI_FILE:
            label_eeg = eeg[eeg["label"].eq(label)].sort_values("idx_in_session")
            if not label_eeg.empty:
                mapped_idx = nearest_by_fraction(task, int(phi_counts.get(label, len(label_eeg))), len(label_eeg))
                match = label_eeg.iloc[mapped_idx]
                timestamp = match["event_utc"]
                time_source = match["time_source"]
                mapping_rule = "h_zero idx_in_session mapped to nearest EEG bin real UTC using per-label source length"
        elif source == b3.EPS72_FILE:
            label_q = quantum[quantum["label"].eq(label)].sort_values("task_idx")
            if not label_q.empty:
                mapped_idx = nearest_by_fraction(task, int(eps72_counts.get(label, len(label_q))), len(label_q))
                match = label_q.iloc[mapped_idx]
                timestamp = match["event_utc"]
                time_source = match["time_source"]
                mapping_rule = "eps72 row index mapped to nearest quantum task real UTC using per-label source length"
        elif source == b3.RICCI_PHASE_SYNC_FILE:
            label_q = quantum[quantum["label"].eq(label)].sort_values("task_idx")
            if not label_q.empty:
                match = label_q.iloc[len(label_q) // 2]
                timestamp = match["event_utc"]
                time_source = match["time_source"]
                mapping_rule = "Ricci session summary mapped to quantum session midpoint real UTC"
        else:
            label_q = quantum[quantum["label"].eq(label)]
            match = label_q[label_q["task_idx"].eq(int(round(task)))]
            if not match.empty:
                row = match.iloc[0]
                timestamp = row["event_utc"]
                time_source = row["time_source"]
                mapping_rule = "event-level task_idx joined to quantum mid_utc"
        new_row = event.to_dict()
        new_row.update({"event_utc": timestamp, "time_source": time_source, "time_mapping_rule": mapping_rule})
        rows.append(new_row)
    timed = pd.DataFrame(rows)
    timed = timed[pd.to_datetime(timed["event_utc"], utc=True, errors="coerce", format="mixed").notna()].copy()
    timed["event_utc"] = pd.to_datetime(timed["event_utc"], utc=True, format="mixed")
    inventory = (
        timed.groupby(["event_class", "source_file", "time_mapping_rule"], as_index=False)
        .agg(n_events=("event_class", "size"), n_labels=("label", "nunique"), first_utc=("event_utc", "min"), last_utc=("event_utc", "max"))
    )
    return timed, inventory


def annual_phase(timestamp: pd.Timestamp) -> float:
    ts = timestamp.tz_convert("UTC")
    start = pd.Timestamp(year=ts.year, month=1, day=1, tz="UTC")
    end = pd.Timestamp(year=ts.year + 1, month=1, day=1, tz="UTC")
    frac = (ts - start).total_seconds() / (end - start).total_seconds()
    return float(2.0 * np.pi * frac)


def daily_phase(timestamp: pd.Timestamp) -> float:
    ts = timestamp.tz_convert("UTC")
    seconds = ts.hour * 3600 + ts.minute * 60 + ts.second + ts.microsecond / 1_000_000
    return float(2.0 * np.pi * seconds / 86400.0)


def circular_resultant(phases: np.ndarray, harmonic: int = 1) -> float:
    if len(phases) == 0:
        return np.nan
    return float(abs(np.mean(np.exp(1j * harmonic * phases))))


def phase_entropy_specificity(phases: np.ndarray, basis: int) -> float:
    if len(phases) == 0:
        return np.nan
    bins = np.floor(np.mod(phases, 2.0 * np.pi) / (2.0 * np.pi) * basis).astype(int)
    counts = np.bincount(bins, minlength=basis).astype(float)
    p = counts[counts > 0] / max(1.0, counts.sum())
    entropy = -float(np.sum(p * np.log(p))) / math.log(basis) if len(p) else 0.0
    return float(np.clip(1.0 - entropy, 0.0, 1.0))


def score_phases(phases: np.ndarray, basis: int) -> dict[str, float]:
    alignment = circular_resultant(phases, harmonic=basis)
    specificity = phase_entropy_specificity(phases, basis)
    return {
        "temporal_phase_alignment": alignment,
        "temporal_phase_specificity": specificity,
        "readout_score": float(np.nanmean([alignment, specificity])),
    }


def p_greater(observed: float, controls: list[float]) -> float:
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


def empirical_controls(
    phases: np.ndarray,
    basis: int,
    rng: np.random.Generator,
    n_rotations: int,
    n_random: int,
    background_phases: np.ndarray,
    same_label_phase_sets: list[np.ndarray],
) -> dict[str, float]:
    observed = score_phases(phases, basis)["readout_score"]
    rotations = [
        score_phases(np.mod(phases + 2.0 * np.pi * k / (n_rotations + 1), 2.0 * np.pi), basis)["readout_score"]
        for k in range(1, n_rotations + 1)
    ]
    scrambles = [
        score_phases(rng.uniform(0.0, 2.0 * np.pi, size=len(phases)), basis)["readout_score"]
        for _ in range(n_random)
    ]
    shifts = [
        score_phases(np.mod(phases + 2.0 * np.pi * k / max(2, basis), 2.0 * np.pi), basis)["readout_score"]
        for k in range(1, max(2, basis))
    ]
    pool = [
        score_phases(rng.choice(background_phases, size=len(phases), replace=True), basis)["readout_score"]
        for _ in range(n_random)
    ]
    label_preserved = []
    for _ in range(n_random):
        sampled = [rng.choice(values) for values in same_label_phase_sets if len(values) > 0]
        label_preserved.append(score_phases(np.asarray(sampled, dtype=float), basis)["readout_score"])
    return {
        "rotation_control_mean": float(np.mean(rotations)),
        "scramble_control_mean": float(np.mean(scrambles)),
        "time_shift_control_mean": float(np.mean(shifts)),
        "event_pool_control_mean": float(np.mean(pool)),
        "label_preserved_time_control_mean": float(np.mean(label_preserved)),
        "effect_vs_rotation": float(observed - np.mean(rotations)),
        "effect_vs_scramble": float(observed - np.mean(scrambles)),
        "effect_vs_time_shift": float(observed - np.mean(shifts)),
        "effect_vs_event_pool": float(observed - np.mean(pool)),
        "effect_vs_label_preserved_time": float(observed - np.mean(label_preserved)),
        "p_vs_rotation": p_greater(observed, rotations),
        "p_vs_scramble": p_greater(observed, scrambles),
        "p_vs_time_shift": p_greater(observed, shifts),
        "p_vs_event_pool": p_greater(observed, pool),
        "p_vs_label_preserved_time": p_greater(observed, label_preserved),
    }


def input_hash_manifest(input_root: Path, b3) -> pd.DataFrame:
    rels = list(b3.INPUT_FILES)
    rels.extend(str(path.relative_to(input_root)) for path in sorted(input_root.glob("P*_quantum_timeseries.csv")))
    rels.extend(str(path.relative_to(input_root)) for path in sorted(input_root.glob("P*_eeg_timeseries.csv")))
    rows = []
    for rel in rels:
        path = input_root / rel
        rows.append({"relative_path": rel, "absolute_path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return pd.DataFrame(rows)


def run_audit(input_root: Path, output_dir: Path, n_rotations: int, n_random: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    b3 = load_b3_module()
    rng = np.random.default_rng(seed)
    events, inventory = add_real_time_to_events(input_root, b3)
    hashes = input_hash_manifest(input_root, b3)
    events[PRIMARY_ANCHOR] = events["event_utc"].map(annual_phase)
    events[SECONDARY_ANCHOR] = events["event_utc"].map(daily_phase)
    rows = []
    for anchor_name in (PRIMARY_ANCHOR, SECONDARY_ANCHOR):
        background_phases = events[anchor_name].to_numpy(float)
        phase_by_label = {
            label: values[anchor_name].to_numpy(float)
            for label, values in events.groupby("label")
        }
        for event_class, sub in events.groupby("event_class"):
            phases = sub[anchor_name].to_numpy(float)
            same_label_phase_sets = [phase_by_label.get(label, np.asarray([], dtype=float)) for label in sub["label"]]
            for basis in BASES:
                row = {
                    "anchor_name": anchor_name,
                    "event_class": event_class,
                    "basis": basis,
                    "basis_role": "primary_C12" if basis == PRIMARY_BASIS else ("lift_D24_Phi24" if basis == LIFT_BASIS else "comparison"),
                    "n_events": len(phases),
                    "first_utc": sub["event_utc"].min(),
                    "last_utc": sub["event_utc"].max(),
                }
                row.update(score_phases(phases, basis))
                row.update(
                    empirical_controls(
                        phases,
                        basis,
                        rng,
                        n_rotations,
                        n_random,
                        background_phases,
                        same_label_phase_sets,
                    )
                )
                rows.append(row)
    result = pd.DataFrame(rows)
    result["combined_control_p"] = result[["p_vs_scramble", "p_vs_event_pool", "p_vs_label_preserved_time"]].max(axis=1)
    result["combined_control_q"] = bh_fdr(result["combined_control_p"].astype(float).tolist())
    contrasts = []
    for anchor_name in (PRIMARY_ANCHOR, SECONDARY_ANCHOR):
        sub = result[result["anchor_name"].eq(anchor_name)]
        basis_scores = sub.pivot(index="event_class", columns="basis", values="readout_score")
        for event_class, values in basis_scores.iterrows():
            c12 = float(values.get(PRIMARY_BASIS, np.nan))
            alternative_pairs = [(b, float(values.get(b, np.nan))) for b in BASES if b != PRIMARY_BASIS]
            alternative_pairs = [(b, x) for b, x in alternative_pairs if np.isfinite(x)]
            c24 = float(values.get(LIFT_BASIS, np.nan))
            best_basis, best_score = max(alternative_pairs, key=lambda item: item[1]) if alternative_pairs else (np.nan, np.nan)
            contrasts.append(
                {
                    "anchor_name": anchor_name,
                    "event_class": event_class,
                    "C12_readout_score": c12,
                    "best_alternative_basis": best_basis,
                    "best_alternative_score": best_score,
                    "C12_vs_best_alternative": c12 - best_score if np.isfinite(best_score) else np.nan,
                    "D24_Phi24_lift_score": c24,
                    "D24_minus_C12": c24 - c12 if np.isfinite(c24) and np.isfinite(c12) else np.nan,
                }
            )
    contrast = pd.DataFrame(contrasts)
    result = result.merge(contrast, on=["anchor_name", "event_class"], how="left")
    result["exploratory_candidate"] = (
        result["anchor_name"].eq(PRIMARY_ANCHOR)
        & result["basis"].eq(PRIMARY_BASIS)
        & (result["C12_vs_best_alternative"] > 0)
        & (result["effect_vs_scramble"] > 0)
        & (result["effect_vs_event_pool"] > 0)
        & (result["effect_vs_label_preserved_time"] > 0)
        & (result["D24_Phi24_lift_score"] >= result["C12_readout_score"] * 0.75)
    )
    result["interpretation"] = result.apply(interpret_row, axis=1)
    output_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_dir / f"{OUTPUT_PREFIX}_results.csv", index=False)
    contrast.to_csv(output_dir / f"{OUTPUT_PREFIX}_basis_contrasts.csv", index=False)
    inventory.to_csv(output_dir / f"{OUTPUT_PREFIX}_time_mapping_inventory.csv", index=False)
    hashes.to_csv(output_dir / f"{OUTPUT_PREFIX}_input_hashes.csv", index=False)
    write_manifest(output_dir / f"{OUTPUT_PREFIX}_manifest.md", input_root, n_rotations, n_random, seed, hashes)
    write_summary(output_dir / f"{OUTPUT_PREFIX}_summary.md", result, contrast, inventory)
    return result, contrast


def interpret_row(row: pd.Series) -> str:
    if bool(row.get("exploratory_candidate", False)):
        return "exploratory_real_time_C12_candidate"
    if row["basis"] == PRIMARY_BASIS:
        return "C12_not_exploratory_candidate_under_real_time_B4_pattern"
    if row["basis"] == LIFT_BASIS:
        return "D24_Phi24_lift_reference"
    return "comparison_basis"


def write_manifest(path: Path, input_root: Path, n_rotations: int, n_random: int, seed: int, hashes: pd.DataFrame) -> None:
    lines = [
        "# Stage B4 Cyclic-Time Anchored C12 Readout Audit Manifest",
        "",
        "This B4 run uses real UTC timestamps rather than session-normalized proxy phase. It overwrites the earlier proxy outputs under the same Stage B4 filename prefix.",
        "",
        f"- input root: `{input_root}`",
        f"- primary anchor: `{PRIMARY_ANCHOR}`",
        f"- secondary anchor: `{SECONDARY_ANCHOR}`",
        f"- bases: {', '.join('C' + str(b) for b in BASES)}",
        f"- n_rotations: {n_rotations}",
        f"- n_random: {n_random}",
        f"- random seed: {seed}",
        "",
        "## Input Hashes",
        "",
        hashes.to_csv(index=False).strip(),
    ]
    path.write_text("\n".join(lines) + "\n")


def write_summary(path: Path, result: pd.DataFrame, contrast: pd.DataFrame, inventory: pd.DataFrame) -> None:
    primary = result[result["anchor_name"].eq(PRIMARY_ANCHOR) & result["basis"].eq(PRIMARY_BASIS)].copy()
    candidates = primary[primary["exploratory_candidate"]]
    cols = [
        "event_class",
        "n_events",
        "readout_score",
        "effect_vs_rotation",
        "effect_vs_scramble",
        "effect_vs_time_shift",
        "effect_vs_event_pool",
        "effect_vs_label_preserved_time",
        "combined_control_p",
        "combined_control_q",
        "C12_vs_best_alternative",
        "D24_Phi24_lift_score",
        "exploratory_candidate",
        "interpretation",
    ]
    lines = [
        "# Stage B4 Cyclic-Time Anchored C12 Readout Audit Summary",
        "",
        "## Purpose",
        "",
        "This run tests the original B4 intuition using real UTC timestamps: C12 as a 12-phase cyclic-time readout basis rather than a session-normalized proxy.",
        "",
        "## Anchors",
        "",
        f"- primary: {PRIMARY_ANCHOR}",
        f"- secondary: {SECONDARY_ANCHOR}",
        "",
        "## Overall Result",
        "",
        f"- event classes tested: {primary['event_class'].nunique()}",
        f"- bases tested: {', '.join('C' + str(b) for b in BASES)}",
        f"- exploratory real-time C12 candidates: {len(candidates)}",
        "",
        "## Real UTC Coverage",
        "",
        f"- first mapped event UTC: {inventory['first_utc'].min()}",
        f"- last mapped event UTC: {inventory['last_utc'].max()}",
        "- this is a real timestamp audit, not a session-normalized proxy audit",
        "",
        "## Primary C12 Annual/Orbital Phase Rows",
        "",
        primary[cols].sort_values("readout_score", ascending=False).to_csv(index=False).strip(),
        "",
        "## Basis Contrast Table",
        "",
        contrast[contrast["anchor_name"].eq(PRIMARY_ANCHOR)].sort_values("C12_vs_best_alternative", ascending=False).to_csv(index=False).strip(),
        "",
        "## Time Mapping Inventory",
        "",
        inventory.to_csv(index=False).strip(),
        "",
        "## Interpretation",
        "",
        "A real-time B4 exploratory candidate requires C12 to outperform the other tested temporal bases under the UTC annual/orbital phase anchor, preserve positive contrasts against random phase, event-pool, and label-preserved time controls, and show a D24 / Phi24 lift in the same direction. Rotation and within-basis phase-shift controls are reported as diagnostics but are not treated as decisive because this score is largely rotation-invariant.",
    ]
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--n-rotations", type=int, default=24)
    parser.add_argument("--n-random", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20260608)
    args = parser.parse_args()
    run_audit(args.input_root, args.output_dir, args.n_rotations, args.n_random, args.seed)


if __name__ == "__main__":
    main()
