# WP7 MPBH & SNH Code Audit Questionnaire

This document answers the eight audit questions from Reviewer 1 (R1-C4) with explicit file and line references from the frozen code.

---

### 1. MPBH Completion-Time Estimate & Travel Surrogate
- **Formula**:
  $$\hat{C}(B) = t_{\text{current}} + \hat{T}_{\text{trip}}(B) = t_{\text{current}} + t_{\text{setup}} + 5 \cdot \sum_{o \in B} Q_o + \hat{T}_{\text{travel}}(B)$$
  ([`src/trigger_method.py:356`](file:///d:/Apps/S3/src/trigger_method.py#L356), [`src/travel_surrogate.py:55-64`](file:///d:/Apps/S3/src/travel_surrogate.py#L55-L64)).
- **Batch Travel Calculation $\hat{T}_{\text{travel}}(B)$**:
  Calculated across the entire temporary candidate batch $B$ using union features across all orders:
  $\mathbf{x}(B) = [1, \text{distinct lines}, \text{total pieces}, \max(\text{aisles}), \text{distinct aisles}]$ ([`src/travel_surrogate.py:16-33`](file:///d:/Apps/S3/src/travel_surrogate.py#L16-L33)).
  The calibrated O(1) linear surrogate regression coefficients are used, **not** exact routing and **not** sum of single-order tours.
- **Timestamp $t$**:
  Uses `env.now` (the current simulation time at the moment a picker slot is free) ([`src/trigger_method.py:356`](file:///d:/Apps/S3/src/trigger_method.py#L356)).

---

### 2. Candidate Construction
- **Mechanism**:
  Candidate batch $B_{\text{temp}}$ is built **incrementally** inside a forward scan over the waiting pool sorted by Earliest Due Time ($\text{EDT}$, key: `(due_seconds, arrival_seconds, order_id)`) ([`src/trigger_method.py:369-370`](file:///d:/Apps/S3/src/trigger_method.py#L369-L370)).
- **Termination & Re-consideration**:
  The scan traverses all waiting orders. An order appended that causes capacity or predicted-late violations triggers trimming of the latest-due order in $B_{\text{temp}}$. If the trimmed order was the newly appended order, the loop advances to the next order in the pool ([`src/trigger_method.py:371-379`](file:///d:/Apps/S3/src/trigger_method.py#L371-L379)).

---

### 3. Removal Loop
- **Removal Target**:
  When $\sum Q_i > C$ or $\sum \mathbb{I}\{\hat{C}(B) > d_i\} > \beta$, the order removed is:
  $$\text{latest} = \arg\max_{o \in B_{\text{temp}}} \text{EDT}(o)$$
  ([`src/trigger_method.py:375-376`](file:///d:/Apps/S3/src/trigger_method.py#L375-L376)).
- **Boundedness**:
  The `while` loop is strictly bounded by the size of $B_{\text{temp}}$, terminating when constraints are restored or the candidate is emptied.

---

### 4. Definition of "Individually Feasible"
- Defined by cart capacity: an order is individually feasible if its piece count $Q_i \le C$ ([`src/trigger_method.py:384`](file:///d:/Apps/S3/src/trigger_method.py#L384)). Because every order has at most 10 items $\times$ 10 pieces = 100 pieces and $C \in \{100, 150, 200\}$, **every order is individually capacity-feasible**.

---

### 5. Fallback Mechanism
- **Trigger Condition**:
  Fires if and only if $B_{\text{temp}}$ is completely empty after scanning the entire waiting pool (`if not temporary: return _capacity_fill(...)[:1]`) ([`src/trigger_method.py:380-384`](file:///d:/Apps/S3/src/trigger_method.py#L380-L384)).
- **Reachability**:
  Occurs under severe congestion when every waiting order in the pool has $d_i < t_{\text{current}} + \hat{T}_{\text{trip}}(\{o\})$, meaning even single-order tours are predicted to be late. The fallback prevents simulation deadlock by releasing the earliest due order as a single-order tour.

---

### 6. Roles of $\beta$ Across Policies
- **MPBH**: Maximum allowed orders predicted late within the candidate batch ($\le \beta$) ([`src/trigger_method.py:373`](file:///d:/Apps/S3/src/trigger_method.py#L373)).
- **SNH**: Threshold count of urgent orders required to trigger the urgent-batching branch ([`src/trigger_method.py:314`](file:///d:/Apps/S3/src/trigger_method.py#L314)).
- **UrgentPicker / UrgentCart**: Minimum urgent orders present in the pool required to trigger an immediate cycle before cart capacity or picker thresholds are reached ([`src/trigger_method.py:236-248`](file:///d:/Apps/S3/src/trigger_method.py#L236-L248)).

---

### 7. Release-Slot & Non-Empty Guarantees
- **Non-empty Batch**: Ensured by checking `if not batch: break` before calling `io_pool.add_batch` ([`src/trigger_method.py:413-415`](file:///d:/Apps/S3/src/trigger_method.py#L413-L415)).
- **Release Slots**: Ensured by the condition `io_pool.get_release_slots() > 0` before constructing or releasing a batch ([`src/trigger_method.py:404`](file:///d:/Apps/S3/src/trigger_method.py#L404)).

---

### 8. Liu (2016) Citation
- Mentioned in conceptual design docstrings as inspiration for priority-based heuristic batching. However, MPBH replaces static heuristic weightings with explicit state-dependent linear surrogate feasibility estimation and dynamic backward trimming.
