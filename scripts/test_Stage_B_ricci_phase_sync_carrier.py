#!/usr/bin/env python3
"""Stage B Ricci oscillation / phase-synchronization carrier test.

This exploratory script connects Luke/Thomas Stage B carrier ideas to the
actual IDPC paper layer: Ricci oscillation, phase synchronization, and eps72
restoring behavior.

It does not claim that Ricci synchronization proves D12RG. It asks whether the
IDPC Ricci phase-synchronization outputs show GKS N=24 / D12 / D8 descriptive
readout structure strongly enough to justify a preregistered follow-up.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from scipy.stats import chisquare, spearmanr
except Exception:  # pragma: no cover
    chisquare = None
    spearmanr = None


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


def candidate_files(input_root: Path, filename: str) -> list[Path]:
    return sorted(path for path in input_root.rglob(filename))


def phase_counts_deg(degrees: np.ndarray, period: int) -> np.ndarray:
    deg = np.mod(degrees, 360.0)
    bins = np.floor(deg / 360.0 * period).astype(int)
    bins = np.clip(bins, 0, period - 1)
    return np.bincount(bins, minlength=period)


def resultant_from_counts(counts: np.ndarray, harmonic: int = 1) -> float:
    total = int(np.sum(counts))
    if total == 0:
        return np.nan
    period = len(counts)
    angles = 2.0 * np.pi * harmonic * np.arange(period) / period
    return float(abs(np.sum(counts * np.exp(1j * angles)) / total))


def chi_square_p(counts: np.ndarray) -> float:
    total = int(np.sum(counts))
    if total == 0 or chisquare is None:
        return np.nan
    expected = np.repeat(total / len(counts), len(counts))
    return float(chisquare(counts, expected).pvalue)


def nearest_grid_distance_deg(degrees: np.ndarray, period: int) -> np.ndarray:
    step = 360.0 / period
    shifted = np.mod(degrees, 360.0)
    residual = np.mod(shifted + step / 2.0, step) - step / 2.0
    return np.abs(residual)


def sync_rows(input_root: Path) -> pd.DataFrame:
    rows = []
    for path in candidate_files(input_root, "ricci_phase_sync_summary.csv"):
        label = display_path(path, input_root)
        condition = condition_from_path(path)
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        required = {"psi_lock_R", "circ_mean_deg", "mean_abs_dpsi_deg"}
        if not required.issubset(df.columns) or len(df) == 0:
            continue
        circ = pd.to_numeric(df["circ_mean_deg"], errors="coerce").dropna().to_numpy()
        abs_dpsi = pd.to_numeric(df["mean_abs_dpsi_deg"], errors="coerce").dropna().to_numpy()
        lock = pd.to_numeric(df["psi_lock_R"], errors="coerce").dropna().to_numpy()
        counts24 = phase_counts_deg(circ, 24)
        counts12 = phase_counts_deg(circ, 12)
        counts8 = phase_counts_deg(circ, 8)
        d24 = nearest_grid_distance_deg(circ, 24)
        d12 = nearest_grid_distance_deg(circ, 12)
        d8 = nearest_grid_distance_deg(circ, 8)
        if spearmanr is not None and len(lock) == len(d12) and len(lock) >= 4:
            rho12, rho12_p = spearmanr(lock, -d12, nan_policy="omit")
            rho24, rho24_p = spearmanr(lock, -d24, nan_policy="omit")
        else:
            rho12 = rho12_p = rho24 = rho24_p = np.nan
        rows.append({
            "source_file": label,
            "condition": condition,
            "n_sessions": len(df),
            "psi_lock_R_mean": float(np.nanmean(lock)),
            "psi_lock_R_median": float(np.nanmedian(lock)),
            "mean_abs_dpsi_deg_mean": float(np.nanmean(abs_dpsi)),
            "mean_abs_dpsi_deg_median": float(np.nanmedian(abs_dpsi)),
            "circ_mean_D24_chi_p": chi_square_p(counts24),
            "circ_mean_D12_chi_p": chi_square_p(counts12),
            "circ_mean_D8_chi_p": chi_square_p(counts8),
            "circ_mean_R_D24": resultant_from_counts(counts24, 1),
            "circ_mean_R_D12": resultant_from_counts(counts12, 1),
            "circ_mean_R_D8": resultant_from_counts(counts8, 1),
            "circ_mean_distance_D24_mean": float(np.nanmean(d24)),
            "circ_mean_distance_D12_mean": float(np.nanmean(d12)),
            "circ_mean_distance_D8_mean": float(np.nanmean(d8)),
            "lock_vs_D12_closeness_spearman_rho": float(rho12),
            "lock_vs_D12_closeness_spearman_p": float(rho12_p),
            "lock_vs_D24_closeness_spearman_rho": float(rho24),
            "lock_vs_D24_closeness_spearman_p": float(rho24_p),
        })
    out = pd.DataFrame(rows)
    for p_col, q_col in [
        ("circ_mean_D24_chi_p", "circ_mean_D24_chi_q"),
        ("circ_mean_D12_chi_p", "circ_mean_D12_chi_q"),
        ("circ_mean_D8_chi_p", "circ_mean_D8_chi_q"),
        ("lock_vs_D12_closeness_spearman_p", "lock_vs_D12_closeness_spearman_q"),
        ("lock_vs_D24_closeness_spearman_p", "lock_vs_D24_closeness_spearman_q"),
    ]:
        if p_col in out.columns:
            out[q_col] = bh_fdr(out[p_col].astype(float).tolist())
    return out


def eps72_rows(input_root: Path) -> pd.DataFrame:
    rows = []
    for path in candidate_files(input_root, "ricci_eps72_restoring_test.csv"):
        label = display_path(path, input_root)
        condition = condition_from_path(path)
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        if not {"eps72_deg", "deps72_deg", "restore"}.issubset(df.columns) or len(df) == 0:
            continue
        eps = pd.to_numeric(df["eps72_deg"], errors="coerce")
        deps = pd.to_numeric(df["deps72_deg"], errors="coerce")
        restore = pd.to_numeric(df["restore"], errors="coerce")
        part = pd.DataFrame({"eps": eps, "deps": deps, "restore": restore}).dropna()
        if len(part) == 0:
            continue
        restore_mask = part["restore"].to_numpy(dtype=float) > 0
        eps_values = part["eps"].to_numpy(dtype=float)
        deps_values = part["deps"].to_numpy(dtype=float)
        for column, values in [("eps72_deg", eps_values), ("deps72_deg", deps_values)]:
            selected = values[restore_mask]
            rejected = values[~restore_mask]
            counts24 = phase_counts_deg(selected, 24)
            rows.append({
                "source_file": label,
                "condition": condition,
                "column": column,
                "n_total": len(values),
                "n_restore": int(restore_mask.sum()),
                "restore_rate": float(np.mean(restore_mask)),
                "restore_D24_chi_p": chi_square_p(counts24),
                "restore_R_D24": resultant_from_counts(counts24, 1),
                "restore_R_D12": resultant_from_counts(phase_counts_deg(selected, 12), 1),
                "restore_R_D8": resultant_from_counts(phase_counts_deg(selected, 8), 1),
                "restore_distance_D24_mean": float(np.nanmean(nearest_grid_distance_deg(selected, 24))) if len(selected) else np.nan,
                "nonrestore_distance_D24_mean": float(np.nanmean(nearest_grid_distance_deg(rejected, 24))) if len(rejected) else np.nan,
            })
    out = pd.DataFrame(rows)
    if "restore_D24_chi_p" in out.columns:
        out["restore_D24_chi_q"] = bh_fdr(out["restore_D24_chi_p"].astype(float).tolist())
    return out


def write_summary(output_path: Path, sync: pd.DataFrame, eps: pd.DataFrame) -> None:
    obs_sync = sync[sync.get("condition", pd.Series(dtype=str)).eq("observed")] if len(sync) else sync
    obs_eps = eps[eps.get("condition", pd.Series(dtype=str)).eq("observed")] if len(eps) else eps
    sync_hits = obs_sync[
        obs_sync.get("circ_mean_D24_chi_q", pd.Series(dtype=float)).le(0.05)
        | obs_sync.get("circ_mean_D12_chi_q", pd.Series(dtype=float)).le(0.05)
    ] if len(obs_sync) else obs_sync
    eps_hits = obs_eps[obs_eps.get("restore_D24_chi_q", pd.Series(dtype=float)).le(0.05)] if len(obs_eps) else obs_eps
    lines = [
        "# Stage B Ricci Oscillation / Phase Synchronization Carrier Summary",
        "",
        "## Purpose",
        "",
        (
            "This exploratory Stage B test connects the carrier-realization "
            "question directly to the IDPC paper's Ricci oscillation, phase "
            "synchronization, and eps72 restoring outputs."
        ),
        "",
        "## Scope",
        "",
        (
            "The results are exploratory. They can suggest a follow-up target, "
            "but they do not confirm D12RG, GKS N=24, or a physical carrier."
        ),
        "",
        "## Results",
        "",
        f"- Ricci phase-sync files tested: {len(sync)}",
        f"- observed phase-sync files tested: {len(obs_sync)}",
        f"- observed phase-sync files with D24/D12 FDR q<=0.05: {len(sync_hits)}",
        f"- eps72 restoring rows tested: {len(eps)}",
        f"- observed eps72 restoring rows tested: {len(obs_eps)}",
        f"- observed eps72 restoring rows with D24 FDR q<=0.05: {len(eps_hits)}",
        "",
    ]
    if len(obs_sync):
        lines.append("## Observed Ricci Phase Sync")
        lines.append("")
        for _, row in obs_sync.iterrows():
            lines.append(
                f"- {row['source_file']}: psi_lock_R_mean={row['psi_lock_R_mean']:.6g}, "
                f"mean_abs_dpsi={row['mean_abs_dpsi_deg_mean']:.6g} deg, "
                f"D24 q={row['circ_mean_D24_chi_q']:.6g}, "
                f"D12 q={row['circ_mean_D12_chi_q']:.6g}, "
                f"R_D24={row['circ_mean_R_D24']:.6g}, "
                f"R_D12={row['circ_mean_R_D12']:.6g}"
            )
        lines.append("")
    if len(obs_eps):
        lines.append("## Observed eps72 Restoring")
        lines.append("")
        for _, row in obs_eps.iterrows():
            lines.append(
                f"- {row['source_file']} / {row['column']}: "
                f"restore_rate={row['restore_rate']:.6g}, "
                f"D24 q={row['restore_D24_chi_q']:.6g}, "
                f"R_D24={row['restore_R_D24']:.6g}, "
                f"restore_D24_distance={row['restore_distance_D24_mean']:.6g} deg"
            )
        lines.append("")
    lines.extend(["## Interpretation", ""])
    if len(sync_hits) or len(eps_hits):
        lines.append(
            "Ricci phase synchronization / eps72 restoration shows strong "
            "D24/D12-structured concentration in observed files. This is the "
            "most direct Stage B connection to the IDPC paper so far."
        )
        lines.append(
            "However, these quantities are already phase-synchronization and "
            "restoration readouts inside IDPC. The result therefore supports a "
            "carrier-readout follow-up hypothesis, not a confirmation of the "
            "carrier."
        )
    else:
        lines.append(
            "The Ricci phase synchronization outputs do not show a strong "
            "D24/D12 carrier-readout signal under the current exploratory test."
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    sync = sync_rows(args.input_root)
    eps = eps72_rows(args.input_root)
    sync_path = args.output_dir / "Stage_B_ricci_phase_sync_carrier_results.csv"
    eps_path = args.output_dir / "Stage_B_ricci_eps72_restoring_carrier_results.csv"
    summary_path = args.output_dir / "Stage_B_ricci_phase_sync_carrier_summary.md"
    sync.to_csv(sync_path, index=False)
    eps.to_csv(eps_path, index=False)
    write_summary(summary_path, sync, eps)
    print(f"wrote {sync_path}")
    print(f"wrote {eps_path}")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
