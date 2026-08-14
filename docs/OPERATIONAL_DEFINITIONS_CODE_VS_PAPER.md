# Definisi Operasional Simulasi: Codebase Saat Ini versus Paper EJIE-337519

Tanggal baseline: 2026-08-12
Paper pembanding: `docs/2026_EJIE-337519.md`
Code/config pembanding: `src/` dan `config/parameters.yaml` pada working tree saat audit
Status: **AS-IS SPECIFICATION — belum merupakan persetujuan atas model final**

> **Decision freeze 2026-08-14.** Pemilik penelitian telah menetapkan target
> implementasi pada `docs/PAPER_CHANGE_IMPACT_LOG.md`. Bagian-bagian “code saat
> ini” di dokumen ini tetap dipertahankan sebagai audit baseline sebelum
> refactor; ia tidak boleh dibaca sebagai target final.

## 1. Tujuan dan cara membaca dokumen

Dokumen ini mendefinisikan secara operasional model yang **benar-benar
dieksekusi codebase saat ini**, lalu membandingkannya dengan model yang
dinyatakan dalam paper. Dokumen ini menjadi baseline sebelum algoritme
diperbaiki, simulasi diulang, dan catatan reviewer dijawab.

Label perbandingan:

- **MATCH** — definisi code dan paper ekuivalen secara operasional.
- **PARTIAL** — konsep sama, tetapi detail, unit, scope, atau implementasinya
  tidak lengkap/tidak identik.
- **DIFFERENT** — implementasi dapat menghasilkan perilaku atau estimand yang
  berbeda dari paper.
- **CODE ONLY** — ada di codebase, tidak didefinisikan paper.
- **PAPER ONLY** — diklaim paper, tidak ada di codebase/artefak.
- **AMBIGUOUS** — paper atau code tidak cukup spesifik untuk memastikan
  ekuivalensi.

“Code saat ini” berarti release-candidate yang telah diperbaiki setelah audit,
bukan source historis yang menghasilkan dataset legacy. Dataset legacy tetap
dikarantina dan tidak dianggap bukti bahwa code saat ini sesuai paper.

## 2. Ringkasan perbedaan yang dapat mengubah hasil paper

| Severity | Perbedaan | Dampak potensial |
|---|---|---|
| P0 | Paper `SNH`; code `DVNS`, dengan detail fallback yang tidak sepenuhnya ekuivalen | identitas treatment dan interpretasi hasil salah |
| P0 | MPBH paper berbeda dari MPBH code | ranking, TLO, Proposition 1/3/4 dapat berubah |
| P0 | Paper menyebut trigger hanya membuka cycle sampai pool kosong/no idle picker; code sering membuat banyak batch dan mengantrekannya tanpa batas picker idle | efek “timing” tercampur dengan composition/queue release pada semua metode |
| P0 | Paper F=360 s; config F=720 s | baseline FTWB dan klaim 27,04% tidak comparable |
| P0 | Paper order size uniform 1–10 total items; code memakai distribusi nonuniform untuk line count dan quantity per line sehingga total dapat 1–100 | beban sistem, cart fill, route time, lateness berubah besar |
| P0 | Paper pick time 5 s/item dan setup 30 s/tour; code 3 s/item dan 180 s/batch | service time dan congestion workload berubah besar |
| P0 | Paper TLO menghitung completed/delivered late; current confirmatory analysis menambahkan overdue outstanding pada horizon | outcome primer berbeda |
| P0 | Paper mengklaim Welch warm-up; code terminating shift tanpa warm-up deletion | initialization/stopping estimand berbeda |
| P1 | Paper urgency memakai O(1) regression travel approximation; code menghitung route order secara eksplisit dan memasukkan availability aktif | urgency set dan complexity berbeda |
| P1 | Paper menyebut picker longest-idle-first; code tidak menyimpan idle duration dan assignment terjadi lewat polling/process order | assignment discipline berbeda |
| P1 | Paper S-shape berbasis 0,5 m/s; code memakai konstanta waktu topologi tanpa representasi jarak/speed | route duration tidak dapat ditelusuri ke 0,5 m/s |
| P1 | Composite Table 4 dan narasi memakai dua scope normalisasi; current pipeline menghapus composite dan memakai Pareto | angka paper tidak memiliki satu pipeline kanonik |
| P1 | Dataset legacy tidak menyimpan seed atau per-order times | reproducibility dan metrik tardiness reviewer tidak dapat dipenuhi dari data lama |

Kesimpulan operasional: hasil lama tidak boleh dianggap hasil dari code saat ini.
Rerun diperlukan setelah definisi kanonik berikut disetujui dan diimplementasikan.

## 3. Scope sistem dan unit analisis

### 3.1 Sistem yang dimodelkan

**Code saat ini.** Satu run memodelkan satu shift gudang manual picker-to-part
selama `T=28.800` detik. Order datang secara online ke `OrderPool`; satu proses
trigger memindahkan order menjadi satu atau lebih batch di `IOPool`; proses
picker mengambil batch pending, menjalani deterministic trip time, lalu
menandai seluruh order dalam batch selesai pada waktu yang sama.

Tidak dimodelkan secara eksplisit: cart sebagai resource terbatas, picker
heterogeneity, congestion/blocking, break, replenishment, packing, dispatch
vehicle, delivery transport, cancellation, split order, failure, overtime, dan
nonstationary arrivals.

**Paper.** Scope umum sama dan paper mengakui homogeneous arrivals/no congestion
sebagai keterbatasan. Namun istilah “delivered” pada TLO secara operasional di
code hanya berarti picking batch selesai di I/O point, bukan customer delivery.

Status: **PARTIAL**.

### 3.2 Unit analisis

- Unit stochastic terkecil: order `o`.
- Unit keputusan: inspeksi trigger pada waktu simulasi `t`.
- Unit layanan: batch/tour picking.
- Unit observasi raw current: satu scenario × repetition/run.
- Unit factorial scenario:
  `(arrival rate, trigger, pickers, batching, cart capacity, routing)`.
- Unit treatment primer paper: trigger method.

Paper tidak menjelaskan secara memadai apakah inferensi dilakukan pada run,
scenario mean, atau matched repetition; ANOVA lama memperlakukan 207.360 row
sebagai observasi. Current pipeline memperlakukan seed/scenario sebagai paired
structure untuk policy comparison. Status: **DIFFERENT**.

## 4. Waktu, state, entity, dan event

### 4.1 Waktu

| Simbol/field | Definisi code | Unit | Paper | Status |
|---|---|---:|---|---|
| `env.now`, `t` | detik elapsed sejak awal run; mulai 0 | s | current time `t` | MATCH |
| `start_time=28800` | nilai config 08:00, tetapi tidak dipakai engine | s kalender | tidak dinyatakan sebagai parameter eksekusi | CODE ONLY/unused |
| `simulation_time=T` | numeric stop pada 28.800 | s | 8 jam/28.800 s | MATCH |
| warm-up | tidak ada deletion; zero-state terminating run | s | “ditentukan Welch”, tanpa nilai | DIFFERENT |
| `Created Time Seconds=a_i` | waktu order masuk pool | s | order arrival tersirat | MATCH |
| `Due Time Seconds=d_i` | `a_i + allowance_i` | s | deadline/due date | MATCH |
| batch timestamp | waktu batch dimasukkan ke IOPool | s | tidak didefinisikan eksplisit | CODE ONLY |
| `Picking Start Time Seconds=s_i` | waktu batch diambil picker | s | tidak didefinisikan | CODE ONLY |
| `Completion Time Seconds=c_i` | `env.now` setelah trip selesai; sama untuk semua order dalam batch | s | completion time | MATCH |

String `Created Time`/`Due Time` hanya format `HH:MM:SS`; seluruh keputusan
current memakai detik numerik, kecuali sorting `DVNS.n1` masih membaca string
`Due Time`. Karena format memakai zero-padded hour dan run <24 jam, urutan tetap
konsisten pada horizon current, tetapi ketergantungan ini tidak ideal.

### 4.2 State paper dan representasi code

Paper mendefinisikan `S_t=(O_t,B_t,P_t,t)`.

| State | Definisi operasional code |
|---|---|
| `O_t` | copy list `OrderPool.orders`: order generated tetapi belum dipindah ke batch |
| `B_t` | `IOPool.batches` dengan status `pending`, `assigned`, atau `completed`; paper hanya menyebut active assigned batches |
| `P_t` | jumlah picker idle = `num_pickers - len(assigned_batches)`; identitas idle tersedia secara implisit, idle duration tidak disimpan |
| `t` | `env.now` |

Code memiliki state tambahan: generated order ID set, pending batch queue,
assigned batch per picker, completed order list, per-picker cumulative busy
time, current batch ID, RNG state, dan execution/checkpoint metadata.

### 4.3 Entity `Order`

| Field | Definisi |
|---|---|
| `Order ID` | `Cust00001`, naik satu per run |
| `Created Time` | presentational string dari arrival |
| `Created Time Seconds` | numeric arrival `a_i` |
| `Order List` | list pasangan `(item_id, quantity)`; item ID unik di dalam order |
| `Total Item=q_i` | jumlah seluruh quantity line |
| `Due Time` | presentational string deadline |
| `Due Time Seconds` | numeric deadline `d_i` |
| `Picking Start Time Seconds` | ditambahkan saat completed |
| `Completion Time Seconds` | ditambahkan saat completed |
| `Waiting Time Seconds` | `s_i-a_i` |
| `Flow Time Seconds` | `c_i-a_i` |
| `Tardiness Seconds` | `max(0,c_i-d_i)` |

Order outstanding tidak memperoleh start/completion/wait/flow/tardiness record
di raw output. Paper hanya mendefinisikan item count, due, dan completion.

### 4.4 Entity `Batch`

Batch code adalah mapping dengan:

- `batch_id`: integer lokal run;
- `orders`: list order;
- `timestamp`: waktu batch dibentuk;
- `total_items`: jumlah `Total Item`;
- `assigned_to`: picker atau `None`;
- `status`: `pending|assigned|completed`;
- `start_time`, `completion_time`, `picking_time`.

Capacity invariant: setiap order harus `q_i<=C`; FCFS/EDT next-fit memastikan
jumlah item per batch `<=C`. Paper mendefinisikan temporary batch MPBH, tetapi
tidak mendefinisikan lifecycle pending/assigned/completed ini.

### 4.5 Event flow current

```text
initialize empty OrderPool, empty IOPool, p picker processes, RNG
start order-generator process
start exactly one trigger-generator process

while simulation clock < T:
    arrival event:
        generate order and append to OrderPool

    trigger inspection event:
        evaluate method-specific condition
        select zero/more waiting orders
        run FCFS or EDT composition over selected orders
        append produced batches to IOPool
        remove selected orders from OrderPool

    each picker polls every 1 second:
        if picker idle, take earliest pending batch by batch timestamp
        compute deterministic route/trip time
        remain busy for trip time
        complete all orders in batch simultaneously

stop at T without draining
compute aggregate run metrics, including state outstanding at T
```

Paper menyatakan trigger tidak diulang dalam active cycle dan batch formation
berlanjut sampai pool kosong atau no picker. Code tidak memiliki objek “active
batching cycle”; trigger generators memeriksa lagi setiap 1 detik (FTWB setiap
F detik) dan dapat mengisi pending queue. Status: **DIFFERENT**.

## 5. Parameter input dan desain eksperimen

### 5.1 Faktor factorial

| Parameter | Code current | Paper | Status |
|---|---|---|---|
| `incoming_rate λ` | {0.5,1,2,4,8,16} order/min | enam level 0.5–16 | MATCH |
| trigger | FTWB, VTWB, MaxPicker, MaxCart, UrgentPicker, UrgentCart, DVNS, MPBH | sama tetapi `SNH`, bukan DVNS | DIFFERENT |
| `num_pickers p` | 1..12 | 1..12 | MATCH |
| batching | FCFS, EDT | FCFS, EDT | MATCH pada label |
| `cart_capacity C` | {100,150,200} item quantity | {100,150,200} items | MATCH |
| routing | Traversal, Largest Gap | S-shape, Largest Gap | PARTIAL; Traversal diasumsikan S-shape tetapi formula belum diselaraskan |
| scenarios | 6×8×12×2×3×2=6.912 | 6.912 | MATCH |
| repetitions | 30 | 30 | MATCH sebagai nominal |
| total planned | 207.360 | 207.360 | MATCH sebagai nominal, bukan provenance |

`SELECTED_CONFIGURATION` adalah mode single scenario: rate key 4 = 4/min,
DVNS, 12 picker, FCFS, capacity 100, Traversal. Ini bukan factorial default dan
tidak disebut paper.

### 5.2 Parameter stochastic order generation

#### Arrival

```text
interarrival ~ Exponential(scale=60/λ seconds)
arrival process stops after first event with env.now > T
```

Ini menghasilkan homogeneous Poisson process seperti paper. Status: **MATCH**.

#### Due allowance

```text
allowance_i ~ discrete integer Uniform{1800,...,7199} seconds
d_i = a_i + allowance_i
```

Paper menyatakan discrete uniform 30–120 menit. Code upper bound eksklusif,
sehingga tepat 120 menit tidak pernah dipilih dan resolusinya detik, bukan menit.
Status: **PARTIAL**.

#### Line count, quantity, dan total order size

Code memakai distribusi yang sama untuk jumlah line `L_i` dan quantity tiap
line `Q_ij`:

| Nilai | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Probabilitas | .30 | .25 | .22 | .17 | .01 | .01 | .01 | .01 | .01 | .01 |

```text
L_i ~ categorical(values 1..10, probabilities above)
choose L_i distinct item IDs without replacement
Q_ij iid ~ same categorical distribution
Total Item q_i = sum_j Q_ij
```

Akibatnya `q_i` secara teoritis 1–100 dan bukan discrete uniform. Paper
menyatakan “order sizes of 1–10 items (discrete uniform)” tanpa memisahkan lines
dan quantities. Status: **DIFFERENT** dan wajib diselesaikan sebelum rerun.

#### Item popularity

Code memilih item tanpa replacement dari 384 SKU menggunakan 23 kelompok
probabilitas per-item pada `config/item_popularity.yaml`. Probabilitas kelompok
dibuat sebagai synthetic ABC-like profile dan berjumlah 1. Paper menyebut ABC
storage approximating 80/20 tetapi tidak memberi 384 probabilitas, mapping zone,
atau bukti bahwa profile code memenuhi tepat 80/20. Status: **PARTIAL**.

### 5.3 Parameter trigger

| Parameter | Code current | Paper | Status |
|---|---:|---:|---|
| `FTWB_interval F` | 720 s | 360 s | DIFFERENT |
| `VTWB_threshold V` | 12 order | 12 order | MATCH |
| `Urgent_threshold β` | 2 urgent orders | 2 | MATCH untuk metode yang memakainya |
| polling interval | 1 s untuk semua selain FTWB | tidak dinyatakan/event conceptual | CODE ONLY |
| `algorithm_variant` | base + enam ablation labels | tidak ada pada main experiment | CODE ONLY |

Komentar config menyebut `Urgent_threshold` sebagai “maximum allowed urgent
order”, tetapi implementasi memakainya sebagai minimum count `>=β` untuk
trigger. Nama/komentar perlu diperjelas.

### 5.4 Warehouse dan service-time parameters

| Parameter | Code current | Paper | Status |
|---|---:|---:|---|
| SKU | 384 | tidak menyatakan jumlah di teks | CODE ONLY |
| aisle | diturunkan 384/32 = 12 | 12 | MATCH |
| shelves per aisle | 32 item slots | figure/text tidak memberi numeric slot | CODE ONLY |
| `half_shelves` | 16 position units | dua cross aisle; tidak ada definisi sama | PARTIAL |
| depot→first aisle | 2 s | speed 0.5 m/s | DIFFERENT representation |
| between aisles | 4 s per index | speed 0.5 m/s | DIFFERENT representation |
| between shelves | 2 s per position | speed 0.5 m/s | DIFFERENT representation |
| pick time | 3 s per quantity unit | 5 s/item | DIFFERENT |
| setup time | 180 s per executed batch/tour | 30 s per batch/tour | DIFFERENT |

Code tidak memiliki parameter meter atau walking speed; karena itu klaim
0,5 m/s tidak dapat dihitung/diuji dari code tanpa definisi jarak.

### 5.5 Reproducibility/control parameters

| Parameter | Definisi code | Paper |
|---|---|---|
| `master_seed` | 20260812 | tidak dilaporkan |
| run seed | first 64 bit SHA-256 dari `master_seed|arrival_key|repetition` | tidak dilaporkan |
| CRN | semua policy/faktor dengan arrival key dan repetition sama berbagi seed | tidak dilaporkan |
| `randomize_execution_order` | shuffle deterministic planned run order | tidak dilaporkan |
| config hash | SHA-256 canonical merged config | tidak dilaporkan |
| source hash | SHA-256 source/config/dependency files | tidak dilaporkan |
| horizon policy | `fixed_with_censoring` | warm-up Welch + 8 h, censoring tidak dijelaskan |

Seed tidak memasukkan cart, picker, batching, atau routing. Demand stream tetap
sama karena random generation hanya bergantung pada arrival key/repetition;
ini disengaja untuk CRN. Dataset legacy tidak menyimpan seed, sehingga skema ini
tidak membuktikan reproducibility hasil paper lama.

### 5.6 Sensitivity-only parameters

Current `src/sensitivity.py` memiliki engineering ranges berikut, belum domain-
validated dan tidak ada pada eksperimen paper:

| Input | Range low–high |
|---|---:|
| due minimum | 1.200–2.400 s |
| due maximum | 5.400–9.000 s |
| pick time | 2–6 s/item |
| setup time | 60–300 s/batch |
| walking-time multiplier | 0,75–1,50 |

LHS dan OAT current mencatat sampled values, tetapi range ini tidak boleh
dipakai sebagai evidence paper sebelum approval domain/PI.

## 6. Algoritme pembentukan batch

### 6.1 FCFS current

```text
input: ordered list selected_orders, capacity C
reject if any individual order q_i > C
current_batch = empty
for order in supplied sequence:
    if q(current_batch)+q_i <= C:
        append order
    else:
        emit current_batch
        current_batch = [order]
emit final non-empty batch
```

Ini adalah next-fit yang mempertahankan **urutan input**, bukan jaminan urutan
arrival jika trigger sebelumnya telah menyortir/memilih order. Paper menyebut
FCFS tetapi tidak mendefinisikan bin-packing detail. Status: **PARTIAL**.

### 6.2 EDT current

Sama dengan FCFS next-fit setelah sorting ascending `(Due Time Seconds, Due Time
string)`. Paper menyebut Earliest Due Date. Status: **MATCH/PARTIAL**, karena
tie-break dan next-fit tidak dijelaskan paper.

### 6.3 Perbedaan cycle formation global

Paper: setelah trigger, jalankan selected batching rule sampai pool kosong atau
tidak ada picker tersedia; trigger hanya timing decision.

Code: masing-masing trigger menentukan sendiri selected order, memanggil
FCFS/EDT, lalu mengantrekan semua batch yang dihasilkan. `IOPool` boleh memiliki
pending batches lebih banyak dari idle picker. Dengan demikian treatment
trigger juga mengubah order selection dan jumlah work yang dilepas.

Status: **DIFFERENT**. Ini harus diperbaiki sebelum ablasi timing-versus-
composition reviewer dapat diinterpretasikan.

## 7. Urgency estimator

### 7.1 Definisi paper

Paper menyatakan order urgent bila:

```text
t + ProcessingTime(o) + SetupTime > DueTime(o)
ProcessingTime(o) = 5 s × Items(o) + O(1) regression travel approximation
SetupTime = 30 s
```

### 7.2 Definisi code

```text
availability_heap = [t] for each picker
for each currently active batch (up to picker count):
    remaining = max(0, full_route_time(active_batch) - elapsed)
    availability[picker] = t + remaining
heapify availability

for waiting order o sorted by due time:
    available_at = earliest picker availability
    trip(o) = setup + explicit routing(o) + pick_time × quantity(o)
    predicted_completion = available_at + trip(o)
    put predicted_completion back into heap
    urgent if predicted_completion > due(o)
```

Perbedaan:

- code mengantrekan seluruh waiting pool secara hypothetical EDT dan
  mempertimbangkan parallel pickers; paper formula menilai single order dari `t`;
- code mempertimbangkan active batch, tetapi mengabaikan batch pending yang
  sudah dilepas ke IOPool;
- code route calculation bukan O(1) regression approximation;
- code trip sudah mengandung setup tepat sekali; nilai 180 s, bukan 30 s;
- code route per order memakai routing scenario aktual;
- complexity code minimal sorting `O(n log n)` + heap `O(n log p)` + route
  calculations, bukan O(n) seperti klaim paper.

Status: **DIFFERENT**.

## 8. Delapan algoritme trigger

Semua loop kecuali FTWB menginspeksi state setiap 1 detik.

### 8.1 FTWB

**Code current**

```text
every F=720 seconds:
    if pool non-empty:
        selected = all waiting orders
        compose selected with configured FCFS/EDT into any number of batches
        enqueue all batches
        clear pool
```

**Paper:** sama secara konseptual tetapi `F=360` dan rule `(t mod F)=0`.
Paper cycle juga seharusnya dibatasi picker availability. Status:
**DIFFERENT**.

### 8.2 VTWB

**Code current**

```text
if |O_t| >= V=12:
    selected = first 12 orders only
    compose selected with FCFS/EDT
    enqueue all resulting batches
    remove selected
```

**Paper:** trigger bila `|O_t|>=12`; tidak jelas apakah hanya V order atau cycle
memproses pool sampai no picker. Section 3.3 menyiratkan cycle, bukan fixed first
V subset. Code juga tidak mensyaratkan picker tersedia. Status: **AMBIGUOUS /
likely DIFFERENT**.

### 8.3 MaxPicker

**Code current**

```text
if pool non-empty and at least one picker not assigned:
    selected = all waiting orders
    compose into any number of batches
    enqueue all; clear pool
```

Paper condition sama, tetapi trigger-only cycle seharusnya berhenti saat no
idle picker. Code dapat mengantrekan jauh lebih banyak batch daripada idle
picker. Status: **PARTIAL/DIFFERENT**.

### 8.4 MaxCart

**Code current**

```text
if sum quantity in pool >= C:
    scan pool order sequence
    append while next order keeps total <= C
    stop at first overflow order (do not skip it)
    if selected non-empty:
        compose selected; enqueue; remove selected
```

Paper mensyaratkan total item `>=C` **dan picker tersedia**. Code tidak memeriksa
picker. Selection code juga bisa menghasilkan underfilled batch karena berhenti
pada first overflow walaupun order berikutnya mungkin muat. Status:
**DIFFERENT**.

### 8.5 UrgentPicker

**Code current**

```text
if pool non-empty:
    urgent_count = current urgency estimator
    all_idle = available_pickers == total_pickers
    if urgent_count >= β or all_idle:
        selected = all waiting orders
        compose/enqueue all; clear pool
```

Paper decision condition secara literal sama. Namun urgency estimator berbeda
dan “all pickers idle” berbeda dari “at least one idle”; cycle dapat mengantrekan
banyak batch. Status: **PARTIAL/DIFFERENT**.

### 8.6 UrgentCart

**Code current**

```text
if pool non-empty and (urgent_count >= β or waiting quantity >= C):
    selected = all waiting orders
    compose/enqueue all; clear pool
```

Paper juga mensyaratkan setidaknya satu picker idle. Code tidak. Urgency dan
cycle berbeda. Status: **DIFFERENT**.

### 8.7 DVNS current versus SNH paper

**Code current**

```text
n1 = all waiting sorted by due string ascending
n2 = all waiting sorted by Total Item descending
urgent = current urgency estimator
n3 = urgent in estimator order + remaining n2

if urgent_count >= β:
    best = all urgent orders
else if total quantity(n1) <= C and picker available:
    best = n1
else:
    scan n2 from largest; append until first order that would overflow C
    if selected_n2 and picker available: best = selected_n2
else fallback:
    scan n3 similarly

compose best with configured FCFS/EDT; enqueue; remove best
```

Catatan implementasi:

- urgent branch tidak memeriksa picker tersedia;
- urgent subset dapat melebihi capacity, lalu FCFS/EDT memecahnya menjadi
  beberapa batch;
- n2 branch hampir selalu menemukan minimal satu order, sehingga n3 fallback
  praktis sulit/tidak terjangkau untuk valid orders `q_i<=C`;
- “maximize capacity” adalah descending next-prefix, bukan optimization subset;
- variants: `urgency_only`, `cart_only`, dan `no_hybrid` menghapus cabang
  tertentu untuk engineering ablation.

**SNH paper** memakai urgency → all EDT fit → capacity maximizing subset →
hybrid fallback, selalu ketika picker tersedia. Nama, picker guard, capacity
semantics, dan reachability fallback berbeda. Status: **DIFFERENT**.

### 8.8 MPBH current versus paper

**Code current**

```text
if pool non-empty and picker available:
    for each order:
        priority(o) = (due(o)-t-trip(o)) / max(1, TotalItem(o))
    sort ascending by (priority, due, Order ID)
    selected = greedy scan that SKIPS non-fitting orders and keeps later fitting orders
    compose selected with configured FCFS/EDT
    enqueue; remove selected
```

Current MPBH variants:

- `base`: slack adjusted route divided by quantity;
- `no_quantity`: denominator 1;
- `no_route`: route term 0.

**MPBH paper**:

```text
when picker available:
    sort O_t by earliest due date
    B_temp = empty
    for each order:
        tentatively append
        if predicted late count(B_temp) > β or quantity(B_temp) > C:
            remove order with latest due date
            recheck
    dispatch B_temp if non-empty
```

Paper MPBH tidak mendefinisikan slack-per-item priority; code MPBH tidak memakai
β atau feasibility restoration. Configured FCFS/EDT sesudah ranking juga dapat
mengubah composition semantics. Status: **DIFFERENT (P0)**.

## 9. Routing, service, dan picker assignment

### 9.1 Item-position mapping

```text
aisle(item) = ceil(item / 32)
shelf(item) = ((ceil(item/2)-1) mod 16)+1
```

Quantity diexpand menjadi repeated item positions untuk pick time, tetapi route
aisle/shelf set effectively tidak bertambah karena repeat location sama.

### 9.2 Traversal/S-shape current

Trip walking time adalah jumlah komponen custom:

- depot to first visited aisle;
- full half-aisle traversal untuk visited aisles tertentu;
- cross-aisle transitions;
- farthest-shelf return pada last aisle tergantung parity;
- return dari last aisle.

Formula memakai konstanta waktu per topology index, bukan distance/speed.
Paper hanya menyebut standard S-shape dan 0,5 m/s. Equivalence belum dibuktikan.

### 9.3 Largest Gap current

Code menghitung largest internal/end gap untuk intermediate aisles lalu
mengurangi traversal depth; first/last aisle menggunakan rules khusus. Fungsi
helper `calculate_largest_gap` ada tetapi main route menghitung gaps langsung.
Paper tidak memberi pseudocode, sehingga fidelity terhadap Roodbergen–Koster
belum dapat diverifikasi dari paper saja.

### 9.4 Total trip/service time

```text
trip_time(batch) = setup_time
                 + walking_time(unique route positions)
                 + picking_time_per_item × sum quantities
```

Setup dibayar sekali per batch. Seluruh order batch mulai dan selesai bersama.
Paper menyatakan setup 30 s dan base pick 5 s, sehingga struktur sama tetapi
nilai berbeda. Paper urgency menyebut travel approximation berbeda dari route
execution; code memakai function route yang sama untuk urgency dan execution.

### 9.5 Picker assignment

Code:

- setiap picker process polling tiap 1 detik;
- pending batches disortir ascending `timestamp`;
- picker process pertama yang terjadwal mengambil earliest pending batch;
- tidak ada state `idle_since`, sehingga longest-idle-first tidak
  diimplementasikan eksplisit;
- picker dapat memegang maksimal satu batch.

Paper menyatakan longest idle time first. Status: **DIFFERENT/unsupported**.

## 10. Initialization, stopping, dan censoring

### 10.1 Initialization

Code mulai dengan zero orders, zero batches, semua picker idle, busy time nol.
Tidak ada preload atau warm-up. Paper tidak menyatakan initial state tetapi
mengklaim warm-up Welch. Status: **PARTIAL/DIFFERENT**.

### 10.2 Stopping

Code menjalankan `env.run(until=T)` dan tidak drain. Order dapat berada di:

- waiting `OrderPool`;
- pending batch;
- assigned/active batch;
- completed batch.

Invariant ditujukan untuk menjaga:

```text
generated = waiting + pending + active + completed
```

Paper TLO/throughput hanya merujuk order completion dan tidak menjelaskan
outstanding/censoring. Status: **DIFFERENT/underreported**.

## 11. Pengukuran per order, batch, picker, dan run

### 11.1 Pengukuran per order current

Untuk completed order:

```text
waiting_i    = start_i - arrival_i
flow_i       = completion_i - arrival_i
tardiness_i  = max(0, completion_i - due_i)
late_i       = 1[completion_i > due_i]
```

Due exactly completion adalah on-time. Paper memakai strict `c_i>d_i`, sama.

### 11.2 Pengukuran primer dan perbedaan estimand

| Metric | Formula code current | Formula paper | Status |
|---|---|---|---|
| late completed | `Σ_completed 1[c_i>d_i]` | TLO `Σ_i 1[c_i>d_i]` untuk processed/delivered | MATCH jika hanya completed |
| late outstanding | waiting/pending/active dengan `d_i<T` | tidak didefinisikan | CODE ONLY |
| analysis `late_orders` | late completed + late outstanding | paper TLO delivered late | DIFFERENT |
| throughput per hour | `completed/(T/3600)` | Eq. (3) count completed; Table 4 “per hour” | PARTIAL; paper internal ambiguity |
| picker utility % | `(completed busy + elapsed active busy)/(T×p)×100` | mean active fraction | MATCH/PARTIAL |
| composite | tidak dihitung current pipeline; Pareto dipakai | weighted score 0.6/0.3/0.1 | PAPER ONLY pada pipeline current |

Paper TLO tidak dapat mengevaluasi unfinished order tanpa `c_i`. Current
analysis menghukum hanya outstanding yang sudah melewati due sebagai late count,
sedangkan service level menghukum **semua** outstanding, termasuk not-yet-due.
Kedua outcome menjawab pertanyaan berbeda dan harus dinamai eksplisit.

### 11.3 Semua metric hasil run current

| Output | Definisi dan unit |
|---|---|
| `generated_orders` | semua arrivals sebelum horizon; order |
| `completed_orders` | order dengan batch selesai sebelum stop; order |
| `outstanding_orders` | generated − completed; order |
| `throughput_per_hour` | completed/(T/3600); order/jam |
| `late_completed_orders` | completed dengan `c_i>d_i`; order |
| `late_outstanding_orders` | outstanding dengan `d_i<T`; order |
| `service_level_percent` | `(completed-late_completed)/generated×100`; % generated |
| `mean_tardiness_seconds` | mean tardiness completed, termasuk nol; s |
| `median_tardiness_seconds` | interpolated/order statistic median completed; s |
| `max_tardiness_seconds` | max completed; s |
| `p95_tardiness_seconds` | linear-interpolated p95 completed; s |
| `mean_flow_time_seconds` | mean `c_i-a_i` completed; s |
| `p95_flow_time_seconds` | p95 completed; s |
| `mean_waiting_time_seconds` | mean `s_i-a_i` completed; s |
| `p95_waiting_time_seconds` | p95 completed; s |
| `picker_utility_percent` | aggregate busy/(T×p); % |
| `picker_utilization_spread_pp` | max−min utilization picker; percentage point |
| `mean_cart_utilization_percent` | mean completed batch `total_items/C×100`; % |
| `trip_count` | jumlah completed batches; trip |
| `conservation_ok` | invariant identity order; boolean |

Metric yang diminta reviewer tetapi belum output eksplisit:

- `late_order_ratio`: dapat diturunkan, tetapi denominator/policy outstanding
  harus dipilih;
- `on_time_rate`: current `service_level_percent/100`, bukan sekadar
  `1-(late completed/generated)` bila definisi berubah;
- average tardiness conditional-on-late: belum ada;
- per-order event data: belum persisted;
- decision time per trigger: belum ada.

### 11.4 Batch dan resource measurements

- Picker busy time adalah planned deterministic trip time untuk completed batch
  ditambah elapsed active time pada horizon.
- Pending time tidak dihitung busy.
- Cart utilization hanya completed batches; pending/active excluded.
- Trip count hanya completed batches.
- Tidak ada queue-length time average, batch-size distribution output, order
  pool waiting trajectory, picker idle duration, atau cart count/cost.

Paper hanya melaporkan picker utilization; reviewer timing/managerial guidance
memerlukan metric tambahan di atas.

### 11.5 Provenance dan audit fields current

Setiap result row juga menyimpan:

- `run_uuid`, sequential execution `run_id`, repetition, seed;
- success/failure status, error type/message;
- seluruh scenario labels dan algorithm variant;
- config SHA-256, Git commit, dirty-state flag, source-tree SHA-256, model
  version;
- sensitivity sample ID dan sampled parameter values.

Manifest menyimpan config/source/dependency metadata, execution-order seed,
environment, counts, checksum, start/end, dan failure summary. Paper tidak
melaporkan metadata ini dan legacy CSV tidak memilikinya.

## 12. Composite score dan analysis pipeline

### 12.1 Definisi paper

Untuk metric `x` antar heuristics:

```text
TLO_norm = 1 - (TLO-TLO_min)/(TLO_max-TLO_min)
TH_norm  = (TH-TH_min)/(TH_max-TH_min)
U_norm   = (U-U_min)/(U_max-U_min)
C = 0.6*TLO_norm + 0.3*TH_norm + 0.1*U_norm
```

Paper mengatakan min/max across all heuristics, tetapi tidak menetapkan apakah
normalisasi terjadi pada run, scenario, atau aggregate mean.

### 12.2 Dua implementasi implisit pada hasil paper

- Table 4 dapat direproduksi dengan normalisasi per factorial cell setelah 30
  replikasi dipool, lalu score dirata-rata per heuristic.
- Narasi dapat direproduksi dengan aggregate mean per heuristic terlebih dahulu,
  lalu min/max atas delapan mean.

Contoh MPBH: 0,864 pada Table 4 versus 0,924 pada narasi.

### 12.3 Pipeline current

Current `analysis_pipeline.py` tidak menghitung composite; ia menghitung summary
service/throughput/utilization/tardiness, Pareto frontier, scenario winners,
paired comparisons dengan Holm correction, serta factorial count/binomial/OLS
models. Historical `analysis3.py` memakai normalisasi **per trigger** dan bobot
0.4/0.3/0.3, bukan Persamaan (8).

Status: **DIFFERENT**. Satu corrected composite function harus dibuat sebagai
secondary analysis tanpa menggantikan Pareto primer.

## 13. Statistical analysis current versus paper

| Area | Current pipeline | Paper | Status |
|---|---|---|---|
| count outcome | Poisson + negative binomial factorial | ANOVA | DIFFERENT; current lebih sesuai count |
| proportion | grouped binomial | tidak ada | CODE ONLY |
| continuous throughput | OLS HC3 | ANOVA/Tukey umum | DIFFERENT |
| CRN | paired by seed/scenario | tidak diperhitungkan eksplisit | DIFFERENT |
| multiplicity | Holm | Tukey HSD | PARTIAL |
| effects | paired differences + 95% CI | F, p, partial eta² | DIFFERENT |
| interactions | specified factorial interactions | ANOVA tables dengan pelaporan inkonsisten | PARTIAL |
| Pareto | tersedia | tidak ada | CODE ONLY |
| weight sensitivity | belum ada | dinyatakan out of scope; reviewer meminta | MISSING |

Analisis final harus dibekukan sebelum rerun. Mengembalikan begitu saja ANOVA
lama akan mengabaikan count distribution, factorial structure, dan CRN.

## 14. Ablation, sensitivity, dan benchmark current

### 14.1 Ablation current

- DVNS: `base`, `urgency_only`, `cart_only`, `no_hybrid`.
- MPBH: `base`, `no_quantity`, `no_route`.

Ini ablation komponen internal, bukan pemisahan trigger timing versus batch
composition seperti permintaan reviewer. Status: **tidak menjawab R1-Mayor #1**.

### 14.2 Runtime benchmark current

Current benchmark mengukur whole simulation dan route kernel dengan
`perf_counter`, CPU time, sampled RSS, Python memory, dan descriptive t-interval.
Ia belum mengukur decision kernel tiap trigger pada pool size n. Status:
**PARTIAL terhadap R2-Mayor #3**.

### 14.3 Beta dan benchmark calibration

- β ada dan parameterized, tetapi current MPBH tidak menggunakannya.
- F/V parameterized, tetapi belum ada tuning/evaluation sweep runner final.
- Tidak ada MIP comparator.

## 15. Appendix identifier yang wajib dipertahankan atau dimigrasikan

Bagian ini mencantumkan identifier exact agar refactor tidak diam-diam
menghilangkan parameter/output. Bila nama diganti, migration map wajib dibuat.

### 15.1 Seluruh schema config utama

| Exact config path | Fungsi operasional |
|---|---|
| `incoming_rate.*` | dictionary level λ |
| `cart_capacity.*` | dictionary level C |
| `trigger_method.*` | registry label delapan trigger |
| `trigger_parameters.FTWB_interval` | F dalam detik |
| `trigger_parameters.VTWB_threshold` | V dalam order |
| `trigger_parameters.Urgent_threshold` | β dalam urgent-order count |
| `batching_method.*` | registry FCFS/EDT |
| `routing_policy.*` | registry Traversal/Largest Gap |
| `simulation_time` | horizon T dalam detik |
| `master_seed` | root seed deterministic |
| `repetitions` | jumlah replication per scenario |
| `horizon_policy` | hanya `fixed_with_censoring` diterima validator current |
| `due_time_min_seconds` | lower due allowance |
| `due_time_max_seconds` | exclusive upper due allowance |
| `randomize_execution_order` | deterministic shuffle switch |
| `algorithm_variant` | base/ablation behavior switch |
| `experiment_design.incoming_rate_keys` | level λ dalam mode full |
| `experiment_design.trigger_method_keys` | level trigger dalam mode full |
| `experiment_design.num_pickers` | level picker dalam mode full |
| `experiment_design.batching_method_keys` | level composition dalam mode full |
| `experiment_design.cart_capacity_keys` | level cart dalam mode full |
| `experiment_design.routing_policy_keys` | level routing dalam mode full |
| `start_time` | present tetapi unused oleh engine |
| `warehouse_items` | jumlah SKU |
| `item_popularity_file` | path profile probability SKU |
| `num_pickers_options` | domain picker count yang valid |
| `walking_times.depot_to_first_aisle` | waktu topology edge, detik |
| `walking_times.between_aisles` | waktu topology edge, detik |
| `walking_times.between_shelves` | waktu topology edge, detik |
| `picking_time_per_item` | detik per quantity unit |
| `setup_time` | detik per batch/tour |
| `warehouse_structure.shelves_per_aisle` | mapping item→aisle |
| `warehouse_structure.half_shelves` | depth position per half aisle |
| `SELECTED_CONFIGURATION.incoming_rate` | selected λ key |
| `SELECTED_CONFIGURATION.trigger_method` | selected trigger key |
| `SELECTED_CONFIGURATION.num_pickers_options` | selected picker count |
| `SELECTED_CONFIGURATION.batching_method` | selected batching key |
| `SELECTED_CONFIGURATION.cart_capacity` | selected capacity key |
| `SELECTED_CONFIGURATION.routing_policy` | selected routing key |

Sensitivity runner menambahkan runtime-only keys `input_sample_id` dan
`walking_time_multiplier`, serta memodifikasi due bounds,
`picking_time_per_item`, `setup_time`, dan ketiga walking times pada deep-copied
config. `LoadedConfig.sha256` dihitung setelah merge/override.

### 15.2 Seluruh schema result row current

Identity/control:

`run_uuid`, `run_id`, `repetition`, `seed`, `status`, `error_type`,
`error_message`.

Scenario/treatment:

`incoming_rate`, `cart_capacity`, `trigger_method`, `batching_method`,
`routing_policy`, `algorithm_variant`, `num_pickers`.

Operational outcomes:

`generated_orders`, `completed_orders`, `outstanding_orders`,
`throughput_per_hour`, `late_completed_orders`, `late_outstanding_orders`,
`service_level_percent`, `mean_tardiness_seconds`,
`median_tardiness_seconds`, `max_tardiness_seconds`,
`p95_tardiness_seconds`, `mean_flow_time_seconds`, `p95_flow_time_seconds`,
`mean_waiting_time_seconds`, `p95_waiting_time_seconds`,
`picker_utility_percent`, `picker_utilization_spread_pp`,
`mean_cart_utilization_percent`, `trip_count`, `conservation_ok`.

Provenance/sensitivity:

`config_sha256`, `git_commit`, `git_dirty`, `source_tree_sha256`,
`model_version`, `input_sample_id`, `sampled_due_time_min_seconds`,
`sampled_due_time_max_seconds`, `sampled_picking_time_per_item`,
`sampled_setup_time`, `sampled_walking_time_multiplier`.

Failed rows hanya dijamin memiliki identity, failure, dan provenance minimum;
scenario/outcome fields lain dapat kosong. Audit final mensyaratkan tidak ada
failed row.

### 15.3 Internal state variables utama

| Module/class | Variable | Semantics |
|---|---|---|
| `OrderPool` | `orders` | waiting orders only |
| `OrderPool` | `generated_order_ids` | all identities ever generated |
| `IOPool` | `batches` | all pending/assigned/completed batches; completed tidak dihapus pada normal run |
| `IOPool` | `assigned_batches` | picker→active batch |
| `IOPool` | `current_batch_id` | next local batch integer |
| `IOPool` | `num_pickers` | resource capacity |
| `IOPool` | `picker_utilization` | accumulated completed busy seconds; nama sebenarnya busy-time accumulator |
| `IOPool` | `picker_busy_time` | completed busy seconds by picker |
| `IOPool` | `total_completed_orders` | completed order counter |
| `IOPool` | `total_late_orders` | completed-late counter |
| `IOPool` | `completed_orders` | in-memory completed order records |
| runner | `planned` | ordered scenario×repetition jobs |
| runner | `execution_order_seed` | deterministic shuffle seed |
| runner | `partial_results.csv` | append-only checkpoint evidence |
| runner | `checkpoint.json` | expected/completed count and last UUID |

### 15.4 Auxiliary runner controls dan measurements

- Experiment CLI: `--config`, `--output-dir`, `--mode`, `--repetitions`.
- Ablation CLI: repetitions dan tujuh variant labels yang disebut Section 14.
- Sensitivity CLI: sample count/seed melalui config master seed, serta mode LHS
  atau OAT.
- Benchmark CLI: `repeats` (minimal 2), `route_calls` (minimal 1), memory sample
  interval 0,005 s.
- Benchmark outputs: `wall_seconds`, `cpu_seconds`,
  `cpu_utilization_percent`, `peak_process_rss_bytes`,
  `peak_python_memory_bytes`, `simulated_seconds_per_wall_second`, dan
  `microseconds_per_call`, masing-masing diringkas mean/SD/approximate 95% CI.
- Analysis derived fields: `late_orders`, `late_rate`,
  `service_proportion`, `pareto_optimal`, paired difference/CI/raw and Holm-
  adjusted p-values, scenario winner, model diagnostics, AIC, dan dispersion.

Identifier auxiliary ini tidak semuanya treatment parameter paper, tetapi harus
dicatat karena memengaruhi reproducibility, resource evidence, atau inferensi.

## 16. Daftar keputusan sebelum perbaikan dan rerun

Keputusan berikut merupakan kontrak implementasi minimum:

1. Sahkan `SNH` sebagai nama/metode kanonik dan pseudocode exact-nya.
2. Sahkan MPBH paper (EDD + β + feasibility restoration) atau revisi paper agar
   sesuai algoritme lain; jangan mencampur keduanya.
3. Pisahkan `TriggerPolicy` dari `CompositionRule`; tetapkan satu batching cycle
   dan batas idle picker yang sama untuk seluruh treatment.
4. Bekukan order-size semantics: total items uniform 1–10 atau line/quantity
   model alternatif dengan justifikasi.
5. Rekonsiliasi F, pick time, setup time, dan walking geometry/speed.
6. Pilih urgency definition: conservative single-order paper atau queue-aware
   estimator current; dokumentasikan pending queue treatment dan complexity.
7. Implementasikan longest-idle-first atau koreksi klaim paper.
8. Tetapkan estimand horizon: delivered-late, overdue-at-horizon, service level,
   dan treatment order outstanding/censoring.
9. Tetapkan terminating no-warm-up atau implementasi Welch yang sesuai tujuan
   steady-state; keduanya tidak boleh diklaim sekaligus.
10. Bekukan corrected composite scope, reference set, constant-range rule, dan
    posisinya sebagai secondary outcome.
11. Bekukan factorial/subset reviewer, CRN mapping, repetitions/power, planned
    contrasts, tuning/evaluation separation, dan multiplicity correction.
12. Tambahkan per-order persistence dan decision-timing instrumentation sebelum
    run besar agar tidak perlu rerun dua kali.

## 17. Acceptance criteria dokumen operasional final

Dokumen ini dapat dinaikkan dari AS-IS menjadi FINAL hanya jika:

- setiap DIFFERENT/PARTIAL di atas memiliki keputusan tertulis;
- pseudocode final memiliki golden test yang dapat dihitung manual;
- config final memuat unit dan provenance setiap parameter;
- model specification, source, config, data dictionary, dan paper memakai nama
  serta formula identik;
- semua KPI memiliki numerator, denominator, horizon, censoring rule, dan unit;
- reviewer experiments dapat dijalankan dari interface yang sama tanpa special
  case yang mengubah treatment;
- run manifest merekam source/config/seed/hardware dan seluruh output dapat
  diaudit;
- independent reviewer menyetujui mapping code-versus-paper sebelum signed tag.

Sampai criteria tersebut dipenuhi, angka hasil rerun hanya boleh disebut pilot
engineering dan tidak boleh menggantikan Table 4 atau jawaban reviewer.
