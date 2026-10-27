# G1 Report: Benchmark Tuning (Class-Tuned Variants, Pre-Specified S2, Addendum SHA-256)
- Status: DONE
- Checkpoint commit: v1.0-frozen
- Addendum file SHA-256: `d8458978ce015f3cf277ad26dc48b328b75eaba434c6d265e8c43b87f7f052b4`
- Tuning data source: `results/WP5/class_tuning_checkpoint.csv` (60,480 runs) + `class_tuning_refinement_checkpoint.csv` (12,960 runs) = **73,440 simulation runs** on replications 0-14.
- Target Metric: `total_late_orders` (cohort TLO measured strictly in **ORDERS**, not seconds).

## 1. Root Cause Analysis: Metric Reconciliation (Orders vs Seconds)
- **Why the previous addendum reported F* = 720 s and MaxPicker mean TLO = 5,776 s**:
  The earlier script averaged `mean_tardiness_seconds` instead of `total_late_orders`. In seconds, long batches at F = 720 s compress late-order tardiness among cleared runs (5,674.86 s), whereas MaxPicker's fast releases yield 5,776.38 s.
- **Corrected Analysis in ORDERS (`total_late_orders`)**:
  - In terms of actual late orders (TLO), F = 5 s achieves the minimum late orders (**1,990.20 orders**), while F = 720 s incurs **2,024.42 orders**.
  - For VTWB, V = 8 orders achieves **1,992.98 orders** (S1) and V = 6 orders achieves **1,993.03 orders** (S2).
  - Therefore, the **frozen parameter file was correct all along** (F* = 5 s, V* = 8 orders S1, V* = 6 orders S2).
  - MaxPicker on the same 144 cells achieves **1,989.86 orders**, exactly matching F = 5 s within 0.34 orders.

## 2. Bitwise Verification: 2,160 MaxPicker Re-Runs vs Factorial Runs
- Number of paired runs compared: **2,160 runs** across 144 cells x replications 0-14.
- Max absolute difference in `total_late_orders`: **0.0 orders** (0 mismatches across 2,160 runs).
- Max absolute difference in `throughput_per_hour`: **0.0 orders/h**.
- Max absolute difference in `completed_orders`: **0 orders**.
- **Bitwise equivalence assertion**: **PASSED**.

### Five Sample (Cell, Replication) Pairs Across lambda = 0.5 to 16:
| lambda | Cell Index | Pickers (m) | Cart (C) | Routing | Batching | Repetition | Factorial MaxPicker TLO | New MaxPicker TLO | FTWB (F=5) TLO | FTWB (F=720) TLO |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 2 | 4 | 150 | S-shape | FCFS | 10 | 0 | 0 | 0 | 0 |
| 1.0 | 24 | 4 | 100 | S-shape | FCFS | 0 | 172 | 172 | 172 | 399 |
| 2.0 | 48 | 4 | 150 | Largest Gap | EDT | 0 | 837 | 837 | 837 | 837 |
| 4.0 | 72 | 2 | 200 | Largest Gap | FCFS | 0 | 1640 | 1640 | 1640 | 1640 |
| 16.0 | 120 | 2 | 150 | Largest Gap | EDT | 0 | 6586 | 6586 | 6586 | 6586 |

## 3. Global Tuning Surface Summary (`total_late_orders` in Orders)
- **FTWB Grid**:
  - F = 5 s: **1,990.20 orders** (Throughput: 42.51 orders/h, Picker Utility: 91.33%)
  - F = 10 s: **1,990.53 orders**
  - F = 15 s: **1,990.94 orders**
  - F = 30 s: **1,992.14 orders**
  - F = 60 s: **1,994.48 orders**
  - F = 120 s: **1,998.74 orders**
  - F = 180 s: **2,002.20 orders**
  - F = 300 s: **2,007.89 orders**
  - F = 600 s: **2,021.15 orders**
  - F = 720 s: **2,024.42 orders**
- **VTWB Grid**:
  - V = 8 orders: **1,992.98 orders** (Throughput: 41.44 orders/h, Picker Utility: 85.26%)
  - V = 6 orders: **1,993.03 orders** (Throughput: 41.13 orders/h, Picker Utility: 85.45%)
  - V = 10 orders: **1,993.88 orders**
  - V = 12 orders: **1,994.82 orders**
  - V = 4 orders: **1,997.81 orders**
  - V = 2 orders: **2,016.34 orders**
  - V = 1 order: **2,059.89 orders**

## 4. Status of Scope B Held-Out Evaluation (51,840 + 25,920 Runs)
- **Execution Status**: **COMPLETE (100%)**.
- **Completed Run Count**:
  - Global variants & sensitivities: **51,840 runs** across all 864 cells x replications 15-29 (15 reps each):
    - FTWB tuned (F = 5 s): 12,960 runs.
    - VTWB tuned S1 (V = 8 orders): 12,960 runs.
    - VTWB tuned S2 (V = 6 orders): 12,960 runs.
    - MPBH beta=1 sensitivity: 6,480 runs.
    - Crossed FTWB(F=5) x MPBH composition: 6,480 runs.
  - Class-tuned VTWB variants: **25,920 runs** across all 864 cells x replications 15-29 (15 reps each):
    - VTWB class-tuned by lambda: 12,960 runs.
    - VTWB class-tuned by lambda x group: 12,960 runs.
  - Total held-out simulation runs executed: **77,760 runs**.
- **Errors**: 0 failed runs.
- **Replication-split assertion log**: Verified strictly 15 <= rep <= 29 across all runs.
- Output raw files:
  - `results/WP5/held_out_evaluation_raw.csv.gz`
  - `results/WP5/held_out_class_tuned_vtwb_raw.csv`

## 5. Scope B Head-to-Head Findings (Replications 15-29)
- MPBH (beta=2): **1,787.47 orders**
- Canonical Pooled: **2,000.42 orders** (MPBH advantage: -212.96 orders, **10.65% reduction**)
- MaxPicker: **1,975.83 orders** (MPBH advantage: -188.36 orders, **9.53% reduction**)
- FTWB Tuned (F* = 5 s): **1,976.16 orders** (MPBH advantage: -188.69 orders, **9.55% reduction**)
- VTWB Tuned S1 (V* = 8 orders): **1,977.76 orders** (MPBH advantage: -190.29 orders, **9.62% reduction**)
- VTWB Tuned S2 (V* = 6 orders): **1,978.12 orders** (MPBH advantage: -190.65 orders, **9.64% reduction**)
- VTWB Class-Tuned by lambda: **1,977.27 orders** (MPBH advantage: -189.81 orders, **9.60% reduction**)
- VTWB Class-Tuned by lambda x group: **1,977.30 orders** (MPBH advantage: -189.83 orders, **9.60% reduction**)
- Tuned Pooled: **1,976.96 orders** (MPBH advantage: -189.49 orders, **9.59% reduction**)
- MPBH beta=1 sensitivity: **1,725.16 orders** (even stronger performance with tighter threshold).

## Files Delivered
- `results/WP5/selected_parameters_addendum.csv`
- `results/WP5/selected_parameters_addendum.csv.sha256`
- `results/WP5/tuning_surface_global.csv`
- `results/WP5/tuning_surface_class.csv`
- `results/WP5/maxpicker_tuning_raw.csv`
- `results/WP5/held_out_evaluation_raw.csv.gz`
- `results/WP5/held_out_class_tuned_vtwb_raw.csv`
- `results/WP5/head_to_head_scopeB_overall.csv`
- `results/WP5/head_to_head_scopeB_by_lambda.csv`
- `results/WP5/head_to_head_scopeB_by_group.csv`
- `results/WP5/head_to_head_scopeB_by_band.csv`
- `results/WP5/head_to_head_scopeB_by_cleared.csv`
- `results/WP5/crossed_tuned_timing_six_cells.csv`
- `results/WP5/crossed_tuned_timing_shapley.csv`
- `results/WP5/crossed_tuned_timing_effects.csv`
