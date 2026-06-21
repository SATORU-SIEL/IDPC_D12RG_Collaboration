#!/usr/bin/env python3
"""Stage B7.3a C12 specificity and H24 collective-necessity audit."""

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


PRIMARY_R_STAR = "receiver_standpoint_magnitude_c"

C_REPRESENTATIONS = [
    PRIMARY_R_STAR,
    "directed_c",
    "receiver_only_c",
    "standpoint_inversion_c",
    "receiver_magnitude_c",
    "scalar_c",
    "endpoint_o1o2_reference",
]

TOPOLOGY_ARMS = [
    "no_topology_baseline",
    "c12_1_2",
    "c12_reversed",
    "c12_side_broken",
    "c12_shuffled",
    "c10",
    "c11",
    "c13",
    "c14",
    "c8_1",
    "topology_capacity_matched_null",
    "path_rewired_control",
    "h24_possible_factorisations_168",
    "h24_available_factorisations_junction_coupled",
    "h24_one_factorisation_class_removed",
    "h24_one_junction_family_broken",
    "h24_paths_available_but_mutually_disconnected",
    "h24_complete_factorisation_suite_coupled",
    "h24_degree_matched_null",
    "h24_216_diagnostic_only",
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
    if name == "c12_shuffled":
        _, n, edges, _, _ = b3.topology_definition("C12(1,2)")
        src = [i for i, _ in edges]
        dst = np.array([j for _, j in edges], dtype=int)
        rng.shuffle(dst)
        shuffled = sorted({(int(i), int(j)) for i, j in zip(src, dst) if int(i) != int(j)})
        while len(shuffled) < len(edges):
            i = int(rng.integers(0, n))
            j = int(rng.integers(0, n))
            if i != j:
                shuffled.append((i, j))
                shuffled = sorted(set(shuffled))
        return n, shuffled[: len(edges)], "C12 capacity-preserving target-shuffled control"
    if name in {"c10", "c11", "c13", "c14"}:
        n = int(name[1:])
        return n, unique_edges(n, (-2, -1, 1, 2)), f"C{n}(1,2) neighbouring-cycle control"
    if name == "c8_1":
        _, n, edges, _, notes = b3.topology_definition("C8(1)")
        return n, edges, notes
    if name == "topology_capacity_matched_null":
        _, n, edges, _, _ = b3.topology_definition("C12(1,2)")
        return n, b3.degree_matched_random_edges(n, edges, rng), "C12 node/edge-capacity matched null"
    if name == "path_rewired_control":
        _, n, edges, _, _ = b3.topology_definition("C12(1,2)")
        rewired = []
        for i, j in edges:
            rewired.append((i, (j + 5) % n))
        return n, sorted(set((i, j) for i, j in rewired if i != j)), "C12 path-rewired control preserving source nodes"
    h24 = h24_edge_sets()
    h168 = list(h24["h24_minimum_factorisation_suite_168"])
    h144 = list(h24["h24_effective_ring_edges_144"])
    junction = sorted(set(h168) - set(h144))
    if name == "h24_possible_factorisations_168":
        return 24, h168, "H24 possible-factorisations 168-edge carrier; static edge-level operationalization"
    if name == "h24_available_factorisations_junction_coupled":
        return 24, h168, "H24 available factorisations with current minimum junction coupling"
    if name == "h24_one_factorisation_class_removed":
        remove = set(h168[::7])
        return 24, sorted(set(h168) - remove), "H24 deterministic nonredundant-class-removal proxy; removes every seventh canonical edge"
    if name == "h24_one_junction_family_broken":
        keep_junction = set(junction[: len(junction) // 2])
        return 24, sorted(set(h144) | keep_junction), "H24 broken-junction proxy retaining effective rings and half of minimum junction edges"
    if name == "h24_paths_available_but_mutually_disconnected":
        return 24, h144, "H24 paths available as effective rings but mutually disconnected from C8 parent junction family"
    if name == "h24_complete_factorisation_suite_coupled":
        return 24, h168, "H24 complete operational factorisation suite with current minimum junction coupling"
    if name == "h24_degree_matched_null":
        return 24, b3.degree_matched_random_edges(24, h168, rng), "degree-matched random graph for canonical H24 168"
    if name == "h24_216_diagnostic_only":
        return 24, list(h24["h24_c8_stitched_derived_216"]), "H24 216-edge C8-stitched derived diagnostic-only carrier"
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
        topology_arms = TOPOLOGY_ARMS if rep == PRIMARY_R_STAR else ["no_topology_baseline", "c12_1_2"]
        for topology in topology_arms:
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
    for contrast in [
        "no_topology_baseline",
        "c8_1",
        "c10",
        "c11",
        "c13",
        "c14",
        "c12_reversed",
        "c12_side_broken",
        "c12_shuffled",
        "topology_capacity_matched_null",
        "path_rewired_control",
        "h24_possible_factorisations_168",
        "h24_available_factorisations_junction_coupled",
        "h24_one_factorisation_class_removed",
        "h24_one_junction_family_broken",
        "h24_paths_available_but_mutually_disconnected",
        "h24_complete_factorisation_suite_coupled",
        "h24_degree_matched_null",
    ]:
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

    def bh_q(p_values: list[float]) -> list[float]:
        p = np.asarray(p_values, dtype=float)
        q = np.full_like(p, np.nan)
        valid = np.isfinite(p)
        if not valid.any():
            return q.tolist()
        pv = p[valid]
        order = np.argsort(pv)
        ranked = pv[order]
        m = len(ranked)
        adjusted = np.minimum.accumulate((ranked * m / np.arange(1, m + 1))[::-1])[::-1]
        out = np.empty_like(pv)
        out[order] = np.clip(adjusted, 0.0, 1.0)
        q[valid] = out
        return q.tolist()

    family = [
        "c12_1_2",
        "c12_reversed",
        "c12_side_broken",
        "c12_shuffled",
        "c10",
        "c11",
        "c13",
        "c14",
        "c8_1",
        "topology_capacity_matched_null",
        "path_rewired_control",
    ]
    rstar_family = results[results["c_representation"].eq(PRIMARY_R_STAR) & results["topology_arm"].isin(family)].copy()
    q_lookup = {}
    if not rstar_family.empty:
        rstar_family["q_topology_family"] = bh_q(rstar_family["p_vs_time_shifted_and_random"].tolist())
        q_lookup = rstar_family.set_index("topology_arm")["q_topology_family"].to_dict()

    def mean_for(rep: str, topo: str) -> float:
        r = row(rep, topo)
        return np.nan if r is None else float(r["mean_bounded_differentiated_recovery"])

    c12 = row(PRIMARY_R_STAR, "c12_1_2")
    c12_specific_controls = [
        "no_topology_baseline",
        "c12_reversed",
        "c12_side_broken",
        "c12_shuffled",
        "c10",
        "c11",
        "c13",
        "c14",
    ]
    c12_reconnection = False
    c12_specificity = False
    directionality = False
    side_required = False
    neighbor_explains = False
    if c12 is not None:
        c12_reconnection = bool(c12["effect_vs_no_topology_baseline"] > 0 and c12["p_vs_time_shifted_and_random"] <= 0.05)
        control_effects = [float(c12[f"effect_vs_{ctrl}"]) for ctrl in c12_specific_controls if ctrl != "no_topology_baseline"]
        c12_specificity = bool(
            c12_reconnection
            and all(effect > 0 for effect in control_effects)
            and q_lookup.get("c12_1_2", 1.0) <= 0.05
        )
        directionality = bool(c12["effect_vs_c12_reversed"] > 0)
        side_required = bool(c12["effect_vs_c12_side_broken"] > 0)
        neighbor_explains = bool(any(float(c12[f"effect_vs_{ctrl}"]) <= 0 for ctrl in ["c10", "c11", "c13", "c14"]))

    endpoint_best = results[results["c_representation"].eq("endpoint_o1o2_reference")]["mean_bounded_differentiated_recovery"].max()
    endpoint_free_best = results[~results["c_representation"].eq("endpoint_o1o2_reference")]["mean_bounded_differentiated_recovery"].max()

    hfull = row(PRIMARY_R_STAR, "h24_complete_factorisation_suite_coupled")
    h_possible = row(PRIMARY_R_STAR, "h24_possible_factorisations_168")
    h_removed = row(PRIMARY_R_STAR, "h24_one_factorisation_class_removed")
    h_broken = row(PRIMARY_R_STAR, "h24_one_junction_family_broken")
    h_disconnected = row(PRIMARY_R_STAR, "h24_paths_available_but_mutually_disconnected")
    h_null = row(PRIMARY_R_STAR, "h24_degree_matched_null")
    h_collective = False
    h_possible_only = False
    h_available_not_required = False
    h_junction_required = False
    h_removal_degrades = False
    h_static_not_sufficient = False
    if hfull is not None:
        h_removal_degrades = h_removed is not None and float(hfull["mean_bounded_differentiated_recovery"]) > float(h_removed["mean_bounded_differentiated_recovery"])
        h_junction_required = h_broken is not None and float(hfull["mean_bounded_differentiated_recovery"]) > float(h_broken["mean_bounded_differentiated_recovery"])
        disconnected_degrades = h_disconnected is not None and float(hfull["mean_bounded_differentiated_recovery"]) > float(h_disconnected["mean_bounded_differentiated_recovery"])
        null_exceeded = h_null is not None and float(hfull["mean_bounded_differentiated_recovery"]) > float(h_null["mean_bounded_differentiated_recovery"])
        h_collective = bool(
            hfull["effect_vs_no_topology_baseline"] > 0
            and h_removal_degrades
            and h_junction_required
            and disconnected_degrades
            and null_exceeded
            and hfull["p_vs_time_shifted_and_random"] <= 0.05
        )
        h_possible_only = bool(h_possible is not None and float(h_possible["mean_bounded_differentiated_recovery"]) >= float(hfull["mean_bounded_differentiated_recovery"]))
        h_available_not_required = bool((not h_removal_degrades) or (not h_junction_required))
        h_static_not_sufficient = not h_collective

    rows.extend([
        ("c12_specificity_supported", c12_specificity, f"{PRIMARY_R_STAR} + c12_1_2 beats no-topology, reversed, side-broken, shuffled, C10/C11/C13/C14 and passes topology-family FDR"),
        ("c12_reconnection_without_specificity", bool(c12_reconnection and not c12_specificity), "C12 improves over no-topology but fails at least one specificity control"),
        ("c12_directionality_supported", directionality, "c12_1_2 exceeds c12_reversed for frozen R_star"),
        ("c12_directionality_not_isolated", not directionality, "c12_reversed is equal or stronger than c12_1_2 for frozen R_star"),
        ("neighboring_cycle_explains_effect", neighbor_explains, "at least one C10/C11/C13/C14 neighbouring cycle equals or exceeds C12 for frozen R_star"),
        ("side_correspondence_required", side_required, "c12_1_2 exceeds c12_side_broken for frozen R_star"),
        ("endpoint_o1o2_reclaims_upper_bound", bool(endpoint_best > endpoint_free_best), f"endpoint best {endpoint_best:.6f}; endpoint-free best {endpoint_free_best:.6f}"),
        ("scalar_c_rejected", bool(row("scalar_c", "c12_1_2") is not None and (row("scalar_c", "c12_1_2")["effect_vs_no_topology_baseline"] <= 0 or row("scalar_c", "c12_1_2")["p_vs_time_shifted_and_random"] > 0.05)), "scalar_c does not produce a significant C12 reconnection over controls"),
        ("unresolved_c12_specificity", not c12_specificity, "frozen R_star C12 specificity was not established under the full B7.3a control set"),
        ("h24_collective_necessity_supported", h_collective, "complete suite beats no-topology, removal, broken-junction, disconnected, and degree-null controls"),
        ("h24_possible_only_sufficient", h_possible_only, "possible/static 168 arm is equal or stronger than complete-suite-coupled arm"),
        ("h24_available_but_not_required", h_available_not_required, "removal or broken-junction controls did not degrade relative to complete-suite-coupled arm"),
        ("h24_junction_coupling_required", h_junction_required, "complete-suite-coupled exceeds one-junction-family-broken control"),
        ("h24_factorisation_removal_degrades", h_removal_degrades, "complete-suite-coupled exceeds one-factorisation-class-removed control"),
        ("h24_restoration_recovers", bool(h_removal_degrades and h_junction_required), "restoring the complete operational suite improves over both removal and broken-junction controls"),
        ("h24_static_topology_not_sufficient", h_static_not_sufficient, "current operational H24 edge-level suite did not satisfy collective necessity"),
        ("h24_168_current_carrier_not_supported", not h_collective, "current edge-level H24 carrier failed the collective-necessity rule"),
        ("h24_216_diagnostic_only", True, "216-edge C8-stitched object is retained only as a derived diagnostic arm"),
    ])
    rows.append(("unresolved_h24_boundary", not h_collective, "H24 collective necessity remains unresolved under the current operational edge-level implementation"))
    return pd.DataFrame([{"criterion": c, "supported": bool(s), "basis": b} for c, s, b in rows])


def write_h24_files(outdir: Path) -> pd.DataFrame:
    edges = h24_edge_sets()
    rows = []
    for name, edge_set in edges.items():
        path = outdir / f"Stage_B7_3a_{name}_edges.csv"
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
    pd.DataFrame(added, columns=["src", "dst"]).to_csv(outdir / "Stage_B7_3a_E216_minus_E168.csv", index=False)
    pd.DataFrame(removed, columns=["src", "dst"]).to_csv(outdir / "Stage_B7_3a_E168_minus_E216.csv", index=False)
    rows.extend([
        {"edge_set": "E216_minus_E168", "n_edges": len(added), "sha256": edge_hash(added), "file": "Stage_B7_3a_E216_minus_E168.csv"},
        {"edge_set": "E168_minus_E216", "n_edges": len(removed), "sha256": edge_hash(removed), "file": "Stage_B7_3a_E168_minus_E216.csv"},
    ])
    rings, splits, req = h24_ring_inventory()
    rings.to_csv(outdir / "Stage_B7_3a_h24_ring_inventory.csv", index=False)
    splits.to_csv(outdir / "Stage_B7_3a_h24_split_inventory.csv", index=False)
    req.to_csv(outdir / "Stage_B7_3a_h24_factorisation_requirements.csv", index=False)
    return pd.DataFrame(rows)


def write_summary(path: Path, results: pd.DataFrame, classification: pd.DataFrame, edge_manifest: pd.DataFrame, args: argparse.Namespace) -> None:
    top = results.sort_values("mean_bounded_differentiated_recovery", ascending=False).head(20)
    lines = [
        "# Stage B7.3a C12 Specificity and H24 Collective-Necessity Audit",
        "",
        "Status: executed after Stage_B7_3a_preregistration.md.",
        "",
        "Primary R_star: `receiver_standpoint_magnitude_c`.",
        "",
        "Scope note: the H24 arms test the current operational edge-level factorisation-suite / junction-coupling structure. Luke's later node-delay, edge-length, and state-dependent-drive requirements are not included because deterministic preregisterable rules are not yet frozen.",
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
    features.to_csv(outdir / "Stage_B7_3a_c_representation_scores.csv", index=False)
    events_by_rep = {rep: event_rows_for_rep(features, rep, args.event_quantile) for rep in C_REPRESENTATIONS}
    events = pd.concat(events_by_rep.values(), ignore_index=True)
    events.to_csv(outdir / "Stage_B7_3a_c_representation_events.csv", index=False)
    edge_manifest = write_h24_files(outdir)
    results = add_effect_contrasts(run_topology_audit(events_by_rep, args))
    classification = classify(results)
    results.to_csv(outdir / "Stage_B7_3a_topology_results.csv", index=False)
    classification.to_csv(outdir / "Stage_B7_3a_primary_classification.csv", index=False)
    edge_manifest.to_csv(outdir / "Stage_B7_3a_h24_edge_manifest.csv", index=False)
    write_summary(outdir / "Stage_B7_3a_preregistered_summary.md", results, classification, edge_manifest, args)
    print("\nStage B7.3a audit")
    print(f"- output_dir: {outdir}")
    print("\nClassification")
    print(classification.to_string(index=False))
    print("\nTop results")
    print(results.sort_values("mean_bounded_differentiated_recovery", ascending=False).head(12)[["c_representation", "topology_arm", "mean_bounded_differentiated_recovery", "effect_vs_no_topology_baseline", "p_vs_time_shifted_and_random"]].to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotated", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_annotated.csv")
    parser.add_argument("--events", type=Path, default=REPO / "reports/stage_b5_5/Stage_B5_5_triadic_constraint_events.csv")
    parser.add_argument("--output-dir", type=Path, default=REPO / "reports/stage_b7_3a")
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
