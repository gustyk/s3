# Roadmap Kualitas Simulasi untuk Publikasi Jurnal Q1

Dokumen ini adalah backlog mutu untuk menjadikan model, eksperimen, data, analisis, dan artefak penelitian dapat diverifikasi. Label “siap submission” hanya boleh digunakan setelah seluruh quality gate wajib lulus. Peringkat jurnal tidak memiliki satu checklist universal; persyaratan akhir tetap harus dipetakan ke *author guidelines* dan kebijakan reproducibility jurnal target.

Blocked-audit terakhir: 2026-08-12. Seluruh dependency eksternal, owner, input,
dan bukti pembuka gate dipetakan di `docs/EXTERNAL_ACTION_REGISTER.md`.
Formulir jawaban dan instruksi penutupan untuk seluruh 30 `BLOCKED_EXTERNAL`
dan 6 `PENDING_FINAL_DATA` tersedia di `docs/Q1_UNBLOCKING_WORKSHEET.md`.
Discovery dan rencana implementasi brief revisi mayor EJIE-337519 tersedia di
`outputs/DISCOVERY_NOTES.md`; pekerjaan reviewer dipetakan ke blocker yang sudah
ada dan tidak menambah jumlah 30 + 6 tersebut.

## Aturan prioritas

- **P0 — Publication blocker:** dapat membatalkan validitas hasil atau membuat penelitian tidak dapat direproduksi. Semua wajib selesai sebelum simulasi final.
- **P1 — Scientific validity:** diperlukan untuk verification, validation, desain eksperimen, dan interpretasi hasil yang defensible.
- **P2 — Statistical and reporting rigor:** diperlukan agar analisis, klaim, serta pelaporan memenuhi praktik penelitian kuantitatif yang kuat.
- **P3 — Engineering quality:** meningkatkan maintainability, reliability, auditability, dan kemudahan reproduksi oleh reviewer.
- **P4 — Excellence:** meningkatkan dampak, transparansi, generalisasi, dan peluang diterimanya manuskrip.

Setiap item harus memiliki pemilik, target tanggal, PR/commit, bukti pengujian, dan status. Status yang digunakan: `TODO`, `IN PROGRESS`, `BLOCKED`, `DONE`, `VERIFIED`.

## Status eksekusi aktual — 2026-08-12

### Release-readiness update — 2026-08-14

- Source/config release candidate telah lulus Ruff, mypy, 67 tests, dan
  branch-aware coverage 93.91%.
- Preflight desain utama mengonfirmasi 6.912 skenario × 30 = 207.360 run,
  parameter kanonik, raw-order gzip, dependency lock, dan kebutuhan minimum
  disk 60 GiB; estimasi arrival-process adalah sekitar 621,6 juta raw rows.
- Final schema mencakup seluruh KPI paper/reviewer serta release reason/time,
  batch size, tour time, censoring, F/V/β aktual, surrogate ID, wall time, dan
  provenance. Release smoke delapan metode lulus strict audit.
- Resume telah diverifikasi terhadap simulated power loss dan timeout proses
  nyata. Checkpoint per run menyimpan certified CSV/GZIP byte boundaries;
  completed runs/cells diaudit dan tidak dihitung ulang.
- Instruksi produksi ada di `docs/FINAL_EXPERIMENT_RUNBOOK.md`; wrapper ada di
  `scripts/run_final_experiments.ps1`. Gate yang masih terbuka sebelum eksekusi
  adalah clean commit/tag oleh owner serta seluruh approval/data eksternal yang
  memang tidak dapat dipenuhi dari repository.

### Reviewer-results update — 2026-08-16

- **DONE_LOCAL:** seluruh computational reviewer experiments dari
  `docs/REVISI01.md` telah selesai: ablation 4.320 run, F/V calibration 24.480
  run, β sensitivity 23.040 run, dan decision benchmark 1.440 measurements.
- **DONE_LOCAL:** seluruh 39 simulation cells lolos artifact audit; seluruh
  aggregate rows berstatus success dan run UUID unik.
- **DECISION FROZEN:** main factorial tetap memakai F=720 s, V=12, β=2 sesuai
  paper-canonical definition. Tuned F=60 dan V=4/6 hanya dilaporkan sebagai
  calibration/robustness evidence.
- **CLAIM REVISION REQUIRED:** hasil ablation menunjukkan MPBH composition
  effect sekitar −153 TLO, sedangkan MPBH timing effect sekitar −18 TLO.
  Proposisi 4 harus dipersempit dan tidak boleh menyatakan timing secara umum
  lebih penting daripada composition.
- **READY_FOR_MAIN:** readiness gate terdokumentasi di
  `docs/MAIN_EXPERIMENT_READINESS_2026-08-16.md`; main run tetap menunggu
  strict preflight pass dan tidak boleh dilakukan dengan source/config yang
  berubah.

### Main-results update — 2026-08-18

- **DONE_LOCAL:** main factorial selesai 207.360/207.360 run, 0 failed;
  `outputs/final-q1-v1/full-factorial/audit.json` berstatus `pass`.
- **DONE_LOCAL:** 621.955.584 raw order rows direkonsiliasi; 522.713.088
  measurement-eligible rows setelah warm-up cocok tepat dengan denominator
  `generated_orders`.
- **DONE_LOCAL:** paired CRN effects, Pareto, corrected composite empat skema
  bobot, censoring-aware extended metrics, dan analysis certification tersedia.
- **FINAL FINDING:** MPBH mengurangi mean TLO 10,66% terhadap pooled canonical
  FTWB/VTWB, bukan 27,04%; MPBH peringkat pertama di empat skema composite.
- **FINAL NEGATIVE RESULT:** Proposition 4 tidak didukung. MPBH composition
  effect sekitar −153 TLO, jauh lebih besar daripada MPBH timing effect −18,119.
- **MODEL WARNING:** Poisson sangat overdispersed; secondary negative-binomial
  tidak konvergen. Primary inference wajib memakai paired CRN effect + 95% CI.
- **DEVIATION/BLOCKER:** manifest main mencatat `git_dirty=True` pada commit
  `724519fb...`; source/config checksum tersedia, tetapi clean signed-tag dan
  immutable archive Gate E belum terpenuhi.
- **QUALITY GATE:** Ruff dan mypy lulus; 67 tests lulus; coverage 93,91%.
- Ringkasan dampak paper: `docs/FINAL_SIMULATION_RESULTS_AND_PAPER_IMPACT_2026-08-18.md`.

Status di bawah bersifat evidence-based. `DONE_LOCAL` berarti implementasi dan
verifikasi otomatis lokal selesai, tetapi belum memenuhi Definition of Done
global yang mensyaratkan review orang kedua. `BLOCKED_EXTERNAL` memerlukan data,
keputusan, otorisasi, atau reviewer di luar repository.

| Workstream | Status | Bukti / pekerjaan tersisa |
|---|---|---|
| P0.1 Legacy data | DONE_LOCAL | `data/legacy/MANIFEST.md`, rename terkarantina, SHA-256, larangan analisis |
| P0.2 Method/config consistency | BLOCKED_EXTERNAL | current code konsisten internal, tetapi discovery reviewer menemukan SNH/DVNS dan MPBH paper tidak ekuivalen dengan implementasi; menunggu keputusan BE-25/BE-28 |
| P0.3 Time/late semantics | DONE_LOCAL | waktu numerik, fixed horizon+censoring, KPI terdefinisi, urgency heap forecast, conservation invariant |
| P0.4 Reproducibility | DONE_LOCAL | injected RNG, CRN seed, UUID, config/commit/version metadata; dua smoke CSV identik byte-for-byte |
| P0.5 Failure semantics | DONE_LOCAL | exception tidak disembunyikan, failed status, atomic CSV, manifest, non-zero batch failure |
| P0.6 Final regeneration | BLOCKED_EXTERNAL | menunggu Gate A–D, tag rilis, pilot repetitions, data/domain validation; dataset final belum boleh dibuat |
| P1.1 Model specification | DONE_LOCAL | `docs/MODEL_SPECIFICATION.md` selesai; approval domain expert tetap Gate A eksternal |
| P1.2 Software verification | DONE_LOCAL | 51 tests; core branch coverage 92.55%; lint dan mypy lulus; CI workflow tersedia |
| P1.3 Domain validation | BLOCKED_EXTERNAL | protokol, provenance, calibration-only distribution fitting, extreme tests, dan executable held-out validation gate tersedia; data WMS, toleransi, benchmark, dan SME belum tersedia |
| P1.4 Experiment design | BLOCKED_EXTERNAL | balanced pilot 512/512 lulus; reviewer subset, crossed ablation, benchmark tuning/evaluation split, β sweep, MPID, dan PI freeze masih perlu keputusan |
| P1.5 KPI | BLOCKED_EXTERNAL | current runner memiliki KPI lengkap, tetapi legacy 207.360 hanya agregat dan tidak memiliki raw per-order untuk average tardiness reviewer |
| P2.1 Analysis pipeline | IN_PROGRESS | pipeline audit/Pareto tersedia; reviewer mewajibkan satu composite-score function konsisten, root-cause artifact, dan weight sensitivity |
| P2.2 Statistical models | DONE_LOCAL | factorial NB/binomial, CRN pairing, Holm, constant-outcome handling, dan robust diagnostics tersedia; eksekusi confirmatory menunggu final data |
| P2.3 Estimation | BLOCKED_EXTERNAL | paired effect+95% CI dan exact adjusted p tersedia; MPID/domain interpretation/final data tertunda |
| P2.4 Sensitivity/generalization | BLOCKED_EXTERNAL | engineering ablations tersedia, tetapi reviewer meminta trigger-vs-composition crossed ablation dan β sweep setelah algoritme/subset dibekukan |
| P2.5 STRESS-DES | BLOCKED_EXTERNAL | `docs/STRESS_DES_CHECKLIST.md` dipetakan; penyelesaian menunggu input-data, validation, dan final results |
| P3.1 Packaging | DONE_LOCAL | `pyproject.toml`, lock, path-safe config, gitignore, version/changelog, code/data licenses |
| P3.2 Refactoring/types | IN_PROGRESS | modularisasi umum tersedia; trigger decision dan composition masih tercampur dan perlu interface eksplisit untuk reviewer |
| P3.3 CI/gates | BLOCKED_EXTERNAL | workflow matrix, lint/type/test/coverage/smoke/audit/container tersedia; branch protection perlu GitHub admin |
| P3.4 Reviewer documentation | IN_PROGRESS | dokumentasi dasar selesai; output manuscript-ready per reviewer dan traceability ID belum dibuat |
| P3.5 Artifact archive | BLOCKED_EXTERNAL | Dockerfile memakai immutable official-image digest dan appendix tersedia; Docker tidak terpasang lokal, DOI dan independent clean-room review tertunda |
| P4 Excellence | BLOCKED_EXTERNAL | whole-run/route benchmark tersedia; decision-kernel timing delapan metode, curve fit, final tagged hardware, independent/statistical review masih tertunda |
| Gate A | BLOCKED_EXTERNAL | memerlukan persetujuan tim/domain expert |
| Gate B | BLOCKED_EXTERNAL | verifikasi otomatis lulus; review orang kedua dan P0.6/final tag belum selesai |
| Gate C | BLOCKED_EXTERNAL | data dan domain validation belum tersedia |
| Gate D | BLOCKED_EXTERNAL | keputusan PI untuk baseline, MPID, repetitions, hypotheses |
| Gate E | BLOCKED_EXTERNAL | final tagged dataset belum dijalankan secara sengaja |
| Gate F | BLOCKED_EXTERNAL | peneliti kedua belum ditunjuk |
| Gate G | BLOCKED_EXTERNAL | jurnal target, validation, archive DOI, dan review belum selesai |

### Bukti verifikasi lokal terakhir

- `pytest`: 51 passed; core branch coverage 92.55% (threshold 90%).
- `ruff check src tests`: passed.
- `mypy src`: passed untuk 20 source files.
- all-method reviewer smoke: 8/8 success; result audit `pass`.
- balanced factorial pilot v5: 512/512 success; SHA-256
  `CC544CB7BF1FDFA9B32AA03B04C01F51C94D1A48F1B6E46F50B83376FCA5001D`;
  evidence in `docs/LOCAL_EVIDENCE_2026-08-12.md`.
- deterministic replay: dua 8-method `results.csv` memiliki SHA-256 identik
  `F28D59ED93E2DF164922166750E62155A2A4242AB3235F694F90550921CCD42E`.
- Docker build: belum dapat diverifikasi lokal karena executable Docker tidak
  tersedia; workflow CI akan mengujinya pada GitHub runner.

---

## P0 — Publication blockers

### P0.1 Bekukan dan karantina hasil lama

- [x] **DONE_LOCAL** — Tandai `simulation_results.csv` saat ini sebagai **legacy/unverified** dan larang penggunaannya untuk klaim utama.
- [x] **DONE_LOCAL** — Simpan salinan read-only beserta SHA-256, tanggal pembuatan jika diketahui, dan commit asal jika dapat dilacak.
- [x] **DONE_LOCAL** — Dokumentasikan anomali yang sudah ditemukan: 72 `run_id` duplikat, rentang ID 185761–186160 hilang, serta hasil MPBH yang tidak dapat dihasilkan source saat ini.
- [x] **DONE_LOCAL** — Buat keputusan tertulis apakah data lama hanya dipakai untuk debugging atau dibuang dari analisis publikasi.

**Acceptance criteria:** manuskrip dan pipeline analisis tidak dapat mengambil dataset legacy secara tidak sengaja; dataset final memiliki manifest dan checksum sendiri.

### P0.2 Sinkronkan konfigurasi, implementasi, dan label hasil

- [x] **DONE_LOCAL** — Implementasi MPBH current telah didefinisikan dan diuji terhadap spesifikasi repository current.
- [ ] **DECISION_REQUIRED (BE-25/BE-28)** — Rekonsiliasi spesifikasi current dengan paper: MPBH paper memakai EDD + constraint β + feasibility restoration, sedangkan current code memakai slack-per-item + route time; pilih satu algoritme kanonik.
- [ ] **DECISION_REQUIRED (BE-25/BE-28)** — Sahkan apakah legacy/current `DVNS` adalah paper `SNH`; selaraskan label, pseudocode, config, tests, dan output.
- [ ] **TODO_REVIEWER** — Tambahkan fidelity tests terhadap pseudocode kanonik dan perbaiki syarat picker-availability pada metode yang diwajibkan paper.
- [x] **DONE_LOCAL** — Teruskan `routing_policy` secara eksplisit ke seluruh trigger yang menghitung urgency.
- [x] **DONE_LOCAL** — Hilangkan hard-code EDT pada DVNS; gunakan `batching_type` eksperimen atau deklarasikan DVNS sebagai metode yang memang intrinsik memakai EDT dan jangan buat kombinasi DVNS–FCFS.
- [x] **DONE_LOCAL** — Buat registry tunggal untuk semua trigger, batching method, dan routing policy agar konfigurasi yang tidak didukung gagal sebelum simulasi dimulai.
- [x] **DONE_LOCAL** — Validasi bahwa setiap label pada output identik dengan algoritme yang benar-benar dieksekusi.

**Acceptance criteria:** seluruh kombinasi konfigurasi lolos smoke test; konfigurasi ilegal gagal cepat dengan pesan yang jelas; tidak ada label output yang menyesatkan.

### P0.3 Perbaiki definisi waktu dan keterlambatan

- [x] **DONE_LOCAL** — Gunakan waktu numerik dalam detik sebagai representasi internal; format `HH:MM:SS` hanya untuk presentasi.
- [x] **DONE_LOCAL** — Definisikan secara formal: waktu kedatangan, due time, waktu mulai, waktu selesai, flow time, waiting time, tardiness, dan status late.
- [x] **DONE_LOCAL** — Putuskan apakah due time relatif terhadap awal simulasi, awal shift, atau waktu kalender; terapkan konsisten.
- [x] **DONE_LOCAL** — Perbaiki estimator urgent agar memperhitungkan kapasitas cart, batch pending/active, ketersediaan picker, dan pemrosesan paralel.
- [x] **DONE_LOCAL** — Tentukan kebijakan akhir horizon: *drain period*, fixed horizon dengan right-censoring, atau dua metrik terpisah untuk completed dan outstanding orders.
- [x] **DONE_LOCAL** — Pastikan order yang belum selesai tidak “menghilang” dari denominator service level.
- [x] **DONE_LOCAL** — Cegah double counting late orders antara pool, pending batch, active batch, dan completed batch.

**Acceptance criteria:** contoh kecil dapat dihitung manual dan memberikan hasil identik; selalu berlaku `generated = completed + waiting + pending + active` pada horizon.

### P0.4 Bangun reproducibility deterministik

- [x] **DONE_LOCAL** — Ganti RNG global dengan `numpy.random.Generator` yang diinjeksi ke generator/order model.
- [x] **DONE_LOCAL** — Tetapkan master seed dan seed deterministik untuk setiap konfigurasi × repetisi.
- [x] **DONE_LOCAL** — Simpan `seed`, repetition ID, run UUID, commit SHA, config hash, code/version tag, Python version, dan dependency lock hash pada output/manifest.
- [x] **DONE_LOCAL** — Gunakan *common random numbers* untuk membandingkan metode pada skenario demand yang sama, bila sesuai dengan desain penelitian.
- [x] **DONE_LOCAL** — Pastikan runner deterministik tidak mengubah seed mapping atau mengulang identitas run; checkpoint/resume memvalidasi config, plan, source tree, count, dan last UUID.
- [x] **DONE_LOCAL** — Tambahkan tes bahwa run dengan seed sama menghasilkan output identik dan seed berbeda menghasilkan input stochastic berbeda.

**Acceptance criteria:** reviewer dapat mereproduksi satu baris hasil secara identik dari metadata baris tersebut.

### P0.5 Hentikan silent failure

- [x] **DONE_LOCAL** — Jangan menangkap `Exception` generik di loop trigger kecuali error dilempar kembali setelah konteks dicatat.
- [x] **DONE_LOCAL** — Jangan menyetel logging ke `CRITICAL` selama eksperimen final; simpan log per run atau ringkasan failure terstruktur.
- [x] **DONE_LOCAL** — Tambahkan status `success/failed`, error type, dan error message pada run manifest.
- [x] **DONE_LOCAL** — Gunakan penulisan output atomik dan manifest tervalidasi.
- [x] **DONE_LOCAL** — Simulasi final harus berakhir non-zero jika ada run gagal atau jumlah run tidak sesuai rencana.

**Acceptance criteria:** fault injection menghasilkan run gagal yang terlihat jelas dan tidak pernah tercatat sebagai hasil sukses.

### P0.6 Regenerasi seluruh hasil final

- [ ] **BLOCKED_EXTERNAL** — Setelah P0.1–P0.5 diverifikasi, buat tag rilis model sebelum eksperimen final; memerlukan approval Gate A–D dan otorisasi release.
- [ ] **BLOCKED_EXTERNAL** — Jalankan eksperimen dari direktori output baru yang kosong setelah repetitions/factor levels dibekukan.
- [ ] **PENDING_FINAL_DATA** — Validasi jumlah konfigurasi, repetisi, uniqueness key, seed, nilai hilang, rentang metrik, dan checksum; automated audit siap.
- [ ] **PENDING_FINAL_DATA** — Bekukan raw output; seluruh transformasi selanjutnya harus menghasilkan derived dataset baru.
- [ ] **PENDING_FINAL_DATA** — Simpan run manifest dan audit report otomatis bersama dataset; runner/pipeline siap.

**Acceptance criteria:** dataset final hanya berasal dari satu tag rilis tervalidasi, tidak memiliki duplikasi, run hilang, atau run gagal.

---

## P1 — Scientific validity

### P1.1 Spesifikasi model konseptual

- [x] **DONE_LOCAL** — Tulis tujuan model, research questions, hypotheses, scope, unit analisis, dan intended use.
- [x] **DONE_LOCAL** — Dokumentasikan entities, attributes, resources, queues, events, state transitions, dan stopping conditions.
- [x] **DONE_LOCAL** — Buat diagram alur order dari arrival hingga completion.
- [x] **DONE_LOCAL** — Dokumentasikan semua asumsi, simplifikasi, boundary conditions, dan konsekuensinya.
- [x] **DONE_LOCAL** — Definisikan setiap algoritme trigger, batching, dan routing dengan pseudocode atau formulasi yang tidak ambigu.
- [x] **DONE_LOCAL** — Jelaskan apakah setup time berlaku per batch, trip, picker, atau shift.

**Acceptance criteria:** seorang domain expert dapat mengimplementasikan ulang model hanya dari spesifikasi dan memperoleh perilaku yang ekuivalen.

### P1.2 Verification model dan software

- [x] **DONE_LOCAL** — Tambahkan unit test untuk `OrderPool`, `IOPool`, generator, batching, routing, dan setiap trigger.
- [x] **DONE_LOCAL** — Tambahkan golden tests untuk Traversal dan Largest Gap menggunakan rute yang dihitung manual.
- [x] **DONE_LOCAL** — Uji batas: pool kosong, satu order, satu item, order tepat/melebihi kapasitas, due time tepat completion time, dan rollover hari numerik.
- [x] **DONE_LOCAL** — Tambahkan property/invariant tests: kapasitas batch tidak terlampaui, order tidak hilang/duplikat, picker tidak memegang dua batch, waktu monoton, dan counter non-negatif.
- [x] **DONE_LOCAL** — Tambahkan integration test untuk setiap metode dan end-to-end deterministic regression test.
- [x] **DONE_LOCAL** — Lakukan trace walkthrough pada model kecil dan bandingkan event log dengan perhitungan manual melalui golden route/completion cases.
- [x] **DONE_LOCAL** — Jalankan static analysis, type checking, linting, dan coverage; tetapkan ambang coverage untuk core model minimal 90% branch coverage.

**Acceptance criteria:** seluruh test dan invariant lulus pada CI; tiap algoritme utama memiliki test normal, boundary, dan failure path.

### P1.3 Validation terhadap sistem nyata/domain

- [ ] **BLOCKED_EXTERNAL** — Identifikasi sumber data untuk arrival, order size, quantity, item popularity, due-time distribution, layout, kecepatan berjalan, picking time, dan setup time.
- [ ] **BLOCKED_EXTERNAL** — Jelaskan provenance, periode observasi, cleaning, missing data, outlier handling, dan keterbatasan data.
- [ ] **BLOCKED_EXTERNAL** — Estimasikan distribusi dari data bila tersedia; calibration-only fitting CLI dengan AIC/BIC/KS dan held-out likelihood siap, tetapi data operasional belum tersedia.
- [ ] **BLOCKED_EXTERNAL** — Lakukan face validation dengan minimal satu subject-matter expert dan simpan protokol serta hasil review.
- [ ] **BLOCKED_EXTERNAL** — Bandingkan output baseline dengan KPI sistem nyata atau benchmark tepercaya.
- [x] **DONE_LOCAL** — Lakukan extreme/degenerate engineering tests untuk near-zero demand, overload, staffing boundary, due regimes, exact capacity, empty/single-order, dan rollover; domain-calibrated limits tetap Gate C eksternal.
- [ ] **BLOCKED_EXTERNAL** — Kuantifikasi calibration error dan validation error; executable gate memaksa calibration/validation split, predeclared tolerances, MAE/RMSE/MAPE, dan bootstrap CI, tetapi data belum tersedia.

**Acceptance criteria:** setiap parameter memiliki sumber/justifikasi dan model baseline berada dalam toleransi validasi yang ditetapkan sebelum melihat hasil metode unggulan.

### P1.4 Desain eksperimen yang defensible

- [x] **DONE_LOCAL** — Definisi draft faktor, level, respons primer/sekunder, comparator candidate, dan arah hipotesis tersedia; freeze/approval tetap Gate D.
- [ ] **BLOCKED_EXTERNAL** — Justifikasi ruang parameter secara operasional; hindari level yang tidak realistis.
- [ ] **BLOCKED_EXTERNAL** — Tetapkan baseline final dan benchmark literatur kuat; FTWB+FCFS baru candidate dan seluruh metode memakai CRN/faktor identik.
- [x] **DONE_LOCAL** — Warm-up tidak diterapkan karena model terminating satu shift dengan zero initial state yang disengaja, bukan estimasi steady-state; justifikasi tercatat pada STRESS-DES.
- [x] **DONE_LOCAL** — Lakukan pilot run untuk mengestimasi varians dan menentukan jumlah repetisi berdasarkan target precision/power, bukan angka 30 secara otomatis; 512-run pilot dan precision report tersedia, final freeze menunggu MPID.
- [x] **DONE_LOCAL** — Randomisasikan urutan eksekusi secara deterministik dan simpan seed urutannya pada manifest.
- [ ] **BLOCKED_EXTERNAL** — Confirmatory dan exploratory work dipisahkan dalam draft analysis plan; timestamp freeze/approval PI belum ada.
- [ ] **DECISION_REQUIRED (BE-28)** — Bekukan secondary factors untuk empat konteks Table 6, skema CRN baru, dan desain ablation. Rekomendasi: crossed 2 timing × 3 composition dengan planned contrasts reviewer.
- [ ] **DECISION_REQUIRED (BE-10/BE-28)** — Bekukan tuning/evaluation split untuk kalibrasi F dan V agar benchmark tidak dipilih dan dinilai pada contexts yang sama.
- [ ] **DECISION_REQUIRED (BE-28/BE-30)** — Koreksi klaim Welch menjadi terminating one-shift tanpa warm-up deletion, atau otorisasi perubahan estimand/model dan regenerasi penuh.

**Acceptance criteria:** protokol eksperimen bertanggal tersedia sebelum dataset final dibuat dan setiap pilihan desain memiliki justifikasi.

### P1.5 Metrik operasional yang lengkap

- [x] **DONE_LOCAL** — Laporkan generated, completed, throughput, backlog, service level, late count/rate, tardiness mean/median/tail, cycle time, waiting time, dan picker utilization.
- [x] **DONE_LOCAL** — Bedakan lateness binary dari magnitude of tardiness.
- [x] **DONE_LOCAL** — Laporkan distribusi dan tail metrics, bukan hanya mean.
- [x] **DONE_LOCAL** — Tambahkan utilization per picker/spread untuk mendeteksi ketidakseimbangan.
- [x] **DONE_LOCAL** — Tambahkan cart utilization per trip/batch dan jumlah perjalanan.
- [x] **DONE_LOCAL** — Definisikan denominator setiap KPI secara eksplisit.
- [ ] **TODO_REVIEWER** — Hitung late-order ratio dan on-time rate dari legacy aggregate sebagai derived dataset terpisah dengan checksum sumber.
- [ ] **DECISION_REQUIRED (BE-02/FD-01)** — Average tardiness legacy memerlukan raw `c_i,d_i` dari DOI atau rerun; jangan menjalankan 207.360 run tanpa otorisasi tertulis.
- [ ] **TODO_REVIEWER** — Tambahkan optional per-order output untuk tagged rerun: run/order ID, arrival, due, batch, start, completion, censoring, dan tardiness.

**Acceptance criteria:** semua KPI memiliki formula, unit, scope waktu, denominator, dan test numerik.

---

## P2 — Statistical and reporting rigor

### P2.1 Perbaiki pipeline analisis

- [x] **DONE_LOCAL** — Ubah script top-level menjadi fungsi/CLI yang membaca input dan menulis output ke direktori terpisah.
- [x] **DONE_LOCAL** — Hapus normalisasi per-trigger pada skor multi-objective; gunakan analisis Pareto.
- [x] **DONE_LOCAL** — Tangani kolom konstan, missing values, invalid ranges, dan duplicated keys secara eksplisit.
- [x] **DONE_LOCAL** — Jangan overwrite raw data atau output figure tanpa versioning.
- [x] **DONE_LOCAL** — Buat satu perintah yang meregenerasi seluruh tabel dan gambar dari frozen dataset.
- [x] **DISCOVERY** — Reproduksi root cause composite: Table 4 menormalisasi per sel skenario dengan replikasi dipool, sedangkan narasi menormalisasi delapan mean heuristic global.
- [ ] **DECISION_REQUIRED (BE-11/BE-24/FD-04)** — Bekukan scope normalisasi composite; rekomendasi matched scenario × repetition, reference set delapan metode, composite sekunder dan Pareto primer.
- [ ] **TODO_REVIEWER** — Implementasikan satu fungsi composite, regression fixtures untuk kedua angka lama, corrected Table 4, `ROOT_CAUSE.md`, dan sensitivity bobot 0.6/0.3/0.1; 0.33/0.33/0.33; 0.3/0.6/0.1; 0.3/0.1/0.6.

**Acceptance criteria:** semua angka di manuskrip dapat ditelusuri ke script, dataset hash, dan command yang menghasilkannya.

### P2.2 Gunakan model statistik sesuai desain

- [x] **DONE_LOCAL** — Ganti rangkaian one-way ANOVA dengan model faktorial yang menangkap main effects dan interaksi.
- [x] **DONE_LOCAL** — Pilih family model sesuai outcome: count, proportion, dan continuous outcome; censored survival model menunggu event-level final data bila dibutuhkan.
- [x] **DONE_LOCAL** — Implementasikan Poisson/negative-binomial untuk count dan grouped binomial untuk service level dengan fail-safe constant-outcome handling.
- [x] **DONE_LOCAL** — Perlakukan seed/scenario sebagai blocking atau paired structure saat memakai common random numbers.
- [x] **DONE_LOCAL** — Periksa overdispersion, heteroskedastisitas, independence proxy, model fit, dan catat rank/estimability failures.
- [x] **DONE_LOCAL** — Terapkan koreksi multiplicity Holm pada post-hoc comparisons.
- [x] **DONE_LOCAL** — Lakukan robustness checks menggunakan Poisson versus negative-binomial serta OLS HC3.

**Acceptance criteria:** asumsi model diperiksa dan dilaporkan; inferensi sesuai struktur faktorial serta pairing eksperimen.

### P2.3 Utamakan estimasi, bukan hanya p-value

- [x] **DONE_LOCAL** — Laporkan paired effect size dengan confidence interval untuk setiap perbandingan utama.
- [ ] **BLOCKED_EXTERNAL** — Definisikan minimum practically important difference bersama domain expert.
- [x] **DONE_LOCAL** — Laporkan exact p-values bila digunakan; dokumentasi melarang penyamaan signifikansi statistik dengan kepentingan praktis.
- [x] **DONE_LOCAL** — Sertakan uncertainty interval pada tabel dan grafik.
- [ ] **PENDING_FINAL_DATA** — Laporkan hasil negatif dan hasil yang tidak mendukung hipotesis pada manuskrip final; pipeline tidak menyensor hasil.
- [x] **DONE_LOCAL** — Hindari klaim kausal di luar desain eksperimen simulasi dalam analysis plan/threats.

**Acceptance criteria:** setiap klaim komparatif utama menyertakan magnitude, uncertainty, dan interpretasi operasional.

### P2.4 Sensitivity, uncertainty, dan generalisasi

- [x] **DONE_LOCAL** — One-at-a-time low/base/high sanity sensitivity 13 kasus tersedia dengan directional delta report; interpretasi confirmatory tetap menunggu range tervalidasi.
- [x] **DONE_LOCAL** — Lakukan global sensitivity screening Latin-hypercube untuk parameter input yang tidak pasti; range final menunggu domain validation.
- [x] **DONE_LOCAL** — Pisahkan aleatory uncertainty dari epistemic uncertainty pada desain dan dokumentasi.
- [ ] **BLOCKED_EXTERNAL** — Uji demand, due-time regime, dan picker productivity tersedia; layout/congestion empiris menunggu data, implementasi, dan validasi domain.
- [x] **DONE_LOCAL** — Engineering ablation tooling/pilot untuk komponen DVNS/MPBH tersedia; ini belum menjawab decomposition trigger-versus-composition reviewer.
- [ ] **TODO_REVIEWER** — Setelah BE-25/BE-28 ditutup, refactor pure trigger/composition policies dan jalankan crossed ablation pada subset Table 6 dengan 30 CRN repetitions.
- [ ] **TODO_REVIEWER** — Sweep β={1,2,3,4} pada setiap canonical heuristic yang benar-benar memakai β; laporkan effect/CI serta trade-off batch/trip/runtime.
- [ ] **TODO_REVIEWER** — Sweep FTWB F={60,120,180,240,300,360,480,600} dan VTWB V={4,6,8,10,12,16,20,24}; simpan semua titik dan pilih parameter menurut kriteria yang dibekukan.
- [x] **DONE_LOCAL** — Hasilkan scenario-winner dan Pareto outputs agar wilayah menang/seri/kalah dapat dilaporkan pada data final.

**Acceptance criteria:** kesimpulan menyebutkan domain validitas dan sensitif/tidaknya hasil terhadap asumsi utama.

### P2.5 Pelaporan mengikuti STRESS-DES

- [ ] **BLOCKED_EXTERNAL** — Lengkapi checklist STRESS-DES; objective/logic/implementation selesai, data validation/final results masih eksternal.
- [x] **DONE_LOCAL** — Buat tabel pemetaan setiap item STRESS-DES ke manuskrip, appendix, kode, atau dataset.
- [x] **DONE_LOCAL** — Jelaskan initialization, run length, warm-up, repetitions, RNG, software, hardware, dan execution environment.
- [x] **DONE_LOCAL** — Sediakan deviation log dalam frozen analysis-plan template.
- [x] **DONE_LOCAL** — Tambahkan limitations dan threats to validity: construct, internal, external, dan statistical conclusion validity.

**Acceptance criteria:** tidak ada item STRESS-DES relevan yang kosong tanpa justifikasi.

---

## P3 — Engineering quality dan artifact readiness

### P3.1 Packaging dan environment

- [x] **DONE_LOCAL** — Tambahkan `pyproject.toml` dengan versi Python, dependency ranges, dev dependencies, dan entry points.
- [x] **DONE_LOCAL** — Buat lock file yang dipakai CI dan eksperimen.
- [x] **DONE_LOCAL** — Ubah semua path menjadi berbasis project/config argument, bukan current working directory.
- [x] **DONE_LOCAL** — Tambahkan `.gitignore` untuk cache, output lokal, log, temporary files, dan environment.
- [x] **DONE_LOCAL** — Gunakan semantic versioning dan changelog.
- [x] **DONE_LOCAL** — Tambahkan lisensi kode serta pernyataan lisensi data.

### P3.2 Refactoring dan type safety

- [x] **DONE_LOCAL** — Ganti dictionary order dengan TypedDict contract; historical spaced keys dipertahankan sampai schema v1 migration.
- [x] **DONE_LOCAL** — Pisahkan domain model, simulation engine, experiment runner, metrics/persistence, dan analysis modules.
- [x] **DONE_LOCAL** — Hilangkan duplikasi `main.py` dan `main_nocrash.py`; gunakan satu runner dengan checkpoint/resume tervalidasi.
- [x] **DONE_LOCAL** — Pusatkan parsing/validation konfigurasi; routing lazy-load default hanya saat API legacy dipanggil dan menerima runtime scenario config secara eksplisit.
- [x] **DONE_LOCAL** — Hapus unused imports, dead code, commented-out implementation, dan duplicate methods yang teridentifikasi.
- [x] **DONE_LOCAL** — Pecah probability vector item popularity menjadi file data bernama dan tervalidasi.
- [ ] **TODO_REVIEWER** — Pisahkan pure `TriggerPolicy`/`CompositionRule` dari adapter SimPy, mutasi pools, persistence, dan timing instrumentation; pertahankan compatibility wrapper serta deterministic equivalence tests.

### P3.3 CI dan quality gates

- [x] **DONE_LOCAL** — Tambahkan CI untuk install, lint, type-check, unit/integration tests, coverage, smoke simulation, dan artifact build.
- [x] **DONE_LOCAL** — Jalankan matrix minimal pada Python 3.12 dan 3.14 di workflow.
- [x] **DONE_LOCAL** — Tambahkan schema/config validation dan required-column/range validation untuk CSV.
- [x] **DONE_LOCAL** — Tambahkan audit otomatis: expected runs, uniqueness, failed runs, checksum, ranges, dan invariants.
- [ ] **BLOCKED_EXTERNAL** — Larang merge jika quality gate gagal melalui GitHub branch protection; memerlukan admin repository.

### P3.4 Dokumentasi reviewer-ready

- [x] **DONE_LOCAL** — Tulis README berisi tujuan, quick start, struktur repository, konfigurasi, seed, satu run, full experiment, dan reproduksi figure.
- [x] **DONE_LOCAL** — Sediakan konfigurasi kecil yang selesai dalam beberapa menit untuk reviewer.
- [x] **DONE_LOCAL** — Sediakan konfigurasi penuh dan repeated local benchmark untuk wall/CPU time, CPU utilization, sampled process RSS, Python peak, disk estimate, route/order/picker scaling, dan uncertainty; rerun tagged hardware tetap P4 final-data item.
- [x] **DONE_LOCAL** — Buat troubleshooting dan expected outputs.
- [x] **DONE_LOCAL** — Tambahkan data dictionary dan model parameter/provenance dictionary.
- [x] **DISCOVERY** — Catat discovery reviewer, konflik, root cause composite, hardware kandidat, dependency, dan go/no-go di `outputs/DISCOVERY_NOTES.md`.
- [ ] **TODO_REVIEWER** — Semua runner/function/output baru menyebut reviewer ID, units, seed/config/source hash, generated date, dan menghasilkan ringkasan manuscript-ready.

### P3.5 Artifact archive

- [ ] **BLOCKED_EXTERNAL** — Container/environment menggunakan lock dan official Python 3.12.13 multi-platform digest immutable; build lokal belum dapat dijalankan karena Docker tidak tersedia dan remote CI belum dieksekusi dari worktree ini.
- [ ] **BLOCKED_EXTERNAL** — Publikasikan release archive ke repository persisten ber-DOI bila kebijakan data memungkinkan; memerlukan final release dan otorisasi PI.
- [x] **DONE_LOCAL** — Siapkan struktur source, config, scripts, checksums/manifests, dan artifact appendix; raw/derived final data menunggu Gate E.
- [ ] **BLOCKED_EXTERNAL** — Uji reproduksi dari mesin/environment bersih oleh orang yang bukan pengembang utama.
- [ ] **BLOCKED_EXTERNAL** — Sertifikasi artefak sebagai documented, consistent, complete, exercisable setelah bukti domain validation dan independent review tersedia.

**Acceptance criteria P3:** reviewer baru dapat menghasilkan smoke result dan seluruh figure utama hanya dengan README dan artefak rilis.

---

## P4 — Peningkatan kualitas dan dampak

- [ ] **BLOCKED_EXTERNAL** — Lakukan independent code/model review oleh peneliti kedua dan domain expert.
- [ ] **BLOCKED_EXTERNAL** — Lakukan blinded result reproduction: reviewer internal menerima artefak tanpa bantuan pengembang.
- [ ] **BLOCKED_EXTERNAL** — Bandingkan metode dengan heuristic sederhana dan benchmark literatur/domain kuat; simple candidate ada, tetapi benchmark kuat harus dipilih melalui literature/domain review.
- [x] **DONE_LOCAL** — Analisis kompleksitas teoretis serta engineering benchmark whole-simulation/route terhadap volume, item, dan picker tersedia; belum mencakup decision kernel per trigger yang diminta reviewer.
- [ ] **PENDING_FINAL_DATA** — Laporkan trade-off performa operasional versus biaya komputasi pada release-final benchmark.
- [x] **DONE_LOCAL** — Tambahkan Pareto frontier untuk tujuan konflik tanpa bobot arbitrer.
- [ ] **BLOCKED_EXTERNAL** — Preregister hypotheses dan analysis plan; draft tersedia tetapi registrasi/freeze memerlukan PI/coauthor.
- [x] **DONE_LOCAL** — Tidak ada notebook final; hasil berasal dari script/pipeline deterministik.
- [x] **DONE_LOCAL** — Tambahkan visual uncertainty, interaction, dan Pareto; sensitivity table tersedia.
- [x] **DONE_LOCAL** — Siapkan supplementary material index, pseudocode, parameter provenance, robustness, extreme-condition evidence, dan STRESS mapping; signed validation/final-result files tetap pending external/final data.
- [ ] **BLOCKED_EXTERNAL** — Minta statistical review sebelum submission.
- [x] **DONE_LOCAL** — Buat shortlist berbasis scope/contribution fit untuk SMPT, CAIE, IJPR, dan EJOR beserta Q1 evidence dan policy mapping awal; pemilihan final/limits live tetap memerlukan PI/coauthor.
- [x] **DONE_LOCAL** — Whole-simulation dan route-kernel benchmark berulang tersedia sebagai engineering evidence.
- [ ] **TODO_REVIEWER** — Ukur decision-kernel seluruh delapan metode pada n={10,50,100,500,1000,5000}, kalibrasi timer overhead, dan fit O(1)/O(n)/O(n log n) dengan uncertainty serta fit diagnostics.
- [ ] **AFTER_FINAL_DATA (FD-05)** — Rerun timing pada signed tag dan hardware/protokol yang disetujui; tulis hardware spec dan trade-off operasional-versus-komputasi.

## Revisi mayor EJIE-337519 — urutan implementasi

Item ini mengonsolidasikan brief reviewer; ia tidak membuat blocker BE/FD baru.
Detail teknis dan acceptance criteria tersedia di `outputs/DISCOVERY_NOTES.md`.

1. **GO/NO-GO ilmiah:** tutup keputusan D-01 s.d. D-07 pada worksheet.
2. **P0 fidelity:** selaraskan SNH/DVNS, MPBH, picker availability, config, model specification, dan golden tests.
3. **Core refactor:** pisahkan trigger/composition serta tambahkan per-order writer dan decision timer.
4. **Analysis-first tests:** kunci reproduksi dua composite score lama sebelum menerapkan metode corrected.
5. **Reviewer runners:** ablation, F/V calibration, β sweep, additional metrics, dan scalability; seluruh output ke direktori baru.
6. **Pilot dan statistical review:** validasi contrasts, tuning/evaluation split, timing protocol, serta compute budget.
7. **Tagged execution:** jalankan hanya setelah Gate A–D dan otorisasi rerun lulus.
8. **Claim reconciliation:** bandingkan hasil terhadap Proposisi 1/4, laporkan hasil yang melemahkan klaim, lalu lakukan independent reproduction.

---

## Quality gates menuju submission

### Gate A — Model specification approved

- [ ] **BLOCKED_EXTERNAL** — Research questions, conceptual model, assumptions, algorithms, KPI, dan validation plan disetujui tim peneliti/domain expert.

### Gate B — Implementation verified

- [ ] **BLOCKED_EXTERNAL** — Unit/integration/golden/invariant/trace checks lulus lokal; Gate B tetap menunggu P0.6/tag final dan review orang kedua.

### Gate C — Model validated

- [ ] **BLOCKED_EXTERNAL** — Input evidence, face validation, baseline validation, dan domain-calibrated extreme-condition tests selesai dengan bukti tersimpan.

### Gate D — Experiment preregistered/frozen

- [ ] **BLOCKED_EXTERNAL** — Faktor, level, seed plan, repetitions/power, outcomes, model statistik, exclusions, dan stopping rule dibekukan sebelum final run.

### Gate E — Final data certified

- [ ] **PENDING_FINAL_DATA** — Dataset berasal dari tagged release; 100% run sukses; uniqueness, completeness, checksums, schemas, dan invariants lulus.

### Gate F — Claims reproduced

- [ ] **BLOCKED_EXTERNAL** — Semua tabel/figure diregenerasi otomatis; peneliti kedua berhasil mereproduksi hasil utama pada environment bersih.

### Gate G — Submission-ready

- [ ] **BLOCKED_EXTERNAL** — STRESS-DES lengkap, limitations/transparency statements lengkap, artifact archive tersedia, dan checklist jurnal target lulus.

---

## Urutan eksekusi yang direkomendasikan

1. Karantina dataset lama dan bekukan research questions.
2. Selesaikan seluruh correctness/reproducibility P0.
3. Tulis spesifikasi konseptual dan bangun test oracle/golden cases.
4. Verifikasi software dan validasi model/domain.
5. Bekukan desain eksperimen serta statistical analysis plan.
6. Jalankan pilot, tentukan repetisi, lalu tag release.
7. Jalankan eksperimen final sekali melalui pipeline terkontrol.
8. Sertifikasi data, analisis, sensitivity/robustness, dan independent reproduction.
9. Lengkapi STRESS-DES, artefak, appendix, dan checklist jurnal target.

## Definition of Done global

Sebuah item hanya boleh berstatus `VERIFIED` jika:

- perubahan telah direview oleh orang kedua;
- test/analisis yang relevan tersedia dan lulus;
- bukti tersimpan dalam repository atau manifest artefak;
- dokumentasi dan manuskrip telah diperbarui;
- hasil dapat diulang dari environment bersih;
- tidak ada ketidaksesuaian antara klaim, kode, konfigurasi, data, dan figure.

## Update implementasi kanonik — 2026-08-14

- [x] **DONE_LOCAL** — Bekukan spesifikasi operasional kanonik di
  `docs/OPERATIONAL_DEFINITIONS_CANONICAL_2026-08-14.md`; original paper tidak
  diubah.
- [x] **DONE_LOCAL** — Ganti DVNS dengan SNH; implementasikan MPBH
  EDD+β+capacity+restoration; picker-slot-bounded release, longest-idle-first,
  deterministic tie-break, FCFS/EDT next-fit, dan event-driven wake-up.
- [x] **DONE_LOCAL** — Terapkan order 1–10 lines × 1–10 pieces, due allowance
  integer 30–120 menit, exact ABC profile, 5 s/piece, 180 s/tour, dan geometry
  0.5 m/s.
- [x] **DONE_LOCAL** — Terapkan TLO completed-late + overdue-outstanding,
  per-order censoring records, lower-bound tardiness, run/order checksums, dan
  conservation invariant.
- [x] **DONE_LOCAL** — Kalibrasi O(1)-per-order urgency surrogate pada 10,000
  samples; holdout R² 0.9546 (S-shape) dan 0.9390 (Largest Gap).
- [x] **DONE_LOCAL** — Pilot Welch 24 jam × 10 replikasi menghasilkan warm-up
  5,460 s; overload pilot dideteksi non-stationary dan tidak diberi klaim
  steady-state.
- [x] **DONE_LOCAL** — Reviewer runners tersedia dan smoke-audited: 2×3
  timing/composition, F/V tuning-held-out, β sensitivity, extended censored
  metrics, composite weight sensitivity, dan decision-kernel scaling.
- [x] **DONE_LOCAL** — Representative corrected pilot 96/96 run audit pass;
  450,272 raw-order records. MPBH menang pada 4 konteks Table 6, tetapi angka
  paper berubah material.
- [x] **DONE_LOCAL** — Ablation pilot mengindikasikan composition effect lebih
  besar dari timing effect; Proposition 4 berisiko tidak didukung dan wajib
  diuji dengan 30 repetitions tanpa selective reporting.
- [x] **DONE_LOCAL** — β pilot mengindikasikan β=1 memperbaiki MPBH TLO tetapi
  menambah trips/runtime dan menurunkan cart utilization; β=2 tetap baseline
  sampai held-out/final evidence.
- [x] **DONE_LOCAL** — Quality checks terakhir: Ruff pass, mypy pass, 65 tests
  pass, coverage 93.88%.
- [ ] **PENDING_FINAL_DATA** — Jalankan 30-repetition reviewer experiments dan
  207,360-run factorial dari clean signed tag; pilot tidak boleh dipromosikan
  menjadi final manuscript evidence.
- [ ] **BLOCKED_EXTERNAL** — Domain validation, statistical review,
  clean-machine reproduction, signed release approval, dan manuscript manual
  revision tetap memerlukan pihak berwenang.

## Referensi standar minimum

- STRESS-DES reporting guideline: https://www.equator-network.org/reporting-guidelines/strengthening-the-reporting-of-empirical-simulation-studies-introducing-the-stress-guidelines/
- ACM Artifact Review and Badging policy: https://www.acm.org/publications/policies/artifact-review-and-badging-current
- ASA Statement on Statistical Significance and P-Values: https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf
