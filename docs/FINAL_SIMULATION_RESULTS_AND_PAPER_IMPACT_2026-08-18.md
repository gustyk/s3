# Final simulation results and paper-impact assessment — 2026-08-18

## Executive decision

The corrected simulation is complete and internally auditable, but the accepted
paper cannot be revised by replacing a few numbers.  The corrected model changes
the magnitude and ranking of several core results.  Sections 5–6, the Abstract,
all propositions, Tables 4–6, and the associated figures require substantive
rewriting.

The defensible headline is now:

- MPBH remains the strongest method for deadline performance and is first under
  all four declared composite-weight schemes;
- its reduction in mean TLO against the pooled canonical static benchmarks is
  **10.66%**, not 27.04%;
- most other adaptive rules provide statistically detectable but operationally
  small TLO reductions against the pooled static benchmark;
- the crossed ablation rejects the broad Proposition-4 claim: MPBH composition
  has a much larger effect than MPBH timing in the tested subset;
- no universal winner exists at every factorial cell, although MPBH wins 770 of
  864 scenario cells (89.12%) under the declared service-level/throughput rule.

## Final-data integrity

| Evidence | Final value |
|---|---:|
| Factorial scenarios | 6,912 |
| Replications | 30 |
| Expected/actual runs | 207,360 / 207,360 |
| Successful/failed runs | 207,360 / 0 |
| Raw order records | 621,955,584 |
| Results SHA-256 | `720f2d70f8ee9e6b440ae30b639aa8513a007ec9fc462b7dc1f4710d362b4448` |
| Orders SHA-256 | `328206013610b3fa07723776da2f112ddfa4ab349f6ea0b57b0d351087a3dbf4` |
| Config SHA-256 | `d359bc8f3a2cda65123a640155339ce18092ae8214913fc6561b916ffd42234f` |
| Strict artifact audit | PASS, no errors |

The simulation manifest records `git_dirty=True`.  The results are still tied to
the config and source-tree hashes, but the clean signed-tag criterion remains an
external release-governance blocker and must not be represented as satisfied.
The 621,955,584 raw rows reconcile exactly across the three worker manifests;
522,713,088 rows are measurement-eligible after warm-up and reconcile exactly
to the sum of run-level `generated_orders`.

## Corrected aggregate results

Values below are means across 25,920 runs per trigger method.  TLO and other
run-level metrics are calculated after the 5,460-second Welch warm-up.

| Method | Mean TLO | SD TLO | Mean late ratio | On-time % | Throughput/h | Picker utility % | Mean completed-order tardiness (s) | Corrected composite |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FTWB | 2,023.145 | 2,279.504 | 0.6018 | 39.823 | 30.498 | 66.119 | 6,065.866 | 0.1590 |
| VTWB | 1,981.448 | 2,306.626 | 0.5524 | 44.765 | 41.605 | 84.707 | 4,704.337 | 0.3041 |
| MaxPicker | 1,977.703 | 2,309.668 | 0.5424 | 45.761 | 42.789 | 91.407 | 5,963.244 | 0.4864 |
| MaxCart | 1,978.413 | 2,309.154 | 0.5444 | 45.562 | 42.520 | 85.807 | 5,975.202 | 0.4084 |
| UrgentPicker | 1,998.911 | 2,295.719 | 0.5699 | 43.006 | 40.927 | 84.308 | 6,113.799 | 0.2600 |
| UrgentCart | 1,978.413 | 2,309.154 | 0.5444 | 45.562 | 42.520 | 85.807 | 5,975.202 | 0.4084 |
| SNH | 1,992.058 | 2,301.919 | 0.5579 | 44.208 | 48.236 | 91.385 | 7,068.097 | 0.4999 |
| MPBH | **1,788.830** | **2,193.369** | **0.4601** | **53.990** | **60.969** | 91.393 | **1,393.042** | **0.9920** |

Pareto analysis identifies MPBH and MaxPicker as non-dominated in the global
three-objective summary.  MPBH is first under original, equal, throughput-
priority, and utilisation-priority composite weights.  Composite remains a
secondary descriptive result; Pareto and paired outcome estimates are primary.

### Censoring-aware all-order tardiness

Exact final tardiness is unobservable for orders still outstanding at the fixed
horizon. The raw-order analysis therefore reports a conservative horizon lower
bound over all measurement-eligible orders, rather than imputing completion.

| Method | Mean completed-order tardiness (s) | Mean all-order tardiness lower bound (s) |
|---|---:|---:|
| FTWB | 6,065.866 | 6,211.023 |
| VTWB | 4,704.337 | 5,517.286 |
| MaxPicker | 5,963.244 | 5,465.659 |
| MaxCart | 5,975.202 | 5,469.194 |
| UrgentPicker | 6,113.799 | 5,566.531 |
| UrgentCart | 5,975.202 | 5,469.194 |
| SNH | 7,068.097 | 5,282.469 |
| MPBH | **1,393.042** | **4,877.198** |

The difference between the completed-only mean and the all-order lower bound is
material, especially for MPBH, and must be explained as right-censoring rather
than presented as contradictory estimates.

## Primary paired CRN contrasts

Every contrast uses 25,920 matched seed × scenario blocks.  Negative differences
mean fewer late orders for the adaptive method.

| Method versus mean(FTWB, VTWB) | Mean ΔTLO | 95% CI | Relative reduction |
|---|---:|---:|---:|
| MaxPicker | −24.594 | [−25.442, −23.746] | 1.23% |
| MaxCart | −23.883 | [−24.728, −23.039] | 1.19% |
| UrgentPicker | −3.385 | [−3.947, −2.824] | 0.17% |
| UrgentCart | −23.883 | [−24.728, −23.039] | 1.19% |
| SNH | −10.238 | [−10.952, −9.525] | 0.51% |
| MPBH | **−213.467** | **[−215.733, −211.200]** | **10.66%** |

The extremely small p-values partly reflect the very large balanced design.
Operational importance must be judged against a domain-approved minimum
practically important difference (MPID), which remains externally blocked.

## Reviewer experiments

### Timing versus composition — R1 Major 1 and 4

| Planned contrast | Mean ΔTLO | 95% CI | Conclusion |
|---|---:|---:|---|
| MPBH timing − FTWB timing | −18.119 | [−20.147, −16.090] | MPBH timing improves TLO |
| EDT − FCFS composition | 0.036 | [−0.006, 0.079] | no supported difference |
| MPBH − FCFS composition | −153.005 | [−163.824, −142.186] | MPBH composition improves TLO |
| MPBH − EDT composition | −153.041 | [−163.859, −142.223] | MPBH composition improves TLO |

The MPBH-composition effect is about 8.4 times the MPBH-timing effect.  The
accepted-paper statement that timing is more important than composition is not
supported by this experiment and must be withdrawn, not merely qualified.

### Benchmark calibration — R1 Major 2

Tuning selects FTWB `F=60 s`, VTWB `V=4` for minimum TLO, and VTWB `V=6` for
maximum calibration composite.  On held-out data, canonical-to-tuned TLO changes
are small, while throughput/utilisation and composite change materially.  Report
canonical and tuned evidence separately; do not call `F=720` or `V=12` optimal.

### Beta sensitivity — R1 Major 10 / R2 Major 4

For MPBH, `beta=1` versus `beta=2` reduces TLO by 65.415 orders
([−69.946, −60.885]) but raises mean trips from 174.63 to 212.57 and reduces
mean cart utilisation from 52.93% to 37.96%.  Higher beta worsens TLO while
reducing trips and increasing cart fill.  Beta is therefore an explicit
service-efficiency trade-off, not a universally optimisable constant.

### Computational scaling — R2 Major 3

At pool size 5,000, median isolated decision latency is approximately 61.34 ms
for MPBH, 14.07 ms for SNH, 6.11 ms for UrgentCart, 5.16 ms for UrgentPicker,
0.38 ms for MaxCart, and effectively below 0.01 ms after timer-overhead
adjustment for FTWB, VTWB, and MaxPicker.  Empirical classifications are
practically constant for FTWB/VTWB/MaxPicker, O(n) for MaxCart/MPBH/SNH/
UrgentPicker, and O(n log n) for UrgentCart.

## Proposition disposition

| Proposition | Final disposition | Required wording |
|---|---|---|
| P1 — adaptive timing outperforms static timing | **Partially supported** | MPBH strongly outperforms the canonical static benchmarks; other adaptive rules show only 0.17–1.23% pooled TLO reductions. Avoid saying adaptive rules generally provide a large advantage. |
| P2 — resource-aware rules are more robust | **Partially supported** | MPBH has the lowest absolute TLO SD, but relative variability and scenario winners are context-dependent. No adaptive method is universally robust. |
| P3 — rankings depend on operational context | **Supported with qualification** | MPBH wins 770/864 cells, MaxPicker 59, SNH 31, and MaxCart 4; context still matters, but MPBH is dominant in most cells. |
| P4 — timing has greater impact than composition | **Not supported** | Crossed ablation finds the opposite ordering in the tested subset. State this negative result explicitly. |

## Material differences from the accepted paper

- MPBH mean TLO changes from 829.5 to 1,788.8.
- MPBH throughput changes from 187.2/h to 61.0/h and becomes the highest,
  replacing the old MaxPicker/MaxCart throughput narrative.
- The reported 27.04% MPBH improvement becomes 10.66% against the pooled
  canonical static benchmarks.
- Composite values `0.864` and `0.924` are replaced by one corrected value,
  `0.9920`, under the original weights and matched-block normalisation.
- UrgentCart is no longer the worst method.  It is operationally identical to
  MaxCart in every main-factorial matched block for TLO, throughput, picker
  utility, and trip count; the old “worst-of-both-worlds” explanation must be
  removed.
- The accepted Table-6 values are invalid.  For example, high-rate/high-picker
  mean MPBH TLO is about 5,890.3 when averaging secondary factors, not 558.52.
- Old one-way/multi-factor ANOVA statistics and partial eta-squared values must
  not be retained.  Primary inference is now paired CRN estimation with 95%
  confidence intervals and multiplicity control.

## Manuscript sections requiring replacement

| Manuscript location | Required action |
|---|---|
| Abstract | Replace 27.04%, remove the general timing-over-composition claim, add the ablation result and qualified P1 conclusion. |
| Sections 3.1–3.4 | Insert canonical operational definitions, warm-up/estimand, TLO censoring, additional metrics, CRN pairing, and tuned-versus-canonical protocol. |
| Sections 4.1–4.4 | Replace all trigger pseudocode, SNH terminology, MPBH logic, parameter values, assignment/routing rules, and complexity claims. |
| Table 4 / Section 5.1 | Replace all means/SDs and composite scores; add late ratio, on-time rate, completed tardiness, and the all-order censoring lower bound. |
| Table 5 / Sections 5.2–5.3 | Replace legacy ANOVA with paired estimates and clearly labelled secondary cell-level models; do not use the nonconverged NB model. |
| Table 6 | Recalculate representative contexts and report ties instead of forcing one winner. |
| Section 5.4 | Replace with the 2×3 crossed-ablation result; conclude P4 is not supported. |
| Section 5.5 | Use the proposition-disposition table above. |
| Section 6 | Rewrite interpretation, managerial guidance, limitations, benchmark calibration, computational trade-offs, and external-validity boundaries. |
| Conclusion | Retain MPBH as the strongest tested policy but use 10.66%, not 27.04%, and explicitly report the non-supported P4. |

## Statistical diagnostics and limitations

- The Poisson count model is severely overdispersed (Pearson dispersion
  3,185.9) and is descriptive only.
- The secondary negative-binomial model did not converge and must not support
  inference.
- The throughput OLS uses HC3 covariance; heteroskedasticity remains strong.
- Replication-level paired CRN contrasts are the primary evidence.
- Exact real-world practical importance cannot be certified without the MPID,
  operational data validation, SME review, and independent statistical review.

## Remaining external gates

The local computational evidence and order-level postprocessing are complete;
the derived-artifact certification passes with documented warnings. Submission
still requires owner action for a
signed release/archive, immutable storage, independent clean-machine
reproduction, domain validation, statistical review, and manual manuscript/
response-letter revision.
