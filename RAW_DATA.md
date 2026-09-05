# IA-FMR Raw Experimental Dataset

This repository accompanies the IA-FMR thesis and journal evaluation.

The Git repository contains the consolidated datasets, analysis and plotting
scripts, figures, and provenance information. The complete selected raw
simulation outputs are distributed separately as release assets because of
their storage volume.

## Preserved experiments

### E1 — Bandwidth evaluation

100 simulation seeds are preserved for RR, PF, MR, and IA-FMR at:

10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, and 100 MHz.

The IA-FMR runs correspond to the final `alpha_full` policy.

### E2 — Scalability

100 simulation seeds are preserved for IA-FMR at 40 MHz with:

- 3 UEs
- 5 UEs
- 7 UEs

The 9-UE case reuses the E1 IA-FMR 40-MHz runs and is not duplicated.

### E3 — XR/QoE

100 simulation seeds are preserved for each final scheduler configuration:

- RR
- PF
- MR
- IA-FMR (`alpha_full`)

## Excluded material

The preservation dataset intentionally excludes development runs, invalid
runs, superseded IA-FMR policies, baseline runs at 35 and 45 MHz, derived
tables that can be regenerated from the raw outputs, diagnostic HARQ-feedback
CSV files, build products, virtual environments, caches, temporary files, and
historical models.

## Provenance

`provenance/raw_dataset/FILE_MANIFEST.tsv` records the relative pathname and
byte size of every preserved raw file.

`provenance/raw_dataset/DATASET_SELECTION.txt` documents the selection rules.

The final training logs are available under:

`provenance/training_logs/final_alpha_full/`

The raw dataset itself is intentionally excluded from normal Git history and
is distributed as compressed release assets.
