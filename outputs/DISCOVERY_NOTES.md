# Discovery Notes — Revisi Mayor EJIE-337519

Tanggal discovery: 2026-08-12
Scope: `R1-Mayor #1`, `#2`, `#5`, `#6`, `#10`; `R2-Mayor #3`, `#4`
Status baseline: **DISCOVERY COMPLETE (2026-08-12)**

> Update 2026-08-14: keputusan D-01–D-07/D-09/D-10 telah diberikan pengguna;
> implementasi dan pilot reviewer sudah dimulai. Spesifikasi current berada di
> `docs/OPERATIONAL_DEFINITIONS_CANONICAL_2026-08-14.md`. Isi berikut
> dipertahankan sebagai audit kondisi sebelum koreksi, bukan status current.

Dokumen ini menjawab tahap discovery pada brief teknis reviewer. Tidak ada
eksperimen reviewer atau rerun 207.360 run yang dilakukan pada tahap ini.
Alasannya: terdapat konflik antara algoritme/manuskrip, source saat ini, dan
dataset legacy yang harus diputuskan tim penulis sebelum angka baru boleh
dihasilkan.

## 1. Ringkasan keputusan

| Area | Temuan | Status |
|---|---|---|
| Trigger/composition | Seluruh trigger ada di `src/trigger_method.py`; keputusan trigger dan komposisi masih bercampur dalam generator SimPy | perlu refactor |
| SNH/DVNS | Paper memakai `SNH`; code/config memakai `DVNS`; ekuivalensi belum disahkan | **blocker ilmiah** |
| MPBH | Implementasi saat ini tidak sama dengan pseudocode MPBH pada paper | **blocker P0** |
| Data asli | Legacy hanya menyimpan agregat per run; tidak ada `c_i`, `d_i`, assignment batch, atau event/order log | tardiness lama tidak dapat dihitung |
| Composite score | Dua angka lama berhasil direproduksi dan berasal dari dua scope normalisasi berbeda | root cause ditemukan; estimand perlu dibekukan |
| FTWB/VTWB | `F` dan `V` sudah dibaca dari config, tetapi nilai current config adalah `F=720`, bukan `360` seperti paper | sweep mudah; rekonsiliasi wajib |
| Subset scenario | Runner mendukung subset melalui `experiment_design`; definisi sekunder untuk empat titik Table 6 belum ditetapkan | keputusan desain diperlukan |
| Seed | Current runner deterministik/CRN; dataset legacy tidak merekam seed | seed asli tidak dapat dipakai ulang |
| Warm-up | Tidak ada implementasi Welch; model current adalah terminating one-shift tanpa deletion | paper harus dikoreksi atau model diubah |
| Timing | Timer whole-run/route sudah ada, tetapi belum ada timer decision-kernel untuk delapan trigger | perlu instrumentasi baru |
| Hardware | Mesin tersedia dan dapat diinventarisasi | benchmark final tetap perlu tagged release |
| DOI | DOI diklaim paper, tetapi isi remote tidak dapat diinventarisasi dari environment audit | identitas remote–lokal belum terbukti |

## 2. Discovery codebase

### 2.1 Lokasi dan modularitas algoritme

- Delapan metode terdaftar dalam `SUPPORTED_TRIGGER_METHODS` dan
  diimplementasikan sebagai generator SimPy di `src/trigger_method.py`:
  `ftwb_trigger`, `vtwb_trigger`, `max_picker_trigger`, `max_cart_trigger`,
  `urgent_picker_trigger`, `urgent_cart_trigger`, `dvns_trigger`, dan
  `mpbh_trigger`.
- FCFS dan EDT berada di `src/batching_method.py` melalui `fcfs_batching`,
  `edt_batching`, dan dispatcher `batching_method`.
- Belum ada interface `TriggerPolicy` atau `CompositionRule`. Setiap generator
  memutuskan kondisi release, memilih order, menjalankan batching, memutasi
  `OrderPool`, dan mengirim batch ke `IOPool` dalam satu loop.
- MPBH mencampur release rule “pool non-empty dan picker tersedia”, ranking
  slack-per-item, greedy cart fill, serta FCFS/EDT batching.
- DVNS mencampur urgency test, tiga ordering/neighbourhood, pemilihan subset,
  batching, dan mutasi state. `hybrid fallback` secara praktis sulit/nyaris
  tidak pernah tercapai karena capacity branch sebelumnya memilih setidaknya
  satu order selama order tidak oversized.
- `MaxCart` dan `UrgentCart` current code tidak memeriksa picker tersedia sebelum
  membentuk pending batch, sedangkan decision rule paper mensyaratkannya.

### 2.2 Konflik definisi SNH dan MPBH

Ini adalah blocker terpenting sebelum refactor:

1. Paper mendefinisikan SNH sebagai urutan fallback urgency → full
   urgency-fit → capacity → hybrid. Code menamainya DVNS dan perilakunya tidak
   sepenuhnya identik dengan teks paper.
2. Paper mendefinisikan MPBH sebagai earliest-due traversal dengan temporary
   batch, constraint predicted late orders `β`, capacity check, dan feasibility
   restoration. Current MPBH mengurutkan
   `(due - now - route_time) / quantity`, lalu greedy capacity fill; `β` tidak
   dipakai.
3. Historical source pada commit awal tidak dapat menghasilkan MPBH, sementara
   dataset legacy memuat baris MPBH. Karena itu “MPBH penuh dari kode existing,
   tidak diubah” tidak dapat dijadikan kontrol yang reproducible.

Tim penulis harus memilih satu spesifikasi kanonik dan menyetujui mapping
`legacy DVNS` ↔ `paper SNH` sebelum hasil reviewer dijalankan.

### 2.3 Data hasil 207.360 run

File lokal adalah
`data/legacy/simulation_results_legacy_unverified.csv` dengan format CSV dan
kolom:

`run_id, incoming_rate, cart_capacity, trigger_method, batching_method,
routing_policy, num_pickers, total_orders, total_late_orders, picker_utility`.

Temuan:

- 207.360 row, 6.912 konfigurasi, 30 row per konfigurasi;
- hanya agregat per run; tidak ada arrival, start, completion (`c_i`), due
  (`d_i`), tardiness per order, batch assignment, event log, maupun seed;
- 72 duplicate `run_id`, rentang 185761–186160 hilang, dan defect provenance
  lain tercatat di `data/legacy/MANIFEST.md`;
- late-order ratio `TLO/N` dan on-time rate masih dapat dihitung dari dua kolom
  agregat, tetapi average tardiness tidak dapat dihitung;
- current simulator menyimpan detail order hanya in-memory di `IOPool` dan
  menulis agregat tardiness per run ke CSV. Ia belum menulis raw per-order
  dataset;
- current output sudah memiliki generated/completed/outstanding, late completed
  dan outstanding, service level, serta mean/median/max/p95 tardiness, tetapi
  angka ini berasal dari model current yang berbeda dari source legacy.

DOI `10.17632/49r2pmymrm.1` disebut paper. Resolusi halaman, pencarian indeks,
dan metadata API dari environment audit tidak menghasilkan inventory yang dapat
diverifikasi (API sebelumnya HTTP 401). Kesamaan DOI dengan file lokal belum
dapat diklaim tanpa file list, size, dan checksum dari pemilik dataset.

**Konsekuensi R1-Mayor #5:** jangan menjalankan ulang 207.360 run secara diam-
diam. Tim perlu mengotorisasi regenerasi dengan spesifikasi kanonik dan menerima
bahwa hasilnya mungkin berubah. Pilihan terbatas untuk data lama adalah
menambahkan late ratio/on-time rate; average tardiness memerlukan rerun atau raw
order file dari DOI/pemilik data.

### 2.4 Root cause composite score

Tidak ada fungsi composite score 0.6/0.3/0.1 dalam pipeline current;
`src/analysis_pipeline.py` memakai Pareto. Historical `analysis3.py` pada Git
memakai normalisasi per trigger dan bobot 0.4/0.3/0.3, sehingga juga bukan sumber
yang dapat mengaudit Persamaan (8).

Namun kedua set angka paper dapat direproduksi secara eksak dari legacy CSV:

| Metode | Table 4: normalisasi per sel skenario, 30 replikasi dipool | Narasi: normalisasi delapan mean global |
|---|---:|---:|
| FTWB | 0.725 | 0.752 |
| VTWB | 0.682 | 0.547 |
| MaxPicker | 0.826 | 0.883 |
| MaxCart | 0.619 | 0.790 |
| UrgentPicker | 0.725 | 0.749 |
| UrgentCart | 0.381 | 0.061 |
| SNH/DVNS | 0.666 | 0.361 |
| MPBH | 0.864 | 0.924 |

Table 4 diperoleh dengan melakukan min–max pada setiap sel yang didefinisikan
oleh incoming rate × picker × batching × capacity × routing, tetapi 30
replikasi tidak dipasangkan sebagai blok terpisah. Narasi diperoleh dengan
mengagregasi mean tiap metode terlebih dahulu, lalu min–max antar delapan mean.

Rekomendasi statistik: pertahankan composite hanya sebagai outcome deskriptif
sekunder; bekukan delapan metode referensi; normalisasi dalam blok
scenario × repetition yang matched/CRN, lalu rata-ratakan score dan laporkan CI.
Pareto tetap menjadi analisis utama. Jika tim memilih scope lain, keputusan dan
alasan harus dibekukan sebelum melihat ranking sensitivitas. Constant-range
cells dan perubahan reference set harus ditangani eksplisit.

### 2.5 Parameter, factorial design, dan seed

- `F` dibaca dari `trigger_parameters.FTWB_interval`; `V` dari
  `trigger_parameters.VTWB_threshold`. Keduanya sudah parameterized.
- `config/parameters.yaml` saat ini memakai `F=720 s`, `V=12`; paper memakai
  `F=360 s`, `V=12`.
- Full design current tersedia di `experiment_design` dan menghasilkan 6.912
  scenario. Daftar level dapat dioverride oleh config turunan, sehingga subset
  tidak membutuhkan perubahan engine.
- Empat titik Table 6 hanya menetapkan rate {0.5, 16} dan picker {1, 12}; tabel
  paper mengagregasi batching, cart, dan routing. Untuk mereplikasi konteks itu,
  rekomendasi adalah mempertahankan semua 2 × 3 × 2 level sekunder atau
  menyatakan secara eksplisit satu baseline sekunder. Keputusan ini belum ada.
- Current seed adalah SHA-256 dari `master_seed | arrival key | repetition`.
  Semua policy dan faktor non-arrival berbagi demand stream untuk rate/repetition
  yang sama. Execution order juga diacak deterministik dan dicatat.
- Legacy CSV tidak merekam seed. Permintaan “seed sama persis dengan run asli”
  tidak dapat dipenuhi atau diverifikasi. Eksperimen tambahan dapat memakai
  CRN current yang baru dan terdokumentasi, bukan mengklaim seed legacy.

### 2.6 Warm-up dan stopping

Tidak ada implementasi Welch atau konstanta warm-up. Current model adalah
terminating simulation satu shift, initialized empty, dijalankan 28.800 detik,
tanpa warm-up deletion, dan mempertahankan censoring pada horizon. Ini tertulis
di `docs/STRESS_DES_CHECKLIST.md`.

Pernyataan paper bahwa warm-up ditentukan dengan Welch tidak didukung oleh
source/artefak. Rekomendasi: koreksi manuskrip menjadi terminating finite-horizon
tanpa warm-up, kecuali tujuan studi diubah menjadi steady-state dan seluruh
desain serta hasil diregenerasi.

### 2.7 Timing dan environment

`src/benchmark.py` telah memakai `time.perf_counter()` untuk whole simulation
dan route kernel serta merekam wall time, CPU, RSS, Python allocation, dan
environment. Belum ada:

- waktu setiap pemanggilan decision kernel untuk delapan trigger;
- synthetic order-pool benchmark `n={10,50,100,500,1000,5000}`;
- pemisahan waktu trigger decision dan composition;
- fit empiris O(1), O(n), dan O(n log n) per metode.

Mesin yang tersedia saat discovery:

- HP EliteDesk 800 G3 DM 65W;
- Intel Core i7-7700 3.60 GHz, 4 core/8 logical processor;
- RAM 34,228,887,552 byte (~31.9 GiB);
- Windows 11 Pro 64-bit, build 10.0.26200;
- Python 3.14.6.

Hardware ini dapat dipakai untuk pilot. Angka publication-final harus dibuat
dari signed/tagged source dengan power plan, background-process protocol,
warm-up benchmark iterations, repeat count, dan CPU power policy yang dibekukan.

## 3. Rencana implementasi

### WP0 — Freeze definisi dan desain (wajib sebelum kode eksperimen)

Owner: PI/coauthors + statistical reviewer.
Reviewer IDs: seluruh butir.

Keputusan yang dibutuhkan:

1. spesifikasi kanonik SNH/DVNS dan MPBH serta label publikasinya;
2. apakah legacy hanya historical atau tetap dipakai untuk tabel revisi;
3. scope normalisasi composite score;
4. secondary factors pada subset Table 6;
5. otorisasi rerun untuk tardiness dan apakah full 207.360 wajib;
6. target hardware benchmark dan optional MIP scope.

Acceptance: keputusan bertanggal, ditandatangani, dan direferensikan oleh config
freeze/hash.

### WP1 — Pisahkan decision policy dan composition (`R1-Mayor #1`)

Rencana:

- buat immutable `SystemState`, protocol `TriggerPolicy`,
  `CompositionRule`, dan result object berisi trigger/no-trigger, selected IDs,
  reason, serta timing;
- jadikan decision kernel pure/deterministic; adapter SimPy menangani polling,
  mutasi pool, dan enqueue batch;
- implementasikan FCFS, EDT, dan canonical MPBH composition terpisah;
- implementasikan canonical FTWB, VTWB, SNH, MPBH trigger terpisah;
- pertahankan compatibility wrapper untuk CLI current;
- tambahkan golden tests dari pseudocode paper, tests untuk picker-availability,
  capacity, urgency β, tie-breaking, dan deterministic equivalence.

Eksperimen yang direkomendasikan adalah full crossed 2 timing policies × 3
composition rules (FCFS/EDT/MPBH), bukan hanya empat kombinasi yang unbalanced.
Empat kombinasi brief tetap dapat dilaporkan sebagai planned contrasts. Desain
2×3 memungkinkan estimasi main effect dan interaction yang lebih sah daripada
ANOVA atas empat label ad hoc.

Output: `outputs/ablation/*`; minimum 30 CRN repetitions setelah design freeze.

### WP2 — Kalibrasi benchmark (`R1-Mayor #2`)

- config sweep terpisah untuk delapan nilai F dan delapan nilai V;
- jangan mengganti raw original; tulis output baru beserta manifest;
- selection criterion primer mean late rate/TLO sesuai freeze, composite hanya
  secondary;
- gunakan nested separation: tuning contexts untuk memilih F*/V*, evaluation
  contexts untuk membandingkan agar tidak memberi benchmark keuntungan in-
  sample;
- simpan seluruh sweep, CI, tie rule, dan selected parameter.

Output: `outputs/benchmark_calibration/*`.

### WP3 — Metrik tambahan (`R1-Mayor #5`)

- script legacy-safe menghitung `late_order_ratio=TLO/total_orders` dan on-time
  rate tanpa mengubah raw CSV;
- tambahkan optional per-order writer (CSV/Parquet) pada current runner dengan
  run UUID, order ID, arrival, due, batch, start, completion, censoring, dan
  tardiness;
- agregasi average tardiness seluruh completed order dan conditional-on-late;
- definisikan penanganan outstanding/censored sebelum eksekusi.

Average tardiness legacy tetap blocked sampai raw order data ditemukan atau
rerun disetujui.

### WP4 — Composite score dan weight sensitivity (`R1-Mayor #6`)

- tulis satu library function dengan scope normalisasi eksplisit;
- regression tests harus mereproduksi kedua set angka lama di atas;
- fungsi corrected harus dipakai oleh Table 4 dan seluruh narasi;
- output baseline serta equal/throughput/utilisation-priority rankings, dengan
  score uncertainty dan rank-stability;
- tulis `ROOT_CAUSE.md` otomatis yang mencatat input checksum, scope, weights,
  reference methods, constant-range handling, dan formula.

Output: `outputs/composite_score/*`.

### WP5 — Decision-time scalability (`R2-Mayor #3`)

- instrument decision kernel, bukan generator loop penuh;
- kalibrasi timer overhead, gunakan warm-up calls dan repeated batches;
- synthetic valid state untuk seluruh `n`, metode, picker state, β, dan routing;
- laporkan median serta mean/SD/CI karena micro-timing skewed;
- fit candidate curves dengan held-out error/AIC dan jangan menyimpulkan kelas
  kompleksitas hanya dari R²;
- simpan hardware/software/protocol dan source/config hash.

Output: `outputs/computation_time/*`.

### WP6 — Sensitivitas β (`R1-Mayor #10`, `R2-Mayor #4`)

- parameter sudah tersedia sebagai `Urgent_threshold`, tetapi rename/schema
  alias ke `urgency_beta_orders` disarankan agar unit jelas;
- sweep β={1,2,3,4} untuk UrgentPicker, UrgentCart, canonical SNH dan canonical
  MPBH hanya jika masing-masing benar-benar memakai β;
- gunakan CRN dan subset yang sama dengan WP1; laporkan effect/CI, batch size,
  trips, service, throughput, dan compute cost.

Output: `outputs/beta_sensitivity/*`.

### WP7 — MIP kecil (`R1-Mayor #3`, opsional)

Tunda sampai WP0–WP6 stabil. Formulasi offline tidak identik dengan online
policy, sehingga hasil harus dilabel sebagai lower-bound/small-instance
benchmark, bukan validasi global. Solver/version/optimality tolerance dan setiap
instance harus diarsipkan.

### Estimasi ukuran eksperimen reviewer

Angka berikut memakai 30 replikasi dan belum termasuk smoke/pilot. Ia membantu
tim memutuskan D-05 dan compute budget:

| Work package | Satu baseline secondary-factor setting | Semua 2 batching × 3 cart × 2 routing |
|---|---:|---:|
| Crossed ablation 2 trigger × 3 composition × 4 extreme contexts | 720 | 4.320* |
| F/V calibration: 16 candidate values × 4 contexts | 1.920 | 23.040 |
| β sensitivity: 4 methods × 4 β × 4 contexts | 1.920 | 23.040 |
| Total indikatif | 4.560 | 50.400* |

`*` Untuk ablation, batching adalah treatment composition; angka 4.320 hanya
mempertahankan 3 cart × 2 routing, bukan menggandakan lagi faktor batching.
Jika brief minimum empat varian dipilih alih-alih crossed 2×3, kebutuhan
ablation turun menjadi 480 atau 2.880 run. Final count harus dihasilkan runner
setelah config freeze, bukan disalin manual dari tabel ini.

## 4. Urutan dan dependency

1. WP0: keputusan kanonik dan freeze.
2. WP1: refactor + fidelity/golden tests.
3. WP3 writer dan WP5 timing hook, karena keduanya menyentuh core interface.
4. WP2, WP4, dan WP6 runners/analysis secara paralel.
5. Smoke/precision pilot; statistical review atas estimand dan contrasts.
6. Signed tag; jalankan eksperimen reviewer ke direktori baru.
7. Audit manifests/checksums; generate manuscript-ready summaries.
8. Independent reproduction dan baru kemudian update klaim paper.

## 5. Blocker yang harus dikembalikan ke tim penulis

| ID | Blocker/konfirmasi | Dampak jika belum dijawab |
|---|---|---|
| D-01 | Apakah `DVNS` secara resmi diganti nama menjadi `SNH`, dan pseudocode mana yang kanonik? | ablation/fidelity tests tidak dapat dibekukan |
| D-02 | Pilih algoritme MPBH paper atau current slack-per-item | kontrol MPBH dan β sweep ambigu |
| D-03 | Izinkan regenerasi hasil atau pertahankan legacy yang tidak reproducible | metrik tardiness dan reviewer experiments tidak dapat dikaitkan aman ke paper |
| D-04 | Tetapkan scope composite score | corrected Table 4/ranking belum boleh difinalkan |
| D-05 | Tetapkan faktor sekunder subset Table 6 | jumlah run dan estimand ablasi/kalibrasi ambigu |
| D-06 | Setujui CRN seed baru; seed legacy tidak tersedia | klaim apples-to-apples dengan run asli tidak mungkin |
| D-07 | Koreksi klaim Welch menjadi no warm-up terminating model atau ubah model | reporting dan estimand horizon konflik |
| D-08 | Sediakan inventory/checksum DOI Mendeley | identitas dataset publik belum terbukti |
| D-09 | Otorisasi rerun besar setelah estimasi biaya | average tardiness legacy tetap blocked |
| D-10 | Setujui target hardware/protocol benchmark | angka runtime belum publication-final |

## 6. Kriteria go/no-go implementasi

Implementasi interface dan unit tests yang tidak mengunci definisi ilmiah dapat
dimulai setelah review dokumen ini. Eksekusi eksperimen dan pembuatan angka
untuk manuskrip adalah **NO-GO** sampai minimal D-01 s.d. D-07 diputuskan.
Tidak ada output pilot yang boleh menggantikan Table 4 atau mendukung klaim
Proposisi 1/4 sebelum audit, statistical review, dan tagged release.
