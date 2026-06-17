#!/usr/bin/env python3
"""Private B6W C Substitution Audit.

Private only. Do not publish, stage, commit, or push.

Question:
    Is the surviving intersection-access effect specific to the true C-state,
    or can any C-like substitute reproduce it?

Boundary:
    C is fixed and not redefined. This audit keeps the A->C->B / B->C->A
    access operation intact, but substitutes the C-state used to condition the
    access policy. A positive result supports non-substitutability of C within
    supported regimes, not existence of C as an object.
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

OPERATORS = [
    "O1_lag0_AB",
    "O2_lag5_AB",
    "O3_A_C_boundary",
    "O4_B_C_boundary",
    "O5_full_TFC",
    "O6_phase_only",
    "O7_suppress_event",
]

FAKE_C_KINDS = [
    "shuffled_c",
    "phase_rotated_c",
    "random_c",
    "balanced_c",
    "foreign_label_c",
]

A_TO_B_MASK = {
    "O1_lag0_AB": 0.20,
    "O2_lag5_AB": 0.80,
    "O3_A_C_boundary": 0.10,
    "O4_B_C_boundary": 1.00,
    "O5_full_TFC": 0.65,
    "O6_phase_only": 0.35,
    "O7_suppress_event": 0.05,
}

B_TO_A_MASK = {
    "O1_lag0_AB": 0.80,
    "O2_lag5_AB": 0.35,
    "O3_A_C_boundary": 1.00,
    "O4_B_C_boundary": 0.10,
    "O5_full_TFC": 0.65,
    "O6_phase_only": 0.35,
    "O7_suppress_event": 0.05,
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 1910)
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
        return np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    return weights / total


def rotate_weights(weights: np.ndarray, shift: int = 1) -> np.ndarray:
    out = np.asarray(weights, dtype=float).copy()
    out[:5] = np.roll(out[:5], shift)
    return normalize_weights(out)


def masked_weights(weights: np.ndarray, direction: str) -> np.ndarray:
    mask_dict = A_TO_B_MASK if direction == "A_to_C_to_B" else B_TO_A_MASK
    mask = np.asarray([mask_dict[op] for op in OPERATORS], dtype=float)
    return normalize_weights(normalize_weights(weights) * mask)


def rotate_phase_in_state(state: str) -> str:
    parts = []
    changed = False
    for part in str(state).split("|"):
        if part.startswith("phase="):
            key, value = part.split("=", 1)
            if str(value).startswith("q"):
                try:
                    idx = (int(str(value)[1:]) - 1 + 1) % 4
                    parts.append(f"{key}=q{idx + 1}")
                    changed = True
                except ValueError:
                    parts.append(part)
            else:
                try:
                    parts.append(f"{key}={(int(value) + 1) % 4}")
                    changed = True
                except ValueError:
                    parts.append(part)
        else:
            parts.append(part)
    return "|".join(parts) if changed else state


def build_base(args: argparse.Namespace):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6p = load_module("private_b6p_for_b6w", B6P_SCRIPT)
    b6l, table = b6p.build_table(args)
    return b6p, b6l, table


def train_info(train: pd.DataFrame, b6p, b6l, mode: str, endpoint: str, args: argparse.Namespace, rng: np.random.Generator) -> dict:
    data = train.copy()
    data["b6p_state_label"] = b6l.state_labels(data, mode)
    info = b6p.train_generators(data, b6l, mode, endpoint, args, rng)
    info["true"] = {k: normalize_weights(v) for k, v in info["true"].items()}
    info["global"] = normalize_weights(info["global"])
    return info


def fake_state(kind: str, row_index: int, state: str, test: pd.DataFrame, all_states: list[str], rng: np.random.Generator) -> str | None:
    if kind == "shuffled_c":
        return str(test.loc[row_index, "shuffled_c_state"])
    if kind == "phase_rotated_c":
        return rotate_phase_in_state(state)
    if kind == "random_c":
        return str(rng.choice(all_states)) if all_states else state
    if kind == "balanced_c":
        return None
    if kind == "foreign_label_c":
        current_label = str(test.loc[row_index, "label"])
        foreign = test[test["label"].astype(str).ne(current_label)]
        if foreign.empty:
            return str(rng.choice(all_states)) if all_states else state
        return str(foreign.iloc[int(rng.integers(0, len(foreign)))]["b6p_state_label"])
    raise ValueError(f"unknown fake C kind {kind}")


def weights_for_c(kind: str, state: str, info: dict) -> np.ndarray:
    if kind == "true_c":
        return info["true"].get(state, info["global"])
    if kind == "balanced_c":
        return np.ones(len(OPERATORS), dtype=float) / len(OPERATORS)
    return info["true"].get(state, info["global"])


def build_substitution_access(table: pd.DataFrame, b6p, b6l, mode: str, endpoint: str, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1920)
    data = table.copy()
    data["b6p_state_label"] = b6l.state_labels(data, mode)
    folds = make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy().reset_index(drop=True)
        info = train_info(train, b6p, b6l, mode, endpoint, args, rng)
        all_states = sorted(set(test["b6p_state_label"].astype(str)).union(info["true"].keys()))
        shuffled_states = test["b6p_state_label"].astype(str).to_numpy(copy=True)
        rng.shuffle(shuffled_states)
        test["shuffled_c_state"] = shuffled_states
        for row_index, row in test.iterrows():
            true_state = str(row["b6p_state_label"])
            base = b6p.baseline_readouts(row, b6l, endpoint)
            for direction in ["A_to_C_to_B", "B_to_C_to_A"]:
                for c_kind in ["true_c", *FAKE_C_KINDS]:
                    if c_kind == "true_c":
                        used_state = true_state
                    else:
                        used_state = fake_state(c_kind, row_index, true_state, test, all_states, rng)
                    weights = weights_for_c(c_kind, used_state if used_state is not None else true_state, info)
                    weights = masked_weights(weights, direction)
                    access = b6p.weighted_reward(row, b6l, weights, endpoint)
                    rows.append(
                        {
                            "mode": mode,
                            "endpoint": endpoint,
                            "fold": fold_index,
                            "label": row["label"],
                            "idx_in_session": row["idx_in_session"],
                            "direction": direction,
                            "c_kind": c_kind,
                            "true_state_label": true_state,
                            "used_state_label": used_state if used_state is not None else "BALANCED_C_NO_STATE",
                            "access_readout": access,
                            "baseline_max": base["baseline_max"],
                            "access_effect": access - base["baseline_max"] if np.isfinite(access) and np.isfinite(base["baseline_max"]) else np.nan,
                        }
                    )
    return pd.DataFrame(rows)


def compare_substitutions(access: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1930)
    rows = []
    index_cols = ["fold", "label", "idx_in_session", "direction", "true_state_label"]
    for (mode, endpoint, direction), sub in access.groupby(["mode", "endpoint", "direction"], sort=False):
        true = sub[sub["c_kind"].eq("true_c")].set_index(index_cols)
        for fake in FAKE_C_KINDS:
            comp = sub[sub["c_kind"].eq(fake)].set_index(index_cols)
            joined = true[["access_effect"]].join(comp[["access_effect"]], how="inner", lsuffix="_true", rsuffix="_fake")
            diff = joined["access_effect_true"].to_numpy(dtype=float) - joined["access_effect_fake"].to_numpy(dtype=float)
            effect, p = signflip_p(diff, rng, args.n_perm)
            rows.append(
                {
                    "mode": mode,
                    "endpoint": endpoint,
                    "direction": direction,
                    "fake_c_kind": fake,
                    "mean_true_c": float(np.nanmean(joined["access_effect_true"])),
                    "mean_fake_c": float(np.nanmean(joined["access_effect_fake"])),
                    "effect_true_minus_fake": effect,
                    "p_true_greater": p,
                    "n_pairs": int(np.isfinite(diff).sum()),
                    "passes": bool(np.isfinite(effect) and effect > 0 and np.isfinite(p) and p <= 0.05),
                }
            )
    return pd.DataFrame(rows)


def summarize(comps: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (mode, endpoint, direction), sub in comps.groupby(["mode", "endpoint", "direction"], sort=False):
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "direction": direction,
                "substitution_pass_count": int(sub["passes"].sum()),
                "true_c_non_substitutable": bool(int(sub["passes"].sum()) >= 4),
                "mean_true_c": float(np.nanmean(sub["mean_true_c"])),
                "mean_fake_c": float(np.nanmean(sub["mean_fake_c"])),
                "mean_effect_true_minus_fake": float(np.nanmean(sub["effect_true_minus_fake"])),
                "passes_shuffled_c": bool(sub[sub["fake_c_kind"].eq("shuffled_c")]["passes"].sum() > 0),
                "passes_phase_rotated_c": bool(sub[sub["fake_c_kind"].eq("phase_rotated_c")]["passes"].sum() > 0),
                "passes_random_c": bool(sub[sub["fake_c_kind"].eq("random_c")]["passes"].sum() > 0),
                "passes_balanced_c": bool(sub[sub["fake_c_kind"].eq("balanced_c")]["passes"].sum() > 0),
                "passes_foreign_label_c": bool(sub[sub["fake_c_kind"].eq("foreign_label_c")]["passes"].sum() > 0),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["true_c_non_substitutable", "substitution_pass_count", "mean_effect_true_minus_fake"],
        ascending=[False, False, False],
    )


def write_report(path: Path, summary: pd.DataFrame, comps: pd.DataFrame, args: argparse.Namespace) -> None:
    lines = [
        "# Private B6W C Substitution Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Question: Can fake C substitute for true C in the surviving intersection-access operation?",
        "",
        "Boundary: C is fixed and not redefined. This tests non-substitutability of the C-conditioned access path, not object-existence of C.",
        "",
        "## Main Findings",
        "",
        f"- true-C non-substitutable conditions: {int(summary['true_c_non_substitutable'].sum())} / {len(summary)}",
        f"- mean substitution pass count: {float(np.nanmean(summary['substitution_pass_count'])):.3f} / {len(FAKE_C_KINDS)}",
        "",
        "## Substitution Summary",
        "",
        summary.to_csv(index=False).strip(),
        "",
        "## Substitution Comparisons",
        "",
        comps.to_csv(index=False).strip(),
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
    table.to_csv(outdir / "private_B6W_state_table.csv", index=False)
    frames = []
    for mode in b6p.MODES:
        for endpoint in b6p.ENDPOINTS:
            access = build_substitution_access(table, b6p, b6l, mode, endpoint, args)
            if not access.empty:
                frames.append(access)
    access = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    comps = compare_substitutions(access, args)
    summary = summarize(comps)

    access.to_csv(outdir / "private_B6W_c_substitution_access_events.csv", index=False)
    comps.to_csv(outdir / "private_B6W_c_substitution_comparison.csv", index=False)
    summary.to_csv(outdir / "private_B6W_c_substitution_summary.csv", index=False)
    write_report(outdir / "private_B6W_c_substitution_summary.md", summary, comps, args)

    print("\nPrivate B6W C substitution outputs")
    print(outdir)
    print(summary.to_string(index=False, max_rows=80))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6w_c_substitution")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=61920)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
