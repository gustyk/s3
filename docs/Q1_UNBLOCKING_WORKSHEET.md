# Worksheet Penutupan Item Q1 yang Masih Terbuka

Dokumen ini mencakup tepat **30 item `BLOCKED_EXTERNAL`** dan **6 item
`PENDING_FINAL_DATA`** yang tercatat di `QUALITY_TODO_Q1.md` pada 2026-08-12.
Gunakan dokumen ini sebagai formulir keputusan, pengumpulan bukti, dan serah
terima. Jangan mengubah checkbox sumber menjadi selesai hanya berdasarkan
jawaban informal atau rencana.

## Cara menggunakan worksheet

1. Isi identitas proyek dan penanggung jawab pada bagian metadata.
2. Untuk setiap item, jawab semua pertanyaan dan lampirkan bukti dengan path,
   URL permanen, DOI, checksum, atau nomor dokumen.
3. Keputusan ilmiah harus disetujui PI/coauthor dan, jika disebutkan, domain
   expert atau statistical reviewer.
4. Bukti final-data harus berasal dari clean checkout atas signed/tagged release,
   bukan pilot dengan dirty worktree.
5. Beri tanda `[x]` pada “Konfirmasi penutupan” hanya setelah acceptance criteria
   item tersebut benar-benar terpenuhi dan diverifikasi orang yang berwenang.
6. Setelah verifikasi, salin ringkasan bukti ke `QUALITY_TODO_Q1.md`, ubah status
   item terkait menjadi `DONE`, dan cantumkan tanggal serta verifier.

## Metadata pengisian

- Judul penelitian: Adaptive Heuristics for Order Batching Initiation Timing in Same-Day Delivery Warehouses
- Principal investigator: Ying-Chin Ho
- Corresponding author: Tikno
- Institusi/lokasi studi: National Central University
- Repository/tag target: https://github.com/gustyk/s3.git
- Tanggal mulai pengisian: 12/8/2026
- Koordinator quality gate: Tikno
- Definisi sumber quartile yang diwajibkan institusi (JCR/SJR/tahun): N/A

## Prefill hasil audit paper `2026_EJIE-337519.md`

Audit dilakukan 2026-08-12. Status naskah “accepted dengan major revision”
berasal dari informasi pengguna; decision letter, reviewer reports, dan approval
metadata tidak terdapat di file paper sehingga status editorial tersebut belum
dapat digunakan sebagai evidence quality gate.

### Kesimpulan audit

- Paper memberi **jawaban parsial pada 21 item** dan **tidak memberi evidence
  relevan pada 15 item**.
- **Tidak ada satu pun dari 36 item yang dapat ditutup hanya dengan paper ini.**
  Sebagian item memerlukan identitas/approval, raw evidence, audit, atau tagged
  release; sebagian lain bertentangan dengan codebase yang sekarang diaudit.
- Paper mengklaim 6.912 scenario × 30 repetitions = 207.360 runs (baris 417–428
  dan 695). Angka dan seluruh statistik Table 4 cocok dengan dataset
  `data/legacy/simulation_results_legacy_unverified.csv` hingga pembulatan.
- Baris `DVNS` di dataset legacy dilaporkan sebagai `SNH` di paper.
- Dataset legacy tidak dapat disertifikasi: terdapat 72 duplicate `run_id`, ID
  185761–186160 hilang, tidak ada seed/config/source hash, MPBH tidak dapat
  dieksekusi source asal, DVNS–FCFS menjalankan EDT, dan routing tidak diteruskan
  ke urgency calculation. Lihat `data/legacy/MANIFEST.md`.
- Rekalkulasi langsung atas 207.360 baris legacy menghasilkan nilai berikut;
  semuanya sama dengan Table 4 setelah pembulatan (throughput dihitung sebagai
  mean `total_orders / 8`):

| Label data | Label paper | Mean TLO | SD TLO | Throughput/jam | Mean utilization |
|---|---|---:|---:|---:|---:|
| DVNS | SNH | 1,401.0370 | 2,326.1068 | 135.9786 | 84.2870 |
| FTWB | FTWB | 1,036.6030 | 1,967.1680 | 203.6202 | 52.9745 |
| MPBH | MPBH | 829.4530 | 1,698.1701 | 187.1949 | 84.1849 |
| MaxCart | MaxCart | 987.6954 | 1,915.6225 | 208.1571 | 49.3802 |
| MaxPicker | MaxPicker | 1,001.7694 | 1,944.3234 | 208.9542 | 83.9904 |
| UrgentCart | UrgentCart | 1,716.2418 | 2,297.4814 | 122.2118 | 70.6395 |
| UrgentPicker | UrgentPicker | 1,040.8538 | 1,963.2691 | 202.2788 | 54.7736 |
| VTWB | VTWB | 1,237.2358 | 2,112.1233 | 180.7151 | 56.4613 |

- DOI Mendeley `10.17632/49r2pmymrm.1` disebut paper (baris 943–945), tetapi
  paper tidak mencantumkan file inventory, checksums, source tag, manifest, atau
  audit report. Verifikasi metadata API dari workspace ini menghasilkan HTTP
  401, sehingga hanya keberadaan klaim DOI yang dapat dicatat.
- Pelaporan composite score tidak konsisten di dalam paper: Table 4 memberi
  MPBH `0.864`, FTWB `0.725`, dan VTWB `0.682`, tetapi paragraf sesudah tabel
  memberi MPBH `0.924`, FTWB `0.752`, dan VTWB `0.547` (baris 472–505).
- Pelaporan effect size juga tidak konsisten: Table 5 memberi partial
  eta-squared `0.396` untuk efek utama trigger dan `0.502` untuk interaksi
  tiga-arah, sedangkan pembahasan mengatribusikan `0.396` kepada interaksi
  tiga-arah (baris 792–870). Keduanya perlu dihitung ulang dari data final yang
  sudah direkonsiliasi.

| Ringkasan pasca-audit | Jumlah | Status operasional |
|---|---:|---|
| `BLOCKED_EXTERNAL` terjawab penuh | 0/30 | seluruh 30 tetap terbuka |
| `BLOCKED_EXTERNAL` terjawab sebagian | 17/30 | perlu bukti/keputusan tambahan |
| `BLOCKED_EXTERNAL` tidak terjawab | 13/30 | perlu masukan eksternal lengkap |
| `PENDING_FINAL_DATA` terjawab penuh | 0/6 | seluruh 6 tetap terbuka |
| `PENDING_FINAL_DATA` terjawab sebagian | 4/6 | perlu artefak final/rekonsiliasi |
| `PENDING_FINAL_DATA` tidak terjawab | 2/6 | perlu artefak final lengkap |

### Konflik paper versus release-candidate code/config

| Elemen | Paper | Code/config saat ini | Konsekuensi |
|---|---|---|---|
| Advanced heuristic | `SNH` + MPBH (baris 54–56, 625–694) | `DVNS` + MPBH | equivalence label/algorithm belum dibuktikan |
| FTWB interval | 360 s (baris 541–558) | 720 s di `config/parameters.yaml` | hasil paper tidak berasal dari config saat ini |
| Pick time | 5 s/item (baris 378–393) | 3 s/item | parameter mismatch |
| Setup time | 30 s/trip (baris 394–399) | 180 s/trip | parameter mismatch |
| Order size | discrete uniform 1–10 (baris 375–380) | non-uniform 0.30/0.25/0.22/0.17/… | stochastic input mismatch |
| Warm-up | ditentukan Welch (baris 428–429), tanpa nilai | terminating one-shift model, zero initial state, tanpa deletion | stopping/analysis mismatch |
| Validation | klaim three-phase validation (baris 433–436) | tidak ada signed/domain/operational evidence | klaim belum dapat diaudit |
| Final runs | 207.360 (baris 13, 424, 695) | hanya pilot current-tree 512 runs | paper menunjuk legacy, bukan tagged final release |
| Composite score | weighted normalization 0.6/0.3/0.1 (baris 480–533) | publication pipeline memakai Pareto | estimand/analysis mismatch |
| Statistical model | ANOVA + Tukey (baris 735–846) | factorial count/binomial/HC3 + CRN/Holm | inference pipeline mismatch |

### Pemetaan 36 item

`PARSIAL-KONFLIK` berarti paper memberi angka/klaim tetapi evidence berasal dari
atau konsisten dengan legacy dataset yang tidak tersertifikasi. `PARSIAL` berarti
informasi dapat diprefill namun acceptance criteria tetap membutuhkan evidence
lain. `TIDAK ADA` berarti paper tidak menjawab requirement.

| ID | Status dari paper | Jawaban/evidence yang dapat diprefill | Yang masih diperlukan |
|---|---|---|---|
| BE-01 | TIDAK ADA | Tidak ada tag, commit, config hash, clean-state, atau release approval | seluruh evidence BE-01 |
| BE-02 | PARSIAL-KONFLIK | Klaim 207.360 runs/6.912 scenario/30 repetitions (baris 13, 417–428, 695) | command, tag, config hash, environment, empty output, exit code; regenerate karena cocok legacy |
| BE-03 | PARSIAL | Literature assumptions: HPP, ABC, order size, due allowance, walking/pick/routing (baris 370–381); WMS fields order pool/due time/picker status (baris 925–930) | sumber operasional, owner, periode, sample, rights |
| BE-04 | TIDAK ADA | Tidak ada query, checksum, missingness, cleaning, outlier, timezone, atau split | extraction report |
| BE-05 | TIDAK ADA | Distribusi ditetapkan sebagai asumsi; tidak ada fitting/AIC/BIC/KS/held-out likelihood | raw inputs dan fit report |
| BE-06 | PARSIAL | Klaim conceptual validation oleh domain experts dan face validity (baris 433–436) | identitas SME, minutes, findings, resolution, signed decision |
| BE-07 | PARSIAL | Klaim operational validation terhadap “known results” (baris 433–436) | benchmark source, observed KPI, tolerance, numerical report |
| BE-08 | TIDAK ADA | Tidak ada calibration/validation split atau MAE/RMSE/MAPE/CI | input, frozen tolerances, report |
| BE-09 | PARSIAL | Arrival 0.5–16, pickers 1–12, FCFS/EDT, carts 100/150/200, S-shape/Largest Gap (baris 417–424); due 30–120 min, pick 5 s, walk 0.5 m/s (baris 375–380) | operational/SME approval dan rekonsiliasi config |
| BE-10 | PARSIAL | FTWB/VTWB literature baselines; F=360, V=12; paper mengakui tidak dituning dan mungkin konservatif (baris 541–562) | strong benchmark, oracle, fair tuning; paper meminta MIP/SOTA (baris 932–937) |
| BE-11 | PARSIAL | RQ utama (baris 43–47), empat propositions (baris 224–244), outcomes/results | preregistration/freeze, exclusions, multiplicity, exploratory labels |
| BE-12 | TIDAK ADA | Tidak ada MPID; 27,04% adalah observed result, bukan threshold prespecified | elicitation SME/PI dan freeze |
| BE-13 | PARSIAL | Tidak memodelkan congestion/blocking; NHPP/congestion adalah future work (baris 908–937) | data, model, tests, scenarios, validation |
| BE-14 | PARSIAL | Objective, logic, factors, metrics, assumptions, limitations, dan data DOI tersedia | completed STRESS-DES map dan final evidence |
| BE-15 | TIDAK ADA | Tidak ada branch-protection evidence | admin action/settings evidence |
| BE-16 | TIDAK ADA | Python/SimPy disebut (baris 428), tanpa version/lock/image/build/test/scan | container evidence |
| BE-17 | PARSIAL | Data Availability menyebut DOI `10.17632/49r2pmymrm.1` (baris 943–945) | inventory, rights, checksums, source/config, audit, download verification |
| BE-18 | TIDAK ADA | Tidak ada clean-machine independent reproduction | reviewer/environment/logs/checksums |
| BE-19 | TIDAK ADA | Tidak ada artifact-evaluation record | evaluator dan criterion evidence |
| BE-20 | PARSIAL | Klaim domain experts dan systematic code testing (baris 433–436) | identities, tagged commit, issues/resolutions, signed review |
| BE-21 | TIDAK ADA | Tidak ada blinded reproduction | protocol/result evidence |
| BE-22 | PARSIAL-KONFLIK | FTWB/VTWB comparison dan negative UrgentCart result; strong benchmark belum dilakukan (baris 789–799, 932–937) | certified data, strong comparator, oracle, fair CRN/tuning, cost |
| BE-23 | TIDAK ADA | Tidak ada registration URL/timestamp/hash | preregistration evidence |
| BE-24 | TIDAK ADA | ANOVA/Tukey bukan evidence independent statistical review | reviewer identity, pre/post review, signed decisions |
| BE-25 | PARSIAL | RQ/model/assumptions/algorithms/KPI/validation claim ditulis | signed team/SME approval, versions/hashes, issue closure |
| BE-26 | PARSIAL | Klaim computational verification/systematic tests (baris 433–436) | clean tag, CI/container logs, coverage/audit, second review |
| BE-27 | PARSIAL | Klaim three-phase validation (baris 433–436) | evidence bundle BE-03–BE-09; numerical validation tidak ada |
| BE-28 | PARSIAL-KONFLIK | Factorial 6.912, 30 reps, 8-hour horizon, factors/levels (baris 417–432) | seed/CRN, power/MPID, freeze/config hash; reconcile warm-up/config/data |
| BE-29 | TIDAK ADA | Tidak ada independent regenerated tables/figures/checksums | Gate F evidence |
| BE-30 | PARSIAL | User menyatakan EJIE major revision; paper memberi Data Availability dan no-conflict statement (baris 943–949) | decision letter, journal guide, STRESS-DES, DOI verification, AI/funding/ethics, approval |
| FD-01 | PARSIAL-KONFLIK | Expected 6.912 × 30 = 207.360 disebut | matching legacy gagal integrity/provenance; tagged regeneration required |
| FD-02 | PARSIAL-KONFLIK | Mendeley DOI diklaim sebagai open simulation results | immutable bundle/checksum/source linkage belum terbukti |
| FD-03 | TIDAK ADA | Tidak ada manifest, hashes, seed map, status, atau audit report | manifest/audit bundle |
| FD-04 | PARSIAL-KONFLIK | Proposition 2 partial; UrgentCart buruk; FCFS/EDT null; limitations dilaporkan (baris 759–856, 908–941) | certified analysis, effect/CI table, all hypotheses, reviewer confirmation |
| FD-05 | PARSIAL | Complexity O(1)/O(n)/O(n log n) dibahas (Section 4; baris 925–930) | tagged runtime/CPU/RSS/disk dan operational trade-off |
| FD-06 | TIDAK ADA | Tidak ada signed tag, strict pass, immutable raw evidence, atau signatures | FD-01–FD-03 dan approval |

### Sisa yang belum dijawab penuh oleh paper

**Tanpa jawaban/bukti substantif (15 item):** BE-01, BE-04, BE-05, BE-08,
BE-12, BE-15, BE-16, BE-18, BE-19, BE-21, BE-23, BE-24, BE-29, FD-03, dan
FD-06.

**Terjawab sebagian tetapi belum dapat ditutup (21 item):** BE-02, BE-03,
BE-06, BE-07, BE-09, BE-10, BE-11, BE-13, BE-14, BE-17, BE-20, BE-22, BE-25,
BE-26, BE-27, BE-28, BE-30, FD-01, FD-02, FD-04, dan FD-05. Kekurangan spesifik
untuk masing-masing item tercantum pada kolom **Yang masih diperlukan** di tabel
pemetaan.

**Konsekuensi:** audit paper tidak mengubah status keseluruhan—30 item
`BLOCKED_EXTERNAL` dan 6 item `PENDING_FINAL_DATA` masih terbuka. Informasi
paper dapat dipakai sebagai prefill, tetapi penutupan memerlukan jawaban
eksplisit, artefak audit, atau output final yang disebut pada setiap kartu.

### Konfirmasi tambahan dari brief revisi mayor reviewer

Brief teknis reviewer diaudit pada 2026-08-12 dan discovery lengkap tersedia di
`outputs/DISCOVERY_NOTES.md`. Item berikut **bukan blocker baru**; semuanya
dipetakan ke BE/FD yang sudah ada agar jumlah tetap tepat 30 + 6. Isi kolom
jawaban/konfirmasi sebelum implementasi eksperimen reviewer dimulai.

| Decision | Dipetakan ke | Temuan dan rekomendasi | Jawaban/konfirmasi tim |
|---|---|---|---|
| D-01 — Label dan algoritme SNH/DVNS | BE-25, BE-28 | Paper memakai SNH, code memakai DVNS; sahkan nama dan pseudocode kanonik | **DIJAWAB 2026-08-14:** DVNS dihapus; SNH paper menjadi kanonik dan telah diimplementasikan |
| D-02 — Algoritme MPBH kanonik | BE-25, BE-28 | MPBH paper memakai EDD + constraint β + feasibility restoration; current code memakai slack-per-item + route time | **DIJAWAB 2026-08-14:** MPBH paper kanonik; EDD+β+capacity+deterministic restoration telah diimplementasikan |
| D-03 — Nasib legacy vs regenerasi | BE-02, FD-01, FD-02 | Legacy cocok dengan paper tetapi tidak tersertifikasi; rekomendasi: historical-only dan regenerate setelah freeze | **DIJAWAB 2026-08-14:** legacy historical-only; rerun model terkoreksi diotorisasi, tanpa klaim identik dengan legacy |
| D-04 — Scope normalisasi composite | BE-11, BE-24, FD-04 | Table 4 dan narasi memakai scope berbeda; rekomendasi: matched scenario × repetition, composite sekunder, Pareto primer | **DIJAWAB 2026-08-14:** matched scenario×repetition; constant tie=0.5; Pareto primary; weight sensitivity wajib |
| D-05 — Secondary factors subset Table 6 | BE-28 | Pilih semua 2 batching × 3 cart × 2 routing atau satu baseline yang dijustifikasi | **DIJAWAB 2026-08-14:** core Table-6 reviewer contrast menahan FCFS/C100/S-shape; robustness config menguji cart/routing levels terpisah |
| D-06 — Seed eksperimen reviewer | BE-28 | Seed legacy tidak tersedia; setujui skema CRN current sebagai seed baru, tanpa klaim identik dengan run lama | **DIJAWAB 2026-08-14:** SHA-256 CRN dari master seed×arrival-level×repetition; seed dan hash dipersisten |
| D-07 — Warm-up/terminating model | BE-28, BE-30 | Tidak ada Welch di code; rekomendasi koreksi paper menjadi terminating 8-hour shift tanpa warm-up deletion | **DIJAWAB 2026-08-14:** Welch 24h merekomendasikan 5,460 s; overload ditafsir finite-horizon/non-stationary, bukan steady state |
| D-08 — Inventory DOI Mendeley | BE-17 | Sediakan file list, size, checksum, license, dan bukti mapping ke file lokal | ______________________________ |
| D-09 — Otorisasi rerun untuk tardiness | BE-02, FD-01 | Raw per-order legacy tidak ada; average tardiness memerlukan raw DOI atau rerun yang disetujui | **DIJAWAB 2026-08-14:** user menugaskan rerun; raw completed dan censored outstanding wajib dipersisten |
| D-10 — Hardware/protokol timing final | FD-05 | Kandidat: HP EliteDesk 800 G3, i7-7700, 4C/8T, RAM ~31.9 GiB, Windows 11, Python 3.14.6 | **KEPUTUSAN AHLI:** perf_counter_ns, adaptive calls, overhead subtraction, GC off, 30 repeats; rerun pada signed tag tetap FD-05 |

**Approval PI/coauthors atas D-01 s.d. D-07:**

- Nama approver: ____________________________________________________
- Tanggal/nomor keputusan: __________________________________________
- Path/URL bukti bertanda tangan: ___________________________________
- Hash config/specification freeze: __________________________________
- [ ] Konfirmasi bahwa eksperimen reviewer boleh dimulai setelah Gate B lulus

**Catatan biaya/otorisasi D-09:**

- Raw order data ditemukan di: ______________________________________
- Jika tidak ada, rerun yang diizinkan (subset/full): _________________
- Batas waktu/compute budget: _______________________________________
- Release operator: __________________________________________________
- [ ] Otorisasi eksplisit rerun besar; kotak kosong berarti **jangan rerun**

### Prefill substantif dari paper

- **Primary research question:** strategi timing optimal untuk memulai online
  batching guna meminimalkan total late orders pada SDD (baris 43–47).
- **Propositions:** adaptive versus static; robustness; context-dependent
  ranking; timing versus composition (baris 224–244).
- **Candidate baselines:** FTWB dan VTWB; parameter tidak dituning dan comparison
  mungkin konservatif (baris 541–562).
- **Paper outcomes:** Total Late Orders, throughput, picker utilization (baris
  437–477).
- **Claimed factor matrix:** 8 × 6 × 12 × 2 × 3 × 2 = 6.912 (baris 417–424).
- **Negative/non-supportive findings:** Proposition 2 partial; UrgentCart gagal;
  FCFS versus EDT tidak signifikan; no universal robust method; HPP/no congestion
  membatasi external validity (baris 759–856, 908–924).
- **Strong-benchmark gap:** MIP optimum dan state-of-the-art scheduling masih
  future work (baris 932–937).
- **Data/COI:** Mendeley DOI `10.17632/49r2pmymrm.1`; authors declare no conflict
  (baris 943–949).

---

# A. BLOCKED_EXTERNAL — 30 item

## BE-01 — Otorisasi tag rilis model

**Tujuan:** membuat tag rilis sebelum eksperimen final setelah Gate A–D lulus.

**Instruksi penutupan:**

1. Pastikan keputusan Gate A–D ditandatangani dan seluruh CI lulus.
2. Bekukan config final dan catat SHA-256-nya.
3. Pastikan `git status --porcelain` kosong.
4. Buat signed semantic-version tag dan catat commit SHA.

**Bukti minimum:** keputusan release, output clean-state, tag, commit SHA, config
hash, dan URL release.

- PI pemberi otorisasi: Ying-Chin Ho (Anda isikan isian di bawah ini setelah saya berikan repo di atas)
- Versi/tag: ____________________ Commit SHA: ________________________
- Config final/path/SHA-256: ________________________________________
- Bukti Gate A–D: ___________________________________________________
- URL/bukti signed tag: _____________________________________________
- Tanggal dan catatan: ______________________________________________
- [ ] Konfirmasi penutupan oleh PI/release owner

## BE-02 — Menjalankan eksperimen final dari direktori kosong

**Instruksi penutupan:** jalankan `RELEASE_RUNBOOK.md` dari clean checkout tag
BE-01, gunakan config/repetitions yang dibekukan, dan targetkan direktori baru
yang terbukti kosong. Jangan menghapus atau memakai ulang output lama.

**Bukti minimum:** command lengkap, tag/commit, config hash, environment/image
digest, path awal kosong, start/end UTC, exit code, dan output path.

- Release operator: Tikno (anda lakukan sendiri dan akan saya review hasilnya)
- Command: __________________________________________________________
- Tag/commit/config hash: ___________________________________________
- Container/environment digest: _____________________________________
- Bukti direktori awal kosong: ______________________________________
- Start/end UTC dan exit code: ______________________________________
- Output final: _____________________________________________________
- [ ] Konfirmasi penutupan oleh release operator dan verifier

## BE-03 — Identifikasi sumber data operasional

**Instruksi penutupan:** gunakan `OPERATIONAL_DATA_SCHEMA.md`; identifikasi
sumber untuk arrival, order size/quantity, item popularity, due time, layout,
walking speed/time, picking time, setup time, staffing, dan KPI baseline.

**Bukti minimum:** data owner, source system/table/query, periode, unit, sample
size, izin penggunaan, dan cakupan parameter.

| Parameter | Source system/table | Periode | Unit/n | Data owner | Hak akses |
|---|---|---|---|---|---|
| Arrival |  |  |  |  |  |
| Order size/quantity |  |  |  |  |  |
| Item popularity |  |  |  |  |  |
| Due time |  |  |  |  |  |
| Layout/travel |  |  |  |  |  |
| Pick/setup time |  |  |  |  |  |
| Staffing/KPI |  |  |  |  |  |

- Kesenjangan data yang diterima: ___________________________________
- [ ] Konfirmasi kelengkapan oleh data owner dan PI

## BE-04 — Dokumentasi provenance dan cleaning data

**Instruksi penutupan:** untuk setiap extract BE-03, dokumentasikan query/version,
timezone, checksum raw, duplicate handling, missingness, exclusions, outlier
rule, unit conversion, confidentiality, dan calibration/validation split.

- Extraction report/path: ___________________________________________
- Raw file checksums: _______________________________________________
- Timezone/DST rule: ________________________________________________
- Missing/duplicate policy: _________________________________________
- Outlier/exclusion policy dan kapan ditetapkan: _____________________
- Calibration period: __________ Validation period: _________________
- Data limitations: __________________________________________________
- [ ] Konfirmasi oleh data steward dan statistical reviewer

## BE-05 — Estimasi distribusi input

**Instruksi penutupan:** siapkan CSV `parameter,value,split`; jalankan
`python -m src.input_analysis ...`; tinjau AIC/BIC, KS, held-out likelihood,
grafik diagnostik, dan plausibilitas domain. Jangan memilih model dari validation
performance lalu mengklaim validation tetap held-out.

- Input CSV/path/SHA-256: ____________________________________________
- Command dan output report: ________________________________________
- Distribusi terpilih per parameter: _________________________________
- Alasan statistik dan domain: ______________________________________
- Fit yang ditolak dan alasannya: ___________________________________
- Reviewer/tanggal: __________________________________________________
- [ ] Konfirmasi oleh statistician dan domain expert

## BE-06 — Face validation dengan subject-matter expert

**Instruksi penutupan:** jalankan `DOMAIN_REVIEW_PROTOCOL.md` tanpa menunjukkan
ranking metode terlebih dahulu; catat setiap material defect, owner, resolusi,
dan retest.

- Nama/peran/pengalaman SME: _________________________________________
- Tanggal dan peserta: ______________________________________________
- Minutes/path: ______________________________________________________
- Defect dan resolusi: ______________________________________________
- Validity domain yang disetujui: ___________________________________
- Keputusan: [ ] accepted [ ] conditionally accepted [ ] rejected
- [ ] Tanda tangan/konfirmasi SME dan PI tersedia

## BE-07 — Validasi baseline terhadap KPI nyata/benchmark tepercaya

**Instruksi penutupan:** bekukan KPI, denominator, tolerance, dan validation
period sebelum perbandingan; jalankan baseline pada kondisi yang sepadan dan
laporkan seluruh pass/fail.

- Baseline final: ___________________________________________________
- KPI dan formula: __________________________________________________
- Validation period/sample: _________________________________________
- Tolerance prespecified: ___________________________________________
- Observed versus simulated report: _________________________________
- Benchmark citation/data source: ___________________________________
- Keputusan dan limitation: _________________________________________
- [ ] Konfirmasi oleh SME, statistician, dan PI

## BE-08 — Kuantifikasi calibration dan validation error

**Instruksi penutupan:** buat input untuk `src.validation`, tetapkan toleransi
sebelum membuka held-out output, lalu laporkan bias, MAE, RMSE, MAPE, bootstrap
CI, serta semua pelanggaran tolerance.

- Input/path/SHA-256: ________________________________________________
- Tolerance JSON/path dan freeze timestamp: __________________________
- Command/report: ___________________________________________________
- Calibration result: _______________________________________________
- Held-out validation result: _______________________________________
- Pelanggaran dan tindakan: _________________________________________
- [ ] Konfirmasi oleh statistician, SME, dan PI

## BE-09 — Justifikasi ruang parameter secara operasional

**Instruksi penutupan:** untuk setiap factor level dan sensitivity range, tautkan
ke evidence BE-03–BE-08 atau elicitation SME. Nyatakan level di luar validity
domain dan jangan mempertahankan level hanya karena memberi hasil menarik.

| Faktor/input | Level/range final | Evidence | Validity domain | Approver |
|---|---|---|---|---|
| Arrival |  |  |  |  |
| Pickers |  |  |  |  |
| Cart capacity |  |  |  |  |
| Due allowance |  |  |  |  |
| Pick/setup/walk |  |  |  |  |
| Layout/congestion |  |  |  |  |

- [ ] Konfirmasi oleh SME dan PI

## BE-10 — Tetapkan baseline final dan benchmark kuat

**Instruksi penutupan:** lakukan literature/domain review; pilih minimal satu
heuristic sederhana dan satu comparator kuat; verifikasi implementasi dengan
published example atau oracle; dokumentasikan deviasi secara adil.

- Search protocol/database/date: ____________________________________
- Simple baseline: __________________ Justifikasi: ___________________
- Strong benchmark: _________________ Citation/DOI: __________________
- Implementation oracle/test: _______________________________________
- Deviasi dari publikasi asli: ______________________________________
- Conflict/fairness check: __________________________________________
- [ ] Konfirmasi oleh OR reviewer, SME, dan PI

## BE-11 — Freeze confirmatory versus exploratory analysis

**Instruksi penutupan:** selesaikan `ANALYSIS_PLAN.md`, tandai outcomes,
contrasts, models, exclusions, multiplicity, stopping rule, dan exploratory work;
buat timestamp/registration yang tidak dapat diedit diam-diam.

- Registry/repository: ______________________________________________
- Freeze timestamp dan version/hash: _________________________________
- Confirmatory hypotheses: __________________________________________
- Exploratory analyses: _____________________________________________
- Approved deviations mechanism: ___________________________________
- PI/coauthor approvals: ____________________________________________
- [ ] Konfirmasi freeze sebelum final run

## BE-12 — Definisikan MPID

**Instruksi penutupan:** sepakati minimum practically important difference untuk
primary outcome dari kebutuhan operasi/cost/risk, bukan dari pilot effect size;
nyatakan unit, arah, konteks, dan justifikasi.

- Primary outcome: __________________________________________________
- MPID dan unit: ____________________________________________________
- Arah/decision consequence: ________________________________________
- Evidence/elicitation method: ______________________________________
- SME: __________________________ PI: _________________________________
- Freeze timestamp: __________________________________________________
- [ ] Konfirmasi MPID sebelum repetitions/final run dibekukan

## BE-13 — Layout dan congestion scenarios empiris

**Instruksi penutupan:** peroleh topology/layout efektif dan bukti congestion;
implementasikan hanya mekanisme yang didukung, verifikasi dengan oracle, lalu
uji demand, due regime, productivity, layout, dan congestion pada range BE-09.

- Layout source/version: _____________________________________________
- Congestion observations/model: ____________________________________
- Implementasi dan tests: ___________________________________________
- Scenario matrix/config: ___________________________________________
- Validation evidence: ______________________________________________
- Limitations: _______________________________________________________
- [ ] Konfirmasi oleh SME dan verifier

## BE-14 — Lengkapi STRESS-DES

**Instruksi penutupan:** isi seluruh baris `STRESS_DES_CHECKLIST.md` memakai
bukti final; setiap item tidak relevan harus memiliki justifikasi. Reconcile
dengan manuscript, appendix, data/code availability, dan deviation log.

- Checklist version/path: ___________________________________________
- Item yang masih N/A dan justifikasi: _______________________________
- Manuscript mapping: _______________________________________________
- Reviewer: ________________________ Tanggal: _________________________
- Open discrepancy: __________________________________________________
- [ ] Tidak ada item relevan kosong tanpa justifikasi

## BE-15 — GitHub branch protection

**Instruksi penutupan:** admin mengaktifkan protection/ruleset pada default
branch: PR required, required quality workflow checks, stale approval dismissal,
conversation resolution, dan larangan bypass yang tidak terdokumentasi.

- Repository/default branch: ________________________________________
- Admin: _____________________________________________________________
- Required checks: __________________________________________________
- Ruleset URL/export/screenshots: ___________________________________
- Bypass actors dan alasan: _________________________________________
- Test PR yang diblokir saat check gagal: ____________________________
- [ ] Konfirmasi oleh repository admin

## BE-16 — Build dan exercise container

**Instruksi penutupan:** pada CI/host dengan Docker, build digest-pinned image,
jalankan test dan reviewer smoke, audit output, serta scan image. Catat host,
Docker version, image digest, logs, dan vulnerability disposition.

- Host/OS/architecture: ______________________________________________
- Docker version: ___________________________________________________
- Build command/log: ________________________________________________
- Image digest: _____________________________________________________
- Test/smoke/audit logs: ____________________________________________
- Security scan dan accepted risks: _________________________________
- [ ] Konfirmasi oleh CI/release operator

## BE-17 — Publikasi archive ber-DOI

**Instruksi penutupan:** setelah final release diterima, unggah source, config,
raw/derived data sesuai hak akses, checksums, docs, dan environment ke Zenodo/
OSF/institutional repository; mint DOI dan verifikasi download.

- Repository/archive owner: _________________________________________
- Access mode/data restrictions: ____________________________________
- Release URL/DOI: __________________________________________________
- Archive checksum: __________________________________________________
- Downloaded checksum verification: _________________________________
- Versioning/embargo terms: _________________________________________
- [ ] Konfirmasi oleh PI dan archive owner

## BE-18 — Clean-machine reproduction

**Instruksi penutupan:** peneliti yang bukan developer utama mengikuti README/
appendix pada mesin bersih, tanpa bantuan sinkron, untuk build, tests, smoke,
audit, dan regenerasi figures.

- Reviewer dan independence statement: ______________________________
- Machine/environment: ______________________________________________
- Start/end time: ___________________________________________________
- Commands dan logs: ________________________________________________
- Checksums versus expected: ________________________________________
- Assistance/discrepancies: _________________________________________
- [ ] Konfirmasi reproduksi oleh reviewer independen

## BE-19 — Sertifikasi artifact evaluation criteria

**Instruksi penutupan:** evaluator menilai documented, consistent, complete,
exercisable, dan validation-supported menggunakan release artifact, bukan
worktree pengembang.

| Criterion | Pass/fail | Evidence | Defect/resolution |
|---|---|---|---|
| Documented |  |  |  |
| Consistent |  |  |  |
| Complete |  |  |  |
| Exercisable |  |  |  |
| Validation-supported |  |  |  |

- Evaluator/date/decision: __________________________________________
- [ ] Seluruh criterion lulus atau deviation diterima tertulis

## BE-20 — Independent code/model review

**Instruksi penutupan:** peneliti kedua dan domain expert mengulas tagged source,
model specification, algorithms, invariants, assumptions, dan issue resolution.

- Reviewer identities/qualifications: _______________________________
- Commit/tag reviewed: ______________________________________________
- Review record/issues: _____________________________________________
- Critical/major issues resolved at commit: _________________________
- Residual limitations: _____________________________________________
- Decision/date: ____________________________________________________
- [ ] Konfirmasi oleh kedua reviewer dan PI

## BE-21 — Blinded result reproduction

**Instruksi penutupan:** reviewer menerima artifact dan preregistered claims
tanpa ranking jawaban/author coaching; reviewer mereproduksi main claims dan
mencatat tolerance serta semua assistance.

- Reviewer/blinding procedure: ______________________________________
- Artifact version: __________________________________________________
- Claims/tolerance supplied: ________________________________________
- Reproduced results/checksums: _____________________________________
- Assistance/unblinding event: ______________________________________
- Decision: _________________________________________________________
- [ ] Konfirmasi blinded reproduction

## BE-22 — Benchmark heuristic/literatur kuat

**Instruksi penutupan:** jalankan comparator BE-10 dengan CRN, factor space,
horizon, resources, tuning budget, dan KPI yang sama; laporkan win/tie/loss,
uncertainty, dan computational cost.

- Comparator versions/configs: ______________________________________
- Fairness/tuning budget: ___________________________________________
- Paired design evidence: ___________________________________________
- Effect/CI/win-tie-loss report: ____________________________________
- Computational comparison: ________________________________________
- Negative results: __________________________________________________
- [ ] Konfirmasi oleh OR reviewer dan statistician

## BE-23 — Preregistrasi hypotheses dan analysis plan

**Instruksi penutupan:** preregister versi BE-11 pada registry publik atau
timestamped institutional repository sebelum final run; sertakan hashes dan
deviation policy.

- Registry: _________________________________________________________
- Registration URL/DOI: _____________________________________________
- Timestamp: __________________ Version/hash: ________________________
- Embargo (jika ada): _______________________________________________
- Coauthor approval: ________________________________________________
- [ ] Registrasi terjadi sebelum final dataset dibuat

## BE-24 — Statistical review

**Instruksi penutupan:** statistician meninjau desain sebelum final run dan
meninjau diagnostics/inference setelah final data tanpa mengubah hypotheses
secara retroaktif.

- Reviewer qualifications/conflicts: ________________________________
- Pre-run review/date: ______________________________________________
- Models/pairing/multiplicity comments: ______________________________
- Post-run diagnostics review: ______________________________________
- Required changes/deviations: ______________________________________
- Final decision/signature: _________________________________________
- [ ] Konfirmasi statistical review lengkap

## BE-25 — Gate A: model specification approved

**Instruksi penutupan:** tim dan SME menyetujui research questions, intended use,
conceptual model, assumptions, algorithms, KPI, dan validation plan setelah
semua issue BE-06/BE-20 diselesaikan.

- Approved document versions/hashes: ________________________________
- Open accepted assumptions: ________________________________________
- Team approvals: ___________________________________________________
- SME approval: _____________________________________________________
- Date/decision record: _____________________________________________
- [ ] Gate A approved

## BE-26 — Gate B: implementation verified

**Instruksi penutupan:** pada clean tagged release, second reviewer memverifikasi
P0 selesai, tests/coverage/static gates, golden traces, smoke/audit, container,
dan issue closure.

- Tag/commit: _______________________________________________________
- CI/container workflow URL: ________________________________________
- Test/coverage/audit evidence: ______________________________________
- Second-review record: _____________________________________________
- Remaining defects: ________________________________________________
- [ ] Gate B approved

## BE-27 — Gate C: model validated

**Instruksi penutupan:** gabungkan input evidence, distribution fitting, face
validation, baseline held-out error, tolerance decisions, dan domain-calibrated
extreme conditions.

- BE-03–BE-09 evidence bundle: ______________________________________
- Baseline validation result: _______________________________________
- Extreme-condition result: _________________________________________
- Validity domain/limitations: ______________________________________
- Signed decision: __________________________________________________
- [ ] Gate C approved

## BE-28 — Gate D: experiment frozen

**Instruksi penutupan:** bekukan factors, levels, seed plan, CRN, repetitions,
outcomes, models, exclusions, stopping rule, baseline, MPID, dan config hash.

- Analysis plan registration: _______________________________________
- Final config/path/hash: ____________________________________________
- Repetitions/power rationale: ______________________________________
- Baseline/MPID: ____________________________________________________
- PI/statistician approvals: ________________________________________
- [ ] Gate D approved before final execution

## BE-29 — Gate F: claims reproduced

**Instruksi penutupan:** setelah final dataset/analysis tersedia, peneliti kedua
meregenerasi seluruh tables/figures dan main claims pada environment bersih;
checksums/tolerances harus cocok atau discrepancy diselesaikan.

- Artifact/tag/DOI: _________________________________________________
- Reviewer environment: _____________________________________________
- Generated artifact manifest: ______________________________________
- Claim comparison/tolerances: ______________________________________
- Discrepancy resolution: ___________________________________________
- [ ] Gate F approved

## BE-30 — Gate G: submission-ready

**Instruksi penutupan:** pilih jurnal final dan versi author guide; selesaikan
STRESS-DES, limitations/transparency, archive DOI, data/code/AI/funding/conflict
statements, format, limits, ethics, dan submission checklist.

- Journal/category/quartile source-year: _____________________________
- Author guide URL/access date: ______________________________________
- Manuscript checklist/path: ________________________________________
- STRESS-DES/limitations evidence: __________________________________
- DOI/data-code statement: __________________________________________
- Ethics/AI/funding/conflict declarations: ___________________________
- Corresponding author approval/date: _______________________________
- [ ] Gate G approved

---

# B. PENDING_FINAL_DATA — 6 item

Item berikut hanya dapat ditutup setelah BE-01, BE-02, dan Gate A–D terpenuhi.
Semua bukti harus menunjuk dataset final dari tagged release.

**Prosedur eksekusi yang sudah tersedia:** gunakan
`docs/FINAL_EXPERIMENT_RUNBOOK.md` dan
`scripts/run_final_experiments.ps1`. Preflight mengunci config/source/plan;
checkpoint per run memungkinkan resume tanpa mengulang run tersertifikasi;
strict audit dan post-processing menghasilkan evidence untuk FD-01 sampai
FD-06. Item tetap `PENDING_FINAL_DATA` sampai run clean-tag benar-benar selesai
dan artifact final diisi pada ruang konfirmasi di bawah.

## FD-01 — Audit kelengkapan dataset final

**Instruksi penutupan:** jalankan strict auditor dan pemeriksaan schema atas raw
final results; verifikasi expected configurations × repetitions, run UUID/ID,
seed map, missing/finite/range checks, invariants, failures, dan checksums.

- Tag/commit/config hash: ____________________________________________
- Results path/SHA-256: _____________________________________________
- Expected versus actual rows: ______________________________________
- Audit command/report: _____________________________________________
- Missing/duplicate/failed runs: ____________________________________
- Verifier/date: ____________________________________________________
- [ ] Audit pass tanpa exception yang tidak disetujui

## FD-02 — Membekukan raw output

**Instruksi penutupan:** pindahkan raw results/manifests/logs ke immutable atau
read-only storage; derived transformations harus berada di path terpisah dan
selalu menyimpan source checksum.

- Raw storage URI/path: ______________________________________________
- Access controls/read-only evidence: ________________________________
- Raw bundle checksum: ______________________________________________
- Retention/backup policy: __________________________________________
- Derived-output root: ______________________________________________
- Custodian/date: ___________________________________________________
- [ ] Raw output tidak dapat tertimpa pipeline

## FD-03 — Menyimpan manifest dan audit final

**Instruksi penutupan:** simpan config, environment, dependency/source hashes,
execution-order seed, result checksum, run counts/status, audit report, command,
dan logs bersama raw dataset; verifikasi silang seluruh hash.

- Manifest path/SHA-256: ____________________________________________
- Audit report path/SHA-256: ________________________________________
- Config/environment/log paths: _____________________________________
- Cross-check result: _______________________________________________
- Archive location: _________________________________________________
- [ ] Manifest/audit bundle lengkap dan konsisten

## FD-04 — Melaporkan hasil negatif/non-supportive

**Instruksi penutupan:** dari frozen analysis output, daftar seluruh hypotheses
yang tidak didukung, null/negative effects, losing/tie scenarios, estimation
failures, dan deviations; jangan hanya memilih hasil signifikan.

- Hypothesis disposition table: _____________________________________
- Negative/null effects dan CI: _____________________________________
- Win/tie/loss report: ______________________________________________
- Non-estimable/model failures: _____________________________________
- Manuscript sections/tables: _______________________________________
- Reviewer confirmation: ____________________________________________
- [ ] Semua hasil relevan dilaporkan tanpa outcome-based censorship

## FD-05 — Trade-off performa versus biaya komputasi

**Instruksi penutupan:** rerun resource benchmark pada tagged release/hardware;
gabungkan outcome effect/CI dengan wall time, CPU, RSS, disk, dan route scaling;
laporkan Pareto dan cost of improvement per metode/scenario.

- Hardware/software/tag: ____________________________________________
- Benchmark results/manifest: _______________________________________
- Operational effect/CI source: _____________________________________
- Trade-off/Pareto table/figure: ____________________________________
- Scaling/parallelism evidence: ______________________________________
- Interpretation/limitations: _______________________________________
- [ ] Konfirmasi oleh OR/statistical reviewer

## FD-06 — Gate E: sertifikasi final data

**Instruksi penutupan:** kumpulkan FD-01–FD-03; pastikan dataset berasal dari
signed tag, 100% run sukses, complete/unique/finite, schema/invariants/checksums
lulus, dan raw bundle immutable.

- Signed tag/commit: ________________________________________________
- FD-01 audit: ______________________________________________________
- FD-02 immutable storage: __________________________________________
- FD-03 manifest bundle: ____________________________________________
- Exceptions/deviations: ____________________________________________
- PI/release owner/verifier signatures: _____________________________
- [ ] Gate E approved

---

# C. Ringkasan persetujuan akhir

| Kategori | Total | Selesai | Belum selesai | Verifier | Tanggal |
|---|---:|---:|---:|---|---|
| BLOCKED_EXTERNAL | 30 |  |  |  |  |
| PENDING_FINAL_DATA | 6 |  |  |  |  |

- Semua referensi bukti dapat diakses reviewer: [ ] Ya [ ] Tidak
- Seluruh hash diverifikasi ulang: [ ] Ya [ ] Tidak
- Tidak ada approval yang diisi oleh pihak tanpa wewenang: [ ] Ya [ ] Tidak
- `QUALITY_TODO_Q1.md` telah disinkronkan: [ ] Ya [ ] Tidak
- Catatan/deviation akhir:

  ___________________________________________________________________

  ___________________________________________________________________

- Nama dan tanda tangan quality-gate coordinator: ____________________
- Tanggal: ___________________________________________________________
