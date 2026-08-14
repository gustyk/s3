# STRESS-DES Reporting Map

This map follows the six STRESS reporting areas. It is an internal completion
map, not a claim of endorsement by the STRESS authors.

| Area | Required disclosure | Repository evidence | Status |
|---|---|---|---|
| Objectives | Purpose, research questions, intended use | `MODEL_SPECIFICATION.md` | DONE; hypotheses need PI approval |
| Logic | Base time unit, entities, activities, queues, resources, events | `MODEL_SPECIFICATION.md`, `src/` | DONE |
| Logic | Algorithms and assumptions | `MODEL_SPECIFICATION.md` | DONE; domain review pending |
| Logic | Initialization and stopping | zero initial state; fixed horizon with censoring in model spec/runner | DONE |
| Data | Input sources and sampling | `PARAMETER_PROVENANCE.md`, `VALIDATION_PROTOCOL.md` | BLOCKED: operational evidence unavailable |
| Data | Input preprocessing and fitting | validation protocol | BLOCKED: operational evidence unavailable |
| Experimentation | Factors, levels, outcomes, scenarios | config, `ANALYSIS_PLAN.md` | IN PROGRESS: PI freeze pending |
| Experimentation | Warm-up, run length, repetitions | fixed transient shift; plan requires pilot precision | IN PROGRESS |
| Experimentation | RNG and variance reduction | injected RNG, deterministic CRN seeds, manifest | DONE |
| Experimentation | Sensitivity/uncertainty | analysis plan and Q1 backlog | IN PROGRESS: final data required |
| Implementation | Software/libraries/hardware | result manifest, lock file, artifact appendix | DONE for software; release hardware pending |
| Implementation | Verification and validation | tests/CI; validation protocol | verification DONE, validation BLOCKED |
| Results | Estimates, uncertainty, negative results | analysis pipeline | IMPLEMENTED; final run pending |
| Code access | Source, dependencies, instructions, license | README, lock, Dockerfile, MIT license | DONE locally |
| Code access | Persistent DOI and access conditions | artifact appendix/data license | BLOCKED: PI/repository authorization |

Initialization uses an empty order and batch system at time zero. Because the
study models one finite work shift rather than steady state, no warm-up deletion
is applied. The horizon is 28,800 seconds by default; uncompleted observations
are explicitly right-censored and retained in denominators. Repetitions remain
provisional until pilot precision analysis is approved.

