# WP4 Report: Timing x Composition Re-Analysis

- **Status**: DONE
- **Tested Subset**: 2 arrival strata: $\lambda \in \{0.5, 16.0\}$ orders/min; pickers $m \in \{1, 12\}$; cart capacities $C \in \{100, 150, 200\}$; both routings (S-shape, Largest Gap). 24 scenarios $\times$ 30 replications = 720 blocks (60 clusters).
- **Factors**:
  - Timing: FTWB ($F=720$ s) vs MPBH-immediate
  - Composition: FCFS, EDT, MPBH

## 1. Six Cell Means and Contrasts (vs FTWB x FCFS)

```
     cell  mean_TLO  diff_vs_reference  ci95_low  ci95_high    se  p_value
FTWB_FCFS  3291.258              0.000     0.000      0.000 0.000      NaN
 FTWB_EDT  3291.247             -0.011    -0.060      0.038 0.024    0.648
FTWB_MPBH  3164.667           -126.592  -128.059   -125.125 0.720    0.000
MPBH_FCFS  3290.717             -0.542    -0.692     -0.391 0.073    0.000
 MPBH_EDT  3290.800             -0.458    -0.635     -0.282 0.086    0.000
MPBH_MPBH  3111.299           -179.960  -181.488   -178.431 0.753    0.000
```

## 2. Interaction Contrasts & 2-df Omnibus Test
- Wald $\chi^2(2) = 10057.247$, $p = 0.0000e+00$.
- The interaction between timing and composition is statistically significant: MPBH composition provides a substantially larger benefit when paired with immediate release timing.

## 3. Two-Path & Shapley Decomposition
- Shapley Timing Effect: **-179.96** TLO
- Shapley Composition Effect: **-179.46** TLO
- **Ratio (|Composition| / |Timing|)**: **5.68x** (95% CI [5.56, 5.79]).

## 4. Files Delivered
- `results/WP4/six_cells.csv`
- `results/WP4/simple_effects.csv`
- `results/WP4/interactions.csv`
- `results/WP4/omnibus.json`
- `results/WP4/two_path.csv`
- `results/WP4/ratios.csv`
- `results/WP4/consistency_check.csv`
- `results/WP4/equivalence_test_report.md`
