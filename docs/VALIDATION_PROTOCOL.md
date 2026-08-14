# Model Validation Protocol

Status: **BLOCKED pending operational data and domain experts**.

For each input, record owner, source system, observation period, sample size,
units, missingness, cleaning, outlier rule, fitted distribution, goodness of fit,
calibration split, validation split, redistribution rights, and reviewer signoff.

Required inputs: arrival timestamps, order-line counts, quantities, item
popularity, due-time allowances, layout, walk time/distance, pick time, setup
time, staffing calendars, breaks, congestion, and benchmark KPI.

Required evidence:

1. Face-validation session with at least one warehouse subject-matter expert.
2. Baseline output comparison against held-out operational KPI with tolerances
   fixed before comparison.
3. Extreme/degenerate tests: zero/near-zero demand, overload, one picker, large
   staffing, exact cart capacity, earliest/latest due regime.
4. Calibration and validation error with uncertainty intervals.
5. Signed decision: accepted, conditionally accepted, or rejected.

Engineering extreme/degenerate evidence is catalogued in
`EXTREME_CONDITION_EVIDENCE.md`. Those tests are necessary verification but do
not replace domain-calibrated stress limits.

## Input-distribution fitting gate

Prepare long-form operational input data with columns `parameter`, `value`, and
`split`; each parameter requires at least eight calibration and three held-out
validation observations. Run:

`python -m src.input_analysis inputs.csv --output input_fit_report.json`

The report compares exponential, gamma, lognormal, Weibull, and uniform models
using calibration AIC/BIC and KS diagnostics, then reports held-out mean
negative log likelihood. No outliers are removed by default; `--outlier-rule
iqr` is available only when that cleaning rule was prespecified and justified.
Automated minimum AIC is a screening result, not a substitute for graphical
diagnostics or domain plausibility review.

No publication claim may call this model “validated” until this protocol is
completed and linked evidence is reviewed.

## Executable validation gate

Prepare a CSV with columns `split`, `metric`, `observed`, and `simulated`.
Every row must be assigned to either `calibration` or held-out `validation`.
Freeze a JSON tolerance file before inspecting validation results, for example:

```json
{
  "throughput_per_hour": {"max_mae": 5, "max_mape_percent": 10},
  "service_level_percent": {"max_mae": 3, "max_rmse": 4}
}
```

Run `python -m src.validation validation.csv --tolerances tolerances.json
--output validation_report.json`. The command reports bias, MAE, RMSE, MAPE,
deterministic bootstrap 95% intervals, and exits non-zero for missing or breached
validation tolerances. Tolerance values require domain approval; the example is
schema illustration only, not an approved criterion.
