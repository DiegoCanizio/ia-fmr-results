# IA-FMR Results

Reproducible consolidated results, analysis scripts, and figures for the
**In-Action Fair Max Rate (IA-FMR)** scheduler.

IA-FMR is a reinforcement-learning-based resource scheduling approach for
5G NR in which the fairness-throughput trade-off coefficient is produced as
part of the agent action together with the values used for radio-resource
allocation.

This repository contains the consolidated experimental results used in the
evaluation of IA-FMR, together with portable Python scripts that regenerate
the public figures without requiring the original ns-3 simulation logs.

## Repository scope

The repository covers three main experimental evaluations and one detailed
temporal analysis.

### E1 — Bandwidth evaluation

- Bandwidths: 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, and 100 MHz
- Schedulers: RR, PF, MR, and IA-FMR
- 100 simulation seeds per configuration

### E1 — Temporal analysis at 40 MHz

- Detailed temporal analysis for representative seed `47889`
- Schedulers: RR, PF, MR, and IA-FMR
- IA-FMR alpha trajectory also aggregated over 100 seeds

### E2 — Scalability

- IA-FMR evaluated with 3, 5, 7, and 9 UEs
- Bandwidth: 40 MHz
- 100 simulation seeds per configuration

### E3 — XR/QoE evaluation

- Schedulers: RR, PF, MR, and IA-FMR
- Packet Delay Budgets (PDB): 60 ms and 80 ms
- 100 simulation seeds per configuration

## Repository structure

    ia-fmr-results/
    ├── data/
    │   ├── derived/
    │   ├── e1_bandwidth/
    │   │   └── temporal_40mhz/
    │   ├── e2_scalability/
    │   └── e3_xr_qoe/
    ├── docs/
    ├── figures/
    │   ├── generated/
    │   └── thesis/
    ├── provenance/
    │   └── validation/
    ├── scripts/
    │   ├── generate_all.py
    │   ├── plot_e1_bandwidth.py
    │   ├── plot_e1_temporal.py
    │   ├── plot_e2_scalability.py
    │   └── plot_e3_qoe.py
    ├── requirements.txt
    └── README.md

## Reproducing the figures

The public figures can be regenerated directly from the consolidated CSV
files contained in this repository.

Create a Python virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Then regenerate all public figures:

    python3 scripts/generate_all.py

A successful run ends with:

    ALL PUBLIC FIGURE PIPELINES PASSED — 60 files generated

The regenerated figures are written to:

    figures/generated/

The individual plotting scripts can also be executed separately. See
`docs/reproducibility.md` for the corresponding commands.

## Generated and thesis figures

Two sets of figures are preserved:

- `figures/generated/` contains figures produced by the portable public
  scripts from the consolidated datasets in `data/`.
- `figures/thesis/` contains the final figure files used in the thesis.

The public plotting scripts were reorganized to remove dependencies on the
original simulation directory structure. The generated figures reproduce the
same datasets, metrics, and scientific interpretation, but they are not
required to be byte-for-byte identical to the archived thesis figures.

## Data organization

### E1 bandwidth evaluation

Principal consolidated dataset:

    data/e1_bandwidth/summary_by_bw.csv

Additional IA-FMR target-versus-applied allocation analyses:

    data/e1_bandwidth/target_vs_applied_summary.csv
    data/e1_bandwidth/target_vs_applied_per_seed.csv

Temporal datasets for the 40 MHz analysis:

    data/e1_bandwidth/temporal_40mhz/

### E2 scalability

Principal consolidated dataset:

    data/e2_scalability/summary_by_ues.csv

### E3 XR/QoE

Principal consolidated datasets:

    data/e3_xr_qoe/qoe_summary.csv
    data/e3_xr_qoe/qoe_composition.csv

### Derived results

Additional consolidated tables derived from the experimental results are
stored under:

    data/derived/

## Data provenance

The datasets in this repository are consolidated outputs derived from the
original ns-3/5G-LENA simulation campaigns.

The full raw slot-level simulation logs are intentionally not included. They
are substantially larger and are not required to regenerate the public
figures distributed here.

SHA-256 manifests for the principal datasets are available under:

    provenance/

The master list of the 100 simulation seeds is also preserved in that
directory.

Selected consistency checks and metric-validation artifacts are available
under:

    provenance/validation/

Further details are documented in:

- `provenance/README.md`
- `provenance/data_provenance.md`
- `docs/experiments.md`
- `docs/reproducibility.md`

## What is not included

This repository does not contain:

- the private IA-FMR training workspace;
- raw training runs;
- the complete raw ns-3 slot logs;
- intermediate experimental directories;
- deprecated or exploratory plotting scripts;
- unresolved training-run-to-bandwidth provenance information.

The ns-3/5G-LENA IA-FMR implementation and the frozen inference models are
intended to be released separately as a simulator artifact.

## Tested environment

The public scripts were tested with:

- Python 3.10.12
- NumPy 2.2.6
- pandas 2.3.3
- Matplotlib 3.10.9

The exact Python package versions used for validation are listed in
`requirements.txt`.

## Integrity verification

From the repository root, verify the SHA-256 manifests with:

    for manifest in provenance/*SHA256SUMS; do
        sha256sum -c "$manifest"
    done

All referenced files should report `OK`.

## License

This repository uses scoped licensing:

- Python code under `scripts/` is licensed under the MIT License
  (`LICENSE-CODE`).
- Datasets, figures, documentation, provenance material, and this README are
  licensed under the Creative Commons Attribution 4.0 International license
  (CC BY 4.0; `LICENSE-DATA`).

See `LICENSE` for the licensing overview.

## Author

Diego Canizio Lopes
