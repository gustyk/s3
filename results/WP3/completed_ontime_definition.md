# Completed On-Time Rate Definition and Handling

- **Definition**:
  $$\text{completed\_ontime\_rate} = \frac{N_{\text{completed on-time}}}{N_{\text{completed}}}$$
- **Handling of Zero Completed Runs**:
  When a simulation run completes zero cohort orders ($N_{\text{completed}} = 0$), the completion-based on-time rate is mathematically undefined (0/0). It is recorded as `NaN` and excluded from the run-mean calculation (never imputed as 0, which would distort survivorship bias).
- **Number of Undefined Runs per Policy**:
  - FTWB: 6,779 runs
  - VTWB: 6,690 runs
  - UrgentPicker: 5,005 runs
  - MaxPicker: 4,959 runs
  - MaxCart / UrgentCart: 4,948 runs
  - SNH: 246 runs
  - MPBH: 0 runs (MPBH completed at least one order in 100% of the 25,920 runs)
