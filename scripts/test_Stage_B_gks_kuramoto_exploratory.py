#!/usr/bin/env python3
"""Stage B exploratory GKS N=24 / sin-cos / lift / Kuramoto tests.

Stage B is explicitly exploratory. It does not rescue Stage A negative results
and does not claim D12RG confirmation. It asks whether broader carrier-
realization motifs suggested by Luke and Thomas leave descriptive signatures in
IDPC-derived structural outputs.

Exploratory families:
    B1. GKS N=24 sin/cos dual readout on structural phase columns.
    B2. 8/12/24 lift-overlap concentration.
    B3. Kuramoto/Ricci synchronization summaries already produced by IDPC.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from scipy.stats import chisquare
except Exception:  # pragma: no cover
    chisquare = None


PHASE_FILE_NAMES = (
    "event_level_with_fes_phase_TRUE_RICCI.csv",
    "ricci_eps72_restoring_test.csv",
    "ricci_phase_sync_summary.csv",
)
KURAMOTO_FILE_NAMES = (
    "kuramoto_test_per_session_latest_riccisync.csv",
    "oscillator_test_per_session_latest_riccisync.csv",
)
PHASE_COLUMNS = (
    "phase",
    "phase_z",
    "phi",
    "dphi",
    "distance",
    "distance_z",
    "r_local",
    "r_local_z",
    "eps72_deg",
    "deps72_deg",
    "circ_mean_deg",
    "mean_abs_dpsi_deg",
)


def bh_fdr(p_values: list[float]) -> list[float]:
    p = np.asarray(p_values, dtype=float)
    out = np.full_like(p, np.nan)
    valid = np.isfinite(p)
    if not valid.any():
        return out.tolist()
    pv = p[valid]
    order = np.argsort(pv)
    ranked = pv[order]
    n = len(ranked)
    q_ranked = ranked * n / np.arange(1, n + 1)
    q_ranked = np.minimum.accumulate(q_ranked[::-1])[::-1]
    q = np.empty_like(q_ranked)
    q[order] = np.clip(q_ranked, 0, 1)
    out[valid] = q
    return out.tolist()


def display_path(path: Path, input_root: Path) -> str:
    try:
        return str(path.relative_to(input_root))
    except ValueError:
        return path.name


def condition_from_path(path: Path) -> str:
    text = str(path).lower()
    if "idpc_reproduction/idpc_reproduction/" in text:
        return "observed"
    if any(token in text for token in ["surrogate", "random", "derangement", "shift", "reverse"]):
        return "control"
    return "other"


def candidate_files(input_root: Path, names: tuple[str, ...]) -> list[Path]:
    return sorted(path for path in input_root.rglob("*.csv") if path.name in names)


def values_to_phase(values: pd.Series, column: str) -> np.ndarray:
    arr = values.replace([np.inf, -np.inf], np.nan).dropna().to_numpy(dtype=float)
    if len(arr) == 0:
        return arr
    lower = column.lower()
    if lower.endswith("_deg") or "deg" in lower:
        return np.mod(np.deg2rad(arr), 2.0 * np.pi)
    if lower in {"phase", "circ_mean_rad", "mean_abs_dpsi_rad"}:
        return np.mod(arr, 2.0 * np.pi)
    ranks = pd.Series(arr).rank(method="first", pct=True).to_numpy()
    return 2.0 * np.pi * np.clip(ranks, 0.0, 1.0 - 1e-12)


def phase_counts(phases: np.ndarray, period: int) -> np.ndarray:
    bins = np.floor(np.mod(phases, 2.0 * np.pi) / (2.0 * np.pi) * period).astype(int)
    bins = np.clip(bins, 0, period - 1)
    return np.bincount(bins, minlength=period)


def resultant_from_counts(counts: np.ndarray, harmonic: int = 1) -> tuple[float, float, float]:
    total = int(np.sum(counts))
    if total == 0:
        return np.nan, np.nan, np.nan
    period = len(counts)
    angles = 2.0 * np.pi * harmonic * np.arange(period) / period
    z = np.sum(counts * np.exp(1j * angles)) / total
    return float(z.real), float(z.imag), float(abs(z))


def chi_square_p(counts: np.ndarray) -> float:
    total = int(np.sum(counts))
    if total == 0 or chisquare is None:
        return np.nan
    expected = np.repeat(total / len(counts), len(counts))
    return float(chisquare(counts, expected).pvalue)


def entropy_deficit(counts: np.ndarray) -> float:
    total = int(np.sum(counts))
    if total == 0:
        return np.nan
    p = counts / total
    p = p[p > 0]
    return float(np.log(len(counts)) + np.sum(p * np.log(p)))


def lift_overlap_score(phases: np.ndarray) -> float:
    return (
        entropy_deficit(phase_counts(phases, 8))
        * entropy_deficit(phase_counts(phases, 12))
        * entropy_deficit(phase_counts(phases, 24))
    )


def lift_null_p(phases: np.ndarray, observed: float, n_perm: int, rng: np.random.Generator) -> float:
    n = len(phases)
    if n < 8 or not np.isfinite(observed):
        return np.nan
    null = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        sample = rng.uniform(0, 2.0 * np.pi, size=n)
        null[i] = lift_overlap_score(sample)
    return float((1.0 + np.sum(null >= observed)) / (n_perm + 1.0))


def collect_phase_rows(input_root: Path, n_perm: int, rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame]:
    phase_rows = []
    lift_rows = []
    for path in candidate_files(input_root, PHASE_FILE_NAMES):
        label = display_path(path, input_root)
        condition = condition_from_path(path)
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        for col in PHASE_COLUMNS:
            if col not in df.columns:
                continue
            phases = values_to_phase(df[col], col)
            if len(phases) < 8:
                continue
            counts24 = phase_counts(phases, 24)
            cos1, sin1, r1 = resultant_from_counts(counts24, harmonic=1)
            cos2, sin2, r2 = resultant_from_counts(counts24, harmonic=2)
            cos3, sin3, r3 = resultant_from_counts(counts24, harmonic=3)
            phase_rows.append({
                "source_file": label,
                "condition": condition,
                "column": col,
                "n_values": len(phases),
                "period": 24,
                "preferred_bin": int(np.argmax(counts24)),
                "chi_square_p": chi_square_p(counts24),
                "Vcos_h1_D24": cos1,
                "Vsin_h1_D24": sin1,
                "resultant_h1_D24": r1,
                "Vcos_h2_D12": cos2,
                "Vsin_h2_D12": sin2,
                "resultant_h2_D12": r2,
                "Vcos_h3_D8": cos3,
                "Vsin_h3_D8": sin3,
                "resultant_h3_D8": r3,
                "sin_cos_balance_h1": 1.0 - abs(abs(cos1) - abs(sin1)),
            })
            score = lift_overlap_score(phases)
            lift_rows.append({
                "source_file": label,
                "condition": condition,
                "column": col,
                "n_values": len(phases),
                "lift_overlap_score_8_12_24": score,
                "entropy_deficit_D8": entropy_deficit(phase_counts(phases, 8)),
                "entropy_deficit_D12": entropy_deficit(phase_counts(phases, 12)),
                "entropy_deficit_D24": entropy_deficit(phase_counts(phases, 24)),
                "raw_p_vs_uniform_phase": lift_null_p(phases, score, n_perm, rng),
            })
    phase = pd.DataFrame(phase_rows)
    lift = pd.DataFrame(lift_rows)
    if "chi_square_p" in phase.columns:
        phase["chi_square_fdr_q"] = bh_fdr(phase["chi_square_p"].astype(float).tolist())
    if "raw_p_vs_uniform_phase" in lift.columns:
        lift["fdr_q_vs_uniform_phase"] = bh_fdr(lift["raw_p_vs_uniform_phase"].astype(float).tolist())
    return phase, lift


def collect_kuramoto_rows(input_root: Path) -> pd.DataFrame:
    rows = []
    for path in candidate_files(input_root, KURAMOTO_FILE_NAMES):
        label = display_path(path, input_root)
        condition = condition_from_path(path)
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        row = {
            "source_file": label,
            "condition": condition,
            "n_rows": len(df),
            "numeric_columns": "; ".join(numeric_cols),
        }
        for col in ["kuramoto_r2", "Delta_omega", "K_est", "oscillator_r2", "n"]:
            if col in df.columns:
                values = pd.to_numeric(df[col], errors="coerce")
                row[f"{col}_mean"] = float(values.mean())
                row[f"{col}_median"] = float(values.median())
                row[f"{col}_sd"] = float(values.std(ddof=1))
        rows.append(row)
    return pd.DataFrame(rows)


def write_summary(output_path: Path, phase: pd.DataFrame, lift: pd.DataFrame, kuramoto: pd.DataFrame) -> None:
    phase_hits = phase[phase.get("chi_square_fdr_q", pd.Series(dtype=float)).le(0.05)] if len(phase) else phase
    lift_hits = lift[lift.get("fdr_q_vs_uniform_phase", pd.Series(dtype=float)).le(0.05)] if len(lift) else lift
    observed_phase = phase[phase.get("condition", pd.Series(dtype=str)).eq("observed")] if len(phase) else phase
    observed_lift = lift[lift.get("condition", pd.Series(dtype=str)).eq("observed")] if len(lift) else lift
    observed_phase_hits = observed_phase[observed_phase.get("chi_square_fdr_q", pd.Series(dtype=float)).le(0.05)] if len(observed_phase) else observed_phase
    observed_lift_hits = observed_lift[observed_lift.get("fdr_q_vs_uniform_phase", pd.Series(dtype=float)).le(0.05)] if len(observed_lift) else observed_lift

    lines = [
        "# Stage B Exploratory GKS / Kuramoto Carrier-Realization Summary",
        "",
        "## Purpose",
        "",
        (
            "Stage B is exploratory. It asks whether broader carrier-realization "
            "motifs, including GKS N=24, sin/cos dual readouts, 8/12/24 lift "
            "overlap, and Kuramoto/Ricci synchronization summaries, show "
            "descriptive structure in IDPC-derived outputs."
        ),
        "",
        "## Scope",
        "",
        (
            "These tests do not rescue Stage A negative D12-specific results "
            "and do not confirm D12RG. They are hypothesis-generating only."
        ),
        "",
        "## Results",
        "",
        f"- GKS N=24 phase rows: {len(phase)}",
        f"- GKS N=24 phase rows with FDR q<=0.05: {len(phase_hits)}",
        f"- observed GKS phase rows with FDR q<=0.05: {len(observed_phase_hits)}",
        f"- 8/12/24 lift rows: {len(lift)}",
        f"- 8/12/24 lift rows with FDR q<=0.05: {len(lift_hits)}",
        f"- observed lift rows with FDR q<=0.05: {len(observed_lift_hits)}",
        f"- Kuramoto / oscillator summary rows: {len(kuramoto)}",
        "",
    ]
    if len(observed_phase):
        lines.append("## Strongest Observed GKS Phase Rows")
        lines.append("")
        for _, row in observed_phase.sort_values("chi_square_p").head(8).iterrows():
            lines.append(
                f"- {row['source_file']} / {row['column']}: "
                f"p={row['chi_square_p']:.6g}, q={row['chi_square_fdr_q']:.6g}, "
                f"R_D24={row['resultant_h1_D24']:.6g}, "
                f"R_D12={row['resultant_h2_D12']:.6g}, "
                f"R_D8={row['resultant_h3_D8']:.6g}"
            )
        lines.append("")
    if len(observed_lift):
        lines.append("## Strongest Observed 8/12/24 Lift Rows")
        lines.append("")
        for _, row in observed_lift.sort_values("raw_p_vs_uniform_phase").head(8).iterrows():
            lines.append(
                f"- {row['source_file']} / {row['column']}: "
                f"score={row['lift_overlap_score_8_12_24']:.6g}, "
                f"p={row['raw_p_vs_uniform_phase']:.6g}, "
                f"q={row['fdr_q_vs_uniform_phase']:.6g}"
            )
        lines.append("")
    lines.extend([
        "## Interpretation",
        "",
    ])
    if len(observed_phase_hits) or len(observed_lift_hits):
        lines.append(
            "Some observed Stage B exploratory rows survive FDR. Because Stage B "
            "was explicitly exploratory and uses broader carrier-realization "
            "motifs, these results should be treated as candidates for a new "
            "pre-registered follow-up, not as confirmation."
        )
        lines.append(
            "The strongest rows are phase/restoration quantities that are already "
            "constructed to express phase locking or residual restoration, so the "
            "signal may reflect IDPC's existing phase geometry rather than a "
            "specific GKS/D12RG carrier."
        )
    else:
        lines.append(
            "The observed Stage B exploratory rows do not yield a clear "
            "carrier-realization signal under the current controls."
        )
    lines.append(
        "Kuramoto/Ricci synchronization rows are summarized descriptively; they "
        "should not be interpreted as topology confirmation without a separate "
        "network-level model."
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--n-perm", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260606)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    phase, lift = collect_phase_rows(args.input_root, args.n_perm, rng)
    kuramoto = collect_kuramoto_rows(args.input_root)

    phase_path = args.output_dir / "Stage_B_gks24_phase_dual_results.csv"
    lift_path = args.output_dir / "Stage_B_lift_overlap_8_12_24_results.csv"
    kuramoto_path = args.output_dir / "Stage_B_kuramoto_ricci_summary_results.csv"
    summary_path = args.output_dir / "Stage_B_exploratory_gks_kuramoto_summary.md"

    phase.to_csv(phase_path, index=False)
    lift.to_csv(lift_path, index=False)
    kuramoto.to_csv(kuramoto_path, index=False)
    write_summary(summary_path, phase, lift, kuramoto)

    print(f"wrote {phase_path}")
    print(f"wrote {lift_path}")
    print(f"wrote {kuramoto_path}")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
