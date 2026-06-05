#!/usr/bin/env python3
"""Stage A+ IDPC structural holonomy / global loop test.

This script adapts the closed-loop idea to the IDPC structural layer.

Primary loop:
    phi_t -> boundary impulse J_t -> residual closure_t -> FES_t -> phi_(t+1)

Primary loop phase:
    H = phi_phase_t + J_phase_t + residual_phase_t + FES_phase_t - phi_phase_(t+1)

This avoids the telescoping cancellation that occurs when a loop is defined as
a simple sum of pairwise phase differences. The test asks whether this fixed
structural loop phase is more concentrated than session-preserving circular
shift nulls.

This is exploratory Stage A+ and should not be interpreted as proof of D12RG.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = ("label", "task_idx", "phi", "J", "distance", "fes_phase")


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


def wrap_angle(x: np.ndarray | float) -> np.ndarray | float:
    return (np.asarray(x) + np.pi) % (2.0 * np.pi) - np.pi


def resultant_length(angles: np.ndarray) -> float:
    if len(angles) == 0:
        return np.nan
    return float(abs(np.mean(np.exp(1j * angles))))


def closure_error(angles: np.ndarray) -> float:
    if len(angles) == 0:
        return np.nan
    return float(np.mean(np.abs(wrap_angle(angles))))


def rank_phase(values: pd.Series, invert: bool = False) -> np.ndarray:
    series = values.replace([np.inf, -np.inf], np.nan)
    arr = series.to_numpy(dtype=float)
    valid = np.isfinite(arr)
    out = np.full(len(arr), np.nan, dtype=float)
    if valid.sum() == 0:
        return out
    ranked = pd.Series(arr[valid]).rank(method="first", pct=True).to_numpy()
    if invert:
        ranked = 1.0 - ranked
    out[valid] = 2.0 * np.pi * np.clip(ranked, 0.0, 1.0 - 1e-12)
    return out


def fes_phase(values: pd.Series) -> np.ndarray:
    raw = values.astype("string").fillna("")
    valid = raw != ""
    out = np.full(len(raw), np.nan, dtype=float)
    states = sorted(raw[valid].unique().tolist())
    if not states:
        return out
    mapping = {state: idx for idx, state in enumerate(states)}
    m = len(states)
    out[valid.to_numpy()] = [
        2.0 * np.pi * mapping[state] / m
        for state in raw[valid].tolist()
    ]
    return out


def prepare_event_table(df: pd.DataFrame) -> pd.DataFrame:
    if not set(REQUIRED_COLUMNS).issubset(df.columns):
        missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
        raise ValueError(f"missing required columns: {missing}")
    part = df.copy()
    part = part.sort_values(["label", "task_idx"], kind="mergesort")
    impulse_col = "J_tilde" if "J_tilde" in part.columns else "J"
    residual_col = "distance_z" if "distance_z" in part.columns else "distance"
    part["phi_phase"] = rank_phase(part["phi"])
    part["j_phase"] = rank_phase(part[impulse_col])
    # Low distance means stronger closure/contraction, so invert rank.
    part["residual_phase"] = rank_phase(part[residual_col], invert=True)
    part["fes_phase_angle"] = fes_phase(part["fes_phase"])
    return part


def loop_angles_from_table(part: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    rows = []
    for label, group in part.groupby("label", sort=False):
        group = group.sort_values("task_idx", kind="mergesort").reset_index(drop=True)
        if len(group) < 2:
            continue
        for idx in range(len(group) - 1):
            current = group.iloc[idx]
            nxt = group.iloc[idx + 1]
            values = [
                current["phi_phase"],
                current["j_phase"],
                current["residual_phase"],
                current["fes_phase_angle"],
                nxt["phi_phase"],
            ]
            if not all(np.isfinite(values)):
                continue
            h = wrap_angle(values[0] + values[1] + values[2] + values[3] - values[4])
            rows.append({
                "label": label,
                "task_idx": current["task_idx"],
                "next_task_idx": nxt["task_idx"],
                "loop_phase": float(h),
            })
    table = pd.DataFrame(rows)
    return table["loop_phase"].to_numpy(dtype=float) if len(table) else np.array([]), table


def shifted_loop_angles(part: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
    shifted = part.copy()
    for label, idx in shifted.groupby("label", sort=False).groups.items():
        idx_list = list(idx)
        n = len(idx_list)
        if n < 2:
            continue
        for col in ["j_phase", "residual_phase", "fes_phase_angle"]:
            offset = int(rng.integers(1, n))
            shifted.loc[idx_list, col] = np.roll(shifted.loc[idx_list, col].to_numpy(), offset)
    angles, _ = loop_angles_from_table(shifted)
    return angles


def root_counts(angles: np.ndarray, ring_size: int = 12) -> tuple[np.ndarray, int, int]:
    if len(angles) == 0:
        return np.zeros(ring_size, dtype=int), -1, 0
    roots = np.mod(np.rint(ring_size * angles / (2.0 * np.pi)).astype(int), ring_size)
    counts = np.bincount(roots, minlength=ring_size)
    preferred = int(np.argmax(counts))
    return counts, preferred, int(counts[preferred])


def chi_square_uniform_p(counts: np.ndarray) -> float:
    total = int(np.sum(counts))
    if total == 0:
        return np.nan
    expected = np.full(len(counts), total / len(counts), dtype=float)
    stat = float(np.sum((counts - expected) ** 2 / expected))
    try:
        from scipy.stats import chi2
        return float(chi2.sf(stat, len(counts) - 1))
    except Exception:  # pragma: no cover
        return np.nan


def permutation_metrics(
    part: pd.DataFrame,
    observed_angles: np.ndarray,
    n_perm: int,
    rng: np.random.Generator,
) -> dict[str, float]:
    observed_r = resultant_length(observed_angles)
    observed_error = closure_error(observed_angles)
    if len(observed_angles) < 3:
        return {
            "null_R_mean": np.nan,
            "null_R_sd": np.nan,
            "R_z": np.nan,
            "R_raw_p": np.nan,
            "null_closure_error_mean": np.nan,
            "null_closure_error_sd": np.nan,
            "closure_error_z": np.nan,
            "closure_error_raw_p": np.nan,
        }
    null_r = np.empty(n_perm, dtype=float)
    null_error = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        angles = shifted_loop_angles(part, rng)
        null_r[i] = resultant_length(angles)
        null_error[i] = closure_error(angles)
    r_sd = float(np.std(null_r, ddof=1)) if n_perm > 1 else np.nan
    e_sd = float(np.std(null_error, ddof=1)) if n_perm > 1 else np.nan
    return {
        "null_R_mean": float(np.mean(null_r)),
        "null_R_sd": r_sd,
        "R_z": (observed_r - float(np.mean(null_r))) / r_sd if r_sd and np.isfinite(r_sd) else np.nan,
        "R_raw_p": float((1.0 + np.sum(null_r >= observed_r)) / (n_perm + 1.0)),
        "null_closure_error_mean": float(np.mean(null_error)),
        "null_closure_error_sd": e_sd,
        "closure_error_z": (float(np.mean(null_error)) - observed_error) / e_sd if e_sd and np.isfinite(e_sd) else np.nan,
        "closure_error_raw_p": float((1.0 + np.sum(null_error <= observed_error)) / (n_perm + 1.0)),
    }


def alternative_ring_rank(angles: np.ndarray) -> dict[str, object]:
    rings = [8, 10, 12, 16, 20, 24]
    scores = {}
    for ring in rings:
        counts, _, preferred_count = root_counts(angles, ring)
        scores[f"D{ring}"] = preferred_count / max(int(np.sum(counts)), 1)
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return {
        "D12_root_fraction_rank": 1 + [name for name, _ in ranked].index("D12"),
        "best_ring": ranked[0][0],
        "best_ring_root_fraction": ranked[0][1],
        "alternative_ring_root_fractions": "; ".join(f"{k}={v:.8g}" for k, v in scores.items() if k != "D12"),
    }


def run_tests(input_root: Path, n_perm: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    result_rows = []
    root_rows = []
    files = sorted(input_root.rglob("event_level_with_fes_phase_TRUE_RICCI.csv"))
    for path in files:
        label = display_path(path, input_root)
        condition = condition_from_path(path)
        try:
            df = pd.read_csv(path)
            part = prepare_event_table(df)
        except Exception as exc:
            result_rows.append({
                "source_file": label,
                "condition": condition,
                "status": "excluded",
                "exclusion_reason": repr(exc),
            })
            continue
        angles, loop_table = loop_angles_from_table(part)
        counts, preferred, preferred_count = root_counts(angles, 12)
        row = {
            "source_file": label,
            "condition": condition,
            "status": "tested" if len(angles) >= 3 else "excluded",
            "exclusion_reason": "" if len(angles) >= 3 else "fewer than 3 completed structural loops",
            "loop_type": "phi_J_residual_FES_next_phi",
            "n_events": len(part),
            "n_completed_loops": len(angles),
            "holonomy_resultant_R": resultant_length(angles),
            "closure_error": closure_error(angles),
            "preferred_root": preferred,
            "preferred_root_count": preferred_count,
            "roots_uniformity_p": chi_square_uniform_p(counts),
            "n_perm": n_perm,
        }
        if len(angles) >= 3:
            row.update(permutation_metrics(part, angles, n_perm, rng))
            row.update(alternative_ring_rank(angles))
        result_rows.append(row)

        total = max(int(np.sum(counts)), 1)
        expected = total / 12.0
        for k, count in enumerate(counts):
            root_rows.append({
                "source_file": label,
                "condition": condition,
                "loop_type": "phi_J_residual_FES_next_phi",
                "ring_size": 12,
                "root_k": k,
                "root_angle": 2.0 * np.pi * k / 12.0,
                "count": int(count),
                "expected_count": expected,
                "standardized_residual": (count - expected) / np.sqrt(expected) if expected > 0 else np.nan,
            })

    results = pd.DataFrame(result_rows)
    roots = pd.DataFrame(root_rows)
    for p_col, q_col in [
        ("R_raw_p", "R_fdr_q"),
        ("closure_error_raw_p", "closure_error_fdr_q"),
        ("roots_uniformity_p", "roots_uniformity_fdr_q"),
    ]:
        if p_col in results.columns:
            tested = results["status"].eq("tested")
            q_values = [np.nan] * len(results)
            for idx, q in zip(
                results.index[tested],
                bh_fdr(results.loc[tested, p_col].astype(float).tolist()),
            ):
                q_values[idx] = q
            results[q_col] = q_values
    return results, roots


def write_summary(output_path: Path, results: pd.DataFrame) -> None:
    tested = results[results.get("status", pd.Series(dtype=str)).eq("tested")]
    observed = tested[tested.get("condition", pd.Series(dtype=str)).eq("observed")]
    control = tested[tested.get("condition", pd.Series(dtype=str)).eq("control")]
    r_hits = tested[tested.get("R_fdr_q", pd.Series(dtype=float)).le(0.05)]
    closure_hits = tested[tested.get("closure_error_fdr_q", pd.Series(dtype=float)).le(0.05)]
    roots_hits = tested[tested.get("roots_uniformity_fdr_q", pd.Series(dtype=float)).le(0.05)]
    observed_d12_rank_first = int(observed.get("D12_root_fraction_rank", pd.Series(dtype=float)).eq(1).sum())

    lines = [
        "# Stage A+ Structural Holonomy Loop Test",
        "",
        "## Purpose",
        "",
        (
            "This test adapts the closed-loop / holonomy idea to the IDPC "
            "structural layer. It tests the fixed loop phi_t -> J_t -> "
            "residual_t -> FES_t -> phi_(t+1)."
        ),
        "",
        "## Loop Definition",
        "",
        "`H = phi_phase_t + J_phase_t + residual_phase_t + FES_phase_t - phi_phase_(t+1)`",
        "",
        "The null model circularly shifts J, residual, and FES phases within each label/session while keeping phi order fixed.",
        "",
        "## Results",
        "",
        f"- tested files: {len(tested)}",
        f"- observed tested files: {len(observed)}",
        f"- control tested files: {len(control)}",
        f"- holonomy concentration FDR q<=0.05 files: {len(r_hits)}",
        f"- closure-error FDR q<=0.05 files: {len(closure_hits)}",
        f"- roots-uniformity FDR q<=0.05 files: {len(roots_hits)}",
        f"- observed files where D12 ranked first among ring controls: {observed_d12_rank_first}",
        "",
    ]
    if len(observed):
        lines.append("## Observed Rows")
        lines.append("")
        for _, row in observed.sort_values("R_raw_p").iterrows():
            lines.append(
                f"- {row['source_file']}: loops={int(row['n_completed_loops'])}, "
                f"R={row['holonomy_resultant_R']:.6g}, "
                f"R p={row['R_raw_p']:.6g}, R q={row['R_fdr_q']:.6g}, "
                f"closure p={row['closure_error_raw_p']:.6g}, "
                f"D12 ring rank={row['D12_root_fraction_rank']}, "
                f"best ring={row['best_ring']}"
            )
        lines.append("")
    lines.extend(["## Interpretation", ""])
    observed_r_hits = r_hits[r_hits.get("condition", pd.Series(dtype=str)).eq("observed")]
    observed_closure_hits = closure_hits[closure_hits.get("condition", pd.Series(dtype=str)).eq("observed")]
    if len(observed_r_hits) or len(observed_closure_hits):
        lines.append(
            "At least one observed structural loop metric survives the current "
            "circular-shift FDR control. This supports further Stage A+ testing, "
            "but does not establish D12RG specificity unless D12 also beats "
            "alternative rings and controls."
        )
    else:
        lines.append(
            "The fixed Stage A+ structural loop does not survive the current "
            "circular-shift FDR controls as a positive holonomy/closure result."
        )
    if observed_d12_rank_first == 0:
        lines.append(
            "D12 does not rank first among the tested ring controls for observed "
            "files, so this run does not support D12-specific loop closure."
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260606)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results, roots = run_tests(args.input_root, args.n_perm, args.seed)
    results_path = args.output_dir / "Stage_A_plus_structural_holonomy_loop_results.csv"
    roots_path = args.output_dir / "Stage_A_plus_structural_holonomy_roots.csv"
    summary_path = args.output_dir / "Stage_A_plus_structural_holonomy_loop_summary.md"
    results.to_csv(results_path, index=False)
    roots.to_csv(roots_path, index=False)
    write_summary(summary_path, results)
    print(f"wrote {results_path}")
    print(f"wrote {roots_path}")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
