# WP10 Report: Figures, Tables, Reconciliation, and Supplement Split

- **Status**: DONE
- **Tasks Addressed**:
  1. **Figure 5 vs Figure 9 Reconciliation**:
     - **Cause identified**: Figure 5 plotted the raw completed-cohort percentage ($\text{completed\_orders} / N \approx 20\% - 29\%$) under high-load cells, whereas Table 4a / Figure 9 plotted the full-cohort $(1 - \text{TLO}/N)$ which was previously labelled `service level` (54% vs 40%).
     - **Resolution**: Renamed metric unambiguously across all figures, tables, and scripts to **`not-yet-late rate`** ($1 - \text{TLO}/N$) to avoid conflation with true on-time completion rates.
  2. **Table 4b Weights**: Explicitly rendered as fractions ("1/3", "1/3", "1/3") instead of decimal approximations ("0.33").
  3. **Section 3.2 Urgency Formula Typo Fix**:
     - Corrected formula for lead researcher:
       $$t + t_{\text{setup}} + 5 \cdot Q_o + \hat{T}_{\text{travel}}(o) > d_o$$
       (replacing the garbled $1t + 180 + \dots$ rendering).
  4. **Supplement Split for Reviewer 2**:
     - Dispersion figures (Figures 10–13, showing standard deviation and coefficient of variation) are designated for migration to `supplement/Supplementary_Figures_S1-S4.pdf`, retaining a concise cross-reference in the main text.
  5. **Tables Generated**:
     - Table 4a Extended (`results/WP3/table4a_extended.csv`)
     - Table 4d Status Partition (`results/WP3/table4d_status_partition.csv`)
     - Table 7 Timing x Composition (`results/WP4/six_cells.csv`, `simple_effects.csv`)
     - Table 10 Load Stratified (`results/WP9/table10.csv`)
