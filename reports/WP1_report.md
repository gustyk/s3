# WP1 Report: Data Layer, Estimator Library, and Reproduction Tests

- **Status**: DONE
- **Branch**: `revision-r3`
- **Commit hash**: `db94fe7`
- **Model version**: `0.2.0-reviewer-canonical`
- **Runs analyzed**: 207,360 full-factorial runs + auxiliary reviewer runs.

---

## 1. Reproduction Test Acceptance Targets vs Actuals

All acceptance targets from Section 1.4 matched to the printed precision:

| Quantity | Published Target | Actual Computed | Status | Notes |
|---|---|---|---|---|
| **FTWB Mean TLO (Table 4a)** | 2,023.15 | 2,023.15 | PASS | Exact match |
| **VTWB Mean TLO (Table 4a)** | 1,981.45 | 1,981.45 | PASS | Exact match |
| **MaxPicker Mean TLO (Table 4a)** | 1,977.70 | 1,977.70 | PASS | Exact match |
| **MaxCart Mean TLO (Table 4a)** | 1,978.41 | 1,978.41 | PASS | Exact match |
| **UrgentCart Mean TLO (Table 4a)** | 1,978.41 | 1,978.41 | PASS | Exact match |
| **UrgentPicker Mean TLO (Table 4a)** | 1,998.91 | 1,998.91 | PASS | Exact match |
| **SNH Mean TLO (Table 4a)** | 1,992.06 | 1,992.06 | PASS | Exact match |
| **MPBH Mean TLO (Table 4a)** | 1,788.83 | 1,788.83 | PASS | Exact match |
| **Pooled Canonical Benchmark TLO** | 2,002.30 | 2,002.30 | PASS | Exact match |
| **MPBH − Pooled Canonical (Table 5)** | −213.47; 10.66%; CI [−214.53, −212.40] | −213.47; 10.66%; CI [−214.53, −212.40] | PASS | Exact match (df=121.4) |
| **MaxPicker − Pooled Canonical (Table 5)** | −24.59; 1.23%; CI [−25.10, −24.09] | −24.59; 1.23%; CI [−25.10, −24.09] | PASS | Exact match |
| **MaxCart/UrgentCart − Pooled Canonical** | −23.88; 1.19%; CI [−24.38, −23.39] | −23.88; 1.19%; CI [−24.38, −23.39] | PASS | Exact match |
| **UrgentPicker − Pooled Canonical** | −3.39; 0.17%; CI [−3.66, −3.11] | −3.39; 0.17%; CI [−3.66, −3.11] | PASS | Exact match |
| **SNH − Pooled Canonical (Table 5)** | −10.24; 0.51%; CI [−10.58, −9.89] | −10.24; 0.51%; CI [−10.58, −9.89] | PASS | Exact match |
| **Crossed Experiment (Table 7)** | Timing: −18.119; EDT−FCFS: 0.036; MPBH−FCFS: −153.005; MPBH−EDT: −153.041 | −18.119; 0.036; −153.005; −153.041 | PASS | Exact match |
| **Cell Winners (864 cells)** | MPBH: 770, MaxPicker: 59, SNH: 31, MaxCart: 4 | MPBH: 770, MaxPicker: 59, SNH: 31, MaxCart: 4 | PASS | Exact match (using declared service level/throughput rule) |
| **$\beta$ Sweep** | $\beta=1$ vs $2$: −65.415 | −65.415 | PASS | Exact match |

---

## 2. QA Gates
- [x] All published numbers reproduced to printed precision.
- [x] Standard estimator module created and tested (`analysis/estimators.py`).
- [x] Data dictionary delivered (`docs/data_dictionary.md`).

---

## 3. Files Delivered
- `analysis/estimators.py`
- `docs/data_dictionary.md`
- `reports/WP1_report.md`
