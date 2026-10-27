# Data Dictionary: S3 Discrete-Event Simulation Datasets

This document describes the schema and conventions for the per-order, per-run aggregate, and scenario configuration datasets.

## 1. Per-Run Aggregate Table (`results.csv`)

| Column Name | Type | Unit | Description |
|---|---|---|---|
| `run_uuid` | string (UUID) | - | Unique identifier for each simulation run |
| `run_id` | integer | - | Sequential run ID in the execution queue |
| `repetition` | integer | - | Replicaton index (1 to 30) |
| `seed` | uint64 | - | 64-bit seed generated from master seed, arrival key, replication |
| `status` | string | - | Execution status (`success`, `failed`) |
| `wall_seconds` | float | s | Wall-clock execution time of the simulation run |
| `incoming_rate` | float | orders/min | Parameter $\lambda \in \{0.5, 1.0, 2.0, 4.0, 8.0, 16.0\}$ |
| `cart_capacity` | integer | items | Cart capacity $C \in \{100, 150, 200\}$ |
| `trigger_method` | string | - | Batch release policy name |
| `batching_method` | string | - | Batch composition rule (`FCFS`, `EDT`) |
| `routing_policy` | string | - | Picking route policy (`S-shape` / `Traversal`, `Largest Gap`) |
| `num_pickers` | integer | - | Staffing level $m \in \{1, \dots, 12\}$ |
| `total_late_orders` | integer | orders | **TLO**: Total Late Orders in measurement cohort (completed late + outstanding overdue) |
| `throughput_per_hour` | float | orders/h | Completed cohort orders per observation hour |
| `service_level_percent` | float | % | Not-yet-late rate: $(1 - \text{TLO}/N) \times 100\%$ |
| `picker_utility_percent` | float | % | Average picker utilization across pickers |
| `trip_count` | integer | trips | Total picking trips/batches completed during measurement window |
| `warmup_seconds` | float | s | Warm-up cutoff $W = 5,460$ s |
| `observation_end_seconds` | float | s | Fixed shift horizon $H = 34,260$ s |

## 2. Per-Order Records (`orders.csv.gz` / parquet)

| Column Name | Type | Unit | Description |
|---|---|---|---|
| `run_uuid` | string | - | Foreign key to `results.csv` |
| `order_id` | integer | - | Customer order sequence number within run |
| `measurement_eligible`| boolean | - | True if $W \le \text{arrival\_seconds} < H$ |
| `arrival_seconds` | float | s | Exact arrival timestamp |
| `due_seconds` | float | s | Exogenous deadline $d_i \in [\text{arrival} + 1800, \text{arrival} + 7200]$ |
| `total_pieces` | integer | pieces | Total items/pieces in order |
| `line_count` | integer | lines | Distinct SKU lines |
| `batch_id` | string | - | Identifier of assigned batch |
| `picker_id` | string | - | Assigned picker |
| `start_seconds` | float / null | s | Timestamp picking commenced |
| `completion_seconds`| float / null | s | Timestamp picking completed at depot |
| `horizon_state` | string | - | Status at $H$: `completed_ontime`, `completed_late`, `outstanding_overdue`, `outstanding_notdue` |
| `late_completed` | boolean | - | True if completed and completion > due |
| `overdue_outstanding`| boolean | - | True if unfinished at $H$ and due < $H$ |
| `tardiness_seconds` | float / null | s | $\max(0, \text{completion} - \text{due})$ for completed orders |

> [!NOTE]
> **Survivorship bias warning**: Mean tardiness calculated solely on completed orders rewards policies that finish fewer orders under heavy congestion. Robust evaluations must use censored/resolved metrics or the all-order lower bound.
