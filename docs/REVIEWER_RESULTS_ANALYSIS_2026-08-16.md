# Analisis hasil eksperimen reviewer — 2026-08-16

## Kesimpulan eksekutif

Seluruh eksperimen komputasional yang diminta reviewer telah selesai dan lolos
audit artifact. Hasil ini cukup untuk membekukan desain simulasi utama, tetapi
belum boleh dipakai untuk menyatakan bahwa parameter tuned menggantikan
parameter canonical paper.

Keputusan pre-main:

1. `F=720 s`, `V=12`, `β=2`, warm-up `5,460 s`, dan desain utama tetap
   dipertahankan karena telah ditetapkan sebagai definisi canonical paper.
2. Nilai tuned dilaporkan sebagai robustness/calibration evidence, bukan
   penggantian post-hoc terhadap desain utama.
3. Proposisi 4 harus dipersempit. Pada ruang eksperimen ini composition MPBH
   memberi efek lebih besar daripada timing MPBH, sehingga klaim “timing lebih
   penting daripada composition” tidak boleh dipertahankan secara umum.

## Integritas dan kelengkapan

| Artifact | Ukuran terverifikasi | Status |
|---|---:|---|
| Crossed ablation | 4,320 run, 59 kolom | 6/6 cell audit pass |
| FTWB calibration | 12,960 run, 9 nilai F | 9/9 cell audit pass |
| VTWB calibration | 11,520 run, 8 nilai V | 8/8 cell audit pass |
| β sensitivity | 23,040 run, 16 method–β cell | 16/16 cell audit pass |
| Decision benchmark | 1,440 measurements | manifest success |
| Run UUID | unik pada setiap aggregate dataset | pass |
| Run status | seluruh run `success` | pass |

Auxiliary reviewer experiments memakai `persist_order_records=false` untuk
menghindari duplikasi raw evidence. Per-order evidence lengkap tetap menjadi
syarat dan akan disimpan oleh factorial utama.

## R1-Mayor #1 dan #4 — timing versus composition

Sumber: `reviewer/ablation/planned_paired_contrasts.csv`.

| Kontras | Mean ΔTLO | 95% CI | p-value |
|---|---:|---:|---:|
| MPBH timing − FTWB timing | −18.119 | [−20.147, −16.090] | <0.001 |
| EDT composition − FCFS composition | 0.036 | [−0.006, 0.079] | 0.095 |
| MPBH composition − FCFS composition | −153.005 | [−163.823, −142.186] | <0.001 |
| MPBH composition − EDT composition | −153.041 | [−163.859, −142.223] | <0.001 |

Interpretasi: dalam ruang komposisi yang diuji, efek MPBH composition sekitar
8.4 kali efek MPBH timing. Kesimpulan reviewer harus menyatakan bahwa hasil
tidak mendukung keunggulan timing yang lebih besar daripada composition secara
umum. Klaim yang masih defensible adalah bahwa timing dan composition sama-sama
berpengaruh, sementara composition MPBH memberi kontribusi lebih besar pada
subset ini. Generalisasi ke proximity clustering, savings rules, local search,
atau VNS belum dilakukan.

## R1-Mayor #2 — kalibrasi FTWB/VTWB

Sumber: `reviewer/calibration/calibrated_params.md` dan
`sensitivity_curves_data.csv`.

- FTWB minimum TLO dan maximum calibration composite: `F=60 s`.
- VTWB minimum TLO: `V=4` orders.
- VTWB maximum calibration composite: `V=6` orders.
- Nilai canonical paper tetap `F=720 s`, `V=12`.

Pelaporan paper harus memisahkan:

- literatur/paper-canonical benchmark;
- tuned benchmark hasil first-half tuning;
- held-out evaluation pada second-half replication.

Tidak boleh memilih F/V berdasarkan held-out evaluation setelah melihat hasil
utama. Untuk menjaga identitas studi, main factorial tetap menggunakan nilai
canonical dan tuned values dilaporkan sebagai robustness comparison.

## R1-Mayor #5 dan #6 — metrik tambahan dan composite

Dataset reviewer sudah membawa `total_late_orders`, late components, late ratio,
on-time rate, tardiness, throughput, utilization, cart utilization, dan trip
count. Composite runner menggunakan satu scope matched scenario × repetition
block, dengan constant-range normalization = 0.5 dan weight sensitivity.

Namun, audit final R1-Mayor #5/#6 belum dapat ditutup sebelum main factorial
karena:

- auxiliary reviewer datasets tidak menyimpan raw order records;
- Tabel 4 utama harus dihitung dari 207,360 run canonical;
- censoring-aware all-order tardiness harus dihitung dari `orders.csv.gz` utama;
- composite ranking paper harus berasal dari satu dataset utama yang sama.

## R1-Mayor #10 dan R2-Mayor #4 — panduan praktis

Hasil reviewer mendukung panduan trade-off, bukan satu pemenang universal:

- MPBH dengan β rendah mengurangi TLO tetapi meningkatkan trip count dan
  menurunkan cart utilization;
- SNH relatif tidak sensitif terhadap β pada hasil ini;
- benchmark FTWB/VTWB perlu dilaporkan dengan nilai canonical dan tuned;
- pemilihan heuristic harus mempertimbangkan keterlambatan, throughput,
  utilization, cart fill, dan computational cost secara simultan.

## R2-Mayor #3 — waktu komputasi dan skalabilitas

Decision benchmark menghasilkan 1,440 measurements pada pool size yang telah
ditentukan. Empirical selected classifications adalah:

| Method | Empirical classification |
|---|---|
| FTWB | practically constant |
| VTWB | practically constant |
| MaxPicker | practically constant |
| MaxCart | O(n) |
| MPBH | O(n) |
| SNH | O(n) |
| UrgentPicker | O(n) |
| UrgentCart | O(n log n) |

Karena itu, istilah “all methods are O(1)” tidak boleh digunakan. Klaim yang
lebih tepat adalah bahwa sebagian trigger sederhana bersifat practically
constant pada benchmark, sedangkan metode yang memeriksa pool/order candidates
memiliki biaya empiris meningkat terhadap ukuran pool.

## Catatan reviewer yang tidak memerlukan run tambahan

R1-Mayor #3 (formalisasi MDP), R1-Mayor #7 (framing TBC), R1-Minor #1–#6,
R2-Mayor #1 (literatur), R2-Mayor #2 (Table 3), dan R2-Mayor #4 (panduan)
memerlukan revisi manuskrip, notasi, literatur terverifikasi, dan response
letter. Item-item tersebut tidak menjadi blocker teknis untuk menjalankan
simulasi utama, tetapi tetap menjadi blocker editorial sebelum resubmission.

## Sumber angka

- `outputs/final-q1-v1/reviewer/ablation/ablation_summary.csv`
- `outputs/final-q1-v1/reviewer/ablation/planned_paired_contrasts.csv`
- `outputs/final-q1-v1/reviewer/calibration/calibrated_params.md`
- `outputs/final-q1-v1/reviewer/calibration/sensitivity_curves_data.csv`
- `outputs/final-q1-v1/reviewer/beta/beta_sweep_summary.csv`
- `outputs/final-q1-v1/reviewer/beta/beta_planned_contrasts.csv`
- `outputs/final-q1-v1/reviewer/decision-benchmark/complexity_fit_results.csv`
