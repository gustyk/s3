# Frozen Analysis Plan Template

Status: **DRAFT — not preregistered and not approved**  
Freeze timestamp: pending principal investigator approval.

## Confirmatory questions

1. Estimate trigger-method effects on service level (primary outcome).
2. Estimate effects on throughput and mean tardiness (secondary outcomes).
3. Test whether trigger effects interact with incoming rate, picker count, cart
   capacity, batching, and routing.

## Design

Full factorial design over configured levels. Random stream is blocked by
incoming-rate level and repetition; all policy/resource combinations at the same
arrival level and repetition receive the same generated demand stream. Execution
order should be randomized in the production runner before Gate D.

Repetitions must be selected after a pilot precision/power analysis. Thirty is
only a placeholder. The target is a 95% CI half-width agreed for the primary
service-level contrast and at least 80% power for the minimum practically
important difference (MPID).

The first engineering pilot used a 600-second horizon, 256 balanced scenarios,
and two repetitions. Using an illustrative—not approved—five percentage-point
CI half-width, the largest paired estimate was 27 repetitions. This supports the
existing 30-run placeholder but does not freeze it: the operational horizon,
MPID, factor levels, and domain validation differ and require PI approval.

## Estimands and models

- Primary: absolute percentage-point service-level contrast between each method
  and the prespecified baseline, with 95% CI.
- Late counts: negative-binomial factorial GLM; inspect Pearson dispersion.
- Service level: grouped binomial factorial GLM with generated orders as weights.
- Paired policy contrasts: CRN-matched differences with 95% t interval and
  Wilcoxon sensitivity test; Holm correction within each outcome family.
- Report magnitude and uncertainty regardless of p-value.

Exclusions are limited to runs explicitly marked failed; any failure invalidates
the final batch until investigated and rerun. No outcome-based exclusion is
permitted. Deviations must be appended below with timestamp, reason, and approver.

## Decisions still requiring approval

- [ ] Select baseline trigger.
- [ ] Define service-level MPID with a domain expert.
- [ ] Approve operationally plausible factor levels.
- [ ] Approve pilot-based repetitions and final hypotheses.

## Deviations

None recorded.
