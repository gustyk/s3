# Result Data Dictionary

Each row is one configuration × repetition run. Time units are seconds and rates
are per stated denominator.

| Field | Meaning |
|---|---|
| `run_uuid` | Stable UUID derived from configuration hash, scenario, repetition |
| `seed` | Deterministic demand-stream seed |
| `status` | `success` or `failed`; final datasets permit only success |
| `generated_orders` | Unique arrivals before horizon |
| `completed_orders` | Orders completed before horizon |
| `outstanding_orders` | Waiting, pending, or active at horizon |
| `late_completed_orders` | Completed after due time |
| `late_outstanding_orders` | Outstanding and already past due at horizon |
| `service_level_percent` | On-time completed / generated × 100 |
| `throughput_per_hour` | Completed / simulated hours |
| `mean_tardiness_seconds` | Mean positive-part lateness over completed orders, including zeros |
| `p95_tardiness_seconds` | Empirical 95th percentile tardiness over completed orders |
| `mean_flow_time_seconds` | Mean completion minus arrival over completed orders |
| `p95_flow_time_seconds` | Empirical 95th percentile flow time |
| `mean_waiting_time_seconds` | Mean start minus arrival over completed orders |
| `p95_waiting_time_seconds` | Empirical 95th percentile waiting time |
| `picker_utility_percent` | Busy picker-seconds / available picker-seconds × 100 |
| `picker_utilization_spread_pp` | Maximum minus minimum individual-picker utilization, percentage points |
| `mean_cart_utilization_percent` | Mean completed batch quantity / capacity × 100 |
| `conservation_ok` | Generated IDs equal union of all terminal locations |
| provenance fields | Config hash, source-tree hash, commit/dirty flag, model version, environment manifest |
