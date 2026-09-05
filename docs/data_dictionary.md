# Data Dictionary

This document describes the public CSV datasets distributed with the
`ia-fmr-results` repository.

The dictionary reflects the final consolidated file structure. Where a metric
appears with statistical suffixes, the suffix conventions below apply.

## Statistical suffix conventions

The consolidated summary tables use the following suffixes:

- `_mean`: arithmetic mean across the simulation repetitions represented by
  the row.
- `_std`: standard deviation across the simulation repetitions.
- `_ci95`: half-width of the 95% confidence interval associated with the
  corresponding mean.
- `_ci99`: half-width of the 99% confidence interval associated with the
  corresponding mean.

Some field names contain an inner `_mean` because the underlying
per-simulation metric is itself a mean. For example,
`mean_delay_ms_mean` is the across-repetition mean of the per-simulation mean
packet delay.

## Common identifiers

- `scenario`: scenario identifier produced by the experimental pipeline.
- `mode`: scheduler identifier as stored in the consolidated data.
- `mode_label`: publication-facing scheduler label.
- `bandwidth_mhz`: configured channel bandwidth in MHz.
- `seed`: simulation seed.
- `n_seeds`: number of distinct seeds represented.
- `n_repetitions`: number of simulation repetitions represented.
- `n_samples`: number of samples used by the corresponding aggregation.

---

# `data/derived/bandwidth_synthesis.csv`

A compact, publication-oriented synthesis of the bandwidth experiment.

**Shape:** 4 rows × 5 columns.

| Column | Type | Description |
|---|---|---|
| `Escalonador` | object | Scheduler label. |
| `Vazão agregada (Mbps)` | float64 | Aggregate throughput summary in Mbps. |
| `Índice de Jain dos RBGs` | float64 | Jain fairness index for RBG allocation. |
| `P5 por fluxo (Mbps)` | float64 | Per-flow throughput 5th percentile in Mbps. |
| `N bandas` | int64 | Number of bandwidth configurations represented. |

---

# `data/e1_bandwidth/summary_by_bw.csv`

Main consolidated table for **E1 — Bandwidth evaluation**.

**Shape:** 48 rows × 140 columns.

Each row corresponds to one scheduler-bandwidth combination. The table
contains four schedulers across twelve bandwidth values.

## Identifier and bookkeeping fields

| Column | Type | Description |
|---|---|---|
| `scenario` | object | Scenario identifier. |
| `bandwidth_mhz` | int64 | Configured bandwidth in MHz. |
| `mode` | object | Scheduler identifier used in the public table. |
| `n_repetitions` | float64 | Number of repetitions represented by the row. |
| `bandwidth` | object | Bandwidth label retained from the consolidation pipeline. |
| `n_samples` | float64 | Number of samples represented in the auxiliary aggregation. |
| `n_seeds` | float64 | Number of simulation seeds represented. |
| `mode_original` | object | Scheduler identifier retained from the original source table. |

## Metric families

For the following metric stems, the table stores the across-repetition
statistics shown in the suffix column.

| Metric stem | Available suffixes | Description / unit |
|---|---|---|
| `bandwidth_mhz` | `_mean`, `_std`, `_ci95`, `_ci99` | Bandwidth in MHz. |
| `n_flows` | `_mean`, `_std`, `_ci95`, `_ci99` | Number of flows. |
| `aggregate_throughput_mbps` | `_mean`, `_std`, `_ci95`, `_ci99` | Aggregate throughput, Mbps. |
| `mean_flow_throughput_mbps` | `_mean`, `_std`, `_ci95`, `_ci99` | Mean per-flow throughput, Mbps. |
| `p5_flow_throughput_mbps` | `_mean`, `_std`, `_ci95`, `_ci99` | 5th percentile of per-flow throughput, Mbps. |
| `min_flow_throughput_mbps` | `_mean`, `_std`, `_ci95`, `_ci99` | Minimum per-flow throughput, Mbps. |
| `max_flow_throughput_mbps` | `_mean`, `_std`, `_ci95`, `_ci99` | Maximum per-flow throughput, Mbps. |
| `std_flow_throughput_mbps` | `_mean`, `_std`, `_ci95`, `_ci99` | Standard deviation of per-flow throughput, Mbps. |
| `jain_flow_throughput` | `_mean`, `_std`, `_ci95`, `_ci99` | Jain index computed over flow throughput. |
| `offered_mbps` | `_mean`, `_std`, `_ci95`, `_ci99` | Offered traffic rate, Mbps. |
| `throughput_over_offered` | `_mean`, `_std`, `_ci95`, `_ci99` | Ratio between achieved and offered throughput. |
| `mean_delay_ms` | `_mean`, `_std`, `_ci95`, `_ci99` | Mean packet delay, ms. |
| `p95_delay_ms` | `_mean`, `_std`, `_ci95`, `_ci99` | 95th percentile of packet delay, ms. |
| `max_delay_ms` | `_mean`, `_std`, `_ci95`, `_ci99` | Maximum packet delay, ms. |
| `mean_jitter_ms` | `_mean`, `_std`, `_ci95`, `_ci99` | Mean packet jitter, ms. |
| `mean_loss_ratio` | `_mean`, `_std`, `_ci95`, `_ci99` | Mean packet-loss ratio. |
| `max_loss_ratio` | `_mean`, `_std`, `_ci95`, `_ci99` | Maximum packet-loss ratio. |
| `tx_packets_total` | `_mean`, `_std`, `_ci95`, `_ci99` | Total transmitted packets. |
| `rx_packets_total` | `_mean`, `_std`, `_ci95`, `_ci99` | Total received packets. |
| `packet_delivery_ratio` | `_mean`, `_std`, `_ci95`, `_ci99` | Packet delivery ratio. |
| `slot_count` | `_mean`, `_std`, `_ci95`, `_ci99` | Number of slots represented. |
| `mean_active_ues_per_slot` | `_mean`, `_std`, `_ci95`, `_ci99` | Mean number of active UEs per slot. |
| `mean_served_ues_per_slot` | `_mean`, `_std`, `_ci95`, `_ci99` | Mean number of served UEs per slot. |
| `pct_buf_gt0_alloc_eq0` | `_mean`, `_std`, `_ci95`, `_ci99` | Percentage associated with pending demand (`buf > 0`) and zero RBG allocation. |
| `jain_rbg_slot_mean` | `_mean`, `_std`, `_ci95`, `_ci99` | Mean slot-level Jain index over RBG allocation. |
| `jain_buf_req_slot_mean` | `_mean`, `_std`, `_ci95`, `_ci99` | Mean slot-level Jain index over buffer demand. |
| `sum_buf_req_mean_per_slot` | `_mean`, `_std`, `_ci95`, `_ci99` | Mean per-slot sum of buffer demand. |
| `sum_buf_req_max_per_slot` | `_mean`, `_std`, `_ci95`, `_ci99` | Maximum per-slot sum of buffer demand. |
| `sum_alloc_rbg_mean_per_slot` | `_mean`, `_std`, `_ci95`, `_ci99` | Mean per-slot sum of allocated RBGs. |
| `sum_alloc_rbg_max_per_slot` | `_mean`, `_std`, `_ci95`, `_ci99` | Maximum per-slot sum of allocated RBGs. |

## Additional allocation/demand aggregation fields

These fields are retained from the final corrected E1 consolidation:

| Column | Type | Description |
|---|---|---|
| `mean_zero_ue_percent_mean` | float64 | Mean zero-allocation UE percentage. |
| `mean_zero_ue_percent_std` | float64 | Standard deviation of the zero-allocation UE percentage. |
| `mean_zero_ue_percent_ci95` | float64 | 95% CI half-width for the zero-allocation UE percentage. |
| `mean_backlogged_ues_per_slot_mean` | float64 | Mean number of backlogged UEs per slot. |
| `mean_backlogged_ues_per_slot_std` | float64 | Standard deviation of the mean backlogged-UE count. |
| `mean_backlogged_ues_per_slot_ci95` | float64 | 95% CI half-width for the mean backlogged-UE count. |
| `mean_jain_buf_req_per_slot_mean` | float64 | Mean Jain index over per-slot buffer demand. |
| `mean_jain_buf_req_per_slot_std` | float64 | Standard deviation of that metric. |
| `mean_jain_buf_req_per_slot_ci95` | float64 | 95% CI half-width for that metric. |
| `mean_jain_alloc_per_slot_mean` | float64 | Mean Jain index over per-slot allocation. |
| `mean_jain_alloc_per_slot_std` | float64 | Standard deviation of that metric. |
| `mean_jain_alloc_per_slot_ci95` | float64 | 95% CI half-width for that metric. |

---

# `data/e1_bandwidth/target_vs_applied_per_seed.csv`

Per-seed comparison between the IA-FMR requested/target allocation and the
allocation effectively applied by the simulation pipeline.

**Shape:** 1200 rows × 10 columns.

| Column | Type | Description |
|---|---|---|
| `bandwidth_mhz` | int64 | Bandwidth in MHz. |
| `seed` | int64 | Simulation seed. |
| `identical_pct` | float64 | Percentage of decisions for which target and applied allocations are identical. |
| `same_ue_set_pct` | float64 | Percentage of decisions preserving the same positively allocated UE set. |
| `divergence_norm` | float64 | Normalized divergence between target and applied allocation vectors. |
| `ues_target_positive` | float64 | Number of UEs with positive target allocation. |
| `ues_applied_positive` | float64 | Number of UEs with positive applied allocation. |
| `jain_target` | float64 | Jain index for the target allocation. |
| `jain_applied` | float64 | Jain index for the applied allocation. |
| `n_decisions` | int64 | Number of scheduling decisions represented. |

---

# `data/e1_bandwidth/target_vs_applied_summary.csv`

Across-seed summary of the target-versus-applied analysis.

**Shape:** 12 rows × 9 columns.

| Column | Type | Description |
|---|---|---|
| `bandwidth_mhz` | int64 | Bandwidth in MHz. |
| `identical_pct` | float64 | Across-seed summary of identical target/applied decisions. |
| `same_ue_set_pct` | float64 | Across-seed summary of same-UE-set decisions. |
| `divergence_norm` | float64 | Across-seed normalized target/applied divergence. |
| `ues_target_positive` | float64 | Summary number of UEs with positive target allocation. |
| `ues_applied_positive` | float64 | Summary number of UEs with positive applied allocation. |
| `jain_target` | float64 | Summary Jain index for target allocation. |
| `jain_applied` | float64 | Summary Jain index for applied allocation. |
| `seeds` | int64 | Number of seeds represented. |

---

# E1 temporal data at 40 MHz

The temporal files use 300 time bins. Files for seed `47889` preserve the
representative-run analysis. `alpha_all_seeds.csv` aggregates IA-FMR alpha
over 100 seeds.

## `data/e1_bandwidth/temporal_40mhz/alpha_all_seeds.csv`

**Shape:** 300 rows × 6 columns.

| Column | Type | Description |
|---|---|---|
| `time_s` | float64 | Time-bin coordinate in seconds. |
| `alpha_mean` | float64 | Mean IA-FMR alpha across seeds. |
| `alpha_ci95` | float64 | 95% CI half-width for mean alpha. |
| `n_seeds` | int64 | Number of seeds represented. |
| `alpha_mean_smooth` | float64 | Smoothed mean alpha trajectory. |
| `alpha_ci95_smooth` | float64 | Smoothed 95% CI half-width. |

## `data/e1_bandwidth/temporal_40mhz/alpha_seed_47889.csv`

**Shape:** 300 rows × 3 columns.

| Column | Type | Description |
|---|---|---|
| `time_bin_s` | float64 | Time-bin coordinate in seconds. |
| `alpha` | float64 | IA-FMR alpha for seed `47889`. |
| `alpha_smooth` | float64 | Smoothed alpha trajectory. |

## `data/e1_bandwidth/temporal_40mhz/backlog_seed_47889.csv`

**Shape:** 1200 rows × 4 columns.

| Column | Type | Description |
|---|---|---|
| `mode` | object | Scheduler. |
| `time_bin_s` | float64 | Time-bin coordinate in seconds. |
| `backlog_mbit` | float64 | Backlog in Mbit. |
| `backlog_mbit_smooth` | float64 | Smoothed backlog trajectory. |

## `data/e1_bandwidth/temporal_40mhz/concentration_seed_47889.csv`

**Shape:** 1200 rows × 6 columns.

| Column | Type | Description |
|---|---|---|
| `mode` | object | Scheduler. |
| `time_bin_s` | float64 | Time-bin coordinate in seconds. |
| `effective_ues` | float64 | Effective number of UEs implied by the allocation distribution. |
| `top1_share_pct` | float64 | Allocation share of the dominant UE, in percent. |
| `effective_ues_smooth` | float64 | Smoothed effective-UE trajectory. |
| `top1_share_pct_smooth` | float64 | Smoothed dominant-UE share trajectory. |

## `data/e1_bandwidth/temporal_40mhz/rbg_share_seed_47889.csv`

**Shape:** 10800 rows × 7 columns.

| Column | Type | Description |
|---|---|---|
| `mode` | object | Scheduler. |
| `time_bin_s` | float64 | Time-bin coordinate in seconds. |
| `ue` | int64 | UE index used in the temporal analysis. |
| `alloc_rbg` | int64 | Number of allocated RBGs represented in the time bin. |
| `total_alloc_rbg` | int64 | Total allocated RBGs represented in the same time bin. |
| `share_pct` | float64 | UE share of RBG allocation, in percent. |
| `share_pct_smooth` | float64 | Smoothed allocation-share trajectory. |

## `data/e1_bandwidth/temporal_40mhz/served_ues_seed_47889.csv`

**Shape:** 1200 rows × 4 columns.

| Column | Type | Description |
|---|---|---|
| `mode` | object | Scheduler. |
| `time_bin_s` | float64 | Time-bin coordinate in seconds. |
| `served_ues` | float64 | Number of served UEs. |
| `served_ues_smooth` | float64 | Smoothed served-UE trajectory. |

---

# `data/e2_scalability/summary_by_ues.csv`

Main consolidated table for **E2 — Scalability**.

**Shape:** 4 rows × 17 columns.

| Column | Type | Description |
|---|---|---|
| `n_ues` | int64 | Number of UEs. |
| `mode` | object | Scheduler label. |
| `n_repetitions` | int64 | Number of repetitions represented. |
| `aggregate_throughput_mbps_mean` | float64 | Mean aggregate throughput, Mbps. |
| `aggregate_throughput_mbps_ci95` | float64 | 95% CI half-width for aggregate throughput. |
| `jain_rbg_slot_mean_mean` | float64 | Mean slot-level Jain index over RBG allocation. |
| `jain_rbg_slot_mean_ci95` | float64 | 95% CI half-width for the Jain RBG metric. |
| `mean_served_ues_per_slot_mean` | float64 | Mean number of served UEs per slot. |
| `mean_served_ues_per_slot_ci95` | float64 | 95% CI half-width for served UEs per slot. |
| `p5_flow_throughput_mbps_mean` | float64 | Mean per-flow throughput P5, Mbps. |
| `p5_flow_throughput_mbps_ci95` | float64 | 95% CI half-width for per-flow throughput P5. |
| `mean_loss_ratio_mean` | float64 | Mean loss ratio. |
| `mean_loss_ratio_ci95` | float64 | 95% CI half-width for loss ratio. |
| `mean_delay_ms_mean` | float64 | Mean packet delay, ms. |
| `mean_delay_ms_ci95` | float64 | 95% CI half-width for packet delay. |
| `pct_buf_gt0_alloc_eq0_mean` | float64 | Mean percentage associated with pending demand and zero allocation. |
| `pct_buf_gt0_alloc_eq0_ci95` | float64 | 95% CI half-width for the pending-without-allocation metric. |

---

# `data/e3_xr_qoe/qoe_composition.csv`

Compact composition table used by the XR/QoE figures.

**Shape:** 8 rows × 5 columns.

| Column | Type | Description |
|---|---|---|
| `mode_label` | object | Publication-facing scheduler label. |
| `pdb_ms` | float64 | Packet Delay Budget in ms. |
| `no_prazo_pct` | float64 | Synthetic video units received on time, percent. |
| `tardias_pct` | float64 | Synthetic video units received late, percent. |
| `nao_recebidas_pct` | float64 | Synthetic video units not received, percent. |

---

# `data/e3_xr_qoe/qoe_summary.csv`

Main consolidated table for **E3 — XR/QoE**.

**Shape:** 8 rows × 75 columns.

Each row represents one scheduler-PDB configuration.

## Identifier fields

| Column | Type | Description |
|---|---|---|
| `scenario` | object | Scenario identifier. |
| `mode` | object | Scheduler identifier from the source pipeline. |
| `bandwidth_mhz` | float64 | Configured bandwidth in MHz. |
| `pdb_ms` | float64 | Packet Delay Budget in ms. |
| `n_seeds` | int64 | Number of seeds represented. |
| `mode_label` | object | Publication-facing scheduler label. |

## XR/QoE metric families

Unless otherwise noted, each metric family has `_mean`, `_std`, and `_ci95`
variants.

| Metric stem | Available suffixes | Description / unit |
|---|---|---|
| `n_ues` | `_mean`, `_std`, `_ci95` | Number of UEs represented. |
| `fsr_mean` | `_mean`, `_std`, `_ci95` | Mean frame success ratio. |
| `fsr_min` | `_mean`, `_std`, `_ci95` | Minimum frame success ratio. |
| `fsr_p5` | `_mean`, `_std`, `_ci95` | 5th percentile of frame success ratio. |
| `jain_fsr` | `_mean`, `_std`, `_ci95` | Jain index over frame success ratio. |
| `useful_throughput_aggregate_mbps` | `_mean`, `_std`, `_ci95` | Aggregate useful throughput, Mbps. |
| `useful_throughput_mean_per_ue_mbps` | `_mean`, `_std`, `_ci95` | Mean useful throughput per UE, Mbps. |
| `jain_useful_throughput` | `_mean`, `_std`, `_ci95` | Jain index over useful throughput. |
| `received_frame_ratio_mean` | `_mean`, `_std`, `_ci95` | Mean received-frame ratio. |
| `late_frame_ratio_mean` | `_mean`, `_std`, `_ci95` | Mean late-frame ratio. |
| `lost_frame_ratio_mean` | `_mean`, `_std`, `_ci95` | Mean lost-frame ratio. |
| `playback_started_pct` | `_mean`, `_std`, `_ci95` | Percentage associated with successful playback start. |
| `freeze_events_per_min_mean` | `_mean`, `_std`, `_ci95` | Mean freeze-event frequency, events/min. |
| `freeze_time_ratio_mean` | `_mean`, `_std`, `_ci95` | Mean fraction of time classified as freeze time. |
| `total_unavailable_time_ratio_mean` | `_mean`, `_std`, `_ci95` | Mean total temporal unavailability ratio. |
| `mean_freeze_ms_mean` | `_mean`, `_std`, `_ci95` | Mean freeze duration, ms. |
| `p95_freeze_ms_across_ues` | `_mean`, `_std`, `_ci95` | P95 freeze duration across UEs, ms. |
| `max_freeze_ms_across_ues` | `_mean`, `_std`, `_ci95` | Maximum freeze duration across UEs, ms. |
| `longest_failed_run_frames_max` | `_mean`, `_std`, `_ci95` | Maximum longest failed run, in frames. |
| `time_to_first_valid_frame_ms_mean` | `_mean`, `_std`, `_ci95` | Mean time to first valid frame, ms. |
| `ues_satisfied_90_pct` | `_mean`, `_std`, `_ci95` | UE satisfaction metric at the 90% threshold. |
| `ues_satisfied_95_pct` | `_mean`, `_std`, `_ci95` | UE satisfaction metric at the 95% threshold. |
| `ues_satisfied_99_pct` | `_mean`, `_std`, `_ci95` | UE satisfaction metric at the 99% threshold. |

## Notes on ratios and percentages

Columns whose names explicitly end in `_pct` are represented as percentage
values by the consolidated pipeline.

Ratio-valued fields retain their native ratio representation in the CSV.
Plotting scripts apply percentage scaling where required for publication
figures.

---

# Validation and provenance tables

Files under `provenance/validation/` are audit outputs rather than primary
analysis datasets. They document selected consistency checks and metric
corrections and are therefore described in `provenance/README.md` rather
than duplicated here.
