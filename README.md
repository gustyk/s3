# S3 Warehouse Simulation

Reproducible discrete-event simulation for comparing warehouse order-release,
batching, routing, cart-capacity, and picker-staffing policies. This repository is
the replication artifact for the manuscript EJIE-337519 (European Journal of
Industrial Engineering), revision 2. The reference version is the release/tag
**`v2.0.2-ejie-r2`** (see [How to cite / version](#how-to-cite--version)).

## Important data warning

The historical CSV is quarantined under `data/legacy/` and is not valid for
confirmatory analysis. Never pass it to the publication analysis pipeline. All
reported results come from the 207,360-run full-factorial dataset described
below.

## Quick start

Requires Python 3.12–3.14. The environment is pinned in
[`requirements.lock`](requirements.lock) (exact versions of all runtime,
analysis, and test dependencies; also used by CI and the `Dockerfile`).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
```

On Linux/macOS use `.venv/bin/python` instead of `.\.venv\Scripts\python.exe`.

### Unit tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Expected result: **80 passed** (the configuration in `pyproject.toml` also enforces
a minimum of 90 % line/branch coverage on the measured modules).

### Smoke test (120 runs, bitwise comparison with the stored full-factorial results)

The smoke test re-simulates 5 scenarios × 3 repetitions (1–3) × 8 policies = 120
runs and checks that total late orders, throughput, and trip count are
identical to the corresponding rows of the stored 207,360-run results. It needs
the unpacked results file (see [Quick start with factorial data](#4-quick-start-with-factorial-data))
at `outputs/final-q1-v1/full-factorial/results.csv`:

```powershell
.\.venv\Scripts\python.exe scripts/run_wp0_smoke.py
```

Expected final output lines: `Completed 120 runs.` and
`All runs bitwise identical to stored results: True` (about 5 minutes on a
single core). The script also rewrites `results/WP0/smoke_test_report.md`.

### Data Availability and Datasets

#### 1. Files Included in the Repository
The git repository contains full source code, test suites, experimental configurations, documentation, and all derived results for the revised manuscript:
- **Full-factorial results:** `data/results_full_factorial.csv.gz` contains the complete 207,360-run full-factorial simulation results (gzip -9, 35.2 MB / 35,159,984 bytes). When decompressed it is byte-identical to `outputs/final-q1-v1/full-factorial/results.csv` (142.5 MB; SHA-256 `720f2d70…b4448`, see the checksum ledger).
- **Derived statistical results and tables:** post-processed outputs under `results/`, organised by analysis work package (`WP0` provenance and change ladder; `WP1` reproduction of Table 5; `WP2`–`WP4` regimes, Table 4 variants and timing-versus-composition effects; `WP5` tuning of the FTWB/VTWB benchmarks; `WP6` setup-time and warm-up sensitivity; `WP7` computation time and surrogate validation; `WP8`–`WP9` late-order decomposition and headline checks). Earlier versions of some files are kept in `results/superseded/`. Per-work-package summaries are in `reports/`.
- **Checksum ledger:** [`data/CHECKSUMS.txt`](data/CHECKSUMS.txt) records SHA-256 hashes and sizes of the dataset artifacts, including those not stored in git.

#### 2. Files Exceeding 100 MB
No file larger than 100 MB is stored in the git history of this repository. The following files are therefore not in git: the uncompressed 207,360-run results (`results.csv`, 142.5 MB), the per-order simulation logs of the three worker processes (`worker-00/orders.csv.gz`, `worker-01/orders.csv.gz`, `worker-02/orders.csv.gz`, about 9.2–9.3 GB each), and the pooled per-order log (`orders.csv.gz`, 27.7 GB, 621,955,584 orders). Sizes are in decimal units (1 GB = 10⁹ bytes).
- **Access:** these files are available from the corresponding author on written request.
- **Verification:** the integrity of received files can be checked against the SHA-256 hashes in [`data/CHECKSUMS.txt`](data/CHECKSUMS.txt). The ledger also lists a few smaller derived files (for example the gzip results file above) for completeness; the `results.csv` hash can be re-checked after decompression.

#### 3. Mendeley Data (DOI 10.17632/49r2pmymrm)
The Mendeley Data record has two public versions. Both are superseded by the GitHub release `v2.0.2-ejie-r2`, which additionally contains all experiments added in revision 2.

| Version | DOI | Content | Status |
|---|---|---|---|
| 1 | [10.17632/49r2pmymrm.1](https://doi.org/10.17632/49r2pmymrm.1) | Results of the original submission (legacy dataset). | Does **not** support the results reported in the revised manuscript (superseded parameters; see `data/legacy/MANIFEST.md` and `results/WP0/provenance_table_B1.csv`). |
| 2 | [10.17632/49r2pmymrm.2](https://doi.org/10.17632/49r2pmymrm.2) | Main full-factorial run-level data (`level_run.csv`, SHA-256-identical to the `results.csv` above), the Table 4c archive, supplementary experiments added in revision 1, an algorithm appendix, provenance files, and an erratum. | Superseded by `v2.0.2-ejie-r2`. Per-order logs are not among the files listed for this version. |

Confirmatory analyses and audits should use `data/results_full_factorial.csv.gz` (or files verified via `data/CHECKSUMS.txt`) from the `v2.0.2-ejie-r2` release.

#### 4. Quick Start with Factorial Data
To audit or run the publication analysis pipeline directly from the repository data:

```powershell
# 1. Unpack full-factorial results
New-Item -ItemType Directory -Force -Path "outputs/final-q1-v1/full-factorial"
python -c "import gzip, shutil; shutil.copyfileobj(gzip.open('data/results_full_factorial.csv.gz', 'rb'), open('outputs/final-q1-v1/full-factorial/results.csv', 'wb'))"

# 2. Audit data integrity against manifest
.\.venv\Scripts\python.exe -m src.audit_results outputs/final-q1-v1/full-factorial/results.csv
```

Run one selected configuration/repetition:

```powershell
.\.venv\Scripts\python.exe -m src.experiment --mode selected --repetitions 1 --output-dir outputs/reviewer-smoke
.\.venv\Scripts\python.exe -m src.audit_results outputs/reviewer-smoke/results.csv
```

Run one repetition for all eight trigger methods using the selected operating
scenario:

```powershell
.\.venv\Scripts\python.exe -m src.experiment --config config/reviewer_smoke.yaml --mode smoke --output-dir outputs/all-methods-smoke
```

The full factorial experiment is intentionally explicit:

```powershell
.\.venv\Scripts\python.exe -m src.experiment --mode full --output-dir outputs/final-TAG
```

The full factorial (207,360 runs, ~27.7 GB of per-order logs) is expensive.
Benchmark a pilot on the target hardware before estimating runtime, CPU, RAM,
and disk. Trigger wake-up is event-driven; the deterministic-equivalence and
invariant tests must remain green before any parallel execution is used.

## Reproduce analysis

The analysis refuses unaudited data and refuses to overwrite an existing output
directory:

```powershell
.\.venv\Scripts\python.exe -m src.analysis_pipeline outputs/final-TAG/results.csv --output-dir outputs/final-TAG-analysis
```

It creates source-hashed summaries, paired effect estimates with confidence
intervals, Holm-adjusted tests, factorial count/service models, Pareto labels,
diagnostic figures, and an analysis manifest.

Additional publication-quality diagnostics:

```powershell
# Pilot repetition estimate (target is an example, not an approved MPID)
.\.venv\Scripts\python.exe -m src.design_tools outputs/pilot/results.csv --baseline FTWB --target-half-width 5 --output outputs/pilot/precision.json

# Epistemic input screening; ranges require domain validation
.\.venv\Scripts\python.exe -m src.sensitivity --config config/reviewer_smoke.yaml --samples 32 --output-dir outputs/sensitivity-v1

# One-at-a-time low/base/high engineering sanity check
.\.venv\Scripts\python.exe -m src.sensitivity --config config/reviewer_smoke.yaml --design oat --output-dir outputs/oat-v1

# Welch warm-up pilot
.\.venv\Scripts\python.exe -m src.welch --config config/welch_stable.yaml --pilot-duration-seconds 86400 --repetitions 10 --output-dir outputs/welch-v1

# 2 timing x 3 composition reviewer ablation
.\.venv\Scripts\python.exe -m src.ablation --config config/reviewer_core.yaml --repetitions 30 --output-dir outputs/ablation-v1

# FTWB F / VTWB V calibration and urgency-beta sensitivity
.\.venv\Scripts\python.exe -m src.benchmark_calibration --config config/reviewer_core.yaml --repetitions 30 --output-dir outputs/benchmark-calibration-v1
.\.venv\Scripts\python.exe -m src.beta_sensitivity --config config/reviewer_core.yaml --repetitions 30 --output-dir outputs/beta-sensitivity-v1

# Censoring-aware extended Table 4 metrics
.\.venv\Scripts\python.exe -m src.additional_metrics outputs/final-TAG/results.csv outputs/final-TAG/orders.csv --output-dir outputs/additional-metrics-v1

# Decision-kernel scalability, n=10,...,5000
.\.venv\Scripts\python.exe -m src.decision_benchmark --config config/parameters.yaml --repeats 30 --target-operations 10000 --output-dir outputs/computation-time-v1

# Runtime and Python-allocation scalability
.\.venv\Scripts\python.exe -m src.benchmark --config config/benchmark_smoke.yaml --repeats 3 --output-dir outputs/benchmark-v1
```

External operational validation requires held-out data and tolerances that are
not part of this repository. When such data are available, run the executable
validation gate:

```powershell
.\.venv\Scripts\python.exe -m src.validation validation.csv --tolerances tolerances.json --output validation_report.json
```

The input must contain `split`, `metric`, `observed`, and `simulated`; both
calibration and validation splits are mandatory.

Fit candidate operational-input distributions without leaking held-out data:

```powershell
.\.venv\Scripts\python.exe -m src.input_analysis inputs.csv --output input_fit_report.json
```

The long-form input requires `parameter`, `value`, and `split` columns.

## Repository map

- `src/experiment.py`: deterministic runner and provenance manifest
- `src/audit_results.py`: final-data certification checks
- `src/analysis_pipeline.py`: publication analysis and figures
- `src/validation.py`: held-out operational validation and tolerance gate
- `src/input_analysis.py`: calibration-only input distribution fitting
- `src/welch.py`: warm-up pilot and non-stationarity diagnostics
- `src/ablation.py`: crossed timing-versus-composition experiment
- `src/benchmark_calibration.py`, `src/beta_sensitivity.py`: reviewer parameter sweeps
- `src/additional_metrics.py`: censoring-aware extended metrics
- `src/decision_benchmark.py`: decision-kernel timing and scalability
- `src/order_generator.py`: stochastic demand with injected RNG
- `src/trigger_method.py`: eight release policies and method registry
- `src/batching_method.py`, `src/routing.py`: batching and route-time logic
- `config/`: versioned experimental configuration
- `docs/`: model specification, analysis plan, validation, reporting, dictionaries
- `tests/`: unit, golden, invariant, integration, and deterministic tests
- `data/`: full-factorial results (`results_full_factorial.csv.gz`), `CHECKSUMS.txt`, and quarantined legacy output in `data/legacy/`
- `results/`: derived tables by analysis work package (`WP0`–`WP9`), see Data Availability
- `reports/`: short per-work-package reports
- `scripts/`: scripts that generated the revision-2 results, tables, and figures

## Expected smoke output

`results.csv` must contain one unique successful row per planned run,
`conservation_ok=True`, percentages in `[0,100]`, and provenance fields. Its
SHA-256 must equal `manifest.json`. `s3-audit` returns a non-zero exit code for
any violation.

## Troubleshooting

- **NumPy DLL blocked on Windows:** use the workspace `.venv`; organization
  application-control policy may block extensions installed to the user site.
- **Run is slow:** use `--mode selected --repetitions 1`; never use legacy data
  as a shortcut for publication results.
- **A run fails:** retain `results.csv` and logs for diagnosis. The runner exits
  non-zero and the batch is not publication-valid.
- **Analysis output exists:** choose a new versioned directory; overwrite is
  intentionally disabled.

## Supplementary material

The compiled supplement is [`supplement/Supplementary_Material.pdf`](supplement/Supplementary_Material.pdf)
(source: [`supplement/Supplementary_Material.md`](supplement/Supplementary_Material.md), built by
`python scripts/build_supplementary.py`; the PDF step needs `pip install reportlab`). Mapping of manuscript items to files:

| Manuscript item | Path |
|---|---|
| Appendix A (algorithm pseudocode) | [`docs/Appendix_A_pseudocode.md`](docs/Appendix_A_pseudocode.md) (extended version: [`docs/ALGORITHM_APPENDIX.md`](docs/ALGORITHM_APPENDIX.md)) |
| Table B1 (parameter provenance and change classification) | [`results/WP0/provenance_table_B1.csv`](results/WP0/provenance_table_B1.csv) |
| Table S1 (tuning surface of the FTWB/VTWB benchmarks; selected values) | [`results/WP5/tuning_surface_global.csv`](results/WP5/tuning_surface_global.csv), [`tuning_surface_global_ftwb.csv`](results/WP5/tuning_surface_global_ftwb.csv), [`tuning_surface_global_vtwb.csv`](results/WP5/tuning_surface_global_vtwb.csv), [`tuning_surface_class.csv`](results/WP5/tuning_surface_class.csv), [`selected_parameters.csv`](results/WP5/selected_parameters.csv) |
| Table S2 (run status partition; tardiness, conditional late, p95) | [`results/WP3/table4d_status_partition_exact.csv`](results/WP3/table4d_status_partition_exact.csv), [`results/WP3/tardiness_all_policies_summary.csv`](results/WP3/tardiness_all_policies_summary.csv) |
| Table S3 (MPBH vs canonical by arrival rate and picker group) | [`results/WP9/table10_v3.csv`](results/WP9/table10_v3.csv) |
| Table S4 (all-arrivals TLO; inherited backlog) | [`results/WP8/all_arrivals_tlo_v4.csv`](results/WP8/all_arrivals_tlo_v4.csv), [`results/WP8/backlog_triage_v4.csv`](results/WP8/backlog_triage_v4.csv) |
| Table S5 (crossed effects and Shapley decomposition; canonical and tuned) | [`results/WP4/crossed_effects_by_lambda_ci.csv`](results/WP4/crossed_effects_by_lambda_ci.csv), [`results/WP4/shapley_by_lambda.csv`](results/WP4/shapley_by_lambda.csv), [`results/WP5/crossed_tuned_timing_effects_by_lambda_ci.csv`](results/WP5/crossed_tuned_timing_effects_by_lambda_ci.csv), [`results/WP5/crossed_tuned_timing_shapley.csv`](results/WP5/crossed_tuned_timing_shapley.csv) |
| Table S6 (setup-time and warm-up sensitivity) | [`results/WP6/setup_sensitivity_with_tuned_and_cis.csv`](results/WP6/setup_sensitivity_with_tuned_and_cis.csv), [`warmup_11k_vs_5k_by_setup.csv`](results/WP6/warmup_11k_vs_5k_by_setup.csv), [`warmup_11k_vs_5k_by_lambda.csv`](results/WP6/warmup_11k_vs_5k_by_lambda.csv) |
| Table S7 (surrogate accuracy at batch level; oracle check) | [`results/WP7/surrogate_batch_validation.csv`](results/WP7/surrogate_batch_validation.csv), [`results/WP7/oracle_check_results_rerun.csv`](results/WP7/oracle_check_results_rerun.csv), [`results/WP7/oracle_decision_mismatch.csv`](results/WP7/oracle_decision_mismatch.csv) |
| Table S8 (change ladder; combined revert) | [`results/WP0/change_ladder_ofat.csv`](results/WP0/change_ladder_ofat.csv), [`results/WP0/combined_revert_results.csv`](results/WP0/combined_revert_results.csv) |
| Figure S1 (SD of TLO vs arrival rate) | [`Figure_10_tlo_sd_by_arrival_rate.png`](docs/revised-paper-assets/generated/Figure_10_tlo_sd_by_arrival_rate.png) |
| Figure S2 (CV of TLO vs arrival rate) | [`Figure_11_tlo_cv_by_arrival_rate.png`](docs/revised-paper-assets/generated/Figure_11_tlo_cv_by_arrival_rate.png) |
| Figure S3 (SD of TLO vs number of pickers) | [`Figure_12_tlo_sd_by_pickers.png`](docs/revised-paper-assets/generated/Figure_12_tlo_sd_by_pickers.png) |
| Figure S4 (CV of TLO vs number of pickers) | [`Figure_13_tlo_cv_by_pickers.png`](docs/revised-paper-assets/generated/Figure_13_tlo_cv_by_pickers.png) |
| Figure S5 (decision-kernel latency by policy) | [`supplement/Figure_S5_latency_scaling_pinned_core.png`](supplement/Figure_S5_latency_scaling_pinned_core.png); data: [`results/WP7/all_policies_latency_scaling_pinned_core.csv`](results/WP7/all_policies_latency_scaling_pinned_core.csv) |

Figures S1-S4 are the standard-deviation and coefficient-of-variation figures numbered 10-13 in revision 1.
`docs/revised-paper-assets/Table_04c_Flow_and_Tour_Efficiency.csv` is Table 4c (formerly named `Table_S01_...`; renamed to avoid clashing with Table S1).
An index of further documentation is in [`docs/SUPPLEMENTARY_MATERIAL.md`](docs/SUPPLEMENTARY_MATERIAL.md).

## Known gaps

The supplementary result files below were produced by analysis code that is not (or only partly) in this repository, or from data that is not distributed with it.
`scripts/regenerate_supplement_tables.py` regenerates the following files from the run-level data in the repository and reports whether they are identical (relative tolerance 1e-9) to the committed files: `results/WP9/table10_v3.csv`, `results/WP8/all_arrivals_tlo_v4.csv`, `results/WP8/backlog_triage_v4.csv`, `results/WP4/crossed_effects_by_lambda_ci.csv`, `results/WP4/shapley_by_lambda.csv`, `results/WP5/crossed_tuned_timing_effects_by_lambda_ci.csv`, `results/WP5/crossed_tuned_timing_shapley.csv` and `results/WP6/setup_sensitivity_with_tuned_and_cis.csv`.

Files without a complete generating script:

- `results/WP3/tardiness_all_policies_summary.csv`: the three run-mean columns are regenerated by the script above; the order-weighted columns and the horizon lower-bound columns need order-level data (`orders.csv.gz`), which is not distributed with this repository.
- Other result files listed in the supplementary mapping that are not named above (for example the Table S1 tuning surfaces, the oracle files of Table S7 and the warm-up comparison files of Table S6) were not regenerated in this release; their generating scripts, where they exist, are in `scripts/`.

## How to cite / version

The version referenced in the manuscript is the GitHub release/tag
**`v2.0.2-ejie-r2`** (revision 2 of EJIE-337519). This release supersedes `v2.0.1-ejie-r2` and `v2.0-ejie-r2` (the tag cited in the revision-2 submission); both older tags are kept unchanged. The three releases contain the same simulation code, configuration and result values; they differ only in documentation, supplementary material, Table B1 and change-ladder metadata, regeneration scripts and repository hygiene (see `CHANGELOG.md`). Cite the software and data of
this repository using [`CITATION.cff`](CITATION.cff) and give the tag (or the
commit it points to) so the exact files can be retrieved:

```powershell
git clone https://github.com/gustyk/s3.git
git checkout v2.0.2-ejie-r2
```

Changes between versions are listed in [`CHANGELOG.md`](CHANGELOG.md). The
Mendeley Data versions (DOI 10.17632/49r2pmymrm.1 and .2) are superseded by
this release; see Data Availability.

## Scientific status

The implementation can be verified in software, but external model validation
requires operational data and domain-expert signoff. See
[`docs/VALIDATION_PROTOCOL.md`](docs/VALIDATION_PROTOCOL.md). Code is MIT
licensed; data licensing is described in [`DATA_LICENSE.md`](DATA_LICENSE.md).
