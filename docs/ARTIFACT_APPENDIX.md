# Artifact Appendix

## Container base

The artifact pins the official `python:3.12.13-slim-bookworm` multi-platform
index digest `sha256:4766d8b510c428e595d74b9cc5bbb2fae8e26316fffb4adc89908d79aacd58a2`,
resolved from Docker Hub on 2026-08-12. CI builds and executes the image; a
local Docker runtime was unavailable during this audit.

## Inventory

The release artifact must contain source, locked environment, configuration,
tests, raw final output, manifests/checksums, analysis scripts, generated tables
and figures, model specification, validation evidence, completed STRESS-DES
mapping, license files, and this appendix. Legacy data is excluded from claims.

## Reviewer workflow

1. Build the documented environment or container.
2. Run `pytest` and confirm all gates pass.
3. Run selected and all-method smoke configurations.
4. Audit the smoke result.
5. Verify final-data checksum against its manifest.
6. Run analysis into a new directory.
7. Compare generated table/figure checksums with the release manifest.

Expected time and resources must be measured on the release candidate and added
here. A reviewer should not need author assistance for steps 1–7.

## External archive

Repository DOI, release URL, archive checksum, data access terms, and artifact
evaluation status are pending. Publication to Zenodo/OSF or an institutional
repository requires principal-investigator authorization and occurs only after
the final tagged release.
