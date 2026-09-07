# Computer Networks article revision artifact

This directory preserves the data tables, plotting script, generated figures,
and validation material used in the revised version of the IA-FMR article
prepared for Computer Networks.

## Structure

- `source_data/`: consolidated input tables required by the plotting script.
- `scripts/`: portable script used to regenerate the revised figures and tables.
- `figures/`: individual PDF and PNG graphics used in the article.
- `tables/`: processed tables and figure-level numerical outputs.
- `validation/`: consistency checks and validation reports produced during figure generation.
- `obsolete_composite_figures/`: superseded composite figures retained for provenance.

## Reproduction

From this directory, run:

```bash
python3 scripts/make_computer_networks_revision.py

The script uses only the files under source_data/ and writes its outputs
inside this artifact directory. It does not depend on server-specific absolute
paths or on the original ns-3 simulation workspace.

The underlying final raw simulation outputs are preserved separately as release
assets of the ia-fmr-results repository.

Notes

The obsolete_composite_figures/ directory contains earlier composite layouts
that were replaced by individual subfigures in the revised manuscript. These
files are retained only for provenance and are not part of the final article
figure set.
