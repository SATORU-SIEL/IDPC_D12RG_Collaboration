#!/usr/bin/env python3
"""Stage B4.1 secondary folded-readout / alias diagnostic.

This diagnostic keeps Stage B4 fixed as negative.  It asks whether the
descriptive C10-over-C12 pattern is stable enough to be interpreted as a
secondary folded-readout / alias structure, or whether it is better explained
by timing distribution and scoring geometry.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


B4_SCRIPT = Path(__file__).with_name("test_Stage_B4_real_time_anchored_C12_readout.py")
BASES = (8, 10, 12, 16, 24)
PRIMARY_ANCHOR = "utc_annual_orbital_phase"
OUTPUT_PREFIX = "Stage_B4_1_secondary_folded_readout_alias"


def load_b4_module():
    spec = importlib.util.spec_from_file_location("stage_b4", B4_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import Stage B4 script: {B4_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def weekly_phase(timestamp: pd.Timestamp) -> float:
    ts = timestamp.tz_convert("UTC")
    seconds = ts.dayofweek * 86400 + ts.hour * 3600 + ts.minute * 60 + ts.second + ts.microsecond / 1_000_000
    return float(2.0 * np.pi * seconds / (7.0 * 86400.0))


def add_anchor_columns(events: pd.DataFrame, b4) -> pd.DataFrame:
    out = events.copy()
    out["utc_annual_orbital_phase"] = out["event_utc"].map(b4.annual_phase)
    out["utc_daily_phase"] = out["event_utc"].map(b4.daily_phase)
    out["utc_weekly_phase"] = out["event_utc"].map(weekly_phase)
    first = out["event_utc"].min()
    last = out["event_utc"].max()
    span = max((last - first).total_seconds(), 1.0)
    out["global_elapsed_phase"] = out["event_utc"].map(lambda ts: float(2.0 * np.pi * (ts - first).total_seconds() / span))
    out["event_date_utc"] = out["event_utc"].dt.strftime("%Y-%m-%d")
    return out


def score_subset(sub: pd.DataFrame, anchor: str, basis: int, b4) -> float:
    if sub.empty:
        return np.nan
    phases = sub[anchor].to_numpy(float)
    return b4.score_phases(phases, basis)["readout_score"]


def basis_rankings(events: pd.DataFrame, anchors: tuple[str, ...], b4) -> pd.DataFrame:
    rows = []
    for anchor in anchors:
        for event_class, sub in events.groupby("event_class"):
            scores = {basis: score_subset(sub, anchor, basis, b4) for basis in BASES}
            ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
            c10 = scores[10]
            c12 = scores[12]
            c24 = scores[24]
            for rank, (basis, score) in enumerate(ranked, start=1):
                rows.append(
                    {
                        "anchor_name": anchor,
                        "event_class": event_class,
                        "basis": basis,
                        "rank": rank,
                        "readout_score": score,
                        "n_events": len(sub),
                        "C10_minus_C12": c10 - c12,
                        "D24_minus_C12": c24 - c12,
                        "best_basis": ranked[0][0],
                        "best_score": ranked[0][1],
                    }
                )
    return pd.DataFrame(rows)


def leave_one_group_stability(events: pd.DataFrame, anchor: str, group_col: str, b4) -> pd.DataFrame:
    rows = []
    for event_class, sub in events.groupby("event_class"):
        groups = sorted(sub[group_col].dropna().unique())
        for group in groups:
            kept = sub[~sub[group_col].eq(group)]
            if len(kept) < 3:
                continue
            scores = {basis: score_subset(kept, anchor, basis, b4) for basis in BASES}
            ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
            rows.append(
                {
                    "anchor_name": anchor,
                    "event_class": event_class,
                    "group_col": group_col,
                    "left_out": group,
                    "n_kept": len(kept),
                    "best_basis": ranked[0][0],
                    "best_score": ranked[0][1],
                    "C10_score": scores[10],
                    "C12_score": scores[12],
                    "C24_score": scores[24],
                    "C10_minus_C12": scores[10] - scores[12],
                    "D24_minus_C12": scores[24] - scores[12],
                }
            )
    return pd.DataFrame(rows)


def stability_summary(stability: pd.DataFrame) -> pd.DataFrame:
    if stability.empty:
        return pd.DataFrame()
    return (
        stability.groupby(["anchor_name", "event_class", "group_col"], as_index=False)
        .agg(
            n_leave_one=("left_out", "size"),
            c10_best_rate=("best_basis", lambda x: float(np.mean(np.asarray(x) == 10))),
            c12_best_rate=("best_basis", lambda x: float(np.mean(np.asarray(x) == 12))),
            c24_best_rate=("best_basis", lambda x: float(np.mean(np.asarray(x) == 24))),
            mean_C10_minus_C12=("C10_minus_C12", "mean"),
            min_C10_minus_C12=("C10_minus_C12", "min"),
            mean_D24_minus_C12=("D24_minus_C12", "mean"),
        )
    )


def p_greater(observed: float, controls: np.ndarray) -> float:
    controls = controls[np.isfinite(controls)]
    if not np.isfinite(observed) or len(controls) == 0:
        return np.nan
    return float((1.0 + np.sum(controls >= observed)) / (len(controls) + 1.0))


def bh_fdr(values: list[float]) -> list[float]:
    p = np.asarray(values, dtype=float)
    q = np.full_like(p, np.nan)
    valid = np.isfinite(p)
    if not valid.any():
        return q.tolist()
    pv = p[valid]
    order = np.argsort(pv)
    ranked = pv[order]
    n = len(ranked)
    ranked_q = ranked * n / np.arange(1, n + 1)
    ranked_q = np.minimum.accumulate(ranked_q[::-1])[::-1]
    out = np.empty_like(ranked_q)
    out[order] = np.clip(ranked_q, 0.0, 1.0)
    q[valid] = out
    return q.tolist()


def margin_controls(events: pd.DataFrame, anchor: str, b4, n_random: int, rng: np.random.Generator) -> pd.DataFrame:
    phase_by_label = {
        label: values[anchor].to_numpy(float)
        for label, values in events.groupby("label")
    }
    rows = []
    for event_class, sub in events.groupby("event_class"):
        observed = score_subset(sub, anchor, 10, b4) - score_subset(sub, anchor, 12, b4)
        controls = []
        for _ in range(n_random):
            sampled = [rng.choice(phase_by_label[label]) for label in sub["label"] if label in phase_by_label]
            sampled_df = pd.DataFrame({anchor: np.asarray(sampled, dtype=float)})
            controls.append(score_subset(sampled_df, anchor, 10, b4) - score_subset(sampled_df, anchor, 12, b4))
        controls = np.asarray(controls, dtype=float)
        rows.append(
            {
                "anchor_name": anchor,
                "event_class": event_class,
                "observed_C10_minus_C12": observed,
                "control_mean_C10_minus_C12": float(np.nanmean(controls)),
                "effect_vs_label_preserved_control": float(observed - np.nanmean(controls)),
                "p_vs_label_preserved_control": p_greater(observed, controls),
                "control_sd": float(np.nanstd(controls)),
                "n_events": len(sub),
            }
        )
    out = pd.DataFrame(rows)
    out["q_vs_label_preserved_control"] = bh_fdr(out["p_vs_label_preserved_control"].tolist())
    return out


def date_clustering(events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for event_class, sub in events.groupby("event_class"):
        counts = sub["event_date_utc"].value_counts()
        rows.append(
            {
                "event_class": event_class,
                "n_events": len(sub),
                "n_dates": int(counts.size),
                "max_date_fraction": float(counts.max() / len(sub)),
                "top_date": str(counts.index[0]),
                "top_date_count": int(counts.iloc[0]),
            }
        )
    return pd.DataFrame(rows)


def input_hash_manifest(input_root: Path, b4) -> pd.DataFrame:
    b3 = b4.load_b3_module()
    rels = list(b3.INPUT_FILES)
    rels.extend(str(path.relative_to(input_root)) for path in sorted(input_root.glob("P*_quantum_timeseries.csv")))
    rels.extend(str(path.relative_to(input_root)) for path in sorted(input_root.glob("P*_eeg_timeseries.csv")))
    rels.append(str(B4_SCRIPT.relative_to(B4_SCRIPT.parents[1])))
    rows = []
    for rel in rels:
        path = input_root / rel if not rel.startswith("scripts/") else B4_SCRIPT.parents[1] / rel
        rows.append({"relative_path": rel, "absolute_path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return pd.DataFrame(rows)


def classify_secondary_pattern(rankings: pd.DataFrame, stability_sum: pd.DataFrame, controls: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    annual = rankings[rankings["anchor_name"].eq(PRIMARY_ANCHOR) & rankings["rank"].eq(1)].copy()
    annual["c10_best"] = annual["best_basis"].eq(10)
    label = stability_sum[
        stability_sum["anchor_name"].eq(PRIMARY_ANCHOR)
        & stability_sum["group_col"].eq("label")
    ][["event_class", "c10_best_rate", "mean_C10_minus_C12", "min_C10_minus_C12"]].rename(
        columns={
            "c10_best_rate": "label_c10_best_rate",
            "mean_C10_minus_C12": "label_mean_C10_minus_C12",
            "min_C10_minus_C12": "label_min_C10_minus_C12",
        }
    )
    date = stability_sum[
        stability_sum["anchor_name"].eq(PRIMARY_ANCHOR)
        & stability_sum["group_col"].eq("event_date_utc")
    ][["event_class", "c10_best_rate", "mean_C10_minus_C12", "min_C10_minus_C12"]].rename(
        columns={
            "c10_best_rate": "date_c10_best_rate",
            "mean_C10_minus_C12": "date_mean_C10_minus_C12",
            "min_C10_minus_C12": "date_min_C10_minus_C12",
        }
    )
    ctrl = controls[controls["anchor_name"].eq(PRIMARY_ANCHOR)][
        ["event_class", "observed_C10_minus_C12", "effect_vs_label_preserved_control", "q_vs_label_preserved_control"]
    ]
    merged = annual[["event_class", "best_basis", "best_score", "C10_minus_C12", "D24_minus_C12", "c10_best"]]
    merged = merged.merge(label, on="event_class", how="left").merge(date, on="event_class", how="left").merge(ctrl, on="event_class", how="left")
    merged["stable_secondary_C10_pattern"] = (
        merged["c10_best"]
        & (merged["label_c10_best_rate"] >= 0.75)
        & (merged["date_c10_best_rate"] >= 0.75)
        & (merged["label_min_C10_minus_C12"] > 0)
        & (merged["date_min_C10_minus_C12"] > 0)
        & (merged["q_vs_label_preserved_control"] < 0.10)
    )
    status = "stable_secondary_C10_pattern_detected" if bool(merged["stable_secondary_C10_pattern"].any()) else "descriptive_only_no_stable_secondary_C10_pattern"
    return status, merged


def write_summary(
    path: Path,
    status: str,
    interpretation: pd.DataFrame,
    rankings: pd.DataFrame,
    stability_sum: pd.DataFrame,
    controls: pd.DataFrame,
    clustering: pd.DataFrame,
) -> None:
    annual_best = rankings[rankings["anchor_name"].eq(PRIMARY_ANCHOR) & rankings["rank"].eq(1)].sort_values("event_class")
    lines = [
        "# Stage B4.1 Secondary Folded-Readout / Alias Diagnostic Summary",
        "",
        "## Boundary",
        "",
        "Stage B4 remains fixed as negative. B4.1 is a secondary diagnostic and does not move the project to Stage C.",
        "",
        "## Result",
        "",
        f"- secondary diagnostic status: `{status}`",
        f"- annual/orbital event classes with C10 as best descriptive basis: {int(annual_best['best_basis'].eq(10).sum())} / {len(annual_best)}",
        f"- annual/orbital event classes with q < 0.10 for C10-C12 margin control: {int((controls[controls['anchor_name'].eq(PRIMARY_ANCHOR)]['q_vs_label_preserved_control'] < 0.10).sum())}",
        "",
        "## Annual/Orbital Best Basis Rows",
        "",
        annual_best[["event_class", "best_basis", "best_score", "C10_minus_C12", "D24_minus_C12", "n_events"]].to_csv(index=False).strip(),
        "",
        "## Secondary Stability Interpretation",
        "",
        interpretation.to_csv(index=False).strip(),
        "",
        "## C10-C12 Margin Controls",
        "",
        controls[controls["anchor_name"].eq(PRIMARY_ANCHOR)].sort_values("q_vs_label_preserved_control").to_csv(index=False).strip(),
        "",
        "## Label/Date Stability Summary",
        "",
        stability_sum[stability_sum["anchor_name"].eq(PRIMARY_ANCHOR)].sort_values(["group_col", "event_class"]).to_csv(index=False).strip(),
        "",
        "## Date Clustering",
        "",
        clustering.sort_values("max_date_fraction", ascending=False).to_csv(index=False).strip(),
        "",
        "## Interpretation",
        "",
        "B4.1 evaluates whether the descriptive C10-over-C12 pattern is stable under label and date leave-one-out diagnostics and label-preserved time controls. A descriptive C10 rank alone is not a positive result.",
    ]
    path.write_text("\n".join(lines) + "\n")


def write_manifest(path: Path, input_root: Path, n_random: int, seed: int, hashes: pd.DataFrame) -> None:
    lines = [
        "# Stage B4.1 Secondary Folded-Readout / Alias Diagnostic Manifest",
        "",
        f"- input root: `{input_root}`",
        f"- bases: {', '.join('C' + str(b) for b in BASES)}",
        f"- primary diagnostic anchor: `{PRIMARY_ANCHOR}`",
        "- sensitivity anchors: `utc_daily_phase`, `utc_weekly_phase`, `global_elapsed_phase`",
        f"- n_random: {n_random}",
        f"- random seed: {seed}",
        "",
        "## Input Hashes",
        "",
        hashes.to_csv(index=False).strip(),
    ]
    path.write_text("\n".join(lines) + "\n")


def run_audit(input_root: Path, output_dir: Path, n_random: int, seed: int) -> tuple[str, pd.DataFrame]:
    b4 = load_b4_module()
    b3 = b4.load_b3_module()
    events, inventory = b4.add_real_time_to_events(input_root, b3)
    events = add_anchor_columns(events, b4)
    rng = np.random.default_rng(seed)
    anchors = ("utc_annual_orbital_phase", "utc_daily_phase", "utc_weekly_phase", "global_elapsed_phase")
    rankings = basis_rankings(events, anchors, b4)
    label_stability = leave_one_group_stability(events, PRIMARY_ANCHOR, "label", b4)
    date_stability = leave_one_group_stability(events, PRIMARY_ANCHOR, "event_date_utc", b4)
    stability = pd.concat([label_stability, date_stability], ignore_index=True)
    stability_sum = stability_summary(stability)
    controls = pd.concat([margin_controls(events, anchor, b4, n_random, rng) for anchor in anchors], ignore_index=True)
    clustering = date_clustering(events)
    hashes = input_hash_manifest(input_root, b4)
    status, interpretation = classify_secondary_pattern(rankings, stability_sum, controls)
    output_dir.mkdir(parents=True, exist_ok=True)
    rankings.to_csv(output_dir / f"{OUTPUT_PREFIX}_basis_rankings.csv", index=False)
    stability.to_csv(output_dir / f"{OUTPUT_PREFIX}_leave_one_stability.csv", index=False)
    stability_sum.to_csv(output_dir / f"{OUTPUT_PREFIX}_stability_summary.csv", index=False)
    controls.to_csv(output_dir / f"{OUTPUT_PREFIX}_margin_controls.csv", index=False)
    clustering.to_csv(output_dir / f"{OUTPUT_PREFIX}_date_clustering.csv", index=False)
    inventory.to_csv(output_dir / f"{OUTPUT_PREFIX}_time_mapping_inventory.csv", index=False)
    interpretation.to_csv(output_dir / f"{OUTPUT_PREFIX}_secondary_interpretation.csv", index=False)
    hashes.to_csv(output_dir / f"{OUTPUT_PREFIX}_input_hashes.csv", index=False)
    write_manifest(output_dir / f"{OUTPUT_PREFIX}_manifest.md", input_root, n_random, seed, hashes)
    write_summary(output_dir / f"{OUTPUT_PREFIX}_summary.md", status, interpretation, rankings, stability_sum, controls, clustering)
    return status, interpretation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--n-random", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260608)
    args = parser.parse_args()
    run_audit(args.input_root, args.output_dir, args.n_random, args.seed)


if __name__ == "__main__":
    main()
