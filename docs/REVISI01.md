**RENCANA REVISI KOMPREHENSIF**

**Manuskrip EJIE-337519**

*"Adaptive Heuristics for Order Batching Initiation Timing in Same-Day
Delivery Warehouses"*

  ----------- ------------------------------
  **Item**    **Detail**

  Jurnal      European Journal of Industrial
              Engineering (Inderscience)

  Keputusan   Acceptable with major
  editor      revisions (kedua reviewer)

  Tanggal     10 Agustus 2026
  email       
  keputusan   

  Batas waktu 30 hari sejak 10 Agustus 2026
  resubmisi   (≈ 9 September 2026)

  Jumlah      2 (Reviewer 1: 7 komentar
  reviewer    mayor + 6 minor; Reviewer 2: 4
              komentar mayor)

  Sumber      File lampiran ulasan
  komentar    (2026_EJIE-337519_RAV2.docx)
  Reviewer 1  

  Sumber      Badan email keputusan editor
  komentar    
  Reviewer 2  
  ----------- ------------------------------

+----------------------------------------------------------------------+
| **Persyaratan wajib dari editor**                                    |
|                                                                      |
| Revisi harus disertai (1) tanggapan rinci dan sistematis terhadap    |
| setiap rekomendasi reviewer di awal manuskrip yang direvisi, (2)     |
| rujukan nomor halaman untuk setiap perubahan (sebaiknya teks yang    |
| diubah disorot/highlight), dan (3) daftar pustaka yang diperbarui    |
| dengan artikel-artikel terbaru yang relevan, termasuk dari EJIE      |
| sendiri.                                                             |
+----------------------------------------------------------------------+

A. Ringkasan Eksekutif & Cara Membaca Dokumen Ini

Dokumen ini adalah rencana kerja rinci untuk merevisi manuskrip
EJIE-337519 agar memenuhi seluruh catatan dari Reviewer 1 (7 komentar
mayor, bernomor 1--7 dan 10, plus 6 komentar minor) dan Reviewer 2 (4
komentar mayor). Total terdapat 17 butir catatan yang harus ditangani.
Karena beberapa butir saling terkait (misalnya, ablasi
timing-vs-komposisi pada R1#1 secara langsung menentukan bagaimana
Proposisi 4 pada R1#4 harus ditulis ulang), Bagian B memetakan
keterkaitan tersebut agar revisi dapat dikerjakan secara efisien, bukan
sebagai 17 tugas terpisah.

Setiap butir pada Bagian C disusun dengan format yang sama: (i) inti
komentar reviewer, (ii) mengapa hal itu penting secara metodologis,
(iii) rencana tindakan konkret, (iv) bagian manuskrip yang terdampak,
dan (v) klasifikasi usaha --- apakah butir tersebut memerlukan
simulasi/komputasi baru, hanya reanalisis data yang sudah ada, atau
murni revisi teks. Klasifikasi ini penting untuk perencanaan waktu dalam
jendela 30 hari.

A.1 Klasifikasi Usaha --- Ringkasan

  --------------------- ---------- ---------------
  **Kategori**          **Jumlah   **Contoh**
                        butir**    

  Memerlukan            3          R1#1 (studi
  simulasi/eksperimen              ablasi), R1#2
  baru                             (kalibrasi
                                   benchmark),
                                   R2#3
                                   (pengukuran
                                   waktu
                                   komputasi)

  Reanalisis data       3          R1#5 (metrik
  simulasi yang sudah              tambahan), R1#6
  ada (tanpa run ulang             (sensitivitas
  penuh)                           bobot & koreksi
                                   Tabel 4)

  Revisi/penguatan      11         R1#3, R1#4,
  teks, notasi, atau               R1#7, R1#10, R1
  kajian pustaka (tanpa            minor 1--6,
  data baru)                       R2#1, R2#2,
                                   R2#4
  --------------------- ---------- ---------------

Prioritaskan tiga butir yang memerlukan eksperimen baru (R1#1, R1#2,
R2#3) di 10--14 hari pertama karena inilah yang menentukan apakah klaim
inti paper (Proposisi 1 dan 4) tetap valid. Sisanya dapat dikerjakan
paralel oleh anggota tim yang menulis, sementara simulasi berjalan.

B. Peta Keterkaitan Antar-Komentar

Menangani butir-butir berikut secara bersamaan akan menghemat waktu
karena keduanya bermuara pada perubahan yang sama:

  -------------- ----------- ------------------------
  **Kelompok**   **Butir     **Alasan digabung**
                 terkait**   

  Timing vs.     R1 Major    Hasil studi ablasi (#1)
  komposisi      #1, R1      adalah bukti yang
                 Major #4    dibutuhkan untuk menulis
                             ulang Proposisi 4 (#4)
                             secara defensif.

  Panduan        R1 Major    Keduanya meminta panduan
  manajerial /   #10, R2     pemilihan heuristik yang
  praktis        Major #4    lebih spesifik konteks
                             --- dapat dijawab dalam
                             satu subbagian Diskusi
                             yang diperluas.

  Metrik & Tabel R1 Major    Keduanya memerlukan
  4              #5, R1      penghitungan ulang dari
                 Major #6    data run yang sama dan
                             revisi Tabel 4/Bagian
                             5.1 secara terpadu.

  Pustaka        R1 Minor    Keduanya meminta
  terkini        #6, R2      penambahan referensi
                 Major #1    terbaru; dapat
                             dikerjakan dalam satu
                             putaran pencarian
                             literatur.

  Formalisasi &  R1 Major    Formalisasi MDP (#3) dan
  kekakuan       #3, R2      pelaporan waktu
  metodologis    Major #3    komputasi/skalabilitas
                             (#R2-3) sama-sama
                             memperkuat argumen bahwa
                             heuristik ini rigorous
                             dan applicable secara
                             real-time.
  -------------- ----------- ------------------------

C. Rencana Revisi Rinci per Komentar

C.1 Reviewer 1 --- Komentar Mayor

R1-Mayor #1 --- Ambiguitas metodologis: MPBH mencampur keputusan
triggering dan komposisi batch

**Inti komentar reviewer:** *MPBH tidak hanya memutuskan kapan memulai
batching, tetapi juga mengurutkan order berdasarkan due date, membangun
batch sementara, memeriksa constraint kapasitas/keterlambatan, dan
membuang order berprioritas rendah. Reviewer meminta pemisahan eksplisit
antara lapisan keputusan triggering, konstruksi batch, penugasan picker,
dan routing, didukung studi ablasi.*

**Mengapa penting:** ISU INI ADALAH YANG PALING KRITIS di seluruh
ulasan. Karena MPBH menggabungkan dua jenis keputusan, tidak dapat
dipastikan apakah keunggulan 27.04% berasal dari waktu pemicuan yang
lebih baik, komposisi batch yang lebih baik, atau interaksi keduanya.
Ini secara langsung melemahkan validitas Proposisi 1 dan terutama
Proposisi 4 (bahwa timing lebih penting daripada komposisi), karena
pembanding komposisi (FCFS/EDT) tidak setara secara struktural dengan
MPBH yang sudah menyertakan logika pemilihan order.

**Rencana tindakan revisi:**

- Definisikan secara eksplisit di Bagian 3.1/4 empat lapisan keputusan
  (triggering, batch construction, picker assignment, routing) dan
  nyatakan lapisan mana yang dioptimasi oleh tiap-tiap dari 8 metode
  yang diuji.

- Rancang eksperimen ablasi 2×2 (minimal) dengan memisahkan komponen
  MPBH: (a) \'MPBH-trigger + FCFS/EDT composition\' --- gunakan aturan
  pemicu MPBH (kondisi berhenti/constraint check) tetapi order
  dimasukkan ke batch secara FCFS biasa setelah trigger menyala; (b)
  \'Trigger standar (FTWB/VTWB) + MPBH composition\' --- gunakan logika
  pengurutan due-date dan pruning MPBH sebagai aturan komposisi setelah
  trigger FTWB/VTWB menyala; (c) MPBH penuh (baseline saat ini) sebagai
  kontrol.

- Jalankan subset representatif dari desain faktorial (misalnya pada
  level λ dan jumlah picker yang mewakili kondisi rendah/sedang/tinggi
  beban, seperti pada Tabel 6) untuk ketiga varian ablasi tersebut,
  dengan jumlah replikasi yang sama (30) agar dapat dibandingkan secara
  statistik.

- Lakukan ANOVA/uji-t untuk mendekomposisi kontribusi varians ke TLO
  dari komponen triggering vs komponen komposisi secara terpisah.

- Tambahkan subbagian baru \'5.x Studi Ablasi: Mendekomposisi Kontribusi
  Timing dan Komposisi\' yang melaporkan hasil ini, dan gunakan hasilnya
  untuk mengkalibrasi ulang klaim pada Proposisi 4 (lihat R1-Mayor #4).

**Bagian manuskrip terdampak:** Bagian 3.1 (definisi lapisan keputusan),
Bagian 4.4 (deskripsi MPBH), Bagian 5 (subbagian ablasi baru), Bagian
5.4/5.5 (Proposisi 4), Diskusi 6.

**Klasifikasi usaha:** Besar \| **Perlu simulasi/komputasi baru: Ya ---
desain ablasi baru + run simulasi tambahan**

R1-Mayor #2 --- Perbandingan benchmark (FTWB/VTWB) belum adil karena
parameter tidak dikalibrasi

**Inti komentar reviewer:** *Parameter F=360s dan V=12 diambil langsung
dari Gil-Borrás et al. (2020) tanpa disesuaikan (retuning) untuk
lingkungan simulasi penelitian ini. Penulis sendiri mengakui hal ini
dapat membuat performa benchmark konservatif, sehingga peningkatan
performa MPBH yang dilaporkan berpotensi overstated.*

**Mengapa penting:** Jika benchmark tidak dikalibrasi secara wajar,
klaim \'27.04% improvement\' menjadi rentan terhadap kritik bahwa MPBH
dibandingkan dengan strawman. Untuk jurnal industrial engineering yang
rigorous, baseline harus kompetitif, bukan hanya representatif
literatur.

**Rencana tindakan revisi:**

- Lakukan studi kalibrasi/sensitivitas parameter: jalankan FTWB pada
  rentang F (misalnya 60s--600s, beberapa titik) dan VTWB pada rentang V
  (misalnya 4--24 order) pada kondisi operasional yang representatif,
  lalu pilih F\* dan V\* yang meminimalkan TLO rata-rata (atau yang
  memaksimalkan composite score) sebagai \'tuned benchmark\'.

- Laporkan performa MPBH terhadap DUA versi benchmark: versi literatur
  (F=360s, V=12, sebagaimana sekarang) dan versi tuned (F\*, V\*),
  sehingga pembaca dapat menilai seberapa banyak keunggulan MPBH
  bertahan setelah benchmark dioptimalkan.

- Tambahkan tabel/figur sensitivitas parameter (TLO vs F; TLO vs V) di
  Bagian 5.1 atau lampiran.

- Revisi kalimat di Bagian 4.1 agar transparan tentang metodologi
  kalibrasi dan mengapa kedua versi (literatur & tuned) dilaporkan.

**Bagian manuskrip terdampak:** Bagian 4.1 (deskripsi FTWB/VTWB), Bagian
5.1 (hasil komparatif), kemungkinan lampiran baru untuk kurva
sensitivitas.

**Klasifikasi usaha:** Besar \| **Perlu simulasi/komputasi baru: Ya ---
grid search/kalibrasi parameter benchmark**

R1-Mayor #3 --- Formulasi matematis dinilai terlalu high-level / belum
rigorous

**Inti komentar reviewer:** *Reviewer meminta formalisasi yang lebih
ketat, misalnya sebagai Markov Decision Process (MDP) atau semi-MDP
dengan definisi state space, action space, fungsi transisi, dan fungsi
biaya --- atau alternatifnya, formulasi Mixed-Integer Programming (MIP)
skala kecil untuk versi offline sebagai pembanding optimal.*

**Mengapa penting:**

**Rencana tindakan revisi:**

- Perluas Bagian 3.1: formalkan OOBSDDP sebagai (semi-)MDP dengan
  komponen eksplisit: State S_t = (O_t, B_t, P_t, t) (sudah ada, perlu
  diperkaya), Action space A = {trigger, wait} (atau untuk MPBH/SNH, A
  juga mencakup pemilihan subset order), fungsi transisi (kedatangan
  order Poisson, penyelesaian picking), dan fungsi cost/reward berbasis
  indikator keterlambatan (Persamaan 2).

- Sertakan diagram/notasi formal yang menunjukkan bagaimana
  masing-masing dari 8 metode adalah kebijakan (policy) π: S_t → A yang
  berbeda dalam kompleksitas dan informasi yang digunakan.

- Opsional namun bernilai tinggi: tambahkan studi benchmark skala kecil
  menggunakan formulasi MIP untuk versi offline (misalnya 10--20 order
  dengan waktu horizon pendek dan due-date diketahui di muka) untuk
  mengukur optimality gap MPBH terhadap solusi optimal --- ini juga
  menjawab saran R1 Minor pada arah riset masa depan dan memperkuat
  kontribusi metodologis secara signifikan.

- Jika opsi MIP tidak memungkinkan dalam 30 hari, jelaskan secara
  eksplisit di bagian keterbatasan (6.1) bahwa perbandingan terhadap
  solusi optimal MIP/exact merupakan agenda riset lanjutan yang
  eksplisit direncanakan, sembari tetap menambahkan formalisasi MDP
  sebagai kontribusi metodologis inti pada revisi ini.

**Bagian manuskrip terdampak:** Bagian 3.1 (perluasan besar), Bagian 6.1
dan 6.2 (jika MIP tidak dikerjakan penuh).

**Klasifikasi usaha:** Sedang--Besar \| **Perlu simulasi/komputasi baru:
Sebagian --- formalisasi MDP tidak perlu run baru; MIP opsional
memerlukan eksperimen kecil baru**

R1-Mayor #4 --- Proposisi 4 (timing \> komposisi) dinilai overstated

**Inti komentar reviewer:** *Klaim bahwa timing initiation memiliki
dampak lebih besar daripada komposisi batch hanya didukung perbandingan
terhadap dua aturan komposisi sederhana (FCFS dan EDT), bukan
metode-metode canggih seperti proximity-based clustering, savings-based
rules, local search, atau VNS. Reviewer mengusulkan kalimat yang lebih
hati-hati: klaim berlaku \'dalam lingkungan SDD yang disimulasikan dalam
studi ini, ketika komposisi batch dibatasi pada aturan FCFS dan EDT
sederhana\'.*

**Mengapa penting:** Ini terkait langsung dengan R1-Mayor #1 --- hasil
ablasi akan menentukan seberapa kuat klaim ini dapat dipertahankan.

**Rencana tindakan revisi:**

- Ganti seluruh kemunculan klaim Proposisi 4 (Abstrak, Bagian 1
  kontribusi, Bagian 2.4, Bagian 5.4, Bagian 5.5, Diskusi 6) dengan
  formulasi terkualifikasi persis seperti yang disarankan reviewer,
  disesuaikan dengan temuan ablasi baru dari R1-Mayor #1.

- Jika hasil ablasi R1-Mayor #1 menunjukkan bahwa sebagian keunggulan
  MPBH memang berasal dari komponen komposisinya, nyatakan hal ini
  secara eksplisit dan sesuaikan besaran klaim (misalnya, laporkan
  ukuran efek terpisah untuk komponen timing murni).

- Tambahkan kalimat pembatas di Bagian 6.2 (arah riset masa depan) yang
  secara eksplisit menyebut metaheuristik komposisi lanjutan (proximity
  clustering, savings-based, VNS/GVNS) sebagai perbandingan yang belum
  dilakukan.

**Bagian manuskrip terdampak:** Abstrak, Bagian 1, Bagian 2.4, Bagian
5.4, Bagian 5.5, Bagian 6 (Diskusi).

**Klasifikasi usaha:** Sedang (tergantung hasil ablasi #1) \| **Perlu
simulasi/komputasi baru: Tidak langsung --- bergantung pada hasil
R1-Mayor #1**

R1-Mayor #5 --- Perlu metrik performa tambahan selain Total Late Orders

**Inti komentar reviewer:** *TLO adalah hitungan absolut yang sangat
dipengaruhi oleh volume order dan tidak membedakan order yang sedikit
terlambat dari yang sangat terlambat. Reviewer meminta metrik tambahan:
rasio order terlambat (late order ratio), tingkat pengiriman tepat waktu
(on-time delivery rate), dan rata-rata tardiness.*

**Mengapa penting:** Tanpa metrik relatif dan metrik keparahan
keterlambatan, klaim keunggulan MPBH sulit dibandingkan lintas skenario
dengan volume order yang berbeda-beda (6 level λ pada desain
eksperimen), dan tidak menangkap trade-off antara \'sedikit terlambat\'
vs \'sangat terlambat\'.

**Rencana tindakan revisi:**

- Definisikan metrik baru secara formal di Bagian 3.4: Late Order Ratio
  = TLO/N; On-Time Delivery Rate = 1 − (TLO/N) atau berbasis Θ; Average
  Tardiness = (1/TLO) Σ max(0, c_i − d_i) untuk order yang terlambat
  (dan/atau rata-rata tardiness atas seluruh N order sebagai ukuran
  tambahan).

- Hitung ulang metrik-metrik ini dari data mentah 207.360 run yang sudah
  tersimpan (lihat Data Availability --- Mendeley Data) TANPA perlu
  menjalankan ulang simulasi, karena completion time (c_i) dan due date
  (d_i) per order seharusnya sudah tercatat.

- Tambahkan kolom/tabel baru (perluasan Tabel 4) dan minimal satu figur
  baru (boxplot rata-rata tardiness per trigger method, seperti Gambar
  2--5) di Bagian 5.1.

- Diskusikan apakah urutan ranking heuristik berubah ketika dievaluasi
  dengan metrik relatif/keparahan dibanding TLO absolut --- ini juga
  memperkuat jawaban untuk R1-Mayor #6 (composite score).

**Bagian manuskrip terdampak:** Bagian 3.4 (definisi metrik), Bagian 5.1
(Tabel 4 diperluas + figur baru).

**Klasifikasi usaha:** Sedang \| **Perlu simulasi/komputasi baru: Tidak,
jika data mentah per-order tersimpan (hanya reanalisis) --- verifikasi
ketersediaan data mentah di Mendeley Data terlebih dahulu**

R1-Mayor #6 --- Composite score memerlukan justifikasi tambahan,
analisis sensitivitas, dan koreksi inkonsistensi angka

**Inti komentar reviewer:** *Bobot 0.6/0.3/0.1 kurang dijustifikasi;
metode normalisasi (across all scenarios / within each scenario / within
each experimental group) tidak dijelaskan secara jelas; dan terdapat
inkonsistensi antara nilai composite score pada Tabel 4 dengan yang
dibahas di teks.*

**Mengapa penting:** Terverifikasi --- ini adalah temuan yang benar
secara faktual. Tabel 4 melaporkan mean composite score MPBH = 0.864
(std 0.093), sementara teks Bagian 5.1 menyatakan \'MPBH ranked first
(0.924)\', dan bahkan urutan peringkat berbeda (teks: MaxCart 0.790 \>
FTWB 0.752; Tabel 4: MaxCart 0.619 \< FTWB 0.725). Ini harus diperbaiki
sebelum publikasi karena kredibilitas seluruh Bagian 5.1 bergantung pada
angka yang konsisten.

**Rencana tindakan revisi:**

- AUDIT NUMERIK WAJIB: telusuri ulang pipeline penghitungan composite
  score dari data mentah untuk menentukan set angka mana yang benar
  (Tabel 4 atau narasi teks), lalu perbaiki SATU set angka yang
  konsisten di kedua tempat. Kemungkinan penyebab: teks menggunakan
  normalisasi/agregasi per-skenario lalu dirata-rata ulang, sedangkan
  Tabel 4 menggunakan agregasi langsung dari seluruh 207.360 run --- ini
  harus dipastikan dan didokumentasikan.

- Jelaskan secara eksplisit di Bagian 3.4 pada persamaan (5)-(8): apakah
  min/max diambil across all 6.912 skenario sekaligus (global), atau
  dihitung ulang per skenario individual lalu dirata-ratakan
  (within-scenario). Pilih satu metodologi, jelaskan alasannya, dan
  pastikan konsisten dengan cara Tabel 4 dihitung.

- Tambahkan analisis sensitivitas composite score dengan minimal 2--3
  skema bobot alternatif (misalnya bobot setara 0.33/0.33/0.33; skema
  berorientasi throughput 0.3/0.6/0.1; skema berorientasi utilisasi
  0.3/0.1/0.6) dan laporkan apakah ranking MPBH sebagai metode terbaik
  tetap stabil di seluruh skema (robustness check).

- Sajikan hasil sensitivitas dalam tabel ringkas baru (mis. \'Tabel 4b:
  Peringkat heuristik di bawah skema bobot alternatif\') di Bagian 5.1
  atau lampiran.

**Bagian manuskrip terdampak:** Bagian 3.4 (Persamaan 5--8), Bagian 5.1
(Tabel 4, teks naratif, dan tabel sensitivitas baru).

**Klasifikasi usaha:** Sedang, tetapi WAJIB dan mendesak (masalah
integritas data) \| **Perlu simulasi/komputasi baru: Tidak ---
reanalisis/perhitungan ulang dari data yang sudah ada**

R1-Mayor #7 --- Kontribusi teoretis terhadap Time-Based Competition
(TBC) perlu dibingkai ulang secara lebih hati-hati

**Inti komentar reviewer:** *TBC saat ini lebih berfungsi sebagai latar
belakang motivasi daripada fondasi teoretis dari mana
heuristik-heuristik itu diturunkan. Reviewer mengusulkan kalimat:
\'Using a time-based competition perspective, this study identifies
batch initiation timing as a micro-operational mechanism through which
warehouse responsiveness can be improved in same-day delivery
environments.\'*

**Mengapa penting:** Klaim \'extending TBC theory\' yang berulang
(Abstrak, kontribusi 1, Bagian 2.1, Diskusi 6.2) adalah klaim teoretis
yang kuat namun heuristik-heuristik yang diusulkan sebenarnya diturunkan
dari pertimbangan operasional (urgency, resource availability), bukan
diturunkan secara formal dari proposisi TBC. Membingkai ulang klaim ini
membuat kontribusi lebih defensif dan akurat.

**Rencana tindakan revisi:**

- Ganti semua frasa \'extending Time-Based Competition (TBC) theory to
  warehouse micro-operations\' dengan variasi kalimat yang disarankan
  reviewer (perspektif, bukan ekstensi teori formal) di: Abstrak,
  kontribusi pertama pada Bagian 1, Bagian 2.1 (penutup), dan Bagian
  6.2.

- Tinjau ulang penggunaan TBC di seluruh naskah untuk memastikan
  konsistensi framing baru ini --- TBC digunakan sebagai
  LENSA/PERSPEKTIF motivasi, bukan sebagai kerangka teori yang diuji
  atau diperluas secara formal.

- Pertimbangkan menambahkan satu-dua kalimat di Bagian 2.1 yang
  menjelaskan secara eksplisit apa yang membedakan \'menerapkan
  perspektif TBC\' dari \'memperluas teori TBC secara formal\', agar
  transisi framing tidak terkesan hanya kosmetik.

**Bagian manuskrip terdampak:** Abstrak, Bagian 1, Bagian 2.1, Bagian
6.2.

**Klasifikasi usaha:** Kecil--Sedang \| **Perlu simulasi/komputasi baru:
Tidak**

R1-Mayor #10 --- Implikasi manajerial perlu lebih spesifik dan
actionable

**Inti komentar reviewer:** *Implikasi manajerial saat ini berfokus pada
keunggulan umum dan implementability MPBH. Reviewer meminta panduan yang
lebih konkret: pada tingkat kedatangan order berapa MPBH paling
bermanfaat? Kapan aturan sederhana (FTWB/VTWB) sudah cukup? Bagaimana
mengkalibrasi ambang urgensi β? Bagaimana ketersediaan picker
memengaruhi pilihan aturan pemicu? Bagaimana trade-off antara TLO,
throughput, dan utilisasi picker sebaiknya dipertimbangkan manajer?*

**Mengapa penting:** Catatan ini tumpang tindih dengan R2-Mayor #4
(lihat Bagian B) --- keduanya dapat dijawab dalam satu subbagian Diskusi
yang diperluas dan sebuah tabel/diagram panduan keputusan.

**Rencana tindakan revisi:**

- Bangun \'tabel/panduan keputusan\' baru di Bagian 6.2 yang memetakan
  kombinasi (tingkat kedatangan λ, jumlah picker, prioritas bisnis) →
  heuristik yang direkomendasikan, memanfaatkan data yang SUDAH ADA di
  Tabel 6 dan Gambar 14 (tidak perlu run baru).

- Jawab secara eksplisit lima pertanyaan yang diajukan reviewer satu per
  satu sebagai sub-poin di Bagian 6.2, dengan merujuk ke bukti
  kuantitatif spesifik (misalnya, dari Gambar 6/7/14, performa heuristik
  konvergen pada λ rendah sehingga FTWB/VTWB memadai; pada λ tinggi dan
  picker terbatas, MPBH menunjukkan keunggulan margin terbesar).

- Untuk kalibrasi β (ambang urgensi, saat ini tetap = 2): tambahkan
  analisis sensitivitas singkat β ∈ {1, 2, 3, 4} pada subset skenario
  representatif (dapat digabung dengan eksperimen ablasi R1-Mayor #1
  agar efisien) dan diskusikan trade-off ukuran batch vs. responsivitas.

- Sertakan diagram alur sederhana (flowchart) \'Panduan Pemilihan
  Trigger Method\' sebagai figur baru untuk memvisualisasikan panduan
  ini bagi pembaca praktisi.

**Bagian manuskrip terdampak:** Bagian 6.2 (perluasan signifikan, tabel
dan figur baru).

**Klasifikasi usaha:** Sedang \| **Perlu simulasi/komputasi baru:
Sebagian --- sensitivitas β idealnya memerlukan run tambahan kecil
(dapat digabung dengan R1-Mayor #1); sisanya sintesis dari data yang
ada**

C.2 Reviewer 1 --- Komentar Minor

R1-Minor #1 --- Standardisasi terminologi (total late orders / late
orders / TLO)

**Inti komentar reviewer:** *Istilah yang merujuk pada metrik yang sama
digunakan secara bergantian dan tidak konsisten di seluruh naskah.*

**Mengapa penting:** Konsistensi istilah adalah persyaratan dasar
kejelasan ilmiah dan mudah diperbaiki, namun sering diabaikan pada draf
yang ditulis bertahap.

**Rencana tindakan revisi:**

- Definisikan istilah lengkap \'Total Late Orders (TLO)\' pada
  kemunculan pertama (Bagian 3, Tabel 3/Persamaan 2), lalu gunakan
  singkatan \'TLO\' secara konsisten pada seluruh kemunculan berikutnya,
  termasuk pada judul tabel, judul gambar, dan teks Bagian 5--6.

- Lakukan pencarian global (\'find\') untuk seluruh variasi --- \'total
  late orders\', \'late orders\', \'TLO\' --- dan seragamkan sesuai
  aturan di atas, termasuk pada judul Gambar 2, 6, 7, 9--14 dan Tabel
  4--6.

**Bagian manuskrip terdampak:** Seluruh naskah (global find-replace yang
cermat).

**Klasifikasi usaha:** Kecil \| **Perlu simulasi/komputasi baru: Tidak**

R1-Minor #2 --- Nama \'Simplified Neighbourhood-based Heuristic (SNH)\'
dinilai kurang tepat

**Inti komentar reviewer:** *SNH tampak lebih dekat dengan
priority-rule-based heuristic dibanding true neighbourhood search.
Reviewer meminta penamaan ulang atau penjelasan yang lebih baik tentang
kaitannya dengan neighbourhood search.*

**Mengapa penting:**

**Rencana tindakan revisi:**

- Opsi A (direkomendasikan, perubahan minimal): pertahankan nama, tetapi
  tambahkan 1--2 kalimat klarifikasi eksplisit di awal Bagian 4.4 yang
  menjelaskan bahwa SNH TERINSPIRASI oleh konsep neighbourhood search
  (evaluasi beberapa \'neighbourhood\'/daftar prioritas alternatif)
  namun diimplementasikan sebagai logika fallback berbasis aturan tetap
  (rule-based), bukan pencarian iteratif sejati --- sebagaimana sudah
  disinggung sekilas di paragraf penutup Bagian 4.4, perlu dipertegas di
  awal bukan di akhir.

- Opsi B (jika tim penulis lebih memilih): ganti nama menjadi
  \'Simplified Priority-List Heuristic (SPLH)\' atau \'Structured
  Priority-Fallback Heuristic (SPFH)\' dan perbarui SEMUA kemunculan
  (teks, Tabel 4--6, Gambar 2--5, 7, 9--14, referensi ke SNH di Diskusi)
  secara konsisten.

**Bagian manuskrip terdampak:** Bagian 4.4, dan jika Opsi B dipilih:
seluruh naskah (Tabel & Gambar).

**Klasifikasi usaha:** Kecil \| **Perlu simulasi/komputasi baru: Tidak**

R1-Minor #3 --- Perlu pseudocode yang lebih rinci untuk seluruh
heuristik demi reproduktifitas

**Inti komentar reviewer:** *Saat ini deskripsi heuristik hanya berupa
\'Decision Rule\' satu baris dan narasi prosa; reviewer meminta
pseudocode formal.*

**Mengapa penting:**

**Rencana tindakan revisi:**

- Tambahkan blok algoritma/pseudocode terformat (mis. gaya
  algorithm2e/algorithmic) untuk kedelapan metode: FTWB, VTWB,
  MaxPicker, MaxCart, UrgentPicker, UrgentCart, SNH, dan MPBH, sebagai
  Lampiran (Appendix A) yang dirujuk dari Bagian 4.1--4.4.

- Untuk SNH dan MPBH, pastikan pseudocode mencerminkan persis
  langkah-langkah bernomor yang sudah dideskripsikan dalam teks (mis.
  langkah 1--7 MPBH), termasuk kondisi loop, kriteria terminasi, dan
  langkah \'feasibility restoration\'.

- Sertakan kompleksitas Big-O pada setiap blok pseudocode sebagai
  komentar, konsisten dengan yang sudah disebutkan di teks (O(1), O(n),
  O(n log n)).

**Bagian manuskrip terdampak:** Bagian 4 (rujukan ke lampiran baru),
Lampiran A baru.

**Klasifikasi usaha:** Sedang \| **Perlu simulasi/komputasi baru:
Tidak**

R1-Minor #4 --- Detail implementasi simulasi (warm-up, random seed,
desain replikasi) perlu diperluas

**Inti komentar reviewer:** *Reviewer meminta detail lebih lanjut
mengenai periode warm-up, implementasi metode Welch, kontrol random
seed, dan desain replikasi.*

**Mengapa penting:**

**Rencana tindakan revisi:**

- Perluas Bagian 3.3: jelaskan secara rinci prosedur metode Welch yang
  digunakan (jumlah replikasi awal untuk deteksi warm-up, kriteria
  penentuan panjang warm-up, dan panjang warm-up final yang digunakan).

- Jelaskan skema random seed: apakah setiap skenario x replikasi
  menggunakan seed independen dan dapat direproduksi (mis. seed =
  f(scenario_id, replication_id)), dan apakah digunakan teknik variance
  reduction (mis. common random numbers) untuk perbandingan
  antar-heuristik dalam skenario yang sama.

- Jelaskan mengapa dipilih 30 replikasi per skenario (power/precision
  analysis, atau konvensi standar) dan sertakan estimasi interval
  kepercayaan/standard error pada metrik utama di Tabel 4 jika belum
  ada.

**Bagian manuskrip terdampak:** Bagian 3.3 (perluasan).

**Klasifikasi usaha:** Kecil--Sedang (dokumentasi prosedur yang sudah
dilakukan) \| **Perlu simulasi/komputasi baru: Tidak, jika prosedur
sudah dijalankan dan hanya perlu didokumentasikan; verifikasi
catatan/log eksperimen asli.**

R1-Minor #5 --- Konflik logika UrgentCart seharusnya diantisipasi di
bagian metode, bukan hanya dibahas post-hoc di hasil

**Inti komentar reviewer:** *Kegagalan UrgentCart dijelaskan dengan baik
di Bagian 5.3, tetapi logika OR yang berpotensi konflik (urgency vs.
cart capacity) semestinya sudah diantisipasi saat heuristik ini
dideskripsikan pertama kali di Bagian 4.3.*

**Mengapa penting:**

**Rencana tindakan revisi:**

- Tambahkan catatan singkat (1--2 kalimat) segera setelah deskripsi
  decision rule UrgentCart pada Bagian 4.3 yang secara proaktif
  memperingatkan bahwa kombinasi OR antara ambang urgency dan ambang
  kapasitas berpotensi menghasilkan trigger yang terlalu sensitif
  (banyak batch kecil) ATAU terlalu lambat merespons urgensi (menahan
  order demi cart penuh), tergantung kondisi mana yang lebih sering
  terpenuhi lebih dulu --- sebagai hipotesis yang akan diuji pada Bagian
  5.

- Tambahkan kalimat penghubung eksplisit di Bagian 5.3 yang merujuk
  kembali ke antisipasi ini (\'sebagaimana diantisipasi pada Bagian 4.3,
  ...\').

**Bagian manuskrip terdampak:** Bagian 4.3 (deskripsi UrgentCart),
Bagian 5.3 (rujukan silang).

**Klasifikasi usaha:** Kecil \| **Perlu simulasi/komputasi baru: Tidak**

R1-Minor #6 --- Kajian pustaka perlu diperkuat dengan pembahasan dynamic
batching, real-time dispatching rules, dan integrated order fulfilment
systems

**Inti komentar reviewer:** *Reviewer meminta cakupan literatur yang
lebih luas pada tiga tema tersebut.*

**Mengapa penting:**

**Rencana tindakan revisi:**

- Lihat Bagian D dokumen ini untuk daftar kandidat referensi terbaru
  (2023--2025) yang relevan pada ketiga tema tersebut, termasuk tinjauan
  taksonomi order batching terbaru dan studi tentang
  reoptimisasi/dispatching real-time.

- Tambahkan 1--2 paragraf baru di Bagian 2.2 dan/atau 2.3 yang secara
  eksplisit membahas: (a) perkembangan terbaru pada dynamic/online order
  batching, (b) real-time dispatching rules pada sistem
  produksi/logistik yang analog (memperkuat paragraf yang sudah
  menyinggung Lian et al. 2022 dan Castro et al. 2024), dan (c)
  integrated order fulfilment systems yang menggabungkan warehouse-level
  decisions dengan last-mile delivery.

**Bagian manuskrip terdampak:** Bagian 2.2, Bagian 2.3, Daftar Pustaka.

**Klasifikasi usaha:** Sedang \| **Perlu simulasi/komputasi baru: Tidak
(butuh pencarian & pembacaan literatur, bukan eksperimen)**

C.3 Reviewer 2 --- Komentar Mayor

R2-Mayor #1 --- Daftar pustaka dinilai relatif lama; diperlukan tinjauan
literatur yang diperbarui

**Inti komentar reviewer:** *Sebagian besar referensi relatif lama;
diperlukan pembaruan literatur review.*

**Mengapa penting:**

**Rencana tindakan revisi:**

- Integrasikan referensi kandidat pada Bagian D dokumen ini (terutama
  publikasi 2023--2026, termasuk artikel EJIE terbaru) ke Bagian 2
  (Kajian Pustaka) sesuai tema masing-masing.

- Prioritaskan penambahan sitasi dari EJIE sendiri (di luar tiga yang
  sudah ada: Babaei et al. 2023, Castro et al. 2024, Dantas et al. 2024,
  Zhang et al. 2025, Wang & Chen 2024, Lian et al. 2022) untuk
  menunjukkan keterlibatan dengan komunitas jurnal, sesuai instruksi
  editor.

- Pastikan setiap referensi baru benar-benar disitasi dalam teks (bukan
  hanya ditambahkan di daftar pustaka) agar konsisten dengan pedoman
  penulisan ilmiah dan permintaan editor.

**Bagian manuskrip terdampak:** Bagian 2 (seluruh subbagian), Daftar
Pustaka.

**Klasifikasi usaha:** Sedang \| **Perlu simulasi/komputasi baru:
Tidak**

R2-Mayor #2 --- Presentasi Tabel 3 (notasi) perlu diperbaiki: pisahkan
variabel dari parameter; perjelas simbol yang ambigu

**Inti komentar reviewer:** *Reviewer secara spesifik menyebut
ProcessingTime(o) dan TotalBatchTime sebagai definisi yang tidak
jelas/tidak lengkap, dan meminta reorganisasi tabel dengan memisahkan
variabel dari parameter.*

**Mengapa penting:**

**Rencana tindakan revisi:**

- Bagi Tabel 3 menjadi dua tabel atau dua blok bersekat dengan header
  jelas: \'Tabel 3a -- Variabel Keadaan Sistem (dinamis, berubah seiring
  waktu t)\' berisi S_t, O_t, B_t, P_t, t, N, dan seterusnya; dan
  \'Tabel 3b -- Parameter Model (tetap/ditentukan di muka)\' berisi C,
  F, V, β, SetupTime, BasePickTime, TotalPickers, dan seterusnya.
  Alternatif: tambahkan kolom baru \'Tipe\' (Variabel/Parameter) pada
  Tabel 3 yang sudah ada.

- Perjelas definisi ProcessingTime(o): tegaskan secara eksplisit di
  tabel bahwa ini adalah estimasi WAKTU PENYELESAIAN SATU ORDER (bukan
  satu batch), dan rumus lengkapnya ProcessingTime(o) = BasePickTime ×
  \|Items(o)\| + TravelTime(Items(o)) dicantumkan langsung pada kolom
  definisi, bukan hanya dijelaskan di teks Bagian 3.2.

- Perjelas definisi TotalBatchTime: tegaskan bahwa dalam rumus
  TotalBatchTime = ProcessingTime(o) + SetupTime pada Bagian 3.2, notasi
  ini merujuk pada kasus KHUSUS batch berukuran satu (worst-case
  single-order batch) yang dipakai untuk uji urgensi --- bukan formula
  umum untuk batch berukuran-n. Pertimbangkan memberi notasi berbeda
  (mis. TotalBatchTime₁ atau TotalBatchTime(single)) agar tidak
  membingungkan pembaca yang mengira ini formula umum untuk batch besar.

- Tambahkan kolom \'Satuan\' (unit: detik, order/menit, item, dsb.) pada
  Tabel 3 yang telah direstrukturisasi untuk memperjelas dimensi setiap
  besaran.

**Bagian manuskrip terdampak:** Tabel 3 (Bagian 3), Bagian 3.2
(penjelasan naratif terkait).

**Klasifikasi usaha:** Sedang \| **Perlu simulasi/komputasi baru:
Tidak**

R2-Mayor #3 --- Perlu pelaporan waktu komputasi aktual dan diskusi
skalabilitas

**Inti komentar reviewer:** *Karena masalah ini bersifat dinamis,
efisiensi komputasi kritis untuk implementasi praktis; penulis diminta
melaporkan hasil waktu komputasi dan mendiskusikan skalabilitas metode
yang diusulkan.*

**Mengapa penting:** Saat ini kompleksitas hanya dilaporkan secara
teoretis (O(1), O(n), O(n log n)) tanpa bukti empiris waktu eksekusi
aktual, sehingga klaim \'computationally efficient\' dan
\'implementable\' pada Abstrak dan Bagian 6.2 belum didukung data.

**Rencana tindakan revisi:**

- Instrumentasi kode simulasi untuk mencatat wall-clock time (atau CPU
  time) yang dibutuhkan SETIAP KALI evaluasi keputusan trigger
  dijalankan, untuk seluruh 8 metode, terutama pada ukuran order pool
  \|O_t\| yang besar (kondisi λ tinggi).

- Jalankan eksperimen skalabilitas terkontrol: ukur rata-rata waktu
  keputusan (dalam milidetik) sebagai fungsi dari ukuran order pool n
  (mis. n = 10, 50, 100, 500, 1000, 5000) untuk masing-masing metode,
  dan plot hasilnya (waktu vs n) untuk memvalidasi secara empiris
  kompleksitas O(1)/O(n)/O(n log n) yang diklaim.

- Tambahkan subbagian baru \'5.x Kinerja Komputasi dan Skalabilitas\'
  yang melaporkan tabel/figur waktu komputasi rata-rata per metode, dan
  diskusikan implikasinya untuk penerapan real-time (mis. apakah semua
  metode, termasuk MPBH, tetap berada jauh di bawah batas waktu
  keputusan operasional yang wajar, misalnya sub-detik, bahkan pada
  order pool sangat besar).

- Rujuk hasil ini secara eksplisit di Bagian 6.2 saat mengklaim \'low
  computational overhead\' agar klaim tersebut berbasis bukti, bukan
  hanya kompleksitas Big-O teoretis.

**Bagian manuskrip terdampak:** Bagian 3.3 (instrumentasi), Bagian 5
(subbagian baru), Bagian 6.2 (rujukan hasil).

**Klasifikasi usaha:** Sedang--Besar \| **Perlu simulasi/komputasi baru:
Ya --- memerlukan instrumentasi & eksperimen skalabilitas khusus (waktu
eksekusi), berbeda dari 207.360 run performa yang sudah ada**

R2-Mayor #4 --- Kontribusi teoretis dinilai terbatas; perlu panduan
praktis pemilihan heuristik pada skenario operasional berbeda

**Inti komentar reviewer:** *Untuk memperkuat kontribusi, penulis
disarankan memberikan panduan praktis mengenai pemilihan heuristik yang
sesuai di bawah skenario operasional yang berbeda.*

**Mengapa penting:** Butir ini pada dasarnya SAMA dengan R1-Mayor #10
(lihat Bagian B) dan dapat dijawab dalam satu paket revisi yang sama.

**Rencana tindakan revisi:**

- Gunakan tabel/panduan keputusan dan flowchart yang dibangun untuk
  R1-Mayor #10 sebagai jawaban langsung untuk butir ini juga --- tidak
  perlu pekerjaan terpisah.

- Pastikan narasi di Bagian 6.2 secara eksplisit menyebutkan bahwa
  panduan ini menjawab kebutuhan akan \'practical guidelines regarding
  the selection of an appropriate heuristic algorithm under different
  operational scenarios\' agar reviewer dapat langsung memverifikasi
  keterkaitannya.

**Bagian manuskrip terdampak:** Bagian 6.2 (sama dengan R1-Mayor #10).

**Klasifikasi usaha:** Tidak ada tambahan (digabung dengan R1-Mayor #10)
\| **Perlu simulasi/komputasi baru: Tidak (lihat R1-Mayor #10)**

D. Kandidat Referensi Baru yang Direkomendasikan

+----------------------------------------------------------------------+
| **Catatan penting**                                                  |
|                                                                      |
| Daftar berikut adalah hasil penelusuran literatur terkini            |
| (2023--2026) sebagai titik awal untuk menjawab R1-Minor #6 dan       |
| R2-Mayor #1. SEBELUM disisipkan ke naskah, tim penulis WAJIB         |
| memverifikasi sendiri detail bibliografi lengkap (volume, nomor,     |
| halaman, DOI) langsung dari basis data jurnal, karena beberapa entri |
| di bawah ini bersumber dari cuplikan pencarian yang mungkin belum    |
| lengkap.                                                             |
+----------------------------------------------------------------------+

  -------------------- ------------------ ------------
  **Referensi          **Tema yang        **Rujuk pada
  (verifikasi detail   didukung**         butir**
  lengkap)**                              

  Pardo, E.G.,         Taksonomi &        R1-Minor #6,
  Gil-Borrás, S.,      tinjauan literatur R2-Mayor #1
  Alonso-Ayuso, A. and order batching     
  Duarte, A. (2024)    terkini; ditulis   
  \'Order batching     oleh kelompok yang 
  problems: taxonomy   sama dengan        
  and literature       Gil-Borrás et al.  
  review\', European   (2020, 2021) yang  
  Journal of           sudah dirujuk      
  Operational                             
  Research, Vol. 313,                     
  No. 1, pp. 1--24.                       

  Boysen, N. and de    Tinjauan besar     R1-Minor #6,
  Koster, R. (2025)    riset warehousing  R2-Mayor #1
  \'50 years of        operations         
  warehousing research research, konteks  
  --- an operations    historis & arah    
  research             masa depan         
  perspective\',                          
  European Journal of                     
  Operational                             
  Research, Vol. 320,                     
  No. 3, pp. 449--464.                    

  Lorenz, C., Otto, A. Online/dynamic     R1-Minor #6,
  and Gendreau, M.     order              R2-Mayor #1,
  (2025) \'Picking     batching-routing   Bagian
  operations in        dengan             2.2--2.3
  warehouses with      reoptimisasi       
  dynamically arriving real-time          
  orders: how good is                     
  reoptimization?\',                      
  Networks, Vol. 86,                      
  No. 2, pp. 157--173.                    

  Vanheusden, S., van  Tinjauan faktor    R1-Minor #6,
  Gils, T., Ramaekers, praktis            R2-Mayor #1
  K., Cornelissens, T. perencanaan order  
  and Caris, A. (2023) picking (pelengkap 
  \'Practical factors  Vanheusden et al.  
  in order picking     2022 yang sudah    
  planning:            dirujuk)           
  state-of-the-art                        
  classification and                      
  review\',                               
  International                           
  Journal of                              
  Production Research,                    
  Vol. 61, No. 6, pp.                     
  2032--2056.                             

  Prnaver, K. and      Order batching     Bagian
  Pisinger, D. (2025)  dengan time window 2.2--2.3
  \'Warehouse picking: (release time &    
  order batching and   due date) ---      
  routing with time    sangat relevan     
  windows\', working   dengan             
  paper/SSRN           urgency-aware      
  (verifikasi status   batching           
  publikasi terbaru).                     

  Smaili, F. et al.    Studi simulasi     Bagian 2.3,
  (2025)               skala besar        R1-Minor #4
  \'Simulation-based   terhadap banyak    (desain
  study of dispatching dispatching rule   eksperimen
  rules in a           di bawah kondisi   simulasi)
  real-world job shop  dinamis --- analog 
  scheduling           metodologis dengan 
  problem\', Journal   desain eksperimen  
  of Simulation, Vol.  paper ini          
  20, No. 3, pp.                          
  277--292.                               
  -------------------- ------------------ ------------

Selain daftar di atas, lakukan pencarian tambahan yang ditargetkan
langsung di situs Inderscience/EJIE
(https://www.inderscienceonline.com/journal/ejie) untuk edisi Vol.
19--21 (2025--2026) guna menemukan artikel-artikel EJIE terbaru yang
secara tematik dekat dengan scheduling, dispatching rules, dan simulasi
warehouse/logistik, karena editor secara eksplisit meminta keterlibatan
dengan literatur EJIE terkini.

E. Kerangka Surat "Response to Reviewers"

Sesuai instruksi editor, dokumen tanggapan ini harus disisipkan di AWAL
manuskrip yang direvisi (sebelum Abstrak atau sebagai file terpisah,
tergantung format yang diminta sistem submisi Inderscience), dan setiap
tanggapan harus merujuk NOMOR HALAMAN spesifik pada manuskrip revisi
serta idealnya menyorot (highlight) teks yang diubah. Kerangka berikut
memuat placeholder yang harus diisi SETELAH revisi aktual pada naskah
selesai dikerjakan, karena nomor halaman baru hanya dapat dipastikan
setelah teks final disusun ulang.

+----------------------------------------------------------------------+
| **Format setiap butir tanggapan (wajib diikuti untuk seluruh 17      |
| butir)**                                                             |
|                                                                      |
| 1\) Kutip/parafrasekan komentar reviewer. 2) Jelaskan tindakan yang  |
| diambil. 3) Sebutkan lokasi perubahan: "Lihat halaman \[X\],         |
| paragraf \[Y\]" atau "Lihat Bagian \[Z\] yang direvisi (teks disorot |
| kuning pada versi track-changes/highlighted)." 4) Jika tidak ada     |
| perubahan pada naskah untuk suatu poin (mis. karena penulis          |
| memberikan justifikasi berbeda), jelaskan alasan secara eksplisit    |
| dan sopan.                                                           |
+----------------------------------------------------------------------+

**Struktur dokumen tanggapan yang disarankan:**

- Paragraf pembuka: ucapan terima kasih kepada editor dan kedua
  reviewer; ringkasan singkat perubahan utama (studi ablasi baru,
  kalibrasi benchmark, formalisasi MDP, metrik tambahan, koreksi Tabel
  4, dsb.).

- Bagian \'Response to Reviewer 1\': jawab berurutan komentar mayor
  #1--#7, #10, lalu komentar minor #1--#6, masing-masing mengikuti
  format kotak di atas.

- Bagian \'Response to Reviewer 2\': jawab berurutan komentar mayor
  #1--#4, mengikuti format yang sama.

- Untuk butir yang tumpang tindih (R1-Mayor #10 & R2-Mayor #4; R1-Minor
  #6 & R2-Mayor #1), boleh menjawab secara ringkas pada butir kedua dan
  merujuk silang ke jawaban lengkap pada butir pertama agar tidak
  terjadi duplikasi teks yang janggal.

- Paragraf penutup: pernyataan bahwa daftar pustaka telah diperbarui dan
  seluruh perubahan telah disorot pada naskah revisi.

F. Checklist Kepatuhan Editorial & Rencana Waktu (30 Hari)

F.1 Checklist Kepatuhan Editorial

- Surat tanggapan rinci ("response to reviewers") disisipkan di AWAL
  manuskrip revisi, menjawab seluruh 17 butir secara sistematis (lihat
  Bagian E).

- Setiap tanggapan merujuk nomor HALAMAN spesifik pada naskah revisi.

- Teks yang direvisi disorot (highlight) pada versi naskah yang
  diunggah, sesuai anjuran editor.

- Daftar pustaka diperbarui dengan artikel-artikel relevan terbaru,
  termasuk dari EJIE sendiri (lihat Bagian D).

- Seluruh angka pada Tabel 4 dan teks Bagian 5.1 telah diaudit ulang dan
  konsisten (R1-Mayor #6).

- File diunggah melalui akun submisi di
  https://indersciencesubmissions.com/ pada bagian \'Track progress of
  your article and submit revisions\', menggunakan file asli yang
  diunduh dari sistem sebagai basis revisi.

- Konfirmasi bahwa TIDAK membalas email keputusan secara langsung
  (fungsi \'Reply\' tidak akan diterima oleh editor).

F.2 Rencana Waktu (30 Hari sejak 10 Agustus 2026)

  ------------ ------------- ---------------
  **Minggu**   **Periode**   **Fokus utama**

  Minggu 1     10--17        Audit numerik
               Agustus 2026  Tabel
                             4/composite
                             score (R1#6);
                             mulai desain
                             eksperimen
                             ablasi (R1#1)
                             dan kalibrasi
                             benchmark
                             (R1#2); mulai
                             pencarian
                             literatur
                             (R1-Minor#6,
                             R2#1).

  Minggu 2     18--24        Jalankan
               Agustus 2026  eksperimen
                             ablasi,
                             kalibrasi
                             benchmark, dan
                             instrumentasi
                             waktu komputasi
                             (R2#3); hitung
                             ulang metrik
                             tambahan dari
                             data mentah
                             (R1#5).

  Minggu 3     25--31        Analisis hasil
               Agustus 2026  eksperimen
                             baru; tulis
                             ulang Proposisi
                             4 (R1#4)
                             berdasarkan
                             hasil ablasi;
                             revisi Tabel 3
                             (R2#2);
                             tambahkan
                             formalisasi MDP
                             (R1#3); tulis
                             subbagian baru
                             (ablasi,
                             skalabilitas,
                             sensitivitas
                             bobot).

  Minggu 4     1--7          Selesaikan
               September     revisi teks
               2026          tersisa
                             (framing TBC
                             R1#7, implikasi
                             manajerial
                             R1#10/R2#4,
                             terminologi,
                             SNH,
                             pseudocode,
                             warm-up/seed,
                             UrgentCart);
                             susun surat
                             tanggapan
                             lengkap; sorot
                             semua
                             perubahan;
                             proofread
                             akhir.

  Buffer       8--9          Unggah ke
               September     sistem submisi
               2026          Inderscience
                             sebelum tenggat
                             ≈ 9 September
                             2026.
  ------------ ------------- ---------------

+----------------------------------------------------------------------+
| **Rekomendasi prioritas jika waktu terbatas**                        |
|                                                                      |
| Jika 30 hari tidak cukup untuk seluruh eksperimen baru, prioritaskan |
| dalam urutan ini: (1) R1-Mayor #6 (audit/koreksi angka --- wajib,    |
| isu integritas data), (2) R1-Mayor #1 (ablasi timing vs komposisi    |
| --- menentukan validitas Proposisi 1 & 4), (3) R1-Mayor #4           |
| (penulisan ulang klaim, bergantung pada #1), (4) R1-Mayor #2         |
| (kalibrasi benchmark), (5) R2-Mayor #3 (waktu komputasi). Semua      |
| butir revisi teks murni (tanpa eksperimen baru) dapat dikerjakan     |
| paralel oleh anggota tim yang tidak terlibat langsung dalam          |
| menjalankan simulasi. Jika opsi MIP pada R1-Mayor #3 tidak sempat    |
| dikerjakan, formalisasi MDP saja (tanpa MIP) sudah menjawab inti     |
| komentar reviewer secara memadai; nyatakan MIP sebagai agenda riset  |
| lanjutan.                                                            |
+----------------------------------------------------------------------+
