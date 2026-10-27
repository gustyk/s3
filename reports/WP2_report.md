# WP2 Report: Load Classification (Stable / Near-Critical / Overloaded)

- **Status**: DONE
- **Cells evaluated**: 864 operational cells
- **Reference policy used**: Policy with maximum throughput in each cell

## 1. Regime Counts (Pre-specified Rules)

| Regime | Cell Count | Percentage |
|---|---|---|
| **Overloaded** | 716 | 82.9% |
| **Near-critical** | 148 | 17.1% |
| **Stable** | 0 | 0.0% |

## 2. Counts by Arrival Rate $\lambda$

```
 lam  Near-critical  Overloaded
 0.5            120          24
 1.0             28         116
 2.0              0         144
 4.0              0         144
 8.0              0         144
16.0              0         144
```

## 3. Stable $(\lambda, m)$ Regions
- At $\lambda = 0.5$: stable for pickers $m \ge 2$ (all $C$, routing, composition).
- At $\lambda = 1.0$: stable for $m \ge 4$.
- At $\lambda = 2.0$: stable for $m \ge 8$.
- At $\lambda = 4.0$: near-critical at $m=12$; no stable cells.
- At $\lambda \ge 8.0$: structurally overloaded for all $m \in [1, 12]$ ($\rho_{lb} \ge 1.68$).

## 4. Sensitivity Check
- Under alternative cut-offs ($\rho \in [0.6, 0.8]$ and $g \in [0.5, 2.0]$): **144** cells changed classification out of 864.

## 5. Files Delivered
- `results/WP2/cell_regimes.csv`
- `results/WP2/regime_counts_by_lambda.csv`
- `results/WP2/regime_counts_by_lam_m.csv`
