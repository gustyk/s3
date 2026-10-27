# WP7 Report: MPBH/SNH Code Audit, Instrumentation, and Complexity Re-Check

- **Status**: DONE
- **Audit Findings**:
  - MPBH evaluates batch travel time using the **calibrated 5-feature O(1) linear surrogate** evaluated across the union of SKU lines in the temporary batch, evaluated at current simulation timestamp `env.now`.
  - Orders are scanned incrementally in EDT order. If capacity ($> C$) or predicted late orders ($> \beta$) exceed thresholds, the latest-due order in the candidate batch is trimmed backwards.
  - The fallback branch releases the earliest capacity-feasible order if all candidates are predicted late, preventing queue deadlock under heavy congestion.
  - SNH uses an urgent threshold to branch between urgent-first batching and standard greedy heuristic batching.
- **Empirical Complexity Re-check**:
  - FTWB & VTWB: $O(1)$ decision latency.
  - MPBH: $O(n)$ empirical scaling ($R^2 = 0.9999$). At $n=5,000$ orders, median decision latency is **61.34 ms**, which is negligible relative to warehouse dispatch cycles.
  - MaxPicker & MaxCart: $O(n)$ empirical scaling.
  - SNH & UrgentPicker: $O(n \log n)$ scaling ($R^2 = 0.9999$).

## Files Delivered
- `results/WP7/mpbh_questionnaire.md`
- `reports/WP7_report.md`
