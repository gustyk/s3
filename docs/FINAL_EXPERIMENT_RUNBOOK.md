# Runbook eksperimen final Q1

## Cakupan yang dibekukan

Batch utama adalah desain faktorial penuh `6 × 8 × 12 × 2 × 3 × 2 × 30 = 207.360` run. Eksperimen reviewer terdiri dari:

- dekomposisi timing × composition: `24 konteks × 6 treatment × 30 = 4.320` run;
- kalibrasi F/V: `48 konteks × 17 kandidat × 30 = 24.480` run;
- sensitivitas β: `48 konteks × 16 method–β × 30 = 23.040` run;
- benchmark biaya keputusan: delapan metode, 30 pengulangan per ukuran pool.

Eksperimen reviewer sengaja tidak menggandakan raw order. Bukti per-order lengkap untuk seluruh faktor dan metode disimpan oleh batch utama sebagai `orders.csv.gz`.

## 1. Bekukan source dan environment

Jalankan dari `D:\Apps\S3` pada drive lokal NTFS. Pastikan komputer tersambung listrik, sleep/hibernation dinonaktifkan selama batch, dan output tidak berada di folder sinkronisasi cloud.

```powershell
python --version
python -m pip install -r requirements.lock
python -m ruff check src tests
python -m mypy src
python -m pytest -q
git status --short
```

Jalankan release smoke delapan metode sebelum commit/tag final; hasilnya harus memiliki delapan run dan audit `pass`:

```powershell
python -m src.experiment --config config/release_smoke.yaml --output-dir outputs/release-smoke-final --mode full --repetitions 1
python -m src.audit_results outputs/release-smoke-final/results.csv --report outputs/release-smoke-final/audit_report.json
```

Commit seluruh perubahan source/config yang akan dipakai, lalu buat tag immutable. Jangan mengubah `src/`, `config/`, `pyproject.toml`, atau `requirements.lock` setelah run dimulai.

```powershell
git status --short
git add -A
git diff --cached --stat
git commit -m "Freeze Q1 simulation model and final experiment workflow"
git tag q1-simulation-final-v1
git status --short
```

`git status --short` harus kosong. Simpan hash berikut dalam catatan eksperimen:

```powershell
git rev-parse HEAD
git describe --tags --exact-match
Get-FileHash requirements.lock -Algorithm SHA256
```

## 2. Jalankan preflight

Gunakan nama output permanen; jangan menggantinya ketika resume. Preflight utama memverifikasi 207.360 run, parameter kanonik, raw evidence, kompresi, config hash, kebersihan source, kompatibilitas checkpoint, dependency lock, dan ruang disk minimum 60 GiB.

```powershell
python -m src.preflight --config config/parameters.yaml --output-dir outputs/final-q1-v1/full-factorial --mode full --repetitions 30 --require-clean --minimum-free-gib 60 --report outputs/final-q1-v1/preflight/full-factorial.json
```

Lanjutkan hanya bila `status` adalah `pass`. Estimasi disk bersifat konservatif berbasis jumlah order ekspektasian; pertahankan ruang tambahan untuk analisis dan salinan backup.

## 3. Jalankan eksperimen reviewer

Perintah wrapper berikut dapat dijalankan ulang dengan aman menggunakan output root yang sama:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_final_experiments.ps1 -Stage reviewer -OutputRoot outputs/final-q1-v1
```

Urutannya adalah ablation, kalibrasi F/V, sensitivitas β, lalu benchmark waktu keputusan. Setiap sel yang telah memiliki manifest valid diaudit dan dilewati; sel parsial dilanjutkan dari checkpoint-nya.

## 4. Jalankan faktorial penuh

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_final_experiments.ps1 -Stage full -OutputRoot outputs/final-q1-v1
```

Runner mengacak urutan eksekusi secara deterministik untuk mengurangi bias drift mesin, tetapi `run_uuid`, seed CRN, dan urutan tersebut tetap dapat direproduksi dari config/manifest.

## 5. Memantau progres

Buka PowerShell kedua. Jangan membuka atau menyunting partial CSV/GZIP.

```powershell
$cp = Get-Content outputs/final-q1-v1/full-factorial/checkpoint.json -Raw | ConvertFrom-Json
$cp | Select-Object completed_runs,expected_runs,last_run_uuid,last_checkpoint_utc,estimated_remaining_simulation_wall_seconds
"{0:P2}" -f ($cp.completed_runs / $cp.expected_runs)
if ($cp.estimated_remaining_simulation_wall_seconds) { [TimeSpan]::FromSeconds($cp.estimated_remaining_simulation_wall_seconds) }
Get-PSDrive D | Select-Object Used,Free
```

Checkpoint ditulis atomik setelah setiap run dan berisi byte boundary yang sudah tersertifikasi untuk aggregate dan raw-order stream.

## 6. Jika proses terputus

1. Hentikan normal dengan `Ctrl+C` satu kali bila masih responsif. Untuk power loss/kill, jangan memperbaiki file secara manual.
2. Pastikan source/config dan nama output tidak berubah.
3. Jalankan ulang perintah tahap yang sama persis.
4. Runner memotong otomatis tail CSV/GZIP yang belum tersertifikasi checkpoint, melewati run/sel yang selesai, dan meneruskan run berikutnya.
5. Bila output final sudah selesai, perintah yang sama hanya mengaudit dan menggunakan kembali artifact tersebut; simulasi tidak dijalankan lagi.

Jangan menghapus `checkpoint.json`, `partial_results.csv`, atau `partial_orders.csv.gz`. Salin ketiganya bersama-sama jika migrasi drive benar-benar diperlukan. Config hash/source hash yang berbeda sengaja ditolak agar evidence tidak tercampur.

## 7. Audit dan post-processing

Tahap `full` otomatis menjalankan audit. Setelah audit `pass`, jalankan:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_final_experiments.ps1 -Stage postprocess -OutputRoot outputs/final-q1-v1
```

Output yang wajib ada:

- `full-factorial/results.csv`: seluruh metrik run-level paper dan reviewer;
- `full-factorial/orders.csv.gz`: record arrival/due, release, batch, picker, start/completion, wait, flow, tardiness/censoring setiap order;
- `full-factorial/manifest.json`: hash source/config/dependency dan checksum artifact;
- `full-factorial/audit_report.json`: harus `pass`;
- `full-factorial/analysis/`: tabel, model, CI, dan diagnostik paper;
- `full-factorial/additional-metrics/`: metrik on-time/tardiness yang censor-aware;
- `full-factorial/composite/`: satu normalisasi komposit kanonik dan sensitivity weights;
- `reviewer/`: ablation, F/V calibration, β sensitivity, dan benchmark komputasi.

Audit `orders.csv.gz` harus membaca seluruh stream dan karena itu dapat memerlukan waktu lama; jangan menyimpulkan macet hanya karena fase ini tidak mencetak progres.

## 8. Arsipkan tanpa mengubah artifact

```powershell
Get-FileHash outputs/final-q1-v1/full-factorial/results.csv -Algorithm SHA256
Get-FileHash outputs/final-q1-v1/full-factorial/orders.csv.gz -Algorithm SHA256
Get-FileHash outputs/final-q1-v1/full-factorial/manifest.json -Algorithm SHA256
```

Salin direktori `outputs/final-q1-v1` ke media backup, lalu verifikasi hash pada salinan. Jangan mengganti CSV secara manual; koreksi analisis harus dibuat sebagai artifact turunan baru dengan provenance yang jelas.
