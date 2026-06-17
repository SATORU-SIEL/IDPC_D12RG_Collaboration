#!/usr/bin/env python3
"""Private B6V Access Without C Audit.

Private only. Do not publish, stage, commit, or push.

Question:
    Does intersection access survive without C? If A<->B direct access alone
    reproduces the B6U/B6P pattern, then C is not necessary. If direct A<->B
    fails while A->C->B / B->C->A survives, C behaves as a necessary access
    condition rather than a redundant extra variable.

Boundary:
    C is not redefined. The C-intersection arm reuses the B6P access operation.
    The no-C arm removes state-conditioned C access and restricts readout to
    direct A-B primitives.
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

CONTROLS = ["random", "balanced", "performance_matched", "shuffled_c", "phase_rotated"]
CORE_CONTROLS = ["balanced", "shuffled_c", "phase_rotated"]

# Direct A<->B access is intentionally restricted to AB primitives. This is the
# counter-hypothesis: perhaps A and B alone explain the effect without C.
AB_DIRECT_MASK = {
    "O1_lag0_AB": 1.00,
    "O2_lag5_AB": 1.00,
    "O3_A_C_boundary": 0.00,
    "O4_B_C_boundary": 0.00,
    "O5_full_TFC": 0.00,
    "O6_phase_only": 0.00,
    "O7_suppress_event": 0.00,
}


class AttrDict(dict):
    __getattr__ = dict.__getitem__


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_folds(labels: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed + 1810)
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


def direct_ab_weights(weights: np.ndarray) -> np.ndarray:
    mask = np.asarray([AB_DIRECT_MASK[op] for op in OPERATORS], dtype=float)
    return normalize_weights(normalize_weights(weights) * mask)


def build_base(args: argparse.Namespace):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    b6p = load_module("private_b6p_for_b6v", B6P_SCRIPT)
    b6l, table = b6p.build_table(args)
    return b6p, b6l, table


def baseline_readouts(row: pd.Series, b6p, b6l, endpoint: str) -> dict[str, float]:
    return b6p.baseline_readouts(row, b6l, endpoint)


def no_c_info(train: pd.DataFrame, b6p, b6l, mode: str, endpoint: str, args: argparse.Namespace, rng: np.random.Generator) -> dict:
    # Build normal C policies only to get the fold's global/performance controls,
    # then discard state-conditioned C mapping from the true no-C arm.
    data = train.copy()
    data["b6p_state_label"] = b6l.state_labels(data, mode)
    info = b6p.train_generators(data, b6l, mode, endpoint, args, rng)
    global_w = normalize_weights(info["global"])
    performance_w = normalize_weights(info["performance"])
    return {
        "true": global_w,
        "balanced": np.ones(len(OPERATORS), dtype=float) / len(OPERATORS),
        "performance_matched": performance_w,
        "shuffled_c": global_w,
        "phase_rotated": rotate_weights(global_w, shift=1),
    }


def no_c_weights(kind: str, info: dict, rng: np.random.Generator) -> np.ndarray:
    if kind == "random":
        return direct_ab_weights(rng.dirichlet(np.ones(len(OPERATORS))))
    return direct_ab_weights(info[kind])


def build_no_c_access(table: pd.DataFrame, b6p, b6l, mode: str, endpoint: str, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1820)
    data = table.copy()
    data["b6p_state_label"] = b6l.state_labels(data, mode)
    folds = make_folds(data["label"].astype(str).unique(), args.n_folds, args.seed)
    rows = []
    for fold_index, test_labels in enumerate(folds):
        test_mask = data["label"].astype(str).isin(set(test_labels))
        train = data[~test_mask].copy()
        test = data[test_mask].copy().reset_index(drop=True)
        info = no_c_info(train, b6p, b6l, mode, endpoint, args, rng)
        for _, row in test.iterrows():
            base = baseline_readouts(row, b6p, b6l, endpoint)
            for direction in ["A_to_B_no_C", "B_to_A_no_C"]:
                for kind in ["true", *CONTROLS]:
                    weights = no_c_weights(kind, info, rng)
                    access = b6p.weighted_reward(row, b6l, weights, endpoint)
                    rows.append(
                        {
                            "mode": mode,
                            "endpoint": endpoint,
                            "fold": fold_index,
                            "label": row["label"],
                            "idx_in_session": row["idx_in_session"],
                            "state_label": "NO_C_AB_DIRECT",
                            "direction": direction,
                            "arm_kind": kind,
                            "access_readout": access,
                            "baseline_max": base["baseline_max"],
                            "access_effect": access - base["baseline_max"] if np.isfinite(access) and np.isfinite(base["baseline_max"]) else np.nan,
                        }
                    )
    return pd.DataFrame(rows)


def compare_access(access: pd.DataFrame, effect_col: str, args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 1830)
    rows = []
    for (mode, endpoint, direction), sub in access.groupby(["mode", "endpoint", "direction"], sort=False):
        true = sub[sub["arm_kind"].eq("true")].set_index(["fold", "label", "idx_in_session", "state_label"])
        for control in CONTROLS:
            comp = sub[sub["arm_kind"].eq(control)].set_index(["fold", "label", "idx_in_session", "state_label"])
            joined = true[[effect_col]].join(comp[[effect_col]], how="inner", lsuffix="_true", rsuffix="_control")
            diff = joined[f"{effect_col}_true"].to_numpy(dtype=float) - joined[f"{effect_col}_control"].to_numpy(dtype=float)
            effect, p = signflip_p(diff, rng, args.n_perm)
            rows.append(
                {
                    "mode": mode,
                    "endpoint": endpoint,
                    "direction": direction,
                    "comparison": f"true_vs_{control}",
                    "control_kind": control,
                    "mean_true": float(np.nanmean(joined[f"{effect_col}_true"])),
                    "mean_control": float(np.nanmean(joined[f"{effect_col}_control"])),
                    "effect": effect,
                    "p_greater": p,
                    "n_pairs": int(np.isfinite(diff).sum()),
                    "passes": bool(np.isfinite(effect) and effect > 0 and np.isfinite(p) and p <= 0.05),
                }
            )
    return pd.DataFrame(rows)


def summarize_comps(comp: pd.DataFrame, arm_type: str) -> pd.DataFrame:
    rows = []
    for (mode, endpoint, direction), sub in comp.groupby(["mode", "endpoint", "direction"], sort=False):
        core = sub[sub["control_kind"].isin(CORE_CONTROLS)]
        rows.append(
            {
                "mode": mode,
                "endpoint": endpoint,
                "direction": direction,
                "arm_type": arm_type,
                "pass_count": int(sub["passes"].sum()),
                "core_pass_count": int(core["passes"].sum()),
                "survives": bool(int(core["passes"].sum()) >= 2 and int(sub["passes"].sum()) >= 4),
                "fails": bool(int(core["passes"].sum()) <= 1),
                "mean_effect": float(np.nanmean(sub["effect"])),
                "mean_core_effect": float(np.nanmean(core["effect"])),
                "mean_true_access_effect": float(np.nanmean(sub["mean_true"])),
            }
        )
    return pd.DataFrame(rows)


def direction_pair(direction: str) -> str:
    if direction == "A_to_C_to_B":
        return "A_path"
    if direction == "B_to_C_to_A":
        return "B_path"
    if direction == "A_to_B_no_C":
        return "A_path"
    if direction == "B_to_A_no_C":
        return "B_path"
    return direction


def compare_c_vs_no_c(c_summary: pd.DataFrame, no_c_summary: pd.DataFrame) -> pd.DataFrame:
    c = c_summary.copy()
    n = no_c_summary.copy()
    c["path"] = c["direction"].map(direction_pair)
    n["path"] = n["direction"].map(direction_pair)
    joined = c.set_index(["mode", "endpoint", "path"]).join(
        n.set_index(["mode", "endpoint", "path"]),
        how="inner",
        lsuffix="_with_c",
        rsuffix="_no_c",
    ).reset_index()
    joined["c_necessary_pattern"] = joined["survives_with_c"] & joined["fails_no_c"]
    joined["access_effect_gap_with_c_minus_no_c"] = joined["mean_core_effect_with_c"] - joined["mean_core_effect_no_c"]
    return joined.sort_values(
        ["c_necessary_pattern", "access_effect_gap_with_c_minus_no_c", "core_pass_count_with_c"],
        ascending=[False, False, False],
    )


def write_report(path: Path, contrast: pd.DataFrame, c_summary: pd.DataFrame, no_c_summary: pd.DataFrame, c_comp: pd.DataFrame, no_c_comp: pd.DataFrame, args: argparse.Namespace) -> None:
    lines = [
        "# Private B6V Access Without C Audit",
        "",
        "Status: local/private screen only. No publication, commit, stage, or push was performed.",
        "",
        "Question: Does A<->B access without C reproduce intersection access?",
        "",
        "Boundary: C is fixed and not redefined. The no-C arm removes C-state conditioning and restricts the access readout to direct AB primitives.",
        "",
        "## Main Findings",
        "",
        f"- C-necessary pattern conditions: {int(contrast['c_necessary_pattern'].sum())} / {len(contrast)}",
        f"- with-C intersection survival conditions: {int(contrast['survives_with_c'].sum())} / {len(contrast)}",
        f"- no-C direct failure conditions: {int(contrast['fails_no_c'].sum())} / {len(contrast)}",
        "",
        "## C vs No-C Contrast",
        "",
        contrast.to_csv(index=False).strip(),
        "",
        "## With-C Intersection Summary",
        "",
        c_summary.to_csv(index=False).strip(),
        "",
        "## No-C Direct AB Summary",
        "",
        no_c_summary.to_csv(index=False).strip(),
        "",
        "## With-C Control Comparisons",
        "",
        c_comp.to_csv(index=False).strip(),
        "",
        "## No-C Control Comparisons",
        "",
        no_c_comp.to_csv(index=False).strip(),
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
    table.to_csv(outdir / "private_B6V_state_table.csv", index=False)

    c_frames = []
    no_c_frames = []
    policy_frames = []
    for mode in b6p.MODES:
        for endpoint in b6p.ENDPOINTS:
            _, c_intersection, policies = b6p.build_arms(table, b6l, mode, endpoint, args)
            c_intersection = c_intersection.rename(columns={"intersection_access_effect": "access_effect"})
            if not c_intersection.empty:
                c_frames.append(c_intersection)
            if not policies.empty:
                policy_frames.append(policies)
            no_c = build_no_c_access(table, b6p, b6l, mode, endpoint, args)
            if not no_c.empty:
                no_c_frames.append(no_c)

    with_c = pd.concat(c_frames, ignore_index=True) if c_frames else pd.DataFrame()
    no_c = pd.concat(no_c_frames, ignore_index=True) if no_c_frames else pd.DataFrame()
    policies = pd.concat(policy_frames, ignore_index=True) if policy_frames else pd.DataFrame()

    c_comp = compare_access(with_c, "access_effect", args)
    no_c_comp = compare_access(no_c, "access_effect", args)
    c_summary = summarize_comps(c_comp, "with_c_intersection")
    no_c_summary = summarize_comps(no_c_comp, "no_c_direct_ab")
    contrast = compare_c_vs_no_c(c_summary, no_c_summary)

    with_c.to_csv(outdir / "private_B6V_with_c_intersection_events.csv", index=False)
    no_c.to_csv(outdir / "private_B6V_no_c_direct_ab_events.csv", index=False)
    c_comp.to_csv(outdir / "private_B6V_with_c_control_comparison.csv", index=False)
    no_c_comp.to_csv(outdir / "private_B6V_no_c_control_comparison.csv", index=False)
    c_summary.to_csv(outdir / "private_B6V_with_c_intersection_summary.csv", index=False)
    no_c_summary.to_csv(outdir / "private_B6V_no_c_direct_ab_summary.csv", index=False)
    contrast.to_csv(outdir / "private_B6V_access_without_c_contrast.csv", index=False)
    policies.to_csv(outdir / "private_B6V_generated_policies.csv", index=False)
    write_report(outdir / "private_B6V_access_without_c_summary.md", contrast, c_summary, no_c_summary, c_comp, no_c_comp, args)

    print("\nPrivate B6V access without C outputs")
    print(outdir)
    print(contrast.to_string(index=False, max_rows=80))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/private_b6v_access_without_c")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=61820)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
