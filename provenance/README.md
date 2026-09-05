# Provenance

This directory contains information used to establish the provenance and
integrity of the public IA-FMR result datasets.

## Seed set

`seeds_100_master_20260618.txt` contains the master set of 100 simulation
seeds used by the experimental campaigns represented in this repository.

## SHA-256 manifests

The principal public datasets are covered by:

```text
e1_summary_by_bw_SHA256SUMS
e1_temporal_40mhz_SHA256SUMS
e2_summary_by_ues_SHA256SUMS
e3_qoe_SHA256SUMS
```

From the repository root, verify them with:

```bash
for manifest in provenance/*SHA256SUMS; do
    sha256sum -c "$manifest"
done
```

## Validation

The `validation/` directory contains selected audit outputs associated with
the construction and verification of the final consolidated datasets.

These files document consistency checks and metric corrections, but are not
required to regenerate the public figures.

## Scope

The provenance material in this repository documents the consolidated public
artifact. It does not attempt to reproduce every intermediate server-side
processing directory or every exploratory analysis used during development.
