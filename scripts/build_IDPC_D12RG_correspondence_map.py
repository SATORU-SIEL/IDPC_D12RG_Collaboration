#!/usr/bin/env python3
"""Build the fixed IDPC-D12RG correspondence map and data inventory.

This script prepares the fixed correspondence table used by later IDPC x D12RG
readout tests and inventories candidate IDPC-derived CSV files for public
structural-layer testing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import pandas as pd


CORRESPONDENCES = [
    {
        "idpc_structure": "non-closed O3",
        "luke_structure": "non-literal normalized closure",
        "connection_hypothesis": (
            "IDPC's internally non-closed but empirically realized "
            "correspondence may match D12RG readout closure without literal "
            "closure"
        ),
        "priority": "high",
        "candidate_files": (
            "Chapter7/new_phi_dataset.csv; "
            "Chapter7/best_true_search_scored_points.csv; "
            "Chapter7/block_permutation_test.csv; "
            "Chapter7/temporal_shift_test.csv"
        ),
        "candidate_columns": "phi; dphi; deltaC_gain; switch_gain; winner; sharp",
        "primary_nulls": "block permutation; temporal shift; train/test split",
        "avoid": "literal closure assumption",
    },
    {
        "idpc_structure": "phi localized selection",
        "luke_structure": "normalized readout closure",
        "connection_hypothesis": (
            "localized selection in phi phase space may be re-described as a "
            "golden-carrier normalized readout"
        ),
        "priority": "high",
        "candidate_files": (
            "Chapter7/new_phi_dataset.csv; "
            "Chapter7/best_true_search_scored_points.csv; "
            "Chapter7/true_search_train_only_vs_quantum.csv"
        ),
        "candidate_columns": (
            "phi; dphi; phi_clean; phi_latent; sharp; deltaC_gain"
        ),
        "primary_nulls": "block permutation; temporal shift; alternative ladders",
        "avoid": "best phase offset or best lag search",
    },
    {
        "idpc_structure": "FES 5-state structure",
        "luke_structure": "primitive trace defect 5",
        "connection_hypothesis": (
            "Five Energy Star may structurally correspond to trace defect 5"
        ),
        "priority": "medium-high",
        "candidate_files": (
            "event_level_with_fes_phase_TRUE_RICCI.csv; "
            "event_level_with_clusters_TRUE_RICCI__HYBRID_PHI.csv; "
            "fes_phase_summary_TRUE_RICCI__HYBRID_PHI.csv"
        ),
        "candidate_columns": "fes_phase; cluster; phase; phase_z",
        "primary_nulls": (
            "state relabeling; transition-count-preserving null; "
            "session-aware null"
        ),
        "avoid": "mere numerology around the number 5",
    },
    {
        "idpc_structure": "FES transitions",
        "luke_structure": "5->10->20 normalization ladder",
        "connection_hypothesis": (
            "5-state structure may expand into 10 directed transitions or "
            "20 oriented/entry-exit transitions"
        ),
        "priority": "medium",
        "candidate_files": (
            "event_level_with_fes_phase_TRUE_RICCI.csv; "
            "fes_assignment_log_TRUE_RICCI__HYBRID_PHI.csv"
        ),
        "candidate_columns": "fes_phase; cluster; J; J_tilde; distance; r_local",
        "primary_nulls": (
            "random relabeling; transition-preserving null; block/session null"
        ),
        "avoid": "interval-only matching",
    },
    {
        "idpc_structure": "boundary impulse J",
        "luke_structure": "trace defect / ladder step",
        "connection_hypothesis": (
            "boundary impulse and phase compression may align with normalized "
            "shells related to trace defect or ladder steps"
        ),
        "priority": "medium",
        "candidate_files": (
            "J_dh_kappa_pooled_v2.csv; "
            "event_level_raw_table_TRUE_RICCI__HYBRID_PHI.csv; "
            "event_level_with_fes_phase_TRUE_RICCI.csv"
        ),
        "candidate_columns": "J; dphi; J_tilde; g_t; distance; phase; r_local",
        "primary_nulls": (
            "boundary-label shuffle; within-session circular shift; block null; "
            "alternative shells"
        ),
        "avoid": "retuning shell scale to target",
    },
    {
        "idpc_structure": "residual contraction",
        "luke_structure": "normalized closure",
        "connection_hypothesis": (
            "phase or structural residual may contract at readout-level closure "
            "positions"
        ),
        "priority": "high",
        "candidate_files": (
            "Chapter3/ricci_phase_sync_summary.csv; "
            "Chapter3/ricci_eps72_restoring_test.csv; "
            "event_level_with_fes_phase_TRUE_RICCI.csv"
        ),
        "candidate_columns": (
            "phase; phase_z; distance; distance_z; r_local; r_local_z; "
            "eps72_deg; deps72_deg"
        ),
        "primary_nulls": (
            "rotation controls; alternative cyclic partitions; "
            "session-preserving null"
        ),
        "avoid": "phase-bin-only test",
    },
    {
        "idpc_structure": "Ricci phase synchronization",
        "luke_structure": "D12 readout phase",
        "connection_hypothesis": (
            "D12-like structure should be tested as residual closure rather "
            "than literal periodicity"
        ),
        "priority": "medium",
        "candidate_files": (
            "Chapter3/ricci_phase_sync_summary.csv; "
            "Chapter3/kuramoto_test_per_session_latest_riccisync.csv; "
            "event_level_with_fes_phase_TRUE_RICCI.csv"
        ),
        "candidate_columns": "circ_mean_deg; mean_abs_dpsi_deg; phase; phase_z",
        "primary_nulls": "session shuffle; phase rotation; block null",
        "avoid": "Kuramoto/topology rescue in first pass",
    },
]


def split_semicolon(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def find_candidate_files(input_root: Path, wanted: Iterable[str]) -> dict[str, list[Path]]:
    found: dict[str, list[Path]] = {}
    if not input_root.exists():
        return {name: [] for name in wanted}

    csv_files = list(input_root.rglob("*.csv"))
    for name in wanted:
        matches = [
            path for path in csv_files
            if str(path).endswith(name) or path.name == Path(name).name
        ]
        found[name] = sorted(matches)
    return found


def summarize_csv(path: Path) -> dict[str, object]:
    try:
        preview = pd.read_csv(path, nrows=200)
        full_rows = sum(1 for _ in path.open("rb")) - 1
    except Exception as exc:  # pragma: no cover - defensive for malformed CSVs
        return {
            "path": str(path),
            "readable": False,
            "error": repr(exc),
            "n_rows_estimate": None,
            "n_preview_rows": 0,
            "n_columns": 0,
            "columns": "",
            "numeric_columns": "",
        }

    numeric_columns = [
        col for col in preview.columns
        if pd.api.types.is_numeric_dtype(preview[col])
    ]
    return {
        "path": str(path),
        "readable": True,
        "error": "",
        "n_rows_estimate": max(full_rows, 0),
        "n_preview_rows": len(preview),
        "n_columns": len(preview.columns),
        "columns": "; ".join(map(str, preview.columns)),
        "numeric_columns": "; ".join(map(str, numeric_columns)),
    }


def display_path(path: Path, input_root: Path) -> str:
    try:
        return str(path.relative_to(input_root))
    except ValueError:
        return path.name


def build_inventory(input_root: Path, correspondences: list[dict[str, str]]) -> pd.DataFrame:
    all_candidate_names = sorted({
        name
        for row in correspondences
        for name in split_semicolon(row["candidate_files"])
    })
    found = find_candidate_files(input_root, all_candidate_names)

    rows: list[dict[str, object]] = []
    for correspondence in correspondences:
        wanted_columns = set(split_semicolon(correspondence["candidate_columns"]))
        for candidate_name in split_semicolon(correspondence["candidate_files"]):
            matches = found.get(candidate_name, [])
            if not matches:
                rows.append({
                    "idpc_structure": correspondence["idpc_structure"],
                    "luke_structure": correspondence["luke_structure"],
                    "priority": correspondence["priority"],
                    "candidate_file_pattern": candidate_name,
                    "matched_path": "",
                    "found": False,
                    "readable": False,
                    "n_rows_estimate": None,
                    "n_columns": None,
                    "columns": "",
                    "numeric_columns": "",
                    "matched_candidate_columns": "",
                    "missing_candidate_columns": "; ".join(sorted(wanted_columns)),
                    "eligibility_note": "candidate file not found under input root",
                })
                continue

            for path in matches:
                summary = summarize_csv(path)
                available = set(split_semicolon(str(summary.get("columns", ""))))
                matched_cols = sorted(wanted_columns & available)
                missing_cols = sorted(wanted_columns - available)
                rows.append({
                    "idpc_structure": correspondence["idpc_structure"],
                    "luke_structure": correspondence["luke_structure"],
                    "priority": correspondence["priority"],
                    "candidate_file_pattern": candidate_name,
                    "matched_path": display_path(path, input_root),
                    "found": True,
                    "readable": bool(summary["readable"]),
                    "n_rows_estimate": summary["n_rows_estimate"],
                    "n_columns": summary["n_columns"],
                    "columns": summary["columns"],
                    "numeric_columns": summary["numeric_columns"],
                    "matched_candidate_columns": "; ".join(matched_cols),
                    "missing_candidate_columns": "; ".join(missing_cols),
                    "eligibility_note": (
                        "usable candidate columns found"
                        if matched_cols else
                        "file found but no pre-registered candidate columns matched"
                    ),
                })
    return pd.DataFrame(rows)


def write_markdown_summary(
    output_path: Path,
    map_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    input_root: Path,
) -> None:
    found_rows = inventory_df[inventory_df["found"] == True]  # noqa: E712
    usable_rows = found_rows[
        found_rows["matched_candidate_columns"].astype(str).str.len() > 0
    ]
    lines = [
        "# IDPC-D12RG Correspondence Map Inventory",
        "",
        "## Purpose",
        "",
        (
            "This report fixes the initial IDPC-D12RG correspondence map and "
            "inventories candidate IDPC-derived CSV files."
        ),
        "",
        "## Input Root",
        "",
        f"`{input_root}`",
        "",
        "## Summary",
        "",
        f"- correspondence rows: {len(map_df)}",
        f"- inventory rows: {len(inventory_df)}",
        f"- matched file rows: {len(found_rows)}",
        f"- rows with usable pre-registered columns: {len(usable_rows)}",
        "",
        "## High-Priority Structures",
        "",
    ]
    high = map_df[map_df["priority"].isin(["high", "medium-high"])]
    for _, row in high.iterrows():
        lines.append(
            f"- {row['idpc_structure']} -> {row['luke_structure']}: "
            f"{row['connection_hypothesis']}"
        )
    lines.extend([
        "",
        "## Files Produced",
        "",
        "- `reports/IDPC_D12RG_correspondence_map.csv`",
        "- `reports/IDPC_D12RG_candidate_data_inventory.csv`",
        "- `reports/IDPC_D12RG_correspondence_inventory_summary.md`",
        "",
        "## Interpretation",
        "",
        (
            "This is a preregistration and discovery step for structural-layer "
            "tests. Later analyses should use these rows to avoid changing the "
            "target structure after seeing statistical results."
        ),
        "",
    ])
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-root",
        type=Path,
        default=Path("."),
        help="Root of a local IDPC_Reproduction checkout or output directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports"),
        help="Directory where report files are written.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    map_df = pd.DataFrame(CORRESPONDENCES)
    inventory_df = build_inventory(args.input_root, CORRESPONDENCES)

    map_path = args.output_dir / "IDPC_D12RG_correspondence_map.csv"
    inventory_path = args.output_dir / "IDPC_D12RG_candidate_data_inventory.csv"
    summary_path = args.output_dir / "IDPC_D12RG_correspondence_inventory_summary.md"
    metadata_path = args.output_dir / "IDPC_D12RG_theoretical_template.json"

    map_df.to_csv(map_path, index=False)
    inventory_df.to_csv(inventory_path, index=False)
    write_markdown_summary(summary_path, map_df, inventory_df, args.input_root)
    metadata_path.write_text(
        json.dumps(
            {
                "U_phi": [[0, 1], [-1, 3]],
                "trace_ladder_A0_to_A12": [
                    2, 3, 7, 18, 47, 123, 322,
                    843, 2207, 5778, 15127, 39603, 103682,
                ],
                "primitive_trace_defect": 5,
                "normalization_ladder": [5, 10, 20],
                "d12_readout": "readout-level structure only; do not assume U_phi^12 = I",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"wrote {map_path}")
    print(f"wrote {inventory_path}")
    print(f"wrote {summary_path}")
    print(f"wrote {metadata_path}")


if __name__ == "__main__":
    main()
