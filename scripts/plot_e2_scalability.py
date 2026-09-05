#!/usr/bin/env python3
from pathlib import Path
import argparse

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


IAFMR_STYLE = {
    "color": "#009E73",
    "linestyle": "-",
    "marker": "D",
    "linewidth": 2.2,
}


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
        "xtick.labelsize": 8.2,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.2,
        "axes.linewidth": 0.8,
    })


def style_axis(ax):
    ax.grid(True, axis="y", linewidth=0.45, alpha=0.35)
    ax.grid(False, axis="x")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def percent_scale(y, is_percent):
    y = pd.to_numeric(y, errors="coerce").astype(float)
    if not is_percent:
        return y, False
    scale = bool(y.max(skipna=True) <= 1.5)
    if scale:
        return y * 100.0, True
    return y, False


def pt_to_in_name(name):
    p = Path(name)
    return f"{p.stem}_IN{p.suffix}"


def save_figure(fig, outdir, filename):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / filename
    fig.savefig(path, bbox_inches="tight", pad_inches=0.08, dpi=600)
    print(f"[OK] {path}")


def plot_single_iafmr_line(
    df,
    x_col,
    mean_col,
    ci_col,
    xlabel,
    ylabel,
    output_name,
    outdir,
    percent=False,
    ylim=None,
    xticks=None,
):
    fig, ax = plt.subplots(figsize=(7.2, 3.25))

    sub = df.sort_values(x_col).copy()
    x = pd.to_numeric(sub[x_col], errors="coerce")
    y, scaled = percent_scale(sub[mean_col], percent)

    ax.plot(
        x,
        y,
        label="IA-FMR",
        color=IAFMR_STYLE["color"],
        linestyle=IAFMR_STYLE["linestyle"],
        marker=IAFMR_STYLE["marker"],
        linewidth=IAFMR_STYLE["linewidth"],
        markersize=4.4,
    )

    if ci_col and ci_col in sub.columns:
        ci = pd.to_numeric(sub[ci_col], errors="coerce")
        if scaled:
            ci = ci * 100.0
        ax.fill_between(
            x.to_numpy(),
            (y - ci).to_numpy(),
            (y + ci).to_numpy(),
            color=IAFMR_STYLE["color"],
            alpha=0.14,
            linewidth=0,
        )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if xticks is not None:
        ax.set_xticks(xticks)
    if ylim is not None:
        ax.set_ylim(*ylim)
    if percent:
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100))

    style_axis(ax)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.20),
        ncol=1,
        frameon=False,
        handlelength=2.0,
    )

    save_figure(fig, outdir, output_name)
    plt.close(fig)


E2_FIGS = [
    {
        "name_pt": "esc_ues_vazao_agregada_media_ic95.png",
        "mean": "aggregate_throughput_mbps_mean",
        "ci": "aggregate_throughput_mbps_ci95",
        "ylabel_pt": "Vazão agregada (Mbps)",
        "ylabel_en": "Aggregate throughput (Mbps)",
        "percent": False,
    },
    {
        "name_pt": "esc_ues_jain_rbg_ic95.png",
        "mean": "jain_rbg_slot_mean_mean",
        "ci": "jain_rbg_slot_mean_ci95",
        "ylabel_pt": "Índice de Jain sobre a alocação de RBGs",
        "ylabel_en": "Jain index over RBG allocation",
        "percent": False,
        "ylim": (0.0, 1.02),
    },
    {
        "name_pt": "esc_ues_ues_servidos_slot_ic95.png",
        "mean": "mean_served_ues_per_slot_mean",
        "ci": "mean_served_ues_per_slot_ci95",
        "ylabel_pt": "UEs servidos por slot",
        "ylabel_en": "Served UEs per slot",
        "percent": False,
    },
    {
        "name_pt": "esc_ues_p5_vazao_fluxo_ic95.png",
        "mean": "p5_flow_throughput_mbps_mean",
        "ci": "p5_flow_throughput_mbps_ci95",
        "ylabel_pt": "Percentil 5 da vazão por fluxo (Mbps)",
        "ylabel_en": "Per-flow throughput P5 (Mbps)",
        "percent": False,
    },
    {
        "name_pt": "esc_ues_taxa_perda_media_ic95.png",
        "mean": "mean_loss_ratio_mean",
        "ci": "mean_loss_ratio_ci95",
        "ylabel_pt": "Taxa de perda (%)",
        "ylabel_en": "Undelivered packet ratio (%)",
        "percent": True,
        "ylim": (0.0, 100.0),
    },
    {
        "name_pt": "esc_ues_atraso_medio_ic95.png",
        "mean": "mean_delay_ms_mean",
        "ci": "mean_delay_ms_ci95",
        "ylabel_pt": "Atraso médio de pacotes (ms)",
        "ylabel_en": "Mean packet delay (ms)",
        "percent": False,
    },
]


def main():
    parser = argparse.ArgumentParser(
        description="Generate IA-FMR scalability figures from the consolidated E2 summary."
    )
    parser.add_argument(
        "--summary",
        required=True,
        help="Path to data/e2_scalability/summary_by_ues.csv",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where the figures will be written.",
    )
    args = parser.parse_args()

    setup_matplotlib()

    summary = Path(args.summary)
    if not summary.is_file():
        raise SystemExit(f"Summary CSV not found: {summary}")

    df = pd.read_csv(summary)

    required = {"n_ues", "mode", "n_repetitions"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Missing required columns: {sorted(missing)}")

    if set(df["mode"].astype(str).unique()) != {"IA-FMR"}:
        raise SystemExit("E2 summary must contain only IA-FMR rows.")

    if sorted(pd.to_numeric(df["n_ues"]).astype(int).unique().tolist()) != [3, 5, 7, 9]:
        raise SystemExit("Expected n_ues values: 3, 5, 7, 9.")

    for spec in E2_FIGS:
        if spec["mean"] not in df.columns:
            print(f"[WARN] Missing column {spec['mean']}; skipping {spec['name_pt']}")
            continue

        plot_single_iafmr_line(
            df=df,
            x_col="n_ues",
            mean_col=spec["mean"],
            ci_col=spec.get("ci"),
            xlabel="Número de UEs",
            ylabel=spec["ylabel_pt"],
            output_name=spec["name_pt"],
            outdir=args.output_dir,
            percent=spec["percent"],
            ylim=spec.get("ylim"),
            xticks=[3, 5, 7, 9],
        )

        plot_single_iafmr_line(
            df=df,
            x_col="n_ues",
            mean_col=spec["mean"],
            ci_col=spec.get("ci"),
            xlabel="Number of UEs",
            ylabel=spec["ylabel_en"],
            output_name=pt_to_in_name(spec["name_pt"]),
            outdir=args.output_dir,
            percent=spec["percent"],
            ylim=spec.get("ylim"),
            xticks=[3, 5, 7, 9],
        )


if __name__ == "__main__":
    main()
