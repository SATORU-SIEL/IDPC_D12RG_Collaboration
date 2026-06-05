#!/usr/bin/env python3
"""Test IDPC boundary impulse J against trace-defect shell candidates.

This structural-layer script has two parts:

1. Boundary impulse law: reproduce whether J tracks dh using a frozen linear
   diagnostic and a label-shuffle null.
2. Trace-defect shell diagnostic: ask whether boundary-derived magnitudes are
   closer to the normalized 5->10->20 shell ratios [1, 2, 4] than random
   increasing ladders.

The shell test is deliberately reported as a specificity diagnostic, because
after scale normalization 5->10->20 becomes a doubling ladder and is not by
itself unique to D12RG.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PRIMARY_SHELL = np.array([1.0, 2.0, 4.0])
FIXED_ALTERNATIVES = {
    "compact_1_1.5_3": np.array([1.0, 1.5, 3.0]),
    "linear_1_2_3": np.array([1.0, 2.0, 3.0]),
    "wide_1_2.5_5": np.array([1.0, 2.5, 5.0]),
    "triple_1_3_6": np.array([1.0, 3.0, 6.0]),
    "phi_1_phi_phi2": np.array([1.0, 1.61803398875, 2.61803398875]),
}
SHELL_COLUMNS = ("J", "J_tilde", "dphi", "distance", "r_local")


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


def impulse_law_metrics(df: pd.DataFrame, n_perm: int, rng: np.random.Generator) -> dict[str, float]:
    part = df[["J", "dh"]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(part) < 5:
        return {
            "status": "excluded",
            "exclusion_reason": "fewer than 5 rows with J and dh",
            "n_rows": len(part),
        }
    x = part["dh"].to_numpy(dtype=float)
    y = part["J"].to_numpy(dtype=float)
    denom = float(np.dot(x, x))
    slope = float(np.dot(x, y) / denom) if denom > 0 else np.nan
    pred = slope * x
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2_no_intercept = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    pearson_r = float(np.corrcoef(x, y)[0, 1]) if np.std(x) > 0 and np.std(y) > 0 else np.nan

    null_abs_r = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        shuffled = np.array(y, copy=True)
        rng.shuffle(shuffled)
        null_abs_r[i] = abs(float(np.corrcoef(x, shuffled)[0, 1]))
    observed_abs_r = abs(pearson_r)
    raw_p = float((1.0 + np.sum(null_abs_r >= observed_abs_r)) / (n_perm + 1.0))
    sd = float(np.std(null_abs_r, ddof=1)) if n_perm > 1 else np.nan
    z = (observed_abs_r - float(np.mean(null_abs_r))) / sd if sd and np.isfinite(sd) else np.nan
    return {
        "status": "tested",
        "exclusion_reason": "",
        "n_rows": len(part),
        "slope_no_intercept": slope,
        "pearson_r": pearson_r,
        "abs_pearson_r": observed_abs_r,
        "r2_no_intercept": r2_no_intercept,
        "null_abs_r_mean": float(np.mean(null_abs_r)),
        "null_abs_r_sd": sd,
        "z_score": z,
        "raw_p": raw_p,
    }


def normalized_magnitudes(series: pd.Series) -> np.ndarray:
    values = series.replace([np.inf, -np.inf], np.nan).dropna().to_numpy(dtype=float)
    values = np.abs(values)
    values = values[values > 0]
    if len(values) == 0:
        return values
    scale = float(np.median(values))
    if not np.isfinite(scale) or scale <= 0:
        return np.array([], dtype=float)
    return values / scale


def shell_distance(values: np.ndarray, shell: np.ndarray) -> float:
    if len(values) == 0:
        return np.nan
    log_values = np.log(values + 1e-12)
    log_shell = np.log(shell + 1e-12)
    distances = np.min(np.abs(log_values[:, None] - log_shell[None, :]), axis=1)
    return float(np.mean(distances))


def random_shells(n_random: int, rng: np.random.Generator) -> np.ndarray:
    shells = np.empty((n_random, 3), dtype=float)
    for i in range(n_random):
        second = rng.uniform(1.2, 3.5)
        third = rng.uniform(second + 0.2, 7.0)
        shells[i] = [1.0, second, third]
    return shells


def shell_specificity_metrics(
    values: np.ndarray,
    n_random: int,
    rng: np.random.Generator,
) -> dict[str, float | str]:
    if len(values) < 5:
        return {
            "status": "excluded",
            "exclusion_reason": "fewer than 5 positive magnitudes",
            "n_values": len(values),
        }
    primary = shell_distance(values, PRIMARY_SHELL)
    fixed_scores = {
        name: shell_distance(values, shell)
        for name, shell in FIXED_ALTERNATIVES.items()
    }
    random_scores = np.array([
        shell_distance(values, shell)
        for shell in random_shells(n_random, rng)
    ])
    raw_p = float((1.0 + np.sum(random_scores <= primary)) / (n_random + 1.0))
    all_fixed = {"primary_1_2_4": primary, **fixed_scores}
    ranked = sorted(all_fixed.items(), key=lambda item: item[1])
    return {
        "status": "tested",
        "exclusion_reason": "",
        "n_values": len(values),
        "primary_shell_score": primary,
        "random_shell_mean": float(np.mean(random_scores)),
        "random_shell_sd": float(np.std(random_scores, ddof=1)),
        "raw_p_vs_random_shells": raw_p,
        "fixed_ladder_rank": 1 + [name for name, _ in ranked].index("primary_1_2_4"),
        "best_fixed_ladder": ranked[0][0],
        "best_fixed_ladder_score": ranked[0][1],
        "alternative_scores": "; ".join(f"{k}={v:.8g}" for k, v in fixed_scores.items()),
    }


def run_tests(
    input_root: Path,
    n_perm: int,
    n_random_shells: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    impulse_rows = []
    shell_rows = []

    for path in candidate_files(input_root, ("J_dh_kappa_pooled_v2.csv",)):
        label = display_path(path, input_root)
        try:
            df = pd.read_csv(path)
        except Exception as exc:  # pragma: no cover
            impulse_rows.append({
                "source_file": label,
                "condition": condition_from_path(path),
                "status": "read_error",
                "exclusion_reason": repr(exc),
            })
            continue
        if {"J", "dh"}.issubset(df.columns):
            row = impulse_law_metrics(df, n_perm, rng)
        else:
            row = {
                "status": "excluded",
                "exclusion_reason": "missing J or dh columns",
                "n_rows": len(df),
            }
        row.update({
            "source_file": label,
            "condition": condition_from_path(path),
            "n_perm": n_perm,
        })
        impulse_rows.append(row)

    shell_file_names = (
        "event_level_raw_table_TRUE_RICCI__HYBRID_PHI.csv",
        "event_level_with_fes_phase_TRUE_RICCI.csv",
    )
    for path in candidate_files(input_root, shell_file_names):
        label = display_path(path, input_root)
        try:
            df = pd.read_csv(path)
        except Exception as exc:  # pragma: no cover
            shell_rows.append({
                "source_file": label,
                "condition": condition_from_path(path),
                "column": "",
                "status": "read_error",
                "exclusion_reason": repr(exc),
            })
            continue
        for column in SHELL_COLUMNS:
            if column not in df.columns:
                continue
            values = normalized_magnitudes(df[column])
            row = shell_specificity_metrics(values, n_random_shells, rng)
            row.update({
                "source_file": label,
                "condition": condition_from_path(path),
                "column": column,
                "n_random_shells": n_random_shells,
            })
            shell_rows.append(row)

    impulse = pd.DataFrame(impulse_rows)
    shell = pd.DataFrame(shell_rows)
    if "raw_p" in impulse.columns:
        tested = impulse["status"].eq("tested")
        q_values = [np.nan] * len(impulse)
        for idx, q in zip(
            impulse.index[tested],
            bh_fdr(impulse.loc[tested, "raw_p"].astype(float).tolist()),
        ):
            q_values[idx] = q
        impulse["fdr_q"] = q_values
    if "raw_p_vs_random_shells" in shell.columns:
        tested = shell["status"].eq("tested")
        q_values = [np.nan] * len(shell)
        for idx, q in zip(
            shell.index[tested],
            bh_fdr(shell.loc[tested, "raw_p_vs_random_shells"].astype(float).tolist()),
        ):
            q_values[idx] = q
        shell["fdr_q_vs_random_shells"] = q_values
    return impulse, shell


def write_summary(output_path: Path, impulse: pd.DataFrame, shell: pd.DataFrame) -> None:
    impulse_tested = impulse[impulse.get("status", pd.Series(dtype=str)).eq("tested")]
    impulse_hits = impulse_tested[impulse_tested.get("fdr_q", pd.Series(dtype=float)).le(0.05)]
    observed_impulse_hits = impulse_hits[
        impulse_hits.get("condition", pd.Series(dtype=str)).eq("observed")
    ]
    control_impulse_hits = impulse_hits[
        impulse_hits.get("condition", pd.Series(dtype=str)).eq("control")
    ]
    shell_tested = shell[shell.get("status", pd.Series(dtype=str)).eq("tested")]
    shell_hits = shell_tested[
        shell_tested.get("fdr_q_vs_random_shells", pd.Series(dtype=float)).le(0.05)
    ]
    observed_shell = shell_tested[shell_tested.get("condition", pd.Series(dtype=str)).eq("observed")]
    observed_rank_first = int(observed_shell.get("fixed_ladder_rank", pd.Series(dtype=float)).eq(1).sum())
    lines = [
        "# Boundary Impulse Trace-Defect Shell Test",
        "",
        "## Purpose",
        "",
        (
            "This structural-layer test checks the IDPC boundary impulse law "
            "and an exploratory trace-defect shell diagnostic."
        ),
        "",
        "## Results",
        "",
        f"- impulse-law tested files: {len(impulse_tested)}",
        f"- impulse-law FDR q<=0.05 files: {len(impulse_hits)}",
        f"- observed impulse-law FDR q<=0.05 files: {len(observed_impulse_hits)}",
        f"- control impulse-law FDR q<=0.05 files: {len(control_impulse_hits)}",
        f"- shell tested rows: {len(shell_tested)}",
        f"- shell FDR q<=0.05 rows vs random shells: {len(shell_hits)}",
        f"- observed shell rows where [1,2,4] ranked first among fixed ladders: {observed_rank_first}",
        "",
    ]
    if len(impulse_tested):
        best = impulse_tested.sort_values("raw_p").head(3)
        lines.append("## Strongest Impulse-Law Rows")
        lines.append("")
        for _, row in best.iterrows():
            lines.append(
                f"- {row['source_file']}: r={row['pearson_r']:.6g}, "
                f"slope={row['slope_no_intercept']:.6g}, "
                f"p={row['raw_p']:.6g}, q={row['fdr_q']:.6g}"
            )
        lines.append("")
    lines.extend([
        "## Interpretation",
        "",
    ])
    if len(observed_impulse_hits) and len(control_impulse_hits) == 0:
        lines.append(
            "The observed boundary impulse law J~dh survives the current "
            "shuffle-null FDR control without matching control-file hits."
        )
    elif len(observed_impulse_hits) and len(control_impulse_hits):
        lines.append(
            "The observed boundary impulse law J~dh survives FDR, but similar "
            "effects also appear in control/back-up files. This reproduces the "
            "impulse relation, but does not establish D12RG specificity."
        )
    elif len(impulse_hits):
        lines.append(
            "Only non-observed/control impulse-law rows survive the current "
            "shuffle-null FDR control."
        )
    else:
        lines.append(
            "The boundary impulse law J~dh does not survive the current "
            "shuffle-null FDR control."
        )
    if len(shell_hits):
        lines.append(
            "Some normalized shell rows beat random shell controls after FDR, "
            "but this remains exploratory unless [1,2,4] also beats fixed "
            "alternative ladders in observed rows."
        )
    else:
        lines.append(
            "The normalized [1,2,4] shell diagnostic does not survive random "
            "shell controls after FDR."
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--n-random-shells", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260606)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    impulse, shell = run_tests(args.input_root, args.n_perm, args.n_random_shells, args.seed)

    impulse_path = args.output_dir / "IDPC_boundary_impulse_law_results.csv"
    shell_path = args.output_dir / "IDPC_boundary_impulse_trace_shell_results.csv"
    summary_path = args.output_dir / "IDPC_boundary_impulse_trace_defect_summary.md"
    impulse.to_csv(impulse_path, index=False)
    shell.to_csv(shell_path, index=False)
    write_summary(summary_path, impulse, shell)

    print(f"wrote {impulse_path}")
    print(f"wrote {shell_path}")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
