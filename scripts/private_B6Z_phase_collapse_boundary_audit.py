#!/usr/bin/env python3
"""Private B6Z Phase-Collapse Boundary Audit.

Private only. Do not publish, stage, commit, or push.

Question:
    Where does C-mediated intersection access collapse under fine phase
    displacement? B6Y corrected showed many collapses at approximately 45
    degrees. This audit samples 0, 22.5, 45, 67.5, and 90 degrees to estimate
    the phase tolerance width of the C-access condition.

Boundary:
    C is fixed and not redefined. This is not a basin-expansion test. It
    estimates the collapse boundary of the C-conditioned access operation.
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
B6W_SCRIPT = SCRIPTS / "private_B6W_c_substitution_audit.py"

PHASE_SHIFTS = [0, 0.25, 0.5, 0.75, 1.0]
PHASE_DEGREES = {shift: shift * 90.0 for shift in PHASE_SHIFTS}

# C-state phase_quadrant is 4-bin in the current operational state. Half-bin
# shifts are implemented by interpolating the two adjacent discrete states.


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 2010)
    labels = np.asarray(sorted(set(map(str, labels))), dtype=object)
    rng.shuffle(labels)
    return [fold for fold in np.array_split(labels, n_folds) if len(fold)]


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


def normalize_weights(weights: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    weights = np.where(np.isfinite(weights), weights, 0.0)
    weights = np.clip(weights, 0.0, None)
    total = float(np.sum(weights))
    if total <= 1e-12:
        return np.ones(len(B6W.OPERATORS), dtype=float) / len(B6W.OPERATORS)
    return weights / total


def phase_parts(state: str) -> tuple[list[str], int | None]:
    parts = str(state).split("|")
    phase_idx = None
    for i, part in enumerate(parts):
        if part.startswith("phase="):
            phase_idx = i
            break
    return parts, phase_idx


def parse_phase_value(value: str) -> tuple[int | None, str]:
    value = str(value)
    if value.startswith("q"):
        try:
            return int(value[1:]) - 1, "q"
        except ValueError:
            return None, "q"
    try:
        return int(value), "int"
    except ValueError:
        return None, "unknown"


def format_phase_value(index: int, style: str) -> str:
    index = int(index) % 4
    if style == "q":
        return f"q{index + 1}"
    return str(index)


def rotate_phase_state(state: str, shift: int) -> str:
    parts, phase_idx = phase_parts(state)
    if phase_idx is None:
        return state
    key, value = parts[phase_idx].split("=", 1)
    parsed, style = parse_phase_value(value)
    if parsed is None:
        return state
    rotated = (parsed + int(shift)) % 4
    parts[phase_idx] = f"{key}={format_phase_value(rotated, style)}"
    return "|".join(parts)


def shifted_weights(state: str, shift: float, info: dict) -> np.ndarray:
    if float(shift).is_integer():
        target = rotate_phase_state(state, int(shift))
        return normalize_weights(info["true"].get(target, info["global"]))
    lower = int(np.floor(shift))
    upper = int(np.ceil(shift))
    frac = float(shift) - lower
    low_state = rotate_phase_state(state, lower)
    high_state = rotate_phase_state(state, upper)
    low = normalize_weights(info["true"].get(low_state, info["global"]))
    high = normalize_weights(info["true"].get(high_state, info["global"]))
    return normalize_weights((1.0 - frac) * low + frac * high)


def build_base(args: argparse.Namespace):
    global B6W
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    B6W = load_module("private_b6w_for_b6z", B6W_SCRIPT)
    b6p, b6l, table = B6W.build_base(args)
    return B6W, b6p, b6l, table


def build_basin_access(table: pd.DataFrame, b6w, b6p, b6l, mode: str, endpoint: str, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 2020)
    data = table.copy()
    data["b6p_state_label"] = b6l.state_labels(data, mode)
    folds = make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy().reset_index(drop=True)
        info = b6w.train_info(train, b6p, b6l, mode, endpoint, args, rng)
        for _, row in test.iterrows():
            state = str(row["b6p_state_label"])
            base = b6p.baseline_readouts(row, b6l, endpoint)
            for direction in ["A_to_C_to_B", "B_to_C_to_A"]:
                for shift in PHASE_SHIFTS:
                    weights = shifted_weights(state, shift, info)
                    weights = b6w.masked_weights(weights, direction)
                    access = b6p.weighted_reward(row, b6l, weights, endpoint)
                    rows.append(
                        {
                            "mode": mode,
                            "endpoint": endpoint,
                            "fold": fold_index,
                            "label": row["label"],
                            "idx_in_session": row["idx_in_session"],
                            "direction": direction,
                            "true_state_label": state,
                            "phase_shift_bins": shift,
                            "phase_shift_degrees": PHASE_DEGREES[shift],
                            "access_readout": access,
                            "baseline_max": base["baseline_max"],
                            "access_effect": access - base["baseline_max"] if np.isfinite(access) and np.isfinite(base["baseline_max"]) else np.nan,
                        }
                    )
    return pd.DataFrame(rows)


def compare_to_true(access: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 2030)
    rows = []
    index_cols = ["fold", "label", "idx_in_session", "direction", "true_state_label"]
    for (mode, endpoint, direction), sub in access.groupby(["mode", "endpoint", "direction"], sort=False):
        true = sub[sub["phase_shift_bins"].eq(0)].set_index(index_cols)
        for shift in [s for s in PHASE_SHIFTS if s != 0]:
            comp = sub[sub["phase_shift_bins"].eq(shift)].set_index(index_cols)
            joined = true[["access_effect"]].join(comp[["access_effect"]], how="inner", lsuffix="_true", rsuffix="_shift")
            diff = joined["access_effect_true"].to_numpy(dtype=float) - joined["access_effect_shift"].to_numpy(dtype=float)
            effect, p = signflip_p(diff, rng, args.n_perm)
            rows.append(
                {
                    "mode": mode,
                    "endpoint": endpoint,
                    "direction": direction,
                    "phase_shift_bins": shift,
                    "phase_shift_degrees": PHASE_DEGREES[shift],
                    "mean_true": float(np.nanmean(joined["access_effect_true"])),
                    "mean_shifted": float(np.nanmean(joined["access_effect_shift"])),
                    "effect_true_minus_shifted": effect,
                    "p_true_greater": p,
                    "n_pairs": int(np.isfinite(diff).sum()),
                    "shift_significantly_worse": bool(np.isfinite(effect) and effect > 0 and np.isfinite(p) and p <= 0.05),
                }
            )
    return pd.DataFrame(rows)


def shift_profile(access: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, sub in access.groupby(["mode", "endpoint", "direction", "phase_shift_bins", "phase_shift_degrees"], sort=False):
        rows.append(
            {
                "mode": keys[0],
                "endpoint": keys[1],
                "direction": keys[2],
                "phase_shift_bins": keys[3],
                "phase_shift_degrees": keys[4],
                "mean_access_effect": float(np.nanmean(sub["access_effect"])),
                "median_access_effect": float(np.nanmedian(sub["access_effect"])),
                "n_events": int(sub["access_effect"].notna().sum()),
            }
        )
    return pd.DataFrame(rows)


def summarize_basin(profile: pd.DataFrame, comps: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (mode, endpoint, direction), prof in profile.groupby(["mode", "endpoint", "direction"], sort=False):
        prof = prof.sort_values("phase_shift_bins")
        true_mean = float(prof[prof["phase_shift_bins"].eq(0)]["mean_access_effect"].iloc[0])
        comp = comps[
            comps["mode"].eq(mode)
            & comps["endpoint"].eq(endpoint)
            & comps["direction"].eq(direction)
        ]
        tolerated = comp[~comp["shift_significantly_worse"]].copy()
        collapse = comp[comp["shift_significantly_worse"]].copy()
        tolerance_width_bins = float(tolerated["phase_shift_bins"].max()) if not tolerated.empty else 0.0
        first_collapse_bins = float(collapse["phase_shift_bins"].min()) if not collapse.empty else np.nan
        profile_after_zero = prof[prof["phase_shift_bins"].gt(0)].copy()
        if len(profile_after_zero) >= 2:
            x = profile_after_zero["phase_shift_bins"].to_numpy(dtype=float)
            y = profile_after_zero["mean_access_effect"].to_numpy(dtype=float)
            finite = np.isfinite(x) & np.isfinite(y)
            local_slope = float(np.polyfit(x[finite], y[finite], 1)[0]) if finite.sum() >= 2 else np.nan
        else:
            local_slope = np.nan
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "direction": direction,
                "true_mean_access_effect": true_mean,
                "tolerance_width_bins": tolerance_width_bins,
                "tolerance_width_degrees": tolerance_width_bins * 90.0,
                "first_significant_collapse_bins": first_collapse_bins,
                "first_significant_collapse_degrees": first_collapse_bins * 90.0 if np.isfinite(first_collapse_bins) else np.nan,
                "n_tolerated_shifts": int(len(tolerated)),
                "n_collapsed_shifts": int(len(collapse)),
                "mean_true_minus_shift": float(np.nanmean(comp["effect_true_minus_shifted"])),
                "collapse_slope_per_bin": local_slope,
                "phase_collapse_detected": bool(len(collapse) >= 1),
                "narrow_boundary_supported": bool(np.isfinite(first_collapse_bins) and first_collapse_bins <= 0.5),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["narrow_boundary_supported", "phase_collapse_detected", "first_significant_collapse_bins", "true_mean_access_effect"],
        ascending=[False, False, True, False],
    )


def write_report(path: Path, summary: pd.DataFrame, profile: pd.DataFrame, comps: pd.DataFrame, args: argparse.Namespace) -> None:
    lines = [
        "# Private B6Z Phase-Collapse Boundary Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Question: Where does C-mediated intersection access collapse under fine phase displacement?",
        "",
        "Boundary: C is fixed and not redefined. This estimates tolerance of the C-conditioned access operation under systematic phase displacement.",
        "",
        "## Main Findings",
        "",
        f"- phase-collapse detected conditions: {int(summary['phase_collapse_detected'].sum())} / {len(summary)}",
        f"- mean tolerance width degrees: {float(np.nanmean(summary['tolerance_width_degrees'])):.3f}",
        f"- narrow boundary conditions <=45deg: {int(summary['narrow_boundary_supported'].sum())} / {len(summary)}",
        f"- median first collapse degrees: {float(np.nanmedian(summary['first_significant_collapse_degrees'])):.3f}",
        "",
        "## Basin Summary",
        "",
        summary.to_csv(index=False).strip(),
        "",
        "## Shift Profile",
        "",
        profile.to_csv(index=False).strip(),
        "",
        "## True-vs-Shift Comparisons",
        "",
        comps.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- phase_shifts_bins: {PHASE_SHIFTS}",
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
    b6w, b6p, b6l, table = build_base(args)
    table.to_csv(outdir / "private_B6Z_state_table.csv", index=False)
    frames = []
    for mode in b6p.MODES:
        for endpoint in b6p.ENDPOINTS:
            access = build_basin_access(table, b6w, b6p, b6l, mode, endpoint, args)
            if not access.empty:
                frames.append(access)
    access = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    profile = shift_profile(access)
    comps = compare_to_true(access, args)
    summary = summarize_basin(profile, comps)

    access.to_csv(outdir / "private_B6Z_phase_collapse_boundary_access_events.csv", index=False)
    profile.to_csv(outdir / "private_B6Z_phase_shift_profile.csv", index=False)
    comps.to_csv(outdir / "private_B6Z_true_vs_shift_comparison.csv", index=False)
    summary.to_csv(outdir / "private_B6Z_phase_collapse_boundary_summary.csv", index=False)
    write_report(outdir / "private_B6Z_phase_collapse_boundary_summary.md", summary, profile, comps, args)

    print("\nPrivate B6Z phase-collapse boundary outputs")
    print(outdir)
    print(summary.to_string(index=False, max_rows=80))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6z_phase_collapse_boundary")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=62020)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
