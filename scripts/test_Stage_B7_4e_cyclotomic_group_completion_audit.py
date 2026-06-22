#!/usr/bin/env python3
"""Stage B7.4e cyclotomic / finite-group-algebra pre-audit of survivor indices."""

from __future__ import annotations

import argparse
import itertools
import math
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
REGISTERED_SURVIVORS = {"P10", "P5", "P21", "P15"}
MARKER_COLUMNS = [
    "cyclotomic_recognized_marker",
    "x3_interaction_marker",
    "complement_direction_marker",
    "full_mod12_generator",
    "high_order_mod24_generator",
    "group_completion_proxy",
    "any_arithmetic_marker",
]


def prime_factors(n: int) -> list[int]:
    out: list[int] = []
    d = 2
    value = int(n)
    while d * d <= value:
        while value % d == 0:
            out.append(d)
            value //= d
        d += 1
    if value > 1:
        out.append(value)
    return out


def additive_order(n: int, mod: int) -> int:
    residue = n % mod
    if residue == 0:
        return 1
    return mod // math.gcd(residue, mod)


def parse_fold_index(label: str) -> int:
    if not str(label).startswith("P"):
        raise ValueError(f"Expected P-index label, got {label!r}")
    return int(str(label)[1:])


def build_index_features(table: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in table.itertuples(index=False):
        label = str(row.heldout_label)
        n = parse_fold_index(label)
        factors = prime_factors(n)
        mod12 = n % 12
        mod24 = n % 24
        complement_to_12 = (12 - mod12) % 12
        order12 = additive_order(n, 12)
        order24 = additive_order(n, 24)
        has_5 = 5 in factors
        has_7 = 7 in factors
        has_3 = 3 in factors
        cyclotomic = n in {5, 10}
        x3 = n in {15, 21}
        complement_direction = (mod12 == 5) or (has_7 and ((12 - 7) == 5)) or (has_5 and has_3)
        full_mod12 = order12 == 12
        high_order24 = order24 >= 12
        group_completion = full_mod12 or high_order24 or (has_3 and (has_5 or has_7))
        rows.append({
            "heldout_label": label,
            "fold_index": n,
            "mod12_position": mod12,
            "mod12_complement_to_12": complement_to_12,
            "mod24_position": mod24,
            "prime_factors": "x".join(str(x) for x in factors) if factors else "1",
            "has_factor_3": has_3,
            "has_factor_5": has_5,
            "has_factor_7": has_7,
            "additive_order_mod12": order12,
            "additive_order_mod24": order24,
            "cyclotomic_recognized_marker": cyclotomic,
            "x3_interaction_marker": x3,
            "complement_direction_marker": complement_direction,
            "full_mod12_generator": full_mod12,
            "high_order_mod24_generator": high_order24,
            "group_completion_proxy": group_completion,
            "any_arithmetic_marker": cyclotomic or x3 or complement_direction or group_completion,
        })
    return pd.DataFrame(rows)


def summarize_groups(merged: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group, sub in merged.groupby("survival_group", sort=False):
        row = {
            "survival_group": group,
            "n_folds": int(len(sub)),
            "mean_c12": float(pd.to_numeric(sub["c12_mean"], errors="coerce").mean()),
            "mean_positive_specificity_controls": float(pd.to_numeric(sub["n_positive_specificity_controls"], errors="coerce").mean()),
            "mean_min_specificity_margin": float(pd.to_numeric(sub["min_specificity_margin"], errors="coerce").mean()),
        }
        for col in MARKER_COLUMNS:
            row[f"rate_{col}"] = float(pd.to_numeric(sub[col], errors="coerce").mean())
        rows.append(row)
    return pd.DataFrame(rows)


def exact_subset_enrichment(merged: pd.DataFrame) -> pd.DataFrame:
    labels = merged["heldout_label"].astype(str).tolist()
    survivor_labels = set(REGISTERED_SURVIVORS)
    observed_mask = [label in survivor_labels for label in labels]
    rows = []
    for col in MARKER_COLUMNS:
        values = pd.to_numeric(merged[col], errors="coerce").fillna(0).astype(float).to_numpy()
        observed = float(values[observed_mask].mean())
        null_means = []
        for combo in itertools.combinations(range(len(values)), len(survivor_labels)):
            null_means.append(float(values[list(combo)].mean()))
        null = np.asarray(null_means, dtype=float)
        rows.append({
            "marker": col,
            "observed_survivor_rate": observed,
            "all_fold_rate": float(values.mean()),
            "exact_subset_p_ge_observed": float(np.mean(null >= observed)),
            "null_mean": float(null.mean()),
            "null_sd": float(null.std()),
            "n_exact_subsets": int(len(null)),
        })
    return pd.DataFrame(rows)


def write_summary(path: Path, merged: pd.DataFrame, group_summary: pd.DataFrame, enrichment: pd.DataFrame, args: argparse.Namespace) -> None:
    survivor_rows = merged[merged["heldout_label"].isin(REGISTERED_SURVIVORS)].copy()
    marker_view_cols = [
        "heldout_label",
        "fold_index",
        "mod12_position",
        "mod12_complement_to_12",
        "mod24_position",
        "prime_factors",
        "cyclotomic_recognized_marker",
        "x3_interaction_marker",
        "complement_direction_marker",
        "group_completion_proxy",
        "any_arithmetic_marker",
        "c12_mean",
        "n_positive_specificity_controls",
        "min_specificity_margin",
    ]
    lines = [
        "# Stage B7.4e Cyclotomic / Finite-Group-Algebra Pre-Audit",
        "",
        "Status: executed after `Stage_B7_4e_preregistration_email_sent.md`.",
        "",
        "## Registered Question",
        "",
        "Are P10/P5/P21/P15 compatible with cyclotomic or finite-group-algebra completion structure around C12?",
        "",
        "This is a pre-audit. It is not a proof of finite group algebra, paired Phi12 quadrature, or a Jacobi 12-product mechanism.",
        "",
        "## Registered Survivors With Frozen Arithmetic Markers",
        "",
        survivor_rows[marker_view_cols].sort_values("fold_index").to_csv(index=False).strip(),
        "",
        "## Group Marker Summary",
        "",
        group_summary.to_csv(index=False).strip(),
        "",
        "## Exact Four-Fold Subset Enrichment",
        "",
        enrichment.to_csv(index=False).strip(),
        "",
        "## Interpretation Guardrail",
        "",
        "- Enrichment supports only a sharper next hypothesis: C12 survival may be tied to arithmetic completion structure around the Jacobi 12-product.",
        "- Lack of enrichment would leave the finite-group-algebra intuition mathematically interesting but unsupported by present fold-index evidence.",
        "- B7.4e makes no paired Phi12 quadrature claim and no finite-group-algebra proof claim.",
        "",
        "## Settings",
        "",
        f"- registered_survivors: {sorted(REGISTERED_SURVIVORS)}",
        f"- b74d_profiles: {args.b74d_profiles}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    profiles = pd.read_csv(args.b74d_profiles)
    index_features = build_index_features(profiles)
    merged = profiles.merge(index_features, on="heldout_label", how="left")
    group_summary = summarize_groups(merged)
    enrichment = exact_subset_enrichment(merged)

    index_features.to_csv(outdir / "Stage_B7_4e_index_arithmetic_features.csv", index=False)
    merged.to_csv(outdir / "Stage_B7_4e_fold_index_readout_join.csv", index=False)
    group_summary.to_csv(outdir / "Stage_B7_4e_group_marker_summary.csv", index=False)
    enrichment.to_csv(outdir / "Stage_B7_4e_exact_subset_enrichment.csv", index=False)
    write_summary(outdir / "Stage_B7_4e_execution_summary.md", merged, group_summary, enrichment, args)

    print(f"output_dir: {outdir}")
    print("\nGroup marker summary")
    print(group_summary.to_string(index=False))
    print("\nExact four-fold subset enrichment")
    print(enrichment.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_4e")
    parser.add_argument("--b74d-profiles", type=Path, default=REPO / "reports/stage_b7_4d/Stage_B7_4d_fold_condition_profiles.csv")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
