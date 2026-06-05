#!/usr/bin/env python3
"""Test FES transition expansion against the 5->10->20 ladder.

This is a structural-layer IDPC x D12RG test. It asks whether the IDPC
Five Energy Star sequence expands as:

    5 states -> 10 unordered non-self transitions -> 20 directed non-self transitions

The null model shuffles FES labels within a sequence, preserving event count
and label frequency while destroying temporal transition order.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PRIMARY_LADDER = (5.0, 10.0, 20.0)
ALTERNATIVE_LADDERS = {
    "4-8-16": (4.0, 8.0, 16.0),
    "6-12-24": (6.0, 12.0, 24.0),
    "3-6-12": (3.0, 6.0, 12.0),
    "7-14-28": (7.0, 14.0, 28.0),
    "8-16-32": (8.0, 16.0, 32.0),
}


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


def find_fes_files(input_root: Path) -> list[Path]:
    names = {
        "event_level_with_fes_phase_TRUE_RICCI.csv",
        "event_level_with_clusters_TRUE_RICCI__HYBRID_PHI.csv",
    }
    return sorted(path for path in input_root.rglob("*.csv") if path.name in names)


def display_path(path: Path, input_root: Path) -> str:
    try:
        return str(path.relative_to(input_root))
    except ValueError:
        return path.name


def sequence_groups(df: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
    if "label" in df.columns:
        groups = [(str(key), part.copy()) for key, part in df.groupby("label")]
    elif "task_idx" in df.columns:
        groups = [(str(key), part.copy()) for key, part in df.groupby("task_idx")]
    else:
        groups = [("all", df.copy())]

    ordered = []
    for name, part in groups:
        sort_cols = [col for col in ["task_idx", "event_task", "time", "t"] if col in part.columns]
        if sort_cols:
            part = part.sort_values(sort_cols, kind="mergesort")
        ordered.append((name, part))
    return ordered


def transition_metrics(values: np.ndarray, ladder: tuple[float, float, float]) -> dict[str, float]:
    values = np.asarray(values)
    values = values[pd.notna(values)]
    if len(values) < 2:
        return {
            "n_events": float(len(values)),
            "n_states": np.nan,
            "n_unordered_nonself_pairs": np.nan,
            "n_directed_nonself_pairs": np.nan,
            "self_transition_rate": np.nan,
            "transition_entropy_norm": np.nan,
            "ladder_distance": np.nan,
        }

    states = sorted(pd.unique(values))
    transitions = list(zip(values[:-1], values[1:]))
    nonself = [(a, b) for a, b in transitions if a != b]
    directed = set(nonself)
    unordered = {tuple(sorted((a, b))) for a, b in nonself}
    counts = pd.Series(transitions).value_counts()
    probs = counts.to_numpy(dtype=float) / counts.sum()
    entropy = -float(np.sum(probs * np.log(probs + 1e-12)))
    max_entropy = np.log(max(len(counts), 1))
    entropy_norm = entropy / max_entropy if max_entropy > 0 else 0.0

    observed = np.array([len(states), len(unordered), len(directed)], dtype=float)
    target = np.array(ladder, dtype=float)
    distance = float(np.mean(np.abs(observed - target) / np.maximum(target, 1.0)))

    return {
        "n_events": float(len(values)),
        "n_states": float(len(states)),
        "n_unordered_nonself_pairs": float(len(unordered)),
        "n_directed_nonself_pairs": float(len(directed)),
        "self_transition_rate": float(1.0 - len(nonself) / max(len(transitions), 1)),
        "transition_entropy_norm": entropy_norm,
        "ladder_distance": distance,
    }


def permutation_test(
    values: np.ndarray,
    ladder: tuple[float, float, float],
    n_perm: int,
    rng: np.random.Generator,
) -> dict[str, float]:
    obs = transition_metrics(values, ladder)
    obs_distance = obs["ladder_distance"]
    if not np.isfinite(obs_distance) or len(values) < 4:
        return {
            **obs,
            "null_mean": np.nan,
            "null_sd": np.nan,
            "z_score": np.nan,
            "raw_p": np.nan,
        }

    null = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        shuffled = np.array(values, copy=True)
        rng.shuffle(shuffled)
        null[i] = transition_metrics(shuffled, ladder)["ladder_distance"]

    # One-sided: smaller distance means closer to the frozen ladder.
    raw_p = (1.0 + float(np.sum(null <= obs_distance))) / (n_perm + 1.0)
    sd = float(np.std(null, ddof=1)) if n_perm > 1 else np.nan
    z = (float(np.mean(null)) - obs_distance) / sd if sd and np.isfinite(sd) else np.nan
    return {
        **obs,
        "null_mean": float(np.mean(null)),
        "null_sd": sd,
        "z_score": z,
        "raw_p": raw_p,
    }


def run_tests(input_root: Path, n_perm: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    result_rows = []
    alt_rows = []
    for path in find_fes_files(input_root):
        path_label = display_path(path, input_root)
        try:
            df = pd.read_csv(path)
        except Exception as exc:  # pragma: no cover
            result_rows.append({
                "source_file": path_label,
                "sequence_id": "",
                "status": "read_error",
                "exclusion_reason": repr(exc),
            })
            continue

        state_col = "fes_phase" if "fes_phase" in df.columns else "cluster" if "cluster" in df.columns else None
        if state_col is None:
            result_rows.append({
                "source_file": path_label,
                "sequence_id": "",
                "status": "excluded",
                "exclusion_reason": "no fes_phase or cluster column",
            })
            continue

        for sequence_id, part in sequence_groups(df):
            values = part[state_col].dropna().to_numpy()
            if len(values) < 4:
                result_rows.append({
                    "source_file": path_label,
                    "sequence_id": sequence_id,
                    "state_column": state_col,
                    "status": "excluded",
                    "exclusion_reason": "fewer than 4 non-null states",
                })
                continue

            primary = permutation_test(values, PRIMARY_LADDER, n_perm, rng)
            result_rows.append({
                "source_file": path_label,
                "sequence_id": sequence_id,
                "state_column": state_col,
                "status": "tested",
                "ladder_name": "5-10-20",
                "n_perm": n_perm,
                "exclusion_reason": "",
                **primary,
            })

            scores = {"5-10-20": primary["ladder_distance"]}
            for name, ladder in ALTERNATIVE_LADDERS.items():
                metrics = transition_metrics(values, ladder)
                scores[name] = metrics["ladder_distance"]
                alt_rows.append({
                    "source_file": path_label,
                    "sequence_id": sequence_id,
                    "state_column": state_col,
                    "alternative_ladder_name": name,
                    "primary_ladder_score": primary["ladder_distance"],
                    "alternative_ladder_score": metrics["ladder_distance"],
                    "golden_is_better": primary["ladder_distance"] < metrics["ladder_distance"],
                })

            ranked = sorted(scores.items(), key=lambda item: item[1])
            rank = 1 + [name for name, _ in ranked].index("5-10-20")
            for row in alt_rows[-len(ALTERNATIVE_LADDERS):]:
                row["golden_rank_among_ladders"] = rank
                row["best_ladder_name"] = ranked[0][0]
                row["best_ladder_score"] = ranked[0][1]

    results = pd.DataFrame(result_rows)
    alternatives = pd.DataFrame(alt_rows)
    if "raw_p" in results.columns:
        tested = results["status"].eq("tested")
        q = [np.nan] * len(results)
        q_tested = bh_fdr(results.loc[tested, "raw_p"].astype(float).tolist())
        for idx, value in zip(results.index[tested], q_tested):
            q[idx] = value
        results["fdr_q"] = q
    return results, alternatives


def write_summary(output_path: Path, results: pd.DataFrame, alternatives: pd.DataFrame) -> None:
    tested = results[results.get("status", pd.Series(dtype=str)).eq("tested")]
    fdr_hits = tested[tested.get("fdr_q", pd.Series(dtype=float)).le(0.05)]
    rank_first = 0
    if not alternatives.empty:
        rank_first = int(
            alternatives.drop_duplicates(["source_file", "sequence_id"])
            ["golden_rank_among_ladders"].eq(1).sum()
        )
    lines = [
        "# FES Transition Ladder Test",
        "",
        "## Purpose",
        "",
        (
            "This structural-layer test asks whether IDPC FES state sequences "
            "show a 5 states -> 10 unordered transitions -> 20 directed "
            "transitions expansion more strongly than order-destroying label "
            "shuffle nulls."
        ),
        "",
        "## Results",
        "",
        f"- tested sequences: {len(tested)}",
        f"- FDR q<=0.05 sequences: {len(fdr_hits)}",
        f"- sequences where 5-10-20 ranked first among fixed ladders: {rank_first}",
        "",
        "## Interpretation",
        "",
    ]
    if len(tested) == 0:
        lines.append("No eligible FES sequences were found.")
    elif len(fdr_hits) == 0:
        lines.append(
            "The 5->10->20 transition expansion did not survive the current "
            "shuffle-null and FDR controls."
        )
    else:
        lines.append(
            "Some FES sequences were closer to the 5->10->20 expansion than "
            "order-destroying nulls after FDR correction. This supports "
            "further structural-layer testing, but does not prove D12RG."
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
    results, alternatives = run_tests(args.input_root, args.n_perm, args.seed)

    result_path = args.output_dir / "IDPC_FES_transition_ladder_results.csv"
    alt_path = args.output_dir / "IDPC_FES_transition_ladder_alternatives.csv"
    summary_path = args.output_dir / "IDPC_FES_transition_ladder_summary.md"
    results.to_csv(result_path, index=False)
    alternatives.to_csv(alt_path, index=False)
    write_summary(summary_path, results, alternatives)

    print(f"wrote {result_path}")
    print(f"wrote {alt_path}")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
