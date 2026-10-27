# Appendix A: Algorithmic Specifications and Mathematical Formulations

This document provides exact, code-accurate specifications for all batching policies, release triggers, and queue-management procedures implemented in the simulation engine. Every step references the authoritative implementation in `src/trigger_method.py` and `src/io_pool.py`, and maps directly to a deterministic unit test in `tests/test_core.py` and `tests/test_reviewer_revision.py`.

---

## 1. Common Queue Management and Dispatch Mechanisms

### 1.1 Slot Reservation Mechanism
* **Implementation**: [`src/io_pool.py:236-239`](file:///d:/Apps/S3/src/io_pool.py#L236-L239)
* **Mathematical Definition**:
  $$\text{ReleaseSlots}(t) = \max\Big(0, (M - |\mathcal{B}_{\text{active}}(t)|) - |\mathcal{B}_{\text{pending}}(t)|\Big)$$
  where $M$ is total pickers (`self.num_pickers`), $\mathcal{B}_{\text{active}}(t)$ is currently assigned batches (`self.assigned_batches`), and $\mathcal{B}_{\text{pending}}(t)$ is queued unassigned batches. A batch cannot be released if $\text{ReleaseSlots}(t) = 0$.
* **Unit Test**: `test_longest_idle_picker_and_release_slot_reservation` in [`tests/test_core.py`](file:///d:/Apps/S3/tests/test_core.py).

### 1.2 Picker Assignment & Tie-Breaking (Longest-Idle-First)
* **Implementation**: [`src/io_pool.py:125-137`](file:///d:/Apps/S3/src/io_pool.py#L125-L137)
* **Mathematical Definition**:
  When a picker requests work or a batch is ready, the assignment is granted strictly to:
  $$p^* = \arg\min_{p \in \mathcal{P}_{\text{available}}} \Big(\text{idle\_since}[p],\; \text{ID}(p)\Big)$$
  where ties in idle timestamp are deterministically broken by integer picker index (`Picker1 < Picker2 < ...`).
* **Unit Test**: `test_longest_idle_picker_and_release_slot_reservation` in [`tests/test_core.py`](file:///d:/Apps/S3/tests/test_core.py).

### 1.3 State-Change Waiting Protocol
* **Implementation**: [`src/trigger_method.py:21-34`](file:///d:/Apps/S3/src/trigger_method.py#L21-L34)
* **Logic**: Event-driven generators yield `_wait_for_state_change(env, order_pool, io_pool, timeout)`. The process wakes up upon either:
  1. A new order arrival (`order_pool.wait_for_change()`).
  2. A picker completing a tour or releasing capacity (`io_pool.wait_for_change()`).
  3. An optional timeout corresponding to the earliest time an existing order becomes urgent (`_seconds_to_next_urgency`).
* **Unit Test**: `test_order_pool_contract_and_duplicate_protection` in [`tests/test_core.py`](file:///d:/Apps/S3/tests/test_core.py).

---

## 3. Deterministic Verification & Unit Test Mapping

Every algorithmic specification and queue invariant is covered by direct unit tests in `tests/test_appendix_a_rules.py` (and supplemented by `tests/test_core.py` and `tests/test_reviewer_revision.py`):

| Rule / Requirement | Mathematical Invariant | Direct Unit Test | Test Suite File |
|---|---|---|---|
| **Empty Pool Guard** | $|\mathcal{W}(t)| = 0 \implies \text{batches\_released} = 0, \Delta \text{Slots} = 0$ | `test_empty_pool_guard` | [`tests/test_appendix_a_rules.py`](file:///d:/Apps/S3/tests/test_appendix_a_rules.py) |
| **Slot Reservation Exhaustion** | $r_t = 0 \implies \text{no dispatch}, |\mathcal{W}(t)| \text{ unchanged}$ | `test_release_slot_exhaustion` | [`tests/test_appendix_a_rules.py`](file:///d:/Apps/S3/tests/test_appendix_a_rules.py) |
| **VTWB First-$V$ Subset** | $\mathcal{V}_{\text{first}} = \text{SortByArrival}(\mathcal{W})[:V]$ | `test_vtwb_first_v_subset` | [`tests/test_appendix_a_rules.py`](file:///d:/Apps/S3/tests/test_appendix_a_rules.py) |
| **UrgentPicker All-Idle** | Fires when $M_{\text{avail}} = M$ even if $U(t) < \beta$ | `test_urgent_picker_all_idle_without_urgency` | [`tests/test_appendix_a_rules.py`](file:///d:/Apps/S3/tests/test_appendix_a_rules.py) |
| **UrgentCart Dual Trigger** | Fires if $\sum \text{pieces} \ge C$ OR $U(t) \ge \beta$ | `test_urgent_cart_capacity_only_and_urgency_only` | [`tests/test_appendix_a_rules.py`](file:///d:/Apps/S3/tests/test_appendix_a_rules.py) |
| **SNH 4-Step Hierarchy** | Tests Urgency Dominance, Full Fit, Capacity Fill, Hybrid Fallback | `test_snh_four_step_logic` | [`tests/test_appendix_a_rules.py`](file:///d:/Apps/S3/tests/test_appendix_a_rules.py) |
| **MaxCart Waiting Pieces** | Triggers iff $\sum_{o \in \mathcal{W}(t)} \text{pieces}(o) \ge C$ and $r_t > 0$ | `test_max_cart_pieces_trigger` | [`tests/test_appendix_a_rules.py`](file:///d:/Apps/S3/tests/test_appendix_a_rules.py) |
| **MPBH $\beta=1, 2$ Trimming** | Trims latest order while $\text{PredictedLate}(\mathcal{B}) > \beta$ | `test_mpbh_beta_trimming` | [`tests/test_appendix_a_rules.py`](file:///d:/Apps/S3/tests/test_appendix_a_rules.py) |
| **MPBH 1-Order No-Trim** | Candidate with 1 order $\le C$ is NEVER dropped for $\beta \ge 1$ | `test_property_single_order_never_trimmed` | [`tests/test_appendix_a_rules.py`](file:///d:/Apps/S3/tests/test_appendix_a_rules.py) |


### 2.1 Fixed-Time Window Batching (FTWB)
* **Implementation**: [`src/trigger_method.py:139-148`](file:///d:/Apps/S3/src/trigger_method.py#L139-L148)
* **Trigger**: Periodic timer $t \pmod F = 0$ (`yield env.timeout(time_window)`).
* **Batch Selection**: Sorts all waiting orders by arrival time (`_arrival_key`), greedy capacity fill up to cart capacity $C$.
* **Unit Test**: `test_canonical_policy_guards_and_dispatch_errors` in [`tests/test_reviewer_revision.py`](file:///d:/Apps/S3/tests/test_reviewer_revision.py).

### 2.2 Variable-Time Window Batching (VTWB)
* **Implementation**: [`src/trigger_method.py:151-158`](file:///d:/Apps/S3/src/trigger_method.py#L151-L158)
* **Trigger**: Fired when pool size $|\mathcal{W}(t)| \ge V$ and $\text{ReleaseSlots}(t) > 0$.
* **Batch Selection**: Strictly selects the **first-$V$ arrived orders**:
  $$\mathcal{V}_{\text{first}} = \text{SortByArrival}(\mathcal{W}(t))[:V]$$
  and applies greedy capacity fill on this subset up to $C$.
* **Unit Test**: `test_canonical_policy_guards_and_dispatch_errors` in [`tests/test_reviewer_revision.py`](file:///d:/Apps/S3/tests/test_reviewer_revision.py).

### 2.3 MaxPicker
* **Implementation**: [`src/trigger_method.py:161-172`](file:///d:/Apps/S3/src/trigger_method.py#L161-L172)
* **Trigger**: Fired whenever $|\mathcal{W}(t)| > 0$ and $\text{ReleaseSlots}(t) > 0$.
* **Batch Selection**: Greedily fills up to $C$ from all waiting orders sorted by arrival time (or EDT if configured).
* **Unit Test**: `test_canonical_policy_guards_and_dispatch_errors` in [`tests/test_reviewer_revision.py`](file:///d:/Apps/S3/tests/test_reviewer_revision.py).

### 2.4 MaxCart
* **Implementation**: [`src/trigger_method.py:175-189`](file:///d:/Apps/S3/src/trigger_method.py#L175-L189)
* **Trigger**: Fired when **total waiting pieces** $\sum_{o \in \mathcal{W}(t)} \text{pieces}(o) \ge C$ and $\text{ReleaseSlots}(t) > 0$.
* **Batch Selection**: Greedy capacity fill of waiting orders sorted by arrival time up to $C$.
* **Unit Test**: `test_batching_respects_capacity_and_edt` in [`tests/test_core.py`](file:///d:/Apps/S3/tests/test_core.py).

### 2.5 UrgentPicker
* **Implementation**: [`src/trigger_method.py:192-231`](file:///d:/Apps/S3/src/trigger_method.py#L192-L231)
* **Trigger**: Fired when $\text{ReleaseSlots}(t) > 0$ AND:
  $$\Big(U(t) \ge \beta\Big) \quad\mathbf{OR}\quad \Big(\text{available\_pickers}(t) == M\Big)$$
  where $U(t)$ is count of urgent orders ($d_o - t \le \text{estimated\_travel}(o)$) and all pickers are completely idle.
* **Unit Test**: `test_paper_canonical_urgency_is_single_order_and_strict` in [`tests/test_reviewer_revision.py`](file:///d:/Apps/S3/tests/test_reviewer_revision.py).

### 2.6 UrgentCart
* **Implementation**: [`src/trigger_method.py:233-271`](file:///d:/Apps/S3/src/trigger_method.py#L233-L271)
* **Trigger**: Fired when $\text{ReleaseSlots}(t) > 0$ AND:
  $$\Big(U(t) \ge \beta\Big) \quad\mathbf{OR}\quad \Big(\sum_{o \in \mathcal{W}(t)} \text{pieces}(o) \ge C\Big)$$
* **Unit Test**: `test_paper_canonical_urgency_is_single_order_and_strict` in [`tests/test_reviewer_revision.py`](file:///d:/Apps/S3/tests/test_reviewer_revision.py).

### 2.7 SNH (Sequential Nearest Heuristic)
* **Implementation**: [`src/trigger_method.py:273-347`](file:///d:/Apps/S3/src/trigger_method.py#L273-L347)
* **Trigger**: Immediate release whenever $\text{ReleaseSlots}(t) > 0$ and $|\mathcal{W}(t)| > 0$.
* **Four-Step Composition Algorithm**:
  1. *Urgency Dominance*: If $U(t) \ge \beta$, return greedy capacity fill of urgent orders sorted by EDT.
  2. *Full Urgency Fit*: If all waiting orders fit in one cart ($\sum \text{pieces} \le C$), return entire pool sorted by EDT.
  3. *Capacity Fill*: Greedy capacity fill on pool sorted by $(-\text{pieces}, \text{EDT})$.
  4. *Hybrid Fallback*: Capacity fill sorted by $(\text{is\_not\_urgent}, \text{due\_time}, -\text{pieces}, \text{arrival})$.
* **Unit Test**: `test_snh_and_mpbh_return_capacity_feasible_deterministic_batches` in [`tests/test_reviewer_revision.py`](file:///d:/Apps/S3/tests/test_reviewer_revision.py).

### 2.8 MPBH (Multi-Picker Batching Heuristic)
* **Implementation**: [`src/trigger_method.py:360-418`](file:///d:/Apps/S3/src/trigger_method.py#L360-L418)
* **Trigger**: State-adaptive immediate release whenever $\text{ReleaseSlots}(t) > 0$ and $|\mathcal{W}(t)| > 0$.
* **Composition Algorithm (Greedy Knapsack with Surrogate Urgency Bound)**:
  1. Initialize candidate batch $\mathcal{B} \leftarrow \emptyset$.
  2. Iterate through orders $o \in \mathcal{W}(t)$ sorted by EDT:
     $$\mathcal{B} \leftarrow \mathcal{B} \cup \{o\}$$
     While $\sum_{i \in \mathcal{B}} \text{pieces}(i) > C$ OR $\text{PredictedLate}(\mathcal{B}) > \beta$:
     $$\text{latest} = \arg\max_{i \in \mathcal{B}} \text{EDT}(i)$$
     $$\mathcal{B} \leftarrow \mathcal{B} \setminus \{\text{latest}\}$$
  3. *Deadlock-Free Fallback*: If $\mathcal{B} \neq \emptyset$, dispatch $\mathcal{B}$. If $\mathcal{B} == \emptyset$ (every order would be predicted late under extreme congestion), dispatch the single earliest-due capacity-feasible order:
     $$\mathcal{B}_{\text{fallback}} = \text{CapacityFill}(\text{SortByEDT}(\mathcal{W}(t)), C)[:1]$$
* **Unit Test**: `test_snh_and_mpbh_return_capacity_feasible_deterministic_batches` in [`tests/test_reviewer_revision.py`](file:///d:/Apps/S3/tests/test_reviewer_revision.py).
