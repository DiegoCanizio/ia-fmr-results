#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


MODE_ORDER = ["RR", "PF", "MR", "IA-FMR"]
PDB_ORDER = [60.0, 80.0]

# Same scheduler colors used in the thesis figures.
COLORS = {
    "RR": "#0072B2",
    "PF": "#E69F00",
    "MR": "#D55E00",
    "IA-FMR": "#009E73",
}

# Distinguish PDB values by hatch.
PDB_HATCH = {
    60.0: "",
    80.0: "///",
}

# Video-unit composition colors.
COMP_COLORS = {
    "on_time": "#56B4E9",
    "late": "#E69F00",
    "lost": "#999999",
}


def setup_matplotlib():
    plt.rcParams.update({
        "figure.dpi": 120,
        "savefig.dpi": 600,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "STIX Two Text", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "legend.title_fontsize": 10,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.major.size": 3.5,
        "ytick.major.size": 3.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
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


def require_columns(df, cols, label):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise SystemExit(
            f"{label}: missing columns: {', '.join(missing)}"
        )


def load_summary(path):
    path = Path(path)
    if not path.is_file():
        raise SystemExit(f"Summary CSV not found: {path}")

    df = pd.read_csv(path)

    if "mode_label" not in df.columns:
        require_columns(df, ["mode"], "Summary")
        df["mode_label"] = df["mode"].map(normalize_mode)
    else:
        df["mode_label"] = df["mode_label"].map(normalize_mode)

    require_columns(df, ["pdb_ms", "n_seeds"], "Summary")

    df["pdb_ms"] = pd.to_numeric(df["pdb_ms"], errors="coerce")
    df = df[df["mode_label"].isin(MODE_ORDER)].copy()
    df = df[df["pdb_ms"].isin(PDB_ORDER)].copy()

    order_map = {m: i for i, m in enumerate(MODE_ORDER)}
    df["mode_order"] = df["mode_label"].map(order_map)
    df = df.sort_values(["pdb_ms", "mode_order"]).drop(columns=["mode_order"])

    expected_pairs = {
        (mode, pdb) for mode in MODE_ORDER for pdb in PDB_ORDER
    }
    actual_pairs = set(zip(df["mode_label"], df["pdb_ms"]))
    if actual_pairs != expected_pairs or len(df) != 8:
        raise SystemExit(
            "Summary must contain exactly 4 schedulers × 2 PDB values (8 rows)."
        )

    if not (pd.to_numeric(df["n_seeds"], errors="coerce") == 100).all():
        raise SystemExit("Expected n_seeds = 100 for all E3 rows.")

    return df


def percent_from_ratio(series):
    s = pd.to_numeric(series, errors="coerce")
    if s.dropna().empty:
        return s
    if s.dropna().max() <= 1.5:
        return s * 100.0
    return s


def make_composition_table(df):
    required = [
        "mode_label",
        "pdb_ms",
        "fsr_mean_mean",
        "late_frame_ratio_mean_mean",
        "lost_frame_ratio_mean_mean",
    ]
    require_columns(df, required, "Summary")

    comp = df[required].copy()
    comp["no_prazo_pct"] = percent_from_ratio(comp["fsr_mean_mean"])
    comp["tardias_pct"] = percent_from_ratio(comp["late_frame_ratio_mean_mean"])
    comp["nao_recebidas_pct"] = percent_from_ratio(comp["lost_frame_ratio_mean_mean"])

    # Residual adjustment only, matching the thesis plotting script,
    # so the stacked bars close visually at 100%.
    total = (
        comp["no_prazo_pct"]
        + comp["tardias_pct"]
        + comp["nao_recebidas_pct"]
    )
    comp["nao_recebidas_pct"] += 100.0 - total

    return comp[
        [
            "mode_label",
            "pdb_ms",
            "no_prazo_pct",
            "tardias_pct",
            "nao_recebidas_pct",
        ]
    ].copy()


def load_and_validate_composition(path, derived):
    path = Path(path)
    if not path.is_file():
        raise SystemExit(f"Composition CSV not found: {path}")

    comp = pd.read_csv(path)
    required = [
        "mode_label",
        "pdb_ms",
        "no_prazo_pct",
        "tardias_pct",
        "nao_recebidas_pct",
    ]
    require_columns(comp, required, "Composition")

    comp["mode_label"] = comp["mode_label"].map(normalize_mode)
    comp["pdb_ms"] = pd.to_numeric(comp["pdb_ms"], errors="coerce")

    comp = comp[
        comp["mode_label"].isin(MODE_ORDER)
        & comp["pdb_ms"].isin(PDB_ORDER)
    ].copy()

    order_map = {m: i for i, m in enumerate(MODE_ORDER)}
    comp["mode_order"] = comp["mode_label"].map(order_map)
    comp = comp.sort_values(["pdb_ms", "mode_order"]).drop(columns=["mode_order"])

    d = derived.copy()
    d["mode_order"] = d["mode_label"].map(order_map)
    d = d.sort_values(["pdb_ms", "mode_order"]).drop(columns=["mode_order"])

    if len(comp) != 8:
        raise SystemExit("Composition CSV must contain exactly 8 rows.")

    for col in ["no_prazo_pct", "tardias_pct", "nao_recebidas_pct"]:
        lhs = pd.to_numeric(comp[col], errors="coerce").to_numpy(float)
        rhs = pd.to_numeric(d[col], errors="coerce").to_numpy(float)
        if not np.allclose(lhs, rhs, rtol=1e-10, atol=1e-8, equal_nan=True):
            raise SystemExit(
                f"Composition CSV differs from values derived from summary: {col}"
            )

    return comp


def style_axis(ax):
    ax.grid(axis="y", alpha=0.22, linewidth=0.7)
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)


def save_single(fig, output_dir, filename):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.155, top=0.88)
    path = output_dir / filename
    fig.savefig(path, dpi=600, pad_inches=0.02)
    plt.close(fig)
    print(f"[OK] {path}")


def save_panel(fig, output_dir, filename):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.subplots_adjust(
        left=0.075,
        right=0.99,
        bottom=0.16,
        top=0.82,
        wspace=0.14,
    )
    path = output_dir / filename
    fig.savefig(path, dpi=600, pad_inches=0.02)
    plt.close(fig)
    print(f"[OK] {path}")


def ordered_comp(comp, pdb_ms):
    sub = comp[np.isclose(comp["pdb_ms"], pdb_ms)].copy()
    sub["mode_label"] = pd.Categorical(
        sub["mode_label"], MODE_ORDER, ordered=True
    )
    return sub.sort_values("mode_label")


def plot_composition_single(comp, pdb_ms, lang, filename, output_dir):
    sub = ordered_comp(comp, pdb_ms)

    if lang == "pt":
        xlabel = "Escalonador"
        ylabel = "Unidades sintéticas de vídeo (%)"
        labels = ["No prazo", "Tardias", "Não recebidas"]
    else:
        xlabel = "Scheduler"
        ylabel = "Synthetic video units (%)"
        labels = ["On time", "Late", "Not received"]

    x = np.arange(len(sub))
    y1 = sub["no_prazo_pct"].to_numpy(float)
    y2 = sub["tardias_pct"].to_numpy(float)
    y3 = sub["nao_recebidas_pct"].to_numpy(float)

    fig, ax = plt.subplots(figsize=(8.2, 4.4))

    ax.bar(
        x,
        y1,
        width=0.62,
        color=COMP_COLORS["on_time"],
        edgecolor="black",
        linewidth=0.6,
        label=labels[0],
    )
    ax.bar(
        x,
        y2,
        width=0.62,
        bottom=y1,
        color=COMP_COLORS["late"],
        edgecolor="black",
        linewidth=0.6,
        hatch="//",
        label=labels[1],
    )
    ax.bar(
        x,
        y3,
        width=0.62,
        bottom=y1 + y2,
        color=COMP_COLORS["lost"],
        edgecolor="black",
        linewidth=0.6,
        hatch="\\\\",
        label=labels[2],
    )

    ax.set_ylim(0, 100)
    ax.set_yticks(np.arange(0, 101, 20))
    ax.set_xticks(x)
    ax.set_xticklabels(sub["mode_label"].astype(str).tolist())
    ax.set_xlabel(xlabel, labelpad=5)
    ax.set_ylabel(ylabel, labelpad=6)
    style_axis(ax)

    ax.legend(
        loc="upper center",
        ncol=3,
        bbox_to_anchor=(0.5, 1.13),
        frameon=False,
        handlelength=1.7,
        columnspacing=1.8,
    )

    save_single(fig, output_dir, filename)


def plot_composition_panels(comp, lang, filename, output_dir):
    if lang == "pt":
        xlabel = "Escalonador"
        ylabel = "Unidades sintéticas de vídeo (%)"
        labels = ["No prazo", "Tardias", "Não recebidas"]
    else:
        xlabel = "Scheduler"
        ylabel = "Synthetic video units (%)"
        labels = ["On time", "Late", "Not received"]

    panel_titles = ["(a) PDB = 60 ms", "(b) PDB = 80 ms"]

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2), sharey=True)

    for ax, pdb_ms, panel_title in zip(axes, PDB_ORDER, panel_titles):
        sub = ordered_comp(comp, pdb_ms)

        x = np.arange(len(sub))
        y1 = sub["no_prazo_pct"].to_numpy(float)
        y2 = sub["tardias_pct"].to_numpy(float)
        y3 = sub["nao_recebidas_pct"].to_numpy(float)

        ax.bar(
            x,
            y1,
            width=0.62,
            color=COMP_COLORS["on_time"],
            edgecolor="black",
            linewidth=0.6,
        )
        ax.bar(
            x,
            y2,
            width=0.62,
            bottom=y1,
            color=COMP_COLORS["late"],
            edgecolor="black",
            linewidth=0.6,
            hatch="//",
        )
        ax.bar(
            x,
            y3,
            width=0.62,
            bottom=y1 + y2,
            color=COMP_COLORS["lost"],
            edgecolor="black",
            linewidth=0.6,
            hatch="\\\\",
        )

        ax.set_title(panel_title, pad=4)
        ax.set_ylim(0, 100)
        ax.set_yticks(np.arange(0, 101, 20))
        ax.set_xticks(x)
        ax.set_xticklabels(sub["mode_label"].astype(str).tolist())
        ax.set_xlabel(xlabel, labelpad=5)
        style_axis(ax)

    axes[0].set_ylabel(ylabel, labelpad=6)

    handles = [
        Patch(
            facecolor=COMP_COLORS["on_time"],
            edgecolor="black",
            linewidth=0.6,
            label=labels[0],
        ),
        Patch(
            facecolor=COMP_COLORS["late"],
            edgecolor="black",
            linewidth=0.6,
            hatch="//",
            label=labels[1],
        ),
        Patch(
            facecolor=COMP_COLORS["lost"],
            edgecolor="black",
            linewidth=0.6,
            hatch="\\\\",
            label=labels[2],
        ),
    ]

    fig.legend(
        handles=handles,
        loc="upper center",
        ncol=3,
        bbox_to_anchor=(0.5, 0.985),
        frameon=False,
        handlelength=1.7,
        columnspacing=1.8,
    )

    save_panel(fig, output_dir, filename)


def plot_grouped_metric(
    df,
    value_col,
    ci_col,
    ylabel_pt,
    ylabel_en,
    filename_base,
    output_dir,
    ylim=None,
    percent=False,
):
    require_columns(
        df,
        ["mode_label", "pdb_ms", value_col, ci_col],
        "Summary",
    )

    for lang, suffix in [("pt", ""), ("en", "_IN")]:
        xlabel = "Escalonador" if lang == "pt" else "Scheduler"
        ylabel = ylabel_pt if lang == "pt" else ylabel_en

        fig, ax = plt.subplots(figsize=(8.2, 4.4))
        x = np.arange(len(MODE_ORDER))
        width = 0.24

        for i, pdb_ms in enumerate(PDB_ORDER):
            offset = (i - 0.5) * width

            for j, mode in enumerate(MODE_ORDER):
                row = df[
                    (df["mode_label"] == mode)
                    & (np.isclose(df["pdb_ms"], pdb_ms))
                ]

                if row.empty:
                    continue

                value = float(row[value_col].iloc[0])
                ci = float(row[ci_col].iloc[0])

                if percent:
                    value *= 100.0
                    ci *= 100.0

                ax.bar(
                    x[j] + offset,
                    value,
                    width=width,
                    color=COLORS[mode],
                    edgecolor="black",
                    linewidth=0.65,
                    hatch=PDB_HATCH[pdb_ms],
                    yerr=ci,
                    capsize=3,
                    ecolor="black",
                    error_kw={
                        "elinewidth": 0.8,
                        "capthick": 0.8,
                    },
                )

        ax.set_xticks(x)
        ax.set_xticklabels(MODE_ORDER)
        ax.set_xlabel(xlabel, labelpad=5)
        ax.set_ylabel(ylabel, labelpad=6)

        if ylim is not None:
            ax.set_ylim(*ylim)

        style_axis(ax)

        handles = [
            Patch(
                facecolor="white",
                edgecolor="black",
                linewidth=0.65,
                hatch=PDB_HATCH[60.0],
                label="60 ms",
            ),
            Patch(
                facecolor="white",
                edgecolor="black",
                linewidth=0.65,
                hatch=PDB_HATCH[80.0],
                label="80 ms",
            ),
        ]

        ax.legend(
            handles=handles,
            title="PDB",
            loc="upper right",
            frameon=False,
            handlelength=1.7,
            borderaxespad=0.4,
        )

        save_single(
            fig,
            output_dir,
            f"{filename_base}{suffix}.png",
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate the public E3 XR/QoE figures from the consolidated "
            "summary and composition datasets."
        )
    )
    parser.add_argument(
        "--summary",
        required=True,
        help="Path to data/e3_xr_qoe/qoe_summary.csv",
    )
    parser.add_argument(
        "--composition",
        required=True,
        help="Path to data/e3_xr_qoe/qoe_composition.csv",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where the figures will be written.",
    )
    args = parser.parse_args()

    setup_matplotlib()

    df = load_summary(args.summary)
    derived_comp = make_composition_table(df)
    comp = load_and_validate_composition(args.composition, derived_comp)

    print(f"Summary: {args.summary}")
    print(f"Composition: {args.composition}")
    print(f"Output: {args.output_dir}")
    print("Rows:", len(df))
    print("Schedulers:", ", ".join(MODE_ORDER))
    print("PDBs:", "60 ms, 80 ms")
    print("Seeds: 100")
    print("[OK] Composition CSV matches values derived from summary.")

    plot_composition_single(
        comp,
        60.0,
        "pt",
        "fig_qoe_01_composicao_60ms.png",
        args.output_dir,
    )
    plot_composition_single(
        comp,
        80.0,
        "pt",
        "fig_qoe_01_composicao_80ms.png",
        args.output_dir,
    )
    plot_composition_single(
        comp,
        60.0,
        "en",
        "fig_qoe_01_composicao_60ms_IN.png",
        args.output_dir,
    )
    plot_composition_single(
        comp,
        80.0,
        "en",
        "fig_qoe_01_composicao_80ms_IN.png",
        args.output_dir,
    )

    plot_composition_panels(
        comp,
        "pt",
        "fig_qoe_01_composicao_60_80ms_paineis.png",
        args.output_dir,
    )
    plot_composition_panels(
        comp,
        "en",
        "fig_qoe_01_composicao_60_80ms_paineis_IN.png",
        args.output_dir,
    )

    plot_grouped_metric(
        df=df,
        value_col="total_unavailable_time_ratio_mean_mean",
        ci_col="total_unavailable_time_ratio_mean_ci95",
        ylabel_pt="Indisponibilidade temporal inferida (%)",
        ylabel_en="Inferred temporal unavailability (%)",
        filename_base="fig_qoe_02_taxa_congelamento_inferida",
        output_dir=args.output_dir,
        ylim=(0, 100),
        percent=True,
    )

    plot_grouped_metric(
        df=df,
        value_col="freeze_events_per_min_mean_mean",
        ci_col="freeze_events_per_min_mean_ci95",
        ylabel_pt="Eventos de congelamento por minuto",
        ylabel_en="Freeze events per minute",
        filename_base="fig_qoe_03a_eventos_congelamento",
        output_dir=args.output_dir,
        percent=False,
    )

    plot_grouped_metric(
        df=df,
        value_col="p95_freeze_ms_across_ues_mean",
        ci_col="p95_freeze_ms_across_ues_ci95",
        ylabel_pt="Duração P95 dos congelamentos (ms)",
        ylabel_en="P95 freeze duration (ms)",
        filename_base="fig_qoe_03b_duracao_p95_congelamento",
        output_dir=args.output_dir,
        percent=False,
    )

    plot_grouped_metric(
        df=df,
        value_col="ues_satisfied_99_pct_mean",
        ci_col="ues_satisfied_99_pct_ci95",
        ylabel_pt="UEs temporalmente satisfeitos (%)",
        ylabel_en="Temporally satisfied UEs (%)",
        filename_base="fig_qoe_04_usuarios_temporalmente_satisfeitos",
        output_dir=args.output_dir,
        ylim=(0, 100),
        percent=False,
    )


if __name__ == "__main__":
    main()
