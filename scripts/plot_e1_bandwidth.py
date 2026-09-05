#!/usr/bin/env python3
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

BANDS = [10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100]
MODE_ORDER = ["RR", "PF", "MR", "IA-FMR"]

STYLE = {
    "RR": {"color": "#0072B2", "linestyle": "-",  "marker": "o", "linewidth": 1.7},
    "PF": {"color": "#E69F00", "linestyle": "--", "marker": "s", "linewidth": 1.7},
    "MR": {"color": "#D55E00", "linestyle": "-.", "marker": "^", "linewidth": 1.7},
    "IA-FMR": {"color": "#009E73", "linestyle": "-", "marker": "D", "linewidth": 2.2},
}

ALIASES = {
    "aggregate_throughput_mbps_mean": [
        "aggregate_throughput_mbps_mean"
    ],
    "aggregate_throughput_mbps_ci95": [
        "aggregate_throughput_mbps_ci95"
    ],

    "jain_rbg_slot_mean_mean": [
        "jain_rbg_slot_mean_mean",
        "jain_rbg_mean_mean",
        "jain_rbg_mean",
        "jain_mean"
    ],
    "jain_rbg_slot_mean_ci95": [
        "jain_rbg_slot_mean_ci95",
        "jain_rbg_mean_ci95",
        "jain_ci95"
    ],

    "served_ues_per_slot_mean": [
        "mean_served_ues_per_slot_mean",
        "served_ues_per_slot_mean",
        "served_ues_mean",
        "served_ues_per_slot_mean_mean",
        "avg_served_ues_mean",
        "n_served_ues_mean"
    ],
    "served_ues_per_slot_ci95": [
        "mean_served_ues_per_slot_ci95",
        "served_ues_per_slot_ci95",
        "served_ues_ci95",
        "served_ues_per_slot_mean_ci95",
        "avg_served_ues_ci95",
        "n_served_ues_ci95"
    ],

    "pending_without_allocation_ratio_mean": [
        "pct_buf_gt0_alloc_eq0_mean",
        "pending_without_allocation_ratio_mean",
        "pending_no_alloc_ratio_mean",
        "starvation_real_ratio_mean",
        "starvation_real_mean",
        "pending_without_allocation_mean",
        "mean_zero_ue_percent_mean"
    ],
    "pending_without_allocation_ratio_ci95": [
        "pct_buf_gt0_alloc_eq0_ci95",
        "pending_without_allocation_ratio_ci95",
        "pending_no_alloc_ratio_ci95",
        "starvation_real_ratio_ci95",
        "starvation_real_ci95",
        "pending_without_allocation_ci95",
        "mean_zero_ue_percent_ci95"
    ],

    "p5_flow_throughput_mbps_mean": [
        "p5_flow_throughput_mbps_mean",
        "flow_throughput_mbps_p5_mean",
        "flow_throughput_p5_mbps_mean",
        "p5_throughput_mbps_mean"
    ],
    "p5_flow_throughput_mbps_ci95": [
        "p5_flow_throughput_mbps_ci95",
        "flow_throughput_mbps_p5_ci95",
        "flow_throughput_p5_mbps_ci95",
        "p5_throughput_mbps_ci95"
    ],

    "mean_loss_ratio_mean": [
        "mean_loss_ratio_mean",
        "loss_ratio_mean",
        "packet_loss_ratio_mean",
        "mean_packet_loss_ratio_mean"
    ],
    "mean_loss_ratio_ci95": [
        "mean_loss_ratio_ci95",
        "loss_ratio_ci95",
        "packet_loss_ratio_ci95",
        "mean_packet_loss_ratio_ci95"
    ],

    "mean_delay_ms_mean": [
        "mean_delay_ms_mean",
        "delay_ms_mean",
        "packet_delay_ms_mean",
        "mean_packet_delay_ms_mean"
    ],
    "mean_delay_ms_ci95": [
        "mean_delay_ms_ci95",
        "delay_ms_ci95",
        "packet_delay_ms_ci95",
        "mean_packet_delay_ms_ci95"
    ],
}

FIGURES = [
    {
        "name": "e1_aggregate_throughput_mbps",
        "mean": "aggregate_throughput_mbps_mean",
        "ci": "aggregate_throughput_mbps_ci95",
        "ylabel": "Aggregate throughput (Mbps)",
        "percent": False,
        "legend": True,
    },
    {
        "name": "e1_jain_rbg_slot",
        "mean": "jain_rbg_slot_mean_mean",
        "ci": "jain_rbg_slot_mean_ci95",
        "ylabel": "Jain index over RBG allocation",
        "percent": False,
        "ylim": (0.0, 1.02),
        "legend": True,
    },
    {
        "name": "e1_served_ues_per_slot",
        "mean": "served_ues_per_slot_mean",
        "ci": "served_ues_per_slot_ci95",
        "ylabel": "Served UEs per slot",
        "percent": False,
        "legend": True,
    },
    {
        "name": "e1_pending_without_allocation",
        "mean": "pending_without_allocation_ratio_mean",
        "ci": "pending_without_allocation_ratio_ci95",
        "ylabel": "Pending demand without allocation (%)",
        "percent": True,
        "ylim": (0.0, 100.0),
        "legend": True,
    },
    {
        "name": "e1_p5_flow_throughput_mbps",
        "mean": "p5_flow_throughput_mbps_mean",
        "ci": "p5_flow_throughput_mbps_ci95",
        "ylabel": "Per-flow throughput P5 (Mbps)",
        "percent": False,
        "legend": True,
    },
    {
        "name": "e1_mean_loss_ratio",
        "mean": "mean_loss_ratio_mean",
        "ci": "mean_loss_ratio_ci95",
        "ylabel": "Undelivered packet ratio (%)",
        "percent": True,
        "ylim": (0.0, 100.0),
        "legend": True,
    },
    {
        "name": "e1_mean_delay_ms",
        "mean": "mean_delay_ms_mean",
        "ci": "mean_delay_ms_ci95",
        "ylabel": "Mean packet delay (ms)",
        "percent": False,
        "legend": True,
    },
]

def setup_matplotlib():
    plt.rcParams.update({
        "figure.dpi": 120,
        "savefig.dpi": 600,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "STIX Two Text", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "axes.labelsize": 9.5,
        "xtick.labelsize": 8.0,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.2,
        "axes.linewidth": 0.8,
    })

def normalize_mode(m):
    ml = str(m).strip().lower()
    if ml == "rr":
        return "RR"
    if ml == "pf":
        return "PF"
    if ml == "mr":
        return "MR"
    if ml in {"fmr", "fmr_rl", "ia_fmr", "ia-fmr", "ia-fmr"}:
        return "IA-FMR"
    return str(m)

def resolve_col(df, canonical):
    for c in ALIASES.get(canonical, [canonical]):
        if c in df.columns:
            return c
    return None

def style_axis(ax):
    ax.grid(True, axis="y", linewidth=0.45, alpha=0.35)
    ax.grid(False, axis="x")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlabel("Bandwidth (MHz)")
    ax.set_xticks(BANDS)
    ax.set_xlim(9, 102)

def save(fig, outdir, name):
    outdir.mkdir(parents=True, exist_ok=True)
    fig.savefig(outdir / f"{name}.pdf", bbox_inches="tight", pad_inches=0.08)
    fig.savefig(outdir / f"{name}.png", bbox_inches="tight", pad_inches=0.08, dpi=600)
    print(f"[OK] saved: {outdir / f'{name}.pdf'}")
    print(f"[OK] saved: {outdir / f'{name}.png'}")

def plot_metric(df, spec, outdir):
    mean_col = resolve_col(df, spec["mean"])
    ci_col = resolve_col(df, spec["ci"])

    if mean_col is None:
        print(f"[WARN] Pulando {spec['name']}: coluna média ausente.")
        print(f"       Esperava uma destas: {ALIASES.get(spec['mean'], [spec['mean']])}")
        return

    fig, ax = plt.subplots(figsize=(7.2, 3.25))

    for mode in MODE_ORDER:
        sub = df[df["mode"] == mode].copy()
        if sub.empty:
            continue

        sub = sub.sort_values("bandwidth_mhz")
        x = sub["bandwidth_mhz"].astype(float)
        y = sub[mean_col].astype(float)

        # Percentuais podem aparecer no CSV como fração [0,1] ou como pontos percentuais [0,100].
        # A decisão de escala deve ser tomada pela média. O IC deve seguir exatamente a mesma escala.
        scale_percent = bool(spec.get("percent", False) and y.max(skipna=True) <= 1.5)
        if scale_percent:
            y = y * 100.0

        style = STYLE[mode]
        ax.plot(
            x, y,
            label=mode,
            color=style["color"],
            linestyle=style["linestyle"],
            marker=style["marker"],
            linewidth=style["linewidth"],
            markersize=4.2,
        )

        if ci_col is not None:
            ci = sub[ci_col].astype(float)

            # O IC usa a mesma escala aplicada à média.
            if scale_percent:
                ci = ci * 100.0

            ax.fill_between(
                x.to_numpy(),
                (y - ci).to_numpy(),
                (y + ci).to_numpy(),
                color=style["color"],
                alpha=0.12,
                linewidth=0,
            )

    ax.set_ylabel(spec["ylabel"])
    style_axis(ax)

    if spec.get("percent", False):
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100))

    if "ylim" in spec:
        ax.set_ylim(*spec["ylim"])

    if spec.get("legend", False):
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.20),
            ncol=4,
            frameon=False,
            handlelength=2.0,
            columnspacing=1.0,
        )

    save(fig, outdir, spec["name"])
    plt.close(fig)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    setup_matplotlib()

    df = pd.read_csv(args.summary)
    df["mode"] = df["mode"].map(normalize_mode)
    df = df[df["bandwidth_mhz"].isin(BANDS)].copy()

    print("[INFO] summary:", args.summary)
    print("[INFO] shape:", df.shape)
    print("[INFO] modes:", sorted(df["mode"].dropna().unique()))
    print("[INFO] bands:", sorted(df["bandwidth_mhz"].dropna().unique()))
    print("[INFO] columns:")
    for c in df.columns:
        print("  ", c)

    outdir = Path(args.output_dir)

    for spec in FIGURES:
        plot_metric(df, spec, outdir)

if __name__ == "__main__":
    main()
