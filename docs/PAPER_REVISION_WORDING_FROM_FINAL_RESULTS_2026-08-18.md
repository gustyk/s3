# Daftar revisi manuskrip berbasis hasil final — EJIE-337519

Tanggal penyusunan: 18 Agustus 2026  
Paper sumber yang **tidak diubah**: `docs/2026_EJIE-337519.md`  
Tujuan: menjadi naskah kerja untuk revisi manual paper dan pembuatan versi
track-changes/highlighted.

## Aturan penggunaan

- Nomor baris merujuk file Markdown paper asli, bukan nomor halaman layout
  jurnal. Nomor halaman harus diisi setelah manuskrip revisi selesai ditata.
- Kutipan lama di bawah dinormalisasi hanya pada spasi dan formula yang rusak
  akibat ekstraksi PDF/Word; substansi dan angkanya dipertahankan.
- Teks **Replacement wording** ditulis dalam bahasa Inggris agar dapat langsung
  dipindahkan ke manuskrip.
- Semua hasil numerik berasal dari hasil final kanonik atau eksperimen reviewer.
  Dataset legacy dan angka pada paper accepted tidak boleh dicampur.
- Nilai p yang tersimpan sebagai `0.0` karena keterbatasan floating point tidak
  boleh ditulis sebagai `p = 0`; gunakan CI, besar efek, dan bila diperlukan
  `p < 0.001`.
- Analisis CRN berpasangan adalah bukti inferensial utama pada revisi ini, tetapi
  jangan menyebutnya *preregistered*: `ANALYSIS_PLAN.md` masih berstatus draft,
  MPID belum disahkan, dan review statistik independen masih terbuka.
- Seed permintaan dibagi oleh semua konfigurasi pada kombinasi arrival-rate ×
  replication. Karena itu, 25,920 scenario-run pairs bukan 25,920 unit stochastic
  independen. CI pada dokumen ini dihitung ulang dari mean effect per independent
  demand-stream cluster (180 cluster main; 60 cluster ablation/β), dengan variasi
  replikasi dihitung di dalam setiap fixed arrival-rate stratum dan enam strata
  main digabung berbobot setara menggunakan derajat bebas Welch–Satterthwaite.
  Pipeline analisis dan tabel turunannya harus diperbarui sebelum submission agar
  menghasilkan stratified cluster-aware CI yang sama.
- Wording tentang DOI, immutable archive, validasi WMS/SME, MPID, dan reproduksi
  independen mengandung placeholder karena bukti eksternal tersebut belum ada.

## Sumber data yang mengikat wording

| Bukti | Lokasi | Status |
|---|---|---|
| Main factorial 207,360 run | `outputs/final-q1-v1/full-factorial/` | audit teknis PASS; 207,360/207,360 sukses |
| Tabel manuskrip final | `outputs/final-q1-v1/full-factorial/manuscript-tables/` | aggregate means final; paired-CI CSV perlu diganti dengan stratified cluster-aware CI pada dokumen ini |
| Metrik order-level | `outputs/final-q1-v1/full-factorial/additional-metrics/` | 621,955,584 raw rows; 522,713,088 measurement rows ter-rekonsiliasi |
| Composite dan Pareto | `outputs/final-q1-v1/full-factorial/composite/` dan `analysis/` | matched-block; empat skema bobot |
| Ablasi timing × composition | `outputs/final-q1-v1/reviewer/ablation/` | 4,320 run; seluruh cell audit PASS |
| Kalibrasi F/V | `outputs/final-q1-v1/reviewer/calibration/` | tuning/held-out terpisah |
| Sensitivitas β | `outputs/final-q1-v1/reviewer/beta/` | 23,040 run |
| Benchmark keputusan | `outputs/final-q1-v1/reviewer/decision-benchmark/` | 1,440 pengukuran |

Catatan provenance: hasil utama terikat pada config SHA-256
`d359bc8f3a2cda65123a640155339ce18092ae8214913fc6561b916ffd42234f`,
results SHA-256
`720f2d70f8ee9e6b440ae30b639aa8513a007ec9fc462b7dc1f4710d362b4448`,
dan orders SHA-256
`328206013610b3fa07723776da2f112ddfa4ab349f6ea0b57b0d351087a3dbf4`.
Manifest merekam `git_dirty=True`; fakta ini wajib dinyatakan pada transparency
statement sampai ada reproduksi dari signed clean release.

---

## 1. Judul

**Lokasi:** judul, baris 3–4.

**Kutipan lama yang diganti**

> Adaptive Heuristics for Order Batching Initiation Timing in Same-Day Delivery Warehouses

**Replacement wording**

> **Adaptive Batch-Release and Composition Heuristics for Same-Day Delivery Warehouses: A Discrete-Event Simulation Study**

Alasan perubahan judul: MPBH dan SNH bukan treatment “timing murni”; keduanya
memiliki logika komposisi intrinsik. Judul lama mempertahankan confounding yang
disorot reviewer.

## 2. Abstract

**Lokasi:** Section Abstract, paragraf tunggal, baris 7–18.

**Kutipan lama yang diganti seluruhnya**

> Same-day delivery (SDD) intensifies order picking and order batching demands in e-commerce distribution warehouses, yet order batching initiation timing remains critically underexplored. Traditional approaches—Fixed Time Window Batching (FTWB) and Variable Time Window Batching (VTWB)—fail to exploit real-time system states, undermining order fulfilment performance. Grounded in Time-Based Competition (TBC) theory, this study develops and evaluates six adaptive heuristics incorporating order urgency and resource availability, benchmarked via discrete-event simulation across 6,912 scenarios (207,360 runs). The Modified Priority Based Heuristic (MPBH) achieves the greatest reduction in total late orders, averaging 27.04% improvement over benchmarks. ANOVA reveals that operational context—trigger method, order rate, and picker availability—explains more performance variance than heuristic choice alone. Crucially, batch initiation timing exerts greater influence on order fulfilment than batch composition, extending TBC theory to warehouse micro-operations and yielding computationally efficient, implementable heuristics.

**Replacement wording**

> Same-day delivery (SDD) makes the release and composition of warehouse picking batches time-critical, yet these decisions are commonly governed by fixed intervals or simple order-count thresholds. Drawing on Time-Based Competition as a temporal-performance lens, this study evaluates two static benchmarks and six adaptive batch-release policies in a discrete-event simulation of a manual picker-to-part warehouse. The full factorial design comprises 6,912 scenarios and 207,360 runs, with 30 common-random-number replications per scenario and a 5,460-s Welch warm-up preceding an eight-hour measurement period. Total late orders count both orders completed after their due time and overdue orders still outstanding at the fixed horizon. MPBH produced the lowest mean total late orders (1,788.83), the highest mean throughput (60.97 orders/h), and the highest matched-block composite score (0.9920). Relative to the mean of the canonical FTWB and VTWB benchmarks, MPBH reduced total late orders by 213.47 orders (10.66%; stratified cluster-aware 95% CI [212.40, 214.53] fewer orders). A crossed timing-by-composition experiment showed that both decisions matter, but the tested MPBH composition effect (approximately 153 fewer late orders) was about 8.4 times the MPBH timing effect (18.12 fewer late orders); therefore, the claim that timing generally dominates composition is not supported. MPBH won 770 of 864 operational cells under the declared service-level/throughput rule, although MaxPicker was also globally non-dominated. At a pool size of 5,000 orders, median MPBH decision latency was 61.34 ms on the reported test hardware. The findings support coordinated, state-aware release and composition rather than a timing-only explanation of temporal competitiveness.

**Keywords—replacement wording**

> Keywords: same-day delivery; online order batching; batch release; batch composition; discrete-event simulation; common random numbers; total late orders; time-based competition.

## 3. Introduction

### 3.1 Research question dan scope klaim

**Lokasi:** Section 1, paragraf 4, baris 43–47.

**Kutipan lama yang diganti**

> This research confronts this deficiency by conceptualising batch initiation timing as a dynamic, optimizable decision process. Our primary research question is: What constitutes an optimal timing strategy for initiating online order batching to minimise total late orders in SDD environments? Secondary inquiries investigate the influence of operational factors on the relative performance of distinct timing strategies.

**Replacement wording**

> This research treats online batch release as a dynamic, state-dependent decision and recognises that some adaptive policies jointly determine release timing and batch composition. Rather than claiming global optimality, the study asks which of the tested policies performs best within the stated simulation domain. Four research questions guide the analysis: **RQ1:** How do the eight tested policies differ in total late orders, service level, throughput, utilisation, and tardiness? **RQ2:** How stable are these differences across arrival rate, picker availability, cart capacity, routing, and basic composition rules? **RQ3:** When timing and composition are experimentally crossed, how much of MPBH's performance is attributable to each decision layer? **RQ4:** What service-efficiency and computational trade-offs arise from benchmark parameters and the urgency threshold?

### 3.2 Deskripsi portfolio heuristic

**Lokasi:** Section 1, paragraf 5, baris 48–56.

**Kutipan lama yang diganti**

> We propose and rigorously evaluate a novel portfolio of adaptive timing heuristics that ascertain the optimal batching moment based on real-time system state variables, incorporating calculated order urgency metrics and resource availability assessments. A central feature is a proactive “urgent order” prioritization mechanism that estimates expected completion times relative to due dates. This design overcomes a key limitation of traditional methods, which typically incorporate due-date information only after late orders becomes unavoidable. This adaptive, TBC-aligned methodology is tested by benchmarking six new strategies (MaxPicker, MaxCart, UrgentPicker, UrgentCart, Simplified Neighbourhood-based Heuristic (SNH), and Modified Priority Based Heuristic (MPBH)) against FTWB and VTWB across a wide spectrum of simulated conditions.

**Replacement wording**

> We evaluate six adaptive policies—MaxPicker, MaxCart, UrgentPicker, UrgentCart, Simplified Neighbourhood-based Heuristic (SNH), and Modified Priority-Based Heuristic (MPBH)—against canonical FTWB and VTWB benchmarks. MaxPicker, MaxCart, UrgentPicker, and UrgentCart primarily define release conditions and then invoke FCFS or EDT next-fit composition. SNH and MPBH additionally impose intrinsic composition logic; they must therefore be interpreted as integrated release-and-composition policies, not as timing-only treatments. Urgency-aware policies use a calibrated constant-time-per-order travel surrogate to predict whether a single-order tour would miss its due time. The study evaluates comparative effectiveness within a specified simulation domain and does not claim that any policy is globally optimal.

### 3.3 Kontribusi

**Lokasi:** Section 1, paragraf 6, baris 57–65.

**Kutipan lama yang diganti**

> This study offers three principal contributions. First, it advances batch initiation timing as a dynamic, state-dependent decision, extending TBC theory to warehouse micro-operations. Second, it provides a systematic comparative evaluation of novel adaptive timing heuristics across 6,912 simulated operational scenarios, furnishing robust empirical evidence of their efficacy. Third, it introduces a tailored simulation framework for modelling SDD dynamics. This framework treats time-sensitivity as a primary performance indicator.

**Replacement wording**

> This study makes three bounded contributions. First, it operationalises temporal responsiveness at the warehouse decision level by linking observable order-pool, due-time, and picker states to batch release, while explicitly separating timing from composition in a crossed experiment. Second, it provides a common-random-number comparison of eight policies across 6,912 operational scenarios and reports service, flow, utilisation, cart-fill, and computational trade-offs rather than relying on a single aggregate count. Third, it provides an auditable discrete-event simulation workflow with Welch warm-up deletion, horizon-censoring rules, deterministic tie-breaking, per-order records, resumable execution, and artifact checksums. The contribution is evidence about the tested policy class and simulated domain, not proof of global optimality or real-world causal effectiveness.

## 4. Literature review dan propositions

### 4.1 TBC harus menjadi mekanisme, bukan sekadar latar

**Lokasi:** Section 2.1, paragraf tunggal, khususnya kalimat penutup baris 81–85.

**Kutipan lama yang diganti**

> This necessitates optimising internal warehouse processes, like order picking and batching, within a TBC framework that intrinsically values responsiveness. The integration of warehouse timing decisions with last-mile delivery constraints is increasingly recognised as a hierarchical optimisation challenge in e-commerce fulfilment, where dispatch sequencing directly shapes downstream service outcomes.

**Replacement wording**

> In this study, TBC is operationalised through a specific mechanism: state-aware warehouse policies use current due-time, workload, and resource information to reduce avoidable waiting before and during batch release. The empirical implications are assessed through total late orders, the non-late-at-horizon rate, waiting and flow times, rather than through cost or market-share outcomes that the model does not represent. This micro-operational interpretation is deliberately bounded to completion of the picking tour at the I/O point; integration with packing and last-mile dispatch remains outside the simulated system.

### 4.2 Baris “This Study” pada Table 1

**Lokasi:** Table 1, baris 117.

**Kutipan lama yang diganti**

> This Study | Online | OOBSDDP | 6 novel heuristics | 480–7680 | 1–10

**Replacement wording**

> This Study | Online | OOBSDDP | 6 adaptive policies | approximately 240–7,680 arrivals per eight-hour measurement period | 1–10 distinct lines; 1–10 pieces per line (1–100 pieces/order)

Tambahkan pada note Table 1 bahwa jumlah aktual stochastic dan bahwa state
warm-up tidak masuk measurement cohort.

### 4.3 Table 2 — mapping research gap

**Lokasi:** Table 2, baris 124–173. Empat cell “Gap Addressed by This
study” perlu diganti karena wording lama memperlakukan semua treatment sebagai
timing murni.

**Kutipan lama yang diganti**

> This study explicitly optimizes timing as a decision variable rather than a fixed parameter.
>
> This study integrates real-time order urgency into the initiation decision.
>
> This study considers resource availability and system state for trigger decisions.
>
> This study develops adaptive heuristics responsive to multiple system variables.

**Replacement wording untuk empat cell terkait**

> This study evaluates state-aware release policies and separately crosses timing with composition; it does not claim to solve a globally optimal timing problem.
>
> This study incorporates due-time urgency in both release and, for integrated policies, order selection.
>
> This study constrains release by unreserved idle-picker slots and evaluates routing and cart-capacity treatments; congestion and integrated routing optimisation remain outside scope.
>
> This study compares transparent state-aware policies using a reproducible finite-horizon simulation and reports where timing and composition effects differ.

### 4.4 Pembaruan literature review

**Lokasi jangkar:** Section 2.2, paragraf baris 189–200, dan Section 2.3,
paragraf baris 202–215.

**Kutipan lama yang perlu diperluas**

> More recently, research has addressed the problem's inherently online nature, frequently leveraging machine learning. Cals et al. (2021) and Beeks et al. (2022) utilised Deep Reinforcement Learning (DRL) for dynamic batching decisions, while Shavaki and Jolai (2021) proposed integrated models for online batching and delivery planning. Although this is significant progress, their primary focus remains on assigning incoming orders to evolving batches or determining processing sequences. Their state representations and action spaces may not fully capture or prioritize the variables most pertinent to the batch initiation timing decision itself.

> The decision of when to initiate batch formation is fundamental in online and time-critical SDD operations. It encapsulates the core operational trade-off: rapid initiation risks inefficiently small batches, whereas delaying initiation to accumulate more orders increases the probability of orders becoming late.

**Replacement wording yang aman sebelum bibliografi final diverifikasi**

> Recent dynamic-batching research increasingly treats release, assignment, sequencing, and routing as interdependent online decisions rather than isolated stages. Learning-based and rolling-horizon methods broaden the available policy class, but their state and action definitions differ substantially from transparent dispatch rules that can be executed directly within a warehouse management system. This distinction matters for the present study: MaxPicker, MaxCart, UrgentPicker, and UrgentCart primarily govern release, whereas SNH and MPBH also determine composition. Accordingly, the research gap is not framed as an absence of all dynamic batching research, but as a need for transparent, reproducible evidence on state-aware release policies and on the separate contribution of release timing and composition under SDD due times.
>
> The release decision embodies a service-efficiency trade-off: immediate release may increase tour count and reduce cart fill, while delayed release may increase waiting and deadline risk. The present study therefore evaluates not only TLO but also the non-late-at-horizon rate, throughput, tardiness, waiting and flow times, picker utilisation, cart utilisation, trip count, and decision latency. **[Insert and verify the final 2023–2026 dynamic batching, real-time dispatching, integrated fulfilment, and recent EJIE references before submission.]**

Placeholder terakhir tidak boleh dibiarkan pada manuskrip yang diunggah. Jangan
menambahkan referensi dari daftar kandidat tanpa memverifikasi judul, status
publikasi, volume, halaman, dan DOI pada sumber penerbit.

### 4.5 Research gap dan empat proposition

**Lokasi:** Section 2.4, baris 216–245. Ganti proposition dan paragraf
penjelasnya sebagai satu blok agar definisi treatment tidak kembali confounded.

**Kutipan lama yang diganti**

> Proposition 1: Adaptive heuristics for batch initiation timing, which incorporate real-time system state information (e.g., order urgency, resource availability), will significantly outperform traditional static timing rules (FTWB, VTWB) in minimising total late orders within dynamic SDD environments.
>
> Proposition 2: Resource-aware adaptive heuristics will demonstrate greater robustness (i.e., more consistent performance) across variations in operational conditions, such as fluctuating order arrival rates and picker availability, compared to traditional timing approaches.
>
> Proposition 3: The relative performance ranking of different batch initiation timing strategies will vary systematically depending on the specific operational context, defined by factors such as picker availability, cart capacity constraints, and the routing policies employed.
>
> Proposition 4: In time-critical SDD environments, the strategic timing of batch initiation may have a comparable or potentially greater impact on overall system performance (particularly total late orders) than the specific method used for subsequent batch composition (e.g., First-Come-First-Served vs. Earliest Due Date).
>
> These propositions directly emanate from the limitations identified in the existing literature. Proposition 1 targets the primary gap concerning the paucity of adaptive timing mechanisms. Proposition 2 addresses the insufficient analysis of robustness in dynamic settings. Proposition 3 confronts the need for understanding context-dependent performance, moving beyond generalized findings. Proposition 4 critically re-evaluates the relative importance of timing versus subsequent batching decisions.

**Replacement wording**

> **Proposition 1 (policy effectiveness).** Relative to the canonical FTWB and VTWB benchmarks, state-aware adaptive release policies are expected to reduce total late orders. Because SNH and MPBH contain intrinsic composition logic, this is an omnibus policy proposition; the timing-specific contribution is evaluated separately.
>
> **Proposition 2 (robustness).** Adaptive policies that use urgency or resource state are expected to show lower deterioration or variability than static benchmarks as arrival rate and picker availability change.
>
> **Proposition 3 (context dependence).** The ranking of the tested policies is expected to vary across operational contexts defined by arrival rate, picker count, cart capacity, routing, and composition treatment.
>
> **Proposition 4 (timing versus composition).** Holding the tested operational context constant, changing from canonical FTWB timing to MPBH-immediate timing is expected to reduce total late orders by at least as much as changing from FCFS or EDT to MPBH composition.
>
> P1–P3 are evaluated in the full factorial experiment. P4 is evaluated only through the separate crossed timing-by-composition experiment; it is not inferred from incomparable main effects in the full factorial design. The propositions are retained as ex-ante directional expectations and are not rewritten to match the observed results.

## 5. Methodology

### 5.1 Table 3 — notasi

**Lokasi:** Table 3, baris 253–327. Ganti seluruh tabel; definisi lama
`N = total number of orders processed`, TLO completed-only, `SetupTime = 30 s`,
dan `Items(o)` tidak lagi memadai.

**Kutipan lama yang diganti (seluruh isi substantif Table 3)**

> t: current time; T: simulation horizon; N: total number of orders processed over T; C: cart capacity; S_t: system state; O_t: orders in the pool; B_t: active batches; P_t: idle pickers; d_i: deadline; TLO: orders delivered after d_i; c_i: completion time; Θ: throughput; U: picker utilisation; τ_p^active: picker active time; C: composite score; w: weight; F: FTWB interval; V: VTWB order threshold; λ: arrival rate; ProcessingTime(o): estimated picking plus travel time; SetupTime: fixed preparation time per batch; UrgentOrders(t): orders predicted late; β: urgency threshold; B_temp: MPBH temporary batch; Items(o): number of items; BasePickTime: average item-pick time; TravelTime(Items(o)): travel approximation; TotalBatchTime: total batch service time; TotalPickers: number of pickers.

**Replacement wording — Table 3a. Dynamic variables and outcomes**

| Symbol | Definition | Unit/type |
|---|---|---|
| `t` | Current event time | s |
| `S_t=(O_t,B_t,P_t,t)` | Simulation state | tuple |
| `O_t` | Generated orders not yet released to a batch | set |
| `B_t` | Pending, assigned, or completed batches/tours | set |
| `P_t` | Picker states, including idle/busy and idle-since time | set |
| `r_t` | Available release slots: idle pickers minus pending batches | picker slots |
| `a_i,d_i,s_i,c_i` | Arrival, due, picking-start, and completion time of order `i`; `s_i,c_i` may be null at the horizon | s |
| `L_i` | Number of distinct SKU lines in order `i` | integer, 1–10 |
| `q_ij` | Pieces requested for line `j` of order `i` | integer, 1–10 |
| `Q_i=Σ_j q_ij` | Total pieces in order `i` | integer, 1–100 |
| `N` | Number of measurement-cohort orders with `a_i ≥ W` and `a_i < H` | orders |
| `TLO` | Completed-late orders plus overdue outstanding orders at `H` | orders |
| `Θ` | Measurement-cohort completed orders divided by eight hours | orders/h |
| `U` | Mean picker busy-time overlap with the measurement window divided by available picker time | % |
| `C_score` | Matched-block composite score; higher is better | [0,1] |
| `B_temp` | Temporary capacity-feasible MPBH candidate batch | ordered set |

**Replacement wording — Table 3b. Fixed and experimental parameters**

| Symbol/parameter | Definition and value | Unit/type |
|---|---|---|
| `W` | Welch warm-up deletion, 5,460 | s |
| `T` | Measurement duration, 28,800 | s |
| `H=W+T` | Engine stop/censor time, 34,260 | s |
| `λ` | Arrival-rate levels `{0.5,1,2,4,8,16}` | orders/min |
| `m` | Number of pickers `{1,…,12}` | pickers |
| `C` | Cart capacity `{100,150,200}` | pieces/tour |
| `F` | Canonical FTWB interval, 720 | s |
| `V` | Canonical VTWB threshold, 12 | orders |
| `β` | Canonical urgency threshold, 2; sensitivity `{1,2,3,4}` | orders |
| `A_i` | Due allowance `DiscreteUniform{30,…,120}` | min |
| `p_pick` | Piece-picking time, 5 | s/piece |
| `t_setup` | Setup time charged once per executed tour, 180 | s/tour |
| `v_walk` | Walking speed, 0.5 | m/s |
| shelf pitch | Longitudinal shelf spacing, 1 | m |
| composition | FCFS or EDT next-fit for non-intrinsic policies | categorical |
| routing | S-shape or Largest Gap | categorical |
| `\hat t_travel(o)` | Cached linear-regression travel estimate for one order | s |
| `w=(0.6,0.3,0.1)` | Baseline composite weights for TLO, throughput, and utilisation | vector |

### 5.2 Section 3.1 — problem formulation dan pemisahan decision layers

**Lokasi:** Section 3.1, seluruh paragraf dan Equation (1), baris 330–369.

**Kutipan lama yang diganti**

> We address the Online Order Batching for Same-Day Delivery Problem (OOBSDDP). This involves dynamically grouping incoming customer orders, each with specific items and delivery deadlines, into batches for efficient picking within stringent SDD time constraints. The problem can be formalized as a mapping function from the current system state to a binary decision (initiate batching or wait). At any given time t, the system state S_t can be represented as S_t=(O_t,B_t,P_t,t). While traditional triggers (FTWB, VTWB) consider only single state elements, our adaptive heuristics incorporate multiple state variables. The primary objective, consistent with SDD imperatives, is minimising total late orders.

**Replacement wording**

> We study an online batch-release and composition problem for a picker-to-part warehouse. At each decision epoch, the observable state is `S_t=(O_t,B_t,P_t,t)`, where `O_t` is the waiting order pool, `B_t` contains pending and active tours, and `P_t` records picker availability and idle duration. A timing action `a_t^T∈{wait,open cycle}` determines whether a release cycle starts. Conditional on opening a cycle, a composition action `a_t^C` selects one or more ordered, capacity-feasible subsets, limited by `r_t`, the number of unreserved idle-picker slots. The cycle stops when the eligible pool is empty or `r_t=0`. FCFS and EDT use deterministic next-fit composition; SNH and MPBH define intrinsic composition actions.
>
> State transitions are stochastic through exponential interarrival times and order contents, and deterministic conditional on the sampled demand, selected policy, picker assignment, and routing calculation. Orders in an executed tour complete simultaneously when the picker returns to the I/O point. Thus, “completion” in this study denotes completion of warehouse picking, not customer delivery. The finite-horizon objective is to minimise expected `TLO`, with throughput, tardiness, waiting and flow times, picker utilisation, cart utilisation, and trip count reported as secondary outcomes. The study compares specified heuristic policies; it does not solve for an optimal policy over the full action space.

Tambahkan sesudah paragraf tersebut:

> The full factorial comparison estimates policy effects, whereas the crossed timing-by-composition experiment separately identifies the effects of the tested timing and composition layers. This separation is necessary because MPBH and SNH are integrated policies and cannot be interpreted as timing-only treatments in the main factorial experiment.

### 5.3 Section 3.2 — warehouse, order generation, service, routing, urgency

**Lokasi:** Section 3.2, baris 370–415. Ganti seluruh blok untuk menghilangkan
order-size ambigu, setup 30 s, dan uraian urgency yang belum terkalibrasi.

**Kutipan lama yang diganti seluruhnya**

> A discrete-event simulation models a manual picker-to-part distribution warehouse that is similar to the one seen in Ho et al. (2008). As shown in Figure 1, the warehouse has twelve parallel picking aisles and two cross aisles (one front cross aisle and one back cross aisle). It also has an I/O point at one of its corners. The I/O point is not only the place where pickers receive order-picking instructions, but also the place where pickers deposit the items they have picked from the warehouse. Key assumptions include: ABC storage (approximating 80/20 rule, Silva et al., 2022); homogeneous Poisson order arrivals (λ) (Boysen et al., 2019); order sizes of 1–10 items (discrete uniform); and SDD-reflective due times (30–120 minutes post-arrival, discrete uniform, Voccia et al., 2019). Manual pickers operate at 0.5 m/s walking speed with a 5 s item pick time (Burinskienė and Lerher, 2021), using S-shape or Largest Gap routing (Roodbergen and Koster, 2001). These parameters, while acknowledging complexities like non-Poisson arrivals, ensure controlled experimentation and comparability.
>
> Several urgency-aware heuristics in Section 4.3 and Section 4.4 rely on a shared urgency criterion to assess whether an order risks becoming late. An order `o∈O_t` at time `t` is deemed “urgent” if its estimated feasible completion time surpasses its due date: `UrgentOrders(t)={o∈O_t | t+ProcessingTime(o)+SetupTime>DueTime(o)}`, where `DueTime(o)` is the delivery deadline for order `o`. `ProcessingTime(o)` is estimated as `BasePickTime×|Items(o)|+TravelTime(Items(o))`, where `BasePickTime` is the average time to pick one item, set at 5 s.
>
> In our model, `SetupTime` is defined as the fixed, non-divisible time required for all preparatory and concluding tasks for a single picking tour (e.g., administrative tasks, equipment preparation, and time allowance), as established in foundational warehouse optimisation literature (Henn, 2012; Coruzzolo et al., 2023). For this simulation, this value was set to a constant 30 seconds, an empirically-derived estimate representing the average time for a picker to receive a mission, acquire a cart, and travel to the first “A” zone pick location.
>
> The inclusion of this per-batch cost (Yu, 2008) in a per-order urgency check is not an accounting error, but a critical and deliberate feature of the predictive model. The purpose of the heuristic is to estimate if an order is at risk of becoming late. To do this, it must model the `TotalBatchTime` of the most conservative, “worst-case” scenario, which is a single-order batch.
>
> As established by the core equations for batch completion time (Yu, 2008; Coruzzolo et al., 2023), the total service time for any batch, regardless of size, is `TotalBatchTime=ProcessingTime(o)+SetupTime`. Therefore, to accurately predict the completion time of a potential single-order batch, the model must include the fixed `SetupTime` cost that this tour would incur. Omitting `SetupTime` would be a methodological error, as it would falsely assume a zero-cost batch initiation, which the literature proves is a primary source of cascading delays (Gil-Borrás et al., 2020). This calculation does not “add” `SetupTime` to every order; it correctly models `TotalBatchTime` for the specific, potential batch being evaluated (a batch of size 1) to determine if that order is a time-critical risk.
>
> The `TravelTime(Items(o))` term in the `ProcessingTime(o)` formula is not derived from a full path calculation, which would be computationally prohibitive in real time. Instead, it is an O(1) complexity approximation using a regression-based formula derived from the number of items and their likely ABC zone distribution.

**Replacement wording**

> The discrete-event model represents a manual picker-to-part warehouse with 12 parallel aisles, 16 longitudinal shelf positions per aisle, front and rear cross aisles, one I/O point, and 384 SKU locations. Orders arrive according to a homogeneous Poisson process with exponential interarrival time `60/λ` seconds. Each order contains `L_i~DiscreteUniform{1,…,10}` distinct SKU lines sampled without replacement. Quantity per selected line is `q_ij~DiscreteUniform{1,…,10}`, so total workload is 1–100 pieces per order. Due allowance is sampled in whole minutes from `DiscreteUniform{30,…,120}` and added to arrival time.
>
> ABC storage assigns SKU 1–77 to class A (20.05% of locations; 80% demand mass), SKU 78–192 to class B (29.95%; 15%), and SKU 193–384 to class C (50%; 5%); sampling probabilities are uniform within class. Shelf pitch is 1 m and walking speed is 0.5 m/s, giving 2 s per longitudinal shelf step and 4 s for the modelled two-pitch aisle transition. Executed tour time is `180 + route_walking_time + 5×total_pieces` seconds. Setup is charged once per executed tour. S-shape and Largest Gap are calculated from the SKU-to-aisle/shelf mapping; orders in a tour complete when the picker returns to the I/O point.
>
> Urgency is evaluated for each waiting order using `urgent(o,t)=1[t+180+5Q_o+\hat t_travel(o)>d_o]`. The travel surrogate is a non-negative linear regression using distinct lines, total pieces, maximum aisle, and number of distinct aisles. Coefficients were frozen after 10,000 deterministic calibration samples. Held-out MAE/RMSE/R² were 9.848/13.800 s/0.9546 for S-shape and 7.531/9.679 s/0.9390 for Largest Gap. Predictions are cached because order content and locations do not change; evaluation is O(1) per order after feature construction. Surrogate error is a model limitation and the exact routing engine, rather than the surrogate, determines executed tour time.

### 5.4 Figure 1

**Lokasi:** placeholder baris 382 dan caption asli baris 1101.

**Kutipan lama yang diganti**

> Figure 1 Warehouse layout (Ho et al., 2008). Reproduced with permission of Elsevier.

**Replacement caption**

> **Figure 1. Simulated picker-to-part warehouse and SKU mapping.** The model contains 12 parallel aisles, 16 longitudinal shelf positions per aisle, front and rear cross aisles, and a corner I/O point. Shelf pitch is 1 m; SKU locations 1–77, 78–192, and 193–384 form the A, B, and C storage classes, respectively. Adapted from Ho et al. (2008); retain the publisher permission statement required by the licence.

Gambar perlu digambar ulang atau dianotasi agar I/O, 1 m pitch, 12 aisles,
ABC zones, dan mapping 384 SKU terlihat. Jangan menggunakan layout Ho et al.
seolah-olah identik tanpa menunjukkan adaptasi model.

### 5.5 Section 3.3 — experimental design, warm-up, CRN, reproducibility

**Lokasi:** Section 3.3, baris 416–436.

**Kutipan lama yang diganti seluruhnya**

> A full factorial experimental design evaluated strategies under diverse conditions. Factors included: Trigger Method (8 levels: FTWB, VTWB benchmarks, and 6 novel heuristics) (Gil-Borrás et al., 2020); Incoming Order Rate (λ) (6 levels: 0.5 to 16 orders/min); Number of Pickers (12 levels: 1 to 12) (Scholz et al., 2017); Batching Method (2 levels: First-Come-First-Served, FCFS; or Earliest Due Date, EDT) (Henn, 2015); Cart Capacity (C) (3 levels: 100, 150, 200 items) (Van Gils et al., 2018; Vanheusden et al., 2022); and Routing Policy (2 levels: S-shape or Largest Gap) (Roodbergen and Koster, 2001). This design yielded 6,912 unique scenarios (`8×6×12×2×3×2`), each replicated 30 times (207,360 total runs) for statistical robustness. This parametric, large-scale simulation design mirrors recent computational experiments in the dispatching literature that systematically evaluate multiple rules across varying load and variability conditions to identify context-dependent performance differences (Castro et al., 2024).
>
> The simulation was built in Python (SimPy), modelling an 8-hour day (28,800 s) with a warm-up period determined by Welch's method. The model manages order generation, pooling, batch triggering, FCFS/EDT batch formation (respecting capacity), picker assignment (longest idle time first) (Ardjmand et al., 2018), and routing. The trigger serves only to initiate a batching cycle. Once activated, batch formation continues using the selected batching rule until either the order pool is empty or no picker is available. The trigger condition is not re-applied within an active cycle. Rigorous three-phase validation was performed: (1) Conceptual Validation (domain experts); (2) Computational Verification (systematic code testing); and (3) Operational Validation (comparing outputs to known results, checking face validity, and sensitivity analyses).

**Replacement wording**

> The main experiment crossed eight policies, six arrival rates `{0.5,1,2,4,8,16}` orders/min, 12 picker counts `{1,…,12}`, two basic composition settings `{FCFS,EDT}`, three cart capacities `{100,150,200}` pieces, and two routing policies `{S-shape,Largest Gap}`. The resulting 6,912 scenarios were each run for 30 replications, giving 207,360 successful runs. For MPBH and SNH, the recorded FCFS/EDT factor does not replace their intrinsic ranking; this duplication is retained for balance and is addressed by the separate crossed ablation.
>
> A Welch pilot used 24-h runs, ten replications, all eight policies, 60-s observations, an 11-point centred moving average, a 5% tolerance, and ten consecutive stable points at `λ=0.5` and 12 pickers. The maximum stabilisation point was 5,460 s. The engine therefore runs to 34,260 s: orders arriving before 5,460 s build state but are excluded from measurement denominators, and the following 28,800 s form the measurement window. Busy time crossing the warm-up boundary contributes only its overlap. A pilot at `λ=4` and 12 pickers showed positive backlog drift; overloaded factorial cells are therefore interpreted as finite-horizon stress performance, not steady-state estimates.
>
> Common random numbers pair policies and non-arrival factors by arrival-rate level and replication. Run seeds are the first 64 bits of SHA-256 over the master seed, arrival key, and replication; run UUIDs are deterministic UUID5 values from the configuration and complete scenario. Picker dispatch is longest-idle-first with numeric picker ID as the tie-break. FCFS sorts by arrival and order ID; EDT sorts by due time, arrival, and order ID; both use next-fit. Pending batches reserve picker slots, preventing over-release. Per-order output records nullable start/completion time, horizon state, censor time, waiting/flow observations, late components, and tardiness lower bounds. The final artifact stores source/config hashes, seed, model version, row counts, and checksums and supports checkpoint-safe resume.
>
> CRN contrasts are first computed within complete scenario-by-replication blocks. Because one generated demand stream is shared by all non-arrival configurations having the same arrival-rate level and replication, uncertainty is calculated from demand-stream-cluster mean effects: 180 independent clusters in the main factorial and 60 in each auxiliary ablation or β analysis. Arrival-rate levels are fixed experimental strata; replication variance is estimated within each stratum, and equally weighted stratum means are combined using Welch–Satterthwaite degrees of freedom. Scenario-run pairs are not treated as independent stochastic replicates. Count-regression diagnostics are secondary: the Poisson model was severely overdispersed (Pearson dispersion 3,185.9), and the attempted negative-binomial model did not converge and is not used for inference. The throughput model uses HC3 covariance but remains heteroskedastic. Effect magnitude and uncertainty are reported regardless of p-value.

### 5.6 Tambahkan Section 3.4 reviewer-directed experiments sebelum metrics

**Lokasi jangkar:** setelah Section 3.3, sebelum Section 3.4 lama.

**Replacement wording baru**

> **3.4 Reviewer-directed experiments.** Four auxiliary experiments were conducted independently of the main factorial. First, a `2×3` crossed design combined timing `{FTWB, MPBH-immediate}` with composition `{FCFS, EDT, MPBH}` using CRN, allowing timing and composition effects to be estimated separately. Second, benchmark calibration evaluated `F∈{60,120,180,240,300,360,480,600,720}` and `V∈{4,6,8,10,12,16,20,24}`; the first 15 replications selected parameters and the remaining 15 provided held-out evaluation. Canonical `F=720` and `V=12` remained fixed in the main experiment and were not relabelled as tuned optima. Third, `β∈{1,2,3,4}` was evaluated for urgency-aware policies. Fourth, isolated decision-kernel latency was measured for pool sizes `{10,50,100,500,1000,5000}` with 30 repeats after subtracting timer overhead. These experiments support decomposition, robustness, and implementation claims; they do not alter the confirmatory main-factorial treatments post hoc.

Renumber Section 3.4 lama menjadi 3.5.

### 5.7 Section 3.4 lama / 3.5 baru — performance metrics

**Lokasi:** baris 437–533, termasuk Equations (2)–(8). Ganti seluruh blok.

**Kutipan lama yang diganti seluruhnya**

> Heuristic effectiveness was evaluated using three primary metrics. Let `N` denote the total number of orders processed over the simulation horizon `T`. Total Late Orders (TLO), the primary SDD indicator, counts orders delivered after their deadline `d_i`: `TLO=Σ_{i=1}^N 1[c_i>d_i]`, where `c_i` is the completion time of order `i` and `1[·]` is the indicator function. Throughput (`Θ`) measures the total number of orders successfully completed within `T`: `Θ=|i:c_i≤T|`. Picker Utilisation (`U`) represents the average fraction of active (non-idle) time across all pickers `p∈P`: `U=(1/|P|)Σ_{p∈P}(τ_p^active/T)`, where `τ_p^active` is the total active picking time of picker `p`.
>
> To enable cross-heuristic comparison, a Composite Score (`C`) was computed by normalising each metric prior to aggregation. Normalisation is necessary for two reasons. First, the three metrics operate on fundamentally different scales—TLO and `Θ` are unbounded integer counts whose magnitude depends on order volume, whereas `U` is already bounded to `[0,1]` as a ratio; combining them directly would allow larger-scaled metrics to disproportionately dominate the composite. Second, the metrics have opposing optimisation directions: TLO is to be minimised, while `Θ` and `U` are to be maximised. Normalisation resolves both issues by mapping each metric to a common `[0,1]` scale with a uniform “higher is better” orientation: `TLO_norm=1−(TLO−TLO_min)/(TLO_max−TLO_min)`, `Θ_norm=(Θ−Θ_min)/(Θ_max−Θ_min)`, and `U_norm=(U−U_min)/(U_max−U_min)`, where min and max are taken across all heuristics compared in the experiment.
>
> The composite score is then `C=0.6×TLO_norm+0.3×Θ_norm+0.1×U_norm`. The weight assignment reflects the primary strategic imperative of SDD operations: minimising late orders (`w=0.6`) constitutes the dominant objective, followed by service capacity (`w=0.3`) and resource efficiency (`w=0.1`). Sensitivity analysis on these weights was beyond this study's scope.

**Replacement wording**

> The measurement cohort contains orders arriving during the eight-hour post-warm-up window. At the fixed censor time `H`, the primary outcome is
>
> `TLO = Σ_i 1[c_i exists and c_i>d_i] + Σ_i 1[c_i is null and d_i<H]`.
>
> Thus, TLO includes both completed-late orders and overdue outstanding orders; outstanding orders that are not yet due are not counted late. The late-order ratio is `TLO/N`. Its complement, `1−TLO/N`, is reported by the software as “on-time rate” but is more precisely a **non-late-at-horizon rate**, because it may include outstanding orders whose due time has not yet passed. Throughput is the number of measurement-cohort orders completed by `H`, divided by eight hours. Picker utilisation is picker busy-time overlap with the measurement window divided by `m×28,800 s`.
>
> For completed orders, tardiness is `max(0,c_i−d_i)`, flow time is `c_i−a_i`, and waiting time is `s_i−a_i`. Exact final tardiness is unobserved for outstanding orders. We therefore report `max(0,H−d_i)` as a conservative horizon lower bound and use observed censored waiting/flow time rather than imputing completion. Cart utilisation is completed-tour pieces divided by capacity; trip count is the number of completed measurement-overlapping tours.
>
> The composite score is secondary to the unnormalised outcomes and Pareto analysis. Within each complete scenario-by-replication CRN block, TLO is reverse min–max normalised and throughput and picker utilisation are benefit-normalised across the fixed eight-policy set. A constant metric range is assigned 0.5. The baseline weights are `(0.6,0.3,0.1)`, and equal, throughput-priority, and utilisation-priority weights are reported as sensitivity analyses. The main text must not compare a block-normalised value with a globally normalised value.

Gunakan kembali bentuk Equations (5)–(8) hanya setelah subscript block `b` dan
aturan constant-range `0.5` ditambahkan eksplisit.

## 6. Section 4 — algoritma

### 6.1 Preamble bersama

**Lokasi:** paragraf pembuka Section 4, baris 534–538.

**Kutipan lama yang diganti seluruhnya**

> This section details the eight heuristics evaluated: two traditional benchmarks (Section 4.1) and six novel adaptive heuristics (Sections 4.2–4.4). The adaptive approaches are categorized by their decision logic (resource awareness, urgency awareness, advanced dynamic mechanisms) to address static trigger limitations.

**Replacement wording**

> This section defines two canonical static benchmarks and six adaptive policies. All policies are event driven. A policy may open a release cycle only when at least one unreserved idle-picker slot exists. A cycle releases at most `r_t` capacity-feasible tours and stops when the eligible order set is empty or no release slot remains. For deterministic reproducibility, every sort and picker assignment uses the tie-breaks stated in Section 3.3. Complete pseudocode and unit-tested edge cases are provided in the supplementary material.

### 6.2 Section 4.1 — FTWB dan VTWB

**Lokasi:** baris 539–562.

**Kutipan lama yang diganti seluruhnya**

> **Fixed Time Window Batching (FTWB):** Triggers at fixed, predetermined time intervals (`F=360 s`, based on Gil-Borrás et al., 2020), batching all orders accumulated in `|O_t|`. This method is simple but non-adaptive to real-time system dynamics. Decision rule: trigger if `(t mod F)=0 and |O_t|>0`; complexity O(1).
>
> **Variable Time Window Batching (VTWB):** Triggers when the order pool `O_t` reaches or exceeds a predefined threshold (`V=12` orders, based on Gil-Borrás et al., 2020). This reacts to order volume but neglects order urgency and resource status. Decision rule: trigger if `|O_t|≥V`; complexity O(1).
>
> The parameters (`F=360 s` and `V=12`) are adopted from Gil-Borrás et al. (2020) to ensure that the benchmarks represent standard, literature-derived baseline policies. These parameters were not re-tuned for our specific simulation environment. Consequently, the benchmark performance may be conservative, which could amplify the relative improvement reported later in Section 5.1, specifically, the 27.04% average reduction in total late orders achieved by MPBH compared with FTWB and VTWB.

**Replacement wording**

> **FTWB.** At each `F=720 s` epoch, if the pool is non-empty and `r_t>0`, FTWB opens one release cycle. The waiting pool is ordered by the configured FCFS or EDT rule and partitioned by next-fit; at most `r_t` batches are released. The predicate is O(1), excluding composition.
>
> **VTWB.** If at least `V=12` orders wait and `r_t>0`, VTWB fixes the first 12 remaining orders by `(arrival time, order ID)` as the eligible subset. The configured FCFS or EDT next-fit rule composes that subset, and at most `r_t` batches are released. Orders beyond the fixed first-`V` subset cannot enter the current cycle. The threshold predicate is O(1), excluding composition.
>
> `F=720` and `V=12` are paper-canonical settings, not empirically optimal settings. A separate tuning/held-out sweep selected `F=60` for minimum TLO and composite, `V=4` for minimum TLO, and `V=6` for maximum composite. Canonical and tuned evidence are therefore reported separately.

### 6.3 Section 4.2 — MaxPicker dan MaxCart

**Lokasi:** baris 563–590.

**Kutipan lama yang diganti seluruhnya**

> **MaxPicker:** Prioritises picker utilisation by initiating a batch immediately when a picker becomes available (`P_t>0`) and orders exist (`O_t>0`), minimising idle time. Decision rule: trigger if `|P_t|>0 and |O_t|>0`; complexity O(1).
>
> **MaxCart:** Focuses on cart utilisation, triggering only when the total item count in `O_t` meets or exceeds cart capacity (`C`) and a picker is available (`P_t>0`). Decision rule: trigger if `Σ_{o∈O_t}|Items(o)|≥C and |P_t|>0`, where `|Items(o)|` is the number of items in order `o`; complexity O(n), where `n=|O_t|`.

**Replacement wording**

> **MaxPicker.** If the pool is non-empty and `r_t>0`, open a release cycle over the waiting pool. Compose FCFS or EDT next-fit batches and stop when the pool is empty or `r_t=0`. The release predicate is O(1).
>
> **MaxCart.** Open a cycle only when both `Σ_{o∈O_t}Q_o≥C` and `r_t>0`. Compose by the configured FCFS or EDT next-fit rule. Summing waiting pieces is O(n) without an incrementally maintained total.

### 6.4 Section 4.3 — UrgentPicker dan UrgentCart

**Lokasi:** baris 591–624.

**Kutipan lama yang diganti seluruhnya**

> **UrgentPicker:** Blends urgency with picker availability. It triggers if the urgent order count `|UrgentOrders(t)|` exceeds a threshold `β=2`, or if all pickers are idle (`|P_t|=TotalPickers`), provided `|O_t|>0`, where `TotalPickers` is the number of pickers (1 to 12) defined in the experimental design. The `β=2` threshold balances proactive response against creating excessively small batches. Decision rule: trigger if `(|UrgentOrders(t)|≥β or |P_t|=TotalPickers) and |O_t|>0`; complexity O(n).
>
> **UrgentCart:** Combines urgency with cart capacity. It triggers if `|UrgentOrders(t)|≥β` (`β=2`) or if total item count `Σ_{o∈O_t}|Items(o)|≥C`, provided `|P_t|>0`. Decision rule: trigger if `(|UrgentOrders(t)|≥β or Σ_{o∈O_t}|Items(o)|≥C) and |P_t|>0`; complexity O(n).
>
> The complexity for this urgency calculation for all `n` orders in the pool is O(n), as the `ProcessingTime(o)` estimation (including the `TravelTime(Items(o))` approximation) is an O(1) complexity calculation for each order. This O(n) complexity operation is considered acceptable for real-time operation and does not conflict with the O(n log n) complexity of MPBH (Section 4.4), which is dominated by its sorting step.

**Replacement wording**

> **UrgentPicker.** If `r_t>0` and the pool is non-empty, open a cycle when `urgent_count(t)≥β` **or** all pickers are idle. Compose by the configured FCFS or EDT next-fit rule. `β=2` is the canonical baseline, not a universal optimum.
>
> **UrgentCart.** If `r_t>0` and the pool is non-empty, open a cycle when `urgent_count(t)≥β` **or** total waiting pieces are at least `C`. Compose by the configured FCFS or EDT next-fit rule. The urgency branch prevents an order at predicted risk from being forced to wait solely for a full cart; the capacity branch releases a sufficiently loaded pool. Under the canonical main factorial, this rule produced the same matched outcomes as MaxCart, indicating that its urgency branch did not change the release outcome in those tested states. This empirical equivalence is not assumed outside the tested domain.
>
> Evaluating cached urgency for all waiting orders is O(n). The decision benchmark nevertheless classified UrgentCart empirically as O(n log n) over the tested implementation and range; empirical fit and algorithmic upper-bound reasoning must be reported separately.

### 6.5 Section 4.4 — SNH dan MPBH

**Lokasi:** baris 625–693.

**Kutipan lama yang diganti seluruhnya**

> This category includes heuristics that apply structured, multi-step decision logic to balance urgency and capacity considerations during batch formation. The dynamic, state-dependent selection logic employed in these advanced heuristics shares conceptual roots with adaptive search frameworks that update operator behaviour based on real-time performance signals in time-constrained logistics contexts (Wang and Chen, 2024).
>
> **Simplified Neighbourhood-based Heuristic (SNH):** a rule-based heuristic inspired by neighbourhood search concepts (Liu, 2016). Rather than exploring neighbourhoods iteratively, it evaluates three predefined priority orderings of the current order pool (`O_t`): an urgency-first list (`N_urgency`) sorted by earliest due date; a capacity-focused list (`N_cart`) ordered to maximise cart utilisation; and a hybrid list (`N_hybrid`) with urgency priority followed by item count. When at least one picker is available (`|P_t|>0`), SNH forms a batch using the first feasible option in the following sequence: (1) if the subset of urgent orders meets the urgency threshold, dispatch those urgent orders; (2) if all orders in `N_urgency` fit within cart capacity, dispatch them together; (3) otherwise scan `N_cart` and select the largest subset that fits; and (4) if the above fail, use `N_hybrid` to select the best capacity-feasible subset. Thus, SNH gives priority to urgency resolution, then to efficient cart loading, using a structured fallback logic rather than iterative search. Computational complexity: O(n log n), dominated by sorting.
>
> **Modified Priority-Based Heuristic (MPBH):** builds a batch incrementally while enforcing urgency and capacity constraints. When `|P_t|>0`: sort orders in `O_t` by earliest due date; initialise an empty temporary batch `B_temp`; traverse the sorted list and tentatively add each order to `B_temp`; after each addition, check whether the number of predicted total late orders in `B_temp` exceeds threshold `β`, or total item count exceeds cart capacity `C`; if violated, remove from `B_temp` the order with the latest due date, then recheck constraints; continue until all orders are evaluated; and dispatch `B_temp` if non-empty. The heuristic therefore prioritises urgent orders, but dynamically prunes lower-priority ones to maintain feasibility, preventing both overloading and excessive total late orders risk. Computational complexity: practically O(n log n), driven by the initial sorting step. Constraint checks are linear, and restoration is infrequent.

**Replacement wording**

> **SNH.** For each available release slot: (1) if at least `β` orders are urgent, select urgent orders in `(due,arrival,ID)` order until capacity; (2) otherwise, if all waiting orders fit, select all in that order; (3) otherwise, sort by descending pieces with `(due,arrival,ID)` ties and fill capacity; and (4) apply a deterministic hybrid fallback if the previous rule would return an empty batch. Every released batch is non-empty and capacity feasible, and selected orders are removed atomically from the pool. SNH is a structured rule set inspired by neighbourhood priorities; it does not perform iterative neighbourhood search or claim local optimality.
>
> **MPBH.** For each available release slot, scan waiting orders in `(due,arrival,ID)` order. Tentatively append each order to `B_temp`. While total pieces exceed `C` or the number of members predicted late at the common candidate completion time exceeds `β`, remove the member with the latest `(due,arrival,ID)`. Release the resulting non-empty batch; if the candidate becomes empty, release the earliest individually feasible order to prevent deadlock. MPBH's intrinsic ordering replaces the configured FCFS/EDT composition.
>
> Sorting gives an O(n log n) algorithmic component for both policies. In the isolated benchmark over `n≤5,000`, the observed latency curves were best described by O(n) fits for the implemented SNH and MPBH kernels. At `n=5,000`, median adjusted decision latency was 14.07 ms for SNH and 61.34 ms for MPBH.

## 7. Results and analysis

### 7.1 Pembuka Section 5

**Lokasi:** baris 694–697.

**Kutipan lama yang diganti**

> This section presents findings from 207,360 simulation runs. We provide a comparative heuristic overview, analyze operational factor impacts and robustness, explore interaction effects, and validate the research propositions.

**Replacement wording**

> This section reports all 207,360 successful main-factorial runs, followed by the crossed ablation, benchmark calibration, β sensitivity, and decision-kernel benchmark. Descriptive summaries are distinguished from CRN-paired estimates. Results from nonconverged or severely misspecified count models are disclosed as diagnostics and are not used to support propositions.

### 7.2 Section 5.1 paragraf komparatif dan Table 4

**Lokasi:** baris 698–722.

**Kutipan lama yang diganti seluruhnya**

> Aggregate statistics across 6,912 scenarios (Table 4) reveal substantial heuristic heterogeneity across all three performance dimensions. MPBH achieved the lowest mean of TLO (829.5 orders), while UrgentCart had the highest (1716.2)—nearly double that of MPBH. Throughput was highest among resource-focused heuristics, with MaxPicker and MaxCart averaging approximately 209.0 and 208.2 orders/hour respectively, whereas SNH (136.0) and UrgentCart (122.2) were substantially lower. Picker utilisation was highest for SNH, MPBH, and MaxPicker (~84%), contrasting with notably lower levels for MaxCart (49.4%) and FTWB (53.0%), suggesting that these heuristics trigger batching before sufficient orders accumulate, leaving pickers intermittently idle.

**Replacement wording**

> Table 4 summarises 25,920 runs per policy after the 5,460-s warm-up. MPBH achieved the lowest mean TLO (1,788.83), the highest model-defined non-late-at-horizon rate (53.99%), the highest mean throughput (60.97 orders/h), and the lowest completed-order mean tardiness (1,393.04 s). MaxPicker recorded the highest mean picker utilisation (91.41%), narrowly above MPBH and SNH. UrgentCart was not the worst policy: it was exactly equal to MaxCart on every reported main-factorial matched outcome. MPBH's completed-only tardiness and all-order horizon lower bound differ materially because many outstanding orders are right-censored; the two estimands must not be interpreted as contradictory.

**Kutipan lama Table 4 yang diganti seluruhnya**

| Trigger method | TLO mean | TLO SD | Throughput/h mean | Throughput/h SD | Picker utilisation mean | Picker utilisation SD | Composite mean | Composite SD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FTWB | 1,036.6 | 1,967.2 | 203.6 | 199.5 | 53.0 | 35.1 | 0.725 | 0.135 |
| VTWB | 1,237.2 | 2,112.1 | 180.7 | 163.6 | 56.5 | 37.2 | 0.682 | 0.179 |
| MaxPicker | 1,001.8 | 1,944.3 | 209.0 | 203.5 | 84.0 | 23.0 | 0.826 | 0.140 |
| MaxCart | 987.7 | 1,915.6 | 208.2 | 205.8 | 49.4 | 37.1 | 0.619 | 0.226 |
| UrgentPicker | 1,040.9 | 1,963.3 | 202.3 | 196.8 | 54.8 | 35.5 | 0.725 | 0.143 |
| UrgentCart | 1,716.2 | 2,297.5 | 122.2 | 93.4 | 70.6 | 35.1 | 0.381 | 0.200 |
| SNH | 1,401.0 | 2,326.1 | 136.0 | 120.0 | 84.3 | 23.2 | 0.666 | 0.329 |
| MPBH | 829.5 | 1,698.2 | 187.2 | 186.2 | 84.2 | 23.2 | 0.864 | 0.093 |

> **Original note.** Best performance in each metric is highlighted in bold. SD = standard deviation.

**Replacement Table 4 — corrected full-factorial summary**

| Policy | Mean TLO (SD) | Late ratio | Non-late at horizon % | Throughput/h | Picker util. % | Completed tardiness, s | All-order tardiness lower bound, s | Composite mean (SD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FTWB | 2,023.145 (2,279.504) | 0.6018 | 39.823 | 30.498 | 66.119 | 6,065.866 | 6,211.023 | 0.1590 (0.2794) |
| VTWB | 1,981.448 (2,306.626) | 0.5524 | 44.765 | 41.605 | 84.707 | 4,704.337 | 5,517.286 | 0.3041 (0.2634) |
| MaxPicker | 1,977.703 (2,309.668) | 0.5424 | 45.761 | 42.789 | **91.407** | 5,963.244 | 5,465.659 | 0.4864 (0.3729) |
| MaxCart | 1,978.413 (2,309.154) | 0.5444 | 45.562 | 42.520 | 85.807 | 5,975.202 | 5,469.194 | 0.4084 (0.2882) |
| UrgentPicker | 1,998.911 (2,295.719) | 0.5699 | 43.006 | 40.927 | 84.308 | 6,113.799 | 5,566.531 | 0.2600 (0.2191) |
| UrgentCart | 1,978.413 (2,309.154) | 0.5444 | 45.562 | 42.520 | 85.807 | 5,975.202 | 5,469.194 | 0.4084 (0.2882) |
| SNH | 1,992.058 (2,301.918) | 0.5579 | 44.208 | 48.236 | 91.385 | 7,068.097 | 5,282.469 | 0.4999 (0.3431) |
| MPBH | **1,788.830 (2,193.369)** | **0.4601** | **53.990** | **60.969** | 91.393 | **1,393.042** | **4,877.198** | **0.9920 (0.0425)** |

> **Table 4 note.** Each policy contains 25,920 runs. TLO includes completed-late and overdue outstanding orders. Completed tardiness averages completed measurement-cohort orders; the all-order value is a horizon lower bound for right-censored outstanding orders. Composite scores use matched scenario-by-replication normalisation over the fixed eight-policy set and baseline weights `(0.6,0.3,0.1)`.

Tambahkan tabel supplement agar flow/wait dan efisiensi tour yang diminta
reviewer tidak hanya tersedia di raw data.

**Supplementary Table S1 — flow and tour-efficiency outcomes**

| Policy | Mean flow time, s | Mean waiting time, s | Mean cart utilisation, % | Mean completed trips |
|---|---:|---:|---:|---:|
| FTWB | 8,262.198 | 7,484.428 | 60.350 | 65.920 |
| VTWB | 7,009.527 | 6,228.793 | 61.047 | 86.757 |
| MaxPicker | 8,039.816 | 7,320.957 | 52.506 | 151.177 |
| MaxCart | 8,228.670 | 7,391.306 | 61.995 | 103.454 |
| UrgentPicker | 8,555.148 | 7,704.622 | 66.939 | 90.827 |
| UrgentCart | 8,228.670 | 7,391.306 | 61.995 | 103.454 |
| SNH | 9,817.755 | 8,850.562 | 76.294 | 166.138 |
| MPBH | **4,150.616** | **3,379.152** | 55.682 | 217.112 |

> **Table S1 note.** Means are run-level means over the measurement cohort. The supplement should additionally report the available p95 flow and waiting times and distinguish censored observations as defined in Section 3.5.

### 7.3 Composite paragraph

**Lokasi:** baris 724–729.

**Kutipan lama yang diganti seluruhnya**

> When evaluated through the composite score `C`, which prioritises on-time delivery, MPBH ranked first (0.924), followed by MaxPicker (0.883), MaxCart (0.790), FTWB (0.752), UrgentPicker (0.749), VTWB (0.547), SNH (0.361), and UrgentCart (0.061). MPBH's top ranking is primarily driven by its superior TLO performance, which carries the dominant weight (`w=0.6`) in the composite formula, while also maintaining competitive utilisation. UrgentCart ranked last despite moderate utilisation, as it scored poorly on both TLO and throughput—the two highest-weighted metrics.

**Replacement wording**

> Under the declared matched-block normalisation and `(0.6,0.3,0.1)` weights, MPBH ranked first (0.9920), followed by SNH (0.4999), MaxPicker (0.4864), MaxCart and UrgentCart (tie, 0.4084), VTWB (0.3041), UrgentPicker (0.2600), and FTWB (0.1590). MPBH remained first under equal, throughput-priority, and utilisation-priority weights. Nevertheless, the composite is secondary: global Pareto analysis using generated-order-weighted late rate, mean throughput, and mean picker utilisation identified both MPBH and MaxPicker as non-dominated. This weighted late-rate estimand must be distinguished from the equally weighted mean run-level late ratio in Table 4.

### 7.4 Figures 2–5 dan narasinya

**Lokasi narasi:** baris 730–734. **Lokasi caption:** baris 1674–1685.

**Kutipan lama yang diganti seluruhnya**

> Boxplots (Figures 2–5) visualise these distributions. Figure 2 confirms MPBH's superior total late orders performance (lower median, tighter interquartile range (IQR)) compared to SNH and UrgentCart. Figures 3 and 4 highlight inherent trade-offs in throughput and utilisation, while Figure 5 (composite score) further underscores MPBH's strong overall performance.

**Replacement wording**

> Figures 2–5 are regenerated exclusively from the final post-warm-up dataset. They show that MPBH leads the aggregate service and throughput summaries, whereas MaxPicker is marginally highest in picker utilisation and remains Pareto non-dominated. MaxCart and UrgentCart overlap exactly in the main factorial. Distribution widths are strongly driven by heterogeneous load cells; therefore, pooled boxplots are descriptive and are interpreted together with paired contrasts and context-specific plots.

**Caption pengganti**

> **Figure 2. Distribution of censoring-aware total late orders by policy across 25,920 final runs per policy.**
>
> **Figure 3. Distribution of post-warm-up throughput and non-late-at-horizon rate by policy.**
>
> **Figure 4. Picker utilisation, cart utilisation, and completed trip count by policy.** This figure displays the service-efficiency trade-off and the exact overlap of MaxCart and UrgentCart in the main factorial.
>
> **Figure 5. Multi-objective robustness of the eight policies.** Panel (a) shows the Pareto frontier for generated-order-weighted late rate, mean throughput, and mean picker utilisation; panel (b) shows ranks under baseline, equal, throughput-priority, and utilisation-priority composite weights.

Jangan mempertahankan gambar lama meskipun caption mirip; data dan normalisasi
lama tidak valid.

### 7.5 Ganti ANOVA/Tukey lama dengan Table 5 paired contrasts

**Lokasi:** baris 735–746 dan Table 5 lama baris 767–783.

**Kutipan lama yang diganti seluruhnya**

> Analysis of Variance (ANOVA) confirmed the trigger method had a statistically significant effect on all four metrics (`p<0.001`), including total late orders (`F(7,207352)=505.58`, `p<0.001`, `ηp²=0.0168`) and picker utilisation (`F(7,207352)=6092.55`, `p<0.001`, `ηp²=0.1706`). Subsequent Tukey's Honestly Significant Difference (HSD) tests confirmed MPBH significantly outperformed all other methods in minimising total late orders (`p<0.001`). While traditional (FTWB, VTWB) and simpler adaptive methods (MaxCart, MaxPicker, UrgentPicker) formed a middle tier, UrgentCart was significantly worse (`p<0.001`). Crucially, MPBH achieved an average total late orders reduction of 27.04% compared to the benchmarks (FTWB, VTWB), strongly supporting Proposition 1.
>
> **Table 5. ANOVA Summary for Interaction Model (Dependent Variable: Total Late Orders).** C(trigger_method): SS `1.47×10¹⁰`, df 7, F `1.94×10⁴`, `p<0.001`, `ηp²=0.396`; C(incoming_rate): SS `6.83×10¹¹`, df 5, F `1.26×10⁶`, `p<0.001`, `ηp²=0.968`; C(num_pickers): SS `4.46×10¹⁰`, df 11, F `3.75×10⁴`, `p<0.001`, `ηp²=0.666`; trigger×rate: SS `2.19×10¹⁰`, df 35, F `5.79×10³`, `p<0.001`, `ηp²=0.495`; trigger×pickers: SS `3.37×10⁹`, df 77, F `4.04×10²`, `p<0.001`, `ηp²=0.131`; rate×pickers: SS `6.26×10¹⁰`, df 55, F `1.05×10⁴`, `p<0.001`, `ηp²=0.737`; trigger×rate×pickers: SS `2.26×10¹⁰`, df 385, F `5.42×10²`, `p<0.001`, `ηp²=0.502`; residual: SS `2.24×10¹⁰`, df 206,784.

**Replacement wording**

> Primary comparisons used matched scenario-by-replication CRN differences between each adaptive policy and the mean of canonical FTWB and VTWB. Uncertainty was calculated over 180 independent arrival-rate-by-replication demand-stream clusters, stratified by the six fixed arrival-rate levels. MPBH reduced mean TLO by 213.47 orders (10.66%; stratified cluster-aware 95% CI [212.40, 214.53] fewer). The remaining adaptive policies reduced pooled benchmark TLO by only 0.17%–1.23%. Practical importance depends on effect magnitude and a domain-approved MPID, which was not available. These results partially, rather than universally, support P1.

**Replacement Table 5 — primary paired CRN contrasts**

| Adaptive policy minus mean(FTWB, VTWB) | Scenario pairs | Independent demand-stream clusters | Mean ΔTLO | Cluster-aware 95% CI | Relative reduction |
|---|---:|---:|---:|---:|---:|
| MaxPicker | 25,920 | 180 | −24.594 | [−25.102, −24.086] | 1.23% |
| MaxCart | 25,920 | 180 | −23.883 | [−24.376, −23.391] | 1.19% |
| UrgentPicker | 25,920 | 180 | −3.385 | [−3.664, −3.106] | 0.17% |
| UrgentCart | 25,920 | 180 | −23.883 | [−24.376, −23.391] | 1.19% |
| SNH | 25,920 | 180 | −10.238 | [−10.585, −9.892] | 0.51% |
| MPBH | 25,920 | 180 | **−213.467** | **[−214.533, −212.400]** | **10.66%** |

> **Table 5 note.** Negative differences favour the adaptive policy. Effects are calculated in complete scenario-by-replication blocks; confidence intervals use independent demand-stream cluster means with replication variance estimated inside each fixed arrival-rate stratum and Welch–Satterthwaite degrees of freedom. Report multiplicity handling in the supplement; do not report floating-point underflow as `p=0`.

### 7.6 Section 5.2 dan Figures 6–13

**Lokasi:** baris 747–766; captions baris 1688–1708.

**Kutipan lama yang diganti seluruhnya**

> Main effects plots (Figures 6–8) show that while total late orders predictably increased with higher incoming rates (`λ`, Figure 6) and decreased with more pickers (Figure 7), effect magnitudes varied. MPBH exhibited greater resilience to high order volumes than SNH or UrgentCart. Picker availability showed diminishing marginal returns, while cart capacity (Figure 8) had a less pronounced main effect on total late orders.
>
> Picker utilisation versus total late orders (Figure 9) revealed moderate positive correlations for FTWB, MaxCart, and VTWB (suggesting system overload), while weaker correlations for MPBH and MaxPicker suggest a better balance of resource activity and deadline adherence.
>
> Robustness was assessed using standard deviation (SD) and coefficient of variation (CV) (Figures 10–13). Interpretation requires nuance: absolute variability (SD) increased with system stress (Figures 10, 12), but relative variability (CV) sometimes stabilised (Figure 11), indicating predictability even as mean performance degraded (i.e., consistently poor performance yields low CV). Although MPBH showed lower absolute variability (SD) under high load, no single heuristic was robust across all conditions and metrics. This finding offers only partial support for Proposition 2. UrgentCart's poor performance and high variability likely stem from conflicting trigger logic.

**Replacement wording**

> TLO rises sharply with arrival rate and falls as picker availability increases, but overloaded cells retain large backlogs within the fixed horizon. These curves are finite-horizon stress responses, not steady-state response surfaces. Aggregate MPBH TLO has the lowest absolute SD (2,193.37), but no policy is uniformly best on every objective or every operational cell. Across the 864 cells obtained by holding all non-policy factors fixed, MPBH was selected in 770 cells (89.12%) by the declared maximum-service-level, then maximum-throughput rule, MaxPicker in 59, SNH in 31, and MaxCart in 4. This supports context dependence with an important qualification: MPBH is dominant in most, though not all, tested cells. MaxCart and UrgentCart must be plotted as overlapping series rather than interpreted as different robustness profiles.

**Caption pengganti**

> **Figure 6. Mean censoring-aware TLO versus arrival rate by policy, with 95% replication uncertainty.**
>
> **Figure 7. Mean censoring-aware TLO versus picker count by policy, with 95% replication uncertainty.**
>
> **Figure 8. Mean censoring-aware TLO versus cart capacity by policy.**
>
> **Figure 9. Non-late-at-horizon rate versus throughput by policy, highlighting the global Pareto frontier.**
>
> **Figure 10. Standard deviation of TLO versus arrival rate by policy.**
>
> **Figure 11. Coefficient of variation of TLO versus arrival rate by policy.** Interpret CV jointly with the mean because consistently poor performance may have a low CV.
>
> **Figure 12. Standard deviation of TLO versus picker count by policy.**
>
> **Figure 13. Coefficient of variation of TLO versus picker count by policy.**

Figure 9 lama berupa korelasi pooled sebaiknya tidak dipertahankan karena
mencampur load strata dan mudah menimbulkan korelasi semu. Gunakan Pareto
service-throughput yang sudah memiliki artefak final.

### 7.7 Section 5.3, Figure 14, dan UrgentCart

**Lokasi:** baris 767–804 dan caption Figure 14 baris 1712.

**Kutipan lama yang diganti seluruhnya**

> A multi-factor ANOVA (Table 5) identified significant (`p<0.001`) two-way and three-way interactions for total late orders, notably Trigger Method × Incoming Rate × Pickers. These interactions confirm that heuristic effectiveness is context-dependent. As visualised in Figure 14, performance differences are minimal at low arrival rates but diverge significantly as rates increase, especially with fewer pickers. MPBH maintains lower total late orders under moderate to high load, whereas SNH and UrgentCart struggle, particularly at the highest rate (16.0 orders/min).
>
> The poor performance of UrgentCart across most scenarios (Figure 14) warrants specific analysis, as it highlights a critical flaw in heuristic design. Its failure stems from its conflicting “OR” logic. The first trigger (if `|UrgentOrders(t)|≥β`) is highly sensitive, initiating many small, inefficient batches that inflate total picker travel time. Conversely, the second trigger (if `Σ_{o∈O_t}|Items(o)|≥C`) holds urgent orders hostage, forcing them to wait for a full cart, which directly contravenes the goal of time-sensitivity. This “worst-of-both-worlds” logic demonstrates that simply combining adaptive triggers without a balancing mechanism—as MPBH does—can degrade performance below even simple benchmarks.

**Replacement wording**

> Context dependence is assessed primarily through matched operational cells and the distribution of cell winners, rather than the legacy ANOVA table. MPBH wins most cells but not all, and MaxPicker and SNH remain preferable in a minority of cells under the declared service-level/throughput rule. Figure 14 should display final cell means and explicitly mark overloaded regions as finite-horizon stress cases. Secondary regression diagnostics do not justify retaining the accepted-paper sums of squares or partial eta-squared values.
>
> UrgentCart requires a different interpretation from the accepted paper. Its main-factorial outcomes are exactly identical to MaxCart for TLO, throughput, picker utilisation, and trip count in every matched block. Consequently, the “worst-of-both-worlds” explanation is contradicted by the corrected model and must be deleted. The result indicates that, at canonical `β=2` and under these sampled states, the urgency branch did not alter releases relative to the capacity branch. The β sweep likewise found no supported difference for `β=1` versus `β=2` and exact equality for `β=3` and `β=4` versus `β=2` in that auxiliary design. This is an empirical inactivity finding, not proof that the two policies are logically equivalent in all environments.

**Replacement Figure 14 caption**

> **Figure 14. Final interaction of policy and picker availability across arrival-rate levels.** Points show replication means from the corrected 207,360-run dataset; panels at sustained backlog are interpreted as finite-horizon stress conditions. MaxCart and UrgentCart overlap in the main factorial.

### 7.8 Table 6 dan paragraf context dependence

**Lokasi:** baris 800–812.

**Kutipan lama yang diganti seluruhnya**

> Table 6 confirms this context-dependency, showing MPBH as the superior heuristic in representative extreme scenarios (both high/low rates), strongly supporting Proposition 3. While interactions with secondary factors (cart capacity, routing, batching method) were sometimes significant, their explained variance in total late orders was substantially smaller than that of the primary factors (trigger method, incoming rate, picker availability).
>
> **Table 6. Best Heuristic (Lowest Avg. total late orders) in Representative Scenarios.** Low Rate (0.5 orders/min) / Low Pickers (1): MPBH, 0.00; Low Rate (0.5 orders/min) / High Pickers (12): MPBH, 0.00; High Rate (16 orders/min) / Low Pickers (1): MPBH, 6,233.22; High Rate (16 orders/min) / High Pickers (12): MPBH, 558.52. Note: This table summarises the optimal heuristic selection based on operational context, demonstrating the context-dependent nature of heuristic performance.

**Replacement wording**

> To avoid confounding the representative contexts by averaging over secondary treatments, Table 6 fixes FCFS, cart capacity 100 pieces, and S-shape routing. MPBH is best in three contexts, while the low-rate/high-picker context contains a four-way zero-TLO tie. The corrected high-rate/high-picker MPBH mean is 5,917.67, not 558.52. These data support P3 with qualification: context changes the winner in some cells, but MPBH dominates most of the full factorial.

**Replacement Table 6**

| Operational context | Best policy or tie | Mean TLO | Fixed secondary factors |
|---|---|---:|---|
| 0.5 orders/min; 1 picker | MPBH | 151.47 | FCFS; C=100; S-shape |
| 0.5 orders/min; 12 pickers | FTWB; MPBH; MaxPicker; SNH | 0.00 | FCFS; C=100; S-shape |
| 16 orders/min; 1 picker | MPBH | 6,413.97 | FCFS; C=100; S-shape |
| 16 orders/min; 12 pickers | MPBH | 5,917.67 | FCFS; C=100; S-shape |

> **Table 6 note.** Ties are retained rather than forced to one winner. The table is illustrative and does not replace the 864-cell winner analysis.

### 7.9 Section 5.4 — timing versus composition

**Lokasi:** baris 813–829. Ganti seluruh subsection.

**Kutipan lama yang diganti seluruhnya**

> Proposition 4 posits that the batch initiation timing decision exerts a greater influence on SDD performance than the subsequent batch composition rule. This was tested by comparing the effect sizes of Trigger Method and Batching Method (FCFS vs. EDT) in the ANOVA model.
>
> Results indicate that the trigger method produced a statistically significant effect on total late orders (`F(7,207352)≈505.58`, `p<0.001`, `ηp²=0.0168`), whereas the batching method had no significant effect (`F(1,207358)≈0.01`, `p≈0.93`, `ηp²=0.000014`).
>
> The difference in partial eta squared values shows that timing decisions explain orders of magnitude more variance in total late orders than composition rules in this SDD context. Operationally, this means when batches are released matters far more than how orders are arranged within a batch, provided composition follows simple priority rules. However, this conclusion is bounded by the comparison to basic composition strategies (FCFS, EDT). Whether advanced composition metaheuristics would alter this balance remains an open research question.

**Replacement wording**

> **5.4 Timing-versus-composition ablation.** The main factorial cannot isolate timing from composition because MPBH has intrinsic ordering and feasibility-restoration logic. We therefore crossed timing `{FTWB, MPBH-immediate}` with composition `{FCFS, EDT, MPBH}` in six CRN-matched cells. Stratified cluster-aware uncertainty uses 60 independent arrival-rate-by-replication demand streams across two fixed arrival-rate strata. Switching from FTWB to MPBH timing reduced TLO by 18.119 orders (95% CI [17.741, 18.497] fewer). EDT and FCFS did not differ meaningfully (EDT−FCFS=0.036; 95% CI [−0.049, 0.121]). In contrast, MPBH composition reduced TLO by 153.005 versus FCFS (95% CI [151.609, 154.400] fewer) and by 153.041 versus EDT (95% CI [151.647, 154.435] fewer). The tested MPBH composition effect was approximately 8.4 times the timing effect. P4 is therefore **not supported**. The conclusion is bounded to the tested timing and composition implementations and does not rank all possible advanced composition methods.

**Tambahkan Table 7**

| Planned contrast | Mean ΔTLO | Cluster-aware 95% CI | Interpretation |
|---|---:|---:|---|
| MPBH timing − FTWB timing | −18.119 | [−18.497, −17.741] | MPBH timing improves TLO |
| EDT − FCFS | 0.036 | [−0.049, 0.121] | no supported difference |
| MPBH composition − FCFS | −153.005 | [−154.400, −151.609] | MPBH composition improves TLO |
| MPBH composition − EDT | −153.041 | [−154.435, −151.647] | MPBH composition improves TLO |

**Tambahkan Figure 15 caption**

> **Figure 15. Crossed timing-by-composition effects on total late orders.** Points and error bars show CRN-paired mean differences and 95% confidence intervals; negative values favour the first-named MPBH level.

### 7.10 Tambahkan calibration dan β sensitivity

**Lokasi:** setelah Section 5.4 baru.

**Replacement wording baru**

> **5.5 Benchmark and urgency-parameter sensitivity.** First-half tuning selected `F=60 s` for both minimum TLO and maximum composite, `V=4` for minimum TLO, and `V=6` for maximum composite. On held-out replications, changing FTWB from canonical `F=720` to `F=60` changed mean TLO only from 3,284.807 to 3,284.424, but increased throughput from 10.800 to 16.053 orders/h and picker utilisation from 60.41% to 79.58%. For VTWB, held-out `V=4`, `V=6`, and canonical `V=12` yielded mean TLO of 3,284.579, 3,284.754, and 3,287.076, respectively; `V=6` had the highest held-out composite (0.6646). These results show that benchmark calibration matters more for efficiency outcomes than for pooled TLO in the calibration subset. `F=720` and `V=12` remain canonical comparators but must not be called optimal.
>
> For MPBH, `β=1` reduced mean TLO by 65.415 relative to canonical `β=2` (stratified cluster-aware 95% CI [64.132, 66.698] fewer), while increasing mean trips from 174.63 to 212.57 and reducing cart utilisation from 52.93% to 37.96%. `β=3` and `β=4` increased TLO by 48.793 (95% CI [47.834, 49.752]) and 88.903 (95% CI [87.910, 89.895]) relative to `β=2`. Thus, β controls a service-versus-tour-efficiency trade-off rather than possessing one universally best value. SNH and the two urgency-only policies were comparatively insensitive in TLO magnitude over this auxiliary design.

**Tambahkan Figure 16 dan Figure 17 captions**

> **Figure 16. Tuning and held-out sensitivity of canonical FTWB and VTWB parameters.** TLO, throughput, utilisation, and matched composite are shown separately; tuning and held-out observations are not pooled.
>
> **Figure 17. MPBH urgency-threshold trade-off.** Mean TLO, trip count, throughput, and cart utilisation are plotted for `β=1,…,4` with `β=2` marked as the canonical baseline.

### 7.11 Tambahkan computational performance

**Lokasi:** setelah sensitivity subsection.

**Replacement wording baru**

> **5.6 Computational performance.** Decision kernels were benchmarked on Windows 11, an Intel processor with four physical/eight logical cores, 31.88 GiB RAM, and Python 3.14.6. At a pool size of 5,000 orders, median overhead-adjusted latency was below 0.001 ms for FTWB, VTWB, and MaxPicker; 0.382 ms for MaxCart; 5.161 ms for UrgentPicker; 6.114 ms for UrgentCart; 14.071 ms for SNH; and 61.339 ms for MPBH. Descriptive AIC fits classified FTWB, VTWB, and MaxPicker as practically constant, MaxCart/MPBH/SNH/UrgentPicker as O(n), and UrgentCart as O(n log n) over the tested range. These empirical fits do not replace algorithmic upper-bound analysis and exclude WMS, database, and network latency.

**Tambahkan Table 8 atau supplementary table**

| Policy | Median latency at n=5,000 | Empirical fit |
|---|---:|---|
| FTWB | <0.001 ms | practically constant |
| VTWB | <0.001 ms | practically constant |
| MaxPicker | <0.001 ms | practically constant |
| MaxCart | 0.382 ms | O(n) |
| UrgentPicker | 5.161 ms | O(n) |
| UrgentCart | 6.114 ms | O(n log n) |
| SNH | 14.071 ms | O(n) |
| MPBH | 61.339 ms | O(n) |

> **Figure 18. Overhead-adjusted decision latency versus order-pool size.** Axes should show all tested pool sizes and use a log scale if required for legibility.

### 7.12 Section 5.5 lama — proposition disposition

**Lokasi:** baris 830–859. Renumber setelah subsection baru.

**Kutipan lama yang diganti seluruhnya**

> **Proposition 1: Supported.** Adaptive heuristics, especially MPBH, significantly outperformed static rules (FTWB, VTWB), achieving an average 27.04% total late orders reduction. Confirmed by ANOVA (`p<0.001`, `ηp²=0.0168`) and post-hoc tests.
>
> **Proposition 2: Partially Supported.** No heuristic demonstrated universal robustness. While some adaptive methods showed advantages in variability (SD or CV) under specific conditions, assessment requires contextualising mean performance and variability.
>
> **Proposition 3: Strongly Supported.** Significant interaction effects (`p<0.001`, `ηp²=0.396`) confirmed context-dependency. Although MPBH excelled in many challenging scenarios (Table 5, Figure 14), relative heuristic performance varied with operational conditions.
>
> **Proposition 4: Supported.** The batch initiation timing heuristic explained substantially more variance in total late orders (`F(7,207352)≈505.58`, `p<0.001`, `ηp²=0.0168`) than the batch composition method (FCFS vs. EDT) (`F(1,207358)≈0.01`, `p≈0.93`, `ηp²=0.000014`). This effect size comparison confirms the greater impact of the timing decision in this SDD context. We must note, however, that this powerful finding is limited to the comparison against simple composition rules (FCFS/EDT). Whether this finding holds when compared against advanced composition metaheuristics (e.g., proximity-based clustering) remains a key question for future research.
>
> These findings collectively validate the core premise: adaptive batch initiation timing is critical for SDD performance, and its impact can surpass that of subsequent batch composition decisions in highly time-sensitive operations.

**Replacement wording**

> **P1—partially supported.** MPBH produced a substantial 10.66% TLO reduction relative to the mean canonical static benchmark, but the other adaptive policies improved pooled TLO by only 0.17%–1.23%. The evidence supports MPBH, not a general claim that every adaptive policy provides a large benefit.
>
> **P2—partially supported.** MPBH had the lowest pooled TLO SD, but no adaptive policy was universally robust across objectives and contexts. Overloaded cells are finite-horizon stress cases, and CV alone is not a service-quality measure.
>
> **P3—supported with qualification.** A policy other than MPBH was selected in 94 of 864 cells; MPBH won the remaining 770 cells (89.12%). Context matters, but MPBH is dominant across most of the tested domain.
>
> **P4—not supported.** The crossed experiment found a beneficial timing effect, but the tested MPBH composition effect was approximately 8.4 times larger. The accepted-paper conclusion that timing generally dominates composition is withdrawn.
>
> Collectively, the results support coordinated state-aware release and composition, with MPBH the strongest tested deadline-oriented policy. They do not support a timing-only explanation or universal superiority of adaptive rules.

## 8. Discussion, limitations, implications, and conclusion

### 8.1 Discussion opening dan interpretation

**Lokasi:** Section “Discussion and Conclusion”, baris 860–895.

**Kutipan lama yang diganti seluruhnya**

> This study demonstrates that adaptive batch initiation timing, informed by real-time order urgency and resource availability, is a critical component of SDD warehousing.
>
> The central finding is not simply that one heuristic is universally superior, but that the context of the operation dictates heuristic performance. The significant three-way interaction effect between the trigger method, incoming rate, and picker availability (`ηp²=0.396`) explained vastly more variance in total late orders than the main effect of the Trigger Method alone (`ηp²=0.0168`). This confirms that the primary challenge is selecting a heuristic logic that is robust to the specific operational environment (Proposition 3).
>
> Within this context-dependent landscape, the MPBH emerged as the most robust strategy, achieving an average 27.04% total late orders reduction over static benchmarks (Proposition 1). Its superiority was most pronounced in high-load scenarios (Figure 14). This robustness stems from its iterative logic: unlike simpler heuristics, MPBH actively balances urgency (sorting by due date) against constraints (capacity and predicted total late orders). By removing the latest due date order upon constraint violation, it dynamically prioritises the most time-critical orders while still attempting to build efficient batches.
>
> Our findings extend prior work that often treats timing as a static parameter (Schleyer and Gue, 2012), showing that optimising the trigger itself yields substantial performance gains. This result is consistent with emerging evidence that frameworks combining adaptive heuristics with stochastic simulation yield substantial advantages over fixed-parameter approaches in on-demand delivery settings, where real-time variability renders static rules structurally insufficient (Zhang et al., 2025). This addresses FTWB limitations in volatile SDD environments (Voccia et al., 2019) by leveraging TBC principles (Stalk, 2012) to balance batching efficiency against delivery risk.
>
> The success of urgency-aware heuristics (MPBH, UrgentPicker) supports prior emphasis on due-date orientation (Henn, 2015). Unlike offline metaheuristics such as GVNS (Bustillo et al., 2015; Menéndez et al., 2017), our heuristics are computationally efficient (O(n) to O(n log n)) and designed for real-time online decision-making in dynamic SDD operations. Notably, MPBH's structured, state-dependent logic offers an implementable solution that contrasts with more opaque, black-box DRL approaches (Cals et al., 2021; Beeks et al., 2022).
>
> The context-dependency of heuristic performance (Proposition 3) is consistent with findings in related logistics problems (Dauod and Won, 2022). Proposition 2 (robustness) is only partially supported; the dramatic failure of UrgentCart (Section 5.3) highlights that adaptivity does not guarantee stability, a critical nuance for heuristic design.

**Replacement wording**

> The corrected results identify MPBH as the strongest tested deadline-oriented policy, not as a universally optimal algorithm. It reduced pooled canonical-benchmark TLO by 10.66%, ranked first under all four declared composite-weight schemes, and won 89.12% of operational cells under the declared winner rule. MaxPicker remains globally Pareto non-dominated because it combines near-maximal picker utilisation with competitive service performance. These findings make policy choice a multi-objective decision rather than a single-rank exercise.
>
> The mechanism is also different from the accepted-paper interpretation. MPBH couples release with EDD-based candidate construction and feasibility restoration. The crossed experiment shows that its composition layer contributes substantially more than its tested timing layer. TBC is therefore supported only in a bounded sense: using current temporal and resource state can reduce avoidable delay, but temporal competitiveness in this model arises from coordinating *when* work is released with *which* orders are released. The data do not support elevating timing above composition as a general theoretical principle.
>
> Adaptivity alone is insufficient. MaxPicker, MaxCart, UrgentPicker, and SNH yielded pooled TLO reductions of at most 1.23% relative to the canonical static mean. UrgentCart did not fail; it reproduced MaxCart's main-factorial outcomes, showing that an added urgency condition can be operationally inactive under a given parameterisation. This equality and the β sensitivity results favour mechanism checks over labels such as “adaptive” or “urgency aware.”
>
> The computational evidence supports online use at the tested scale but with a clear cost gradient. MPBH was the slowest kernel at 61.34 ms for 5,000 waiting orders, still below one second on the test machine, while simpler rules were substantially faster. This benchmark excludes data-access and systems-integration latency, so it supports algorithmic feasibility rather than end-to-end WMS performance.

### 8.2 P4 discussion

**Lokasi:** baris 896–907.

**Kutipan lama yang diganti seluruhnya**

> Perhaps the most significant finding, strongly supporting Proposition 4, is that the timing of batch initiation has a greater impact on total late orders than the method of batch composition (FCFS vs. EDT). The timing heuristic explained substantially more variance in total late orders (main effect `ηp²=0.0168`) than composition (`ηp²=0.000014`). This suggests a paradigm shift: in time-critical SDD, “when” to batch may matter more than “how” (Shavaki and Jolai, 2021). We must state this finding with a critical caveat: this comparison is limited to the simple, non-advanced composition rules (FCFS/EDT) used in this study. Whether this finding holds when compared against sophisticated, proximity-based composition metaheuristics (e.g., Henn and Schmid, 2013) remains a critical question for future research.

**Replacement wording**

> The timing-versus-composition result is a substantive negative finding. MPBH timing improved TLO relative to FTWB timing, but MPBH composition produced an effect approximately 8.4 times larger in the crossed subset. P4 is therefore not supported, and the “when matters more than how” claim is withdrawn. The valid conclusion is narrower: timing and composition are separable contributors, and advanced composition can dominate their relative effect. Generalisation beyond FCFS, EDT, and the tested MPBH composition requires comparison with proximity, savings, local-search, and optimisation-based methods under an equal tuning budget.

### 8.3 Section 6.1 — limitations

**Lokasi:** baris 908–924. Ganti dua limitation lama dengan daftar threat yang
sesuai model final.

**Kutipan lama yang diganti seluruhnya**

> While this simulation study is extensive, its external validity is bounded by two key modelling simplifications. First, the model employs a homogeneous Poisson process (HPP) for order arrivals (Boysen et al., 2019), which does not capture the non-stationary nature of a true SDD environment that features distinct peaks and lulls (i.e., a non-homogeneous Poisson process, or NHPP). We hypothesise that an NHPP would, in fact, amplify the performance differences, as the adaptive rules (like MPBH) are specifically designed to respond to such volatility, while static rules (FTWB) would fail significantly during unmanaged peaks.
>
> Second, the model does not include picker congestion or blocking. In a high-load scenario (e.g., 12 pickers at 16 orders/min), congestion would become a dominant factor in operational delays, and our processing time estimates are therefore optimistic. We hypothesise that congestion would disproportionately degrade the performance of simple, resource-aware heuristics like MaxPicker. This rule triggers immediately when a picker is free, which, in a congested system, would merely dispatch more pickers into an already-crowded environment, potentially worsening the bottleneck. The logic of MPBH, which balances urgency against batch capacity, may be inherently more robust to these effects, though this remains to be proven.

**Replacement wording**

> **6.1 Limitations and threats to validity.** First, arrivals, due allowances, order lines, quantities, and ABC demand are synthetic. The homogeneous Poisson process excludes peaks, lulls, correlation, and customer heterogeneity; no result establishes that an NHPP would favour MPBH. Second, the model excludes picker congestion and blocking, stockouts and replenishment, packing, vehicle dispatch, breaks, failures, overtime, heterogeneous picker speeds, split orders, and carts as independently constrained resources. Completion denotes return to the warehouse I/O point rather than customer delivery.
>
> Third, high-load cells exhibit positive backlog drift and are finite-horizon stress experiments, not steady-state estimates. The 5,460-s Welch deletion removes initialisation transient in a stable pilot but does not make overloaded cells stationary. Fourth, exact tardiness is unavailable for outstanding orders; the all-order measure is explicitly a lower bound at the censor horizon. Fifth, the urgency estimator is a calibrated surrogate with non-zero holdout error, although executed tour time uses exact model routing.
>
> Sixth, canonical `F=720`, `V=12`, and `β=2` are identity-preserving baselines, not globally tuned values. The auxiliary calibration covers a limited scenario subset and tuning budget. Seventh, the main factorial cannot isolate timing from intrinsic MPBH/SNH composition; causal separation relies on the smaller crossed experiment. Eighth, no MIP optimum, advanced literature comparator, operational MPID, empirical WMS validation, domain-expert sign-off, or independent statistical reproduction is available. Finally, the final run manifest records a dirty source tree. Config and source hashes preserve traceability, but a signed clean-release reproduction and immutable archive are still required.

### 8.4 Section 6.2 — managerial implications

**Lokasi:** baris 925–931.

**Kutipan lama yang diganti seluruhnya**

> Theoretically, this work advances the order batching literature by elevating batch initiation timing from an implicit parameter to a critical, state-dependent decision variable, extending TBC theory to warehouse micro-operations (Peng and Lu, 2017). Practically, strategies like MPBH are implementable using standard WMS data (order pool, due times, picker status) with low computational overhead (ranging from O(n) for urgency-aware rules to O(n log n) for MPBH). The 27.04% average total late orders reduction suggests significant potential for cost savings and customer satisfaction improvement.

**Replacement wording**

> **6.2 Managerial implications.** A warehouse should select a policy against its service and resource priorities, not solely from an aggregate rank. MPBH is the default candidate when deadline performance and throughput dominate: it has the lowest TLO, highest non-late-at-horizon rate and throughput, and first composite rank under all tested weights. MaxPicker is a credible alternative when implementation simplicity and picker utilisation dominate and is the only other globally non-dominated policy. At low arrival rate with 12 pickers, FTWB, MPBH, MaxPicker, and SNH all achieved zero mean TLO in the representative fixed-factor context, so the simplest acceptable rule may be preferred.
>
> Parameter choices should be exposed as operating controls. Reducing MPBH from `β=2` to `β=1` improved TLO but increased trip count and reduced cart fill. Reducing canonical FTWB from `F=720` to tuned `F=60` changed held-out pooled TLO only slightly while materially improving throughput and utilisation. Managers should therefore set service, trip, labour, and cart-fill thresholds before tuning; the present study cannot translate these effects into cost savings because no cost model or empirical MPID was supplied. A production pilot must also include WMS/database latency, congestion, and local demand validation.

**Tambahkan managerial guide table**

| Operating priority/condition | Evidence-based candidate | Qualification |
|---|---|---|
| Minimise TLO / maximise non-late-at-horizon rate | MPBH | strongest aggregate and 770/864 cells; highest compute cost |
| High picker utilisation with simpler logic | MaxPicker | globally Pareto non-dominated; weaker deadline performance than MPBH |
| Low rate, abundant pickers | FTWB, MPBH, MaxPicker, or SNH | four-way zero-TLO tie in the representative fixed-factor context |
| More aggressive MPBH service | `β=1` | fewer late orders, more trips, lower cart fill |
| More tour consolidation | higher β | more late orders in MPBH sensitivity |
| Static benchmark deployment | calibrate F/V locally | do not assume canonical F/V is optimal |

### 8.5 Future research

**Lokasi:** baris 932–941.

**Kutipan lama yang diganti seluruhnya**

> Based on our findings and these limitations, future research should move in several directions. The most pressing need is to evaluate these heuristics under more realistic conditions, including empirical non-homogeneous arrival patterns (NHPP) and by incorporating dynamic picker congestion models. Furthermore, to truly understand the optimality gap, MPBH should be benchmarked against (a) optimal solutions for small, tractable instances (e.g., via Mixed-Integer Programming, MIP) and (b) state-of-the-art dynamic scheduling rules from the literature, not just simple composition methods. Finally, this work should be extended by integrating warehouse timing decisions with last-mile delivery constraints, such as fixed vehicle dispatch schedules. The integrated scheduling-routing framework for products with hard delivery deadlines—where time constraints function analogously to SDD cutoffs—offers a methodological template for such extensions (Dantas et al., 2024).

**Replacement wording**

> Future work should first validate arrival, workload, due-time, travel, and congestion inputs against operational data and establish a domain-approved MPID. Confirmatory comparisons should then be reproduced from a signed clean release and immutable archive. Methodologically, MPBH should be compared with exact solutions on tractable instances and with proximity, savings, local-search, rolling-horizon, and learning-based policies under equal information and tuning budgets. Extensions should include non-homogeneous and correlated demand, heterogeneous pickers, aisle congestion, stock and packing constraints, and vehicle cut-offs. Finally, an integrated warehouse-to-last-mile model is needed before making claims about customer delivery, cost savings, or TBC effects beyond the picking system.

### 8.6 Tambahkan Section 7 — Conclusion terpisah

**Lokasi:** sesudah Section 6.2/future research, sebelum Data Availability.

**Replacement wording baru**

> **7. Conclusion.** Across 207,360 corrected simulation runs, MPBH was the strongest tested policy for deadline performance: it reduced mean TLO by 10.66% relative to the pooled canonical FTWB/VTWB benchmark, achieved the highest non-late-at-horizon rate and throughput, and won 770 of 864 operational cells. MaxPicker remained Pareto non-dominated, and most other adaptive policies delivered only small pooled TLO improvements. The crossed experiment did not support the proposition that timing has greater impact than composition; MPBH composition had the larger effect in the tested subset. β sensitivity and benchmark calibration further showed that service, trip count, cart fill, utilisation, and computational cost must be considered jointly. These findings support coordinated state-aware release and composition within the simulated domain, while real-world effectiveness remains contingent on empirical validation and independent reproduction.

## 9. Data Availability dan transparency

### 9.1 Data Availability

**Lokasi:** baris 943–945.

**Kutipan lama yang diganti**

> The simulation results data supporting the findings of this study are openly available in Mendeley Data at https://doi.org/10.17632/49r2pmymrm.1.

**Replacement wording sementara yang tidak membuat klaim palsu**

> The accepted-paper dataset at https://doi.org/10.17632/49r2pmymrm.1 contains legacy results and does not support the corrected numerical claims reported in this revision. The corrected aggregate results, per-order records, configuration, analysis code, manifests, and SHA-256 checksums will be deposited in **[repository and versioned DOI to be supplied]** after release approval and verification of the archived bundle. Until that archive is available, the revised results should not be described as openly reproducible from the legacy DOI.

Ganti placeholder hanya setelah FD-02/FD-06 dan archive DOI benar-benar selesai.

### 9.2 Tambahkan reproducibility/transparency statement

**Lokasi:** sesudah Data Availability.

**Replacement wording baru**

> **Reproducibility statement.** All 207,360 planned main-factorial runs completed successfully and passed the local artifact audit. The final aggregate and per-order files contain 207,360 run rows and 621,955,584 order rows, respectively; 522,713,088 order rows belong to the post-warm-up measurement cohort. The release bundle records seeds, run UUIDs, model and configuration versions, source/config hashes, row counts, and file checksums. The production manifest records `git_dirty=True`; consequently, clean-machine reproduction from a signed release and independent verification are outstanding and are reported as limitations rather than completed controls.

## 10. Daftar revisi semua figure

| Figure asli | Kutipan caption lama | Tindakan dan caption revisi |
|---|---|---|
| 1 | Warehouse layout (Ho et al., 2008) | Redraw/annotate exact model; gunakan caption Section 5.4 dokumen ini |
| 2 | Boxplot of Total Late Orders by Trigger Method | Regenerate final censoring-aware TLO; gunakan caption Section 7.4 |
| 3 | Boxplot of Throughput per Hour by Trigger Method | Regenerate dan pasangkan dengan non-late-at-horizon rate |
| 4 | Boxplot of Picker Utilisation by Trigger Method | Regenerate; tambahkan cart utilisation/trips |
| 5 | Boxplot of Composite Score by Trigger Method | Replace dengan Pareto + four-weight sensitivity |
| 6 | Average TLO vs Incoming Rate | Regenerate final + uncertainty + finite-horizon warning |
| 7 | Average TLO vs Number of Pickers | Regenerate final + uncertainty |
| 8 | Average TLO vs Cart Capacity | Regenerate final |
| 9 | Scatter TLO vs Picker Utilisation | Replace; pooled correlation dihapus, gunakan service-throughput Pareto |
| 10 | SD TLO vs Incoming Rate | Regenerate final |
| 11 | CV TLO vs Incoming Rate | Regenerate final, interpret with mean |
| 12 | SD TLO vs Number of Pickers | Regenerate final |
| 13 | CV TLO vs Number of Pickers | Regenerate final |
| 14 | Trigger × Pickers interaction faceted by rate | Regenerate final; mark stress/non-stationary panels and MaxCart/UrgentCart overlap |
| 15 baru | tidak ada | Crossed timing × composition paired effects |
| 16 baru | tidak ada | F/V tuning and held-out sensitivity |
| 17 baru | tidak ada | β service-efficiency trade-off |
| 18 baru | tidak ada | Decision latency scaling |

Semua gambar harus menampilkan unit, n/replications, definisi error bar, dan
caption yang menyebut dataset final. Jika batas jumlah figure jurnal ketat,
Figures 10–13 dan detail sensitivity dapat dipindahkan ke supplement; jangan
menghapus hasil negatif P4, calibration, atau computational benchmark.

## 11. Standardisasi global di seluruh paper

Lakukan pencarian global setelah seluruh penggantian di atas:

| Cari/konsep lama | Ganti/aturan final |
|---|---|
| `27.04%` | `10.66%` hanya untuk MPBH versus mean canonical FTWB/VTWB |
| MPBH TLO `829.5` | `1,788.830` |
| MPBH throughput `187.2` | `60.969 orders/h` |
| UrgentCart `worst`, `poor`, `failure`, `1716.2` | hapus; main results identical to MaxCart |
| `F=360 s` | canonical `F=720 s`; tuned `F=60 s` dilabel terpisah |
| setup `30 s` | `180 s per executed tour` |
| `1–10 items/order` | `1–10 distinct lines; 1–10 pieces/line; 1–100 pieces/order` |
| `delivered late` | `completed late plus overdue outstanding at the horizon`; completion = picking return to I/O |
| `optimal` / `optimality` untuk policy winner | `best-performing among the tested policies` |
| `timing heuristic` untuk SNH/MPBH | `integrated release-and-composition policy` |
| `timing matters more than composition` | hapus; P4 not supported |
| legacy ANOVA F/ηp² | hapus dari abstract/results/discussion/conclusion |
| `p=0` | jangan digunakan; laporkan CI dan `p<0.001` bila perlu |
| `DVNS` | `SNH` |
| `items` sebagai workload | gunakan `distinct lines` atau `pieces` secara eksplisit |
| `picker utility` | `picker utilisation` secara konsisten |
| `Total Late Order(s)` | `total late orders (TLO)` |
| `all methods computationally O(1)` | gunakan hasil per-policy pada Section 5.6 |
| claim cost/customer satisfaction | hapus kecuali cost model/empirical validation ditambahkan |

Perbaiki juga heading hasil ekstraksi yang masih berupa bullet (`- Proposed
Heuristics`, `- Results and Analysis`, `- Discussion and Conclusion`) menjadi
heading bernomor yang konsisten.

## 12. Klaim yang wajib dihapus, bukan hanya dilemahkan

1. “MPBH improves TLO by 27.04%.”
2. “UrgentCart is the worst method” dan seluruh mekanisme
   “worst-of-both-worlds”.
3. “Timing has greater influence than composition” atau “when matters more
   than how”.
4. Seluruh F-statistic, Tukey result, dan partial-eta-squared legacy pada
   Sections 5–6.
5. Nilai accepted Table 4–6 dan semua figure yang dibuat dari dataset legacy.
6. Klaim bahwa `F=720`, `V=12`, atau `β=2` adalah optimum.
7. Klaim bahwa hasil telah membuktikan cost saving, customer satisfaction,
   last-mile delivery, atau real-world TBC effect.
8. Klaim open reproducibility melalui DOI lama untuk angka revisi.

## 13. Pemeriksaan akhir sebelum wording dipindahkan ke manuskrip

- [ ] Setiap angka pada Abstract, Sections 5–7, Tables 4–8, dan captions cocok
  dengan source CSV final.
- [ ] P1 partial, P2 partial, P3 supported with qualification, P4 not supported.
- [ ] Main factorial, ablation, calibration, β sensitivity, dan latency tidak
  dipool seolah berasal dari desain yang sama.
- [ ] Table 6 menyebut secondary factors fixed dan mempertahankan ties.
- [ ] Completed-only tardiness dibedakan dari all-order horizon lower bound.
- [ ] Poisson overdispersion dan NB nonconvergence dilaporkan; NB tidak dipakai
  untuk inference.
- [ ] Tidak ada kata *preregistered* kecuali registration timestamp dan URL
  benar-benar tersedia.
- [ ] DOI revisi, signed tag, immutable archive, clean-machine reproduction,
  MPID, SME validation, dan statistical review hanya dinyatakan selesai jika
  bukti eksternalnya telah ditutup.
- [ ] Semua referensi baru telah diverifikasi pada sumber penerbit.
- [ ] Setelah layout final, response letter menunjuk page dan paragraph aktual,
  dan seluruh perubahan di-highlight sesuai instruksi editor.
