# Report T4: Work Package 5 (Benchmark Calibration and Head-to-Head Evaluation)

**Status:** NOT RUN  
**Git Commit:** `222784287f05eea5d847ac749a4bb2783daedb6c`  
**Model Version:** `v1.0-frozen`  
**Evaluation Protocol:** Replications 1–15 reserved for calibration/tuning; replications 16–30 strictly held out for final evaluation.  

---

## 1. Status Notice & Work-Package Overview
Task T4 is officially designated as **NOT RUN** in strict compliance with Rule R1:
- The full pre-specified extended-grid class-tuning sweep requires:
  $$\text{144 stratified cells} \times \text{15 tuning replications (1..15)} \times \text{28 grid points} = \mathbf{60,480\text{ simulation runs}}$$
  - **$F$ grid:** $\{5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 300, 360, 480, 600, 720\}\text{ s}$ (16 points).
  - **$V$ grid:** $\{1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24\}\text{ orders}$ (12 points).
- The subsequent held-out Scope B evaluation across all 864 cells on replications 16–30 requires:
  $$\text{4 tuned variants} \times \text{864 cells} \times \text{15 held-out replications (16..30)} = \mathbf{51,840\text{ simulation runs}}$$
- The legacy pilot runs ($N=5,760$ on 24 extreme cells) remain archived as diagnostic only and do NOT constitute completion of T4.
- Total required runs for T4: **$60,480 + 51,840 = \mathbf{112,320\text{ runs}}$**.

---

## 2. Pre-Specified Stratified Class-Tuning Sample (144 Cells)
The 144 class-tuning cells were drawn by stratified random sampling (fixed seed 42, before any tuning job) across the 6 arrival strata (24 cells per $\lambda$), evenly distributed across picker groups (8 scarce $m \in 1..4$, 8 mid $m \in 5..8$, 8 abundant $m \in 9..12$):
- Cell list archived: [`results/WP5/class_tuning_sample_144cells.csv`](file:///d:/Apps/S3/results/WP5/class_tuning_sample_144cells.csv).

---

## 3. Parameter Freezing & Cryptographic SHA-256 Gate
Before running held-out Scope B evaluation runs, `results/WP5/selected_parameters.csv` will be frozen and verified against its committed SHA-256 sidecar:
- Current diagnostic template hash: `results/WP5/selected_parameters.csv.sha256` (`e40bd7ac61dd6d56e547d204b99f60574a4738d446c414b35857d3ad62c5fc71`).
