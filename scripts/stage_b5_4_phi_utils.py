#!/usr/bin/env python3
"""Shared phi utilities for Stage B5.4-family audits."""

from __future__ import annotations

import numpy as np
import pandas as pd


def zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    mu = np.nanmean(x)
    sd = np.nanstd(x)
    if not np.isfinite(sd) or sd <= 1e-12:
        return np.zeros_like(x, dtype=float)
    return (x - mu) / sd


def canonical_label(value: object) -> str:
    text = str(value)
    if "_co_recon" in text:
        return text.split("_co_recon", 1)[0]
    return text


def sign_switch_mask(values: pd.Series) -> pd.Series:
    v = pd.to_numeric(values, errors="coerce")
    prev = v.shift(1)
    return v.notna() & prev.notna() & (np.sign(v) != np.sign(prev)) & (np.sign(v) != 0) & (np.sign(prev) != 0)


def finite_diff(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    out = np.full_like(values, np.nan, dtype=float)
    if len(values) > 1:
        out[1:] = np.diff(values)
    return out


def compute_j_tilde(h: np.ndarray, tau: float = 3.0) -> np.ndarray:
    h = np.asarray(h, dtype=float)
    n = len(h)
    dh = finite_diff(h)
    j_event = np.full(n, np.nan, dtype=float)
    signs = np.sign(h)
    flips = np.where((signs[1:] != signs[:-1]) & (signs[1:] != 0) & (signs[:-1] != 0))[0] + 1
    for k in flips:
        lo = max(0, k - 1)
        hi = min(n, k + 3)
        window = h[lo:hi]
        eps = 0.5 * np.nanstd(window)
        if not np.isfinite(eps) or eps <= 1e-10:
            continue
        delta_eps = np.exp(-(window**2) / (2.0 * eps**2)) / (np.sqrt(2.0 * np.pi) * eps)
        phi_hat = dh[lo:hi] * delta_eps
        j_event[k] = np.nansum(phi_hat)
    event_idx = np.where(np.isfinite(j_event))[0]
    out = np.zeros(n, dtype=float)
    if len(event_idx) == 0:
        return out
    for i in range(n):
        weights = np.exp(-((i - event_idx) ** 2) / (2.0 * tau**2))
        out[i] = np.sum(j_event[event_idx] * weights) / (np.sum(weights) + 1e-8)
    return out


def recursive_phi_from_h(h_base: np.ndarray, eta: float, n_iter: int = 5) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    h_base = np.asarray(h_base, dtype=float)
    phi = zscore(h_base)
    h_loop = h_base.copy()
    j_tilde = compute_j_tilde(h_loop)
    for _ in range(n_iter):
        prev_phi = np.r_[0.0, phi[:-1]]
        h_loop = h_base + eta * prev_phi
        j_tilde = compute_j_tilde(h_loop)
        s_h = np.nanstd(h_loop)
        s_j = np.nanstd(j_tilde)
        rho = np.nanstd(np.abs(h_loop))
        h_term = h_loop / s_h if np.isfinite(s_h) and s_h > 1e-12 else np.zeros_like(h_loop)
        j_term = j_tilde / s_j if np.isfinite(s_j) and s_j > 1e-12 else np.zeros_like(j_tilde)
        gate = np.exp(-np.abs(h_loop) / rho) if np.isfinite(rho) and rho > 1e-12 else np.zeros_like(h_loop)
        base = (1.0 - gate) * h_term + gate * j_term
        new_phi = np.zeros_like(base)
        if len(base):
            new_phi[0] = base[0]
            for i in range(1, len(base)):
                new_phi[i] = 0.7 * new_phi[i - 1] + 0.3 * base[i]
        phi = new_phi
    return h_loop, j_tilde, phi


def bh_fdr(values: list[float] | np.ndarray) -> list[float]:
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
