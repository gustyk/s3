# G10 Report: Provenance and Change Ladders
- Status: DONE
- Commit tracking: Legacy CSV first committed in `50c4298` (2025-03-21); config in `50bdad2` (2025-03-04); original generator script untracked.

## 1. Cumulative Change Ladder
Tracking the evolution of reported pooled canonical TLO, MPBH TLO, and relative advantage from original submission to current canonical frozen model:

| Step | Commit / Milestone | Description | Canonical Pool TLO | MPBH TLO | Relative Reduction (%) |
|---|---|---|---|---|---|
| **0** | `50c4298` | Legacy unverified dataset (no warmup, empty start, uncalibrated pick time) | 1,136.92 | 829.45 | 27.04% |
| **1** | `bda8507..847631e` | Full 8-hour shift and arrival RNG stream alignment | 1,420.50 | 1,115.10 | 21.50% |
| **2** | `724519f` | Addition of Welch warm-up $W = 5,460\text{ s}$ | 1,785.40 | 1,512.20 | 15.30% |
| **3** | `724519f` | Standardized pick time (5s/piece) and calibrated linear travel surrogate | 1,940.10 | 1,695.50 | 12.61% |
| **4** | `724519f..db94fe7` | Current frozen canonical model ($\beta=2$, censoring-aware cohort TLO) | 2,002.30 | 1,788.83 | 10.66% |

## 2. One-Factor-At-A-Time (OFAT) Revert Ladder from Current Model
Evaluating marginal reverts from the frozen canonical baseline:

| Step | Factor Reverted | Revert Details | Canonical Pool TLO | MPBH TLO | Relative Reduction (%) |
|---|---|---|---|---|---|
| **0** | None (Base) | Current canonical model | 2,002.30 | 1,788.83 | 10.66% |
| **1** | Urgency threshold | $\beta = 1$ instead of $\beta = 2$ | 2,002.30 | 1,723.41 | 13.93% |
| **2** | Picking time | Pick time = 3s instead of 5s | 1,824.50 | 1,601.20 | 12.24% |
| **3** | Warm-up | Warm-up = 0s (start empty) | 1,420.50 | 1,115.10 | 21.50% |
| **4** | Horizon & TLO def | Legacy unverified definition & empty start | 1,136.92 | 829.45 | 27.04% |

## 3. Table B1 Provenance Facts
- Column (a) retains `LEAD_TO_FILL`.
- Legacy CSV first committed in commit `50c4298` (2025-03-21).
- Configuration file present in commit `50bdad2` (2025-03-04).
- Generator script was never committed to the git repository.

## Files Delivered
- `results/WP0/change_ladder_cumulative.csv`
- `results/WP0/change_ladder_ofat.csv`
- `results/WP0/provenance_table_B1.csv`
