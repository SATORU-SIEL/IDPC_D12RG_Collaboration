#!/usr/bin/env python3
"""Test residual contraction / closure against a fixed D12 readout.

This structural-layer test does not use event index mod 12. It asks whether
IDPC-derived contraction or closure-like subsets are closer to fixed D12 phase
readout positions than matched random subsets, rotations, or alternative cyclic
partitions.

Primary readout:
    D12 fixed origin, phase positions every 30 degrees.

Primary contraction subsets:
    - ricci_eps72_restoring_test.csv: restore == 1 on eps72_deg
    - event_level_with_fes_phase_TRUE_RICCI.csv: lowest 25% distance by phase
    - event_level_with_fes_phase_TRUE_RICCI.csv: highest 25% r_local by phase

The output is a fixed-origin residual-closure readout diagnostic.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ALTERNATIVE_PARTITIONS = (8, 10, 11, 13, 16, 20)


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


def phase_to_degrees(values: pd.Series, source: str) -> np.ndarray:
    arr = values.replace([np.inf, -np.inf], np.nan).dropna().to_numpy(dtype=float)
    if source == "radians":
        arr = np.degrees(arr)
    return np.mod(arr, 360.0)


def angular_distance_to_grid(degrees: np.ndarray, n: int, offset_deg: float = 0.0) -> np.ndarray:
    step = 360.0 / float(n)
    shifted = np.mod(degrees - offset_deg, 360.0)
    residual = np.mod(shifted + step / 2.0, step) - step / 2.0
    return np.abs(residual)


def mean_grid_distance(degrees: np.ndarray, mask: np.ndarray, n: int = 12, offset_deg: float = 0.0) -> float:
    if mask.sum() == 0:
        return np.nan
    return float(np.mean(angular_distance_to_grid(degrees[mask], n, offset_deg)))


def rotation_scores(degrees: np.ndarray, mask: np.ndarray, n: int = 12) -> dict[str, float | str]:
    if mask.sum() == 0:
        return {
            "rotation_control_rank": np.nan,
            "best_rotation_deg": np.nan,
            "best_rotation_score": np.nan,
            "rotation_scores": "",
        }
    step = 360.0 / n
    offsets = np.arange(n, dtype=float) * (step / n)
    # The offsets cover one D12 bin width. Other rotations repeat modulo 30 deg.
    scores = np.array([mean_grid_distance(degrees, mask, n, off) for off in offsets])
    fixed_score = scores[0]
    order = np.argsort(scores)
    rank = 1 + int(np.where(order == 0)[0][0])
    return {
        "rotation_control_rank": rank,
        "best_rotation_deg": float(offsets[order[0]]),
        "best_rotation_score": float(scores[order[0]]),
        "rotation_scores": "; ".join(f"{off:.6g}:{score:.8g}" for off, score in zip(offsets, scores)),
    }


def partition_scores(degrees: np.ndarray, mask: np.ndarray) -> dict[str, float | str]:
    if mask.sum() == 0:
        return {
            "partition_rank_d12": np.nan,
            "best_partition": "",
            "best_partition_score": np.nan,
            "alternative_partition_scores": "",
        }
    scores = {"D12": mean_grid_distance(degrees, mask, 12, 0.0)}
    for n in ALTERNATIVE_PARTITIONS:
        scores[f"D{n}"] = mean_grid_distance(degrees, mask, n, 0.0)
    ranked = sorted(scores.items(), key=lambda item: item[1])
    return {
        "partition_rank_d12": 1 + [name for name, _ in ranked].index("D12"),
        "best_partition": ranked[0][0],
        "best_partition_score": ranked[0][1],
        "alternative_partition_scores": "; ".join(f"{k}={v:.8g}" for k, v in scores.items() if k != "D12"),
    }


def random_subset_null(
    degrees: np.ndarray,
    mask: np.ndarray,
    n_perm: int,
    rng: np.random.Generator,
) -> dict[str, float]:
    n = len(degrees)
    k = int(mask.sum())
    if n < 5 or k < 2 or k >= n:
        return {
            "null_mean": np.nan,
            "null_sd": np.nan,
            "z_score": np.nan,
            "raw_p": np.nan,
        }
    observed = mean_grid_distance(degrees, mask, 12, 0.0)
    null = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        rand_mask = np.zeros(n, dtype=bool)
        rand_mask[rng.choice(n, size=k, replace=False)] = True
        null[i] = mean_grid_distance(degrees, rand_mask, 12, 0.0)
    # One-sided: smaller distance means more concentrated near fixed D12 readout.
    raw_p = float((1.0 + np.sum(null <= observed)) / (n_perm + 1.0))
    sd = float(np.std(null, ddof=1)) if n_perm > 1 else np.nan
    z = (float(np.mean(null)) - observed) / sd if sd and np.isfinite(sd) else np.nan
    return {
        "null_mean": float(np.mean(null)),
        "null_sd": sd,
        "z_score": z,
        "raw_p": raw_p,
    }


def make_result_row(
    source_file: str,
    condition: str,
    test_type: str,
    phase_column: str,
    degrees: np.ndarray,
    mask: np.ndarray,
    n_perm: int,
    rng: np.random.Generator,
) -> dict[str, object]:
    observed = mean_grid_distance(degrees, mask, 12, 0.0)
    row: dict[str, object] = {
        "source_file": source_file,
        "condition": condition,
        "test_type": test_type,
        "phase_column": phase_column,
        "status": "tested" if np.isfinite(observed) else "excluded",
        "exclusion_reason": "" if np.isfinite(observed) else "empty selected subset",
        "n_total": len(degrees),
        "n_selected": int(mask.sum()),
        "observed_d12_mean_distance_deg": observed,
        "n_perm": n_perm,
    }
    if np.isfinite(observed):
        row.update(random_subset_null(degrees, mask, n_perm, rng))
        row.update(rotation_scores(degrees, mask, 12))
        row.update(partition_scores(degrees, mask))
    return row


def eps72_rows(
    path: Path,
    input_root: Path,
    n_perm: int,
    rng: np.random.Generator,
) -> list[dict[str, object]]:
    label = display_path(path, input_root)
    condition = condition_from_path(path)
    try:
        df = pd.read_csv(path)
    except Exception as exc:  # pragma: no cover
        return [{
            "source_file": label,
            "condition": condition,
            "test_type": "eps72_restore",
            "phase_column": "eps72_deg",
            "status": "read_error",
            "exclusion_reason": repr(exc),
        }]
    if not {"eps72_deg", "restore"}.issubset(df.columns):
        return [{
            "source_file": label,
            "condition": condition,
            "test_type": "eps72_restore",
            "phase_column": "eps72_deg",
            "status": "excluded",
            "exclusion_reason": "missing eps72_deg or restore columns",
            "n_total": len(df),
            "n_selected": 0,
        }]
    part = df[["eps72_deg", "restore"]].replace([np.inf, -np.inf], np.nan).dropna()
    degrees = phase_to_degrees(part["eps72_deg"], "degrees")
    mask = part["restore"].to_numpy(dtype=float) > 0
    return [make_result_row(label, condition, "eps72_restore", "eps72_deg", degrees, mask, n_perm, rng)]


def quantile_mask(values: pd.Series, mode: str, q: float = 0.25) -> np.ndarray:
    arr = values.replace([np.inf, -np.inf], np.nan).to_numpy(dtype=float)
    valid = np.isfinite(arr)
    mask = np.zeros(len(arr), dtype=bool)
    if valid.sum() < 5:
        return mask
    if mode == "low":
        threshold = np.nanquantile(arr[valid], q)
        mask = valid & (arr <= threshold)
    elif mode == "high":
        threshold = np.nanquantile(arr[valid], 1.0 - q)
        mask = valid & (arr >= threshold)
    return mask


def event_level_rows(
    path: Path,
    input_root: Path,
    n_perm: int,
    rng: np.random.Generator,
) -> list[dict[str, object]]:
    label = display_path(path, input_root)
    condition = condition_from_path(path)
    try:
        df = pd.read_csv(path)
    except Exception as exc:  # pragma: no cover
        return [{
            "source_file": label,
            "condition": condition,
            "test_type": "event_level",
            "phase_column": "phase",
            "status": "read_error",
            "exclusion_reason": repr(exc),
        }]
    if "phase" not in df.columns:
        return []
    phase_valid = df["phase"].replace([np.inf, -np.inf], np.nan).notna().to_numpy()
    degrees_all = np.full(len(df), np.nan, dtype=float)
    degrees_all[phase_valid] = phase_to_degrees(df.loc[phase_valid, "phase"], "radians")

    rows = []
    tests = []
    if "distance" in df.columns:
        tests.append(("low_distance_q25", quantile_mask(df["distance"], "low", 0.25)))
    if "distance_z" in df.columns:
        tests.append(("low_distance_z_q25", quantile_mask(df["distance_z"], "low", 0.25)))
    if "r_local" in df.columns:
        tests.append(("high_r_local_q25", quantile_mask(df["r_local"], "high", 0.25)))
    if "r_local_z" in df.columns:
        tests.append(("high_r_local_z_q25", quantile_mask(df["r_local_z"], "high", 0.25)))

    for test_type, mask in tests:
        valid = phase_valid & mask
        degrees = degrees_all[phase_valid]
        selected = valid[phase_valid]
        if len(degrees) == 0:
            continue
        rows.append(make_result_row(label, condition, test_type, "phase", degrees, selected, n_perm, rng))
    return rows


def run_tests(input_root: Path, n_perm: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for path in candidate_files(input_root, ("ricci_eps72_restoring_test.csv",)):
        rows.extend(eps72_rows(path, input_root, n_perm, rng))
    for path in candidate_files(input_root, ("event_level_with_fes_phase_TRUE_RICCI.csv",)):
        rows.extend(event_level_rows(path, input_root, n_perm, rng))
    results = pd.DataFrame(rows)
    if "raw_p" in results.columns:
        tested = results["status"].eq("tested")
        q_values = [np.nan] * len(results)
        for idx, q in zip(
            results.index[tested],
            bh_fdr(results.loc[tested, "raw_p"].astype(float).tolist()),
        ):
            q_values[idx] = q
        results["fdr_q"] = q_values
    return results


def write_summary(output_path: Path, results: pd.DataFrame) -> None:
    tested = results[results.get("status", pd.Series(dtype=str)).eq("tested")]
    observed = tested[tested.get("condition", pd.Series(dtype=str)).eq("observed")]
    control = tested[tested.get("condition", pd.Series(dtype=str)).eq("control")]
    hits = tested[tested.get("fdr_q", pd.Series(dtype=float)).le(0.05)]
    observed_hits = hits[hits.get("condition", pd.Series(dtype=str)).eq("observed")]
    control_hits = hits[hits.get("condition", pd.Series(dtype=str)).eq("control")]
    observed_d12_rank_first = int(observed.get("partition_rank_d12", pd.Series(dtype=float)).eq(1).sum())
    observed_rotation_first = int(observed.get("rotation_control_rank", pd.Series(dtype=float)).eq(1).sum())

    lines = [
        "# Residual Closure D12 Readout Test",
        "",
        "## Purpose",
        "",
        (
            "This structural-layer test asks whether IDPC residual closure or "
            "contraction subsets are closer to fixed D12 readout positions than "
            "matched random subsets, phase rotations, and alternative cyclic "
            "partitions."
        ),
        "",
        "## Results",
        "",
        f"- tested rows: {len(tested)}",
        f"- observed tested rows: {len(observed)}",
        f"- control tested rows: {len(control)}",
        f"- FDR q<=0.05 rows: {len(hits)}",
        f"- observed FDR q<=0.05 rows: {len(observed_hits)}",
        f"- control FDR q<=0.05 rows: {len(control_hits)}",
        f"- observed rows where D12 ranked first among partitions: {observed_d12_rank_first}",
        f"- observed rows where fixed D12 origin ranked first among rotations: {observed_rotation_first}",
        "",
    ]
    if len(observed):
        lines.append("## Observed Rows")
        lines.append("")
        for _, row in observed.sort_values("raw_p").head(8).iterrows():
            lines.append(
                f"- {row['source_file']} / {row['test_type']}: "
                f"distance={row['observed_d12_mean_distance_deg']:.6g} deg, "
                f"p={row['raw_p']:.6g}, q={row['fdr_q']:.6g}, "
                f"D12 partition rank={row['partition_rank_d12']}, "
                f"rotation rank={row['rotation_control_rank']}"
            )
        lines.append("")
    lines.extend(["## Interpretation", ""])
    if len(observed_hits) and len(control_hits) == 0:
        lines.append(
            "At least one observed residual-closure row survives FDR without "
            "matching control hits. This supports further D12 readout testing, "
            "but does not prove D12RG."
        )
    elif len(observed_hits) and len(control_hits):
        lines.append(
            "Observed residual-closure rows survive FDR, but control rows also "
            "survive. This suggests a generic contraction/readout geometry "
            "rather than D12RG specificity."
        )
    elif len(observed):
        lines.append(
            "Observed residual-closure rows do not survive the combined random "
            "subset, rotation, partition, and FDR checks as D12-specific."
        )
    else:
        lines.append("No observed residual-closure rows were eligible.")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260606)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = run_tests(args.input_root, args.n_perm, args.seed)

    result_path = args.output_dir / "IDPC_residual_closure_d12_readout_results.csv"
    summary_path = args.output_dir / "IDPC_residual_closure_d12_readout_summary.md"
    results.to_csv(result_path, index=False)
    write_summary(summary_path, results)

    print(f"wrote {result_path}")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
