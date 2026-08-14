# External Action Register

Blocked audit: 2026-08-12. The implementation agent exhausted worktree-local
actions. This register identifies the external state required to complete the
remaining 36 checklist items; no item may be self-certified by code alone.

| Package | Accountable owner | Required input/action | Minimum admissible evidence | Gates/items unblocked |
|---|---|---|---|---|
| A. Scientific approval | PI and coauthors | approve questions, intended use, factor levels, baseline, hypotheses, exclusions, stopping rule, MPID, validation tolerances, and repetitions | dated signed decision plus frozen `ANALYSIS_PLAN.md`/final config hash | P0.6, P1.4, P2.3, Gate A/D |
| B. Operational data | warehouse data owner and data steward | deliver pseudonymized extracts defined in `OPERATIONAL_DATA_SCHEMA.md`, ownership/rights, calibration/validation periods, and benchmark KPI | immutable files, extraction report, checksums, data license/access decision | P1.3, P2.4, Gate C |
| C. Domain validation | warehouse SME independent enough to challenge assumptions | execute `DOMAIN_REVIEW_PROTOCOL.md`, approve validity domain/ranges, review traces and validation errors | signed minutes, issue-resolution log, accepted/conditional/rejected decision | P1.3, Gate A/C |
| D. Literature/statistics review | OR subject specialist and statistician | select and verify a strong benchmark, review novelty, estimands, model families, multiplicity, diagnostics, and practical interpretation | search protocol/citations, implementation oracle, signed statistical review and resolutions | P1.4, P4, Gate D/G |
| E. Repository/infrastructure | repository admin and CI operator | commit approved tree, configure required checks/branch protection, run remote CI and digest-pinned Docker build/security scan | protected-branch settings export/screenshots, green workflow URL/logs, image digest and scan report | P3.3/P3.5, Gate B |
| F. Independent reproduction | second researcher not the primary developer | execute smoke, final audit, analysis, and main-claim reproduction from clean artifact without author help | completed `REVIEW_CHECKLISTS.md`, environment log, checksums, discrepancy record | P3.5, P4, Gate F |
| G. Tagged final experiment | authorized release operator after A–F prerequisites | follow `RELEASE_RUNBOOK.md` from clean signed tag; produce final, sensitivity, ablation, and resource datasets | clean git state, signed tag/commit, 100% successful manifests/audits, immutable raw storage and derived manifests | P0.6, P2/P4 final-data items, Gate E/F |
| H. Archive/submission | PI/corresponding author and repository owner | select journal, complete live author checklist, publish accepted artifact, mint DOI, declare data/code/AI/funding/conflicts | selected journal/versioned checklist, public or controlled-access DOI, downloaded checksum verification | P3.5, P4, Gate G |

## Current environment constraints

- `origin` is `https://github.com/gustyk/s3.git`; no GitHub CLI/authenticated
  administration capability is available in this workspace.
- Docker executable is unavailable, so the locally prepared image cannot be
  built or independently exercised here.
- No operational dataset, signed PI decision, SME, second researcher, archive
  account, or final journal decision has been supplied.
- The current worktree is intentionally uncommitted/dirty; its audited pilot is
  engineering evidence only and cannot be relabeled as final release data.

Work resumes when at least one package above has an accountable owner and its
required input/evidence is placed in scope.
