# Table 3a. Dynamic Variables and Outcomes

| Symbol | Definition | Unit/type |
|---|---|---|
| `t` | Current event time | s |
| `S_t=(O_t,B_t,P_t,t)` | Simulation state | tuple |
| `O_t` | Generated orders not yet released to a batch | set |
| `B_t` | Pending, assigned, or completed batches/tours | set |
| `P_t` | Picker states, including idle/busy and idle-since time | set |
| `r_t` | Available release slots: idle pickers minus pending batches | picker slots |
| `a_i,d_i,s_i,c_i` | Arrival, due, picking-start, and completion time of order `i`; `s_i,c_i` may be null at the horizon | s |
| `L_i` | Number of distinct SKU lines in order `i` | integer, 1-10 |
| `q_ij` | Pieces requested for line `j` of order `i` | integer, 1-10 |
| `Q_i=sum_j q_ij` | Total pieces in order `i` | integer, 1-100 |
| `N` | Measurement-cohort orders with `a_i >= W` and `a_i < H` | orders |
| `TLO` | Completed-late orders plus overdue outstanding orders at `H` | orders |
| `Theta` | Measurement-cohort completed orders divided by eight hours | orders/h |
| `U` | Mean picker busy-time overlap with the measurement window divided by available picker time | % |
| `C_score` | Matched-block composite score; higher is better | [0,1] |
| `B_temp` | Temporary capacity-feasible MPBH candidate batch | ordered set |