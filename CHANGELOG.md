# Changelog

## [2.0.2-ejie-r2] - 2026-11-16

Release `v2.0.2-ejie-r2`. **Supersedes `v2.0.1-ejie-r2`** (and `v2.0-ejie-r2`); both older tags are unchanged. No simulation code, configuration, result values or data files changed.

- Commit references to 2846f9a, a local commit that is not on `main`, were replaced by a2e7d35 (the commit of release `v2.0-ejie-r2`) in `results/WP0/change_ladder_ofat.csv` and `scripts/run_ofat_ladder.py`. The `src/` directory (and `config/parameters.yaml`, apart from line endings) at 2846f9a is identical to a2e7d35 (`git diff 2846f9a a2e7d35 -- src` is empty). The `commit_hash` column in `results/WP7/*_pinned_core.csv` still reads 2846f9a because those are result files and were not modified.
- Supplementary Material: confidence-interval methods are now stated per table (cluster t intervals with df = 29, df = 14 for held-out replications 15-29, and Shapley timing share), and Table S8 is shown in full in the PDF.
- Added `scripts/regenerate_supplement_tables.py`, which regenerates Tables S3, S4, S5 and S6 files (WP4, WP5, WP6, WP8, WP9) from the repository data and checks them against the committed files; README section "Known gaps" lists files without a complete generating script.

## [2.0.1-ejie-r2] - 2026-11-16

Release `v2.0.1-ejie-r2`. **Supersedes `v2.0-ejie-r2`** (the tag cited in the revision-2 submission; that tag is unchanged). No simulation code, configuration, result values or data files changed.

- Table B1 (`results/WP0/provenance_table_B1.csv`): corrected the original-submission values of urgency beta (1 at 50bdad2, 2 at 50c4298), simulation length (3,600 s at 50bdad2, 28,800 s at 50c4298) and the `config/parameters.yaml` line numbers cited in columns (b) and (d). Classifications are unchanged.
- The change ladder (`results/WP0/change_ladder_ofat.csv`) and Table B1 scripts cite commit 2846f9a, a local commit that is not on `main`; its model code (`src/`) is identical to the code of the tagged release.
- Added `supplement/Supplementary_Material.pdf` (source `.md`, built by `scripts/build_supplementary.py`) with Tables S1-S8 and Figures S1-S5; README and `docs/SUPPLEMENTARY_MATERIAL.md` map every item to its file.
- Renamed `docs/revised-paper-assets/Table_S01_Flow_and_Tour_Efficiency.csv` to `Table_04c_Flow_and_Tour_Efficiency.csv` (it is Table 4c).
- Added generators for WP4 Panel B, WP5 Figure 11 and Supplementary Figure S5 to `scripts/generate_revised_figures.py`.
- Removed internal working files (response-letter drafts, agent prompts, TODO notes, placeholder and Mendeley helper scripts) from tracking and added them to `.gitignore`; they remain in the git history of earlier commits.
- README: Mendeley Data versions, reproduction instructions, supplementary mapping and citation information updated; `CITATION.cff` updated.

## [2.0-ejie-r2] - 2026-10-27

Release `v2.0-ejie-r2`: replication artifact for revision 2 of manuscript EJIE-337519.

- Full-factorial results (207,360 runs; 6,912 scenarios × 30 replications) stored as `data/results_full_factorial.csv.gz`, with a SHA-256 ledger in `data/CHECKSUMS.txt`.
- Revision-2 analyses under `results/WP0`–`results/WP9` (parameter provenance Table B1 and change ladder, Table 4 variants, timing-versus-composition effects, FTWB/VTWB tuning, setup-time and warm-up sensitivity, decision-kernel latency, late-order decomposition), with reports in `reports/` and scripts in `scripts/`.
- Appendix A pseudocode with fallback-path tests (`docs/Appendix_A_pseudocode.md`).
- Superseded intermediate result files archived in `results/superseded/`.
- Unit tests: 80 passed (see README for how to run them), plus a 120-run bitwise smoke test.
- Mendeley Data versions 1 and 2 (DOI 10.17632/49r2pmymrm) are superseded by this release.

## [Unreleased]

- Added deterministic checkpoint/resume validation, source-tree and dependency-lock provenance.
- Strengthened final-result audit for schema, identity, finite ranges, invariants, and manifest consistency.
- Added executable held-out validation, OAT/global sensitivity, ablation, benchmark, and Q1 journal-fit artifacts.
- Added leakage-resistant operational input fitting and formal WMS/SME validation templates.
- Added near-zero, overload, staffing, and due-regime extreme-condition tests.
- Added repeated CPU/RSS/disk benchmark evidence with Student-t intervals and atomic artifacts.

- Rebuild the experiment runner around deterministic seeds and auditable manifests.
- Correct method/configuration mismatches and late-order accounting.
- Add scientific verification, validation, reporting, and artifact workflows.

## [0.1.0] - 2026-08-12

- Establish the first publication-quality baseline.
