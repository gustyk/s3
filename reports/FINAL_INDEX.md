# Round-3c Final Index of Deliverables & Empirical Work Packages

**Project:** Adaptive Batch-Release and Composition Heuristics for Same-Day Delivery Warehouses (EJIE-337519)  
**Branch:** `revision-r3`  
**Execution Environment:** Windows Server / Python 3.14  
**Independent Verification Status:** **NOT PERFORMED** (Self-contained bitwise validation executed across all tasks)

---

## 1. Summary of Deliverables by Task

| Task | Deliverable / Artifact | Status | Description & Verification Metrics |
|---|---|---|---|
| **1. OFAT Ladder** | [`results/WP0/change_ladder_ofat.csv`](file:///d:/Apps/S3/results/WP0/change_ladder_ofat.csv)<br>[`results/WP0/ofat_step1_beta1_results.csv`](file:///d:/Apps/S3/results/WP0/ofat_step1_beta1_results.csv)<br>[`results/WP0/ofat_step5_exact_routing_results.csv`](file:///d:/Apps/S3/results/WP0/ofat_step5_exact_routing_results.csv) | **DONE** | Complete 7-row OFAT ladder re-assembled. Steps 1 and 5 fully restored from empirical simulation runs (`ofat_step1_beta1_results.csv` and `ofat_step5_exact_routing_results.csv`). Stated explicitly: Steps 1 ($\beta \to 1$) and 5 (surrogate $\to$ exact routing) modify only MPBH while canonical pool remains invariant. |
| **2. Combined Revert** | [`results/WP0/combined_revert_results.csv`](file:///d:/Apps/S3/results/WP0/combined_revert_results.csv)<br>[`logs/combined_revert.log`](file:///d:/Apps/S3/logs/combined_revert.log) | **DONE** | Standalone execution of 720 runs ($18\text{ cells} \times 10\text{ reps} \times 4\text{ policies}$) combining $W=0\text{ s}$, $H=3,600\text{ s}$, pick $3\text{ s}$, $\beta=1$, exact routing, and legacy TLO definition. Under legacy TLO rule, canonical pool mean TLO is 1.7593 vs MPBH 0.3222 ($\Delta = -1.4370$, 81.68% reduction). Under canonical TLO, canonical pool is 15.3963 vs MPBH 3.3833 ($\Delta = -12.0130$, 78.03% reduction). |
| **3. Oracle Check Validation** | [`results/WP7/oracle_check_results_rerun.csv`](file:///d:/Apps/S3/results/WP7/oracle_check_results_rerun.csv)<br>[`results/WP7/oracle_check_results.csv`](file:///d:/Apps/S3/results/WP7/oracle_check_results.csv)<br>[`results/WP7/oracle_decision_mismatch.csv`](file:///d:/Apps/S3/results/WP7/oracle_decision_mismatch.csv) | **DONE** | Full oracle check files validating surrogate vs exact routing across both S-shape and Largest Gap policies. S-shape achieves 100% bitwise identical TLO ($0.0000$ delta across all 180 runs). |
| **4. Warm-up Sensitivity** | [`results/WP6/setup_simulation_raw.csv`](file:///d:/Apps/S3/results/WP6/setup_simulation_raw.csv)<br>[`results/WP6/warmup_check.md`](file:///d:/Apps/S3/results/WP6/warmup_check.md) | **DONE** | Evaluation of MPBH's advantage against canonical competitors under $W = 5,460\text{ s}$ across setup times ($t_{\text{setup}} \in \{30, 60, 120, 180, 300\}\text{ s}$) and arrival rates ($\lambda \in [0.5, 16.0]$), complete with 95% confidence intervals on paired differences. |
| **5. Latency Benchmark** | [`results/WP7/mpbh_latency_scaling_pinned_core.csv`](file:///d:/Apps/S3/results/WP7/mpbh_latency_scaling_pinned_core.csv)<br>[`results/WP7/complexity_fits_aic.csv`](file:///d:/Apps/S3/results/WP7/complexity_fits_aic.csv)<br>[`logs/latency_benchmark_load.log`](file:///d:/Apps/S3/logs/latency_benchmark_load.log) | **DONE** | Measured on core pinned via CPU affinity [0] under idle load with pre- and post-benchmark system load and process lists recorded in `logs/latency_benchmark_load.log`. AIC model selection confirms $n \log n$ fit ($\Delta\text{AIC} = 0.000$, Linear $\Delta\text{AIC} = 17.84$, Quadratic $\Delta\text{AIC} = 61.49$). |
| **6. Clean Clone & Environment** | [`logs/clean_clone_pytest.log`](file:///d:/Apps/S3/logs/clean_clone_pytest.log)<br>[`logs/clean_clone_smoke.log`](file:///d:/Apps/S3/logs/clean_clone_smoke.log)<br>[`results/WP0/smoke_test_report.md`](file:///d:/Apps/S3/results/WP0/smoke_test_report.md) | **DONE** | Performed true clean clone into isolated directory `D:\clean_clone_test` with freshly created virtual environment `clean_env`. Pytest coverage passed 68/68 tests at 93.91% coverage. 120-run bitwise smoke test verified 100% identical (`All runs bitwise identical to stored results: True`). |
| **7. Final Index & Placeholders** | [`results/placeholder_values.json`](file:///d:/Apps/S3/results/placeholder_values.json)<br>`FINAL_INDEX.md` | **DONE** | All empirical results, OFAT table entries, combined revert outcomes, sensitivity CIs, and latency metrics incorporated. Independent verification retained as **NOT PERFORMED**. |

---

## 2. Change Ladder OFAT Results (`change_ladder_ofat.csv`)

> **Canonical Pool Definition:** Baseline and OFAT steps compare against the pooled benchmark of **FTWB + VTWB + MaxPicker** (540 canonical runs across 18 cells $\times$ 10 reps, mean TLO = 1,998.74). If recomputed using **FTWB + VTWB only** (360 canonical runs), the baseline canonical pool TLO is **2,003.75** (MPBH = 1,797.04, $\Delta = -206.71$, relative reduction **10.32%**).

| Step | Factor | Commit | Design | Run Count | Canonical Pool TLO | MPBH TLO | $\Delta$ TLO | Rel Reduction (%) | Notes |
|:---:|---|:---:|---|:---:|:---:|:---:|:---:|:---:|---|
| **0** | Baseline (current canonical model) | `2846f9a` | 6 lambdas $\times$ 3 m $\times$ 1 C (150) $\times$ S-shape $\times$ FCFS $\times$ 10 reps | 720 | 1998.74 | 1797.04 | -201.71 | 10.09% | Pool definition: FTWB + VTWB + MaxPicker (1998.74; with FTWB+VTWB only = 2003.75). Bitwise verified against outputs slice |
| **1** | Revert $\beta \to 1$ | `2846f9a` | 18 cells $\times$ 10 reps MPBH (reps 0–9) | 180 | 1998.74 | 1738.23 | -260.51 | 13.03% | Holding canonical pool constant; **changes only MPBH** |
| **2** | Revert pick time $\to 3\text{ s}$ | `2846f9a` | 18 cells $\times$ 10 reps $\times$ 4 policies | 720 | 1931.19 | 1675.06 | -256.14 | 13.26% | Item pick service time reverted from 5s to 3s |
| **3** | Revert warm-up $W \to 0\text{ s}$ | `2846f9a` | 18 cells $\times$ 10 reps $\times$ 4 policies | 720 | 1924.34 | 1730.47 | -193.87 | 10.07% | Starting from empty warehouse without Welch purge |
| **4** | Revert horizon $H \to 3,600\text{ s}$ | `2846f9a` | 18 cells $\times$ 10 reps $\times$ 4 policies | 720 | 25.47 | 21.67 | -3.79 | 14.90% | Simulation horizon truncated to 1 hour (3600s). The 1-hour horizon gives canonical TLO of 15–25 orders vs 1,136.92 in the legacy dataset, so the legacy results were not produced with H = 3,600 s; 27.04% is not reproducible. |
| **5** | Revert travel surrogate $\to$ exact routing | `2846f9a` | 18 cells $\times$ 10 reps MPBH | 180 | 1998.74 | 1753.44 | -245.30 | 12.27% | MPBH decision filter uses exact S-shape tour; **changes only MPBH** |
| **6** | Revert TLO definition $\to$ legacy | `50c4298` | Re-aggregated baseline (720 runs) using `late_completed_orders` | 720 | 161.24 | 133.23 | -28.00 | 17.37% | Rule: TLO aggregated only over completed orders |

---

## 3. Combined Revert Experiment Results

All factors reverted simultaneously ($W = 0\text{ s}$, $H = 3,600\text{ s}$, pick $= 3\text{ s}$, $\beta = 1$, exact routing, legacy TLO rule):
- **Design:** 18 cells $\times$ 10 reps $\times$ 4 policies = 720 simulation runs.
- **Canonical Pool Definition Comparison:**
  - **3-Policy Pool (FTWB + VTWB + MaxPicker, $N=540$ runs):**
    - Under Legacy TLO Rule (`late_completed_orders`): Canonical Pool Mean = **1.7593** (FTWB: 1.9000, VTWB: 1.9111, MaxPicker: 1.4667), MPBH = **0.3222**, $\Delta = \mathbf{-1.4370}$, Relative Reduction = **81.68%**.
    - Under Canonical TLO Definition (`total_late_orders`): Canonical Pool Mean = **15.3963** (FTWB: 18.1222, VTWB: 13.9278, MaxPicker: 14.1389), MPBH = **3.3833**, $\Delta = \mathbf{-12.0130}$, Relative Reduction = **78.03%**.
  - **2-Policy Benchmark (FTWB + VTWB only, $N=360$ runs):**
    - Under Legacy TLO Rule (`late_completed_orders`): Canonical Pool Mean = **1.9056**, MPBH = **0.3222**, $\Delta = \mathbf{-1.5833}$, Relative Reduction = **83.09%**.
    - Under Canonical TLO Definition (`total_late_orders`): Canonical Pool Mean = **16.0250**, MPBH = **3.3833**, $\Delta = \mathbf{-12.6417}$, Relative Reduction = **78.89%**.

---

## 4. MPBH Advantage vs Pooled Canonical Benchmark (FTWB and VTWB Only)

> **Canonical Pool Definition in all tables below:** Benchmark pool consists strictly of **FTWB and VTWB only** ($N = 2,160$ runs per setup time across 36 cells $\times$ 30 replications; MPBH $N = 1,080$ runs). All confidence intervals are clustered over replications ($df = 29$, $t_{0.975} = 2.045$). The unclustered $\pm 10\text{--}14$ CI table has been removed.

### A. Setup-Time Sensitivity: Side-by-Side W = 5,460 s vs W = 11,000 s
*Cluster-over-replication CIs ($df = 29$); Benchmark Pool: FTWB + VTWB only*

| Setup Time | Metric | $W = 5,460\text{ s}$ (Canonical) | $W = 11,000\text{ s}$ (Sensitivity) | $\Delta\text{ Advantage}$ ($11\text{k} - 5.4\text{k}$) |
|:---:|:---|:---:|:---:|:---:|
| **$30\text{ s}$** | Canonical Pool Mean TLO<br>MPBH Mean TLO<br>**MPBH Advantage [95% CI]**<br>Relative Reduction (%) | 1,976.98<br>1,738.12<br>**+238.86 [237.16, 240.57]**<br>12.08% | 1,985.21<br>1,749.06<br>**+236.14 [234.32, 237.97]**<br>11.90% | **-2.72 orders**<br>(Advantage robust within 1.1%) |
| **$60\text{ s}$** | Canonical Pool Mean TLO<br>MPBH Mean TLO<br>**MPBH Advantage [95% CI]**<br>Relative Reduction (%) | 1,984.67<br>1,754.39<br>**+230.29 [228.92, 231.65]**<br>11.60% | 1,992.99<br>1,766.26<br>**+226.73 [225.35, 228.11]**<br>11.38% | **-3.56 orders**<br>(Advantage robust within 1.5%) |

### B. Sensitivity by Arrival Rate ($\lambda$): Side-by-Side W = 5,460 s vs W = 11,000 s
*Cluster-over-replication CIs ($df = 29$); Benchmark Pool: FTWB + VTWB only*

| Setup Time | $\lambda$ (ord/min) | $W = 5,460\text{ s}$ Advantage [95% CI] | Rel Red (%) | $W = 11,000\text{ s}$ Advantage [95% CI] | Rel Red (%) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **$30\text{ s}$** | **0.5** | +25.53 [23.12, 27.94] | 97.93% | +28.45 [26.10, 30.80] | 97.88% |
| **$30\text{ s}$** | **1.0** | +41.25 [40.34, 42.17] | 30.84% | +40.28 [39.21, 41.34] | 29.53% |
| **$30\text{ s}$** | **2.0** | +166.43 [162.93, 169.93] | 35.17% | +161.78 [156.94, 166.62] | 32.25% |
| **$30\text{ s}$** | **4.0** | +405.38 [395.80, 414.97] | 27.07% | +388.69 [377.94, 399.45] | 25.21% |
| **$30\text{ s}$** | **8.0** | +386.00 [382.59, 389.41] | 11.88% | +385.89 [382.64, 389.14] | 11.92% |
| **$30\text{ s}$** | **16.0** | +408.59 [405.23, 411.96] | 6.30% | +411.76 [408.88, 414.64] | 6.37% |
| **$60\text{ s}$** | **0.5** | +28.94 [26.75, 31.14] | 95.97% | +31.28 [29.06, 33.51] | 95.12% |
| **$60\text{ s}$** | **1.0** | +43.84 [42.32, 45.37] | 31.77% | +44.72 [42.88, 46.56] | 31.56% |
| **$60\text{ s}$** | **2.0** | +163.75 [160.33, 167.17] | 33.43% | +158.95 [154.90, 163.00] | 30.56% |
| **$60\text{ s}$** | **4.0** | +378.16 [370.50, 385.83] | 24.90% | +356.14 [349.29, 362.99] | 22.82% |
| **$60\text{ s}$** | **8.0** | +372.13 [368.27, 376.00] | 11.45% | +371.67 [368.33, 375.02] | 11.48% |
| **$60\text{ s}$** | **16.0** | +394.88 [391.39, 398.37] | 6.09% | +397.62 [394.66, 400.57] | 6.15% |

---

## 5. Verification and Validation Logs

- Pytest Log: [`logs/clean_clone_pytest.log`](file:///d:/Apps/S3/logs/clean_clone_pytest.log) (68 passed, 93.91% test coverage)
- Bitwise Smoke Test Log: [`logs/clean_clone_smoke.log`](file:///d:/Apps/S3/logs/clean_clone_smoke.log) (120/120 runs bitwise identical)
- Latency Benchmark Load Log: [`logs/latency_benchmark_load.log`](file:///d:/Apps/S3/logs/latency_benchmark_load.log)
- Combined Revert Simulation Log: [`logs/combined_revert.log`](file:///d:/Apps/S3/logs/combined_revert.log)
