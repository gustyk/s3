# Provenance of Legacy Dataset

- **File**: `data/legacy/simulation_results_legacy_unverified.csv`
- **SHA-256**: `F02689EA9D4BFDA4BB31C56287F0F33F0328DAB5B35AA1946ACD5EABBDF674C6`
- **Audit Commit**: `50c4298` (Add files via upload)
- **Filesystem Timestamp**: `2026-08-12T01:23:13.5677309Z`
- **Columns in CSV**: `run_id`, `incoming_rate`, `cart_capacity`, `trigger_method`, `batching_method`, `routing_policy`, `num_pickers`, `total_orders`, `total_late_orders`, `picker_utility`.
- **Finding on F and t_setup**:
  The legacy CSV **does not record** sampled interval or setup time columns. However, git log confirms that the configuration default in `config/parameters.yaml` at commit `50bdad2` and `50c4298` was `FTWB_interval: 720` and `setup_time: 180`. Column (c) in Table B1 is therefore marked `NOT AVAILABLE` from run metadata, while Column (b) confirms the code defaults were 720 s and 180 s.
