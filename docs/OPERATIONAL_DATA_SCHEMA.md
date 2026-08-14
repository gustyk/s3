# Operational Data Acquisition Schema

Status: **TEMPLATE — no operational records have been supplied**.

All timestamps must use ISO 8601 with an explicit offset or be accompanied by a
single documented warehouse timezone. Raw extracts are immutable; identifiers
must be pseudonymized consistently before entering this repository.

## Required extracts

### `orders.csv`

| Field | Type/unit | Requirement |
|---|---|---|
| `order_id` | string | unique, non-empty pseudonymous key |
| `arrival_at` | timestamp | time order becomes eligible for release |
| `due_at` | timestamp | operational promise/deadline definition documented |
| `release_at` | timestamp | nullable if not observable |
| `pick_start_at` | timestamp | nullable with missingness reason |
| `pick_complete_at` | timestamp | nullable/censored orders retained |
| `shift_id` | string | joins staffing and operating regime |

### `order_lines.csv`

| Field | Type/unit | Requirement |
|---|---|---|
| `order_id` | string | foreign key to orders |
| `sku_id` | string | pseudonymous SKU/location key |
| `quantity` | positive integer | units picked on the line |
| `location_id` | string | joins location master effective at event time |

### `picker_events.csv`

| Field | Type/unit | Requirement |
|---|---|---|
| `picker_id` | string | pseudonymous; used only for heterogeneity/resource checks |
| `trip_id` | string | batch/trip key |
| `event_at` | timestamp | setup/start/pick/complete event time |
| `event_type` | category | controlled event vocabulary |
| `order_id` | string | nullable only for trip-level events |
| `sku_id` | string | nullable except item-pick events |

### `staffing.csv` and `locations.csv`

Staffing records require shift start/end, available picker count, breaks, and
known downtime. Location records require effective dates, aisle/shelf/side,
travel distance or validated topology, cart limits, and layout changes.

## Mandatory extraction report

Record data owner, source system/query version, extraction timestamp, observation
period, timezone/DST handling, row counts, duplicate keys, missingness by field,
cancelled/returned order policy, outlier rule, unit conversion, confidentiality,
redistribution rights, and checksum of every raw extract.

## Leakage-resistant split

Choose calibration and held-out validation periods chronologically before model
comparison. Seasonal regimes and layout/staffing changes must be represented or
declared outside the validity domain. The held-out split must not influence
distribution family, cleaning thresholds, tolerances, factor levels, or MPID.

Derived long-form input data for `src.input_analysis` use columns `parameter`,
`value`, and `split`. KPI comparisons for `src.validation` use `split`, `metric`,
`observed`, and `simulated`.
