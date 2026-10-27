# WP5 & WP6 Simulation Budget and Execution Plan

## 1. Hardware & Runtime Profiling
- **Hardware**: Windows 11 64-bit AMD64, Intel64 Family 6 Model 158 Stepping 9
- **Mean runtime per single run**:
  - Low arrival rate ($\lambda = 0.5$): ~0.08 s / run
  - High arrival rate ($\lambda = 16.0$): ~0.85 s / run
  - Average across factorial: ~0.35 s / run

## 2. WP5 Benchmark Calibration & Head-to-Head Runs
- **Extended Grids**:
  - $F \in \{5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 300, 360, 480, 600, 720\}$ s (16 values)
  - $V \in \{1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24\}$ orders (12 values)
- **Tuning Sample (Replications 1–15)**:
  - Global tuning on calibration subset: 24 scenarios $\times$ 15 reps $\times$ 28 grid points = 10,080 runs
  - Class-tuning sample (6 $\lambda$ strata $\times$ 24 sampled cells = 144 cells): 144 cells $\times$ 15 reps $\times$ 28 grid points = 60,480 runs
- **Held-out Evaluation (Replications 16–30)**:
  - Canonical benchmarks (FTWB, VTWB, MPBH, MaxPicker) on reps 16–30: Reused directly from verified full-factorial results (0 additional runs).
  - Globally tuned FTWB, globally tuned VTWB, class-tuned FTWB, class-tuned VTWB, plus MPBH $\beta=1$: 864 cells $\times$ 15 reps $\times$ 5 variants = 64,800 runs.
- **Estimated WP5 compute time**: ~135,000 runs @ ~0.35 s $\approx$ 13.1 core-hours (executable via multi-worker multiprocessing).

## 3. WP6 Setup-Time Sensitivity Runs
- Design: $t_{\text{setup}} \in \{30, 60, 120, 180, 300\}$ s
- 36 cells $\times$ 30 replications $\times$ 10 policies
- $t_{\text{setup}} = 180$ s runs: 36 $\times$ 30 $\times$ 8 = 8,640 runs reused bitwise from stored factorial.
- New runs for $\{30, 60, 120, 300\}$ s: 36 $\times$ 30 $\times$ 4 settings $\times$ 10 policies = 43,200 runs.
- **Estimated WP6 compute time**: ~43,200 runs @ ~0.35 s $\approx$ 4.2 core-hours.
