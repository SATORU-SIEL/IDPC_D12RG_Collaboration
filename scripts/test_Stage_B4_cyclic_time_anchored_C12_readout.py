#!/usr/bin/env python3
"""Stage B4 cyclic-time anchored C12 readout audit.

This exploratory audit tests whether IDPC events become more organized when
read through a predefined cyclic 12-phase temporal basis than through
alternative temporal bases and phase-anchor controls.
"""

from __future__ import annotations

import argparse
import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd


B3_SCRIPT = Path(__file__).with_name("test_Stage_B3_endogenous_event_carrier_readout.py")
BASES = (8, 10, 12, 16, 24)
PRIMARY_BASIS = 12
LIFT_BASIS = 24
PRIMARY_ANCHOR = "session_normalized_event_position"


def load_b3_module():
    spec = importlib.util.spec_from_file_location("stage_b3", B3_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import Stage B3 script: {B3_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def circular_resultant(phases: np.ndarray, harmonic: int = 1) -> float:
    if len(phases) == 0:
        return np.nan
    return float(abs(np.mean(np.exp(1j * harmonic * phases))))


def basis_alignment(phases: np.ndarray, basis: int) -> float:
    if len(phases) == 0:
        return np.nan
    # Harmonic locking reads whether phases organize into a basis-folded grid.
    return circular_resultant(phases, harmonic=basis)


def phase_entropy_specificity(phases: np.ndarray, basis: int) -> float:
    if len(phases) == 0:
        return np.nan
    bins = np.floor(np.mod(phases, 2.0 * np.pi) / (2.0 * np.pi) * basis).astype(int)
    counts = np.bincount(bins, minlength=basis).astype(float)
    p = counts[counts > 0] / max(1.0, counts.sum())
    entropy = -float(np.sum(p * np.log(p))) / math.log(basis) if len(p) else 0.0
    return float(np.clip(1.0 - entropy, 0.0, 1.0))


def canonical_label(value: object) -> str:
    text = str(value)
    if "_co_recon" in text:
        return text.split("_co_recon", 1)[0]
    return text


def source_ranges(input_root: Path, b3) -> pd.DataFrame:
    rows = []
    primary = b3.load_event_table(input_root)
    for label, sub in primary.groupby("label"):
        rows.append(
            {
                "source_file": b3.EVENT_FILE,
                "label": canonical_label(label),
                "min_task": float(sub["task_idx"].min()),
                "max_task": float(sub["task_idx"].max()),
            }
        )
    phi = pd.read_csv(input_root / b3.PHI_FILE)
    phi["label"] = phi["label"].map(canonical_label)
    for label, sub in phi.groupby("label"):
        rows.append(
            {
                "source_file": b3.PHI_FILE,
                "label": canonical_label(label),
                "min_task": float(sub["idx_in_session"].min()),
                "max_task": float(sub["idx_in_session"].max()),
            }
        )
    eps72 = pd.read_csv(input_root / b3.EPS72_FILE)
    eps72["label"] = eps72["label"].map(canonical_label)
    eps72["_idx"] = eps72.groupby("label").cumcount()
    for label, sub in eps72.groupby("label"):
        rows.append(
            {
                "source_file": b3.EPS72_FILE,
                "label": canonical_label(label),
                "min_task": float(sub["_idx"].min()),
                "max_task": float(sub["_idx"].max()),
            }
        )
    ricci = pd.read_csv(input_root / b3.RICCI_PHASE_SYNC_FILE)
    ricci["label"] = ricci["label"].map(canonical_label)
    for _, row in ricci.iterrows():
        rows.append(
            {
                "source_file": b3.RICCI_PHASE_SYNC_FILE,
                "label": canonical_label(row["label"]),
                "min_task": 0.0,
                "max_task": max(float(row["n_points"]) - 1.0, 1.0),
            }
        )
    return pd.DataFrame(rows)


def add_anchor_phase(events: pd.DataFrame, ranges: pd.DataFrame) -> pd.DataFrame:
    out = events.copy()
    merged = out.merge(ranges, on=["source_file", "label"], how="left")
    missing = merged["min_task"].isna() | merged["max_task"].isna()
    if missing.any():
        missing_rows = merged.loc[missing, ["source_file", "label"]].drop_duplicates()
        raise ValueError(f"missing source ranges for events: {missing_rows.to_dict('records')}")
    denom = np.maximum(merged["max_task"].to_numpy(float) - merged["min_task"].to_numpy(float), 1.0)
    frac = (merged["task_idx"].to_numpy(float) - merged["min_task"].to_numpy(float)) / denom
    merged["anchor_fraction"] = np.mod(frac, 1.0)
    merged["anchor_phase_rad"] = 2.0 * np.pi * merged["anchor_fraction"]
    merged["anchor_name"] = PRIMARY_ANCHOR
    return merged


def rotate_phases(phases: np.ndarray, offset: float) -> np.ndarray:
    return np.mod(phases + offset, 2.0 * np.pi)


def shifted_phases(phases: np.ndarray, shift_bins: int, basis: int) -> np.ndarray:
    return rotate_phases(phases, 2.0 * np.pi * shift_bins / basis)


def score_phases(phases: np.ndarray, basis: int) -> dict[str, float]:
    alignment = basis_alignment(phases, basis)
    specificity = phase_entropy_specificity(phases, basis)
    return {
        "temporal_phase_alignment": alignment,
        "temporal_phase_specificity": specificity,
        "readout_score": float(np.nanmean([alignment, specificity])),
    }


def empirical_controls(
    phases: np.ndarray,
    basis: int,
    rng: np.random.Generator,
    n_rotations: int,
    n_random: int,
) -> dict[str, float]:
    if len(phases) == 0:
        return {
            "rotation_control_mean": np.nan,
            "scramble_control_mean": np.nan,
            "time_shift_control_mean": np.nan,
            "p_vs_rotation": np.nan,
            "p_vs_scramble": np.nan,
            "p_vs_time_shift": np.nan,
        }
    observed = score_phases(phases, basis)["readout_score"]
    rotations = []
    for k in range(1, n_rotations + 1):
        rotations.append(score_phases(rotate_phases(phases, 2.0 * np.pi * k / (n_rotations + 1)), basis)["readout_score"])
    scrambles = []
    for _ in range(n_random):
        scrambles.append(score_phases(rng.uniform(0.0, 2.0 * np.pi, size=len(phases)), basis)["readout_score"])
    shifts = []
    for k in range(1, max(2, basis)):
        shifts.append(score_phases(shifted_phases(phases, k, basis), basis)["readout_score"])
    return {
        "rotation_control_mean": float(np.mean(rotations)),
        "scramble_control_mean": float(np.mean(scrambles)),
        "time_shift_control_mean": float(np.mean(shifts)),
        "effect_vs_rotation": float(observed - np.mean(rotations)),
        "effect_vs_scramble": float(observed - np.mean(scrambles)),
        "effect_vs_time_shift": float(observed - np.mean(shifts)),
        "p_vs_rotation": p_greater(observed, rotations),
        "p_vs_scramble": p_greater(observed, scrambles),
        "p_vs_time_shift": p_greater(observed, shifts),
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


def run_audit(
    input_root: Path,
    output_dir: Path,
    n_rotations: int,
    n_random: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    b3 = load_b3_module()
    rng = np.random.default_rng(seed)
    hashes = b3.input_hash_manifest(input_root)
    events = add_anchor_phase(b3.load_b3_event_rows(input_root), source_ranges(input_root, b3))
    rows = []
    for event_class, sub in events.groupby("event_class"):
        phases = sub["anchor_phase_rad"].to_numpy(float)
        for basis in BASES:
            row = {
                "anchor_name": PRIMARY_ANCHOR,
                "event_class": event_class,
                "basis": basis,
                "basis_role": "primary_C12" if basis == PRIMARY_BASIS else ("lift_D24_Phi24" if basis == LIFT_BASIS else "comparison"),
                "n_events": len(phases),
            }
            row.update(score_phases(phases, basis))
            row.update(empirical_controls(phases, basis, rng, n_rotations, n_random))
            rows.append(row)
    result = pd.DataFrame(rows)
    result["combined_control_p"] = result[["p_vs_rotation", "p_vs_scramble", "p_vs_time_shift"]].max(axis=1)
    result["combined_control_q"] = bh_fdr(result["combined_control_p"].astype(float).tolist())
    basis_scores = result.pivot(index="event_class", columns="basis", values="readout_score")
    c12_contrasts = []
    for event_class, values in basis_scores.iterrows():
        c12 = float(values.get(PRIMARY_BASIS, np.nan))
        alternatives = [float(values.get(b, np.nan)) for b in BASES if b != PRIMARY_BASIS]
        alternatives = [x for x in alternatives if np.isfinite(x)]
        c24 = float(values.get(LIFT_BASIS, np.nan))
        c12_contrasts.append(
            {
                "event_class": event_class,
                "C12_readout_score": c12,
                "best_alternative_score": max(alternatives) if alternatives else np.nan,
                "C12_vs_best_alternative": c12 - max(alternatives) if alternatives else np.nan,
                "D24_Phi24_lift_score": c24,
                "D24_minus_C12": c24 - c12 if np.isfinite(c24) and np.isfinite(c12) else np.nan,
            }
        )
    contrast = pd.DataFrame(c12_contrasts)
    result = result.merge(contrast, on="event_class", how="left")
    result["exploratory_candidate"] = (
        result["basis"].eq(PRIMARY_BASIS)
        & (result["C12_vs_best_alternative"] > 0)
        & (result["effect_vs_scramble"] > 0)
        & (result["effect_vs_time_shift"] > 0)
        & (result["D24_Phi24_lift_score"] >= result["C12_readout_score"] * 0.75)
    )
    result["interpretation"] = result.apply(interpret_row, axis=1)
    output_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_dir / "Stage_B4_cyclic_time_anchored_C12_readout_results.csv", index=False)
    contrast.to_csv(output_dir / "Stage_B4_cyclic_time_anchored_C12_readout_basis_contrasts.csv", index=False)
    hashes.to_csv(output_dir / "Stage_B4_cyclic_time_anchored_C12_readout_input_hashes.csv", index=False)
    write_manifest(output_dir / "Stage_B4_cyclic_time_anchored_C12_readout_manifest.md", input_root, n_rotations, n_random, seed, hashes)
    write_summary(output_dir / "Stage_B4_cyclic_time_anchored_C12_readout_summary.md", result, contrast)
    return result, contrast


def interpret_row(row: pd.Series) -> str:
    if bool(row.get("exploratory_candidate", False)):
        return "exploratory_C12_cyclic_time_candidate"
    if row["basis"] == PRIMARY_BASIS:
        return "C12_not_exploratory_candidate_under_B4_pattern"
    if row["basis"] == LIFT_BASIS:
        return "D24_Phi24_lift_reference"
    return "comparison_basis"


def write_manifest(path: Path, input_root: Path, n_rotations: int, n_random: int, seed: int, hashes: pd.DataFrame) -> None:
    lines = [
        "# Stage B4 Cyclic-Time Anchored C12 Readout Audit Manifest",
        "",
        "Stage B4 is exploratory. It tests C12 as a cyclic-time anchored readout basis, not as an autonomous spatial graph.",
        "",
        f"- input root: `{input_root}`",
        f"- primary anchor: `{PRIMARY_ANCHOR}`",
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


def write_summary(path: Path, result: pd.DataFrame, contrast: pd.DataFrame) -> None:
    c12 = result[result["basis"].eq(PRIMARY_BASIS)].copy()
    candidates = c12[c12["exploratory_candidate"]].copy()
    lines = [
        "# Stage B4 Cyclic-Time Anchored C12 Readout Audit Summary",
        "",
        "## Purpose",
        "",
        "Stage B4 tests the exploratory intuition that C12 is not a spatial graph that closes by itself, but a 12-phase cyclic-time readout basis.",
        "",
        "## Boundary",
        "",
        "This does not rescue B2/B3/B3.1/B3.2. Earlier negative / inconclusive results remain unchanged.",
        "",
        "## Primary Anchor",
        "",
        f"- {PRIMARY_ANCHOR}",
        "",
        "Absolute calendar / orbital timestamps were not available in the current input bundle, so this first B4 run tests session-normalized cyclic-time anchoring rather than literal annual/orbital anchoring.",
        "",
        "## Overall Result",
        "",
        f"- event classes tested: {c12['event_class'].nunique()}",
        f"- bases tested: {', '.join('C' + str(b) for b in BASES)}",
        f"- exploratory C12 candidates: {len(candidates)}",
        "",
        "## C12 Basis Rows",
        "",
    ]
    cols = [
        "event_class",
        "n_events",
        "readout_score",
        "effect_vs_rotation",
        "effect_vs_scramble",
        "effect_vs_time_shift",
        "combined_control_p",
        "combined_control_q",
        "C12_vs_best_alternative",
        "D24_Phi24_lift_score",
        "exploratory_candidate",
        "interpretation",
    ]
    lines.append(c12[cols].sort_values("readout_score", ascending=False).to_csv(index=False).strip())
    lines += [
        "",
        "## Basis Contrast Table",
        "",
        contrast.sort_values("C12_vs_best_alternative", ascending=False).to_csv(index=False).strip(),
        "",
        "## Interpretation",
        "",
        "A B4 exploratory candidate requires C12 to outperform the other tested temporal bases, preserve positive contrasts against phase-anchor controls, and show a D24 / Phi24 lift in the same direction. This is an exploratory pattern, not a final confirmation.",
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
