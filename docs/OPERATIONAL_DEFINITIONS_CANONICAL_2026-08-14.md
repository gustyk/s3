# Definisi Operasional Kanonik Simulasi EJIE-337519

Status: **implemented release candidate; final numerical results not yet certified**  
Decision freeze: 14 August 2026  
Paper pembanding (tidak diubah): `docs/2026_EJIE-337519.md`  
Baseline historis sebelum koreksi: `docs/OPERATIONAL_DEFINITIONS_CODE_VS_PAPER.md`

Dokumen ini adalah spesifikasi operasional yang sekarang dieksekusi codebase.
Jika narasi paper lama berbeda, definisi di sini merupakan keputusan kanonik
untuk rerun; lokasi paper yang perlu direvisi dicatat di
`docs/PAPER_CHANGE_IMPACT_LOG.md`.

## 1. Estimand dan batas sistem

Satu run memodelkan operasi picking manual picker-to-part. Order tiba online,
menunggu di order pool, dilepas oleh trigger menjadi batch/tour, diambil oleh
picker idle, lalu seluruh order dalam tour selesai serentak ketika picker
kembali ke I/O point. “Delivered/completed” dalam model berarti **picking tour
selesai di I/O**, bukan pengiriman last-mile ke konsumen.

Periode pengukuran adalah delapan jam (`28,800 s`) setelah warm-up `5,460 s`.
Engine karena itu berjalan sampai `34,260 s`. Order dengan arrival sebelum
5,460 s membangun state tetapi tidak masuk denominator/KPI; pekerjaannya yang
melintasi batas warm-up tetap menyumbang busy-time hanya pada bagian overlap.

Model tidak merepresentasikan congestion antar-picker, stockout/replenishment,
packing, kendaraan, break, failure, overtime, heterogenitas picker, split
order, atau cart sebagai resource terpisah. Cart capacity adalah batas quantity
per tour.

## 2. Entity, state, dan event

State pada waktu `t` adalah `(O_t, B_t, P_t, t)`:

- `O_t`: order generated yang belum dilepas ke batch;
- `B_t`: batch berstatus `pending`, `assigned`, atau `completed`;
- `P_t`: picker beserta status idle/busy dan waktu mulai idle;
- `t`: waktu kontinu SimPy dalam detik.

Event utama: order arrival, trigger/release, batch assignment, tour completion,
Welch observation, dan simulation stop. Trigger non-periodik bangun saat order
pool atau picker state berubah; urgency-aware trigger juga bangun tepat setelah
deadline prediksi urgency berikutnya. Refactor event-driven ini ekuivalen dengan
evaluasi state kontinu pada event relevan dan menghilangkan polling 1 s yang
tidak memengaruhi keputusan.

### Order

| Field/variabel | Definisi dan unit |
|---|---|
| `Order ID` | `Cust00001`, ...; unik per run |
| `a_i` / `Created Time Seconds` | waktu arrival, s |
| `d_i` / `Due Time Seconds` | `a_i + A_i`, s |
| `Order List` | pasangan unik `(SKU, quantity)` |
| `L_i` / line count | jumlah SKU berbeda, integer 1–10 |
| `q_ij` | pieces untuk line j, integer 1–10 |
| `Q_i` / `Total Item` | `sum_j(q_ij)`, integer 1–100 |
| `Batch ID`, `Picker ID` | assignment aktual; kosong jika belum assigned |
| `s_i` | picking start, nullable, s |
| `c_i` | completion, nullable, s |
| horizon state | `waiting`, `pending`, `assigned`, atau `completed` |

Outstanding order tetap ditulis ke raw output dengan `s_i/c_i` nullable,
censor time, observed wait/flow, late indicator, dan lower bound tardiness.

## 3. Stochastic inputs dan storage

### Arrival

Interarrival `X ~ Exponential(mean=60/lambda)` detik. Level `lambda` dalam
order/menit: `{0.5, 1, 2, 4, 8, 16}`. Arrival process homogen selama warm-up
dan measurement period.

### Order content

```text
L_i ~ DiscreteUniform{1,...,10}
select L_i distinct SKU without replacement using ABC probabilities
for each selected SKU j: q_ij ~ DiscreteUniform{1,...,10}
Q_i = sum(q_ij), hence 1 <= Q_i <= 100
```

Jadi “1–10 items” pada paper lama harus diperjelas menjadi 1–10 **distinct
item lines**, masing-masing 1–10 pieces.

### Due allowance

`A_i ~ DiscreteUniform{30,31,...,120}` menit, sehingga `d_i=a_i+60*A_i`.
Batas inklusif dan resolusi 60 s menghindari distribusi kontinu yang tidak
dimaksud paper.

### ABC storage

Warehouse memiliki 384 SKU:

- A: SKU 1–77 (20.05% SKU), total probability mass 0.80;
- B: SKU 78–192 (29.95% SKU), mass 0.15;
- C: SKU 193–384 (50.00% SKU), mass 0.05.

Probability seragam di dalam kelas. Sampling line tanpa replacement memakai
bobot tersebut dan dinormalisasi oleh NumPy pada setiap draw.

## 4. Warehouse, service, dan routing

Mapping SKU ke lokasi:

```text
aisle(item) = ceil(item / 32)                  # 12 aisles
shelf(item) = ((ceil(item / 2)-1) mod 16) + 1 # 16 longitudinal positions
```

Setiap shelf pitch diasumsikan 1 m. Pada speed 0.5 m/s, satu shelf pitch = 2 s;
transisi aisle melewati dua shelf pitches = 4 s. Depot-to-first-aisle = 2 s.

Tour time:

```text
tour_time(B) = 180 s setup
             + route_walking_time(B, routing)
             + 5 s * total_pieces(B)
```

Setup dibebankan sekali per executed batch/tour. Dua routing treatment adalah:

- `S-shape`: traversal aisle berdasarkan urutan aisle yang dikunjungi,
  full-aisle movement untuk pasangan traversal dan return movement pada aisle
  terakhir bila diperlukan;
- `Largest Gap`: first/last-aisle movement dan largest untraversed gap untuk
  aisle internal.

Formula rinci yang dieksekusi berada di `src/routing.py`; semua komponennya
dalam detik dan berasal dari mapping 1 m / 0.5 m/s di atas.

## 5. Resource dan assignment picker

Jumlah picker `m in {1,...,12}`. Setiap picker menangani paling banyak satu
tour. Pending batch mereservasi satu idle slot, sehingga trigger tidak boleh
melepas batch melebihi:

```text
release_slots = idle_pickers - pending_batches
```

Assignment memakai **longest-idle-first**. Tie pada idle-since yang sama
dipecahkan oleh numeric Picker ID terkecil. Batch dipilih berdasarkan release
timestamp lalu Batch ID.

## 6. Capacity dan composition rules

Cart capacity `C in {100,150,200}` pieces. Karena `Q_i<=100`, setiap order
feasible untuk semua level C dan order tidak pernah dipecah.

FCFS sort key: `(arrival_seconds, Order ID)`. EDT sort key:
`(due_seconds, arrival_seconds, Order ID)`. Keduanya memakai **next-fit**:
order dimasukkan ke current batch jika fit; jika tidak, current batch ditutup
dan order menjadi anggota pertama batch berikutnya. Dalam satu trigger cycle,
hanya sebanyak `release_slots` batch pertama yang dilepas.

## 7. Shared urgency estimator

Untuk setiap order tunggal:

```text
x(o) = [1, distinct_lines, total_pieces, max_aisle, distinct_aisles]
travel_hat_r(o) = max(0, x(o)' theta_r)
trip_hat_r(o) = 180 + 5*total_pieces + travel_hat_r(o)
urgent(o,t) iff t + trip_hat_r(o) > d_o
```

Coefficient `theta_r` dibekukan dari 10,000 calibration samples dengan held-out
evidence di `outputs/travel-surrogate-calibration-v1/`. Holdout performance:

| Routing | MAE (s) | RMSE (s) | R² |
|---|---:|---:|---:|
| S-shape | 9.848 | 13.800 | 0.9546 |
| Largest Gap | 7.531 | 9.679 | 0.9390 |

Prediction satu order di-cache karena content/location immutable. Ini tidak
mengubah criterion dan menjaga evaluation O(1) per order setelah feature build.

`beta=2` adalah minimum urgent-order count pada baseline; sensitivity runner
menguji `{1,2,3,4}`.

## 8. Delapan trigger methods

Semua cycle berhenti ketika pool kosong atau tidak ada release slot.

### FTWB

Setiap `F=720 s`, buka cycle dan compose FCFS/EDT dari semua waiting orders,
dibatasi picker availability. Paper lama yang menulis `F=360 s` harus direvisi.

### VTWB

Jika paling sedikit `V=12` order menunggu dan ada release slot, ambil fixed
first-V subset menurut arrival order, lalu compose FCFS/EDT. Order setelah V
tidak boleh masuk cycle tersebut.

### MaxPicker

Jika pool nonempty dan minimal satu picker idle/unreserved, buka cycle dari
seluruh waiting pool; release berhenti saat no idle picker.

### MaxCart

Cycle hanya dibuka jika `(sum waiting pieces >= C) AND (release_slots > 0)`.
Kedua syarat wajib; composition menggunakan FCFS/EDT.

### UrgentPicker

Cycle dibuka jika ada release slot dan `(urgent_count >= beta OR all pickers
idle)`. Composition menggunakan FCFS/EDT.

### UrgentCart

Cycle dibuka jika ada release slot dan `(urgent_count >= beta OR total waiting
pieces >= C)`. Composition menggunakan FCFS/EDT.

### SNH

Istilah DVNS tidak berlaku. Untuk setiap release slot:

1. jika urgent count `>=beta`, pilih urgent orders berurutan EDT sampai C;
2. jika semua waiting orders fit, pilih semua dalam EDT order;
3. selain itu, sort descending quantity dengan tie EDT, lalu capacity-fill;
4. deterministic hybrid fallback mencegah empty/deadlocked feasible batch.

Setiap hasil wajib nonempty (jika pool nonempty), capacity-feasible, dan order
yang dilepas dihapus atomik dari pool.

### MPBH

MPBH mengikuti paper: EDD scan, temporary batch, constraints beta dan capacity,
serta deterministic feasibility restoration.

```text
temporary = []
for o in waiting sorted by (due, arrival, ID):
    append o
    while quantity(temporary)>C or predicted_late_count(temporary)>beta:
        remove member with latest (due, arrival, ID)
if temporary nonempty: release temporary
else: release earliest individually feasible order  # no-deadlock restoration
```

`predicted_late_count` memakai completion estimate batch yang sama untuk setiap
member. MPBH tidak menjalankan configured FCFS/EDT setelah intrinsic ranking.

## 9. Reviewer timing × composition decomposition

Main experiment mempertahankan delapan metode di atas. Eksperimen reviewer
terpisah meng-cross:

```text
timing in {FTWB, MPBH-immediate}
composition in {FCFS, EDT, MPBH}
```

Enam cell memakai CRN dan paired scenario×repetition blocks. Primary inference
adalah planned paired contrasts atas TLO; OLS factorial HC3 hanya secondary.
`SELECTED_CONFIGURATION` tidak digunakan untuk production/full mode.

## 10. Horizon, censoring, dan KPI

Measurement cohort: order dengan `a_i >= 5,460 s`. Stop time `H=34,260 s`.

```text
late_completed_i = 1[c_i exists and c_i > d_i]
overdue_outstanding_i = 1[c_i absent at H and d_i < H]
TLO = sum(late_completed_i) + sum(overdue_outstanding_i)
late_order_ratio = TLO / N_generated_measurement
on_time_rate = 1 - late_order_ratio
```

KPI lain:

- throughput/hour = completed measurement orders / 8;
- tardiness completed order = `max(0,c_i-d_i)`;
- mean tardiness: mean atas seluruh completed measurement orders;
- mean late tardiness: mean conditional pada positive tardiness;
- flow = `c_i-a_i`; wait = `s_i-a_i`;
- outstanding observed flow/wait dicensor di H dan tardiness lower bound adalah
  `max(0,H-d_i)`;
- picker utilization = mean picker busy-overlap / (`m*28,800`) ×100;
- utilization spread = max minus min picker utilization, percentage points;
- cart utilization = mean completed-tour pieces/C ×100;
- trip count = completed measurement-overlapping tours.

Conservation invariant wajib: setiap generated Order ID tepat satu kali berada
di waiting pool atau suatu pending/assigned/completed batch.

## 11. Welch warm-up

Welch pilot 24 jam × 10 replications × 8 methods pada stable regime
`lambda=0.5/min, m=12` menggunakan observation 60 s, centered moving average 11
points, 5% tolerance, dan 10 consecutive points. Maksimum stabilization point
adalah `5,460 s`; bukti: `outputs/welch-stable-24h-v2/`.

Pilot `lambda=4/min, m=12` menunjukkan positive backlog drift untuk seluruh
metode dan diklasifikasikan overload/non-stationary. Warm-up 5,460 s tetap
menghapus initialization transient, tetapi hasil overload ditafsirkan sebagai
finite-horizon performance, bukan steady-state estimate.

## 12. Reproducibility dan control parameters

| Parameter | Nilai/aturan |
|---|---|
| master seed | `20260812` |
| run seed | first 64 bits SHA-256 of `master_seed|arrival-key|repetition` |
| CRN | seluruh policy/factor non-arrival berbagi demand stream untuk arrival level dan repetition sama |
| repetitions | 30 final; pilot dapat override dan wajib dilabeli |
| execution order | deterministic randomized permutation dari master seed + config hash |
| run UUID | UUID5 dari config hash + complete scenario + repetition |
| horizon policy | `fixed_with_censoring` |
| algorithm variant | hanya `base` pada production |
| model version | `0.2.0-reviewer-canonical` |
| provenance | config SHA-256, source-tree SHA-256, Git commit/dirty flag, dependency-lock SHA-256 |

Resume hanya menerima checkpoint dengan config hash, source hash, planned UUID,
dan per-order evidence konsisten. Setiap checkpoint menyertifikasi byte boundary
aggregate CSV dan GZIP raw-order; tail yang sempat tertulis sebelum interupsi
tetapi belum tersertifikasi dipotong otomatis. Artifact final dengan manifest
valid diaudit lalu digunakan kembali secara idempoten, bukan dihitung ulang.

## 13. Factorial dan sensitivity-only parameters

Main design: `8 triggers × 6 arrival rates × 12 picker counts × 2 composition
rules × 3 cart capacities × 2 routing policies = 6,912 scenarios`; 30
replications menghasilkan 207,360 run.

Sensitivity-only parameters tidak mengubah main factorial:

- `beta in {1,2,3,4}` untuk UrgentPicker/UrgentCart/SNH/MPBH;
- FTWB robustness grid `F in {60,120,180,240,300,360,480,600,720}` s;
- VTWB grid `V in {4,6,8,10,12,16,20,24}` orders;
- timing×composition crossed ablation;
- global epistemic ranges untuk arrival, due bounds, pick/setup, dan walking
  multiplier hanya untuk sensitivity, bukan nilai main model.

Benchmark calibration memakai first-half repetitions untuk tuning dan
second-half held-out evaluation. F=720 tetap definisi paper-canonical; optimum
sweep yang berbeda dilaporkan sebagai robustness finding, bukan diganti secara
post-hoc.

## 14. Composite score

Satu normalisasi digunakan: matched scenario×repetition block yang memiliki
seluruh delapan trigger. Untuk metric constant dalam block, normalized value
ditetapkan 0.5. TLO dibalik (lebih rendah lebih baik); throughput dan picker
utilization adalah benefit metrics. Baseline weights `(0.6,0.3,0.1)`.

Sensitivity weights: equal, throughput-priority, dan utilization-priority.
Pareto dominance atas unnormalized outcomes adalah primary robustness check;
composite ranking tidak boleh dipakai tanpa melaporkan weight sensitivity.

## 15. Raw dan aggregate outputs

Setiap aggregate result menyimpan scenario factors, seed, status/error,
generated/completed/outstanding, TLO components, ratios/rates, tardiness,
flow/wait percentiles, utilization, cart utilization, trips, warm-up/window,
invariants, sampled assumptions, dan provenance.

Setiap raw order menyimpan treatment mapping, arrival/due/content, batch ID,
release reason/time, batch order/piece count, picker, nullable start/completion,
tour time, censor/state, observed wait/flow, late components,
tardiness/lower bound, F/V/β aktual, observation boundary, model version, dan
config/source hashes. Aggregate juga menyimpan wall time per run dan ID
kalibrasi surrogate. Manifest menyimpan checksum dan row count aggregate CSV
serta streaming-gzip `orders.csv.gz`. Release smoke final menghasilkan delapan
metode, 440 raw rows, audit pass, dan pemanggilan ulang tanpa re-simulasi; auxiliary
sweeps dapat menonaktifkan duplikasi raw secara eksplisit sementara main rerun
selalu mempertahankannya.

Legacy `data/legacy/simulation_results_legacy_unverified.csv` tidak mempunyai
seed dan per-order timing; ia tidak dapat dipakai untuk merekonstruksi metric
baru atau mengklaim reproducibility.

## 16. Perbedaan terhadap paper accepted yang wajib direvisi manual

| Topik | Paper accepted | Model rerun kanonik | Dampak |
|---|---|---|---|
| F | 360 s | 720 s | benchmark FTWB dan seluruh angka komparatif berubah |
| setup | 30 s/tour pada narasi tertentu | 180 s/tour | capacity/congestion/TLO berubah material |
| order size | “1–10 items” | 1–10 lines × 1–10 pieces | workload maksimum 100 pieces/order |
| TLO | delivered/completed late | completed late + overdue outstanding | estimand primary berubah |
| warm-up | Welch tanpa nilai | 5,460 s, protocol/evidence tersedia | denominator dan state awal berubah |
| SNH | SNH | SNH code kini cocok; DVNS dihapus | treatment identity dipulihkan |
| MPBH | EDD+beta+restoration | implementasi diselaraskan | legacy MPBH results tidak comparable |
| release | cycle sampai pool/no idle | picker-slot bounded | menghilangkan over-release pending queue |
| urgency | O(1) regression claim | calibrated coefficients+error+cache | claim sekarang terukur |
| picker | longest idle | implemented with deterministic tie | assignment kini auditable |
| composite | Table 4 vs narrative inconsistent | satu matched-block function | Table 4 dan semua kutipan harus dihitung ulang |

Konsekuensinya, angka, ranking, effect sizes, proposition tests, Table 4–6,
figures, managerial implications, limitations, reproducibility statement, dan
response letter harus bersumber dari dataset rerun—bukan dataset legacy.

## 17. Validation status

Selesai lokal: 67 tests, 93.91% branch-aware coverage, Ruff, mypy, artifact
audit smoke, travel-surrogate holdout, Welch evidence, six-cell ablation smoke,
F/V smoke, beta smoke, 30-repeat decision benchmark, atomic byte-boundary
resume test, preflight 207.360-run pass, dan idempotent final-artifact reuse.

Belum menjadikan hasil final tersertifikasi: domain/WMS validation, independent
statistical review, clean signed release tag, final 207,360-run execution,
complete artifact audit, dan independent reproduction.
