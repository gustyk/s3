# Main experiment readiness gate — 2026-08-16

## Decision

**GO secara teknis untuk menjalankan simulasi utama 207,360 run**, dengan
parameter canonical yang sudah dibekukan. Jangan mengubah source, config, seed,
atau output directory setelah gate ini dilewati.

GO ini berarti pipeline simulasi siap dan reviewer computational gates selesai.
Ini bukan berarti manuskrip final sudah siap dikirim; revisi teks, literatur,
MDP notation, response letter, dan regenerasi tabel utama masih harus dilakukan
setelah main output tersedia.

## Gate results

| Gate | Status | Evidence |
|---|---|---|
| Reviewer brief REVISI01 dipetakan | PASS | 17 reviewer items mapped |
| Ablation timing × composition | PASS | 4,320 rows; 6/6 audits pass |
| F/V calibration | PASS | 24,480 rows; 17/17 audits pass |
| β sensitivity | PASS | 23,040 rows; 16/16 audits pass |
| Decision benchmark | PASS | 1,440 measurements; manifest success |
| Run UUID/status/schema integrity | PASS | no duplicate UUID; all success |
| Canonical F/V/β | PASS | F=720, V=12, β=2 |
| Warm-up and fixed horizon | PASS | warm-up=5,460 s; horizon=28,800 s |
| Main per-order evidence | READY | main config persists `orders.csv.gz` |
| Main factorial count | PASS | 6,912 scenarios × 30 = 207,360 |
| Source/config immutability | PASS | strict preflight passed on 2026-08-16 |

## Frozen main configuration

- Incoming rates: 6 levels.
- Trigger methods: 8 methods, including SNH and MPBH.
- Picker counts: 12 levels.
- Batching: FCFS and EDT.
- Cart capacities: 3 levels.
- Routing: S-shape and Largest Gap.
- Repetitions: 30.
- F: 720 seconds.
- V: 12 orders.
- Urgency β: 2.
- Pick time: 5 seconds/piece.
- Setup time: 180 seconds/tour.
- Warm-up: 5,460 seconds.
- Observation horizon: 28,800 seconds after warm-up.
- TLO: completed-late plus overdue outstanding.
- Main raw output: `orders.csv.gz` enabled.

## Completed final preflight

The strict preflight passed on 2026-08-16 with config SHA-256
`d359bc8f3a2cda65123a640155339ce18092ae8214913fc6561b916ffd42234f`.
It confirmed 207,360 planned runs, canonical parameters, per-order evidence,
clean relevant source tree, dependency lock, and 167+ GiB free disk. The full
report is `outputs/final-q1-v1/preflight/full-factorial-2026-08-16.json`.

## Main execution command

```powershell
python -m src.preflight `
  --config config/parameters.yaml `
  --output-dir outputs/final-q1-v1/full-factorial `
  --mode full `
  --repetitions 30 `
  --require-clean `
  --minimum-free-gib 60 `
  --report outputs/final-q1-v1/preflight/full-factorial.json
```

Proceed only when the report contains `"status": "pass"`. Then run:

```powershell
python -u -m src.experiment `
  --config config/parameters.yaml `
  --output-dir outputs/final-q1-v1/full-factorial `
  --mode full `
  --repetitions 30 `
  --log-level WARNING
```

Use the same output directory and command to resume after interruption.

## Explicit no-go conditions

Stop before starting if any of the following occurs:

- preflight status is not `pass`;
- config hash differs from the approved canonical config;
- source tree is dirty in `src`, `config`, `pyproject.toml`, or
  `requirements.lock`;
- an existing main output has a different manifest/config hash;
- disk free space is below 60 GiB;
- any reviewer result cell is later found to have a failed audit;
- anyone proposes replacing F=720/V=12 solely because a tuned sensitivity value
  performed better.

## Post-main gates

After the main run, the following remain mandatory before manuscript revision is
finalized:

1. strict `audit_results` on main `results.csv` and `orders.csv.gz`;
2. censoring-aware extended metrics from raw order evidence;
3. corrected composite score and weight sensitivity on the main eight-method
   dataset;
4. factorial models, paired contrasts, confidence intervals, and figures;
5. response-to-reviewer entries with exact output paths and final page numbers;
6. manual revision of the original paper, which must remain unchanged in this
   repository until the author performs that step separately.
