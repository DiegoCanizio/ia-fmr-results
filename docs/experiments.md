# Experimental Evaluations

This document describes the organization of the experimental results
distributed in the `ia-fmr-results` repository.

## E1 — Bandwidth Evaluation

E1 evaluates the behavior of the scheduling policies as the available 5G NR
bandwidth changes.

### Schedulers

- Round Robin (RR)
- Proportional Fair (PF)
- Max Rate (MR)
- In-Action Fair Max Rate (IA-FMR)

### Bandwidth Values

The evaluated bandwidths are:

```text
10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100 MHz
```

Each scheduler-bandwidth configuration is represented by 100 simulation
seeds.

The principal consolidated result table is:

```text
data/e1_bandwidth/summary_by_bw.csv
```

Additional IA-FMR target-versus-applied allocation analyses are available in:

```text
data/e1_bandwidth/target_vs_applied_summary.csv
data/e1_bandwidth/target_vs_applied_per_seed.csv
```

### Main Metric Families

The E1 consolidated table includes statistics for, among others:

- aggregate throughput;
- per-flow throughput, including P5;
- packet delay;
- packet loss;
- served and active UEs per slot;
- Jain fairness indices;
- pending demand without allocation;
- buffer demand; and
- allocated RBGs.

Where available, the table preserves standard deviation and 95% and 99%
confidence-interval half-widths in addition to means.

## E1 — Temporal Analysis at 40 MHz

A representative run using seed `47889` is preserved for detailed temporal
inspection.

The analysis contains temporal information for:

- backlog;
- number of served UEs;
- effective number of UEs receiving RBGs;
- allocation share assigned to the dominant UE;
- per-UE RBG allocation share; and
- IA-FMR alpha.

The temporal CSV files are stored under:

```text
data/e1_bandwidth/temporal_40mhz/
```

The representative-run tables use 300 temporal bins for each scheduler.

The per-UE RBG-allocation table represents:

```text
4 schedulers × 300 temporal bins × 9 UEs
```

The IA-FMR alpha trajectory is also provided as an aggregate over all
100 seeds.

## E2 — Scalability

E2 evaluates IA-FMR while varying the number of active UEs.

### Number of UEs

```text
3, 5, 7, 9
```

### Configuration

- Scheduler: IA-FMR
- Bandwidth: 40 MHz
- Simulation repetitions: 100 seeds per UE count

The consolidated result table is:

```text
data/e2_scalability/summary_by_ues.csv
```

The table contains statistics for aggregate throughput, Jain fairness over RBG
allocation, served UEs per slot, per-flow throughput P5, packet loss, packet
delay, and pending demand without allocation.

## E3 — XR/QoE Evaluation

E3 evaluates the schedulers using XR-oriented quality-of-experience metrics.

### Schedulers

- RR
- PF
- MR
- IA-FMR

### Packet Delay Budgets

```text
60 ms
80 ms
```

Each scheduler-PDB combination contains results from 100 simulation seeds.

The principal datasets are:

```text
data/e3_xr_qoe/qoe_summary.csv
data/e3_xr_qoe/qoe_composition.csv
```

The QoE summary includes metric families related to:

- frame success ratio;
- useful throughput;
- Jain fairness;
- received, late, and lost frame ratios;
- playback start;
- freeze-event frequency;
- temporal unavailability;
- freeze duration; and
- UE satisfaction thresholds.

The composition table separates synthetic video units into:

- on time;
- late; and
- not received.

The public E3 plotting script validates the composition table against the
corresponding values derived from the consolidated QoE summary before
generating the figures.

## Confidence Intervals

The public plotting scripts consume the statistics already stored in the
consolidated datasets.

They do not recompute simulation-level confidence intervals from the original
raw ns-3 logs.

## Scope of This Repository

This repository supports reproducibility from the consolidated result layer:

```text
consolidated datasets
        ↓
portable plotting scripts
        ↓
public figures
```

The complete raw simulation logs and private training workspace are outside
the scope of this results artifact.
