# Design Lock — Kelompok 1 (Repair-Based, Budget-Aware GA)

Berkas ini **dikunci sebelum** eksperimen test dijalankan. Setiap perubahan setelah
tanggal kunci dicatat di bagian *Amendment log* dan dilaporkan sebagai analisis
tambahan, bukan sebagai evaluasi test baru (protokol anti-kebocoran brief).

Tanggal kunci: **2026-10-29** (WITA) — dibuat setelah pilot parameter selesai,
sebelum run test.

---

## 1. Pertanyaan riset

**RQ1 (utama).** Pada anggaran evaluasi yang sama, apakah GA dengan *repair*
kendala-hard menemukan jadwal feasible lebih sering dan/atau dengan pelanggaran
hard lebih rendah daripada GA standar tanpa repair?

**RQ2.** Berapa *biaya* repair dalam satuan evaluasi (porsi anggaran yang
terpakai untuk repair, jumlah generasi yang hilang) dan pada kondisi
ketersediaan dosen seperti apa biaya itu terbayar?

**RQ3.** Apakah manfaat repair bergantung pada intensitas repair (jumlah sesi
yang diperbaiki per offspring, jumlah kandidat yang diperiksa, dan ada/tidaknya
tukar-sesi)?

## 2. Hipotesis (dinyatakan sebelum melihat hasil test)

- **H1.** Pada instance dengan ketersediaan dosen ketat (pola C: 10% slot sisa),
  GA+repair menghasilkan pelanggaran hard lebih rendah daripada GA standar pada
  anggaran yang sama.
- **H2.** Pada instance longgar (pola A/B), keunggulan repair mengecil atau
  hilang, karena GA standar pun dapat mencapai feasible dan kedalaman pencarian
  (jumlah generasi) lebih menentukan kualitas soft.
- **H3.** Biaya repair terukur: porsi evaluasi untuk repair signifikan
  (> 25% anggaran) dan jumlah generasi GA+repair lebih sedikit daripada GA
  standar pada anggaran yang sama.
- **H4.** Efek repair monoton-tidak dalam intensitas: terlalu sedikit sesi
  diperbaiki per offspring meninggalkan pelanggaran; terlalu banyak menghabiskan
  anggaran sebelum populasi berevolusi.

Arah kontribusi = hipotesis yang diuji, **bukan** klaim kebaruan.

## 3. Domain & instance

Domain: *Curriculum-Based Course Timetabling* (CB-CTT, ITC2007 Track 2):
sesi kuliah → (ruang, slot); kendala hard: konflik dosen, konflik kelompok,
bentrok ruang, kapasitas ruang, slot terlarang; kendala soft: slot kosong di
antara jam kuliah kelompok pada hari yang sama (penalti P).

Instance **sintetis** (dibangun *feasible by construction*, lalu kendala
ketersediaan dipersempit sehingga tetap feasible):

| keluarga | n sesi | pola ketersediaan |
|---|---|---|
| syn30A/B/C | 30 | A longgar (60% slot sisa), B sedang (30%), C ketat (10%) |
| syn60A/B/C | 60 | idem |
| syn90A/B/C | 90 | idem |

Instance **benchmark publik**: ITC2007 CB-CTT `comp01 … comp12` (format `.ctt`,
mirror: repositori GitHub `Docheinstein/itc2007-cct`), tanpa modifikasi.

**Dev/pilot (boleh dilihat berulang):** `01_data/pilot/pilot45B.json`,
`01_data/pilot/pilot45C.json`, `01_data/benchmark/comp13.json`,
`01_data/benchmark/comp14.json`.

**Test (dibekukan; hanya dievaluasi sekali di akhir):** 9 instance sintetis
`syn30A..syn90C` + benchmark `comp01 … comp12`.

Jumlah unit test: **21 instance** × 3 metode utama × **20 seed** (metode stokastik, sesuai ketentuan brief).

## 4. Metode

1. **Greedy konstruktif deterministik** (baseline, tanpa tuning):
   most-constrained-first (ketersediaan dosen terketat lebih dulu), pilih
   pasangan (ruang, slot) dengan leksikografis (ΔH, ΔP, ruang, slot).
   Deterministik → satu run per instance; evaluasi sebenarnya (pasangan yang
   dinilai) dilaporkan, tidak dipotong anggaran.
2. **GA standar**: seleksi turnamen (k=3), crossover seragam per gen
   (pc = 0.8), mutasi per gen (pm dari pilot), elitisme 2, inisialisasi
   *greedy-seeded* (individu 0 = greedy deterministik, sisanya greedy acak).
3. **GA + repair**: identik dengan GA standar, ditambah operator repair yang
   dijalankan pada setiap offspring sebelum penilaian: sesi yang melanggar
   hard dipindahkan ke pasangan (ruang, slot) valid dengan tambahan penalti
   terkecil; bila tidak ada slot bebas, dicoba tukar-sesi (*ejection*).
   Parameter intensitas (jumlah sesi per offspring, kandidat per sesi, tukar)
   dipilih dari pilot.

Kedua varian GA memakai **konfigurasi sama** kecuali operator repair, sehingga
perbandingan terkendali.

## 5. Akuntansi anggaran evaluasi

**Satu evaluasi** = satu penilaian objektif atas satu kandidat:

- (a) penilaian lengkap satu jadwal (fitness individu GA; skor greedy), atau
- (b) satu kandidat perpindahan (ruang, slot) atau satu kandidat tukar-sesi
  yang diperiksa repair.

Semua penilaian yang dilakukan algoritma dibebankan: inisialisasi populasi,
repair, dan kandidat duplikat. Pembangunan indeks okupansi (array hitung) adalah
pembukuan, bukan penilaian objektif → tidak dibebankan; biayanya terlihat pada
runtime.

**Batas:** 10.000 evaluasi per run (nilai awal brief; dipakai tanpa perubahan
setelah pilot memastikan kedua varian GA memperoleh cukup generasi).
Metode stokastik berhenti saat `budget_used == 10.000` (atau batas keamanan
dinding 900 s). Greedy deterministik tidak dipotong (dilaporkan berapa
evaluasi sebenarnya yang ia pakai).

Runtime dilaporkan terpisah dari anggaran (detik dinding, satu core, hardware
dicatat pada README).

## 6. Metrik

**Primer**
- `best_H`: pelanggaran hard minimum yang ditemukan dalam anggaran (lebih kecil
  lebih baik; 0 = feasible).
- `feasible`: best_H == 0 (proporsi run feasible per instance).
- `evals_to_first_feasible`: evaluasi saat jadwal feasible pertama ditemukan
  (censored bila tidak pernah; dilaporkan sebagai "tidak tercapai").

**Sekunder**
- `best_P`: penalti soft pada solusi terbaik (leksikografis (H, P)).
- `runtime_s`, `generations`, `repair_probes`, `repair_sessions`,
  `repair_swaps`, `repair_failures`, `budget_limited`, porsi anggaran untuk
  repair = `repair_probes / evals`.
- Kurva konvergensi (best_H dan best_P terhadap evaluasi terpakai).

**Validasi**: setiap solusi terbaik divalidasi ulang oleh validator independen
(`model.validate`, implementasi terpisah dari scorer). Run dengan `validated_H`
≠ `best_H` atau `validated_P` ≠ `best_P` dinyatakan **gagal** dan dilaporkan
sebagai kegagalan, bukan dirata-ratakan sebagai sukses.

## 7. Desain statistik

- Unit analisis = **instance** (bukan seed). Untuk tiap instance, metode
  stokastik diwakili **median 20 seed**; perbandingan berpasangan dilakukan
  antar-metode pada instance yang sama.
- Uji primer RQ1: **Wilcoxon signed-rank** berpasangan (GA standar vs GA+repair)
  atas `best_H` per instance (n = 21 instance).
- Perbandingan tiga metode (greedy, GA standar, GA+repair): **Friedman** +
  post-hoc berpasangan dengan koreksi **Holm**.
- Effect size: **Cliff's delta** (berpasangan) dilaporkan bersama p-value.
- Analisis per keluarga instance (pola A/B/C; ukuran 30/60/90; sintetis vs
  benchmark) dilaporkan deskriptif; uji formal hanya pada tingkat instance.
- Analisis proporsi feasible memakai uji binomial berpasangan (McNemar) atas
  instance (feasible/tidak per metode, mayoritas seed).
- Tidak ada klaim independensi dari seed berulang pada instance yang sama.

## 8. Aturan berhenti & pengecualian

- Berhenti normal: anggaran habis.
- Batas keamanan dinding 900 s per run; bila tercapai, run ditandai `timed_out`
  dan dilaporkan (tidak dibuang).
- Run yang crash dicatat sebagai gagal (`status = "error"`) dan dilaporkan.

## 9. Konfigurasi final (diisi setelah pilot, sebelum run test)

Pilot memilih dari grid terbatas (dijalankan hanya pada instance dev):

| parameter | grid pilot | nilai terkunci |
|---|---|---|
| `pm` (mutasi per gen) | {1/n, 0.02, 0.05} (nilai awal brief 0,05) | **1/n** (0,00625–0,0333 tergantung n) |
| `pm` untuk GA standar | {1/n, 0.02, 0.05} | **1/n** |
| `repair_max_sessions` (k) | {1, 3, 5} | **5** |
| `repair_attempts` | {1, 2} | **1** |
| `swap_attempts` | {0, 1} | **0** (tanpa tukar-sesi) |

Hasil grid pilot lengkap: `04_results/tables/pilot_selection.csv`
(sumber `03_experiments/raw/pilot.jsonl`, 472 run, 36 kombinasi repair × 4
instance dev × 3 seed, ditambah sweep pm GA standar dan baseline greedy).
Kombinasi terpilih mencapai feasible pada 12/12 run dev (median H = 0,
median P = 6, porsi anggaran repair 0,66, median 69 generasi); GA standar
dengan pm = 1/n mencapai feasible pada 6/12 run dev (median H = 1, 208
generasi).

Aturan pemilihan (pre-registered): untuk tiap kombinasi, hitung (i) proporsi run
dev yang feasible, (ii) median `best_H`, (iii) median `best_P`; pilih kombinasi
dengan proporsi feasible tertinggi, lalu `best_H` terendah, lalu `best_P`
terendah; bila seri, pilih biaya repair terendah (porsi anggaran). Konfigurasi
terpilih dipakai untuk **semua** instance test tanpa perubahan.

Ablation (dijalankan pada instance test, dilaporkan terpisah dari RQ1). Karena
konfigurasi terkunci sudah memakai `swap_attempts=0`, `k=5`, `repair_attempts=1`
dan seeding greedy, varian ablation didefinisikan ulang agar tidak redundan:
`repair_attempts=3` (uji batas percobaan perpindahan yang diminta brief),
`k=1`, `k=10`, `swap_attempts=1`, dan `seed_mode=random`. "Repair dimatikan"
diwakili oleh GA standar pada suite utama.

## 10. Reproduksibilitas

- Seed algoritma: 1..20 per instance per metode stokastik (dicatat di setiap baris hasil).
- Generator instance sintetis: seed tercatat di dalam berkas JSON (dan di
  `01_data/synthetic/README.md`); jadwal basis feasible disimpan di berkas.
- Semua hasil mentah: `03_experiments/raw/*.jsonl` (satu baris per run, memuat
  konfigurasi lengkap, hasil, jejak evaluasi, versi, hardware).
- Log stdout/stderr tiap eksekusi: `03_experiments/logs/`.
- Setiap tabel/gambar dihasilkan skrip dari hasil mentah (tidak ada angka
  manual).

## Amendment log

1. **2026-10-29, sebelum run test dianalisis.** Daftar varian ablation pada §9
   disesuaikan agar tidak redundan dengan konfigurasi terkunci (k=5,
   `repair_attempts`=1, `swap_attempts`=0, seeding greedy). Perubahan ini
   dilakukan *sebelum* hasil test dibaca dan tidak mengubah RQ, hipotesis,
   metrik, budget, jumlah seed, maupun daftar instance test.
