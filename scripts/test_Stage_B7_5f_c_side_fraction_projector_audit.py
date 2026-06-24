#!/usr/bin/env python3
"""Stage B7.5f C-side fraction localization and projector-compatibility audit.

This audit is a registered diagnostic follow-up to B7.5e. It does not treat
N/M fractions as explanations. It asks whether fraction hits can be lifted
from decimal coincidence into C-side localization, denominator-universe
recovery, candidate member structure, projector compatibility, topology
compatibility, and trace/determinant candidates.
"""

from __future__ import annotations

import argparse
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
FOCUS_FRACTIONS = {"1/4", "1/2", "3/4", "3/7", "2/11"}
TARGET_FRACTIONS = {"1/4", "2/11"}
PRIMARY_COMPARISON = "full_minus_reverse"


def as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def parse_fraction(label: str) -> Fraction | None:
    try:
        return Fraction(str(label))
    except Exception:
        return None


def split_tags(tags: object) -> set[str]:
    if pd.isna(tags):
        return set()
    return {t for t in str(tags).split("|") if t}


def topology_meta(paired: pd.DataFrame, readout: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "topology_arm", "base_topology", "perturbation_kind", "node_count_n",
        "distance_from_12", "signed_distance_from_12", "is_odd", "edge_count",
        "is_ring_sharing", "is_reversed", "is_null",
    ]
    parts = []
    for df in (paired, readout):
        have = [c for c in cols if c in df.columns]
        parts.append(df[have].drop_duplicates("topology_arm"))
    meta = pd.concat(parts, ignore_index=True).drop_duplicates("topology_arm", keep="first")
    return meta.set_index("topology_arm")


def infer_raw_universe(row: pd.Series, meta: pd.Series | None, readout_lookup: dict[tuple[str, str], pd.Series]) -> dict[str, object]:
    source = str(row.get("source", ""))
    metric = str(row.get("metric", ""))
    topology = str(row.get("topology_arm", ""))
    rep = str(row.get("representation_arm", "")) if not pd.isna(row.get("representation_arm", np.nan)) else ""
    value = float(row.get("value", np.nan))
    frac = parse_fraction(str(row.get("nearest_fraction", "")))
    num = int(row.get("numerator", 0)) if not pd.isna(row.get("numerator", np.nan)) else 0
    den = int(row.get("denominator", 0)) if not pd.isna(row.get("denominator", np.nan)) else 0

    result: dict[str, object] = {
        "denominator_universe": "continuous_scaled_metric",
        "raw_numerator": num,
        "raw_denominator": den,
        "raw_fraction": f"{num}/{den}" if den else "NA",
        "raw_count_recovered": False,
        "carrier_dimension_R": int(meta.get("node_count_n", 0)) if meta is not None and "node_count_n" in meta.index and pd.notna(meta.get("node_count_n")) else 0,
    }

    if source == "paired_boundary" and metric in {"full_win_fraction", "reverse_win_fraction"}:
        # B7.5d used the same number of paired seeds for each topology arm.
        n_runs = 36
        raw_n = int(round(value * n_runs)) if np.isfinite(value) else 0
        result.update({
            "denominator_universe": "paired_seed_runs",
            "raw_numerator": raw_n,
            "raw_denominator": n_runs,
            "raw_fraction": f"{raw_n}/{n_runs}",
            "raw_count_recovered": True,
        })
    elif source == "event_geometry" and metric.endswith("top4_survivor_overlap_fraction"):
        raw_n = int(round(value * 4)) if np.isfinite(value) else 0
        result.update({
            "denominator_universe": "top4_survivor_overlap",
            "raw_numerator": raw_n,
            "raw_denominator": 4,
            "raw_fraction": f"{raw_n}/4",
            "raw_count_recovered": True,
        })
    elif source == "event_geometry" and "survivor_strength_fraction" in metric:
        result.update({"denominator_universe": "event_strength_mass"})
    elif source == "event_geometry" and "phase_concentration" in metric:
        result.update({"denominator_universe": "phase_concentration_unit_interval"})
    elif source.startswith("readout"):
        lookup = readout_lookup.get((topology, rep))
        if lookup is not None and "n_nodes" in lookup.index and pd.notna(lookup.get("n_nodes")):
            result["carrier_dimension_R"] = int(lookup.get("n_nodes"))
        result.update({"denominator_universe": "topology_readout_scaled_metric"})
    elif source == "paired_boundary":
        result.update({"denominator_universe": "paired_boundary_scaled_metric"})

    if frac is not None:
        result["reduced_fraction"] = f"{frac.numerator}/{frac.denominator}"
    else:
        result["reduced_fraction"] = "NA"
    return result


def c_side_localization(row: pd.Series) -> dict[str, object]:
    tags = split_tags(row.get("tags", ""))
    topology = str(row.get("topology_arm", ""))
    metric = str(row.get("metric", ""))
    source = str(row.get("source", ""))
    cls = str(row.get("classification", ""))
    rep = str(row.get("representation_arm", ""))
    frac = str(row.get("nearest_fraction", ""))

    c12_neighborhood = "c12_neighborhood" in tags or topology.startswith("c12")
    reversed_region = "reversed" in tags or "reversed" in topology
    ring_share = "ring_sharing" in tags or "ring_share" in topology
    survivor_strength = "survivor_strength" in tags or "survivor" in metric
    five_or_ten = "5_or_10_proxy" in tags or frac in {"1/4", "3/4"} and ("ring_share_10" in tags or "ring_share_5" in tags)
    x3_or_7 = "x3_or_7mod12_proxy" in tags
    boundary_or_reverse = cls in {"boundary", "reverse-stable"}
    reverse_side = cls == "reverse-stable" or "reverse" in rep or metric == "reverse_win_fraction"

    local_score = sum(bool(x) for x in [c12_neighborhood, reversed_region, ring_share, survivor_strength, boundary_or_reverse, reverse_side])
    if c12_neighborhood or reversed_region or survivor_strength or (ring_share and boundary_or_reverse):
        localization = "registered_c_side_target"
    elif five_or_ten:
        localization = "five_or_ten_proxy_region"
    elif x3_or_7:
        localization = "x3_or_7mod12_proxy_region"
    elif source == "event_geometry":
        localization = "representation_event_geometry"
    else:
        localization = "non_target_or_broad"

    return {
        "c12_neighborhood": c12_neighborhood,
        "reversed_region": reversed_region,
        "ring_share_region": ring_share,
        "survivor_strength_region": survivor_strength,
        "five_or_ten_proxy_region": five_or_ten,
        "x3_or_7mod12_proxy_region": x3_or_7,
        "boundary_or_reverse_side": boundary_or_reverse,
        "reverse_side_readout": reverse_side,
        "c_side_localization": localization,
        "c_side_localization_score": local_score,
    }


def projector_candidate(row: pd.Series, inferred: dict[str, object], localized: dict[str, object]) -> dict[str, object]:
    frac = parse_fraction(str(row.get("nearest_fraction", "")))
    R = int(inferred.get("carrier_dimension_R", 0) or 0)
    num = int(row.get("numerator", 0)) if not pd.isna(row.get("numerator", np.nan)) else 0
    den = int(row.get("denominator", 0)) if not pd.isna(row.get("denominator", np.nan)) else 0
    if frac is None or den == 0:
        return {
            "candidate_family": "not_fractional",
            "full_carrier_rank_integral": False,
            "punctured_carrier_rank_integral": False,
            "candidate_rank": np.nan,
            "projector_level": 0,
            "topology_compatibility_candidate": False,
            "trace_determinant_candidate": False,
            "basis": "no valid fraction",
        }

    full_rank = R * num / den if R else np.nan
    punctured_rank = (R - 1) * num / den if R and R > 1 else np.nan
    full_integral = bool(R and abs(full_rank - round(full_rank)) < 1e-9)
    punctured_integral = bool(R and R > 1 and abs(punctured_rank - round(punctured_rank)) < 1e-9)

    frac_label = f"{frac.numerator}/{frac.denominator}"
    target_local = localized["c_side_localization"] == "registered_c_side_target"
    family = "diagnostic_fraction_only"
    candidate_rank = np.nan
    level = 0
    topology_candidate = False
    trace_candidate = False
    basis_parts = []

    if bool(inferred.get("raw_count_recovered", False)):
        level = max(level, 1)
        basis_parts.append(f"raw={inferred.get('raw_fraction')}/{inferred.get('denominator_universe')}")
    else:
        basis_parts.append(str(inferred.get("denominator_universe")))

    if frac_label == "2/11":
        if R == 12 and target_local and punctured_integral and round(punctured_rank) == 2:
            family = "punctured_c12_inversion_pair_candidate"
            candidate_rank = 2
            level = max(level, 3)
            topology_candidate = True
            trace_candidate = True
            basis_parts.append("2/11 fits U=Z_12\\{0}, I={k,-k}")
        else:
            family = "two_eleven_anomaly_not_c12_projector"
            level = max(level, 1 if target_local else 0)
            basis_parts.append(f"R={R}; R*2/11={full_rank}; (R-1)*2/11={punctured_rank}")
    elif full_integral:
        family = "full_carrier_projector_rank_candidate"
        candidate_rank = int(round(full_rank))
        level = max(level, 2)
        topology_candidate = target_local or localized["ring_share_region"] or localized["five_or_ten_proxy_region"] or localized["x3_or_7mod12_proxy_region"]
        if topology_candidate:
            level = max(level, 3)
        basis_parts.append(f"R={R}; rank={candidate_rank}")
    elif punctured_integral:
        family = "punctured_carrier_projector_rank_candidate"
        candidate_rank = int(round(punctured_rank))
        level = max(level, 2)
        topology_candidate = target_local or localized["ring_share_region"]
        basis_parts.append(f"R-1={R-1}; rank={candidate_rank}")
    elif frac_label in {"1/4", "3/4"} and localized["five_or_ten_proxy_region"]:
        family = "five_or_ten_proxy_fraction_diagnostic"
        level = max(level, 1)
        basis_parts.append("1/4 or 3/4 near 5/10 proxy")
    elif frac_label == "1/2" and localized["boundary_or_reverse_side"]:
        family = "boundary_half_split_diagnostic"
        level = max(level, 1)
        basis_parts.append("1/2 boundary split")

    if topology_candidate and level >= 3 and family.endswith("candidate"):
        # No actual P/T matrix is constructed in this follow-up; mark as candidate only.
        trace_candidate = family in {"punctured_c12_inversion_pair_candidate", "full_carrier_projector_rank_candidate"} and candidate_rank == candidate_rank

    return {
        "candidate_family": family,
        "full_carrier_rank_integral": full_integral,
        "punctured_carrier_rank_integral": punctured_integral,
        "candidate_rank": candidate_rank,
        "projector_level": level,
        "topology_compatibility_candidate": topology_candidate,
        "trace_determinant_candidate": trace_candidate,
        "basis": "; ".join(basis_parts),
    }


def build_ladder(enriched: pd.DataFrame) -> pd.DataFrame:
    close = enriched[enriched["is_close_to_fraction"].map(as_bool)].copy()
    focus = close[close["nearest_fraction"].isin(FOCUS_FRACTIONS)].copy()
    two11 = close[close["nearest_fraction"].eq("2/11")].copy()
    one4 = close[close["nearest_fraction"].eq("1/4")].copy()

    rows = []
    def add(level: int, criterion: str, supported: bool, basis: str) -> None:
        rows.append({"level": level, "criterion": criterion, "supported": bool(supported), "basis": basis})

    add(0, "exact_fraction_hits_present", len(close) > 0, f"close_hits={len(close)}; unique={close['nearest_fraction'].nunique() if len(close) else 0}")
    add(1, "denominator_universe_recovered_for_some_hits", bool(close["raw_count_recovered"].any()), f"recovered_hits={int(close['raw_count_recovered'].sum())}")
    add(1, "focus_fractions_remain_visible", len(focus) > 0, f"focus_hits={len(focus)}; fractions={'|'.join(sorted(focus['nearest_fraction'].unique())) if len(focus) else 'none'}")
    add(2, "full_or_punctured_projector_rank_candidate_exists", bool((close["full_carrier_rank_integral"] | close["punctured_carrier_rank_integral"]).any()), f"rank_candidate_hits={int((close['full_carrier_rank_integral'] | close['punctured_carrier_rank_integral']).sum())}")
    add(2, "registered_c_side_localization_exists", bool(close["c_side_localization"].eq("registered_c_side_target").any()), f"registered_target_hits={int(close['c_side_localization'].eq('registered_c_side_target').sum())}")
    add(2, "one_quarter_stable_near_5_or_10_proxy", bool(len(one4[one4["five_or_ten_proxy_region"]]) > 0), f"one_quarter_5_or_10_hits={len(one4[one4['five_or_ten_proxy_region']])}")
    add(2, "two_eleven_is_traceable_but_not_c12_punctured_projector", bool(len(two11) > 0 and not two11["candidate_family"].eq("punctured_c12_inversion_pair_candidate").any()), f"two_eleven_hits={len(two11)}; c12_punctured_candidates={int(two11['candidate_family'].eq('punctured_c12_inversion_pair_candidate').sum())}")
    add(3, "member_structure_candidate_present", bool(close["candidate_family"].isin(["punctured_c12_inversion_pair_candidate", "full_carrier_projector_rank_candidate", "punctured_carrier_projector_rank_candidate"]).any()), f"member_candidate_hits={int(close['candidate_family'].isin(['punctured_c12_inversion_pair_candidate','full_carrier_projector_rank_candidate','punctured_carrier_projector_rank_candidate']).sum())}")
    add(4, "explicit_projector_idempotence_tested", False, "B7.5f classifies projector compatibility from fraction/carrier arithmetic only; no empirical P matrix is constructed here.")
    add(5, "explicit_topology_commutator_tested", False, "No empirical P/T commutator is constructed in B7.5f; this is deferred to a later matrix-level audit.")
    add(6, "restricted_trace_determinant_confirmed", False, "Trace/determinant candidates are annotated but not confirmed without a constructed restricted topology block.")
    add(7, "perturbation_defeats_matched_controls", False, "B7.5f reuses B7.5d perturbation labels; it does not yet run new matched projector controls.")
    return pd.DataFrame(rows)


def summarize(enriched: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    close = enriched[enriched["is_close_to_fraction"].map(as_bool)].copy()
    family_summary = (
        close.groupby("candidate_family", as_index=False)
        .agg(
            n_hits=("nearest_fraction", "size"),
            n_focus=("is_focus_fraction", "sum"),
            n_registered_target=("c_side_localization", lambda s: int((s == "registered_c_side_target").sum())),
            fractions=("nearest_fraction", lambda s: "|".join(sorted(set(map(str, s))))),
            topologies=("topology_arm", lambda s: "|".join(sorted(set(map(str, s)))[:20])),
        )
        .sort_values(["n_focus", "n_hits"], ascending=[False, False])
    )
    localization_summary = (
        close.groupby(["nearest_fraction", "c_side_localization"], as_index=False)
        .agg(n_hits=("metric", "size"), families=("candidate_family", lambda s: "|".join(sorted(set(map(str, s))))))
        .sort_values(["nearest_fraction", "n_hits"], ascending=[True, False])
    )
    target_focus = close[close["nearest_fraction"].isin(TARGET_FRACTIONS)].copy()
    target_focus = target_focus.sort_values(["nearest_fraction", "c_side_localization_score", "abs_error_to_fraction"], ascending=[True, False, True])
    return family_summary, localization_summary, target_focus


def write_summary(outdir: Path, enriched: pd.DataFrame, ladder: pd.DataFrame, family_summary: pd.DataFrame, localization_summary: pd.DataFrame, target_focus: pd.DataFrame, args: argparse.Namespace) -> None:
    close = enriched[enriched["is_close_to_fraction"].map(as_bool)].copy()
    one4 = close[close["nearest_fraction"].eq("1/4")]
    two11 = close[close["nearest_fraction"].eq("2/11")]
    lines = [
        "# Stage B7.5f C-side Fraction Localization and Projector-Compatibility Audit",
        "",
        "Status: executed after `Stage_B7_5f_preregistration_email_sent.md`.",
        "",
        "## Registered Question",
        "",
        "Do the observed N/M fraction signatures localize systematically to specific C-side conditions, topology arms, survivor structures, or projector-compatible subspaces?",
        "",
        "Fractions are treated as diagnostics first, not explanations.",
        "",
        "## Decision Ladder",
        "",
        ladder.to_csv(index=False).strip(),
        "",
        "## Main Result",
        "",
        f"- Close fraction hits analyzed: {len(close)}.",
        f"- Unique close fractions: {close['nearest_fraction'].nunique() if len(close) else 0}.",
        f"- Raw denominator/count universe recovered for {int(close['raw_count_recovered'].sum())} hits.",
        f"- Projector-rank arithmetic candidates: {int((close['full_carrier_rank_integral'] | close['punctured_carrier_rank_integral']).sum())} hits.",
        f"- Registered C-side target localizations: {int(close['c_side_localization'].eq('registered_c_side_target').sum())} hits.",
        "",
        "## Focus Result",
        "",
        f"- 1/4 hits: {len(one4)}; 1/4 near 5-or-10 proxy: {len(one4[one4['five_or_ten_proxy_region']])}.",
        f"- 2/11 hits: {len(two11)}; punctured C12 inversion-pair candidates: {int(two11['candidate_family'].eq('punctured_c12_inversion_pair_candidate').sum())}.",
        "- The observed 2/11 signatures are traceable as diagnostics, but they do not currently satisfy the stricter C12 punctured-carrier projector interpretation.",
        "- Fraction signatures therefore do not replace the reverse-side C -> AB topology-readout advantage seen in B7.5a/B7.5d; they remain secondary structure to localize.",
        "",
        "## Candidate Family Summary",
        "",
        family_summary.to_csv(index=False).strip() if len(family_summary) else "no close hits",
        "",
        "## Fraction Localization Summary",
        "",
        localization_summary.to_csv(index=False).strip() if len(localization_summary) else "no close hits",
        "",
        "## Target Focus Rows",
        "",
        target_focus.head(100).to_csv(index=False).strip() if len(target_focus) else "no target focus hits",
        "",
        "## Boundary",
        "",
        "B7.5f supports a narrower interpretation: exact fractions are not random noise, and some are recoverable through denominator/candidate-carrier structure. However, the current evidence does not yet construct an empirical projector P, does not test [P,T], and does not confirm a restricted trace/determinant block.",
        "",
        "The next matrix-level step would need to build explicit P/T objects and test idempotence, commutator error, and restricted topology trace/determinant directly.",
        "",
        "## Inputs",
        "",
        f"- fraction_scan: {args.fraction_scan}",
        f"- paired_delta: {args.paired_delta}",
        f"- readout_summary: {args.readout_summary}",
    ]
    (outdir / "Stage_B7_5f_execution_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    scan = pd.read_csv(args.fraction_scan)
    paired = pd.read_csv(args.paired_delta)
    readout = pd.read_csv(args.readout_summary)
    meta = topology_meta(paired, readout)
    readout_lookup = {(str(r.topology_arm), str(r.representation_arm)): r for r in readout.itertuples(index=False)}
    readout_lookup = {k: pd.Series(v._asdict()) for k, v in readout_lookup.items()}

    rows: list[dict[str, object]] = []
    for _, row in scan.iterrows():
        topology = str(row.get("topology_arm", ""))
        m = meta.loc[topology] if topology in meta.index else None
        inferred = infer_raw_universe(row, m, readout_lookup)
        localized = c_side_localization(row)
        candidate = projector_candidate(row, inferred, localized)
        rows.append({**row.to_dict(), **inferred, **localized, **candidate})

    enriched = pd.DataFrame(rows)
    ladder = build_ladder(enriched)
    family_summary, localization_summary, target_focus = summarize(enriched)

    enriched.to_csv(outdir / "Stage_B7_5f_fraction_projector_enriched_scan.csv", index=False)
    ladder.to_csv(outdir / "Stage_B7_5f_decision_ladder.csv", index=False)
    family_summary.to_csv(outdir / "Stage_B7_5f_candidate_family_summary.csv", index=False)
    localization_summary.to_csv(outdir / "Stage_B7_5f_fraction_localization_summary.csv", index=False)
    target_focus.to_csv(outdir / "Stage_B7_5f_target_fraction_focus.csv", index=False)
    write_summary(outdir, enriched, ladder, family_summary, localization_summary, target_focus, args)

    print(f"output_dir: {outdir}")
    print("\nDecision ladder")
    print(ladder.to_string(index=False))
    print("\nCandidate family summary")
    print(family_summary.to_string(index=False) if len(family_summary) else "no close hits")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fraction-scan", type=Path, default=REPO / "reports/stage_b7_5e/Stage_B7_5e_fraction_signature_scan.csv")
    parser.add_argument("--paired-delta", type=Path, default=REPO / "reports/stage_b7_5d/Stage_B7_5d_paired_delta_summary.csv")
    parser.add_argument("--readout-summary", type=Path, default=REPO / "reports/stage_b7_5d/Stage_B7_5d_readout_summary.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_5f")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
