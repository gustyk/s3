# Limitations and Threats to Validity

## Construct validity

Service level penalizes every outstanding order, including not-yet-due orders;
late outstanding is also reported separately. This conservative metric may not
match a business SLA. Cart capacity is represented by item quantity rather than
weight/volume. Picker utility measures simulated busy time, not productive labor
from a workforce system.

## Internal validity

Common random numbers reduce comparison noise but require paired analysis.
Urgency is forecast with a deterministic queue approximation. No hidden run
failure is permitted, and conservation/manifest checks protect against missing
orders and mislabeled output. Remaining model-form error must be assessed during
domain validation.

## External validity

The model omits congestion, interference, breaks, fatigue, stockouts,
replenishment, failures, cancellation, and learning. Synthetic stationary input
distributions may not represent temporal peaks or SKU seasonality. Conclusions
must be restricted to validated parameter regions.

## Statistical conclusion validity

The analysis plan uses factorial models, CRN pairing, effect sizes, confidence
intervals, and Holm adjustment. Model fit, overdispersion, residual structure,
pilot-based repetition count, MPID, and robustness models must be reported before
claims are finalized. A low p-value is not interpreted as operational importance.

