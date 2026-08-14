# Final Experiment Release Runbook

Status: **READY FOR EXECUTION AFTER GATES A–D; do not run yet**.

1. Archive signed Gate A/C/D records and the frozen analysis plan.
2. Set approved baseline, factor levels, horizon, MPID, and repetitions in a new
   versioned final configuration; review its canonical SHA-256.
3. Require all CI jobs and independent code/model review to pass.
4. Commit the approved tree, require `git status --porcelain` to be empty, and
   create a signed semantic-version tag. Record tag and commit in the release
   decision. Never use a dirty-tree pilot as final evidence.
5. Build the digest-pinned container and record image digest, host CPU/RAM/OS,
   runtime, and security-scan result.
6. From a clean checkout of the tag, create a new empty output directory and run
   `python -m src.experiment --config config/<final>.yaml --mode full
   --output-dir outputs/final-<tag>`.
7. Require zero failed runs, then run `src.audit_results`. Copy raw result,
   manifest, audit report, config, logs, and checksums to read-only storage.
8. Run `src.analysis_pipeline` into a separate derived directory. Never modify
   raw results. Regenerate all tables/figures and retain the analysis manifest.
9. Run sensitivity, ablation, and resource benchmark from the same tag using
   approved ranges/repetitions; record negative, tie, and losing scenarios.
10. Give the artifact and appendix to an independent reviewer for clean-room
    reproduction. Resolve discrepancies through a documented deviation, never
    by silently editing frozen output.
11. Publish the accepted release to the authorized persistent repository, mint
    the DOI, verify downloaded checksums, and complete the journal checklist.

Any code/config change after tagging invalidates downstream final data and
requires a new tag and output directory.
