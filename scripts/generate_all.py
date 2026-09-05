#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Regenerate all public IA-FMR result figures from the consolidated datasets.

This script uses only files inside the ia-fmr-results repository:
  data/
  scripts/

Outputs are written to:
  figures/generated/
"""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCRIPTS = ROOT / "scripts"
FIGURES = ROOT / "figures" / "generated"


JOBS = [
    {
        "name": "E1 bandwidth",
        "script": SCRIPTS / "plot_e1_bandwidth.py",
        "args": [
            "--summary",
            DATA / "e1_bandwidth" / "summary_by_bw.csv",
            "--output-dir",
            FIGURES / "e1_bandwidth",
        ],
        "expected_files": 14,
    },
    {
        "name": "E1 temporal 40 MHz",
        "script": SCRIPTS / "plot_e1_temporal.py",
        "args": [
            "--data-dir",
            DATA / "e1_bandwidth" / "temporal_40mhz",
            "--output-dir",
            FIGURES / "e1_temporal_40mhz",
        ],
        "expected_files": 20,
    },
    {
        "name": "E2 scalability",
        "script": SCRIPTS / "plot_e2_scalability.py",
        "args": [
            "--summary",
            DATA / "e2_scalability" / "summary_by_ues.csv",
            "--output-dir",
            FIGURES / "e2_scalability",
        ],
        "expected_files": 12,
    },
    {
        "name": "E3 XR/QoE",
        "script": SCRIPTS / "plot_e3_qoe.py",
        "args": [
            "--summary",
            DATA / "e3_xr_qoe" / "qoe_summary.csv",
            "--composition",
            DATA / "e3_xr_qoe" / "qoe_composition.csv",
            "--output-dir",
            FIGURES / "e3_xr_qoe",
        ],
        "expected_files": 14,
    },
]


def count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for p in path.iterdir() if p.is_file())


def main():
    print(f"Repository root: {ROOT}")
    print(f"Python: {sys.executable}")
    print()

    for job in JOBS:
        script = job["script"]

        if not script.is_file():
            raise SystemExit(f"Missing script: {script}")

        args = [str(x) for x in job["args"]]
        output_dir = Path(args[args.index("--output-dir") + 1])
        output_dir.mkdir(parents=True, exist_ok=True)

        print("=" * 72)
        print(job["name"])
        print("=" * 72)

        cmd = [sys.executable, str(script), *args]
        subprocess.run(cmd, check=True)

        n_files = count_files(output_dir)
        expected = job["expected_files"]

        if n_files != expected:
            raise SystemExit(
                f"{job['name']}: expected {expected} files in "
                f"{output_dir}, found {n_files}."
            )

        print(
            f"[OK] {job['name']}: {n_files} files generated in {output_dir}"
        )
        print()

    total = sum(
        count_files(
            Path(
                [str(x) for x in job["args"]][
                    [str(x) for x in job["args"]].index("--output-dir") + 1
                ]
            )
        )
        for job in JOBS
    )

    print("=" * 72)
    print(f"ALL PUBLIC FIGURE PIPELINES PASSED — {total} files generated")
    print("=" * 72)


if __name__ == "__main__":
    main()
