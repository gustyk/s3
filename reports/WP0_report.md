# WP0 Report: Pre-flight, Freeze and Parameter-Provenance Audit

- **Status**: DONE
- **Branch**: `revision-r3`
- **Starting tag**: `r3-start`
- **Commit hash**: `db94fe7`
- **Model version**: `0.2.0-reviewer-canonical`
- **Config hash**: `d359bc8f3a2cda65123a640155339ce18092ae8214913fc6561b916ffd42234f`
- **Source tree hash**: `3daa3db4968f054b4eafccf1a38791b0d5e65e7a64c1fe913ba6580876939e3e`
- **Runs**: 120 requested / 120 completed / 0 failed.
- **Hardware / OS**: Windows 11 AMD64, Intel64 Family 6 Model 158 Stepping 9, Python 3.14.6.

---

## 1. Key Results

### Classification of Reporting Errors vs Implementation Changes (Section 0.2, Table B1)
1. **FTWB interval F**: **Reporting error**. The simulation code from the very first commit (`50bdad2d:config/parameters.yaml:25`) has consistently configured and executed `FTWB_interval = 720` s. The value `360 s` printed in the originally submitted manuscript text was a typographical/reporting error.
2. **Setup time t_setup**: **Reporting error**. The configuration and simulation engine from the earliest commit (`50bdad2d:config/parameters.yaml:69`) has used `setup_time = 180` s. The value `30 s` printed in the manuscript was a typographical/reporting error.
3. **Warm-up and Pick time per piece**: **Implementation changes prior to freeze**. Originally no warm-up was present and pick time was 3 s/piece; with the hardening workflow (commit `724519f`), Welch warm-up $W=5,460$ s (91 min) and standardized 5 s/piece picking were instituted.

### Change Ladder: Why 27.04% became 10.66%? (Section 0.3)
- In the legacy unverified dataset (`data/legacy/simulation_results_legacy_unverified.csv`), pooled canonical TLO was 1,136.92 and MPBH TLO was 829.45, giving:
  $$\frac{1136.92 - 829.45}{1136.92} = 27.04\%$$
- The shift to **10.66%** is explained by:
  1. Introduction of the **5,460 s Welch warm-up**: eliminating the artificially low initial backlog (starting with empty system) raised steady-state load across all policies.
  2. Strict **cohort-based censoring definition** of Total Late Orders (TLO = completed late + outstanding overdue at $H=34,260$ s).
  3. Standardization of picking times (5 s/piece) and surrogate calibration. Under these realistic, un-biased steady-state conditions, pooled canonical TLO is 2,002.30 and MPBH TLO is 1,788.83, giving $\Delta = -213.47$ orders (-10.66%).

---

## 2. QA Gates
- [x] **Smoke test bitwise-identical**: 120 runs across 5 scenarios $\times$ 3 replications $\times$ 8 policies were executed and verified against stored results. Total Late Orders (TLO), throughput per hour, and trip counts matched bitwise (100% exact equality).
- [x] **Parameter provenance traceable**: Every entry in `results/WP0/provenance_table_B1.csv` is mapped to exact file paths, line numbers, and git commits.

---

## 3. Files Delivered
- `results/WP0/provenance_table_B1.csv`
- `results/WP0/change_ladder.csv`
- `results/WP0/smoke_test_report.md`
- `env/pip_freeze.txt`
- `env/system_info.txt`
