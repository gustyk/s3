# Local Engineering Evidence — 2026-08-12

This evidence is suitable for software verification and experiment planning,
not for final scientific claims or domain validation.

## Factorial pilot

- Design: 256 balanced configurations × 2 repetitions = 512 runs.
- Horizon: 600 seconds (engineering pilot only).
- Trigger methods: all eight.
- Other factors: two levels each for arrival, picker count, batching, cart
  capacity, and routing.
- Execution order: deterministically randomized; seed recorded in manifest.
- Audit: 512/512 success, no duplicate UUID, conservation true, checksum pass.
- Final local evidence batch: v5; source-tree SHA-256
  `EC6527ADD1614D601AE9C22F4794DFB9AB992EB13806D19BFAE99BF3162E7047`.
- Dependency-lock SHA-256:
  `C023B056E5327FFF4A9E25F4ACB2046AAA1A05E2798FAEF828916BFAC8AAB157`.
- Results SHA-256: `CC544CB7BF1FDFA9B32AA03B04C01F51C94D1A48F1B6E46F50B83376FCA5001D`.
- Illustrative five-percentage-point CI half-width estimate: maximum 27
  repetitions. This does not replace PI/domain approval of the MPID.

Count models were not estimable because no late order occurred in the short
pilot. The analysis pipeline recorded this explicitly rather than fabricating an
inferential result. Binomial service and HC3 throughput models fitted; the
Breusch–Pagan result indicated heteroskedasticity, supporting robust covariance.

## Sensitivity and ablation

- Latin-hypercube screening: 16 epistemic samples across six inputs.
- One-at-a-time screening: 13 baseline/low/high directional engineering cases.
- Constant tardiness was marked `not_estimable`; no NaN correlation was
  interpreted.
- Ablations: DVNS base/urgency-only/cart-only/no-hybrid and MPBH
  base/no-quantity/no-route, two engineering repetitions each.
- All seven ablation jobs (14 runs) completed and each artifact audit passed.
  Aggregate summary SHA-256 is
  `A900F7D8E36DD5069549DACAB6F0B6D7903987AD32895F96EDE9F51702A6D74B`.
  Final interpretation requires
  validated ranges and publication-horizon repetitions.

## Scalability benchmark

- Engineering configuration: 120 simulated seconds; three arrival rates × three
  picker levels, each measured three times.
- Route kernel: 1, 16, 64, 128, 256, and 384 item lines; three repeats of 1,000
  calls each.
- On the current 8-logical-CPU Windows/Python 3.14 workspace, route-kernel means
  ranged approximately 73–278 microseconds/call. Simulation wall-time means
  ranged approximately 0.070–0.267 seconds.
- Sampled process RSS means ranged approximately 101.7–102.2 MB. CPU time,
  utilization, Python allocation peak, Student-t descriptive intervals, and raw
  file size are recorded in the benchmark CSV/metadata.
- Estimated `results.csv` size for the currently configured 6,912-row full
  experiment is 2,744,832 bytes, excluding logs, figures, and derived outputs.
- Raw benchmark SHA-256:
  `9D9AFFE4EB0EC07938AD22DD0D9D15F9568C141B8583677CFC2952F8AA852B75`;
  summary SHA-256:
  `6A3C338F30E99937E763A47209CD9ECCB189A97D160DBCD8EB92802477A21AE1`.
- These are local engineering measurements; tagged-release hardware rerun and
  deterministic parallel-equivalence evidence remain required.

## Verification

- 51 tests pass.
- Core branch coverage: 92.55% (gate: 90%).
- Ruff and mypy pass for 20 source files.
- Git diff whitespace check passes.
- Two all-method smoke results are byte-identical with SHA-256
  `F28D59ED93E2DF164922166750E62155A2A4242AB3235F694F90550921CCD42E`;
  both strict audits pass 8/8.
