#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate the public temporal E1 figures for the 40 MHz representative run.

Inputs are the consolidated CSV files in:
  data/e1_bandwidth/temporal_40mhz/

No raw ns-3 slot logs are required.
"""

from pathlib import Path
import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


MODE_ORDER = ["RR", "PF", "MR", "IA-FMR"]

MODE_COLORS = {
    "RR": "#0072B2",
    "PF": "#E69F00",
    "MR": "#D55E00",
    "IA-FMR": "#009E73",
}

MODE_STYLES = {
    "RR": "-",
    "PF": "--",
    "MR": "-.",
    "IA-FMR": "-",
}

UE_MARKERS = ["o", "s", "^", "v", "D", "P", "X", "<", ">"]


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
        "legend.fontsize": 8.0,
        "axes.linewidth": 0.8,
    })


def normalize_mode(value):
    value = str(value).strip()
    low = value.lower()

    if value in MODE_ORDER:
        return value
    if low == "rr":
        return "RR"
    if low == "pf":
        return "PF"
    if low == "mr":
        return "MR"
    if low in {"fmr_rl", "ia-fmr", "ia_fmr", "fmr"}:
        return "IA-FMR"
    return value


def read_csv(path, required_cols, label):
    path = Path(path)
    if not path.is_file():
        raise SystemExit(f"{label}: file not found: {path}")

    df = pd.read_csv(path)
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise SystemExit(
            f"{label}: missing required columns: {', '.join(missing)}"
        )
    return df


def style_axis(ax):
    ax.grid(True, axis="y", linewidth=0.45, alpha=0.32)
    ax.grid(False, axis="x")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def save_figure(fig, outdir, filename):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / filename
    fig.savefig(path, bbox_inches="tight", pad_inches=0.08, dpi=600)
    plt.close(fig)
    print(f"[OK] {path}")


def pt_to_in_name(name):
    p = Path(name)
    return f"{p.stem}_IN{p.suffix}"


def validate_mode_time_table(df, label):
    df = df.copy()
    df["mode"] = df["mode"].map(normalize_mode)

    modes = set(df["mode"].unique())
    if modes != set(MODE_ORDER):
        raise SystemExit(
            f"{label}: expected modes {MODE_ORDER}, found {sorted(modes)}"
        )

    counts = df.groupby("mode")["time_bin_s"].nunique()
    if len(set(counts.tolist())) != 1:
        raise SystemExit(
            f"{label}: schedulers do not have the same number of time bins."
        )

    return df


def plot_modes(
    df,
    y_col,
    ylabel_pt,
    ylabel_en,
    filename_pt,
    outdir,
    ylim=None,
):
    for lang in ["pt", "en"]:
        fig, ax = plt.subplots(figsize=(7.2, 3.35))

        for mode in MODE_ORDER:
            sub = df[df["mode"] == mode].sort_values("time_bin_s")
            ax.plot(
                sub["time_bin_s"],
                sub[y_col],
                label=mode,
                color=MODE_COLORS[mode],
                linestyle=MODE_STYLES[mode],
                linewidth=2.0 if mode == "IA-FMR" else 1.7,
            )

        ax.set_xlabel("Tempo (s)" if lang == "pt" else "Time (s)")
        ax.set_ylabel(ylabel_pt if lang == "pt" else ylabel_en)

        if ylim is not None:
            ax.set_ylim(*ylim)

        style_axis(ax)
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.20),
            ncol=4,
            frameon=False,
            handlelength=2.0,
            columnspacing=1.3,
        )

        filename = filename_pt if lang == "pt" else pt_to_in_name(filename_pt)
        save_figure(fig, outdir, filename)


def plot_alpha_seed(alpha_seed, outdir):
    for lang in ["pt", "en"]:
        fig, ax = plt.subplots(figsize=(7.2, 3.35))

        ax.plot(
            alpha_seed["time_bin_s"],
            alpha_seed["alpha"],
            linewidth=0.9,
            alpha=0.30,
            color=MODE_COLORS["IA-FMR"],
            label="α" if lang == "pt" else "α",
        )

        ax.plot(
            alpha_seed["time_bin_s"],
            alpha_seed["alpha_smooth"],
            linewidth=2.0,
            color=MODE_COLORS["IA-FMR"],
            label="α suavizado" if lang == "pt" else "Smoothed α",
        )

        ax.set_xlabel("Tempo (s)" if lang == "pt" else "Time (s)")
        ax.set_ylabel("Coeficiente α" if lang == "pt" else "Coefficient α")
        ax.set_ylim(0.0, 1.02)

        style_axis(ax)
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.18),
            ncol=2,
            frameon=False,
        )

        name = (
            "temporal_alpha_seed_47889.png"
            if lang == "pt"
            else "temporal_alpha_seed_47889_IN.png"
        )
        save_figure(fig, outdir, name)


def plot_alpha_all_seeds(alpha_all, outdir):
    for lang in ["pt", "en"]:
        fig, ax = plt.subplots(figsize=(7.2, 3.35))

        x = pd.to_numeric(alpha_all["time_s"], errors="coerce").to_numpy(float)
        mean = pd.to_numeric(
            alpha_all["alpha_mean_smooth"], errors="coerce"
        ).to_numpy(float)
        ci = pd.to_numeric(
            alpha_all["alpha_ci95_smooth"], errors="coerce"
        ).to_numpy(float)

        ax.plot(
            x,
            mean,
            linewidth=2.0,
            color=MODE_COLORS["IA-FMR"],
            label=(
                "Média de α (100 seeds)"
                if lang == "pt"
                else "Mean α (100 seeds)"
            ),
        )

        ax.fill_between(
            x,
            mean - ci,
            mean + ci,
            color=MODE_COLORS["IA-FMR"],
            alpha=0.16,
            linewidth=0,
            label="IC 95%" if lang == "pt" else "95% CI",
        )

        ax.set_xlabel("Tempo (s)" if lang == "pt" else "Time (s)")
        ax.set_ylabel("Coeficiente α" if lang == "pt" else "Coefficient α")
        ax.set_ylim(0.0, 1.02)

        style_axis(ax)
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.18),
            ncol=2,
            frameon=False,
        )

        name = (
            "temporal_alpha_all_seeds.png"
            if lang == "pt"
            else "temporal_alpha_all_seeds_IN.png"
        )
        save_figure(fig, outdir, name)


def plot_rbg_share_per_mode(rbg, outdir):
    modes = MODE_ORDER

    for mode in modes:
        sub_mode = rbg[rbg["mode"] == mode].copy()
        ues = sorted(pd.to_numeric(sub_mode["ue"]).dropna().astype(int).unique())

        if ues != list(range(1, 10)):
            raise SystemExit(
                f"RBG share ({mode}): expected UEs 1..9, found {ues}"
            )

        for lang in ["pt", "en"]:
            fig, ax = plt.subplots(figsize=(7.2, 3.55))

            for idx, ue in enumerate(ues):
                sub = (
                    sub_mode[sub_mode["ue"] == ue]
                    .sort_values("time_bin_s")
                )

                ax.plot(
                    sub["time_bin_s"],
                    sub["share_pct_smooth"],
                    label=f"UE {ue}",
                    linewidth=1.25,
                    marker=UE_MARKERS[idx],
                    markersize=2.5,
                    markevery=30,
                )

            ax.set_xlabel("Tempo (s)" if lang == "pt" else "Time (s)")
            ax.set_ylabel(
                "Participação na alocação de RBGs (%)"
                if lang == "pt"
                else "RBG allocation share (%)"
            )
            ax.set_ylim(bottom=0)

            style_axis(ax)
            ax.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, 1.27),
                ncol=5,
                frameon=False,
                handlelength=1.8,
                columnspacing=1.0,
            )

            slug = mode.lower().replace("-", "_")
            name = (
                f"temporal_rbg_share_{slug}.png"
                if lang == "pt"
                else f"temporal_rbg_share_{slug}_IN.png"
            )
            save_figure(fig, outdir, name)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate temporal 40 MHz E1 figures from the consolidated "
            "public CSV files."
        )
    )
    parser.add_argument(
        "--data-dir",
        required=True,
        help=(
            "Directory containing alpha_all_seeds.csv, "
            "alpha_seed_47889.csv, backlog_seed_47889.csv, "
            "concentration_seed_47889.csv, rbg_share_seed_47889.csv "
            "and served_ues_seed_47889.csv."
        ),
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where the figures will be written.",
    )
    args = parser.parse_args()

    setup_matplotlib()

    data_dir = Path(args.data_dir)

    alpha_all = read_csv(
        data_dir / "alpha_all_seeds.csv",
        [
            "time_s",
            "alpha_mean",
            "alpha_ci95",
            "n_seeds",
            "alpha_mean_smooth",
            "alpha_ci95_smooth",
        ],
        "alpha_all_seeds",
    )

    alpha_seed = read_csv(
        data_dir / "alpha_seed_47889.csv",
        ["time_bin_s", "alpha", "alpha_smooth"],
        "alpha_seed_47889",
    )

    backlog = read_csv(
        data_dir / "backlog_seed_47889.csv",
        ["mode", "time_bin_s", "backlog_mbit", "backlog_mbit_smooth"],
        "backlog_seed_47889",
    )

    concentration = read_csv(
        data_dir / "concentration_seed_47889.csv",
        [
            "mode",
            "time_bin_s",
            "effective_ues",
            "top1_share_pct",
            "effective_ues_smooth",
            "top1_share_pct_smooth",
        ],
        "concentration_seed_47889",
    )

    rbg = read_csv(
        data_dir / "rbg_share_seed_47889.csv",
        [
            "mode",
            "time_bin_s",
            "ue",
            "alloc_rbg",
            "total_alloc_rbg",
            "share_pct",
            "share_pct_smooth",
        ],
        "rbg_share_seed_47889",
    )

    served = read_csv(
        data_dir / "served_ues_seed_47889.csv",
        ["mode", "time_bin_s", "served_ues", "served_ues_smooth"],
        "served_ues_seed_47889",
    )

    # Structural validation.
    if len(alpha_all) != 300 or alpha_all["n_seeds"].nunique() != 1:
        raise SystemExit(
            "alpha_all_seeds: expected 300 rows and a single n_seeds value."
        )

    if int(alpha_all["n_seeds"].iloc[0]) != 100:
        raise SystemExit("alpha_all_seeds: expected n_seeds = 100.")

    if len(alpha_seed) != 300:
        raise SystemExit("alpha_seed_47889: expected 300 rows.")

    backlog = validate_mode_time_table(backlog, "backlog")
    concentration = validate_mode_time_table(concentration, "concentration")
    served = validate_mode_time_table(served, "served_ues")

    rbg = rbg.copy()
    rbg["mode"] = rbg["mode"].map(normalize_mode)

    if set(rbg["mode"].unique()) != set(MODE_ORDER):
        raise SystemExit("rbg_share: scheduler set is inconsistent.")

    if len(rbg) != 10800:
        raise SystemExit(
            f"rbg_share: expected 10800 rows, found {len(rbg)}."
        )

    print("Temporal E1 validation:")
    print("  alpha_all_seeds: 300 bins, 100 seeds")
    print("  alpha_seed_47889: 300 bins")
    print("  backlog: 4 schedulers × 300 bins")
    print("  concentration: 4 schedulers × 300 bins")
    print("  served UEs: 4 schedulers × 300 bins")
    print("  RBG share: 4 schedulers × 300 bins × 9 UEs")
    print("[OK] Structural validation passed.")

    plot_alpha_all_seeds(alpha_all, args.output_dir)
    plot_alpha_seed(alpha_seed, args.output_dir)

    plot_modes(
        backlog,
        "backlog_mbit_smooth",
        "Backlog (Mbit)",
        "Backlog (Mbit)",
        "temporal_backlog_seed_47889.png",
        args.output_dir,
    )

    plot_modes(
        served,
        "served_ues_smooth",
        "UEs servidos",
        "Served UEs",
        "temporal_served_ues_seed_47889.png",
        args.output_dir,
        ylim=(0, 9.3),
    )

    plot_modes(
        concentration,
        "effective_ues_smooth",
        "Número efetivo de UEs",
        "Effective number of UEs",
        "temporal_effective_ues_seed_47889.png",
        args.output_dir,
        ylim=(0, 9.3),
    )

    plot_modes(
        concentration,
        "top1_share_pct_smooth",
        "Participação do UE dominante (%)",
        "Dominant-UE share (%)",
        "temporal_top1_share_seed_47889.png",
        args.output_dir,
        ylim=(0, 100),
    )

    plot_rbg_share_per_mode(rbg, args.output_dir)


if __name__ == "__main__":
    main()
