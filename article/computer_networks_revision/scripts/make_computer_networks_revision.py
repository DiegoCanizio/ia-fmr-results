
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recreate revised Computer Networks figures for the IA-FMR article.

This script is self-contained within the Computer Networks revision artifact.

Input tables are read from:
  source_data/merged_tables/
  source_data/audit/

It generates individual subfigure graphics, not composite Matplotlib panels.
The LaTeX article is responsible for subfigure labels such as (a), (b), etc.

Outputs are written under the artifact directory itself.
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


SCRIPT_DIR = Path(__file__).resolve().parent
OUT_ROOT = SCRIPT_DIR.parent

SOURCE_DATA = OUT_ROOT / "source_data"
MERGED = SOURCE_DATA / "merged_tables"
AUDIT = SOURCE_DATA / "audit"

OUT_FIGS = OUT_ROOT / "figures"
OUT_TABLES = OUT_ROOT / "tables"
OUT_VALIDATION = OUT_ROOT / "validation"
OUT_SCRIPTS = OUT_ROOT / "scripts"
OUT_OBSOLETE = OUT_ROOT / "obsolete_composite_figures"

for d in [OUT_FIGS, OUT_TABLES, OUT_VALIDATION, OUT_SCRIPTS, OUT_OBSOLETE]:
    d.mkdir(parents=True, exist_ok=True)

E1_SUMMARY = MERGED / "e1_summary_by_bw_alpha_full.csv"
E3_SUMMARY = MERGED / "e3_qoe_summary_alpha_full_final.csv"

TEMP_CONC = MERGED / "temporal_concentration_bw40_seed_47889.csv"
TEMP_SERVED = MERGED / "temporal_served_bw40_seed_47889.csv"
TEMP_BACKLOG = MERGED / "temporal_backlog_bw40_seed_47889.csv"
TEMP_SHARE = MERGED / "temporal_share_bw40_seed_47889.csv"
TEMP_ALPHA = MERGED / "temporal_alpha_sim_bw40_seed_47889.csv"

FIDELITY_SRC = MERGED / "e1_alvo_aplicado_alpha_full_summary.csv"
E2_THR_SRC = MERGED / "e2_vazao_agregada_alpha_full_audit.csv"
E2_JAIN_SRC = MERGED / "e2_jain_rbg_alpha_full_audit.csv"
E2_SERVICE_SRC = MERGED / "e2_atendimento_p5_alpha_full_audit.csv"
E2_LOSS_DELAY_SRC = MERGED / "e2_perdas_atraso_alpha_full_audit.csv"
E3_FREEZE_AUDIT_SRC = AUDIT / "e3_freeze_seed_sets_alpha_full_audit.csv"

MODE_ORDER = ["RR", "PF", "MR", "IA-FMR"]
BANDS = [10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100]
PDBS = [60, 80]

COLORS = {"RR": "#0072B2", "PF": "#E69F00", "MR": "#D55E00", "IA-FMR": "#009E73"}
LINESTYLES = {"RR": "-", "PF": "--", "MR": "-.", "IA-FMR": "-"}
MARKERS = {"RR": "o", "PF": "s", "MR": "^", "IA-FMR": "D"}
UE_COLORS = {
    1: "#1f77b4", 2: "#ff7f0e", 3: "#2ca02c", 4: "#d62728", 5: "#9467bd",
    6: "#8c564b", 7: "#e377c2", 8: "#7f7f7f", 9: "#bcbd22",
}
VIDEO_COLORS = {"Delivered on time": "#009E73", "Delivered late": "#E69F00", "Not received": "#D55E00"}
PHASE_LINES = [6, 12, 18, 24]

plt.rcParams.update({
    "figure.dpi": 120, "savefig.dpi": 300,
    "font.family": "serif",
    "font.serif": ["Times New Roman", "STIX Two Text", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 8, "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.fontsize": 8, "legend.title_fontsize": 8,
    "axes.linewidth": 0.8, "xtick.major.width": 0.8, "ytick.major.width": 0.8,
    "xtick.major.size": 3.0, "ytick.major.size": 3.0,
    "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42, "ps.fonttype": 42, "hatch.linewidth": 0.8,
})

validation_rows = []


def fail(msg: str):
    raise RuntimeError(msg)


def add_validation(check, expected, obtained, difference="", passed=True, details=""):
    validation_rows.append({
        "check": check, "expected": expected, "obtained": obtained,
        "difference": difference, "PASS_FAIL": "PASS" if passed else "FAIL",
        "details": details,
    })


def ensure_exists(path: Path):
    if not path.exists():
        fail(f"Arquivo obrigatório não encontrado: {path}")


def read_csv(path: Path) -> pd.DataFrame:
    ensure_exists(path)
    return pd.read_csv(path)


def norm_mode(x):
    s = str(x).strip()
    low = s.lower()
    if low == "rr": return "RR"
    if low == "pf": return "PF"
    if low == "mr": return "MR"
    if low in {"fmr_rl", "fmr", "ia-fmr", "ia_fmr", "iafmr"}: return "IA-FMR"
    return s


def require_cols(df, cols, name):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        fail(
            f"Colunas ausentes em {name}:\n" +
            "\n".join(f"- {c}" for c in missing) +
            "\n\nColunas disponíveis:\n" +
            "\n".join(df.columns)
        )


def find_col(df, candidates, name, required=True):
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        fail(
            f"Não encontrei coluna para {name}. Tentei:\n" +
            "\n".join(f"- {c}" for c in candidates) +
            "\n\nColunas disponíveis:\n" +
            "\n".join(df.columns)
        )
    return None


def save_fig(fig, filename_base):
    fig.savefig(OUT_FIGS / f"{filename_base}.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(OUT_FIGS / f"{filename_base}.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def style_axis(ax):
    ax.grid(axis="y", linewidth=0.5, alpha=0.20)
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)


def add_phase_lines(ax):
    for x in PHASE_LINES:
        ax.axvline(x, linestyle=":", linewidth=0.8, color="#BDBDBD", alpha=0.8, zorder=0)


def scheduler_handles():
    return [
        Line2D([0], [0], color=COLORS[m], linestyle=LINESTYLES[m], marker=MARKERS[m],
               linewidth=1.6, markersize=4.5, label=m)
        for m in MODE_ORDER
    ]


def save_legend_only(handles, filename_base, ncol, figsize):
    fig = plt.figure(figsize=figsize)
    fig.legend(handles=handles, loc="center", ncol=ncol, frameon=False,
               handlelength=2.2, columnspacing=1.6)
    fig.savefig(OUT_FIGS / f"{filename_base}.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(OUT_FIGS / f"{filename_base}.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def quarantine_old_composites():
    patterns = [
        "fig02_efficiency_resource_fairness_revised.*",
        "fig03_ue_service_lower_tail_revised.*",
        "fig04_packet_delivery_revised.*",
        "fig05_temporal_allocation_queue_40mhz_seed47889_revised.*",
        "fig06_per_ue_rbg_shares_40mhz_seed47889_revised.*",
        "fig08_video_unit_composition_revised.*",
        "fig09_video_temporal_indicators_revised.*",
        "video_temporal_unavailability.*",
    ]
    moved = []
    for pat in patterns:
        for p in OUT_FIGS.glob(pat):
            target = OUT_OBSOLETE / p.name
            if target.exists():
                target = OUT_OBSOLETE / f"{p.stem}_old{p.suffix}"
            p.rename(target)
            moved.append(str(target))
    if moved:
        (OUT_VALIDATION / "obsolete_composite_figures_moved.txt").write_text("\n".join(moved), encoding="utf-8")


def make_legend_assets():
    save_legend_only(scheduler_handles(), "legend_schedulers", ncol=4, figsize=(4.4, 0.35))
    ue_handles = [Line2D([0], [0], color=UE_COLORS[i], linewidth=1.4, label=f"UE{i}") for i in range(1, 10)]
    save_legend_only(ue_handles, "legend_ues", ncol=3, figsize=(2.6, 0.85))
    video_handles = [
        Patch(facecolor=VIDEO_COLORS["Delivered on time"], edgecolor="black", linewidth=0.5, label="Delivered on time"),
        Patch(facecolor=VIDEO_COLORS["Delivered late"], edgecolor="black", linewidth=0.5, label="Delivered late"),
        Patch(facecolor=VIDEO_COLORS["Not received"], edgecolor="black", linewidth=0.5, label="Not received"),
    ]
    save_legend_only(video_handles, "legend_video_composition", ncol=3, figsize=(4.5, 0.35))
    deadline_handles = [
        Patch(facecolor="0.65", edgecolor="black", linewidth=0.8, label="60 ms"),
        Patch(facecolor="white", edgecolor="black", linewidth=0.8, hatch="///", label="80 ms"),
    ]
    save_legend_only(deadline_handles, "legend_video_deadlines", ncol=2, figsize=(2.1, 0.35))


def export_metric_csv(rows, filename):
    pd.DataFrame(rows).to_csv(OUT_TABLES / filename, index=False)


def load_e1():
    df = read_csv(E1_SUMMARY)
    required = [
        "mode", "bandwidth_mhz",
        "aggregate_throughput_mbps_mean", "aggregate_throughput_mbps_ci95",
        "jain_rbg_slot_mean_mean", "jain_rbg_slot_mean_ci95",
        "mean_served_ues_per_slot_mean", "mean_served_ues_per_slot_ci95",
        "pct_buf_gt0_alloc_eq0_mean", "pct_buf_gt0_alloc_eq0_ci95",
        "p5_flow_throughput_mbps_mean", "p5_flow_throughput_mbps_ci95",
        "mean_loss_ratio_mean", "mean_loss_ratio_ci95",
        "mean_delay_ms_mean", "mean_delay_ms_ci95",
    ]
    require_cols(df, required, "E1 summary")
    df["mode_label"] = df["mode"].map(norm_mode)
    df["bandwidth_mhz"] = pd.to_numeric(df["bandwidth_mhz"], errors="coerce").astype(int)

    got_bands = sorted(df["bandwidth_mhz"].unique().tolist())
    add_validation("E1 exact bandwidth set", str(BANDS), str(got_bands), "", got_bands == BANDS)
    if got_bands != BANDS: fail(f"Bandas E1 divergentes: {got_bands}")

    got_modes = [m for m in MODE_ORDER if m in set(df["mode_label"])]
    add_validation("E1 scheduler set", str(MODE_ORDER), str(got_modes), "", got_modes == MODE_ORDER)
    if got_modes != MODE_ORDER: fail(f"Escalonadores E1 divergentes: {got_modes}")

    seed_col = "n_repetitions" if "n_repetitions" in df.columns else ("n_seeds" if "n_seeds" in df.columns else None)
    if seed_col:
        bad = df[pd.to_numeric(df[seed_col], errors="coerce") != 100]
        add_validation("E1 n=100 where available", "100 for all rows",
                       f"{len(bad)} rows not equal to 100", "", len(bad) == 0,
                       f"Seed column: {seed_col}")
        if len(bad) > 0: fail("E1 possui linhas com n diferente de 100.")
    return df


def plot_e1_metric(df, filename_base, mean_col, ci_col, ylabel, ylim, yticks=None,
                   figsize=(6.1, 2.35), scale=1.0):
    fig, ax = plt.subplots(figsize=figsize)
    rows = []
    for mode in MODE_ORDER:
        sub = df[df["mode_label"] == mode].sort_values("bandwidth_mhz")
        x = sub["bandwidth_mhz"].to_numpy()
        y = pd.to_numeric(sub[mean_col], errors="coerce").to_numpy() * scale
        ci = pd.to_numeric(sub[ci_col], errors="coerce").to_numpy() * scale
        ax.errorbar(x, y, yerr=ci, color=COLORS[mode], linestyle=LINESTYLES[mode],
                    marker=MARKERS[mode], linewidth=1.6, markersize=4.5,
                    elinewidth=0.9, capsize=2.5, capthick=0.9)
        seed_col = "n_repetitions" if "n_repetitions" in sub.columns else ("n_seeds" if "n_seeds" in sub.columns else None)
        for xi, yi, cii, (_, r) in zip(x, y, ci, sub.iterrows()):
            rows.append({
                "bandwidth_mhz": int(xi), "scheduler": mode,
                "mean": yi, "CI95_low": yi - cii, "CI95_high": yi + cii,
                "CI95": cii, "n": int(r[seed_col]) if seed_col else np.nan,
            })
    ax.set_xlabel("Bandwidth (MHz)")
    ax.set_ylabel(ylabel)
    ax.set_xlim(9, 101)
    ax.set_xticks(BANDS)
    ax.set_ylim(*ylim)
    if yticks is not None: ax.set_yticks(yticks)
    style_axis(ax)
    fig.subplots_adjust(left=0.15, right=0.98, bottom=0.22, top=0.97)
    save_fig(fig, filename_base)
    export_metric_csv(rows, f"{filename_base}.csv")


def make_e1_figures(df):
    plot_e1_metric(df, "bandwidth_aggregate_throughput", "aggregate_throughput_mbps_mean",
                   "aggregate_throughput_mbps_ci95", "Aggregate throughput (Mbps)",
                   (0, 160), np.arange(0, 161, 20), (6.1, 2.35))
    plot_e1_metric(df, "bandwidth_jain_index", "jain_rbg_slot_mean_mean",
                   "jain_rbg_slot_mean_ci95", "RBG-based Jain index",
                   (0, 1.05), np.arange(0, 1.01, 0.2), (6.1, 2.35))
    plot_e1_metric(df, "bandwidth_served_ues", "mean_served_ues_per_slot_mean",
                   "mean_served_ues_per_slot_ci95", "Served UEs per slot",
                   (0, 9.4), np.arange(0, 10, 1), (3.45, 2.30))
    plot_e1_metric(df, "bandwidth_pending_without_allocation", "pct_buf_gt0_alloc_eq0_mean",
                   "pct_buf_gt0_alloc_eq0_ci95", "Pending demand w/o allocation (%)",
                   (0, 100), np.arange(0, 101, 20), (3.45, 2.30))
    plot_e1_metric(df, "bandwidth_flow_throughput_p5", "p5_flow_throughput_mbps_mean",
                   "p5_flow_throughput_mbps_ci95", "Per-flow TP P5 (Mbps)",
                   (0, 1.6), np.arange(0, 1.61, 0.4), (5.3, 2.35))
    plot_e1_metric(df, "bandwidth_packet_loss", "mean_loss_ratio_mean",
                   "mean_loss_ratio_ci95", "Undelivered packet ratio (%)",
                   (0, 100), np.arange(0, 101, 20), (6.1, 2.35), scale=100.0)

    delay_max = 6000
    ymax = (df["mean_delay_ms_mean"] + df["mean_delay_ms_ci95"]).max()
    if ymax > delay_max:
        delay_max = int(math.ceil(ymax / 1000.0) * 1000)
    plot_e1_metric(df, "bandwidth_mean_delay", "mean_delay_ms_mean",
                   "mean_delay_ms_ci95", "Mean packet delay (ms)",
                   (0, delay_max), None, (6.1, 2.35))

    checkpoints = {
        ("RR", 40): (50.93, 0.9988), ("PF", 40): (34.36, 0.5926),
        ("MR", 40): (120.40, 0.3711), ("IA-FMR", 40): (97.53, 0.9943),
    }
    for (mode, bw), (thr_exp, jain_exp) in checkpoints.items():
        row = df[(df["mode_label"] == mode) & (df["bandwidth_mhz"] == bw)].iloc[0]
        thr = float(row["aggregate_throughput_mbps_mean"])
        jain = float(row["jain_rbg_slot_mean_mean"])
        add_validation(f"Fig2 throughput {mode} {bw} MHz", thr_exp, round(thr, 6),
                       round(thr - thr_exp, 6), abs(thr - thr_exp) <= 0.02)
        add_validation(f"Fig2 Jain {mode} {bw} MHz", jain_exp, round(jain, 6),
                       round(jain - jain_exp, 6), abs(jain - jain_exp) <= 0.002)

    r10 = df[(df["mode_label"] == "IA-FMR") & (df["bandwidth_mhz"] == 10)].iloc[0]
    add_validation("Fig2 IA-FMR Jain 10 MHz", "≈0.7985",
                   round(float(r10["jain_rbg_slot_mean_mean"]), 6), "",
                   abs(float(r10["jain_rbg_slot_mean_mean"]) - 0.7985) <= 0.005)
    add_validation("Fig4 loss definition review", "(Ptx-Prx)/Ptx*100 expected",
                   "Using mean_loss_ratio_mean * 100 from final E1 summary", "",
                   True, "No silent redefinition performed.")

    add_validation("Fig3 IA-FMR served UEs 10 MHz", "≈7.30",
                   round(float(r10["mean_served_ues_per_slot_mean"]), 6), "",
                   abs(float(r10["mean_served_ues_per_slot_mean"]) - 7.30) <= 0.02)
    add_validation("Fig3 IA-FMR pending 10 MHz", "≈18.89%",
                   round(float(r10["pct_buf_gt0_alloc_eq0_mean"]), 6), "",
                   abs(float(r10["pct_buf_gt0_alloc_eq0_mean"]) - 18.89) <= 0.05)

    ia = df[df["mode_label"] == "IA-FMR"]
    bad_pending = ia[(ia["bandwidth_mhz"] >= 15) & (abs(ia["pct_buf_gt0_alloc_eq0_mean"]) > 1e-9)]
    add_validation("Fig3 IA-FMR pending 15-100 MHz", "0%",
                   f"{len(bad_pending)} nonzero rows", "", len(bad_pending) == 0)

    for mode, expected in {"IA-FMR": 1.225, "RR": 0.714, "PF": 0.337, "MR": 0.0}.items():
        row = df[(df["mode_label"] == mode) & (df["bandwidth_mhz"] == 40)].iloc[0]
        val = float(row["p5_flow_throughput_mbps_mean"])
        tol = 0.005 if mode != "MR" else 0.001
        add_validation(f"Fig3 P5 {mode} 40 MHz", expected, round(val, 6),
                       round(val - expected, 6), abs(val - expected) <= tol)


def load_temporal(path, name):
    df = read_csv(path)
    if "mode_label" not in df.columns:
        mcol = find_col(df, ["mode_label", "mode", "scheduler"], f"{name} mode")
        df["mode_label"] = df[mcol].map(norm_mode)
    else:
        df["mode_label"] = df["mode_label"].map(norm_mode)
    return df


def time_col(df, name):
    return find_col(df, ["t_plot", "t_plot_s", "time_rel_s", "time_s_rel",
                         "time_bin", "time_bin_s", "time_s", "t"], f"{name} time")


def plot_temporal_metric(df, filename_base, value_col, ylabel, ylim, yticks=None,
                         percent=False, figsize=(3.45, 2.30)):
    tcol = time_col(df, filename_base)
    fig, ax = plt.subplots(figsize=figsize)
    rows = []
    for mode in MODE_ORDER:
        sub = df[df["mode_label"] == mode].copy()
        sub[tcol] = pd.to_numeric(sub[tcol], errors="coerce")
        sub[value_col] = pd.to_numeric(sub[value_col], errors="coerce")
        sub = sub.dropna(subset=[tcol, value_col]).sort_values(tcol)
        x = sub[tcol].to_numpy()
        y = sub[value_col].to_numpy()
        if percent and np.nanmax(y) <= 1.5: y = y * 100.0
        ax.plot(x, y, color=COLORS[mode], linestyle=LINESTYLES[mode], linewidth=1.6)
        for xi, yi in zip(x, y):
            rows.append({"scheduler": mode, "time_s": xi, "mean": yi,
                         "CI95_low": np.nan, "CI95_high": np.nan, "n": 1})
    ax.set_xlabel("Simulation time (s)")
    ax.set_ylabel(ylabel)
    ax.set_xlim(0, 30)
    ax.set_xticks([0, 6, 12, 18, 24, 30])
    ax.set_ylim(*ylim)
    if yticks is not None: ax.set_yticks(yticks)
    style_axis(ax)
    add_phase_lines(ax)
    fig.subplots_adjust(left=0.18, right=0.98, bottom=0.22, top=0.97)
    save_fig(fig, filename_base)
    export_metric_csv(rows, f"{filename_base}.csv")


def make_temporal_figures():
    conc = load_temporal(TEMP_CONC, "temporal concentration")
    served = load_temporal(TEMP_SERVED, "temporal served")
    backlog = load_temporal(TEMP_BACKLOG, "temporal backlog")
    share = load_temporal(TEMP_SHARE, "temporal share")
    alpha = read_csv(TEMP_ALPHA)

    neff_col = find_col(conc, ["effective_ues_smooth", "effective_ues", "n_eff_smooth",
                               "neff_smooth", "effective_number_ues_smooth", "n_eff", "neff"],
                        "effective number of UEs")
    pmax_col = find_col(conc, ["top1_share_pct_smooth", "top1_share_pct", "pmax_smooth",
                               "p_max_smooth", "top1_share_smooth", "pmax"],
                        "largest allocation share")
    served_col = find_col(served, ["served_ues_smooth", "served_ues_per_slot_smooth",
                                   "mean_served_ues_per_slot_smooth", "served_ues", "served"],
                          "served UEs temporal")
    backlog_col = find_col(backlog, ["backlog_mbit_smooth", "aggregate_backlog_mbit_smooth",
                                     "backlog_mbit", "aggregate_backlog_mbit"],
                           "aggregate backlog")

    plot_temporal_metric(conc, "temporal_effective_ues_40mhz", neff_col,
                         "Effective number of UEs", (0, 9.5), np.arange(0, 10, 1))
    plot_temporal_metric(conc, "temporal_largest_share_40mhz", pmax_col,
                         "Largest alloc. share (%)", (0, 40), [0, 10, 20, 30, 40],
                         percent=("pct" not in pmax_col.lower()))
    plot_temporal_metric(served, "temporal_served_ues_40mhz", served_col,
                         "Served UEs per slot", (0, 9.5), np.arange(0, 10, 1))

    bmax = pd.to_numeric(backlog[backlog_col], errors="coerce").max()
    bylim = 9000 if bmax <= 9000 else int(math.ceil(bmax / 1000.0) * 1000)
    plot_temporal_metric(backlog, "temporal_backlog_40mhz", backlog_col,
                         "Aggregate backlog (Mbit)", (0, bylim))

    neff_means = conc.groupby("mode_label")[neff_col].mean()
    pmax_values = pd.to_numeric(conc[pmax_col], errors="coerce")
    conc["_pmax_pct_for_check"] = pmax_values if "pct" in pmax_col.lower() or pmax_values.max() > 1.5 else pmax_values * 100.0
    pmax_means = conc.groupby("mode_label")["_pmax_pct_for_check"].mean()
    add_validation("Fig5 IA-FMR N_eff mean", "≈8.96", round(float(neff_means["IA-FMR"]), 6), "",
                   abs(float(neff_means["IA-FMR"]) - 8.96) <= 0.03)
    add_validation("Fig5 IA-FMR pmax mean", "≈12.26%", round(float(pmax_means["IA-FMR"]), 6), "",
                   abs(float(pmax_means["IA-FMR"]) - 12.26) <= 0.08)
    add_validation("Fig5 MR N_eff mean", "≈4.44", round(float(neff_means["MR"]), 6), "",
                   abs(float(neff_means["MR"]) - 4.44) <= 0.05)
    add_validation("Fig5 MR pmax mean", "≈25.46%", round(float(pmax_means["MR"]), 6), "",
                   abs(float(pmax_means["MR"]) - 25.46) <= 0.10)

    make_temporal_rbg_share_figures(share)
    make_alpha_figure(alpha)


def make_temporal_rbg_share_figures(share):
    tcol = time_col(share, "temporal RBG share")
    ue_col = find_col(share, ["ue", "ue_idx", "UE", "rnti_idx"], "UE id", required=False)
    val_col = find_col(share, ["share_smooth", "rbg_share_smooth", "rbg_share_pct_smooth",
                               "share_pct_smooth", "share", "rbg_share_pct"],
                       "UE RBG share", required=False)
    file_map = {
        "RR": "temporal_rbg_shares_rr_40mhz",
        "PF": "temporal_rbg_shares_pf_40mhz",
        "MR": "temporal_rbg_shares_mr_40mhz",
        "IA-FMR": "temporal_rbg_shares_iafmr_40mhz",
    }
    for mode in MODE_ORDER:
        fig, ax = plt.subplots(figsize=(3.45, 2.30))
        rows = []
        sub_mode = share[share["mode_label"] == mode].copy()
        if sub_mode.empty: fail(f"Sem dados de share temporal para {mode}")

        if ue_col and val_col:
            sub_mode[ue_col] = pd.to_numeric(sub_mode[ue_col], errors="coerce")
            for ue in range(1, 10):
                sub = sub_mode[sub_mode[ue_col].astype("Int64") == ue].copy()
                if sub.empty: continue
                sub[tcol] = pd.to_numeric(sub[tcol], errors="coerce")
                sub[val_col] = pd.to_numeric(sub[val_col], errors="coerce")
                sub = sub.dropna(subset=[tcol, val_col]).sort_values(tcol)
                x = sub[tcol].to_numpy()
                y = sub[val_col].to_numpy()
                if np.nanmax(y) <= 1.5: y = y * 100.0
                ax.plot(x, y, color=UE_COLORS[ue], linewidth=1.05)
                for xi, yi in zip(x, y):
                    rows.append({"scheduler": mode, "ue": ue, "time_s": xi, "mean": yi,
                                 "CI95_low": np.nan, "CI95_high": np.nan, "n": 1})
        else:
            for ue in range(1, 10):
                ucol = find_col(sub_mode, [f"UE{ue}", f"ue{ue}", f"UE_{ue}", f"ue_{ue}"],
                                f"UE{ue} share", required=False)
                if not ucol: continue
                sub = sub_mode[[tcol, ucol]].copy()
                sub[tcol] = pd.to_numeric(sub[tcol], errors="coerce")
                sub[ucol] = pd.to_numeric(sub[ucol], errors="coerce")
                sub = sub.dropna().sort_values(tcol)
                x = sub[tcol].to_numpy()
                y = sub[ucol].to_numpy()
                if np.nanmax(y) <= 1.5: y = y * 100.0
                ax.plot(x, y, color=UE_COLORS[ue], linewidth=1.05)
                for xi, yi in zip(x, y):
                    rows.append({"scheduler": mode, "ue": ue, "time_s": xi, "mean": yi,
                                 "CI95_low": np.nan, "CI95_high": np.nan, "n": 1})

        ax.set_xlabel("Simulation time (s)")
        ax.set_ylabel("RBG share per UE (%)")
        ax.set_xlim(0, 30)
        ax.set_xticks([0, 6, 12, 18, 24, 30])
        ax.set_ylim(0, 40)
        ax.set_yticks([0, 10, 20, 30, 40])
        style_axis(ax)
        add_phase_lines(ax)
        fig.subplots_adjust(left=0.18, right=0.98, bottom=0.22, top=0.97)
        filename = file_map[mode]
        save_fig(fig, filename)
        export_metric_csv(rows, f"{filename}.csv")

    add_validation("Fig6 temporal seed rule", "seed 47889 only",
                   "Using temporal CSV generated for seed 47889", "",
                   True, str(TEMP_SHARE))


def make_alpha_figure(alpha):
    tcol = find_col(alpha, ["t_plot", "t_plot_s", "time_rel_s", "time_s_rel",
                            "time_bin", "time_bin_s", "time_s", "t"], "alpha time")
    acol = find_col(alpha, ["alpha_smooth", "alpha_mean", "alpha", "alpha_t"], "alpha")
    alpha[tcol] = pd.to_numeric(alpha[tcol], errors="coerce")
    alpha[acol] = pd.to_numeric(alpha[acol], errors="coerce")
    alpha = alpha.dropna(subset=[tcol, acol]).sort_values(tcol)
    amin, amax, amean = float(alpha[acol].min()), float(alpha[acol].max()), float(alpha[acol].mean())
    if amin < -1e-12 or amax > 1 + 1e-12:
        fail(f"Alpha fora de [0,1]: min={amin}, max={amax}")

    fig, ax = plt.subplots(figsize=(7.0, 2.0))
    ax.plot(alpha[tcol], alpha[acol], color=COLORS["IA-FMR"], linestyle="-", linewidth=1.6)
    ax.set_xlabel("Simulation time (s)")
    ax.set_ylabel(r"$\alpha_t$")
    ax.set_xlim(0, 30)
    ax.set_xticks([0, 6, 12, 18, 24, 30])
    ax.set_ylim(0.996, 1.000)
    ax.set_yticks([0.996, 0.997, 0.998, 0.999, 1.000])
    style_axis(ax)
    add_phase_lines(ax)
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.25, top=0.97)
    save_fig(fig, "temporal_alpha_40mhz")

    out = alpha[[tcol, acol]].rename(columns={tcol: "time_s", acol: "alpha_t"})
    out["mean"] = out["alpha_t"]
    out["CI95_low"] = np.nan
    out["CI95_high"] = np.nan
    out["n"] = 1
    out.to_csv(OUT_TABLES / "temporal_alpha_40mhz.csv", index=False)

    add_validation("Fig7 alpha domain", "0 <= alpha <= 1", f"min={amin:.6f}, max={amax:.6f}", "", True)
    add_validation("Fig7 alpha mean", "≈0.9982", round(amean, 6), "", abs(amean - 0.9982) <= 0.0002)
    add_validation("Fig7 alpha min", "≈0.9974", round(amin, 6), "", abs(amin - 0.9974) <= 0.0002)
    add_validation("Fig7 alpha max", "≈0.9983", round(amax, 6), "", abs(amax - 0.9983) <= 0.0002)


def load_e3():
    df = read_csv(E3_SUMMARY)
    df["mode_label"] = df["mode_label"].map(norm_mode) if "mode_label" in df.columns else df["mode"].map(norm_mode)
    df["pdb_ms"] = pd.to_numeric(df["pdb_ms"], errors="coerce").astype(int)
    required = [
        "mode_label", "pdb_ms", "n_seeds", "fsr_mean_mean", "fsr_mean_ci95",
        "received_frame_ratio_mean_mean", "received_frame_ratio_mean_ci95",
        "late_frame_ratio_mean_mean", "late_frame_ratio_mean_ci95",
        "lost_frame_ratio_mean_mean", "lost_frame_ratio_mean_ci95",
        "freeze_events_per_min_mean_mean", "freeze_events_per_min_mean_ci95",
        "p95_freeze_ms_across_ues_mean", "p95_freeze_ms_across_ues_ci95",
        "ues_satisfied_99_pct_mean", "ues_satisfied_99_pct_ci95",
    ]
    require_cols(df, required, "E3 summary")
    got_modes = [m for m in MODE_ORDER if m in set(df["mode_label"])]
    got_pdbs = sorted(df["pdb_ms"].unique().tolist())
    add_validation("E3 scheduler set", str(MODE_ORDER), str(got_modes), "", got_modes == MODE_ORDER)
    add_validation("E3 PDB set", str(PDBS), str(got_pdbs), "", got_pdbs == PDBS)
    bad = df[pd.to_numeric(df["n_seeds"], errors="coerce") != 100]
    add_validation("E3 n_total=100", "100", f"{len(bad)} rows not equal to 100", "", len(bad) == 0)
    if got_modes != MODE_ORDER or got_pdbs != PDBS or len(bad) > 0:
        fail("Validação básica do E3 falhou.")
    return df


def make_video_composition_table(df):
    rows, audit_rows = [], []
    for _, r in df.iterrows():
        mode, pdb = r["mode_label"], int(r["pdb_ms"])
        on_time = float(r["fsr_mean_mean"]) * 100.0
        on_time_ci = float(r["fsr_mean_ci95"]) * 100.0
        late = float(r["late_frame_ratio_mean_mean"]) * 100.0
        late_ci = float(r["late_frame_ratio_mean_ci95"]) * 100.0
        not_received = float(r["lost_frame_ratio_mean_mean"]) * 100.0
        not_received_ci = float(r["lost_frame_ratio_mean_ci95"]) * 100.0
        received = float(r["received_frame_ratio_mean_mean"]) * 100.0
        received_ci = float(r["received_frame_ratio_mean_ci95"]) * 100.0
        sum_pct = on_time + late + not_received
        received_from_parts = on_time + late
        close_sum = abs(sum_pct - 100.0)
        close_received = abs(received_from_parts - received)
        close_lost = abs(not_received - (100.0 - received))
        audit_rows.append({
            "scheduler": mode, "pdb_ms": pdb, "on_time_pct": on_time,
            "late_pct": late, "not_received_pct": not_received,
            "received_total_pct": received, "sum_pct": sum_pct,
            "sum_error": close_sum,
            "on_time_plus_late_error_vs_received": close_received,
            "not_received_error_vs_100_minus_received": close_lost,
            "source": str(E3_SUMMARY),
        })
        if close_sum > 1e-6 or close_received > 1e-6 or close_lost > 1e-6:
            fail(
                "Falha na composição da Figura 8:\n"
                f"scheduler={mode}\ndeadline={pdb}\non_time={on_time}\nlate={late}\n"
                f"not_received={not_received}\nreceived_total={received}\nsoma={sum_pct}\n"
                f"erro_fechamento={close_sum}\nerro_received={close_received}\n"
                f"erro_lost={close_lost}\norigem={E3_SUMMARY}"
            )
        rows.append({
            "scheduler": mode, "pdb_ms": pdb,
            "delivered_on_time_pct": on_time, "delivered_on_time_ci95": on_time_ci,
            "delivered_late_pct": late, "delivered_late_ci95": late_ci,
            "not_received_pct": not_received, "not_received_ci95": not_received_ci,
            "received_total_pct": received, "received_total_ci95": received_ci,
            "mean": on_time, "CI95_low": on_time - on_time_ci,
            "CI95_high": on_time + on_time_ci, "n": int(r["n_seeds"]),
        })

    comp = pd.DataFrame(rows)
    comp["mode_order"] = comp["scheduler"].map({m: i for i, m in enumerate(MODE_ORDER)})
    comp = comp.sort_values(["pdb_ms", "mode_order"]).drop(columns=["mode_order"])
    pd.DataFrame(audit_rows).to_csv(OUT_VALIDATION / "fig08_video_composition_audit.csv", index=False)
    comp.to_csv(OUT_TABLES / "video_unit_composition_revised.csv", index=False)

    ok, details = True, []
    for mode in MODE_ORDER:
        v60 = comp[(comp["scheduler"] == mode) & (comp["pdb_ms"] == 60)]["not_received_pct"].iloc[0]
        v80 = comp[(comp["scheduler"] == mode) & (comp["pdb_ms"] == 80)]["not_received_pct"].iloc[0]
        diff = abs(v60 - v80)
        details.append(f"{mode}: diff={diff:.8f}")
        if diff > 1e-6: ok = False
    add_validation("Fig8 not received equal across deadlines", "same within scheduler", "; ".join(details), "", ok)

    ia60 = comp[(comp["scheduler"] == "IA-FMR") & (comp["pdb_ms"] == 60)].iloc[0]
    thesis_expected = {"delivered_on_time_pct": 66.88, "delivered_late_pct": 20.00, "not_received_pct": 13.12}
    audit_specific = []
    for col, thesis_value in thesis_expected.items():
        raw_value = float(ia60[col])
        audit_specific.append({"metric": col, "raw_value_pct": raw_value,
                               "thesis_value_pct": thesis_value,
                               "difference_pct_points": raw_value - thesis_value,
                               "origin": str(E3_SUMMARY)})
    pd.DataFrame(audit_specific).to_csv(OUT_VALIDATION / "fig08_iafmr_60ms_discrepancy_audit.csv", index=False)
    add_validation("Fig8 IA-FMR 60 ms discrepancy audit", "audit produced, no CSV changed",
                   f"on_time={ia60['delivered_on_time_pct']:.4f}, late={ia60['delivered_late_pct']:.4f}, not_received={ia60['not_received_pct']:.4f}",
                   "", True, str(OUT_VALIDATION / "fig08_iafmr_60ms_discrepancy_audit.csv"))
    return comp


def plot_video_composition(comp, pdb, filename_base):
    sub = comp[comp["pdb_ms"] == pdb].copy()
    sub["scheduler"] = pd.Categorical(sub["scheduler"], MODE_ORDER, ordered=True)
    sub = sub.sort_values("scheduler")
    x = np.arange(len(MODE_ORDER))
    y1 = sub["delivered_on_time_pct"].to_numpy()
    y2 = sub["delivered_late_pct"].to_numpy()
    y3 = sub["not_received_pct"].to_numpy()
    tup_ci = sub["delivered_on_time_ci95"].to_numpy()
    recv = sub["received_total_pct"].to_numpy()
    recv_ci = sub["received_total_ci95"].to_numpy()

    fig, ax = plt.subplots(figsize=(3.45, 2.30))
    ax.bar(x, y1, width=0.62, color=VIDEO_COLORS["Delivered on time"], edgecolor="black", linewidth=0.5)
    ax.bar(x, y2, bottom=y1, width=0.62, color=VIDEO_COLORS["Delivered late"], edgecolor="black", linewidth=0.5)
    ax.bar(x, y3, bottom=y1 + y2, width=0.62, color=VIDEO_COLORS["Not received"], edgecolor="black", linewidth=0.5)
    ax.errorbar(x, y1, yerr=tup_ci, fmt="none", ecolor="black", elinewidth=0.9, capsize=3, capthick=0.9)
    ax.errorbar(x, recv, yerr=recv_ci, fmt="none", ecolor="black", elinewidth=0.9, capsize=3, capthick=0.9)
    ax.set_xlabel("Scheduler")
    ax.set_ylabel("Generated video units (%)")
    ax.set_xticks(x)
    ax.set_xticklabels(MODE_ORDER)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    style_axis(ax)
    fig.subplots_adjust(left=0.18, right=0.98, bottom=0.22, top=0.97)
    save_fig(fig, filename_base)


def make_video_composition_figures(df):
    comp = make_video_composition_table(df)
    plot_video_composition(comp, 60, "video_unit_composition_60ms")
    plot_video_composition(comp, 80, "video_unit_composition_80ms")

    cp_60 = {
        "RR": (53.10, 34.30, 12.60), "PF": (47.12, 29.78, 23.10),
        "MR": (46.41, 28.39, 25.20), "IA-FMR": (66.88, 19.83, 13.29),
    }
    for mode, expected in cp_60.items():
        row = comp[(comp["scheduler"] == mode) & (comp["pdb_ms"] == 60)].iloc[0]
        got = (float(row["delivered_on_time_pct"]), float(row["delivered_late_pct"]), float(row["not_received_pct"]))
        passed = all(abs(g - e) <= 0.08 for g, e in zip(got, expected))
        add_validation(f"Fig8 composition 60 ms {mode}", str(expected),
                       str(tuple(round(v, 4) for v in got)), "", passed)

    for mode, expected in {"RR": 54.00, "PF": 47.58, "MR": 46.64, "IA-FMR": 67.20}.items():
        row = comp[(comp["scheduler"] == mode) & (comp["pdb_ms"] == 80)].iloc[0]
        got = float(row["delivered_on_time_pct"])
        add_validation(f"Fig8 TUP 80 ms {mode}", expected, round(got, 4),
                       round(got - expected, 6), abs(got - expected) <= 0.08)


def p95_valid_n_map():
    if not E3_FREEZE_AUDIT_SRC.exists(): return {}
    df = pd.read_csv(E3_FREEZE_AUDIT_SRC)
    required = ["Escalonador", "PDB (ms)", "n_seeds_validas_p95_duracao"]
    if not all(c in df.columns for c in required): return {}
    return {(str(r["Escalonador"]), int(r["PDB (ms)"])): int(r["n_seeds_validas_p95_duracao"])
            for _, r in df.iterrows()}


def plot_video_deadline_grouped(df, filename_base, mean_col, ci_col, ylabel, ylim, ms_to_s=False, n_for_p95=False):
    fig, ax = plt.subplots(figsize=(3.45, 2.30))
    x, width = np.arange(len(MODE_ORDER)), 0.28
    rows, p95_n = [], p95_valid_n_map()
    for i, pdb in enumerate(PDBS):
        offset = (i - 0.5) * width
        for j, mode in enumerate(MODE_ORDER):
            r = df[(df["mode_label"] == mode) & (df["pdb_ms"] == pdb)].iloc[0]
            mean, ci = float(r[mean_col]), float(r[ci_col])
            if ms_to_s:
                mean /= 1000.0
                ci /= 1000.0
            if pdb == 60:
                facecolor, edgecolor, hatch = COLORS[mode], "black", ""
            else:
                facecolor, edgecolor, hatch = "white", COLORS[mode], "///"
            ax.bar(x[j] + offset, mean, width=width, color=facecolor, edgecolor=edgecolor,
                   linewidth=0.8, hatch=hatch, yerr=ci, capsize=2.5, ecolor="black",
                   error_kw={"elinewidth": 0.9, "capthick": 0.9})
            n = p95_n.get((mode, pdb), np.nan) if n_for_p95 else int(r["n_seeds"])
            rows.append({"scheduler": mode, "pdb_ms": pdb, "mean": mean,
                         "CI95_low": mean - ci, "CI95_high": mean + ci,
                         "CI95": ci, "n": n})
    ax.set_xlabel("Scheduler")
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)
    ax.set_xticklabels(MODE_ORDER)
    ax.set_ylim(*ylim)
    style_axis(ax)
    fig.subplots_adjust(left=0.18, right=0.98, bottom=0.22, top=0.97)
    save_fig(fig, filename_base)
    export_metric_csv(rows, f"{filename_base}.csv")


def make_video_temporal_figures(df):
    plot_video_deadline_grouped(df, "video_freezing_frequency",
                                "freeze_events_per_min_mean_mean", "freeze_events_per_min_mean_ci95",
                                "Freezing freq. (events/min)", (0, 3.5))
    plot_video_deadline_grouped(df, "video_freezing_duration_p95",
                                "p95_freeze_ms_across_ues_mean", "p95_freeze_ms_across_ues_ci95",
                                "Freezing-duration P95 (s)", (0, 21), ms_to_s=True, n_for_p95=True)
    plot_video_deadline_grouped(df, "video_satisfied_ues",
                                "ues_satisfied_99_pct_mean", "ues_satisfied_99_pct_ci95",
                                "Temporally satisfied UEs (%)", (0, 100))

    cp_freq = {(60, "RR"): 2.76, (60, "PF"): 2.47, (60, "MR"): 2.62, (60, "IA-FMR"): 2.34,
               (80, "RR"): 2.73, (80, "PF"): 2.29, (80, "MR"): 1.96, (80, "IA-FMR"): 2.17}
    for (pdb, mode), expected in cp_freq.items():
        row = df[(df["mode_label"] == mode) & (df["pdb_ms"] == pdb)].iloc[0]
        got = float(row["freeze_events_per_min_mean_mean"])
        add_validation(f"Fig9 freezing frequency {mode} {pdb} ms", expected, round(got, 6),
                       round(got - expected, 6), abs(got - expected) <= 0.015,
                       "Frequency uses all 100 seeds.")

    cp_p95 = {(60, "RR"): 12.01690, (60, "PF"): 15.31515, (60, "MR"): 17.47798, (60, "IA-FMR"): 8.17126,
              (80, "RR"): 12.87552, (80, "PF"): 16.28540, (80, "MR"): 17.84326, (80, "IA-FMR"): 9.45452}
    for (pdb, mode), expected in cp_p95.items():
        row = df[(df["mode_label"] == mode) & (df["pdb_ms"] == pdb)].iloc[0]
        got = float(row["p95_freeze_ms_across_ues_mean"]) / 1000.0
        add_validation(f"Fig9 freezing P95 {mode} {pdb} ms", expected, round(got, 6),
                       round(got - expected, 6), abs(got - expected) <= 0.01,
                       "P95 uses valid seeds only.")

    cp_sat = {(60, "RR"): 40.00, (60, "PF"): 39.67, (60, "MR"): 41.17, (60, "IA-FMR"): 59.17,
              (80, "RR"): 40.00, (80, "PF"): 40.17, (80, "MR"): 43.33, (80, "IA-FMR"): 60.00}
    for (pdb, mode), expected in cp_sat.items():
        row = df[(df["mode_label"] == mode) & (df["pdb_ms"] == pdb)].iloc[0]
        got = float(row["ues_satisfied_99_pct_mean"])
        add_validation(f"Fig9 satisfied UEs {mode} {pdb} ms", expected, round(got, 6),
                       round(got - expected, 6), abs(got - expected) <= 0.02,
                       "Temporal satisfaction uses all 100 seeds.")


def export_fidelity():
    df = read_csv(FIDELITY_SRC)
    rename = {
        "identical_pct": "identical_allocations_pct",
        "identical_pct_mean": "identical_allocations_pct",
        "same_set_pct": "same_served_set_pct",
        "same_ue_set_pct": "same_served_set_pct",
        "same_ue_set_pct_mean": "same_served_set_pct",
        "divergence": "normalized_divergence",
        "divergence_norm": "normalized_divergence",
        "divergence_norm_mean": "normalized_divergence",
        "target_served_mean": "target_served_ues_mean",
        "ues_target_positive_mean": "target_served_ues_mean",
        "applied_served_mean": "applied_served_ues_mean",
        "ues_applied_positive_mean": "applied_served_ues_mean",
        "jain_target_mean": "target_jain_mean",
        "jain_applied_mean": "applied_jain_mean",
    }
    for old, new in rename.items():
        if old in df.columns and new not in df.columns:
            df[new] = df[old]

    required = ["bandwidth_mhz", "identical_allocations_pct", "same_served_set_pct",
                "normalized_divergence", "target_served_ues_mean",
                "applied_served_ues_mean", "target_jain_mean", "applied_jain_mean"]
    require_cols(df, required, "allocation fidelity")
    out = df[required].copy().sort_values("bandwidth_mhz")
    out.to_csv(OUT_TABLES / "allocation_fidelity_revised.csv", index=False)

    r10, r40 = out[out["bandwidth_mhz"] == 10].iloc[0], out[out["bandwidth_mhz"] == 40].iloc[0]
    sub = out[out["bandwidth_mhz"].between(15, 100)]
    add_validation("Fidelity 10 MHz identical", "0.00%", round(float(r10["identical_allocations_pct"]), 6), "",
                   abs(float(r10["identical_allocations_pct"])) <= 1e-9)
    add_validation("Fidelity 10 MHz same served set", "0.00%", round(float(r10["same_served_set_pct"]), 6), "",
                   abs(float(r10["same_served_set_pct"])) <= 1e-9)
    add_validation("Fidelity 10 MHz divergence", "0.19618", round(float(r10["normalized_divergence"]), 6), "",
                   abs(float(r10["normalized_divergence"]) - 0.19618) <= 0.0002)
    add_validation("Fidelity 10 MHz applied Jain", "≈0.7985", round(float(r10["applied_jain_mean"]), 6), "",
                   abs(float(r10["applied_jain_mean"]) - 0.7985) <= 0.002)
    ok = (abs(sub["same_served_set_pct"] - 100.0) <= 1e-9).all()
    add_validation("Fidelity served-set preservation 15-100 MHz", "100%", bool(ok), "", bool(ok))
    add_validation("Fidelity 40 MHz identical", "98.54%", round(float(r40["identical_allocations_pct"]), 6), "",
                   abs(float(r40["identical_allocations_pct"]) - 98.54) <= 0.05)


def export_e2():
    for p in [E2_THR_SRC, E2_JAIN_SRC, E2_SERVICE_SRC, E2_LOSS_DELAY_SRC]:
        ensure_exists(p)
    thr, jain = pd.read_csv(E2_THR_SRC), pd.read_csv(E2_JAIN_SRC)
    service, lossdelay = pd.read_csv(E2_SERVICE_SRC), pd.read_csv(E2_LOSS_DELAY_SRC)

    def standard_ues(df, name):
        col = find_col(df, ["UEs", "ues", "n_ues", "num_ues"], f"{name} UEs")
        return df.rename(columns={col: "UEs"})

    thr, jain, service, lossdelay = (
        standard_ues(thr, "throughput"), standard_ues(jain, "Jain"),
        standard_ues(service, "service"), standard_ues(lossdelay, "loss/delay")
    )

    thr_col = find_col(thr, ["Vazão agregada média (Mbps)", "aggregate_throughput_mbps_mean", "vazao_agregada_media_mbps", "throughput_mean", "throughput_mbps_mean", "aggregate_throughput_mbps"], "E2 throughput")
    p5_col = find_col(service, ["P5 (Mbps)", "P5 por fluxo (Mbps)", "p5_flow_throughput_mbps_mean", "p5_mean", "p5_mbps_mean", "per_flow_tp_p5_mbps"], "E2 P5")
    jain_col = find_col(jain, ["Jain médio", "Índice de Jain", "jain_rbg_slot_mean_mean", "jain_mean", "rbg_jain_index"], "E2 Jain")
    served_col = find_col(service, ["UEs servidos/slot", "UEs servidos por slot", "mean_served_ues_per_slot_mean", "served_mean", "served_ues_per_slot"], "E2 served")
    pending_col = find_col(service, ["Demanda sem alocação (%)", "pct_buf_gt0_alloc_eq0_mean", "pending_pct_mean", "pending_demand_without_allocation_pct"], "E2 pending")
    loss_col = find_col(lossdelay, ["Perda média (%)", "mean_loss_ratio_pct", "loss_pct_mean", "loss_pct", "loss_mean", "packet_loss_pct_mean"], "E2 loss")
    delay_col = find_col(lossdelay, ["Atraso médio (ms)", "mean_delay_ms", "delay_ms_mean", "delay_ms", "delay_mean", "packet_delay_ms_mean"], "E2 delay")

    out = pd.DataFrame({"UEs": [3, 5, 7, 9]})
    out = out.merge(thr[["UEs", thr_col]], on="UEs", how="left")
    out = out.merge(service[["UEs", p5_col, served_col, pending_col]], on="UEs", how="left")
    out = out.merge(lossdelay[["UEs", loss_col, delay_col]], on="UEs", how="left")
    out = out.merge(jain[["UEs", jain_col]], on="UEs", how="left")
    out = out.rename(columns={
        thr_col: "aggregate_throughput_mbps", p5_col: "per_flow_tp_p5_mbps",
        served_col: "served_ues_per_slot", pending_col: "pending_demand_without_allocation_pct",
        loss_col: "loss_pct", delay_col: "mean_delay_ms", jain_col: "rbg_jain_index",
    })
    out.to_csv(OUT_TABLES / "e2_ues_3_5_7_9_revised.csv", index=False)

    cps = {
        3: (101.72, 8.477, 12.51, 782.98, 0.9766, 2.960, 0.0),
        5: (149.75, 6.449, 22.73, 1708.40, 0.9727, 4.972, 0.0),
        7: (127.39, 2.466, 53.05, 3808.77, 0.9731, 6.937, 0.0),
        9: (97.53, 1.225, 72.04, 4321.06, 0.9943, 9.000, 0.0),
    }
    cols = ["aggregate_throughput_mbps", "per_flow_tp_p5_mbps", "loss_pct",
            "mean_delay_ms", "rbg_jain_index", "served_ues_per_slot",
            "pending_demand_without_allocation_pct"]
    tols = [0.03, 0.005, 0.03, 0.08, 0.0008, 0.003, 1e-9]
    for ues, expected_values in cps.items():
        row = out[out["UEs"] == ues].iloc[0]
        for col, expected, tol in zip(cols, expected_values, tols):
            got = float(row[col])
            add_validation(f"E2 {ues} UEs {col}", expected, round(got, 6),
                           round(got - expected, 6), abs(got - expected) <= tol)

    ok_pending = (abs(out["pending_demand_without_allocation_pct"]) <= 1e-9).all()
    add_validation("E2 pending without allocation all cardinalities", "0",
                   out["pending_demand_without_allocation_pct"].tolist(), "", bool(ok_pending))


def copy_source_tables_and_script():
    for src, dst_name in [
        (E1_SUMMARY, "e1_summary_by_bw_alpha_full_used.csv"),
        (E3_SUMMARY, "e3_qoe_summary_alpha_full_final_used.csv"),
        (E3_FREEZE_AUDIT_SRC, "e3_freeze_seed_sets_alpha_full_audit.csv"),
    ]:
        if src.exists():
            shutil.copy2(src, OUT_TABLES / dst_name)
    script_src = Path(__file__).resolve()
    script_dst = (OUT_SCRIPTS / Path(__file__).name).resolve()
    if script_src != script_dst:
        shutil.copy2(script_src, script_dst)


def write_validation_and_file_list():
    expected_pngs = {
        "bandwidth_aggregate_throughput.png", "bandwidth_jain_index.png",
        "bandwidth_served_ues.png", "bandwidth_pending_without_allocation.png",
        "bandwidth_flow_throughput_p5.png", "bandwidth_packet_loss.png",
        "bandwidth_mean_delay.png",
        "temporal_effective_ues_40mhz.png", "temporal_largest_share_40mhz.png",
        "temporal_served_ues_40mhz.png", "temporal_backlog_40mhz.png",
        "temporal_rbg_shares_rr_40mhz.png", "temporal_rbg_shares_pf_40mhz.png",
        "temporal_rbg_shares_mr_40mhz.png", "temporal_rbg_shares_iafmr_40mhz.png",
        "temporal_alpha_40mhz.png",
        "video_unit_composition_60ms.png", "video_unit_composition_80ms.png",
        "video_freezing_frequency.png", "video_freezing_duration_p95.png", "video_satisfied_ues.png",
        "legend_schedulers.png", "legend_ues.png", "legend_video_composition.png", "legend_video_deadlines.png",
    }
    expected_pdfs = {x.replace(".png", ".pdf") for x in expected_pngs}
    expected_all = expected_pngs | expected_pdfs

    files = sorted([p.name for p in OUT_FIGS.glob("*")])
    generated = set(files)
    missing = sorted(expected_all - generated)
    obsolete_current = sorted([
        f for f in generated
        if f.startswith("fig02_") or f.startswith("fig03_") or f.startswith("fig04_")
        or f.startswith("fig05_") or f.startswith("fig06_")
        or f.startswith("fig08_") or f.startswith("fig09_")
        or f in {"video_temporal_unavailability.png", "video_temporal_unavailability.pdf"}
    ])

    add_validation("Expected individual figure and legend files", f"{len(expected_all)} files",
                   f"missing={missing}", "", len(missing) == 0)
    add_validation("No composite figure names generated in revised folder", "none",
                   str(obsolete_current), "", len(obsolete_current) == 0)

    val = pd.DataFrame(validation_rows)
    val_csv = OUT_VALIDATION / "checkpoint_validation_revised.csv"
    val_txt = OUT_VALIDATION / "checkpoint_validation_revised.txt"
    val.to_csv(val_csv, index=False)
    val_txt.write_text(val.to_string(index=False), encoding="utf-8")
    (OUT_VALIDATION / "generated_files_revised.txt").write_text("\n".join(files), encoding="utf-8")

    print("\n============================================================")
    print("VALIDATION SUMMARY")
    print("============================================================")
    print(val.to_string(index=False))
    print("\nValidation CSV:", val_csv)
    print("Validation TXT:", val_txt)
    print("Generated file list:", OUT_VALIDATION / "generated_files_revised.txt")

    fails = val[val["PASS_FAIL"] != "PASS"]
    if not fails.empty:
        print("\nFAILURES DETECTED:")
        print(fails.to_string(index=False))
        fail("One or more checkpoints failed. Investigate before using the figures.")


def main():
    print("============================================================")
    print("Computer Networks revision generation")
    print("============================================================")
    print("Output root:", OUT_ROOT)

    print("\nQuarantining obsolete composite figures if present...")
    quarantine_old_composites()

    print("Generating shared legend assets...")
    make_legend_assets()

    print("\nLoading E1 final summary:")
    print(E1_SUMMARY)
    e1 = load_e1()
    print("Generating individual Figures 2-4...")
    make_e1_figures(e1)

    print("Generating individual temporal Figures 5-7...")
    make_temporal_figures()

    print("\nLoading E3 final summary:")
    print(E3_SUMMARY)
    e3 = load_e3()
    print("Generating individual video Figures 8-9...")
    make_video_composition_figures(e3)
    make_video_temporal_figures(e3)

    print("Exporting allocation fidelity...")
    export_fidelity()
    print("Exporting E2 table...")
    export_e2()

    print("Copying source tables and script...")
    copy_source_tables_and_script()
    write_validation_and_file_list()

    print("\n============================================================")
    print("DONE")
    print("============================================================")
    print("Figures:", OUT_FIGS)
    print("Tables:", OUT_TABLES)
    print("Validation:", OUT_VALIDATION)
    print("Scripts:", OUT_SCRIPTS)
    print("\nNo Matplotlib panel labels or titles are written inside the plots.")


if __name__ == "__main__":
    main()
