# Parameter Provenance Register

Current values are synthetic assumptions inherited from the audited repository.
They are not yet empirically calibrated.

| Parameter | Current value/source | Evidence quality | Required action |
|---|---|---|---|
| Arrival rate | configured 0.5–16 orders/min; homogeneous Poisson | assumption | fit/check time-varying arrivals from WMS timestamps |
| Due allowance | uniform 1,800–7,200 s | assumption | estimate contractual/observed due-time process |
| Order line/quantity | named categorical probabilities in generator | inherited assumption | estimate from order lines and quantify uncertainty |
| Item popularity | `config/item_popularity.yaml` | inherited synthetic profile | validate against SKU picks and seasonality |
| Layout | 384 items, 32 shelves/aisle, half-shelf 16 | inherited assumption | reconcile against scaled drawing/location master |
| Walking times | 2/4/2 s components | inherited assumption | time-motion or distance/speed calibration |
| Pick time | 3 s/item | inherited assumption | time-motion distribution, picker heterogeneity |
| Setup time | 180 s/trip | inherited assumption | define included tasks and measure distribution |
| Picker count | 1–12 | scenario factor | domain expert plausibility approval |
| Cart capacity | 100/150/200 quantity units | scenario factor | verify physical and ergonomic constraint |

Owner, observation period, sample size, missingness, cleaning rules, rights, and
calibration/validation split remain pending for every operational source.

When data become available, `src/input_analysis.py` enforces separate
calibration and validation observations and compares positive continuous
candidate distributions without using held-out observations for AIC selection.
The resulting fit report must be reviewed alongside source provenance and
domain plausibility before any configuration value is changed.
