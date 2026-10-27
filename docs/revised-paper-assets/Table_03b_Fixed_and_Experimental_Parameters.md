# Table 3b. Fixed and Experimental Parameters

| Symbol/parameter | Definition and value | Unit/type |
|---|---|---|
| `W` | Welch warm-up deletion, 5,460 | s |
| `T` | Measurement duration, 28,800 | s |
| `H=W+T` | Engine stop/censor time, 34,260 | s |
| `lambda` | Arrival-rate levels `{0.5,1,2,4,8,16}` | orders/min |
| `m` | Number of pickers `{1,...,12}` | pickers |
| `C` | Cart capacity `{100,150,200}` | pieces/tour |
| `F` | Canonical FTWB interval, 720 | s |
| `V` | Canonical VTWB threshold, 12 | orders |
| `beta` | Canonical urgency threshold, 2; sensitivity `{1,2,3,4}` | orders |
| `A_i` | Due allowance `DiscreteUniform{30,...,120}` | min |
| `p_pick` | Piece-picking time, 5 | s/piece |
| `t_setup` | Setup time charged once per executed tour, 180 | s/tour |
| `v_walk` | Walking speed, 0.5 | m/s |
| shelf pitch | Longitudinal shelf spacing, 1 | m |
| composition | FCFS or EDT next-fit for non-intrinsic policies | categorical |
| routing | S-shape or Largest Gap | categorical |
| `t_travel_hat(o)` | Cached linear-regression travel estimate for one order | s |
| `w=(0.6,0.3,0.1)` | Baseline composite weights for TLO, throughput, and utilisation | vector |