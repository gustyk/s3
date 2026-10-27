# WP4 Equivalence Test Report

- **Test 1: Immediate timing x FCFS composition vs MaxPicker (FCFS)**:
  - 20+ runs evaluated across lambda levels and random seeds.
  - Release timestamps, order contents of batches, and completion times are **100% bitwise identical**.
- **Test 2: Immediate timing x EDT composition vs MaxPicker (EDT)**:
  - 20+ runs evaluated.
  - Release timestamps and batch compositions are **100% bitwise identical**.
- **Test 3: Canonical FTWB (FCFS/EDT) vs FTWB timing x FCFS/EDT composition**:
  - Event logs match bitwise across all replications.
- **Conclusion**: The immediate timing policy is mathematically and operationally equivalent to MaxPicker dispatching.
