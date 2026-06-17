#!/usr/bin/env python3
"""Private B6U Objectification Failure Audit.

Private only. Do not publish, stage, commit, or push.

Question:
    Why does intersection access survive while objectification fails? More
    specifically, when object-scoring of the same generated C-state operators is
    made progressively richer, does the object arm remain unstable while the
    intersection-access arm remains supported?

Boundary:
    This does not observe subjectivity as an object. It tests whether attempts
    to objectify the generated C-state operator profile fail to recover the
    robust effect that appears only through intersection access.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
SCRIPTS = REPO / "scripts"
B6P_SCRIPT = SCRIPTS / "private_B6P_objectification_vs_intersection_audit.py"

OBJECT_CONTROLS = ["random", "balanced", "performance_matched", "shuffled_c", "phase_rotated"]
CORE_OBJECT_CONTROLS = ["balanced", "shuffled_c", "phase_rotated"]
CORE_INTERSECTION_CONTROLS = ["balanced", "shuffled_c", "phase_rotated"]

OBJECTIFICATION_LEVELS = {
    "L1_novelty_only": ["z_novelty"],
    "L2_novelty_selected_distance": ["z_novelty", "z_distance_to_selected"],
    "L3_add_entropy_noncollapse": ["z_novelty", "z_distance_to_selected", "z_entropy", "z_non_collapse"],
    "L4_add_coherence": ["z_novelty", "z_distance_to_selected", "z_entropy", "z_non_collapse", "z_coherence"],
    "L5_full_objectification": [
        "z_novelty",
        "z_distance_to_selected",
        "z_entropy",
        "z_non_collapse",
        "z_coherence",
        "z_state_specificity",
    ],
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def signflip_p(diff: np.ndarray, rng: np.random.Generator, n_perm: int) -> tuple[float, float]:
    diff = np.asarray(diff, dtype=float)
    diff = diff[np.isfinite(diff)]
    if len(diff) < 6:
        return np.nan, np.nan
    obs = float(np.nanmean(diff))
    count = 1
    for _ in range(n_perm):
        signs = rng.choice([-1.0, 1.0], size=len(diff), replace=True)
        if float(np.nanmean(diff * signs)) >= obs:
            count += 1
    return obs, count / float(n_perm + 1)


def zscore(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    out = np.full(len(values), np.nan, dtype=float)
    mask = np.isfinite(values)
    if mask.sum() < 3:
        return out
    mu = float(np.nanmean(values[mask]))
    sd = float(np.nanstd(values[mask]))
    if not np.isfinite(sd) or sd <= 1e-12:
        out[mask] = 0.0
    else:
        out[mask] = (values[mask] - mu) / sd
    return out


def build_base(args: argparse.Namespace):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6p = load_module("private_b6p_for_b6u", B6P_SCRIPT)
    b6l, table = b6p.build_table(args)
    return b6p, b6l, table


def add_objectification_levels(object_df: pd.DataFrame) -> pd.DataFrame:
    out = object_df.copy()
    for level, cols in OBJECTIFICATION_LEVELS.items():
        out[level] = out[cols].sum(axis=1, skipna=False)
        for (mode, endpoint), idx in out.groupby(["mode", "endpoint"]).groups.items():
            idx = list(idx)
            out.loc[idx, f"z_{level}"] = zscore(out.loc[idx, level].to_numpy(dtype=float))
    return out


def compare_object_levels(object_df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1710)
    rows = []
    for (mode, endpoint), sub in object_df.groupby(["mode", "endpoint"], sort=False):
        for level in OBJECTIFICATION_LEVELS:
            score_col = f"z_{level}"
            true = sub[sub["arm_kind"].eq("true")].set_index(["fold", "state_label"])
            for control in OBJECT_CONTROLS:
                comp = sub[sub["arm_kind"].eq(control)].set_index(["fold", "state_label"])
                joined = true[[score_col]].join(comp[[score_col]], how="inner", lsuffix="_true", rsuffix="_control")
                diff = joined[f"{score_col}_true"].to_numpy(dtype=float) - joined[f"{score_col}_control"].to_numpy(dtype=float)
                effect, p = signflip_p(diff, rng, args.n_perm)
                rows.append(
                    {
                        "mode": mode,
                        "endpoint": endpoint,
                        "objectification_level": level,
                        "comparison": f"true_vs_{control}",
                        "control_kind": control,
                        "mean_true": float(np.nanmean(joined[f"{score_col}_true"])),
                        "mean_control": float(np.nanmean(joined[f"{score_col}_control"])),
                        "effect": effect,
                        "p_greater": p,
                        "n_pairs": int(np.isfinite(diff).sum()),
                        "passes": bool(np.isfinite(effect) and effect > 0 and np.isfinite(p) and p <= 0.05),
                    }
                )
    return pd.DataFrame(rows)


def compare_intersection(intersection_df: pd.DataFrame, b6p, args: argparse.Namespace) -> pd.DataFrame:
    # Use the B6P comparison to preserve exactly the same access operation.
    return b6p.compare_intersection(intersection_df, args)


def summarize_object_levels(object_comp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (mode, endpoint, level), sub in object_comp.groupby(["mode", "endpoint", "objectification_level"], sort=False):
        core = sub[sub["control_kind"].isin(CORE_OBJECT_CONTROLS)]
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "objectification_level": level,
                "object_pass_count": int(sub["passes"].sum()),
                "object_core_pass_count": int(core["passes"].sum()),
                "object_fails_core": bool(int(core["passes"].sum()) <= 1),
                "object_collapses_against_balanced": bool(
                    sub[sub["control_kind"].eq("balanced")]["passes"].sum() == 0
                ),
                "object_collapses_against_phase_rotated": bool(
                    sub[sub["control_kind"].eq("phase_rotated")]["passes"].sum() == 0
                ),
                "mean_object_effect": float(np.nanmean(sub["effect"])),
                "mean_core_object_effect": float(np.nanmean(core["effect"])),
                "mean_true_object_score": float(np.nanmean(sub["mean_true"])),
            }
        )
    return pd.DataFrame(rows)


def summarize_intersection(intersection_comp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (mode, endpoint, direction), sub in intersection_comp.groupby(["mode", "endpoint", "direction"], sort=False):
        sub = sub.copy()
        sub["control_kind"] = sub["comparison"].str.replace("true_vs_", "", regex=False)
        core = sub[sub["control_kind"].isin(CORE_INTERSECTION_CONTROLS)]
        passes = (sub["effect"].gt(0) & sub["p_greater"].le(0.05))
        core_passes = (core["effect"].gt(0) & core["p_greater"].le(0.05))
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "direction": direction,
                "intersection_pass_count": int(passes.sum()),
                "intersection_core_pass_count": int(core_passes.sum()),
                "intersection_survives": bool(int(core_passes.sum()) >= 2 and int(passes.sum()) >= 4),
                "mean_intersection_effect": float(np.nanmean(sub["effect"])),
                "mean_core_intersection_effect": float(np.nanmean(core["effect"])),
                "mean_true_intersection_effect": float(np.nanmean(sub["mean_true"])),
            }
        )
    return pd.DataFrame(rows)


def pressure_summary(object_level_summary: pd.DataFrame, intersection_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    level_order = list(OBJECTIFICATION_LEVELS.keys())
    for (mode, endpoint), obj in object_level_summary.groupby(["mode", "endpoint"], sort=False):
        obj = obj.set_index("objectification_level").reindex(level_order).reset_index()
        x = np.arange(len(obj), dtype=float)
        y = obj["mean_core_object_effect"].to_numpy(dtype=float)
        if np.isfinite(y).sum() >= 2:
            slope = float(np.polyfit(x[np.isfinite(y)], y[np.isfinite(y)], 1)[0])
        else:
            slope = np.nan
        final = obj[obj["objectification_level"].eq("L5_full_objectification")].iloc[0]
        for _, inter in intersection_summary[
            intersection_summary["mode"].eq(mode) & intersection_summary["endpoint"].eq(endpoint)
        ].iterrows():
            object_failure = bool(final["object_fails_core"] and final["object_collapses_against_balanced"] and final["object_collapses_against_phase_rotated"])
            survives = bool(inter["intersection_survives"])
            rows.append(
                {
                    "mode": mode,
                    "endpoint": endpoint,
                    "direction": inter["direction"],
                    "final_object_core_pass_count": int(final["object_core_pass_count"]),
                    "max_object_core_pass_count": int(obj["object_core_pass_count"].max()),
                    "object_pressure_slope": slope,
                    "objectification_failure": object_failure,
                    "intersection_survives": survives,
                    "object_failure_with_intersection_survival": bool(object_failure and survives),
                    "intersection_core_pass_count": int(inter["intersection_core_pass_count"]),
                    "intersection_pass_count": int(inter["intersection_pass_count"]),
                    "mean_final_object_core_effect": float(final["mean_core_object_effect"]),
                    "mean_intersection_core_effect": float(inter["mean_core_intersection_effect"]),
                    "object_intersection_effect_gap": float(inter["mean_core_intersection_effect"] - final["mean_core_object_effect"]),
                    "mean_true_intersection_effect": float(inter["mean_true_intersection_effect"]),
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["object_failure_with_intersection_survival", "object_intersection_effect_gap", "intersection_core_pass_count"],
        ascending=[False, False, False],
    )


def write_report(path: Path, pressure: pd.DataFrame, object_levels: pd.DataFrame, intersection: pd.DataFrame, object_comp: pd.DataFrame, intersection_comp: pd.DataFrame, args: argparse.Namespace) -> None:
    lines = [
        "# Private B6U Objectification Failure Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Question: Why does intersection access survive while objectification fails?",
        "",
        "Interpretation boundary: this does not observe subjectivity as an object. It tests whether progressively richer objectification remains weaker than access-by-intersection.",
        "",
        "## Objectification Levels",
        "",
        "- L1_novelty_only: novelty from nearest primitive.",
        "- L2_novelty_selected_distance: novelty plus distance from best selected operator.",
        "- L3_add_entropy_noncollapse: adds entropy and non-collapse.",
        "- L4_add_coherence: adds within-state coherence.",
        "- L5_full_objectification: adds state specificity, matching the full object-score pressure.",
        "",
        "## Main Findings",
        "",
        f"- object failure with intersection survival: {int(pressure['object_failure_with_intersection_survival'].sum())} / {len(pressure)} direction conditions",
        f"- final objectification failure conditions: {int(pressure['objectification_failure'].sum())} / {len(pressure)} direction conditions",
        f"- intersection survival conditions: {int(pressure['intersection_survives'].sum())} / {len(pressure)} direction conditions",
        "",
        "## Pressure Summary",
        "",
        pressure.to_csv(index=False).strip(),
        "",
        "## Object Level Summary",
        "",
        object_levels.to_csv(index=False).strip(),
        "",
        "## Intersection Summary",
        "",
        intersection.to_csv(index=False).strip(),
        "",
        "## Object Control Comparisons",
        "",
        object_comp.to_csv(index=False).strip(),
        "",
        "## Intersection Control Comparisons",
        "",
        intersection_comp.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- n_folds: {args.n_folds}",
        f"- min_state_events: {args.min_state_events}",
        f"- temperature: {args.temperature}",
        f"- n_perm: {args.n_perm}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    b6p, b6l, table = build_base(args)
    table.to_csv(outdir / "private_B6U_state_table.csv", index=False)

    object_frames = []
    intersection_frames = []
    policy_frames = []
    for mode in b6p.MODES:
        for endpoint in b6p.ENDPOINTS:
            obj, inter, policies = b6p.build_arms(table, b6l, mode, endpoint, args)
            if not obj.empty:
                object_frames.append(obj)
            if not inter.empty:
                intersection_frames.append(inter)
            if not policies.empty:
                policy_frames.append(policies)

    object_df = pd.concat(object_frames, ignore_index=True) if object_frames else pd.DataFrame()
    intersection_df = pd.concat(intersection_frames, ignore_index=True) if intersection_frames else pd.DataFrame()
    policies = pd.concat(policy_frames, ignore_index=True) if policy_frames else pd.DataFrame()
    object_df = add_objectification_levels(object_df)

    object_comp = compare_object_levels(object_df, args)
    intersection_comp = compare_intersection(intersection_df, b6p, args)
    object_levels = summarize_object_levels(object_comp)
    intersection = summarize_intersection(intersection_comp)
    pressure = pressure_summary(object_levels, intersection)

    object_df.to_csv(outdir / "private_B6U_objectification_level_scores.csv", index=False)
    intersection_df.to_csv(outdir / "private_B6U_intersection_arm_effects.csv", index=False)
    object_comp.to_csv(outdir / "private_B6U_object_level_control_comparison.csv", index=False)
    intersection_comp.to_csv(outdir / "private_B6U_intersection_control_comparison.csv", index=False)
    object_levels.to_csv(outdir / "private_B6U_object_level_summary.csv", index=False)
    intersection.to_csv(outdir / "private_B6U_intersection_summary.csv", index=False)
    pressure.to_csv(outdir / "private_B6U_objectification_pressure_summary.csv", index=False)
    policies.to_csv(outdir / "private_B6U_generated_policies.csv", index=False)
    write_report(outdir / "private_B6U_objectification_failure_summary.md", pressure, object_levels, intersection, object_comp, intersection_comp, args)

    print("\nPrivate B6U objectification failure outputs")
    print(outdir)
    print(pressure.to_string(index=False, max_rows=80))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6u_objectification_failure")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=61720)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
