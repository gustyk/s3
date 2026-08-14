# Decision Freeze dan Paper Change Impact Log — EJIE-337519

Tanggal keputusan: 2026-08-14

Dokumen ini membekukan target implementasi dan mencatat bagian paper yang harus
direvisi manual setelah code, eksperimen, dan analisis selesai. File paper asli
`docs/2026_EJIE-337519.md` tidak boleh diedit oleh workflow ini.

## 1. Keputusan kanonik

| Area | Keputusan final untuk implementasi | Dampak paper awal |
|---|---|---|
| Heuristic 7 | Hapus label/implementasi DVNS; gunakan SNH sesuai sequence paper dengan capacity-safe deterministic fallback | sinkronkan seluruh label, pseudocode, tabel, gambar, dan dataset |
| MPBH | Gunakan EDD + temporary batch + urgency-β/capacity constraints + deterministic feasibility restoration | hapus penjelasan/artefak slack-per-item jika muncul |
| Batching cycle | Trigger membuka cycle; buat batch hanya sebanyak release slots/idle picker; stop saat pool/eligible subset kosong atau tidak ada slot | revisi Section 3.3/pseudocode bila detail belum eksplisit |
| FTWB F | 720 s | ubah 360 s menjadi 720 s dan revisi justifikasi baseline |
| VTWB | V=12; eligible set adalah first 12 remaining orders by arrival; cycle dibatasi picker | tambahkan detail subset/tie-break |
| Order structure | line count 1–10 discrete-uniform; setiap distinct item memiliki quantity 1–10 discrete-uniform; total 1–100 pcs | ganti frasa ambigu “order size 1–10 items” dengan lines/quantity/total |
| ABC | kelas A≈20% SKU/80% demand, B≈30%/15%, C≈50%/5%; item ditempatkan A→B→C | tambahkan class boundaries dan probability mass |
| Pick time | 5 s per piece | pertahankan angka paper, jelaskan unit piece |
| Setup | 180 s per executed batch/tour | keputusan spesifik terakhir mengungguli catatan 30 s; ubah Section 3.2 dan seluruh formula/justifikasi |
| Walking | 0,5 m/s; shelf pitch 1 m=2 s; aisle transition 2 m=4 s | tambahkan geometry-to-time mapping |
| Routing | `Traversal` dilabel `S-shape`; exact route untuk execution | selaraskan terminology |
| Urgency | O(1)-per-order calibrated linear travel surrogate; setup/pick termasuk sekali; single-order conservative prediction seperti paper | tambahkan coefficients, calibration error, dan version/hash |
| Warm-up | 5,460 s (91 min), dibekukan dari pilot Welch 24 jam, 10 replikasi, seluruh 8 metode pada regime stabil λ=0.5/min dan 12 picker | revisi Section 3.3 dan laporkan rule maksimum lintas backlog/active-pickers; overload tetap finite-horizon non-stationary |
| Picker dispatch | longest-idle-first, deterministic tie by picker ID | tambahkan tie-break dan bukti implementasi |
| TLO | completed late + overdue outstanding at observation horizon | revisi Persamaan (2), denominator, dan censoring explanation |
| Outstanding raw | nullable start/completion; censor time; observed waiting/flow; tardiness lower bound; state at horizon | tambahkan data dictionary/metric handling |
| Warm-up | Welch-estimated pre-observation period; state berlanjut; KPI utama hanya cohort arrival dalam 8-hour observation window | isi nilai final/metode Welch dan ubah initialization/stopping |
| Composite | min–max dalam matched scenario × repetition terhadap fixed eight-method reference set, kemudian aggregate; weights 0.6/0.3/0.1 | Table 4 dan narasi harus berasal dari satu function/output |
| Primary multiobjective | Pareto tetap primer; composite sekunder + weight sensitivity | tambah robustness interpretation |
| Reproducibility | explicit CRN seed, run UUID, source/config/dependency hash, order-level data, manifest, hardware | perluas Section 3.3/Data Availability/supplement |

Jika keputusan baru bertentangan dengan baris ini, perubahan harus dicatat
sebagai amendment bertanggal sebelum run confirmatory.

## 2. Keputusan ahli untuk detail yang belum ditetapkan

1. Due allowance adalah integer discrete-uniform 30–120 menit **inklusif**,
   disampling dalam menit lalu dikonversi ke detik. Ini membuat wording paper
   literal dan menghindari pseudo-presisi detik.
2. FCFS selalu mengurutkan remaining eligible orders dengan
   `(arrival_seconds, order_id)`; EDT dengan `(due_seconds, arrival_seconds,
   order_id)`. Keduanya memakai deterministic next-fit.
3. Batch cycle menggunakan `release_slots = picker_count - active_batches -
   pending_batches`; pending batch mereservasi satu picker slot agar queue tidak
   dilepas melebihi resource availability.
4. Outstanding order tidak diberi completion fiktif. `completion_time` tetap
   null, `censor_time=observation_end`, dan tardiness yang disimpan adalah lower
   bound `max(0,censor_time-due)`.
5. Warm-up cohort tidak masuk numerator/denominator KPI utama, tetapi state dan
   workload-nya tetap memengaruhi observation window. Busy-time crossing
   boundary hanya dihitung overlap dengan observation window.
6. Travel surrogate dikalibrasi deterministic terhadap exact route engine dan
   wajib melaporkan holdout MAE/RMSE/R²; coefficients dibekukan sebelum final.
7. Advanced SNH/MPBH menghasilkan satu capacity-feasible proposal per release
   slot. FCFS/EDT tetap digunakan untuk six non-intrinsic trigger methods;
   timing-versus-composition reviewer study menggunakan crossed policies secara
   eksplisit, bukan menyamarkan composition sebagai trigger.
8. Main factorial dan reviewer experiments memakai CRN current yang baru;
   tidak ada klaim seed-identical terhadap legacy.
9. Legacy hanya historical comparison. Seluruh klaim revisi berasal dari
   regenerated certified data.

## 3. Paper sections yang pasti terdampak

| Bagian paper | Perubahan yang harus dilakukan setelah hasil final | Evidence yang akan dibuat |
|---|---|---|
| Abstract | run count final, metode terbaik, effect/CI, dan klaim yang berubah | final analysis summary |
| Section 1 | kontribusi/claim scope bila ranking berubah | claim-impact matrix |
| Section 3/Table notation | TLO baru, observation cohort, censoring, raw fields, surrogate notation | model/data dictionary |
| Section 3.1 | state perlu pending batches/release slots bila relevan | final model spec |
| Section 3.2 | order lines/quantity, ABC, 5 s pick, 180 s setup, walking geometry, urgency surrogate | config + surrogate report |
| Section 3.3 | F=720, warm-up Welch value, longest-idle, cycle semantics, RNG/CRN, final scenario/run count | manifest + Welch report |
| Section 3.4 | revised TLO, late ratio, on-time rate, tardiness variants, composite scope | metric tests + corrected table |
| Sections 4.1–4.4 | pseudocode exact seluruh trigger; SNH/MPBH final; complexity corrected | golden tests + decision benchmark |
| Table 4/Figures 2–5 | regenerate seluruh angka/plots; satu composite pipeline | certified final outputs |
| Section 5.1 | ranking/effect claims dan 27,04% harus dihitung ulang | paired estimates/CI |
| Sections 5.2–5.4 | factorial interactions, timing-vs-composition ablation, proposition status | model diagnostics + ablation |
| Table 5 | regenerate ANOVA replacement/robust factorial results dan effect sizes | statistical outputs |
| Table 6 | regenerate representative contexts dengan secondary factors eksplisit | scenario winner outputs |
| Section 5.5 | status setiap proposition dapat didukung, parsial, atau ditolak | claim-impact matrix |
| Section 6 | managerial implications dari calibrated F/V dan β sensitivity | reviewer experiment summaries |
| Limitations | synthetic inputs, surrogate error, no congestion, censoring, external validity | threats-to-validity update |
| Data Availability | ganti/versikan DOI dengan source/config/data/checksums lengkap | release archive manifest |
| Response letter | jawab setiap reviewer ID dengan commit, command, table, dan interpretation | reviewer response matrix |

## 4. Change-log template per implementasi

Setiap perubahan code/analysis harus menambahkan entry berikut sebelum final
handoff:

| Change ID | Reviewer ID | Source/config changed | Behavioral difference | Tests | Output/manifest | Paper sections affected | Claim impact |
|---|---|---|---|---|---|---|---|
| pending | pending | pending | pending | pending | pending | pending | pending |

### Entries completed on 2026-08-14

| Change ID | Reviewer ID | Source/config changed | Behavioral difference | Tests | Output/manifest | Paper sections affected | Claim impact |
|---|---|---|---|---|---|---|---|
| C-001 canonical model | R1#1/#5/#10; R2#3/#4; Minor#4 | trigger/order/routing/IO/experiment/config | aligns algorithms, workload, release, KPI, raw censoring, warm-up | 65 pass; 93.88% | representative pilot audit pass | 3–7, Tables 4–6, all result figures | all legacy numbers invalid for revised claims |
| C-002 urgency surrogate | R1#1; R2#3 | `travel_surrogate.py`, coefficients | exact route replaced only inside urgency prediction by frozen O(1)-per-order regression | unit + holdout | `outputs/travel-surrogate-calibration-v1` | 3.2, 4, complexity/limitations | supports implementability with disclosed error |
| C-003 Welch | R1-Minor#4 | warm-up runner/config | 5,460-s deletion after stable 24h pilot; overload flagged non-stationary | Welch tests | `outputs/welch-stable-24h-v2` | 3.3, limitations | changes measurement cohort and all estimates |
| C-004 ablation | R1#1 | crossed adapter/runner | independently crosses 2 timing × 3 composition | six-cell tests + audits | `outputs/ablation-pilot-v1` | 5.4, Proposition 4 | pilot suggests composition effect exceeds timing effect |
| C-005 beta | R1#10; R2#4 | beta runner | β={1,2,3,4}, paired CRN, trade-off metrics | smoke + 16 cell audits | `outputs/beta-sensitivity-pilot-v1` | 5.x, 6 | β=1 pilot lowers MPBH TLO but increases trips/runtime |
| C-006 compute | R2#3 | decision benchmark | 30-repeat latency at n=10…5000 with overhead calibration | static checks | `outputs/computation_time_final` | 4 complexity, 6 implementation | all methods remain online-feasible at tested n; MPBH is costliest |
| C-007 raw storage | R1#5; reproducibility | experiment/audit/config | stream per-order evidence to gzip; manifest records filename/compression/hash/rows; auxiliary sweeps may omit duplicate raw | compressed integration test + audit | `outputs/compression-smoke-v1` | Data Availability/Supplement | prevents projected 345-GiB uncompressed full output from exhausting current disk |
| C-008 release/resume hardening | reproducibility; all final-data reviewer items | experiment/audit/preflight/scripts/config | per-order release/tour/control trace; wall time; atomic byte-certified checkpoints; audited idempotent cell/final reuse; explicit reviewer grids and runbook | 67 pass; forced interruption/restart; 8/8 release smoke audit pass | `outputs/release-smoke-final-v1`; `docs/FINAL_EXPERIMENT_RUNBOOK.md` | Section 3.3–3.4, reproducibility, Data Availability, supplement | final run can resume without mixing plans or repeating certified work; all paper/reviewer metrics have traceable fields |

## 4A. Preliminary claim-impact findings (pilot only)

- MPBH remains the lowest-TLO method in all four Table-6 contexts, but the
  accepted high-rate/high-picker value 558.52 becomes 5,940.00 in the
  corrected three-repetition pilot. The 27.04% manuscript-wide reduction must
  be withdrawn until recomputed from final data.
- Corrected MPBH advantage over the next-best policy is approximately 25.4%
  (low/one picker), tie at zero (low/12), 1.17% (high/one), and 8.76%
  (high/12). The claim that superiority is most pronounced at high load is not
  supported by this pilot.
- Crossed ablation estimates MPBH-timing minus FTWB timing at −18 TLO, while
  MPBH-composition minus FCFS/EDT is −147.42 TLO. This preliminary direction
  weakens/reverses Proposition 4 and must be reported even if confirmed as a
  negative finding.
- β=1 minus β=2 for MPBH is −66.67 TLO in the pilot, accompanied by more trips,
  lower cart utilization, and higher compute time. Managerial guidance must
  present the trade-off rather than declare a universal β optimum.
- F/V calibration pilot finds F=60 s and V=4 maximize the internal calibration
  composite in both tuning and held-out slices. FTWB TLO is invariant across F
  in these four contexts, but F=60 yields higher throughput/utilization than
  F=720. The main model remains F=720 per owner decision; Section 3.3 must
  distinguish “paper-canonical benchmark” from “pilot-calibrated benchmark” and
  discuss this fairness threat instead of claiming F=720 is empirically optimal.
- Exact tardiness of horizon-outstanding orders is unidentifiable. The revised
  paper must distinguish completed-order tardiness, conditional late
  tardiness, and all-order **horizon lower-bound** tardiness.

## 5. Larangan dan gate

- Jangan overwrite atau mengedit paper original.
- Jangan memakai legacy untuk klaim revisi.
- Jangan menjalankan factorial besar sebelum warm-up, surrogate, algorithms,
  KPI, seeds, per-order schema, dan reviewer instrumentation lulus tests/pilot.
- Jangan mempertahankan klaim lama jika regenerated result melemahkannya.
- Setiap tabel/angka paper revisi harus memiliki source CSV, command, config
  hash, source hash, dan independent audit status.
