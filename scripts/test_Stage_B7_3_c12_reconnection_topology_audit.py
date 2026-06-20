#!/usr/bin/env python3
"""Stage B7.3 C12/H24 reconnection topology audit."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
from collections import Counter
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path("/Users/satoru/Documents/Codex/2026-06-09/dear-marcel-luke-all-b5-2/IDPC_D12RG_Collaboration")
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import test_Stage_B7_1a_ab_history_control_validity as b71a  # noqa: E402
import test_Stage_B7_2g_receiver_standpoint_parity_audit as b72g  # noqa: E402


C_REPRESENTATIONS = [
    "scalar_c",
    "directed_c",
    "receiver_only_c",
    "magnitude_only_c",
    "receiver_magnitude_c",
    "standpoint_inversion_c",
    "receiver_standpoint_magnitude_c",
    "endpoint_o1o2_reference",
]

TOPOLOGY_ARMS = [
    "no_topology_baseline",
    "c12_1_2",
    "c12_reversed",
    "c12_side_broken",
    "c8_1",
    "h24_minimum_factorisation_suite_168",
    "h24_effective_ring_edges_144",
    "h24_c8_stitched_derived_216",
    "h24_degree_matched_null",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def zscore(values: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    mu = np.nanmean(arr)
    sd = np.nanstd(arr)
    if not np.isfinite(sd) or sd <= 1e-12:
        return np.zeros_like(arr, dtype=float)
    return (arr - mu) / sd


def p_greater(observed: float, controls: np.ndarray | list[float]) -> float:
    arr = np.asarray(controls, dtype=float)
    arr = arr[np.isfinite(arr)]
    if not np.isfinite(observed) or len(arr) == 0:
        return np.nan
    return float((1.0 + np.sum(arr >= observed)) / (len(arr) + 1.0))


def sign_switch_mask(series: pd.Series) -> pd.Series:
    vals = pd.to_numeric(series, errors="coerce")
    prev = vals.shift(1)
    return vals.notna() & prev.notna() & (np.sign(vals) != np.sign(prev)) & (np.sign(vals) != 0) & (np.sign(prev) != 0)


def unique_edges(n_nodes: int, jumps: tuple[int, ...]) -> list[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for i in range(n_nodes):
        for jump in jumps:
            j = (i + jump) % n_nodes
            if i != j:
                edges.add((i, j))
    return sorted(edges)


def ring_edges(seq: tuple[int, ...]) -> list[tuple[int, int]]:
    if len(seq) < 2:
        return []
    return [(src, seq[(i + 1) % len(seq)]) for i, src in enumerate(seq)]


def normalize_cycle(seq: tuple[int, ...]) -> tuple[int, ...]:
    seq = tuple(seq)
    return min(seq[i:] + seq[:i] for i in range(len(seq))) if seq else seq


def split_ring(seq: tuple[int, ...], parts: int) -> list[tuple[int, ...]]:
    if len(seq) % parts:
        raise ValueError("bad H24 split")
    return [tuple(seq[offset::parts]) for offset in range(parts)]


def unordered_factorisations(n: int, start: int = 2) -> list[tuple[int, ...]]:
    out = [(n,)]
    f = start
    while f * f <= n:
        if n % f == 0:
            for rest in unordered_factorisations(n // f, f):
                out.append((f,) + rest)
        f += 1
    return out


def ordered_factorisation_paths(n: int) -> list[tuple[int, ...]]:
    paths = []
    for fac in unordered_factorisations(n):
        paths.extend(set(itertools.permutations(fac)))
    return sorted(set(paths), key=lambda x: (len(x), x))


def h24_ring_inventory() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rings: dict[tuple[int, ...], dict[str, object]] = {}
    splits = []
    paths = ordered_factorisation_paths(24)

    def add_ring(seq: tuple[int, ...], path: str, level: int, role: str) -> str:
        key = normalize_cycle(seq)
        if key not in rings:
            ring_id = f"R{len(rings) + 1:04d}"
            rings[key] = {
                "ring_id": ring_id,
                "length": len(key),
                "residues": ";".join(str(x) for x in key),
                "source_paths": set(),
                "levels": set(),
                "roles": set(),
                "parent_ids": set(),
                "child_ids": set(),
            }
        row = rings[key]
        row["source_paths"].add(path)
        row["levels"].add(str(level))
        row["roles"].add(role)
        return str(row["ring_id"])

    by_id: dict[str, dict[str, object]] = {}
    for path in paths:
        label = "*".join(str(x) for x in path)
        full = tuple(range(24))
        full_id = add_ring(full, label, 0, "full_carrier")
        by_id = {str(v["ring_id"]): v for v in rings.values()}
        if len(path) == 1:
            continue
        current = [(full, full_id)]
        for level, parts in enumerate(path[:-1], start=1):
            next_current = []
            for seq, parent_id in current:
                for child in split_ring(seq, parts):
                    role = "leaf_ring" if level == len(path) - 1 else "intermediate_ring"
                    child_id = add_ring(child, label, level, role)
                    by_id = {str(v["ring_id"]): v for v in rings.values()}
                    by_id[parent_id]["child_ids"].add(child_id)
                    by_id[child_id]["parent_ids"].add(parent_id)
                    splits.append({"path": label, "level": level, "split_parts": parts, "parent_id": parent_id, "child_id": child_id})
                    next_current.append((child, child_id))
            current = next_current

    rows = []
    for row in rings.values():
        rows.append({
            "ring_id": row["ring_id"],
            "length": row["length"],
            "residues": row["residues"],
            "source_paths": ";".join(sorted(row["source_paths"])),
            "levels": ";".join(sorted(row["levels"])),
            "roles": ";".join(sorted(row["roles"])),
            "parent_ids": ";".join(sorted(row["parent_ids"])),
            "child_ids": ";".join(sorted(row["child_ids"])),
        })
    ring_df = pd.DataFrame(rows)
    split_df = pd.DataFrame(splits)
    req = pd.DataFrame([
        {
            "path": "*".join(str(x) for x in path),
            "factor_count": len(path),
            "leaf_ring_length": path[-1],
            "leaf_ring_count": int(np.prod(path[:-1])) if len(path) > 1 else 1,
            "ordinary_d24": "yes",
            "routing": "full_j_square",
        }
        for path in paths
    ])
    return ring_df, split_df, req


def parse_residues(text: object) -> tuple[int, ...]:
    return tuple(int(x) for x in str(text).split(";") if x != "")


def edges_from_rings(rings: pd.DataFrame) -> set[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for _, row in rings.iterrows():
        edges.update(ring_edges(parse_residues(row["residues"])))
    return edges


def h24_edge_sets() -> dict[str, list[tuple[int, int]]]:
    rings, _, _ = h24_ring_inventory()
    literal = sorted(edges_from_rings(rings))
    effective = sorted(edges_from_rings(rings[~rings["length"].eq(8)].copy()))
    c8 = rings[rings["length"].eq(8)].copy()
    stitched = list(effective)
    for _, row in c8.iterrows():
        for offset in range(24):
            stitched.append((offset, (offset + 3) % 24))
    return {
        "h24_minimum_factorisation_suite_168": literal,
        "h24_effective_ring_edges_144": effective,
        "h24_c8_stitched_derived_216": stitched,
    }


def edge_hash(edges: list[tuple[int, int]] | set[tuple[int, int]]) -> str:
    text = "\n".join(f"{i},{j}" for i, j in sorted(list(edges))) + "\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def topology_edges(name: str, rng: np.random.Generator) -> tuple[int, list[tuple[int, int]], str]:
    b3 = load_module("b3_for_b73", SCRIPTS / "test_Stage_B3_endogenous_event_carrier_readout.py")
    if name == "no_topology_baseline":
        return 12, [], "12 nodes with no coupling edges"
    if name == "c12_1_2":
        _, n, edges, _, notes = b3.topology_definition("C12(1,2)")
        return n, edges, notes
    if name == "c12_reversed":
        _, n, edges, _, _ = b3.topology_definition("C12(1,2)")
        return n, sorted((j, i) for i, j in edges), "C12(1,2) with all directed arrows reversed"
    if name == "c12_side_broken":
        _, n, edges, _, _ = b3.topology_definition("C12(1,2)")
        return n, b3.degree_matched_random_edges(n, edges, rng), "degree-matched C12 side-correspondence-broken control"
    if name == "c8_1":
        _, n, edges, _, notes = b3.topology_definition("C8(1)")
        return n, edges, notes
    h24 = h24_edge_sets()
    if name == "h24_degree_matched_null":
        edges = h24["h24_minimum_factorisation_suite_168"]
        return 24, b3.degree_matched_random_edges(24, edges, rng), "degree-matched random graph for canonical H24 168"
    if name in h24:
        return 24, list(h24[name]), "H24 deterministic factorisation-suite carrier"
    raise ValueError(f"unknown topology {name}")


def load_b72_features(args: argparse.Namespace) -> pd.DataFrame:
    b72c = b72g.load_b72c()
    b72b = b72c.load_b72b()
    b6p = b71a.load_module("b6p_for_b73", b71a.B6P_SCRIPT)
    b6l, table = b6p.build_table(b71a.build_args(args))
    left = b72g.add_features(table, b72c, b72b, "A_to_C_to_B", args.seed).add_prefix("ab__")
    right = b72g.add_features(table, b72c, b72b, "B_to_C_to_A", args.seed + 1).add_prefix("ba__")
    base = table[["label", "idx_in_session", "phase", "strength", "C_memory_scalar", "O1_lag0_AB_raw", "O2_lag5_AB_raw"]].copy()
    for col in [
        "receiver_side",
        "sender_side",
        "standpoint_polarity",
        "inverted_standpoint_polarity",
        "standpoint_magnitude",
        "inverted_standpoint_magnitude",
    ]:
        base[f"ab_{col}"] = pd.to_numeric(left[f"ab__{col}"], errors="coerce")
        base[f"ba_{col}"] = pd.to_numeric(right[f"ba__{col}"], errors="coerce")
    return base


def add_representation_scores(data: pd.DataFrame) -> pd.DataFrame:
    out = data.copy()
    out["scalar_c"] = zscore(out["C_memory_scalar"])
    out["directed_c"] = zscore(out["ab_receiver_side"] - out["ba_receiver_side"])
    out["receiver_only_c"] = zscore(np.nanmean(np.vstack([np.abs(out["ab_receiver_side"]), np.abs(out["ba_receiver_side"])]), axis=0))
    out["magnitude_only_c"] = zscore(np.nanmean(np.vstack([out["ab_standpoint_magnitude"], out["ba_standpoint_magnitude"]]), axis=0))
    out["receiver_magnitude_c"] = zscore(out["receiver_only_c"] + out["magnitude_only_c"])
    out["standpoint_inversion_c"] = zscore(
        np.nanmean(
            np.vstack([
                np.abs(out["ab_standpoint_polarity"] - out["ab_inverted_standpoint_polarity"]),
                np.abs(out["ba_standpoint_polarity"] - out["ba_inverted_standpoint_polarity"]),
            ]),
            axis=0,
        )
    )
    out["receiver_standpoint_magnitude_c"] = zscore(out["receiver_magnitude_c"] + out["standpoint_inversion_c"])
    out["endpoint_o1o2_reference"] = zscore(np.abs(out["O1_lag0_AB_raw"]) + np.abs(out["O2_lag5_AB_raw"]))
    return out


def event_rows_for_rep(data: pd.DataFrame, rep: str, q: float) -> pd.DataFrame:
    rows = []
    for label, sub in data.sort_values(["label", "idx_in_session"]).groupby("label", sort=False):
        score = pd.to_numeric(sub[rep], errors="coerce")
        cut = score.quantile(q)
        chosen = sub[score.ge(cut)].copy()
        for _, row in chosen.iterrows():
            rows.append({
                "event_class": rep,
                "label": str(label),
                "task_idx": float(row["idx_in_session"]),
                "phase": float(row["phase"]) if pd.notna(row["phase"]) else 0.0,
                "strength": float(abs(row[rep])) if pd.notna(row[rep]) else 1.0,
                "event_rule": f"per-label top {q:.2f} of {rep}",
            })
    return pd.DataFrame(rows)


def build_event_schedule(rows: pd.DataFrame, steps: int, n_nodes: int) -> tuple[list[dict[str, float]], dict[str, float]]:
    if rows.empty:
        return [], {"n_events": 0, "mean_strength": np.nan, "total_impulse_budget": np.nan}
    min_task = float(rows["task_idx"].min())
    max_task = float(rows["task_idx"].max())
    denom = max(max_task - min_task, 1.0)
    schedule = []
    for ordinal, (_, row) in enumerate(rows.sort_values(["label", "task_idx"]).iterrows()):
        frac = (float(row["task_idx"]) - min_task) / denom
        step = int(np.clip(round(frac * (steps - 1)), 0, steps - 1))
        phase = float(row.get("phase", 0.0))
        target = int(np.mod(round((np.mod(phase, 2.0 * np.pi) / (2.0 * np.pi)) * n_nodes), n_nodes))
        schedule.append({"step": step, "strength": max(abs(float(row["strength"])), 1e-9), "target": target, "ordinal": ordinal})
    strengths = np.asarray([x["strength"] for x in schedule], dtype=float)
    if np.nanmax(strengths) > np.nanmin(strengths):
        scaled = 0.05 + 0.15 * (strengths - np.nanmin(strengths)) / (np.nanmax(strengths) - np.nanmin(strengths))
    else:
        scaled = np.full_like(strengths, 0.10)
    for item, strength in zip(schedule, scaled):
        item["strength"] = float(strength)
    return schedule, {"n_events": len(schedule), "mean_strength": float(np.mean(scaled)), "total_impulse_budget": float(np.sum(scaled))}


def shifted_schedule(schedule: list[dict[str, float]], steps: int, shift: int) -> list[dict[str, float]]:
    return [{**item, "step": int((item["step"] + shift) % steps)} for item in schedule]


def random_schedule(schedule: list[dict[str, float]], steps: int, rng: np.random.Generator) -> list[dict[str, float]]:
    steps_random = rng.choice(np.arange(steps), size=len(schedule), replace=len(schedule) > steps)
    return [{**item, "step": int(step)} for item, step in zip(schedule, steps_random)]


def simulate_many(n_nodes: int, edges: list[tuple[int, int]], schedule: list[dict[str, float]], args: argparse.Namespace, rng: np.random.Generator) -> tuple[np.ndarray, dict[str, float]]:
    b3 = load_module("b3_sim_for_b73", SCRIPTS / "test_Stage_B3_endogenous_event_carrier_readout.py")
    values = []
    metrics = []
    for _ in range(args.n_runs):
        metric = b3.simulate_event_conditioned(n_nodes, edges, schedule, int(rng.integers(0, 2**31 - 1)), steps=args.steps)
        metrics.append(metric)
        values.append(metric.get("differentiated_recovery", np.nan))
    return np.asarray(values, dtype=float), b3.average_dicts(metrics)


def run_topology_audit(events_by_rep: dict[str, pd.DataFrame], args: argparse.Namespace) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed + 73)
    rows = []
    for rep, events in events_by_rep.items():
        for topology in TOPOLOGY_ARMS:
            n_nodes, edges, notes = topology_edges(topology, rng)
            schedule, meta = build_event_schedule(events, args.steps, n_nodes)
            shifted = shifted_schedule(schedule, args.steps, max(7, args.steps // 5))
            random_event = random_schedule(schedule, args.steps, rng)
            endogenous_values, endogenous_avg = simulate_many(n_nodes, edges, schedule, args, rng)
            shifted_values, _ = simulate_many(n_nodes, edges, shifted, args, rng)
            random_values, _ = simulate_many(n_nodes, edges, random_event, args, rng)
            obs = float(np.nanmean(endogenous_values))
            rows.append({
                "c_representation": rep,
                "topology_arm": topology,
                "n_nodes": n_nodes,
                "n_directed_edges": len(edges),
                "topology_notes": notes,
                "n_seed_events": meta["n_events"],
                "mean_seed_strength": meta["mean_strength"],
                "total_impulse_budget": meta["total_impulse_budget"],
                "mean_bounded_differentiated_recovery": obs,
                "sd_bounded_differentiated_recovery": float(np.nanstd(endogenous_values)),
                "effect_vs_time_shifted": obs - float(np.nanmean(shifted_values)),
                "effect_vs_random_event": obs - float(np.nanmean(random_values)),
                "p_vs_time_shifted_and_random": p_greater(obs, np.r_[shifted_values, random_values]),
                **endogenous_avg,
            })
    return pd.DataFrame(rows)


def add_effect_contrasts(results: pd.DataFrame) -> pd.DataFrame:
    out = results.copy()
    lookup = out.set_index(["c_representation", "topology_arm"])["mean_bounded_differentiated_recovery"].to_dict()
    for contrast in ["no_topology_baseline", "c8_1", "c12_reversed", "c12_side_broken", "h24_effective_ring_edges_144", "h24_degree_matched_null", "h24_minimum_factorisation_suite_168"]:
        out[f"effect_vs_{contrast}"] = [
            row.mean_bounded_differentiated_recovery - lookup.get((row.c_representation, contrast), np.nan)
            for row in out.itertuples(index=False)
        ]
    return out


def classify(results: pd.DataFrame) -> pd.DataFrame:
    rows = []
    def row(rep: str, topo: str) -> pd.Series | None:
        sub = results[results["c_representation"].eq(rep) & results["topology_arm"].eq(topo)]
        return None if sub.empty else sub.iloc[0]

    c12_supported = False
    h24_supported = False
    best_topology_specific = None
    for rep in C_REPRESENTATIONS:
        c12 = row(rep, "c12_1_2")
        h24 = row(rep, "h24_minimum_factorisation_suite_168")
        if c12 is not None:
            ok = (
                c12["effect_vs_no_topology_baseline"] > 0
                and c12["effect_vs_c8_1"] > 0
                and c12["effect_vs_c12_reversed"] > 0
                and c12["effect_vs_c12_side_broken"] > 0
                and c12["p_vs_time_shifted_and_random"] <= 0.05
            )
            c12_supported = c12_supported or bool(ok)
        if h24 is not None:
            ok = (
                h24["effect_vs_no_topology_baseline"] > 0
                and h24["effect_vs_h24_effective_ring_edges_144"] > 0
                and h24["effect_vs_h24_degree_matched_null"] > 0
                and h24["p_vs_time_shifted_and_random"] <= 0.05
            )
            h24_supported = h24_supported or bool(ok)
        candidates = results[(results["c_representation"].eq(rep)) & (results["topology_arm"].isin(["c12_1_2", "h24_minimum_factorisation_suite_168"]))]
        if not candidates.empty:
            best = candidates.sort_values("mean_bounded_differentiated_recovery", ascending=False).iloc[0]
            if best_topology_specific is None or best["mean_bounded_differentiated_recovery"] > best_topology_specific["mean_bounded_differentiated_recovery"]:
                best_topology_specific = best

    def mean_for(rep: str, topo: str) -> float:
        r = row(rep, topo)
        return np.nan if r is None else float(r["mean_bounded_differentiated_recovery"])

    coupled = mean_for("receiver_standpoint_magnitude_c", "c12_1_2")
    simpler = max(
        mean_for("scalar_c", "c12_1_2"),
        mean_for("receiver_only_c", "c12_1_2"),
        mean_for("magnitude_only_c", "c12_1_2"),
        mean_for("receiver_magnitude_c", "c12_1_2"),
    )
    endpoint_best = results[results["c_representation"].eq("endpoint_o1o2_reference")]["mean_bounded_differentiated_recovery"].max()
    endpoint_free_best = results[~results["c_representation"].eq("endpoint_o1o2_reference")]["mean_bounded_differentiated_recovery"].max()
    h168 = results[results["topology_arm"].eq("h24_minimum_factorisation_suite_168")].set_index("c_representation")
    h216 = results[results["topology_arm"].eq("h24_c8_stitched_derived_216")].set_index("c_representation")
    hdiff = max(abs(float(h168.loc[rep, "mean_bounded_differentiated_recovery"]) - float(h216.loc[rep, "mean_bounded_differentiated_recovery"])) for rep in sorted(set(h168.index) & set(h216.index)))

    rows.extend([
        ("c12_incremental_gain_supported", c12_supported, "C12 beats no-topology, C8, reversed, and side-broken under at least one frozen C representation"),
        ("h24_168_incremental_gain_supported", h24_supported, "canonical H24 168 beats no-topology, H24-144, and H24 degree-null under at least one frozen C representation"),
        ("h24_216_differs_from_168", bool(hdiff >= 0.005), f"max absolute 216-vs-168 mean recovery difference = {hdiff:.6f}"),
        ("coupled_receiver_standpoint_magnitude_bridge_supported", bool(np.isfinite(coupled) and coupled > simpler), f"coupled C12 mean {coupled:.6f}; simpler best {simpler:.6f}"),
        ("endpoint_o1o2_reference_remains_upper_bound", bool(endpoint_best > endpoint_free_best), f"endpoint best {endpoint_best:.6f}; endpoint-free best {endpoint_free_best:.6f}"),
        ("c12_reconnection_not_supported", not c12_supported, "no C12 topology arm satisfied the incremental decision rule"),
        ("h24_reconnection_not_supported", not h24_supported, "canonical H24 168 did not satisfy the incremental decision rule"),
    ])
    unresolved = not c12_supported and not h24_supported
    rows.append(("unresolved_c12_h24_boundary", unresolved, "neither C12 nor canonical H24 passed the preregistered incremental rule"))
    return pd.DataFrame([{"criterion": c, "supported": bool(s), "basis": b} for c, s, b in rows])


def write_h24_files(outdir: Path) -> pd.DataFrame:
    edges = h24_edge_sets()
    rows = []
    for name, edge_set in edges.items():
        path = outdir / f"Stage_B7_3_{name}_edges.csv"
        pd.DataFrame(edge_set, columns=["src", "dst"]).to_csv(path, index=False)
        rows.append({"edge_set": name, "n_edges": len(edge_set), "sha256": edge_hash(edge_set), "file": path.name})
    c216 = Counter(edges["h24_c8_stitched_derived_216"])
    c168 = Counter(edges["h24_minimum_factorisation_suite_168"])
    added = []
    removed = []
    for edge in sorted(set(c216) | set(c168)):
        delta = c216[edge] - c168[edge]
        target = added if delta > 0 else removed
        for _ in range(abs(delta)):
            if delta:
                target.append(edge)
    pd.DataFrame(added, columns=["src", "dst"]).to_csv(outdir / "Stage_B7_3_E216_minus_E168.csv", index=False)
    pd.DataFrame(removed, columns=["src", "dst"]).to_csv(outdir / "Stage_B7_3_E168_minus_E216.csv", index=False)
    rows.extend([
        {"edge_set": "E216_minus_E168", "n_edges": len(added), "sha256": edge_hash(added), "file": "Stage_B7_3_E216_minus_E168.csv"},
        {"edge_set": "E168_minus_E216", "n_edges": len(removed), "sha256": edge_hash(removed), "file": "Stage_B7_3_E168_minus_E216.csv"},
    ])
    rings, splits, req = h24_ring_inventory()
    rings.to_csv(outdir / "Stage_B7_3_h24_ring_inventory.csv", index=False)
    splits.to_csv(outdir / "Stage_B7_3_h24_split_inventory.csv", index=False)
    req.to_csv(outdir / "Stage_B7_3_h24_factorisation_requirements.csv", index=False)
    return pd.DataFrame(rows)


def write_summary(path: Path, results: pd.DataFrame, classification: pd.DataFrame, edge_manifest: pd.DataFrame, args: argparse.Namespace) -> None:
    top = results.sort_values("mean_bounded_differentiated_recovery", ascending=False).head(20)
    lines = [
        "# Stage B7.3 C12 Reconnection and H24 Topology Falsification Audit",
        "",
        "Status: executed after Stage_B7_3_preregistration.md.",
        "",
        "## Primary Classification",
        "",
        classification.to_csv(index=False).strip(),
        "",
        "## Top Results",
        "",
        top[[
            "c_representation",
            "topology_arm",
            "n_nodes",
            "n_directed_edges",
            "n_seed_events",
            "mean_bounded_differentiated_recovery",
            "effect_vs_no_topology_baseline",
            "effect_vs_time_shifted",
            "effect_vs_random_event",
            "p_vs_time_shifted_and_random",
        ]].to_csv(index=False).strip(),
        "",
        "## H24 Edge Manifest",
        "",
        edge_manifest.to_csv(index=False).strip(),
        "",
        "## Settings",
        "",
        f"- event_quantile: {args.event_quantile}",
        f"- steps: {args.steps}",
        f"- n_runs: {args.n_runs}",
        f"- seed: {args.seed}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    features = add_representation_scores(load_b72_features(args))
    features.to_csv(outdir / "Stage_B7_3_c_representation_scores.csv", index=False)
    events_by_rep = {rep: event_rows_for_rep(features, rep, args.event_quantile) for rep in C_REPRESENTATIONS}
    events = pd.concat(events_by_rep.values(), ignore_index=True)
    events.to_csv(outdir / "Stage_B7_3_c_representation_events.csv", index=False)
    edge_manifest = write_h24_files(outdir)
    results = add_effect_contrasts(run_topology_audit(events_by_rep, args))
    classification = classify(results)
    results.to_csv(outdir / "Stage_B7_3_topology_results.csv", index=False)
    classification.to_csv(outdir / "Stage_B7_3_primary_classification.csv", index=False)
    edge_manifest.to_csv(outdir / "Stage_B7_3_h24_edge_manifest.csv", index=False)
    write_summary(outdir / "Stage_B7_3_preregistered_summary.md", results, classification, edge_manifest, args)
    print("\nStage B7.3 audit")
    print(f"- output_dir: {outdir}")
    print("\nClassification")
    print(classification.to_string(index=False))
    print("\nTop results")
    print(results.sort_values("mean_bounded_differentiated_recovery", ascending=False).head(12)[["c_representation", "topology_arm", "mean_bounded_differentiated_recovery", "effect_vs_no_topology_baseline", "p_vs_time_shifted_and_random"]].to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_3")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--min-state-events", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.35)
    parser.add_argument("--n-random-draws", type=int, default=200)
    parser.add_argument("--n-control-draws", type=int, default=500)
    parser.add_argument("--n-perm", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--event-quantile", type=float, default=0.75)
    parser.add_argument("--steps", type=int, default=240)
    parser.add_argument("--n-runs", type=int, default=80)
    parser.add_argument("--seed", type=int, default=73073)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
