# Manuscript Claim Checks

## 1. Claim: "MPBH's advantage widens monotonically with arrival rate"
- **Absolute gap (orders)**:
  - lam=0.5: delta = -18.55
  - lam=1.0: delta = -54.55
  - lam=2.0: delta = -203.04
  - lam=4.0: delta = -318.33
  - lam=8.0: delta = -337.56
  - lam=16.0: delta = -348.78
  - Absolute gap widens monotonically with arrival rate: **TRUE**.
- **Relative gap (%)**:
  - lam=0.5: 58.08%
  - lam=1.0: 43.58%
  - lam=2.0: 38.64%
  - lam=4.0: 19.90%
  - lam=8.0: 10.39%
  - lam=16.0: 5.38%
  - Relative gap decreases monotonically with arrival rate: **TRUE**.
- **Overall Verdict**: **PARTIALLY TRUE** (Absolute gap widens, relative percentage shrinks).

## 2. Claim: "Additional pickers allow every policy to clear the order pool before deadlines"
- At lam=0.5: m=3 (MPBH, MaxPicker, SNH), m=5 (FTWB).
- At lam=1.0: m=5 (MPBH), m=6 (MaxPicker, SNH, MaxCart).
- At lam=2.0: m=9 (MPBH), m=11 (MaxPicker, SNH, MaxCart).
- At lam >= 4.0: **NO POLICY** clears the order pool even with 12 pickers.
- **Overall Verdict**: **FALSE** (Additional pickers clear the pool only for lam <= 2.0; at lam >= 4.0, capacity is structurally deficient).

## 3. Claim: "Low-rate / 12-picker four-way zero-TLO tie"
- At lam=0.5 and m=12: FTWB, VTWB, MaxPicker, and MPBH all achieve mean TLO = 0.00 across all 30 replications: **TRUE**.
