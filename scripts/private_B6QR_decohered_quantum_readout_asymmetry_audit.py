#!/usr/bin/env python3
"""Private B6Q-R Decohered Quantum Readout Asymmetry Audit.

Private only. Do not publish, stage, commit, or push.

Correction from B6Q:
    The quantum-side values are not treated as direct projections of absolute
    subjectivity. They are decohered quantum operator readouts. This audit
    tests asymmetry between EEG relative readout and decohered quantum readout.

Boundary:
    This does not test direct Absolute/Relative asymmetry, conscious
    experience, AGI, or recursive self-improvement.
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
B6O_SCRIPT = SCRIPTS / "private_B6O_subjectivity_intersection_access_audit.py"

MODES = [
    "combined_c_fes_gmr72",
    "gmr72_phase_conditioned",
    "fes_string_conditioned",
    "linear_c_state",
]

ENDPOINTS = ["z_reward", "rank_reward", "gmr72_bridge_composite"]

CONTROL_KINDS = [
    "true_intersection",
    "random_intersection",
    "balanced_intersection",
    "performance_matched_intersection",
    "shuffled_c_intersection",
    "phase_rotated_intersection",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def signflip_p(diff: np.ndarray, rng: np.random.Generator, n_perm: int, alternative: str = "greater") -> tuple[float, float]:
    diff = np.asarray(diff, dtype=float)
    diff = diff[np.isfinite(diff)]
    if len(diff) < 6:
        return np.nan, np.nan
    obs = float(np.nanmean(diff))
    count = 1
    for _ in range(n_perm):
        signs = rng.choice([-1.0, 1.0], size=len(diff), replace=True)
        stat = float(np.nanmean(diff * signs))
        if alternative == "greater":
            passed = stat >= obs
        elif alternative == "two-sided":
            passed = abs(stat) >= abs(obs)
        else:
            raise ValueError(f"unknown alternative {alternative}")
        if passed:
            count += 1
    return obs, count / float(n_perm + 1)


def build_access_table(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6o = load_module("private_b6o_for_b6qr", B6O_SCRIPT)
    b6l, table = b6o.build_table(args)
    all_access = []
    all_policies = []
    for mode in MODES:
        for endpoint in ENDPOINTS:
            access, policies = b6o.run_condition(table, b6l, mode, endpoint, args)
            if not access.empty:
                all_access.append(access)
            if not policies.empty:
                all_policies.append(policies)
    access = pd.concat(all_access, ignore_index=True) if all_access else pd.DataFrame()
    policies = pd.concat(all_policies, ignore_index=True) if all_policies else pd.DataFrame()
    return access, policies


def make_asymmetry_table(access: pd.DataFrame) -> pd.DataFrame:
    key_cols = ["mode", "endpoint", "fold", "label", "idx_in_session", "state_label", "control_kind"]
    relative_to_decohered = access[access["direction"].eq("A_to_C_to_B")].set_index(key_cols)
    decohered_to_relative = access[access["direction"].eq("B_to_C_to_A")].set_index(key_cols)
    joined = relative_to_decohered[
        ["access_readout", "intersection_access_effect", "opposite_access_effect", "own_access_effect"]
    ].join(
        decohered_to_relative[
            ["access_readout", "intersection_access_effect", "opposite_access_effect", "own_access_effect"]
        ],
        how="inner",
        lsuffix="_relative_to_decohered",
        rsuffix="_decohered_to_relative",
    ).reset_index()
    out = pd.DataFrame(
        {
            "mode": joined["mode"],
            "endpoint": joined["endpoint"],
            "fold": joined["fold"],
            "label": joined["label"],
            "idx_in_session": joined["idx_in_session"],
            "state_label": joined["state_label"],
            "control_kind": joined["control_kind"],
            "relative_to_decohered_effect": joined["intersection_access_effect_relative_to_decohered"],
            "decohered_to_relative_effect": joined["intersection_access_effect_decohered_to_relative"],
            "readout_asymmetry": joined["intersection_access_effect_decohered_to_relative"] - joined["intersection_access_effect_relative_to_decohered"],
            "abs_readout_asymmetry": (
                joined["intersection_access_effect_decohered_to_relative"]
                - joined["intersection_access_effect_relative_to_decohered"]
            ).abs(),
            "relative_to_decohered_readout": joined["access_readout_relative_to_decohered"],
            "decohered_to_relative_readout": joined["access_readout_decohered_to_relative"],
            "relative_to_decohered_opposite_effect": joined["opposite_access_effect_relative_to_decohered"],
            "decohered_to_relative_opposite_effect": joined["opposite_access_effect_decohered_to_relative"],
            "relative_to_decohered_own_effect": joined["own_access_effect_relative_to_decohered"],
            "decohered_to_relative_own_effect": joined["own_access_effect_decohered_to_relative"],
        }
    )
    return out


def summarize_directions(asym: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1830)
    rows = []
    for (mode, endpoint, kind), sub in asym.groupby(["mode", "endpoint", "control_kind"], sort=False):
        vals = pd.to_numeric(sub["readout_asymmetry"], errors="coerce").to_numpy(dtype=float)
        effect, p_two = signflip_p(vals, rng, args.n_perm, alternative="two-sided")
        direction = "decohered_to_relative" if effect > 0 else "relative_to_decohered"
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "control_kind": kind,
                "mean_relative_to_decohered": float(np.nanmean(sub["relative_to_decohered_effect"])),
                "mean_decohered_to_relative": float(np.nanmean(sub["decohered_to_relative_effect"])),
                "mean_readout_asymmetry": effect,
                "mean_abs_readout_asymmetry": float(np.nanmean(sub["abs_readout_asymmetry"])),
                "p_asymmetry_two_sided": p_two,
                "dominant_direction": direction,
                "n_events": int(np.isfinite(vals).sum()),
            }
        )
    return pd.DataFrame(rows)


def compare_true_to_controls(asym: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1840)
    rows = []
    controls = [kind for kind in CONTROL_KINDS if kind != "true_intersection"]
    metrics = [
        "abs_readout_asymmetry",
        "readout_asymmetry",
        "decohered_to_relative_effect",
        "relative_to_decohered_effect",
    ]
    for (mode, endpoint), sub in asym.groupby(["mode", "endpoint"], sort=False):
        true = sub[sub["control_kind"].eq("true_intersection")].set_index(["fold", "label", "idx_in_session", "state_label"])
        for metric in metrics:
            true_vals = true[[metric]]
            for control in controls:
                comp = sub[sub["control_kind"].eq(control)].set_index(["fold", "label", "idx_in_session", "state_label"])
                joined = true_vals.join(comp[[metric]], how="inner", lsuffix="_true", rsuffix="_control")
                diff = joined[f"{metric}_true"].to_numpy(dtype=float) - joined[f"{metric}_control"].to_numpy(dtype=float)
                effect, p = signflip_p(diff, rng, args.n_perm, alternative="greater")
                rows.append(
                    {
                        "mode": mode,
                        "endpoint": endpoint,
                        "metric": metric,
                        "comparison": f"true_vs_{control}",
                        "mean_true": float(np.nanmean(joined[f"{metric}_true"])),
                        "mean_control": float(np.nanmean(joined[f"{metric}_control"])),
                        "effect": effect,
                        "p_greater": p,
                        "n_pairs": int(np.isfinite(diff).sum()),
                    }
                )
    return pd.DataFrame(rows)


def fold_stability(asym: pd.DataFrame) -> pd.DataFrame:
    true = asym[asym["control_kind"].eq("true_intersection")].copy()
    rows = []
    for (mode, endpoint), sub in true.groupby(["mode", "endpoint"], sort=False):
        fold_means = sub.groupby("fold")["readout_asymmetry"].mean()
        signs = np.sign(fold_means.to_numpy(dtype=float))
        nonzero = signs[signs != 0]
        if len(nonzero) == 0:
            rate = np.nan
            dominant = "none"
        else:
            pos = float(np.mean(nonzero > 0))
            neg = float(np.mean(nonzero < 0))
            rate = max(pos, neg)
            dominant = "decohered_to_relative" if pos >= neg else "relative_to_decohered"
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "dominant_fold_direction": dominant,
                "fold_direction_stability": rate,
                "n_folds": int(len(fold_means)),
                "fold_mean_asymmetry_min": float(np.nanmin(fold_means)),
                "fold_mean_asymmetry_max": float(np.nanmax(fold_means)),
            }
        )
    return pd.DataFrame(rows)


def summarize_conditions(direction_summary: pd.DataFrame, comparisons: pd.DataFrame, stability: pd.DataFrame) -> pd.DataFrame:
    rows = []
    true_summary = direction_summary[direction_summary["control_kind"].eq("true_intersection")].copy()
    stability_by = stability.set_index(["mode", "endpoint"]) if not stability.empty else pd.DataFrame()
    for _, row in true_summary.iterrows():
        mode = row["mode"]
        endpoint = row["endpoint"]
        comp = comparisons[
            comparisons["mode"].eq(mode)
            & comparisons["endpoint"].eq(endpoint)
            & comparisons["metric"].eq("abs_readout_asymmetry")
        ].set_index("comparison")
        pass_names = [
            "true_vs_random_intersection",
            "true_vs_balanced_intersection",
            "true_vs_performance_matched_intersection",
            "true_vs_shuffled_c_intersection",
            "true_vs_phase_rotated_intersection",
        ]
        pass_count = int(
            sum(
                name in comp.index
                and comp.loc[name, "effect"] > 0
                and comp.loc[name, "p_greater"] <= 0.05
                for name in pass_names
            )
        )
        stability_rate = np.nan
        fold_direction = "missing"
        stable = False
        if not stability_by.empty and (mode, endpoint) in stability_by.index:
            srow = stability_by.loc[(mode, endpoint)]
            stability_rate = float(srow["fold_direction_stability"])
            fold_direction = str(srow["dominant_fold_direction"])
            stable = bool(stability_rate >= 0.8)
        nonzero = bool(row["p_asymmetry_two_sided"] <= 0.05)
        minimum = bool(nonzero and pass_count >= 3)
        strong = bool(minimum and pass_count >= 4 and stable)
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "minimum_success": minimum,
                "strong_success": strong,
                "control_asymmetry_pass_count": pass_count,
                "true_asymmetry_nonzero": nonzero,
                "fold_direction_stable": stable,
                "dominant_direction": row["dominant_direction"],
                "fold_dominant_direction": fold_direction,
                "fold_direction_stability": stability_rate,
                "mean_relative_to_decohered": float(row["mean_relative_to_decohered"]),
                "mean_decohered_to_relative": float(row["mean_decohered_to_relative"]),
                "mean_readout_asymmetry": float(row["mean_readout_asymmetry"]),
                "mean_abs_readout_asymmetry": float(row["mean_abs_readout_asymmetry"]),
                "p_asymmetry_two_sided": float(row["p_asymmetry_two_sided"]),
                "effect_vs_random_abs": float(comp.loc["true_vs_random_intersection", "effect"]) if "true_vs_random_intersection" in comp.index else np.nan,
                "p_vs_random_abs": float(comp.loc["true_vs_random_intersection", "p_greater"]) if "true_vs_random_intersection" in comp.index else np.nan,
                "effect_vs_balanced_abs": float(comp.loc["true_vs_balanced_intersection", "effect"]) if "true_vs_balanced_intersection" in comp.index else np.nan,
                "p_vs_balanced_abs": float(comp.loc["true_vs_balanced_intersection", "p_greater"]) if "true_vs_balanced_intersection" in comp.index else np.nan,
                "effect_vs_shuffled_c_abs": float(comp.loc["true_vs_shuffled_c_intersection", "effect"]) if "true_vs_shuffled_c_intersection" in comp.index else np.nan,
                "p_vs_shuffled_c_abs": float(comp.loc["true_vs_shuffled_c_intersection", "p_greater"]) if "true_vs_shuffled_c_intersection" in comp.index else np.nan,
                "effect_vs_phase_rotated_abs": float(comp.loc["true_vs_phase_rotated_intersection", "effect"]) if "true_vs_phase_rotated_intersection" in comp.index else np.nan,
                "p_vs_phase_rotated_abs": float(comp.loc["true_vs_phase_rotated_intersection", "p_greater"]) if "true_vs_phase_rotated_intersection" in comp.index else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["strong_success", "minimum_success", "control_asymmetry_pass_count", "mean_abs_readout_asymmetry"],
        ascending=[False, False, False, False],
    )


def write_report(path: Path, results: pd.DataFrame, direction_summary: pd.DataFrame, comparisons: pd.DataFrame, stability: pd.DataFrame, args: argparse.Namespace) -> None:
    best = results.iloc[0] if len(results) else None
    best_label = f"{best['mode']} / {best['endpoint']}" if best is not None else "none"
    lines = [
        "# Private B6Q-R Decohered Quantum Readout Asymmetry Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Question: Is C-mediated access asymmetric between EEG relative readout and decohered quantum operator readout?",
        "",
        "Correction: This audit does not treat quantum operator results as direct Absolute Subjectivity projection. They are decohered quantum readouts.",
        "",
        "## Direction Mapping",
        "",
        "- A_to_C_to_B = EEG -> C -> decohered quantum readout = Relative -> Decohered-quantum access.",
        "- B_to_C_to_A = decohered quantum readout -> C -> EEG = Decohered-quantum -> Relative access.",
        "- readout_asymmetry = Decohered_to_Relative - Relative_to_Decohered.",
        "",
        "## Main Findings",
        "",
        f"- strongest decohered-readout asymmetry condition: {best_label}",
        f"- minimum-success conditions: {int(results['minimum_success'].sum())} / {len(results)}",
        f"- strong-success conditions: {int(results['strong_success'].sum())} / {len(results)}",
        "",
        "## Condition Results",
        "",
        results.to_csv(index=False).strip(),
        "",
        "## Direction Summary",
        "",
        direction_summary.to_csv(index=False).strip(),
        "",
        "## Control Comparisons",
        "",
        comparisons.to_csv(index=False).strip(),
        "",
        "## Fold Stability",
        "",
        stability.to_csv(index=False).strip(),
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
    access, policies = build_access_table(args)
    asym = make_asymmetry_table(access)
    direction_summary = summarize_directions(asym, args)
    comparisons = compare_true_to_controls(asym, args)
    stability = fold_stability(asym)
    results = summarize_conditions(direction_summary, comparisons, stability)

    access.to_csv(outdir / "private_B6QR_intersection_access_input.csv", index=False)
    asym.to_csv(outdir / "private_B6QR_decohered_readout_asymmetry_events.csv", index=False)
    direction_summary.to_csv(outdir / "private_B6QR_direction_summary.csv", index=False)
    comparisons.to_csv(outdir / "private_B6QR_control_comparison.csv", index=False)
    stability.to_csv(outdir / "private_B6QR_fold_stability.csv", index=False)
    results.to_csv(outdir / "private_B6QR_decohered_readout_asymmetry_results.csv", index=False)
    policies.to_csv(outdir / "private_B6QR_generated_access_policies.csv", index=False)
    write_report(outdir / "private_B6QR_decohered_quantum_readout_asymmetry_summary.md", results, direction_summary, comparisons, stability, args)
    print("\nPrivate B6Q-R decohered quantum readout asymmetry outputs")
    print(outdir)
    print(results.to_string(index=False, max_rows=80))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6qr_decohered_quantum_readout_asymmetry")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=61720)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
