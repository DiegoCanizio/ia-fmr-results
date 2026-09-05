# Data Provenance

The datasets distributed in this repository were obtained from the final
experimental campaigns used to evaluate IA-FMR.

The original simulation environment produced substantially larger raw
datasets, including per-seed and slot-level ns-3 logs. For the public result
artifact, only the validated consolidated datasets required for scientific
inspection and figure reproduction are retained.

## E1 — Bandwidth evaluation

The public E1 bandwidth table represents:

```text
12 bandwidths × 4 schedulers
```

with 100 simulation seeds per scheduler-bandwidth configuration.

The temporal analysis at 40 MHz preserves both:

- representative seed `47889`; and
- the IA-FMR alpha trajectory aggregated over 100 seeds.

The target-versus-applied IA-FMR tables retain per-seed and consolidated
information about the difference between requested and effectively applied
allocations.

## E2 — Scalability

The E2 scalability dataset represents IA-FMR with:

```text
3, 5, 7, and 9 UEs
```

at 40 MHz, with 100 seeds for each configuration.

## E3 — XR/QoE

The E3 QoE summary represents:

```text
4 schedulers × 2 PDB values
```

with 100 seeds for each scheduler-PDB configuration.

The public composition table is validated by the plotting pipeline against
the corresponding values derived from the QoE summary.

## Validation artifacts

Selected audit outputs are retained under:

```text
provenance/validation/
```

They include checks associated with:

- pending demand without allocation;
- denominator consistency for the corresponding E1 metric;
- before/after validation of the corrected E1 metric; and
- E3 seed-set consistency.

## Excluded material

The public result artifact does not contain:

- raw slot-level simulation logs;
- intermediate experimental directories;
- temporary or exploratory post-processing outputs;
- the private reinforcement-learning training workspace; or
- unresolved training-run-to-bandwidth provenance information.

The final item is intentionally excluded until its provenance can be
independently verified.
