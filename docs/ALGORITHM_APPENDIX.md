<mark># Appendix A. Complete Algorithm Pseudocode (New in Revision)</mark>

<mark>**Revision status.** This entire appendix is new supplementary material added for the revised submission. The complete appendix is highlighted for track-change review. It specifies the paper-canonical implementation used by the revised simulation and addresses Reviewer 1, Minor Comment 3.</mark>

<mark>## A.1 Scope, notation, and shared invariants</mark>

<mark>At decision time `t`, `O_t` is the waiting order pool, `C` is cart capacity, and `r_t` is the number of unreserved release slots:</mark>

<mark>`r_t = max(0, available_pickers(t) - pending_unassigned_batches(t))`.</mark>

<mark>A release slot is reserved atomically by `ADD_BATCH`; therefore a policy may release at most `r_t` batches in one cycle. `P_t` denotes currently available pickers and `N` denotes the configured total number of pickers. An order has quantity `Q_o = Total Item`, due time `d_o`, creation time `a_o`, and identifier `id_o`.</mark>

<mark>Canonical parameters are `F = 720 s` (FTWB), `V = 12 orders` (VTWB), `beta = 2 orders` (urgency threshold), `C in {100, 150, 200}` pieces, and `SetupTime = 180 s`. The simulation horizon is `28,800 s` with a `5,460 s` warm-up. `beta = 2` is the canonical baseline, not a claim of universal optimality.</mark>

<mark>**Capacity invariant.** Every input order must satisfy `0 < Q_o <= C`. A policy never emits an empty batch or a batch whose total quantity exceeds `C`. An oversized order is a configuration/data error and is rejected by the batching layer; it is not silently dropped.</mark>

<mark>**Deterministic keys.** Use `FCFS_KEY(o) = (a_o, id_o)` and `EDT_KEY(o) = (d_o, a_o, id_o)`, ascending. For equal quantities in a capacity ranking, use `EDT_KEY`. For equal picker idle times, use numeric picker suffix (`Picker1` before `Picker2`, etc.).</mark>

<mark>**Urgency.** With routing policy `R`, `ProcessingTime(o) = BasePickTime * Q_o + TravelSurrogate(o, R)` and `BasePickTime = 5 s`. An order is urgent exactly when:</mark>

<mark>`URGENT(o, t) := t + SetupTime + ProcessingTime(o) > d_o`.</mark>

<mark>The urgency calculation is an O(1) prediction per order; `urgent_count(t)` is the count over `O_t`. Equality with the due time is not urgent.</mark>

<mark>## A.2 Shared subroutines</mark>

<mark>```text
function RELEASE_SLOTS(io_pool):
    return max(0, io_pool.available_pickers()
                  - io_pool.pending_unassigned_batches())

function SORT_FOR_COMPOSITION(orders, batching_rule):
    if batching_rule == FCFS:
        return sort(orders, by=(created_time, order_id))
    if batching_rule == EDT:
        return sort(orders, by=(due_time, created_time, order_id))
    raise invalid batching rule

function NEXT_FIT(ordered_orders, C):
    batches = []
    current = []
    used = 0
    for o in ordered_orders:
        require 0 < Q_o <= C
        if used + Q_o <= C:
            append o to current
            used = used + Q_o
        else:
            if current is not empty:
                append current to batches
            current = [o]
            used = Q_o
    if current is not empty:
        append current to batches
    return batches

function RELEASE_NEXT_FIT(io_pool, order_pool, eligible, C, batching_rule, reason):
    slots = RELEASE_SLOTS(io_pool)       # reserve before release
    if slots == 0 or eligible is empty:
        return 0
    ordered = SORT_FOR_COMPOSITION(eligible, batching_rule)
    candidate_batches = NEXT_FIT(ordered, C)
    batches = first min(slots, length(candidate_batches)) batches
    released_ids = empty set
    for batch in batches:
        require batch is not empty
        require sum(Q_o for o in batch) <= C
        io_pool.add_batch(batch, release_reason=reason)
        add every id_o in batch to released_ids
    order_pool.remove_orders(released_ids) # atomic with cycle bookkeeping
    return length(batches)

function WAIT_FOR_EVENT_OR_URGENCY(env, order_pool, io_pool, next_due):
    wait for the next order arrival, picker/batch state change,
    or (when next_due exists) the first strict-urgency transition
```</mark>

<mark>`RELEASE_NEXT_FIT` is the shared event-cycle operation for the six policies whose composition is FCFS/EDT. Its release predicate is evaluated before composition, and the trigger is not re-applied inside the active cycle. A cycle terminates when `O_t` has no eligible orders or `RELEASE_SLOTS(io_pool) == 0`.</mark>

<mark>Picker assignment is performed by the simulation dispatcher after release:</mark>

<mark>```text
function ASSIGN_PENDING_BATCH(picker_id, io_pool):
    if picker_id already has a batch or no pending batch exists:
        return NONE
    available = all pickers without an assigned batch
    longest_idle = argmin(available,
                          by=(idle_since, numeric_picker_suffix))
    if picker_id != longest_idle:
        return NONE
    batch = earliest pending batch by (release_timestamp, batch_id)
    assign batch to picker_id
    stamp Picker ID and picking start time on every order in batch
    return batch
```</mark>

<mark>This rule is deterministic and prevents two picker processes from claiming the same batch. After completion, the picker becomes available and emits a state-change event; a waiting policy may then begin a new cycle.</mark>

<mark>## A.3 FTWB: Fixed Time Window Batching</mark>

<mark>```text
algorithm FTWB(env, order_pool, io_pool, C, F, batching_rule):
    # Decision predicate: O(1), excluding composition.
    repeat until simulation horizon:
        wait until the next fixed epoch t where t mod F == 0
        if order_pool is not empty and RELEASE_SLOTS(io_pool) > 0:
            eligible = all orders in O_t
            RELEASE_NEXT_FIT(io_pool, order_pool, eligible,
                             C, batching_rule, "FTWB")
        # The cycle ends when the pool is empty or no slot remains.
```</mark>

<mark>With the canonical configuration, `F = 720 s`. The fixed epoch is the only eligibility condition; FTWB does not inspect urgency, cart fill, or picker-idleness beyond the required unreserved slot.</mark>

<mark>## A.4 VTWB: Variable Time Window Batching</mark>

<mark>```text
algorithm VTWB(env, order_pool, io_pool, C, V, batching_rule):
    # Decision predicate: O(1), excluding composition.
    repeat until simulation horizon:
        if count(O_t) >= V and RELEASE_SLOTS(io_pool) > 0:
            eligible = first V orders in sort(O_t, by=(created_time, order_id))
            RELEASE_NEXT_FIT(io_pool, order_pool, eligible,
                             C, batching_rule, "VTWB")
        wait for the next arrival or picker/batch state-change event
```</mark>

<mark>With `V = 12`, the first twelve orders are fixed before composition. Orders after that deterministic prefix cannot enter this cycle. The condition is checked again only after an event, and the cycle terminates on an empty eligible prefix or zero release slots.</mark>

<mark>## A.5 MaxPicker: picker-availability release</mark>

<mark>```text
algorithm MaxPicker(env, order_pool, io_pool, C, batching_rule):
    # Release predicate: O(1), excluding composition.
    repeat until simulation horizon:
        if O_t is not empty and RELEASE_SLOTS(io_pool) > 0:
            RELEASE_NEXT_FIT(io_pool, order_pool, all orders in O_t,
                             C, batching_rule, "MaxPicker")
        wait for the next arrival or picker/batch state-change event
```</mark>

<mark>MaxPicker releases immediately whenever at least one unreserved picker slot and one waiting order exist. It does not use `N` as a separate trigger input; `r_t` is the controlling availability quantity.</mark>

<mark>## A.6 MaxCart: cart-fill release</mark>

<mark>```text
algorithm MaxCart(env, order_pool, io_pool, C, batching_rule):
    # Release predicate: O(n), because waiting quantity is summed.
    repeat until simulation horizon:
        waiting_quantity = sum(Q_o for o in O_t)
        if waiting_quantity >= C and RELEASE_SLOTS(io_pool) > 0:
            RELEASE_NEXT_FIT(io_pool, order_pool, all orders in O_t,
                             C, batching_rule, "MaxCart")
        wait for the next arrival or picker/batch state-change event
```</mark>

<mark>Both capacity and release-slot eligibility are required. A full cart without an unreserved slot does not release or reserve work.</mark>

<mark>## A.7 UrgentPicker: urgency-or-all-idle release</mark>

<mark>```text
algorithm UrgentPicker(env, order_pool, io_pool, C, beta, N, batching_rule, R):
    # Urgency scan: O(n), excluding composition.
    repeat until simulation horizon:
        if O_t is not empty and RELEASE_SLOTS(io_pool) > 0:
            urgent_count = count(o in O_t where URGENT(o, t))
            all_idle = io_pool.available_pickers() == N
            if urgent_count >= beta or all_idle:
                RELEASE_NEXT_FIT(io_pool, order_pool, all orders in O_t,
                                 C, batching_rule, "UrgentPicker")
        next_due = earliest time at which any remaining order becomes urgent
        wait for arrival, picker/batch state change, or next_due
```</mark>

<mark>The OR condition is evaluated only after the pool and release-slot guards. The canonical threshold is `beta = 2`. If no order is waiting, no cycle opens; if no slot is available, urgency cannot reserve a batch.</mark>

<mark>## A.8 UrgentCart: urgency-or-cart-fill release</mark>

<mark>```text
algorithm UrgentCart(env, order_pool, io_pool, C, beta, batching_rule, R):
    # Urgency scan is O(n); quantity scan is O(n), excluding composition.
    repeat until simulation horizon:
        if O_t is not empty and RELEASE_SLOTS(io_pool) > 0:
            urgent_count = count(o in O_t where URGENT(o, t))
            capacity_ready = sum(Q_o for o in O_t) >= C
            if urgent_count >= beta or capacity_ready:
                RELEASE_NEXT_FIT(io_pool, order_pool, all orders in O_t,
                                 C, batching_rule, "UrgentCart")
        next_due = earliest time at which any remaining order becomes urgent
        wait for arrival, picker/batch state change, or next_due
```</mark>

<mark>The OR branches are intentional: urgency is not forced to wait for a full cart, and a full waiting cart can release even when fewer than `beta` orders are urgent. The release-slot guard remains mandatory.</mark>

<mark>## A.9 SNH: Simplified Neighbourhood-based Heuristic</mark>

<mark>SNH is a deterministic rule-based priority fallback inspired by neighbourhood-search concepts; it does not perform iterative neighbourhood search or claim local optimality. It builds one intrinsic batch per available release slot.</mark>

<mark>```text
function SNH_BATCH(t, O_t, C, beta, R):
    if O_t is empty:
        return EMPTY
    urgent = [o in sort(O_t, by=EDT_KEY) where URGENT(o, t)]

    # 1. Urgency option: preserve EDT tie-breaking and fill capacity.
    if length(urgent) >= beta:
        return CAPACITY_FILL(urgent, C, skip_non_fitting=true)

    # 2. Full urgency-order option.
    urgency_order = sort(O_t, by=EDT_KEY)
    if sum(Q_o for o in urgency_order) <= C:
        return urgency_order

    # 3. Capacity option: largest pieces first, then EDT ties.
    capacity_order = sort(O_t, by=(-Q_o, d_o, a_o, id_o))
    capacity_batch = CAPACITY_FILL(capacity_order, C, skip_non_fitting=true)
    if capacity_batch is not empty:
        return capacity_batch

    # 4. Hybrid fallback: urgent first, then due, pieces, arrival, ID.
    hybrid_order = sort(O_t, by=(not URGENT(o,t), d_o, -Q_o, a_o, id_o))
    return CAPACITY_FILL(hybrid_order, C, skip_non_fitting=true)

algorithm SNH(env, order_pool, io_pool, C, beta, R):
    # O(n log n) algorithmic bound from deterministic sorting.
    repeat until simulation horizon:
        while O_t is not empty and RELEASE_SLOTS(io_pool) > 0:
            batch = SNH_BATCH(t, O_t, C, beta, R)
            if batch is empty:
                break                       # no feasible batch; await state change
            require sum(Q_o for o in batch) <= C
            io_pool.add_batch(batch, release_reason="SNH")
            order_pool.remove_orders(ids(batch))
        wait for the next arrival or picker/batch state-change event
```</mark>

<mark>`CAPACITY_FILL` scans its already ordered list and accepts an order when it fits, skipping a non-fitting order rather than closing the batch. Under the capacity invariant, the fallback returns a non-empty batch whenever `O_t` is non-empty. The explicit empty guard prevents a busy loop if invalid data or a future variant violates that invariant.</mark>

<mark>## A.10 MPBH: Modified Priority-Based Heuristic</mark>

<mark>MPBH uses intrinsic EDT ordering and does not apply the configured FCFS/EDT composition rule. `PredictedLateCount(B,t)` evaluates all members at one common candidate completion time:</mark>

<mark>`candidate_completion = t + SetupTime + ProcessingTime(B, R)` and `PredictedLateCount(B,t) = count(d_o < candidate_completion for o in B)`.</mark>

<mark>The canonical implementation uses the routing-based trip estimate for the candidate batch. The fixed setup parameter is `SetupTime = 180 s`; it is included once in the candidate batch completion estimate, not added separately to every order.</mark>

<mark>```text
function MPBH_BATCH(t, O_t, C, beta, R):
    ordered = sort(O_t, by=EDT_KEY)
    B_temp = empty list

    for o in ordered:
        append o to B_temp
        while B_temp is not empty and
              (sum(Q_x for x in B_temp) > C or
               PredictedLateCount(B_temp, t, R) > beta):
            latest = argmax(B_temp, by=EDT_KEY)
            remove latest from B_temp
            # Recheck both constraints after every restoration removal.

    if B_temp is not empty:
        require sum(Q_o for o in B_temp) <= C
        require PredictedLateCount(B_temp, t, R) <= beta
        return B_temp

    # Deadlock prevention / feasibility restoration.
    individually_feasible = [o in ordered where Q_o <= C]
    if individually_feasible is empty:
        return EMPTY                    # invalid input; caller must not spin
    return [first individually_feasible order]

algorithm MPBH(env, order_pool, io_pool, C, beta, R):
    # O(n log n) algorithmic component from initial EDT sorting.
    repeat until simulation horizon:
        while O_t is not empty and RELEASE_SLOTS(io_pool) > 0:
            batch = MPBH_BATCH(t, O_t, C, beta, R)
            if batch is empty:
                break                       # invalid/unsatisfiable input
            io_pool.add_batch(batch, release_reason="MPBH")
            order_pool.remove_orders(ids(batch))
        wait for the next arrival or picker/batch state-change event
```</mark>

<mark>After every tentative addition, MPBH restores feasibility by removing the latest due order and then rechecking capacity and predicted lateness. If pruning removes every candidate, the earliest individually capacity-feasible order is dispatched. This explicit restoration branch prevents an urgent/overdue pool from deadlocking the simulation; an all-oversized pool is a data error and is terminated rather than retried indefinitely.</mark>

<mark>## A.11 Verification matrix and edge-case checks</mark>

<mark>The following checks are the acceptance criteria for this appendix. The unit tests in `tests/test_reviewer_revision.py` and related tests exercise the deterministic implementations; the same invariants apply to all eight blocks.</mark>

<mark>| Policy | Event eligibility | Slot reservation | Sort / composition | Capacity and termination | Special rule |
|---|---|---|---|---|---|
| FTWB | fixed epoch, non-empty pool | `r_t > 0` | FCFS/EDT next-fit | at most `r_t`; stop on empty pool or zero slots | `F=720 s` |
| VTWB | `|O_t| >= V` | `r_t > 0` | first `V` by `(arrival, ID)`, then FCFS/EDT next-fit | same cycle stop | `V=12` |
| MaxPicker | pool non-empty | `r_t > 0` | FCFS/EDT next-fit | same cycle stop | immediate availability |
| MaxCart | waiting pieces `>= C` | `r_t > 0` | FCFS/EDT next-fit | same cycle stop | O(n) quantity scan |
| UrgentPicker | urgent count `>= beta` OR all idle | `r_t > 0` | FCFS/EDT next-fit | same cycle stop | `beta=2`, O(n) urgency |
| UrgentCart | urgent count `>= beta` OR pieces `>= C` | `r_t > 0` | FCFS/EDT next-fit | same cycle stop | both OR branches explicit |
| SNH | pool non-empty and slot available | one slot per intrinsic batch | urgency, full-fit, capacity, hybrid | non-empty capacity-safe batch; break on no feasible batch | deterministic fallback |
| MPBH | pool non-empty and slot available | one slot per intrinsic batch | EDT, incremental append | restore constraints; fallback prevents deadlock | `beta=2`, capacity + lateness |
|</mark>

<mark>Minimum edge cases to verify manually or in unit tests are: empty pool; zero release slots with waiting orders; exactly-on-time urgency (not urgent); exactly `beta` urgent orders; exactly `C` pieces; an order that exactly fills `C`; FCFS and EDT ties resolved by arrival then ID; multiple available pickers with equal idle timestamps; more composed batches than available slots; MPBH pruning that removes the latest due order; and an MPBH candidate that becomes empty and must dispatch the earliest individually feasible order.</mark>

<mark>## A.12 Audit crosswalk</mark>

<mark>This appendix is intended to be audited against revised manuscript Section 4.1-4.4 and Reviewer 1 Minor Comment 3 as follows:</mark>

<mark>- Section 4.1: FTWB/VTWB predicates, `F=720`, `V=12`, deterministic prefix for VTWB, and FCFS/EDT next-fit.
- Section 4.2: MaxPicker and MaxCart resource predicates, release slots, and quantity scan.
- Section 4.3: UrgentPicker/UrgentCart urgency definition, `beta=2`, strict lateness test, and OR branches.
- Section 4.4: SNH's four ordered options and MPBH's EDT append, capacity check, predicted-late check, latest-due restoration, and deadlock fallback.
- Shared Section 3.3 rules: event-driven wake-up, reserved-slot bound, longest-idle picker assignment, deterministic tie-breaking, atomic order removal, and termination.

<mark>Complexity labels describe algorithmic bounds of the decision kernels and exclude the cost of the simulation event scheduler. Empirical latency fits are reported separately in the revised results; they do not replace these bounds.</mark>
