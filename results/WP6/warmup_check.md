# WP6 Warmup and Setup Time Sensitivity Check
Commit: `e97b57d87a31cf4869b10829ff6d528bd8b2d4ad`

## Setup Sensitivity Overview
The setup-time experiment tested $t_{\text{setup}} \in \{30, 60, 120, 180, 300\}\$ seconds across all 36 canonical cells and 30 replications (1,080 runs per policy per setup level).

### Performance Across Setup Times
| $t_{\text{setup}}$ (s) | MPBH Mean TLO | Canonical Pooled Mean TLO | Rel Reduction (%) | MPBH Cleared Cells (/36) |
|---|---|---|---|---|
| 30 | 1738.12 | 1976.98 | 12.08% | 10/36 |
| 60 | 1754.39 | 1984.67 | 11.60% | 10/36 |
| 120 | 1782.10 | 2002.06 | 10.99% | 10/36 |
| 180 | 1803.16 | 2014.18 | 10.48% | 9/36 |
| 300 | 1832.91 | 2026.87 | 9.57% | 8/36 |

## Warmup Validity
The simulation warm-up duration $W = 5,460$ s (91 minutes) remains significantly longer than any picker setup overhead or trip cycle time across all $t_{\text{setup}} \in [30, 300]$ s.
Even under the highest setup duration ($t_{\text{setup}} = 300$ s), the steady-state queue dynamics stabilize prior to $W$, confirming cohort isolation ($W \le \text{arrival} < H$).
